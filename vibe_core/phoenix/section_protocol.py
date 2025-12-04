"""
ConfigSection Protocol - The Fractal Pattern for Phoenix Config.

Just as KernelPlugin defines how plugins extend the kernel,
ConfigSection defines how sections extend PhoenixConfig.

FRACTAL ARCHITECTURE:
    Kernel (Vishnu)              Phoenix Config
    ───────────────              ──────────────
    plugin_protocol.py    ↔      section_protocol.py
    plugin_loader.py      ↔      section_loader.py
    vibe_core/plugins/    ↔      vibe_core/phoenix/sections/

New section = New file in sections/ = Auto-discovered
No more touching config.py!
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Type


class ConfigSection(ABC):
    """
    Base class for all Phoenix Config Sections.

    Sections are auto-discovered from vibe_core/phoenix/sections/
    and loaded from corresponding YAML files in config/.

    Example:
        # vibe_core/phoenix/sections/quality.py
        @dataclass
        class QualityConfig(ConfigSection):
            section_id = "quality"  # → loads from config/quality.yaml

            lint: LintConfig = field(default_factory=LintConfig)
            ...
    """

    # Class-level section identifier (must be overridden)
    section_id: ClassVar[str] = ""

    @classmethod
    def get_section_id(cls) -> str:
        """Get the section identifier."""
        return cls.section_id

    @classmethod
    def get_source_file(cls, config_dir: Path = Path("config")) -> Path:
        """
        Get the source YAML file for this section.

        Default: config/{section_id}.yaml
        Override for custom locations.
        """
        return config_dir / f"{cls.section_id}.yaml"

    @classmethod
    def get_priority(cls) -> int:
        """
        Loading order (lower = earlier).

        Standard Priorities:
        - 0-99: Core sections (kernel, city)
        - 100-199: Standard sections (quality, routing)
        - 200+: User/optional sections
        """
        return 100

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfigSection":
        """Create instance from dictionary (YAML parsed data)."""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        pass

    def validate(self) -> List[str]:
        """
        Validate the configuration.

        Returns:
            List of validation error messages (empty = valid)

        Override this to add custom validation logic.
        """
        return []

    def get_defaults(self) -> Dict[str, Any]:
        """
        Get default values for this section.

        Override to provide custom defaults documentation.
        """
        return self.to_dict()


# Type alias for section registry
SectionRegistry = Dict[str, Type[ConfigSection]]


@dataclass
class SectionMeta:
    """Metadata about a loaded section."""

    section_id: str
    section_class: Type[ConfigSection]
    source_file: Optional[Path]
    priority: int
    loaded_from_yaml: bool

    def __repr__(self) -> str:
        src = self.source_file.name if self.source_file else "defaults"
        return f"<Section:{self.section_id} from={src} priority={self.priority}>"
