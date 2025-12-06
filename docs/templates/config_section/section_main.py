"""
My Section Configuration - Description of what this configures.

Copy this to vibe_core/phoenix/sections/my_section/ and modify.

Steps:
1. cp -r docs/templates/config_section vibe_core/phoenix/sections/my_section
2. Edit manifest.json: id, name, config_file
3. Rename MySectionConfig and implement fields
4. Create config/my_section.yaml with default values
5. Auto-discovered on next PhoenixConfig.load()
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class NestedConfig:
    """Example nested configuration."""

    setting_a: str = "default_a"
    setting_b: int = 42

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NestedConfig":
        return cls(
            setting_a=data.get("setting_a", "default_a"),
            setting_b=data.get("setting_b", 42),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "setting_a": self.setting_a,
            "setting_b": self.setting_b,
        }


@dataclass
class MySectionConfig:
    """
    My Section Configuration.

    Loaded from config/my_section.yaml via Phoenix auto-discovery.

    Required attributes:
    - section_id: str - Unique identifier (must match manifest.json id)
    - source_file: str - YAML filename in config/

    Required methods:
    - from_dict(data) -> Self - Create instance from YAML data
    - to_dict() -> dict - Serialize to dict
    - validate() -> List[str] - Return list of errors (empty = valid)
    """

    # Required: Must match manifest.json "id"
    section_id: str = "my_section"
    source_file: str = "my_section.yaml"

    # Your config fields
    enabled: bool = True
    debug: bool = False
    nested: NestedConfig = field(default_factory=NestedConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MySectionConfig":
        """Create config from YAML dictionary."""
        nested_data = data.get("nested", {})

        return cls(
            enabled=data.get("enabled", True),
            debug=data.get("debug", False),
            nested=NestedConfig.from_dict(nested_data),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary (for saving/export)."""
        return {
            "enabled": self.enabled,
            "debug": self.debug,
            "nested": self.nested.to_dict(),
        }

    def validate(self) -> List[str]:
        """
        Validate configuration.

        Returns:
            List of error messages (empty = valid)
        """
        errors = []

        # Add your validation rules here
        if self.nested.setting_b < 0:
            errors.append("nested.setting_b must be non-negative")

        return errors
