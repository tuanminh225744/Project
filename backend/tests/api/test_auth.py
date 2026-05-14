import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_register_user_duplicate_email(client: AsyncClient):
    # First, register a user
    await client.post("/auth/register", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    })

    # Then, try to register the same email again
    response = await client.post("/auth/register", json={
        "username": "testuser2",
        "email": "testuser@example.com",
        "password": "testpassword2"
    })
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_register_user_duplicate_username(client: AsyncClient):
    # First, register a user
    await client.post("/auth/register", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    })

    # Then, try to register the same username again
    response = await client.post("/auth/register", json={
        "username": "testuser",
        "email": "testuser2@example.com",
        "password": "testpassword2"
    })
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    # First, register a user
    await client.post("/auth/register", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    })

    # Then, try to login with the correct credentials
    response = await client.post("/auth/login", data={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_user_invalid_credentials(client: AsyncClient):
    # First, register a user
    await client.post("/auth/register", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    })

    # Then, try to login with invalid credentials
    response = await client.post("/auth/login", data={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    # First, register a user
    await client.post("/auth/register", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    })

    # Then, try to login with the correct credentials
    response = await client.post("/auth/login", data={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    refresh_token = data["refresh_token"]

    # Now, try to refresh the token
    response = await client.post("/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_refresh_token_invalid_token(client: AsyncClient):
    # Try to refresh with an invalid token
    response = await client.post("/auth/refresh", json={
        "refresh_token": "invalidtoken"
    })
    assert response.status_code == 401