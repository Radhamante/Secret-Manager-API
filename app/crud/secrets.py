from datetime import datetime, timedelta
from sqlalchemy import or_
from sqlalchemy.orm import Session
from models.secret import Secret
from hash_manager import hash_password, verify_password
from crypting import encrypt_text
from models.secretFileContent import SecretFileContent
from models.secretTextContent import SecretTextContent
from schemas.secret import SecretCreateText, SecretType


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
        db.commit()
        db.refresh(secret)
        return secret
    else:
        return None


def read_secrets(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Secret).offset(skip).limit(limit).all()


def create_secret(db: Session, secret: SecretCreateText):
    now = datetime.now()

    if secret.type == SecretType.TEXT:
        content = SecretTextContent(
            content=encrypt_text(secret.content, secret.password)
        )
    elif secret.type == SecretType.FILE:
        content = SecretFileContent(
            content=encrypt_text(secret.content, secret.password),
            filename=secret.filename,
        )
    else:
        raise ValueError("Invalid secret type")

    db_secret = Secret(
        creation=now,
        destruction=(
            now + timedelta(minutes=secret.duration) if secret.duration else None
        ),
        usage_limit=secret.usage_limit if secret.usage_limit else None,
        hashed_password=hash_password(secret.password),
        content=content,
    )

    db.add(db_secret)
    db.commit()
    db.refresh(db_secret)
    return db_secret
