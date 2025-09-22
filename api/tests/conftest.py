"""
Test configuration and fixtures for InstaBids Management API tests
"""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Set test environment variables before importing main
os.environ["SUPABASE_URL"] = "https://lmbpvkfcfhdfaihigfdu.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxtYnB2a2ZjZmhkZmFpaGlnZmR1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxMjgzNTIsImV4cCI6MjA3MzcwNDM1Mn0.WH4-iA_FnW1EqGTl-hcpotzqBGgeCutKWBBMaa6Tnmg"
)
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["API_ENV"] = "testing"

from api.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """Create a TestClient for FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async client for testing async endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_user_data():
    """Test user registration data."""
    return {
        "email": "test@instabids.com",
        "password": "TestPass123!",
        "full_name": "Test User",
        "user_type": "property_manager",
        "phone": "+1234567890",
        "organization_name": "Test Organization",
    }


@pytest.fixture
def test_contractor_data():
    """Test contractor registration data."""
    return {
        "email": "contractor@instabids.com",
        "password": "TestPass123!",
        "full_name": "Test Contractor",
        "user_type": "contractor",
        "phone": "+1987654321",
    }


@pytest.fixture
def test_login_data():
    """Test login data."""
    return {"email": "test@instabids.com", "password": "TestPass123!"}


@pytest.fixture
def invalid_user_data():
    """Invalid user data for testing validation."""
    return {
        "email": "invalid-email",
        "password": "weak",
        "full_name": "",
        "user_type": "invalid_type",
    }


@pytest.fixture
def auth_headers():
    """Mock authorization headers."""
    return {"Authorization": "Bearer test-jwt-token"}


class TestConfig:
    """Test configuration constants."""

    TEST_DB_CLEANUP = True
    SUPABASE_TEST_PROJECT = "lmbpvkfcfhdfaihigfdu"
    API_BASE_URL = "http://localhost:8000"
    TIMEOUT_SECONDS = 30
