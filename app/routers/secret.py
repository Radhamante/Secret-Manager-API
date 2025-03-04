import logging
from io import BytesIO
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    Query,
    UploadFile,
    status,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from sse_starlette import EventSourceResponse

from app.auth_user import get_current_user
from app.crud.secrets import (
    count_secrets,
    create_secret_from_file,
    create_secret_from_text,
    read_secret,
    read_secret_type,
    read_user_secrets,
)
from app.crypting import decrypt_text
from app.database import get_db
from app.events import secret_created_event
from app.models.user import User
from app.schemas.secret import (
    DecryptedSecret,
    Secret,
    SecretCreateFile,
    SecretCreateText,
    SecretType,
)

SECRET_PREFIX = "/secrets"
secrets_router = APIRouter(
    prefix=SECRET_PREFIX,
    tags=["Secrets"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)


@secrets_router.post(
    "/file",
    response_model=Secret,
    summary="Upload a secret file",
    description="Upload a file that will be stored as a secret. The file requires a password and has optional usage limits and duration.",
    response_description="The details of the uploaded secret file",
)
async def post_secret_file(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
    file: UploadFile = File(..., description="The file to be uploaded"),
    password: str = Form(..., description="The password for the secret"),
    usage_limit: int = Form(
        ..., description="The usage limit for the secret. 0 = No limit"
    ),
    duration: int = Form(
        ..., description="The duration for which the secret is valid. 0 = No expiration"
    ),
):
    try:
        # Read the file content asynchronously
        file_content = await file.read()

        # Create a SecretCreateFile object with the provided data
        secret_create_file = SecretCreateFile(
            duration=duration,
            password=password,
            usage_limit=usage_limit,
            file_content=file_content,
            type=SecretType.FILE,
            filename=file.filename,
        )

        # Create the secret in the database
        created_secret = create_secret_from_file(
            db=db,
            user=user,
            secret_create_file=secret_create_file,
        )

        # Return the created secret
        return created_secret
    except Exception as e:
        # Log the error and raise an HTTP 500 exception
        logger.error(f"Error creating secret: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@secrets_router.post(
    "/text",
    response_model=Secret,
    summary="Create a secret text",
    description="Create a secret text that will be stored securely. The text requires a password and has optional usage limits and duration.",
    response_description="The details of the created secret text",
)
async def post_secret_text(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
    content: str = Form(..., description="The text content to be stored as a secret"),
    usage_limit: int = Form(
        ..., description="The usage limit for the secret. 0 = No limit"
    ),
    password: str = Form(..., description="The password for the secret"),
    duration: int = Form(
        ..., description="The duration for which the secret is valid. 0 = No expiration"
    ),
):
    try:
        # Create a SecretCreateText object with the provided details
        secret_create_text = SecretCreateText(
            duration=duration,
            password=password,
            usage_limit=usage_limit,
            text_content=content,
            type=SecretType.TEXT,
        )

        # Create the secret in the database
        created_secret = create_secret_from_text(
            db=db,
            user=user,
            secret_create_text=secret_create_text,
        )

        # Return the created secret
        return created_secret
    except Exception as e:
        logger.error(f"Error creating secret: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@secrets_router.get(
    "/count",
    summary="Get the count of secrets created",
    description="Get the count of secrets in real-time using Server-Sent Events (SSE). ( Only visible in console )",
)
async def get_secret_count(db: Session = Depends(get_db)):
    async def secret_created_event_generator(db):
        secret_created_event.set()
        while True:
            await secret_created_event.wait()
            secret_created_event.clear()
            count = count_secrets(db)
            yield {"data": str(count)}

    return EventSourceResponse(
        secret_created_event_generator(db),
        send_timeout=30,
    )


@secrets_router.get(
    "/{secret_uuid}/type",
    responses={
        200: {
            "content": {
                "application/json": {},
            },
            "description": "Successful Response",
        },
        404: {"description": "Secret not found"},
        500: {"description": "Internal Server Error"},
    },
    summary="Retrieve a secret type",
    description="Retrieve a secret type using its UUID",
    response_description="The type of the retrieved secret",
)
async def get_secret_type(
    secret_uuid: str = Path(..., description="The UUID of the secret to retrieve"),
    db: Session = Depends(get_db),
):
    try:
        # Read the secret from the database
        secret_type: str = read_secret_type(db, secret_uuid) or "text"
        return JSONResponse(content=jsonable_encoder({"type": secret_type}))
    except Exception as e:
        logger.error(f"Error retrieving secret type: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@secrets_router.get(
    "/{secret_uuid}",
    responses={
        200: {
            "content": {
                "application/json": {},
                "application/octet-stream": {},
            },
            "description": "Successful Response",
        },
        404: {"description": "Secret not found"},
        500: {"description": "Internal Server Error"},
    },
    response_model=DecryptedSecret,
    summary="Retrieve a secret",
    description="Retrieve a secret using its UUID and password. The secret can be either text or a file.",
    response_description="The details of the retrieved secret",
)
async def get_secret(
    secret_uuid: str = Path(..., description="The UUID of the secret to retrieve"),
    password: str = Query(..., description="The password for the secret"),
    db: Session = Depends(get_db),
):
    try:
        # Read the secret from the database
        secret = read_secret(db, secret_uuid, password)
        if not secret:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Secret not found or wrong password or usage limit reached or expired",
            )

        # Decrypt the secret content
        decrypted_content = decrypt_text(secret.content.content, password)

        # Check if the secret is a file
        if secret.content.type == SecretType.FILE.value:
            file_stream = BytesIO(decrypted_content)
            return StreamingResponse(
                file_stream,
                media_type="application/octet-stream",
                headers={"Content-Disposition": f"filename={secret.content.filename}"},
            )
        else:
            secret_dict = secret.__dict__.copy()
            secret_dict.pop("content", None)
            decrypted_secret = DecryptedSecret(
                **secret_dict, content=decrypted_content.decode()
            )
            return decrypted_secret
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving secret: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@secrets_router.get(
    "/",
    response_model=list[Secret],
    summary="Retrieve all secrets of a user",
    description="Retrieve all secrets of a user with pagination.",
    response_description="All secrets paginated",
)
async def get_secrets(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    skip: int = Query(0, description="The number of secrets to skip"),
    limit: int = Query(10, description="The maximum number of secrets to return"),
):
    if user:
        return read_user_secrets(db, user, skip, limit)
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")
