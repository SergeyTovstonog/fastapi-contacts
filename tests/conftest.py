import asyncio
from asyncio import tasks

import pytest
import pytest_asyncio
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config.db import Base, get_db
from config.general import settings
from main import app
from src.auth.models import Role, User
from src.auth.pass_utils import get_password_hash
from src.auth.schemas import RoleEnum
from src.auth.utils import create_access_token, create_refresh_token
from src.contacts.models import Contact

engine = create_async_engine(settings.database_test_url, echo=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the event loop to be used in tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def setup_db():
    async with engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_db):
    async with SessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def user_password(faker):
    return faker.password()


@pytest_asyncio.fixture(scope="function")
async def user_role(db_session):
    role = Role(
        id=1,
        name=RoleEnum.USER.value,
    )
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession, faker, user_password, user_role):
    hashed_password = get_password_hash(user_password)
    new_user = User(
        username=faker.user_name(),
        email=faker.email(),
        is_active=True,
        hashed_password=hashed_password,
        role_id=user_role.id,
    )

    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)  # To get the ID from the database
    return new_user


@pytest_asyncio.fixture(scope="function")
def override_get_db(db_session):
    async def _get_db():
        async with db_session as session:
            yield session

    app.dependency_overrides[get_db] = _get_db

    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def auth_headers(test_user):
    access_token = create_access_token(data={"sub": test_user.username})
    refresh_token = create_refresh_token(data={"sub": test_user.username})
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Refresh-Token": refresh_token,
        "Content-Type": "application/json",
    }
    return headers


@pytest_asyncio.fixture(scope="function")
async def test_user_contact(db_session, test_user: User, faker) -> Contact:
    contact = Contact(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=faker.email(),
        phone_number=faker.phone_number(),
        owner_id=test_user.id,
        birthday=faker.date_of_birth(),
        additional_info=faker.text(),  # Normally optional field with some content. In real-world application, it could be None or empty string.  # noqa: E501
    )
    db_session.add(contact)
    await db_session.commit()
    await db_session.refresh(contact)
    return contact
