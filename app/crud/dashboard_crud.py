from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import json
from app.core.db import engine as db
from app.core.logger import logger


def get_docs_by_hash_db(user_id, doc_hash):
    """
    Function to get all document for a given hash and user

    :param user_id, doc_hash
    :return list of docs
    """
    try:
        with db.connect() as conn:
            query = text("""
                            Select id
                            from document
                            where user_id=:user_id and doc_hash=:doc_hash and deleted_at is null
                        """)
            result = conn.execute(query, {
                "user_id": user_id,
                "doc_hash": doc_hash
            })

            docs = result.fetchall()
            docs = [dict(zip(result.keys(), row))
                    for row in docs]
            return docs

    except SQLAlchemyError as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:32]')
        raise e

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:37]')
        raise e


def store_doc_info_db(doc_info):
    """
    Function to insert document details into the database

    :param data: document details
    :return: status, document id
    """
    try:
        with db.connect() as conn:
            query = text("""
                        INSERT INTO document
                        (doc_name, user_id, doc_path, doc_hash, file_size, document_type) 
                        VALUES 
                        (:doc_name, :user_id, :doc_path, :doc_hash, :file_size, :document_type)
                        """)
            
            result = conn.execute(query, {
                "doc_name": doc_info["doc_name"],
                "user_id": doc_info["user_id"],
                "doc_path": doc_info["doc_path"],
                "doc_hash": doc_info["doc_hash"],
                "file_size": doc_info["file_size"],
                "document_type": doc_info["doc_type"] if doc_info["doc_type"] else None
            })

            id = result.lastrowid
            conn.commit()
            return id

    except SQLAlchemyError as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:71]')
        raise e

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:75]')
        raise e


def get_docs_for_user_db(user_id, page, limit, document_search):
    try:
        with db.connect() as conn:
            offset = (page - 1) * limit

            count_query = text("""
                            SELECT COUNT(*) 
                            FROM document
                            WHERE user_id = :user_id
                            AND deleted_at IS NULL
                            """)
            if document_search:
                count_query = text("""
                            SELECT COUNT(*) 
                            FROM document
                            WHERE user_id = :user_id
                            AND deleted_at IS NULL
                            AND doc_name REGEXP :document_search
                            """)
            count_result = conn.execute(
                count_query, {"user_id": user_id, 'document_search': document_search})
            total_records = count_result.scalar()

            total_pages = (total_records + limit - 1) // limit

            query = text("""
                        SELECT 
                            d.id, 
                            d.doc_name,
                            dt.name as doc_type,
                            d.doc_path,
                            d.file_size,
                            d.thumbnail_path,
                            DATE_FORMAT(CONVERT_TZ(d.created_at, '+00:00', '+05:30'), '%d/%m/%Y %H:%i') AS created_at, 
                            DATE_FORMAT(CONVERT_TZ(d.updated_at, '+00:00', '+05:30'), '%d/%m/%Y %H:%i') AS updated_at, 
                            TIMESTAMPDIFF(SECOND, d.updated_at, NOW()) AS time_diff_seconds
                        FROM document as d
                        LEFT JOIN 
                            document_types as dt 
                        ON
                            d.document_type = dt.id
                        WHERE user_id = :user_id
                        AND d.deleted_at IS NULL
                        ORDER BY d.id DESC
                        LIMIT :limit
                        OFFSET :offset
                        """)
            if document_search:
                query = text("""
                        SELECT 
                            d.id, 
                            d.doc_name,
                            dt.name as doc_type,
                            d.doc_path,
                            d.file_size,
                            d.thumbnail_path,
                            DATE_FORMAT(CONVERT_TZ(d.created_at, '+00:00', '+05:30'), '%d/%m/%Y %H:%i') AS created_at, 
                            DATE_FORMAT(CONVERT_TZ(d.updated_at, '+00:00', '+05:30'), '%d/%m/%Y %H:%i') AS updated_at, 
                            TIMESTAMPDIFF(SECOND, d.updated_at, NOW()) AS time_diff_seconds
                        FROM document as d
                        LEFT JOIN 
                            document_types as dt 
                        ON
                            d.document_type = dt.id
                        WHERE user_id = :user_id
                        AND d.deleted_at IS NULL
                        AND d.doc_name REGEXP :document_search
                        ORDER BY d.id DESC
                        LIMIT :limit
                        OFFSET :offset
                        """)
            result = conn.execute(query, {
                "user_id": user_id,
                "limit": limit,
                "offset": offset,
                "document_search": document_search
            })

            docs = result.fetchall()
            docs = [dict(zip(result.keys(), row))
                    for row in docs]
            for doc in docs:
                query = text("""
                            SELECT 
                            name as module_name,
                            status,
                            time_taken,
                            extracted_data
                            FROM extraction_data
                            WHERE doc_id=:doc_id and deleted_at is NULL
                            """)
                result = conn.execute(query, {
                    "doc_id": doc["id"]
                })
                modules = result.fetchall()
                modules = [dict(zip(result.keys(), row))
                        for row in modules]
                for module in modules:
                    if module["extracted_data"]:
                        module["extracted_data"] = json.loads(module["extracted_data"])
                        if module["extracted_data"]:
                            module["has_error"] = True
                        else:
                            module["has_error"] = False
                    else:
                        module["has_error"] = False
                    del module["extracted_data"]
                doc["modules"] = modules

            return docs, total_pages, total_records

    except SQLAlchemyError as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:32]')
        raise e

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:37]')
        raise e


def delete_docs_db(doc_ids, user_id):
    """
    Function to delete multiple docs from the database based on a list of doc IDs.

    :param doc_ids: list of doc IDs
    :param user_id: user ID
    """
    try:
        with db.connect() as con:
            for doc_id in doc_ids:
                query = text("""
                            select id 
                            from document 
                            where id = :doc_id and 
                            user_id = :user_id and 
                            deleted_at IS NULL
                            """)
                result = con.execute(query, {
                    "doc_id": doc_id,
                    "user_id": user_id
                })
                db_doc = result.fetchone()

                if not db_doc:
                    continue
                query = text("""
                    UPDATE document 
                    SET deleted_at = current_timestamp 
                    WHERE id = :doc_id
                    AND user_id = :user_id
                """)
                con.execute(query, {
                    "doc_id": doc_id,
                    "user_id": user_id
                })

            con.commit()
    except SQLAlchemyError as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:32]')
        raise e

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:37]')
        raise e


def edit_doc_name_db(doc_info, user_id):
    """
    Function to edit doc name in the database

    :param doc_info: new doc name and id
    :param user_id: user id
    """
    try:
        with db.connect() as con:
            query = text("""
                        select id 
                        from document 
                        where id = :doc_id and 
                        user_id = :user_id and 
                        deleted_at IS NULL
                        """)
            result = con.execute(query, {
                "doc_id": doc_info.doc_id,
                "user_id": user_id
            })
            db_doc = result.fetchone()

            if not db_doc:
                return False

            query = text("""
                        update document 
                        set doc_name = :doc_name 
                        where id = :doc_id 
                        and user_id = :user_id
                        """)
            con.execute(query, {
                "doc_name": doc_info.new_doc_name,
                "doc_id": doc_info.doc_id,
                "user_id": user_id
            })
            con.commit()
            return True

    except SQLAlchemyError as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:32]')
        raise e

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:37]')
        raise e


def get_doc_details(user_id, doc_id):
    """
    Function to get doc details in the database

    :param doc_id: doc id
    :param user_id: user id
    """
    try:
        with db.connect() as con:
            query = text("""
                        SELECT 
                            id, 
                            doc_name,
                            doc_path,
                            file_size,
                            thumbnail_path,
                            DATE_FORMAT(CONVERT_TZ(created_at, '+00:00', '+05:30'), '%d/%m/%Y %H:%i') AS created_at, 
                            DATE_FORMAT(CONVERT_TZ(updated_at, '+00:00', '+05:30'), '%d/%m/%Y %H:%i') AS updated_at, 
                            TIMESTAMPDIFF(SECOND, updated_at, NOW()) AS time_diff_seconds
                        FROM document
                        where id=:doc_id
                        AND user_id=:user_id
                        """)
            result = con.execute(query, {
                "doc_id": doc_id,
                "user_id": user_id
            })
            doc_info = result.fetchone()
            if doc_info:
                column_names = result.keys()
                doc_info = dict(zip(column_names, doc_info))
                return doc_info
            else:
                return {}

    except SQLAlchemyError as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:32]')
        raise e

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:37]')
        raise e


def insert_initial_module_db(module_name, doc_id):
    """
    Function to store module initial information in the db
    """
    try:
        with db.connect() as con:
            query = text("""
                        INSERT INTO extraction_data 
                        (name, status, doc_id)
                        VALUES
                        (:module_name, 'processing', :doc_id)
                        """)
            result = con.execute(query, {
                "module_name": module_name,
                "doc_id": doc_id
            })

            id = result.lastrowid
            con.commit()
            return id

    except SQLAlchemyError as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:32]')
        raise e

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:37]')
        raise e


def store_module_extraction_data(module_id, extracted_data, time_taken):
    """
    Function to store extracted data for module
    """
    try:
        with db.connect() as con:
            query = text("""
                    UPDATE extraction_data
                    SET extracted_data=:extracted_data, time_taken=:time_taken, status='processed'
                    where id=:module_id
                    """)
            con.execute(query, {
                "extracted_data": extracted_data,
                "time_taken": time_taken,
                "module_id": module_id
            })
            con.commit()

    except SQLAlchemyError as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:32]')
        raise e

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:37]')
        raise e

def update_module_status(module_id, status):
    """
    Function to update the module status
    """
    try:
        with db.connect() as con:
            query = text("""
                        UPDATE extraction_data
                        SET status=:status
                        where id=:module_id
                        """)
            con.execute(query, {
                'status': status,
                "module_id": module_id
            })
            con.commit()

    except SQLAlchemyError as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:32]')
        raise e

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:37]')
        raise e
    

def get_doc_data_db(user_id, doc_id):
    """
    Function to get the doc data with user Id and doc Id
    """
    try:
        with db.connect() as con:
            query = text("""
                        SELECT
                            d.id, 
                            d.doc_name,
                            d.doc_path,
                            d.file_size,
                            DATE_FORMAT(CONVERT_TZ(d.created_at, '+00:00', '+05:30'), '%d/%m/%Y %H:%i') AS created_at, 
                            DATE_FORMAT(CONVERT_TZ(d.updated_at, '+00:00', '+05:30'), '%d/%m/%Y %H:%i') AS updated_at
                        FROM document as d
                        WHERE d.id=:doc_id AND d.user_id=:user_id AND d.deleted_at is NULL
                        """)
            result = con.execute(query, {
                "doc_id": doc_id,
                "user_id": user_id
            })
            doc_info = result.fetchone()
            if doc_info:
                column_names = result.keys()
                doc_info = dict(zip(column_names, doc_info))

                query = text("""
                            SELECT 
                                name as module_name,
                                status,
                                time_taken,
                                extracted_data
                            FROM extraction_data
                            WHERE doc_id=:doc_id and deleted_at is NULL
                            """)
                result = con.execute(query, {
                    "doc_id": doc_id
                })
                modules = result.fetchall()
                modules = [dict(zip(result.keys(), row))
                        for row in modules]
                for module in modules:
                    module["extracted_data"] = json.loads(module["extracted_data"]) if module["extracted_data"] else []
                doc_info["modules"] = modules
                return doc_info
                
            else:
                return {}
            
    except SQLAlchemyError as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:32]')
        raise e

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:37]')
        raise e
    

def get_doc_by_id_db(user_id, doc_id):
    """
    Function to get all document for a given hash and user

    :param user_id, doc_hash
    :return list of docs
    """
    try:
        with db.connect() as conn:
            query = text("""
                            Select doc_path, doc_path_local, doc_name
                            from document
                            where user_id=:user_id and id=:doc_id and deleted_at is null
                        """)
            result = conn.execute(query, {
                "user_id": user_id,
                "doc_id": doc_id
            })

            doc_info = result.fetchone()
            if doc_info:
                column_names = result.keys()
                doc_info = dict(zip(column_names, doc_info))
            else:
                doc_info = {}
            return doc_info

    except SQLAlchemyError as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:32]')
        raise e

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:37]')
        raise e


def store_local_path_db(doc_id, local_path):
    """
    Function to store the local_path in the db
    """
    try:
        with db.connect() as con:
            query = text("""
                        UPDATE document
                        SET doc_path_local=:local_path
                        where id=:doc_id
                        """)
            con.execute(query, {
                'doc_id': doc_id,
                "local_path": local_path
            })
            con.commit()

    except SQLAlchemyError as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:32]')
        raise e

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:37]')
        raise e
    

def get_all_doc_types_db():
    """
    Function to get all doc types from the db 
    """
    try:
        with db.connect() as con:
            query = text("""
                        SELECT 
                            id, 
                            name
                        FROM
                            document_types
                        ORDER BY
                            name ASC
                        """)
            result = con.execute(query)
            doc_types = result.fetchall()
            doc_types = [dict(zip(result.keys(), row))
                    for row in doc_types]
            return doc_types

    except SQLAlchemyError as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:32]')
        raise e

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:37]')
        raise e
    

def get_page_margins_db(doc_type_id):
    """
    Function to get page margins for doc type
    """
    try:
        with db.connect() as con:
            query = text("""
                        SELECT 
                            page_margins
                        FROM
                            document_types
                        WHERE id=:id
                        """)
            result = con.execute(query, {
                "id": doc_type_id
            })
            doc_type = result.fetchone()

            if doc_type:
                column_names = result.keys()
                doc_type = dict(zip(column_names, doc_type))
            else:
                doc_type = {}
            return doc_type
        
    except SQLAlchemyError as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:32]')
        raise e

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/dashboard_crud.py:37]')
        raise e