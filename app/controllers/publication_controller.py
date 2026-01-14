import os
import shutil
import time
from app.core.logger import logger
from app.core.utils import response_json
from config import DOWNLOAD_DIR, STATIC_DIR, WEBAPP_BASE_URL
from app.crud.publication_crud import submit_publication_db, get_all_publications_db, \
    get_publication_data_db
from app.services.mail_service import sendSubmitEmail
from app.services.s3_services import (
    upload_file_to_s3,
    generate_pre_signed_url
)


async def submit_publication_controller(
        background_tasks,
        main_docx,
        supporting_image,
        img_description,
        first_name,
        last_name,
        email,
        submission_type,
        publication_title,
        author_bio,
        db
):
    try:
        logger.debug(f"{first_name} is trying to submnit a publication....")
        main_file_extension = os.path.splitext(main_docx.filename)[1].lower()
        if main_file_extension != ".docx":
            logger.error("Uploaded wrong file...")
            return response_json({}, "Docx supported only", 400)

        current_time_stamp = str(time.time()).replace('.', '')

        docx_key = f"{first_name}/{current_time_stamp}/{main_docx.filename}"
        await upload_file_to_s3(main_docx, docx_key)

        img_key = f"{first_name}/{current_time_stamp}/{supporting_image.filename}"
        await upload_file_to_s3(supporting_image, img_key)

        submitted_id = await submit_publication_db(
            docx_key,
            img_key,
            img_description,
            first_name,
            last_name,
            email,
            submission_type,
            publication_title,
            author_bio,
            db
        )
        if submitted_id:
            logger.debug('Successfully Submitted...')

            logger.debug("Sending Mail to Admin")
            background_tasks.add_task(sendSubmitEmail, {
                "title": publication_title.title(),
                "author": f"{first_name} {last_name}".title(),
                "category": submission_type.title(),
                "submission_link": f"{WEBAPP_BASE_URL}/admin/view_submission/{submitted_id}"
            })
            return response_json({}, "Successfully Submitted.", 201)

        return response_json({}, "Something went wrong", 500)

    except Exception as e:
        logger.exception(str(e))
        return response_json({}, 'Something went wrong', 500)


async def get_publications_controller(filter_by, search_param, page_number, limit, db):
    try:
        logger.debug("User is trying to get all publications...")
        get_all_publications, next_page = await get_all_publications_db(
            filter_by, search_param, page_number, limit, db)

        for pub in get_all_publications:
            pub["img"] = generate_pre_signed_url(pub["img"])
        return response_json({
            "publications": get_all_publications,
            "next_page": next_page
        }, "Successfully retrieved all publications", 200)

    except Exception as e:
        logger.exception(str(e))
        return response_json({}, 'Something went wrong', 500)


async def get_publication_data_controller(publication_id, db):
    try:
        logger.debug(f"User is trying to get publication : {publication_id}")
        publication_data = await get_publication_data_db(publication_id, db)
        if publication_data:
            publication_data["img"] = generate_pre_signed_url(publication_data["img"])
            return response_json(publication_data, "Successfully retrived publication data", 200)
        return response_json({}, "Publication not found!", 404)

    except Exception as e:
        logger.exception(str(e))
        return response_json({}, 'Something went wrong', 500)
