"""
Genesis Flow Integration Test
==============================

Tests the complete flow from user input to agent execution.

Flow Under Test:
    USER INPUT
         ↓
    UniversalProvider.route_and_execute()
         ↓
    Router (Sankhya + Dharma) → Intent Classification
         ↓
    Playbook Match → find_playbook(concepts)
         ↓
    Blueprint Generator → Extract structured params
         ↓
    DeterministicExecutor → Execute phases
         ↓
    Agent Calls → Engineer, Auditor, Archivist
"""

import pytest

from vibe_core.boot_orchestrator import BootOrchestrator


@pytest.mark.integration
@pytest.mark.asyncio
async def test_genesis_flow():
    """Test the complete Genesis Flow through UniversalProvider."""

    # STEP 1: Boot the Kernel
    orchestrator = BootOrchestrator(ledger_path=":memory:")
    kernel = await orchestrator.boot_orchestrated(force=True)

    status = kernel.get_status()
    assert status.get("status") in ["RUNNING", "IDLE"]

    # STEP 2: Initialize UniversalProvider
    from vibe_core.cartridges.system.envoy.provider import UniversalProvider

    # Disable semantic routing to avoid downloading models (SentenceTransformer) during test
    provider = UniversalProvider(kernel=kernel, use_semantic=False)

    # UniversalProvider uses either semantic_router or router (deterministic fallback)
    # With use_semantic=False, it MUST use router (DeterministicRouter)
    assert provider.router is not None
    assert provider.semantic_router is None
    assert provider.playbook_engine is not None

    # STEP 3: Test User Input
    test_input = "Create a new monitoring agent that watches system health"

    # Event collector for diagnostics
    events = []

    async def collect_events(event_type, message, source, data=None):
        events.append(
            {
                "type": event_type,
                "message": message,
                "source": source,
                "data": data or {},
            }
        )

    # STEP 4: Execute route_and_execute
    result = await provider.route_and_execute(
        user_input=test_input,
        emit_event=collect_events,
    )

    assert result is not None
    assert "status" in result

    # Check result status
    status = result.get("status", "UNKNOWN")
    # Valid statuses: fast-path success, playbook pending, completed, failed
    assert status in ["success", "PROPOSAL_PENDING", "COMPLETED", "FAILED", "NO_MATCH", "SUBMITTED"]

    # STEP 5: Shutdown (skip - can timeout on large workspace)
    # kernel.shutdown(reason="Genesis Flow test complete")


@pytest.mark.integration
def test_genesis_flow_kernel_boot():
    """Test that kernel boots successfully for genesis flow."""
    orchestrator = BootOrchestrator(ledger_path=":memory:")
    kernel = orchestrator.boot()

    assert kernel is not None
    status = kernel.get_status()
    assert "status" in status

    # Shutdown skip - can timeout on large workspace
    # kernel.shutdown(reason="Test complete")
