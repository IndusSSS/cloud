from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    is_superuser: bool = False


class UserRead(BaseModel):
    id: int
    username: str
    is_superuser: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str
