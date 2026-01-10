"""
OPUS-040: Operation Cerebro - Memory Store Mutation Tests

These tests are designed to KILL mutants in the MANAS hippocampus.

CRITICAL MEMORY TESTS:
- Success rate MUST increase with successes
- Success rate MUST decrease with failures
- Memory MUST be persisted (no amnesia)
- Cooldown MUST prevent repeated failures

"A system without memory makes every mistake infinitely."
"A system with corrupt memory holds errors as truths."
"""

import json
from datetime import datetime

import pytest

# Import the module under test
from vibe_core.plugins.opus_assistant.manas.memory_store import (
    MemoryEntry,
    MemoryStore,
)
from vibe_core.protocols.akashic import AkashicProtocol
from vibe_core.state.state_service import reset_state_service


@pytest.fixture(autouse=True)
def clean_state_service():
    """Ensure state service is fresh for each test."""
    reset_state_service()
    yield
    reset_state_service()



def test_implements_akashic_protocol():
    """
    YAMARAJA TEST: MemoryStore must satisfy AkashicProtocol.
    """
    store = MemoryStore()
    assert isinstance(store, AkashicProtocol), "MemoryStore must implement AkashicProtocol"


# =============================================================================
# SECTION 1: MemoryEntry MUTATION TESTS
# =============================================================================


class TestMemoryEntry:
    """Tests for MemoryEntry dataclass."""

    def test_to_dict_returns_dict(self):
        """Mutation killer: to_dict must return a dictionary."""
        entry = MemoryEntry(
            intent_type="test",
            intent_description="Test entry",
            timestamp=datetime.utcnow().isoformat(),
            outcome="success",
        )
        result = entry.to_dict()
        assert isinstance(result, dict)

    def test_to_dict_contains_all_fields(self):
        """Mutation killer: to_dict must include all fields."""
        entry = MemoryEntry(
            intent_type="test_type",
            intent_description="Test description",
            timestamp="2025-01-01T00:00:00",
            outcome="success",
            context={"key": "value"},
            feedback="test feedback",
            execution_time_ms=100,
        )
        result = entry.to_dict()

        assert result["intent_type"] == "test_type"
        assert result["intent_description"] == "Test description"
        assert result["timestamp"] == "2025-01-01T00:00:00"
        assert result["outcome"] == "success"
        assert result["context"] == {"key": "value"}
        assert result["feedback"] == "test feedback"
        assert result["execution_time_ms"] == 100

    def test_from_dict_creates_entry(self):
        """Mutation killer: from_dict must create valid entry."""
        data = {
            "intent_type": "test",
            "intent_description": "Test",
            "timestamp": "2025-01-01T00:00:00",
            "outcome": "failed",
            "context": {},
            "feedback": None,
            "execution_time_ms": None,
        }
        entry = MemoryEntry.from_dict(data)

        assert entry.intent_type == "test"
        assert entry.outcome == "failed"

    def test_roundtrip_serialization(self):
        """Mutation killer: to_dict → from_dict must preserve data."""
        original = MemoryEntry(
            intent_type="roundtrip_test",
            intent_description="Testing roundtrip",
            timestamp="2025-01-01T12:00:00",
            outcome="success",
            context={"test": True},
            feedback="all good",
            execution_time_ms=500,
        )

        dict_form = original.to_dict()
        restored = MemoryEntry.from_dict(dict_form)

        assert restored.intent_type == original.intent_type
        assert restored.intent_description == original.intent_description
        assert restored.timestamp == original.timestamp
        assert restored.outcome == original.outcome
        assert restored.context == original.context
        assert restored.feedback == original.feedback
        assert restored.execution_time_ms == original.execution_time_ms


# =============================================================================
# SECTION 2: SUCCESS RATE MUTATION TESTS (MOST CRITICAL)
# =============================================================================


class TestSuccessRate:
    """
    Tests for get_success_rate - the learning mechanism.

    These tests prevent:
    - "Eternal Junior" (always returns 0)
    - "Dunning-Kruger" (always returns 1)
    - Inverted success counting
    """

    @pytest.fixture
    def store(self, tmp_path):
        """Create memory store with temp workspace."""
        (tmp_path / ".opus_state").mkdir()
        return MemoryStore(workspace=tmp_path)

    def test_no_history_returns_neutral(self, store):
        """
        Mutation killer: No history should return 0.5 (neutral).

        NOT 0.0 (eternal junior) and NOT 1.0 (Dunning-Kruger).
        """
        rate = store.get_success_rate("unknown_type")

        assert rate == 0.5, "No history should return neutral 0.5"
        assert rate != 0.0, "Must NOT return 0.0 (eternal junior)"
        assert rate != 1.0, "Must NOT return 1.0 (Dunning-Kruger)"

    def test_all_successes_returns_one(self, store):
        """
        Mutation killer: All successes should return 1.0.
        """
        # Add 3 successes
        for _ in range(3):
            store.record_intent_outcome("test_type", "Test", "success")

        rate = store.get_success_rate("test_type")
        assert rate == 1.0

    def test_all_failures_returns_zero(self, store):
        """
        Mutation killer: All failures should return 0.0.
        """
        # Add 3 failures
        for _ in range(3):
            store.record_intent_outcome("test_type", "Test", "failed")

        rate = store.get_success_rate("test_type")
        assert rate == 0.0

    def test_mixed_outcomes_returns_ratio(self, store):
        """
        CRITICAL MUTATION KILLER: Mixed outcomes must return correct ratio.

        This catches mutants that:
        - Swap success/failure counting
        - Return hardcoded values
        - Miscalculate the ratio
        """
        # 2 successes, 2 failures = 0.5
        store.record_intent_outcome("mixed_type", "Test", "success")
        store.record_intent_outcome("mixed_type", "Test", "success")
        store.record_intent_outcome("mixed_type", "Test", "failed")
        store.record_intent_outcome("mixed_type", "Test", "failed")

        rate = store.get_success_rate("mixed_type")
        assert rate == 0.5

    def test_success_rate_increases_with_success(self, store):
        """
        MUTATION KILLER: Success MUST increase success rate.

        The "eternal junior" mutant would fail this test.
        """
        # Start with 1 failure
        store.record_intent_outcome("learning_type", "Test", "failed")
        rate_before = store.get_success_rate("learning_type")

        # Add a success
        store.record_intent_outcome("learning_type", "Test", "success")
        rate_after = store.get_success_rate("learning_type")

        assert rate_after > rate_before, "Success MUST increase rate!"

    def test_success_rate_decreases_with_failure(self, store):
        """
        MUTATION KILLER: Failure MUST decrease success rate.

        The "Dunning-Kruger" mutant would fail this test.
        """
        # Start with 1 success
        store.record_intent_outcome("humble_type", "Test", "success")
        rate_before = store.get_success_rate("humble_type")

        # Add a failure
        store.record_intent_outcome("humble_type", "Test", "failed")
        rate_after = store.get_success_rate("humble_type")

        assert rate_after < rate_before, "Failure MUST decrease rate!"

    def test_rejected_and_pending_not_counted(self, store):
        """
        Mutation killer: Only success/failed should affect rate.
        """
        # Add success and rejected
        store.record_intent_outcome("filter_type", "Test", "success")
        store.record_intent_outcome("filter_type", "Test", "rejected")
        store.record_intent_outcome("filter_type", "Test", "pending")

        # Only 1 countable outcome (success), so rate should be 1.0
        rate = store.get_success_rate("filter_type")
        assert rate == 1.0

    def test_different_types_independent(self, store):
        """
        Mutation killer: Different intent types have independent rates.
        """
        store.record_intent_outcome("type_a", "Test", "success")
        store.record_intent_outcome("type_a", "Test", "success")
        store.record_intent_outcome("type_b", "Test", "failed")
        store.record_intent_outcome("type_b", "Test", "failed")

        assert store.get_success_rate("type_a") == 1.0
        assert store.get_success_rate("type_b") == 0.0


# =============================================================================
# SECTION 3: MEMORY PERSISTENCE TESTS (ANTI-AMNESIA)
# =============================================================================


class TestMemoryPersistence:
    """
    Tests for memory persistence - anti-amnesia protection.

    These tests prevent:
    - "Amnesia" mutation (remember does nothing)
    - "Goldfish" mutation (save does nothing)
    """

    def test_remember_actually_stores(self, tmp_path):
        """
        MUTATION KILLER: remember() MUST actually store the entry.

        The "amnesia" mutant would fail this test.
        """
        (tmp_path / ".opus_state").mkdir()
        store = MemoryStore(workspace=tmp_path)

        entry = MemoryEntry(
            intent_type="amnesia_test",
            intent_description="Testing memory",
            timestamp=datetime.utcnow().isoformat(),
            outcome="success",
        )

        before_count = len(store.get_all_memories())
        store.remember(entry)
        after_count = len(store.get_all_memories())

        assert after_count == before_count + 1, "remember() MUST add entry!"

    def test_memory_persists_across_instances(self, tmp_path):
        """
        MUTATION KILLER: Memory MUST survive instance recreation.

        The "goldfish" mutant would fail this test.
        """
        (tmp_path / ".opus_state").mkdir()

        # First instance - store a memory
        store1 = MemoryStore(workspace=tmp_path)
        store1.record_intent_outcome("persistent_test", "Test", "success")

        # Second instance - memory should still be there
        store2 = MemoryStore(workspace=tmp_path)
        memories = store2.get_all_memories()

        assert len(memories) >= 1, "Memory MUST persist across instances!"
        assert any(m.intent_type == "persistent_test" for m in memories)

    def test_memory_file_created(self, tmp_path):
        """
        Mutation killer: Memory file must be created on save.
        """
        (tmp_path / ".opus_state").mkdir()
        store = MemoryStore(workspace=tmp_path)
        store.record_intent_outcome("file_test", "Test", "success")

        assert store._memory_file.exists(), "Memory file MUST be created!"

    def test_memory_file_valid_json(self, tmp_path):
        """
        Mutation killer: Memory file must contain valid JSON.
        """
        (tmp_path / ".opus_state").mkdir()
        store = MemoryStore(workspace=tmp_path)
        store.record_intent_outcome("json_test", "Test", "success")

        content = store._memory_file.read_text()

        # Should not raise
        data = json.loads(content)
        assert "memories" in data
        assert isinstance(data["memories"], list)


# =============================================================================
# SECTION 4: COOLDOWN MUTATION TESTS
# =============================================================================


class TestCooldown:
    """
    Tests for cooldown mechanism - prevent repeated failures.

    These tests prevent:
    - "Fearless Fool" mutation (cooldown always returns False)
    """

    @pytest.fixture
    def store(self, tmp_path):
        """Create memory store with temp workspace."""
        (tmp_path / ".opus_state").mkdir()
        return MemoryStore(workspace=tmp_path)

    def test_no_failure_no_cooldown(self, store):
        """
        Mutation killer: No failure means no cooldown.
        """
        assert store.is_in_cooldown("no_failure_type") is False

    def test_recent_failure_triggers_cooldown(self, store):
        """
        MUTATION KILLER: Recent failure MUST trigger cooldown.

        The "fearless fool" mutant would fail this test.
        """
        store.record_intent_outcome("cooldown_test", "Test", "failed")

        assert store.is_in_cooldown("cooldown_test") is True, "Recent failure MUST trigger cooldown!"

    def test_success_does_not_trigger_cooldown(self, store):
        """
        Mutation killer: Success should NOT trigger cooldown.
        """
        store.record_intent_outcome("success_type", "Test", "success")

        assert store.is_in_cooldown("success_type") is False

    def test_cooldown_is_type_specific(self, store):
        """
        Mutation killer: Cooldown should be per intent type.
        """
        store.record_intent_outcome("failing_type", "Test", "failed")

        assert store.is_in_cooldown("failing_type") is True
        assert store.is_in_cooldown("other_type") is False


# =============================================================================
# SECTION 5: REJECTION TRACKING TESTS
# =============================================================================


class TestRejectionTracking:
    """Tests for was_recently_rejected - respect user decisions."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create memory store with temp workspace."""
        (tmp_path / ".opus_state").mkdir()
        return MemoryStore(workspace=tmp_path)

    def test_no_rejection_returns_false(self, store):
        """Mutation killer: No rejection means not rejected."""
        assert store.was_recently_rejected("never_rejected") is False

    def test_recent_rejection_returns_true(self, store):
        """
        MUTATION KILLER: Recent rejection MUST be detected.
        """
        store.record_intent_outcome("rejected_type", "Test", "rejected")

        assert store.was_recently_rejected("rejected_type") is True

    def test_rejection_is_type_specific(self, store):
        """Mutation killer: Rejection tracking is per type."""
        store.record_intent_outcome("rejected_type", "Test", "rejected")

        assert store.was_recently_rejected("rejected_type") is True
        assert store.was_recently_rejected("other_type") is False


# =============================================================================
# SECTION 6: SUCCESSFUL PATTERNS TESTS
# =============================================================================


class TestSuccessfulPatterns:
    """Tests for get_successful_patterns - muscle memory."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create memory store with temp workspace."""
        (tmp_path / ".opus_state").mkdir()
        return MemoryStore(workspace=tmp_path)

    def test_empty_store_returns_empty(self, store):
        """Mutation killer: Empty store has no patterns."""
        patterns = store.get_successful_patterns()
        assert patterns == []

    def test_single_success_not_pattern(self, store):
        """Mutation killer: Need at least 2 attempts for pattern."""
        store.record_intent_outcome("single_success", "Test", "success")

        patterns = store.get_successful_patterns()
        assert "single_success" not in patterns

    def test_consistent_success_is_pattern(self, store):
        """
        MUTATION KILLER: Consistent success MUST be recognized as pattern.
        """
        # 3 successes = 100% success rate
        store.record_intent_outcome("muscle_memory", "Test", "success")
        store.record_intent_outcome("muscle_memory", "Test", "success")
        store.record_intent_outcome("muscle_memory", "Test", "success")

        patterns = store.get_successful_patterns()
        assert "muscle_memory" in patterns

    def test_mostly_failure_not_pattern(self, store):
        """
        Mutation killer: Low success rate should NOT be pattern.
        """
        # 1 success, 2 failures = 33% success rate (below 70% threshold)
        store.record_intent_outcome("failure_prone", "Test", "success")
        store.record_intent_outcome("failure_prone", "Test", "failed")
        store.record_intent_outcome("failure_prone", "Test", "failed")

        patterns = store.get_successful_patterns()
        assert "failure_prone" not in patterns

    def test_threshold_is_70_percent(self, store):
        """
        Mutation killer: Threshold is exactly 70%.
        """
        # 7 successes, 3 failures = 70% (should be included)
        for _ in range(7):
            store.record_intent_outcome("exactly_70", "Test", "success")
        for _ in range(3):
            store.record_intent_outcome("exactly_70", "Test", "failed")

        patterns = store.get_successful_patterns()
        assert "exactly_70" in patterns

        # 69% should NOT be included
        for _ in range(69):
            store.record_intent_outcome("below_70", "Test", "success")
        for _ in range(31):
            store.record_intent_outcome("below_70", "Test", "failed")

        patterns = store.get_successful_patterns()
        assert "below_70" not in patterns


# =============================================================================
# SECTION 7: PRUNING AND LIMITS TESTS
# =============================================================================


class TestPruningAndLimits:
    """Tests for memory pruning and limits."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create memory store with temp workspace."""
        (tmp_path / ".opus_state").mkdir()
        return MemoryStore(workspace=tmp_path)

    def test_max_memories_enforced(self, store):
        """
        Mutation killer: Memory should not exceed MAX_MEMORIES.
        """
        # Add more than MAX_MEMORIES
        for i in range(store.MAX_MEMORIES + 50):
            store.record_intent_outcome(f"type_{i}", "Test", "success")

        assert len(store.get_all_memories()) <= store.MAX_MEMORIES

    def test_clear_removes_all(self, store):
        """
        Mutation killer: clear() must remove all memories.
        """
        store.record_intent_outcome("to_clear", "Test", "success")
        store.record_intent_outcome("to_clear_2", "Test", "failed")

        store.clear()

        assert len(store.get_all_memories()) == 0


# =============================================================================
# SECTION 8: GET LAST ATTEMPT TESTS
# =============================================================================


class TestGetLastAttempt:
    """Tests for get_last_attempt - finding most recent."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create memory store with temp workspace."""
        (tmp_path / ".opus_state").mkdir()
        return MemoryStore(workspace=tmp_path)

    def test_no_attempts_returns_none(self, store):
        """Mutation killer: No attempts should return None."""
        result = store.get_last_attempt("nonexistent")
        assert result is None

    def test_returns_most_recent(self, store):
        """
        Mutation killer: Should return the MOST RECENT attempt.
        """
        store.record_intent_outcome("recent_test", "First", "failed")
        store.record_intent_outcome("recent_test", "Second", "success")

        result = store.get_last_attempt("recent_test")

        assert result is not None
        assert result.intent_description == "Second"
        assert result.outcome == "success"
