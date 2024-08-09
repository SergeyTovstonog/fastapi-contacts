from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from src.contacts.models import Contact


@pytest.mark.asyncio
async def test_create_contac(test_user, auth_headers, override_get_db, monkeypatch):
    mock_cache = AsyncMock()
    monkeypatch.setattr("src.contacts.routers.invalidate_contacts_cache", mock_cache)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:

        response = await ac.post(
            "/contacts/",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone_number": "123456789",
                "birthday": "1990-01-01",
                "additional_info": "Some info",
            },
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"


@pytest.mark.asyncio
async def test_get_contact(
    override_get_db, test_user_contact: Contact, auth_headers, monkeypatch
):
    mock_cache = AsyncMock()
    monkeypatch.setattr("src.contacts.routers.invalidate_contacts_cache", mock_cache)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:

        # Then, retrieve the contact by ID
        response = await ac.get(
            f"/contacts/{test_user_contact.id}", headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == test_user_contact.first_name
    assert data["last_name"] == test_user_contact.last_name
