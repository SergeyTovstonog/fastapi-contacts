import pytest
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.mark.asyncio
async def test_user_register(override_get_db, user_role, faker):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:

        email = faker.email
        response = await ac.post("/auth/register", json={
            "email": "user@email.com",
            "username": "user_name",
            "password": "password"
        })


    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@email.com"
    assert data["id"] == user_role.id

@pytest.mark.asyncio
async def test_user_login(override_get_db, test_user, user_password, faker):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:

        response = await ac.post("/auth/token", data={
            "username": test_user.username,
            "password": user_password
        })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data