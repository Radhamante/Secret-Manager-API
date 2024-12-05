from io import BytesIO
from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from models.user import User
from auth_user import get_current_user
from crud.secrets import read_secrets
from crypting import decrypt_text
from models.secretFileContent import SecretFileContent
from models.secretTextContent import SecretTextContent
from models.secret import Secret as SecretModel
from hash_manager import verify_password
from schemas.secret import (
    DecryptedSecret,
    SecretCreateText,
    Secret,
    SecretType,
)
from database import get_db
from crud.secrets import create_secret, read_secret
import logging

secrets_router = APIRouter(
    prefix="/secrets",
    tags=["secrets"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)


@secrets_router.post("/file", response_model=Secret)
async def post_secret_file(
    file: Annotated[UploadFile, File()],
    usage_limit: Annotated[int, Form()],
    password: Annotated[str, Form()],
    duration: Annotated[int, Form()],
    db: Session = Depends(get_db),
):
    # use post_secret to create a secret with a file
    try:
        # create a SecretCreateText from the SecretCreate and file content
        secret_text = SecretCreateText(
            duration=duration,
            password=password,
            usage_limit=usage_limit,
            content=file.file.read().decode(),
            type=SecretType.FILE,
            filename=file.filename,
        )
        logger.error(secret_text)
        created_secret = create_secret(db=db, secret=secret_text)
        logger.info(f"Secret created with UUID: {created_secret.uuid}")
        return created_secret
    except Exception as e:
        logger.error(f"Error creating secret: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@secrets_router.post("/", response_model=Secret)
async def post_secret(
    secret: SecretCreateText,
    db: Session = Depends(get_db),
):
    try:
        logger.error(secret)
        created_secret = create_secret(db=db, secret=secret)
        logger.info(f"Secret created with UUID: {created_secret.uuid}")
        return created_secret
    except Exception as e:
        logger.error(f"Error creating secret: {e}")
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
)
async def get_secret(
    secret_uuid: str,
    password: str,
    db: Session = Depends(get_db),
):
    try:
        secret = read_secret(db, secret_uuid, password)
        if not secret or not verify_password(password, secret.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Secret not found or wrong password or usage limit reached or expired",
            )

        if secret.content.type == SecretType.FILE.value:
            decrypted_content = decrypt_text(secret.content.content, password)
            file_stream = BytesIO(decrypted_content.encode())
            return StreamingResponse(
                file_stream,
                media_type="application/octet-stream",
                headers={
                    "Content-Disposition": f"attachment; filename={secret.content.filename}"
                },
            )
        else:
            decrypted_content = decrypt_text(secret.content.content, password)
            secret_dict = secret.__dict__.copy()
            secret_dict.pop("content", None)
            decrypted_secret = DecryptedSecret(**secret_dict, content=decrypted_content)
            return decrypted_secret
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving secret: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@secrets_router.get("/", response_model=list[Secret])
async def get_secrets(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.is_admin:
        return read_secrets(db)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")
