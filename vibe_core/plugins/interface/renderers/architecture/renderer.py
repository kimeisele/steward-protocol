"""
Architecture Renderer - Generates dynamic Mermaid diagrams from actual code.

Reads the codebase and generates:
- Plugin dependency graph
- Component size table
- Import relationships
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

from ..base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol


class ArchitectureRenderer(BaseRenderer):
    """Generates architecture diagrams from live code analysis."""

    def __init__(self, kernel: "KernelProtocol"):
        super().__init__(kernel)
        self._root = Path(".")
        self._register_data_sources()

    @property
    def name(self) -> str:
        return "architecture"

    @property
    def output_file(self) -> str:
        return "ARCHITECTURE.md"

    @property
    def doc_type(self):
        """Document type for IO service."""
        from vibe_core.io_service import DocumentType

        return DocumentType.READONLY

    def generate_content(self) -> str:
        """Generate full ARCHITECTURE.md content (UNIFIED UI pattern)."""
        lines = ["# Architecture Overview", ""]

        # Mermaid diagram
        lines.append(self._generate_mermaid())
        lines.append("")

        # Component sizes
        lines.append("## Component Sizes")
        lines.append("")
        components = self._get_component_sizes()
        if components:
            lines.append("| Component | File | LOC |")
            lines.append("| --- | --- | --- |")
            for c in components:
                lines.append(f"| {c['Component']} | {c['File']} | {c['LOC']} |")
        lines.append("")

        # Plugin status
        lines.append("## Plugin Status")
        lines.append("")
        plugins = self._get_plugin_info()
        if plugins:
            lines.append("| Plugin | Status | Type |")
            lines.append("| --- | --- | --- |")
            for p in plugins:
                lines.append(f"| {p['Plugin']} | {p['Status']} | {p['Type']} |")

        return "\n".join(lines)

    def _register_data_sources(self) -> None:
        """Register live data sources."""
        self.register_data_source("arch.mermaid", self._generate_mermaid)
        self.register_data_source("arch.components", self._get_component_sizes)
        self.register_data_source("arch.plugins", self._get_plugin_info)

    def render(self) -> None:
        """Render ARCHITECTURE.md using config-driven sections."""
        config = self.get_config()
        if config and config.sections:
            content = self.render_sections()
            self.merge_and_write(content)
        else:
            content = self.generate_content()
            if content:
                self.merge_and_write(content)

    # =========================================================================
    # LIVE DATA GENERATION
    # =========================================================================

    def _generate_mermaid(self) -> str:
        """Generate Mermaid diagram from actual plugin structure."""
        plugins = self._discover_plugins()

        lines = ["```mermaid", "graph TB"]

        # Kernel
        kernel_loc = self._count_loc("vibe_core/kernel_impl.py")
        lines.append(f'    K["🧠 Kernel ({kernel_loc} LOC)"]')

        # Plugins subgraph
        lines.append('    subgraph Plugins["📦 Plugins"]')
        for name, info in plugins.items():
            short = name.replace("Plugin", "")
            lines.append(f'        P_{short}["{name}"]')
        lines.append("    end")

        # Connections
        lines.append("    K --> Plugins")

        # Phoenix Config
        lines.append('    subgraph Config["🔥 Phoenix Config"]')
        lines.append("        PC[PhoenixConfig]")
        lines.append("    end")
        lines.append("    K --> Config")

        lines.append("```")
        return "\n".join(lines)

    def _get_component_sizes(self) -> List[Dict[str, Any]]:
        """Get LOC for major components."""
        components = [
            ("vibe_core/kernel_impl.py", "Kernel"),
            ("vibe_core/kernel_ops.py", "Kernel Ops"),
            ("vibe_core/plugins/interface/renderers/base.py", "BaseRenderer"),
            ("vibe_core/plugins/interface/plugin_main.py", "InterfacePlugin"),
            ("vibe_core/event_bus.py", "EventBus"),
            ("vibe_core/phoenix/config.py", "PhoenixConfig"),
            ("vibe_core/phoenix/sections/interface/section_main.py", "InterfaceConfig"),
        ]

        result = []
        for path, name in components:
            loc = self._count_loc(path)
            if loc > 0:
                result.append(
                    {
                        "Component": name,
                        "File": path.split("/")[-1],
                        "LOC": loc,
                    }
                )

        # Sort by LOC descending
        result.sort(key=lambda x: x["LOC"], reverse=True)
        return result

    def _get_plugin_info(self) -> List[Dict[str, Any]]:
        """Get info about loaded plugins from kernel."""
        result = []

        # _plugins is a list of plugin instances
        if hasattr(self.kernel, "_plugins"):
            for plugin in self.kernel._plugins:
                result.append(
                    {
                        "Plugin": getattr(plugin, "plugin_id", type(plugin).__name__),
                        "Status": "✅ Active",
                        "Type": type(plugin).__name__,
                    }
                )

        return result if result else [{"Plugin": "None loaded", "Status": "⚪", "Type": "-"}]

    def _discover_plugins(self) -> Dict[str, Dict[str, Any]]:
        """Discover plugins from filesystem."""
        plugins_dir = self._root / "vibe_core" / "plugins"
        result = {}

        if plugins_dir.exists():
            for item in plugins_dir.iterdir():
                if item.is_dir() and not item.name.startswith("_"):
                    plugin_main = item / "plugin_main.py"
                    if plugin_main.exists():
                        result[item.name] = {
                            "path": str(item),
                            "loc": self._count_loc(str(plugin_main)),
                        }

        return result

    def _count_loc(self, path: str) -> int:
        """Count lines of code in a file (raw wc -l style)."""
        try:
            full_path = self._root / path
            if full_path.exists():
                return len(full_path.read_text().splitlines())
        except Exception:
            pass
        return 0


def create_renderer(kernel: "KernelProtocol", config: Dict[str, Any]) -> ArchitectureRenderer:
    """Factory function."""
    return ArchitectureRenderer(kernel)
