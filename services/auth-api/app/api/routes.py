from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from common import User, create_access_token, hash_password, verify_password
from ..core.config import settings
from ..db.session import get_session

router = APIRouter()


@router.post("/register")
async def register(email: str, password: str, session=Depends(get_session)):
    hashed = hash_password(password)
    user = User(email=email, password_hash=hashed, tenant_id=1, role="user")
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {"id": user.id, "email": user.email}


@router.post("/login")
async def login(email: str, password: str, session=Depends(get_session)):
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        secret=settings.secret_key,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh():
    return {"detail": "not implemented"}


@router.post("/logout")
async def logout():
    return {"detail": "not implemented"}
