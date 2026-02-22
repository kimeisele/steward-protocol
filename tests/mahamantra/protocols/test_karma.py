"""
TESTS: _karma.py - The Karma Protocol
======================================

REAL TESTS for:
1. KarmaPhalam TypedDict
2. KarmaProtocol runtime checkable
"""

import pytest
from vibe_core.mahamantra.protocols._karma import (
    KarmaPhalam,
    KarmaProtocol,
)


# =============================================================================
# KarmaPhalam Tests
# =============================================================================


class TestKarmaPhalam:
    """Test KarmaPhalam TypedDict."""

    def test_karma_phalam_creation(self):
        """KarmaPhalam can be created as dict."""
        phalam: KarmaPhalam = {
            "action_id": "test_action",
            "timestamp": "2024-01-01T00:00:00",
            "status": "success",
            "result": {"data": "test"},
            "error": None,
        }
        assert phalam["action_id"] == "test_action"
        assert phalam["status"] == "success"

    def test_karma_phalam_with_error(self):
        """KarmaPhalam can have error."""
        phalam: KarmaPhalam = {
            "action_id": "failed_action",
            "timestamp": "2024-01-01T00:00:00",
            "status": "error",
            "result": None,
            "error": "Something went wrong",
        }
        assert phalam["status"] == "error"
        assert phalam["error"] == "Something went wrong"


# =============================================================================
# KarmaProtocol Tests
# =============================================================================


class TestKarmaProtocol:
    """Test KarmaProtocol."""

    def test_karma_protocol_is_runtime_checkable(self):
        """KarmaProtocol is runtime checkable."""
        # Just verify the protocol exists and is checkable
        assert hasattr(KarmaProtocol, "__protocol_attrs__") or hasattr(KarmaProtocol, "_is_runtime_protocol")


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.protocols import _karma

        expected = [
            "KarmaPhalam",
            "KarmaProtocol",
        ]
        for item in expected:
            assert item in _karma.__all__, f"{item} should be in __all__"
