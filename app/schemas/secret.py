from datetime import datetime
from enum import Enum
from typing import Optional
import uuid
from fastapi import File
from pydantic import BaseModel
from typing import Annotated

class SecretType(Enum):
    TEXT = "text"
    FILE = "file"

class SecretBase(BaseModel):
    usage_limit: Optional[int]
    type: SecretType = SecretType.TEXT


class SecretCreate(SecretBase):
    password: str
    duration: int
    filename: Optional[str]
    pass

class SecretCreateText(SecretCreate):
    content: str
    pass

class SecretCreateFile(SecretCreate):
    file: Annotated[bytes, File()]

    pass

class Secret(SecretBase):
    uuid: uuid.UUID
    creation: datetime
    destruction: Optional[datetime]
    usage_count: int

    class Config:
        orm_mode = True

class DecryptedSecret(Secret):
    content: str

    class Config:
        orm_mode = True
