from uuid import uuid4

from app.crud.user import create_user, get_user_by_username_password, get_user_by_uuid
from app.hash_manager import verify_password
from app.models.user import User
from app.schemas.user import UserCreate
from sqlalchemy.orm import Session


def test_create_user(db_session: Session):

    user_create = UserCreate(username=uuid4().hex, password="password")
    result = create_user(db_session, user_create)

    assert result.username == user_create.username
    assert verify_password(user_create.password, result.hashed_password)


def test_create_user_with_same_username(db_session: Session):
    username = uuid4().hex
    user_create = UserCreate(username=username, password="password")
    result = create_user(db_session, user_create)

    assert result.username == user_create.username
    assert verify_password(user_create.password, result.hashed_password)

    second_user_create = UserCreate(username=username, password="different_password")
    second_result = create_user(db_session, second_user_create)

    assert second_result == None


def test_get_user_by_uuid(db_session: Session, user: User):
    result = get_user_by_uuid(db_session, user.uuid)

    assert result.username == user.username


def test_get_user_by_username_password(db_session: Session, user: User):
    result = get_user_by_username_password(db_session, user.username, "password")

    assert result != None
    assert result.username == user.username
    assert verify_password("password", result.hashed_password)


def test_get_user_by_uuid_not_found(db_session: Session):
    result = get_user_by_uuid(db_session, uuid4())
    assert result is None


def test_get_user_with_wrong_password(db_session: Session, user: User):
    result = get_user_by_username_password(db_session, user.username, "wrong_password")
    assert result == None
