"""CLI Configuration - Fractal CLI System settings from cli.yaml."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xc17e3e2d"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class OutputConfig:
    """CLI output format configuration."""

    default_format: str = "human"  # human, json, yaml
    json_indent: int = 2
    yaml_sort_keys: bool = False
    rich_enabled: bool = True  # Use Rich library for human output


@dataclass
class ObserveConfig:
    """Observability/introspection configuration."""

    enabled: bool = True
    auto_discover: bool = True  # Auto-discover monitors from plugins
    refresh_interval_ms: int = 1000  # For streaming observe


@dataclass
class NamespacesConfig:
    """CLI namespace configuration."""

    enabled: List[str] = field(default_factory=list)  # Empty = all enabled
    disabled: List[str] = field(default_factory=list)  # Explicit disables


@dataclass
class CLIConfig:
    """
    CLI Configuration - The Fractal CLI System settings.

    Loaded from config/cli.yaml via Phoenix auto-discovery.
    """

    section_id: str = "cli"
    source_file: str = "cli.yaml"

    output: OutputConfig = field(default_factory=OutputConfig)
    observe: ObserveConfig = field(default_factory=ObserveConfig)
    namespaces: NamespacesConfig = field(default_factory=NamespacesConfig)

    # Feature flags
    enabled: bool = True
    debug: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CLIConfig":
        """Create CLIConfig from dictionary (YAML data)."""
        output_data = data.get("output", {})
        output = OutputConfig(
            default_format=output_data.get("default_format", "human"),
            json_indent=output_data.get("json_indent", 2),
            yaml_sort_keys=output_data.get("yaml_sort_keys", False),
            rich_enabled=output_data.get("rich_enabled", True),
        )

        observe_data = data.get("observe", {})
        observe = ObserveConfig(
            enabled=observe_data.get("enabled", True),
            auto_discover=observe_data.get("auto_discover", True),
            refresh_interval_ms=observe_data.get("refresh_interval_ms", 1000),
        )

        namespaces_data = data.get("namespaces", {})
        namespaces = NamespacesConfig(
            enabled=namespaces_data.get("enabled", []),
            disabled=namespaces_data.get("disabled", []),
        )

        return cls(
            output=output,
            observe=observe,
            namespaces=namespaces,
            enabled=data.get("enabled", True),
            debug=data.get("debug", False),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "enabled": self.enabled,
            "debug": self.debug,
            "output": {
                "default_format": self.output.default_format,
                "json_indent": self.output.json_indent,
                "yaml_sort_keys": self.output.yaml_sort_keys,
                "rich_enabled": self.output.rich_enabled,
            },
            "observe": {
                "enabled": self.observe.enabled,
                "auto_discover": self.observe.auto_discover,
                "refresh_interval_ms": self.observe.refresh_interval_ms,
            },
            "namespaces": {
                "enabled": self.namespaces.enabled,
                "disabled": self.namespaces.disabled,
            },
        }

    def validate(self) -> List[str]:
        """Validate configuration."""
        errors = []

        if self.output.default_format not in ("human", "json", "yaml"):
            errors.append(f"Invalid output.default_format: {self.output.default_format}")

        if self.output.json_indent < 0:
            errors.append("output.json_indent must be non-negative")

        if self.observe.refresh_interval_ms < 100:
            errors.append("observe.refresh_interval_ms must be >= 100")

        return errors
