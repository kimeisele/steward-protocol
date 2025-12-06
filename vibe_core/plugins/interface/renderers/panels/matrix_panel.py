"""
Matrix Panel - Tools, Circuits & Playbooks Overview.

DATA-DRIVEN: Discovers from kernel registry and YAML files.
Shows what's available to execute.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

import yaml

from .base_panel import OpusPanel

logger = logging.getLogger("PANEL_MATRIX")


class MatrixPanel(OpusPanel):
    """
    System capabilities matrix - what can be executed.

    Shows:
    - Registered tools (from kernel.tool_registry)
    - Available circuits (from playbook/circuits/*.yaml)
    - Available playbooks (from playbook/playbooks/*.yaml)
    - Agent capabilities (from cartridges)
    """

    @property
    def panel_id(self) -> str:
        return "matrix"

    @property
    def priority(self) -> int:
        return 60  # After debt panel

    def render(self, config: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Render the matrix panel."""
        lines = ["## System Matrix", "", "> **Available Capabilities**", ""]

        # Get kernel from context if available
        kernel = context.get("kernel")

        # 1. Tools
        tools = self._discover_tools(kernel)
        lines.append("### Tools")
        lines.append("")
        if tools:
            lines.append("| Tool | Domain | Description |")
            lines.append("|------|--------|-------------|")
            for tool in tools[:15]:  # Limit to 15
                lines.append(f"| `{tool['name']}` | {tool['domain']} | {tool['desc'][:40]} |")
        else:
            lines.append("_No tools registered_")
        lines.append("")

        # 2. Circuits
        circuits = self._discover_circuits()
        lines.append("### Circuits")
        lines.append("")
        if circuits:
            lines.append("| Circuit | Domain | Version |")
            lines.append("|---------|--------|---------|")
            for circuit in circuits[:12]:
                lines.append(f"| `{circuit['id']}` | {circuit['domain']} | {circuit['version']} |")
            if len(circuits) > 12:
                lines.append(f"| ... | +{len(circuits) - 12} more | |")
        else:
            lines.append("_No circuits found_")
        lines.append("")

        # 3. Quick Stats
        playbooks = self._count_playbooks()
        agents = self._count_agents()

        lines.append("### Quick Stats")
        lines.append("")
        lines.append(f"- **Tools:** {len(tools)}")
        lines.append(f"- **Circuits:** {len(circuits)}")
        lines.append(f"- **Playbooks:** {playbooks}")
        lines.append(f"- **Agent Cartridges:** {agents}")
        lines.append("")

        lines.append("---")
        lines.append("*See MATRIX.md for full routing table*")

        return "\n".join(lines)

    def _discover_tools(self, kernel) -> List[Dict[str, str]]:
        """Discover registered tools from kernel."""
        tools = []

        if kernel and hasattr(kernel, "tool_registry"):
            try:
                for tool_name in kernel.tool_registry.list_tools():
                    tool = kernel.tool_registry.get_tool(tool_name)
                    domain = getattr(tool, "domain", "general") if tool else "general"
                    desc = getattr(tool, "description", "")[:40] if tool else ""
                    tools.append({"name": tool_name, "domain": domain, "desc": desc})
            except Exception as e:
                logger.debug(f"Could not list tools: {e}")

        # Fallback: scan tool directories
        if not tools:
            tools = self._scan_tool_dirs()

        return tools

    def _scan_tool_dirs(self) -> List[Dict[str, str]]:
        """Scan for tools in cartridge directories."""
        tools = []
        root = Path.cwd()

        # Check system cartridges
        system_path = root / "vibe_core" / "cartridges" / "system"
        if system_path.exists():
            for agent_dir in system_path.iterdir():
                if agent_dir.is_dir():
                    tools_dir = agent_dir / "tools"
                    if tools_dir.exists():
                        for tool_file in tools_dir.glob("*_tool.py"):
                            name = tool_file.stem.replace("_tool", "")
                            tools.append(
                                {
                                    "name": name,
                                    "domain": agent_dir.name,
                                    "desc": f"From {agent_dir.name}",
                                }
                            )

        return tools[:20]  # Limit

    def _discover_circuits(self) -> List[Dict[str, str]]:
        """Discover circuits from YAML files."""
        circuits = []
        root = Path.cwd()
        circuits_path = root / "vibe_core" / "playbook" / "circuits"

        if not circuits_path.exists():
            return circuits

        for yaml_file in circuits_path.glob("*.yaml"):
            try:
                with open(yaml_file) as f:
                    data = yaml.safe_load(f)

                if data and "circuit" in data:
                    circuit = data["circuit"]
                    circuits.append(
                        {
                            "id": circuit.get("id", yaml_file.stem),
                            "domain": circuit.get("domain", "-"),
                            "version": circuit.get("version", "-"),
                        }
                    )
            except Exception as e:
                logger.debug(f"Could not parse {yaml_file}: {e}")

        return sorted(circuits, key=lambda x: x["id"])

    def _count_playbooks(self) -> int:
        """Count available playbooks."""
        root = Path.cwd()
        playbooks_path = root / "vibe_core" / "playbook" / "playbooks"
        if playbooks_path.exists():
            return len(list(playbooks_path.glob("*.yaml")))
        return 0

    def _count_agents(self) -> int:
        """Count agent cartridges."""
        count = 0
        root = Path.cwd()

        for cartridge_type in ["system", "agent_city"]:
            path = root / "vibe_core" / "cartridges" / cartridge_type
            if path.exists():
                count += len([d for d in path.iterdir() if d.is_dir() and not d.name.startswith("_")])

        return count
