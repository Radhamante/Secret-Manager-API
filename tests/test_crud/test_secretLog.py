from app.crud.secretLog import create_secret_logs, read_secret_log, read_secret_logs
from app.crud.secrets import read_secret
from app.schemas.secretLog import SecretLogActionEnum
from tests.test_crud.test_secret import test_create_secret_from_text


def test_create_secret_logs(
    db_session,
    user,
):
    created_secret = test_create_secret_from_text(db_session, user)
    result = create_secret_logs(
        db=db_session,
        secret_uuid=created_secret.uuid,
        action=SecretLogActionEnum.GET,
    )
    assert result.secret_id == created_secret.uuid


def test_read_secret_log(db_session, user):
    created_secret = test_create_secret_from_text(db_session, user)
    result = read_secret_log(db_session, created_secret.uuid)
    assert result[0].secret_id == created_secret.uuid
    assert result[0].action == SecretLogActionEnum.CREATE


def test_secret_log_enum(db_session, user):
    password = "password"
    created_create_secret = test_create_secret_from_text(
        db_session, user, password=password, usage_limit=1
    )
    read_secret(db_session, created_create_secret.uuid, password)
    result = read_secret_log(db_session, created_create_secret.uuid)

    assert result[0].secret_id == created_create_secret.uuid
    assert result[0].action == SecretLogActionEnum.CREATE

    assert result[1].secret_id == created_create_secret.uuid
    assert result[1].action == SecretLogActionEnum.GET

    assert result[2].secret_id == created_create_secret.uuid
    assert result[2].action == SecretLogActionEnum.EXPIRE
