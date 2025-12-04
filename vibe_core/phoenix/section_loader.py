"""
Section Loader - Auto-discovery for Phoenix Config Sections.

Mirrors the PluginLoader pattern:
- Scans vibe_core/phoenix/sections/ for classes with section_id
- Loads corresponding YAML files from config/
- Returns dict of section_id -> instantiated section

FRACTAL:
    plugin_loader.py → Discovers KernelPlugin subclasses
    section_loader.py → Discovers ConfigSection classes (duck typed)

Duck Typing: Any class with section_id, from_dict(), to_dict() is a valid section.
This avoids circular import issues.
"""

import importlib
import logging
import pkgutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple, Type, runtime_checkable

import yaml

logger = logging.getLogger(__name__)


@runtime_checkable
class ConfigSectionProtocol(Protocol):
    """
    Protocol for config sections (duck typing).

    Any class with these attributes/methods is a valid section.
    """

    section_id: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfigSectionProtocol": ...

    def to_dict(self) -> Dict[str, Any]: ...


@dataclass
class SectionMeta:
    """Metadata about a loaded section."""

    section_id: str
    section_class: Type
    source_file: Optional[Path]
    priority: int
    loaded_from_yaml: bool

    def __repr__(self) -> str:
        src = self.source_file.name if self.source_file else "defaults"
        return f"<Section:{self.section_id} from={src} priority={self.priority}>"


# Type aliases
SectionRegistry = Dict[str, Type]
SectionInstances = Dict[str, Any]  # section_id -> instance


def _get_section_priority(cls: Type) -> int:
    """Get priority from class, with sensible defaults."""
    if hasattr(cls, "get_priority"):
        return cls.get_priority()
    if hasattr(cls, "priority"):
        return cls.priority
    # Default priorities based on section_id
    defaults = {
        "kernel": 0,
        "city": 10,
        "quality": 100,
        "circuits": 150,
        "routing": 160,
    }
    section_id = getattr(cls, "section_id", "")
    return defaults.get(section_id, 100)


def _get_source_file(cls: Type, config_dir: Path) -> Path:
    """Get source YAML file for a section class."""
    if hasattr(cls, "get_source_file"):
        return cls.get_source_file(config_dir)
    if hasattr(cls, "source_file"):
        return config_dir / cls.source_file
    # Default: config/{section_id}.yaml
    section_id = getattr(cls, "section_id", "unknown")
    return config_dir / f"{section_id}.yaml"


class SectionLoader:
    """
    Auto-discovery loader for Phoenix Config Sections.

    Usage:
        sections, meta = SectionLoader.discover()
        # sections = {"kernel": KernelConfig(...), "quality": QualityConfig(...), ...}
        # meta = {"kernel": SectionMeta(...), ...}
    """

    # Cache discovered section classes (class-level)
    _section_registry: Optional[SectionRegistry] = None

    @classmethod
    def discover_classes(cls, sections_dir: str = "vibe_core/phoenix/sections") -> SectionRegistry:
        """
        Discover all config section classes in the sections directory.

        A valid section class must have:
        - section_id: str (non-empty class attribute)
        - from_dict(data) -> instance (class method)
        - to_dict() -> dict (instance method)

        Args:
            sections_dir: Path to sections directory

        Returns:
            Dict mapping section_id -> section class
        """
        if cls._section_registry is not None:
            return cls._section_registry

        registry: SectionRegistry = {}

        # Resolve path
        base_path = Path(__file__).parent.parent.parent  # steward-protocol/
        sections_path = base_path / sections_dir

        if not sections_path.exists():
            logger.warning(f"Sections directory not found: {sections_path}")
            return registry

        logger.debug(f"Discovering config sections in: {sections_path}")

        # Convert to module path
        try:
            relative_path = sections_path.relative_to(base_path)
            package_name = str(relative_path).replace("/", ".").replace("\\", ".")
        except ValueError:
            package_name = sections_dir.replace("/", ".").replace("\\", ".")

        # Iterate over modules
        for module_info in pkgutil.iter_modules([str(sections_path)]):
            if module_info.name.startswith("_"):
                continue  # Skip __init__, __pycache__, etc.

            try:
                full_module_name = f"{package_name}.{module_info.name}"
                module = importlib.import_module(full_module_name)

                # Find classes with section_id
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if not isinstance(attr, type):
                        continue

                    # Check for section_id class attribute
                    section_id = getattr(attr, "section_id", None)
                    if not section_id or not isinstance(section_id, str):
                        continue

                    # Check for required methods
                    if not hasattr(attr, "from_dict") or not callable(getattr(attr, "from_dict")):
                        logger.warning(f"Section {attr_name} missing from_dict(), skipping")
                        continue
                    if not hasattr(attr, "to_dict"):
                        logger.warning(f"Section {attr_name} missing to_dict(), skipping")
                        continue

                    # Register
                    if section_id in registry:
                        logger.warning(f"Duplicate section_id '{section_id}' in {attr_name}, skipping")
                        continue

                    registry[section_id] = attr
                    logger.debug(f"   Registered section: {section_id} ({attr_name})")

            except Exception as e:
                logger.error(f"Failed to load section module {module_info.name}: {e}")

        cls._section_registry = registry
        logger.debug(f"Discovered {len(registry)} config sections")
        return registry

    @classmethod
    def load_yaml(cls, yaml_path: Path) -> Dict[str, Any]:
        """Load a YAML file, return empty dict if not found."""
        if not yaml_path.exists():
            logger.debug(f"YAML not found, using defaults: {yaml_path}")
            return {}
        try:
            with open(yaml_path) as f:
                data = yaml.safe_load(f)
                return data if data else {}
        except Exception as e:
            logger.error(f"Failed to load YAML {yaml_path}: {e}")
            return {}

    @classmethod
    def discover(
        cls,
        config_dir: Path = Path("config"),
        sections_dir: str = "vibe_core/phoenix/sections",
    ) -> Tuple[SectionInstances, Dict[str, SectionMeta]]:
        """
        Discover and instantiate all config sections.

        Args:
            config_dir: Directory containing YAML config files
            sections_dir: Directory containing section Python files

        Returns:
            Tuple of:
            - sections: Dict mapping section_id -> instantiated section
            - metadata: Dict mapping section_id -> SectionMeta
        """
        # Discover section classes
        registry = cls.discover_classes(sections_dir)

        sections: SectionInstances = {}
        metadata: Dict[str, SectionMeta] = {}

        # Sort by priority
        sorted_sections = sorted(registry.items(), key=lambda x: _get_section_priority(x[1]))

        for section_id, section_class in sorted_sections:
            try:
                # Get source file path
                source_file = _get_source_file(section_class, config_dir)

                # Load YAML data
                yaml_data = cls.load_yaml(source_file)

                # Instantiate section
                if yaml_data:
                    instance = section_class.from_dict(yaml_data)
                    loaded_from_yaml = True
                else:
                    # Use defaults (empty dict)
                    instance = section_class.from_dict({})
                    loaded_from_yaml = False

                sections[section_id] = instance
                metadata[section_id] = SectionMeta(
                    section_id=section_id,
                    section_class=section_class,
                    source_file=source_file if source_file.exists() else None,
                    priority=_get_section_priority(section_class),
                    loaded_from_yaml=loaded_from_yaml,
                )

                logger.debug(f"   Loaded section: {section_id} (from={'yaml' if loaded_from_yaml else 'defaults'})")

            except Exception as e:
                logger.error(f"Failed to instantiate section {section_id}: {e}")

        logger.info(f"Loaded {len(sections)} config sections")
        return sections, metadata

    @classmethod
    def validate_all(cls, sections: SectionInstances) -> Dict[str, List[str]]:
        """
        Validate all sections.

        Returns:
            Dict mapping section_id -> list of validation errors
            (empty list = valid)
        """
        errors: Dict[str, List[str]] = {}
        for section_id, section in sections.items():
            if hasattr(section, "validate"):
                section_errors = section.validate()
                if section_errors:
                    errors[section_id] = section_errors
        return errors

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the section registry cache (useful for testing)."""
        cls._section_registry = None
