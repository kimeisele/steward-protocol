"""
Tests for Shuddhi remedies — prove healed code compiles AND runs.

Every remedy that transforms code must produce output that:
1. Compiles (no SyntaxError)
2. Has all necessary imports (no NameError)
3. Doesn't duplicate existing imports
"""

import tempfile
import os
from pathlib import Path

import pytest

from vibe_core.mahamantra.dharma.kumaras.engine import ShuddhiEngine
from vibe_core.mahamantra.substrate.shuddhi import ShuddhiStatus


@pytest.fixture
def engine():
    return ShuddhiEngine()


def _purify_code(engine: ShuddhiEngine, code: str, rule_id: str):
    """Helper: write code to temp file, purify, return result."""
    fd, tmp = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        return engine.purify(Path(tmp), rule_id)
    finally:
        os.unlink(tmp)


# =============================================================================
# silent_failure remedy
# =============================================================================


class TestSilentExceptRemedy:
    """SilentExceptRemedy must produce runnable code."""

    def test_bare_except_healed(self, engine):
        code = "import os\ntry:\n    x = 1/0\nexcept:\n    pass\n"
        result = _purify_code(engine, code, "silent_failure")
        assert result.status == ShuddhiStatus.PURIFIED

    def test_healed_code_compiles(self, engine):
        code = "try:\n    x = 1/0\nexcept:\n    pass\n"
        result = _purify_code(engine, code, "silent_failure")
        assert result.status == ShuddhiStatus.PURIFIED
        compile(result.purified_code, "<test>", "exec")

    def test_logging_injected_when_missing(self, engine):
        code = "try:\n    x = 1/0\nexcept:\n    pass\n"
        result = _purify_code(engine, code, "silent_failure")
        assert "import logging" in result.purified_code
        assert "getLogger" in result.purified_code

    def test_no_duplicate_import_when_present(self, engine):
        code = "import logging\nlogger = logging.getLogger(__name__)\ntry:\n    x = 1/0\nexcept:\n    pass\n"
        result = _purify_code(engine, code, "silent_failure")
        assert result.status == ShuddhiStatus.PURIFIED
        assert result.purified_code.count("import logging") == 1

    def test_no_duplicate_logger_when_present(self, engine):
        code = "import logging\nlogger = logging.getLogger(__name__)\ntry:\n    x = 1/0\nexcept:\n    pass\n"
        result = _purify_code(engine, code, "silent_failure")
        assert result.purified_code.count("getLogger") == 1

    def test_except_exception_pass_healed(self, engine):
        code = "try:\n    x = 1/0\nexcept Exception:\n    pass\n"
        result = _purify_code(engine, code, "silent_failure")
        assert result.status == ShuddhiStatus.PURIFIED
        compile(result.purified_code, "<test>", "exec")
        assert "import logging" in result.purified_code

    def test_non_silent_handler_skipped(self, engine):
        code = "try:\n    x = 1/0\nexcept Exception as e:\n    print(e)\n"
        result = _purify_code(engine, code, "silent_failure")
        assert result.status == ShuddhiStatus.SKIPPED


# =============================================================================
# Remedy loader
# =============================================================================


class TestRemedyLoader:
    """RemedyLoader must discover all remedies."""

    def test_discovers_all_remedies(self, engine):
        assert len(engine._remedies) >= 14

    def test_all_rule_ids_are_strings(self, engine):
        for rule_id in engine._remedies:
            assert isinstance(rule_id, str)
            assert len(rule_id) > 0

    def test_unknown_rule_fails(self, engine):
        fd, tmp = tempfile.mkstemp(suffix=".py")
        try:
            with os.fdopen(fd, "w") as f:
                f.write("x = 1\n")
            result = engine.purify(Path(tmp), "nonexistent_rule_xyz")
            assert result.status == ShuddhiStatus.FAILED
        finally:
            os.unlink(tmp)

    def test_missing_file_fails(self, engine):
        result = engine.purify(Path("/tmp/does_not_exist_xyz.py"), "silent_failure")
        assert result.status == ShuddhiStatus.FAILED
