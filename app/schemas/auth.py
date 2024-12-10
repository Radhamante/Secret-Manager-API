from pydantic import BaseModel

class AuthBase(BaseModel):
    username: str
    password: str

class Auth(AuthBase):
    class Config:
        from_attributes = True