from uuid import uuid4

import pytest

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

    with pytest.raises(Exception) as excinfo:
        user_create = UserCreate(username="username", password="different_password")
        create_user(db_session, user_create)
        print(excinfo)
    assert excinfo.value.args[0] == "Username already exists"
    assert excinfo.typename == "ValueError"


def test_create_user_with_same_username_different_password(db_session):
    user_create = UserCreate(username="username", password="password")
    result = create_user(db_session, user_create)

    assert result.username == user_create.username
    assert verify_password(user_create.password, result.hashed_password)

    with pytest.raises(Exception) as excinfo:
        user_create = UserCreate(username="username", password="different_password")
        create_user(db_session, user_create)
        print(excinfo.statement)
    assert excinfo.value.args[0] == "Username already exists"
    assert excinfo.typename == "ValueError"


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

    with pytest.raises(Exception) as excinfo:
        result = get_user_by_uuid(db_session, uuid4())
    assert excinfo.typename == "Exception"
    assert excinfo.value.args[0] == "User not found"


def test_get_user_not_found_empty_db(db_session):
    with pytest.raises(Exception) as excinfo:
        result = get_user_by_uuid(db_session, uuid4())
    assert excinfo.typename == "Exception"
    assert excinfo.value.args[0] == "User not found"


def test_get_user_with_wrong_password(db_session):
    user_create = UserCreate(username="username", password="password")
    result = create_user(db_session, user_create)

    assert result.username == user_create.username
    assert verify_password(user_create.password, result.hashed_password)

    with pytest.raises(Exception) as excinfo:
        result = get_user_by_username_password(
            db_session, user_create.username, "wrong_password"
        )
    assert excinfo.typename == "Exception"
    assert excinfo.value.args[0] == "Invalid username or password"
