"""
Agents Renderer.
Renders AGENTS.md from Kernel Registry.

Architecture Pattern:
- Uses render_sections() from BaseRenderer (config-driven)
- Registers data sources for agent data
- Fallback to generate_content() if no sections defined
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.io_service import DocumentType

from .base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol


class AgentsRenderer(BaseRenderer):
    """Renders AGENTS.md from the Kernel's Agent Registry."""

    def __init__(self, kernel: "KernelProtocol"):
        super().__init__(kernel)
        self._register_data_sources()

    @property
    def name(self) -> str:
        return "agents"

    @property
    def output_file(self) -> str:
        return "AGENTS.md"

    @property
    def doc_type(self) -> DocumentType:
        return DocumentType.READONLY

    def render(self) -> None:
        """Render AGENTS.md using config-driven sections."""
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
        self.register_data_source("kernel.status", self._get_kernel_status)
        self.register_data_source("agents.list", self._get_agents_list)
        self.register_data_source("agents.stats", self._get_agents_stats)

    def _get_kernel_status(self) -> Dict[str, Any]:
        """Get kernel status for header section."""
        return {
            "status": self.kernel.status.value if hasattr(self.kernel, "status") else "UNKNOWN",
            "agent_count": len(self.kernel.agent_registry),
        }

    def _get_agents_list(self) -> List[Dict[str, Any]]:
        """Get list of agents for table rendering."""
        agents = []
        for agent_id, agent in sorted(self.kernel.agent_registry.items()):
            capabilities = getattr(agent, "capabilities", [])
            agents.append(
                {
                    "Agent ID": f"`{agent_id}`",
                    "Name": f"**{getattr(agent, 'name', agent_id)}**",
                    "Domain": getattr(agent, "domain", "UNKNOWN"),
                    "Capabilities": ", ".join(capabilities) if capabilities else "_",
                }
            )
        return (
            agents if agents else [{"Agent ID": "_No agents registered_", "Name": "", "Domain": "", "Capabilities": ""}]
        )

    def _get_agents_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        agents = self.kernel.agent_registry
        domains = {}
        for agent in agents.values():
            domain = getattr(agent, "domain", "UNKNOWN")
            domains[domain] = domains.get(domain, 0) + 1
        return {
            "total": len(agents),
            "by_domain": domains,
        }

    def generate_content(self) -> Optional[str]:
        """Fallback content generation if config sections not defined."""
        agents = self.kernel.agent_registry
        lines = ["# 👥 AGENT REGISTRY", ""]

        total_agents = len(agents)
        lines.append(f"**Total Agents:** {total_agents}")
        lines.append("")

        lines.append("| Agent ID | Name | Domain | Capabilities |")
        lines.append("| :--- | :--- | :--- | :--- |")

        if not agents:
            lines.append("| _No agents registered_ | | | |")
        else:
            for agent_id, agent in sorted(agents.items()):
                name = getattr(agent, "name", agent_id)
                domain = getattr(agent, "domain", "UNKNOWN")
                capabilities = getattr(agent, "capabilities", [])
                caps_str = ", ".join(capabilities) if capabilities else "_"
                lines.append(f"| `{agent_id}` | **{name}** | {domain} | {caps_str} |")

        lines.append("")
        lines.append("> **Note:** This registry is live and updates on every kernel tick.")

        return "\n".join(lines)


def create_renderer(kernel: "KernelProtocol", config: Dict[str, Any]) -> AgentsRenderer:
    """Factory function for InterfacePlugin."""
    return AgentsRenderer(kernel)
