"""
Unit tests for UnifiedRouter (OPUS Phase 2).

Tests routing logic, circuit matching, and gate decisions.
"""

from vibe_core.runtime.unified_execution import ExecutionPath, MilkOceanGate, UnifiedRouter


def test_router_routes_fast_commands():
    """Router should route fast commands to correct circuit."""
    router = UnifiedRouter()

    request = router.route("status")

    assert request.execution_path == ExecutionPath.FAST_COMMAND
    assert request.target_id == "SYSTEM_STATUS_V2"
    assert request.confidence == 1.0


def test_router_routes_help_command():
    """Router should route help command."""
    router = UnifiedRouter()

    request = router.route("help")

    assert request.execution_path == ExecutionPath.FAST_COMMAND
    assert request.target_id == "HELP_COMMAND"
    assert request.confidence == 1.0


def test_router_fallback_on_unknown_intent():
    """Router should fallback on unknown intent."""
    router = UnifiedRouter()

    request = router.route("completely unknown request xyz")

    assert request.execution_path == ExecutionPath.FALLBACK
    assert request.target_id == "SIMPLE_QUERY"
    assert request.confidence == 0.3


def test_router_does_not_use_legacy_routers():
    """Router should not reference legacy routers."""
    router = UnifiedRouter()

    # Router should not have _playbook_router or _milk_ocean_router
    assert not hasattr(router, "_playbook_router")
    assert not hasattr(router, "_milk_ocean_router")


def test_router_gate_allows_by_default():
    """Router gate should allow requests by default."""
    router = UnifiedRouter()

    request = router.route("status")
    gate = router.check_gate(request)

    assert gate == MilkOceanGate.ALLOW
    assert request.gate_decision == MilkOceanGate.ALLOW


def test_router_creates_unique_request_ids():
    """Router should create unique request IDs."""
    router = UnifiedRouter()

    request1 = router.route("status")
    request2 = router.route("status")

    assert request1.request_id != request2.request_id


def test_router_marks_request_as_routed():
    """Router should mark request with routing metadata."""
    router = UnifiedRouter()

    request = router.route("status")

    assert request.routed_at is not None
    assert request.execution_path is not None
    assert request.target_id is not None


def test_router_normalizes_input():
    """Router should normalize user input (lowercase, strip)."""
    router = UnifiedRouter()

    request1 = router.route("  STATUS  ")
    request2 = router.route("status")

    # Both should route to same target
    assert request1.target_id == request2.target_id
    assert request1.execution_path == request2.execution_path
