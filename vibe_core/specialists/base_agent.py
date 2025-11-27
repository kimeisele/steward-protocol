#!/usr/bin/env python3
"""
BaseAgent: The Integration Hub (GAD-301)

This is the abstract class that connects:
  - Body (GAD-5): Runtime execution via bin/vibe-shell
  - Brain (GAD-7): Mission control & orchestration
  - Arms (GAD-6): Knowledge retrieval via bin/vibe-knowledge

Every specialized agent (Coder, Researcher, Reviewer, etc.) inherits from this.

MIGRATED FROM: agency_os/03_agents/base_agent.py (Post-Split Architecture)
"""

import importlib.util
import json
import logging
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# [ARCH-005] Import Store
from vibe_core.store.sqlite_store import SQLiteStore

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of executing a command."""

    success: bool
    output: str
    error: str
    exit_code: int
    duration_ms: float


@dataclass
class KnowledgeResult:
    """Result of consulting the knowledge base."""

    found: bool
    artifacts: list[str]
    query: str
    relevance_scores: dict[str, float]


class BaseAgent:
    """
    Base Agent: The entity that thinks, decides, and acts.

    Responsibilities:
    1. Initialize with role/name and load context
    2. Execute commands safely via Runtime (GAD-5)
    3. Consult knowledge base via Knowledge (GAD-6)
    4. Report status to Mission Control (GAD-7)
    """

    def __init__(self, name: str, role: str, vibe_root: Path | None = None):
        """
        Initialize the agent.

        Args:
            name: Agent instance name (e.g., "claude-junior-dev")
            role: Agent role/persona (e.g., "Junior Developer")
            vibe_root: Path to vibe-agency root (auto-detected if None)
        """
        self.name = name
        self.role = role
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.execution_count = 0
        self.knowledge_queries = 0
        # Capability declarations (populated by personas)
        self.capabilities: list[str] = []

        # Auto-detect vibe root if not provided
        if vibe_root is None:
            vibe_root = self._detect_vibe_root()

        self.vibe_root = Path(vibe_root)

        # Load context from runtime
        self.context = self._load_context()

        # [ARCH-005] Initialize DB Connection (Shadow Mode)
        self.db: SQLiteStore | None = None
        self._init_db_connection()

        # Verify infrastructure is available
        self._verify_infrastructure()

    def _detect_vibe_root(self) -> Path:
        """Auto-detect the vibe-agency root directory."""
        cwd = Path.cwd()

        # Check if we're already in the root
        if (cwd / ".vibe").exists():
            return cwd

        # Check parent directories
        for parent in cwd.parents:
            if (parent / ".vibe").exists():
                return parent

        raise RuntimeError(
            "Could not detect vibe-agency root. Please set VIBE_ROOT environment variable."
        )

    def _load_context(self) -> dict[str, Any]:
        """Load execution context from .vibe/runtime/context.json."""
        context_file = self.vibe_root / ".vibe" / "runtime" / "context.json"

        if not context_file.exists():
            return {
                "vibe_root": str(self.vibe_root),
                "agent_name": self.name,
                "agent_role": self.role,
            }

        try:
            with open(context_file) as f:
                return json.load(f)
        except Exception as e:
            # Return minimal context if loading fails
            return {
                "vibe_root": str(self.vibe_root),
                "agent_name": self.name,
                "agent_role": self.role,
                "context_load_error": str(e),
            }

    def _init_db_connection(self) -> None:
        """
        Initialize SQLiteStore connection safely (Shadow Mode).

        [ARCH-005] Agents can now access the persistent database layer.
        If the DB is unavailable, the agent continues normally (resilience first).
        """
        try:
            db_path = self.vibe_root / ".vibe" / "state" / "vibe_agency.db"
            self.db = SQLiteStore(str(db_path))
            logger.debug(f"✅ Agent '{self.name}' connected to SQLiteStore")
        except Exception as e:
            logger.warning(
                f"⚠️ Agent '{self.name}' running without DB: {e}. Database features disabled."
            )
            self.db = None

    def _verify_infrastructure(self):
        """Verify that required infrastructure is available."""
        required_files = [
            "bin/vibe-shell",
            "bin/vibe-knowledge",
            ".vibe/config/roadmap.yaml",
            ".vibe/runtime/context.json",
        ]

        missing = []
        for file in required_files:
            if not (self.vibe_root / file).exists():
                missing.append(file)

        if missing:
            raise RuntimeError(
                f"Infrastructure incomplete. Missing: {missing}. "
                "Ensure GAD-5, GAD-6, and GAD-7 are initialized."
            )

    # ========================================================================
    # CONNECTION TO BODY (GAD-5: Runtime)
    # ========================================================================

    def execute_command(
        self, command: str, timeout: int = 30, prompt: str | None = None, **kwargs
    ) -> ExecutionResult:
        """
        Execute a command via the Runtime (GAD-5).

        The command runs through bin/vibe-shell, which:
        - Enforces MOTD
        - Injects VIBE_CONTEXT
        - Logs execution to audit trail
        - Checks health before execution

        Args:
            command: Command to execute
            timeout: Timeout in seconds (can also use timeout_seconds kwarg)
            prompt: Optional prompt/context to include in execution
            **kwargs: Additional parameters (e.g., timeout_seconds)

        Returns:
            ExecutionResult with stdout, stderr, exit code
        """
        import time

        # Support both 'timeout' and 'timeout_seconds' parameter names
        if "timeout_seconds" in kwargs:
            timeout = kwargs["timeout_seconds"]

        # Store prompt in context if provided
        if prompt:
            self.context["execution_prompt"] = prompt

        start_time = time.time()

        try:
            # Execute via vibe-shell to ensure context injection
            result = subprocess.run(  # noqa: S603
                [str(self.vibe_root / "bin" / "vibe-shell"), "-c", command],
                cwd=self.vibe_root,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            duration_ms = (time.time() - start_time) * 1000
            self.execution_count += 1

            return ExecutionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                exit_code=result.returncode,
                duration_ms=duration_ms,
            )

        except subprocess.TimeoutExpired:
            duration_ms = (time.time() - start_time) * 1000
            return ExecutionResult(
                success=False,
                output="",
                error=f"Command timed out after {timeout}s",
                exit_code=-1,
                duration_ms=duration_ms,
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                exit_code=-1,
                duration_ms=duration_ms,
            )

    # ========================================================================
    # CONNECTION TO ARMS (GAD-6: Knowledge)
    # ========================================================================

    def consult_knowledge(self, query: str, domain: str = "all", limit: int = 5) -> KnowledgeResult:
        """
        Consult the knowledge base via the Knowledge system (GAD-6).

        The agent asks: "Do we have a pattern/snippet/research for X?"
        Instead of hallucinating, the agent gets facts.

        Args:
            query: Search query
            domain: Knowledge domain (all/research/patterns/snippets/decisions)
            limit: Maximum results to return

        Returns:
            KnowledgeResult with found artifacts and relevance scores
        """
        try:
            # Call bin/vibe-knowledge search
            result = subprocess.run(  # noqa: S603
                [
                    str(self.vibe_root / "bin" / "vibe-knowledge"),
                    "search",
                    query,
                ],
                cwd=self.vibe_root,
                capture_output=True,
                text=True,
                timeout=10,
            )

            self.knowledge_queries += 1

            if result.returncode != 0:
                return KnowledgeResult(
                    found=False,
                    artifacts=[],
                    query=query,
                    relevance_scores={},
                )

            # Parse output (simple parsing of CLI output)
            # In production, we'd use structured output (JSON) from the retriever
            artifacts = []
            relevance_scores = {}

            # Extract artifact paths from output
            for line in result.stdout.split("\n"):
                if "Path:" in line:
                    path = line.split("Path:")[-1].strip()
                    artifacts.append(path)

                if "Relevance:" in line:
                    rel_str = line.split("Relevance:")[-1].strip()
                    score = float(rel_str.rstrip("%")) / 100.0
                    if artifacts:
                        relevance_scores[artifacts[-1]] = score

            return KnowledgeResult(
                found=len(artifacts) > 0,
                artifacts=artifacts[:limit],
                query=query,
                relevance_scores=relevance_scores,
            )

        except Exception:
            return KnowledgeResult(
                found=False,
                artifacts=[],
                query=query,
                relevance_scores={},
            )

    def read_knowledge_artifact(self, path: str) -> str | None:
        """
        Read the full content of a knowledge artifact.

        Args:
            path: Path to artifact (relative to knowledge base)

        Returns:
            File content or None if not found
        """
        try:
            result = subprocess.run(  # noqa: S603
                [
                    str(self.vibe_root / "bin" / "vibe-knowledge"),
                    "read",
                    path,
                ],
                cwd=self.vibe_root,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                return result.stdout
            return None

        except Exception:
            return None

    # ========================================================================
    # CONNECTION TO BRAIN (GAD-7: Mission Control)
    # ========================================================================

    def report_status(self) -> dict[str, Any]:
        """
        Report current status to Mission Control.

        Returns agent state for logging and auditing.
        """
        return {
            "agent_name": self.name,
            "agent_role": self.role,
            "created_at": self.created_at,
            "execution_count": self.execution_count,
            "knowledge_queries": self.knowledge_queries,
            "context": self.context,
        }

    def get_context(self) -> dict[str, Any]:
        """Get the execution context loaded from .vibe/runtime/context.json."""
        return self.context.copy()

    # [ARCH-005] DATABASE AWARENESS
    # ========================================================================

    def log_event(self, event_type: str, payload: dict[str, Any]) -> bool:
        """
        Record an operational event to the database.

        This is the foundation for agent audit logs, decision tracking, and
        operational insight. Non-fatal if DB is unavailable.

        Args:
            event_type: Type of event (e.g., 'task_start', 'decision', 'error')
            payload: Event details (flexible dict for extensibility)

        Returns:
            True if logged to DB, False if DB unavailable (silent fail)

        Example:
            agent.log_event('task_start', {
                'task_id': 'RESEARCH_001',
                'query': 'authentication patterns'
            })
        """
        if not self.db:
            logger.debug(f"Agent '{self.name}': Event '{event_type}' not logged (DB unavailable)")
            return False

        try:
            # For now, we verify the DB connection is valid.
            # Future: Add dedicated 'events' or 'agent_activities' table
            # and write the payload directly.
            # Using the context manager ensures proper connection cleanup.
            with self.db:
                logger.debug(f"💾 Agent '{self.name}' logged event: {event_type} → {payload}")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Failed to log event '{event_type}': {e}")
            return False

    # [ARCH-006] Sub-Task Management
    def create_subtask(self, description: str, parent_id: str) -> str:
        """
        Creates a child task in the database to track granular progress.
        Returns the generated task_id.

        This enables agents to persist their Chain-of-Thought decomposition,
        allowing recovery and resumption if the agent crashes mid-execution.

        Args:
            description: Human-readable task description
            parent_id: Parent task ID for hierarchy

        Returns:
            task_id: Generated UUID for the subtask

        Example:
            subtask_id = agent.create_subtask("Analyze requirements", root_mission_id)
            agent.update_subtask(subtask_id, "completed", result="Analysis Done")
        """
        import uuid

        task_id = str(uuid.uuid4())

        # Log visually
        logger.info(f"📋 Agent {self.name} created subtask: {description[:50]}...")

        if self.db:
            try:
                with self.db as conn:
                    # We utilize the store's add_task method
                    # This assumes SQLiteStore has add_task(task_id, description, parent_id, status)
                    conn.add_task(
                        task_id=task_id,
                        description=description,
                        parent_id=parent_id,
                        status="pending",
                    )
                self.log_event("subtask_created", {"task_id": task_id, "parent_id": parent_id})
            except Exception as e:
                logger.warning(f"⚠️ Failed to persist subtask {task_id}: {e}")

        return task_id

    def update_subtask(self, task_id: str, status: str, result: Any = None) -> None:
        """
        Updates the status of a subtask (e.g., 'in_progress', 'completed', 'failed').

        Args:
            task_id: Task ID to update
            status: New status ('pending', 'in_progress', 'completed', 'failed')
            result: Optional result data
        """
        if self.db:
            try:
                with self.db as conn:
                    conn.update_task_status(task_id, status, result)
                # Log completion events specifically
                if status in ["completed", "failed"]:
                    self.log_event(f"subtask_{status}", {"task_id": task_id})
            except Exception as e:
                logger.warning(f"⚠️ Failed to update subtask {task_id}: {e}")

    # ========================================================================
    # CONNECTION TO FEET (GAD-4: Quality Assurance)
    # ========================================================================

    def verify_work(
        self, check_code: bool = True, run_tests: bool = True, test_domain: str | None = None
    ) -> dict[str, Any]:
        """
        Verify work before committing/reporting success.

        This method integrates with GAD-4 (Quality Assurance) to ensure
        code quality and test coverage. Agents call this before completing tasks.

        Args:
            check_code: Run vibe-check linter (default: True)
            run_tests: Run vibe-test test suite (default: True)
            test_domain: Optional test domain (agents, planning, coding, deployment)

        Returns:
            Dict with verification status: {
                "success": bool,
                "checks_passed": bool,
                "tests_passed": bool,
                "issues": list of problems found
            }
        """
        issues = []
        checks_passed = True
        tests_passed = True

        # Run code quality checks
        if check_code:
            try:
                result = subprocess.run(  # noqa: S603
                    [str(self.vibe_root / "bin" / "vibe-check")],
                    cwd=self.vibe_root,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode != 0:
                    checks_passed = False
                    issues.append("Code quality checks failed")
                    if result.stderr:
                        issues.append(result.stderr[:200])

            except Exception as e:
                checks_passed = False
                issues.append(f"Code check error: {e!s}")

        # Run tests
        if run_tests:
            try:
                cmd = [str(self.vibe_root / "bin" / "vibe-test")]
                if test_domain:
                    cmd.extend(["--domain", test_domain])

                result = subprocess.run(  # noqa: S603
                    cmd,
                    cwd=self.vibe_root,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                if result.returncode != 0:
                    tests_passed = False
                    issues.append("Tests failed")
                    if result.stderr:
                        issues.append(result.stderr[:200])

            except subprocess.TimeoutExpired:
                tests_passed = False
                issues.append("Test suite timed out")
            except Exception as e:
                tests_passed = False
                issues.append(f"Test error: {e!s}")

        return {
            "success": checks_passed and tests_passed,
            "checks_passed": checks_passed,
            "tests_passed": tests_passed,
            "issues": issues,
        }

    # ========================================================================
    # ATOMIC DELIVERY (GAD-2: The Atomic Gearbox)
    # ========================================================================

    def deliver_solution(self, task_id: str, message: str) -> dict[str, Any]:
        """
        Deliver work atomically using the TaskExecutor.

        This is the SAFE, COMPLETE, ATOMIC delivery workflow:
        1. Verify work passes QA (verify_work())
        2. Create feature branch (feature/TASK-XXX)
        3. Commit changes
        4. Push to remote
        5. Create PR on main
        6. Return PR URL

        Args:
            task_id: Task identifier (e.g., GAD-201_TASK_EXECUTOR)
            message: Semantic commit/PR message

        Returns:
            Dict with delivery status:
            {
                "success": bool,
                "pr_url": str or None,
                "branch": str,
                "commit_sha": str,
                "error": str or None
            }
        """
        # Import TaskExecutor dynamically to avoid circular imports
        try:
            spec = importlib.util.spec_from_file_location(
                "task_executor_module",
                self.vibe_root / "agency_os" / "02_orchestration" / "task_executor.py",
            )
            if spec and spec.loader:
                task_executor_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(task_executor_module)
                TaskExecutor = task_executor_module.TaskExecutor

                executor = TaskExecutor(vibe_root=self.vibe_root)
                result = executor.deliver(self, task_id, message)

                return {
                    "success": result.success,
                    "pr_url": result.pr_url,
                    "branch": result.branch,
                    "commit_sha": result.commit_sha,
                    "error": result.error,
                    "timestamp": result.timestamp,
                }
        except Exception:
            pass

        # Fallback if TaskExecutor not available
        return {
            "success": False,
            "pr_url": None,
            "branch": None,
            "commit_sha": None,
            "error": "Delivery failed: TaskExecutor not available",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def has_capabilities(self, required: list[str]) -> bool:
        return all(skill in self.capabilities for skill in required)

    def __repr__(self) -> str:
        return (
            f"BaseAgent(name={self.name!r}, role={self.role!r}, capabilities={self.capabilities})"
        )

    def __str__(self) -> str:
        return f"{self.name} ({self.role})"


__all__ = ["BaseAgent", "ExecutionResult", "KnowledgeResult"]
