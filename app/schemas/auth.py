from pydantic import BaseModel

class AuthBase(BaseModel):
    username: str
    password: str

class Auth(AuthBase):
    class Config:
        orm_mode = True