"""
TEST: ArchivistCartridge - The History Keeper
=============================================
Target: archivist/cartridge_main.py
Standard: GAD-5000
"""

import pytest

from vibe_core.cartridges.system.archivist.cartridge_main import ArchivistCartridge


class TestArchivistCartridgeInit:
    """Test ArchivistCartridge initialization."""

    def test_cartridge_can_be_instantiated(self):
        """Should instantiate without errors."""
        cartridge = ArchivistCartridge()
        assert cartridge is not None

    def test_cartridge_has_correct_agent_id(self):
        """Should have correct agent_id."""
        cartridge = ArchivistCartridge()
        assert cartridge.agent_id == "archivist"

    def test_cartridge_has_correct_name(self):
        """Should have correct name."""
        cartridge = ArchivistCartridge()
        assert cartridge.name == "ARCHIVIST"

    def test_cartridge_has_version(self):
        """Should have version string."""
        cartridge = ArchivistCartridge()
        assert hasattr(cartridge, "version")
        assert cartridge.version == "2.0.0"

    def test_cartridge_has_seal_capabilities(self):
        """Should have seal_history and ledger capabilities."""
        cartridge = ArchivistCartridge()
        assert len(cartridge.capabilities) > 0
        assert "seal_history" in cartridge.capabilities
        assert "ledger" in cartridge.capabilities

    def test_cartridge_domain_is_system(self):
        """Should have SYSTEM domain."""
        cartridge = ArchivistCartridge()
        assert cartridge.domain == "SYSTEM"

    def test_cartridge_has_oath_sworn(self):
        """Should have sworn constitutional oath."""
        cartridge = ArchivistCartridge()
        assert hasattr(cartridge, "oath_sworn")
        assert cartridge.oath_sworn is True


class TestArchivistManifest:
    """Test get_manifest method."""

    def test_manifest_method_exists(self):
        """Should have get_manifest method."""
        cartridge = ArchivistCartridge()
        assert hasattr(cartridge, "get_manifest")
        assert callable(cartridge.get_manifest)

    def test_manifest_returns_agent_manifest(self):
        """Should return AgentManifest instance."""
        from vibe_core.protocols import AgentManifest

        cartridge = ArchivistCartridge()
        manifest = cartridge.get_manifest()
        assert isinstance(manifest, AgentManifest)

    def test_manifest_has_correct_agent_id(self):
        """Should return manifest with correct agent_id."""
        cartridge = ArchivistCartridge()
        manifest = cartridge.get_manifest()
        assert manifest.agent_id == "archivist"

    def test_manifest_has_no_dependencies(self):
        """Should have empty dependencies list."""
        cartridge = ArchivistCartridge()
        manifest = cartridge.get_manifest()
        assert manifest.dependencies == []


class TestArchivistReportStatus:
    """Test report_status method."""

    def test_report_status_exists(self):
        """Should have report_status method."""
        cartridge = ArchivistCartridge()
        assert hasattr(cartridge, "report_status")
        assert callable(cartridge.report_status)

    def test_report_status_returns_dict(self):
        """Should return status dict."""
        cartridge = ArchivistCartridge()
        status = cartridge.report_status()
        assert isinstance(status, dict)

    def test_report_status_has_agent_id(self):
        """Should include agent_id in status."""
        cartridge = ArchivistCartridge()
        status = cartridge.report_status()
        assert "agent_id" in status
        assert status["agent_id"] == "archivist"

    def test_report_status_has_running_status(self):
        """Should report RUNNING status."""
        cartridge = ArchivistCartridge()
        status = cartridge.report_status()
        assert "status" in status
        assert status["status"] == "RUNNING"


class TestArchivistSealHistory:
    """Test seal_history method."""

    def test_seal_history_method_exists(self):
        """Should have seal_history method."""
        cartridge = ArchivistCartridge()
        assert hasattr(cartridge, "seal_history")
        assert callable(cartridge.seal_history)

    def test_seal_history_rejects_failed_audit(self):
        """Should reject sealing when audit_result.passed is False."""
        from unittest.mock import MagicMock

        cartridge = ArchivistCartridge()
        task = MagicMock()
        task.payload = {
            "source_path": "/tmp/test.py",
            "dest_path": "src/test.py",
            "audit_result": {"passed": False, "reason": "Syntax error"},
        }
        result = cartridge.seal_history(task)
        assert result["status"] == "rejected"
        assert "Audit failed" in result["reason"]

    def test_seal_history_rejects_missing_source(self):
        """Should reject when source file does not exist."""
        from unittest.mock import MagicMock

        cartridge = ArchivistCartridge()
        task = MagicMock()
        task.payload = {
            "source_path": "/nonexistent/file.py",
            "dest_path": "src/test.py",
            "audit_result": {"passed": True},
        }
        result = cartridge.seal_history(task)
        assert result["status"] == "error"
        assert "Source file" in result["reason"] or "vanished" in result["reason"]
