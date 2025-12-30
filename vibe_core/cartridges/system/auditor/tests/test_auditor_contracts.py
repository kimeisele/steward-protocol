"""
TEST: AuditorCartridge - The Quality Gate
==========================================
Target: auditor/cartridge_main.py
Standard: GAD-5000
"""

import pytest

from vibe_core.cartridges.system.auditor.cartridge_main import AuditorCartridge


class TestAuditorCartridgeInit:
    """Test AuditorCartridge initialization."""

    def test_cartridge_can_be_instantiated(self):
        """Should instantiate without errors."""
        cartridge = AuditorCartridge()
        assert cartridge is not None

    def test_cartridge_has_correct_agent_id(self):
        """Should have correct agent_id."""
        cartridge = AuditorCartridge()
        assert cartridge.agent_id == "auditor"

    def test_cartridge_has_correct_name(self):
        """Should have correct name."""
        cartridge = AuditorCartridge()
        assert cartridge.name == "AUDITOR"

    def test_cartridge_has_version(self):
        """Should have version string (Tool Protocol v3.0)."""
        cartridge = AuditorCartridge()
        assert hasattr(cartridge, "version")
        assert cartridge.version == "3.0.0"

    def test_cartridge_has_verify_capabilities(self):
        """Should have verify_changes and auditing capabilities."""
        cartridge = AuditorCartridge()
        assert len(cartridge.capabilities) > 0
        assert "verify_changes" in cartridge.capabilities
        assert "auditing" in cartridge.capabilities

    def test_cartridge_domain_is_security(self):
        """Should have SECURITY domain (Ring 5 Krauncha)."""
        cartridge = AuditorCartridge()
        assert cartridge.domain == "SECURITY"

    def test_cartridge_has_oath_sworn(self):
        """Should have sworn constitutional oath."""
        cartridge = AuditorCartridge()
        assert hasattr(cartridge, "oath_sworn")
        assert cartridge.oath_sworn is True


class TestAuditorManifest:
    """Test get_manifest method."""

    def test_manifest_method_exists(self):
        """Should have get_manifest method."""
        cartridge = AuditorCartridge()
        assert hasattr(cartridge, "get_manifest")
        assert callable(cartridge.get_manifest)

    def test_manifest_returns_agent_manifest(self):
        """Should return AgentManifest instance."""
        from vibe_core.protocols import AgentManifest

        cartridge = AuditorCartridge()
        manifest = cartridge.get_manifest()
        assert isinstance(manifest, AgentManifest)

    def test_manifest_has_correct_agent_id(self):
        """Should return manifest with correct agent_id."""
        cartridge = AuditorCartridge()
        manifest = cartridge.get_manifest()
        assert manifest.agent_id == "auditor"

    def test_manifest_has_no_dependencies(self):
        """Should have empty dependencies list."""
        cartridge = AuditorCartridge()
        manifest = cartridge.get_manifest()
        assert manifest.dependencies == []


class TestAuditorReportStatus:
    """Test report_status method."""

    def test_report_status_exists(self):
        """Should have report_status method."""
        cartridge = AuditorCartridge()
        assert hasattr(cartridge, "report_status")
        assert callable(cartridge.report_status)

    def test_report_status_returns_dict(self):
        """Should return status dict."""
        cartridge = AuditorCartridge()
        status = cartridge.report_status()
        assert isinstance(status, dict)

    def test_report_status_has_agent_id(self):
        """Should include agent_id in status."""
        cartridge = AuditorCartridge()
        status = cartridge.report_status()
        assert "agent_id" in status
        assert status["agent_id"] == "auditor"

    def test_report_status_has_running_status(self):
        """Should report RUNNING status."""
        cartridge = AuditorCartridge()
        status = cartridge.report_status()
        assert "status" in status
        assert status["status"] == "RUNNING"


class TestAuditorVerifyChanges:
    """Test verify_changes method."""

    def test_verify_changes_method_exists(self):
        """Should have verify_changes method."""
        cartridge = AuditorCartridge()
        assert hasattr(cartridge, "verify_changes")
        assert callable(cartridge.verify_changes)

    def test_verify_changes_file_not_found(self):
        """Should return error for non-existent file."""
        from unittest.mock import MagicMock

        cartridge = AuditorCartridge()
        task = MagicMock()
        task.payload = {"path": "/nonexistent/path/file.py"}
        result = cartridge.verify_changes(task)
        assert result["passed"] is False
        assert "not found" in result["reason"].lower()


class TestAuditorConstitutionalVerdict:
    """Test constitutional verdict method."""

    def test_render_constitutional_verdict_exists(self):
        """Should have render_constitutional_verdict method."""
        cartridge = AuditorCartridge()
        assert hasattr(cartridge, "render_constitutional_verdict")
        assert callable(cartridge.render_constitutional_verdict)
