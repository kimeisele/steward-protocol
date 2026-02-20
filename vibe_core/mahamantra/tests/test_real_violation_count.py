"""Reality check: targeted scan of known files proves engine sees violations."""

__mahajana__ = "kumaras"
__position__ = 5
__genesis__ = "0xfe9a70b8"

from pathlib import Path

import pytest

from vibe_core.mahamantra.dharma.kumaras.engine import ShuddhiEngine
from vibe_core.mahamantra.substrate.shuddhi import ShuddhiStatus


@pytest.fixture(scope="module")
def engine():
    return ShuddhiEngine()


class TestAnyTypeDetection:
    """any_type_usage must DETECT files that use Any in annotations."""

    def test_attention_has_any(self, engine):
        f = Path("vibe_core/mahamantra/adapters/attention.py")
        r = engine.purify(f, "any_type_usage")
        assert r.status in (ShuddhiStatus.DETECTED, ShuddhiStatus.PURIFIED)

    def test_llm_has_any(self, engine):
        f = Path("vibe_core/mahamantra/adapters/llm.py")
        r = engine.purify(f, "any_type_usage")
        assert r.status in (ShuddhiStatus.DETECTED, ShuddhiStatus.PURIFIED)

    def test_compliance_has_any(self, engine):
        f = Path("vibe_core/mahamantra/audit/compliance.py")
        r = engine.purify(f, "any_type_usage")
        assert r.status in (ShuddhiStatus.DETECTED, ShuddhiStatus.PURIFIED)


class TestSilentFailureDetection:
    """silent_failure must PURIFY bare except:pass."""

    def test_snippet_bare_except(self, engine):
        code = "try:\n    x = 1\nexcept:\n    pass\n"
        r = engine.scan_cell(code, "silent_failure", Path("<test>"))
        assert r is not None
        assert r.status == ShuddhiStatus.PURIFIED
        assert "logger.exception" in r.purified_code

    def test_snippet_except_exception(self, engine):
        code = "try:\n    x = 1\nexcept Exception:\n    pass\n"
        r = engine.scan_cell(code, "silent_failure", Path("<test>"))
        assert r is not None
        assert r.status == ShuddhiStatus.PURIFIED


class TestHardcodedConstants:
    """hardcoded_constants must DETECT magic numbers without _seed import."""

    def test_magic_16_detected(self, engine):
        code = "x = 16\n"
        r = engine.scan_cell(code, "hardcoded_constants", Path("<test>"))
        assert r is not None
        assert r.status == ShuddhiStatus.DETECTED

    def test_magic_37_detected(self, engine):
        code = "x = 37\n"
        r = engine.scan_cell(code, "hardcoded_constants", Path("<test>"))
        assert r is not None
        assert r.status == ShuddhiStatus.DETECTED

    def test_with_seed_import_clean(self, engine):
        code = "from vibe_core.mahamantra.protocols._seed import WORDS\nx = WORDS\n"
        r = engine.scan_cell(code, "hardcoded_constants", Path("<test>"))
        # Should be None (no violation) since seed is imported
        assert r is None


class TestSubprocessTimeout:
    """subprocess_timeout must PURIFY calls without timeout."""

    def test_run_without_timeout(self, engine):
        code = "import subprocess\nsubprocess.run(['ls'])\n"
        r = engine.scan_cell(code, "subprocess_timeout", Path("<test>"))
        assert r is not None
        assert r.status == ShuddhiStatus.PURIFIED
        assert "timeout" in r.purified_code

    def test_run_with_timeout_clean(self, engine):
        code = "import subprocess\nsubprocess.run(['ls'], timeout=30)\n"
        r = engine.scan_cell(code, "subprocess_timeout", Path("<test>"))
        assert r is None


class TestFractalRoutingSafety:
    """missing_fractal_routing must NOT inject into non-__init__.py."""

    def test_regular_file_detected_not_purified(self, engine):
        from vibe_core.mahamantra.substrate._paths import SUBSTRATE_ROOT
        f = SUBSTRATE_ROOT / "pancha_tattva.py"
        r = engine.purify(f, "missing_fractal_routing")
        assert r.status == ShuddhiStatus.DETECTED
        assert r.purified_code is None
