from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.config import settings
from secrets import compare_digest

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token security
security = HTTPBearer()

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    sub: Optional[str] = None
    exp: Optional[datetime] = None

class UserCredentials(BaseModel):
    username: str
    password: str


# User store — credentials from environment, never hardcoded.
# Set ADMIN_PASSWORD / N8N_PASSWORD in the environment (see .env.example).
# A missing admin password is a startup-time configuration error in production;
# in DEBUG it falls back to a known dev password so local dev still boots.
_DEBUG_FALLBACK_ADMIN = "admin123"
_DEBUG_FALLBACK_N8N = "n8n_webhook_secret"

_ADMIN_PASSWORD = settings.admin_password or (_DEBUG_FALLBACK_ADMIN if settings.debug else '')
_N8N_PASSWORD = settings.n8n_password or (_DEBUG_FALLBACK_N8N if settings.debug else '')

_USERS_DB = {
    "admin": {
        "username": "admin",
        "password": _ADMIN_PASSWORD,
        "disabled": False
    },
    "n8n": {
        "username": "n8n",
        "password": _N8N_PASSWORD,
        "disabled": False
    }
}

if not _ADMIN_PASSWORD or not _N8N_PASSWORD:
    # Fail loudly at import time — a silent empty password would allow
    # authenticate_user("admin", "") to succeed depending on comparison logic.
    raise RuntimeError(
        "Auth configuration error: set ADMIN_PASSWORD and N8N_PASSWORD environment "
        "variables (DEBUG=true allows the legacy dev defaults)."
    )

if not settings.debug and (len(settings.jwt_secret_key) < 32 or settings.jwt_secret_key == 'your-secret-key-change-in-production'):
    raise RuntimeError('Set a strong JWT_SECRET_KEY before running with DEBUG=false.')

# Lazy-initialized hashed passwords cache

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt

def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return TokenData(sub=payload.get("sub"), exp=payload.get("exp"))
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Validate JWT token and return username"""
    token_data = decode_token(credentials.credentials)
    if token_data.sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    if token_data.sub.startswith('demo-'):
        path = request.url.path
        allowed = path == '/auth/me' or any(path == prefix or path.startswith(prefix + '/') for prefix in (
            '/api/v1/owner', '/api/v1/workspace', '/api/v1/sales', '/api/v1/ad-optimization', '/api/v1/workflows', '/api/v1/ads', '/api/v1/bookkeeping', '/api/v1/hr', '/api/v1/billing', '/api/v1/agent-chat', '/api/v1/channels'))
        paid = any(path == prefix or path.startswith(prefix + '/') for prefix in (
            '/api/v1/ads/copy', '/api/v1/ads/image', '/api/v1/ads/video'))
        if not allowed or paid:
            raise HTTPException(403, 'Demo sessions support internal workspace tools only. Paid generation and external actions are disabled.')
    return token_data.sub

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user credentials"""
    user = _USERS_DB.get(username)
    if not user:
        return None
    if not compare_digest(password.encode('utf-8'), user['password'].encode('utf-8')):
        return None
    if user.get("disabled"):
        return None
    return user

async def get_admin_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Return 'admin' if the current user is admin, otherwise raise 403."""
    current_user = await get_current_user(request, credentials)
    if current_user != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


async def require_business_access(request: Request, actor: str = Depends(get_current_user)):
    """Legacy business-ID endpoints must not bypass the owner portal's actor boundary."""
    sources = [dict(request.query_params)]
    if request.method in ('POST', 'PUT', 'PATCH') and request.headers.get('content-type', '').startswith('application/json') and not request.url.path.startswith('/api/v1/ads/'):
        try:
            body = await request.json()
            if isinstance(body, dict):
                sources.append(body)
        except ValueError:
            pass  # Endpoint validation reports malformed input.
    for values in sources:
        if values.get('user_id') is not None and values['user_id'] != actor:
            raise HTTPException(403, 'You can only access your own business data.')
        business_id = values.get('business_profile_id')
        if business_id:
            if not isinstance(business_id, str):
                raise HTTPException(422, 'Invalid business profile ID')
            from app.database import async_session_maker, BusinessProfile
            from sqlalchemy import select
            async with async_session_maker() as db:
                owned = await db.scalar(select(BusinessProfile.id).where(BusinessProfile.id == business_id, BusinessProfile.user_id == actor))
            if not owned:
                raise HTTPException(404, 'Business profile not found')