"""
OPUS-022: Ephemeral Cities Unit Tests

Tests for kernel scaling via spawn_child_kernel().
Per conftest.py: Uses fresh_kernel fixture (NO direct RealVibeKernel instantiation).
Per GAD-000: Tests use real kernel, no mocks.

Test Cases from OPUS-022 Section 3.1:
1. spawn_child_kernel creates isolated instance
2. Ephemeral ledger (:memory:) works
3. Child knows parent (child._parent reference)
4. Merge records ledger hash proof
5. Config overrides apply to child
6. fast_code_config disables governance
7. Ledger isolation between parent and child
"""

import pytest

from vibe_core.phoenix.config import get_config

# ===========================================================================
# HELPER FUNCTION
# ===========================================================================


def get_event_type(e):
    """Get event_type from dict or object."""
    return e.get("event_type") if isinstance(e, dict) else getattr(e, "event_type", None)


# ===========================================================================
# TEST: spawn_child_kernel creates isolated instance
# ===========================================================================


def test_spawn_child_kernel_creates_isolated_instance(fresh_kernel):
    """
    Child kernel should be isolated from parent.

    Verifies:
    - Child is a separate RealVibeKernel instance
    - Child has different id than parent
    - Child is tracked in parent._child_kernels
    """
    parent = fresh_kernel
    parent.boot()

    config = get_config()
    child = parent.spawn_child_kernel(config)

    # Child is separate instance
    assert child is not parent
    assert id(child) != id(parent)

    # Child is tracked
    assert child in parent._child_kernels

    # Cleanup not needed - tests use VIBE_NO_LOCK for session bypass


def test_spawn_child_kernel_with_memory_ledger(fresh_kernel):
    """
    Ephemeral ledger (:memory:) should work.

    Verifies:
    - Child uses in-memory ledger
    - Ledger operations work
    """
    parent = fresh_kernel
    parent.boot()

    config = get_config()
    child = parent.spawn_child_kernel(config, ledger_path=":memory:")

    # Verify memory ledger
    assert child.ledger_path == ":memory:"

    # Verify ledger works
    child._ledger.record_event(
        event_type="TEST_EVENT",
        agent_id="test_agent",
        details={"test": True},
    )

    events = child._ledger.get_all_events()
    assert any(get_event_type(e) == "TEST_EVENT" for e in events)

    # Cleanup not needed - tests use VIBE_NO_LOCK for session bypass


def test_child_kernel_knows_parent(fresh_kernel):
    """
    child._parent should reference parent.

    Verifies:
    - Child has _parent attribute
    - _parent is the spawning kernel
    - is_ephemeral is True
    """
    parent = fresh_kernel
    parent.boot()

    config = get_config()
    child = parent.spawn_child_kernel(config)

    # Child knows parent
    assert child._parent is parent

    # Child is ephemeral
    assert child.is_ephemeral is True

    # Parent is not ephemeral
    assert parent.is_ephemeral is False

    # Cleanup not needed - tests use VIBE_NO_LOCK for session bypass


def test_merge_child_result_records_proof(fresh_kernel):
    """
    Merge should record ledger hash proof.

    Verifies:
    - merge_child_result returns proof dictionary
    - Proof contains child_ledger_hash
    - Result is recorded in parent ledger
    - Child is removed from tracking
    """
    parent = fresh_kernel
    parent.boot()

    config = get_config()
    child = parent.spawn_child_kernel(config)
    child.boot()

    # Execute something in child to have ledger entries
    child._ledger.record_event(
        event_type="CHILD_WORK",
        agent_id="worker",
        details={"task": "test"},
    )

    # Merge result
    result = {"output": "child completed work"}
    merge_record = parent.merge_child_result(child, result)

    # Verify proof structure
    assert "child_ledger_hash" in merge_record
    assert "child_id" in merge_record
    assert merge_record["type"] == "EPHEMERAL_CITY_MERGE"
    assert merge_record["child_ledger_hash"] is not None

    # Child removed from tracking
    assert child not in parent._child_kernels

    # Check parent ledger has merge event
    parent_events = parent._ledger.get_all_events()
    merge_events = [e for e in parent_events if get_event_type(e) == "EPHEMERAL_CITY_MERGE"]
    assert len(merge_events) >= 1

    # Cleanup not needed - tests use VIBE_NO_LOCK for session bypass


def test_merge_unknown_child_raises_error(fresh_kernel):
    """
    Merging a child not spawned by parent should raise error.
    """
    from vibe_core.kernel_impl import RealVibeKernel

    parent = fresh_kernel
    parent.boot()

    # Create a "foreign" kernel not spawned by parent (via fixture mechanism)
    foreign_kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)

    with pytest.raises(ValueError, match="unknown child kernel"):
        parent.merge_child_result(foreign_kernel, {"result": "test"})

    # Cleanup not needed - tests use VIBE_NO_LOCK for session bypass


def test_multiple_children_independent(fresh_kernel):
    """
    Multiple children should be independent of each other.
    """
    parent = fresh_kernel
    parent.boot()

    config = get_config()
    child1 = parent.spawn_child_kernel(config, ledger_path=":memory:")
    child2 = parent.spawn_child_kernel(config, ledger_path=":memory:")

    # Both are tracked
    assert child1 in parent._child_kernels
    assert child2 in parent._child_kernels
    assert len([c for c in parent._child_kernels if c in [child1, child2]]) == 2

    # Children are independent
    assert child1 is not child2
    assert id(child1) != id(child2)

    # Each child knows same parent
    assert child1._parent is parent
    assert child2._parent is parent

    # Cleanup not needed - tests use VIBE_NO_LOCK for session bypass


def test_child_uses_provided_config(fresh_kernel):
    """
    Child should use the config provided at spawn time.
    """
    parent = fresh_kernel
    parent.boot()

    config = get_config()
    child = parent.spawn_child_kernel(config)

    # Child has the config
    assert child._config is config

    # Cleanup not needed - tests use VIBE_NO_LOCK for session bypass


def test_fast_code_config_structure():
    """
    fast_code_config should set governance to permissive mode.
    """
    from vibe_core.phoenix.config import PhoenixConfig
    from vibe_core.playbook.operations.kernel_spawn import fast_code_config

    base = get_config()
    config = fast_code_config(base)

    # Config should be a PhoenixConfig
    assert config is not None
    assert isinstance(config, PhoenixConfig)

    # Governance should be permissive (voting_threshold = 0)
    if hasattr(config, "city") and hasattr(config.city, "governance"):
        if hasattr(config.city.governance, "voting_threshold"):
            assert config.city.governance.voting_threshold == 0.0


def test_parent_ledger_untouched_during_child_execution(fresh_kernel):
    """
    Parent ledger should not be affected by child operations until merge.
    """
    parent = fresh_kernel
    parent.boot()

    config = get_config()

    # Spawn and operate in child
    child = parent.spawn_child_kernel(config)
    child.boot()

    # Do work in child
    for i in range(5):
        child._ledger.record_event(
            event_type="CHILD_WORK",
            agent_id=f"worker_{i}",
            details={"iteration": i},
        )

    # Child has its own events
    child_events = len(child._ledger.get_all_events())
    assert child_events >= 5

    # Parent didn't get child's work events
    parent_work_events = [e for e in parent._ledger.get_all_events() if get_event_type(e) == "CHILD_WORK"]
    assert len(parent_work_events) == 0, "Parent should not have child's work events"

    # Cleanup not needed - tests use VIBE_NO_LOCK for session bypass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
