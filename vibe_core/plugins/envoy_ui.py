from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List

from vibe_core.doc_renderer import DocRenderer, EnvoyRenderState
from vibe_core.envoy_sync import EnvoySync, EnvoySyncState
from vibe_core.plugin_protocol import KernelPlugin

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.scheduling import Task


class EnvoyUIPlugin(KernelPlugin):
    """
    Plugin for ENVOY.md synchronization.
    Handles the Terminal Interface.
    """

    @property
    def plugin_id(self) -> str:
        return "envoy_ui"

    @property
    def priority(self) -> int:
        return 60  # After settings

    def __init__(self):
        self.sync = EnvoySync()
        self.last_modified = 0.0
        self.pending_tasks: Dict[str, Dict[str, Any]] = {}
        self.request_history: List[Dict[str, Any]] = []
        self.doc_renderer = DocRenderer()

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        pass

    def on_tick_pre(self, kernel: "RealVibeKernel") -> None:
        """Check for changes in ENVOY.md and dispatch tasks."""
        if self.sync.check_file_changed(self.last_modified):
            state = EnvoySyncState(
                last_modified=self.last_modified,
                writing=False,
                pending_tasks=self.pending_tasks,
                request_history=self.request_history,
            )

            result = self.sync.sync_to_reality(
                state,
                router_callback=kernel._playbook_router.route,
                submit_callback=kernel.scheduler.submit_task,
                task_factory=lambda payload: self._create_task(payload),
            )

            if result.new_mtime > 0:
                self.last_modified = result.new_mtime

            self.pending_tasks.update(result.pending_tasks)

    def on_tick_post(self, kernel: "RealVibeKernel") -> None:
        """Render ENVOY.md."""
        snapshot = self._generate_snapshot(kernel)

        state = EnvoyRenderState(
            pending_tasks=self.pending_tasks,
            request_history=self.request_history,
            available_routes=kernel._playbook_router.list_available_routes(),
            extract_request_fn=lambda p: self.sync.extract_request_content(),
        )
        self.doc_renderer.render_envoy(snapshot, state)

    def on_task_completed(self, kernel: "RealVibeKernel", task_id: str, result: Any) -> None:
        """Update task status in ENVOY.md."""
        self.sync.update_task_status(
            task_id,
            "COMPLETED",
            str(result) if result else "Task completed successfully",
            self.pending_tasks,
            self.request_history,
        )

    def on_task_failed(self, kernel: "RealVibeKernel", task_id: str, error: str) -> None:
        """Update task status in ENVOY.md."""
        self.sync.update_task_status(task_id, "FAILED", str(error), self.pending_tasks, self.request_history)

    def _create_task(self, task_data: Dict[str, Any]) -> "Task":
        """Helper to create Task object."""
        from vibe_core.scheduling import Task

        return Task(**task_data)

    def _generate_snapshot(self, kernel: "RealVibeKernel") -> Dict[str, Any]:
        """Generate kernel snapshot for rendering."""
        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "kernel_status": kernel.status.value,
            "agents": {},
            "scheduler": kernel.scheduler.get_queue_status(),
            "ledger_stats": {
                "total_events": len(kernel.ledger.get_all_events()),
            },
        }

        for agent_id, agent in kernel.agent_registry.items():
            try:
                agent_status = agent.report_status() if hasattr(agent, "report_status") else {}
                if agent_id in kernel._paused_agents:
                    agent_status["status"] = "PAUSED"
                snapshot["agents"][agent_id] = agent_status
            except Exception:
                snapshot["agents"][agent_id] = {"error": "Failed to get status"}

        return snapshot
