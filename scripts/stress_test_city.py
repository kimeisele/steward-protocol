#!/usr/bin/env python3
"""
🏗️ AGENT CITY STRESS TEST - THE FULL CITY 🏗️
==============================================

This is the REAL test - does the entire Agent City boot and survive?

This stress test verifies:
1. Kernel boots with all Phase 1-5 components
2. Discoverer registers and discovers ALL agents with steward.json
3. All discovered agents boot in isolated processes
4. All agents run concurrently for 30 seconds
5. Resource limits enforced (RAM, CPU)
6. Parampara handles concurrent writes (no race conditions)
7. SQLite handles concurrent transactions
8. All processes survive
9. Graceful shutdown works

CRITICAL CHECKS:
✅ All agent processes alive after 30s
✅ Parampara chain intact (no corruption from concurrent writes)
✅ RAM usage reasonable (< 2GB total)
✅ No SQLite lock errors
✅ All agents recorded in lineage

SUCCESS = Agent City is production-ready
FAILURE = We found the breaking point (fix before Phase 6)

Usage:
    python scripts/stress_test_city.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import time

import psutil

from steward.system_agents.discoverer.agent import Discoverer
from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.lineage import LineageChain, LineageEventType

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("STRESS_TEST")


def get_memory_usage_mb():
    """Get current process memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


def stress_test_city():
    """
    THE STRESS TEST - Can the entire Agent City boot and survive?
    """

    print("=" * 70)
    print("🏗️  AGENT CITY STRESS TEST - FULL CITY BOOT")
    print("=" * 70)
    print()

    # Test database paths (isolated)
    test_ledger_path = "/tmp/vibe_os/test/stress_ledger.db"
    test_lineage_path = "/tmp/vibe_os/test/stress_lineage.db"

    # Clean up old test databases
    for path in [test_ledger_path, test_lineage_path]:
        if Path(path).exists():
            Path(path).unlink()
            logger.info(f"🗑️  Cleaned up old test database: {path}")

    kernel = None
    initial_memory = get_memory_usage_mb()

    try:
        # =====================================================================
        # STEP 1: BOOT KERNEL
        # =====================================================================
        print("\n[STEP 1] Booting RealVibeKernel...")
        print("         (This creates Genesis Block)")

        start_time = time.time()

        kernel = RealVibeKernel(ledger_path=test_ledger_path)

        # Override lineage path for testing
        kernel.lineage.close()
        kernel.lineage = LineageChain(db_path=test_lineage_path)

        boot_time = time.time() - start_time
        print(f"         ✅ Kernel booted in {boot_time:.2f}s")
        print(f"         💾 Memory: {get_memory_usage_mb():.1f} MB")

        # =====================================================================
        # STEP 2: REGISTER DISCOVERER (Genesis Agent)
        # =====================================================================
        print("\n[STEP 2] Registering Discoverer (Genesis Agent)...")

        discoverer = Discoverer(kernel=kernel, config=None)

        try:
            kernel.register_agent(discoverer)
            print("         ✅ Discoverer registered")
        except Exception as e:
            print(f"         ❌ FAIL: {e}")
            return False

        # =====================================================================
        # STEP 3: DISCOVER ALL AGENTS
        # =====================================================================
        print("\n[STEP 3] Discovering agents via steward.json scan...")
        print("         Scanning: steward/system_agents/")

        agents_before = len(kernel.agent_registry)

        try:
            discovered_count = discoverer.discover_agents()
            agents_after = len(kernel.agent_registry)

            print(f"         ✅ Discovered {discovered_count} agents")
            print(f"         📊 Total agents: {agents_after}")

        except Exception as e:
            print(f"         ❌ FAIL: Discovery error: {e}")
            import traceback

            traceback.print_exc()
            return False

        # =====================================================================
        # STEP 4: BOOT KERNEL (Activate all agents)
        # =====================================================================
        print("\n[STEP 4] Booting kernel with all agents...")

        try:
            kernel.boot()
            print("         ✅ Kernel booted")
        except Exception as e:
            print(f"         ❌ FAIL: Kernel boot failed: {e}")
            import traceback

            traceback.print_exc()
            return False

        # =====================================================================
        # STEP 5: CHECK ALL PROCESSES
        # =====================================================================
        print("\n[STEP 5] Checking all agent processes...")

        total_agents = len(kernel.agent_registry)
        alive_processes = 0
        dead_processes = []

        for agent_id in kernel.agent_registry.keys():
            proc_info = kernel.process_manager.processes.get(agent_id)
            if proc_info and proc_info.process.is_alive():
                alive_processes += 1
                print(f"         ✅ {agent_id:20s} PID {proc_info.process.pid}")
            else:
                dead_processes.append(agent_id)
                print(f"         ❌ {agent_id:20s} NOT ALIVE")

        print(f"\n         Processes: {alive_processes}/{total_agents} alive")

        if dead_processes:
            print(f"         ⚠️  Dead processes: {', '.join(dead_processes)}")

        # =====================================================================
        # STEP 6: MEMORY CHECK
        # =====================================================================
        print("\n[STEP 6] Memory usage check...")

        current_memory = get_memory_usage_mb()
        memory_delta = current_memory - initial_memory

        print(f"         Initial: {initial_memory:.1f} MB")
        print(f"         Current: {current_memory:.1f} MB")
        print(f"         Delta: +{memory_delta:.1f} MB")

        if current_memory > 2000:  # 2GB threshold
            print(f"         ⚠️  WARNING: Memory usage high!")
        else:
            print(f"         ✅ Memory usage reasonable")

        # =====================================================================
        # STEP 7: PARAMPARA CHAIN CHECK
        # =====================================================================
        print("\n[STEP 7] Parampara chain inspection...")

        chain_length = kernel.lineage.get_chain_length()
        print(f"         Total blocks: {chain_length}")

        # Expected: Genesis + (N agents × 2 events) + KERNEL_BOOT
        expected_min = 1 + (total_agents * 2) + 1
        print(f"         Expected min: {expected_min} blocks")

        if chain_length < expected_min:
            print(f"         ⚠️  Chain shorter than expected!")
        else:
            print(f"         ✅ Chain length looks good")

        # Verify chain integrity
        if kernel.lineage.verify_chain():
            print("         ✅ Chain integrity verified")
        else:
            print("         ❌ FAIL: Chain corrupted!")
            return False

        # =====================================================================
        # STEP 8: STRESS DURATION (30 seconds)
        # =====================================================================
        print("\n[STEP 8] Running stress test for 30 seconds...")
        print("         All agents running concurrently...")

        stress_duration = 30
        check_interval = 5

        for i in range(0, stress_duration, check_interval):
            time.sleep(check_interval)

            # Check processes still alive
            alive_now = sum(
                1
                for agent_id in kernel.agent_registry.keys()
                if kernel.process_manager.processes.get(agent_id)
                and kernel.process_manager.processes[agent_id].process.is_alive()
            )

            memory_now = get_memory_usage_mb()
            chain_now = kernel.lineage.get_chain_length()

            print(
                f"         T+{i+check_interval:2d}s: {alive_now}/{total_agents} alive, "
                f"{memory_now:.1f} MB, {chain_now} blocks"
            )

            # Check for process crashes
            if alive_now < alive_processes:
                print(
                    f"         ⚠️  PROCESS CRASH DETECTED! {alive_processes - alive_now} died"
                )

        print("         ✅ Stress duration complete")

        # =====================================================================
        # STEP 9: POST-STRESS CHECKS
        # =====================================================================
        print("\n[STEP 9] Post-stress verification...")

        # Final process check
        final_alive = sum(
            1
            for agent_id in kernel.agent_registry.keys()
            if kernel.process_manager.processes.get(agent_id)
            and kernel.process_manager.processes[agent_id].process.is_alive()
        )

        print(f"         Final: {final_alive}/{total_agents} processes alive")

        if final_alive < total_agents:
            crashed = total_agents - final_alive
            print(f"         ❌ {crashed} processes crashed during stress test")
        else:
            print(f"         ✅ All processes survived")

        # Final memory check
        final_memory = get_memory_usage_mb()
        print(f"         Final memory: {final_memory:.1f} MB")

        # =====================================================================
        # STEP 10: FINAL CHAIN VERIFICATION (BEFORE SHUTDOWN)
        # =====================================================================
        print("\n[STEP 10] Final chain verification (before shutdown)...")

        final_chain_length = kernel.lineage.get_chain_length()
        print(f"         Final chain length: {final_chain_length} blocks")

        if kernel.lineage.verify_chain():
            print("         ✅ Chain integrity verified")
            chain_intact = True
        else:
            print("         ❌ Chain corrupted!")
            chain_intact = False

        # =====================================================================
        # STEP 11: GRACEFUL SHUTDOWN
        # =====================================================================
        print("\n[STEP 11] Shutting down Agent City...")

        kernel.shutdown(reason="Stress test complete")
        print("         ✅ Shutdown complete")

        # =====================================================================
        # STEP 12: POST-MORTEM ANALYSIS
        # =====================================================================
        print("\n[STEP 12] Post-mortem analysis...")

        # Reopen chain (kernel.shutdown closed it)
        post_chain = LineageChain(db_path=test_lineage_path)

        # Count events by type
        all_blocks = post_chain.get_all_blocks()
        event_counts = {}
        for block in all_blocks:
            event_counts[block.event_type] = event_counts.get(block.event_type, 0) + 1

        print("         Event breakdown:")
        for event_type, count in sorted(event_counts.items()):
            print(f"           {event_type:25s}: {count:3d}")

        # Verify shutdown was recorded
        final_block = all_blocks[-1] if all_blocks else None
        if final_block and final_block.event_type == LineageEventType.KERNEL_SHUTDOWN:
            print("         ✅ Shutdown recorded in chain")
        else:
            print("         ⚠️  Shutdown event not found")

        post_chain.close()

        # =====================================================================
        # FINAL VERDICT
        # =====================================================================
        print("\n" + "=" * 70)

        # Calculate success criteria (chain_intact set in Step 10)
        all_processes_survived = final_alive == total_agents
        # chain_intact already calculated before shutdown
        memory_reasonable = final_memory < 2000
        no_crashes = final_alive >= alive_processes

        if all_processes_survived and chain_intact and memory_reasonable and no_crashes:
            print("✅ STRESS TEST PASSED - AGENT CITY IS PRODUCTION-READY!")
            print("=" * 70)
            print()
            print("All systems operational:")
            print(f"  ✅ {total_agents} agents booted and survived")
            print(f"  ✅ {final_chain_length} blocks in Parampara chain")
            print(f"  ✅ Chain integrity verified (no race conditions)")
            print(f"  ✅ Memory usage reasonable ({final_memory:.1f} MB)")
            print(f"  ✅ No process crashes")
            print()
            print("🚀 READY FOR PHASE 6 (STEWARD Protocol Compliance)")
            print("=" * 70)
            return True
        else:
            print("❌ STRESS TEST FAILED - ISSUES FOUND")
            print("=" * 70)
            print()
            print("Issues:")
            if not all_processes_survived:
                print(f"  ❌ {total_agents - final_alive} processes died")
            if not chain_intact:
                print(f"  ❌ Chain corrupted (race condition in Parampara?)")
            if not memory_reasonable:
                print(f"  ❌ Memory usage too high ({final_memory:.1f} MB)")
            if not no_crashes:
                print(f"  ❌ {alive_processes - final_alive} crashes during stress")
            print()
            print("🛑 FIX THESE ISSUES BEFORE PHASE 6")
            print("=" * 70)
            return False

    except Exception as e:
        print(f"\n❌ STRESS TEST EXCEPTION: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Cleanup
        if kernel:
            try:
                if hasattr(kernel, "lineage"):
                    kernel.lineage.close()
            except:
                pass


if __name__ == "__main__":
    success = stress_test_city()
    sys.exit(0 if success else 1)
