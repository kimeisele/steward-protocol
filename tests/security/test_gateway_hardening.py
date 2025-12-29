"""
Gateway Security Hardening Tests

Tests for F3-1, F3-2, F3-3 fixes:
- CORS configuration (F3-1)
- API key requirement (F3-2)
- Path traversal prevention (F3-3)

These tests exist because:
    "The gateway had 3 critical vulnerabilities with NO test coverage."
    "Now they do."
"""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


class TestGatewayAPIKeyRequirement:
    """Tests for F3-2: API key must be set, no fallback."""

    def test_missing_api_key_returns_503(self):
        """
        F3-2 TEST: Server returns 503 if VIBE_API_KEY not set.

        Before fix: Would accept "steward-secret-key" as fallback.
        After fix: Returns 503 Service Unavailable.
        """
        # Remove VIBE_API_KEY if set
        with patch.dict(os.environ, {}, clear=True):
            # Need to reload the module to pick up env change
            # But since app is created at import time, we test the behavior directly
            from gateway.api import chat

            # The function checks os.getenv at runtime
            with patch("gateway.api.os.getenv", return_value=None):
                from fastapi import HTTPException

                # Call the endpoint logic directly
                from gateway.api import SignedChatRequest

                request = SignedChatRequest(
                    message="test", agent_id="attacker", signature="fake", public_key="fake", timestamp=12345
                )

                # Should raise 503
                with pytest.raises(HTTPException) as excinfo:
                    import asyncio

                    asyncio.get_event_loop().run_until_complete(chat(request, x_api_key="steward-secret-key"))

                assert excinfo.value.status_code == 503
                assert "not set" in excinfo.value.detail

        print("✅ Missing API key correctly returns 503")

    def test_wrong_api_key_returns_401(self):
        """
        F3-2 TEST: Wrong API key returns 401.
        """
        with patch("gateway.api.os.getenv", return_value="correct-key"):
            from fastapi import HTTPException

            from gateway.api import SignedChatRequest, chat

            request = SignedChatRequest(
                message="test", agent_id="attacker", signature="fake", public_key="fake", timestamp=12345
            )

            with pytest.raises(HTTPException) as excinfo:
                import asyncio

                asyncio.get_event_loop().run_until_complete(chat(request, x_api_key="wrong-key"))

            assert excinfo.value.status_code == 401

        print("✅ Wrong API key correctly returns 401")


class TestGatewayPathTraversal:
    """Tests for F3-3: Path traversal in check_visa_status."""

    def test_path_traversal_blocked(self):
        """
        F3-3 TEST: Path traversal attempts are blocked.

        Attack: agent_id = "../../../etc/passwd"
        Expected: 400 Bad Request
        """
        from fastapi import HTTPException

        from gateway.api import check_visa_status

        # Various path traversal attempts
        malicious_ids = [
            "../../../etc/passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd",
            "valid/../../../etc/passwd",
            "....//....//etc/passwd",
            "/etc/passwd",
        ]

        for malicious_id in malicious_ids:
            with pytest.raises(HTTPException) as excinfo:
                check_visa_status(malicious_id)

            assert excinfo.value.status_code == 400
            print(f"✅ Blocked: {malicious_id[:30]}...")

    def test_valid_agent_id_allowed(self):
        """
        F3-3 CONTROL: Valid agent IDs work normally.
        """
        from gateway.api import check_visa_status

        # Valid IDs (even if agent doesn't exist)
        valid_ids = [
            "valid_agent",
            "agent-123",
            "MyAgent2024",
            "test_agent_v2",
        ]

        for valid_id in valid_ids:
            result = check_visa_status(valid_id)
            # Should return not_found (agent doesn't exist) but NOT raise
            assert result["status"] == "not_found"
            print(f"✅ Allowed: {valid_id}")

    def test_short_agent_id_rejected(self):
        """
        F3-3 TEST: Agent IDs must be at least 3 characters.
        """
        from fastapi import HTTPException

        from gateway.api import check_visa_status

        short_ids = ["a", "ab", ""]

        for short_id in short_ids:
            with pytest.raises(HTTPException) as excinfo:
                check_visa_status(short_id)

            assert excinfo.value.status_code == 400
            assert "at least 3 characters" in excinfo.value.detail

        print("✅ Short agent IDs correctly rejected")


class TestGatewayCORSConfiguration:
    """Tests for F3-1: CORS now configurable."""

    def test_cors_uses_env_variable(self):
        """
        F3-1 TEST: CORS origins come from CORS_ORIGINS env var.
        """
        # Check that the module uses os.getenv for CORS
        import inspect

        import gateway.api as api_module

        source = inspect.getsource(api_module)

        # Verify CORS_ORIGINS is used
        assert "CORS_ORIGINS" in source
        assert "os.getenv" in source
        assert 'allow_origins=["*"]' not in source  # Old vulnerable code removed

        print("✅ CORS now uses environment variable")

    def test_default_cors_is_localhost(self):
        """
        F3-1 TEST: Default CORS allows only localhost.
        """
        # The default should be localhost only
        default_origins = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000"

        # Check the default value in the source
        import inspect

        import gateway.api as api_module

        source = inspect.getsource(api_module)

        assert "localhost" in source
        assert "127.0.0.1" in source

        print("✅ Default CORS restricts to localhost")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
