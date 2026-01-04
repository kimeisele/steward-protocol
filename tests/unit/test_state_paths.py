"""Tests for OPUS state paths module."""

import tempfile
from pathlib import Path

import pytest


class TestStatePaths:
    """Tests for state path resolution."""

    def test_import_state_files_constant(self):
        """Can import STATE_FILES constant."""
        from vibe_core.plugins.opus_assistant.core.state_paths import STATE_FILES

        assert "intents" in STATE_FILES
        assert STATE_FILES["intents"] == "manas_intents.json"
        assert STATE_FILES["synapses"] == "synapses.json"

    def test_import_state_dirs_constant(self):
        """Can import STATE_DIRS constant."""
        from vibe_core.plugins.opus_assistant.core.state_paths import STATE_DIRS

        assert "logs" in STATE_DIRS
        assert STATE_DIRS["logs"] == "logs"

    def test_get_opus_state_path_returns_path(self):
        """get_opus_state_path returns a Path object."""
        from vibe_core.plugins.opus_assistant.core.state_paths import get_opus_state_path

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            path = get_opus_state_path(workspace, "test.json")

            assert isinstance(path, Path)
            assert path.name == "test.json"
            # Should be under .vibe/state/plugins/opus_assistant/
            assert ".vibe" in str(path)
            assert "opus_assistant" in str(path)

    def test_save_creates_directory(self):
        """Saving creates parent directories automatically."""
        from vibe_core.plugins.opus_assistant.core.state_paths import (
            get_opus_state_path,
            save_opus_state,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir).resolve()

            # Save should create directory and file
            success = save_opus_state(workspace, "test.json", {"test": True})
            assert success

            # File and directory should now exist
            path = get_opus_state_path(workspace, "test.json")
            assert path.exists()

    def test_get_opus_state_service_returns_service(self):
        """get_opus_state_service returns a StateService instance."""
        from vibe_core.plugins.opus_assistant.core.state_paths import get_opus_state_service

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            service = get_opus_state_service(workspace)

            # Should have save/load methods
            assert hasattr(service, "save")
            assert hasattr(service, "load")
            assert hasattr(service, "append")

    def test_state_path_uses_plugin_namespace(self):
        """State path is under plugins/opus_assistant."""
        from vibe_core.plugins.opus_assistant.core.state_paths import get_opus_state_path

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir).resolve()  # Resolve symlinks for macOS
            path = get_opus_state_path(workspace, "test.json")

            # Should contain .vibe/state/plugins/opus_assistant/test.json
            path_str = str(path)
            assert ".vibe/state/plugins/opus_assistant/test.json" in path_str

    def test_load_opus_state_returns_default(self):
        """load_opus_state returns default when file doesn't exist."""
        from vibe_core.plugins.opus_assistant.core.state_paths import load_opus_state

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            result = load_opus_state(workspace, "nonexistent.json", default={"key": "value"})

            assert result == {"key": "value"}

    def test_save_and_load_opus_state(self):
        """Can save and load state."""
        from vibe_core.plugins.opus_assistant.core.state_paths import load_opus_state, save_opus_state

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            data = {"test": "data", "number": 42}

            # Save
            success = save_opus_state(workspace, "test.json", data)
            assert success

            # Load
            loaded = load_opus_state(workspace, "test.json")
            assert loaded == data

    def test_get_opus_state_dir_creates_directory(self):
        """get_opus_state_dir creates subdirectory."""
        from vibe_core.plugins.opus_assistant.core.state_paths import get_opus_state_dir

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            dir_path = get_opus_state_dir(workspace, "logs")

            assert dir_path.exists()
            assert dir_path.is_dir()
            assert dir_path.name == "logs"

    def test_get_legacy_path_returns_opus_state(self):
        """get_legacy_path returns .opus_state/ path."""
        from vibe_core.plugins.opus_assistant.core.state_paths import get_legacy_path

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            path = get_legacy_path(workspace, "test.json")

            assert ".opus_state" in str(path)
            assert path.name == "test.json"

    def test_has_legacy_state_false_when_missing(self):
        """has_legacy_state returns False when file doesn't exist."""
        from vibe_core.plugins.opus_assistant.core.state_paths import has_legacy_state

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            assert not has_legacy_state(workspace, "test.json")

    def test_has_legacy_state_true_when_exists(self):
        """has_legacy_state returns True when file exists."""
        from vibe_core.plugins.opus_assistant.core.state_paths import has_legacy_state

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            # Create legacy file
            legacy_dir = workspace / ".opus_state"
            legacy_dir.mkdir()
            (legacy_dir / "test.json").write_text("{}")

            assert has_legacy_state(workspace, "test.json")

    def test_append_opus_state(self):
        """Can append to JSONL file."""
        from vibe_core.plugins.opus_assistant.core.state_paths import (
            append_opus_state,
            get_opus_state_path,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)

            # Append entries
            assert append_opus_state(workspace, "test.jsonl", {"entry": 1})
            assert append_opus_state(workspace, "test.jsonl", {"entry": 2})

            # Read and verify
            path = get_opus_state_path(workspace, "test.jsonl")
            content = path.read_text()
            lines = content.strip().split("\n")
            assert len(lines) == 2


class TestStateFilesConstants:
    """Tests for STATE_FILES constant completeness."""

    def test_state_files_has_core_manas(self):
        """STATE_FILES includes core MANAS files."""
        from vibe_core.plugins.opus_assistant.core.state_paths import STATE_FILES

        assert "intents" in STATE_FILES
        assert "memory" in STATE_FILES
        assert "awareness" in STATE_FILES
        assert "session" in STATE_FILES

    def test_state_files_has_cognitive(self):
        """STATE_FILES includes cognitive state files."""
        from vibe_core.plugins.opus_assistant.core.state_paths import STATE_FILES

        assert "synapses" in STATE_FILES
        assert "decisions" in STATE_FILES
        assert "reinforcement" in STATE_FILES
        assert "karma" in STATE_FILES

    def test_state_files_has_strategic(self):
        """STATE_FILES includes strategic state files."""
        from vibe_core.plugins.opus_assistant.core.state_paths import STATE_FILES

        assert "sankalpa" in STATE_FILES
        assert "sutra_history" in STATE_FILES
        assert "sanskrit_matrix" in STATE_FILES
        assert "akshara_graph" in STATE_FILES


class TestImportFromCore:
    """Tests for importing from core module."""

    def test_import_all_from_core(self):
        """Can import all state path functions from core module."""
        from vibe_core.plugins.opus_assistant.core import (
            STATE_DIRS,
            STATE_FILES,
            append_opus_state,
            get_legacy_path,
            get_opus_state_dir,
            get_opus_state_path,
            get_opus_state_service,
            has_legacy_state,
            load_opus_state,
            save_opus_state,
        )

        # All should be callable or dict
        assert callable(get_opus_state_path)
        assert callable(get_opus_state_service)
        assert callable(get_opus_state_dir)
        assert callable(load_opus_state)
        assert callable(save_opus_state)
        assert callable(append_opus_state)
        assert callable(get_legacy_path)
        assert callable(has_legacy_state)
        assert isinstance(STATE_FILES, dict)
        assert isinstance(STATE_DIRS, dict)
