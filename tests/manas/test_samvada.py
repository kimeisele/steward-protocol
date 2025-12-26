"""
OPUS-042: SAMVADA (The Dialogue) - Tests.

TDD: These tests define the expected behavior BEFORE implementation.

"The dialogue between human and machine must be clear and true."
"""

import asyncio
import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# =============================================================================
# SECTION 1: MESSAGE PROTOCOL TESTS
# =============================================================================


class TestSamvadaMessage:
    """Tests for the message protocol."""

    def test_message_has_type(self):
        """Mutation killer: Message must have a type."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaMessage

        msg = SamvadaMessage(msg_type="chat", content="Hello")
        assert msg.msg_type == "chat"

    def test_message_has_content(self):
        """Mutation killer: Message must have content."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaMessage

        msg = SamvadaMessage(msg_type="chat", content="Hello MANAS")
        assert msg.content == "Hello MANAS"

    def test_message_to_json(self):
        """Mutation killer: Message must serialize to JSON."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaMessage

        msg = SamvadaMessage(msg_type="chat", content="Test")
        json_str = msg.to_json()
        data = json.loads(json_str)
        assert data["type"] == "chat"
        assert data["content"] == "Test"

    def test_message_from_json(self):
        """Mutation killer: Message must deserialize from JSON."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaMessage

        json_str = '{"type": "chat", "content": "Hello"}'
        msg = SamvadaMessage.from_json(json_str)
        assert msg.msg_type == "chat"
        assert msg.content == "Hello"

    def test_message_has_id(self):
        """Mutation killer: Message must have unique ID."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaMessage

        msg1 = SamvadaMessage(msg_type="chat", content="1")
        msg2 = SamvadaMessage(msg_type="chat", content="2")
        assert msg1.msg_id != msg2.msg_id


class TestSamvadaResponse:
    """Tests for response messages."""

    def test_response_has_success_status(self):
        """Mutation killer: Response must have success status."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaResponse

        resp = SamvadaResponse(success=True, content="OK")
        assert resp.success is True

    def test_response_has_content(self):
        """Mutation killer: Response must have content."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaResponse

        resp = SamvadaResponse(success=True, content="MANAS says hello")
        assert resp.content == "MANAS says hello"

    def test_response_can_have_error(self):
        """Mutation killer: Failed response must have error."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaResponse

        resp = SamvadaResponse(success=False, content="", error="Connection refused")
        assert resp.success is False
        assert "Connection" in resp.error

    def test_response_to_json(self):
        """Mutation killer: Response must serialize to JSON."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaResponse

        resp = SamvadaResponse(success=True, content="OK")
        json_str = resp.to_json()
        data = json.loads(json_str)
        assert data["success"] is True
        assert data["content"] == "OK"


# =============================================================================
# SECTION 2: LISTENER (THE EAR) TESTS
# =============================================================================


class TestSamvadaListener:
    """Tests for the socket listener."""

    @pytest.fixture
    def socket_path(self, tmp_path):
        """Create temp socket path."""
        return str(tmp_path / "samvada.sock")

    def test_listener_has_socket_path(self, socket_path):
        """Mutation killer: Listener must have configurable socket path."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaListener

        listener = SamvadaListener(socket_path=socket_path)
        assert listener.socket_path == socket_path

    def test_listener_default_socket_path(self, tmp_path):
        """Mutation killer: Listener must have default socket path."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaListener

        with patch.dict(os.environ, {"HOME": str(tmp_path)}):
            listener = SamvadaListener()
            assert ".opus" in listener.socket_path
            assert "samvada" in listener.socket_path

    def test_listener_is_not_running_initially(self, socket_path):
        """Mutation killer: Listener must not be running initially."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaListener

        listener = SamvadaListener(socket_path=socket_path)
        assert listener.is_running is False

    def test_listener_has_message_handler(self, socket_path):
        """Mutation killer: Listener must accept a message handler."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaListener

        handler = MagicMock()
        listener = SamvadaListener(socket_path=socket_path, handler=handler)
        assert listener._handler is not None


@pytest.mark.skip(reason="Unix socket path too long in pytest tmp_path on macOS")
class TestSamvadaListenerAsync:
    """Async tests for the socket listener."""

    @pytest.fixture
    def socket_path(self, tmp_path):
        """Create temp socket path."""
        return str(tmp_path / "samvada.sock")

    @pytest.mark.asyncio
    async def test_listener_start_creates_socket(self, socket_path):
        """Mutation killer: Starting listener creates socket file."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaListener

        listener = SamvadaListener(socket_path=socket_path)

        # Start and stop quickly
        start_task = asyncio.create_task(listener.start())
        await asyncio.sleep(0.1)  # Give it time to create socket

        assert Path(socket_path).exists() or listener.is_running
        await listener.stop()
        start_task.cancel()
        try:
            await start_task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_listener_stop_sets_running_false(self, socket_path):
        """Mutation killer: Stopping listener sets is_running to False."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaListener

        listener = SamvadaListener(socket_path=socket_path)

        start_task = asyncio.create_task(listener.start())
        await asyncio.sleep(0.1)

        await listener.stop()
        assert listener.is_running is False

        start_task.cancel()
        try:
            await start_task
        except asyncio.CancelledError:
            pass


# =============================================================================
# SECTION 3: CLIENT (THE MOUTH) TESTS
# =============================================================================


class TestSamvadaClient:
    """Tests for the client (chat command backend)."""

    @pytest.fixture
    def socket_path(self, tmp_path):
        """Create temp socket path."""
        return str(tmp_path / "samvada.sock")

    def test_client_has_socket_path(self, socket_path):
        """Mutation killer: Client must have socket path."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaClient

        client = SamvadaClient(socket_path=socket_path)
        assert client.socket_path == socket_path

    def test_client_default_timeout(self, socket_path):
        """Mutation killer: Client must have reasonable default timeout."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaClient

        client = SamvadaClient(socket_path=socket_path)
        assert 5 <= client.timeout <= 60  # Reasonable range


@pytest.mark.skip(reason="Unix socket path too long in pytest tmp_path on macOS")
class TestSamvadaClientAsync:
    """Async tests for the client."""

    @pytest.fixture
    def socket_path(self, tmp_path):
        """Create temp socket path."""
        return str(tmp_path / "samvada.sock")

    @pytest.mark.asyncio
    async def test_client_send_returns_response(self, socket_path):
        """Mutation killer: send() must return a SamvadaResponse."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import (
            SamvadaClient,
            SamvadaListener,
            SamvadaResponse,
        )

        # Create a simple echo handler
        async def echo_handler(msg):
            return SamvadaResponse(success=True, content=f"Echo: {msg.content}")

        # Start listener
        listener = SamvadaListener(socket_path=socket_path, handler=echo_handler)
        server_task = asyncio.create_task(listener.start())
        await asyncio.sleep(0.2)

        try:
            # Send message
            client = SamvadaClient(socket_path=socket_path)
            response = await client.send("Hello MANAS")

            assert isinstance(response, SamvadaResponse)
            assert response.success is True
            assert "Echo" in response.content
        finally:
            await listener.stop()
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass

    @pytest.mark.asyncio
    async def test_client_handles_connection_error(self, socket_path):
        """Mutation killer: Client must handle missing server gracefully."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import SamvadaClient, SamvadaResponse

        client = SamvadaClient(socket_path=socket_path, timeout=1)
        response = await client.send("Hello?")

        assert isinstance(response, SamvadaResponse)
        assert response.success is False
        assert response.error is not None


# =============================================================================
# SECTION 4: INTEGRATION TESTS
# =============================================================================


@pytest.mark.skip(reason="Unix socket path too long in pytest tmp_path on macOS")
class TestSamvadaIntegration:
    """Integration tests for the full dialogue flow."""

    @pytest.fixture
    def socket_path(self, tmp_path):
        """Create temp socket path."""
        return str(tmp_path / "samvada.sock")

    @pytest.mark.asyncio
    async def test_full_dialogue_flow(self, socket_path):
        """Integration: Full human -> MANAS -> response flow."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import (
            SamvadaClient,
            SamvadaListener,
            SamvadaResponse,
        )

        messages_received = []

        async def handler(msg):
            messages_received.append(msg)
            return SamvadaResponse(success=True, content=f"MANAS received: {msg.content}")

        listener = SamvadaListener(socket_path=socket_path, handler=handler)
        server_task = asyncio.create_task(listener.start())
        await asyncio.sleep(0.2)

        try:
            client = SamvadaClient(socket_path=socket_path)

            # Send multiple messages
            resp1 = await client.send("Status report")
            resp2 = await client.send("Check CI")

            assert resp1.success is True
            assert resp2.success is True
            assert len(messages_received) == 2
            assert messages_received[0].content == "Status report"
            assert messages_received[1].content == "Check CI"
        finally:
            await listener.stop()
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass

    @pytest.mark.asyncio
    async def test_handler_error_returns_failed_response(self, socket_path):
        """Integration: Handler error results in failed response."""
        from vibe_core.plugins.opus_assistant.manas.cortex.samvada import (
            SamvadaClient,
            SamvadaListener,
        )

        async def failing_handler(msg):
            raise ValueError("Handler failed!")

        listener = SamvadaListener(socket_path=socket_path, handler=failing_handler)
        server_task = asyncio.create_task(listener.start())
        await asyncio.sleep(0.2)

        try:
            client = SamvadaClient(socket_path=socket_path)
            response = await client.send("Trigger error")

            assert response.success is False
            assert "error" in response.error.lower() or "failed" in response.error.lower()
        finally:
            await listener.stop()
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
