from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(hashed_password: str, password: str) -> bool:
    return pwd_context.verify(password, hashed_password)
