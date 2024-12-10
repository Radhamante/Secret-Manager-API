from enum import Enum

from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel

class SecretLogActionEnum(Enum):
    CREATE = "create"
    GET = "get"
    EXPIRE = "expire"

class BaseSecretLog(BaseModel):
    uuid: UUID
    action: SecretLogActionEnum
    timestamp: datetime
    secret_id: UUID

class SecretLog(BaseSecretLog):
    class Config:
        from_attributes = True