#!/usr/bin/env python3
"""
🛸 LIVE FIRE EXERCISE: GAD-5500 Safe Evolution Loop
================================================================================
Tests the REAL VibeKernel with actual agent cartridges and playbook execution.

This is NOT a mock. This is the production code path.
"""

import asyncio
import logging
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("LIVE_FIRE_TEST")

# Add project root to Python path (discover dynamically)
import os

_script_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_script_dir))  # scripts/testing -> project root
sys.path.insert(0, _project_root)


async def run_live_fire():
    """Execute the live fire test with real kernel"""

    logger.info("=" * 80)
    logger.info("🛸 LIVE FIRE EXERCISE: GAD-5500 SAFE EVOLUTION LOOP")
    logger.info("=" * 80)

    # PHASE 1: BOOT KERNEL
    logger.info("\n[PHASE 1] BOOTING REAL VIBE KERNEL...")
    print("-" * 80)

    try:
        from vibe_core.cartridges.system.archivist.cartridge_main import ArchivistCartridge
        from vibe_core.cartridges.system.auditor.cartridge_main import AuditorCartridge
        from vibe_core.cartridges.system.engineer.cartridge_main import EngineerCartridge
        from vibe_core.kernel_impl import RealVibeKernel

        # Create kernel instance
        kernel = RealVibeKernel(ledger_path=":memory:")
        logger.info("✅ Kernel instance created")

        # Register agents (THE CRITICAL STEP)
        agents_to_register = [
            ("engineer", EngineerCartridge()),
            ("auditor", AuditorCartridge()),
            ("archivist", ArchivistCartridge()),
        ]

        logger.info("\n📝 Registering GAD-5500 agents...")
        for agent_id, agent_instance in agents_to_register:
            kernel.register_agent(agent_instance)
            logger.info(f"   ✅ {agent_id} registered")

        # Boot the kernel
        logger.info("\n⚙️  Booting kernel...")
        kernel.boot()
        logger.info("✅ KERNEL BOOTED")

        # Verify agents are loaded
        registry_keys = list(kernel.agent_registry.keys())
        logger.info(f"\n🤖 Loaded agents: {', '.join(registry_keys)}")

        required_agents = {"engineer", "auditor", "archivist"}
        actual_agents = set(registry_keys)

        if not required_agents.issubset(actual_agents):
            missing = required_agents - actual_agents
            logger.error(f"❌ CRITICAL: Missing agents: {missing}")
            logger.error("   The kernel will not be able to execute playbooks!")
            return False

        logger.info("✅ All required agents present in kernel registry")

    except Exception as e:
        logger.error(f"❌ KERNEL BOOT FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False

    # PHASE 2: PREPARE PLAYBOOK ENGINE
    logger.info("\n[PHASE 2] INITIALIZING PLAYBOOK ENGINE...")
    print("-" * 80)

    try:
        from envoy.deterministic_executor import DeterministicExecutor

        engine = DeterministicExecutor(knowledge_dir="knowledge")
        logger.info(f"✅ DeterministicExecutor initialized with {len(engine.playbooks)} playbooks")

        # Check for the GAD-5500 playbook
        if "FEATURE_IMPLEMENT_SAFE_V1" not in engine.playbooks:
            logger.error("❌ FEATURE_IMPLEMENT_SAFE_V1 playbook not found!")
            return False

        playbook = engine.playbooks["FEATURE_IMPLEMENT_SAFE_V1"]
        logger.info(f"✅ Playbook loaded: {playbook.name} ({len(playbook.phases)} phases)")

    except Exception as e:
        logger.error(f"❌ PLAYBOOK INIT FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False

    # PHASE 3: EXECUTE PLAYBOOK
    logger.info("\n[PHASE 3] EXECUTING PLAYBOOK...")
    print("-" * 80)

    try:
        # Create test context
        context = {
            "feature_name": "LiveFireTest",
            "feature_description": "A production test to verify the Safe Evolution Loop works end-to-end",
            "path": "src/live_test.py",
            "content": "def live_fire():\n    return 'System Functional!'\n",
        }

        logger.info("\n📋 Context:")
        logger.info(f"   Feature: {context['feature_name']}")
        logger.info(f"   Path: {context['path']}")

        # Create intent vector (simplified)
        from vibe_core.cartridges.system.envoy.provider_legacy.universal_provider import IntentType, IntentVector

        intent_vector = IntentVector(
            raw_input=context["feature_description"],
            intent_type=IntentType.CREATION,
            target_domain="engineering",
            confidence=0.95,
        )

        # Execute playbook
        logger.info("\n▶️  PLAYBOOK EXECUTION STARTING...")

        result = await engine.execute(
            playbook_id="FEATURE_IMPLEMENT_SAFE_V1",
            user_input=context["feature_description"],
            intent_vector=intent_vector,
            kernel=kernel,
            emit_event=None,  # Optional event emitter
        )

        logger.info("\n🏁 PLAYBOOK EXECUTION COMPLETE")
        logger.info(f"   Status: {result.get('status')}")
        logger.info(f"   Playbook: {result.get('playbook_name')}")

        if result.get("status") == "COMPLETED":
            logger.info("✅ PLAYBOOK COMPLETED SUCCESSFULLY")
            return True
        else:
            logger.error(f"❌ PLAYBOOK FAILED: {result}")
            return False

    except Exception as e:
        logger.error(f"❌ PLAYBOOK EXECUTION FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main entry point"""
    success = await run_live_fire()

    print("\n" + "=" * 80)
    if success:
        logger.info("🏆 LIVE FIRE EXERCISE: SUCCESS")
        logger.info("=" * 80)
        logger.info("\n✅ The Safe Evolution Loop (GAD-5500) is FULLY OPERATIONAL")
        logger.info("✅ Kernel boots and loads all agents correctly")
        logger.info("✅ Playbook engine executes with real kernel")
        logger.info("\n🚀 SYSTEM IS READY FOR PRODUCTION")
        return 0
    else:
        logger.error("❌ LIVE FIRE EXERCISE: FAILED")
        logger.error("=" * 80)
        logger.error("\n❌ System is NOT ready for production")
        logger.error("See error messages above for details")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
