"""
Tests for OPUS StateManager - Plugin-Local State Abstraction

This tests the Fractal Holon pattern:
- Each plugin owns its state
- State is JSON-based and git-trackable
- Clean isolation from system-wide resources
"""

from datetime import datetime

import pytest

from vibe_core.plugins.opus_assistant.core.state_manager import (
    DEFAULT_STATE_DIR,
    KarmaEntry,
    ObservationEntry,
    OpusStateManager,
    SessionState,
    get_state_manager,
)


class TestStateManagerModule:
    """Test module imports and basics."""

    def test_module_importable(self):
        """StateManager module should be importable."""
        from vibe_core.plugins.opus_assistant.core import state_manager

        assert state_manager is not None

    def test_observation_entry_importable(self):
        """ObservationEntry should be importable."""
        assert ObservationEntry is not None

    def test_karma_entry_importable(self):
        """KarmaEntry should be importable."""
        assert KarmaEntry is not None

    def test_session_state_importable(self):
        """SessionState should be importable."""
        assert SessionState is not None

    def test_get_state_manager_importable(self):
        """get_state_manager should be importable."""
        assert get_state_manager is not None


class TestObservationEntry:
    """Test ObservationEntry dataclass."""

    def test_create_observation_entry(self):
        """Should create an observation entry."""
        entry = ObservationEntry(
            timestamp="2025-12-13T12:00:00",
            severity="ALERT",
            message="Test alert",
            source="test_source",
        )
        assert entry.timestamp == "2025-12-13T12:00:00"
        assert entry.severity == "ALERT"
        assert entry.message == "Test alert"
        assert entry.source == "test_source"
        assert entry.context_hash is None

    def test_to_dict(self):
        """Should convert to dict."""
        entry = ObservationEntry(
            timestamp="2025-12-13T12:00:00",
            severity="WARN",
            message="Test warning",
            source="test",
        )
        d = entry.to_dict()
        assert d["timestamp"] == "2025-12-13T12:00:00"
        assert d["severity"] == "WARN"
        assert d["message"] == "Test warning"

    def test_from_dict(self):
        """Should create from dict."""
        d = {
            "timestamp": "2025-12-13T12:00:00",
            "severity": "ALERT",
            "message": "From dict",
            "source": "dict_source",
        }
        entry = ObservationEntry.from_dict(d)
        assert entry.timestamp == "2025-12-13T12:00:00"
        assert entry.severity == "ALERT"
        assert entry.message == "From dict"


class TestKarmaEntry:
    """Test KarmaEntry dataclass."""

    def test_create_karma_entry(self):
        """Should create a karma entry."""
        entry = KarmaEntry(
            timestamp="2025-12-13T12:00:00",
            score=75,
            error_count=2,
            warning_count=5,
        )
        assert entry.score == 75
        assert entry.error_count == 2
        assert entry.warning_count == 5
        assert entry.boot_mode == "full_power"

    def test_karma_entry_to_dict(self):
        """Should convert to dict."""
        entry = KarmaEntry(
            timestamp="2025-12-13T12:00:00",
            score=50,
            crash_count=1,
        )
        d = entry.to_dict()
        assert d["score"] == 50
        assert d["crash_count"] == 1


class TestOpusStateManager:
    """Test OpusStateManager class."""

    @pytest.fixture
    def temp_plugin_root(self, tmp_path):
        """Create a temporary plugin root."""
        return tmp_path / "opus_assistant"

    @pytest.fixture
    def state_manager(self, temp_plugin_root):
        """Create a state manager with temp directory."""
        return OpusStateManager(plugin_root=temp_plugin_root)

    def test_creates_state_dir(self, state_manager, temp_plugin_root):
        """Should create state directory on init."""
        state_dir = temp_plugin_root / DEFAULT_STATE_DIR
        assert state_dir.exists()
        assert (state_dir / ".gitkeep").exists()

    def test_state_dir_property(self, state_manager, temp_plugin_root):
        """Should expose state_dir property."""
        expected = temp_plugin_root / DEFAULT_STATE_DIR
        assert state_manager.state_dir == expected

    def test_append_observation_alert(self, state_manager):
        """Should persist ALERT observations."""
        entry = ObservationEntry(
            timestamp=datetime.now().isoformat(),
            severity="ALERT",
            message="Test alert",
            source="test",
        )
        result = state_manager.append_observation(entry)
        assert result is True

        # Verify it was written
        obs = state_manager.get_observations()
        assert len(obs) == 1
        assert obs[0].severity == "ALERT"

    def test_append_observation_warn(self, state_manager):
        """Should persist WARN observations."""
        entry = ObservationEntry(
            timestamp=datetime.now().isoformat(),
            severity="WARN",
            message="Test warning",
            source="test",
        )
        result = state_manager.append_observation(entry)
        assert result is True

        obs = state_manager.get_observations()
        assert len(obs) == 1
        assert obs[0].severity == "WARN"

    def test_skip_info_observation(self, state_manager):
        """Should NOT persist INFO observations (transient)."""
        entry = ObservationEntry(
            timestamp=datetime.now().isoformat(),
            severity="INFO",
            message="Test info",
            source="test",
        )
        result = state_manager.append_observation(entry)
        assert result is True  # Returns True but doesn't persist

        obs = state_manager.get_observations()
        assert len(obs) == 0  # Not persisted

    def test_record_karma(self, state_manager):
        """Should record karma entries."""
        entry = KarmaEntry(
            timestamp=datetime.now().isoformat(),
            score=85,
            error_count=1,
        )
        result = state_manager.record_karma(entry)
        assert result is True

        history = state_manager.get_karma_history()
        assert len(history) == 1
        assert history[0].score == 85

    def test_get_last_karma(self, state_manager):
        """Should get last karma entry."""
        # Add multiple entries
        for score in [100, 90, 80]:
            entry = KarmaEntry(
                timestamp=datetime.now().isoformat(),
                score=score,
            )
            state_manager.record_karma(entry)

        last = state_manager.get_last_karma()
        assert last is not None
        assert last.score == 80  # Last one added

    def test_save_and_load_session(self, state_manager):
        """Should save and load session state."""
        session = SessionState(
            session_id="test-session-123",
            started_at=datetime.now().isoformat(),
            last_karma_score=95,
            observation_count=5,
        )
        state_manager.save_session(session)

        loaded = state_manager.load_session()
        assert loaded is not None
        assert loaded.session_id == "test-session-123"
        assert loaded.last_karma_score == 95

    def test_clear_all(self, state_manager):
        """Should clear all state."""
        # Add some data
        obs = ObservationEntry(
            timestamp=datetime.now().isoformat(),
            severity="ALERT",
            message="Test",
            source="test",
        )
        state_manager.append_observation(obs)

        karma = KarmaEntry(timestamp=datetime.now().isoformat(), score=50)
        state_manager.record_karma(karma)

        # Clear
        state_manager.clear_all()

        # Verify cleared
        assert len(state_manager.get_observations()) == 0
        assert len(state_manager.get_karma_history()) == 0
        assert state_manager.load_session() is None

    def test_get_stats(self, state_manager):
        """Should return stats."""
        stats = state_manager.get_stats()
        assert "state_dir" in stats
        assert "observation_count" in stats
        assert "karma_entry_count" in stats


class TestGetStateManager:
    """Test get_state_manager convenience function."""

    def test_auto_detects_plugin_root(self):
        """Should auto-detect plugin root."""
        # This should work when called from within the plugin
        manager = get_state_manager()
        assert manager is not None
        assert isinstance(manager, OpusStateManager)

    def test_accepts_custom_root(self, tmp_path):
        """Should accept custom plugin root."""
        manager = get_state_manager(plugin_root=tmp_path)
        assert manager.state_dir == tmp_path / DEFAULT_STATE_DIR


class TestStateManagerIntegration:
    """Integration tests for StateManager with other components."""

    def test_observation_logger_uses_state_manager(self, tmp_path):
        """ObservationLogger should use StateManager for persistence."""
        from vibe_core.plugins.opus_assistant.core.observation_logger import (
            ObservationLogger,
        )

        # Create state manager
        state_mgr = OpusStateManager(plugin_root=tmp_path / "plugin")

        # Create logger with state manager
        logger = ObservationLogger(
            workspace_root=tmp_path,
            state_manager=state_mgr,
        )

        # Log an ALERT
        logger.log_alert("Test integration alert", source="integration_test")

        # Verify it was persisted
        obs = state_mgr.get_observations()
        assert len(obs) == 1
        assert obs[0].severity == "ALERT"
        assert "Test integration alert" in obs[0].message

    def test_observations_newest_first(self, tmp_path):
        """Observations should be returned newest first."""
        state_mgr = OpusStateManager(plugin_root=tmp_path)

        # Add observations in order
        for i in range(3):
            entry = ObservationEntry(
                timestamp=f"2025-12-13T12:0{i}:00",
                severity="ALERT",
                message=f"Message {i}",
                source="test",
            )
            state_mgr.append_observation(entry)

        # Get observations - should be newest first
        obs = state_mgr.get_observations()
        assert len(obs) == 3
        assert "Message 2" in obs[0].message  # Newest
        assert "Message 0" in obs[2].message  # Oldest
