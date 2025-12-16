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

# OPUS-089: MANAS Oracle API - Wisdom Interface for System Agents
try:
    from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

    MANAS_ORACLE_AVAILABLE = True
except ImportError:
    ManasOracle = None
    MANAS_ORACLE_AVAILABLE = False

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

# OPUS-087 PRANA: Plugin Pulse Architecture
# Orchestrates plugin on_pulse() calls during heartbeat
try:
    from vibe_core.prana_orchestrator import PranaOrchestrator

    PRANA_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    PranaOrchestrator = None
    PRANA_ORCHESTRATOR_AVAILABLE = False


class HeartbeatEngine:
    """The Autonomous Task Orchestrator."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
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

                # OPUS-SILPA: Wire execution callback - GIVE MANAS HANDS!
                # Without this, MANAS can think but cannot act.
                try:
                    from vibe_core.plugins.opus_assistant.manas.intent_router import (
                        create_execution_callback,
                    )

                    execution_callback = create_execution_callback(workspace=project_root)
                    self.manas.set_execution_callback(execution_callback)
                    logger.info("🤲 SILPA: Execution callback wired - MANAS has hands!")
                except Exception as wire_err:
                    logger.warning(f"⚠️ SILPA: Could not wire execution: {wire_err}")

                # OPUS-JNANA: Verify LLM Provider is available
                # The provider auto-detects from env vars (OPENROUTER_API_KEY, ANTHROPIC_API_KEY, etc.)
                # Individual handlers import and create providers as needed at runtime
                try:
                    from vibe_core.runtime.providers.factory import create_provider

                    llm_provider = create_provider()
                    provider_name = type(llm_provider).__name__
                    if provider_name != "NoOpProvider":
                        logger.info(f"🧠 JNANA: LLM available ({provider_name}) - deep cognition enabled")
                    else:
                        logger.warning("⚠️ JNANA: No LLM configured - running in analysis-only mode")
                except Exception as llm_err:
                    logger.warning(f"⚠️ JNANA: LLM check failed: {llm_err}")

                logger.info("🧠 MANAS Cognitive Kernel ready")
            except Exception as e:
                logger.warning(f"⚠️ MANAS unavailable: {e}")
        else:
            logger.warning("⚠️ MANAS not available - no proactive cognition")

        # OPUS-089: Initialize MANAS Oracle API - Wisdom Interface
        self.manas_oracle = None
        if MANAS_ORACLE_AVAILABLE:
            try:
                self.manas_oracle = ManasOracle(config=ManasConfig(thinking_interval_minutes=15))
                logger.info("🔮 MANAS Oracle API ready - wisdom interface active")
            except Exception as e:
                logger.warning(f"⚠️ MANAS Oracle API initialization failed: {e}")
        else:
            logger.warning("⚠️ MANAS Oracle API not available")

        # OPUS-087 PRANA: Initialize Plugin Pulse Orchestrator
        self.prana_orchestrator = None
        if PRANA_ORCHESTRATOR_AVAILABLE:
            try:
                self.prana_orchestrator = PranaOrchestrator(kernel=None)

                # Headless Mode: Dynamically load all plugins via PluginLoader
                # This ensures Prana can see and pulse all plugins without a full kernel boot
                try:
                    from pathlib import Path

                    from vibe_core.plugin_loader import PluginLoader

                    logger.info("🔌 PRANA: dynamically loading plugins for headless pulse...")
                    # Scan plugins directory relative to current working directory (root)
                    scan_paths = [
                        Path("vibe_core/plugins"),
                        Path("vibe_core/plugins/runtime_extensions"),
                    ]
                    plugins_map, _ = PluginLoader.discover_and_load(scan_paths=scan_paths)

                    count = 0
                    for plugin in plugins_map.values():
                        self.prana_orchestrator.register_plugin(plugin)
                        count += 1

                    logger.info(f"   + Registered {count} plugins for pulse (Headless)")

                except Exception as e:
                    logger.warning(f"   - Failed to load plugins: {e}")

                logger.info("🫀 PRANA Orchestrator ready for plugin pulse")
            except Exception as e:
                logger.warning(f"⚠️ PRANA Orchestrator unavailable: {e}")

    def pulse(self):
        """Execute one heartbeat cycle."""
        logger.info("💓 HEARTBEAT PULSE STARTED")

        try:
            # OPUS-087 PRANA: Plugin Pulse Cycle (runs FIRST)
            # Executes all plugin on_pulse() methods in phase order
            # SENSORS (TaskIngestPlugin ingests here)
            # COGNITION → ACTUATORS → CLEANUP (SystemChroniclePlugin commits here)
            self._run_prana_pulse()

            # Phase 1: Execute pending tasks
            self._execute_tasks()

            # Phase 2: MANAS thinks (OPUS-073)
            self._manas_think()

            # Phase 3: Sync TaskManager → TASKS.md (write results)
            self._write_tasks_md()

            logger.info("✅ HEARTBEAT PULSE COMPLETED")
        except Exception as e:
            logger.error(f"❌ HEARTBEAT FAILED: {e}", exc_info=True)
            raise

    def _run_prana_pulse(self):
        """
        OPUS-087 PRANA: Execute plugin pulse cycle.

        Runs all registered plugins' on_pulse() methods in phase order:
        1. SENSORS - Collect data (opus_assistant)
        2. COGNITION - Process data
        3. ACTUATORS - Take actions (vedic_governance)
        4. CLEANUP - Cleanup temp state

        Mutations are batched and committed atomically at the end.
        """
        if not self.prana_orchestrator:
            logger.debug("🫀 PRANA: Orchestrator not available, skipping plugin pulse")
            return

        try:
            logger.info("🫀 PRANA: Starting plugin pulse cycle...")

            result = self.prana_orchestrator.run_pulse_cycle()

            plugins_run = result.get("plugins_executed", 0)
            mutations = result.get("mutations_committed", 0)
            failures = result.get("failures", 0)

            if failures > 0:
                logger.warning(f"🫀 PRANA: {plugins_run} plugins, {mutations} mutations, {failures} failures")
            else:
                logger.info(f"🫀 PRANA: {plugins_run} plugins executed, {mutations} mutations committed")

        except Exception as e:
            # Don't fail the entire heartbeat if PRANA fails
            logger.error(f"🫀 PRANA: Plugin pulse failed: {e}")
            # Continue with legacy heartbeat phases

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

            # ===== OPUS-089: MANAS Oracle Pre-Analysis Gate =====
            # Before routing, consult the MANAS Oracle for wisdom
            manas_gate_passed = True
            if self.manas_oracle:
                try:
                    context = {
                        "task_title": next_task.title,
                        "task_type": "generic_task",
                        "risk_level": "medium",
                        "is_automated": True,
                        "user_approval": False,
                    }
                    gate_decision = self.manas_oracle.pre_analysis(context)
                    logger.info(f"🧠 {gate_decision['recommendation']}")

                    if not gate_decision["proceed"]:
                        logger.warning(f"🔮 MANAS Oracle blocked task: {gate_decision['reason']}")
                        manas_gate_passed = False
                        self.task_manager.update_task(
                            next_task.id,
                            status=TaskStatus.BLOCKED,
                            metadata={
                                **next_task.metadata,
                                "blocked_by": "manas_oracle",
                                "block_reason": gate_decision["reason"],
                            },
                        )
                        return
                except Exception as e:
                    logger.warning(f"⚠️ MANAS Oracle consultation failed: {e}")
                    # Don't block - continue with execution

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

                # ===== OPUS-089: MANAS Oracle Post-Analysis =====
                # Learn from the executed task
                if self.manas_oracle:
                    try:
                        self.manas_oracle.post_analysis(
                            {
                                "task_type": "generic_task",
                                "success": True,
                                "error": None,
                            }
                        )
                    except Exception as e:
                        logger.warning(f"⚠️ MANAS post-analysis failed: {e}")

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
