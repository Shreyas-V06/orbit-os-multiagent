from pydantic import BaseModel
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserPublic(BaseModel):
    username: str
    email: Optional[str] = None
    disabled: Optional[bool] = None

class UserPrivate(UserPublic):
    hashed_password: str
