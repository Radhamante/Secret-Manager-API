from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session
from models.user import User
from auth_user import get_current_user
from crud.secretLog import read_secret_log, read_secret_logs
from schemas.secretLog import SecretLog
from database import get_db
import logging

from routers.secret import SECRET_PREFIX

SECRET_LOGS_PREFIX = "/logs"
secrets_log_router = APIRouter(
    prefix=f"{SECRET_PREFIX}/{SECRET_LOGS_PREFIX}",
    tags=["secrets-logs"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)


@secrets_log_router.get("/", response_model=list[SecretLog])
async def get_secret_logs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    user: User = Depends(get_current_user),
):
    if user.is_admin:
        return read_secret_logs(db, skip, limit)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")


@secrets_log_router.get("/{secret_uuid}", response_model=list[SecretLog])
async def get_secret_logs(
    secret_uuid: str,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    user: User = Depends(get_current_user),
):
    if user.is_admin:
        return read_secret_log(db, secret_uuid, skip, limit)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")
