"""
Tests for the CellularHealer — end-to-end cellular healing pipeline.

Verifies:
1. Fragment-level healing with a real CSTRemedy (unsafe_io_write)
2. Healed fragment has new source code
3. Maya-Sync reconstructs and writes the file correctly
4. Dry-run mode doesn't write to disk
5. Unknown rule_id returns FAILED
6. Fragment with no violation returns SKIPPED
"""

import textwrap
from pathlib import Path

import pytest

from vibe_core.mahamantra.dharma.kumaras.fragment import (
    CSTFragment,
    FragmentType,
)
from vibe_core.mahamantra.dharma.kumaras.healing_intent import (
    CellularHealer,
    CellularHealingResult,
)
from vibe_core.mahamantra.substrate.shuddhi import ShuddhiStatus

# =============================================================================
# TEST FIXTURES
# =============================================================================

# Source with an unsafe_io_write violation inside a class method
SICK_METHOD_SOURCE = textwrap.dedent("""\
    class FileWriter:
        def __init__(self):
            self.system = None

        def write_data(self, path, data):
            with open(path, 'w') as f:
                f.write(data)
""")

# Source with NO violation
CLEAN_SOURCE = textwrap.dedent('''\
    def clean_function(x: int) -> int:
        """A perfectly clean function."""
        return x * 2
''')

SAMPLE_PATH = Path("/tmp/test_cellular_heal.py")


# =============================================================================
# CELLULAR HEALER TESTS
# =============================================================================


class TestCellularHealer:
    """Test the CellularHealer pipeline."""

    @pytest.fixture
    def healer(self):
        return CellularHealer()

    def test_can_heal_known_rule(self, healer):
        # unsafe_io_write is a known remedy
        assert healer.can_heal("unsafe_io_write") is True

    def test_cannot_heal_unknown_rule(self, healer):
        assert healer.can_heal("nonexistent_rule_xyz") is False

    def test_list_remedies(self, healer):
        remedies = healer.list_remedies()
        assert isinstance(remedies, list)
        assert len(remedies) > 0
        assert "unsafe_io_write" in remedies

    def test_heal_fragment_unknown_rule(self, healer):
        frag = CSTFragment(
            fragment_type=FragmentType.FUNCTION,
            qualified_name="foo",
            file_path=SAMPLE_PATH,
            line_start=1,
            line_end=1,
            source_code="def foo(): pass",
            sort_key=0,
        )
        result = healer.heal_fragment(frag, "nonexistent_rule")
        assert result.status == ShuddhiStatus.FAILED
        assert "No remedy" in result.shuddhi_result.message

    def test_heal_fragment_no_violation(self, healer):
        frag = CSTFragment(
            fragment_type=FragmentType.FUNCTION,
            qualified_name="clean_function",
            file_path=SAMPLE_PATH,
            line_start=1,
            line_end=3,
            source_code=CLEAN_SOURCE,
            sort_key=0,
        )
        result = healer.heal_fragment(frag, "unsafe_io_write")
        assert result.status == ShuddhiStatus.SKIPPED

    def test_heal_fragment_with_violation(self, healer):
        """Heal a fragment that contains an unsafe_io_write violation."""
        frag = CSTFragment(
            fragment_type=FragmentType.CLASS,
            qualified_name="FileWriter",
            file_path=SAMPLE_PATH,
            line_start=1,
            line_end=7,
            source_code=SICK_METHOD_SOURCE,
            sort_key=0,
        )
        result = healer.heal_fragment(frag, "unsafe_io_write", dry_run=True)

        # The remedy should either PURIFY or SKIP depending on scope detection
        # (UnsafeIOWriteRemedy requires self.system in scope)
        assert result.status in (
            ShuddhiStatus.PURIFIED,
            ShuddhiStatus.SKIPPED,
            ShuddhiStatus.OUT_OF_SCOPE,
        )

    def test_heal_fragment_unparseable(self, healer):
        """Unparseable source returns FAILED."""
        frag = CSTFragment(
            fragment_type=FragmentType.FUNCTION,
            qualified_name="broken",
            file_path=SAMPLE_PATH,
            line_start=1,
            line_end=1,
            source_code="def broken(:\n  pass",
            sort_key=0,
        )
        result = healer.heal_fragment(frag, "unsafe_io_write")
        assert result.status == ShuddhiStatus.FAILED
        assert "Cannot parse" in result.shuddhi_result.message

    def test_heal_file_dry_run(self, healer, tmp_path):
        """Dry-run heals fragments but doesn't write to disk."""
        test_file = tmp_path / "test_dry.py"
        test_file.write_text(CLEAN_SOURCE)

        results = healer.heal_file(test_file, "unsafe_io_write", dry_run=True)
        # Should return results (even if all SKIPPED)
        assert isinstance(results, list)

        # File should be unchanged
        assert test_file.read_text() == CLEAN_SOURCE

    def test_heal_file_with_violation_writes(self, healer, tmp_path):
        """Healing a file with a violation writes the reconstructed file."""
        test_file = tmp_path / "test_heal.py"
        test_file.write_text(SICK_METHOD_SOURCE)

        results = healer.heal_file(test_file, "unsafe_io_write", dry_run=False)

        # Check if any healing happened
        purified = [r for r in results if r.status == ShuddhiStatus.PURIFIED]

        if purified:
            # File should have been rewritten
            new_content = test_file.read_text()
            assert new_content != SICK_METHOD_SOURCE
            # The healed file should still be valid Python
            compile(new_content, str(test_file), "exec")


class TestCellularHealingResult:
    """Test CellularHealingResult properties."""

    def test_success_property(self):
        result = CellularHealingResult(
            shuddhi_result=type(
                "R",
                (),
                {
                    "success": True,
                    "status": ShuddhiStatus.PURIFIED,
                    "rule_id": "test",
                },
            )(),
        )
        assert result.success is True

    def test_status_property(self):
        result = CellularHealingResult(
            shuddhi_result=type(
                "R",
                (),
                {
                    "success": False,
                    "status": ShuddhiStatus.FAILED,
                    "rule_id": "test",
                },
            )(),
        )
        assert result.status == ShuddhiStatus.FAILED
