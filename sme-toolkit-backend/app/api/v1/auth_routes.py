from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta

from app.auth import (
    Token,
    UserCredentials,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from app.config import settings
from app.database import get_db
from app.services.demo import seed_demo

auth_router = APIRouter()


@auth_router.post("/token", response_model=Token)
async def login_for_access_token(credentials: UserCredentials):
    """Authenticate a configured account and issue a short-lived session token."""
    user = authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60
    )


@auth_router.post('/demo', response_model=Token)
async def demo_session(db=Depends(get_db)):
    if not settings.debug:
        raise HTTPException(403, 'The sample enterprise is available in local development only.')
    actor = await seed_demo(db)
    return Token(access_token=create_access_token({'sub': actor}, timedelta(hours=2)), expires_in=7200)

@auth_router.get('/me')
async def current_account(username: str = Depends(get_current_user)):
    return {'username': username}


@auth_router.post("/refresh", response_model=Token)
async def refresh_token(credentials: UserCredentials):
    """Refresh an expired token by re-authenticating"""
    return await login_for_access_token(credentials)
