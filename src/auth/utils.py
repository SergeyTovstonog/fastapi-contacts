from datetime import timedelta, datetime, timezone

from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from fastapi_jwt import JwtAccessBearerCookie, JwtRefreshBearer, JwtAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db import get_db
from config.general import settings

from src.auth.models import User
from src.auth.repo import UserRepository
from src.auth.schemas import TokenData, RoleEnum, UserResponse

  # You should store this in .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
VERIFICATION_TOKEN_EXPIRE_HOURS = 24
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def create_verification_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS)
    to_encode = {"exp": expire, "sub": email}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def decode_verification_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None

access_security = JwtAccessBearerCookie(
    secret_key=settings.secret_key,
    auto_error=False,
    access_expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # change access token validation timedelta
)
# Read refresh token from bearer header only
refresh_security = JwtRefreshBearer(
    secret_key=settings.secret_key,
    auto_error=True,  # automatically raise HTTPException: HTTP_401_UNAUTHORIZED
    access_expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
)


class RoleChecker:
    def __init__(self, allowed_roles: list[RoleEnum]):
        self.allowed_roles = allowed_roles

    async def __call__(self, credentials: JwtAuthorizationCredentials = Security(refresh_security), db: AsyncSession = Depends(get_db)) -> User:
        user = await get_current_user(credentials, db)
        if user and user.role.name not in [role.value for role in self.allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )
        return user



async def get_current_user(credentials: JwtAuthorizationCredentials = Security(refresh_security), db: AsyncSession = Depends(get_db)) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        raise credentials_exception
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_username(credentials["username"])
    if user is None:
        raise credentials_exception
    return user
