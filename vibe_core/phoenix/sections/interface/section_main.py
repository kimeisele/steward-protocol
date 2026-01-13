"""Interface Configuration - UI Rendering System.

This config defines HOW the UI renders markdown files:
- Which renderers are enabled
- Refresh intervals per renderer
- UI element types, layouts, and dependencies
- Section ownership (LIVE/AI/HUMAN)
- Custom renderers (fractal - agents can add their own!)

Philosophy:
- InterfacePlugin is the "Window Manager" - sole authority for UI
- Config drives behavior, no hardcoding
- Fractal: broker agent wants bitcoin UI? Add to custom_renderers
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x9031c52a"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# =============================================================================
# SECTION CONFIG (per-section ownership)
# =============================================================================


@dataclass
class SectionConfig:
    """Configuration for a document section."""

    id: str
    owner: str = "live"  # live | ai | human
    source: Optional[str] = None  # callable path for live sections (e.g., "kernel.status")
    element_type: Optional[str] = None  # table | list | status | metric | terminal
    template: Optional[str] = None  # custom template override

    def to_dict(self) -> Dict[str, Any]:
        result = {"id": self.id, "owner": self.owner}
        if self.source:
            result["source"] = self.source
        if self.element_type:
            result["element_type"] = self.element_type
        if self.template:
            result["template"] = self.template
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SectionConfig":
        return cls(
            id=data.get("id", ""),
            owner=data.get("owner", "live"),
            source=data.get("source"),
            element_type=data.get("element_type"),
            template=data.get("template"),
        )


# =============================================================================
# RENDERER CONFIG
# =============================================================================


@dataclass
class RendererConfig:
    """Configuration for a single renderer/document."""

    name: str
    enabled: bool = True
    output: str = ""  # Output filename (e.g., "AGENTS.md")
    template: Optional[str] = None  # Template file (optional)
    view_type: str = "docs"  # docs | dashboard | terminal | workspace | workflow
    interval: int = 0  # Refresh interval in seconds (0 = every tick)
    data_source: Optional[str] = None  # For custom renderers
    sections: List[SectionConfig] = field(default_factory=list)

    def __post_init__(self):
        if not self.output:
            self.output = f"{self.name.upper()}.md"

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "enabled": self.enabled,
            "output": self.output,
            "view_type": self.view_type,
            "interval": self.interval,
        }
        if self.template:
            result["template"] = self.template
        if self.data_source:
            result["data_source"] = self.data_source
        if self.sections:
            result["sections"] = [s.to_dict() for s in self.sections]
        return result

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "RendererConfig":
        sections_data = data.get("sections", [])
        sections = [SectionConfig.from_dict(s) for s in sections_data]

        return cls(
            name=name,
            enabled=data.get("enabled", True),
            output=data.get("output", f"{name.upper()}.md"),
            template=data.get("template"),
            view_type=data.get("view_type", "docs"),
            interval=data.get("interval", 0),
            data_source=data.get("data_source"),
            sections=sections,
        )


# =============================================================================
# FORMATTING CONFIG
# =============================================================================


@dataclass
class FormattingConfig:
    """Time and date formatting settings."""

    timezone: str = "UTC"
    date_format: str = "%Y-%m-%d"
    time_format: str = "%H:%M:%S"
    datetime_format: str = "%Y-%m-%d %H:%M:%S"
    relative_time: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timezone": self.timezone,
            "date_format": self.date_format,
            "time_format": self.time_format,
            "datetime_format": self.datetime_format,
            "relative_time": self.relative_time,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FormattingConfig":
        return cls(
            timezone=data.get("timezone", "UTC"),
            date_format=data.get("date_format", "%Y-%m-%d"),
            time_format=data.get("time_format", "%H:%M:%S"),
            datetime_format=data.get("datetime_format", "%Y-%m-%d %H:%M:%S"),
            relative_time=data.get("relative_time", True),
        )


# =============================================================================
# UI ELEMENT TYPE CONFIG
# =============================================================================


@dataclass
class ElementTypeConfig:
    """Configuration for a UI element type."""

    name: str
    settings: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return self.settings

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "ElementTypeConfig":
        return cls(name=name, settings=data)


# =============================================================================
# LAYOUT CONFIG
# =============================================================================


@dataclass
class LayoutConfig:
    """Configuration for a document layout."""

    name: str
    has_header: bool = True
    has_footer: bool = True
    has_nav: bool = True
    sections: List[str] = field(default_factory=list)
    columns: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "has_header": self.has_header,
            "has_footer": self.has_footer,
            "has_nav": self.has_nav,
            "sections": self.sections,
            "columns": self.columns,
        }

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "LayoutConfig":
        return cls(
            name=name,
            has_header=data.get("has_header", True),
            has_footer=data.get("has_footer", True),
            has_nav=data.get("has_nav", True),
            sections=data.get("sections", []),
            columns=data.get("columns", 1),
        )


# =============================================================================
# OWNERSHIP TYPE CONFIG
# =============================================================================


@dataclass
class OwnershipTypeConfig:
    """Configuration for section ownership type."""

    name: str
    writable_by: str = "system"  # system | ai | human
    preserve_on_render: bool = False
    refresh_on_tick: bool = True
    marker_start: str = ""
    marker_end: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "writable_by": self.writable_by,
            "preserve_on_render": self.preserve_on_render,
            "refresh_on_tick": self.refresh_on_tick,
            "marker_start": self.marker_start,
            "marker_end": self.marker_end,
        }

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "OwnershipTypeConfig":
        return cls(
            name=name,
            writable_by=data.get("writable_by", "system"),
            preserve_on_render=data.get("preserve_on_render", False),
            refresh_on_tick=data.get("refresh_on_tick", True),
            marker_start=data.get("marker_start", ""),
            marker_end=data.get("marker_end", ""),
        )


# =============================================================================
# VIEW TYPE CONFIG
# =============================================================================


@dataclass
class ViewTypeConfig:
    """Configuration for a view/window type."""

    name: str
    layout: str = "fullpage"
    editable: bool = False
    auto_refresh: bool = False
    refresh_interval: int = 30

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layout": self.layout,
            "editable": self.editable,
            "auto_refresh": self.auto_refresh,
            "refresh_interval": self.refresh_interval,
        }

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "ViewTypeConfig":
        return cls(
            name=name,
            layout=data.get("layout", "fullpage"),
            editable=data.get("editable", False),
            auto_refresh=data.get("auto_refresh", False),
            refresh_interval=data.get("refresh_interval", 30),
        )


# =============================================================================
# DEPENDENCY CONFIG
# =============================================================================


@dataclass
class DependencyConfig:
    """Configuration for UI element dependency."""

    name: str
    requires: List[str] = field(default_factory=list)
    fallback: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"requires": self.requires, "fallback": self.fallback}

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "DependencyConfig":
        return cls(
            name=name,
            requires=data.get("requires", []),
            fallback=data.get("fallback", ""),
        )


# =============================================================================
# HEADER CONFIG
# =============================================================================


@dataclass
class HeaderConfig:
    """Header settings for rendered documents."""

    show_nav: bool = True
    show_timestamp: bool = True
    show_kernel_status: bool = True
    generator_name: str = "InterfacePlugin"
    nav_docs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "show_nav": self.show_nav,
            "show_timestamp": self.show_timestamp,
            "show_kernel_status": self.show_kernel_status,
            "generator_name": self.generator_name,
            "nav_docs": self.nav_docs,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HeaderConfig":
        return cls(
            show_nav=data.get("show_nav", True),
            show_timestamp=data.get("show_timestamp", True),
            show_kernel_status=data.get("show_kernel_status", True),
            generator_name=data.get("generator_name", "InterfacePlugin"),
            nav_docs=data.get("nav_docs", []),
        )


# =============================================================================
# FOOTER CONFIG
# =============================================================================


@dataclass
class FooterConfig:
    """Footer settings for rendered documents."""

    show_generator: bool = True
    show_timestamp: bool = True
    format: str = "*Generated by {generator} | {timestamp}*"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "show_generator": self.show_generator,
            "show_timestamp": self.show_timestamp,
            "format": self.format,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FooterConfig":
        return cls(
            show_generator=data.get("show_generator", True),
            show_timestamp=data.get("show_timestamp", True),
            format=data.get("format", "*Generated by {generator} | {timestamp}*"),
        )


# =============================================================================
# MAIN INTERFACE CONFIG
# =============================================================================


@dataclass
class InterfaceConfig:
    """
    Complete interface configuration.

    Auto-discovered by SectionLoader → loads from config/interface.yaml

    Fractal Design:
    - System renderers: Built-in (readme, agents, operations, etc.)
    - Custom renderers: User/agent defined (broker_btc, weather, etc.)
    - Section ownership: LIVE/AI/HUMAN per section
    - Element types: table, list, status, metric, terminal, nav
    - Layouts: fullpage, content_only, dashboard, terminal
    - View types: docs, dashboard, terminal, workspace, workflow
    """

    section_id = "interface"

    templates_dir: str = "knowledge/interface/templates"
    default_interval: int = 0

    # Global variables (available in all templates)
    variables: Dict[str, Any] = field(default_factory=dict)

    # Formatting settings
    formatting: FormattingConfig = field(default_factory=FormattingConfig)

    # UI element types
    element_types: Dict[str, ElementTypeConfig] = field(default_factory=dict)

    # Layout types
    layouts: Dict[str, LayoutConfig] = field(default_factory=dict)

    # Ownership types (LIVE/AI/HUMAN)
    ownership_types: Dict[str, OwnershipTypeConfig] = field(default_factory=dict)

    # View types
    view_types: Dict[str, ViewTypeConfig] = field(default_factory=dict)

    # Dependencies
    dependencies: Dict[str, DependencyConfig] = field(default_factory=dict)

    # System renderers (built-in)
    renderers: Dict[str, RendererConfig] = field(default_factory=dict)

    # Custom renderers (user/agent defined) - FRACTAL!
    custom_renderers: Dict[str, RendererConfig] = field(default_factory=dict)

    # Header settings
    header: HeaderConfig = field(default_factory=HeaderConfig)

    # Footer settings
    footer: FooterConfig = field(default_factory=FooterConfig)

    # Default templates per element type
    default_templates: Dict[str, str] = field(default_factory=dict)

    def get_renderer(self, name: str) -> Optional[RendererConfig]:
        """Get a renderer by name (system or custom)."""
        if name in self.renderers:
            return self.renderers[name]
        return self.custom_renderers.get(name)

    def get_enabled_renderers(self) -> Dict[str, RendererConfig]:
        """Get all enabled renderers (system + custom)."""
        result = {}
        for name, config in self.renderers.items():
            if config.enabled:
                result[name] = config
        for name, config in self.custom_renderers.items():
            if config.enabled:
                result[name] = config
        return result

    def list_renderers(self) -> List[str]:
        """List all renderer names."""
        return list(self.renderers.keys()) + list(self.custom_renderers.keys())

    def add_custom_renderer(self, name: str, config: RendererConfig) -> None:
        """Add a custom renderer (fractal - agents call this)."""
        self.custom_renderers[name] = config

    def remove_custom_renderer(self, name: str) -> bool:
        """Remove a custom renderer."""
        if name in self.custom_renderers:
            del self.custom_renderers[name]
            return True
        return False

    def get_ownership_config(self, owner: str) -> Optional[OwnershipTypeConfig]:
        """Get ownership type config."""
        return self.ownership_types.get(owner)

    def get_layout(self, name: str) -> Optional[LayoutConfig]:
        """Get layout config."""
        return self.layouts.get(name)

    def get_view_type(self, name: str) -> Optional[ViewTypeConfig]:
        """Get view type config."""
        return self.view_types.get(name)

    def get_element_type(self, name: str) -> Optional[ElementTypeConfig]:
        """Get element type config."""
        return self.element_types.get(name)

    def get_dependency(self, name: str) -> Optional[DependencyConfig]:
        """Get dependency config."""
        return self.dependencies.get(name)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "templates_dir": self.templates_dir,
            "default_interval": self.default_interval,
            "variables": self.variables,
            "formatting": self.formatting.to_dict(),
            "element_types": {k: v.to_dict() for k, v in self.element_types.items()},
            "layouts": {k: v.to_dict() for k, v in self.layouts.items()},
            "ownership_types": {k: v.to_dict() for k, v in self.ownership_types.items()},
            "view_types": {k: v.to_dict() for k, v in self.view_types.items()},
            "dependencies": {k: v.to_dict() for k, v in self.dependencies.items()},
            "renderers": {k: v.to_dict() for k, v in self.renderers.items()},
            "custom_renderers": {k: v.to_dict() for k, v in self.custom_renderers.items()},
            "header": self.header.to_dict(),
            "footer": self.footer.to_dict(),
            "default_templates": self.default_templates,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InterfaceConfig":
        # Parse renderers
        renderers_data = data.get("renderers", {})
        renderers = {k: RendererConfig.from_dict(k, v) for k, v in renderers_data.items()}

        # Parse custom renderers
        custom_data = data.get("custom_renderers", {})
        custom_renderers = {k: RendererConfig.from_dict(k, v) for k, v in custom_data.items()}

        # Parse element types
        element_types_data = data.get("element_types", {})
        element_types = {k: ElementTypeConfig.from_dict(k, v) for k, v in element_types_data.items()}

        # Parse layouts
        layouts_data = data.get("layouts", {})
        layouts = {k: LayoutConfig.from_dict(k, v) for k, v in layouts_data.items()}

        # Parse ownership types
        ownership_data = data.get("ownership_types", {})
        ownership_types = {k: OwnershipTypeConfig.from_dict(k, v) for k, v in ownership_data.items()}

        # Parse view types
        view_types_data = data.get("view_types", {})
        view_types = {k: ViewTypeConfig.from_dict(k, v) for k, v in view_types_data.items()}

        # Parse dependencies
        deps_data = data.get("dependencies", {})
        dependencies = {k: DependencyConfig.from_dict(k, v) for k, v in deps_data.items()}

        return cls(
            templates_dir=data.get("templates_dir", "knowledge/interface/templates"),
            default_interval=data.get("default_interval", 0),
            variables=data.get("variables", {}),
            formatting=FormattingConfig.from_dict(data.get("formatting", {})),
            element_types=element_types,
            layouts=layouts,
            ownership_types=ownership_types,
            view_types=view_types,
            dependencies=dependencies,
            renderers=renderers,
            custom_renderers=custom_renderers,
            header=HeaderConfig.from_dict(data.get("header", {})),
            footer=FooterConfig.from_dict(data.get("footer", {})),
            default_templates=data.get("default_templates", {}),
        )

    @classmethod
    def from_yaml(cls, path: str) -> "InterfaceConfig":
        """Load config from YAML file."""
        config_path = Path(path)
        if config_path.exists():
            data = yaml.safe_load(config_path.read_text())
            return cls.from_dict(data or {})
        return get_default_interface_config()


def get_default_interface_config() -> InterfaceConfig:
    """Get default interface config with standard renderers."""
    return InterfaceConfig(
        templates_dir="knowledge/interface/templates",
        default_interval=0,
        renderers={
            "readme": RendererConfig(name="readme", output="README.md", interval=60),
            "index": RendererConfig(name="index", output="INDEX.md", interval=60),
            "help": RendererConfig(name="help", output="HELP.md", interval=300),
            "agents": RendererConfig(name="agents", output="AGENTS.md", interval=30),
            "citymap": RendererConfig(name="citymap", output="CITYMAP.md", interval=60),
            "operations": RendererConfig(name="operations", output="OPERATIONS.md", interval=10),
            "dashboard": RendererConfig(name="dashboard", output="DASHBOARD.md", interval=30),
            "envoy": RendererConfig(name="envoy", output="ENVOY.md", view_type="terminal", interval=5),
            "settings": RendererConfig(name="settings", output="SETTINGS.md", view_type="terminal", interval=5),
            "rag": RendererConfig(name="rag", output="RAG.md", interval=120),
            "git": RendererConfig(name="git", output="GIT.md", interval=30),
            "tasks": RendererConfig(name="tasks", output="TASKS.md", interval=10),
            "ephemeral": RendererConfig(name="ephemeral", output="EPHEMERAL.md", interval=60),
        },
        custom_renderers={},
        header=HeaderConfig(),
        footer=FooterConfig(),
    )
