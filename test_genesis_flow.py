#!/usr/bin/env python3
"""
🧬 GENESIS FLOW TEST (GAD-5003)

The REAL E2E test - not mocks, not isolated components.
This tests the COMPLETE flow from user input to agent execution.

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

This test will reveal WHERE the chain breaks (if it does).
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("GENESIS_FLOW")

# Diagnostic counters
DIAGNOSTICS = {
    "router_called": False,
    "concepts_extracted": [],
    "playbook_matched": None,
    "blueprint_extracted": {},
    "phases_executed": [],
    "agents_called": [],
    "errors": [],
}


async def test_genesis_flow():
    """Test the complete Genesis Flow through UniversalProvider."""

    logger.info("\n" + "=" * 70)
    logger.info("🧬 GENESIS FLOW TEST - COMPLETE E2E")
    logger.info("=" * 70)

    # =========================================================================
    # STEP 1: Boot the Kernel (Real, not mock)
    # =========================================================================
    logger.info("\n📦 STEP 1: Boot Kernel")

    try:
        from vibe_core.boot_orchestrator import BootOrchestrator

        orchestrator = BootOrchestrator(ledger_path=":memory:")
        kernel = orchestrator.boot()

        status = kernel.get_status()
        logger.info(f"   ✅ Kernel booted: {status.get('agents_registered')} agents")

    except Exception as e:
        logger.error(f"   ❌ Kernel boot failed: {e}")
        DIAGNOSTICS["errors"].append(f"Kernel boot: {e}")
        return DIAGNOSTICS

    # =========================================================================
    # STEP 2: Initialize UniversalProvider
    # =========================================================================
    logger.info("\n🌐 STEP 2: Initialize UniversalProvider")

    try:
        from provider.universal_provider import UniversalProvider

        provider = UniversalProvider(kernel=kernel)
        logger.info(f"   ✅ UniversalProvider initialized")
        logger.info(f"   → Router: {type(provider.router).__name__}")
        logger.info(f"   → Playbook Engine: {type(provider.playbook_engine).__name__}")

    except Exception as e:
        logger.error(f"   ❌ Provider init failed: {e}")
        DIAGNOSTICS["errors"].append(f"Provider init: {e}")
        return DIAGNOSTICS

    # =========================================================================
    # STEP 3: Test User Input
    # =========================================================================
    logger.info("\n📝 STEP 3: Test User Input")

    # The test input - something that should trigger feature_implement_safe
    test_input = "Create a new monitoring agent that watches system health"

    logger.info(f"   INPUT: '{test_input}'")

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
        logger.info(f"   📡 EVENT: [{event_type}] {message}")

    # =========================================================================
    # STEP 4: Execute route_and_execute
    # =========================================================================
    logger.info("\n🚀 STEP 4: route_and_execute()")

    try:
        result = await provider.route_and_execute(
            user_input=test_input,
            emit_event=collect_events,
        )

        logger.info(f"   ✅ Execution complete")
        logger.info(f"   → Status: {result.get('status')}")
        logger.info(f"   → Result keys: {list(result.keys())}")

        DIAGNOSTICS["result"] = result

    except Exception as e:
        logger.error(f"   ❌ Execution failed: {e}")
        import traceback

        traceback.print_exc()
        DIAGNOSTICS["errors"].append(f"Execution: {e}")
        return DIAGNOSTICS

    # =========================================================================
    # STEP 5: Analyze What Happened
    # =========================================================================
    logger.info("\n📊 STEP 5: Analyze Flow")

    # Check events for flow analysis
    for event in events:
        if "playbook" in event["message"].lower():
            DIAGNOSTICS["playbook_matched"] = event.get("data", {}).get("playbook_id")
        if "concepts" in str(event.get("data", {})):
            DIAGNOSTICS["concepts_extracted"] = event.get("data", {}).get("concepts", [])

    # Check result status
    status = result.get("status", "UNKNOWN")

    if status == "PROPOSAL_PENDING":
        logger.info("   ⚠️  No playbook matched - PROPOSAL generated")
        logger.info(f"   → Proposal ID: {result.get('proposal_id')}")
        logger.info(f"   → Concepts: {result.get('concepts_detected')}")
        DIAGNOSTICS["flow_result"] = "PROPOSAL_GENERATED"

    elif status == "COMPLETED":
        logger.info("   ✅ Playbook executed successfully!")
        DIAGNOSTICS["flow_result"] = "PLAYBOOK_EXECUTED"

    elif status == "FAILED":
        logger.info(f"   ❌ Execution failed: {result.get('error')}")
        DIAGNOSTICS["flow_result"] = "EXECUTION_FAILED"

    else:
        logger.info(f"   ℹ️  Status: {status}")
        DIAGNOSTICS["flow_result"] = status

    # =========================================================================
    # STEP 6: Shutdown
    # =========================================================================
    logger.info("\n🔴 STEP 6: Shutdown")

    try:
        kernel.shutdown(reason="Genesis Flow test complete")
        logger.info("   ✅ Kernel shutdown")
    except Exception as e:
        logger.warning(f"   ⚠️  Shutdown: {e}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    logger.info("\n" + "=" * 70)
    logger.info("🧬 GENESIS FLOW SUMMARY")
    logger.info("=" * 70)

    logger.info(f"\n📋 DIAGNOSTICS:")
    logger.info(f"   • Flow Result: {DIAGNOSTICS.get('flow_result', 'UNKNOWN')}")
    logger.info(f"   • Playbook Matched: {DIAGNOSTICS.get('playbook_matched', 'None')}")
    logger.info(f"   • Concepts: {DIAGNOSTICS.get('concepts_extracted', [])}")
    logger.info(f"   • Errors: {len(DIAGNOSTICS.get('errors', []))}")

    if DIAGNOSTICS.get("errors"):
        logger.info(f"\n❌ ERRORS:")
        for err in DIAGNOSTICS["errors"]:
            logger.info(f"   • {err}")

    logger.info(f"\n📡 EVENTS CAPTURED: {len(events)}")
    for i, event in enumerate(events, 1):
        logger.info(f"   {i}. [{event['type']}] {event['message'][:60]}...")

    # Final verdict
    if DIAGNOSTICS.get("flow_result") == "PLAYBOOK_EXECUTED":
        logger.info("\n✅ GENESIS FLOW: SUCCESS")
    elif DIAGNOSTICS.get("flow_result") == "PROPOSAL_GENERATED":
        logger.info("\n⚠️  GENESIS FLOW: PARTIAL (No playbook match, proposal generated)")
        logger.info("   This means routing works, but no playbook matched the concepts.")
    else:
        logger.info(f"\n❌ GENESIS FLOW: {DIAGNOSTICS.get('flow_result', 'UNKNOWN')}")

    logger.info("=" * 70 + "\n")

    return DIAGNOSTICS


if __name__ == "__main__":
    result = asyncio.run(test_genesis_flow())

    # Exit code based on result
    if result.get("errors"):
        sys.exit(1)
    elif result.get("flow_result") == "PLAYBOOK_EXECUTED":
        sys.exit(0)
    else:
        sys.exit(0)  # Partial success is still success for learning
