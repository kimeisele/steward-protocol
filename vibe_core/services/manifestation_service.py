"""
OPUS-308: Manifestation Service - CORE KERNEL SERVICE

THE RENDERING ENGINE OF REALITY.

This is NOT a plugin. It's a Staatsorgan (state organ) of the Kernel,
alongside KernelIOService. It manifests plugins into Markdown reality.

Philosophy (OPUS-151):
    "The Markdown files are not the map. They are the territory."

Architecture:
    KernelIOService  = LOW-LEVEL I/O (bytes, locks, atomic writes)
    ManifestationService = HIGH-LEVEL UI (schemas, sections, manifestation)

The Inversion of Control:
    OLD: Plugin writes its own Markdown (chaos, spaghetti)
    NEW: Plugin provides data, Kernel manifests (order, composability)

Usage:
    # In Kernel __init__:
    self.io = KernelIOService(self)
    self.manifestation = ManifestationService(self)

    # Plugin declares in manifest.json:
    "manifestation": {
        "output": "ENVOY.md",
        "schema": "agent_standard"
    }

    # Plugin implements:
    def get_manifestation_data(self) -> Dict[str, Any]:
        return {"status": {...}, "capabilities": [...]}
"""

import hashlib
import logging
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set

# Lazy Jinja2 import for template support
_jinja2_env = None

from vibe_core.protocols.manifestation import (
    ManifestationDeclaration,
    ManifestationProtocol,
    ManifestationType,
    ManifestHeader,
    Section,
    SectionOwnership,
)

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("MANIFESTATION")


# =============================================================================
# MANIFEST INDEX (O(1) Lookup)
# =============================================================================


class ManifestIndex:
    """
    In-memory index of all manifestations.

    Lazy scan with 1-second TTL cache.
    The filesystem is the Source of Truth.
    The index is the Access Pattern.
    """

    def __init__(self, workspace: Path):
        self._workspace = workspace
        self._cache: Dict[str, Path] = {}
        self._reverse: Dict[Path, str] = {}
        self._cache_time: float = 0
        self._ttl: float = 1.0

        self._scan_locations: List[Path] = [
            workspace,
            workspace / ".vibe",
            workspace / "docs",
        ]

    def find(self, entity_id: str) -> Optional[Path]:
        """O(1) lookup by entity ID."""
        self._maybe_refresh()
        return self._cache.get(entity_id)

    def find_by_path(self, path: Path) -> Optional[str]:
        """O(1) reverse lookup."""
        self._maybe_refresh()
        return self._reverse.get(path.resolve())

    def all_manifestations(self) -> List[Path]:
        """Return all known manifestation paths."""
        self._maybe_refresh()
        return list(self._cache.values())

    def rebuild(self) -> None:
        """Full scan of manifestation locations."""
        self._cache.clear()
        self._reverse.clear()

        for location in self._scan_locations:
            if not location.exists():
                continue

            for md_file in location.glob("*.md"):
                if md_file.name.startswith("."):
                    continue

                entity_id = self._extract_entity_id(md_file)
                if entity_id:
                    resolved = md_file.resolve()
                    self._cache[entity_id] = resolved
                    self._reverse[resolved] = entity_id

        self._cache_time = time.time()
        logger.debug(f"ManifestIndex rebuilt: {len(self._cache)} manifestations")

    def _maybe_refresh(self) -> None:
        if time.time() - self._cache_time > self._ttl:
            self.rebuild()

    def _extract_entity_id(self, path: Path) -> Optional[str]:
        """Extract @MANIFEST entity ID from file header."""
        try:
            content = path.read_text(encoding="utf-8")
            header = content[:500]

            match = re.search(r"@MANIFEST:\s*(\S+)", header)
            if match:
                return match.group(1)

            return path.stem.lower()
        except Exception as e:
            # OPUS-312: Log extraction failures
            import logging

            logging.getLogger("MANIFESTATION").warning(f"Entity ID extraction failed for {path}: {e}")
            return None

    def on_file_created(self, path: Path) -> None:
        """Update index when new file detected."""
        if path.suffix != ".md":
            return
        entity_id = self._extract_entity_id(path)
        if entity_id:
            resolved = path.resolve()
            self._cache[entity_id] = resolved
            self._reverse[resolved] = entity_id

    def on_file_deleted(self, path: Path) -> None:
        """Update index when file removed."""
        resolved = path.resolve()
        entity_id = self._reverse.pop(resolved, None)
        if entity_id:
            self._cache.pop(entity_id, None)


# =============================================================================
# CHANGE DETECTOR (Infinite Loop Prevention)
# =============================================================================


class ChangeDetector:
    """
    Hash-based change detection to prevent infinite loops.

    Only triggers processing if @HUMAN sections actually changed.
    """

    def __init__(self):
        self._human_hashes: Dict[Path, str] = {}

    def should_process(self, path: Path) -> bool:
        """Check if @HUMAN sections changed (not just @LIVE)."""
        try:
            content = path.read_text(encoding="utf-8")
            human_content = self._extract_human_sections(content)
            current_hash = hashlib.md5(human_content.encode()).hexdigest()

            resolved = path.resolve()
            stored_hash = self._human_hashes.get(resolved)

            if stored_hash == current_hash:
                return False

            self._human_hashes[resolved] = current_hash
            return True
        except Exception:
            return True

    def update_hash(self, path: Path, human_content: str) -> None:
        """Update stored hash after processing."""
        resolved = path.resolve()
        self._human_hashes[resolved] = hashlib.md5(human_content.encode()).hexdigest()

    def _extract_human_sections(self, content: str) -> str:
        """Extract all @HUMAN section content for hashing."""
        pattern = r"<!--\s*@SECTION:\w+\s+OWNER:human\s*-->(.*?)<!--\s*/@SECTION\s*-->"
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        return "\n".join(m.strip() for m in matches)

    def extract_commands(self, path: Path) -> List[Dict[str, Any]]:
        """
        Extract commands from @HUMAN sections.

        Command format: "- ACTION target args..."
        Returns list of parsed command dicts.
        """
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            return []

        human_content = self._extract_human_sections(content)
        commands = []

        for line in human_content.split("\n"):
            line = line.strip()
            # Skip non-command lines
            if not line.startswith("- ") and not line.startswith("* "):
                continue
            # Skip already processed (strikethrough) or annotated
            if line.startswith("- ~~") or "<!-- @OK" in line or "<!-- @ERROR" in line:
                continue

            cmd_text = line[2:].strip()
            if not cmd_text:
                continue

            # Parse: ACTION target args
            parts = cmd_text.split(None, 2)
            commands.append(
                {
                    "raw": cmd_text,
                    "action": parts[0].upper() if parts else "",
                    "target": parts[1] if len(parts) > 1 else None,
                    "args": parts[2] if len(parts) > 2 else None,
                    "line": line,
                }
            )

        return commands


# =============================================================================
# SCHEMA SECTION DEFINITION
# =============================================================================


@dataclass
class SchemaSection:
    """A section definition from a schema."""

    id: str
    owner: SectionOwnership
    title: Optional[str]
    required: bool
    description: str


# =============================================================================
# REGISTERED MANIFESTATION
# =============================================================================


@dataclass
class RegisteredManifestation:
    """A plugin registered for manifestation."""

    plugin_id: str
    declaration: ManifestationDeclaration
    plugin_instance: Any  # The actual plugin object


@dataclass
class KernelSource:
    """A kernel-native manifestation (no plugin required)."""

    output: str  # Filename: "SETTINGS.md"
    schema: str  # Schema from config/manifestation.yaml
    data_getter: Callable[[], Dict[str, Any]]  # Lambda that returns section data
    frequency: str = "tick"
    location: str = "root"
    template: Optional[str] = None  # Jinja2 template path for complex UIs


# =============================================================================
# MANIFESTATION SERVICE - THE CORE SERVICE
# =============================================================================


class ManifestationService:
    """
    CORE KERNEL SERVICE: The Rendering Engine of Reality.

    NOT A PLUGIN. Lives alongside KernelIOService in the Kernel.

    Responsibilities:
    - Auto-discover plugins with "manifestation" config
    - Call get_manifestation_data() on each plugin
    - Render Markdown using schemas
    - Handle @HUMAN section preservation
    - Red Pen annotations for errors
    """

    SECTION_START = "<!-- @SECTION:{id} OWNER:{owner} -->"
    SECTION_END = "<!-- /@SECTION -->"
    ERROR_ANNOTATION = "<!-- @ERROR: {message} -->"
    SUCCESS_ANNOTATION = "<!-- @OK: {message} -->"

    def __init__(self, kernel: "RealVibeKernel"):
        """
        Initialize ManifestationService.

        Called in Kernel.__init__, BEFORE plugins boot.
        """
        self._kernel = kernel
        self._workspace = getattr(kernel, "workspace_path", None) or Path.cwd()

        # Core components
        self._index = ManifestIndex(self._workspace)
        self._change_detector = ChangeDetector()

        # Registered manifestations (populated when plugins boot)
        self._registered: Dict[str, RegisteredManifestation] = {}

        # Kernel-native sources (no plugin required)
        self._kernel_sources: Dict[str, KernelSource] = {}

        # Schemas (loaded from YAML)
        self._schemas: Dict[str, List[SchemaSection]] = {}
        self._load_schemas()

        # Interface config cache (lazy-loaded from Phoenix)
        self._interface_config_cache = None

        logger.info("ManifestationService initialized (CORE)")

    # =========================================================================
    # INTERFACE CONFIG (Phoenix-driven, not hardcoded!)
    # =========================================================================

    def _get_interface_config(self):
        """
        Get interface config from Phoenix (SINGLE SOURCE OF TRUTH).

        Uses lazy loading with caching.
        Falls back to None if Phoenix not available.
        """
        if self._interface_config_cache is not None:
            return self._interface_config_cache

        try:
            from vibe_core.phoenix.config import get_config

            self._interface_config_cache = get_config().interface
            return self._interface_config_cache
        except (ImportError, AttributeError) as e:
            logger.debug(f"Phoenix interface config not available: {e}")
            return None

    def _get_element_type_config(self, element_type: str) -> dict:
        """
        Get element type config (table, list, status, etc.) from Phoenix.

        Falls back to sensible defaults if config not available.
        """
        config = self._get_interface_config()
        if config and hasattr(config, "element_types"):
            elem_config = config.element_types.get(element_type)
            if elem_config:
                # Convert dataclass to dict if needed
                if hasattr(elem_config, "__dict__"):
                    return elem_config.__dict__
                return elem_config

        # Sensible defaults (matches interface.yaml defaults)
        defaults = {
            "table": {"header_style": "bold", "alignment": "left", "separator": "|"},
            "status": {
                "icons": {"running": "🟢", "stopped": "🔴", "warning": "🟡", "unknown": "⚪"},
                "format": "{icon} {label}",
            },
            "list": {"bullet": "-", "checkbox_empty": "[ ]", "checkbox_checked": "[x]", "indent": 2},
            "metric": {"format": "{label}: {value} {unit}", "progress_bar": True},
        }
        return defaults.get(element_type, {})

    @property
    def index(self) -> ManifestIndex:
        """Access the ManifestIndex."""
        return self._index

    @property
    def change_detector(self) -> ChangeDetector:
        """Access the ChangeDetector."""
        return self._change_detector

    # =========================================================================
    # PLUGIN REGISTRATION (Called when plugins boot)
    # =========================================================================

    def register_plugin(self, plugin_id: str, plugin_instance: Any, manifest: Dict[str, Any]) -> bool:
        """
        Register a plugin for manifestation.

        Called by PluginLoader when a plugin with "manifestation" config boots.

        Args:
            plugin_id: The plugin's ID
            plugin_instance: The plugin object (must have get_manifestation_data)
            manifest: The plugin's manifest.json content

        Returns:
            True if registered successfully
        """
        manifestation_config = manifest.get("manifestation")
        if not manifestation_config:
            return False

        # Validate plugin has get_manifestation_data
        if not hasattr(plugin_instance, "get_manifestation_data"):
            logger.warning(f"Plugin {plugin_id} has manifestation config but no get_manifestation_data()")
            return False

        # Parse declaration
        try:
            declaration = ManifestationDeclaration(
                output=manifestation_config.get("output", f"{plugin_id.upper()}.md"),
                schema=manifestation_config.get("schema", "agent_standard"),
                frequency=manifestation_config.get("frequency", "tick"),
                location=manifestation_config.get("location", "root"),
                template=manifestation_config.get("template"),  # Jinja2 template path
            )
        except Exception as e:
            logger.error(f"Invalid manifestation config for {plugin_id}: {e}")
            return False

        # Validate schema exists
        if declaration.schema not in self._schemas:
            logger.warning(f"Unknown schema '{declaration.schema}' for {plugin_id}, using agent_standard")
            declaration.schema = "agent_standard"

        self._registered[plugin_id] = RegisteredManifestation(
            plugin_id=plugin_id,
            declaration=declaration,
            plugin_instance=plugin_instance,
        )

        logger.info(f"Registered manifestation: {plugin_id} -> {declaration.output}")
        return True

    def unregister_plugin(self, plugin_id: str) -> None:
        """Unregister a plugin from manifestation."""
        if plugin_id in self._registered:
            del self._registered[plugin_id]
            logger.debug(f"Unregistered manifestation: {plugin_id}")

    # =========================================================================
    # KERNEL-NATIVE REGISTRATION (No plugin required)
    # =========================================================================

    def register_kernel_source(
        self,
        output: str,
        schema: str,
        data_getter: Callable[[], Dict[str, Any]],
        frequency: str = "tick",
        location: str = "root",
        template: Optional[str] = None,
    ) -> bool:
        """
        Register a kernel-native manifestation.

        For things like SETTINGS.md that are part of the kernel itself,
        not a plugin. The kernel provides a lambda that returns the data.

        Args:
            output: Filename (e.g., "SETTINGS.md")
            schema: Schema name from config/manifestation.yaml
            data_getter: Callable that returns section data dict
            frequency: "tick" | "on_change" | "manual"
            location: "root" | ".vibe" | custom path
            template: Optional Jinja2 template path for complex UIs

        Returns:
            True if registered successfully
        """
        # Validate schema exists
        if schema not in self._schemas:
            logger.warning(f"Unknown schema '{schema}' for {output}, using config_bidirectional")
            schema = "config_bidirectional"

        source = KernelSource(
            output=output,
            schema=schema,
            data_getter=data_getter,
            frequency=frequency,
            location=location,
            template=template,
        )

        self._kernel_sources[output] = source
        logger.info(f"Registered kernel source: {output} (schema: {schema})")
        return True

    def unregister_kernel_source(self, output: str) -> None:
        """Unregister a kernel-native source."""
        if output in self._kernel_sources:
            del self._kernel_sources[output]
            logger.debug(f"Unregistered kernel source: {output}")

    # =========================================================================
    # MANIFESTATION CYCLE (Called on kernel tick)
    # =========================================================================

    def tick(self) -> None:
        """
        Manifestation tick - called from kernel tick.

        BIDIRECTIONAL LOOP:
        1. SENSE: Check for @HUMAN changes, extract commands
        2. DISPATCH: Send commands to plugins/kernel
        3. MANIFEST: Render @LIVE sections
        """
        # Phase 1: SENSE - Check for user input
        self._process_user_input()

        # Phase 2: MANIFEST - Render all sources
        # Plugin manifestations
        for plugin_id, reg in self._registered.items():
            if reg.declaration.frequency != "tick":
                continue

            try:
                self._manifest_plugin(reg)
            except Exception as e:
                logger.error(f"Manifestation failed for {plugin_id}: {e}")

        # Kernel-native manifestations
        for output, source in self._kernel_sources.items():
            if source.frequency != "tick":
                continue

            try:
                self._manifest_kernel_source(source)
            except Exception as e:
                logger.error(f"Manifestation failed for {output}: {e}")

    def force_manifest(self, plugin_id: str) -> Optional[str]:
        """
        Force immediate manifestation of a single plugin.

        Used by cmd_opus_refresh and other manual triggers.
        Bypasses frequency check - manifests NOW.

        Args:
            plugin_id: Plugin to manifest (e.g., "opus_assistant")

        Returns:
            Rendered content string, or None if failed
        """
        if plugin_id not in self._registered:
            logger.warning(f"Plugin {plugin_id} not registered for manifestation")
            return None

        reg = self._registered[plugin_id]

        # Get output path
        if reg.declaration.location == "root":
            output_path = self._workspace / reg.declaration.output
        elif reg.declaration.location == ".vibe":
            output_path = self._workspace / ".vibe" / reg.declaration.output
        else:
            output_path = self._workspace / reg.declaration.location / reg.declaration.output

        # Get data from plugin
        try:
            data = reg.plugin_instance.get_manifestation_data()
        except Exception as e:
            logger.error(f"get_manifestation_data() failed for {plugin_id}: {e}")
            return None

        # Render with template if available
        if reg.declaration.template:
            content = self.render_with_template(reg.declaration.template, data)
            if content:
                # Write to file
                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(content, encoding="utf-8")
                    self._index.on_file_created(output_path)
                    logger.info(f"Force manifested: {output_path.name} ({len(content)} chars)")
                    return content
                except Exception as e:
                    logger.error(f"Failed to write manifestation: {e}")
                    return None

        # Schema-based rendering (fallback)
        if not output_path.exists():
            self.spawn(output_path, reg.declaration.schema, data)
            return output_path.read_text(encoding="utf-8") if output_path.exists() else None

        live_sections = self._format_data_for_sections(reg.declaration.schema, data)
        self.update_live_sections(output_path, live_sections)
        return output_path.read_text(encoding="utf-8") if output_path.exists() else None

    def _process_user_input(self) -> None:
        """
        BIDIRECTIONAL: Sense and process @HUMAN section changes.

        For each manifestation:
        1. Check if @HUMAN sections changed (ChangeDetector)
        2. Extract commands
        3. Dispatch to owner (plugin or kernel)
        4. Annotate results (Red/Green Pen)
        """
        # Check all indexed manifestations
        for path in self._index.all_manifestations():
            if not self._change_detector.should_process(path):
                continue

            # Extract commands from @HUMAN sections
            commands = self._change_detector.extract_commands(path)
            if not commands:
                continue

            logger.info(f"User input detected: {path.name} ({len(commands)} commands)")

            # Find owner and dispatch
            entity_id = self._index.find_by_path(path)
            for cmd in commands:
                self._dispatch_command(path, entity_id, cmd)

    def _dispatch_command(self, path: Path, entity_id: Optional[str], cmd: Dict[str, Any]) -> None:
        """
        Dispatch a command to its owner and annotate result.

        Tries plugin first, then kernel, then fails with Red Pen.
        """
        action = cmd.get("action", "")
        line = cmd.get("line", "")

        # Try plugin handler
        if entity_id and entity_id in self._registered:
            reg = self._registered[entity_id]
            if hasattr(reg.plugin_instance, "handle_command"):
                try:
                    result = reg.plugin_instance.handle_command(cmd)
                    self.annotate_success(path, line, f"Executed: {action}")
                    return
                except Exception as e:
                    self.annotate_error(path, line, str(e))
                    return

        # Try kernel handler
        if hasattr(self._kernel, "handle_command"):
            try:
                result = self._kernel.handle_command(cmd)
                self.annotate_success(path, line, f"Executed: {action}")
                return
            except Exception as e:
                self.annotate_error(path, line, str(e))
                return

        # No handler found
        self.annotate_error(path, line, f"Unknown command: {action}")

    def _manifest_plugin(self, reg: RegisteredManifestation) -> None:
        """Manifest a single plugin."""
        # Get output path
        if reg.declaration.location == "root":
            output_path = self._workspace / reg.declaration.output
        elif reg.declaration.location == ".vibe":
            output_path = self._workspace / ".vibe" / reg.declaration.output
        else:
            output_path = self._workspace / reg.declaration.location / reg.declaration.output

        # Get data from plugin
        try:
            data = reg.plugin_instance.get_manifestation_data()
        except Exception as e:
            logger.error(f"get_manifestation_data() failed for {reg.plugin_id}: {e}")
            data = {"status": f"ERROR: {e}"}

        # TEMPLATE RENDERING: If plugin has a Jinja2 template, use that
        if reg.declaration.template:
            self._manifest_with_template(output_path, reg.declaration.template, data)
            return

        # Check if file exists, spawn if not
        if not output_path.exists():
            self.spawn(output_path, reg.declaration.schema, data)
            return

        # Update @LIVE sections
        live_sections = self._format_data_for_sections(reg.declaration.schema, data)
        self.update_live_sections(output_path, live_sections)

    def _manifest_with_template(
        self,
        output_path: Path,
        template_path: str,
        data: Dict[str, Any],
    ) -> None:
        """
        Manifest using Jinja2 template (for complex UIs like OPUS.md).

        Template-based manifestations:
        1. Render entire document with Jinja2
        2. Preserve @HUMAN sections from existing file
        3. Write atomically

        The template has full control over document structure.
        @HUMAN sections are injected back after rendering.
        """
        # Render with template
        rendered = self.render_with_template(template_path, data)
        if rendered is None:
            logger.error(f"Template rendering failed: {template_path}")
            return

        # If file exists, preserve @HUMAN sections
        if output_path.exists():
            try:
                existing = output_path.read_text(encoding="utf-8")
                existing_sections = self._parse_sections(existing)

                # Find @HUMAN sections in existing file
                human_sections = {
                    sid: sec
                    for sid, sec in existing_sections.items()
                    if sec.owner in (SectionOwnership.HUMAN, SectionOwnership.AI)
                }

                # Inject preserved @HUMAN content into rendered output
                for sid, sec in human_sections.items():
                    marker = self.SECTION_START.format(id=sid, owner=sec.owner.value)
                    if marker in rendered:
                        # Replace template's placeholder with preserved content
                        pattern = re.escape(marker) + r"(.*?)" + re.escape(self.SECTION_END)
                        replacement = f"{marker}\n{sec.content}\n{self.SECTION_END}"
                        rendered = re.sub(pattern, replacement, rendered, flags=re.DOTALL)
            except Exception as e:
                logger.warning(f"Failed to preserve @HUMAN sections: {e}")

        # Write
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered, encoding="utf-8")
            self._index.on_file_created(output_path)

            # Update change detector hash
            human_content = self._change_detector._extract_human_sections(rendered)
            self._change_detector.update_hash(output_path, human_content)

            logger.debug(f"Manifested with template: {output_path.name}")
        except Exception as e:
            logger.error(f"Failed to write template manifestation: {e}")

    def _manifest_kernel_source(self, source: KernelSource) -> None:
        """Manifest a kernel-native source."""
        # Get output path
        if source.location == "root":
            output_path = self._workspace / source.output
        elif source.location == ".vibe":
            output_path = self._workspace / ".vibe" / source.output
        else:
            output_path = self._workspace / source.location / source.output

        # Get data from kernel lambda
        try:
            data = source.data_getter()
        except Exception as e:
            logger.error(f"data_getter() failed for {source.output}: {e}")
            data = {"status": {"error": str(e)}}

        # TEMPLATE RENDERING: If source has a Jinja2 template, use that
        if source.template:
            self._manifest_with_template(output_path, source.template, data)
            return

        # Check if file exists, spawn if not
        if not output_path.exists():
            self.spawn(output_path, source.schema, data)
            return

        # Update @LIVE sections
        live_sections = self._format_data_for_sections(source.schema, data)
        self.update_live_sections(output_path, live_sections)

    def _format_data_for_sections(self, schema: str, data: Dict[str, Any]) -> Dict[str, str]:
        """Format raw data into section content strings."""
        sections = self._schemas.get(schema, [])
        formatted: Dict[str, str] = {}

        for section in sections:
            if section.owner != SectionOwnership.LIVE:
                continue

            section_data = data.get(section.id)
            if section_data is None:
                continue

            # Format based on type
            if isinstance(section_data, dict):
                formatted[section.id] = self._format_table_from_dict(section.title, section_data)
            elif isinstance(section_data, list):
                formatted[section.id] = self._format_table_from_list(section.title, section_data)
            else:
                formatted[section.id] = f"## {section.title or section.id}\n\n{section_data}"

        return formatted

    def _format_table_from_dict(self, title: Optional[str], data: Dict[str, Any]) -> str:
        """
        Format dict as markdown table using Phoenix element_types config.

        Uses interface.yaml → element_types.table for styling.
        """
        config = self._get_element_type_config("table")
        sep = config.get("separator", "|")
        alignment = config.get("alignment", "left")

        # Alignment markers
        align_map = {"left": ":---", "center": ":---:", "right": "---:"}
        align_marker = align_map.get(alignment, "---")

        lines = []
        if title:
            lines.append(f"## {title}")
            lines.append("")

        lines.append(f"{sep} Key {sep} Value {sep}")
        lines.append(f"{sep} {align_marker} {sep} {align_marker} {sep}")
        for k, v in data.items():
            lines.append(f"{sep} {k} {sep} {v} {sep}")

        return "\n".join(lines)

    def _format_table_from_list(self, title: Optional[str], data: List[Any]) -> str:
        """
        Format list as markdown table using Phoenix element_types config.

        Uses interface.yaml → element_types.table for styling.
        """
        config = self._get_element_type_config("table")
        sep = config.get("separator", "|")
        alignment = config.get("alignment", "left")

        align_map = {"left": ":---", "center": ":---:", "right": "---:"}
        align_marker = align_map.get(alignment, "---")

        lines = []
        if title:
            lines.append(f"## {title}")
            lines.append("")

        if data and isinstance(data[0], dict):
            headers = list(data[0].keys())
            lines.append(f"{sep} " + f" {sep} ".join(headers) + f" {sep}")
            lines.append(f"{sep} " + f" {sep} ".join([align_marker] * len(headers)) + f" {sep}")
            for item in data:
                values = [str(item.get(h, "")) for h in headers]
                lines.append(f"{sep} " + f" {sep} ".join(values) + f" {sep}")
        else:
            lines.append(f"{sep} Value {sep}")
            lines.append(f"{sep} {align_marker} {sep}")
            for item in data:
                lines.append(f"{sep} {item} {sep}")

        return "\n".join(lines)

    # =========================================================================
    # JINJA2 TEMPLATE RENDERING (for complex manifestations like OPUS.md)
    # =========================================================================

    def _get_jinja_env(self):
        """
        Get or create Jinja2 environment.

        Lazy loading - only imports jinja2 when needed.
        Templates are loaded from workspace root.
        """
        global _jinja2_env
        if _jinja2_env is None:
            try:
                from jinja2 import Environment, FileSystemLoader, select_autoescape

                _jinja2_env = Environment(
                    loader=FileSystemLoader(str(self._workspace)),
                    autoescape=select_autoescape(["html", "xml"]),
                    trim_blocks=True,
                    lstrip_blocks=True,
                )
                logger.debug("Jinja2 environment initialized")
            except ImportError:
                logger.warning("Jinja2 not available, template rendering disabled")
                return None
        return _jinja2_env

    def render_with_template(self, template_path: str, data: Dict[str, Any]) -> Optional[str]:
        """
        Render manifestation using Jinja2 template.

        For complex manifestations like OPUS.md that need more than
        simple table formatting.

        Args:
            template_path: Path to .j2 template (relative to workspace)
            data: Context dict from get_manifestation_data()

        Returns:
            Rendered markdown string, or None if template not found
        """
        env = self._get_jinja_env()
        if env is None:
            return None

        try:
            template = env.get_template(template_path)
            rendered = template.render(**data)
            return rendered
        except Exception as e:
            logger.error(f"Template render failed: {template_path} - {e}")
            return None

    def _format_data_for_sections_with_template(
        self,
        schema: str,
        data: Dict[str, Any],
        template_path: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Format data using template OR schema-based formatting.

        If template_path is provided, renders entire document with Jinja2.
        Otherwise falls back to schema-based section formatting.
        """
        if template_path:
            rendered = self.render_with_template(template_path, data)
            if rendered:
                # For template-based rendering, return single "content" section
                return {"_template_content": rendered}

        # Fall back to schema-based formatting
        return self._format_data_for_sections(schema, data)

    # =========================================================================
    # RED PEN: In-file annotations (GAD-000 Transparency)
    # =========================================================================

    def annotate_error(self, path: Path, line_content: str, error_msg: str) -> bool:
        """
        THE RED PEN - Annotate error in file.

        "Invisible = Doesn't Exist" (GAD-000)
        User must SEE errors in the file, not just logs.
        """
        try:
            content = path.read_text(encoding="utf-8")
            annotation = f"<!-- @ERROR: {error_msg} -->"

            # Find the line and add annotation after it
            if line_content in content and annotation not in content:
                content = content.replace(
                    line_content,
                    f"{line_content}\n{annotation}",
                )
                path.write_text(content, encoding="utf-8")
                logger.debug(f"Red Pen: {path.name} - {error_msg}")
                return True
            return False
        except Exception as e:
            logger.error(f"annotate_error failed: {e}")
            return False

    def annotate_success(self, path: Path, line_content: str, result_msg: str) -> bool:
        """
        THE GREEN PEN - Annotate success in file.

        Confirms command execution to user.
        """
        try:
            content = path.read_text(encoding="utf-8")
            timestamp = datetime.utcnow().strftime("%H:%M:%S")
            annotation = f"<!-- @OK: {result_msg} ({timestamp}) -->"

            if line_content in content and "<!-- @OK" not in content.split(line_content)[1][:100]:
                content = content.replace(
                    line_content,
                    f"{line_content}\n{annotation}",
                )
                path.write_text(content, encoding="utf-8")
                logger.debug(f"Green Pen: {path.name} - {result_msg}")
                return True
            return False
        except Exception as e:
            logger.error(f"annotate_success failed: {e}")
            return False

    # =========================================================================
    # SPAWN: Create new manifestation
    # =========================================================================

    def spawn(self, path: Path, schema: str, initial_data: Dict[str, Any]) -> bool:
        """Create a new manifestation from a schema."""
        if schema not in self._schemas:
            logger.error(f"Unknown schema: {schema}")
            return False

        sections = self._schemas[schema]
        lines: List[str] = []

        # Header
        entity_id = path.stem.lower()
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        lines.extend(
            [
                "<!--",
                f"  @MANIFEST: {entity_id}",
                "  @TYPE: bidirectional",
                f"  @SCHEMA: {schema}",
                "  @VERSION: 1.0",
                f"  @GENERATED: {timestamp}",
                "-->",
                f"# {path.stem.upper()}",
                "",
            ]
        )

        # Sections
        for section in sections:
            marker_start = self.SECTION_START.format(id=section.id, owner=section.owner.value)
            marker_end = self.SECTION_END

            lines.append(marker_start)

            if section.title:
                lines.append(f"## {section.title}")
                lines.append("")

            # Content based on owner
            if section.owner == SectionOwnership.LIVE:
                section_data = initial_data.get(section.id, "_No data_")
                if isinstance(section_data, dict):
                    # Use table formatter for dicts
                    table = self._format_table_from_dict(None, section_data)
                    lines.append(table)
                elif isinstance(section_data, list):
                    # Use table formatter for list of dicts, bullet list for simple items
                    if section_data and isinstance(section_data[0], dict):
                        table = self._format_table_from_list(None, section_data)
                        lines.append(table)
                    else:
                        for item in section_data[:10]:
                            lines.append(f"- {item}")
                else:
                    lines.append(str(section_data))
            elif section.owner == SectionOwnership.HUMAN:
                lines.append(f"> Write your {section.id} here.")
                lines.append("")
                lines.append(f"_No pending {section.id}._")
            else:
                lines.append(f"_Empty {section.id}._")

            lines.append("")
            lines.append(marker_end)
            lines.append("")

        content = "\n".join(lines)

        # Write
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            self._index.on_file_created(path)
            logger.info(f"Spawned: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to spawn {path}: {e}")
            return False

    # =========================================================================
    # UPDATE: Merge new @LIVE content with preserved @HUMAN
    # =========================================================================

    def update_live_sections(self, path: Path, sections: Dict[str, str]) -> bool:
        """Update @LIVE sections, preserving @HUMAN sections exactly."""
        if not path.exists():
            return False

        try:
            content = path.read_text(encoding="utf-8")
            parsed = self._parse_sections(content)

            new_lines: List[str] = []

            # Preserve header
            header_end = content.find("-->")
            if header_end != -1:
                new_lines.append(content[: header_end + 3])
            else:
                entity_id = path.stem.lower()
                timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                new_lines.extend(
                    [
                        "<!--",
                        f"  @MANIFEST: {entity_id}",
                        f"  @GENERATED: {timestamp}",
                        "-->",
                    ]
                )

            # Preserve title
            title_match = re.search(r"-->\s*(#\s+.+?)(?:\n|$)", content)
            if title_match:
                new_lines.append("")
                new_lines.append(title_match.group(1))
            new_lines.append("")

            # Rebuild sections
            for section_id, section in parsed.items():
                marker_start = self.SECTION_START.format(id=section_id, owner=section.owner.value)
                marker_end = self.SECTION_END

                new_lines.append(marker_start)

                if section.owner in (SectionOwnership.HUMAN, SectionOwnership.AI):
                    # PRESERVE exactly
                    new_lines.append(section.content)
                elif section_id in sections:
                    # UPDATE with new content
                    new_lines.append(sections[section_id])
                else:
                    new_lines.append(section.content)

                new_lines.append(marker_end)
                new_lines.append("")

            merged = "\n".join(new_lines)
            path.write_text(merged, encoding="utf-8")

            # Update hash
            human_content = self._change_detector._extract_human_sections(merged)
            self._change_detector.update_hash(path, human_content)

            return True
        except Exception as e:
            logger.error(f"Failed to update {path}: {e}")
            return False

    def _parse_sections(self, content: str) -> Dict[str, Section]:
        """Parse sections from content."""
        sections: Dict[str, Section] = {}
        seen_ids: Set[str] = set()

        start_pattern = r"<!--\s*@SECTION:(\w+)\s+OWNER:(\w+)\s*-->"
        end_pattern = r"<!--\s*/@SECTION\s*-->"

        starts = list(re.finditer(start_pattern, content, re.IGNORECASE))

        for i, match in enumerate(starts):
            section_id = match.group(1)
            owner_str = match.group(2)

            try:
                owner = SectionOwnership(owner_str.lower())
            except ValueError:
                owner = SectionOwnership.LIVE

            start_pos = match.end()

            end_match = re.search(end_pattern, content[start_pos:], re.IGNORECASE)
            if end_match:
                end_pos = start_pos + end_match.start()
            elif i + 1 < len(starts):
                end_pos = starts[i + 1].start()
            else:
                end_pos = len(content)

            section_content = content[start_pos:end_pos].strip()

            final_id = section_id
            if section_id in seen_ids:
                dup_count = 1
                while f"{section_id}_dup{dup_count}" in seen_ids:
                    dup_count += 1
                final_id = f"{section_id}_dup{dup_count}"

            seen_ids.add(final_id)

            title = None
            title_match = re.match(r"##\s+(.+?)(?:\n|$)", section_content)
            if title_match:
                title = title_match.group(1)

            sections[final_id] = Section(
                id=final_id,
                owner=owner,
                content=section_content,
                title=title,
            )

        return sections

    def read_structure(self, path: Path) -> Dict[str, Section]:
        """Parse a manifestation into sections."""
        if not path.exists():
            return {}
        try:
            content = path.read_text(encoding="utf-8")
            return self._parse_sections(content)
        except Exception:
            return {}

    def read_header(self, path: Path) -> Optional[ManifestHeader]:
        """Extract manifest header from a file."""
        if not path.exists():
            return None

        try:
            content = path.read_text(encoding="utf-8")
            header_area = content[:500]

            entity_match = re.search(r"@MANIFEST:\s*(\S+)", header_area)
            if not entity_match:
                return None

            type_match = re.search(r"@TYPE:\s*(\S+)", header_area)
            schema_match = re.search(r"@SCHEMA:\s*(\S+)", header_area)
            version_match = re.search(r"@VERSION:\s*(\S+)", header_area)
            generated_match = re.search(r"@GENERATED:\s*(\S+)", header_area)

            type_str = type_match.group(1) if type_match else "bidirectional"
            try:
                manifest_type = ManifestationType(type_str)
            except ValueError:
                manifest_type = ManifestationType.BIDIRECTIONAL

            return ManifestHeader(
                entity_id=entity_match.group(1),
                schema=schema_match.group(1) if schema_match else "unknown",
                version=version_match.group(1) if version_match else "1.0",
                manifest_type=manifest_type,
                generated=generated_match.group(1) if generated_match else "",
            )
        except Exception:
            return None

    def render_section_error(self, section_id: str, error: Exception, trace_id: str) -> str:
        """Generate error placeholder for crashed section."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"""<!-- @RENDER_ERROR
  section: {section_id}
  error: "{str(error)[:100]}"
  timestamp: {timestamp}
  trace_id: {trace_id}
-->

**Section unavailable** - {section_id} failed to render.
See trace_id `{trace_id}` for details."""

    # =========================================================================
    # SCHEMA LOADING
    # =========================================================================

    def _load_schemas(self) -> None:
        """Load manifestation schemas from config/manifestation.yaml."""
        import yaml

        schema_path = self._workspace / "config/manifestation.yaml"
        if not schema_path.exists():
            logger.warning(f"Schema file not found: {schema_path}")
            return

        try:
            content = schema_path.read_text(encoding="utf-8")
            docs = list(yaml.safe_load_all(content))

            for doc in docs:
                if not isinstance(doc, dict):
                    continue

                for schema_name, schema_def in doc.items():
                    if schema_name.startswith("_"):
                        continue
                    if not isinstance(schema_def, dict):
                        continue

                    sections = []
                    for sec in schema_def.get("sections", []):
                        owner_str = sec.get("owner", "live")
                        try:
                            owner = SectionOwnership(owner_str)
                        except ValueError:
                            owner = SectionOwnership.LIVE

                        sections.append(
                            SchemaSection(
                                id=sec.get("id", "unknown"),
                                owner=owner,
                                title=sec.get("title"),
                                required=sec.get("required", False),
                                description=sec.get("description", ""),
                            )
                        )

                    self._schemas[schema_name] = sections

            logger.info(f"Loaded {len(self._schemas)} schemas")
        except Exception as e:
            logger.error(f"Failed to load schemas: {e}")

    # =========================================================================
    # STATUS
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get manifestation service status."""
        return {
            "registered_plugins": list(self._registered.keys()),
            "kernel_sources": list(self._kernel_sources.keys()),
            "schemas_loaded": list(self._schemas.keys()),
            "manifestations_indexed": len(self._index.all_manifestations()),
        }
