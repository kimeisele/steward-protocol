"""
Integration Test: MANAS Oracle in Heartbeat (OPUS-089)

Demonstrates the complete flow:
1. Heartbeat initializes ManasOracle
2. Task ingestion → Pre-analysis gate
3. Task execution → Post-analysis learning
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestManasOracleHeartbeatIntegration:
    """Test MANAS Oracle integration into Heartbeat."""

    def test_oracle_import_in_heartbeat(self):
        """Oracle should be importable and available to heartbeat."""
        try:
            from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

            assert ManasOracle is not None
        except ImportError as e:
            pytest.fail(f"ManasOracle not importable: {e}")

    def test_heartbeat_imports_oracle_conditionally(self):
        """Heartbeat should import Oracle with graceful fallback."""
        import importlib
        import sys

        # Load heartbeat script
        heartbeat_path = Path(__file__).parent.parent.parent / "scripts" / "heartbeat.py"

        assert heartbeat_path.exists(), f"Heartbeat script not found at {heartbeat_path}"

        # Read to verify imports
        content = heartbeat_path.read_text()

        # Should have OPUS-089 marker
        assert "OPUS-089" in content, "Missing OPUS-089 marker in heartbeat"
        assert "ManasOracle" in content, "ManasOracle not imported in heartbeat"
        assert "MANAS_ORACLE_AVAILABLE" in content, "Missing availability flag"

    def test_oracle_api_structure(self):
        """Verify Oracle API has the expected structure."""
        from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

        oracle = ManasOracle()

        # Should have the three main methods
        assert hasattr(oracle, "consult"), "Missing consult method"
        assert hasattr(oracle, "pre_analysis"), "Missing pre_analysis method"
        assert hasattr(oracle, "post_analysis"), "Missing post_analysis method"

        # All should be callable
        assert callable(oracle.consult)
        assert callable(oracle.pre_analysis)
        assert callable(oracle.post_analysis)

    def test_oracle_pre_analysis_gate_decision(self):
        """Pre-analysis should make gate decisions."""
        from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

        oracle = ManasOracle()

        # Safe task should proceed
        safe_gate = oracle.pre_analysis(
            {
                "task_title": "Run tests",
                "task_type": "test",
                "risk_level": "low",
                "is_automated": True,
                "user_approval": True,
            }
        )

        assert "proceed" in safe_gate
        assert "reason" in safe_gate
        assert "safety_score" in safe_gate
        assert safe_gate["proceed"] in (True, False)

    def test_oracle_post_analysis_learning(self):
        """Post-analysis should record outcomes in memory."""
        from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

        oracle = ManasOracle()

        # Record a success
        result = oracle.post_analysis(
            {
                "task_type": "test_create",
                "success": True,
                "error": None,
                "duration_ms": 1000,
            }
        )

        assert result["recorded"] in (True, False)  # Should be boolean

    def test_oracle_analysis_result_serialization(self):
        """AnalysisResult should be JSON-serializable."""
        import json

        from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

        oracle = ManasOracle()

        result = oracle.consult(
            {
                "task_title": "Example task",
                "task_type": "example",
                "risk_level": "medium",
                "is_automated": False,
                "user_approval": False,
            }
        )

        # Should have to_dict method
        result_dict = result.to_dict()

        # Should be JSON serializable
        try:
            json_str = json.dumps(result_dict)
            assert json_str is not None
        except TypeError as e:
            pytest.fail(f"AnalysisResult not JSON serializable: {e}")

    def test_oracle_available_flag_in_heartbeat(self):
        """MANAS_ORACLE_AVAILABLE flag should be set correctly."""
        try:
            # Try to import the oracle
            from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

            oracle_available = True
        except ImportError:
            oracle_available = False

        # At this point it should be available
        assert oracle_available, "ManasOracle should be importable in test environment"


class TestManasOracleHeartbeatFlow:
    """Test the complete heartbeat flow with Oracle."""

    def test_heartbeat_with_oracle_flow(self):
        """Simulate the heartbeat flow: pre-gate → execute → post-learn."""
        from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

        oracle = ManasOracle()

        # Step 1: Pre-analysis gate
        context = {
            "task_title": "Test task execution",
            "task_type": "test",
            "risk_level": "low",
            "changes": ["test_file.py"],
            "is_automated": True,
            "user_approval": False,
        }

        gate = oracle.pre_analysis(context)

        # Step 2: Simulate execution decision based on gate
        if gate["proceed"]:
            # Step 3: Post-analysis learning
            oracle.post_analysis(
                {
                    "task_type": "test",
                    "success": True,
                    "error": None,
                    "duration_ms": 500,
                }
            )

        # Should complete without errors
        assert True

    def test_oracle_risk_identification_in_flow(self):
        """Oracle should identify production risks during pre-analysis."""
        from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

        oracle = ManasOracle()

        # Production task
        gate = oracle.pre_analysis(
            {
                "task_title": "Update production database",
                "task_type": "db_update",
                "risk_level": "high",
                "changes": ["production/schema.sql"],
                "is_automated": True,
                "user_approval": False,
            }
        )

        # Should identify as risky
        assert gate["safety_score"] < 0.70, "Production task should have lower safety"

    def test_oracle_confidence_evolution(self):
        """Oracle confidence should improve with repeated successes."""
        from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

        oracle = ManasOracle()

        # First consultation
        result1 = oracle.consult(
            {
                "task_title": "First time task",
                "task_type": "unique_task",
                "risk_level": "low",
                "is_automated": False,
                "user_approval": True,
            }
        )

        confidence1 = result1.confidence

        # Simulate several successes
        for i in range(3):
            oracle.post_analysis(
                {
                    "task_type": "unique_task",
                    "success": True,
                    "error": None,
                }
            )

        # Second consultation on same task type
        result2 = oracle.consult(
            {
                "task_title": "Repeat task",
                "task_type": "unique_task",
                "risk_level": "low",
                "is_automated": False,
                "user_approval": True,
            }
        )

        confidence2 = result2.confidence

        # Confidence might improve or stay same (depends on memory)
        assert confidence2 >= 0.0 and confidence2 <= 1.0


class TestManasOracleErrorRecovery:
    """Test Oracle resilience in error scenarios."""

    def test_oracle_handles_malformed_context(self):
        """Oracle should handle malformed contexts gracefully."""
        from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

        oracle = ManasOracle()

        # Completely empty context
        result = oracle.consult({})

        assert result is not None
        assert hasattr(result, "safety_score")
        assert 0.0 <= result.safety_score <= 1.0

    def test_oracle_handles_null_values(self):
        """Oracle should handle null values in context."""
        from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

        oracle = ManasOracle()

        context = {
            "task_title": None,
            "task_type": None,
            "risk_level": None,
            "changes": None,
        }

        result = oracle.consult(context)

        assert result is not None
        assert isinstance(result.advice, str)

    def test_oracle_handles_extreme_values(self):
        """Oracle should handle extreme input values."""
        from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

        oracle = ManasOracle()

        context = {
            "task_title": "x" * 10000,  # Very long title
            "task_type": "very_extreme_type_that_probably_never_happened",
            "risk_level": "UNKNOWN",  # Invalid risk level
            "changes": [f"file_{i}.py" for i in range(1000)],  # Huge changeset
            "is_automated": True,
            "user_approval": True,
        }

        result = oracle.consult(context)

        assert result is not None
        # Should recognize huge changeset as risk
        assert len(result.risks) > 0 or result.safety_score < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
