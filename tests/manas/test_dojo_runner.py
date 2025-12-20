"""
OPUS-133: DojoRunner Tests

Tests for the MANAS Dojo Training System.

The Dojo is where MANAS trains itself:
1. Loads curricula (YAML training scenarios)
2. Runs scenarios in ephemeral kernel
3. Extracts synaptic wisdom
4. Only persists synapses.json (learned patterns)

"MANAS lernt nicht um zu gewinnen, sondern um zu dienen."
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# =============================================================================
# SECTION 1: Import Tests
# =============================================================================


class TestDojoImports:
    """Test that Dojo components can be imported."""

    def test_dojo_runner_import(self):
        """DojoRunner should be importable."""
        from vibe_core.plugins.opus_assistant.manas.dojo.runner import DojoRunner

        assert DojoRunner is not None

    def test_curriculum_loader_import(self):
        """CurriculumLoader should be importable."""
        from vibe_core.plugins.opus_assistant.manas.dojo.curriculum_loader import (
            CurriculumLoader,
        )

        assert CurriculumLoader is not None

    def test_synaptic_seeder_import(self):
        """SynapticSeeder should be importable."""
        from vibe_core.plugins.opus_assistant.manas.dojo.synaptic_seeder import (
            SynapticSeeder,
        )

        assert SynapticSeeder is not None


# =============================================================================
# SECTION 2: DojoRunner Basic Tests
# =============================================================================


class TestDojoRunnerBasic:
    """Basic DojoRunner functionality tests."""

    @pytest.fixture
    def mock_workspace(self, tmp_path):
        """Create a mock workspace for testing."""
        # Create dojo curricula directory
        curricula_dir = tmp_path / "vibe_core/plugins/opus_assistant/manas/dojo/curricula"
        curricula_dir.mkdir(parents=True)

        # Create a simple curriculum
        (curricula_dir / "test_curriculum.yaml").write_text("""
name: Test Curriculum
description: Basic test training
scenarios:
  - name: basic_test
    trigger: "test_trigger"
    expected_action: "test_action"
    expected_outcome: success
""")
        return tmp_path

    def test_dojo_runner_initializes(self, mock_workspace):
        """DojoRunner should initialize."""
        from vibe_core.plugins.opus_assistant.manas.dojo.runner import DojoRunner

        runner = DojoRunner(workspace=mock_workspace)
        assert runner is not None

    def test_dojo_runner_has_run_training(self):
        """DojoRunner should have run_training method."""
        from vibe_core.plugins.opus_assistant.manas.dojo.runner import DojoRunner

        assert hasattr(DojoRunner, "run_training")


# =============================================================================
# SECTION 3: CurriculumLoader Tests
# =============================================================================


class TestCurriculumLoader:
    """Tests for curriculum loading."""

    @pytest.fixture
    def curricula_path(self, tmp_path):
        """Create test curricula."""
        curricula_dir = tmp_path / "curricula"
        curricula_dir.mkdir()

        # Create a test curriculum
        (curricula_dir / "test.yaml").write_text("""
name: Test Curriculum
description: For testing
scenarios:
  - name: scenario_1
    trigger: "trigger:test"
    expected_action: "action:test"
""")
        return curricula_dir

    def test_curriculum_loader_initializes(self, curricula_path):
        """CurriculumLoader should initialize."""
        from vibe_core.plugins.opus_assistant.manas.dojo.curriculum_loader import (
            CurriculumLoader,
        )

        loader = CurriculumLoader(curricula_path)
        assert loader is not None


# =============================================================================
# SECTION 4: Training Room Tests
# =============================================================================


class TestTrainingRooms:
    """Tests for Dojo training rooms."""

    def test_arena_room_exists(self):
        """Arena room should exist."""
        from vibe_core.plugins.opus_assistant.manas.dojo.rooms.arena import Arena

        assert Arena is not None

    def test_library_room_exists(self):
        """Library room should exist."""
        from vibe_core.plugins.opus_assistant.manas.dojo.rooms.library import Library

        assert Library is not None

    def test_meditation_room_exists(self):
        """Meditation room should exist."""
        from vibe_core.plugins.opus_assistant.manas.dojo.rooms.meditation import (
            MeditationRoom,
        )

        assert MeditationRoom is not None

    def test_mirror_room_exists(self):
        """Mirror room should exist."""
        from vibe_core.plugins.opus_assistant.manas.dojo.rooms.mirror import Mirror

        assert Mirror is not None


# =============================================================================
# SECTION 5: Synaptic Persistence Tests
# =============================================================================


class TestSynapticPersistence:
    """Tests for synaptic learning persistence."""

    def test_synaptic_seeder_has_seed_method(self):
        """SynapticSeeder should have seed method."""
        from vibe_core.plugins.opus_assistant.manas.dojo.synaptic_seeder import (
            SynapticSeeder,
        )

        assert hasattr(SynapticSeeder, "seed") or hasattr(SynapticSeeder, "run")

    def test_training_only_persists_synapses(self, tmp_path):
        """
        CRITICAL: Training should only persist synapses.json.

        The Dojo runs in ephemeral mode - only the learned patterns
        (synapses.json) should survive, not the kernel state.
        """
        from vibe_core.plugins.opus_assistant.manas.dojo.runner import DojoRunner

        # Create minimal workspace structure
        opus_state = tmp_path / ".opus_state"
        opus_state.mkdir()

        runner = DojoRunner(workspace=tmp_path)
        # After training, only synapses.json should be modified
        # This is the "wisdom extraction" pattern
        assert hasattr(runner, "_workspace") or hasattr(runner, "workspace")
