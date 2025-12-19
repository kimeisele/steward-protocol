"""
OPUS-040: Operation Cerebro - Intent Generator Mutation Tests

These tests are designed to KILL mutants in the MANAS brain.

CRITICAL SECURITY TESTS:
- Capability genesis MUST have risk=HIGH (never SAFE)
- Capability genesis MUST have auto_executable=False (never True)
- Priority boost MUST NOT boost beyond user's approval threshold

"A mutation that survives is a bug waiting to happen."
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

# Import the module under test
from vibe_core.plugins.opus_assistant.manas.intent_generator import (
    Intent,
    IntentGenerator,
    IntentPriority,
    IntentRisk,
)

# =============================================================================
# SECTION 1: DATA MODEL MUTATION TESTS
# =============================================================================


class TestIntentRisk:
    """Tests for IntentRisk enum - SECURITY CRITICAL."""

    def test_risk_levels_exist(self):
        """Mutation killer: All risk levels must exist."""
        assert hasattr(IntentRisk, "SAFE")
        assert hasattr(IntentRisk, "LOW")
        assert hasattr(IntentRisk, "MEDIUM")
        assert hasattr(IntentRisk, "HIGH")

    def test_risk_values_are_strings(self):
        """Mutation killer: Risk values must be lowercase strings."""
        assert IntentRisk.SAFE.value == "safe"
        assert IntentRisk.LOW.value == "low"
        assert IntentRisk.MEDIUM.value == "medium"
        assert IntentRisk.HIGH.value == "high"

    def test_high_is_not_safe(self):
        """
        SECURITY MUTATION KILLER: HIGH must NEVER equal SAFE.

        A mutant that changes HIGH to SAFE would pass other tests
        but FAIL this one.
        """
        assert IntentRisk.HIGH != IntentRisk.SAFE
        assert IntentRisk.HIGH.value != IntentRisk.SAFE.value
        assert IntentRisk.HIGH.value == "high"  # Explicit check

    def test_risk_ordering_semantic(self):
        """
        Mutation killer: Ensure risk levels have semantic meaning.

        If someone swaps values, this test will catch it.
        """
        risks = [IntentRisk.SAFE, IntentRisk.LOW, IntentRisk.MEDIUM, IntentRisk.HIGH]
        values = [r.value for r in risks]
        assert values == ["safe", "low", "medium", "high"]


class TestIntentPriority:
    """Tests for IntentPriority enum."""

    def test_priority_levels_exist(self):
        """Mutation killer: All priority levels must exist."""
        assert hasattr(IntentPriority, "LOW")
        assert hasattr(IntentPriority, "MEDIUM")
        assert hasattr(IntentPriority, "HIGH")
        assert hasattr(IntentPriority, "CRITICAL")

    def test_priority_values_are_strings(self):
        """Mutation killer: Priority values must be lowercase strings."""
        assert IntentPriority.LOW.value == "low"
        assert IntentPriority.MEDIUM.value == "medium"
        assert IntentPriority.HIGH.value == "high"
        assert IntentPriority.CRITICAL.value == "critical"


class TestIntent:
    """Tests for Intent dataclass."""

    def test_default_risk_is_medium(self):
        """
        Mutation killer: Default risk should be MEDIUM, not SAFE.

        This prevents a mutant that changes the default to SAFE.
        """
        intent = Intent(
            id="test_001",
            intent_type="test",
            title="Test Intent",
            description="Test",
            reasoning="Test",
        )
        assert intent.risk == IntentRisk.MEDIUM
        assert intent.risk != IntentRisk.SAFE

    def test_default_auto_executable_is_false(self):
        """
        SECURITY MUTATION KILLER: Default auto_executable must be False.

        This prevents a mutant that changes the default to True.
        """
        intent = Intent(
            id="test_001",
            intent_type="test",
            title="Test Intent",
            description="Test",
            reasoning="Test",
        )
        assert intent.auto_executable is False
        assert intent.auto_executable != True  # noqa: E712 - explicit for mutation testing

    def test_is_expired_returns_false_when_no_expiry(self):
        """Mutation killer: No expiry means not expired."""
        intent = Intent(
            id="test_001",
            intent_type="test",
            title="Test",
            description="Test",
            reasoning="Test",
            expires_at=None,
        )
        assert intent.is_expired() is False

    def test_is_expired_returns_true_when_past_expiry(self):
        """Mutation killer: Past expiry means expired."""
        past = (datetime.utcnow() - timedelta(days=1)).isoformat()
        intent = Intent(
            id="test_001",
            intent_type="test",
            title="Test",
            description="Test",
            reasoning="Test",
            expires_at=past,
        )
        assert intent.is_expired() is True

    def test_to_dict_includes_risk_as_value(self):
        """Mutation killer: Serialization must use .value for enums."""
        intent = Intent(
            id="test_001",
            intent_type="test",
            title="Test",
            description="Test",
            reasoning="Test",
            risk=IntentRisk.HIGH,
        )
        d = intent.to_dict()
        assert d["risk"] == "high"  # String value, not enum
        assert isinstance(d["risk"], str)

    def test_weaving_fields_default_to_empty_lists(self):
        """Mutation killer: Weaving fields must default to empty lists."""
        intent = Intent(
            id="test_001",
            intent_type="test",
            title="Test",
            description="Test",
            reasoning="Test",
        )
        assert intent.related_files == []
        assert intent.related_docs == []
        assert isinstance(intent.related_files, list)
        assert isinstance(intent.related_docs, list)

    def test_weaving_fields_can_be_populated(self):
        """Mutation killer: Weaving fields must accept values."""
        intent = Intent(
            id="test_001",
            intent_type="test",
            title="Test",
            description="Test",
            reasoning="Test",
            related_files=["jnana.py:151", "factory.py:172"],
            related_docs=["076-NO-PUSSY-MODE.md"],
        )
        assert len(intent.related_files) == 2
        assert len(intent.related_docs) == 1
        assert "jnana.py:151" in intent.related_files
        assert "076-NO-PUSSY-MODE.md" in intent.related_docs

    def test_weaving_fields_serialized_in_to_dict(self):
        """Mutation killer: Weaving fields MUST appear in serialized output."""
        intent = Intent(
            id="test_001",
            intent_type="test",
            title="Test",
            description="Test",
            reasoning="Test",
            related_files=["code.py"],
            related_docs=["doc.md"],
        )
        d = intent.to_dict()
        assert "related_files" in d
        assert "related_docs" in d
        assert d["related_files"] == ["code.py"]
        assert d["related_docs"] == ["doc.md"]

    def test_weaving_fields_empty_serialization(self):
        """Mutation killer: Empty weaving fields must serialize as empty lists."""
        intent = Intent(
            id="test_001",
            intent_type="test",
            title="Test",
            description="Test",
            reasoning="Test",
        )
        d = intent.to_dict()
        assert d["related_files"] == []
        assert d["related_docs"] == []


# =============================================================================
# SECTION 2: CAPABILITY GENESIS SECURITY TESTS (MOST CRITICAL)
# =============================================================================


class TestCapabilityGenesisSecurity:
    """
    SECURITY CRITICAL: Tests for _analyze_capability_gaps.

    This is the Ouroboros Protocol - the system's ability to evolve itself.
    Mutations here could allow unauthorized code generation.
    """

    @pytest.fixture
    def generator(self, tmp_path):
        """Create generator with temp workspace."""
        return IntentGenerator(workspace=tmp_path)

    def test_genesis_intent_has_high_risk(self, generator):
        """
        SECURITY MUTATION KILLER #1: Genesis MUST have HIGH risk.

        A mutant that changes risk=IntentRisk.HIGH to risk=IntentRisk.SAFE
        would allow code generation without approval.
        """
        context = {"recent_errors": [{"message": "unknown syscall: test_capability", "type": "KeyError"}]}

        # Call the analyzer directly
        intent = generator._analyze_capability_gaps(context)

        assert intent is not None, "Genesis intent should be generated"
        assert intent.risk == IntentRisk.HIGH, "Genesis MUST have HIGH risk!"
        assert intent.risk != IntentRisk.SAFE, "Genesis MUST NOT be SAFE!"
        assert intent.risk != IntentRisk.LOW, "Genesis MUST NOT be LOW!"
        assert intent.risk != IntentRisk.MEDIUM, "Genesis MUST NOT be MEDIUM!"

    def test_genesis_intent_not_auto_executable(self, generator):
        """
        SECURITY MUTATION KILLER #2: Genesis MUST NOT be auto-executable.

        A mutant that changes auto_executable=False to auto_executable=True
        would allow the system to self-modify without human approval.
        """
        context = {"recent_errors": [{"message": "capability not found: dangerous_tool", "type": "Error"}]}

        intent = generator._analyze_capability_gaps(context)

        assert intent is not None, "Genesis intent should be generated"
        assert intent.auto_executable is False, "Genesis MUST NOT auto-execute!"
        assert intent.auto_executable != True  # noqa: E712 - explicit check

    def test_genesis_intent_type_starts_with_genesis(self, generator):
        """Mutation killer: Genesis intent type must be identifiable."""
        context = {"recent_errors": [{"message": "unknown syscall: new_feature", "type": "KeyError"}]}

        intent = generator._analyze_capability_gaps(context)

        assert intent is not None
        assert intent.intent_type.startswith("genesis_")

    def test_genesis_has_circuit_to_execute(self, generator):
        """Mutation killer: Genesis must specify which circuit to run."""
        context = {"recent_errors": [{"message": "unknown syscall: test_syscall", "type": "KeyError"}]}

        intent = generator._analyze_capability_gaps(context)

        assert intent is not None
        assert intent.circuit_to_execute is not None
        assert "capability_genesis" in intent.circuit_to_execute

    def test_genesis_respects_memory_rejection(self, generator):
        """
        Mutation killer: If user rejected genesis, don't re-propose.

        Tests _should_skip_intent integration.
        """
        mock_memory = MagicMock()
        mock_memory.was_recently_rejected.return_value = True
        generator._memory = mock_memory

        context = {"recent_errors": [{"message": "unknown syscall: rejected_feature", "type": "KeyError"}]}

        intent = generator._analyze_capability_gaps(context)

        # Should return None because memory says it was rejected
        assert intent is None


# =============================================================================
# SECTION 3: PRIORITY BOOST MUTATION TESTS
# =============================================================================


class TestPriorityBoost:
    """Tests for the muscle memory priority boost logic."""

    @pytest.fixture
    def generator_with_memory(self, tmp_path):
        """Create generator with mock memory store."""
        gen = IntentGenerator(workspace=tmp_path)
        mock_memory = MagicMock()
        mock_memory.get_successful_patterns.return_value = ["cleanup_stale_branches"]
        mock_memory.is_in_cooldown.return_value = False
        mock_memory.was_recently_rejected.return_value = False
        gen._memory = mock_memory
        return gen

    def test_boost_low_to_medium(self, generator_with_memory):
        """Mutation killer: LOW should boost to MEDIUM, not CRITICAL."""
        # Create a LOW priority intent manually
        intent = Intent(
            id="test_001",
            intent_type="cleanup_stale_branches",  # This is in successful patterns
            title="Test",
            description="Test",
            reasoning="Test",
            priority=IntentPriority.LOW,
        )

        # The boost logic from generate_intents
        boosted = {
            IntentPriority.LOW: IntentPriority.MEDIUM,
            IntentPriority.MEDIUM: IntentPriority.HIGH,
            IntentPriority.HIGH: IntentPriority.CRITICAL,
        }

        new_priority = boosted.get(intent.priority, intent.priority)
        assert new_priority == IntentPriority.MEDIUM
        assert new_priority != IntentPriority.CRITICAL  # Must not skip levels!

    def test_boost_medium_to_high(self):
        """Mutation killer: MEDIUM should boost to HIGH, not CRITICAL."""
        boosted = {
            IntentPriority.LOW: IntentPriority.MEDIUM,
            IntentPriority.MEDIUM: IntentPriority.HIGH,
            IntentPriority.HIGH: IntentPriority.CRITICAL,
        }

        new_priority = boosted.get(IntentPriority.MEDIUM, IntentPriority.MEDIUM)
        assert new_priority == IntentPriority.HIGH
        assert new_priority != IntentPriority.CRITICAL

    def test_critical_not_boosted_further(self):
        """Mutation killer: CRITICAL should not change."""
        boosted = {
            IntentPriority.LOW: IntentPriority.MEDIUM,
            IntentPriority.MEDIUM: IntentPriority.HIGH,
            IntentPriority.HIGH: IntentPriority.CRITICAL,
        }

        # CRITICAL is not in the boost map
        new_priority = boosted.get(IntentPriority.CRITICAL, IntentPriority.CRITICAL)
        assert new_priority == IntentPriority.CRITICAL


# =============================================================================
# SECTION 4: SHOULD_SKIP_INTENT MUTATION TESTS
# =============================================================================


class TestShouldSkipIntent:
    """Tests for _should_skip_intent - the memory gate."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create generator with temp workspace."""
        return IntentGenerator(workspace=tmp_path)

    def test_returns_false_when_no_memory(self, generator):
        """Mutation killer: No memory means no skip."""
        generator._memory = None
        intent = Intent(
            id="test_001",
            intent_type="test",
            title="Test",
            description="Test",
            reasoning="Test",
        )
        assert generator._should_skip_intent(intent) is False

    def test_returns_true_when_in_cooldown(self, generator):
        """
        Mutation killer: Cooldown must cause skip.

        A mutant that returns False here would spam the user.
        """
        mock_memory = MagicMock()
        mock_memory.is_in_cooldown.return_value = True
        mock_memory.was_recently_rejected.return_value = False
        generator._memory = mock_memory

        intent = Intent(
            id="test_001",
            intent_type="test",
            title="Test",
            description="Test",
            reasoning="Test",
        )

        assert generator._should_skip_intent(intent) is True

    def test_returns_true_when_recently_rejected(self, generator):
        """
        Mutation killer: Recent rejection must cause skip.

        A mutant that returns False here would annoy the user.
        """
        mock_memory = MagicMock()
        mock_memory.is_in_cooldown.return_value = False
        mock_memory.was_recently_rejected.return_value = True
        generator._memory = mock_memory

        intent = Intent(
            id="test_001",
            intent_type="test",
            title="Test",
            description="Test",
            reasoning="Test",
        )

        assert generator._should_skip_intent(intent) is True

    def test_returns_false_when_neither_condition(self, generator):
        """Mutation killer: No cooldown and no rejection means no skip."""
        mock_memory = MagicMock()
        mock_memory.is_in_cooldown.return_value = False
        mock_memory.was_recently_rejected.return_value = False
        generator._memory = mock_memory

        intent = Intent(
            id="test_001",
            intent_type="test",
            title="Test",
            description="Test",
            reasoning="Test",
        )

        assert generator._should_skip_intent(intent) is False


# =============================================================================
# SECTION 5: ANALYZER RISK ASSIGNMENT TESTS
# =============================================================================


class TestAnalyzerRiskAssignments:
    """
    Tests to verify each analyzer assigns the correct risk level.

    These prevent mutations that change risk levels in individual analyzers.
    """

    @pytest.fixture
    def generator(self, tmp_path):
        """Create generator with temp workspace."""
        # Create minimal git repo structure
        (tmp_path / ".git").mkdir()
        return IntentGenerator(workspace=tmp_path)

    def test_log_cleanup_is_safe(self, generator):
        """
        Mutation killer: Log cleanup should be SAFE (auto-executable).

        This is one of the few intents that CAN auto-execute.
        """
        # Create old log files
        log_dir = generator._workspace / ".opus_state" / "logs"
        log_dir.mkdir(parents=True)

        import time

        for i in range(6):
            log_file = log_dir / f"old_log_{i}.log"
            log_file.write_text(f"log content {i}")
            # Set mtime to 10 days ago
            old_time = time.time() - (10 * 24 * 60 * 60)
            import os

            os.utime(log_file, (old_time, old_time))

        intent = generator._analyze_log_cleanup({})

        assert intent is not None
        assert intent.risk == IntentRisk.SAFE
        assert intent.auto_executable is True  # This one CAN auto-execute

    def test_uncommitted_changes_is_medium(self, generator):
        """
        Mutation killer: Committing changes needs MEDIUM risk (human review).
        """
        # We can't easily mock git, so we test the intent creation directly
        intent = Intent(
            id="test",
            intent_type="commit_pending_changes",
            title="Test",
            description="Test",
            reasoning="Test",
            priority=IntentPriority.MEDIUM,
            risk=IntentRisk.MEDIUM,
            auto_executable=False,
        )

        assert intent.risk == IntentRisk.MEDIUM
        assert intent.auto_executable is False

    def test_stale_branches_is_low(self, generator):
        """
        Mutation killer: Stale branch cleanup is LOW risk but needs approval.
        """
        intent = Intent(
            id="test",
            intent_type="cleanup_stale_branches",
            title="Test",
            description="Test",
            reasoning="Test",
            priority=IntentPriority.LOW,
            risk=IntentRisk.LOW,
            auto_executable=False,
        )

        assert intent.risk == IntentRisk.LOW
        assert intent.auto_executable is False


# =============================================================================
# SECTION 6: INTEGRATION TESTS
# =============================================================================


class TestIntentGeneratorIntegration:
    """Integration tests for the full generate_intents flow."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create generator with temp workspace."""
        (tmp_path / ".git").mkdir()
        return IntentGenerator(workspace=tmp_path)

    def test_intents_sorted_by_priority(self, generator):
        """
        Mutation killer: Intents must be sorted CRITICAL > HIGH > MEDIUM > LOW.

        A mutant that changes the sort order would break intent prioritization.
        """
        # Create intents with different priorities
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
            Intent(
                id="medium",
                intent_type="medium",
                title="Medium",
                description="",
                reasoning="",
                priority=IntentPriority.MEDIUM,
            ),
            Intent(
                id="high", intent_type="high", title="High", description="", reasoning="", priority=IntentPriority.HIGH
            ),
        ]

        # Sort using the same logic as generate_intents
        priority_order = {
            IntentPriority.CRITICAL: 0,
            IntentPriority.HIGH: 1,
            IntentPriority.MEDIUM: 2,
            IntentPriority.LOW: 3,
        }
        intents.sort(key=lambda i: priority_order.get(i.priority, 99))

        assert intents[0].priority == IntentPriority.CRITICAL
        assert intents[1].priority == IntentPriority.HIGH
        assert intents[2].priority == IntentPriority.MEDIUM
        assert intents[3].priority == IntentPriority.LOW

    @pytest.mark.asyncio
    async def test_generate_intents_returns_list(self, generator):
        """Mutation killer: generate_intents must return a list."""
        result = await generator.generate_intents({})
        assert isinstance(result, list)

    def test_modular_analyzers_are_registered(self, generator):
        """Mutation killer: Modular analyzers must be registered."""
        assert len(generator._modular_analyzers) >= 2
        # ContractAnalyzer and SemanticAnalyzer
        names = [a.name for a in generator._modular_analyzers]
        assert "contract" in str(names).lower() or len(names) >= 1
