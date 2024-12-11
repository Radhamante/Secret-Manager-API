import uuid

from pydantic import BaseModel


class BaseUser(BaseModel):
    username: str

    class Config:
        from_attributes = True


class UserCreate(BaseUser):
    password: str


class User(BaseUser):
    uuid: uuid.UUID

    class Config:
        from_attributes = True
