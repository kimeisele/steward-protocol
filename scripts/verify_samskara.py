"""
OPUS-220: SAMSKARA VERIFICATION - Memory Implant Test

Proof that the Router consults learned experience before routing.

Protocol:
1. Inject artificial memory: "echo intent handled by shell_handler (weight=0.95)"
2. Fire echo intent through router
3. Verify log output contains: "🧠 SAMSKARA RECALL"
4. If yes: System has awakened to use memory. If no: System is amnesiac.
"""

import asyncio
import json
import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("VERIFY_SAMSKARA")

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def verify_samskara():
    """Run the Samskara Verification Ritual."""
    logger.info("🧠 [SAMSKARA RITUAL] Verifying Memory-Based Routing (OPUS-220)")

    # =========================================================================
    # STEP 1: MEMORY INJECTION - Plant a specific neuron in the brain
    # =========================================================================
    logger.info("\n📝 STEP 1: Injecting artificial memory into synapses.json...")

    from vibe_core.state.synapse_store import SynapseStore

    synapse_store = SynapseStore.get_instance(workspace=project_root)

    # Inject very specific memory:
    # "When we see intent_type='test_echo', the shell_handler should handle it"
    # Weight=0.95 ensures it passes the 0.70 confidence threshold
    trigger = "trigger:test_echo"
    action = "action:shell_handler"
    weight = 0.95

    logger.info(f"💉 Injecting: {trigger} → {action} (weight={weight})")
    synapse_store.set_weight(trigger, action, weight, defer_save=False)

    # Verify injection worked
    injected_weight = synapse_store.get_weight(trigger, action)
    logger.info(f"✅ Injection verified: {trigger} → {action} = {injected_weight}")

    if injected_weight != weight:
        logger.error(f"❌ INJECTION FAILED: Expected {weight}, got {injected_weight}")
        return False

    # =========================================================================
    # STEP 2: STIMULUS - Send intent that should trigger the memory
    # =========================================================================
    logger.info("\n🔥 STEP 2: Firing test_echo intent through the Router...")

    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent, IntentPriority, IntentRisk
    from vibe_core.plugins.opus_assistant.manas.intent_router import IntentRouter

    router = IntentRouter(workspace=project_root)

    # Create intent that matches our injected trigger
    test_intent = Intent(
        id=f"samskara_test_{uuid.uuid4().hex[:8]}",
        intent_type="test_echo",  # This will create trigger "trigger:test_echo"
        title="Samskara Memory Test Intent",
        description="Testing if router recalls learned patterns",
        reasoning="Verifying SAMSKARA RECALL mechanism",
        priority=IntentPriority.MEDIUM,
        risk=IntentRisk.SAFE,
        auto_executable=True,
        params={},
    )

    logger.info(f"📤 Intent created: {test_intent.id} (type={test_intent.intent_type})")

    # Route the intent
    logger.info("🔀 Routing intent through IntentRouter...")
    route_result = await router.route(test_intent)

    logger.info(f"📥 Route result: success={route_result.success}, error={route_result.error}")

    # =========================================================================
    # STEP 3: REVELATION - Check if SAMSKARA was consulted
    # =========================================================================
    logger.info("\n🔍 STEP 3: Analyzing whether Router consulted Samskara...")

    # The proof is in the log output:
    # We need to check if the intent.params contains samskara data
    if hasattr(test_intent, "params") and "samskara_recommended_handler" in test_intent.params:
        samskara_handler = test_intent.params.get("samskara_recommended_handler")
        samskara_confidence = test_intent.params.get("samskara_confidence", 0)

        logger.info(
            f"✨ SAMSKARA DETECTED: Router recalled memory!\n"
            f"   Recommended Handler: {samskara_handler}\n"
            f"   Confidence: {samskara_confidence:.2f}\n"
            f"   Status: {'PASS' if samskara_confidence > 0.70 else 'FAIL (low confidence)'}"
        )

        if samskara_handler and samskara_confidence > 0.70:
            logger.info("🎉 SUCCESS: SAMSKARA RECALL ACTIVATED - Router is wise!")
            return True
        else:
            logger.error("❌ FAILURE: Samskara data exists but confidence too low")
            return False
    else:
        logger.error("❌ FAILURE: Router did not consult Samskara (no memory params in intent)")
        logger.error(f"   Intent params: {test_intent.params if hasattr(test_intent, 'params') else 'N/A'}")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(verify_samskara())

        if success:
            logger.info("\n" + "=" * 70)
            logger.info("🏆 SAMSKARA VERIFICATION PASSED")
            logger.info("=" * 70)
            logger.info("✨ The Router has awakened to its own memory.")
            logger.info("✨ Manas (Mind) is now connected to Chitta (Memory).")
            logger.info("✨ The system is no longer amnesiac - it LEARNS and RECALLS.")
            logger.info("=" * 70)
            sys.exit(0)
        else:
            logger.error("\n" + "=" * 70)
            logger.error("💀 SAMSKARA VERIFICATION FAILED")
            logger.error("=" * 70)
            logger.error("The Router ignores memory. System is still Write-Only.")
            logger.error("=" * 70)
            sys.exit(1)

    except Exception as e:
        logger.error(f"💥 CRITICAL ERROR: {e}", exc_info=True)
        sys.exit(1)
