"""
TEST: EnvoyCartridge - The Brain Connected to the Heart
========================================================
Target: envoy/cartridge_main.py
Standard: GAD-5000
"""

import pytest

from vibe_core.cartridges.system.envoy.cartridge_main import EnvoyCartridge


class TestEnvoyCartridgeInit:
    """Test EnvoyCartridge initialization."""

    def test_cartridge_can_be_instantiated(self):
        """Should instantiate without errors."""
        cartridge = EnvoyCartridge()
        assert cartridge is not None

    def test_cartridge_has_correct_agent_id(self):
        """Should have correct agent_id."""
        cartridge = EnvoyCartridge()
        assert cartridge.agent_id == "envoy"

    def test_cartridge_has_correct_name(self):
        """Should have correct name."""
        cartridge = EnvoyCartridge()
        assert cartridge.name == "ENVOY"

    def test_cartridge_has_version(self):
        """Should have version string (GAD-5500 Wiring)."""
        cartridge = EnvoyCartridge()
        assert hasattr(cartridge, "version")
        assert cartridge.version == "3.1.0"

    def test_cartridge_has_orchestration_capabilities(self):
        """Should have orchestration and governance capabilities."""
        cartridge = EnvoyCartridge()
        assert len(cartridge.capabilities) > 0
        assert "orchestration" in cartridge.capabilities
        assert "governance" in cartridge.capabilities

    def test_cartridge_domain_is_interface(self):
        """Should have INTERFACE domain."""
        cartridge = EnvoyCartridge()
        assert cartridge.domain == "INTERFACE"

    def test_cartridge_has_oath_sworn(self):
        """Should have sworn constitutional oath."""
        cartridge = EnvoyCartridge()
        assert hasattr(cartridge, "oath_sworn")
        assert cartridge.oath_sworn is True


class TestEnvoyManifest:
    """Test get_manifest method."""

    def test_manifest_method_exists(self):
        """Should have get_manifest method."""
        cartridge = EnvoyCartridge()
        assert hasattr(cartridge, "get_manifest")
        assert callable(cartridge.get_manifest)

    def test_manifest_returns_agent_manifest(self):
        """Should return AgentManifest instance."""
        from vibe_core.protocols import AgentManifest

        cartridge = EnvoyCartridge()
        manifest = cartridge.get_manifest()
        assert isinstance(manifest, AgentManifest)

    def test_manifest_has_correct_agent_id(self):
        """Should return manifest with correct agent_id."""
        cartridge = EnvoyCartridge()
        manifest = cartridge.get_manifest()
        assert manifest.agent_id == "envoy"


class TestEnvoyReportStatus:
    """Test report_status method."""

    def test_report_status_exists(self):
        """Should have report_status method."""
        cartridge = EnvoyCartridge()
        assert hasattr(cartridge, "report_status")
        assert callable(cartridge.report_status)

    @pytest.mark.skip(reason="Requires system interface for sandbox path access")
    def test_report_status_returns_dict(self):
        """Should return status dict when connected to kernel."""
        cartridge = EnvoyCartridge()
        status = cartridge.report_status()
        assert isinstance(status, dict)


class TestEnvoyRoutingMethods:
    """Test routing-related methods."""

    def test_route_command_method_exists(self):
        """Should have _route_command private method."""
        cartridge = EnvoyCartridge()
        assert hasattr(cartridge, "_route_command")
        assert callable(cartridge._route_command)

    def test_log_operation_method_exists(self):
        """Should have _log_operation private method."""
        cartridge = EnvoyCartridge()
        assert hasattr(cartridge, "_log_operation")
        assert callable(cartridge._log_operation)


class TestEnvoyLazyProperties:
    """Test lazy-loaded properties."""

    def test_has_log_path_property(self):
        """Should have log_path property."""
        cartridge = EnvoyCartridge()
        assert hasattr(EnvoyCartridge, "log_path")

    def test_has_router_property(self):
        """Should have router property."""
        cartridge = EnvoyCartridge()
        assert hasattr(EnvoyCartridge, "router")

    def test_has_executor_property(self):
        """Should have executor property (OPUS-307)."""
        cartridge = EnvoyCartridge()
        assert hasattr(EnvoyCartridge, "executor")


class TestEnvoyState:
    """Test internal state management."""

    def test_operation_log_exists(self):
        """Should have operation_log list."""
        cartridge = EnvoyCartridge()
        assert hasattr(cartridge, "operation_log")
        assert isinstance(cartridge.operation_log, list)
