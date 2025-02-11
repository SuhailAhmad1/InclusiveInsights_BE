from fastapi import Depends, APIRouter, UploadFile, File, Form
from app.controllers.publication_controller import submit_publication_controller

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
