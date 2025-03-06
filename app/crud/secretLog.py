from sqlalchemy.orm import Session
from app.models.secretLogs import SecretLogs


def read_secret_logs(db: Session, skip: int = 0, limit: int = 10):
    return db.query(SecretLogs).offset(skip).limit(limit).all()


def read_secret_log(db: Session, secret_uuid: str, skip: int = 0, limit: int = 10):
    return (
        db.query(SecretLogs)
        .filter(SecretLogs.secret_id == secret_uuid)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_secret_logs(db: Session, secret_uuid: str, action: str):

    secret_log = SecretLogs(
        secret_id=secret_uuid,
        action=action,
    )
    db.add(secret_log)
    db.commit()
    db.refresh(secret_log)
    return secret_log
