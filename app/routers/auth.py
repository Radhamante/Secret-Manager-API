import logging
from sqlalchemy.exc import IntegrityError
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.access_token_manager import create_access_token
from app.crud.user import create_user, get_user_by_username_password
from app.database import get_db
from app.schemas.user import User, UserCreate

auth_router = APIRouter(
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)


@auth_router.post(
    "/register",
    summary="Register a new user",
    description="Create a new user account with a unique username.",
    response_model=User,
    responses={
        409: {"description": "Username already exists"},
        500: {"description": "Internal Server Error"},
    },
)
def register(
    auth: Annotated[UserCreate, Depends()],
    db: Session = Depends(get_db),
) -> User:
    try:
        user = create_user(db, auth)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    return user


@auth_router.post(
    "/login",
    summary="Login a user",
    description="Authenticate a user and return an access token.",
    responses={
        401: {"description": "Invalid credentials"},
        500: {"description": "Internal Server Error"},
    },
)
def login(
    auth: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    try:
        user = get_user_by_username_password(db, auth.username, auth.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        access_token = create_access_token(data={"sub": str(user.uuid)})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
