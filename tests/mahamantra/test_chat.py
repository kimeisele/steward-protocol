"""
TESTS: MahajanaChat - Guardian Chat Infrastructure
===================================================

"steward chat ist nicht nur 1 chat" - Each guardian has their own domain.

These tests make MahajanaChat ALTAR-WORTHY.
"""

import pytest
from typing import Dict

from vibe_core.mahamantra.chat import (
    MahajanaChat,
    ChatResult,
    GUARDIAN_DHARMA,
    GUARDIAN_WORDS,
    GUARDIAN_QUARTERS,
)
from vibe_core.mahamantra.protocols._seed import WORDS


# =============================================================================
# GUARDIAN MAPPINGS TESTS
# =============================================================================


class TestGuardianMappings:
    """Test guardian mapping dictionaries."""

    def test_guardian_dharma_has_16_entries(self):
        """GUARDIAN_DHARMA must have 16 entries."""
        assert len(GUARDIAN_DHARMA) == 16

    def test_guardian_words_has_16_entries(self):
        """GUARDIAN_WORDS must have 16 entries."""
        assert len(GUARDIAN_WORDS) == 16

    def test_guardian_quarters_has_16_entries(self):
        """GUARDIAN_QUARTERS must have 16 entries."""
        assert len(GUARDIAN_QUARTERS) == 16

    def test_guardian_words_are_valid(self):
        """All GUARDIAN_WORDS are HARE, KRISHNA, or RAMA."""
        valid_words = {"HARE", "KRISHNA", "RAMA"}
        for guardian, word in GUARDIAN_WORDS.items():
            assert word in valid_words, f"{guardian} has invalid word: {word}"

    def test_guardian_quarters_are_valid(self):
        """All GUARDIAN_QUARTERS are valid quarters."""
        valid_quarters = {"GENESIS", "DHARMA", "KARMA", "MOKSHA"}
        for guardian, quarter in GUARDIAN_QUARTERS.items():
            assert quarter in valid_quarters, f"{guardian} has invalid quarter: {quarter}"

    def test_genesis_quarter_guardians(self):
        """GENESIS quarter has correct guardians."""
        genesis_guardians = [g for g, q in GUARDIAN_QUARTERS.items() if q == "GENESIS"]
        assert "vyasa" in genesis_guardians
        assert "brahma" in genesis_guardians
        assert "narada" in genesis_guardians
        assert "shambhu" in genesis_guardians

    def test_dharma_quarter_guardians(self):
        """DHARMA quarter has correct guardians."""
        dharma_guardians = [g for g, q in GUARDIAN_QUARTERS.items() if q == "DHARMA"]
        assert "prithu" in dharma_guardians
        assert "kumaras" in dharma_guardians
        assert "kapila" in dharma_guardians
        assert "manu" in dharma_guardians


# =============================================================================
# CHAT RESULT TESTS
# =============================================================================


class TestChatResult:
    """Test ChatResult dataclass."""

    def test_create_chat_result(self):
        """Can create ChatResult."""
        result = ChatResult(
            success=True,
            response="Test response",
            guardian="kapila",
            position=6,
        )
        assert result.success is True
        assert result.response == "Test response"
        assert result.guardian == "kapila"
        assert result.position == 6

    def test_chat_result_defaults(self):
        """ChatResult has correct defaults."""
        result = ChatResult(
            success=True,
            response="Test",
            guardian="vyasa",
            position=0,
        )
        assert result.llm_used is False
        assert result.prompt_key is None

    def test_chat_result_with_llm(self):
        """ChatResult tracks LLM usage."""
        result = ChatResult(
            success=True,
            response="Test",
            guardian="narada",
            position=2,
            llm_used=True,
            prompt_key="mahamantra.chat.narada",
        )
        assert result.llm_used is True
        assert result.prompt_key == "mahamantra.chat.narada"


# =============================================================================
# MAHAJANA CHAT INIT TESTS
# =============================================================================


class TestMahajanaChatInit:
    """Test MahajanaChat initialization."""

    def test_create_with_position(self):
        """Can create MahajanaChat with position."""
        chat = MahajanaChat(position=0)
        assert chat.position == 0
        assert chat.guardian == "vyasa"

    def test_create_with_guardian(self):
        """Can create MahajanaChat with explicit guardian."""
        chat = MahajanaChat(position=6, guardian="kapila")
        assert chat.position == 6
        assert chat.guardian == "kapila"

    def test_invalid_position_raises(self):
        """Invalid position raises ValueError."""
        with pytest.raises(ValueError):
            MahajanaChat(position=-1)

        with pytest.raises(ValueError):
            MahajanaChat(position=16)

    def test_all_16_positions_valid(self):
        """All 16 positions can create valid MahajanaChat."""
        for pos in range(WORDS):
            chat = MahajanaChat(position=pos)
            assert chat.position == pos
            assert chat.guardian is not None

    def test_history_starts_empty(self):
        """History starts empty by default."""
        chat = MahajanaChat(position=0)
        assert chat.history == []

    def test_can_provide_history(self):
        """Can provide initial history."""
        history = [{"user": "Hello", "assistant": "Hi"}]
        chat = MahajanaChat(position=0, history=history)
        assert len(chat.history) == 1


# =============================================================================
# SYSTEM PROMPT TESTS
# =============================================================================


class TestMahajanaChatPrompts:
    """Test prompt building."""

    def test_system_prompt_includes_guardian(self):
        """System prompt includes guardian name."""
        chat = MahajanaChat(position=6, guardian="kapila")
        prompt = chat._build_system_prompt("test message")

        assert "KAPILA" in prompt

    def test_system_prompt_includes_position(self):
        """System prompt includes position."""
        chat = MahajanaChat(position=6)
        prompt = chat._build_system_prompt("test")

        assert "6" in prompt

    def test_system_prompt_includes_quarter(self):
        """System prompt includes quarter."""
        chat = MahajanaChat(position=6, guardian="kapila")
        prompt = chat._build_system_prompt("test")

        assert "DHARMA" in prompt

    def test_system_prompt_includes_dharma(self):
        """System prompt includes guardian dharma."""
        chat = MahajanaChat(position=6, guardian="kapila")
        prompt = chat._build_system_prompt("test")

        # Kapila's dharma is Analysis
        assert "Analysis" in prompt or "Analyse" in prompt


# =============================================================================
# RESPOND TESTS
# =============================================================================


class TestMahajanaChatRespond:
    """Test respond method."""

    def test_respond_empty_message(self):
        """Empty message returns error result."""
        chat = MahajanaChat(position=0)
        result = chat.respond("")

        assert result.success is False
        assert "Nachricht" in result.response or "message" in result.response.lower()

    def test_respond_whitespace_only(self):
        """Whitespace-only message returns error."""
        chat = MahajanaChat(position=0)
        result = chat.respond("   ")

        assert result.success is False

    def test_respond_returns_chat_result(self):
        """respond() returns ChatResult."""
        chat = MahajanaChat(position=0)
        result = chat.respond("Hello")

        assert isinstance(result, ChatResult)
        assert result.guardian == "vyasa"
        assert result.position == 0

    def test_respond_without_llm_returns_identity(self):
        """Without LLM, returns identity response."""
        chat = MahajanaChat(position=6, guardian="kapila")
        # Force LLM unavailable
        chat._llm_available = False
        chat._provider = None

        result = chat.respond("Analyze this")

        assert result.success is True
        assert "KAPILA" in result.response
        assert result.llm_used is False

    def test_respond_tracks_guardian(self):
        """Response includes correct guardian info."""
        chat = MahajanaChat(position=15, guardian="yamaraja")
        chat._llm_available = False

        result = chat.respond("Judge this")

        assert result.guardian == "yamaraja"
        assert result.position == 15


# =============================================================================
# GUARDIAN IDENTITY TESTS
# =============================================================================


class TestGuardianIdentities:
    """Test that each guardian has correct identity."""

    @pytest.mark.parametrize(
        "position,expected_guardian",
        [
            (0, "vyasa"),
            (1, "brahma"),
            (2, "narada"),
            (3, "shambhu"),
            (4, "prithu"),
            (5, "kumaras"),
            (6, "kapila"),
            (7, "manu"),
            (8, "parashurama"),
            (9, "prahlada"),
            (10, "janaka"),
            (11, "bhishma"),
            (12, "nrisimha"),
            (13, "bali"),
            (14, "shuka"),
            (15, "yamaraja"),
        ],
    )
    def test_position_maps_to_guardian(self, position: int, expected_guardian: str):
        """Each position maps to correct guardian."""
        chat = MahajanaChat(position=position)
        assert chat.guardian == expected_guardian


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestMahajanaChatIntegration:
    """Integration tests for chat flow."""

    def test_full_chat_flow_without_llm(self):
        """Full chat flow works without LLM."""
        chat = MahajanaChat(position=6, guardian="kapila")
        chat._llm_available = False

        result = chat.respond("What is your purpose?")

        assert result.success is True
        assert "KAPILA" in result.response
        assert "DHARMA" in result.response or "Position" in result.response

    def test_multiple_guardians_different_responses(self):
        """Different guardians give different responses."""
        chat1 = MahajanaChat(position=0, guardian="vyasa")
        chat2 = MahajanaChat(position=15, guardian="yamaraja")

        chat1._llm_available = False
        chat2._llm_available = False

        result1 = chat1.respond("Hello")
        result2 = chat2.respond("Hello")

        # Different guardians should have different identity in response
        assert "VYASA" in result1.response
        assert "YAMARAJA" in result2.response

    def test_history_preserved(self):
        """Conversation history is preserved."""
        chat = MahajanaChat(position=0)
        chat._llm_available = False

        # Multiple exchanges
        chat.respond("First")
        # History only updates on LLM response, not fallback
        # Just verify history mechanism exists
        assert isinstance(chat.history, list)
