from typing import Annotated
from fastapi import FastAPI, Depends, File, Form, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from database import create_tables

from auth_user import get_current_user
from routers.items import items_router
from routers.secret import secrets_router
from routers.auth import auth_router


from fastapi.openapi.utils import get_openapi

app = FastAPI()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="API sécurisée avec Bearer Token",
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

app.include_router(items_router)
app.include_router(auth_router)
app.include_router(secrets_router)


@app.on_event("startup")
async def onStartup():
    create_tables()


@app.get("/protected")
def protected_route(current_user: str = Depends(get_current_user)):
    return {"message": f"Hello, {current_user}"}

@app.post("/files/")
async def create_file(
    file: Annotated[bytes, File()],
    fileb: Annotated[UploadFile, File()],
    token: Annotated[str, Form()],
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }

@app.get("/")
def redirectToStatic():
    return RedirectResponse(url="/index.html")


app.mount("/", StaticFiles(directory="frontend/build"), name="static")