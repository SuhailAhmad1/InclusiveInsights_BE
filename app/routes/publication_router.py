from fastapi import Depends, APIRouter, UploadFile, File, Form, Query
from app.controllers.publication_controller import submit_publication_controller,\
    get_publications_controller, get_publication_data_controller

publication_router = APIRouter(prefix="/api/publication")


@publication_router.post("/submit_publication")
def submit_publication(
        main_docx: UploadFile = File(...),
        supporting_image: UploadFile = File(...),
        first_name: str = Form(...),
        last_name: str = Form(...),
        email: str = Form(...),
        submission_type: str = Form(...),
        publication_title: str = Form(...),
        author_bio: str = Form(...)
):
    return submit_publication_controller(
        main_docx,
        supporting_image,
        first_name,
        last_name,
        email,
        submission_type,
        publication_title,
        author_bio
    )


@publication_router.get("/get_publications")
def get_publications(filter_by: str = Query("", alias="filter_by"),
                     search_param: str = Query("", alias="search_param"),
                     page_number: int = Query(1, alias="page_number"),
                     limit: int = Query(6, alias="limit")):
    return get_publications_controller(filter_by, search_param, page_number, limit)


@publication_router.get("/get_publication_data")
def get_publication_data(publication_id: str = Query(..., alias="publication_id")):
    return get_publication_data_controller(publication_id)