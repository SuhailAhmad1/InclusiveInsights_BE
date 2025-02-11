from pydantic import BaseModel
from typing import List, Optional, Dict

class UserRegistration(BaseModel):
    name: str
    email: str
    password: str
    user_role: str
    secret_key :str


class UserLogin(BaseModel):
    email: str
    password: str

class TokenData(BaseModel):
    email: Optional[str] = None