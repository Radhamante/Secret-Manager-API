from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import User, UserCreate, UserLogin
from app.hash_manager import verify_password
from app.access_token_manager import create_access_token
from app.crud.user import create_user, get_user_by_username_password
from app.database import get_db
import logging
from app.models.user import User as UserModel

auth_router = APIRouter(
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)


@auth_router.post("/register")
def register(auth: UserCreate, db: Session = Depends(get_db)) -> User:
    try:
        return create_user(db, auth)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@auth_router.post("/login")
def login(auth: UserLogin, db: Session = Depends(get_db)):
    try:
        user = get_user_by_username_password(db, auth.username, auth.password)
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
