"""
Tests for PrakritiStatePanel - OPUS-027 State Visualization

Verifies the panel correctly displays:
- Session status (active/inactive)
- Three-layer status (STHULA/PRANA/PURUSHA)
- Cryptographic Zipper sync status
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestPrakritiStatePanel:
    """Test suite for PrakritiStatePanel."""

    @pytest.fixture
    def mock_kernel(self):
        """Create a mock kernel for testing."""
        kernel = MagicMock()
        kernel.status = MagicMock()
        kernel.status.value = "RUNNING"
        kernel._agents = {"agent1": MagicMock(), "agent2": MagicMock()}
        return kernel

    @pytest.fixture
    def panel(self, mock_kernel):
        """Create panel instance with mock kernel."""
        from vibe_core.plugins.interface.renderers.opus.panels.prakriti_state import (
            PrakritiStatePanel,
        )

        panel = PrakritiStatePanel(mock_kernel)
        panel._root = Path(".")
        return panel

    def test_panel_id(self, panel):
        """Panel should have correct ID."""
        assert panel.panel_id == "prakriti_state"

    def test_panel_title(self, panel):
        """Panel should have correct title."""
        assert "Prakriti" in panel.title
        assert "OPUS-027" in panel.title

    def test_panel_priority(self, panel):
        """Panel should have high priority (low number = shown first)."""
        assert panel.priority < 10  # Should be near top

    def test_render_without_prakriti(self, mock_kernel):
        """Panel should handle missing Prakriti gracefully."""
        from vibe_core.plugins.interface.renderers.opus.panels.prakriti_state import (
            PrakritiStatePanel,
        )

        # Kernel without prakriti attribute
        mock_kernel.prakriti = None
        panel = PrakritiStatePanel(mock_kernel)
        panel._root = Path("/nonexistent")  # Force fallback to fail too

        content = panel.render()
        assert "not available" in content.lower() or "Prakriti" in content

    def test_render_with_active_session(self, panel):
        """Panel should show active session details."""
        # Mock Prakriti with active session
        mock_prakriti = MagicMock()
        mock_session = MagicMock()
        mock_session.session_id = "abc123"
        mock_session.boot_commit = "deadbeef1234567890"
        mock_session.commit_count = 5
        mock_session.crash_recovery = False
        mock_prakriti.session = mock_session

        # Mock git status
        mock_prakriti.git.status.return_value = {"is_dirty": False, "branch": "main"}
        mock_prakriti.git.head_sha.return_value = "abc123def456"

        # Mock personas
        mock_prakriti.personas.status.return_value = {
            "active_persona": None,
            "available_personas": [],
        }

        # Mock ledger
        mock_prakriti.ledger.get_current_head_hash.return_value = None
        mock_prakriti.ledger.get_last_sync_commit.return_value = None

        with patch.object(panel, "_get_prakriti", return_value=mock_prakriti):
            content = panel.render()

        assert "abc123" in content  # Session ID
        assert "deadbee" in content  # Boot commit (truncated)
        assert "5" in content  # Commit count

    def test_render_three_layers(self, panel):
        """Panel should show all three layer statuses."""
        mock_prakriti = MagicMock()
        mock_prakriti.session = None
        mock_prakriti.git.status.return_value = {"is_dirty": True, "branch": "feature"}
        mock_prakriti.git.head_sha.return_value = "abc123"
        mock_prakriti.personas.status.return_value = {
            "active_persona": "steward",
            "available_personas": ["steward", "architect"],
        }
        mock_prakriti.ledger.get_current_head_hash.return_value = "ledger123"
        mock_prakriti.ledger.get_last_sync_commit.return_value = "abc123"

        with patch.object(panel, "_get_prakriti", return_value=mock_prakriti):
            content = panel.render()

        # Check three layers mentioned
        assert "STHULA" in content
        assert "PRANA" in content
        assert "PURUSHA" in content

    def test_sthula_status_clean(self, panel):
        """STHULA layer should show clean status correctly."""
        mock_prakriti = MagicMock()
        mock_prakriti.git.status.return_value = {"is_dirty": False, "branch": "main"}

        result = panel._get_sthula_status(mock_prakriti)
        assert result["icon"] == "✅"
        assert "Clean" in result["details"]

    def test_sthula_status_dirty(self, panel):
        """STHULA layer should show dirty status correctly."""
        mock_prakriti = MagicMock()
        mock_prakriti.git.status.return_value = {"is_dirty": True, "branch": "feature"}

        result = panel._get_sthula_status(mock_prakriti)
        assert result["icon"] == "🟡"
        assert "Dirty" in result["details"]

    def test_prana_status_running(self, panel):
        """PRANA layer should show running status."""
        result = panel._get_prana_status(None)  # Uses self.kernel
        assert result["icon"] == "✅"
        assert "Running" in result["details"]
        assert "2 agents" in result["details"]

    def test_prana_status_stopped(self, mock_kernel):
        """PRANA layer should show stopped status."""
        from vibe_core.plugins.interface.renderers.opus.panels.prakriti_state import (
            PrakritiStatePanel,
        )

        mock_kernel.status.value = "STOPPED"
        panel = PrakritiStatePanel(mock_kernel)

        result = panel._get_prana_status(None)
        assert result["icon"] == "⏹️"
        assert "Stopped" in result["details"]

    def test_purusha_status_with_persona(self, panel):
        """PURUSHA layer should show active persona."""
        mock_prakriti = MagicMock()
        mock_prakriti.personas.status.return_value = {
            "active_persona": "steward",
            "available_personas": ["steward"],
        }

        result = panel._get_purusha_status(mock_prakriti)
        assert result["icon"] == "✅"
        assert "steward" in result["details"]

    def test_purusha_status_no_persona(self, panel):
        """PURUSHA layer should handle no personas."""
        mock_prakriti = MagicMock()
        mock_prakriti.personas.status.return_value = {
            "active_persona": None,
            "available_personas": [],
        }

        result = panel._get_purusha_status(mock_prakriti)
        assert result["icon"] == "⚪"
        assert "No personas" in result["details"]

    def test_sync_status_synced(self, panel):
        """Cryptographic Zipper should show synced status."""
        mock_prakriti = MagicMock()
        mock_prakriti.git.head_sha.return_value = "abc123def456"
        mock_prakriti.ledger.get_current_head_hash.return_value = "ledger789"
        mock_prakriti.ledger.get_last_sync_commit.return_value = "abc123def456"

        result = panel._get_sync_status(mock_prakriti)
        assert result["synced"] is True
        assert result["sync_icon"] == "✅"

    def test_sync_status_drifted(self, panel):
        """Cryptographic Zipper should detect drift."""
        mock_prakriti = MagicMock()
        mock_prakriti.git.head_sha.return_value = "abc123def456"
        mock_prakriti.ledger.get_current_head_hash.return_value = "ledger789"
        mock_prakriti.ledger.get_last_sync_commit.return_value = "different_commit"

        result = panel._get_sync_status(mock_prakriti)
        assert result["synced"] is False
        assert result["sync_icon"] == "⚠️"

    def test_sync_status_empty_ledger(self, panel):
        """Cryptographic Zipper should handle empty ledger."""
        mock_prakriti = MagicMock()
        mock_prakriti.git.head_sha.return_value = "abc123def456"
        mock_prakriti.ledger.get_current_head_hash.return_value = None
        mock_prakriti.ledger.get_last_sync_commit.return_value = None

        result = panel._get_sync_status(mock_prakriti)
        # Empty ledger is OK for fresh repos
        assert result["synced"] is True
        assert result["sync_icon"] == "⚪"

    def test_error_handling_in_layers(self, panel):
        """All layer methods should handle errors gracefully."""
        mock_prakriti = MagicMock()

        # Force errors
        mock_prakriti.git.status.side_effect = Exception("Git error")
        mock_prakriti.personas.status.side_effect = Exception("Persona error")
        mock_prakriti.ledger.get_current_head_hash.side_effect = Exception("Ledger error")

        # Should not raise, should return error status
        sthula = panel._get_sthula_status(mock_prakriti)
        assert sthula["icon"] == "❌"
        assert "Error" in sthula["details"]

        purusha = panel._get_purusha_status(mock_prakriti)
        assert purusha["icon"] == "❌"
        assert "Error" in purusha["details"]

        sync = panel._get_sync_status(mock_prakriti)
        assert sync["sync_icon"] == "❌"


class TestPrakritiStatePanelIntegration:
    """Integration tests with real Prakriti (if available)."""

    @pytest.fixture
    def real_prakriti(self):
        """Try to create real Prakriti instance."""
        try:
            from vibe_core.state.prakriti import Prakriti

            return Prakriti(Path("."))
        except Exception:
            pytest.skip("Prakriti not available")

    def test_real_prakriti_snapshot(self, real_prakriti):
        """Real Prakriti should provide valid snapshot."""
        snapshot = real_prakriti.snapshot()
        assert snapshot.timestamp > 0
        assert isinstance(snapshot.git, dict)
        assert isinstance(snapshot.files, dict)
