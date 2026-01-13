"""
CityMap Renderer.
Directly renders CITYMAP.md from Kernel Topology.

UNIFIED UI: Implements generate_content() pattern.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x60465953"  # GenesisByte: parampara % 37 == 0

from collections import defaultdict
from typing import Any, Dict, List, Optional

from vibe_core.io_service import DocumentType

from .base import BaseRenderer


class CityMapRenderer(BaseRenderer):
    """Directly renders CITYMAP.md from the Kernel's Runtime State."""

    @property
    def name(self) -> str:
        return "citymap"

    @property
    def output_file(self) -> str:
        return "CITYMAP.md"

    @property
    def doc_type(self) -> DocumentType:
        return DocumentType.READONLY

    def generate_content(self) -> Optional[str]:
        """Generate CITYMAP.md content (UNIFIED UI pattern)."""
        agents = self.kernel.agent_registry
        tools = self.kernel.tool_registry.list_tools()

        domains = defaultdict(list)
        for agent_id, agent in agents.items():
            domain = getattr(agent, "domain", "UNKNOWN")
            domains[domain].append(agent)

        return self._generate_markdown(agents, domains, tools)

    def _generate_markdown(self, agents: Dict[str, Any], domains: Dict[str, List[Any]], tools: List[str]) -> str:
        """Generate Markdown content."""
        lines = ["# 🗺️ CITY MAP", ""]

        # System Status
        status = self.kernel.status.value if hasattr(self.kernel, "status") else "UNKNOWN"
        lines.append(f"**System Status:** `{status}`")
        lines.append(f"**Population:** {len(agents)} Agents")
        lines.append(f"**Tools Available:** {len(tools)}")
        lines.append("")

        # Topology Diagram (ASCII)
        lines.append("## 🏔️ Topology")
        lines.append(self._generate_topology_diagram(len(agents)))
        lines.append("")

        # Domain Breakdown
        lines.append("## 🏙️ Districts (Domains)")

        if not domains:
            lines.append("_No active districts_")
        else:
            for domain, domain_agents in sorted(domains.items()):
                lines.append(f"### {domain} ({len(domain_agents)})")
                for agent in sorted(domain_agents, key=lambda a: getattr(a, "name", "")):
                    name = getattr(agent, "name", "Unknown")
                    agent_id = getattr(agent, "agent_id", "unknown")
                    desc = getattr(agent, "description", "")
                    lines.append(f"- **{name}** (`{agent_id}`) - {desc}")
                lines.append("")

        # Routing Layer (Tools)
        lines.append("## 🔧 Routing Layer (Tools)")
        if not tools:
            lines.append("_No tools registered_")
        else:
            # Group tools by namespace (agent_id.tool_name)
            tool_groups = defaultdict(list)
            for tool in tools:
                parts = tool.split(".", 1)
                namespace = parts[0] if len(parts) > 1 else "core"
                tool_groups[namespace].append(tool)

            for namespace, group_tools in sorted(tool_groups.items()):
                lines.append(f"**{namespace.upper()}**")
                lines.append(f"`{', '.join(sorted(group_tools))}`")
                lines.append("")

        return "\n".join(lines)

    def _generate_topology_diagram(self, total_agents: int) -> str:
        """Generate ASCII topology diagram."""
        return f"""```
         🏔️ MOUNT MERU (Kernel)
              │
    ┌─────────┼─────────┐
  SYSTEM    CIVIC     USER
   (Core)  (Economy) (Apps)
     │        │        │
    ...      ...      ...

  Total Active Nodes: {total_agents}
```"""
