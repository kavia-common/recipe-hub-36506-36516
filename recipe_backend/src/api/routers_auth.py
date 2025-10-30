from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.core.security import (
    create_access_token,
    decode_token,
    get_password_hash,
    oauth2_scheme,
    verify_password,
)
from src.db.models import User
from src.db.schemas import User as UserSchema, UserCreate
from src.db.session import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Type of token")


def _get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def _get_current_user(db: Session, token: str) -> User:
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    email = payload.get("sub")
    user = _get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# PUBLIC_INTERFACE
@router.post(
    "/register",
    response_model=UserSchema,
    summary="Register new user",
    description="Create a new user account using email and password.",
)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> UserSchema:
    """
    Register a user.

    Parameters:
        user_in: UserCreate with email, password, and optional full_name.
        db: Database session dependency.
    Returns:
        The created user.
    """
    existing = _get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed = get_password_hash(user_in.password)
    user = User(email=user_in.email, hashed_password=hashed, full_name=user_in.full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# PUBLIC_INTERFACE
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Authenticate with email and password to receive an access token.",
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> TokenResponse:
    """
    Login to obtain JWT token.

    Parameters:
        form_data: OAuth2PasswordRequestForm containing username (email) and password.
        db: Database session.
    Returns:
        TokenResponse with access token.
    """
    # OAuth2PasswordRequestForm uses "username" field which we treat as email
    user = _get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")

    token = create_access_token(subject=user.email)
    return TokenResponse(access_token=token, token_type="bearer")


# PUBLIC_INTERFACE
@router.get(
    "/me",
    response_model=UserSchema,
    summary="Get current user",
    description="Return the currently authenticated user's profile.",
)
def me(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> UserSchema:
    """
    Retrieve the current authenticated user.
    """
    return _get_current_user(db, token)
