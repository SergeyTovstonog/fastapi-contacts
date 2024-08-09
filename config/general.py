from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    database_test_url: str
    secret_key: str = "secret_key_one"
    mail_username: str = "test"
    mail_password: str = "test"
    mail_from: str = "admin@23web.com"
    mail_port: int = 1025
    mail_server: str = "localhost"
    redis_url: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
