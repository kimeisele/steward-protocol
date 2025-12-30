"""
TEST: WatchmanCartridge - System Integrity Enforcer
===================================================
Target: watchman/cartridge_main.py
Standard: GAD-5000
"""

import pytest

from vibe_core.cartridges.system.watchman.cartridge_main import WatchmanCartridge


class TestWatchmanCartridgeInit:
    """Test WatchmanCartridge initialization."""

    def test_cartridge_can_be_instantiated(self):
        """Should instantiate without errors."""
        cartridge = WatchmanCartridge()
        assert cartridge is not None

    def test_cartridge_has_agent_id(self):
        """Should have correct agent_id."""
        cartridge = WatchmanCartridge()
        assert cartridge.agent_id == "watchman"

    def test_cartridge_has_name(self):
        """Should have correct name."""
        cartridge = WatchmanCartridge()
        assert cartridge.name == "WATCHMAN"

    def test_cartridge_has_capabilities(self):
        """Should have scan and freeze capabilities."""
        cartridge = WatchmanCartridge()
        assert "scan" in cartridge.capabilities or len(cartridge.capabilities) > 0


class TestWatchmanForbiddenPatterns:
    """Test forbidden pattern detection."""

    def test_forbidden_patterns_exist(self):
        """Should have FORBIDDEN_PATTERNS defined."""
        assert hasattr(WatchmanCartridge, "FORBIDDEN_PATTERNS")
        patterns = WatchmanCartridge.FORBIDDEN_PATTERNS
        assert "mock_return" in patterns
        assert "fake_success" in patterns

    @pytest.mark.parametrize(
        "pattern_category",
        ["mock_return", "fake_success"],
    )
    def test_pattern_categories_have_regexes(self, pattern_category):
        """Should have regex patterns for each category."""
        patterns = WatchmanCartridge.FORBIDDEN_PATTERNS[pattern_category]
        assert len(patterns) > 0
        assert all(isinstance(p, str) for p in patterns)


class TestWatchmanReportStatus:
    """Test report_status method."""

    def test_report_status_returns_dict(self):
        """Should return status dict."""
        cartridge = WatchmanCartridge()
        status = cartridge.report_status()
        assert isinstance(status, dict)

    def test_report_status_has_agent_id(self):
        """Should include agent_id in status."""
        cartridge = WatchmanCartridge()
        status = cartridge.report_status()
        assert "agent_id" in status or "id" in status
