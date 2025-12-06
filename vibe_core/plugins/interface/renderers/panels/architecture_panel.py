"""
Architecture Panel - System Overview with Mermaid Diagram.

Generates a LIVE architecture view showing:
- Core kernel components
- Plugin connections
- Agent ecosystem
- Data flows

DATA-DRIVEN: Scans actual code structure.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

from .base_panel import OpusPanel

logger = logging.getLogger("PANEL_ARCHITECTURE")


class ArchitecturePanel(OpusPanel):
    """
    Live architecture diagram generator.

    Creates a Mermaid flowchart showing actual system structure.
    """

    @property
    def panel_id(self) -> str:
        return "architecture"

    @property
    def priority(self) -> int:
        return 5  # Very high - overview first

    def render(self, config: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Render architecture overview with mermaid diagram."""
        lines = ["## System Architecture", "", "> **Live Component Map**", ""]

        # Get live data
        kernel = context.get("kernel")
        plugins = self._discover_plugins()
        agents = self._discover_agents()
        renderers = self._discover_renderers()

        # Build mermaid diagram
        lines.append("```mermaid")
        lines.append("flowchart TB")
        lines.append("    subgraph KERNEL[Kernel Layer]")
        lines.append("        K[RealVibeKernel]")
        lines.append("        KO[KernelOps]")
        lines.append("        IO[IOService]")
        lines.append("        SCH[Scheduler]")
        lines.append("    end")
        lines.append("")
        lines.append("    subgraph PLUGINS[Plugin Layer]")

        for i, plugin in enumerate(plugins[:6]):
            node_id = f"P{i}"
            lines.append(f"        {node_id}[{plugin}]")

        lines.append("    end")
        lines.append("")
        lines.append("    subgraph AGENTS[Agent Layer]")

        # Group agents
        system_agents = [
            a
            for a in agents
            if "system" in a.lower() or a in ["envoy", "engineer", "analyst", "herald", "watchman", "archivist"]
        ]
        city_agents = [a for a in agents if a not in system_agents]

        for i, agent in enumerate(system_agents[:4]):
            lines.append(f"        SA{i}[{agent}]")
        if city_agents:
            lines.append(f"        CITY[+{len(city_agents)} city agents]")

        lines.append("    end")
        lines.append("")
        lines.append("    subgraph UI[Interface Layer]")
        lines.append("        IP[InterfacePlugin]")

        for i, renderer in enumerate(renderers[:4]):
            lines.append(f"        R{i}[{renderer}.md]")

        if len(renderers) > 4:
            lines.append(f"        RMORE[+{len(renderers) - 4} more]")

        lines.append("    end")
        lines.append("")

        # Connections
        lines.append("    K --> KO")
        lines.append("    K --> IO")
        lines.append("    K --> SCH")
        lines.append("    K --> PLUGINS")
        lines.append("    PLUGINS --> AGENTS")
        lines.append("    K --> IP")
        lines.append("    IP --> UI")

        lines.append("```")
        lines.append("")

        # Component counts
        lines.append("### Component Summary")
        lines.append("")
        lines.append("| Layer | Components | Status |")
        lines.append("|-------|------------|--------|")
        lines.append("| Kernel | 4 core modules | ACTIVE |")
        lines.append(f"| Plugins | {len(plugins)} plugins | ACTIVE |")
        lines.append(f"| Agents | {len(agents)} cartridges | LOADED |")
        lines.append(f"| UI | {len(renderers)} renderers | LIVE |")
        lines.append("")

        # Key paths
        lines.append("### Key Paths")
        lines.append("")
        lines.append("| Component | Path |")
        lines.append("|-----------|------|")
        lines.append("| Kernel | `vibe_core/kernel_impl.py` |")
        lines.append("| Plugins | `vibe_core/plugins/` |")
        lines.append("| Agents | `vibe_core/cartridges/` |")
        lines.append("| UI | `vibe_core/plugins/interface/renderers/` |")
        lines.append("| Config | `config/*.yaml` |")
        lines.append("")

        lines.append("---")

        return "\n".join(lines)

    def _discover_plugins(self) -> List[str]:
        """Discover registered plugins."""
        plugins = []
        root = Path.cwd()
        plugins_path = root / "vibe_core" / "plugins"

        if plugins_path.exists():
            for item in plugins_path.iterdir():
                if item.is_dir() and not item.name.startswith("_"):
                    plugins.append(item.name)

        return sorted(plugins)

    def _discover_agents(self) -> List[str]:
        """Discover agent cartridges."""
        agents = []
        root = Path.cwd()

        for cartridge_type in ["system", "agent_city"]:
            path = root / "vibe_core" / "cartridges" / cartridge_type
            if path.exists():
                for item in path.iterdir():
                    if item.is_dir() and not item.name.startswith("_"):
                        agents.append(item.name)

        return sorted(agents)

    def _discover_renderers(self) -> List[str]:
        """Discover UI renderers."""
        renderers = []
        root = Path.cwd()
        renderers_path = root / "vibe_core" / "plugins" / "interface" / "renderers"

        if renderers_path.exists():
            for item in renderers_path.glob("*.py"):
                if item.name not in ("__init__.py", "base.py"):
                    name = item.stem.upper()
                    renderers.append(name)

        return sorted(renderers)
