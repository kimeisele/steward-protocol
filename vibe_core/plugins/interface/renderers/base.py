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

from vibe_core.errors import ErrorCode, StructuredError

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol
    from vibe_core.phoenix.sections.interface import (
        InterfaceConfig,
        RendererConfig,
        SectionConfig,
    )

logger = logging.getLogger("BASE_RENDERER")


class BaseRenderer(ABC):
    """Abstract base class for Interface Renderers with section support."""

    def __init__(self, kernel: "KernelProtocol"):
        self.kernel = kernel
        self._config: Optional["RendererConfig"] = None
        self._interface_config: Optional["InterfaceConfig"] = None
        self._root_path: Path = Path(__file__).parent  # Default fallback

        # Data source registry - maps source paths to callables
        self._data_sources: Dict[str, Callable[[], Any]] = {}

        # Law 3: Content hash for dirty tracking (skip writes if unchanged)
        self._last_content_hash: Optional[str] = None

        # Law 1: Backup tracking for rollback
        self._backup_path: Optional[Path] = None

    def set_root_path(self, path: Path) -> None:
        """Called by loader to inject the true container root context."""
        self._root_path = path

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the renderer (e.g. 'envoy', 'settings')."""
        pass

    def render(self) -> None:
        """
        Legacy render method - DEPRECATED.

        Subclasses should implement generate_content() instead.
        InterfacePlugin handles the actual writing.
        """
        if self.generate_content() is None:
            raise NotImplementedError(f"Renderer '{self.name}' must implement generate_content() or render()")

    def generate_content(self) -> Optional[str]:
        """
        Generate content for this renderer (optional pattern).

        Override this method to provide content.
        Return None if not using this pattern.
        """
        return None

    def render_with_dirty_tracking(self) -> None:
        """
        Helper: Render with Law 3 (hash-based dirty tracking).

        Subclasses that use generate_content() can call this instead of
        implementing render() directly. It handles the hashing.

        Example:
            class MyRenderer(BaseRenderer):
                def render(self) -> None:
                    self.render_with_dirty_tracking()

                def generate_content(self) -> str:
                    return "my content"
        """
        import hashlib

        # Law 2 (Error Boundary) - Safety check at generating content
        try:
            new_content = self.generate_content()
        except Exception as e:
            logger.error(f"{self.name}: Failed to generate content: {e}")
            raise  # Re-raise to be caught by plugin_main

        if new_content is None:
            return

        # Law 3: Check if content actually changed
        new_hash = hashlib.md5(new_content.encode()).hexdigest()

        if new_hash == self._last_content_hash:
            logger.debug(f"{self.name}: No changes, skipping write")
            return

        # Content changed, merge and write
        # This calls merge_and_write which handles Law 1 (Backup)
        if self.merge_and_write(new_content):
            self._last_content_hash = new_hash

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

        Law 1 (Atomic Write with Backup):
        - Creates backup before write for bidirectional docs
        - Detects data loss (file shrunk >50%)
        - Rolls back on suspicious writes

        This is the recommended way to write for bidirectional documents.
        """
        config = self.get_config()
        if not config:
            return False

        output_path = Path(config.output)

        # Law 1: Create backup before write if file exists
        if output_path.exists():
            self._create_backup()

        # If file doesn't exist, just write
        if not output_path.exists():
            return self.write_document(new_content)

        try:
            existing = output_path.read_text()
            merged = self._merge_content(existing, new_content)
            result = self.write_document(merged)

            # Law 1: Check for data loss after write
            if result and self._file_suspiciously_smaller():
                logger.error(f"Data loss detected in {config.output} (file shrunk >50%)")
                self._rollback_from_backup()
                raise StructuredError(
                    code=ErrorCode.E3005_INTERNAL_ERROR,
                    message="Render produced suspiciously small output",
                    context={"document": self.name},
                )

            # Law 1: Clean up backup on success
            if result:
                self._cleanup_backup()

            return result
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

    # =========================================================================
    # LAW 1: ATOMIC WRITE WITH BACKUP (Data Safety)
    # =========================================================================

    def _create_backup(self) -> None:
        """Law 1: Create backup before writing bidirectional doc."""
        config = self.get_config()
        if not config:
            return

        path = Path(config.output)
        if not path.exists():
            return

        backup_path = path.with_suffix(path.suffix + ".bak")
        try:
            import shutil

            shutil.copy2(path, backup_path)
            self._backup_path = backup_path
            logger.debug(f"Backup created: {backup_path}")
        except Exception as e:
            logger.warning(f"Failed to create backup for {path}: {e}")

    def _rollback_from_backup(self) -> None:
        """Law 1: Restore from backup on suspicious write."""
        if self._backup_path and self._backup_path.exists():
            config = self.get_config()
            if config:
                try:
                    import shutil

                    shutil.copy2(self._backup_path, config.output)
                    logger.warning(f"Rolled back to backup: {self._backup_path}")
                except Exception as e:
                    logger.error(f"Failed to rollback from backup: {e}")

    def _cleanup_backup(self) -> None:
        """Law 1: Remove backup after successful write."""
        if self._backup_path and self._backup_path.exists():
            try:
                self._backup_path.unlink()
                logger.debug(f"Backup cleaned up: {self._backup_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup backup: {e}")
            finally:
                self._backup_path = None

    def _get_backup_size(self) -> int:
        """Get size of backup file in bytes."""
        if self._backup_path and self._backup_path.exists():
            try:
                return self._backup_path.stat().st_size
            except Exception:
                return 0
        return 0

    def _get_current_size(self) -> int:
        """Get size of current file in bytes."""
        config = self.get_config()
        if not config:
            return 0
        try:
            path = Path(config.output)
            if path.exists():
                return path.stat().st_size
            return 0
        except Exception:
            return 0

    def _file_suspiciously_smaller(self) -> bool:
        """Detect if file shrunk >50% (likely data loss)."""
        backup_size = self._get_backup_size()
        current_size = self._get_current_size()
        if backup_size > 0 and current_size < backup_size * 0.5:
            return True
        return False
