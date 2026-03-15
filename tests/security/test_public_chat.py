"""
Public Chat Endpoint Security Tests

Tests for /v1/public-chat endpoint:
- Rate limiting (10 requests per minute per IP)
- Input validation (max 2000 chars)
- No authentication required (intentional)

GAD-000: Operator Inversion - Tests verify the machine works correctly.

Author: Mahamantra Substrate
"""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

fastapi = pytest.importorskip("fastapi", reason="fastapi not installed")
from fastapi import HTTPException

from gateway.api import (
    RATE_LIMIT_MAX,
    RATE_LIMIT_WINDOW,
    PublicChatRequest,
    _check_rate_limit,
    _rate_limit_cache,
    public_chat,
)


class TestPublicChatRateLimiting:
    """Tests for rate limiting on public-chat endpoint."""

    def setup_method(self):
        """Clear rate limit cache before each test."""
        _rate_limit_cache.clear()

    def test_rate_limit_allows_first_request(self):
        """First request from an IP should be allowed."""
        assert _check_rate_limit("192.168.1.1") is True
        print("✅ First request allowed")

    def test_rate_limit_allows_up_to_max(self):
        """Should allow up to RATE_LIMIT_MAX requests."""
        ip = "192.168.1.2"
        for i in range(RATE_LIMIT_MAX):
            assert _check_rate_limit(ip) is True
        print(f"✅ Allowed {RATE_LIMIT_MAX} requests")

    def test_rate_limit_blocks_after_max(self):
        """Should block after RATE_LIMIT_MAX requests."""
        ip = "192.168.1.3"
        # Exhaust the limit
        for _ in range(RATE_LIMIT_MAX):
            _check_rate_limit(ip)
        # Next should be blocked
        assert _check_rate_limit(ip) is False
        print("✅ Blocked after max requests")

    def test_rate_limit_different_ips_independent(self):
        """Different IPs have independent rate limits."""
        ip1 = "192.168.1.4"
        ip2 = "192.168.1.5"

        # Exhaust ip1
        for _ in range(RATE_LIMIT_MAX):
            _check_rate_limit(ip1)

        # ip2 should still be allowed
        assert _check_rate_limit(ip2) is True
        print("✅ Different IPs are independent")

    def test_rate_limit_resets_after_window(self):
        """Rate limit should reset after RATE_LIMIT_WINDOW seconds."""
        ip = "192.168.1.6"

        # Exhaust the limit
        for _ in range(RATE_LIMIT_MAX):
            _check_rate_limit(ip)

        # Verify blocked
        assert _check_rate_limit(ip) is False

        # Simulate time passing
        _rate_limit_cache[ip] = (RATE_LIMIT_MAX, time.time() - RATE_LIMIT_WINDOW - 1)

        # Should be allowed again
        assert _check_rate_limit(ip) is True
        print("✅ Rate limit resets after window")


class TestPublicChatInputValidation:
    """Tests for input validation on public-chat endpoint."""

    def test_message_max_length(self):
        """Message must be <= 2000 characters."""
        # Valid message
        valid = PublicChatRequest(message="Hello Steward")
        assert len(valid.message) <= 2000

        # Max length message
        max_msg = PublicChatRequest(message="x" * 2000)
        assert len(max_msg.message) == 2000

        print("✅ Valid messages accepted")

    def test_message_too_long_rejected(self):
        """Message > 2000 characters should be rejected."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            PublicChatRequest(message="x" * 2001)

        print("✅ Oversized messages rejected")

    def test_empty_message_rejected(self):
        """Empty message should be rejected."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            PublicChatRequest(message="")

        print("✅ Empty messages rejected")


class TestPublicChatEndpoint:
    """Integration tests for the public-chat endpoint."""

    def setup_method(self):
        """Clear rate limit cache before each test."""
        _rate_limit_cache.clear()

    @pytest.mark.asyncio
    async def test_rate_limit_returns_429(self):
        """Should return 429 when rate limited."""
        ip = "10.0.0.1"

        # Create mock request
        mock_request = MagicMock()
        mock_request.client.host = ip

        # Exhaust rate limit
        for _ in range(RATE_LIMIT_MAX):
            _check_rate_limit(ip)

        # Next request should get 429
        body = PublicChatRequest(message="test")

        with pytest.raises(HTTPException) as excinfo:
            await public_chat(mock_request, body)

        assert excinfo.value.status_code == 429
        assert "Rate limit" in excinfo.value.detail
        print("✅ Returns 429 when rate limited")

    @pytest.mark.asyncio
    async def test_service_unavailable_when_provider_none(self):
        """Should return 503 when provider is not initialized."""
        mock_request = MagicMock()
        mock_request.client.host = "10.0.0.2"

        body = PublicChatRequest(message="test")

        with patch("gateway.api.provider", None):
            with pytest.raises(HTTPException) as excinfo:
                await public_chat(mock_request, body)

            assert excinfo.value.status_code == 503
            assert "starting up" in excinfo.value.detail

        print("✅ Returns 503 when provider not ready")

    @pytest.mark.asyncio
    async def test_successful_request(self):
        """Should return success when everything works."""
        mock_request = MagicMock()
        mock_request.client.host = "10.0.0.3"

        body = PublicChatRequest(message="Hello Steward")

        mock_provider = AsyncMock()
        mock_provider.route_and_execute.return_value = {"response": "Hare Krishna"}

        with patch("gateway.api.provider", mock_provider):
            result = await public_chat(mock_request, body)

        assert result["status"] == "success"
        assert result["data"]["response"] == "Hare Krishna"
        mock_provider.route_and_execute.assert_called_once_with("Hello Steward")
        print("✅ Successful request returns data")


class TestPublicChatConstants:
    """Tests for rate limit constants - verify they're sane."""

    def test_rate_limit_window_is_reasonable(self):
        """Rate limit window should be 60 seconds."""
        assert RATE_LIMIT_WINDOW == 60
        print("✅ Rate limit window is 60 seconds")

    def test_rate_limit_max_is_reasonable(self):
        """Rate limit max should be 10 requests."""
        assert RATE_LIMIT_MAX == 10
        print("✅ Rate limit max is 10 requests")

    def test_rate_limit_not_too_restrictive(self):
        """Rate limit should allow reasonable usage."""
        # 10 requests per minute = 1 every 6 seconds = reasonable for chat
        assert RATE_LIMIT_MAX >= 5
        assert RATE_LIMIT_WINDOW <= 120
        print("✅ Rate limits are not too restrictive")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
