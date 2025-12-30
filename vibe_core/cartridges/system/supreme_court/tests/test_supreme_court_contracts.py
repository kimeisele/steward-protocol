"""
TEST: SupremeCourtCartridge - The Appellate Justice System
==========================================================
Target: supreme_court/cartridge_main.py
Standard: GAD-5000
"""

import pytest

from vibe_core.cartridges.system.supreme_court.cartridge_main import SupremeCourtCartridge


class TestSupremeCourtCartridgeInit:
    """Test SupremeCourtCartridge initialization."""

    def test_cartridge_can_be_instantiated(self):
        """Should instantiate without errors."""
        cartridge = SupremeCourtCartridge()
        assert cartridge is not None

    def test_cartridge_has_correct_agent_id(self):
        """Should have correct agent_id."""
        cartridge = SupremeCourtCartridge()
        assert cartridge.agent_id == "supreme_court"

    def test_cartridge_has_correct_name(self):
        """Should have correct name."""
        cartridge = SupremeCourtCartridge()
        assert cartridge.name == "Supreme Court"

    def test_cartridge_has_version(self):
        """Should have version string."""
        cartridge = SupremeCourtCartridge()
        assert hasattr(cartridge, "version")
        assert cartridge.version == "1.0.0"

    def test_cartridge_has_capabilities(self):
        """Should have governance and auditing capabilities."""
        cartridge = SupremeCourtCartridge()
        assert len(cartridge.capabilities) > 0
        # Should include governance capability
        assert any("governance" in str(cap).lower() for cap in cartridge.capabilities)

    def test_cartridge_domain_is_justice(self):
        """Should have JUSTICE domain."""
        cartridge = SupremeCourtCartridge()
        assert cartridge.domain == "JUSTICE"

    def test_cartridge_has_oath_sworn(self):
        """Should have sworn constitutional oath."""
        cartridge = SupremeCourtCartridge()
        assert hasattr(cartridge, "oath_sworn")
        assert cartridge.oath_sworn is True


class TestSupremeCourtManifest:
    """Test get_manifest method."""

    def test_manifest_method_exists(self):
        """Should have get_manifest method."""
        cartridge = SupremeCourtCartridge()
        assert hasattr(cartridge, "get_manifest")
        assert callable(cartridge.get_manifest)

    def test_manifest_returns_agent_manifest(self):
        """Should return AgentManifest instance."""
        from vibe_core.protocols import AgentManifest

        cartridge = SupremeCourtCartridge()
        manifest = cartridge.get_manifest()
        assert isinstance(manifest, AgentManifest)

    def test_manifest_has_correct_agent_id(self):
        """Should return manifest with correct agent_id."""
        cartridge = SupremeCourtCartridge()
        manifest = cartridge.get_manifest()
        assert manifest.agent_id == "supreme_court"

    def test_manifest_has_dependencies(self):
        """Should declare auditor as dependency."""
        cartridge = SupremeCourtCartridge()
        manifest = cartridge.get_manifest()
        assert hasattr(manifest, "dependencies")
        assert "auditor" in manifest.dependencies


class TestSupremeCourtReportStatus:
    """Test report_status method."""

    def test_report_status_exists(self):
        """Should have report_status method."""
        cartridge = SupremeCourtCartridge()
        assert hasattr(cartridge, "report_status")
        assert callable(cartridge.report_status)

    def test_report_status_returns_dict(self):
        """Should return status dict."""
        cartridge = SupremeCourtCartridge()
        status = cartridge.report_status()
        assert isinstance(status, dict)

    def test_report_status_has_agent_id(self):
        """Should include agent_id in status."""
        cartridge = SupremeCourtCartridge()
        status = cartridge.report_status()
        assert "agent_id" in status
        assert status["agent_id"] == "supreme_court"

    def test_report_status_has_status_field(self):
        """Should include status field."""
        cartridge = SupremeCourtCartridge()
        status = cartridge.report_status()
        assert "status" in status
        assert status["status"] == "healthy"


class TestSupremeCourtProcess:
    """Test process method structure."""

    def test_process_method_exists(self):
        """Should have process method."""
        cartridge = SupremeCourtCartridge()
        assert hasattr(cartridge, "process")
        assert callable(cartridge.process)

    @pytest.mark.asyncio
    async def test_process_unknown_action_returns_error(self):
        """Should return error for unknown action."""
        from unittest.mock import MagicMock

        cartridge = SupremeCourtCartridge()
        mock_task = {"action": "unknown_action", "payload": {}}
        result = await cartridge.process(mock_task)
        assert result["status"] == "error"
        assert "Unknown action" in result["error"]
