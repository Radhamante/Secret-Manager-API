import logging

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.database import create_tables
from app.routers.auth import auth_router
from app.routers.secret import secrets_router
from app.routers.secretLogs import secrets_log_router

logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(auth_router)
app.include_router(secrets_router)
app.include_router(secrets_log_router)


@app.on_event("startup")
async def onStartup():
    create_tables()


@app.get("/", include_in_schema=False)
def redirectToStatic():
    return RedirectResponse(url="/docs")
