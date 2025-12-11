"""
OPUS-022: Kernel Scaling Integration Tests

Tests for spawn_city playbook operation end-to-end.
Per conftest.py: Uses test_context fixture (NO direct kernel instantiation).
Per GAD-000: Tests use real kernel, no mocks.

Test Cases from OPUS-022 Section 3.2:
1. spawn_city async works via playbook system
2. spawn_city returns valid SpawnCityResult
3. Child kernel executes and merges result
"""

import pytest

from vibe_core.playbook.operations.kernel_spawn import SpawnCityResult, spawn_city

# ===========================================================================
# TEST: spawn_city playbook operation works end-to-end
# ===========================================================================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_spawn_city_returns_valid_result(test_context):
    """
    spawn_city() should return a valid SpawnCityResult.

    This tests the TRANSMISSION (integration layer):
    - Parent kernel exists
    - spawn_city creates child kernel
    - Child executes task
    - Result merges back with proof
    """
    with test_context as ctx:
        kernel = ctx.kernel
        kernel.boot()

        # Execute spawn_city with parent kernel
        result = await spawn_city(
            task="echo integration test",
            parent_kernel=kernel,
            timeout_seconds=30,
        )

        # Verify result structure
        assert result is not None
        assert isinstance(result, SpawnCityResult)
        assert result.child_id is not None
        assert result.proof is not None
        assert isinstance(result.proof, str)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_spawn_city_child_is_merged(test_context):
    """
    spawn_city() should merge child result back to parent.

    Verification:
    - Child kernel created
    - Child kernel no longer tracked after merge
    - Parent ledger has EPHEMERAL_CITY_MERGE event
    """
    with test_context as ctx:
        kernel = ctx.kernel
        kernel.boot()

        # Track initial child count
        initial_children = len(kernel._child_kernels)

        # Execute spawn_city
        result = await spawn_city(
            task="ephemeral task",
            parent_kernel=kernel,
            timeout_seconds=30,
        )

        # After spawn_city completes, child should be merged (removed)
        final_children = len(kernel._child_kernels)
        assert final_children == initial_children, "Child should be merged after spawn_city"

        # Check parent ledger has merge event
        def get_event_type(e):
            return e.get("event_type") if isinstance(e, dict) else getattr(e, "event_type", None)

        events = kernel._ledger.get_all_events()
        merge_events = [e for e in events if get_event_type(e) == "EPHEMERAL_CITY_MERGE"]
        assert len(merge_events) >= 1, "Parent ledger should have EPHEMERAL_CITY_MERGE event"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_spawn_city_with_config_overrides(test_context):
    """
    spawn_city() should apply config overrides to child.
    """
    with test_context as ctx:
        kernel = ctx.kernel
        kernel.boot()

        # Execute with config overrides
        result = await spawn_city(
            task="config test",
            parent_kernel=kernel,
            config_overrides={
                "city.governance.voting_threshold": 0.0,
            },
            timeout_seconds=30,
        )

        # Should succeed
        assert result is not None
        assert result.child_id is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_spawn_city_with_fast_code_config(test_context):
    """
    spawn_city() with fast_code_config should disable governance.
    """
    from vibe_core.playbook.operations.kernel_spawn import fast_code_config

    with test_context as ctx:
        kernel = ctx.kernel
        kernel.boot()

        # Execute with fast_code_config factory
        result = await spawn_city(
            task="fast code test",
            parent_kernel=kernel,
            config_factory=fast_code_config,
            timeout_seconds=30,
        )

        # Should succeed
        assert result is not None
        assert isinstance(result, SpawnCityResult)


@pytest.mark.integration
def test_spawn_city_sync_wrapper(test_context):
    """
    spawn_city_sync() should work from non-async code.
    """
    from vibe_core.playbook.operations.kernel_spawn import spawn_city_sync

    with test_context as ctx:
        kernel = ctx.kernel
        kernel.boot()

        # Execute sync version
        result = spawn_city_sync(
            task="sync test",
            parent_kernel=kernel,
            timeout_seconds=30,
        )

        # Should return result
        assert result is not None
        assert isinstance(result, SpawnCityResult)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
