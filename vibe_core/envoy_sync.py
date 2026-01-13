#!/usr/bin/env python3
"""
EnvoySync - Bidirectional ENVOY.md Terminal Interface

EXTRACTED FROM kernel_impl.py to reduce kernel complexity.

Implements the Async Dispatch pattern:
1. User writes request in ENVOY.md "Request" section
2. Kernel parses request on next tick (fast mtime check)
3. PlaybookRouter routes request (pattern match, no LLM)
4. Task queued to scheduler (non-blocking)
5. Request cleared, status updated in ENVOY.md
6. Task executes async, result written to Response History

This module handles the ENVOY.md bidirectional interface:
- User → ENVOY.md → Kernel (request dispatch)
- Kernel → ENVOY.md → User (status updates)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x104cbff7"  # GenesisByte: parampara % 37 == 0

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.io_service import KernelIOService

logger = logging.getLogger(__name__)


@dataclass
class EnvoySyncState:
    """
    State container for envoy synchronization.

    Passed from kernel to EnvoySync methods.
    """

    last_modified: float = 0.0
    writing: bool = False
    pending_tasks: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    request_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class EnvoySyncResult:
    """Result of envoy synchronization."""

    new_mtime: float = 0.0
    requests_dispatched: int = 0
    failed_dispatches: int = 0
    pending_tasks: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    history_entries: List[Dict[str, Any]] = field(default_factory=list)


class EnvoySync:
    """
    ENVOY.md bidirectional terminal interface.

    Usage in kernel:
        sync = EnvoySync()

        # In tick loop:
        if sync.check_file_changed(state.last_modified):
            result = sync.sync_to_reality(
                state,
                router=playbook_router,
                submit_task=scheduler.submit_task,
            )
            state.last_modified = result.new_mtime
            state.pending_tasks.update(result.pending_tasks)
    """

    def __init__(self, envoy_path: Path = Path("ENVOY.md"), io_service: Optional["KernelIOService"] = None):
        """
        Initialize sync with path to ENVOY.md.

        Args:
            envoy_path: Path to ENVOY.md file
            io_service: Optional KernelIOService for audited writes
        """
        self.envoy_path = envoy_path
        self._io_service = io_service

    def render_document(self, content: str) -> bool:
        """
        Render the document content.

        Preserves user sections via I/O Service (BIDIRECTIONAL mode).
        """
        return self._write_envoy(content)

    def _write_envoy(self, content: str) -> bool:
        """
        Write envoy content through I/O Service or fallback.

        BIDIRECTIONAL doc type preserves user sections.

        Returns:
            True if write succeeded, False otherwise
        """
        if self._io_service:
            from vibe_core.io_service import DocumentType

            result = self._io_service.write_document(
                name=str(self.envoy_path),
                content=content,
                doc_type=DocumentType.BIDIRECTIONAL,
                writer_id="ENVOY_SYNC",
                add_header=False,  # ENVOY.md has its own format
            )
            if not result.success:
                logger.error(f"❌ I/O Service write failed: {result.error}")
                return False
            return True
        else:
            # Fallback: direct write for standalone/test mode (no kernel)
            try:
                self.envoy_path.write_text(content, encoding="utf-8")  # Fallback: standalone mode
                return True
            except Exception as e:
                logger.error(f"❌ Direct write failed: {e}")
                return False

    def check_file_changed(self, last_modified: float) -> bool:
        """
        Check if ENVOY.md has been modified since last read.

        Fast mtime check - suitable for tick loop.

        Args:
            last_modified: Previous mtime to compare against

        Returns:
            True if file changed, False otherwise
        """
        try:
            if not self.envoy_path.exists():
                return False

            current_mtime = self.envoy_path.stat().st_mtime

            if current_mtime > last_modified:
                logger.debug(f"📬 ENVOY.md changed (mtime: {current_mtime})")
                return True

            return False

        except Exception as e:
            logger.error(f"❌ Failed to check ENVOY.md: {e}")
            return False

    def extract_request_content(self) -> str:
        """
        Extract user's request content from ENVOY.md Request section.

        Preserves user content, strips boilerplate/placeholders.

        Returns:
            Raw request text (may be multiline)
        """
        try:
            if not self.envoy_path.exists():
                return ""

            content = self.envoy_path.read_text()
            in_request_section = False
            request_lines = []

            for line in content.split("\n"):
                # Detect section boundaries
                if "## 💬 Request" in line:
                    in_request_section = True
                    continue

                if in_request_section and line.strip().startswith("##"):
                    break

                # Filter boilerplate
                if in_request_section:
                    stripped = line.strip()
                    if stripped.startswith(">"):  # Instructions
                        continue
                    if stripped.startswith("_") and stripped.endswith("_"):  # Placeholders
                        continue
                    if stripped == "---":  # Separators
                        continue
                    if stripped:
                        request_lines.append(line)

            result = "\n".join(request_lines)
            return result

        except Exception as e:
            logger.error(f"❌ Failed to extract request content: {e}")
            return ""

    def parse_requests(self) -> List[str]:
        """
        Parse pending requests from ENVOY.md.

        Returns:
            List of request strings (one per line, non-empty)
        """
        try:
            content = self.extract_request_content()
            if not content.strip():
                return []

            # Split into individual requests
            requests = [line.strip() for line in content.split("\n") if line.strip()]
            return requests

        except Exception as e:
            logger.error(f"❌ Failed to parse ENVOY.md requests: {e}")
            return []

    def dispatch_request(
        self,
        request: str,
        router_callback: Callable[[str, Dict], Any],
        submit_callback: Callable[[Any], str],
        task_factory: Callable[[Dict], Any],
    ) -> Dict[str, Any]:
        """
        Route and dispatch a single user request.

        Async dispatch pattern:
        1. Route via PlaybookRouter (fast pattern match)
        2. Create Task object
        3. Submit to scheduler (non-blocking)
        4. Return metadata

        Args:
            request: The user's natural language request
            router_callback: Router.route(request, context) -> route object
            submit_callback: Scheduler.submit_task(task) -> task_id
            task_factory: Factory to create Task from payload dict

        Returns:
            Dict with task_id, status, route info
        """
        try:
            # Route the request (no LLM - pattern matching only)
            context = {
                "session": {"phase": "CODING"},
                "git": {"uncommitted": 0},
                "tests": {"failing_count": 0},
            }
            route = router_callback(request, context)

            # Handle both dict and PlaybookRoute object responses
            if isinstance(route, dict):
                # dict response (from kernel.envoy.route or provider.route)
                task_name = route.get("task", route.get("rule_name", "unknown"))
                description = route.get("description", route.get("intent_type", "CHAT"))
                confidence = route.get("confidence", "contextual")
                source = route.get("source", route.get("agent", "envoy"))
            else:
                # PlaybookRoute object (from PlaybookRouter.route)
                task_name = route.task
                description = route.description
                confidence = route.confidence
                source = route.source

            logger.info(f"📬 Request routed: '{request[:30]}...' → {task_name} ({confidence})")

            # Create task
            task = task_factory(
                {
                    "agent_id": "envoy",
                    "payload": {
                        "type": "envoy_request",
                        "request": request,
                        "route": task_name,
                        "description": description,
                        "confidence": confidence,
                        "source": source,
                    },
                    "priority": 1 if confidence == "explicit" else 0,
                }
            )

            # Submit to scheduler (NON-BLOCKING)
            # Submit to scheduler (NON-BLOCKING)
            task_id = submit_callback(task)

            logger.info(f"📬 Task queued: {task_id} for route '{task_name}'")

            return {
                "task_id": task_id,
                "status": "QUEUED",
                "request": request,
                "route": task_name,
                "description": description,
                "confidence": confidence,
                "timestamp": datetime.utcnow().strftime("%H:%M:%S UTC"),
            }

        except Exception as e:
            logger.error(f"❌ Failed to dispatch request: {e}")
            return {
                "task_id": None,
                "status": "FAILED",
                "request": request,
                "error": str(e),
                "timestamp": datetime.utcnow().strftime("%H:%M:%S UTC"),
            }

    def clear_requests(self) -> None:
        """
        Clear processed requests from ENVOY.md Request section.

        Preserves section structure and instructions.
        """
        try:
            if not self.envoy_path.exists():
                return

            content = self.envoy_path.read_text()
            lines = content.split("\n")

            new_lines = []
            in_request_section = False

            for line in lines:
                # Detect section boundaries
                if "## 💬 Request" in line:
                    in_request_section = True
                    new_lines.append(line)
                    continue

                if in_request_section and line.strip().startswith("##"):
                    in_request_section = False

                # In request section: keep only boilerplate
                if in_request_section:
                    stripped = line.strip()
                    # Keep instructions and empty lines
                    if stripped.startswith(">") or not stripped:
                        new_lines.append(line)
                    continue

                new_lines.append(line)

            content = "\n".join(new_lines)
            if not self._write_envoy(content):
                logger.error("❌ Failed to write ENVOY.md after request cleanup")
            else:
                logger.debug("📬 Cleared processed requests from ENVOY.md")

        except Exception as e:
            logger.error(f"❌ Failed to clear ENVOY.md requests: {e}")

    def update_task_status(
        self,
        task_id: str,
        status: str,
        response: str,
        pending_tasks: Dict[str, Dict[str, Any]],
        history: List[Dict[str, Any]],
    ) -> None:
        """
        Update a task's status when it completes.

        Moves task from pending_tasks to history.

        Args:
            task_id: The task ID to update
            status: New status (COMPLETED, FAILED)
            response: Response message
            pending_tasks: Dict of pending tasks (modified in place)
            history: History list (modified in place)
        """
        if task_id not in pending_tasks:
            logger.warning(f"⚠️  Task {task_id} not found in pending tasks")
            return

        task_meta = pending_tasks.pop(task_id)
        task_meta["status"] = status
        task_meta["response"] = response

        history.append(task_meta)
        logger.info(f"📬 Task {task_id} completed: {status}")

    def sync_to_reality(
        self,
        state: EnvoySyncState,
        router_callback: Callable[[str, Dict], Any],
        submit_callback: Callable[[Any], str],
        task_factory: Callable[[Dict], Any],
    ) -> EnvoySyncResult:
        """
        Full sync: Parse → Dispatch → Cleanup.

        Main entry point for kernel tick loop.

        Args:
            state: Current sync state
            router_callback: PlaybookRouter.route method
            submit_callback: Scheduler.submit_task method
            task_factory: Task constructor

        Returns:
            EnvoySyncResult with new mtime and task tracking
        """
        result = EnvoySyncResult(
            pending_tasks=dict(state.pending_tasks),
            history_entries=list(state.request_history),
        )

        try:
            # Parse requests
            requests = self.parse_requests()

            if not requests:
                logger.debug("📬 No pending requests in ENVOY.md")
                return result

            logger.info(f"📬 Processing {len(requests)} request(s) from ENVOY.md")

            # Dispatch each request
            for request in requests:
                dispatch_result = self.dispatch_request(
                    request,
                    router_callback,
                    submit_callback,
                    task_factory,
                )

                task_id = dispatch_result.get("task_id")
                if task_id:
                    result.pending_tasks[task_id] = dispatch_result
                    result.requests_dispatched += 1
                else:
                    result.history_entries.append(dispatch_result)
                    result.failed_dispatches += 1
                    logger.warning(f"📬 Request dispatch failed: {dispatch_result.get('error')}")

            # Clear processed requests
            self.clear_requests()

            # Update mtime
            if self.envoy_path.exists():
                result.new_mtime = self.envoy_path.stat().st_mtime

            logger.info("✅ ENVOY.md requests dispatched to scheduler")

        except Exception as e:
            logger.error(f"❌ ENVOY sync failed: {e}")

        return result
