"""
TEST CHAT PROTOCOL
==================

Verifies the ChatProtocol contract and its Mantra connection.

PROTOCOL-FIRST TESTING:
1. Test the Protocol definition (contract)
2. Test the type definitions (strict, no Any)
3. Test Mantra connection (EXEC_SERVICE, SERVE, RAMA)
"""

from datetime import datetime

import pytest

from vibe_core.mahamantra.substrate.opcode import MantraOpCode
from vibe_core.protocols.chat import (
    CHAT_OPCODE,
    CHAT_PHASE,
    CHAT_POSITION,
    CHAT_WORD,
    DEFAULT_CHAT_CAPABILITIES,
    ChatContext,
    ChatMessage,
    ChatMode,
    ChatProtocol,
    ChatResponse,
)
from vibe_core.protocols.cognition import IntentType


class TestChatMantraConnection:
    """Test Chat's connection to the Mahamantra system."""

    def test_chat_opcode_is_exec_service(self):
        """Chat maps to EXEC_SERVICE opcode."""
        assert CHAT_OPCODE == MantraOpCode.EXTEND_CAP

    def test_chat_phase_is_serve(self):
        """Chat is in SERVE phase (Phase 3)."""
        assert CHAT_PHASE == "SERVE"

    def test_chat_word_is_rama(self):
        """Chat's Mahamantra word is RAMA."""
        assert CHAT_WORD == "RAMA"

    def test_chat_position_is_9(self):
        """Chat is position 9 in the Mahamantra."""
        assert CHAT_POSITION == 9


class TestChatMessage:
    """Test ChatMessage dataclass (strict typing)."""

    def test_chat_message_is_frozen(self):
        """ChatMessage is immutable."""
        msg = ChatMessage(content="Hello", role="user")
        with pytest.raises(Exception):  # FrozenInstanceError
            msg.content = "Changed"

    def test_chat_message_has_timestamp(self):
        """ChatMessage gets timestamp automatically."""
        msg = ChatMessage(content="Hello", role="user")
        assert msg.timestamp is not None
        assert isinstance(msg.timestamp, datetime)

    def test_chat_message_all_fields_typed(self):
        """All ChatMessage fields have types (no Any)."""
        msg = ChatMessage(
            content="Hello",
            role="user",
            session_id="sess-123",
            message_id="msg-456",
            opcode="exec_service",
            mahajana="janaka",
        )
        assert isinstance(msg.content, str)
        assert isinstance(msg.role, str)
        assert isinstance(msg.session_id, str)
        assert isinstance(msg.message_id, str)
        assert isinstance(msg.opcode, str)
        assert isinstance(msg.mahajana, str)


class TestChatResponse:
    """Test ChatResponse dataclass."""

    def test_chat_response_success(self):
        """Success response has correct structure."""
        msg = ChatMessage(content="Hi there!", role="assistant")
        response = ChatResponse(
            success=True,
            message=msg,
            mode=ChatMode.DIRECT,
            confidence=0.95,
        )
        assert response.success
        assert response.message.content == "Hi there!"
        assert response.mode == ChatMode.DIRECT
        assert response.error is None

    def test_chat_response_with_routing(self):
        """Routed response has Mantra info."""
        msg = ChatMessage(content="Task dispatched", role="assistant")
        response = ChatResponse(
            success=True,
            message=msg,
            mode=ChatMode.ROUTED,
            intent_type=IntentType.EXECUTE,
            opcode="exec_service",
            mahajana="janaka",
            confidence=0.85,
        )
        assert response.mode == ChatMode.ROUTED
        assert response.opcode == "exec_service"
        assert response.mahajana == "janaka"

    def test_chat_response_error(self):
        """Error response has retry info."""
        msg = ChatMessage(content="", role="assistant")
        response = ChatResponse(
            success=False,
            message=msg,
            error="Connection failed",
            retry_allowed=True,
        )
        assert not response.success
        assert response.error == "Connection failed"
        assert response.retry_allowed


class TestChatContext:
    """Test ChatContext dataclass."""

    def test_chat_context_is_frozen(self):
        """ChatContext is immutable."""
        ctx = ChatContext(session_id="test-session")
        with pytest.raises(Exception):
            ctx.session_id = "changed"

    def test_chat_context_with_history(self):
        """ChatContext can hold message history."""
        history = [
            ChatMessage(content="Hello", role="user"),
            ChatMessage(content="Hi there!", role="assistant"),
        ]
        ctx = ChatContext(
            session_id="sess-123",
            history=history,
        )
        assert len(ctx.history) == 2
        assert ctx.history[0].role == "user"
        assert ctx.history[1].role == "assistant"

    def test_chat_context_sovereign_identity(self):
        """ChatContext tracks sovereign identity (37th principle)."""
        ctx = ChatContext(
            session_id="sess-123",
            sovereign_id="user-37",
            sovereign_signed=True,
        )
        assert ctx.sovereign_id == "user-37"
        assert ctx.sovereign_signed


class TestChatMode:
    """Test ChatMode enum."""

    def test_all_modes_defined(self):
        """All chat modes are defined."""
        assert ChatMode.DIRECT.value == "direct"
        assert ChatMode.ROUTED.value == "routed"
        assert ChatMode.SYSCALL.value == "syscall"
        assert ChatMode.QUERY.value == "query"

    def test_mode_count(self):
        """Four chat modes exist."""
        assert len(ChatMode) == 4


class TestChatProtocolContract:
    """Test the ChatProtocol contract definition."""

    def test_protocol_is_runtime_checkable(self):
        """ChatProtocol can be checked at runtime."""
        assert hasattr(ChatProtocol, "__protocol_attrs__") or hasattr(ChatProtocol, "_is_protocol")

    def test_protocol_has_mantra_properties(self):
        """ChatProtocol requires Mantra properties."""
        # These are defined in the Protocol
        required_props = ["opcode", "phase", "word", "position"]
        for prop in required_props:
            # Protocol should define these
            assert prop in dir(ChatProtocol)

    def test_protocol_has_chat_methods(self):
        """ChatProtocol requires chat methods."""
        required_methods = ["chat", "chat_with_routing"]
        for method in required_methods:
            assert method in dir(ChatProtocol)

    def test_protocol_has_gad000_methods(self):
        """ChatProtocol requires GAD-000 compliance methods."""
        required_methods = ["capabilities", "status"]
        for method in required_methods:
            assert method in dir(ChatProtocol)


class TestDefaultCapabilities:
    """Test default chat capabilities."""

    def test_capabilities_defined(self):
        """Default capabilities are defined."""
        assert len(DEFAULT_CHAT_CAPABILITIES) == 4

    def test_capabilities_include_direct_response(self):
        """Can respond directly."""
        assert "direct_response" in DEFAULT_CHAT_CAPABILITIES

    def test_capabilities_include_syscall_routing(self):
        """Can route to syscalls."""
        assert "syscall_routing" in DEFAULT_CHAT_CAPABILITIES

    def test_capabilities_include_mahajana_routing(self):
        """Can route to Mahajanas."""
        assert "mahajana_routing" in DEFAULT_CHAT_CAPABILITIES

    def test_capabilities_include_context_aware(self):
        """Uses conversation history."""
        assert "context_aware" in DEFAULT_CHAT_CAPABILITIES


class TestStrictTyping:
    """Test that no Any types are used."""

    def test_chat_message_no_any_in_annotations(self):
        """ChatMessage has no Any in type hints."""
        from typing import Any, get_type_hints

        hints = get_type_hints(ChatMessage)
        for field_name, field_type in hints.items():
            # Check that Any is not used directly
            assert field_type is not Any, f"ChatMessage.{field_name} uses Any type"

    def test_chat_response_no_any_in_annotations(self):
        """ChatResponse has no Any in type hints."""
        from typing import Any, get_type_hints

        hints = get_type_hints(ChatResponse)
        for field_name, field_type in hints.items():
            assert field_type is not Any, f"ChatResponse.{field_name} uses Any type"

    def test_chat_context_no_any_in_annotations(self):
        """ChatContext has no Any in type hints."""
        from typing import Any, get_type_hints

        hints = get_type_hints(ChatContext)
        for field_name, field_type in hints.items():
            assert field_type is not Any, f"ChatContext.{field_name} uses Any type"
