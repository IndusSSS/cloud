from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.security import create_access_token

router = APIRouter()

class LoginIn(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=TokenOut)
async def login(data: LoginIn):
    # TODO: replace with real user lookup & password check
    if data.username == "admin" and data.password == "SecretPass!":
        token = create_access_token(tenant_id=1)
        return TokenOut(access_token=token)
    raise HTTPException(status_code=401, detail="Invalid credentials")
