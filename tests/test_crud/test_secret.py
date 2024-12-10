import asyncio

import pytest

from app.crud.secrets import create_secret_from_text, read_secret
from app.crypting import decrypt_text
from app.schemas.secret import SecretCreateText, SecretType


def test_create_secret_from_text(
    db_session,
    duration=1,
    password="passwword",
    usage_limit=1,
    usage_count=0,
    text_content="content",
):
    # Create a SecretCreateText object with the provided details
    secret_create_text = SecretCreateText(
        duration=duration,
        password=password,
        usage_limit=usage_limit,
        usage_count=usage_count,
        text_content=text_content,
        type=SecretType.TEXT,
    )

    # Create the secret in the database
    result = create_secret_from_text(
        db=db_session,
        secret_create_text=secret_create_text,
    )

    assert (
        decrypt_text(
            result.content.content,
            secret_create_text.password,
        )
        == secret_create_text.text_content
    )
    assert result.hashed_password is not None
    return result


def test_read_secret_success(db_session):
    password = "password"
    secret = test_create_secret_from_text(db_session, password=password)

    result = read_secret(db_session, secret.uuid, password)

    assert result == secret
    assert secret.usage_count == 1


@pytest.mark.asyncio
async def test_read_secret_expired(db_session):
    password = "password"
    secret = test_create_secret_from_text(
        db_session,
        password=password,
        duration=1,
    )

    await asyncio.sleep(61)

    result = read_secret(db_session, secret.uuid, password)

    assert result is None


def test_read_secret_usage_limit_exceeded(db_session):
    password = "password"
    secret = test_create_secret_from_text(
        db_session,
        password=password,
        usage_limit=1,
        usage_count=1,
    )
    read_secret(db_session, secret.uuid, password)
    result = read_secret(db_session, secret.uuid, password)

    assert result is None


def test_read_secret_invalid_password(db_session):
    password = "password"
    secret = test_create_secret_from_text(
        db_session,
        password=password,
        usage_limit=1,
        usage_count=1,
    )
    result = read_secret(db_session, secret.uuid, "wrong_password")

    assert result is None
