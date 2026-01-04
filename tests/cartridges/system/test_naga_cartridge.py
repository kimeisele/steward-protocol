"""
Tests for NAGA Cartridge.

Tests the NAGA Federation Cartridge:
- Cartridge initialization
- Tool Protocol compliance
- Action dispatch
- Federation integration
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestNagaCartridgeInit:
    """Test NAGA cartridge initialization."""

    def test_cartridge_init(self):
        """Should initialize with correct properties."""
        from vibe_core.cartridges.system.naga import NagaCartridge

        cartridge = NagaCartridge()

        assert cartridge.agent_id == "naga"
        assert cartridge.name == "NAGA Federation"
        assert cartridge.domain == "SECURITY"
        assert "status" in cartridge.capabilities
        assert "scan" in cartridge.capabilities
        assert "detect" in cartridge.capabilities

    def test_cartridge_manifest(self):
        """Should return valid manifest."""
        from vibe_core.cartridges.system.naga import NagaCartridge

        cartridge = NagaCartridge()
        manifest = cartridge.get_manifest()

        assert manifest.agent_id == "naga"
        assert manifest.domain == "SECURITY"
        assert manifest.version == "1.0.0"

    def test_oath_sworn(self):
        """Should have sworn constitutional oath."""
        from vibe_core.cartridges.system.naga import NagaCartridge

        cartridge = NagaCartridge()

        assert cartridge.oath_sworn is True


class TestNagaCartridgeStatus:
    """Test status action."""

    def test_status_without_federation(self):
        """Should return unavailable when federation not registered."""
        from vibe_core.cartridges.system.naga import NagaCartridge

        cartridge = NagaCartridge()

        # Force federation to None
        cartridge._federation = None

        result = cartridge._get_status()

        assert result["status"] == "unavailable"
        assert result["healthy"] is False

    def test_status_with_mock_federation(self):
        """Should return federation status when available."""
        from vibe_core.cartridges.system.naga import NagaCartridge

        cartridge = NagaCartridge()

        # Mock federation
        mock_federation = MagicMock()
        mock_federation.is_ready.return_value = True
        mock_federation.get_status.return_value = {"sesha": "healthy"}

        cartridge._federation = mock_federation

        result = cartridge._get_status()

        assert result["status"] == "healthy"
        assert result["healthy"] is True


class TestNagaCartridgeScan:
    """Test toxicity scan action."""

    @pytest.mark.asyncio
    async def test_scan_no_content(self):
        """Should return error when no content provided."""
        from vibe_core.cartridges.system.naga import NagaCartridge

        cartridge = NagaCartridge()

        result = await cartridge._scan_toxicity({})

        assert "error" in result
        assert result["toxicity"] == 0.0

    @pytest.mark.asyncio
    async def test_scan_without_takshaka(self):
        """Should return error when Takshaka unavailable."""
        from vibe_core.cartridges.system.naga import NagaCartridge

        cartridge = NagaCartridge()
        cartridge._federation = MagicMock()
        cartridge._federation.takshaka = None

        result = await cartridge._scan_toxicity({"content": "test content"})

        assert "error" in result
        assert "not available" in result["error"]

    @pytest.mark.asyncio
    async def test_scan_with_mock_takshaka(self):
        """Should return scan results from Takshaka."""
        from vibe_core.cartridges.system.naga import NagaCartridge

        cartridge = NagaCartridge()

        # Mock federation with Takshaka
        mock_result = MagicMock()
        mock_result.score = 0.5
        mock_result.blocked = True
        mock_result.patterns = ["pattern1"]

        mock_takshaka = MagicMock()
        mock_takshaka.scan_toxicity.return_value = mock_result

        mock_federation = MagicMock()
        mock_federation.takshaka = mock_takshaka

        cartridge._federation = mock_federation

        result = await cartridge._scan_toxicity({"content": "toxic content"})

        assert result["toxicity"] == 0.5
        assert result["blocked"] is True
        assert result["patterns"] == ["pattern1"]


class TestNagaCartridgeDetect:
    """Test drift detection action."""

    def test_detect_without_federation(self):
        """Should return empty when federation unavailable."""
        from vibe_core.cartridges.system.naga import NagaCartridge

        cartridge = NagaCartridge()
        cartridge._federation = None

        result = cartridge._get_detections()

        assert "error" in result
        assert result["detections"] == []

    def test_detect_with_mock_watcher(self):
        """Should return CommitWatcher stats."""
        from vibe_core.cartridges.system.naga import NagaCartridge

        cartridge = NagaCartridge()

        # Mock federation with CommitWatcher
        mock_stats = {
            "total_observed": 100,
            "panic_count": 2,
            "alerts_generated": 1,
        }

        mock_watcher = MagicMock()
        mock_watcher.get_stats.return_value = mock_stats

        mock_federation = MagicMock()
        mock_federation.commit_watcher = mock_watcher
        mock_federation.flood_manager = None

        cartridge._federation = mock_federation

        result = cartridge._get_detections()

        assert "commit_watcher" in result
        assert result["stats"]["panic_count"] == 2


class TestNagaCartridgeFlood:
    """Test flood status action."""

    def test_flood_without_manager(self):
        """Should return error when FloodManager unavailable."""
        from vibe_core.cartridges.system.naga import NagaCartridge

        cartridge = NagaCartridge()

        mock_federation = MagicMock()
        mock_federation.flood_manager = None

        cartridge._federation = mock_federation

        result = cartridge._get_flood_status()

        assert "error" in result
        assert result["active"] is False

    def test_flood_with_mock_manager(self):
        """Should return FloodManager status."""
        from vibe_core.cartridges.system.naga import NagaCartridge

        cartridge = NagaCartridge()

        # Mock federation with FloodManager
        mock_status = {
            "active": True,
            "total_observations": 500,
            "subscriber_count": 3,
        }

        mock_flood = MagicMock()
        mock_flood.get_status.return_value = mock_status

        mock_federation = MagicMock()
        mock_federation.flood_manager = mock_flood

        cartridge._federation = mock_federation

        result = cartridge._get_flood_status()

        assert result["active"] is True
        assert result["total_observations"] == 500


class TestNagaCartridgeProcess:
    """Test main process dispatch."""

    @pytest.mark.asyncio
    async def test_process_status_action(self):
        """Should dispatch status action."""
        from vibe_core.cartridges.system.naga import NagaCartridge
        from vibe_core.scheduling.task import Task

        cartridge = NagaCartridge()
        cartridge._federation = None

        task = Task(
            agent_id="naga",
            payload={"action": "status"},
        )

        result = await cartridge.process(task)

        assert result["status"] == "unavailable"

    @pytest.mark.asyncio
    async def test_process_unknown_action(self):
        """Should return ignored for unknown action."""
        from vibe_core.cartridges.system.naga import NagaCartridge
        from vibe_core.scheduling.task import Task

        cartridge = NagaCartridge()

        task = Task(
            agent_id="naga",
            payload={"action": "unknown_action"},
        )

        result = await cartridge.process(task)

        assert result["status"] == "ignored"
        assert "Unknown action" in result["reason"]


class TestNagaCartridgeReportStatus:
    """Test report_status method."""

    def test_report_status_degraded(self):
        """Should report DEGRADED when federation not ready."""
        from vibe_core.cartridges.system.naga import NagaCartridge

        cartridge = NagaCartridge()
        cartridge._federation = None

        status = cartridge.report_status()

        assert status["agent_id"] == "naga"
        assert status["status"] == "DEGRADED"
        assert status["federation_ready"] is False

    def test_report_status_running(self):
        """Should report RUNNING when federation ready."""
        from vibe_core.cartridges.system.naga import NagaCartridge

        cartridge = NagaCartridge()

        mock_federation = MagicMock()
        mock_federation.is_ready.return_value = True

        cartridge._federation = mock_federation

        status = cartridge.report_status()

        assert status["status"] == "RUNNING"
        assert status["federation_ready"] is True


class TestFederationStatusTool:
    """Test FederationStatusTool."""

    def test_tool_properties(self):
        """Should have correct tool properties."""
        from vibe_core.cartridges.system.naga.tools import FederationStatusTool

        tool = FederationStatusTool()

        assert tool.name == "naga.status"
        assert "health" in tool.description.lower()

    def test_validate_missing_action(self):
        """Should raise on missing action."""
        from vibe_core.cartridges.system.naga.tools import FederationStatusTool

        tool = FederationStatusTool()

        with pytest.raises(ValueError, match="Missing required parameter"):
            tool.validate({})

    def test_validate_invalid_action(self):
        """Should raise on invalid action."""
        from vibe_core.cartridges.system.naga.tools import FederationStatusTool

        tool = FederationStatusTool()

        with pytest.raises(ValueError, match="Invalid action"):
            tool.validate({"action": "invalid"})

    def test_execute_no_federation(self):
        """Should return unavailable when federation not registered."""
        from vibe_core.cartridges.system.naga.tools import FederationStatusTool

        tool = FederationStatusTool()
        tool._federation = None

        result = tool.execute({"action": "check_all"})

        assert result.success is True
        assert result.output["status"] == "unavailable"


class TestToxicityScanTool:
    """Test ToxicityScanTool."""

    def test_tool_properties(self):
        """Should have correct tool properties."""
        from vibe_core.cartridges.system.naga.tools import ToxicityScanTool

        tool = ToxicityScanTool()

        assert tool.name == "naga.scan"
        assert "toxicity" in tool.description.lower()

    def test_validate_missing_content(self):
        """Should raise on missing content."""
        from vibe_core.cartridges.system.naga.tools import ToxicityScanTool

        tool = ToxicityScanTool()

        with pytest.raises(ValueError, match="Missing required parameter"):
            tool.validate({"action": "scan"})

    def test_validate_invalid_threshold(self):
        """Should raise on invalid threshold."""
        from vibe_core.cartridges.system.naga.tools import ToxicityScanTool

        tool = ToxicityScanTool()

        with pytest.raises(ValueError, match="threshold must be"):
            tool.validate({"action": "scan", "content": "test", "threshold": 1.5})


class TestDriftDetectionTool:
    """Test DriftDetectionTool."""

    def test_tool_properties(self):
        """Should have correct tool properties."""
        from vibe_core.cartridges.system.naga.tools import DriftDetectionTool

        tool = DriftDetectionTool()

        assert tool.name == "naga.detect"
        assert "drift" in tool.description.lower()

    def test_validate_invalid_action(self):
        """Should raise on invalid action."""
        from vibe_core.cartridges.system.naga.tools import DriftDetectionTool

        tool = DriftDetectionTool()

        with pytest.raises(ValueError, match="Invalid action"):
            tool.validate({"action": "invalid"})

    def test_execute_no_federation(self):
        """Should return warning when federation unavailable."""
        from vibe_core.cartridges.system.naga.tools import DriftDetectionTool

        tool = DriftDetectionTool()
        tool._federation = None

        result = tool.execute({"action": "detect_all"})

        assert result.success is True
        assert "warning" in result.output
