import asyncio
import logging
import os
import resource
import sys
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict

# Setup basic logging
logging.basicConfig(level=logging.WARN, format="%(asctime)s [%(levelname)s] %(message)s")  # Reduced logging
logger = logging.getLogger("KALI_YUGA")
logger.setLevel(logging.INFO)

# Import Kernel types
# Adjust Python path if needed
sys.path.append(os.getcwd())

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.protocols import AgentManifest, VibeAgent


@dataclass
class EphemeralAgent(VibeAgent):
    """
    An ephemeral agent wrapper that exists only to create karma (load).
    """

    agent_id: str
    kernel: RealVibeKernel = None

    def get_manifest(self) -> AgentManifest:
        # BYPASS THE ILLUSION (MAYA)
        return AgentManifest(
            name=self.agent_id,
            version="0.0.1",
            author="KALI_YUGA",
            description="Ephemeral Agent",
            source="maya",
            domain="chaos",
        )

    def set_kernel(self, kernel: RealVibeKernel):
        self.kernel = kernel

    # Implement abstract method
    async def process(self, task: Any) -> Any:
        # We don't verify process logic here, just need to exist
        pass

    async def generate_karma(self):
        """Write to ledger to generate entropy."""
        if not self.kernel:
            return

        # Simulating a "Desire" (Write Operation)
        event = {
            "desire": "consume_resource",
            "entropy": str(uuid.uuid4()) * 50,  # Increased entropy to ensure memory pressure
            "timestamp": time.time(),
        }

        # Direct ledger write (bypassing normal safe channels to simulate raw chaos)
        try:
            self.kernel.record_verified_event(
                event_type="KALI_YUGA_DESIRE", agent_id=self.agent_id, details=event, caller_agent=self
            )
        except Exception as e:
            # Swallow errors to simulate "Ignorance" (Tamas)
            pass


def get_memory_usage_mb():
    """Get current RSS memory usage in MB."""
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return usage / 1024 / 1024  # macOS returns bytes
    else:
        return usage / 1024


async def run_kali_yuga():
    """
    THE KALI YUGA STRESS TEST

    Spawns 10,000 agents.
    Each writes to the ledger.
    We measure if the Kernel collapses or Memory explodes.
    """
    logger.info("🔱 INITIATING KALI YUGA STRESS TEST 🔱")
    logger.info(f"Initial Memory: {get_memory_usage_mb():.2f} MB")

    # 1. Boot Kernel (In-Memory for maximum speed/chaos)
    # We disable plugins to isolate kernel core memory leak
    kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)
    logger.info("Kernel Booted (Sato-Guna state).")

    # 2. The Maya (Illusion) of Scale
    # We will spawn 10,000 agents
    NUM_AGENTS = 10000
    batch_size = 1000
    agents = []

    start_time = time.time()

    logger.info(f"Spawning {NUM_AGENTS} distinct Jivas (Agents)...")

    try:
        for i in range(0, NUM_AGENTS, batch_size):
            batch_num = i // batch_size + 1
            if batch_num % 1 == 0:
                logger.info(f"Spawning Batch {batch_num}...")

            # Create batch
            current_batch = []
            for j in range(batch_size):
                agent_id = f"jiva_{i + j}"
                agent = EphemeralAgent(agent_id=agent_id)
                kernel.register_agent(agent, spawn_process=False)  # No processes, pure object overhead
                current_batch.append(agent)

            agents.extend(current_batch)

            # Execute Karma (Write to Ledger)
            # We assume the kernel is running in the same loop context for this test
            tasks = [agent.generate_karma() for agent in current_batch]
            await asyncio.gather(*tasks)

            mem = get_memory_usage_mb()
            if mem > 3000:  # 3GB Safety Limit
                logger.critical("🚨 SYSTEM COLLAPSE IMMINENT: MEMORY EXCEEDED 3GB")
                break

    except Exception as e:
        logger.error(f"💥 CHAOS ENSUED: {e}")
        import traceback

        traceback.print_exc()

    end_time = time.time()
    duration = end_time - start_time

    final_mem = get_memory_usage_mb()
    # Check registry size which should be huge
    # and ledger which should be huge

    # We access private members because "Manas sees all"
    ledger_events = kernel._ledger.get_all_events() if hasattr(kernel, "_ledger") else []
    registry_size = len(kernel._agent_registry)

    logger.info("=" * 50)
    logger.info("📊 RESULTS OF THE YUGA")
    logger.info("=" * 50)
    logger.info(f"Total Agents Spawned: {registry_size}")
    logger.info(f"Total Ledger Events:  {len(ledger_events)}")
    logger.info(f"Final Memory Usage:   {final_mem:.2f} MB")
    logger.info(f"Time Taken:           {duration:.2f} seconds")
    try:
        events_per_sec = len(ledger_events) / duration
    except ZeroDivisionError:
        events_per_sec = 0
    logger.info(f"Events per Second:    {events_per_sec:.2f}")

    # 3. VERDICT
    # Low threshold for detection
    if final_mem > 500:
        logger.warning(
            f"⚠️  KARMIC DEBT DETECTED: Memory usage high ({final_mem:.2f} MB). Entropy is not being released."
        )
    else:
        logger.info("✅ System held stable (Unlikely).")

    # 4. Clean shutdown attempt (Does it hang?)
    logger.info("Attempting Pralaya (Dissolution/Shutdown)...")
    # No explicit shutdown method in non-running kernel, but we check if refs persist
    kernel = None
    agents = None
    import gc

    gc.collect()
    post_gc_mem = get_memory_usage_mb()
    logger.info(f"Post-GC Memory: {post_gc_mem:.2f} MB")

    # Check if memory released
    # If > 100MB persists, it's a leak (base overhead is small around 60MB)
    if post_gc_mem > 120:
        logger.error("🛑 MEMORY LEAK CONFIRMED: Objects persisted after Pralaya.")
    else:
        logger.info("✨ Clean Dissolution.")


if __name__ == "__main__":
    asyncio.run(run_kali_yuga())
