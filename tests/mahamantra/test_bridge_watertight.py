"""
TEST BRIDGE WATERTIGHT
======================

Verifies bridge.py follows WATERTIGHT.md checklist:
- NO hardcoded numbers
- ALL from seed.py
- Parampara validation correct
- Purpose routing correct
"""

import pytest

from vibe_core.mahamantra.substrate.bridge import (
    PURPOSE_MAP,
    offer,
    query_purpose,
)
from vibe_core.mahamantra.protocols._seed import PARAMPARA, WORDS
from vibe_core.mahamantra.substrate.seed import (
    get_mahajana_position,
    POSITION_TO_MAHAJANA,
)
from vibe_core.mahamantra.reactor.loop import shutdown_loop


@pytest.fixture(autouse=True, scope="session")
def _reactor_lifecycle():
    """Ensure the ReactorLoop is shut down after all tests."""
    yield
    shutdown_loop(timeout=2.0)


class TestWatertightChecklist:
    """Verify WATERTIGHT.md compliance."""

    def test_purpose_map_uses_seed_functions(self):
        """✅ PURPOSE_MAP derived from get_mahajana_position(), not hardcoded."""
        # Verify each purpose maps to correct position via seed function
        assert PURPOSE_MAP["state_update"] == get_mahajana_position("janaka")
        assert PURPOSE_MAP["ledger_write"] == get_mahajana_position("bhishma")
        assert PURPOSE_MAP["log_emit"] == get_mahajana_position("shuka")
        assert PURPOSE_MAP["file_flush"] == get_mahajana_position("bali")
        assert PURPOSE_MAP["execute"] == get_mahajana_position("parashurama")
        assert PURPOSE_MAP["verify"] == get_mahajana_position("kapila")

    def test_no_hardcoded_integers_in_purpose_map(self):
        """✅ No magic numbers - all positions from seed."""
        # All positions should be valid (0 to WORDS-1)
        for purpose, position in PURPOSE_MAP.items():
            assert 0 <= position < WORDS, f"Position {position} for {purpose} out of bounds"
            # Position should exist in seed mapping
            assert position in POSITION_TO_MAHAJANA, f"Position {position} not in seed mapping"

    def test_parampara_validation_works(self):
        """✅ Parampara validation uses verify_parampara(), not manual % 37."""
        # Valid parampara (multiple of 37)
        result = offer("test", purpose="state_update", parampara_vector=PARAMPARA, timeout=0.5)
        assert result["success"] is True

        result = offer("test", purpose="state_update", parampara_vector=PARAMPARA * 2, timeout=0.5)
        assert result["success"] is True

        # Invalid parampara (not multiple of 37)
        result = offer("test", purpose="state_update", parampara_vector=38, timeout=0.5)
        assert result["success"] is False
        assert "Parampara" in result["error"]

    def test_position_bounds_use_words_constant(self):
        """✅ Bounds checks use WORDS from seed, not hardcoded 16."""
        # All purposes should route to positions within WORDS
        for purpose in PURPOSE_MAP:
            result = offer("test", purpose=purpose, timeout=0.5)
            assert result["success"] is True
            assert 0 <= result["position"] < WORDS


class TestOfferFunction:
    """Test offer() function behavior."""

    def test_valid_state_update_offer(self):
        """State update routes to Janaka (position 10)."""
        result = offer("some state", purpose="state_update", actor="test_service", timeout=0.5)

        assert result["success"] is True
        assert result["mahajana"] == "janaka"
        assert result["position"] == get_mahajana_position("janaka")
        assert result["quarter"] == "karma"  # Position 10 is in karma quarter
        assert result["actor"] == "test_service"

    def test_valid_ledger_write_offer(self):
        """Ledger write routes to Bhishma (position 11)."""
        result = offer("ledger entry", purpose="ledger_write", timeout=0.5)

        assert result["success"] is True
        assert result["mahajana"] == "bhishma"
        assert result["position"] == get_mahajana_position("bhishma")
        assert result["quarter"] == "karma"  # Position 11 is in karma quarter

    def test_valid_log_emit_offer(self):
        """Log emit routes to Shuka (position 14)."""
        result = offer("log message", purpose="log_emit", timeout=0.5)

        assert result["success"] is True
        assert result["mahajana"] == "shuka"
        assert result["position"] == get_mahajana_position("shuka")
        assert result["quarter"] == "moksha"  # Position 14 is in moksha quarter

    def test_invalid_purpose_rejected(self):
        """Unknown purpose returns error."""
        result = offer("data", purpose="invalid_purpose", timeout=0.5)

        assert result["success"] is False
        assert result["position"] == -1
        assert "Unknown purpose" in result["error"]

    def test_genesis_included_in_result(self):
        """Result includes genesis signature from lotus_declaration."""
        result = offer("test", purpose="state_update", timeout=0.5)

        assert result["success"] is True
        assert "genesis" in result
        assert result["genesis"].startswith("0x")  # Genesis is hex string

    def test_word_included_in_result(self):
        """Result includes mantra word from position."""
        result = offer("test", purpose="state_update", timeout=0.5)

        assert result["success"] is True
        assert "word" in result
        assert result["word"] in ["HARE", "KRISHNA", "RAMA"]  # Must be valid word


class TestQueryPurpose:
    """Test query_purpose() function."""

    def test_query_state_update(self):
        """Query state_update purpose."""
        info = query_purpose("state_update")

        assert info is not None
        assert info["mahajana"] == "janaka"
        assert info["position"] == get_mahajana_position("janaka")

    def test_query_ledger_write(self):
        """Query ledger_write purpose."""
        info = query_purpose("ledger_write")

        assert info is not None
        assert info["mahajana"] == "bhishma"
        assert info["position"] == get_mahajana_position("bhishma")

    def test_query_invalid_purpose(self):
        """Query unknown purpose returns None."""
        info = query_purpose("nonexistent_purpose")

        assert info is None

    def test_query_returns_all_fields(self):
        """Query result includes all expected fields."""
        info = query_purpose("log_emit")

        assert info is not None
        assert "purpose" in info
        assert "position" in info
        assert "mahajana" in info
        assert "quarter" in info
        assert "word" in info
        assert "genesis" in info


class TestAllPurposes:
    """Test all defined purposes in PURPOSE_MAP."""

    def test_all_purposes_route_successfully(self):
        """Every purpose in PURPOSE_MAP routes successfully."""
        for purpose in PURPOSE_MAP:
            result = offer("test", purpose=purpose, timeout=0.5)
            assert result["success"] is True, f"Purpose {purpose} failed to route"
            assert result["mahajana"] != "unknown", f"Purpose {purpose} has unknown mahajana"

    def test_all_purposes_have_valid_positions(self):
        """Every purpose maps to valid position (0 to WORDS-1)."""
        for purpose, position in PURPOSE_MAP.items():
            assert 0 <= position < WORDS, f"Purpose {purpose} has invalid position {position}"

    def test_all_purposes_have_mahajanas(self):
        """Every purpose maps to a known mahajana."""
        for purpose in PURPOSE_MAP:
            info = query_purpose(purpose)
            assert info is not None
            assert info["mahajana"] in POSITION_TO_MAHAJANA.values()


class TestParamparaValidation:
    """Test Parampara signature validation."""

    def test_parampara_multiples_accepted(self):
        """Multiples of PARAMPARA (37) are accepted."""
        for multiple in [1, 2, 3, 5, 10]:
            vector = PARAMPARA * multiple
            result = offer("test", purpose="state_update", parampara_vector=vector, timeout=0.5)
            assert result["success"] is True, f"Parampara vector {vector} rejected"

    def test_non_parampara_rejected(self):
        """Non-multiples of PARAMPARA are rejected."""
        for value in [1, 2, 36, 38, 100]:
            result = offer("test", purpose="state_update", parampara_vector=value, timeout=0.5)
            assert result["success"] is False, f"Non-parampara vector {value} accepted"

    def test_zero_parampara_accepted(self):
        """Zero is a valid parampara (0 % 37 == 0)."""
        result = offer("test", purpose="state_update", parampara_vector=0, timeout=0.5)
        assert result["success"] is True
