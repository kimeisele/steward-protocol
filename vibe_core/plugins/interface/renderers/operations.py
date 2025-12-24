"""
Operations Renderer.
Renders OPERATIONS.md (Dashboard) via kernel.io.

Architecture Pattern:
- Uses render_sections() from BaseRenderer (config-driven)
- Registers data sources for system health, queue, events
- Fallback to generate_content() if no sections defined
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.io_service import DocumentType

from .base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("RENDERER_OPERATIONS")


class OperationsRenderer(BaseRenderer):
    """Renders OPERATIONS.md dashboard."""

    def __init__(self, kernel: "RealVibeKernel"):
        super().__init__(kernel)
        self._register_data_sources()

    @property
    def name(self) -> str:
        return "operations"

    @property
    def output_file(self) -> str:
        return "OPERATIONS.md"

    @property
    def doc_type(self) -> DocumentType:
        return DocumentType.READONLY

    def render(self) -> None:
        """Render OPERATIONS.md using config-driven sections."""
        config = self.get_config()
        if config and config.sections:
            content = self.render_sections()
            self.merge_and_write(content)
        else:
            content = self.generate_content()
            if content:
                self.merge_and_write(content)

    def _register_data_sources(self) -> None:
        """Register data sources for section-based rendering."""
        self.register_data_source("kernel.health", self._get_kernel_health)
        self.register_data_source("scheduler.queue", self._get_scheduler_queue)
        self.register_data_source("events.recent", self._get_recent_events)

    def _get_kernel_health(self) -> Dict[str, Any]:
        """Get kernel health for system_status section."""
        status = self.kernel.status.value if hasattr(self.kernel, "status") else "UNKNOWN"
        agent_count = len(self.kernel.agent_registry)
        queue_size = 0
        if hasattr(self.kernel, "_scheduler"):
            queue_status = self.kernel._scheduler.get_queue_status()
            queue_size = queue_status.get("queue_length", 0)
        return {
            "status": status,
            "agent_count": agent_count,
            "queue_size": queue_size,
        }

    def _get_scheduler_queue(self) -> List[Dict[str, Any]]:
        """Get scheduler queue for task_queue section."""
        if not hasattr(self.kernel, "_scheduler"):
            return [{"Task": "_No scheduler_", "Status": "-", "Priority": "-"}]
        queue_status = self.kernel._scheduler.get_queue_status()
        tasks = queue_status.get("tasks", [])
        if not tasks:
            return [{"Task": "_Queue empty_", "Status": "-", "Priority": "-"}]
        return [
            {"Task": t.get("id", "?"), "Status": t.get("status", "?"), "Priority": t.get("priority", "?")}
            for t in tasks[:10]
        ]

    def _get_recent_events(self) -> List[Dict[str, Any]]:
        """Get recent events for events section."""
        if not hasattr(self.kernel, "_event_bus"):
            return [{"Type": "_No event bus_", "Agent": "-", "Time": "-"}]
        status = self.kernel._event_bus.get_status()
        type_counts = status.get("type_counts", {})
        if not type_counts:
            return [{"Type": "_No events_", "Count": "-"}]
        return [{"Type": t, "Count": c} for t, c in sorted(type_counts.items(), key=lambda x: -x[1])[:10]]

    def generate_content(self) -> Optional[str]:
        """Fallback content generation if config sections not defined."""
        try:
            lines = ["# OPERATIONS DASHBOARD", ""]

            status = self.kernel.status.value if hasattr(self.kernel, "status") else "UNKNOWN"
            agent_count = len(self.kernel.agent_registry)
            queue_size = 0
            if hasattr(self.kernel, "_scheduler"):
                queue_status = self.kernel._scheduler.get_queue_status()
                queue_size = queue_status.get("queue_length", 0)

            lines.extend(
                [
                    "## Kernel Status",
                    "",
                    f"- **Status:** `{status}`",
                    f"- **Agents Registered:** {agent_count}",
                    f"- **Queue Length:** {queue_size}",
                    "",
                ]
            )

            lines.extend(["## Agent Status", ""])
            if not self.kernel.agent_registry:
                lines.append("_No agents registered_")
            else:
                lines.append("| Agent ID | Name | Domain | Status |")
                lines.append("| :--- | :--- | :--- | :--- |")
                for agent_id, agent in sorted(self.kernel.agent_registry.items()):
                    name = getattr(agent, "name", agent_id)
                    domain = getattr(agent, "domain", "UNKNOWN")
                    lines.append(f"| `{agent_id}` | {name} | {domain} | ACTIVE |")

            lines.extend(["", "---", "*Auto-generated by InterfacePlugin*"])
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error generating OPERATIONS content: {e}")
            return None


def create_renderer(kernel: "RealVibeKernel", config: Dict[str, Any]) -> OperationsRenderer:
    """Factory function for InterfacePlugin."""
    return OperationsRenderer(kernel)
