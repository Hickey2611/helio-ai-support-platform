
import os
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from pwdlib import PasswordHash
from pydantic import EmailStr, BaseModel, Field as PydanticField
from sqlmodel import SQLModel, Field, Session, select

from app.database import get_session


SECRET_KEY = os.environ["JWT_SECRET"]
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Database table
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str


# Request and response schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = PydanticField(min_length=12, max_length=128)


class UserRead(BaseModel):
    id: int
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def create_access_token(user_id: int) -> str:
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRE_MINUTES
    )

    return jwt.encode(
        {
            "sub": str(user_id),
            "exp": expires,
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session),
) -> User:
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = int(payload["sub"])

    except (
            InvalidTokenError,
            KeyError,
            ValueError,
            TypeError,
    ):
        raise error

    user = session.get(User, user_id)

    if user is None:
        raise error

    return user


@router.post(
    "/register",
    response_model=UserRead,
    status_code=201,
)
def register(
        data: UserCreate,
        session: Session = Depends(get_session),
):
    email = str(data.email).lower()

    existing = session.exec(
        select(User).where(User.email == email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    user = User(
        email=email,
        hashed_password=password_hash.hash(data.password),
    )

    session.add(user)

    try:
        session.commit()
    except Exception:
        session.rollback()
        raise

    session.refresh(user)
    return user


@router.post("/token", response_model=TokenResponse)
def login(
        form: OAuth2PasswordRequestForm = Depends(),
        session: Session = Depends(get_session),
):
    email = form.username.lower()

    user = session.exec(
        select(User).where(User.email == email)
    ).first()

    if not user or not password_hash.verify(
            form.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(user.id)
    )


@router.get("/me", response_model=UserRead)
def current_user_profile(
        user: User = Depends(get_current_user),
):
    return user
