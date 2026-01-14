from fastapi import Depends, APIRouter
from app.controllers.auth_controller import register_user_controller, login_user_controller, \
    refresh_access_token_controller, get_user_info_controller
from app.schemas.auth_schema import UserRegistration, UserLogin
from app.services.auth_service import AuthService
from app.core.db import get_db

auth_service = AuthService()

auth_router = APIRouter(
    prefix="/api/auth",
)


@auth_router.post("/register", include_in_schema=False)
async def register_user(
    user: UserRegistration,
    db=Depends(get_db)
):
    """
    Router to Register new user
    """
    return await register_user_controller(user, db)


@auth_router.post("/login")
async def login_for_access_token(
    user: UserLogin,
    db=Depends(get_db)
):
    """
    Router to login
    """
    return await login_user_controller(user, db)


@auth_router.get("/refresh")
async def refresh_access_token(
    current_user: dict = Depends(auth_service.get_current_user),
    db = Depends(get_db)
):
    """
    Router to get Access token
    """
    return await refresh_access_token_controller(current_user, db)
