"""
TEST: ChronicleCartridge - The Keeper of Temporal Lines
=======================================================
Target: chronicle/cartridge_main.py
Standard: GAD-5000
"""

import pytest

from vibe_core.cartridges.system.chronicle.cartridge_main import ChronicleCartridge


class TestChronicleCartridgeInit:
    """Test ChronicleCartridge initialization."""

    def test_cartridge_can_be_instantiated(self):
        """Should instantiate without errors."""
        cartridge = ChronicleCartridge()
        assert cartridge is not None

    def test_cartridge_has_agent_id(self):
        """Should have correct agent_id."""
        cartridge = ChronicleCartridge()
        assert cartridge.agent_id == "chronicle"

    def test_cartridge_has_capabilities(self):
        """Should have git-related capabilities."""
        cartridge = ChronicleCartridge()
        assert len(cartridge.capabilities) > 0


class TestChronicleManifest:
    """Test get_manifest method."""

    def test_manifest_exists(self):
        """Should have get_manifest method."""
        cartridge = ChronicleCartridge()
        assert hasattr(cartridge, "get_manifest")

    def test_manifest_returns_data(self):
        """Should return manifest with agent info."""
        cartridge = ChronicleCartridge()
        manifest = cartridge.get_manifest()
        assert manifest is not None
        assert manifest.agent_id == "chronicle"


class TestChronicleReportStatus:
    """Test report_status method."""

    def test_report_status_exists(self):
        """Should have report_status method."""
        cartridge = ChronicleCartridge()
        assert hasattr(cartridge, "report_status")
        assert callable(cartridge.report_status)

    @pytest.mark.skip(reason="Requires kernel system connection for git tool execution")
    def test_report_status_returns_dict(self):
        """Should return status dict when connected to kernel."""
        cartridge = ChronicleCartridge()
        status = cartridge.report_status()
        assert isinstance(status, dict)
        assert "agent_id" in status
