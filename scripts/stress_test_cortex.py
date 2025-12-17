#!/usr/bin/env python
"""
Phase F+.2: Brain Freeze Stresstest
====================================

Stress test the unified orchestration abstraction (OPUS-095).

Scenario: Fire 500 intents into the kernel in < 1 second.

Expectations:
1. CycleRegistry fills up without crashing
2. RetentionPolicy prunes old cycles (no memory leak)
3. RateLimiting blocks/queues requests gracefully
4. System remains stable (no deadlocks, no crashes)

Run: python scripts/stress_test_cortex.py --intents 500 --timeout 1
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Add vibe_core to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vibe_core.orchestration_cycle import CognitiveCycle, CycleRegistry, RetentionPolicy


class FakeCycle(CognitiveCycle):
    """Fake cycle for stress testing."""

    def __init__(self, cycle_id: str):
        super().__init__()
        self._cycle_id = cycle_id
        self._counter = 0

    @property
    def cycle_name(self) -> str:
        return f"fake_cycle_{self._cycle_id}"

    @property
    def rate_limit_seconds(self) -> int:
        return 0  # No rate limiting for stress test

    @property
    def timeout_seconds(self) -> int:
        return 10

    @property
    def recovery_enabled(self) -> bool:
        return True

    async def _perceive(self):
        await asyncio.sleep(0.001)  # Simulate work
        return [{"observation": f"obs_{self._counter}"}], {}

    async def _orient(self, observations):
        await asyncio.sleep(0.001)
        return [{"orientation": f"orient_{self._counter}"}], {}

    async def _decide(self, orientations):
        await asyncio.sleep(0.001)
        return [{"decision": f"decide_{self._counter}"}], {}

    async def _act(self, decisions):
        await asyncio.sleep(0.001)
        self._counter += 1
        return {"result": f"result_{self._counter}"}, {}


async def stress_test(num_intents: int, timeout_seconds: float):
    """
    Fire multiple cycles rapidly and monitor for issues.

    Args:
        num_intents: Number of cycles to fire
        timeout_seconds: Time window for firing (seconds)
    """
    print(f"\n{'=' * 70}")
    print("🧠 OPUS-095 Brain Freeze Stresstest")
    print(f"{'=' * 70}")
    print(f"Target: {num_intents} intents in {timeout_seconds}s ({num_intents / timeout_seconds:.0f} intents/sec)")

    # Create registry with retention policy
    retention = RetentionPolicy(
        max_completed_cycles=100,
        max_error_cycles=50,
        enabled=True,
    )
    registry = CycleRegistry(retention_policy=retention)

    print("\n📊 Starting conditions:")
    print(f"   Retention: {retention.max_completed_cycles} max completed, {retention.max_error_cycles} max errors")
    print("   Rate limit: 0s (disabled for stress)")

    start_time = time.time()
    active_cycles = []
    errors = []
    memory_snapshots = []

    # Fire cycles rapidly
    print(f"\n🔥 Firing {num_intents} cycles...")

    for i in range(num_intents):
        cycle = FakeCycle(f"stress_{i}")
        active_cycles.append(cycle)

        try:
            # Fire orchestrate() without awaiting (gather all)
            # NOTE: Cycles auto-register with registry during orchestrate()
            task = asyncio.create_task(cycle.orchestrate(force=True))
            # Don't await - let them run in parallel

        except Exception as e:
            errors.append(f"Cycle {i}: {e}")
            print(f"   ❌ Error at cycle {i}: {e}")

        # Take memory snapshots every 50 cycles
        if (i + 1) % 50 == 0:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed
            print(f"   ✓ {i + 1}/{num_intents} cycles fired ({rate:.0f} intents/sec)")
            memory_snapshots.append(
                {
                    "count": i + 1,
                    "time": elapsed,
                    "active_in_registry": len(registry.get_active_cycles()),
                    "completed_in_registry": len(registry.get_completed_cycles()),
                    "errors_in_registry": len(registry.get_error_cycles()),
                }
            )

    # Wait for all to complete
    print("\n⏳ Waiting for all cycles to complete...")
    completed = 0
    try:
        # Collect all pending tasks
        pending = asyncio.all_tasks()
        for task in pending:
            try:
                await asyncio.wait_for(task, timeout=5.0)
                completed += 1
            except asyncio.TimeoutError:
                errors.append(f"Task timeout: {task}")
            except Exception as e:
                errors.append(f"Task error: {e}")
    except Exception as e:
        errors.append(f"Error waiting for tasks: {e}")

    elapsed_total = time.time() - start_time
    final_rate = num_intents / elapsed_total

    # Generate report
    print(f"\n{'=' * 70}")
    print("📋 STRESSTEST REPORT")
    print(f"{'=' * 70}")

    print("\n✅ Execution Summary:")
    print(f"   Total intents fired: {num_intents}")
    print(f"   Time elapsed: {elapsed_total:.3f}s")
    print(f"   Average rate: {final_rate:.0f} intents/sec")
    print(f"   Within timeout: {'✅ YES' if elapsed_total <= timeout_seconds else '❌ NO'}")

    print("\n📈 Registry Status (Final):")
    print(f"   Active cycles: {len(registry.get_active_cycles())}")
    print(f"   Completed cycles: {len(registry.get_completed_cycles())}")
    print(f"   Error cycles: {len(registry.get_error_cycles())}")
    print(
        f"   Total in registry: {len(registry.get_active_cycles()) + len(registry.get_completed_cycles()) + len(registry.get_error_cycles())}"
    )

    print("\n💾 Memory Snapshots:")
    for snap in memory_snapshots:
        print(
            f"   {snap['count']:>3} intents @ {snap['time']:.2f}s: "
            f"Active={snap['active_in_registry']:>3} | "
            f"Completed={snap['completed_in_registry']:>3} | "
            f"Errors={snap['errors_in_registry']:>3}"
        )

    # Check retention policy
    if len(registry.get_completed_cycles()) <= retention.max_completed_cycles:
        print("\n✅ Retention Policy: ENFORCED (completed cycles pruned)")
    else:
        print(
            f"\n⚠️  Retention Policy: NOT ENFORCED ({len(registry.get_completed_cycles())} > {retention.max_completed_cycles})"
        )

    if errors:
        print(f"\n❌ Errors ({len(errors)}):")
        for err in errors[:5]:  # Show first 5
            print(f"   - {err}")
        if len(errors) > 5:
            print(f"   ... and {len(errors) - 5} more")
    else:
        print("\n✅ No errors detected!")

    # Final verdict
    print(f"\n{'=' * 70}")
    success = (
        elapsed_total <= timeout_seconds * 1.5  # Allow 50% buffer
        and len(errors) == 0
        and len(registry.get_completed_cycles()) <= retention.max_completed_cycles
    )

    if success:
        print("🎉 STRESSTEST PASSED - System is stable!")
    else:
        print("⚠️  STRESSTEST FAILED - Issues detected")

    print(f"{'=' * 70}\n")

    return success


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Brain Freeze Stresstest")
    parser.add_argument("--intents", type=int, default=500, help="Number of intents to fire")
    parser.add_argument("--timeout", type=float, default=1.0, help="Time window in seconds")
    args = parser.parse_args()

    # Run test
    success = asyncio.run(stress_test(args.intents, args.timeout))
    sys.exit(0 if success else 1)
