from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from hash_manager import hash_password
from models.user import User
from schemas.user import UserCreate


def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_uuid: str) -> User:
    db_user = db.query(User).filter(User.uuid == user_uuid).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return db_user
