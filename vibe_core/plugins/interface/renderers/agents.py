"""
Agents Renderer.
Directly renders AGENTS.md from Kernel Registry.
"""

from typing import Any, Dict

from vibe_core.io_service import DocumentType

from .base import BaseRenderer


class AgentsRenderer(BaseRenderer):
    """
    Directly renders AGENTS.md from the Kernel's Agent Registry.
    """

    @property
    def name(self) -> str:
        return "agents"

    def render(self) -> None:
        """Render AGENTS.md directly from kernel state."""
        # 1. Get Agents from Registry
        # Note: agent_registry is a MappingProxyType, so we can iterate it safely
        agents = self.kernel.agent_registry

        # 2. Generate Content
        content = self._generate_markdown(agents)

        # 3. Write to File via Kernel I/O
        self.kernel.io.write_document(
            name="AGENTS.md",
            content=content,
            doc_type=DocumentType.READONLY,
            writer_id="interface_plugin",
            add_header=True,
        )

    def _generate_markdown(self, agents: Dict[str, Any]) -> str:
        """Generate Markdown content."""
        lines = ["# 👥 AGENT REGISTRY", ""]

        # Statistics
        total_agents = len(agents)
        lines.append(f"**Total Agents:** {total_agents}")
        lines.append("")

        # Table Header
        lines.append("| Agent ID | Name | Domain | Capabilities |")
        lines.append("| :--- | :--- | :--- | :--- |")

        if not agents:
            lines.append("| _No agents registered_ | | | |")
        else:
            # Sort by Agent ID
            for agent_id, agent in sorted(agents.items()):
                name = getattr(agent, "name", agent_id)
                domain = getattr(agent, "domain", "UNKNOWN")
                capabilities = getattr(agent, "capabilities", [])

                # Format capabilities
                caps_str = ", ".join(capabilities) if capabilities else "_"

                lines.append(f"| `{agent_id}` | **{name}** | {domain} | {caps_str} |")

        lines.append("")
        lines.append("> **Note:** This registry is live and updates on every kernel tick.")

        return "\n".join(lines)
