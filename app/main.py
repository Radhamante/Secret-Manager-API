from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db, create_tables

from auth.hash_manager import hash_password, verify_password
from auth.access_token_manager import create_access_token
from auth.user import get_current_user
from schemas.auth import Auth
from routers.items import items_router

from models.user import User

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



@app.on_event("startup")
async def onStartup():
    create_tables()


@app.get("/")
async def read_root(db: Session = Depends(get_db)):
    return {"Hello": "World 2"}


@app.post("/register")
def register(auth: Auth, db: Session = Depends(get_db)):
    hashed_password = hash_password(auth.password)
    user = User(username=auth.username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully"}


@app.post("/login")
def login(auth: Auth, db: Session = Depends(get_db)):
    print(type(auth))
    user = db.query(User).filter(User.username == auth.username).first()
    if not user or not verify_password(auth.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/protected")
def protected_route(current_user: str = Depends(get_current_user)):
    return {"message": f"Hello, {current_user}"}


app.include_router(items_router)
