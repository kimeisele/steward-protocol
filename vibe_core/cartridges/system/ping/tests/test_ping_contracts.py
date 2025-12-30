"""
TEST: PingCartridge - Minimal System Agent
==========================================
Target: ping/cartridge_main.py
Standard: GAD-5000

Tests the simplest cartridge as a reference implementation.
"""

from unittest.mock import MagicMock

import pytest

from vibe_core.cartridges.system.ping.cartridge_main import PingCartridge
from vibe_core.protocols import AgentManifest


class TestPingCartridgeInit:
    """Test PingCartridge initialization."""

    def test_cartridge_can_be_instantiated(self):
        """Should instantiate without errors."""
        cartridge = PingCartridge()
        assert cartridge is not None

    def test_cartridge_has_correct_agent_id(self):
        """Should have agent_id 'ping'."""
        cartridge = PingCartridge()
        assert cartridge.agent_id == "ping"

    def test_cartridge_has_correct_name(self):
        """Should have name 'PING'."""
        cartridge = PingCartridge()
        assert cartridge.name == "PING"

    def test_cartridge_has_capabilities(self):
        """Should have ping and status capabilities."""
        cartridge = PingCartridge()
        assert "ping" in cartridge.capabilities
        assert "status" in cartridge.capabilities

    def test_cartridge_domain_is_system(self):
        """Should be in SYSTEM domain."""
        cartridge = PingCartridge()
        assert cartridge.domain == "SYSTEM"

    def test_cartridge_swears_oath(self):
        """Should have sworn oath (OathMixin)."""
        cartridge = PingCartridge()
        # OathMixin sets _sworn attribute
        assert hasattr(cartridge, "_sworn") or hasattr(cartridge, "oath_sworn")


class TestPingCartridgeManifest:
    """Test get_manifest method."""

    def test_manifest_returns_agent_manifest(self):
        """Should return AgentManifest instance."""
        cartridge = PingCartridge()
        manifest = cartridge.get_manifest()
        assert isinstance(manifest, AgentManifest)

    def test_manifest_has_correct_fields(self):
        """Should have correct manifest fields."""
        cartridge = PingCartridge()
        manifest = cartridge.get_manifest()

        assert manifest.agent_id == "ping"
        assert manifest.name == "PING"
        assert manifest.version == "1.0.0"
        assert manifest.domain == "SYSTEM"
        assert "ping" in manifest.capabilities


class TestPingCartridgeProcess:
    """Test process method."""

    @pytest.mark.asyncio
    async def test_ping_action_returns_pong(self):
        """Should return pong for ping action."""
        cartridge = PingCartridge()

        mock_task = MagicMock()
        mock_task.payload = {"action": "ping"}
        mock_task.id = "test-task-001"

        result = await cartridge.process(mock_task)

        assert result["status"] == "success"
        assert result["response"] == "pong"

    @pytest.mark.asyncio
    async def test_status_action_returns_operational_info(self):
        """Should return status info for status action."""
        cartridge = PingCartridge()

        mock_task = MagicMock()
        mock_task.payload = {"action": "status"}
        mock_task.id = "test-task-002"

        result = await cartridge.process(mock_task)

        assert result["status"] == "success"
        assert result["agent"] == "ping"
        assert "degradation_level" in result

    @pytest.mark.asyncio
    async def test_default_action_is_ping(self):
        """Should default to ping action."""
        cartridge = PingCartridge()

        mock_task = MagicMock()
        mock_task.payload = {}  # No action specified
        mock_task.id = "test-task-003"

        result = await cartridge.process(mock_task)

        assert result["response"] == "pong"


class TestPingCartridgeReportStatus:
    """Test report_status method."""

    def test_report_status_returns_dict(self):
        """Should return status dict."""
        cartridge = PingCartridge()

        status = cartridge.report_status()

        assert isinstance(status, dict)

    def test_report_status_has_required_fields(self):
        """Should have all required observability fields."""
        cartridge = PingCartridge()

        status = cartridge.report_status()

        assert status["agent_id"] == "ping"
        assert status["name"] == "PING"
        assert status["status"] == "OPERATIONAL"
        assert status["domain"] == "SYSTEM"
        assert "capabilities" in status
        assert "degradation_level" in status

    def test_report_status_capabilities_match(self):
        """Should report correct capabilities."""
        cartridge = PingCartridge()

        status = cartridge.report_status()

        assert "ping" in status["capabilities"]
        assert "status" in status["capabilities"]
