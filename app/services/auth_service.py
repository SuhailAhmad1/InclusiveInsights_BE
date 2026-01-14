import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Union
from app.core.logger import logger
from app.schemas.auth_schema import TokenData
from app.core.db import get_db
from app.crud.user_crud import get_user_by_email_db
from config import SECRET_KEY, ALGORITHM


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthService:
    def verify_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    async def get_current_user(self, token: str = Depends(oauth_2_scheme), db = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
        try:
            payload = jwt.decode(token, SECRET_KEY,
                                 algorithms=[ALGORITHM])

            email: str = payload.get("sub")
            logger.debug(f"Email {email}")
            if email is None:
                logger.debug("Entering email none")
                raise credentials_exception
            token_data = TokenData(email=email)
        except JWTError:
            raise credentials_exception

        user = await get_user_by_email_db(email=token_data.email, db=db)
        if user is None or user["user_role"] != "admin":
            raise credentials_exception
        return user

    def create_access_token(self, data: dict, expires_delta: Union[timedelta, None] = None):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

