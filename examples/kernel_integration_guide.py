#!/usr/bin/env python3
"""
KERNEL INTEGRATION GUIDE - Connecting The Judge & Watchdog to VibeKernel

This guide shows how to integrate the semantic auditor into the main kernel loop.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger("KERNEL_INTEGRATION")


class KernelWithSemanticAuditor:
    """
    Example kernel implementation WITH semantic verification built-in.

    This shows the minimal changes needed to add semantic auditor to an
    existing VibeKernel implementation.
    """

    def __init__(self, root_path: Path = Path(".")):
        """
        Initialize kernel WITH semantic auditor.

        Args:
            root_path: Repository root
        """
        logger.info("🫀 Kernel: Initialization")

        # ... normal kernel init ...
        self.root_path = root_path
        self.task_queue = []
        self.task_count = 0
        self.running = False

        # ========== NEW: Load AUDITOR cartridge ==========
        logger.info("🔍 Loading AUDITOR cartridge")
        from steward.system_agents.auditor.cartridge_main import AuditorCartridge

        self.auditor = AuditorCartridge(root_path=root_path)

        # Start watchdog daemon
        logger.info("👁️  Starting Watchdog daemon")
        watchdog_result = self.auditor.start_watchdog()

        if watchdog_result["status"] == "started":
            logger.info("✅ Watchdog ready")
        else:
            logger.error("❌ Watchdog failed to start")
            raise RuntimeError("Watchdog initialization failed")

        logger.info("✅ Kernel ready with semantic verification")

    def add_task(self, task_id: str, task_name: str, payload: Dict[str, Any]):
        """Queue a task"""
        self.task_queue.append({"id": task_id, "name": task_name, "payload": payload})
        logger.info(f"📋 Task queued: {task_name}")

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task (simplified)"""
        logger.info(f"⚙️  Executing: {task['name']}")

        # Simulate work
        result = {
            "task_id": task["id"],
            "status": "completed",
            "result": f"Task {task['name']} completed",
        }

        return result

    def kernel_loop(self):
        """
        Main kernel loop WITH semantic verification
        """
        logger.info("🫀 Starting kernel loop")
        self.running = True

        try:
            while self.running and self.task_queue:
                # Pop next task
                task = self.task_queue.pop(0)

                # Execute task
                try:
                    result = self.execute_task(task)
                    self.task_count += 1

                    logger.info(f"✅ Task completed (#{self.task_count})")

                except Exception as e:
                    logger.error(f"❌ Task execution error: {e}")
                    self.task_count += 1

                # ========== NEW: Watchdog check every N tasks ==========
                # This is the integration point - very simple!
                if self.task_count % 10 == 0:
                    logger.info(f"👁️  [Tick {self.task_count}] Running Watchdog check...")

                    halt_result = self.auditor.watchdog_integration.kernel_tick(self.task_count)

                    if halt_result["should_halt"]:
                        logger.error("🚨 CRITICAL VIOLATION - HALTING KERNEL")
                        logger.error(f"   Reason: {halt_result['reason']}")
                        logger.error(f"   Details: {halt_result.get('check_result')}")

                        # Halt the kernel
                        self.halt_critical_violation(halt_result)
                        break
                    else:
                        logger.debug(f"👁️  Watchdog OK")

        finally:
            logger.info("🫀 Kernel loop ended")

    def halt_critical_violation(self, violation_result: Dict[str, Any]):
        """
        Handle critical violation detected by watchdog.

        This is called when a CRITICAL invariant violation is found.
        """
        self.running = False

        logger.error("=" * 70)
        logger.error("🚨 SYSTEM INTEGRITY VIOLATION")
        logger.error("=" * 70)

        check_result = violation_result.get("check_result", {})
        violations = check_result.get("violations", [])

        for v in violations:
            logger.error(f"   Violation: {v.get('violation_type')}")
            logger.error(f"   Severity: {v.get('severity')}")
            logger.error(f"   Message: {v.get('message')}")

        logger.error("=" * 70)
        logger.error("System halted. Manual intervention required.")
        logger.error("=" * 70)

    def run_pre_boot_verification(self):
        """
        Run semantic verification BEFORE kernel starts (optional but recommended).
        """
        logger.info("⚖️  Pre-boot semantic verification...")

        result = self.auditor.run_semantic_verification()

        if result["status"] == "error":
            logger.error(f"❌ Pre-boot verification failed: {result['error']}")
            raise RuntimeError("Pre-boot verification failed")

        if not result["passed"]:
            logger.error(f"❌ Semantic violations found: {result['violations']}")
            logger.error("   Fix violations before starting kernel")
            raise RuntimeError("Semantic verification failed")

        logger.info(f"✅ Pre-boot verification passed ({result['events_checked']} events)")

    def shutdown(self):
        """Graceful shutdown"""
        logger.info("🫀 Kernel: Shutting down")
        self.running = False
        logger.info("✅ Kernel shutdown complete")


def example_usage():
    """Example of how to use the kernel with semantic auditor"""

    print("\n" + "=" * 70)
    print("KERNEL INTEGRATION EXAMPLE")
    print("=" * 70 + "\n")

    # Create kernel
    kernel = KernelWithSemanticAuditor(Path("."))

    # Queue some tasks
    print("📋 Queuing tasks...")
    kernel.add_task("task_1", "Initialize System", {})
    kernel.add_task("task_2", "Civic License Check", {"agent": "herald"})
    kernel.add_task("task_3", "Herald Broadcast", {"message": "System online"})
    kernel.add_task("task_4", "Process Proposal", {"proposal_id": "p1"})
    kernel.add_task("task_5", "Vote on Proposal", {"proposal_id": "p1", "vote": "yes"})

    # Run pre-boot verification (optional)
    print("\n🔍 Running pre-boot verification...")
    try:
        kernel.run_pre_boot_verification()
    except RuntimeError as e:
        print(f"⚠️  Pre-boot check: {e}")
        # Could recover here if needed

    # Run kernel
    print("\n🫀 Starting kernel loop...")
    kernel.kernel_loop()

    # Shutdown
    kernel.shutdown()

    print("\n✅ Example completed\n")


def minimal_integration_example():
    """
    MINIMAL integration example - just the core changes.

    This shows the absolute minimum you need to add to an existing kernel.
    """

    code_snippet = """
    # In your existing VibeKernel class:
    
    def __init__(self):
        # ... existing kernel init ...
        
        # ADD THESE THREE LINES:
        from steward.system_agents.auditor.cartridge_main import AuditorCartridge
        self.auditor = AuditorCartridge()
        self.auditor.start_watchdog()
    
    def kernel_loop(self):
        while self.running:
            task = self.scheduler.next_task()
            
            if task:
                self.execute_task(task)
                self.task_count += 1
                
                # ADD THIS BLOCK:
                if self.task_count % 10 == 0:  # Check every 10 tasks
                    halt_result = self.auditor.watchdog_integration.kernel_tick(
                        self.task_count
                    )
                    if halt_result["should_halt"]:
                        logger.error("CRITICAL VIOLATION - HALTING")
                        self.running = False
                        break
    """

    print(code_snippet)


if __name__ == "__main__":
    # Show minimal integration
    print("\n📖 MINIMAL INTEGRATION (just copy-paste these changes):\n")
    minimal_integration_example()

    # Run full example
    print("\n📖 FULL EXAMPLE WITH OUTPUT:\n")
    try:
        example_usage()
    except Exception as e:
        print(f"Example error (expected in demo): {e}")
