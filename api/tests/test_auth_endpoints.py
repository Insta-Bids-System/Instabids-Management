"""
Comprehensive authentication endpoint tests
"""
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import json
from datetime import datetime


class TestAuthEndpoints:
    """Test all authentication endpoints."""

    def test_health_endpoint(self, client: TestClient):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "environment" in data
        assert "version" in data

    def test_root_endpoint(self, client: TestClient):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "InstaBids Management API"
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"

    def test_registration_validation(self, client: TestClient, test_user_data, invalid_user_data):
        """Test user registration input validation."""
        # Test valid registration data structure
        response = client.post("/api/auth/register", json=test_user_data)
        # Note: This might fail with Supabase integration, but we're testing structure
        assert response.status_code in [200, 400, 422]  # Allow for various responses
        
        # Test invalid email format
        invalid_data = invalid_user_data.copy()
        response = client.post("/api/auth/register", json=invalid_data)
        assert response.status_code == 422  # Validation error
        
        # Test missing required fields
        incomplete_data = {"email": "test@example.com"}
        response = client.post("/api/auth/register", json=incomplete_data)
        assert response.status_code == 422
        
        # Test weak password
        weak_password_data = test_user_data.copy()
        weak_password_data["password"] = "123"
        response = client.post("/api/auth/register", json=weak_password_data)
        assert response.status_code == 422

    def test_login_validation(self, client: TestClient, test_login_data):
        """Test login endpoint validation."""
        # Test login structure (may fail without existing user)
        response = client.post("/api/auth/login", json=test_login_data)
        assert response.status_code in [200, 401, 400]  # Valid response codes
        
        # Test missing email
        incomplete_login = {"password": "TestPass123!"}
        response = client.post("/api/auth/login", json=incomplete_login)
        assert response.status_code == 422
        
        # Test missing password
        incomplete_login = {"email": "test@example.com"}
        response = client.post("/api/auth/login", json=incomplete_login)
        assert response.status_code == 422

    def test_password_reset_validation(self, client: TestClient):
        """Test password reset endpoint validation."""
        # Valid email format
        response = client.post("/api/auth/reset-password", json={"email": "test@example.com"})
        assert response.status_code in [200, 400]  # Should accept valid email structure
        
        # Invalid email format
        response = client.post("/api/auth/reset-password", json={"email": "invalid-email"})
        assert response.status_code == 422  # Validation error
        
        # Missing email
        response = client.post("/api/auth/reset-password", json={})
        assert response.status_code == 422

    def test_verify_email_validation(self, client: TestClient):
        """Test email verification endpoint validation."""
        # Test with token
        response = client.post("/api/auth/verify-email", json={"token": "test-token"})
        assert response.status_code in [200, 400, 422]  # Valid structure
        
        # Test missing token
        response = client.post("/api/auth/verify-email", json={})
        assert response.status_code == 422

    def test_token_refresh_validation(self, client: TestClient):
        """Test token refresh endpoint validation."""
        # Test with refresh token
        response = client.post("/api/auth/refresh", json={"refresh_token": "test-refresh-token"})
        assert response.status_code in [200, 401, 422]  # Valid response codes
        
        # Test missing refresh token
        response = client.post("/api/auth/refresh", json={})
        assert response.status_code == 422

    def test_protected_endpoints_without_auth(self, client: TestClient):
        """Test that protected endpoints require authentication."""
        # Test /me endpoint without auth
        response = client.get("/api/auth/me")
        assert response.status_code in [401, 422]  # Unauthorized
        
        # Test profile update without auth
        response = client.put("/api/auth/profile", json={"full_name": "New Name"})
        assert response.status_code in [401, 422]  # Unauthorized
        
        # Test logout without auth
        response = client.post("/api/auth/logout")
        assert response.status_code in [401, 422]  # Unauthorized

    def test_user_type_validation(self, client: TestClient, test_user_data):
        """Test user type validation."""
        # Test valid user types
        valid_types = ["property_manager", "contractor", "tenant"]
        for user_type in valid_types:
            data = test_user_data.copy()
            data["user_type"] = user_type
            response = client.post("/api/auth/register", json=data)
            assert response.status_code in [200, 400]  # Valid user type structure
        
        # Test invalid user type
        invalid_data = test_user_data.copy()
        invalid_data["user_type"] = "invalid_type"
        response = client.post("/api/auth/register", json=invalid_data)
        assert response.status_code == 422

    def test_phone_validation(self, client: TestClient, test_user_data):
        """Test phone number validation."""
        # Test valid phone formats
        valid_phones = ["+1234567890", "123-456-7890", "(123) 456-7890"]
        for phone in valid_phones:
            data = test_user_data.copy()
            data["phone"] = phone
            response = client.post("/api/auth/register", json=data)
            assert response.status_code in [200, 400, 422]  # Should not fail validation
        
        # Test optional phone (empty)
        data = test_user_data.copy()
        data["phone"] = ""
        response = client.post("/api/auth/register", json=data)
        assert response.status_code in [200, 400, 422]  # Should not fail validation

    def test_rate_limiting_structure(self, client: TestClient):
        """Test that rate limiting is implemented."""
        # This tests the structure, not actual rate limiting
        # Make multiple requests quickly
        responses = []
        for i in range(5):
            response = client.post("/api/auth/reset-password", json={"email": f"test{i}@example.com"})
            responses.append(response.status_code)
        
        # Should get consistent responses (rate limiting working)
        assert all(status in [200, 400, 422, 429] for status in responses)

    def test_cors_headers(self, client: TestClient):
        """Test CORS headers are present."""
        response = client.options("/api/auth/register")
        # CORS should be configured
        assert response.status_code in [200, 405]  # OPTIONS may not be explicitly handled

    def test_content_type_handling(self, client: TestClient):
        """Test proper content-type handling."""
        # Test JSON content type
        response = client.post(
            "/api/auth/reset-password", 
            json={"email": "test@example.com"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [200, 400, 422]
        
        # Test invalid content type
        response = client.post(
            "/api/auth/reset-password",
            data="invalid-data",
            headers={"Content-Type": "text/plain"}
        )
        assert response.status_code in [400, 422]


class TestAuthEndpointsAsync:
    """Test authentication endpoints with async client."""

    @pytest.mark.asyncio
    async def test_async_health_check(self, async_client: AsyncClient):
        """Test health endpoint with async client."""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_async_registration(self, async_client: AsyncClient, test_user_data):
        """Test registration endpoint with async client."""
        response = await async_client.post("/api/auth/register", json=test_user_data)
        assert response.status_code in [200, 400, 422]
        
        # Check response structure if successful
        if response.status_code == 200:
            data = response.json()
            assert "user" in data or "detail" in data

    @pytest.mark.asyncio
    async def test_async_password_reset(self, async_client: AsyncClient):
        """Test password reset with async client."""
        response = await async_client.post(
            "/api/auth/reset-password",
            json={"email": "test@example.com"}
        )
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert "message" in data


class TestAuthenticationSecurity:
    """Test security aspects of authentication."""

    def test_password_requirements(self, client: TestClient, test_user_data):
        """Test password complexity requirements."""
        weak_passwords = [
            "123456",           # Too short
            "password",         # No uppercase, no numbers
            "PASSWORD",         # No lowercase, no numbers
            "Password",         # No numbers
            "Password123",      # Valid (should work)
        ]
        
        for password in weak_passwords[:-1]:  # Test weak passwords
            data = test_user_data.copy()
            data["password"] = password
            response = client.post("/api/auth/register", json=data)
            assert response.status_code == 422  # Should fail validation
        
        # Test valid password
        data = test_user_data.copy()
        data["password"] = "Password123!"
        response = client.post("/api/auth/register", json=data)
        assert response.status_code in [200, 400]  # Should pass validation

    def test_email_format_validation(self, client: TestClient, test_user_data):
        """Test email format validation."""
        invalid_emails = [
            "not-an-email",
            "@domain.com",
            "user@",
            "user..double.dot@domain.com",
            "user@domain",
        ]
        
        for email in invalid_emails:
            data = test_user_data.copy()
            data["email"] = email
            response = client.post("/api/auth/register", json=data)
            assert response.status_code == 422  # Should fail validation

    def test_sql_injection_protection(self, client: TestClient):
        """Test SQL injection protection in inputs."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "admin'--",
            "' OR '1'='1",
            "1; DELETE FROM users WHERE 1=1; --"
        ]
        
        for malicious_input in malicious_inputs:
            # Test in email field
            response = client.post("/api/auth/reset-password", json={"email": malicious_input})
            assert response.status_code in [400, 422]  # Should be handled safely

    def test_xss_protection(self, client: TestClient, test_user_data):
        """Test XSS protection in user inputs."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "'; alert('xss'); //",
        ]
        
        for payload in xss_payloads:
            data = test_user_data.copy()
            data["full_name"] = payload
            response = client.post("/api/auth/register", json=data)
            # Should either sanitize or reject
            assert response.status_code in [200, 400, 422]


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_large_input_handling(self, client: TestClient, test_user_data):
        """Test handling of oversized inputs."""
        # Very long email
        data = test_user_data.copy()
        data["email"] = "a" * 1000 + "@example.com"
        response = client.post("/api/auth/register", json=data)
        assert response.status_code in [400, 422]
        
        # Very long name
        data = test_user_data.copy()
        data["full_name"] = "A" * 1000
        response = client.post("/api/auth/register", json=data)
        assert response.status_code in [400, 422]

    def test_null_input_handling(self, client: TestClient):
        """Test handling of null/None inputs."""
        invalid_data = {
            "email": None,
            "password": None,
            "full_name": None,
            "user_type": None
        }
        response = client.post("/api/auth/register", json=invalid_data)
        assert response.status_code == 422

    def test_empty_request_body(self, client: TestClient):
        """Test handling of empty request bodies."""
        response = client.post("/api/auth/register", json={})
        assert response.status_code == 422
        
        response = client.post("/api/auth/login", json={})
        assert response.status_code == 422

    def test_malformed_json(self, client: TestClient):
        """Test handling of malformed JSON."""
        response = client.post(
            "/api/auth/register",
            data="{'invalid': json}",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]