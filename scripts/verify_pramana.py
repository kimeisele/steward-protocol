import asyncio
import json
import logging
import subprocess
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("VERIFY_PRAMANA")

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from vibe_core.event_bus import EventBus
from vibe_core.plugins.opus_assistant.manas.action_manager import ActionManager
from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import CognitiveKernel
from vibe_core.plugins.opus_assistant.manas.intent_buffer import IntentBufferEntry
from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent, IntentPriority, IntentRisk
from vibe_core.runtime.unified_trace import UnifiedTrace


def kill_existing_kernels():
    """Kill any running kernel processes to free up resources/locks."""
    try:
        subprocess.run(["pkill", "-f", "boot_kernel"], check=False)
        subprocess.run(["rm", "-f", "boot.pid", ".vibe/state/pulse.json"], check=False)
    except Exception:
        pass


async def verify_loop():
    logger.info("🧪 [1/2] Verifying Feedback Loop (Karma -> Phala -> Samskara)")

    # 1. Setup Infrastructure
    trace = UnifiedTrace()
    event_bus = EventBus()

    # 2. Initialize Kernel
    manas = CognitiveKernel.get_instance(workspace=project_root)
    # Ensure event bus is wired for listener
    manas.setup(trace, event_bus, steward_context={})
    manas.boot()

    # 3. Create a UNIQUE Test Intent to avoid buffer collisions
    unique_id = f"pramana_fire_{uuid.uuid4().hex[:8]}"
    test_intent = Intent(
        id=unique_id,
        intent_type="echo",
        title=f"Pramana Live Fire {unique_id}",
        description="Testing the feedback loop with fresh ID",
        reasoning="Verifying that action execution results are correctly reported back to the kernel via EventBus.",
        params={"message": "Pramana Alive"},
        priority=IntentPriority.HIGH,
        risk=IntentRisk.SAFE,
        auto_executable=True,
    )

    # Clear any potential stale entry from buffer (belt and suspenders)
    if manas._buffer.find(unique_id):
        logger.warning(f"🧹 Clearing existing entry for {unique_id}")
        manas._buffer._intents = [i for i in manas._buffer._intents if i.intent.id != unique_id]

    # 4. Inject into Buffer
    entry = IntentBufferEntry(intent=test_intent)
    manas._buffer.add(entry)
    logger.info(f"📥 Fresh intent injected: {test_intent.id}")

    # 5. Execute Action
    action_manager = manas._action_manager
    logger.info("🎬 Executing Intent...")

    # Call execute asynchronously
    try:
        success = await action_manager.execute(entry, buffer=manas._buffer)
        logger.info(f"   Execution returned: {success}")
    except Exception as e:
        logger.error(f"   Execution failed with exception: {e}")
        import traceback

        traceback.print_exc()
        return False

    # 6. Verify Feedback Loop
    logger.info("⏳ Waiting for Event Bus feedback loop (3s)...")
    await asyncio.sleep(3)

    updated_entry = manas._buffer.find(test_intent.id)

    if updated_entry and updated_entry.status == "executed":
        logger.info("✅ SUCCESS: Intent marked 'executed' via Event Loop")
        if updated_entry.pramana:
            logger.info(f"   Pramana Proof found: {updated_entry.pramana.keys()}")
            # Verify basic proof structure
            if "executed_at" in updated_entry.pramana and "success" in updated_entry.pramana:
                logger.info("   Proof structure valid.")
            else:
                logger.warning(f"   Proof Incomplete: {updated_entry.pramana}")
    else:
        status = updated_entry.status if updated_entry else "MISSING"
        logger.error(f"❌ FAILURE: Intent status is '{status}' (Expected 'executed')")
        if updated_entry and updated_entry.execution_result:
            logger.error(f"   Result in Buffer: {updated_entry.execution_result}")
        return False

    return True


async def verify_zombies():
    logger.info("\n🧟 [2/2] Verifying Zombie Purge (Cleanup Stale)")

    manas = CognitiveKernel.get_instance()  # Already booted

    # 1. Create Stale Intent
    zombie_id = f"zombie_{uuid.uuid4().hex[:8]}"
    stale_intent = Intent(
        id=zombie_id,
        intent_type="sleep_forever",
        title="I am stale",
        description="A stale intent for testing cleanup",
        reasoning="Testing the zombie purge mechanism",
        priority=IntentPriority.LOW,
        risk=IntentRisk.SAFE,
        created_at=(datetime.utcnow() - timedelta(minutes=10)).isoformat(),
    )

    entry = IntentBufferEntry(intent=stale_intent)
    # Force stale state by manipulation
    entry.ttl_seconds = 1  # 1 second TTL
    entry.added_at = (datetime.utcnow() - timedelta(minutes=5)).isoformat()
    # Recalculate stale_at manually
    entry.stale_at = (datetime.utcnow() - timedelta(minutes=4)).isoformat()

    manas._buffer.add(entry)
    logger.info(f"📥 Zombie injected: {stale_intent.id}")

    # 2. Run Cleanup
    logger.info("🧹 Running cleanup_stale()...")
    count = manas._buffer.cleanup_stale()

    logger.info(f"   Cleaned up: {count}")

    # 3. Verify
    updated_entry = manas._buffer.find(stale_intent.id)
    if updated_entry and updated_entry.status == "stale":
        logger.info("✅ SUCCESS: Zombie marked 'stale'")
    else:
        status = updated_entry.status if updated_entry else "MISSING"
        logger.error(f"❌ FAILURE: Zombie status is '{status}' (Expected 'stale')")
        return False

    return True


if __name__ == "__main__":
    kill_existing_kernels()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        success_loop = loop.run_until_complete(verify_loop())
        success_zombie = loop.run_until_complete(verify_zombies())

        if success_loop and success_zombie:
            logger.info("\n🎉 ALL TESTS PASSED: Pramana is fully operational.")
            sys.exit(0)
        else:
            logger.error("\n💥 TESTS FAILED")
            sys.exit(1)
    except Exception as e:
        logger.error(f"💥 CRITICAL ERROR: {e}", exc_info=True)
        sys.exit(1)
