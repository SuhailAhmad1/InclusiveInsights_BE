import os
import shutil
import time
from fastapi.responses import FileResponse
from app.core.logger import logger
from app.core.utils import response_json
from config import WEBAPP_BASE_URL
from app.crud.publication_crud import (
    get_all_publications_admin_db,
    delete_submission_db,
    get_submission_data_admin_db,
    reject_submission_db,
    publish_submission_db
)
from app.services.mail_service import sendPublishedMail, sendRejectionMail


def get_all_submissions_controller(start_date, end_date, category, limit):
    try:
        logger.debug("admin is trying to get all publications...")
        get_all_publications, total_published, total_pending, total_rejected = get_all_publications_admin_db(
            start_date, end_date, category)

        return response_json({
            "publications": get_all_publications,
            "total_submissions": len(get_all_publications),
            "total_published": total_published,
            "total_pending": total_pending,
            "total_rejected": total_rejected
        }, "Successfully retrieved all publications", 200)

    except Exception as e:
        logger.exception(str(e))
        return response_json({}, 'Something went wrong', 500)


def get_submission_data_controller(submission_id):
    try:
        logger.debug(f"User is trying to get publication : {submission_id}")
        publication_data = get_submission_data_admin_db(submission_id)
        if publication_data:
            return response_json(publication_data, "Successfully retrived submission data", 200)
        return response_json({}, "Submission not found!", 404)

    except Exception as e:
        logger.exception(str(e))
        return response_json({}, 'Something went wrong', 500)


def delete_submission_controller(submission_id, current_user):
    try:
        logger.debug("admin is trying to delete a doc")
        delete_submission_db(submission_id)

        return response_json({}, "Successfully deleted a submission", 200)

    except Exception as e:
        logger.exception(str(e))
        return response_json({}, 'Something went wrong', 500)


def reject_submission_controller(background_tasks, submission_id, current_user):
    try:
        logger.debug("admin is trying to reject a doc")
        publication_data = reject_submission_db(submission_id)
        if publication_data:
            logger.debug("Successfully rejected")
            logger.debug("Mail send to the user in the background...")
            background_tasks.add_task(sendRejectionMail, {
                "author": publication_data["author"],
                "title": publication_data["title"],
                "user_email": publication_data["email"]
            })
            return response_json({}, "Successfully rejected a submission", 200)

        raise Exception("Something went wrong")

    except Exception as e:
        logger.exception(str(e))
        return response_json({}, 'Something went wrong', 500)


def download_manuscript_controller(submission_id, current_user):
    try:
        logger.debug(f"User is trying to get publication : {submission_id}")
        publication_data = get_submission_data_admin_db(submission_id)

        if publication_data and os.path.isfile(publication_data["docx_path"]):
            return FileResponse(
                path=publication_data["docx_path"],
                filename=os.path.basename(publication_data["docx_path"]),
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        return response_json({}, "Submission not found!", 404)

    except Exception as e:
        logger.exception(str(e))
        return response_json({}, 'Something went wrong', 500)


def publish_submission_controller(background_tasks, payload, current_user):
    try:
        logger.debug("admin is trying to publish a doc")
        publication_data = publish_submission_db(payload)
        if publication_data:
            logger.debug("Successfully Published")
            logger.debug("Mail send to the user in the background...")
            background_tasks.add_task(sendPublishedMail, {
                "author": publication_data["author"],
                "title": publication_data["title"],
                "publication_link": f"{WEBAPP_BASE_URL}/publications/{payload.submission_id}",
                "user_email": publication_data["email"]
            })
            return response_json({}, "Successfully published a submission", 200)

        raise Exception("Something went wrong")

    except Exception as e:
        logger.exception(str(e))
        return response_json({}, 'Something went wrong', 500)
