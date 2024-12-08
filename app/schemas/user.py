from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel

class BaseUser(BaseModel):
    username: str

    class Config:
        from_attributes = True

class UserCreate(BaseUser):
    is_admin: bool = False
    password: str

class UserLogin(BaseUser):
    password: str


class User(BaseUser):
    uuid: uuid.UUID

    class Config:
        from_attributes = True