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
        Execute during SENSORS phase.

        Args:
            kernel: Kernel instance (may be minimal in headless mode)
            transaction: PulseTransaction for mutations

        Returns:
            HookResult with ingestion summary
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

        except Exception as e:
            logger.error(f"❌ TaskManager failed: {e}", exc_info=True)
            return HookResult.error(f"Task management failed: {e}")

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
