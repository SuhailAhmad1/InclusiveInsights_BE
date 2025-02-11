import os
from sqlalchemy.exc import SQLAlchemyError
import boto3
import hashlib
from urllib.parse import urlparse
from io import BytesIO
from fastapi.responses import StreamingResponse
import time
import json

from app.core.logger import logger
from app.core.utils import response_json
from app.crud.dashboard_crud import store_doc_info_db, get_docs_by_hash_db, \
    get_docs_for_user_db, delete_docs_db, edit_doc_name_db, get_doc_details, \
    insert_initial_module_db, get_doc_data_db, get_doc_by_id_db, store_local_path_db, \
    get_all_doc_types_db, get_page_margins_db
from app.controllers.utils.dashboard_utils import generate_thumbnail, generate_pre_signed_url, \
    initiate_extraction_task
from config import ALLOWED_EXTENSIONS, AWS_ACCESS_KEY_ID, \
    AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, S3_BUCKET_NAME, DOCX_MODULES_DATA, \
    STATIC_FILES_DIR, EXCEL_MODULES_DATA

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)


def hash_s3_file_sha256(bucket_name, object_key, chunk_size=8192):

    sha256_hash = hashlib.sha256()

    s3_object = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    file_stream = s3_object['Body']

    for chunk in iter(lambda: file_stream.read(chunk_size), b''):
        sha256_hash.update(chunk)

    return sha256_hash.hexdigest()


async def upload_docs_controller(files, doc_type, current_user):
    """
    Controller to upload multiple docs

    :return: json response ("Success or failure message")
    """
    try:
        logger.debug(str(f"{current_user['email']} is trying to upload the docs...") +
                     '[BE_Novo_New/app/controllers/dashboard_controller.py:12]')
        unsupported_files = []
        duplicate_files = []
        for file in files:
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in ALLOWED_EXTENSIONS:
                logger.warning(f"{file.filename}'s extension not supported")
                unsupported_files.append(file.filename)
                continue

            key = f"{current_user['name']}/{file.filename}"

            file_content = await file.read()
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=key,
                Body=file_content
            )

            s3_path = f"s3://{S3_BUCKET_NAME}/{current_user['name']}/{file.filename}"
            file_hash = hash_s3_file_sha256(S3_BUCKET_NAME, key)
            doc_data = {
                "doc_name": file.filename,
                "user_id": current_user['id'],
                "doc_path": s3_path,
                "doc_hash": file_hash,
                "file_size": len(file_content)/1000000,
                "doc_type": doc_type
            }
            docs = get_docs_by_hash_db(
                doc_data["user_id"], doc_data["doc_hash"])
            if docs:
                duplicate_files.append(file.filename)
                continue
            
            inserted_doc_id = store_doc_info_db(doc_data)

            # Call DS tasks through Celery here
            modules = []
            if file_extension == ".docx":
                modules = DOCX_MODULES_DATA

            elif file_extension == '.xlsx':
                modules = EXCEL_MODULES_DATA

            for module in modules:
                inserted_module_id = insert_initial_module_db(
                    module["name"], inserted_doc_id)
                
                page_margins = None
                if module["name"] == "page_margins" and doc_type:
                    page_margins = json.loads(get_page_margins_db(doc_type)["page_margins"])
                    page_margins = {
                        "top": page_margins[0],
                        "bottom": page_margins[1],
                        "left": page_margins[2],
                        "right": page_margins[3]
                    }
                task = initiate_extraction_task.delay(
                    inserted_module_id, module["endpoint"], s3_path, page_margins)
                if task is None:
                    logger.error(str(f"Failed to initiate task for {module['name']}") +
                                '[BE_Novo_New/app/controllers/dashboard_controller.py:106]')
            

        return response_json({
            "duplicate_files": duplicate_files,
            "unsupported_files": unsupported_files}, "Files uploaded successfully", 201)

    except SQLAlchemyError as e:
        return response_json({}, "Database error", 500)

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Novo_New/app/controllers/dashboard_controller.py:100]')
        return response_json({}, 'Something went wrong', 500)


def view_all_docs_controller(current_user, page, limit, document_search):
    """
    Function to get all the docs for a user

    :return: List of files
    """
    try:
        logger.debug(str(f"Fetching all documents for user {current_user['name']}...") +
                     '[BE_Novo_New/app/controllers/dashboard_controller.py:112]')

        docs, total_pages, total_records = get_docs_for_user_db(
            current_user["id"], page, limit, document_search)
        for doc in docs:
            doc["doc_signed_url"] = generate_pre_signed_url(doc["doc_path"])
            del doc["doc_path"]

        data = {
            "documents": docs,
            "page_size": limit,
            "page_index": page,
            "total_pages": total_pages,
            "total_documents": total_records
        }
        return response_json(data, "Retrieved all docs", 200)

    except SQLAlchemyError as e:
        return response_json({}, "Database error", 500)

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Novo_New/app/controllers/dashboard_controller.py:100]')
        return response_json({}, 'Something went wrong', 500)


def delete_docs_controller(current_user, doc_info):
    """
    Controller to delete the documents

    :return: json response ("Success or failure message")
    """
    try:
        logger.debug(str(f"{current_user['name']} is trying to delete {doc_info.doc_ids}") +
                     '[BE_Novo_New/app/controllers/dashboard_controller.py:145]')
        delete_docs_db(doc_info.doc_ids, current_user["id"])
        logger.debug(str("Successfully deleted all docs...") +
                     '[BE_Novo_New/app/controllers/dashboard_controller.py:148]')
        return response_json({}, "Documents deleted successfully", 200)

    except SQLAlchemyError as e:
        return response_json({}, "Database error", 500)

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Novo_New/app/controllers/dashboard_controller.py:100]')
        return response_json({}, 'Something went wrong', 500)


def edit_doc_controller(current_user, doc_info):
    """
    Controller to edit the doc name

    :return: json response ("Success or failure message")
    """
    try:
        logger.debug(f"{current_user['name']} is trying to update doc name - {doc_info.doc_id}" +
                     '[BE_Novo_New/app/controllers/dashboard_controller.py:168]')
        status = edit_doc_name_db(doc_info, current_user["id"])
        if status:
            logger.debug(str("Successfully edited the doc name") +
                         '[BE_Novo_New/app/controllers/dashboard_controller.py:168]')
            return response_json({}, "Document edited successfully", 200)
        logger.error(str("Doc does not exist...") +
                     '[BE_Novo_New/app/controllers/dashboard_controller.py:168]')
        return response_json({}, "Doc does not exist", 404)

    except SQLAlchemyError as e:
        return response_json({}, "Database error", 500)

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Novo_New/app/controllers/dashboard_controller.py:100]')
        return response_json({}, 'Something went wrong', 500)


def download_doc_controller(current_user, doc_id):
    """
    Controller to download the file from s3 and send it to client
    """
    try:
        logger.debug(str(f"{current_user['name']} is trying to downlaod doc with id {doc_id}...") +
                     '[BE_Novo_New/app/controllers/dashboard_controller.py:194]')
        doc_info = get_doc_details(current_user['id'], doc_id)
        if not doc_info:
            logger.error(str("Doc does not exist or not authorized...") +
                         '[BE_Novo_New/app/controllers/dashboard_controller.py:197]')
            return response_json({}, "Doc does not exist", 404)

        parsed_url = urlparse(doc_info['doc_path'])
        bucket_name = parsed_url.netloc
        s3_key = parsed_url.path.lstrip('/')

        s3_object = s3_client.get_object(Bucket=bucket_name, Key=s3_key)

        return StreamingResponse(
            s3_object['Body'],
            media_type="application/msword",  # MIME type for DOC files
            headers={
                "Content-Disposition": f"attachment; filename={doc_info['doc_name']}"}
        )

    except SQLAlchemyError as e:
        return response_json({}, "Database error", 500)

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Novo_New/app/controllers/dashboard_controller.py:100]')
        return response_json({}, 'Something went wrong', 500)


def get_doc_data_controller(current_user, doc_id):
    """
    Controller to get the extracted data of the document
    """
    try:
        logger.debug(str(f"{current_user['name']} is trying to get doc info - {doc_id}...") +
                     '[BE_Novo_New/app/controllers/dashboard_controller.py:248]')
        doc_info = get_doc_data_db(current_user["id"], doc_id)
        if not doc_info:
            logger.error(str("Doc does not exist or not authorized...") +
                         '[BE_Novo_New/app/controllers/dashboard_controller.py:197]')
            return response_json({}, "Doc does not exist", 404)
        doc_info["doc_signed_url"] = generate_pre_signed_url(
            doc_info["doc_path"])
        del doc_info["doc_path"]
        return response_json(doc_info, "Successfully Retrieved doc data", 200)

    except SQLAlchemyError as e:
        return response_json({}, "Database error", 500)

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Novo_New/app/controllers/dashboard_controller.py:100]')
        return response_json({}, 'Something went wrong', 500)


def get_doc_path_controller(current_user, doc_id):
    """
    Controller to get the extracted data of the document
    """
    try:
        logger.debug(str(f"{current_user['name']} is trying to get doc info - {doc_id}...") +
                     '[BE_Novo_New/app/controllers/dashboard_controller.py:248]')
        doc_info = get_doc_by_id_db(current_user["id"], doc_id)
        if not doc_info:
            logger.error(str("Doc does not exist or not authorized...") +
                         '[BE_Novo_New/app/controllers/dashboard_controller.py:197]')
            return response_json({}, "Doc does not exist", 404)

        if not doc_info["doc_path_local"]:
            parsed_url = urlparse(doc_info["doc_path"])
            bucket_name = parsed_url.netloc
            s3_key = parsed_url.path.lstrip('/')

            current_time_stamp = str(time.time()).replace('.', '')

            if not os.path.isdir(f"{STATIC_FILES_DIR}{current_user['id']}"):
                os.mkdir(f"{STATIC_FILES_DIR}{current_user['id']}")
            if not os.path.isdir(f"{STATIC_FILES_DIR}{current_user['id']}/{current_time_stamp}"):
                os.mkdir(
                    f"{STATIC_FILES_DIR}{current_user['id']}/{current_time_stamp}")
            filepath = os.path.join(f"{STATIC_FILES_DIR}{current_user['id']}/{current_time_stamp}", f"{doc_info['doc_name']}.docx")

            s3_client.download_file(bucket_name, s3_key, filepath)

            store_local_path_db(doc_id, f"/files/{current_user['id']}/{current_time_stamp}/{doc_info['doc_name']}"+".docx")
            return response_json({
                "path": f"/files/{current_user['id']}/{current_time_stamp}/{doc_info['doc_name']}"+".docx"
                }, "Successfully Retrieved doc path", 200)

        return response_json({"path": doc_info["doc_path_local"]},
                             "Successfully Retrieved doc path", 200)

    except SQLAlchemyError as e:
        return response_json({}, "Database error", 500)

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Novo_New/app/controllers/dashboard_controller.py:100]')
        return response_json({}, 'Something went wrong', 500)


def get_all_doc_types_controller(current_user):
    """
    Controller to get all the doc types for upload fucntionality
    """
    try:
        logger.debug(str(f"{current_user['name']} is try to get all doc types...")+
                     '[BE_Novo_New/app/controllers/dashboard_controller.py:314]')
        
        all_doc_types = get_all_doc_types_db()

        return response_json(all_doc_types, "Successfully Retrieved doc types", 200)
    except SQLAlchemyError as e:
        return response_json({}, "Database error", 500)

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Novo_New/app/controllers/dashboard_controller.py:320]')
        return response_json({}, 'Something went wrong', 500)