from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException

from access_token_manager import decode_access_token
from models.user import User
from crud.user import get_user
from database import get_db
from sqlalchemy.orm import Session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_access_token(token)
        uuid = payload.get("sub")
        if uuid is None:
            raise ValueError("Invalid token")
        return get_user(db, uuid)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
