"""Interface Configuration - UI Rendering System.

This config defines HOW the UI renders markdown files:
- Which renderers are enabled
- Refresh intervals per renderer
- Document types (readonly vs bidirectional)
- Custom renderers (fractal - agents can add their own!)

Philosophy:
- InterfacePlugin is the "Window Manager" - sole authority for UI
- Config drives behavior, no hardcoding
- Fractal: broker agent wants bitcoin UI? Add to custom_renderers
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class RendererConfig:
    """Configuration for a single renderer."""

    name: str
    enabled: bool = True
    output: str = ""  # Output filename (e.g., "AGENTS.md")
    template: Optional[str] = None  # Template file (optional)
    doc_type: str = "readonly"  # readonly or bidirectional
    interval: int = 0  # Refresh interval in seconds (0 = every tick)
    data_source: Optional[str] = None  # For custom renderers

    def __post_init__(self):
        if not self.output:
            self.output = f"{self.name.upper()}.md"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "output": self.output,
            "template": self.template,
            "doc_type": self.doc_type,
            "interval": self.interval,
            "data_source": self.data_source,
        }

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "RendererConfig":
        return cls(
            name=name,
            enabled=data.get("enabled", True),
            output=data.get("output", f"{name.upper()}.md"),
            template=data.get("template"),
            doc_type=data.get("doc_type", "readonly"),
            interval=data.get("interval", 0),
            data_source=data.get("data_source"),
        )


@dataclass
class HeaderConfig:
    """Header settings for rendered documents."""

    show_nav: bool = True
    show_timestamp: bool = True
    show_kernel_status: bool = True
    generator_name: str = "InterfacePlugin"
    quick_start_command: str = "python -m vibe_core.cli boot"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "show_nav": self.show_nav,
            "show_timestamp": self.show_timestamp,
            "show_kernel_status": self.show_kernel_status,
            "generator_name": self.generator_name,
            "quick_start_command": self.quick_start_command,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HeaderConfig":
        return cls(
            show_nav=data.get("show_nav", True),
            show_timestamp=data.get("show_timestamp", True),
            show_kernel_status=data.get("show_kernel_status", True),
            generator_name=data.get("generator_name", "InterfacePlugin"),
            quick_start_command=data.get("quick_start_command", "python -m vibe_core.cli boot"),
        )


@dataclass
class DocumentTypeConfig:
    """Configuration for a document type."""

    preserve_user_content: bool = False
    add_header: bool = True
    user_section_marker: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "preserve_user_content": self.preserve_user_content,
            "add_header": self.add_header,
        }
        if self.user_section_marker:
            result["user_section_marker"] = self.user_section_marker
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentTypeConfig":
        return cls(
            preserve_user_content=data.get("preserve_user_content", False),
            add_header=data.get("add_header", True),
            user_section_marker=data.get("user_section_marker"),
        )


@dataclass
class InterfaceConfig:
    """
    Complete interface configuration.

    Auto-discovered by SectionLoader → loads from config/interface.yaml

    Fractal Design:
    - System renderers: Built-in (readme, agents, operations, etc.)
    - Custom renderers: User/agent defined (broker_btc, weather, etc.)

    Example usage:
        config = InterfaceConfig.from_yaml("config/interface.yaml")
        for name, renderer in config.get_enabled_renderers().items():
            if renderer.interval > 0:
                schedule_at_interval(renderer.interval)
    """

    section_id = "interface"

    templates_dir: str = "knowledge/interface/templates"
    default_interval: int = 0

    # System renderers (built-in)
    renderers: Dict[str, RendererConfig] = field(default_factory=dict)

    # Custom renderers (user/agent defined) - FRACTAL!
    custom_renderers: Dict[str, RendererConfig] = field(default_factory=dict)

    # Header settings
    header: HeaderConfig = field(default_factory=HeaderConfig)

    # Document type definitions
    doc_types: Dict[str, DocumentTypeConfig] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize default doc types if none provided."""
        if not self.doc_types:
            self.doc_types = {
                "readonly": DocumentTypeConfig(
                    preserve_user_content=False,
                    add_header=True,
                ),
                "bidirectional": DocumentTypeConfig(
                    preserve_user_content=True,
                    add_header=True,
                    user_section_marker="## 💬",
                ),
            }

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

    def get_doc_type_config(self, doc_type: str) -> DocumentTypeConfig:
        """Get config for a document type."""
        return self.doc_types.get(doc_type, DocumentTypeConfig())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "templates_dir": self.templates_dir,
            "default_interval": self.default_interval,
            "renderers": {k: v.to_dict() for k, v in self.renderers.items()},
            "custom_renderers": {k: v.to_dict() for k, v in self.custom_renderers.items()},
            "header": self.header.to_dict(),
            "doc_types": {k: v.to_dict() for k, v in self.doc_types.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InterfaceConfig":
        # Parse system renderers
        renderers_data = data.get("renderers", {})
        renderers = {k: RendererConfig.from_dict(k, v) for k, v in renderers_data.items()}

        # Parse custom renderers
        custom_data = data.get("custom_renderers", {})
        custom_renderers = {k: RendererConfig.from_dict(k, v) for k, v in custom_data.items()}

        # Parse doc types
        doc_types_data = data.get("doc_types", {})
        doc_types = {k: DocumentTypeConfig.from_dict(v) for k, v in doc_types_data.items()}

        return cls(
            templates_dir=data.get("templates_dir", "knowledge/interface/templates"),
            default_interval=data.get("default_interval", 0),
            renderers=renderers,
            custom_renderers=custom_renderers,
            header=HeaderConfig.from_dict(data.get("header", {})),
            doc_types=doc_types if doc_types else {},
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
            "envoy": RendererConfig(name="envoy", output="ENVOY.md", doc_type="bidirectional", interval=5),
            "settings": RendererConfig(name="settings", output="SETTINGS.md", doc_type="bidirectional", interval=5),
            "rag": RendererConfig(name="rag", output="RAG.md", interval=120),
            "git": RendererConfig(name="git", output="GIT.md", interval=30),
            "tasks": RendererConfig(name="tasks", output="TASKS.md", interval=10),
            "ephemeral": RendererConfig(name="ephemeral", output="EPHEMERAL.md", interval=60),
        },
        custom_renderers={},
        header=HeaderConfig(),
    )
