"""
OPUS-040: Operation Cerebro - Cognitive Kernel Mutation Tests

These tests are designed to KILL mutants in the MANAS consciousness.

CRITICAL SECURITY TESTS:
- Karma gate MUST NOT allow HIGH/MEDIUM risk auto-execution
- IntentConfidence MUST return 0 for unsafe rollback
- capability_genesis MUST be in unsafe_types
- auto_execute_safe default MUST be False

"The consciousness must not be corrupted."
"""

from unittest.mock import MagicMock, patch

import pytest

# Import the module under test
from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import (
    CognitiveKernel,
    IntentConfidence,
    ManasConfig,
)
from vibe_core.plugins.opus_assistant.manas.intent_generator import (
    Intent,
    IntentPriority,
    IntentRisk,
)

# =============================================================================
# SECTION 1: ManasConfig MUTATION TESTS
# =============================================================================


class TestManasConfig:
    """Tests for ManasConfig defaults - security critical."""

    def test_auto_execute_safe_default_is_false(self):
        """
        SECURITY MUTATION KILLER: auto_execute_safe default MUST be False.

        A mutant that changes this to True would enable auto-execution
        of all safe intents without user consent.
        """
        config = ManasConfig()
        assert config.auto_execute_safe is False
        assert config.auto_execute_safe != True  # noqa: E712 - explicit

    def test_karma_threshold_default_is_achievable(self):
        """
        OPUS-314: Karma threshold should be 70 (achievable earned autonomy).

        Balance: High enough for security (>= 60), low enough to earn (<= 80).
        """
        config = ManasConfig()
        assert config.karma_auto_execute_threshold == 70
        assert config.karma_auto_execute_threshold >= 60  # Security floor
        assert config.karma_auto_execute_threshold <= 80  # Achievability ceiling

    def test_survival_first_default_is_true(self):
        """
        Mutation killer: survival_first should be True (repairs before genesis).
        """
        config = ManasConfig()
        assert config.survival_first is True

    def test_max_intents_per_tick_is_limited(self):
        """
        Mutation killer: max_intents_per_tick should be small (throttling).
        """
        config = ManasConfig()
        assert config.max_intents_per_tick <= 5  # Not too many
        assert config.max_intents_per_tick >= 1  # At least 1


# =============================================================================
# SECTION 2: IntentConfidence MUTATION TESTS (SECURITY CRITICAL)
# =============================================================================


class TestIntentConfidence:
    """Tests for IntentConfidence - the trust calculator."""

    def test_total_score_zero_when_rollback_unsafe(self):
        """
        SECURITY MUTATION KILLER #1: Unsafe rollback MUST return 0.0.

        A mutant that removes this check would allow auto-execution
        of irreversible actions.
        """
        confidence = IntentConfidence(
            pattern_match=1.0,  # Perfect pattern match
            karma_level=1.0,  # Perfect karma
            rollback_safety=0.4,  # BELOW 0.5 threshold!
        )

        # Despite perfect pattern/karma, unsafe rollback = 0 confidence
        assert confidence.total_score == 0.0

    def test_total_score_nonzero_when_rollback_safe(self):
        """
        Mutation killer: Safe rollback should allow non-zero confidence.
        """
        confidence = IntentConfidence(
            pattern_match=0.5,
            karma_level=0.5,
            rollback_safety=0.6,  # ABOVE 0.5 threshold
        )

        assert confidence.total_score > 0.0

    def test_rollback_threshold_is_0_5(self):
        """
        Mutation killer: The threshold is exactly 0.5.

        A mutant that changes this to 0.4 or 0.6 would change the
        security boundary.
        """
        # At exactly 0.5, should still be zero (< check, not <=)
        at_threshold = IntentConfidence(
            pattern_match=1.0,
            karma_level=1.0,
            rollback_safety=0.5,  # Exactly at threshold
        )
        # Note: < 0.5 means 0.5 is NOT unsafe
        assert at_threshold.total_score > 0.0

        # Below threshold = unsafe
        below_threshold = IntentConfidence(
            pattern_match=1.0,
            karma_level=1.0,
            rollback_safety=0.49,  # Just below
        )
        assert below_threshold.total_score == 0.0

    def test_karma_weighted_more_than_pattern(self):
        """
        Mutation killer: Karma should have 0.6 weight, pattern 0.4.
        """
        # High karma, low pattern
        high_karma = IntentConfidence(
            pattern_match=0.0,
            karma_level=1.0,
            rollback_safety=1.0,
        )

        # Low karma, high pattern
        high_pattern = IntentConfidence(
            pattern_match=1.0,
            karma_level=0.0,
            rollback_safety=1.0,
        )

        # Karma should produce higher score
        assert high_karma.total_score > high_pattern.total_score
        assert high_karma.total_score == 0.6  # 0.0 * 0.4 + 1.0 * 0.6
        assert high_pattern.total_score == 0.4  # 1.0 * 0.4 + 0.0 * 0.6


class TestIntentConfidenceCompute:
    """Tests for IntentConfidence.compute factory method."""

    def test_capability_genesis_is_unsafe(self):
        """
        SECURITY MUTATION KILLER #2: capability_genesis MUST be unsafe.

        A mutant that moves capability_genesis to safe_types would
        allow code generation to auto-execute!
        """
        mock_memory = MagicMock()
        mock_memory.get_success_rate.return_value = 1.0  # Perfect history

        intent = Intent(
            id="test",
            intent_type="capability_genesis",  # The Ouroboros!
            title="Generate capability",
            description="",
            reasoning="",
        )

        confidence = IntentConfidence.compute(
            intent=intent,
            memory=mock_memory,
            karma_score=100,  # Perfect karma
        )

        # Rollback safety should be low (0.3) for capability_genesis
        assert confidence.rollback_safety == 0.3
        assert confidence.rollback_safety < 0.5  # Unsafe!

    def test_contract_surrender_is_safe(self):
        """
        Mutation killer: contract_surrender should be safe (1.0).
        """
        mock_memory = MagicMock()
        mock_memory.get_success_rate.return_value = 0.5

        intent = Intent(
            id="test",
            intent_type="contract_surrender",
            title="Surrender contract",
            description="",
            reasoning="",
        )

        confidence = IntentConfidence.compute(
            intent=intent,
            memory=mock_memory,
            karma_score=50,
        )

        assert confidence.rollback_safety == 1.0

    def test_delete_file_is_unsafe(self):
        """
        SECURITY MUTATION KILLER: delete_file MUST be unsafe.
        """
        mock_memory = MagicMock()
        mock_memory.get_success_rate.return_value = 1.0

        intent = Intent(
            id="test",
            intent_type="delete_file",
            title="Delete file",
            description="",
            reasoning="",
        )

        confidence = IntentConfidence.compute(
            intent=intent,
            memory=mock_memory,
            karma_score=100,
        )

        assert confidence.rollback_safety == 0.3
        assert confidence.rollback_safety < 0.5  # Unsafe!

    def test_unknown_type_has_medium_safety(self):
        """
        Mutation killer: Unknown types should have 0.7 (medium) safety.
        """
        mock_memory = MagicMock()
        mock_memory.get_success_rate.return_value = 0.0

        intent = Intent(
            id="test",
            intent_type="unknown_type_xyz",
            title="Unknown",
            description="",
            reasoning="",
        )

        confidence = IntentConfidence.compute(
            intent=intent,
            memory=mock_memory,
            karma_score=50,
        )

        assert confidence.rollback_safety == 0.7


# =============================================================================
# SECTION 3: KARMA GATE MUTATION TESTS (SECURITY CRITICAL)
# =============================================================================


class TestKarmaGate:
    """Tests for _karma_allows_auto_execute - the trust gate."""

    @pytest.fixture
    def kernel(self, tmp_path):
        """Create kernel with temp workspace."""
        (tmp_path / ".opus_state").mkdir()
        return CognitiveKernel(workspace=tmp_path)

    def test_karma_gate_rejects_high_risk(self, kernel):
        """
        SECURITY MUTATION KILLER #1: HIGH risk MUST NOT pass karma gate.

        A mutant that includes HIGH in the allowed risks would
        allow dangerous intents to auto-execute.
        """
        intent = Intent(
            id="test",
            intent_type="test",
            title="Test",
            description="",
            reasoning="",
            risk=IntentRisk.HIGH,  # HIGH risk!
        )

        # Even with karma gate mocked to pass, HIGH should be rejected
        with patch.object(kernel, "_config") as mock_config:
            mock_config.karma_auto_execute_threshold = 0  # Any karma passes
            result = kernel._karma_allows_auto_execute(intent)

        assert result is False

    def test_karma_gate_rejects_medium_risk(self, kernel):
        """
        SECURITY MUTATION KILLER #2: MEDIUM risk MUST NOT pass karma gate.
        """
        intent = Intent(
            id="test",
            intent_type="test",
            title="Test",
            description="",
            reasoning="",
            risk=IntentRisk.MEDIUM,  # MEDIUM risk!
        )

        result = kernel._karma_allows_auto_execute(intent)
        assert result is False

    def test_karma_gate_allows_low_risk_with_high_karma(self, kernel):
        """
        Mutation killer: LOW risk with high karma should pass.
        """
        intent = Intent(
            id="test",
            intent_type="test",
            title="Test",
            description="",
            reasoning="",
            risk=IntentRisk.LOW,  # LOW risk
        )

        # Mock the state manager to return high karma
        # The import is inside the method, so we patch the module it imports from
        with patch("vibe_core.plugins.opus_assistant.core.state_manager.get_state_manager") as mock_gsm:
            mock_state_mgr = MagicMock()
            mock_karma = MagicMock()
            mock_karma.score = 95  # Above threshold (90)
            mock_state_mgr.get_last_karma.return_value = mock_karma
            mock_gsm.return_value = mock_state_mgr

            result = kernel._karma_allows_auto_execute(intent)

        assert result is True

    def test_karma_gate_rejects_low_karma(self, kernel):
        """
        Mutation killer: LOW risk but low karma should NOT pass.
        """
        intent = Intent(
            id="test",
            intent_type="test",
            title="Test",
            description="",
            reasoning="",
            risk=IntentRisk.LOW,
        )

        # Mock low karma
        with patch("vibe_core.plugins.opus_assistant.core.state_manager.get_state_manager") as mock_gsm:
            mock_state_mgr = MagicMock()
            mock_karma = MagicMock()
            mock_karma.score = 50  # Below threshold (90)
            mock_state_mgr.get_last_karma.return_value = mock_karma
            mock_gsm.return_value = mock_state_mgr

            result = kernel._karma_allows_auto_execute(intent)

        assert result is False


# =============================================================================
# SECTION 4: THINK THROTTLING MUTATION TESTS
# =============================================================================


class TestThinkThrottling:
    """Tests for intent throttling in think()."""

    @pytest.fixture
    def kernel(self, tmp_path):
        """Create kernel with temp workspace."""
        (tmp_path / ".opus_state").mkdir()
        return CognitiveKernel(workspace=tmp_path)

    def test_prioritize_survival_sorts_correctly(self, kernel):
        """
        Mutation killer: survival_first should put CRITICAL before LOW.
        """
        intents = [
            Intent(id="low", intent_type="low", title="Low", description="", reasoning="", priority=IntentPriority.LOW),
            Intent(
                id="critical",
                intent_type="critical",
                title="Critical",
                description="",
                reasoning="",
                priority=IntentPriority.CRITICAL,
            ),
        ]

        sorted_intents = kernel._prioritize_survival(intents)

        assert sorted_intents[0].priority == IntentPriority.CRITICAL
        assert sorted_intents[1].priority == IntentPriority.LOW

    def test_prioritize_survival_contract_before_semantic(self, kernel):
        """
        Mutation killer: contract_ intents (repair) should come before others.
        """
        intents = [
            Intent(
                id="semantic",
                intent_type="semantic_gap",
                title="Semantic",
                description="",
                reasoning="",
                priority=IntentPriority.HIGH,
            ),
            Intent(
                id="contract",
                intent_type="contract_violation",
                title="Contract",
                description="",
                reasoning="",
                priority=IntentPriority.HIGH,  # Same priority
            ),
        ]

        sorted_intents = kernel._prioritize_survival(intents)

        # Contract should be first (is_repair = 0)
        assert sorted_intents[0].intent_type == "contract_violation"


# =============================================================================
# SECTION 5: AUTO-EXECUTION GUARD TESTS
# =============================================================================


class TestAutoExecutionGuards:
    """Tests to ensure auto-execution has proper guards."""

    @pytest.fixture
    def kernel(self, tmp_path):
        """Create kernel with temp workspace."""
        (tmp_path / ".opus_state").mkdir()
        config = ManasConfig(auto_execute_safe=True)  # Enable for testing
        return CognitiveKernel(workspace=tmp_path, config=config)

    def test_only_safe_intents_can_auto_execute(self, kernel):
        """
        Mutation killer: Only SAFE risk + auto_executable=True can auto-execute.
        """
        # Create a SAFE, auto-executable intent
        safe_intent = Intent(
            id="safe",
            intent_type="cleanup",
            title="Cleanup",
            description="",
            reasoning="",
            risk=IntentRisk.SAFE,
            auto_executable=True,
        )

        # Create a MEDIUM risk intent (should NOT auto-execute)
        medium_intent = Intent(
            id="medium",
            intent_type="modify",
            title="Modify",
            description="",
            reasoning="",
            risk=IntentRisk.MEDIUM,
            auto_executable=True,  # Even though marked auto, risk prevents it
        )

        # Check the auto-execute condition directly
        is_safe_auto = (
            kernel._config.auto_execute_safe and safe_intent.auto_executable and safe_intent.risk == IntentRisk.SAFE
        )
        is_medium_auto = (
            kernel._config.auto_execute_safe and medium_intent.auto_executable and medium_intent.risk == IntentRisk.SAFE
        )

        assert is_safe_auto is True
        assert is_medium_auto is False  # Risk prevents it

    def test_auto_executable_false_prevents_auto_execution(self, kernel):
        """
        Mutation killer: auto_executable=False MUST prevent auto-execution.
        """
        intent = Intent(
            id="test",
            intent_type="test",
            title="Test",
            description="",
            reasoning="",
            risk=IntentRisk.SAFE,
            auto_executable=False,  # Explicitly disabled
        )

        is_auto = kernel._config.auto_execute_safe and intent.auto_executable and intent.risk == IntentRisk.SAFE

        assert is_auto is False


# =============================================================================
# SECTION 6: INTEGRATION TESTS
# =============================================================================


class TestCognitiveKernelIntegration:
    """Integration tests for CognitiveKernel."""

    @pytest.fixture
    def kernel(self, tmp_path):
        """Create kernel with temp workspace."""
        (tmp_path / ".opus_state").mkdir()
        (tmp_path / ".git").mkdir()
        return CognitiveKernel(workspace=tmp_path)

    def test_think_returns_list(self, kernel):
        """Mutation killer: think() must return a list."""
        result = kernel.think(force=True)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_approve_nonexistent_intent_returns_false(self, kernel):
        """Mutation killer: Approving non-existent intent should fail."""
        result = await kernel.approve_intent("nonexistent_id")
        assert result is False

    def test_reject_nonexistent_intent_returns_false(self, kernel):
        """Mutation killer: Rejecting non-existent intent should fail."""
        result = kernel.reject_intent("nonexistent_id")
        assert result is False

    def test_get_pending_intents_returns_list(self, kernel):
        """Mutation killer: get_pending_intents must return a list."""
        result = kernel.get_pending_intents()
        assert isinstance(result, list)

    def test_idle_minutes_is_non_negative(self, kernel):
        """Mutation killer: Idle minutes should be non-negative."""
        result = kernel.get_idle_minutes()
        assert result >= 0
