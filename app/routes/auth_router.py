# from fastapi import Depends, APIRouter
# from app.controllers.auth_controller import register_user_controller, login_user_controller, \
#     refresh_access_token_controller, get_user_info_controller
# from app.schemas.auth_schema import UserRegistration, UserLogin
# from app.services.auth_service import AuthService

# auth_service = AuthService()

# auth_router = APIRouter(
#     prefix="/api/auth",
# )


# @auth_router.post("/register", include_in_schema=False)
# def register_user(user: UserRegistration):
#     """
#     Router to Register new user
#     """
#     return register_user_controller(user)


# @auth_router.post("/login")
# def login_for_access_token(user: UserLogin):
#     """
#     Router to login
#     """
#     return login_user_controller(user)


# @auth_router.get("/refresh")
# def refresh_access_token(current_user: dict = Depends(auth_service.get_current_user)):
#     """
#     Router to get Access token
#     """
#     return refresh_access_token_controller(current_user)


# @auth_router.get("/user_info")
# def get_user_info(current_user: dict = Depends(auth_service.get_current_user)):
#     """
#     Router to get user info
#     """
#     return get_user_info_controller(current_user)
