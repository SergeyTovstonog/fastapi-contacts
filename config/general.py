import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str = "secret_key"
    mail_username: str = "test"
    mail_password: str = "test"
    mail_from: str = "admin@23web.com"
    mail_port: int = 1025
    mail_server: str = "localhost"
    redis_url: str  # Add Redis URL

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
