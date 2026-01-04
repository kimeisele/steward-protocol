"""
⚙️ TASK MANAGER PLUGIN - Stateless Ingestor

OPUS-213: ADVAITA - Unified Task Sovereignty
============================================
This plugin is now a STATELESS ingestor that delegates to Core TaskManager.
No local state. Single Source of Truth.

Responsibilities:
1. SENSORS phase: Ingest from data/inbox/*.json and TASKS.md -> Core
2. ACTUATORS phase: Execute pending tasks via UnifiedRouter
3. CLEANUP phase: Request Core stats
"""

import json
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.di import ServiceRegistry
from vibe_core.plugin_protocol import HookResult, KernelPlugin, PulsePhase
from vibe_core.protocols.task import TaskProtocol
from vibe_core.task_types import TaskStatus

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol


# =============================================================================
# OPUS-213: CoreManagerAdapter
# =============================================================================
# Wraps Core TaskManager to provide the API the plugin expects.
# This allows zero changes to plugin logic while using Core as backend.
# =============================================================================


class CoreManagerAdapter:
    """
    Adapter that wraps Core TaskManager with plugin-compatible API.

    Maps:
        get_next_pending() -> get_next_task()
        get_stats() -> get_metrics()
        update_status(id, status) -> update_task(id, status=status)
        get_all_tasks() -> list_tasks()
    """

    def __init__(self, core_manager):
        self._core = core_manager

    def add_task(self, title: str, description: str = "", type: str = "general", metadata: Dict = None):
        """Delegate to core with field mapping."""
        task = self._core.add_task(title=title, description=description)
        # Core Task has different structure, wrap for compatibility
        return _TaskWrapper(task)

    def get_next_pending(self):
        """Map to get_next_task()."""
        task = self._core.get_next_task()
        return _TaskWrapper(task) if task else None

    def get_stats(self) -> Dict[str, Any]:
        """Map to get_metrics()."""
        metrics = self._core.get_metrics()
        # Normalize to expected format
        return {
            "total": metrics.get("total_tasks", 0),
            "pending": metrics.get("pending", 0),
            "in_progress": metrics.get("in_progress", 0),
            "completed": metrics.get("completed", 0),
            "failed": metrics.get("failed", 0),
            "blocked": metrics.get("blocked", 0),
        }

    def update_status(self, task_id: str, status: TaskStatus):
        """Map to update_task()."""
        self._core.update_task(task_id, status=status)

    def get_all_tasks(self) -> List:
        """Map to list_tasks()."""
        tasks = self._core.list_tasks()
        return [_TaskWrapper(t) for t in tasks]

    def get_task(self, task_id: str):
        """Direct delegation."""
        task = self._core.get_task(task_id)
        return _TaskWrapper(task) if task else None


class _TaskWrapper:
    """Wraps Core Task to provide plugin-expected attributes."""

    def __init__(self, core_task):
        self._task = core_task

    def __getattr__(self, name):
        if self._task is None:
            return None
        return getattr(self._task, name, None)

    @property
    def type(self):
        """Core uses metadata, plugin expects .type"""
        if self._task is None:
            return "general"
        return getattr(self._task, "type", None) or self._task.metadata.get("type", "general")


class NullTaskManager:
    """
    Noop fallback when TaskProtocol is not in ServiceRegistry.

    Allows manifestation to work with empty data instead of crashing.
    """

    def add_task(self, title: str, description: str = "", type: str = "general", metadata: Dict = None):
        """Noop - return None."""
        return None

    def get_next_pending(self):
        """No tasks."""
        return None

    def get_stats(self) -> Dict[str, Any]:
        """Return zero stats."""
        return {"total": 0, "pending": 0, "in_progress": 0, "completed": 0, "failed": 0, "blocked": 0}

    def update_status(self, task_id: str, status: TaskStatus):
        """Noop."""
        pass

    def get_all_tasks(self) -> List:
        """Empty list."""
        return []

    def get_task(self, task_id: str):
        """No task."""
        return None


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

# OPUS-125: Reflex Arc - DisharmonyDetector integration
try:
    from vibe_core.plugins.opus_assistant.manas.disharmony_detector import (
        DisharmonyDetector,
        DisharmonyFinding,
    )

    DISHARMONY_DETECTOR_AVAILABLE = True
except ImportError:
    DISHARMONY_DETECTOR_AVAILABLE = False
    logger.debug("DisharmonyDetector not available - no reflex arc")

# OPUS-126: Karma Loop - Lineage integration for reflex events
try:
    from vibe_core.lineage import LineageChain, LineageEventType

    LINEAGE_AVAILABLE = True
except ImportError:
    LINEAGE_AVAILABLE = False
    logger.debug("LineageChain not available - reflex events won't be recorded")


class TaskManagerPlugin(KernelPlugin):
    """
    OPUS-213: Stateless Task Ingestor.

    Delegates all state to Core TaskManager via ServiceRegistry.
    Uses CoreManagerAdapter to bridge API differences.
    """

    def __init__(self):
        super().__init__()
        # OPUS-213: No local state. Manager is fetched on-demand from ServiceRegistry.
        self._manager = None
        logger.info("✅ TaskManagerPlugin initialized (Stateless Mode)")

    @property
    def manager(self):
        """Lazy-load manager from ServiceRegistry with adapter."""
        if self._manager is None:
            core = ServiceRegistry.get(TaskProtocol)
            if core:
                self._manager = CoreManagerAdapter(core)
            else:
                logger.warning("⚠️ TaskProtocol not in ServiceRegistry - using NullTaskManager")
                # Fallback: Use NullTaskManager (noop) when Core not available
                self._manager = NullTaskManager()
        return self._manager

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

    def on_pulse(self, kernel: "KernelProtocol", transaction) -> HookResult:
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
            # OPUS-213: Get manager (triggers lazy load from ServiceRegistry)
            manager = self.manager
            if manager is None:
                logger.error("❌ No TaskManager available")
                return HookResult.error("No TaskManager available")

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

        # OPUS-125: Phase 3: Reflex Arc - Check for disharmony (pain sensors)
        reflex_count = self._check_disharmony(project_root)

        total = inbox_count + markdown_count + reflex_count
        if total > 0:
            msg = f"Ingested {total} tasks ({inbox_count} inbox, {markdown_count} markdown, {reflex_count} reflex)"
            logger.info(f"⚙️ SENSORS: {msg}")
            return HookResult.ok(
                data={
                    "ingested": total,
                    "inbox": inbox_count,
                    "markdown": markdown_count,
                    "reflex": reflex_count,
                    "phase": "sensors",
                }
            )
        else:
            logger.debug("⚙️ SENSORS: No new tasks to ingest")
            return HookResult.ok(data={"ingested": 0, "phase": "sensors"})

    def _handle_actuators(self, kernel: "KernelProtocol", project_root: Path) -> HookResult:
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

    # =========================================================================
    # OPUS-125: REFLEX ARC - Autonomous Self-Healing
    # =========================================================================
    # "Schmerz → Aufgabe → Aktion" (Pain → Task → Action)
    #
    # The Reflex Arc connects pain sensors (DisharmonyDetector) to effectors
    # (TaskManager) WITHOUT requiring conscious thought (human intervention).
    # This is the autonomic nervous system of the codebase.
    # =========================================================================

    def _check_disharmony(self, project_root: Path) -> int:
        """
        OPUS-125: Reflex Arc - Scan for disharmony and create repair tasks.
        OPUS-126: Karma Loop - Record reflex events in lineage chain.

        This is the spinal cord - it receives pain signals (disharmony findings)
        and automatically creates tasks to address them. No brain (human) needed.

        The Karma Loop (Samskara) records each reflex action in the lineage chain,
        enabling chronic pain detection and historical analysis.

        Args:
            project_root: Workspace path

        Returns:
            Number of repair tasks created
        """
        if not DISHARMONY_DETECTOR_AVAILABLE:
            return 0

        try:
            detector = DisharmonyDetector(project_root)

            # Only react to HIGH and CRITICAL disharmony (real pain, not minor discomfort)
            report = detector.scan_all(min_severity="high")

            if report.is_harmonious:
                logger.debug("🧘 REFLEX ARC: System is harmonious")
                return 0

            logger.info(f"⚡ REFLEX ARC: Detected {report.total_findings} disharmony findings")

            # OPUS-126: Initialize lineage chain for event recording
            lineage = None
            if LINEAGE_AVAILABLE:
                try:
                    lineage = LineageChain()
                except Exception as e:
                    logger.warning(f"⚠️ KARMA LOOP: Could not initialize lineage: {e}")

            created = 0
            for finding in report.findings:
                # Check for existing task (avoid duplicate reflex responses)
                task_title = self._finding_to_title(finding)
                existing = [t for t in self.manager.get_all_tasks() if t.title == task_title]
                if existing:
                    logger.debug(f"   ↩️ Skipping (already exists): {task_title}")
                    continue

                # Create repair task
                try:
                    task = self.manager.add_task(
                        title=task_title,
                        description=self._finding_to_description(finding),
                        type="disharmony_repair",
                        metadata={
                            "source": "reflex_arc",
                            "severity": finding.severity,
                            "path": finding.path,
                            "location_varga": finding.location_varga.name,
                            "content_varga": finding.content_varga.name,
                            "varga_distance": finding.varga_distance,
                            "evidence": finding.evidence,
                        },
                    )
                    logger.info(f"   🩹 REFLEX: {task.title} (ID: {task.id})")
                    created += 1

                    # OPUS-126: Record reflex action in lineage chain (Karma Loop)
                    if lineage:
                        try:
                            lineage.add_block(
                                event_type=LineageEventType.REPAIR_TASK_CREATED,
                                agent_id="plugin.task_manager.reflex_arc",
                                data={
                                    "task_id": task.id,
                                    "task_title": task_title,
                                    "severity": finding.severity,
                                    "path": finding.path,
                                    "location_varga": finding.location_varga.name,
                                    "content_varga": finding.content_varga.name,
                                    "varga_distance": finding.varga_distance,
                                    "samskara": "reflex_arc",  # Karmic imprint type
                                },
                            )
                            logger.debug(f"   📜 KARMA: Recorded reflex action for {task.id}")
                        except Exception as e:
                            logger.warning(f"   ⚠️ KARMA: Failed to record event: {e}")

                except Exception as e:
                    logger.warning(f"   ⚠️ Failed to create repair task: {e}")

            if created > 0:
                logger.info(f"🔥 REFLEX ARC: Created {created} repair tasks")

                # OPUS-126: Record summary REFLEX_ACTION event
                if lineage:
                    try:
                        lineage.add_block(
                            event_type=LineageEventType.REFLEX_ACTION,
                            agent_id="plugin.task_manager.reflex_arc",
                            data={
                                "total_findings": report.total_findings,
                                "tasks_created": created,
                                "min_severity": "high",
                                "workspace": str(project_root),
                            },
                        )
                        logger.info(f"📜 KARMA LOOP: Recorded {created} reflex actions in lineage")
                    except Exception as e:
                        logger.warning(f"⚠️ KARMA: Failed to record summary: {e}")

            return created

        except Exception as e:
            logger.warning(f"⚠️ REFLEX ARC scan failed: {e}")
            return 0

    def _finding_to_title(self, finding: "DisharmonyFinding") -> str:
        """Convert a DisharmonyFinding to a task title."""
        # Extract filename from path
        filename = Path(finding.path).name
        return f"[{finding.severity.upper()}] Repair disharmony: {filename}"

    def _finding_to_description(self, finding: "DisharmonyFinding") -> str:
        """Convert a DisharmonyFinding to a task description."""
        return f"""DISHARMONY DETECTED (Auto-generated by Reflex Arc)

Path: {finding.path}
Severity: {finding.severity.upper()}
Varga Distance: {finding.varga_distance}

Location: {finding.location_layer} (where file is)
Content: {finding.content_layer} (what file does)

Description:
{finding.description}

Recommendation:
{finding.recommendation}

Evidence:
{chr(10).join(f"  - {e}" for e in finding.evidence)}
"""

    # =========================================================================
    # OPUS-307 Phase II: CLI Command Handlers
    # "steward tasks" namespace - visibility into task queue
    # =========================================================================

    def cmd_tasks_list(self, status: Optional[str] = None, json: bool = False) -> Dict[str, Any]:
        """
        CLI Handler: steward tasks:list

        List all tasks, optionally filtered by status.

        Args:
            status: Filter by status (pending, in_progress, completed, failed)
            json: If True, return raw JSON-compatible data

        Returns:
            Dict with task listing
        """
        all_tasks = self.manager.get_all_tasks()

        # Filter by status if specified
        if status:
            status_upper = status.upper()
            try:
                target_status = TaskStatus[status_upper]
                all_tasks = [t for t in all_tasks if t.status == target_status]
            except KeyError:
                return {"success": False, "error": f"Unknown status: {status}"}

        tasks_data = []
        for t in all_tasks:
            tasks_data.append(
                {
                    "id": t.id,
                    "title": t.title,
                    "status": t.status.value if hasattr(t.status, "value") else str(t.status),
                    "type": getattr(t, "type", "general"),
                }
            )

        result = {
            "success": True,
            "count": len(tasks_data),
            "filter": status,
            "tasks": tasks_data,
        }

        if not json:
            lines = [f"📋 TASKS ({len(tasks_data)} total" + (f", filter: {status}" if status else "") + ")"]
            lines.append("=" * 60)
            status_icons = {
                "pending": "⏳",
                "in_progress": "🔄",
                "completed": "✅",
                "failed": "❌",
                "blocked": "🚫",
            }
            for t in tasks_data:
                icon = status_icons.get(t["status"], "❓")
                lines.append(f"  {icon} [{t['id'][:8]}] {t['title'][:40]}")
            lines.append("=" * 60)
            result["formatted"] = "\n".join(lines)

        return result

    def cmd_tasks_stats(self) -> Dict[str, Any]:
        """
        CLI Handler: steward tasks:stats

        Show task queue statistics.

        Returns:
            Dict with stats
        """
        stats = self.manager.get_stats()

        result = {
            "success": True,
            "stats": stats,
        }

        lines = ["📊 TASK QUEUE STATISTICS"]
        lines.append("=" * 40)
        lines.append(f"  Total:       {stats.get('total', 0)}")
        lines.append(f"  ⏳ Pending:    {stats.get('pending', 0)}")
        lines.append(f"  🔄 In Progress: {stats.get('in_progress', 0)}")
        lines.append(f"  ✅ Completed:  {stats.get('completed', 0)}")
        lines.append(f"  ❌ Failed:     {stats.get('failed', 0)}")
        lines.append(f"  🚫 Blocked:    {stats.get('blocked', 0)}")
        lines.append("=" * 40)
        result["formatted"] = "\n".join(lines)

        return result

    # =========================================================================
    # OPUS-308: Manifestation Protocol
    # "The Paper is the Truth" - TASKS.md is manifested by this plugin
    # =========================================================================

    def get_manifestation_data(self) -> Dict[str, Any]:
        """
        OPUS-308: Return data for TASKS.md manifestation.

        Maps to config_bidirectional schema sections:
        - current: Active tasks summary
        - available: Task queue metrics
        - history: Recently completed tasks
        """
        stats = self.manager.get_stats()
        all_tasks = self.manager.get_all_tasks()

        # Current - active tasks
        active = [t for t in all_tasks if t.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS)]
        current = []
        for t in active[:10]:
            status_icon = "🔄" if t.status == TaskStatus.IN_PROGRESS else "⏳"
            current.append(
                {
                    "Task": f"{status_icon} {t.title[:40]}",
                    "Status": t.status.value if hasattr(t.status, "value") else str(t.status),
                    "Type": getattr(t, "type", "general"),
                }
            )
        if not current:
            current = [{"Task": "_No active tasks_", "Status": "-", "Type": "-"}]

        # Available - queue metrics
        available = {
            "Total Tasks": stats.get("total", 0),
            "Pending": stats.get("pending", 0),
            "In Progress": stats.get("in_progress", 0),
            "Completed": stats.get("completed", 0),
            "Failed": stats.get("failed", 0),
            "Blocked": stats.get("blocked", 0),
        }

        # History - recently completed
        completed = [t for t in all_tasks if t.status == TaskStatus.COMPLETED]
        completed.sort(key=lambda x: getattr(x, "updated_at", ""), reverse=True)
        history = []
        for t in completed[:10]:
            history.append(
                {
                    "Task": f"✅ {t.title[:35]}",
                    "Completed": str(getattr(t, "updated_at", ""))[:16],
                }
            )
        if not history:
            history = [{"Task": "_No completed tasks_", "Completed": "-"}]

        return {
            "current": current,
            "available": available,
            "history": history,
        }

    def cmd_tasks_next(self) -> Dict[str, Any]:
        """
        CLI Handler: steward tasks:next

        Show the next pending task.

        Returns:
            Dict with next task info
        """
        next_task = self.manager.get_next_pending()

        if not next_task:
            return {
                "success": True,
                "message": "No pending tasks",
                "formatted": "📋 No pending tasks in queue",
            }

        result = {
            "success": True,
            "task": {
                "id": next_task.id,
                "title": next_task.title,
                "description": getattr(next_task, "description", ""),
                "type": getattr(next_task, "type", "general"),
                "status": next_task.status.value if hasattr(next_task.status, "value") else str(next_task.status),
            },
        }

        lines = ["📋 NEXT PENDING TASK"]
        lines.append("=" * 60)
        lines.append(f"  ID:          {next_task.id}")
        lines.append(f"  Title:       {next_task.title}")
        lines.append(f"  Type:        {getattr(next_task, 'type', 'general')}")
        desc = getattr(next_task, "description", "")
        if desc:
            lines.append(f"  Description: {desc[:50]}...")
        lines.append("=" * 60)
        result["formatted"] = "\n".join(lines)

        return result
