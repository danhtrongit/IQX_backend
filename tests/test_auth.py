"""Authentication tests."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Test successful user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@test.com",
            "password": "Password123",
            "fullname": "New User",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "tokens" in data
    assert data["user"]["email"] == "newuser@test.com"
    assert data["user"]["role"] == "USER"
    assert "access_token" in data["tokens"]
    assert "refresh_token" in data["tokens"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with duplicate email."""
    # First registration
    await client.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@test.com", "password": "Password123"},
    )
    
    # Second registration with same email
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@test.com", "password": "Password456"},
    )
    
    assert response.status_code == 409
    assert "already exists" in response.json()["error"]["message"]


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    """Test registration with weak password."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "weak@test.com", "password": "weak"},
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login."""
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@test.com", "password": "Password123"},
    )
    
    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@test.com", "password": "Password123"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "tokens" in data
    assert data["user"]["email"] == "login@test.com"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@test.com", "password": "wrong"},
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    """Test token refresh."""
    # Register and get tokens
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "refresh@test.com", "password": "Password123"},
    )
    refresh_token = register_response.json()["tokens"]["refresh_token"]
    
    # Refresh
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    """Test get current user profile."""
    # Register and get token
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "me@test.com", "password": "Password123"},
    )
    access_token = register_response.json()["tokens"]["access_token"]
    
    # Get profile
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    
    assert response.status_code == 200
    assert response.json()["email"] == "me@test.com"


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    """Test logout."""
    # Register and get tokens
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "logout@test.com", "password": "Password123"},
    )
    tokens = register_response.json()["tokens"]
    
    # Logout
    response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={"refresh_token": tokens["refresh_token"]},
    )
    
    assert response.status_code == 200
    assert "success" in response.json()["message"].lower()



