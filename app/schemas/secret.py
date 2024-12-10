import uuid
from datetime import datetime
from enum import Enum
from typing import Annotated, BinaryIO, Optional

from fastapi import File, UploadFile
from pydantic import BaseModel


class SecretType(Enum):
    TEXT = "text"
    FILE = "file"


class SecretBase(BaseModel):
    usage_limit: Optional[int]
    type: SecretType = SecretType.TEXT


class SecretCreate(SecretBase):
    password: str
    duration: int


class SecretCreateText(SecretCreate):
    text_content: str


class SecretCreateFile(SecretCreate):
    file_content: bytes
    filename: str


class Secret(SecretBase):
    uuid: uuid.UUID
    creation: datetime
    destruction: Optional[datetime]
    usage_count: int

    class Config:
        from_attributes = True


class DecryptedSecret(Secret):
    content: str

    class Config:
        from_attributes = True
