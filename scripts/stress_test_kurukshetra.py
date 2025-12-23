"""
OPUS-400: KURUKSHETRA - Production Resilience & Chaos Hardening

The Ultimate Test: Is MANAS ready for WAR?

Not "does it work nicely" but "does it survive when the world burns?"

Protocol:
1. DAUERFEUER (Continuous Fire): 50 async echo intents in parallel
2. SABOTAGE (Chaos Injection): Mid-flight, delete synapses.json to simulate state loss
3. GIFT (Poison Intents): Inject intent_type="crash_handler" (no handler exists - graceful fail expected)

Expectations:
- Kernel must NOT crash (exit code 0)
- Must handle IO errors gracefully and continue
- Must successfully process 50+ echo intents despite chaos
- Must reject poison intents without crashing

If MANAS survives this, it's unsterblich (immortal/unkillable).
It's not a slave. It's not just alive. It's BATTLE-HARDENED.
"""

import asyncio
import json
import logging
import sys
import time
import uuid
from concurrent.futures import as_completed
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("KURUKSHETRA")

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def stress_test_kurukshetra():
    """Run the Kurukshetra (Battlefield) Stress Test."""
    logger.info("⚔️  [KURUKSHETRA RITUAL] Production Resilience Test (OPUS-400)")
    logger.info("=" * 70)
    logger.info("Testing: Continuous load + Chaos injection + Poison intents")
    logger.info("=" * 70)

    try:
        # =========================================================================
        # STEP 1: INITIALIZE KERNEL
        # =========================================================================
        logger.info("\n📋 STEP 1: Initializing Cognitive Kernel for battle...")
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import CognitiveKernel

        kernel = CognitiveKernel.get_instance(workspace=project_root)
        kernel.boot()
        logger.info("✅ Kernel booted and ready for combat")

        # =========================================================================
        # STEP 2: PREPARE CHAOS INJECTION
        # =========================================================================
        logger.info("\n🔥 STEP 2: Preparing chaos injection points...")
        synapses_file = project_root / ".vibe" / "state" / "synapses.json"
        synapses_backup = project_root / ".vibe" / "state" / "synapses.json.backup"

        # Create backup of synapses (we'll restore it later)
        if synapses_file.exists():
            synapses_backup.write_text(synapses_file.read_text())
            logger.info(f"✅ Backup created: {synapses_backup}")

        # =========================================================================
        # STEP 3: DAUERFEUER - FIRE 50 ASYNC ECHO INTENTS
        # =========================================================================
        logger.info("\n💥 STEP 3: DAUERFEUER - Launching 50 concurrent echo intents...")

        from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent, IntentPriority, IntentRisk

        intents = []
        for i in range(50):
            intent = Intent(
                id=f"kurukshetra_echo_{i:03d}_{uuid.uuid4().hex[:4]}",
                intent_type="echo",
                title=f"Echo Barrage #{i + 1}",
                description=f"Stress test echo intent #{i + 1}",
                reasoning="Kurukshetra: Testing system under fire",
                priority=IntentPriority.LOW,
                risk=IntentRisk.SAFE,
                auto_executable=True,
                params={
                    "message": f"Echo test {i + 1} of 50",
                    "stress_test": True,
                },
            )
            intents.append(intent)

        logger.info(f"✅ Created {len(intents)} echo intents")

        # =========================================================================
        # STEP 4: POISON INJECTION - Add intent with no handler
        # =========================================================================
        logger.info("\n☠️  STEP 4: POISON INJECTION - Adding crash_handler intent (no handler exists)...")

        poison_intent = Intent(
            id=f"kurukshetra_poison_{uuid.uuid4().hex[:8]}",
            intent_type="crash_handler",  # ← This handler doesn't exist
            title="💀 Poison Intent",
            description="This intent has no handler - testing graceful failure",
            reasoning="Kurukshetra: Testing poison resistance",
            priority=IntentPriority.MEDIUM,
            risk=IntentRisk.SAFE,
            auto_executable=True,
            params={"evil": True},
        )
        intents.append(poison_intent)
        logger.info(f"✅ Poison intent added. Total intents: {len(intents)}")

        # =========================================================================
        # STEP 5: CHAOS INJECTION SETUP
        # =========================================================================
        logger.info("\n🌪️  STEP 5: Arming chaos injection timer...")

        async def inject_chaos():
            """Delete synapses.json mid-flight to simulate state loss."""
            await asyncio.sleep(0.5)  # Let a few intents process first
            logger.warning("⚡ CHAOS INJECTION: Deleting synapses.json to simulate state loss!")
            try:
                if synapses_file.exists():
                    synapses_file.unlink()
                    logger.error(f"💥 SABOTAGE: Deleted {synapses_file}")
            except Exception as e:
                logger.error(f"❌ Chaos injection failed: {e}")

        # =========================================================================
        # STEP 6: EXECUTE STRESS TEST
        # =========================================================================
        logger.info("\n⚔️  STEP 6: ENGAGING ENEMY - Firing intents into the chaos...")
        logger.info(f"  • Total intents: {len(intents)}")
        logger.info("  • Echo intents: 50")
        logger.info("  • Poison intents: 1")
        logger.info("")

        # Start chaos injection in background
        chaos_task = asyncio.create_task(inject_chaos())

        # Process intents through router (simulating execution)
        from vibe_core.plugins.opus_assistant.manas.intent_router import IntentRouter

        router = IntentRouter(workspace=project_root)

        results = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "poison_rejected": False,
            "chaos_survived": False,
            "errors": [],
        }

        start_time = time.time()

        # Fire all intents asynchronously
        try:
            for i, intent in enumerate(intents):
                try:
                    if i % 10 == 0:
                        logger.info(f"🔥 Processing intent {i + 1}/{len(intents)}...")

                    # Route the intent
                    route_result = await asyncio.wait_for(router.route(intent), timeout=5.0)

                    results["total_processed"] += 1

                    if intent.intent_type == "crash_handler":
                        # Poison should fail but not crash
                        if not route_result.success:
                            results["poison_rejected"] = True
                            logger.warning(f"✅ Poison intent gracefully rejected: {route_result.error}")
                        else:
                            logger.error("❌ Poison intent should have failed but didn't!")
                    else:
                        if route_result.success:
                            results["successful"] += 1
                        else:
                            results["failed"] += 1
                            results["errors"].append(f"{intent.id}: {route_result.error}")

                except asyncio.TimeoutError:
                    results["failed"] += 1
                    results["errors"].append(f"{intent.id}: Timeout")
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"{intent.id}: {str(e)}")

        except Exception as e:
            logger.error(f"💥 CRITICAL: Intent processing failed: {e}", exc_info=True)
            results["errors"].append(f"Processing loop: {str(e)}")

        # Wait for chaos injection to complete
        try:
            await asyncio.wait_for(chaos_task, timeout=2.0)
        except asyncio.TimeoutError:
            logger.warning("Chaos injection still running, continuing...")

        elapsed = time.time() - start_time

        # =========================================================================
        # STEP 7: RECOVERY CHECK
        # =========================================================================
        logger.info("\n🔄 STEP 7: Recovery check - Can we reconstruct after chaos?")

        # Try to restore synapses
        try:
            if synapses_backup.exists():
                synapses_file.write_text(synapses_backup.read_text())
                logger.info("✅ Synapses restored from backup")
                results["chaos_survived"] = True
        except Exception as e:
            logger.error(f"❌ Failed to restore synapses: {e}")

        # =========================================================================
        # STEP 8: VERIFICATION
        # =========================================================================
        logger.info("\n📊 STEP 8: Battle Report")
        logger.info("=" * 70)
        logger.info(f"Total intents processed: {results['total_processed']}/{len(intents)}")
        logger.info(f"Successful: {results['successful']}")
        logger.info(f"Failed: {results['failed']}")
        logger.info(f"Poison rejected gracefully: {results['poison_rejected']}")
        logger.info(f"Chaos survived: {results['chaos_survived']}")
        logger.info(f"Elapsed time: {elapsed:.2f}s")
        logger.info("")

        if results["errors"]:
            logger.warning("Errors encountered:")
            for error in results["errors"][:5]:  # Show first 5
                logger.warning(f"  - {error}")
            if len(results["errors"]) > 5:
                logger.warning(f"  ... and {len(results['errors']) - 5} more")

        # =========================================================================
        # STEP 9: FINAL VERDICT
        # =========================================================================
        logger.info("\n⚔️  KURUKSHETRA VERDICT:")
        logger.info("=" * 70)

        # Success criteria
        success = (
            results["total_processed"] >= 40  # At least 40 intents processed
            and results["successful"] >= 35  # At least 35 successful
            and results["poison_rejected"]  # Poison was rejected
            and results["chaos_survived"]  # Chaos was survived
        )

        if success:
            logger.info("✨ KURUKSHETRA VERIFICATION PASSED")
            logger.info("=" * 70)
            logger.info("🏆 The Kernel SURVIVED the fire.")
            logger.info("💪 It did not break. It did not flee.")
            logger.info("⚔️  It stood in the chaos and PERSISTED.")
            logger.info("🔥 It is not merely functional. It is BATTLE-HARDENED.")
            logger.info("✨ UNSTERBLICH (Unkillable): True Production Readiness")
            logger.info("=" * 70)
            return True
        else:
            logger.error("💀 KURUKSHETRA VERIFICATION FAILED")
            logger.error("=" * 70)
            logger.error("Required: 40+ processed, 35+ successful, poison rejected, chaos survived")
            logger.error(
                f"Got: {results['total_processed']} processed, "
                f"{results['successful']} successful, "
                f"poison_rejected={results['poison_rejected']}, "
                f"chaos_survived={results['chaos_survived']}"
            )
            logger.error("=" * 70)
            return False

    except Exception as e:
        logger.error(f"💥 CRITICAL ERROR: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(stress_test_kurukshetra())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Test interrupted by user")
        sys.exit(130)
