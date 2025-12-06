"""Base Renderer with Section-based Rendering Support.

Renderers can now use config-driven sections with ownership:
- LIVE: System writes, refreshed on each render
- AI: AI can write, preserved between renders
- HUMAN: User writes, always preserved

Usage:
    class MyRenderer(BaseRenderer):
        @property
        def name(self) -> str:
            return "myrenderer"

        def render(self) -> None:
            # Use section-based rendering from config
            content = self.render_sections()
            self.merge_and_write(content)  # preserves AI/HUMAN sections
"""

import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.phoenix.sections.interface import (
        InterfaceConfig,
        RendererConfig,
        SectionConfig,
    )

logger = logging.getLogger("BASE_RENDERER")


class BaseRenderer(ABC):
    """Abstract base class for Interface Renderers with section support."""

    def __init__(self, kernel: "RealVibeKernel"):
        self.kernel = kernel
        self._config: Optional["RendererConfig"] = None
        self._interface_config: Optional["InterfaceConfig"] = None

        # Data source registry - maps source paths to callables
        self._data_sources: Dict[str, Callable[[], Any]] = {}

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the renderer (e.g. 'envoy', 'settings')."""
        pass

    @abstractmethod
    def render(self) -> None:
        """Perform rendering logic."""
        pass

    # =========================================================================
    # CONFIG ACCESS
    # =========================================================================

    def get_config(self) -> Optional["RendererConfig"]:
        """Get renderer config from InterfaceConfig."""
        if self._config is None:
            self._load_config()
        return self._config

    def get_interface_config(self) -> Optional["InterfaceConfig"]:
        """Get full interface config."""
        if self._interface_config is None:
            self._load_config()
        return self._interface_config

    def _load_config(self) -> None:
        """Load config from Phoenix Config."""
        try:
            from vibe_core.phoenix.sections.interface import InterfaceConfig

            self._interface_config = InterfaceConfig.from_yaml("config/interface.yaml")
            self._config = self._interface_config.get_renderer(self.name)
        except Exception as e:
            logger.warning(f"Could not load config for {self.name}: {e}")

    # =========================================================================
    # DATA SOURCE REGISTRY
    # =========================================================================

    def register_data_source(self, path: str, callback: Callable[[], Any]) -> None:
        """
        Register a data source for LIVE sections.

        Example:
            self.register_data_source("kernel.status", lambda: self.kernel.status)
            self.register_data_source("agents.list", self._get_agent_list)
        """
        self._data_sources[path] = callback

    def get_data(self, source_path: str) -> Any:
        """
        Get data from a registered source.

        Supports dotted paths like "kernel.status" or "agents.list".
        """
        # Check registered sources first
        if source_path in self._data_sources:
            try:
                return self._data_sources[source_path]()
            except Exception as e:
                logger.warning(f"Data source {source_path} failed: {e}")
                return None

        # Try to resolve from kernel
        return self._resolve_kernel_path(source_path)

    def _resolve_kernel_path(self, path: str) -> Any:
        """Resolve a dotted path from kernel (e.g., 'kernel.status')."""
        parts = path.split(".")
        obj: Any = self.kernel

        for part in parts:
            if obj is None:
                return None
            if hasattr(obj, part):
                obj = getattr(obj, part)
            elif isinstance(obj, dict) and part in obj:
                obj = obj[part]
            else:
                return None

        # If it's callable, call it
        if callable(obj) and not isinstance(obj, type):
            try:
                return obj()
            except Exception:
                return obj
        return obj

    # =========================================================================
    # SECTION-BASED RENDERING
    # =========================================================================

    def render_sections(self) -> str:
        """
        Render all sections from config with ownership handling.

        Returns:
            Rendered markdown content
        """
        config = self.get_config()
        if not config or not config.sections:
            # Fallback: no sections defined, return empty
            return ""

        interface_config = self.get_interface_config()
        lines: List[str] = []

        # Add header if configured
        if interface_config:
            header = self._render_header(interface_config)
            if header:
                lines.append(header)

        # Render each section
        for section in config.sections:
            section_content = self._render_section(section, interface_config)
            if section_content:
                lines.append(section_content)

        # Add footer if configured
        if interface_config:
            footer = self._render_footer(interface_config)
            if footer:
                lines.append(footer)

        return "\n".join(lines)

    def _render_section(self, section: "SectionConfig", interface_config: Optional["InterfaceConfig"]) -> str:
        """Render a single section based on ownership."""
        ownership_config = None
        if interface_config:
            ownership_config = interface_config.get_ownership_config(section.owner)

        # Get markers
        marker_start = ""
        marker_end = ""
        if ownership_config:
            marker_start = ownership_config.marker_start.format(id=section.id)
            marker_end = ownership_config.marker_end

        lines: List[str] = []

        # Add start marker
        if marker_start:
            lines.append(marker_start)

        # Render content based on ownership
        if section.owner == "live":
            # LIVE: Get fresh data from source
            content = self._render_live_section(section)
            lines.append(content)
        elif section.owner in ("ai", "human"):
            # AI/HUMAN: Preserve existing content or add placeholder
            content = self._get_preserved_content(section)
            if content:
                lines.append(content)
            else:
                lines.append(self._get_section_placeholder(section))
        else:
            # Unknown owner, treat as live
            content = self._render_live_section(section)
            lines.append(content)

        # Add end marker
        if marker_end:
            lines.append(marker_end)

        return "\n".join(lines)

    def _render_live_section(self, section: "SectionConfig") -> str:
        """Render a LIVE section by fetching data from source."""
        if not section.source:
            return f"## {section.id.replace('_', ' ').title()}\n\n_No data source configured_"

        data = self.get_data(section.source)
        if data is None:
            return f"## {section.id.replace('_', ' ').title()}\n\n_Data unavailable_"

        # Format based on element type
        element_type = section.element_type or "text"
        return self._format_data(section.id, data, element_type)

    def _format_data(self, section_id: str, data: Any, element_type: str) -> str:
        """Format data based on element type."""
        title = f"## {section_id.replace('_', ' ').title()}"

        if element_type == "table" and isinstance(data, (list, dict)):
            return f"{title}\n\n{self._format_table(data)}"
        elif element_type == "list" and isinstance(data, (list, dict)):
            return f"{title}\n\n{self._format_list(data)}"
        elif element_type == "status":
            return f"{title}\n\n{self._format_status(data)}"
        elif element_type == "metric":
            return f"{title}\n\n{self._format_metric(data)}"
        elif element_type == "terminal":
            return f"{title}\n\n{self._format_terminal(data)}"
        else:
            # Default: plain text
            return f"{title}\n\n{data}"

    def _format_table(self, data: Any) -> str:
        """Format data as markdown table."""
        if isinstance(data, list) and data:
            if isinstance(data[0], dict):
                # List of dicts -> table
                headers = list(data[0].keys())
                lines = ["| " + " | ".join(headers) + " |"]
                lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                for row in data:
                    values = [str(row.get(h, "")) for h in headers]
                    lines.append("| " + " | ".join(values) + " |")
                return "\n".join(lines)
            else:
                # Simple list -> single column
                lines = ["| Value |", "| --- |"]
                for item in data:
                    lines.append(f"| {item} |")
                return "\n".join(lines)
        elif isinstance(data, dict):
            # Dict -> key-value table
            lines = ["| Key | Value |", "| --- | --- |"]
            for k, v in data.items():
                lines.append(f"| {k} | {v} |")
            return "\n".join(lines)
        return str(data)

    def _format_list(self, data: Any) -> str:
        """Format data as markdown list."""
        if isinstance(data, list):
            return "\n".join(f"- {item}" for item in data)
        elif isinstance(data, dict):
            return "\n".join(f"- **{k}**: {v}" for k, v in data.items())
        return str(data)

    def _format_status(self, data: Any) -> str:
        """Format data as status indicator."""
        config = self.get_interface_config()
        icons = {"running": "🟢", "stopped": "🔴", "warning": "🟡", "unknown": "⚪"}

        if config and config.element_types.get("status"):
            icons = config.element_types["status"].settings.get("icons", icons)

        if isinstance(data, str):
            icon = icons.get(data.lower(), icons.get("unknown", "⚪"))
            return f"{icon} {data}"
        elif isinstance(data, dict):
            lines = []
            for k, v in data.items():
                icon = icons.get(str(v).lower(), icons.get("unknown", "⚪"))
                lines.append(f"{icon} **{k}**: {v}")
            return "\n".join(lines)
        return str(data)

    def _format_metric(self, data: Any) -> str:
        """Format data as metric display."""
        if isinstance(data, dict):
            lines = []
            for k, v in data.items():
                lines.append(f"**{k}**: {v}")
            return " | ".join(lines)
        return str(data)

    def _format_terminal(self, data: Any) -> str:
        """Format data as terminal/command block."""
        if isinstance(data, str):
            return f"```\n{data}\n```"
        return f"```\n{data}\n```"

    def _get_preserved_content(self, section: "SectionConfig") -> Optional[str]:
        """Get preserved content from existing document for AI/HUMAN sections."""
        config = self.get_config()
        if not config:
            return None

        output_path = Path(config.output)
        if not output_path.exists():
            return None

        try:
            content = output_path.read_text()

            # Find section by markers
            interface_config = self.get_interface_config()
            if not interface_config:
                return None

            ownership_config = interface_config.get_ownership_config(section.owner)
            if not ownership_config:
                return None

            marker_start = ownership_config.marker_start.format(id=section.id)
            marker_end = ownership_config.marker_end

            # Extract content between markers
            pattern = re.escape(marker_start) + r"(.*?)" + re.escape(marker_end)
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()

        except Exception as e:
            logger.warning(f"Could not read preserved content: {e}")

        return None

    def _get_section_placeholder(self, section: "SectionConfig") -> str:
        """Get placeholder for AI/HUMAN sections."""
        title = f"## {section.id.replace('_', ' ').title()}"
        if section.owner == "ai":
            return f"{title}\n\n<!-- AI can write here -->\n_No entries_"
        elif section.owner == "human":
            return f"{title}\n\n<!-- User section -->\n_No entries_"
        return f"{title}\n\n_Empty_"

    def _render_header(self, config: "InterfaceConfig") -> str:
        """Render document header."""
        if not config.header.show_nav and not config.header.show_timestamp:
            return ""

        lines = ["<!--"]
        lines.append(f"AUTO-GENERATED by {config.header.generator_name}")

        if config.header.show_timestamp:
            timestamp = datetime.utcnow().strftime(config.formatting.datetime_format)
            lines.append(f"Last Updated: {timestamp} {config.formatting.timezone}")

        if config.header.show_kernel_status:
            status = getattr(self.kernel, "status", "UNKNOWN")
            lines.append(f"Kernel: {status}")

        lines.append("-->")

        if config.header.show_nav and config.header.nav_docs:
            nav_links = []
            for doc in config.header.nav_docs:
                name = doc.replace(".md", "")
                nav_links.append(f"[{name}]({doc})")
            lines.append(f"> **Docs:** {' · '.join(nav_links)}")

        return "\n".join(lines) + "\n"

    def _render_footer(self, config: "InterfaceConfig") -> str:
        """Render document footer."""
        if not config.footer.show_generator and not config.footer.show_timestamp:
            return ""

        timestamp = datetime.utcnow().strftime(config.formatting.datetime_format)
        return config.footer.format.format(
            generator=config.header.generator_name, timestamp=f"{timestamp} {config.formatting.timezone}"
        )

    # =========================================================================
    # DOCUMENT WRITING
    # =========================================================================

    def write_document(self, content: str) -> bool:
        """
        Write document through kernel IO service.

        Handles bidirectional documents with section preservation.
        """
        config = self.get_config()
        if not config:
            return False

        try:
            self.kernel.io.write_document(
                name=config.output,
                content=content,
                writer_id=f"RENDERER_{self.name.upper()}",
                add_header=False,  # Renderer generates its own header via render_sections()
            )
            return True
        except Exception as e:
            logger.error(f"Failed to write {config.output}: {e}")
            return False

    def merge_and_write(self, new_content: str) -> bool:
        """
        Merge new content with existing document, preserving AI/HUMAN sections.

        This is the recommended way to write for bidirectional documents.
        """
        config = self.get_config()
        if not config:
            return False

        output_path = Path(config.output)

        # If file doesn't exist, just write
        if not output_path.exists():
            return self.write_document(new_content)

        try:
            existing = output_path.read_text()
            merged = self._merge_content(existing, new_content)
            return self.write_document(merged)
        except Exception as e:
            logger.error(f"Failed to merge {config.output}: {e}")
            return False

    def _merge_content(self, existing: str, new_content: str) -> str:
        """Merge existing content with new content, preserving marked sections."""
        config = self.get_config()
        interface_config = self.get_interface_config()

        if not config or not interface_config:
            return new_content

        result = new_content

        # For each section that should be preserved (AI/HUMAN)
        for section in config.sections:
            if section.owner not in ("ai", "human"):
                continue

            ownership_config = interface_config.get_ownership_config(section.owner)
            if not ownership_config:
                continue

            marker_start = ownership_config.marker_start.format(id=section.id)
            marker_end = ownership_config.marker_end

            # Extract from existing
            pattern = re.escape(marker_start) + r"(.*?)" + re.escape(marker_end)
            existing_match = re.search(pattern, existing, re.DOTALL)

            if existing_match:
                preserved = existing_match.group(0)
                # Replace in new content
                new_match = re.search(pattern, result, re.DOTALL)
                if new_match:
                    result = result[: new_match.start()] + preserved + result[new_match.end() :]

        return result
