import logging

from app.database import create_tables
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse
from app.routers.auth import auth_router
from app.routers.secret import secrets_router
from app.routers.secretLogs import secrets_log_router

logger = logging.getLogger(__name__)

app = FastAPI()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="API",
        version="1.0.0",
        description="API protégée par Bearer Token",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",  # Indiquez ici le format du token si pertinent (par exemple, "JWT")
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Appliquer le schéma OpenAPI personnalisé
app.openapi = custom_openapi


app.include_router(auth_router)
app.include_router(secrets_router)
app.include_router(secrets_log_router)


@app.on_event("startup")
async def onStartup():
    create_tables()


@app.get("/", include_in_schema=False)
def redirectToStatic():
    return RedirectResponse(url="/docs")
