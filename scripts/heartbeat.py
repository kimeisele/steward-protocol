#!/usr/bin/env python3
"""
🫀 HEARTBEAT ENGINE - The Autonomous Task Orchestrator

This is the "ignition key" for the TaskManager Ferrari.
Runs every 15 minutes via GitHub Actions to:
1. Sync TASKS.md ↔ TaskManager (bi-directional)
2. Ingest tasks from data/inbox/*.json
3. Execute pending tasks
4. Commit progress to Git

Architecture:
- Paper UI: TASKS.md (human-friendly interface)
- State Machine: TaskManager (vibe_core)
- Persistence: SQLite (data/vibe_agency.db)
- Concurrency: FileLock (.vibe/state/.lock)
"""

import json
import logging
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from vibe_core.task_management.models import TaskStatus
from vibe_core.task_management.task_manager import TaskManager

# Import Unified Router for task execution/routing
try:
    from vibe_core.runtime.unified_execution import ExecutionRequest, MilkOceanGate, UnifiedRouter

    UNIFIED_ROUTER_AVAILABLE = True
except ImportError:
    UnifiedRouter = None
    UNIFIED_ROUTER_AVAILABLE = False

# OPUS-073: MANAS Cognitive Kernel - Proactive System Intelligence
try:
    from vibe_core.plugins.opus_assistant.manas import CognitiveKernel, ManasConfig

    MANAS_AVAILABLE = True
except ImportError:
    CognitiveKernel = None
    ManasConfig = None
    MANAS_AVAILABLE = False

# OPUS-074 WIRING: SQLiteLedger for VAJRA binding in headless mode
try:
    from vibe_core.ledger import SQLiteLedger

    LEDGER_AVAILABLE = True
except ImportError:
    SQLiteLedger = None
    LEDGER_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("HEARTBEAT")

# PRANA integration - config-driven behavior
# Allows changing heartbeat behavior via config/prana.yaml WITHOUT touching
# the VISNU-protected workflow files in .github/workflows/
try:
    from vibe_core.prana import (
        ensure_kernel_running,
        get_last_heartbeat,
        record_heartbeat,
    )
    from vibe_core.prana import (
        load_config as load_prana_config,
    )

    PRANA_AVAILABLE = True
except ImportError:
    PRANA_AVAILABLE = False
    load_prana_config = None


class HeartbeatEngine:
    """The Autonomous Task Orchestrator."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tasks_md = project_root / "TASKS.md"
        self.inbox_dir = project_root / "data" / "inbox"
        self.task_manager = TaskManager(project_root)

        # Initialize Unified Router for intelligent task execution
        self.router = None
        if UNIFIED_ROUTER_AVAILABLE:
            try:
                # Initialize without kernel (standalone mode)
                self.router = UnifiedRouter(kernel=None)
                logger.info("🌊 Unified Router ready for task routing")
            except Exception as e:
                logger.warning(f"⚠️ Unified Router unavailable: {e}")
        else:
            logger.warning("⚠️ Unified Router not available - tasks will queue but not execute")

        # OPUS-074 WIRING: Initialize SQLiteLedger for VAJRA (headless mode)
        self.ledger = None
        if LEDGER_AVAILABLE:
            try:
                ledger_path = project_root / "data" / "vibe_ledger.db"
                ledger_path.parent.mkdir(parents=True, exist_ok=True)
                self.ledger = SQLiteLedger(str(ledger_path))
                logger.info("⚡ VAJRA: SQLiteLedger ready (headless mode)")
            except Exception as e:
                logger.warning(f"⚠️ VAJRA: Ledger unavailable: {e}")
        else:
            logger.warning("⚠️ VAJRA: SQLiteLedger not available - running in shadow mode")

        # OPUS-073: Initialize MANAS Cognitive Kernel
        self.manas = None
        if MANAS_AVAILABLE:
            try:
                config = ManasConfig(
                    thinking_interval_minutes=15,  # Match heartbeat interval
                    auto_execute_safe=True,  # Execute SAFE intents automatically
                )
                self.manas = CognitiveKernel(workspace=project_root, config=config)

                # OPUS-074 WIRING: Inject Ledger for VAJRA binding
                if self.ledger and hasattr(self.manas, "inject_ledger"):
                    self.manas.inject_ledger(self.ledger)
                    logger.info("⚡ VAJRA: Ledger bound to MANAS")

                logger.info("🧠 MANAS Cognitive Kernel ready")
            except Exception as e:
                logger.warning(f"⚠️ MANAS unavailable: {e}")
        else:
            logger.warning("⚠️ MANAS not available - no proactive cognition")

    def pulse(self):
        """Execute one heartbeat cycle."""
        logger.info("💓 HEARTBEAT PULSE STARTED")

        try:
            # Phase 1: Ingest from inbox
            self._ingest_inbox()

            # Phase 2: Sync TASKS.md → TaskManager (read user input)
            self._read_tasks_md()

            # Phase 3: Execute pending tasks
            self._execute_tasks()

            # Phase 4: MANAS thinks (OPUS-073)
            self._manas_think()

            # Phase 4.5: Refresh OPUS.md via Circuit Executor (OPUS-083)
            self._execute_maintenance_circuit()

            # Phase 5: Sync TaskManager → TASKS.md (write results)
            self._write_tasks_md()

            # Phase 6: Commit progress
            self._commit_progress()

            logger.info("✅ HEARTBEAT PULSE COMPLETED")
        except Exception as e:
            logger.error(f"❌ HEARTBEAT FAILED: {e}", exc_info=True)
            raise

    def _ingest_inbox(self):
        """Ingest tasks from data/inbox/*.json."""
        if not self.inbox_dir.exists():
            return

        json_files = list(self.inbox_dir.glob("*.json"))
        if not json_files:
            return

        logger.info(f"📥 Ingesting {len(json_files)} tasks from inbox...")

        for json_file in json_files:
            try:
                with open(json_file, "r") as f:
                    task_data = json.load(f)

                # Create task in TaskManager
                task = self.task_manager.add_task(
                    title=task_data.get("title", "Untitled Task"),
                    description=task_data.get("description", ""),
                    priority=task_data.get("priority", 0),
                    assigned_agent=task_data.get("assignee"),
                )

                logger.info(f"   ✅ Ingested: {task.title} (ID: {task.id})")

                # Remove from inbox (now safely in SQLite)
                json_file.unlink()

            except Exception as e:
                logger.warning(f"   ⚠️  Failed to ingest {json_file.name}: {e}")

    def _read_tasks_md(self):
        """Read TASKS.md and create new tasks from checkboxes."""
        if not self.tasks_md.exists():
            logger.warning("⚠️  TASKS.md not found, skipping sync")
            return

        content = self.tasks_md.read_text()

        # Parse inbox section
        inbox_match = re.search(r"## 🎯 Inbox \(New Commands\).*?(?=##|\Z)", content, re.DOTALL)

        if not inbox_match:
            return

        inbox_text = inbox_match.group(0)

        # Strip code blocks (examples shouldn't be parsed as real tasks)
        inbox_text = re.sub(r"```.*?```", "", inbox_text, flags=re.DOTALL)

        # Find unchecked tasks: - [ ] Task description @agent priority:high
        # Fixed regex: capture until @ or priority: or end of line (not greedy single char)
        task_pattern = re.compile(
            r"- \[ \] ([^@\n]+?)(?:\s*@(\w+))?(?:\s*priority:(high|medium|low))?\s*$", re.MULTILINE
        )

        new_tasks = 0
        for match in task_pattern.finditer(inbox_text):
            description = match.group(1).strip()
            agent = match.group(2)
            priority_str = match.group(3)

            # Map priority
            priority_map = {"high": 90, "medium": 50, "low": 10}
            priority = priority_map.get(priority_str, 50)

            # Check if task already exists (avoid duplicates)
            existing = [t for t in self.task_manager.list_tasks() if t.title == description]
            if existing:
                continue

            # Create task
            try:
                task = self.task_manager.add_task(
                    title=description,
                    description=f"Created from TASKS.md at {datetime.now().isoformat()}",
                    priority=priority,
                    assigned_agent=agent,
                )
                logger.info(f"📝 Created task from TASKS.md: {task.title}")
                new_tasks += 1
            except Exception as e:
                logger.warning(f"⚠️  Failed to create task '{description}': {e}")

        if new_tasks > 0:
            logger.info(f"   ✅ Created {new_tasks} new tasks from TASKS.md")

    def _execute_tasks(self):
        """Execute pending tasks."""
        next_task = self.task_manager.get_next_task()

        if not next_task:
            logger.info("📭 No pending tasks to execute")
            return

        logger.info(f"🚀 Executing task: {next_task.title}")

        # Update status to IN_PROGRESS
        self.task_manager.update_task(next_task.id, status=TaskStatus.IN_PROGRESS)

        try:
            if not self.router:
                logger.warning("⚠️ No Unified Router available - task queued but not executed")
                logger.info(f"   📋 Task: {next_task.title}")
                logger.info(f"   🎯 Agent: {next_task.assignee or 'auto-route'}")
                logger.info(f"   ⚡ Priority: {next_task.priority}")
                return

            # Build the execution request
            # If assignee is specified, mention it in the prompt
            if next_task.assignee:
                prompt = f"@{next_task.assignee}: {next_task.description}"
            else:
                prompt = next_task.description

            logger.info("   🔄 Routing task through UnifiedRouter...")
            logger.info(f"   📝 Prompt: {prompt[:100]}...")

            # --- UNIFIED EXECUTOR ADAPTATION ---
            # Create request
            req = ExecutionRequest(user_input=prompt, source="HEARTBEAT_ENGINE")

            # 1. Check Gate
            gate = self.router.check_gate(req)

            result = {}  # Mock result dict for compatibility

            if gate == MilkOceanGate.BLOCK:
                result["status"] = "blocked"
                result["reason"] = "Blocked by MilkOcean Gate"
            elif gate == MilkOceanGate.QUEUE:
                result["status"] = "queued"
            elif gate == MilkOceanGate.CRITICAL:
                result["status"] = "critical"
            else:
                # 2. Route (Dry Run - No Kernel/Executor)
                route_res = self.router.route(prompt, source="HEARTBEAT_ENGINE")
                result["status"] = "routing"
                # ExecutionRequest is a dataclass, not dict - use attributes
                result["path"] = route_res.target_id or route_res.execution_path.value
                result["route_info"] = {
                    "execution_path": route_res.execution_path.value,
                    "target_id": route_res.target_id,
                    "confidence": route_res.confidence,
                }

            logger.info(f"   ✅ Router response: {result.get('status', 'unknown')}")

            # Store result in task metadata
            self.task_manager.update_task(
                next_task.id,
                metadata={
                    **next_task.metadata,
                    "execution_result": result,
                    "executed_at": datetime.now().isoformat(),
                },
            )

            # Update status based on router response
            status = result.get("status")

            if status == "blocked":
                logger.warning(f"   ⛔ Task blocked: {result.get('reason', 'unknown')}")
                self.task_manager.update_task(next_task.id, status=TaskStatus.BLOCKED)

            elif status == "queued":
                # Task is in lazy queue - keep as IN_PROGRESS
                logger.info("   📋 Task queued for later processing")
                # Don't change status - stays IN_PROGRESS

            elif status == "delegated":
                # Task delegated to agent - track the agent task
                logger.info(f"   🔄 Task delegated to {result.get('agent')}")
                self.task_manager.update_task(
                    next_task.id,
                    metadata={
                        **next_task.metadata,
                        "delegated_task_id": result.get("task_id"),
                        "delegated_to": result.get("agent"),
                    },
                )
                # Don't mark complete - agent hasn't finished yet

            elif status == "routing":
                # IMPORTANT: "routing" means MilkOcean decided WHERE to route,
                # but did NOT actually execute the agent (no LLM configured).
                # This is a SILENT FAILURE we need to catch!
                logger.warning(f"   ⚠️  Task routed to '{result.get('path')}' but NOT executed")
                logger.warning("   💡 Reason: No live execution (Heartbeat runs in DRY RUN mode)")
                logger.warning("   📋 This is a DRY RUN - task marked as PENDING for manual review")
                # Keep task as PENDING, don't mark completed
                self.task_manager.update_task(
                    next_task.id,
                    status=TaskStatus.PENDING,
                    metadata={
                        **next_task.metadata,
                        "routing_result": result,
                        "warning": "Task was routed but not executed (DRY RUN MODE)",
                        "recommended_agent": result.get("path"),
                    },
                )

            elif status == "critical" or status == "critical_handled":
                # P4.2: Critical tasks were handled with emergency priority
                logger.info("   🐘 CRITICAL task handled via Gajendra Protocol")
                self.task_manager.update_task(
                    next_task.id,
                    status=TaskStatus.COMPLETED,
                    metadata={
                        **next_task.metadata,
                        "critical_handled": True,
                        "protocol": "Gajendra",
                    },
                )

            elif status == "COMPLETED" or status == "completed" or status == "success":
                # Only mark as completed if agent actually ran
                logger.info("   🎉 Task successfully executed")
                self.task_manager.update_task(next_task.id, status=TaskStatus.COMPLETED)

            else:
                # Unknown status - be conservative
                logger.warning(f"   ⚠️  Unknown router status: {status}")
                logger.warning("   📋 Marking as PENDING for safety")
                self.task_manager.update_task(next_task.id, status=TaskStatus.PENDING)

        except Exception as e:
            logger.error(f"   ❌ Task execution failed: {e}")
            import traceback

            traceback.print_exc()
            self.task_manager.update_task(
                next_task.id,
                status=TaskStatus.BLOCKED,
                metadata={
                    **next_task.metadata,
                    "error": str(e),
                    "failed_at": datetime.now().isoformat(),
                },
            )

    def _manas_think(self):
        """OPUS-073: Invoke MANAS cognitive cycle."""
        if not self.manas:
            logger.info("🧠 MANAS not available - skipping cognitive cycle")
            return

        logger.info("🧠 MANAS: Starting cognitive cycle...")

        try:
            # Force=True because heartbeat runs on schedule (not rate-limited)
            intents = self.manas.think(force=True)

            if intents:
                logger.info(f"🧠 MANAS generated {len(intents)} intent(s):")
                for intent in intents:
                    logger.info(f"   • [{intent.risk.value}] {intent.title}")
                    if intent.auto_executable:
                        logger.info(f"     → Auto-executable: {intent.action}")
            else:
                logger.info("🧠 MANAS: No new intents generated")

        except Exception as e:
            logger.warning(f"⚠️ MANAS cognitive cycle failed: {e}")
            # Don't raise - MANAS failure shouldn't stop heartbeat

    def _execute_maintenance_circuit(self):
        """
        OPUS-083: Execute maintenance_pulse circuit via CognitiveCircuitExecutor.

        This is THE FIX for the "parallel structures" problem.
        The heartbeat now refreshes OPUS.md through the proper circuit architecture.

        Fallback: If circuit not found, refresh OPUS.md directly.
        """
        logger.info("⚡ Executing maintenance circuit...")

        try:
            from vibe_core.plugins.opus_assistant.manas.circuit_executor import (
                CognitiveCircuitExecutor,
            )

            executor = CognitiveCircuitExecutor(self.project_root)
            result = executor.execute_circuit("maintenance_pulse")

            if result.get("success"):
                logger.info(f"⚡ Maintenance circuit completed: {result.get('states_executed', 0)} states")
            else:
                # Circuit not found or failed - fallback to direct refresh
                logger.warning(f"⚠️ Circuit failed, using direct refresh: {result.get('error')}")
                self._direct_opus_refresh()

        except ImportError as e:
            logger.warning(f"⚠️ CognitiveCircuitExecutor not available: {e}")
            self._direct_opus_refresh()
        except Exception as e:
            logger.warning(f"⚠️ Maintenance circuit failed: {e}")
            self._direct_opus_refresh()

    def _direct_opus_refresh(self):
        """
        Fallback: Refresh OPUS.md directly via OpusDashboardRenderer.

        Used when circuit executor is not available or circuit not found.
        """
        try:
            from vibe_core.plugins.opus_assistant.render.opus_dashboard_renderer import (
                OpusDashboardRenderer,
            )

            renderer = OpusDashboardRenderer(self.project_root, kernel=None)
            content = renderer.render(quick=True)

            opus_path = self.project_root / "OPUS.md"
            opus_path.write_text(content)
            logger.info("📋 OPUS.md refreshed (direct fallback)")

        except Exception as e:
            logger.warning(f"⚠️ Direct OPUS refresh failed: {e}")

    def _write_tasks_md(self):
        """Write TaskManager state back to TASKS.md."""
        all_tasks = self.task_manager.list_tasks()

        # Categorize tasks
        pending = [t for t in all_tasks if t.status == TaskStatus.PENDING]
        running = [t for t in all_tasks if t.status == TaskStatus.IN_PROGRESS]
        completed = [t for t in all_tasks if t.status == TaskStatus.COMPLETED]
        blocked = [t for t in all_tasks if t.status == TaskStatus.BLOCKED]

        # Build new TASKS.md content
        content = f"""# 📋 Mission Control

> **Auto-Generated Task Board** | Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
> **Status:** 🟢 Operational | **Active Tasks:** {len(running)} | **Completed:** {len(completed)}

---

## 🎯 Inbox (New Commands)

Write your tasks here. The heartbeat will pick them up automatically.

**Syntax:**
```markdown
- [ ] Task description @agent_name priority:high
- [ ] Another task @engineer priority:medium
- [ ] Analyze codebase @analyst
```

**Available Agents:**
`@envoy` `@engineer` `@analyst` `@herald` `@civic` `@scribe` `@auditor` `@mechanic` `@archivist` `@marketer` `@scientist` `@watchman`

---

## 🔄 Active Missions (In Progress)

"""
        if running:
            for task in running:
                agent = task.assignee or "auto-routed"
                content += f"- [~] {task.title} @{agent}\n"
                content += f"  > *Status: RUNNING (ID: {task.id[:8]}...)*\n"
                content += f"  > **Priority:** {task.priority} | **Started:** {task.updated_at.strftime('%H:%M')}\n\n"
        else:
            content += "No active missions yet.\n\n"

        content += "---\n\n## ✅ Recently Completed\n\n"

        if completed:
            recent = sorted(completed, key=lambda t: t.updated_at, reverse=True)[:5]
            for task in recent:
                agent = task.assignee or "auto-routed"
                content += f"- [x] {task.title} @{agent}\n"
                content += f"  > *Completed: {task.updated_at.strftime('%Y-%m-%d %H:%M')}*\n\n"
        else:
            content += "No completed tasks yet.\n\n"

        content += "---\n\n## 📊 System Health\n\n"
        content += "| Metric | Value |\n"
        content += "|--------|-------|\n"
        content += f"| Total Tasks | {len(all_tasks)} |\n"
        content += f"| Pending | {len(pending)} |\n"
        content += f"| Running | {len(running)} |\n"
        content += f"| Completed | {len(completed)} |\n"
        content += f"| Blocked | {len(blocked)} |\n\n"

        content += "---\n\n"
        content += "**Heartbeat:** Operational  \n"
        content += f"**Last Pulse:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}  \n"
        content += "**Next Check:** ~15 minutes\n\n"

        content += """---

## 📖 How It Works

1. **Write tasks** in the Inbox section using checkboxes `- [ ]`
2. **Tag agents** with `@agent_name` to route directly (optional)
3. **Set priority** with `priority:high|medium|low` (optional)
4. **Save & commit** the file
5. **Heartbeat runs** every 15 minutes (GitHub Actions)
6. **Tasks execute** and update their status automatically
7. **Results appear** in the Active/Completed sections

**Unified Router** handles task intelligence.

---

*Generated by STEWARD Protocol Task Management System*
"""

        self.tasks_md.write_text(content)
        logger.info("📝 Updated TASKS.md with current state")

    def _commit_progress(self):
        """Commit changes to Git."""
        try:
            # Stage changes
            subprocess.run(
                ["git", "add", "TASKS.md", "data/vibe_agency.db"],
                cwd=self.project_root,
                check=True,
                capture_output=True,
            )

            # Check if there are changes to commit
            result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=self.project_root, capture_output=True)

            if result.returncode == 0:
                logger.info("📝 No changes to commit")
                return

            # Commit
            commit_msg = f"🫀 Heartbeat pulse: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=self.project_root, check=True, capture_output=True)

            logger.info("✅ Changes committed to Git")

        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️  Git commit failed: {e}")


def main():
    """
    Main entry point.

    PRANA Integration:
    - Checks config/prana.yaml for settings
    - Respects min_interval_minutes to prevent duplicate runs
    - Optionally boots kernel before processing tasks
    - Records heartbeat timestamp for tracking

    This allows changing behavior WITHOUT modifying VISNU-protected workflows.
    """
    # PRANA: Config-driven behavior
    if PRANA_AVAILABLE:
        config = load_prana_config()

        # Check if heartbeat is enabled
        if not config.heartbeat.enabled:
            logger.info("💓 PRANA: Heartbeat disabled in config. Exiting.")
            return

        # Check minimum interval (prevent duplicate runs)
        last_pulse = get_last_heartbeat()
        if last_pulse:
            from datetime import datetime, timedelta

            try:
                last_dt = datetime.fromisoformat(last_pulse)
                min_interval = timedelta(minutes=config.heartbeat.min_interval_minutes)
                if datetime.utcnow() - last_dt < min_interval:
                    logger.info(
                        f"💓 PRANA: Skipping - last pulse was {last_pulse} (interval: {config.heartbeat.min_interval_minutes}min)"
                    )
                    return
            except Exception as e:
                logger.warning(f"⚠️ Could not parse last heartbeat: {e}")

        # Boot kernel if configured
        if config.heartbeat.boot_kernel_first:
            logger.info("💓 PRANA: Ensuring kernel is running...")
            ensure_kernel_running(config)

        # Record this heartbeat
        record_heartbeat()

        logger.info(f"💓 PRANA: Config loaded - max_tasks={config.heartbeat.max_tasks_per_pulse}")
    else:
        logger.warning("⚠️ PRANA not available - running with defaults")

    # Run the heartbeat
    engine = HeartbeatEngine(project_root)
    engine.pulse()


if __name__ == "__main__":
    main()
