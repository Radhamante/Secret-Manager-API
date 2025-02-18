import logging
from datetime import datetime, timedelta

from app.crud.secretLog import create_secret_logs
from app.crypting import encrypt_text
from app.events import secret_created_event
from app.hash_manager import hash_password, verify_password
from app.models.secret import Secret
from app.models.secretContent import SecretContent
from app.models.secretFileContent import SecretFileContent
from app.models.secretTextContent import SecretTextContent
from app.schemas.secret import SecretCreate, SecretCreateFile, SecretCreateText
from app.schemas.secretLog import SecretLogActionEnum
from sqlalchemy import or_
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def read_secret_type(db: Session, secret_uuid: str) -> str | None:
    secret = db.query(Secret).filter(Secret.uuid == secret_uuid).first()
    if secret:
        return secret.content.type
    else:
        return None


def read_secret(db: Session, secret_uuid: str, password: str):
    secret = (
        db.query(Secret)
        .filter(
            Secret.uuid == secret_uuid,
            or_(Secret.destruction == None, Secret.destruction > datetime.now()),
            or_(Secret.usage_limit == None, Secret.usage_limit > Secret.usage_count),
        )
        .first()
    )
    if secret and verify_password(password, secret.hashed_password):
        secret.usage_count += 1
        create_secret_logs(db, secret_uuid, SecretLogActionEnum.GET)
        if secret.usage_limit and secret.usage_limit >= secret.usage_count:
            create_secret_logs(db, secret_uuid, SecretLogActionEnum.EXPIRE)
        db.commit()
        db.refresh(secret)
        return secret
    else:
        return None


def read_secrets(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Secret).offset(skip).limit(limit).all()


def create_secret_from_text(db: Session, secret_create_text: SecretCreateText):
    content = SecretTextContent(
        content=encrypt_text(
            secret_create_text.text_content.encode(),
            secret_create_text.password,
        )
    )
    secret_create = SecretCreate(
        **secret_create_text.__dict__,
    )
    return create_secret(
        db,
        content=content,
        secret_create=secret_create,
    )


def create_secret_from_file(db: Session, secret_create_file: SecretCreateFile):
    content = SecretFileContent(
        content=encrypt_text(
            secret_create_file.file_content,
            secret_create_file.password,
        ),
        filename=secret_create_file.filename,
    )
    secret_create = SecretCreate(
        **secret_create_file.__dict__,
    )
    return create_secret(
        db,
        content=content,
        secret_create=secret_create,
    )


def create_secret(db: Session, secret_create: SecretCreate, content: SecretContent):
    now = datetime.now()

    db_secret = Secret(
        creation=now,
        destruction=(
            now + timedelta(minutes=secret_create.duration)
            if secret_create.duration
            else None
        ),
        usage_limit=secret_create.usage_limit if secret_create.usage_limit else None,
        hashed_password=hash_password(secret_create.password),
        content=content,
    )

    db.add(db_secret)
    db.commit()
    db.refresh(db_secret)
    secret_created_event.set()
    create_secret_logs(db, db_secret.uuid, SecretLogActionEnum.CREATE)
    return db_secret


def count_secrets(db: Session):
    return db.query(Secret).count()
