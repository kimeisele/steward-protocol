"""Tests for the explicit public intent bridge."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from gateway.api import PublicIntentRequest, _rate_limit_cache, public_intent_status, public_intents


class TestPublicIntentBridge:
    def setup_method(self):
        _rate_limit_cache.clear()

    @pytest.mark.asyncio
    async def test_public_intent_bridge_requires_configuration(self):
        request = MagicMock()
        request.client.host = "10.0.0.10"
        body = PublicIntentRequest(intent_type="request_fork", title="Fork city")

        with patch(
            "gateway.api.os.getenv",
            side_effect=lambda key, default=None: {
                "AGENT_INTERNET_LOTUS_BASE_URL": "",
                "AGENT_INTERNET_LOTUS_TOKEN": "",
            }.get(key, default),
        ):
            with pytest.raises(HTTPException) as excinfo:
                await public_intents(request, body)

        assert excinfo.value.status_code == 503
        assert "not configured" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_public_intent_bridge_forwards_explicit_typed_request(self):
        request = MagicMock()
        request.client.host = "10.0.0.11"
        body = PublicIntentRequest(
            intent_type="request_slot",
            title="Need social slot",
            description="Please create a social slot for the assistant.",
            space_id="space:city-a:moltbook_assistant",
            requested_by_handle="ss",
            labels={"source": "test"},
        )

        class _FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return b'{"intent":{"intent_id":"intent:slot-1","status":"pending"}}'

        getenv_values = {
            "AGENT_INTERNET_LOTUS_BASE_URL": "http://agent-internet.local",
            "AGENT_INTERNET_LOTUS_TOKEN": "bridge-token",
            "AGENT_INTERNET_LOTUS_TIMEOUT_S": "5.0",
        }

        with patch("gateway.api.os.getenv", side_effect=lambda key, default=None: getenv_values.get(key, default)):
            with patch("gateway.api.urlopen", return_value=_FakeResponse()) as mocked_urlopen:
                result = await public_intents(request, body)

        assert result["status"] == "success"
        assert result["data"]["intent"]["intent_id"] == "intent:slot-1"
        forwarded_request = mocked_urlopen.call_args.args[0]
        assert forwarded_request.full_url == "http://agent-internet.local/v1/lotus/intents"
        assert forwarded_request.headers["Authorization"] == "Bearer bridge-token"
        payload = forwarded_request.data.decode("utf-8")
        assert '"intent_type": "request_slot"' in payload
        assert '"requested_by_handle": "ss"' in payload
        assert '"channel": "public_edge"' in payload

    @pytest.mark.asyncio
    async def test_public_intent_bridge_rate_limits_like_public_chat(self):
        request = MagicMock()
        request.client.host = "10.0.0.12"
        body = PublicIntentRequest(intent_type="request_issue", title="Need issue")

        _rate_limit_cache[request.client.host] = (10, __import__("time").time())

        with pytest.raises(HTTPException) as excinfo:
            await public_intents(request, body)

        assert excinfo.value.status_code == 429

    @pytest.mark.asyncio
    async def test_public_intent_status_bridge_reads_single_intent(self):
        request = MagicMock()
        request.client.host = "10.0.0.13"

        class _FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return b'{"intent":{"intent_id":"intent:slot-1","status":"accepted"}}'

        getenv_values = {
            "AGENT_INTERNET_LOTUS_BASE_URL": "http://agent-internet.local",
            "AGENT_INTERNET_LOTUS_TOKEN": "bridge-token",
            "AGENT_INTERNET_LOTUS_TIMEOUT_S": "5.0",
        }

        with patch("gateway.api.os.getenv", side_effect=lambda key, default=None: getenv_values.get(key, default)):
            with patch("gateway.api.urlopen", return_value=_FakeResponse()) as mocked_urlopen:
                result = await public_intent_status("intent:slot-1", request)

        assert result["status"] == "success"
        assert result["data"]["intent"]["status"] == "accepted"
        forwarded_request = mocked_urlopen.call_args.args[0]
        assert forwarded_request.full_url == "http://agent-internet.local/v1/lotus/intents/intent%3Aslot-1"
