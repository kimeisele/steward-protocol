"""
JANAKA SERVICE - Duty & Execution
=================================

Implements JanakaProtocol (Execution).
Wraps InMemoryScheduler and UnifiedExecutor.

"Janaka acts without attachment. The work is the offering."
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x8f947260"  # GenesisByte: parampara % 37 == 0

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, Any

from vibe_core.protocols.mahajanas.janaka import (
    ExecutionResult,
    ExecutionState,
    JanakaProtocol,
    TaskPriority,
    TaskValue,
)
from vibe_core.protocols.mahajanas.router import Mahajana
from vibe_core.scheduling.in_memory import InMemoryScheduler
from vibe_core.scheduling.task import Task as SchedulerTask
from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol, TattvaDict

logger = logging.getLogger("JANAKA_SERVICE")


class JanakaService(JanakaProtocol, PanchaTattvaProtocol):
    """
    JanakaService - The Executor.
    Manages task scheduling and execution.
    Wraps InMemoryScheduler.
    """

    @property
    def __tattva__(self) -> TattvaDict:
        """The 5-fold Truth of Janaka Service."""
        return {
            "chaitanya": "Execution & Scheduling Service",
            "nityananda": "InMemoryScheduler Implementation",
            "advaita": "Task Lifecycle & Orchestration Logic",
            "gadadhara": "Command Execution Flow",
            "srivasa": "Sovereign Task Governance",
        }

    def __init__(self):
        self._scheduler = InMemoryScheduler()
        self._is_paused = False
        self._karma_accumulated = 0.0

    @property
    def owner(self) -> Mahajana:
        return Mahajana.JANAKA  # Position 10

    # =========================================================================
    # JanakaProtocol Implementation
    # =========================================================================

    def submit(
        self,
        name: str,
        task_input: TaskValue,
        priority: TaskPriority = TaskPriority.NORMAL,
        sovereign_id: str = "",
    ) -> str:
        """Submit a task for execution."""
        prio_map = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.NORMAL: 2,
            TaskPriority.LOW: 3,
            TaskPriority.BACKGROUND: 3,
        }
        int_priority = prio_map.get(priority, 2)

        task = SchedulerTask(
            task_id=f"task_{int(datetime.now().timestamp() * 1000)}",
            agent_id=sovereign_id or "system",
            payload={"input": str(task_input), "name": name},
            priority=int_priority,
        )

        task_id = self._scheduler.submit_task(task)
        logger.info(f"👑 JANAKA: Accepted task {name} ({task_id})")
        return task_id

    def execute(self, task_id: str) -> ExecutionResult:
        """Execute a task immediately (simulated picking from queue)."""
        task = self._scheduler.next_task()
        if not task:
            return {
                "success": False,
                "task_id": task_id,
                "output_type": "None",
                "output_repr": "No tasks pending",
                "execution_time_ms": 0,
                "error_message": "Queue empty",
            }

        start = datetime.now()
        # Execution logic would go here
        end = datetime.now()
        duration = int((end - start).total_seconds() * 1000)

        logger.info(f"👑 JANAKA: Executed task {task.task_id}")

        return {
            "success": True,
            "task_id": task.task_id,
            "output_type": "str",
            "output_repr": "Executed",
            "execution_time_ms": duration,
            "error_message": "",
        }

    def cancel(self, task_id: str) -> bool:
        return False

    def get_task(self, task_id: str) -> Optional[object]:
        return None

    def get_result(self, task_id: str) -> Optional[ExecutionResult]:
        if task_id in self._scheduler.completed:
            return {
                "success": True,
                "task_id": task_id,
                "output_type": "unknown",
                "output_repr": "completed",
                "execution_time_ms": 0,
                "error_message": "",
            }
        return None

    def is_busy(self) -> bool:
        return self._scheduler.executing is not None

    def pause(self) -> bool:
        self._is_paused = True
        return True

    def resume(self) -> bool:
        self._is_paused = False
        return True

    def get_karma(self) -> float:
        return self._karma_accumulated

    def release_karma(self) -> float:
        released = self._karma_accumulated
        self._karma_accumulated = 0.0
        return released

    def get_state(self) -> ExecutionState:
        status = self._scheduler.get_queue_status()
        return {
            "pending_tasks": [],
            "running_tasks": [],
            "completed_count": status.get("completed", 0),
            "failed_count": 0,
            "total_karma": self._karma_accumulated,
            "is_busy": self.is_busy(),
            "health": "healthy",
        }

    # =========================================================================
    # Kernel Orchestration (Delegated from RealVibeKernel)
    # =========================================================================

    def get_reactor(self, kernel: object) -> Optional[object]:
        """Get or initialize the Quantum Reactor. Delegated from Kernel."""
        current_reactor = getattr(kernel, "_reactor", None)
        if current_reactor is None:
            try:
                from vibe_core.reactor import QuantumReactor

                current_reactor = QuantumReactor(initial_inertia=0.5)
                logger.info("☢️ JANAKA: QuantumReactor loaded as execution primitive")
                setattr(kernel, "_reactor", current_reactor)
            except ImportError:
                pass
        return current_reactor

    def get_akasha_hash(self, kernel: object) -> str:
        """Get current akasha hash. Delegated from Kernel."""
        reactor = self.get_reactor(kernel)
        if reactor is not None:
            return str(getattr(reactor, "_chain_hash", lambda: "")())
        return str(getattr(kernel, "_akasha_field", ""))

    def compute_capability_resonance(self, kernel: object, agent_id: str, capability: str) -> float:
        """Compute resonance for capability check. Delegated from Kernel."""
        reactor = self.get_reactor(kernel)
        if reactor is None:
            checker = getattr(kernel, "_check_agent_capability", lambda a, c: False)
            return 1.0 if checker(agent_id, capability) else 0.0

        try:
            from vibe_core.reactor import encode

            akasha = self.get_akasha_hash(kernel)
            agent_tensor = encode(f"agent:{agent_id}", akasha)
            cap_tensor = encode(f"capability:{capability}", akasha)
            field = reactor.resonate(agent_tensor, cap_tensor)  # type: ignore
            return float(min(1.0, field.total_energy))
        except Exception:
            return 0.0

    async def pulse_orchestration(self, kernel: object, plugins: List[object]) -> Dict[str, object]:
        """💓 THE ASYNC PULSE ORCHESTRATION. Delegated from Kernel."""
        # This matches the call in kernel_impl.py
        return {"status": "pulsed", "timestamp": datetime.now().isoformat()}

    async def tick_orchestration(self, kernel: object) -> None:
        """💓 THE ASYNC TICK ORCHESTRATION. Delegated from Kernel."""
        status = getattr(kernel, "_status", "STOPPED")
        if str(status) != "RUNNING":
            return

        plugins = getattr(kernel, "_plugins", [])
        for plugin in plugins:
            if hasattr(plugin, "on_tick_pre"):
                plugin.on_tick_pre(kernel)

        task = self._scheduler.next_task()
        if task:
            logger.info(f"👑 JANAKA: Executing {task.task_id}")
            # Task execution logic would go here

        for plugin in plugins:
            if hasattr(plugin, "on_tick_post"):
                plugin.on_tick_post(kernel)

    def submit_task(self, kernel: object, task: Any) -> str:
        """Submit a task. Delegated from Kernel."""
        plugins = getattr(kernel, "_plugins", [])
        for plugin in plugins:
            if hasattr(plugin, "on_task_submit"):
                plugin.on_task_submit(kernel, task)
        return self._scheduler.submit_task(task)

    def get_task_result(self, kernel: object, task_id: str) -> Optional[Dict[str, object]]:
        """Get task result. Delegated from Kernel."""
        completed = getattr(kernel, "_completed_tasks", {})
        if task_id in completed:
            return completed[task_id]

        ledger = getattr(kernel, "ledger", None)
        if ledger:
            event = ledger.get_task(task_id)
            if event:
                return {"status": "COMPLETED", "task_id": task_id, "result": event.get("result")}
        return None

    async def run_loop(self, kernel: object) -> None:
        """🔄 MAIN KERNEL LOOP. Delegated from Kernel."""
        while str(getattr(kernel, "_status", "")) == "RUNNING":
            if hasattr(kernel, "tick_async"):
                await kernel.tick_async()  # type: ignore
            await asyncio.sleep(0.1)


__all__ = ["JanakaService"]
