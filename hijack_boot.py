import asyncio
import json
import logging
import sys
from pathlib import Path

# Add project root to path to allow imports
PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from vibe_core.boot_orchestrator import BootOrchestrator
from vibe_core.config import load_config
from vibe_core.scheduling.task import Task

# Basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s", datefmt="%H:%M:%S")


def get_kernel():
    """
    Hijacks the boot process to get a direct handle to the kernel.
    """
    print("🚀 Hijacking boot sequence...")
    config = load_config("config/matrix.yaml")
    orchestrator = BootOrchestrator(config=config, project_root=PROJECT_ROOT)
    kernel = orchestrator.boot()
    print("✅ Kernel booted successfully.")
    return kernel


async def main():
    kernel = get_kernel()

    print(f"Registered agents: {list(kernel.agent_registry.keys())}")

    status = kernel.get_status()
    print("\n--- KERNEL STATUS ---")
    print(json.dumps(status, indent=2))
    print("---------------------\n")

    print("Hijack successful. The 'kernel' object is now available.")
    print("Instructing the 'engineer' agent to manifest the restaurant app...")

    # Create a task for the engineer agent
    engineer_task = Task(
        agent_id="engineer",
        payload={
            "action": "manifest_reality",
            "feature_spec": "A restaurant ordering system",
            "path": "src/restaurant_app.py",
            "use_brain": False,
            "content": "print('Hello from the restaurant app!')",
        },
        priority=1,
    )

    # Submit the task to the kernel
    task_id = kernel.submit_task(engineer_task)
    print(f"Submitted task {task_id} to kernel for agent 'engineer'.")

    # Manually tick the kernel to process the task
    print("Ticking kernel to process task...")
    kernel.tick()
    print("Kernel ticked.")

    # Check the status of the task
    # In a real scenario, this would be asynchronous. We are simulating a wait.
    await asyncio.sleep(5)  # Give the agent time to work

    task_result = kernel.get_task_result(task_id)

    print("\n--- TASK RESULT ---")
    # Convert Path object to string for printing, if it exists
    if task_result and "path" in task_result and isinstance(task_result["path"], Path):
        task_result["path"] = str(task_result["path"])
    print(json.dumps(task_result, indent=2))
    print("-------------------\n")

    # Verify the file content
    if task_result and task_result.get("status") == "manifested":
        file_path = task_result.get("path")
        if file_path and Path(file_path).exists():
            print(f"--- CONTENT of {file_path} ---")
            print(Path(file_path).read_text())
            print("---------------------------------\n")
        else:
            print(f"--- File not found at {file_path} ---")

    print("Engineer has completed its task. Check the output files for the results.")


if __name__ == "__main__":
    asyncio.run(main())  # Run the async main function
