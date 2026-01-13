"""
MarkdownUIManager - Central Coordination for Markdown Interfaces
================================================================

Extracts UI coordination logic from Kernel.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xf5b258ab"  # GenesisByte: parampara % 37 == 0

import logging
from typing import TYPE_CHECKING, Any, Dict, Set

from .doc_renderer import DocRenderer
from .envoy_sync import EnvoySync, EnvoySyncState
from .settings_sync import SettingsSync, SettingsSyncState

if TYPE_CHECKING:
    from .kernel_impl import RealVibeKernel

logger = logging.getLogger(__name__)


class MarkdownUIManager:
    """
    Zentrale Koordination aller Markdown-Interfaces.

    Manages state for:
    - SETTINGS.md (Command Queue)
    - ENVOY.md (Terminal Interface)
    - DocRenderer (Documentation)
    """

    def __init__(self, kernel_ref: "RealVibeKernel"):
        self.kernel = kernel_ref  # Weak reference to Kernel (or direct ref)

        # Sub-components
        self.settings_sync = SettingsSync()
        self.envoy_sync = EnvoySync()
        # Use kernel.io for centralized file writes (atomic + audited)
        self.doc_renderer = DocRenderer(io_service=kernel_ref.io)

        # Settings Executor (for side effects like RESTART/REFRESH)
        from .settings_executor import get_executor

        self.settings_executor = get_executor()

        # STATE MOVED FROM KERNEL:
        # Settings State
        self.settings_last_modified = 0.0
        self.settings_writing = False
        self.paused_agents: Set[str] = set()
        # Execution history needs to be maintained here
        self.settings_execution_history: list = []

        # Envoy State
        self.envoy_last_modified = 0.0
        self.envoy_writing = False
        self.envoy_pending_tasks: Dict[str, Dict[str, Any]] = {}
        self.envoy_request_history: list = []

    def sync_all(self) -> None:
        """
        Called by kernel.tick() - Single entry point for UI sync.
        """
        self._sync_settings()
        self._sync_envoy()

    def _sync_settings(self) -> None:
        """Synchronize SETTINGS.md"""
        # 1. Check for changes
        if not self.settings_writing and self.settings_sync.check_file_changed(self.settings_last_modified):
            # Prepare state
            state = SettingsSyncState(
                last_modified=self.settings_last_modified,
                writing=self.settings_writing,
                paused_agents=self.paused_agents,
                agent_ids=set(self.kernel.agent_registry.keys()),
                execution_history=list(self.settings_execution_history),
            )

            # Execute Sync
            result = self.settings_sync.sync_to_reality(state, ledger_callback=self.kernel.record_verified_event)

            # Update State
            if result.new_mtime > 0:
                self.settings_last_modified = result.new_mtime

            self.paused_agents = result.paused_agents
            self.settings_execution_history.extend(result.history_entries)

            # Execute side effects (RESTART, REFRESH, verbose)
            # Delegated to SettingsExecutor
            self.settings_executor.execute(result, self.kernel)

    def _sync_envoy(self) -> None:
        """Synchronize ENVOY.md"""
        # 1. Check for changes
        if self.envoy_sync.check_file_changed(self.envoy_last_modified):
            # Prepare state
            state = EnvoySyncState(
                last_modified=self.envoy_last_modified,
                writing=self.envoy_writing,
                pending_tasks=self.envoy_pending_tasks,
                request_history=list(self.kernel._envoy_request_history)
                if hasattr(self.kernel, "_envoy_request_history")
                else [],
            )

            # Execute Sync
            result = self.envoy_sync.sync_to_reality(
                state,
                router_callback=self.kernel._playbook_router.route,
                submit_callback=self.kernel.scheduler.submit_task,
                task_factory=lambda payload: self._create_envoy_task(payload),
            )

            # Update State
            if result.new_mtime > 0:
                self.envoy_last_modified = result.new_mtime

            self.envoy_pending_tasks.update(result.pending_tasks)

            # Update history in kernel (if we want to keep it there for now, or move it here fully)
            # For now, let's assume we might need to sync back history if it's used elsewhere
            # But ideally, history should live here.
            # Let's keep history in kernel for now to minimize breakage, or move it.
            # The plan said "Hat ALLEN State", so we should move history here too.

    def _create_envoy_task(self, task_data: Dict[str, Any]) -> Any:
        """Helper to create Task object (avoiding circular imports if possible)"""
        from vibe_core.scheduling import Task

        return Task(**task_data)

    def update_envoy_task_status(self, task_id: str, status: str, response: str) -> None:
        """
        Called by Kernel when an Envoy task completes.
        """
        # We need to maintain history here if we move it here.
        if not hasattr(self, "envoy_request_history"):
            self.envoy_request_history = []

        self.envoy_sync.update_task_status(
            task_id, status, response, self.envoy_pending_tasks, self.envoy_request_history
        )

    def render_all(self, snapshot: Dict[str, Any]) -> None:
        """
        Render all markdown files (OPERATIONS.md, SETTINGS.md, ENVOY.md).
        Called by kernel._pulse().
        """
        # 1. Render OPERATIONS.md
        self.doc_renderer.render_operations(snapshot)

        # 2. Render SETTINGS.md
        self.settings_writing = True
        try:
            from .doc_renderer import SettingsRenderState

            # Ensure execution history exists
            if not hasattr(self, "settings_execution_history"):
                self.settings_execution_history = []

            settings_state = SettingsRenderState(
                ledger_path=str(self.kernel.ledger_path),
                varna_registry=self.kernel._varna_registry,
                ashrama_registry=self.kernel._ashrama_registry,
                execution_history=list(self.settings_execution_history),
            )

            new_mtime = self.doc_renderer.render_settings(snapshot, settings_state)
            if new_mtime:
                self.settings_last_modified = new_mtime
        finally:
            self.settings_writing = False

        # 3. Render ENVOY.md
        self.envoy_writing = True
        try:
            from .doc_renderer import EnvoyRenderState

            # Ensure request history exists
            if not hasattr(self, "envoy_request_history"):
                self.envoy_request_history = []

            envoy_state = EnvoyRenderState(
                pending_tasks=self.envoy_pending_tasks,
                request_history=list(self.envoy_request_history),
                available_routes=self.kernel._playbook_router.list_available_routes(),
                extract_request_fn=lambda p: self.envoy_sync.extract_request_content(),
            )
            self.doc_renderer.render_envoy(snapshot, envoy_state)
        finally:
            self.envoy_writing = False
