"""Tests for the verified/signed intent bridge."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from gateway.api import SignedIntentRequest, SignedIntentStatusRequest, verified_intent_status, verified_intents


class TestVerifiedIntentBridge:
    @pytest.mark.asyncio
    async def test_verified_intent_bridge_requires_valid_api_key(self):
        body = SignedIntentRequest(
            intent_type="request_fork",
            title="Fork city",
            agent_id="agent_ss",
            signature="sig",
            public_key="pem",
            timestamp=123,
        )

        with patch("gateway.api.os.getenv", side_effect=lambda key, default=None: {"VIBE_API_KEY": "correct-key"}.get(key, default)):
            with pytest.raises(HTTPException) as excinfo:
                await verified_intents(body, x_api_key="wrong-key")

        assert excinfo.value.status_code == 401

    @pytest.mark.asyncio
    async def test_verified_intent_bridge_rejects_invalid_signature(self):
        body = SignedIntentRequest(
            intent_type="request_slot",
            title="Need slot",
            agent_id="agent_ss",
            signature="bad-sig",
            public_key="pem",
            timestamp=123,
        )
        verify_result = SimpleNamespace(
            is_valid=False,
            status=__import__("gateway.takshaka_lite", fromlist=["VerifyStatus"]).VerifyStatus.INVALID_SIGNATURE,
            reason="bad sig",
            toxic_patterns=[],
            fingerprint="fp-bad",
        )
        fake_takshaka = MagicMock()
        fake_takshaka.verify_request.return_value = verify_result

        with patch("gateway.api.os.getenv", side_effect=lambda key, default=None: {"VIBE_API_KEY": "correct-key"}.get(key, default)):
            with patch("gateway.api.get_takshaka", return_value=fake_takshaka):
                with pytest.raises(HTTPException) as excinfo:
                    await verified_intents(body, x_api_key="correct-key")

        assert excinfo.value.status_code == 401
        assert "Invalid signature" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_verified_intent_bridge_forwards_verified_metadata(self):
        body = SignedIntentRequest(
            intent_type="request_pr_draft",
            title="Draft PR",
            description="Prepare a draft PR for the line.",
            repo="org/city-b",
            requested_by_handle="ss",
            labels={"source": "verified-test"},
            agent_id="agent_ss",
            signature="sig",
            public_key="pem",
            timestamp=123,
        )
        verify_result = SimpleNamespace(
            is_valid=True,
            status=None,
            reason="",
            toxic_patterns=[],
            fingerprint="fp-verified",
        )
        fake_takshaka = MagicMock()
        fake_takshaka.verify_request.return_value = verify_result

        class _FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return b'{"intent":{"intent_id":"intent:pr-1","status":"pending"}}'

        getenv_values = {
            "VIBE_API_KEY": "correct-key",
            "AGENT_INTERNET_LOTUS_BASE_URL": "http://agent-internet.local",
            "AGENT_INTERNET_VERIFIED_LOTUS_TOKEN": "verified-token",
            "AGENT_INTERNET_LOTUS_TIMEOUT_S": "5.0",
        }

        with patch("gateway.api.os.getenv", side_effect=lambda key, default=None: getenv_values.get(key, default)):
            with patch("gateway.api.get_takshaka", return_value=fake_takshaka):
                with patch("gateway.api.urlopen", return_value=_FakeResponse()) as mocked_urlopen:
                    result = await verified_intents(body, x_api_key="correct-key")

        assert result["status"] == "success"
        assert result["data"]["intent"]["intent_id"] == "intent:pr-1"
        assert result["data"]["verified_agent_id"] == "agent_ss"
        assert result["data"]["verified_fingerprint"] == "fp-verified"
        verify_call = fake_takshaka.verify_request.call_args.kwargs
        assert '"intent_type":"request_pr_draft"' in verify_call["message"]
        assert verify_call["agent_id"] == "agent_ss"
        forwarded_request = mocked_urlopen.call_args.args[0]
        assert forwarded_request.headers["Authorization"] == "Bearer verified-token"
        payload = forwarded_request.data.decode("utf-8")
        assert '"channel": "verified_edge"' in payload
        assert '"verified_agent_id": "agent_ss"' in payload
        assert '"verified_fingerprint": "fp-verified"' in payload
        assert '"requested_by_subject_id": "verified_agent:agent_ss"' in payload

    @pytest.mark.asyncio
    async def test_verified_intent_status_bridge_reads_single_intent(self):
        body = SignedIntentStatusRequest(
            intent_id="intent:pr-1",
            agent_id="agent_ss",
            signature="sig",
            public_key="pem",
            timestamp=123,
        )
        verify_result = SimpleNamespace(
            is_valid=True,
            status=None,
            reason="",
            toxic_patterns=[],
            fingerprint="fp-verified",
        )
        fake_takshaka = MagicMock()
        fake_takshaka.verify_request.return_value = verify_result

        class _FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return b'{"intent":{"intent_id":"intent:pr-1","status":"accepted"}}'

        getenv_values = {
            "VIBE_API_KEY": "correct-key",
            "AGENT_INTERNET_LOTUS_BASE_URL": "http://agent-internet.local",
            "AGENT_INTERNET_VERIFIED_LOTUS_TOKEN": "verified-token",
            "AGENT_INTERNET_LOTUS_TIMEOUT_S": "5.0",
        }

        with patch("gateway.api.os.getenv", side_effect=lambda key, default=None: getenv_values.get(key, default)):
            with patch("gateway.api.get_takshaka", return_value=fake_takshaka):
                with patch("gateway.api.urlopen", return_value=_FakeResponse()) as mocked_urlopen:
                    result = await verified_intent_status(body, x_api_key="correct-key")

        assert result["status"] == "success"
        assert result["data"]["intent"]["status"] == "accepted"
        assert result["data"]["verified_agent_id"] == "agent_ss"
        assert result["data"]["verified_fingerprint"] == "fp-verified"
        verify_call = fake_takshaka.verify_request.call_args.kwargs
        assert verify_call["message"] == '{"intent_id":"intent:pr-1"}'
        forwarded_request = mocked_urlopen.call_args.args[0]
        assert forwarded_request.full_url == "http://agent-internet.local/v1/lotus/intents/intent%3Apr-1"
        assert forwarded_request.headers["Authorization"] == "Bearer verified-token"