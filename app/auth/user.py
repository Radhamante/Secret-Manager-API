from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException

from auth.access_token_manager import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if username is None:
            raise ValueError("Invalid token")
        return username
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
