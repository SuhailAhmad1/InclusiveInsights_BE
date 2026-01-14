from fastapi import Depends, APIRouter, UploadFile, File, Form, Query, BackgroundTasks
from app.controllers.publication_controller import submit_publication_controller, \
    get_publications_controller, get_publication_data_controller
from app.core.db import get_db

publication_router = APIRouter(prefix="/api/publication")


@publication_router.post("/submit_publication")
async def submit_publication(
        background_tasks: BackgroundTasks,
        main_docx: UploadFile = File(...),
        supporting_image: UploadFile = File(...),
        img_description: str = Form(...),
        first_name: str = Form(...),
        last_name: str = Form(...),
        email: str = Form(...),
        submission_type: str = Form(...),
        publication_title: str = Form(...),
        author_bio: str = Form(...),
        db=Depends(get_db)
):
    return await submit_publication_controller(
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
    )


@publication_router.get("/get_publications")
async def get_publications(
    filter_by: str = Query("", alias="filter_by"),
    search_param: str = Query("", alias="search_param"),
    page_number: int = Query(1, alias="page_number"),
    limit: int = Query(6, alias="limit"),
    db=Depends(get_db)
):
    return await get_publications_controller(
        filter_by,
        search_param,
        page_number,
        limit,
        db
    )


@publication_router.get("/get_publication_data")
async def get_publication_data(
    publication_id: str = Query(..., alias="publication_id"),
    db=Depends(get_db)
):
    return await get_publication_data_controller(
        publication_id,
        db
    )
