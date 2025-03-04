from typing import Annotated
import uuid

from fastapi import Form
from pydantic import BaseModel


class BaseUser(BaseModel):
    username: str

    class Config:
        from_attributes = True


class UserCreate:
    def __init__(
        self,
        *,
        username: Annotated[
            str,
            Form(),
        ],
        password: Annotated[
            str,
            Form(),
        ]
    ):
        self.username = username
        self.password = password


class User(BaseUser):
    uuid: uuid.UUID

    class Config:
        from_attributes = True
