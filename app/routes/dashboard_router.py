# from fastapi import Depends, APIRouter, UploadFile, File, Query, Form
# from typing import List
# from app.controllers.dashboard_controller import upload_docs_controller, view_all_docs_controller, \
#     delete_docs_controller, edit_doc_controller, download_doc_controller, get_doc_data_controller, \
#     get_doc_path_controller, get_all_doc_types_controller
# from app.schemas.dashboard_schema import DeleteDocs, EditDoc
# from app.services.auth_service import AuthService

# auth_service = AuthService()

# dashboard_router = APIRouter(
#     prefix="/api/dashboard",
# )

# @dashboard_router.get("/get_all_doc_types")
# def get_all_doc_types(current_user: dict = Depends(auth_service.get_current_user)):
#     return get_all_doc_types_controller(current_user)


# @dashboard_router.post("/upload_docs")
# async def upload_docs(
#         files: List[UploadFile] = File(...),
#         doc_type: int = Form(...),
#         current_user: dict = Depends(auth_service.get_current_user)):
#     return await upload_docs_controller(files, doc_type, current_user)


# @dashboard_router.get("/view_all_docs")
# def view_all_docs(page: int = Query(1, alias="page_num"),
#                   limit: int = Query(5, alias="page_size"),
#                   document_search: str = Query(None, alias="document_search"),
#                   current_user: dict = Depends(auth_service.get_current_user)):
#     return view_all_docs_controller(current_user, page, limit, document_search)


# @dashboard_router.delete("/delete_docs")
# def delete_docs(doc_info: DeleteDocs,
#                 current_user: dict = Depends(auth_service.get_current_user)):
#     return delete_docs_controller(current_user, doc_info)


# @dashboard_router.post("/edit_doc")
# def edit_doc(doc_info: EditDoc,
#              current_user: dict = Depends(auth_service.get_current_user)):
#     return edit_doc_controller(current_user, doc_info)


# @dashboard_router.get("/download_doc")
# def download_doc(doc_id: int = Query(None, alias="doc_id"),
#                  current_user: dict = Depends(auth_service.get_current_user)):
#     return download_doc_controller(current_user, doc_id)


# @dashboard_router.get("/get_doc_data")
# def get_doc_data(doc_id: int = Query(1, alias="doc_id"),
#                  current_user: dict = Depends(auth_service.get_current_user)):
#     return get_doc_data_controller(current_user, doc_id)


# @dashboard_router.get("/get_doc_path")
# def get_doc_path(doc_id: int = Query(1, alias="doc_id"),
#                  current_user: dict = Depends(auth_service.get_current_user)):
#     return get_doc_path_controller(current_user, doc_id)
