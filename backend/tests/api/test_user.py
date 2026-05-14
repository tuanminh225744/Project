import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_user(client: AsyncClient):
    # First, register a user
    await client.post("/auth/register", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    })

    # Then, retrieve the user
    response = await client.get("/users/1")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_users(client: AsyncClient):
    # First, register a user
    await client.post("/auth/register", json={
        "username": "testuser2",
        "email": "testuser2@example.com",
        "password": "testpassword"
    })

    # Then, retrieve the users
    response = await client.get("/users/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_user(client: AsyncClient):
    # First, register a user
    await client.post("/auth/register", json={
        "username": "testuser3",
        "email": "testuser3@example.com",
        "password": "testpassword"
    })

    # Then, login to get the access token

    response = await client.post("/auth/login", data={
        "username": "testuser3",
        "password": "testpassword"
    })
    access_token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}


    # Then, update the user
    response = await client.put("/users/3", json={
        "username": "updateduser3",
        "email": "updateduser3@example.com"
    }, headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient):
    # First, register a user
    await client.post("/auth/register", json={
        "username": "testuser4",
        "email": "testuser4@example.com",
        "password": "testpassword"
    })

    # Then, login to get the access token
    response = await client.post("/auth/login", data={
        "username": "testuser4",
        "password": "testpassword"
    })
    access_token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}

    # Then, delete the user
    response = await client.delete("/users/4", headers=headers)
    # Admin is required to delete users, so this should return 403 Forbidden
    assert response.status_code == 403
