"""
TESTS: bridge.py - The Setu Bandha (Bridge Pattern)
===================================================

"setubandhaṁ samudrasya bhagavān pracakāra ha"

REAL TESTS for:
1. PURPOSE_MAP constant
2. offer() function
3. query_purpose() function
4. OfferResult class
"""

import pytest
from vibe_core.mahamantra.substrate.bridge import (
    PURPOSE_MAP,
    OfferResult,
    offer,
    query_purpose,
)
from vibe_core.mahamantra.reactor.loop import shutdown_loop


@pytest.fixture(autouse=True, scope="session")
def _reactor_lifecycle():
    """Ensure the ReactorLoop is shut down after all tests in this module."""
    yield
    shutdown_loop(timeout=2.0)


# =============================================================================
# PURPOSE_MAP Tests
# =============================================================================


class TestPurposeMap:
    """Test PURPOSE_MAP constant."""

    def test_purpose_map_exists(self):
        """PURPOSE_MAP exists."""
        assert PURPOSE_MAP is not None

    def test_purpose_map_is_dict(self):
        """PURPOSE_MAP is a dict."""
        assert isinstance(PURPOSE_MAP, dict)

    def test_purpose_map_has_state_update(self):
        """PURPOSE_MAP has state_update."""
        assert "state_update" in PURPOSE_MAP

    def test_purpose_map_has_ledger_write(self):
        """PURPOSE_MAP has ledger_write."""
        assert "ledger_write" in PURPOSE_MAP

    def test_purpose_map_has_log_emit(self):
        """PURPOSE_MAP has log_emit."""
        assert "log_emit" in PURPOSE_MAP

    def test_purpose_map_has_file_flush(self):
        """PURPOSE_MAP has file_flush."""
        assert "file_flush" in PURPOSE_MAP

    def test_purpose_map_has_execute(self):
        """PURPOSE_MAP has execute."""
        assert "execute" in PURPOSE_MAP

    def test_purpose_map_has_verify(self):
        """PURPOSE_MAP has verify."""
        assert "verify" in PURPOSE_MAP

    def test_purpose_map_values_are_ints(self):
        """All PURPOSE_MAP values are integers (positions)."""
        for purpose, position in PURPOSE_MAP.items():
            assert isinstance(position, int), f"{purpose} should map to int"

    def test_purpose_map_positions_in_range(self):
        """All positions are in valid range (0-15)."""
        for purpose, position in PURPOSE_MAP.items():
            assert 0 <= position < 16, f"{purpose} position {position} out of range"


# =============================================================================
# OfferResult Tests
# =============================================================================


class TestOfferResult:
    """Test OfferResult class."""

    def test_offer_result_is_dict(self):
        """OfferResult inherits from dict."""
        result = OfferResult(success=True, position=0)
        assert isinstance(result, dict)

    def test_offer_result_key_access(self):
        """OfferResult supports key access."""
        result = OfferResult(success=True, position=5, mahajana="test")
        assert result["success"] is True
        assert result["position"] == 5
        assert result["mahajana"] == "test"


# =============================================================================
# offer() Function Tests
# =============================================================================


class TestOffer:
    """Test offer() function."""

    def test_offer_valid_state_update(self):
        """offer with valid state_update purpose succeeds."""
        result = offer("test content", purpose="state_update", timeout=0.5)
        assert result["success"] is True
        assert "position" in result
        assert "mahajana" in result

    def test_offer_valid_ledger_write(self):
        """offer with valid ledger_write purpose succeeds."""
        result = offer("ledger entry", purpose="ledger_write", timeout=0.5)
        assert result["success"] is True

    def test_offer_valid_log_emit(self):
        """offer with valid log_emit purpose succeeds."""
        result = offer("log message", purpose="log_emit", timeout=0.5)
        assert result["success"] is True

    def test_offer_valid_file_flush(self):
        """offer with valid file_flush purpose succeeds."""
        result = offer("file content", purpose="file_flush", timeout=0.5)
        assert result["success"] is True

    def test_offer_unknown_purpose_fails(self):
        """offer with unknown purpose fails."""
        result = offer("content", purpose="unknown_purpose_xyz")
        assert result["success"] is False
        assert "error" in result
        assert result["error"] is not None

    def test_offer_returns_mahajana(self):
        """offer returns mahajana name."""
        result = offer("content", purpose="state_update", timeout=0.5)
        assert result["mahajana"] is not None
        assert isinstance(result["mahajana"], str)

    def test_offer_returns_position(self):
        """offer returns position."""
        result = offer("content", purpose="state_update", timeout=0.5)
        assert "position" in result
        assert isinstance(result["position"], int)

    def test_offer_returns_quarter(self):
        """offer returns quarter."""
        result = offer("content", purpose="state_update", timeout=0.5)
        assert "quarter" in result

    def test_offer_with_actor(self):
        """offer with actor parameter."""
        result = offer("content", purpose="state_update", actor="test_actor", timeout=0.5)
        assert result["success"] is True
        assert result.get("actor") == "test_actor"

    def test_offer_with_valid_parampara_vector(self):
        """offer with valid parampara_vector succeeds."""
        # 37 is divisible by 37
        result = offer("content", purpose="state_update", parampara_vector=37, timeout=0.5)
        assert result["success"] is True

    def test_offer_with_invalid_parampara_vector(self):
        """offer with invalid parampara_vector fails."""
        # 36 is not divisible by 37
        result = offer("content", purpose="state_update", parampara_vector=36)
        assert result["success"] is False
        assert "Parampara validation failed" in result["error"]

    def test_offer_with_dict_content(self):
        """offer accepts dict content."""
        result = offer({"key": "value"}, purpose="state_update", timeout=0.5)
        assert result["success"] is True

    def test_offer_with_bytes_content(self):
        """offer accepts bytes content."""
        result = offer(b"binary content", purpose="file_flush", timeout=0.5)
        assert result["success"] is True


# =============================================================================
# query_purpose() Function Tests
# =============================================================================


class TestQueryPurpose:
    """Test query_purpose() function."""

    def test_query_purpose_state_update(self):
        """query_purpose returns info for state_update."""
        info = query_purpose("state_update")
        assert info is not None
        assert "position" in info
        assert "mahajana" in info

    def test_query_purpose_unknown(self):
        """query_purpose returns None for unknown purpose."""
        info = query_purpose("unknown_purpose_xyz")
        assert info is None

    def test_query_purpose_returns_position(self):
        """query_purpose returns position."""
        info = query_purpose("ledger_write")
        assert isinstance(info["position"], int)

    def test_query_purpose_returns_mahajana(self):
        """query_purpose returns mahajana name."""
        info = query_purpose("log_emit")
        assert isinstance(info["mahajana"], str)

    def test_query_purpose_returns_quarter(self):
        """query_purpose returns quarter."""
        info = query_purpose("execute")
        assert "quarter" in info

    def test_query_purpose_returns_genesis(self):
        """query_purpose returns genesis."""
        info = query_purpose("verify")
        assert "genesis" in info

    def test_query_purpose_all_purposes(self):
        """query_purpose works for all purposes in PURPOSE_MAP."""
        for purpose in PURPOSE_MAP.keys():
            info = query_purpose(purpose)
            assert info is not None, f"query_purpose failed for {purpose}"
            assert info["purpose"] == purpose


# =============================================================================
# Integration Tests
# =============================================================================


class TestBridgeIntegration:
    """Integration tests for bridge module."""

    def test_offer_position_matches_query(self):
        """offer position matches query_purpose position."""
        for purpose in PURPOSE_MAP.keys():
            offer_result = offer("test", purpose=purpose, timeout=0.5)
            query_result = query_purpose(purpose)
            assert offer_result["position"] == query_result["position"]

    def test_offer_mahajana_matches_query(self):
        """offer mahajana matches query_purpose mahajana."""
        for purpose in PURPOSE_MAP.keys():
            offer_result = offer("test", purpose=purpose, timeout=0.5)
            query_result = query_purpose(purpose)
            assert offer_result["mahajana"] == query_result["mahajana"]

    def test_purpose_maps_to_correct_domain(self):
        """Purposes map to correct domain guardians."""
        # State operations should go to janaka (position 10)
        info = query_purpose("state_update")
        assert info["mahajana"] == "janaka"

        # Ledger operations should go to bhishma (position 11)
        info = query_purpose("ledger_write")
        assert info["mahajana"] == "bhishma"

        # Log operations should go to shuka (position 14)
        info = query_purpose("log_emit")
        assert info["mahajana"] == "shuka"


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.substrate import bridge
        assert "offer" in bridge.__all__
        assert "query_purpose" in bridge.__all__
        assert "PURPOSE_MAP" in bridge.__all__
        assert "OfferResult" in bridge.__all__
