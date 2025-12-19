"""
⚙️ TASK MANAGER PLUGIN - Sub-Operating System for Work

OPUS-091 Phase 3: Complete task lifecycle management with STATE SOVEREIGNTY

Responsibilities:
1. Initialize JsonTaskManager (plugin-local state)
2. SENSORS phase: Ingest from data/inbox/*.json and TASKS.md
3. ACTUATORS phase: Execute pending tasks via UnifiedRouter
4. CLEANUP phase: Sync TaskManager state back to TASKS.md
5. Inject manager into context (Dependency Inversion)

This is the hub. All work flows through here.
ARCHITECTURE: The plugin OWNS its state. It injects the manager into context
so other plugins (Interface) can read it.

VEDA-4 Architecture:
- SHABDA (Sound): Task ingestion (input)
- ARTHA (Meaning): Task interpretation
- PRATYAYA (Perception): State tracking
- KARMA (Action): Execution lifecycle
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from vibe_core.plugin_protocol import HookResult, KernelPlugin, PulsePhase

# OPUS-122: Import TaskStatus from SSOT
from vibe_core.task_types import TaskStatus

from .state_store import JsonTaskManager

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("TASK_MANAGER_PLUGIN")

# Import execution dependencies (graceful degradation if unavailable)
try:
    from vibe_core.runtime.unified_execution import (
        ExecutionRequest,
        MilkOceanGate,
        UnifiedExecutor,
        UnifiedRouter,
    )

    UNIFIED_EXECUTION_AVAILABLE = True
except ImportError:
    UNIFIED_EXECUTION_AVAILABLE = False
    logger.debug("UnifiedExecution not available - execution will be queued only")

try:
    from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

    MANAS_ORACLE_AVAILABLE = True
except ImportError:
    MANAS_ORACLE_AVAILABLE = False
    logger.debug("MANAS Oracle not available - no pre/post task analysis")

# OPUS-009 Wire 2: PrakritiSense Gate
try:
    from vibe_core.plugins.opus_assistant.manas.cortex.prakriti_sense import PrakritiSense

    PRAKRITI_SENSE_AVAILABLE = True
except ImportError:
    PRAKRITI_SENSE_AVAILABLE = False
    logger.debug("PrakritiSense not available - no Tamas gate check")


class TaskManagerPlugin(KernelPlugin):
    """
    Sub-OS for task management with STATE SOVEREIGNTY.

    The plugin OWNS its JsonTaskManager (local JSON state).
    It injects this into context so the system can use it.
    No legacy DB dependency.
    """

    def __init__(self):
        super().__init__()
        # STATE SOVEREIGNTY: Plugin owns its state directory
        self.state_dir = Path(__file__).parent / ".state"
        self.manager = JsonTaskManager(self.state_dir)
        logger.info(f"✅ TaskManager initialized with local state at {self.state_dir}")

    @property
    def plugin_id(self) -> str:
        return "task_manager"

    @property
    def pulse_phase(self) -> PulsePhase:
        """Can run in multiple phases - handle all task lifecycle."""
        return PulsePhase.SENSORS

    @property
    def priority(self) -> int:
        return 95  # High priority - run early in sensors phase

    def on_pulse(self, kernel: "RealVibeKernel", transaction) -> HookResult:
        """
        Execute during SENSORS, ACTUATORS, and CLEANUP phases.

        Routes to appropriate handler based on kernel's current pulse phase.
        CRITICAL: Inject self.manager into context so other plugins see it.

        Args:
            kernel: Kernel instance (may be minimal in headless mode)
            transaction: PulseTransaction for mutations

        Returns:
            HookResult with phase-specific summary
        """
        try:
            # DEPENDENCY INJECTION: Ensure our manager is in context
            if hasattr(kernel, "context"):
                kernel.context["task_manager"] = self.manager
                logger.debug("💉 TaskManager injected into kernel context")

            # Get project root from kernel or use cwd
            project_root = Path(kernel.workspace) if kernel and hasattr(kernel, "workspace") else Path.cwd()

            # Route based on current pulse phase
            current_phase = getattr(kernel, "pulse_phase", None)

            if current_phase == PulsePhase.SENSORS:
                return self._handle_sensors(project_root)
            elif current_phase == PulsePhase.ACTUATORS:
                return self._handle_actuators(kernel, project_root)
            elif current_phase == PulsePhase.CLEANUP:
                return self._handle_cleanup(project_root)
            else:
                logger.debug(f"⚙️ TaskManager: No handler for phase {current_phase}")
                return HookResult.ok(data={"phase": str(current_phase), "action": "skipped"})

        except Exception as e:
            logger.error(f"❌ TaskManager failed: {e}", exc_info=True)
            return HookResult.error(f"Task management failed: {e}")

    def _handle_sensors(self, project_root: Path) -> HookResult:
        """Handle SENSORS phase: Ingest tasks."""
        logger.info("⚙️ SENSORS: Task Manager initialization...")

        # Phase 1: Ingest JSON files from inbox
        inbox_count = self._ingest_json_files(project_root)

        # Phase 2: Parse TASKS.md for new tasks
        markdown_count = self._read_tasks_md(project_root)

        total = inbox_count + markdown_count
        if total > 0:
            msg = f"Ingested {total} tasks ({inbox_count} from inbox, {markdown_count} from TASKS.md)"
            logger.info(f"⚙️ SENSORS: {msg}")
            return HookResult.ok(
                data={"ingested": total, "inbox": inbox_count, "markdown": markdown_count, "phase": "sensors"}
            )
        else:
            logger.debug("⚙️ SENSORS: No new tasks to ingest")
            return HookResult.ok(data={"ingested": 0, "phase": "sensors"})

    def _handle_actuators(self, kernel: "RealVibeKernel", project_root: Path) -> HookResult:
        """Handle ACTUATORS phase: Execute pending tasks."""
        try:
            logger.info("⚙️ ACTUATORS: Task execution phase...")

            next_task = self.manager.get_next_pending()

            if not next_task:
                logger.debug("⚙️ ACTUATORS: No pending tasks to execute")
                return HookResult.ok(data={"executed": 0, "phase": "actuators"})

            logger.info(f"🚀 Executing task: {next_task.title}")

            # OPUS-009 Wire 2: Tamas Gate - Block if system state is broken
            if PRAKRITI_SENSE_AVAILABLE:
                try:
                    sense = PrakritiSense(project_root)
                    guna = sense.perceive_state()
                    if guna.needs_attention:
                        logger.warning(f"🔮 TAMAS GATE: {guna.tamas_count} paths in Tamas - blocking execution")
                        logger.info("   💊 Attempting auto-heal before task execution...")
                        # Try to heal
                        for plugin_id, paths in sense._discovered_paths.items():
                            for path_info in paths:
                                if sense.diagnose(path_info.path).value == "tamas":
                                    sense.heal(path_info.path)
                        # Re-check
                        guna = sense.perceive_state(refresh=True)
                        if guna.needs_attention:
                            logger.error(f"❌ TAMAS GATE: Still {guna.tamas_count} paths in Tamas after heal")
                            self.manager.update_status(next_task.id, TaskStatus.BLOCKED)
                            return HookResult.ok(data={"executed": 0, "blocked_by": "tamas_gate", "phase": "actuators"})
                        logger.info("   ✅ Healed to Sattva - proceeding with task")
                except Exception as e:
                    logger.warning(f"⚠️ PrakritiSense check failed: {e}")

            # Update status to IN_PROGRESS
            self.manager.update_status(next_task.id, TaskStatus.IN_PROGRESS)

            try:
                # OPUS-124: Get router AND executor from kernel context
                router = getattr(kernel, "router", None) if kernel else None
                executor = getattr(kernel, "executor", None) if kernel else None

                if not router and UNIFIED_EXECUTION_AVAILABLE:
                    try:
                        router = UnifiedRouter(kernel=kernel)
                    except Exception:
                        router = None

                if not executor and UNIFIED_EXECUTION_AVAILABLE and kernel:
                    try:
                        executor = UnifiedExecutor(kernel=kernel)
                    except Exception:
                        executor = None

                if not router:
                    logger.warning("⚠️ No Unified Router available - task queued but not executed")
                    logger.info(f"   📋 Task: {next_task.title}")
                    logger.info(f"   ⚡ Type: {next_task.type}")
                    return HookResult.ok(data={"executed": 0, "queued": 1, "phase": "actuators"})

                # Build execution prompt
                prompt = next_task.description

                logger.info("   🔄 Routing task through UnifiedRouter...")

                # MANAS Oracle Pre-Analysis Gate
                manas_oracle = getattr(kernel, "manas_oracle", None) if kernel else None
                if manas_oracle and MANAS_ORACLE_AVAILABLE:
                    try:
                        context = {
                            "task_title": next_task.title,
                            "task_type": next_task.type,
                            "is_automated": True,
                            "user_approval": False,
                        }
                        gate_decision = manas_oracle.pre_analysis(context)
                        logger.info(f"🧠 {gate_decision.get('recommendation', 'Proceeding...')}")

                        if not gate_decision.get("proceed", True):
                            logger.warning(f"🔮 MANAS Oracle blocked task: {gate_decision.get('reason')}")
                            self.manager.update_status(next_task.id, TaskStatus.BLOCKED)
                            return HookResult.ok(data={"executed": 0, "blocked": 1, "phase": "actuators"})
                    except Exception as e:
                        logger.warning(f"⚠️ MANAS Oracle consultation failed: {e}")

                # OPUS-124: Route first, then ACTUALLY execute
                req = ExecutionRequest(user_input=prompt, source="TASK_MANAGER_PLUGIN")
                gate = router.check_gate(req)

                result = {}

                if gate == MilkOceanGate.BLOCK:
                    result["status"] = "blocked"
                    result["reason"] = "Blocked by MilkOcean Gate"
                    self.manager.update_status(next_task.id, TaskStatus.BLOCKED)
                    logger.info("   🚫 Task blocked by MilkOcean Gate")
                    return HookResult.ok(data={"executed": 0, "blocked": 1, "phase": "actuators"})

                elif gate == MilkOceanGate.QUEUE:
                    result["status"] = "queued"
                    logger.info("   📋 Task queued for later execution")
                    return HookResult.ok(data={"executed": 0, "queued": 1, "phase": "actuators"})

                elif gate == MilkOceanGate.CRITICAL:
                    result["status"] = "critical"
                    logger.warning("   ⚠️ CRITICAL gate - escalating")
                    # Critical tasks still proceed but with elevated priority

                # Route to determine execution path
                route_res = router.route(prompt, source="TASK_MANAGER_PLUGIN")
                result["route_info"] = {
                    "execution_path": route_res.execution_path.value,
                    "target_id": route_res.target_id,
                    "confidence": route_res.confidence,
                }

                logger.info(
                    f"   📍 Routed to: {route_res.target_id or route_res.execution_path.value} "
                    f"(confidence={route_res.confidence:.2f})"
                )

                # OPUS-124: ACTUALLY EXECUTE (this was missing!)
                if executor:
                    import asyncio

                    logger.info("   ⚡ Executing task...")

                    # Run async executor in sync context
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                    exec_result = loop.run_until_complete(executor.execute(route_res))

                    if exec_result.status == "completed":
                        result["status"] = "completed"
                        result["response"] = exec_result.response
                        result["duration"] = exec_result.duration_seconds
                        self.manager.update_status(next_task.id, TaskStatus.COMPLETED)
                        logger.info(f"   ✅ Task completed ({exec_result.duration_seconds:.2f}s)")
                    else:
                        result["status"] = "failed"
                        result["error"] = exec_result.error
                        self.manager.update_status(next_task.id, TaskStatus.FAILED)
                        logger.error(f"   ❌ Task failed: {exec_result.error}")
                else:
                    # No executor available - mark as routed but not executed
                    logger.warning("   ⚠️ No executor available - task routed but not executed")
                    result["status"] = "routed_only"
                    # Don't mark as COMPLETED - it wasn't actually executed
                    return HookResult.ok(data={"executed": 0, "routed": 1, "phase": "actuators"})

                return HookResult.ok(data={"executed": 1, "status": result.get("status"), "phase": "actuators"})

            except Exception as e:
                logger.error(f"   ❌ Task execution failed: {e}")
                self.manager.update_status(next_task.id, TaskStatus.BLOCKED)
                return HookResult.error(f"Task execution failed: {e}")

        except Exception as e:
            logger.error(f"❌ ACTUATORS phase failed: {e}", exc_info=True)
            return HookResult.error(f"Actuators phase failed: {e}")

    def _handle_cleanup(self, project_root: Path) -> HookResult:
        """Handle CLEANUP phase: Cleanup and synchronization (delegated to interface)."""
        logger.debug("⚙️ CLEANUP: TaskManager state ready for interface rendering")
        stats = self.manager.get_stats()
        logger.info(f"📊 Task stats: {stats}")
        return HookResult.ok(data={"phase": "cleanup", "action": "interface_renders", "stats": stats})

    def _ingest_json_files(self, project_root: Path) -> int:
        """
        Ingest tasks from data/inbox/*.json files.

        Expected JSON format:
        {
            "title": "Task name",
            "description": "Optional description",
            "type": "general"
        }

        Returns:
            Number of successfully ingested tasks
        """
        inbox_dir = project_root / "data" / "inbox"

        if not inbox_dir.exists():
            return 0

        json_files = list(inbox_dir.glob("*.json"))
        if not json_files:
            return 0

        count = 0
        for json_file in json_files:
            try:
                with open(json_file, "r") as f:
                    task_data = json.load(f)

                # Create task in JsonTaskManager
                task = self.manager.add_task(
                    title=task_data.get("title", "Untitled Task"),
                    description=task_data.get("description", ""),
                    type=task_data.get("type", "general"),
                    metadata=task_data.get("metadata", {}),
                )

                logger.info(f"   ✅ Inbox: {task.title} (ID: {task.id})")
                count += 1

                # Remove from inbox (now safely in JSON state)
                json_file.unlink()

            except Exception as e:
                logger.warning(f"   ⚠️  Failed to ingest {json_file.name}: {e}")

        return count

    def _read_tasks_md(self, project_root: Path) -> int:
        """
        Parse TASKS.md and create tasks from unchecked checkboxes.

        Expected markdown format:
        - [ ] Task description

        Returns:
            Number of successfully created tasks
        """
        tasks_md = project_root / "TASKS.md"

        if not tasks_md.exists():
            logger.debug("⚠️  TASKS.md not found")
            return 0

        try:
            content = tasks_md.read_text()
        except Exception as e:
            logger.warning(f"⚠️  Could not read TASKS.md: {e}")
            return 0

        # Parse inbox section
        inbox_match = re.search(r"## 🎯 Inbox \(New Commands\).*?(?=##|\Z)", content, re.DOTALL)

        if not inbox_match:
            return 0

        inbox_text = inbox_match.group(0)

        # Find unchecked tasks: - [ ] Task description
        task_pattern = re.compile(r"- \[ \] (.+?)(?:\n|$)")

        new_tasks = 0
        for match in task_pattern.finditer(inbox_text):
            description = match.group(1).strip()

            # Check if task already exists (avoid duplicates)
            existing = [t for t in self.manager.get_all_tasks() if t.title == description]
            if existing:
                continue

            # Create task
            try:
                task = self.manager.add_task(
                    title=description,
                    description="Created from TASKS.md",
                    type="general",
                )
                logger.info(f"   ✅ Markdown: {task.title} (ID: {task.id})")
                new_tasks += 1
            except Exception as e:
                logger.warning(f"   ⚠️  Failed to create task '{description}': {e}")

        return new_tasks
