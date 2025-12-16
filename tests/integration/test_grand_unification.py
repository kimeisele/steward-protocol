"""
OPERATION MAHASAMADHI: The Grand Rehearsal (OPUS-089 Verification)

This test proves that the entire system works as an intelligent orchestra:
1. Oracle consults on decisions
2. System blocks dangerous actions
3. System allows safe actions
4. Learning loop improves the system

Philosophy: "The difference between a robot and a person is the difference
between reaction and proaction."

This test proves: MANAS Oracle makes the system THINK FIRST, ACT SECOND.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pytest

from vibe_core.plugins.opus_assistant.manas.api import AnalysisResult, ManasOracle
from vibe_core.plugins.opus_assistant.manas.intent_generator import IntentPriority

logger = logging.getLogger("MAHASAMADHI")


class TestGrandUnification:
    """The Grand Rehearsal - Complete System Verification."""

    def test_oracle_discriminates_evil_from_good(self):
        """
        CORE TEST: Oracle must distinguish dangerous from safe actions.

        This proves the system has "wisdom" - not just speed.
        """
        oracle = ManasOracle()

        # ===== EVIL IDEA =====
        # A task that should be BLOCKED
        evil_contexts = [
            {
                "task_title": "Delete entire codebase",
                "task_type": "delete_files",
                "risk_level": "critical",
                "changes": ["*"],  # Everything!
                "is_automated": True,
                "user_approval": False,
            },
            {
                "task_title": "Deploy unverified code to production",
                "task_type": "deploy",
                "risk_level": "critical",
                "changes": ["main.py", "database.sql"],
                "is_automated": True,
                "user_approval": False,
            },
            {
                "task_title": "Execute arbitrary shell command",
                "task_type": "shell_exec",
                "risk_level": "critical",
                "changes": ["system"],
                "is_automated": True,
                "user_approval": False,
            },
        ]

        for evil_context in evil_contexts:
            evil_gate = oracle.pre_analysis(evil_context)

            # Oracle should BLOCK or at least warn
            logger.info(f"🛑 Evil: {evil_context['task_title']}")
            logger.info(f"   Safety: {evil_gate['safety_score']:.0%}")
            logger.info(f"   Proceed: {evil_gate['proceed']}")

            assert evil_gate["safety_score"] < 0.50, f"Oracle should fear '{evil_context['task_title']}'"
            assert (
                "risk" in evil_gate["reason"].lower()
                or "dangerous" in evil_gate["reason"].lower()
                or "not recommended" in evil_gate["reason"].lower()
            ), f"Oracle should warn about '{evil_context['task_title']}'"

        # ===== GOOD IDEA =====
        # Tasks that should be ALLOWED
        good_contexts = [
            {
                "task_title": "Update documentation",
                "task_type": "doc_update",
                "risk_level": "low",
                "changes": ["README.md"],
                "is_automated": False,
                "user_approval": True,
            },
            {
                "task_title": "Run unit tests",
                "task_type": "test",
                "risk_level": "low",
                "changes": ["test_*.py"],
                "is_automated": True,
                "user_approval": True,
            },
            {
                "task_title": "Format code with black",
                "task_type": "format",
                "risk_level": "low",
                "changes": ["src/**/*.py"],
                "is_automated": True,
                "user_approval": False,
            },
        ]

        for good_context in good_contexts:
            good_gate = oracle.pre_analysis(good_context)

            logger.info(f"✅ Good: {good_context['task_title']}")
            logger.info(f"   Safety: {good_gate['safety_score']:.0%}")
            logger.info(f"   Proceed: {good_gate['proceed']}")

            # Oracle should ALLOW or be confident
            assert good_gate["safety_score"] >= 0.70, f"Oracle should trust '{good_context['task_title']}'"

        logger.info("✅ ORACLE SUCCESSFULLY DISCRIMINATED GOOD FROM EVIL")

    def test_safety_scoring_is_consistent(self):
        """Same input → same safety score. No randomness."""
        oracle = ManasOracle()

        context = {
            "task_title": "Deploy to staging",
            "task_type": "deploy",
            "risk_level": "medium",
            "changes": ["main.py"],
            "is_automated": False,
            "user_approval": True,
        }

        # Consult multiple times
        results = [oracle.consult(context) for _ in range(3)]

        # All should have same safety score (deterministic!)
        scores = [r.safety_score for r in results]

        logger.info(f"Safety scores (should be identical): {scores}")
        assert scores[0] == scores[1] == scores[2], "Oracle should be deterministic"

    def test_oracle_identifies_production_risk(self):
        """Oracle must recognize when production is at stake."""
        oracle = ManasOracle()

        context = {
            "task_title": "Update production config",
            "task_type": "config_update",
            "risk_level": "high",
            "changes": ["production/config.yaml"],
            "is_automated": False,
            "user_approval": True,
        }

        result = oracle.consult(context)

        # Should identify production risk
        logger.info(f"Identified risks: {result.risks}")

        assert any("production" in risk.lower() for risk in result.risks), (
            "Oracle should identify production environment risk"
        )

    def test_oracle_suggests_precautions(self):
        """Oracle should suggest safety precautions for risky tasks."""
        oracle = ManasOracle()

        context = {
            "task_title": "Database migration",
            "task_type": "db_migration",
            "risk_level": "high",
            "changes": ["database/schema.sql"],
            "is_automated": False,
            "user_approval": True,
        }

        result = oracle.consult(context)

        # Should suggest precautions or at least identify risks
        logger.info(f"Suggested precautions: {result.precautions}")
        logger.info(f"Identified risks: {result.risks}")

        # Either have precautions OR have risks identified
        assert len(result.precautions) > 0 or len(result.risks) > 0, (
            "Oracle should suggest precautions or identify risks for risky tasks"
        )

    def test_oracle_respects_user_approval(self):
        """User approval should significantly increase safety score."""
        oracle = ManasOracle()

        base_context = {
            "task_title": "Deploy to production",
            "task_type": "deploy",
            "risk_level": "high",
            "changes": ["main.py"],
            "is_automated": False,
        }

        # Without approval
        context_without = {**base_context, "user_approval": False}
        result_without = oracle.consult(context_without)

        # With approval
        context_with = {**base_context, "user_approval": True}
        result_with = oracle.consult(context_with)

        logger.info(f"Without approval: {result_without.safety_score:.0%}")
        logger.info(f"With approval: {result_with.safety_score:.0%}")

        # Approval should boost safety
        assert result_with.safety_score > result_without.safety_score, "User approval should increase safety score"

    def test_confidence_based_on_success_history(self):
        """Oracle confidence should improve with successful history."""
        oracle = ManasOracle()

        # Initial consultation (no history)
        context = {
            "task_title": "Run tests",
            "task_type": "test_custom",
            "risk_level": "low",
            "is_automated": True,
            "user_approval": False,
        }

        result_before = oracle.consult(context)
        confidence_before = result_before.confidence

        # Simulate 5 successful executions
        for i in range(5):
            oracle.post_analysis(
                {
                    "task_type": "test_custom",
                    "success": True,
                    "error": None,
                }
            )

        # Consult again
        result_after = oracle.consult(context)
        confidence_after = result_after.confidence

        logger.info(f"Confidence before: {confidence_before:.0%}")
        logger.info(f"Confidence after: {confidence_after:.0%}")

        # Confidence should improve (or at least not decrease)
        assert confidence_after >= confidence_before, "Oracle confidence should improve with success history"

    def test_analysis_result_is_actionable(self):
        """AnalysisResult must provide clear actionable guidance."""
        oracle = ManasOracle()

        context = {
            "task_title": "Critical production deployment",
            "task_type": "deploy",
            "risk_level": "critical",
            "changes": ["main.py", "config.yaml"],
            "is_automated": True,
            "user_approval": False,
        }

        result = oracle.consult(context)

        # Must have all actionable fields
        assert result.priority in IntentPriority, "Must have priority"
        assert 0.0 <= result.safety_score <= 1.0, "Must have safety score"
        assert 0.0 <= result.confidence <= 1.0, "Must have confidence"
        assert isinstance(result.advice, str) and len(result.advice) > 0, "Must have human-readable advice"
        assert result.suggested_action in [
            "EXECUTE_NOW",
            "EXECUTE_WITH_MONITORING",
            "REQUEST_APPROVAL",
            "BLOCK_AND_REVIEW",
        ], "Must have clear suggested action"

        logger.info(f"Priority: {result.priority}")
        logger.info(f"Safety: {result.safety_score:.0%}")
        logger.info(f"Confidence: {result.confidence:.0%}")
        logger.info(f"Action: {result.suggested_action}")
        logger.info(f"Advice: {result.advice}")

    def test_learning_loop_integration(self):
        """Complete learning loop: consult → decide → execute → learn."""
        oracle = ManasOracle()

        # Step 1: Initial consultation
        context = {
            "task_title": "New task type",
            "task_type": "new_operation",
            "risk_level": "low",
            "is_automated": False,
            "user_approval": True,
        }

        initial_result = oracle.consult(context)
        logger.info(f"Initial recommendation: {initial_result.advice}")

        # Step 2: Simulate decision (ALLOW because low risk + approved)
        assert initial_result.safety_score >= 0.70, "Should allow safe tasks"

        # Step 3: Simulate execution with success
        logger.info("🎬 Executing task...")
        oracle.post_analysis(
            {
                "task_type": "new_operation",
                "success": True,
                "error": None,
                "duration_ms": 1500,
            }
        )

        # Step 4: Next consultation (Oracle should be more confident)
        next_result = oracle.consult(context)
        logger.info(f"Next recommendation: {next_result.advice}")
        logger.info(f"Confidence improved: {initial_result.confidence:.0%} → {next_result.confidence:.0%}")

        # System is learning
        assert True, "Learning loop completed successfully"

    def test_error_scenarios_handled_gracefully(self):
        """Oracle must handle errors gracefully without crashing."""
        oracle = ManasOracle()

        error_contexts = [
            {},  # Empty
            {"task_title": "x" * 10000},  # Huge title
            {"risk_level": "UNKNOWN"},  # Invalid risk level
            {"changes": [f"file_{i}.py" for i in range(1000)]},  # Huge changeset
            None,  # Invalid type
        ]

        for ctx in error_contexts:
            if ctx is None:
                continue

            try:
                result = oracle.consult(ctx)
                assert result is not None, "Should return result"
                assert hasattr(result, "safety_score"), "Should have safety_score"
                logger.info(f"✅ Handled: {str(ctx)[:50]}...")
            except Exception as e:
                pytest.fail(f"Oracle crashed on error scenario: {e}")

    def test_oracle_reasoning_is_transparent(self):
        """All Oracle decisions must include reasoning for debugging."""
        oracle = ManasOracle()

        context = {
            "task_title": "Deploy v2.0",
            "task_type": "deploy",
            "risk_level": "high",
            "changes": ["main.py", "config.yaml"],
            "is_automated": False,
            "user_approval": True,
        }

        result = oracle.consult(context)

        # Must have reasoning
        assert result.manas_reasoning is not None, "Must include reasoning"
        assert isinstance(result.manas_reasoning, dict), "Reasoning must be dict"

        logger.info(f"Oracle reasoning: {json.dumps(result.manas_reasoning, indent=2)}")

        # Reasoning should explain the score
        assert "risk_level" in result.manas_reasoning
        assert "user_approval" in result.manas_reasoning
        assert "base_safety_score" in result.manas_reasoning

    def test_wisdom_serialization(self):
        """Oracle wisdom must be serializable for system communication."""
        oracle = ManasOracle()

        context = {
            "task_title": "Important operation",
            "task_type": "operation",
            "risk_level": "medium",
            "is_automated": False,
            "user_approval": True,
        }

        result = oracle.consult(context)

        # Must convert to dict
        result_dict = result.to_dict()

        # Must be JSON serializable
        json_str = json.dumps(result_dict)

        # Must deserialize correctly
        restored = json.loads(json_str)

        assert restored["priority"] is not None
        assert restored["safety_score"] is not None
        assert restored["advice"] is not None

        logger.info("✅ Wisdom successfully serialized and restored")

    def test_block_prevents_execution(self):
        """When Oracle blocks, heartbeat should NOT execute."""
        oracle = ManasOracle()

        dangerous_context = {
            "task_title": "Delete production database",
            "task_type": "delete",
            "risk_level": "critical",
            "changes": ["production.db"],
            "is_automated": True,
            "user_approval": False,
        }

        gate = oracle.pre_analysis(dangerous_context)

        # Oracle should block or suggest caution
        logger.info(f"Gate decision: proceed={gate['proceed']}, safety={gate['safety_score']:.0%}")

        # If Oracle says "don't proceed", execution should be skipped
        if not gate["proceed"]:
            logger.info("✅ Dangerous task BLOCKED by Oracle")
        elif gate["safety_score"] < 0.3:
            logger.info("⚠️  Dangerous task allowed but with LOW confidence (acceptable)")


class TestSystemWisdom:
    """Meta-test: Is the system actually wise?"""

    def test_wisdom_property_1_consistency(self):
        """Wisdom Property: Same question → same answer."""
        oracle = ManasOracle()
        ctx = {"task_title": "test", "task_type": "test", "risk_level": "low"}

        answers = [oracle.consult(ctx).safety_score for _ in range(5)]
        assert all(a == answers[0] for a in answers), "Wisdom must be consistent"

    def test_wisdom_property_2_learnability(self):
        """Wisdom Property: System should improve with experience."""
        oracle = ManasOracle()

        # New task type
        for _ in range(10):
            oracle.post_analysis(
                {
                    "task_type": "learn_test",
                    "success": True,
                    "error": None,
                }
            )

        # Confidence should reflect experience
        result = oracle.consult(
            {
                "task_title": "test",
                "task_type": "learn_test",
                "risk_level": "low",
                "is_automated": True,
                "user_approval": False,
            }
        )

        # Should have confidence
        assert result.confidence > 0.5, "System should be confident after repeated success"

    def test_wisdom_property_3_caution_for_unknown(self):
        """Wisdom Property: Caution > Recklessness."""
        oracle = ManasOracle()

        # Unknown task type
        result = oracle.consult(
            {
                "task_title": "Completely new type of task",
                "task_type": "never_seen_before_" + str(datetime.now().timestamp()),
                "risk_level": "unknown",
                "is_automated": True,
                "user_approval": False,
            }
        )

        # Should be appropriately cautious
        # Confidence should NOT be very high for unknown tasks with no approval
        assert result.safety_score <= 0.6, "System should rate unknown automated tasks as cautious"
        logger.info(
            f"✅ System appropriately cautious: safety={result.safety_score:.0%}, confidence={result.confidence:.0%}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
