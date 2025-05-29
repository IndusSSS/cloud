import os
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

# ───────────────────────────────────────────────────────────
# Configuration (override via ENV in production)
# ───────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("JWT_SECRET", "ReplaceThisWithAStrongKey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Single admin user (move to a real DB for multi-admin setups)
ADMIN_USERNAME = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASS", "ChangeMe123!")

# ───────────────────────────────────────────────────────────
# Password hashing & token setup
# ───────────────────────────────────────────────────────────
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")

router = APIRouter(
    prefix="/v1/auth",
    tags=["auth"],
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_ctx.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_ctx.hash(password)


def authenticate_user(username: str, password: str) -> bool:
    """
    Verify username/password against our single admin.
    """
    if username != ADMIN_USERNAME:
        return False
    # compare against the hash of the ENV password
    return verify_password(password, get_password_hash(ADMIN_PASSWORD))


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT token with an expiration.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ───────────────────────────────────────────────────────────
# Routes
# ───────────────────────────────────────────────────────────
@router.post("/login", summary="Obtain a JWT token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Exchange username & password for a bearer token.
    """
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token({"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", summary="Validate token & return current user")
async def me(current_user: str = Depends(oauth2_scheme)):
    """
    A simple endpoint to verify a token is valid. Returns the 'sub' claim.
    """
    try:
        payload = jwt.decode(current_user, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username != ADMIN_USERNAME:
            raise JWTError()
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return {"username": username}
