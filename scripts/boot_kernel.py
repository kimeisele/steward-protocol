#!/usr/bin/env python3
"""
🚀 REAL KERNEL BOOT 🚀
======================
Boots the VibeOS Kernel in persistent daemon mode.
"""
import sys
import time
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vibe_core.kernel_impl import RealVibeKernel
from steward.system_agents.discoverer.agent import Discoverer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("KERNEL_BOOT")


def boot_kernel():
    print("🚀 BOOTING VIBE KERNEL (DAEMON MODE)...")

    # Initialize Kernel
    # Use default paths: data/vibe_ledger.db and /tmp/vibe_os/kernel/lineage.db
    kernel = RealVibeKernel()

    # Register Discoverer (Genesis Agent)
    # Note: Config is optional for now, Discoverer handles it
    discoverer = Discoverer(kernel=kernel)
    kernel.register_agent(discoverer)

    # Discover Agents
    print("🔍 Discovering agents...")
    count = discoverer.discover_agents()
    print(f"✅ Discovered {count} agents")

    # Boot Kernel (Starts loops)
    # kernel.boot() # Hangs at _pulse()

    # Manual boot
    print("⚙️  Manually booting kernel...")
    from vibe_core.kernel import KernelStatus

    kernel._status = KernelStatus.RUNNING

    # Register manifests
    for agent_id, agent in kernel._agent_registry.items():
        manifest = agent.get_manifest()
        kernel._manifest_registry.register(manifest)
        print(f"   📜 {agent_id}: {manifest.description}")

    print("✅ Kernel booted (Manual). Press Ctrl+C to stop.")

    # Keep alive and watch for tasks
    print("👀 Watching /tmp/vibe_os/tasks/ for new tasks...")
    import glob
    import json
    from vibe_core.scheduling import Task

    try:
        while True:
            # Check for new tasks
            task_files = glob.glob("/tmp/vibe_os/tasks/*.json")
            if task_files:
                print(f"🔎 Glob found {len(task_files)} files: {task_files}")
            for task_file in task_files:
                try:
                    print(f"📄 Found task file: {task_file}")
                    with open(task_file, "r") as f:
                        data = json.load(f)

                    task_id = data.get("task_id")
                    agent_id = data.get("agent_id")
                    description = data.get("description")

                    # Construct Task for Envoy
                    # Envoy expects payload={"command": ...}
                    # We map description to command for now
                    task = Task(
                        agent_id=agent_id,
                        payload={"command": description, "args": {}},
                        task_id=task_id,
                    )

                    print(f"📨 Dispatching task {task_id} to {agent_id}: {description}")
                    kernel.process_manager.send_task(agent_id, task)

                    # Delete file
                    Path(task_file).unlink()
                    print(f"🗑️  Deleted task file: {task_file}")

                except Exception as e:
                    print(f"❌ Error processing task {task_file}: {e}")

            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        kernel.shutdown()


if __name__ == "__main__":
    try:
        boot_kernel()
    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"CRITICAL FAILURE: {e}")
