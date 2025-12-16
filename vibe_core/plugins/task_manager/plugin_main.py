"""
⚙️ TASK MANAGER PLUGIN - Sub-Operating System for Work

OPUS-091 Phase 3: Complete task lifecycle management

Responsibilities:
1. SENSORS phase: Ingest from data/inbox/*.json and TASKS.md
2. ACTUATORS phase: Execute pending tasks via UnifiedRouter
3. CLEANUP phase: Sync TaskManager state back to TASKS.md

This is the hub. All work flows through here.

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
from vibe_core.task_management.models import TaskStatus

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("TASK_MANAGER_PLUGIN")

# Import execution dependencies (graceful degradation if unavailable)
try:
    from vibe_core.runtime.unified_execution import ExecutionRequest, MilkOceanGate

    UNIFIED_ROUTER_AVAILABLE = True
except ImportError:
    UNIFIED_ROUTER_AVAILABLE = False
    logger.debug("UnifiedRouter not available - execution will be queued only")

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
    Sub-OS for task management.

    Ingests, queues, executes, and archives all work.
    """

    @property
    def plugin_id(self) -> str:
        return "task_manager"

    @property
    def pulse_phase(self) -> PulsePhase:
        """Can run in multiple phases - handle all task lifecycle."""
        # Note: This plugin handles SENSORS, ACTUATORS, and CLEANUP
        # The pulse phase property returns SENSORS as primary, but on_pulse
        # checks kernel.pulse_phase to route to appropriate handler
        return PulsePhase.SENSORS

    @property
    def priority(self) -> int:
        return 95  # High priority - run early in sensors phase

    def on_pulse(self, kernel: "RealVibeKernel", transaction) -> HookResult:
        """
        Execute during SENSORS, ACTUATORS, and CLEANUP phases.

        Routes to appropriate handler based on kernel's current pulse phase.

        Args:
            kernel: Kernel instance (may be minimal in headless mode)
            transaction: PulseTransaction for mutations

        Returns:
            HookResult with phase-specific summary
        """
        try:
            # Get task manager from kernel
            if not kernel or not hasattr(kernel, "task_manager"):
                logger.warning("❌ TaskManager: kernel/task_manager not available")
                return HookResult.error("No task manager in kernel")

            task_manager = kernel.task_manager

            # Get project root from kernel or use cwd
            if kernel and hasattr(kernel, "workspace"):
                project_root = Path(kernel.workspace)
            else:
                project_root = Path.cwd()

            # Route based on current pulse phase
            current_phase = getattr(kernel, "pulse_phase", None)

            if current_phase == PulsePhase.SENSORS:
                return self._handle_sensors(task_manager, project_root)
            elif current_phase == PulsePhase.ACTUATORS:
                return self._handle_actuators(kernel, task_manager, project_root)
            elif current_phase == PulsePhase.CLEANUP:
                return self._handle_cleanup(task_manager, project_root)
            else:
                logger.debug(f"⚙️ TaskManager: No handler for phase {current_phase}")
                return HookResult.ok(data={"phase": str(current_phase), "action": "skipped"})

        except Exception as e:
            logger.error(f"❌ TaskManager failed: {e}", exc_info=True)
            return HookResult.error(f"Task management failed: {e}")

    def _handle_sensors(self, task_manager, project_root: Path) -> HookResult:
        """Handle SENSORS phase: Ingest tasks."""
        logger.info("⚙️ SENSORS: Task Manager initialization...")

        # Phase 1: Ingest JSON files from inbox
        inbox_count = self._ingest_json_files(task_manager, project_root)

        # Phase 2: Parse TASKS.md for new tasks
        markdown_count = self._read_tasks_md(task_manager, project_root)

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

    def _handle_actuators(self, kernel: "RealVibeKernel", task_manager, project_root: Path) -> HookResult:
        """Handle ACTUATORS phase: Execute pending tasks."""
        try:
            logger.info("⚙️ ACTUATORS: Task execution phase...")

            next_task = task_manager.get_next_pending()

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
                            task_manager.update_status(next_task.id, TaskStatus.BLOCKED)
                            return HookResult.ok(data={"executed": 0, "blocked_by": "tamas_gate", "phase": "actuators"})
                        logger.info("   ✅ Healed to Sattva - proceeding with task")
                except Exception as e:
                    logger.warning(f"⚠️ PrakritiSense check failed: {e}")

            # Update status to IN_PROGRESS
            task_manager.update_status(next_task.id, TaskStatus.IN_PROGRESS)

            try:
                # Get router from kernel context
                router = getattr(kernel, "router", None)
                if not router and UNIFIED_ROUTER_AVAILABLE:
                    try:
                        from vibe_core.runtime.unified_execution import UnifiedRouter

                        router = UnifiedRouter(kernel=kernel)
                    except Exception:
                        router = None

                if not router:
                    logger.warning("⚠️ No Unified Router available - task queued but not executed")
                    logger.info(f"   📋 Task: {next_task.title}")
                    logger.info(f"   🎯 Agent: {next_task.assigned_agent or 'auto-route'}")
                    logger.info(f"   ⚡ Priority: {next_task.priority}")
                    return HookResult.ok(data={"executed": 0, "queued": 1, "phase": "actuators"})

                # Build execution prompt
                if next_task.assigned_agent:
                    prompt = f"@{next_task.assigned_agent}: {next_task.description}"
                else:
                    prompt = next_task.description

                logger.info("   🔄 Routing task through UnifiedRouter...")

                # MANAS Oracle Pre-Analysis Gate
                manas_oracle = getattr(kernel, "manas_oracle", None)
                if manas_oracle and MANAS_ORACLE_AVAILABLE:
                    try:
                        context = {
                            "task_title": next_task.title,
                            "task_type": "generic_task",
                            "risk_level": "medium",
                            "is_automated": True,
                            "user_approval": False,
                        }
                        gate_decision = manas_oracle.pre_analysis(context)
                        logger.info(f"🧠 {gate_decision.get('recommendation', 'Proceeding...')}")

                        if not gate_decision.get("proceed", True):
                            logger.warning(f"🔮 MANAS Oracle blocked task: {gate_decision.get('reason')}")
                            task_manager.update_status(next_task.id, TaskStatus.BLOCKED)
                            return HookResult.ok(data={"executed": 0, "blocked": 1, "phase": "actuators"})
                    except Exception as e:
                        logger.warning(f"⚠️ MANAS Oracle consultation failed: {e}")

                # Route and execute
                from vibe_core.runtime.unified_execution import ExecutionRequest, MilkOceanGate

                req = ExecutionRequest(user_input=prompt, source="TASK_MANAGER_PLUGIN")
                gate = router.check_gate(req)

                result = {}

                if gate == MilkOceanGate.BLOCK:
                    result["status"] = "blocked"
                    result["reason"] = "Blocked by MilkOcean Gate"
                elif gate == MilkOceanGate.QUEUE:
                    result["status"] = "queued"
                elif gate == MilkOceanGate.CRITICAL:
                    result["status"] = "critical"
                else:
                    route_res = router.route(prompt, source="TASK_MANAGER_PLUGIN")
                    result["status"] = "routing"
                    result["path"] = route_res.target_id or route_res.execution_path.value
                    result["route_info"] = {
                        "execution_path": route_res.execution_path.value,
                        "target_id": route_res.target_id,
                        "confidence": route_res.confidence,
                    }

                logger.info(f"   ✅ Router response: {result.get('status', 'unknown')}")

                # Update task with result
                task_manager.update_status(next_task.id, TaskStatus.COMPLETED)

                return HookResult.ok(data={"executed": 1, "status": result.get("status"), "phase": "actuators"})

            except Exception as e:
                logger.error(f"   ❌ Task execution failed: {e}")
                task_manager.update_status(next_task.id, TaskStatus.BLOCKED)
                return HookResult.error(f"Task execution failed: {e}")

        except Exception as e:
            logger.error(f"❌ ACTUATORS phase failed: {e}", exc_info=True)
            return HookResult.error(f"Actuators phase failed: {e}")

    def _handle_cleanup(self, task_manager, project_root: Path) -> HookResult:
        """Handle CLEANUP phase: Cleanup and synchronization (delegated to interface)."""
        logger.debug("⚙️ CLEANUP: TaskManager state ready for interface rendering")
        return HookResult.ok(data={"phase": "cleanup", "action": "interface_renders"})

    def _ingest_json_files(self, task_manager, project_root: Path) -> int:
        """
        Ingest tasks from data/inbox/*.json files.

        Expected JSON format:
        {
            "title": "Task name",
            "description": "Optional description",
            "priority": 0-100,
            "assignee": "optional_agent_name"
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

                # Create task in TaskManager
                task = task_manager.add_task(
                    title=task_data.get("title", "Untitled Task"),
                    description=task_data.get("description", ""),
                    priority=task_data.get("priority", 0),
                    assigned_agent=task_data.get("assignee"),
                )

                logger.info(f"   ✅ Inbox: {task.title} (ID: {task.id[:8]}...)")
                count += 1

                # Remove from inbox (now safely in SQLite)
                json_file.unlink()

            except Exception as e:
                logger.warning(f"   ⚠️  Failed to ingest {json_file.name}: {e}")

        return count

    def _read_tasks_md(self, task_manager, project_root: Path) -> int:
        """
        Parse TASKS.md and create tasks from unchecked checkboxes.

        Expected markdown format:
        - [ ] Task description @agent_name priority:high
        - [ ] Another task priority:medium

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

        # Find unchecked tasks: - [ ] Task description @agent priority:high
        task_pattern = re.compile(r"- \[ \] (.+?)(?:@(\w+))?\s*(?:priority:(high|medium|low))?")

        new_tasks = 0
        for match in task_pattern.finditer(inbox_text):
            description = match.group(1).strip()
            agent = match.group(2)
            priority_str = match.group(3)

            # Map priority strings to numeric values
            priority_map = {"high": 90, "medium": 50, "low": 10}
            priority = priority_map.get(priority_str, 50)

            # Check if task already exists (avoid duplicates)
            existing = [t for t in task_manager.list_tasks() if t.title == description]
            if existing:
                continue

            # Create task
            try:
                task = task_manager.add_task(
                    title=description,
                    description=f"Created from TASKS.md at {datetime.now().isoformat()}",
                    priority=priority,
                    assigned_agent=agent,
                )
                logger.info(f"   ✅ Markdown: {task.title} (ID: {task.id[:8]}...)")
                new_tasks += 1
            except Exception as e:
                logger.warning(f"   ⚠️  Failed to create task '{description}': {e}")

        return new_tasks
