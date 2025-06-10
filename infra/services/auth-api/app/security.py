import os
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, Header, status
from jose import jwt, JWTError
from pydantic import BaseModel

# Load secret & expiry from env (fallbacks for dev)
JWT_SECRET   = os.getenv("JWT_SECRET", "CHANGE_ME")
JWT_ALGO     = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class TokenData(BaseModel):
    tenant_id: int
    exp:       int

def create_access_token(*, tenant_id: int) -> str:
    now = datetime.utcnow()
    payload = {
        "tenant_id": tenant_id,
        "exp":        now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

async def get_current_tenant(
    authorization: str = Header(..., description="Bearer <JWT>")
) -> TokenData:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid auth scheme")
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return TokenData(**data)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
