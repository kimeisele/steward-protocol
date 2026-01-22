"""
TESTS: venu/voice.py - MantraVoice Parallel Execution
======================================================

REAL TESTS for:
1. MantraVoice class
2. voice_id property
3. submit method
4. get_tasks method
5. clear method
"""

import pytest
from vibe_core.mahamantra.venu.voice import MantraVoice
from vibe_core.mahamantra.protocols._venu import VENU_POSITIONS


# =============================================================================
# MantraVoice Tests
# =============================================================================


class TestMantraVoice:
    """Test MantraVoice class."""

    def test_mantra_voice_creation(self):
        """MantraVoice can be created."""
        voice = MantraVoice(voice_id=0)
        assert voice is not None

    def test_mantra_voice_id(self):
        """MantraVoice has voice_id property."""
        voice = MantraVoice(voice_id=42)
        assert voice.voice_id == 42

    def test_mantra_voice_initial_empty(self):
        """MantraVoice starts with no tasks."""
        voice = MantraVoice(voice_id=0)
        for pos in range(VENU_POSITIONS):
            assert voice.get_tasks(pos) == []

    def test_mantra_voice_submit_task(self):
        """submit adds task to specified position."""
        voice = MantraVoice(voice_id=0)
        task = lambda: "test"
        voice.submit(task, position=5)
        tasks = voice.get_tasks(5)
        assert len(tasks) == 1

    def test_mantra_voice_submit_default_position(self):
        """submit uses position 0 by default."""
        voice = MantraVoice(voice_id=0)
        task = lambda: "test"
        voice.submit(task)
        tasks = voice.get_tasks(0)
        assert len(tasks) == 1

    def test_mantra_voice_submit_multiple_tasks(self):
        """submit can add multiple tasks to same position."""
        voice = MantraVoice(voice_id=0)
        voice.submit(lambda: 1, position=3)
        voice.submit(lambda: 2, position=3)
        voice.submit(lambda: 3, position=3)
        tasks = voice.get_tasks(3)
        assert len(tasks) == 3

    def test_mantra_voice_submit_different_positions(self):
        """submit can add tasks to different positions."""
        voice = MantraVoice(voice_id=0)
        voice.submit(lambda: 1, position=0)
        voice.submit(lambda: 2, position=5)
        voice.submit(lambda: 3, position=15)

        assert len(voice.get_tasks(0)) == 1
        assert len(voice.get_tasks(5)) == 1
        assert len(voice.get_tasks(15)) == 1

    def test_mantra_voice_submit_invalid_position_low(self):
        """submit raises for position < 0."""
        voice = MantraVoice(voice_id=0)
        with pytest.raises(ValueError):
            voice.submit(lambda: 1, position=-1)

    def test_mantra_voice_submit_invalid_position_high(self):
        """submit raises for position >= VENU_POSITIONS."""
        voice = MantraVoice(voice_id=0)
        with pytest.raises(ValueError):
            voice.submit(lambda: 1, position=VENU_POSITIONS)

    def test_mantra_voice_get_tasks_returns_copy(self):
        """get_tasks returns a copy of the task list."""
        voice = MantraVoice(voice_id=0)
        voice.submit(lambda: 1, position=0)
        tasks1 = voice.get_tasks(0)
        tasks2 = voice.get_tasks(0)
        # Should be equal but not same object
        assert tasks1 == tasks2
        assert tasks1 is not tasks2

    def test_mantra_voice_get_tasks_invalid_position(self):
        """get_tasks raises for invalid position."""
        voice = MantraVoice(voice_id=0)
        with pytest.raises(ValueError):
            voice.get_tasks(-1)
        with pytest.raises(ValueError):
            voice.get_tasks(VENU_POSITIONS)

    def test_mantra_voice_clear(self):
        """clear removes all tasks at position."""
        voice = MantraVoice(voice_id=0)
        voice.submit(lambda: 1, position=5)
        voice.submit(lambda: 2, position=5)
        assert len(voice.get_tasks(5)) == 2

        voice.clear(5)
        assert len(voice.get_tasks(5)) == 0

    def test_mantra_voice_clear_only_specified_position(self):
        """clear only affects specified position."""
        voice = MantraVoice(voice_id=0)
        voice.submit(lambda: 1, position=5)
        voice.submit(lambda: 2, position=10)

        voice.clear(5)
        assert len(voice.get_tasks(5)) == 0
        assert len(voice.get_tasks(10)) == 1

    def test_mantra_voice_clear_invalid_position(self):
        """clear raises for invalid position."""
        voice = MantraVoice(voice_id=0)
        with pytest.raises(ValueError):
            voice.clear(-1)
        with pytest.raises(ValueError):
            voice.clear(VENU_POSITIONS)

    def test_mantra_voice_repr(self):
        """MantraVoice has string representation."""
        voice = MantraVoice(voice_id=42)
        rep = repr(voice)
        assert "MantraVoice" in rep
        assert "id=42" in rep
        assert "tasks=" in rep

    def test_mantra_voice_repr_shows_task_count(self):
        """repr shows total task count."""
        voice = MantraVoice(voice_id=0)
        voice.submit(lambda: 1, position=0)
        voice.submit(lambda: 2, position=5)
        voice.submit(lambda: 3, position=10)
        rep = repr(voice)
        assert "tasks=3" in rep

    def test_mantra_voice_task_execution(self):
        """Tasks can be executed after retrieval."""
        voice = MantraVoice(voice_id=0)
        results = []
        voice.submit(lambda: results.append(1), position=0)
        voice.submit(lambda: results.append(2), position=0)

        tasks = voice.get_tasks(0)
        for task in tasks:
            task()

        assert results == [1, 2]


# =============================================================================
# Multiple Voices Tests
# =============================================================================


class TestMultipleVoices:
    """Test multiple MantraVoice instances."""

    def test_multiple_voices_independent(self):
        """Multiple voices are independent."""
        voice1 = MantraVoice(voice_id=0)
        voice2 = MantraVoice(voice_id=1)

        voice1.submit(lambda: 1, position=5)
        voice2.submit(lambda: 2, position=5)

        assert len(voice1.get_tasks(5)) == 1
        assert len(voice2.get_tasks(5)) == 1

    def test_multiple_voices_different_ids(self):
        """Multiple voices have different IDs."""
        voice1 = MantraVoice(voice_id=0)
        voice2 = MantraVoice(voice_id=1)
        voice3 = MantraVoice(voice_id=2)

        assert voice1.voice_id != voice2.voice_id
        assert voice2.voice_id != voice3.voice_id
        assert voice1.voice_id != voice3.voice_id
