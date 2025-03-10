import os
import shutil
import time
from app.core.logger import logger
from app.core.utils import response_json
from config import DOWNLOAD_DIR, STATIC_DIR
from app.crud.publication_crud import submit_publication_db, get_all_publications_db


def submit_publication_controller(main_docx, supporting_image, first_name, last_name, email, submission_type, publication_title, author_bio):
    try:
        logger.debug(f"{first_name} is trying to submnit a publication....")
        main_file_extension = os.path.splitext(main_docx.filename)[1].lower()
        if main_file_extension != ".docx":
            logger.error("Uploaded wrong file...")
            return response_json({}, "Docx supported only", 400)

        current_time_stamp = str(time.time()).replace('.', '')

        if not os.path.isdir(f"{DOWNLOAD_DIR}/{current_time_stamp}"):
            os.makedirs(f"{DOWNLOAD_DIR}/{current_time_stamp}")
        docx_path = f"{DOWNLOAD_DIR}/{current_time_stamp}/{main_docx.filename}"
        with open(docx_path, "wb") as buffer:
            shutil.copyfileobj(main_docx.file, buffer)

        if not os.path.isdir(f"{STATIC_DIR}/{current_time_stamp}"):
            os.makedirs(f"{STATIC_DIR}/{current_time_stamp}")
        img_path = f"{STATIC_DIR}/{current_time_stamp}/{supporting_image.filename}"
        with open(img_path, "wb") as buffer:
            shutil.copyfileobj(supporting_image.file, buffer)

        db_img_path = f"/files/{current_time_stamp}/{supporting_image.filename}"
        status = submit_publication_db(docx_path, db_img_path, first_name,
                                       last_name, email, submission_type, publication_title, author_bio)
        if status:
            logger.debug('Successfully Submutted...')
            return response_json({}, "Successfully Submitted.", 201)

        return response_json({}, "Something went wrong", 500)

    except Exception as e:
        logger.exception(str(e))
        return response_json({}, 'Something went wrong', 500)


def get_publications_controller(filter_by, search_param, page_number):
    try:
        logger.debug("User is trying to get all publications...")
        get_all_publications, next_page = get_all_publications_db(
            filter_by, search_param, page_number)

        return response_json({
            "publications": get_all_publications,
            "next_page": next_page
        }, "Successfully retrieved all publications", 200)

    except Exception as e:
        logger.exception(str(e))
        return response_json({}, 'Something went wrong', 500)
