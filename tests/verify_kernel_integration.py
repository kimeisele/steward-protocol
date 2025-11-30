#!/usr/bin/env python3
"""
⚠️ OPERATION: OPEN HEART ⚠️
============================

REAL KERNEL INTEGRATION TEST

This is NOT a mock. This script:
1. Imports the REAL VibeOS Kernel implementation
2. Loads the REAL Herald and Civic cartridges
3. Executes them in the kernel
4. Records everything in the REAL ledger

This proves that steward-protocol cartridges are native VibeOS citizens.

Prerequisites:
- All dependencies of Herald and Civic must be available
- LLM provider keys (if Herald runs content generation)
"""

import logging
import sys

# Setup logging to see everything
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("INTEGRATION_TEST")

# ============================================================================
# 1. IMPORT REAL KERNEL
# ============================================================================

try:
    from vibe_core.kernel_impl import RealVibeKernel

    logger.info("🔌 CONNECTED: Real VibeOS Kernel imported")
except ImportError as e:
    logger.error(f"❌ FATAL: Could not import real kernel: {e}")
    sys.exit(1)

# ============================================================================
# 2. IMPORT REAL CARTRIDGES
# ============================================================================

try:
    from herald.cartridge_main import HeraldCartridge

    logger.info("🔌 CONNECTED: Herald Cartridge imported")
except ImportError as e:
    logger.error(f"❌ FATAL: Could not import Herald: {e}")
    sys.exit(1)

try:
    from civic.cartridge_main import CivicCartridge

    logger.info("🔌 CONNECTED: Civic Cartridge imported")
except ImportError as e:
    logger.error(f"❌ FATAL: Could not import Civic: {e}")
    sys.exit(1)

# Import Task for task creation
try:
    from vibe_core import Task

    logger.info("🔌 CONNECTED: Task class imported")
except ImportError as e:
    logger.error(f"❌ FATAL: Could not import Task: {e}")
    sys.exit(1)


# ============================================================================
# 3. THE INTEGRATION TEST
# ============================================================================


def run_integration_test():
    """Execute the real integration test"""

    print("\n" + "=" * 70)
    print("🩸 OPERATION: OPEN HEART 🩸")
    print("=" * 70)

    # ========================================================================
    # PHASE 1: BOOT THE KERNEL
    # ========================================================================

    print("\n[PHASE 1] 🚀 BOOTING REAL VIBE KERNEL...")
    kernel = RealVibeKernel(ledger_path=":memory:")

    # ========================================================================
    # PHASE 2: LOAD CARTRIDGES
    # ========================================================================

    print("\n[PHASE 2] 📦 LOADING CARTRIDGES INTO KERNEL...")

    try:
        civic = CivicCartridge()
        kernel.register_agent(civic)
        logger.info(f"✅ CIVIC registered (agent_id: {civic.agent_id})")
    except Exception as e:
        logger.error(f"❌ CIVIC load failed: {e}")
        sys.exit(1)

    try:
        herald = HeraldCartridge()
        kernel.register_agent(herald)
        logger.info(f"✅ HERALD registered (agent_id: {herald.agent_id})")
    except Exception as e:
        logger.error(f"❌ HERALD load failed: {e}")
        sys.exit(1)

    # ========================================================================
    # PHASE 3: KERNEL BOOT (MANIFEST REGISTRATION)
    # ========================================================================

    print("\n[PHASE 3] ⚙️  KERNEL BOOT SEQUENCE...")
    kernel.boot()

    print("\n📊 KERNEL STATUS AFTER BOOT:")
    status = kernel.get_status()
    print(f"   - Kernel Status: {status['status']}")
    print(f"   - Agents Registered: {status['agents_registered']}")
    print(f"   - Manifests in Registry: {status['manifests']}")

    # ========================================================================
    # PHASE 4: VERIFY MANIFESTS (PROOF OF INTEGRATION)
    # ========================================================================

    print("\n[PHASE 4] 📜 VERIFYING MANIFESTS...")

    civic_manifest = kernel.get_agent_manifest("civic")
    if civic_manifest:
        print("   ✅ CIVIC Manifest Found:")
        print(f"      - Name: {civic_manifest.name}")
        print(f"      - Domain: {civic_manifest.domain}")
        print(f"      - Capabilities: {civic_manifest.capabilities}")
    else:
        logger.error("❌ CIVIC manifest not registered!")
        sys.exit(1)

    herald_manifest = kernel.get_agent_manifest("herald")
    if herald_manifest:
        print("   ✅ HERALD Manifest Found:")
        print(f"      - Name: {herald_manifest.name}")
        print(f"      - Domain: {herald_manifest.domain}")
        print(f"      - Capabilities: {herald_manifest.capabilities}")
    else:
        logger.error("❌ HERALD manifest not registered!")
        sys.exit(1)

    # ========================================================================
    # PHASE 5: SUBMIT REAL TASK TO CIVIC
    # ========================================================================

    print("\n[PHASE 5] ⚡ SUBMITTING TASK: CIVIC status report...")

    task_civic = Task(agent_id="civic", payload={"action": "report_status"})

    task_id_civic = kernel.submit_task(task_civic)
    print(f"   📨 Task submitted: {task_id_civic}")

    # ========================================================================
    # PHASE 6: TICK THE KERNEL (EXECUTE TASK)
    # ========================================================================

    print("\n[PHASE 6] ⏱️  TICKING KERNEL (ONE CYCLE)...")
    kernel.tick()

    # ========================================================================
    # PHASE 7: VERIFY LEDGER
    # ========================================================================

    print("\n[PHASE 7] 🔍 VERIFYING LEDGER...")

    result = kernel.get_task_result(task_id_civic)

    if result and result["status"] == "COMPLETED":
        print("   ✅ TASK COMPLETED in real kernel")
        print("   📄 Output:")
        output = result.get("output_result", {})
        if isinstance(output, dict):
            for key, value in output.items():
                print(f"      - {key}: {value}")
        else:
            print(f"      {output}")
    else:
        logger.error(f"❌ TASK FAILED or missing result: {result}")
        sys.exit(1)

    # ========================================================================
    # PHASE 8: SUBMIT TASK TO HERALD
    # ========================================================================

    print("\n[PHASE 8] ⚡ SUBMITTING TASK: HERALD status report...")

    task_herald = Task(agent_id="herald", payload={"action": "report_status"})

    task_id_herald = kernel.submit_task(task_herald)
    print(f"   📨 Task submitted: {task_id_herald}")

    # ========================================================================
    # PHASE 9: TICK THE KERNEL (EXECUTE HERALD TASK)
    # ========================================================================

    print("\n[PHASE 9] ⏱️  TICKING KERNEL (HERALD CYCLE)...")
    kernel.tick()

    # ========================================================================
    # PHASE 10: VERIFY HERALD TASK IN LEDGER
    # ========================================================================

    print("\n[PHASE 10] 🔍 VERIFYING HERALD TASK IN LEDGER...")

    result = kernel.get_task_result(task_id_herald)

    if result and result["status"] == "COMPLETED":
        print("   ✅ HERALD TASK COMPLETED in real kernel")
        print("   📄 Output:")
        output = result.get("output_result", {})
        if isinstance(output, dict):
            for key, value in output.items():
                print(f"      - {key}: {value}")
        else:
            print(f"      {output}")
    else:
        logger.error(f"❌ HERALD TASK FAILED: {result}")
        sys.exit(1)

    # ========================================================================
    # PHASE 11: DUMP LEDGER (PROOF)
    # ========================================================================

    print("\n[PHASE 11] 📊 FULL LEDGER DUMP...")
    ledger_events = kernel.dump_ledger()

    print(f"\n   Total events recorded: {len(ledger_events)}")
    for i, event in enumerate(ledger_events, 1):
        print(f"\n   Event {i}:")
        print(f"      Type: {event.get('event_type')}")
        print(f"      Task: {event.get('task_id')}")
        print(f"      Agent: {event.get('agent_id')}")
        print(f"      Timestamp: {event.get('timestamp')}")

    # ========================================================================
    # PHASE 12: FINAL VERDICT
    # ========================================================================

    print("\n" + "=" * 70)
    print("🎉 INTEGRATION TEST SUCCESSFUL 🎉")
    print("=" * 70)
    print("\n✅ PROOF OF INTEGRATION:")
    print("   1. Herald and Civic loaded as real VibeAgents")
    print("   2. Kernel registered both agents")
    print("   3. Manifests published to kernel registry")
    print("   4. Tasks submitted and executed")
    print("   5. Results recorded in immutable ledger")
    print("   6. Ledger verified for task completion")
    print("\n🩸 THIS IS REAL. THIS IS NOT A MOCK. 🩸")
    print("\n")


if __name__ == "__main__":
    try:
        run_integration_test()
    except Exception as e:
        logger.exception(f"❌ INTEGRATION TEST FAILED: {e}")
        sys.exit(1)
