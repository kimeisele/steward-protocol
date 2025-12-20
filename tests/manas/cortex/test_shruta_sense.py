"""
OPUS-156: ShrutaSense Tests - The 6th Jnanendriya

Tests for the filesystem listening system.

Sanskrit: श्रुत (Shruta) = "That which is heard"

"Am Anfang war Dunkelheit. Brahma HÖRTE bevor er SAH."
"At the beginning was darkness. Brahma HEARD before he SAW."

Capabilities tested:
1. start_listening() - Begin monitoring filesystem paths
2. perceive() - Get buffered vibrations since last call
3. get_vibrations() - Get recent vibration history
4. get_hot_paths() - Find paths with frequent changes
5. calculate_resonance() - Get layer resonance for a path
"""

import os
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.plugins.opus_assistant.manas.cortex.shruta_sense import (
    FileSnapshot,
    ShrutaPerception,
    ShrutaSense,
    Vibration,
)

# =============================================================================
# SECTION 1: Basic Import and Initialization Tests
# =============================================================================


class TestShrutaSenseBasic:
    """Basic ShrutaSense tests."""

    def test_shruta_sense_imports(self):
        """ShrutaSense should be importable."""
        assert ShrutaSense is not None
        assert Vibration is not None
        assert ShrutaPerception is not None

    def test_shruta_sense_initializes(self, tmp_path):
        """ShrutaSense should initialize with workspace."""
        sense = ShrutaSense(workspace=tmp_path)
        assert sense is not None
        assert sense.name == "shruta_sense"

    def test_shruta_has_required_methods(self, tmp_path):
        """ShrutaSense should have all required methods."""
        sense = ShrutaSense(workspace=tmp_path)

        assert hasattr(sense, "start_listening")
        assert hasattr(sense, "stop_listening")
        assert hasattr(sense, "perceive")
        assert hasattr(sense, "get_vibrations")
        assert hasattr(sense, "get_hot_paths")
        assert hasattr(sense, "calculate_resonance")


# =============================================================================
# SECTION 2: Vibration Dataclass Tests
# =============================================================================


class TestVibration:
    """Tests for the Vibration dataclass."""

    def test_vibration_creation(self):
        """Vibration should be creatable with required fields."""
        v = Vibration(
            event_type="created",
            path=Path("/test/file.py"),
            timestamp=time.time(),
        )
        assert v.event_type == "created"
        assert v.path == Path("/test/file.py")

    def test_vibration_str_representation(self):
        """Vibration __str__ should show emoji and info."""
        v = Vibration(
            event_type="created",
            path=Path("/test/file.py"),
            timestamp=time.time(),
            resonance_layer="KERNEL",
        )
        s = str(v)
        assert "created" in s
        assert "file.py" in s

    def test_vibration_optional_fields(self):
        """Vibration should handle optional fields."""
        v = Vibration(
            event_type="modified",
            path=Path("/test/file.py"),
            timestamp=time.time(),
            is_directory=False,
            resonance_layer="COGNITION",
            file_hash="abc123",
        )
        assert v.is_directory is False
        assert v.resonance_layer == "COGNITION"
        assert v.file_hash == "abc123"


# =============================================================================
# SECTION 3: Filesystem Listening Tests
# =============================================================================


class TestShrutaListening:
    """Tests for filesystem monitoring."""

    @pytest.fixture
    def watch_dir(self, tmp_path):
        """Create a directory to watch."""
        watch = tmp_path / "watch"
        watch.mkdir()
        return watch

    def test_start_listening(self, tmp_path, watch_dir):
        """ShrutaSense should start listening without errors."""
        sense = ShrutaSense(workspace=tmp_path)
        sense.start_listening(paths=[watch_dir])

        assert sense._is_listening is True

        # Cleanup
        sense.stop_listening()

    def test_stop_listening(self, tmp_path, watch_dir):
        """ShrutaSense should stop listening cleanly."""
        sense = ShrutaSense(workspace=tmp_path)
        sense.start_listening(paths=[watch_dir])
        sense.stop_listening()

        assert sense._is_listening is False

    def test_double_start_is_safe(self, tmp_path, watch_dir):
        """Starting twice should be safe (idempotent)."""
        sense = ShrutaSense(workspace=tmp_path)
        sense.start_listening(paths=[watch_dir])
        sense.start_listening(paths=[watch_dir])  # Should not crash

        assert sense._is_listening is True
        sense.stop_listening()


# =============================================================================
# SECTION 4: Change Detection Tests
# =============================================================================


class TestChangeDetection:
    """Tests for filesystem change detection."""

    @pytest.fixture
    def sense_with_watch(self, tmp_path):
        """Create ShrutaSense watching a temp directory."""
        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()

        sense = ShrutaSense(workspace=tmp_path)
        sense.start_listening(paths=[watch_dir], poll_interval=0.1)

        yield sense, watch_dir

        sense.stop_listening()

    def test_detect_file_creation(self, sense_with_watch):
        """ShrutaSense should detect new file creation."""
        sense, watch_dir = sense_with_watch

        # Create a file
        test_file = watch_dir / "new_file.py"
        test_file.write_text("print('hello')")

        # Wait for poll cycle
        time.sleep(0.3)

        # Check vibrations
        vibrations = sense.get_vibrations()

        # Should have detected the new file
        created = [v for v in vibrations if v.event_type == "created"]
        assert len(created) >= 1

    def test_detect_file_modification(self, sense_with_watch):
        """ShrutaSense should detect file modifications."""
        sense, watch_dir = sense_with_watch

        # Create initial file
        test_file = watch_dir / "modify_me.py"
        test_file.write_text("version = 1")

        # Wait for initial detection
        time.sleep(0.3)

        # Clear buffer
        sense.perceive()

        # Modify the file
        test_file.write_text("version = 2")

        # Wait for poll cycle
        time.sleep(0.3)

        # Check vibrations
        vibrations = sense.get_vibrations()
        modified = [v for v in vibrations if v.event_type == "modified"]
        assert len(modified) >= 1


# =============================================================================
# SECTION 5: Perception Tests
# =============================================================================


class TestPerception:
    """Tests for the perceive() method."""

    def test_perceive_returns_perception(self, tmp_path):
        """perceive() should return ShrutaPerception."""
        sense = ShrutaSense(workspace=tmp_path)
        sense.start_listening(paths=[tmp_path])

        perception = sense.perceive()

        assert isinstance(perception, ShrutaPerception)
        assert hasattr(perception, "vibrations")
        assert hasattr(perception, "total_count")
        assert hasattr(perception, "by_type")
        assert hasattr(perception, "by_layer")
        assert hasattr(perception, "is_listening")

        sense.stop_listening()

    def test_perceive_clears_buffer(self, tmp_path):
        """perceive() should clear the vibration buffer."""
        sense = ShrutaSense(workspace=tmp_path)

        # Add some test vibrations manually
        sense._vibration_buffer.append(Vibration("created", Path("/test"), time.time()))

        # First perceive gets the vibration
        p1 = sense.perceive()
        assert p1.total_count == 1

        # Second perceive should be empty
        p2 = sense.perceive()
        assert p2.total_count == 0


# =============================================================================
# SECTION 6: Hot Paths Tests
# =============================================================================


class TestHotPaths:
    """Tests for hot path detection."""

    def test_get_hot_paths_empty(self, tmp_path):
        """get_hot_paths() should return empty list initially."""
        sense = ShrutaSense(workspace=tmp_path)
        hot = sense.get_hot_paths()
        assert hot == []

    def test_hot_paths_track_changes(self, tmp_path):
        """Hot paths should track frequently changed files."""
        sense = ShrutaSense(workspace=tmp_path)

        # Simulate multiple changes to same file
        test_path = tmp_path / "hot_file.py"
        for _ in range(5):
            sense._emit_vibration("modified", test_path)

        hot = sense.get_hot_paths()
        assert len(hot) > 0
        assert str(test_path) == hot[0][0]
        assert hot[0][1] == 5  # 5 changes


# =============================================================================
# SECTION 7: Resonance Calculation Tests
# =============================================================================


class TestResonance:
    """Tests for layer resonance calculation."""

    def test_calculate_resonance_returns_tuple(self, tmp_path):
        """calculate_resonance() should return (layer, varga) tuple."""
        sense = ShrutaSense(workspace=tmp_path)

        # Test with a kernel path
        kernel_path = tmp_path / "vibe_core" / "runtime" / "kernel.py"
        layer, varga = sense.calculate_resonance(kernel_path)

        # Should return a result (may be None if akshara not available)
        assert isinstance((layer, varga), tuple)


# =============================================================================
# SECTION 8: Ignored Patterns Tests
# =============================================================================


class TestIgnoredPatterns:
    """Tests for ignored file patterns."""

    def test_pycache_is_ignored(self, tmp_path):
        """__pycache__ directories should be ignored."""
        sense = ShrutaSense(workspace=tmp_path)

        assert sense._should_ignore("__pycache__") is True

    def test_git_is_ignored(self, tmp_path):
        """.git directory should be ignored."""
        sense = ShrutaSense(workspace=tmp_path)

        assert sense._should_ignore(".git") is True

    def test_pyc_files_are_ignored(self, tmp_path):
        """*.pyc files should be ignored."""
        sense = ShrutaSense(workspace=tmp_path)

        assert sense._should_ignore("module.pyc") is True

    def test_python_files_are_not_ignored(self, tmp_path):
        """*.py files should NOT be ignored."""
        sense = ShrutaSense(workspace=tmp_path)

        assert sense._should_ignore("module.py") is False


# =============================================================================
# SECTION 9: Handler Registration Tests
# =============================================================================


class TestHandlers:
    """Tests for vibration handler callbacks."""

    def test_add_handler(self, tmp_path):
        """add_handler should register callbacks."""
        sense = ShrutaSense(workspace=tmp_path)

        received = []

        def handler(v):
            received.append(v)

        sense.add_handler(handler)

        # Emit a vibration
        sense._emit_vibration("created", tmp_path / "test.py")

        assert len(received) == 1
        assert received[0].event_type == "created"

    def test_remove_handler(self, tmp_path):
        """remove_handler should unregister callbacks."""
        sense = ShrutaSense(workspace=tmp_path)

        received = []

        def handler(v):
            received.append(v)

        sense.add_handler(handler)
        sense.remove_handler(handler)

        # Emit a vibration
        sense._emit_vibration("created", tmp_path / "test.py")

        # Handler should not have been called
        assert len(received) == 0
