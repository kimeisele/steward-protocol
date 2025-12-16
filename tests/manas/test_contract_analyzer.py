"""
OPUS-032: Contract Analyzer Tests - The Immune System.

These tests verify the ContractAnalyzer:
1. Converts verification failures to repair intents
2. Handles different ContractFailureTypes correctly
3. Respects config limits
4. Generates appropriate priority/risk levels
"""

import pytest

from vibe_core.governance import ContractFailure, ContractFailureType
from vibe_core.plugins.opus_assistant.manas.analyzers.contract_analyzer import (
    ContractAnalyzer,
)
from vibe_core.plugins.opus_assistant.manas.intent_generator import (
    IntentPriority,
    IntentRisk,
)


class TestContractAnalyzerBasics:
    """Basic functionality tests."""

    @pytest.fixture
    def analyzer(self, tmp_path):
        """Create analyzer with temp workspace."""
        return ContractAnalyzer(workspace=tmp_path)

    def test_analyzer_name(self, analyzer):
        """Analyzer has correct name."""
        assert analyzer.name == "contract_analyzer"

    def test_empty_context_returns_empty_list(self, analyzer):
        """No failures = no intents."""
        intents = analyzer.analyze({})
        assert intents == []

    def test_no_failures_returns_empty_list(self, analyzer):
        """Empty failures list = no intents."""
        context = {"verification_results": {"failures": []}}
        intents = analyzer.analyze(context)
        assert intents == []


class TestFailureToIntent:
    """Test failure type to intent conversion."""

    @pytest.fixture
    def analyzer(self, tmp_path):
        return ContractAnalyzer(workspace=tmp_path)

    def test_file_missing_creates_high_priority_intent(self, analyzer):
        """FILE_MISSING → HIGH priority intent."""
        failure = ContractFailure(
            type=ContractFailureType.FILE_MISSING,
            path="vibe_core/missing.py",
            message="File not found",
            harness_source="test.md",
        )
        context = {"verification_results": {"failures": [failure]}}

        intents = analyzer.analyze(context)

        assert len(intents) == 1
        assert intents[0].priority == IntentPriority.HIGH
        assert intents[0].intent_type == "contract_file_create"
        assert "missing.py" in intents[0].title

    def test_file_extra_creates_low_priority_intent(self, analyzer):
        """FILE_EXTRA → LOW priority review intent."""
        failure = ContractFailure(
            type=ContractFailureType.FILE_EXTRA,
            path="vibe_core/stale.py",
            message="Should not exist",
            harness_source="test.md",
        )
        context = {"verification_results": {"failures": [failure]}}

        intents = analyzer.analyze(context)

        assert len(intents) == 1
        assert intents[0].priority == IntentPriority.LOW
        assert intents[0].intent_type == "contract_file_review"

    def test_pattern_missing_creates_medium_risk_intent(self, analyzer):
        """PATTERN_MISSING → MEDIUM risk intent."""
        failure = ContractFailure(
            type=ContractFailureType.PATTERN_MISSING,
            path="vibe_core/module.py",
            message="inject_kernel not found",
            harness_source="wiring.md",
            details={"pattern": "inject_kernel"},
        )
        context = {"verification_results": {"failures": [failure]}}

        intents = analyzer.analyze(context)

        assert len(intents) == 1
        assert intents[0].risk == IntentRisk.MEDIUM
        assert intents[0].intent_type == "contract_pattern_fix"

    def test_doc_stale_is_auto_executable(self, analyzer):
        """DOC_STALE → SAFE risk, auto_executable."""
        failure = ContractFailure(
            type=ContractFailureType.DOC_STALE,
            path="docs/README.md",
            message="Outdated paths",
            harness_source="test.md",
        )
        context = {"verification_results": {"failures": [failure]}}

        intents = analyzer.analyze(context)

        assert len(intents) == 1
        assert intents[0].risk == IntentRisk.SAFE
        assert intents[0].auto_executable is True
        assert intents[0].intent_type == "contract_doc_update"

    def test_semantic_import_fail_creates_critical_intent(self, analyzer):
        """SEMANTIC_IMPORT_FAIL → CRITICAL priority, never auto-executable."""
        failure = ContractFailure(
            type=ContractFailureType.SEMANTIC_IMPORT_FAIL,
            path="vibe_core/broken.py",
            message="ImportError: No module named X",
            harness_source="test.md",
            details={"error": "ImportError"},
        )
        context = {"verification_results": {"failures": [failure]}}

        intents = analyzer.analyze(context)

        assert len(intents) == 1
        assert intents[0].priority == IntentPriority.CRITICAL
        assert intents[0].auto_executable is False


class TestDictFailureHandling:
    """Test handling of dict-formatted failures."""

    @pytest.fixture
    def analyzer(self, tmp_path):
        return ContractAnalyzer(workspace=tmp_path)

    def test_handles_dict_failure(self, analyzer):
        """Can process failure as dict."""
        failure_dict = {
            "type": "FILE_MISSING",
            "path": "test/path.py",
            "message": "Not found",
            "harness_source": "test.md",
        }
        context = {"verification_results": {"failures": [failure_dict]}}

        intents = analyzer.analyze(context)

        assert len(intents) == 1
        assert "path.py" in intents[0].title

    def test_handles_unknown_type_gracefully(self, analyzer):
        """Unknown failure type returns None."""
        failure_dict = {
            "type": "UNKNOWN_TYPE",
            "path": "test/path.py",
            "message": "???",
        }
        context = {"verification_results": {"failures": [failure_dict]}}

        intents = analyzer.analyze(context)

        assert intents == []


class TestConfigLimits:
    """Test configuration limits."""

    def test_respects_max_intents_per_run(self, tmp_path):
        """Respects max_intents_per_run config."""
        from vibe_core.plugins.opus_assistant.manas.analyzers.base import AnalyzerConfig

        config = AnalyzerConfig(max_intents_per_run=2)
        analyzer = ContractAnalyzer(workspace=tmp_path, config=config)

        # Create 5 failures
        failures = [
            ContractFailure(
                type=ContractFailureType.FILE_MISSING,
                path=f"path{i}.py",
                message="Missing",
                harness_source="test.md",
            )
            for i in range(5)
        ]
        context = {"verification_results": {"failures": failures}}

        intents = analyzer.analyze(context)

        assert len(intents) == 2  # Limited by config


class TestIntentIdGeneration:
    """Test intent ID generation."""

    @pytest.fixture
    def analyzer(self, tmp_path):
        return ContractAnalyzer(workspace=tmp_path)

    def test_generates_unique_ids(self, analyzer):
        """Each intent gets unique ID."""
        failures = [
            ContractFailure(
                type=ContractFailureType.FILE_MISSING,
                path=f"path{i}.py",
                message="Missing",
                harness_source="test.md",
            )
            for i in range(3)
        ]
        context = {"verification_results": {"failures": failures}}

        intents = analyzer.analyze(context)

        ids = [i.id for i in intents]
        assert len(ids) == len(set(ids))  # All unique

    def test_id_prefix_is_contract(self, analyzer):
        """Intent IDs start with 'contract_'."""
        failure = ContractFailure(
            type=ContractFailureType.FILE_MISSING,
            path="test.py",
            message="Missing",
            harness_source="test.md",
        )
        context = {"verification_results": {"failures": [failure]}}

        intents = analyzer.analyze(context)

        assert intents[0].id.startswith("contract_")
