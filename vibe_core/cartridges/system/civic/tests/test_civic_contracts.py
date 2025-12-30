"""
TEST: CivicCartridge - The Bureaucrat (Administrative Agent)
============================================================
Target: civic/cartridge_main.py
Standard: GAD-5000
"""

import pytest

from vibe_core.cartridges.system.civic.cartridge_main import CivicCartridge


class TestCivicCartridgeInit:
    """Test CivicCartridge initialization."""

    def test_cartridge_can_be_instantiated(self):
        """Should instantiate without errors."""
        cartridge = CivicCartridge()
        assert cartridge is not None

    def test_cartridge_has_correct_agent_id(self):
        """Should have correct agent_id."""
        cartridge = CivicCartridge()
        assert cartridge.agent_id == "civic"

    def test_cartridge_has_correct_name(self):
        """Should have correct name."""
        cartridge = CivicCartridge()
        assert cartridge.name == "CIVIC"

    def test_cartridge_has_version(self):
        """Should have version string (v2.0.0 P1 Refactor)."""
        cartridge = CivicCartridge()
        assert hasattr(cartridge, "version")
        assert cartridge.version == "2.0.0"

    def test_cartridge_has_governance_capabilities(self):
        """Should have registry, licensing, and governance capabilities."""
        cartridge = CivicCartridge()
        assert len(cartridge.capabilities) > 0
        assert "registry" in cartridge.capabilities
        assert "governance" in cartridge.capabilities

    def test_cartridge_domain_is_governance(self):
        """Should have GOVERNANCE domain."""
        cartridge = CivicCartridge()
        assert cartridge.domain == "GOVERNANCE"

    def test_cartridge_has_oath_sworn(self):
        """Should have sworn constitutional oath."""
        cartridge = CivicCartridge()
        assert hasattr(cartridge, "oath_sworn")
        assert cartridge.oath_sworn is True


class TestCivicDelegatedAgents:
    """Test delegated agents (P1 Refactor architecture)."""

    def test_has_registry_agent(self):
        """Should have RegistryAgent delegate."""
        cartridge = CivicCartridge()
        assert hasattr(cartridge, "registry_agent")
        assert cartridge.registry_agent is not None

    def test_has_economy_agent(self):
        """Should have EconomyAgent delegate."""
        cartridge = CivicCartridge()
        assert hasattr(cartridge, "economy_agent")
        assert cartridge.economy_agent is not None

    def test_has_lifecycle_agent(self):
        """Should have LifecycleAgent delegate."""
        cartridge = CivicCartridge()
        assert hasattr(cartridge, "lifecycle_agent")
        assert cartridge.lifecycle_agent is not None


class TestCivicManifest:
    """Test get_manifest method."""

    def test_manifest_method_exists(self):
        """Should have get_manifest method."""
        cartridge = CivicCartridge()
        assert hasattr(cartridge, "get_manifest")
        assert callable(cartridge.get_manifest)

    def test_manifest_returns_agent_manifest(self):
        """Should return AgentManifest instance."""
        from vibe_core.protocols import AgentManifest

        cartridge = CivicCartridge()
        manifest = cartridge.get_manifest()
        assert isinstance(manifest, AgentManifest)

    def test_manifest_has_correct_agent_id(self):
        """Should return manifest with correct agent_id."""
        cartridge = CivicCartridge()
        manifest = cartridge.get_manifest()
        assert manifest.agent_id == "civic"


class TestCivicReportStatus:
    """Test report_status method."""

    def test_report_status_exists(self):
        """Should have report_status method."""
        cartridge = CivicCartridge()
        assert hasattr(cartridge, "report_status")
        assert callable(cartridge.report_status)

    @pytest.mark.skip(reason="Requires kernel system connection for economy_agent ledger tool")
    def test_report_status_returns_dict(self):
        """Should return status dict when connected to kernel."""
        cartridge = CivicCartridge()
        status = cartridge.report_status()
        assert isinstance(status, dict)

    @pytest.mark.skip(reason="Requires kernel system connection for economy_agent ledger tool")
    def test_report_status_has_agent_id(self):
        """Should include agent_id in status when connected to kernel."""
        cartridge = CivicCartridge()
        status = cartridge.report_status()
        assert "agent_id" in status
        assert status["agent_id"] == "civic"

    @pytest.mark.skip(reason="Requires kernel system connection for economy_agent ledger tool")
    def test_report_status_has_running_status(self):
        """Should report RUNNING status when connected to kernel."""
        cartridge = CivicCartridge()
        status = cartridge.report_status()
        assert "status" in status
        assert status["status"] == "RUNNING"

    @pytest.mark.skip(reason="Requires kernel system connection for economy_agent ledger tool")
    def test_report_status_has_delegated_agents_status(self):
        """Should include status from all delegated agents when connected to kernel."""
        cartridge = CivicCartridge()
        status = cartridge.report_status()
        assert "delegated_agents" in status
        assert "registry" in status["delegated_agents"]
        assert "economy" in status["delegated_agents"]
        assert "lifecycle" in status["delegated_agents"]


class TestCivicMatrixConfig:
    """Test THE MATRIX configuration loading."""

    def test_matrix_attribute_exists(self):
        """Should have matrix attribute."""
        cartridge = CivicCartridge()
        assert hasattr(cartridge, "matrix")

    def test_get_matrix_config_method_exists(self):
        """Should have get_matrix_config method."""
        cartridge = CivicCartridge()
        assert hasattr(cartridge, "get_matrix_config")
        assert callable(cartridge.get_matrix_config)

    def test_default_matrix_has_city_name(self):
        """Should have city_name in matrix (default or loaded)."""
        cartridge = CivicCartridge()
        assert "city_name" in cartridge.matrix
