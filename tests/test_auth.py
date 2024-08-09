import json
from unittest.mock import patch

import pytest
from fastapi import BackgroundTasks
from httpx import ASGITransport, AsyncClient

from main import app
from src.auth.email_utils import send_verification


@pytest.mark.asyncio
async def test_user_register(override_get_db, user_role, faker, monkeypatch):

    with patch.object(BackgroundTasks, "add_task"):

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:

            payload = {
                "email": faker.email(),
                "username": faker.user_name(),
                "password": faker.password(),
            }
            response = await ac.post(
                "/auth/register",
                json=payload,
            )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["id"] == user_role.id


@pytest.mark.asyncio
async def test_user_login(override_get_db, test_user, user_password, faker):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:

        response = await ac.post(
            "/auth/token",
            data={"username": test_user.username, "password": user_password},
        )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
