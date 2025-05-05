from fastapi import Depends, APIRouter, UploadFile, File, Query, Form
from typing import List
from app.controllers.admin_controller import (
    get_all_submissions_controller,
    delete_submission_controller,
    get_submission_data_controller,
    reject_submission_controller,
    download_manuscript_controller,
    publish_submission_controller
)
from app.schemas.admin_schema import PublishSubmission
from app.services.auth_service import AuthService

auth_service = AuthService()

admin_router = APIRouter(
    prefix="/api/admin",
)


@admin_router.get("/get_all_submissions")
def get_all_submissions(
    start_date: str = Query("", alias="start_date"),
    end_date: str = Query("", alias="end_date"),
    category: str = Query("", alias="category"),
    current_user: dict = Depends(auth_service.get_current_user)
):
    return get_all_submissions_controller(start_date, end_date, category, current_user)


@admin_router.get("/get_submission_data")
def get_submission_data(submission_id: str = Query(..., alias="submission_id"),
                        current_user: dict = Depends(auth_service.get_current_user)):
    return get_submission_data_controller(submission_id)


@admin_router.delete("/delete_submission")
def delete_submission(
    submission_id: str = Query("", alias="submission_id"),
    current_user: dict = Depends(auth_service.get_current_user)
):
    return delete_submission_controller(submission_id, current_user)


@admin_router.delete("/reject_submission")
def reject_submission(
    submission_id: str = Query("", alias="submission_id"),
    current_user: dict = Depends(auth_service.get_current_user)
):
    return reject_submission_controller(submission_id, current_user)


@admin_router.get("/download_manuscript")
def download_manuscript(
    submission_id: str = Query("", alias="submission_id"),
    current_user: dict = Depends(auth_service.get_current_user)
):
    return download_manuscript_controller(submission_id, current_user)

@admin_router.post("/publish_submission")
def publish_submission(
    payload: PublishSubmission,
    current_user: dict = Depends(auth_service.get_current_user)
):
    return publish_submission_controller(payload, current_user)