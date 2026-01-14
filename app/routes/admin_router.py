from fastapi import Depends, APIRouter, UploadFile, File, Query, BackgroundTasks
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
from app.core.db import get_db

auth_service = AuthService()

admin_router = APIRouter(
    prefix="/api/admin",
)


@admin_router.get("/get_all_submissions")
async def get_all_submissions(
    start_date: str = Query("", alias="start_date"),
    end_date: str = Query("", alias="end_date"),
    category: str = Query("", alias="category"),
    current_user: dict = Depends(auth_service.get_current_user),
    db=Depends(get_db)
):
    return await get_all_submissions_controller(
        start_date,
        end_date,
        category,
        current_user,
        db
    )


@admin_router.get("/get_submission_data")
async def get_submission_data(
    submission_id: str = Query(..., alias="submission_id"),
    current_user: dict = Depends(auth_service.get_current_user),
    db=Depends(get_db)
):
    return await get_submission_data_controller(
        submission_id,
        db
    )


@admin_router.delete("/delete_submission")
async def delete_submission(
    submission_id: str = Query("", alias="submission_id"),
    current_user: dict = Depends(auth_service.get_current_user),
    db=Depends(get_db)
):
    return await delete_submission_controller(
        submission_id,
        current_user,
        db
    )


@admin_router.delete("/reject_submission")
async def reject_submission(
    background_tasks: BackgroundTasks,
    submission_id: str = Query("", alias="submission_id"),
    current_user: dict = Depends(auth_service.get_current_user),
    db=Depends(get_db)
):
    return await reject_submission_controller(
        background_tasks,
        submission_id,
        current_user,
        db
    )


@admin_router.get("/download_manuscript")
async def download_manuscript(
    submission_id: str = Query("", alias="submission_id"),
    current_user: dict = Depends(auth_service.get_current_user),
    db=Depends(get_db)
):
    return await download_manuscript_controller(
        submission_id,
        current_user,
        db
    )


@admin_router.post("/publish_submission")
async def publish_submission(
    background_tasks: BackgroundTasks,
    payload: PublishSubmission,
    current_user: dict = Depends(auth_service.get_current_user),
    db=Depends(get_db)
):
    return await publish_submission_controller(
        background_tasks,
        payload,
        current_user,
        db
    )
