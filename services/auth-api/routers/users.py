from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from models import User
from schemas import UserCreate, UserRead
from security import get_password_hash
from dependencies import get_session, require_super_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
def create_user(
    data: UserCreate,
    session: Session = Depends(get_session),
    _: User = Depends(require_super_admin),
) -> User:
    if session.exec(select(User).where(User.username == data.username)).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered"
        )
    user = User(
        username=data.username,
        hashed_password=get_password_hash(data.password),
        is_superuser=data.is_superuser,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/", response_model=list[UserRead])
def list_users(
    session: Session = Depends(get_session), _: User = Depends(require_super_admin)
) -> list[User]:
    return list(session.exec(select(User)).all())


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_super_admin),
) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_super_admin),
) -> None:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    session.delete(user)
    session.commit()
