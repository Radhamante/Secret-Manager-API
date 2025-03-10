from uuid import uuid4

from app.crud.user import create_user, get_user_by_username_password, get_user_by_uuid
from app.hash_manager import verify_password
from app.schemas.user import UserCreate


def test_create_user(db_session):

    user_create = UserCreate(username="username", password="password")
    result = create_user(db_session, user_create)

    assert result.username == user_create.username
    assert verify_password(user_create.password, result.hashed_password)


def test_create_user_with_same_username(db_session):
    user_create = UserCreate(username="username", password="password")
    result = create_user(db_session, user_create)

    assert result.username == user_create.username
    assert verify_password(user_create.password, result.hashed_password)

    second_user_create = UserCreate(username="username", password="different_password")
    second_result = create_user(db_session, second_user_create)

    assert second_result == None


def test_create_user_with_same_username_different_password(db_session):
    user_create = UserCreate(username="username", password="password")
    result = create_user(db_session, user_create)

    assert result.username == user_create.username
    assert verify_password(user_create.password, result.hashed_password)

    second_user_create = UserCreate(username="username", password="different_password")
    second_result = create_user(db_session, second_user_create)

    assert second_result == None


def test_get_user_by_uuid(db_session):
    user_create = UserCreate(username="username", password="password")
    result = create_user(db_session, user_create)

    assert result.username == user_create.username
    assert verify_password(user_create.password, result.hashed_password)

    result = get_user_by_uuid(db_session, result.uuid)

    assert result.username == user_create.username
    assert verify_password(user_create.password, result.hashed_password)


def test_get_user_by_username_password(db_session):
    user_create = UserCreate(username="username", password="password")
    result = create_user(db_session, user_create)

    assert result.username == user_create.username
    assert verify_password(user_create.password, result.hashed_password)

    result = get_user_by_username_password(
        db_session, user_create.username, user_create.password
    )

    assert result.username == user_create.username
    assert verify_password(user_create.password, result.hashed_password)


def test_get_user_by_uuid_not_found(db_session):
    user_create = UserCreate(username="username", password="password")
    result = create_user(db_session, user_create)

    assert result.username == user_create.username
    assert verify_password(user_create.password, result.hashed_password)

    result = get_user_by_uuid(db_session, uuid4())
    assert result is None


def test_get_user_not_found_empty_db(db_session):
    result = get_user_by_uuid(db_session, uuid4())
    assert result == None


def test_get_user_with_wrong_password(db_session):
    user_create = UserCreate(username="username", password="password")
    result = create_user(db_session, user_create)

    assert result.username == user_create.username
    assert verify_password(user_create.password, result.hashed_password)

    result = get_user_by_username_password(
        db_session, user_create.username, "wrong_password"
    )
    assert result == None
