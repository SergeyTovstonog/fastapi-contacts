

from fastapi import APIRouter, Depends, HTTPException, status, Security, BackgroundTasks
from fastapi_jwt import JwtAuthorizationCredentials
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from config.db import get_db
from src.auth.email_utils import send_verification
from src.auth.repo import UserRepository
from src.auth.schemas import UserResponse, Token, UserCreate
from src.auth.utils import access_security, refresh_security, create_verification_token, decode_verification_token
from src.auth.pass_utils import verify_password

router = APIRouter()
env = Environment(loader=FileSystemLoader('src/templates'))

@router.post("/register", response_model=UserResponse)
async def register(user_create: UserCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_username(user_create.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already exists")
    user =  await user_repo.create_user(user_create)
    verification_token = create_verification_token(user.email)
    verification_link = f"http://localhost:8000/auth/verify-email?token={verification_token}"

    # Render email template
    template = env.get_template('verification_email.html')
    email_body = template.render(verification_link=verification_link)

    # Send verification email
    background_tasks.add_task(send_verification, user.email, email_body)
    return user


@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    email: str = decode_verification_token(token)
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    await user_repo.activate_user(user)
    return {"msg": "Email verified successfully"}

@router.post("/token", response_model=Token)
async def login_for_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_username(form_data.username)
    if not user or not verify_password(user.hashed_password, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    subject = {"username": user.username, "role": user.role.name}

    # Create new access/refresh tokens pair
    access_token = access_security.create_access_token(subject=subject)
    refresh_token = refresh_security.create_refresh_token(subject=subject)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }



@router.post("/refresh", response_model=Token)
async def refresh_token(
        credentials: JwtAuthorizationCredentials = Security(refresh_security), db: AsyncSession = Depends(get_db)):

    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_username(credentials["username"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    subject = {"username": user.username, "role": user.role.name}
    # Create new access/refresh tokens pair
    access_token = access_security.create_access_token(subject=subject)
    refresh_token = refresh_security.create_refresh_token(subject=subject)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


