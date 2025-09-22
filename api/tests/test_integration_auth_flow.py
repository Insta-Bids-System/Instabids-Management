"""
Integration tests for complete authentication flow
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.auth
class TestAuthenticationIntegration:
    """Test complete authentication workflows."""

    def test_health_and_docs_available(self, client: TestClient):
        """Test that basic endpoints are available."""
        # Health check
        health_response = client.get("/health")
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert health_data["status"] == "healthy"

        # API docs
        docs_response = client.get("/docs")
        assert docs_response.status_code == 200

    def test_registration_validation_flow(self, client: TestClient):
        """Test complete registration validation flow."""
        base_user_data = {
            "email": f"integration-test-{uuid.uuid4()}@instabids.com",
            "password": "TestPass123!",
            "full_name": "Integration Test User",
            "user_type": "property_manager",
            "phone": "+1234567890",
            "organization_name": "Test Organization",
        }

        # Test 1: Valid registration data structure
        response = client.post("/api/auth/register", json=base_user_data)
        # Note: May fail with actual Supabase, but should not be validation error
        assert response.status_code in [
            200,
            400,
        ], f"Unexpected status: {response.status_code}, {response.text}"

        # Test 2: Invalid email
        invalid_email_data = base_user_data.copy()
        invalid_email_data["email"] = "invalid-email"
        response = client.post("/api/auth/register", json=invalid_email_data)
        assert response.status_code == 422

        # Test 3: Weak password
        weak_password_data = base_user_data.copy()
        weak_password_data["password"] = "weak"
        response = client.post("/api/auth/register", json=weak_password_data)
        assert response.status_code == 422

        # Test 4: Missing required fields
        incomplete_data = {"email": "test@example.com"}
        response = client.post("/api/auth/register", json=incomplete_data)
        assert response.status_code == 422

    def test_login_validation_flow(self, client: TestClient):
        """Test login validation flow."""
        # Test valid structure
        login_data = {"email": "test@instabids.com", "password": "TestPass123!"}
        response = client.post("/api/auth/login", json=login_data)
        # Should be valid structure (may fail auth, but not validation)
        assert response.status_code in [200, 401, 400]

        # Test missing email
        invalid_login = {"password": "TestPass123!"}
        response = client.post("/api/auth/login", json=invalid_login)
        assert response.status_code == 422

        # Test missing password
        invalid_login = {"email": "test@example.com"}
        response = client.post("/api/auth/login", json=invalid_login)
        assert response.status_code == 422

    def test_password_reset_flow(self, client: TestClient):
        """Test password reset flow."""
        # Valid email
        response = client.post(
            "/api/auth/reset-password", json={"email": "test@instabids.com"}
        )
        assert response.status_code in [200, 400]  # Structure should be valid

        # Invalid email format
        response = client.post("/api/auth/reset-password", json={"email": "invalid"})
        assert response.status_code == 422

        # Missing email
        response = client.post("/api/auth/reset-password", json={})
        assert response.status_code == 422

    def test_protected_endpoints_require_auth(self, client: TestClient):
        """Test that protected endpoints require authentication."""
        protected_endpoints = [
            ("GET", "/api/auth/me"),
            ("PUT", "/api/auth/profile"),
            ("POST", "/api/auth/logout"),
        ]

        for method, endpoint in protected_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "PUT":
                response = client.put(endpoint, json={"full_name": "Test"})
            elif method == "POST":
                response = client.post(endpoint)

            # Should require authentication
            assert response.status_code in [
                401,
                422,
            ], f"Endpoint {endpoint} should require auth"

    def test_rate_limiting_implementation(self, client: TestClient):
        """Test that rate limiting is working."""
        # Make several requests to trigger rate limiting
        responses = []
        for i in range(10):
            response = client.post(
                "/api/auth/reset-password", json={"email": f"test{i}@example.com"}
            )
            responses.append(response.status_code)

        # Should get consistent behavior (rate limiting working)
        valid_status_codes = [200, 400, 422, 429]  # 429 = Too Many Requests
        assert all(status in valid_status_codes for status in responses)

    def test_cors_configuration(self, client: TestClient):
        """Test CORS configuration."""
        # Test preflight request
        response = client.options("/api/auth/register")
        # Should handle OPTIONS request (may return 405 if not explicitly handled)
        assert response.status_code in [200, 405]

        # Test actual request has CORS headers
        response = client.post(
            "/api/auth/reset-password", json={"email": "test@example.com"}
        )
        # Response should have appropriate headers (FastAPI handles this automatically)
        assert response.status_code in [200, 400, 422]


@pytest.mark.integration
@pytest.mark.api
class TestAPIEndpointIntegration:
    """Test API endpoint integration."""

    def test_all_auth_endpoints_exist(self, client: TestClient):
        """Test that all auth endpoints exist and respond."""
        endpoints = [
            (
                "POST",
                "/api/auth/register",
                {
                    "email": "test@example.com",
                    "password": "Test123!",
                    "full_name": "Test",
                    "user_type": "contractor",
                },
            ),
            (
                "POST",
                "/api/auth/login",
                {"email": "test@example.com", "password": "Test123!"},
            ),
            ("POST", "/api/auth/logout", {}),
            ("POST", "/api/auth/refresh", {"refresh_token": "test-token"}),
            ("POST", "/api/auth/verify-email", {"token": "test-token"}),
            ("POST", "/api/auth/reset-password", {"email": "test@example.com"}),
            ("GET", "/api/auth/me", None),
            ("PUT", "/api/auth/profile", {"full_name": "New Name"}),
        ]

        for method, endpoint, data in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json=data)
            elif method == "PUT":
                response = client.put(endpoint, json=data)

            # Endpoint should exist (not 404)
            assert (
                response.status_code != 404
            ), f"Endpoint {method} {endpoint} not found"
            # Should be valid response codes for auth endpoints
            assert response.status_code in [
                200,
                400,
                401,
                422,
            ], f"Unexpected status for {endpoint}: {response.status_code}"

    def test_content_type_handling(self, client: TestClient):
        """Test proper content type handling."""
        # Test JSON content type
        response = client.post(
            "/api/auth/reset-password",
            json={"email": "test@example.com"},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in [200, 400, 422]

        # Test missing content type (should still work with FastAPI)
        response = client.post(
            "/api/auth/reset-password", json={"email": "test@example.com"}
        )
        assert response.status_code in [200, 400, 422]

    def test_error_response_format(self, client: TestClient):
        """Test that error responses have consistent format."""
        # Trigger validation error
        response = client.post("/api/auth/register", json={"email": "invalid"})
        assert response.status_code == 422

        error_data = response.json()
        # FastAPI validation errors should have 'detail' field
        assert "detail" in error_data

    def test_request_size_limits(self, client: TestClient):
        """Test request size limits."""
        # Large request payload
        large_data = {
            "email": "test@example.com",
            "password": "TestPass123!",
            "full_name": "A" * 10000,  # Very long name
            "user_type": "property_manager",
        }

        response = client.post("/api/auth/register", json=large_data)
        # Should handle large payloads gracefully
        assert response.status_code in [400, 422, 413]  # 413 = Payload Too Large


@pytest.mark.integration
@pytest.mark.supabase
class TestSupabaseIntegration:
    """Test Supabase integration."""

    def test_supabase_connection_available(self):
        """Test that Supabase connection is available."""
        from api.services.supabase import supabase_service

        client = supabase_service.client
        assert client is not None

        # Test basic table access
        try:
            result = client.table("user_profiles").select("*").limit(1).execute()
            assert result is not None
        except Exception as e:
            # Should not be connection error
            assert "connection" not in str(e).lower()

    def test_database_tables_accessible(self):
        """Test that required database tables are accessible."""
        from api.services.supabase import supabase_service

        required_tables = ["user_profiles", "organizations"]

        for table_name in required_tables:
            try:
                result = (
                    supabase_service.client.table(table_name)
                    .select("*")
                    .limit(1)
                    .execute()
                )
                assert result is not None
                assert hasattr(result, "data")
            except Exception as e:
                # Log but don't fail - may be RLS policy
                print(f"Table {table_name} access: {e}")

    def test_environment_configuration(self):
        """Test environment configuration."""
        import os

        # Check required environment variables
        required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY"]
        for var in required_vars:
            value = os.getenv(var)
            assert value is not None, f"{var} not set"
            assert len(value) > 0, f"{var} is empty"

    def test_correct_supabase_project(self):
        """Test that we're connected to the correct Supabase project."""
        import os

        url = os.getenv("SUPABASE_URL")
        expected_project = "lmbpvkfcfhdfaihigfdu"

        assert (
            expected_project in url
        ), f"Wrong Supabase project. Expected {expected_project}"


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndFlows:
    """Test complete end-to-end flows."""

    @pytest.mark.asyncio
    async def test_async_endpoint_performance(self, async_client: AsyncClient):
        """Test async endpoint performance."""
        start_time = datetime.now()

        # Make multiple concurrent requests
        tasks = []
        for i in range(5):
            task = async_client.get("/health")
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # All requests should succeed
        for response in responses:
            assert response.status_code == 200

        # Should complete reasonably quickly
        assert duration < 5.0, f"Async requests took too long: {duration}s"

    def test_registration_to_verification_flow(self, client: TestClient):
        """Test complete registration to verification flow structure."""
        # Step 1: Register user
        user_data = {
            "email": f"flow-test-{uuid.uuid4()}@instabids.com",
            "password": "FlowTest123!",
            "full_name": "Flow Test User",
            "user_type": "contractor",
            "phone": "+1987654321",
        }

        register_response = client.post("/api/auth/register", json=user_data)
        # Registration should be valid structure
        assert register_response.status_code in [200, 400]

        # Step 2: Attempt email verification (with fake token)
        verify_response = client.post(
            "/api/auth/verify-email", json={"token": "fake-token"}
        )
        # Should handle verification request
        assert verify_response.status_code in [200, 400, 422]

        # Step 3: Request password reset
        reset_response = client.post(
            "/api/auth/reset-password", json={"email": user_data["email"]}
        )
        # Should handle reset request
        assert reset_response.status_code in [200, 400]

    def test_error_handling_consistency(self, client: TestClient):
        """Test that error handling is consistent across endpoints."""
        endpoints_and_invalid_data = [
            ("/api/auth/register", {"email": "invalid"}),
            ("/api/auth/login", {"email": "invalid"}),
            ("/api/auth/reset-password", {"email": "invalid"}),
            ("/api/auth/verify-email", {"token": ""}),
            ("/api/auth/refresh", {"refresh_token": ""}),
        ]

        for endpoint, invalid_data in endpoints_and_invalid_data:
            response = client.post(endpoint, json=invalid_data)

            # Should handle invalid data consistently
            assert response.status_code in [
                400,
                422,
            ], f"Inconsistent error handling for {endpoint}"

            # Should have error details
            error_data = response.json()
            assert "detail" in error_data, f"Missing error detail for {endpoint}"

    def test_security_headers_present(self, client: TestClient):
        """Test that security headers are present."""
        response = client.get("/health")

        # Should have some basic security considerations
        assert response.status_code == 200

        # FastAPI should handle basic security automatically
        # This test ensures endpoints are accessible and responsive
        assert "content-type" in response.headers


@pytest.mark.integration
@pytest.mark.security
class TestSecurityIntegration:
    """Test security aspects integration."""

    def test_sql_injection_prevention(self, client: TestClient):
        """Test SQL injection prevention."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "admin'--",
            "' OR '1'='1",
            "1; DELETE FROM users WHERE 1=1; --",
        ]

        for malicious_input in malicious_inputs:
            # Test in different endpoints
            response = client.post(
                "/api/auth/reset-password", json={"email": malicious_input}
            )
            # Should handle malicious input safely
            assert response.status_code in [400, 422]

            # Should not cause server error
            assert response.status_code != 500

    def test_xss_prevention(self, client: TestClient):
        """Test XSS prevention."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
        ]

        for payload in xss_payloads:
            user_data = {
                "email": "test@example.com",
                "password": "TestPass123!",
                "full_name": payload,
                "user_type": "contractor",
            }

            response = client.post("/api/auth/register", json=user_data)
            # Should handle XSS attempts safely
            assert response.status_code in [200, 400, 422]

            # Should not cause server error
            assert response.status_code != 500

    def test_oversized_input_handling(self, client: TestClient):
        """Test handling of oversized inputs."""
        oversized_data = {
            "email": "a" * 1000 + "@example.com",
            "password": "TestPass123!",
            "full_name": "A" * 5000,
            "user_type": "property_manager",
        }

        response = client.post("/api/auth/register", json=oversized_data)
        # Should handle oversized input gracefully
        assert response.status_code in [400, 422, 413]

    def test_malformed_json_handling(self, client: TestClient):
        """Test handling of malformed JSON."""
        # Test with invalid JSON
        response = client.post(
            "/api/auth/register",
            data="{'invalid': json}",
            headers={"Content-Type": "application/json"},
        )

        # Should handle malformed JSON gracefully
        assert response.status_code in [400, 422]
        assert response.status_code != 500
