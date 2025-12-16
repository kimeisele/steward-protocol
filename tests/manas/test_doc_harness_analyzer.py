"""
Tests for DocHarnessAnalyzer - The Self-Healing Documentation System.

TDD: These tests define the contract for harness analysis.
"""


import pytest


class TestDocHarnessAnalyzerExists:
    """The analyzer must exist and be importable."""

    def test_importable(self):
        from vibe_core.plugins.opus_assistant.manas.analyzers.doc_harness_analyzer import (
            DocHarnessAnalyzer,
        )

        assert DocHarnessAnalyzer is not None

    def test_instantiable(self, tmp_path):
        from vibe_core.plugins.opus_assistant.manas.analyzers.doc_harness_analyzer import (
            DocHarnessAnalyzer,
        )

        analyzer = DocHarnessAnalyzer(workspace=tmp_path)
        assert analyzer is not None

    def test_has_correct_name(self, tmp_path):
        from vibe_core.plugins.opus_assistant.manas.analyzers.doc_harness_analyzer import (
            DocHarnessAnalyzer,
        )

        analyzer = DocHarnessAnalyzer(workspace=tmp_path)
        assert analyzer.name == "doc_harness_analyzer"


class TestHarnessDetection:
    """Detecting @HARNESS in OPUS files."""

    @pytest.fixture
    def analyzer_with_opus_dir(self, tmp_path):
        from vibe_core.plugins.opus_assistant.manas.analyzers.doc_harness_analyzer import (
            DocHarnessAnalyzer,
        )

        # Create OPUS directory
        opus_dir = tmp_path / "docs" / "architecture" / "OPUS"
        opus_dir.mkdir(parents=True)
        return DocHarnessAnalyzer(workspace=tmp_path), opus_dir

    def test_detects_missing_harness(self, analyzer_with_opus_dir):
        analyzer, opus_dir = analyzer_with_opus_dir

        # Create file without harness
        (opus_dir / "001-TEST.md").write_text("# Test Doc\n\nNo harness here.")

        intents = analyzer.analyze({})

        assert len(intents) == 1
        assert intents[0].intent_type == "harness_missing"

    def test_detects_existing_harness(self, analyzer_with_opus_dir):
        analyzer, opus_dir = analyzer_with_opus_dir

        # Create file with valid harness (referencing existing file)
        harness_content = """# Test Doc

<!-- @HARNESS
files:
  - path: docs/architecture/OPUS/001-TEST.md
    required: true
-->
"""
        (opus_dir / "001-TEST.md").write_text(harness_content)

        intents = analyzer.analyze({})

        # Should have no intents (harness exists and is valid)
        assert len(intents) == 0

    def test_detects_broken_harness(self, analyzer_with_opus_dir):
        analyzer, opus_dir = analyzer_with_opus_dir

        # Create file with harness referencing non-existent file
        harness_content = """# Test Doc

<!-- @HARNESS
files:
  - path: nonexistent/file.py
    required: true
-->
"""
        (opus_dir / "001-TEST.md").write_text(harness_content)

        intents = analyzer.analyze({})

        assert len(intents) == 1
        assert intents[0].intent_type == "harness_broken"
        assert "nonexistent/file.py" in intents[0].params.get("files_missing", [])


class TestSanskritModuleDetection:
    """Detecting Sanskrit module files (050-060 series)."""

    @pytest.fixture
    def analyzer_with_sanskrit(self, tmp_path):
        from vibe_core.plugins.opus_assistant.manas.analyzers.doc_harness_analyzer import (
            DocHarnessAnalyzer,
        )

        # Create OPUS and cortex directories
        opus_dir = tmp_path / "docs" / "architecture" / "OPUS"
        opus_dir.mkdir(parents=True)

        cortex_dir = tmp_path / "vibe_core" / "plugins" / "opus_assistant" / "manas" / "cortex"
        cortex_dir.mkdir(parents=True)

        return DocHarnessAnalyzer(workspace=tmp_path), opus_dir, cortex_dir

    def test_identifies_sanskrit_module(self, analyzer_with_sanskrit):
        analyzer, opus_dir, cortex_dir = analyzer_with_sanskrit

        # Create Sanskrit doc without harness
        (opus_dir / "050-VEDA.md").write_text("# VEDA Module\n\nNo harness.")

        # Create the actual module file
        (cortex_dir / "veda.py").write_text("# VEDA implementation")

        intents = analyzer.analyze({})

        assert len(intents) == 1
        assert intents[0].intent_type == "harness_auto_generate"
        assert intents[0].params.get("module_name") == "veda"
        assert intents[0].auto_executable is True  # Safe to auto-execute

    def test_auto_generate_intent_is_safe(self, analyzer_with_sanskrit):
        """Auto-generate intents should be SAFE risk (only markdown changes)."""
        from vibe_core.plugins.opus_assistant.manas.intent_generator import IntentRisk

        analyzer, opus_dir, cortex_dir = analyzer_with_sanskrit

        (opus_dir / "051-MANDALA.md").write_text("# MANDALA\n\nNo harness.")
        (cortex_dir / "mandala.py").write_text("# MANDALA impl")

        intents = analyzer.analyze({})

        assert len(intents) == 1
        assert intents[0].risk == IntentRisk.SAFE


class TestHarnessReport:
    """Harness health reporting."""

    @pytest.fixture
    def analyzer_with_mixed_files(self, tmp_path):
        from vibe_core.plugins.opus_assistant.manas.analyzers.doc_harness_analyzer import (
            DocHarnessAnalyzer,
        )

        opus_dir = tmp_path / "docs" / "architecture" / "OPUS"
        opus_dir.mkdir(parents=True)

        # File with valid harness
        (opus_dir / "001-VALID.md").write_text("""# Valid
<!-- @HARNESS
files:
  - path: docs/architecture/OPUS/001-VALID.md
    required: true
-->
""")

        # File without harness
        (opus_dir / "002-MISSING.md").write_text("# No harness")

        # File with broken harness
        (opus_dir / "003-BROKEN.md").write_text("""# Broken
<!-- @HARNESS
files:
  - path: nonexistent.py
    required: true
-->
""")

        return DocHarnessAnalyzer(workspace=tmp_path)

    def test_report_has_coverage_stats(self, analyzer_with_mixed_files):
        report = analyzer_with_mixed_files.get_harness_report()

        assert "total_files" in report
        assert "with_harness" in report
        assert "without_harness" in report
        assert "coverage_percent" in report

    def test_report_identifies_broken(self, analyzer_with_mixed_files):
        report = analyzer_with_mixed_files.get_harness_report()

        assert report["broken_harness"] == 1
        assert "003-BROKEN.md" in report["broken_files"]


class TestAnalyzerIntegration:
    """Integration with MANAS system."""

    def test_inherits_from_base_analyzer(self):
        from vibe_core.plugins.opus_assistant.manas.analyzers.base import BaseAnalyzer
        from vibe_core.plugins.opus_assistant.manas.analyzers.doc_harness_analyzer import (
            DocHarnessAnalyzer,
        )

        assert issubclass(DocHarnessAnalyzer, BaseAnalyzer)

    def test_respects_max_intents_config(self, tmp_path):
        from vibe_core.plugins.opus_assistant.manas.analyzers.base import AnalyzerConfig
        from vibe_core.plugins.opus_assistant.manas.analyzers.doc_harness_analyzer import (
            DocHarnessAnalyzer,
        )

        # Create many files without harness
        opus_dir = tmp_path / "docs" / "architecture" / "OPUS"
        opus_dir.mkdir(parents=True)

        for i in range(10):
            (opus_dir / f"00{i}-TEST.md").write_text(f"# Test {i}")

        # Limit to 3 intents
        config = AnalyzerConfig(max_intents_per_run=3)
        analyzer = DocHarnessAnalyzer(workspace=tmp_path, config=config)

        intents = analyzer.analyze({})

        assert len(intents) <= 3
