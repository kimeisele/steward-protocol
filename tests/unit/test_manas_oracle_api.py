"""
Test: MANAS Oracle API (OPUS-089)

Tests the clean separation of concerns: ManasOracle as a Wisdom Interface.
"""

import pytest

from vibe_core.plugins.opus_assistant.manas.api import AnalysisResult, ManasOracle
from vibe_core.plugins.opus_assistant.manas.intent_generator import IntentPriority


class TestManasOracleBasics:
    """Test basic Oracle functionality."""

    def test_oracle_initialization(self):
        """Oracle should initialize without errors."""
        oracle = ManasOracle()
        assert oracle is not None
        assert oracle.kernel is not None
        assert oracle.config is not None

    def test_consult_low_risk_task(self):
        """Oracle should give high safety score to low-risk tasks."""
        oracle = ManasOracle()

        context = {
            "task_title": "Write documentation",
            "task_type": "doc_update",
            "risk_level": "low",
            "changes": ["README.md"],
            "is_automated": False,
            "user_approval": True,
        }

        result = oracle.consult(context)

        assert isinstance(result, AnalysisResult)
        assert result.safety_score >= 0.90
        assert result.priority == IntentPriority.LOW
        assert result.confidence > 0.0

    def test_consult_high_risk_task(self):
        """Oracle should give low safety score to high-risk tasks."""
        oracle = ManasOracle()

        context = {
            "task_title": "Delete production database",
            "task_type": "dangerous_op",
            "risk_level": "high",
            "changes": ["production.db"],
            "is_automated": True,
            "user_approval": False,
        }

        result = oracle.consult(context)

        assert result.safety_score < 0.70
        assert result.priority in (IntentPriority.HIGH, IntentPriority.CRITICAL)
        assert len(result.risks) > 0
        assert len(result.precautions) > 0

    def test_analysis_result_to_dict(self):
        """AnalysisResult should serialize to dict."""
        result = AnalysisResult(
            priority=IntentPriority.MEDIUM,
            safety_score=0.75,
            confidence=0.85,
            advice="Test advice",
            risks=["test risk"],
            precautions=["test precaution"],
        )

        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict["priority"].lower() == "medium"
        assert result_dict["safety_score"] == 0.75
        assert result_dict["confidence"] == 0.85
        assert "Test advice" in result_dict["advice"]

    def test_analysis_result_str(self):
        """AnalysisResult should have readable string representation."""
        result = AnalysisResult(
            priority=IntentPriority.HIGH,
            safety_score=0.5,
            confidence=0.6,
            advice="High risk detected",
            risks=["Database corruption"],
        )

        result_str = str(result)

        assert "high" in result_str.lower()
        assert "50%" in result_str or "0.5" in result_str
        assert "High risk detected" in result_str


class TestManasOracleAPIs:
    """Test the three main APIs: consult, pre_analysis, post_analysis."""

    def test_pre_analysis_allows_safe_task(self):
        """pre_analysis should allow safe tasks to proceed."""
        oracle = ManasOracle()

        context = {
            "task_title": "Run tests",
            "task_type": "test",
            "risk_level": "low",
            "is_automated": True,
            "user_approval": True,
        }

        gate = oracle.pre_analysis(context)

        assert gate["proceed"] is True
        assert "reason" in gate
        assert "recommendation" in gate

    def test_pre_analysis_blocks_dangerous_task(self):
        """pre_analysis should block very dangerous tasks."""
        oracle = ManasOracle()

        context = {
            "task_title": "Deploy to production",
            "task_type": "deploy",
            "risk_level": "critical",
            "changes": ["main.py", "config.yaml", "database.sql"],
            "is_automated": True,
            "user_approval": False,
        }

        gate = oracle.pre_analysis(context)

        # Critical + automated + no approval should be blocked
        assert gate["proceed"] is False or gate["safety_score"] < 0.5

    def test_post_analysis_records_success(self):
        """post_analysis should record successful task execution."""
        oracle = ManasOracle()

        result = oracle.post_analysis(
            {
                "task_type": "test_create",
                "success": True,
                "error": None,
                "duration_ms": 1250,
            }
        )

        assert result["recorded"] is True
        assert result["success"] is True

    def test_post_analysis_records_failure(self):
        """post_analysis should record failed task execution."""
        oracle = ManasOracle()

        result = oracle.post_analysis(
            {
                "task_type": "deploy",
                "success": False,
                "error": "Connection timeout",
                "duration_ms": 5000,
            }
        )

        assert result["recorded"] is True
        assert result["success"] is False


class TestManasOracleRiskIdentification:
    """Test the risk identification logic."""

    def test_identifies_production_risk(self):
        """Oracle should identify production environment risk."""
        oracle = ManasOracle()

        context = {
            "task_title": "Update config in production",
            "task_type": "config_update",
            "risk_level": "medium",
            "changes": ["production/config.yaml"],
            "is_automated": False,
            "user_approval": False,
        }

        result = oracle.consult(context)

        assert any("production" in risk.lower() for risk in result.risks)

    def test_identifies_large_changeset_risk(self):
        """Oracle should identify risk from large changesets."""
        oracle = ManasOracle()

        changes = [f"file_{i}.py" for i in range(15)]

        context = {
            "task_title": "Refactor entire module",
            "task_type": "refactor",
            "risk_level": "medium",
            "changes": changes,
            "is_automated": False,
            "user_approval": False,
        }

        result = oracle.consult(context)

        assert any("changeset" in risk.lower() or "large" in risk.lower() for risk in result.risks)

    def test_suggests_production_precautions(self):
        """Oracle should suggest backup/rollback for production changes."""
        oracle = ManasOracle()

        context = {
            "task_title": "Deploy to production",
            "task_type": "deploy",
            "risk_level": "high",
            "changes": ["main.py"],
            "is_automated": False,
            "user_approval": True,
        }

        result = oracle.consult(context)

        precautions_text = " ".join(result.precautions).lower()
        assert "backup" in precautions_text or "rollback" in precautions_text or "staging" in precautions_text


class TestManasOracleMemoryIntegration:
    """Test integration with memory store for learning."""

    def test_confidence_based_on_history(self):
        """Oracle confidence should improve with successful history."""
        oracle = ManasOracle()

        # Simulate several successes
        for i in range(5):
            oracle.post_analysis(
                {
                    "task_type": "test_create",
                    "success": True,
                    "error": None,
                }
            )

        # Now consult on same task type
        context = {
            "task_title": "Create new test",
            "task_type": "test_create",
            "risk_level": "low",
            "is_automated": True,
            "user_approval": False,
        }

        result = oracle.consult(context)

        # Confidence should be reasonably high
        assert result.confidence >= 0.5


class TestManasOracleErrorHandling:
    """Test Oracle resilience and error handling."""

    def test_consult_handles_missing_context_keys(self):
        """Oracle should handle partial context gracefully."""
        oracle = ManasOracle()

        # Minimal context
        context = {
            "task_title": "Something",
        }

        result = oracle.consult(context)

        assert result is not None
        assert result.safety_score >= 0.0 and result.safety_score <= 1.0

    def test_consult_returns_safe_default_on_error(self):
        """Oracle should return a safe analysis even on internal errors."""
        oracle = ManasOracle()

        # Inject an invalid context that might cause issues
        context = {
            "task_title": None,  # Invalid
            "task_type": 123,  # Invalid type
        }

        # Should not raise - should return safe default
        result = oracle.consult(context)

        assert result is not None
        assert isinstance(result, AnalysisResult)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
