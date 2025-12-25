"""
Section Loader - Auto-discovery for Phoenix Config Sections.

INHERITS FROM UnifiedLoader - The fraktal pattern!

Specifics for Sections:
- Supports both NEW-style folders (manifest.json) and OLD-style .py files
- Loads YAML config files from config/ directory
- Uses duck typing (section_id, from_dict, to_dict)
- Returns instances populated with config values
"""

import importlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple, Type, runtime_checkable

import yaml

from vibe_core.loaders import LoaderRegistry, UnifiedLoader

logger = logging.getLogger("SECTION.LOADER")


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
    """Metadata about a loaded section (backward compat)."""

    section_id: str
    section_class: Type
    source_file: Optional[Path]
    priority: int
    loaded_from_yaml: bool

    def __repr__(self) -> str:
        src = self.source_file.name if self.source_file else "defaults"
        return f"<Section:{self.section_id} from={src} priority={self.priority}>"


# Type aliases (backward compat)
SectionRegistry = Dict[str, Type]
SectionInstances = Dict[str, Any]


class SectionLoader(UnifiedLoader):
    """
    Auto-discovery loader for Phoenix Config Sections.

    Inherits from UnifiedLoader - VEDA-4 pattern.

    Section-specific:
    - Loads YAML config from config/ directory
    - Instantiates with from_dict(yaml_data)
    - Supports both new-style (folder) and old-style (.py file)

    Usage:
        sections, meta = SectionLoader.discover()
    """

    # === UNIFIED LOADER CONFIG ===
    item_type = "section"
    scan_paths = [Path("vibe_core/phoenix/sections")]
    manifest_filenames = ["manifest.json"]
    entry_suffix = "_main.py"
    base_class = None  # Duck typing instead

    # Section-specific
    config_dir = Path("config")

    # Cache for backward compat
    _section_registry: Optional[SectionRegistry] = None

    # =========================================================================
    # MAIN ENTRY POINT
    # =========================================================================

    @classmethod
    def discover(
        cls,
        config_dir: Path = Path("config"),
        sections_dir: str = "vibe_core/phoenix/sections",
    ) -> Tuple[SectionInstances, Dict[str, SectionMeta]]:
        """
        Discover and instantiate all config sections.

        OPUS-307 Phase F: Uses ManifestRegistry (NO iterdir!).
        Das System WEISS welche Sections installiert sind.

        Args:
            config_dir: Directory containing YAML config files
            sections_dir: Directory containing section definitions (legacy, unused)

        Returns:
            Tuple of (section_instances, metadata)
        """
        from vibe_core.loaders.manifest_registry import ManifestRegistry

        cls.config_dir = config_dir

        sections: SectionInstances = {}
        metadata: Dict[str, SectionMeta] = {}

        # OPUS-307: Use ManifestRegistry instead of iterdir()
        ManifestRegistry._ensure_scanned()
        entries = ManifestRegistry.get_enabled("section")

        if not entries:
            logger.warning("[section] No section manifests found in ManifestRegistry")
            return sections, metadata

        logger.info(f"[section] Loading {len(entries)} sections from ManifestRegistry...")

        for entry in entries:
            # entry.parent_dir is the section directory
            section_dir = entry.parent_dir

            result = cls._load_new_style_section(section_dir, config_dir)
            if result:
                section_id, instance, meta = result
                sections[section_id] = instance
                metadata[section_id] = meta
                logger.info(f"  ✅ Loaded: {section_id}")

        # Sort by priority
        sorted_sections = dict(sorted(sections.items(), key=lambda x: metadata[x[0]].priority))

        logger.info(f"[section] Loaded {len(sorted_sections)} config sections")
        return sorted_sections, metadata

    # =========================================================================
    # NEW-STYLE LOADING (folder + manifest.json)
    # =========================================================================

    @classmethod
    def _load_new_style_section(
        cls,
        section_dir: Path,
        config_dir: Path,
    ) -> Optional[Tuple[str, Any, SectionMeta]]:
        """Load a new-style section from folder with manifest.json."""
        import json

        manifest_path = section_dir / "manifest.json"

        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load manifest: {manifest_path}: {e}")
            return None

        section_id = manifest.get("id", section_dir.name)
        entry_point = manifest.get("entry_point", "section_main.py")
        entry_class_name = manifest.get("entry_class")
        priority = manifest.get("priority", 100)
        config_file = manifest.get("config_file")

        # Load entry class
        entry_path = section_dir / entry_point
        if not entry_path.exists():
            logger.error(f"Entry point not found: {entry_path}")
            return None

        section_class = cls._load_section_class(entry_path, section_id, entry_class_name)
        if not section_class:
            return None

        # Load YAML config
        yaml_path = Path(config_file) if config_file else config_dir / f"{section_id}.yaml"
        yaml_data = cls._load_yaml(yaml_path)

        # Instantiate
        try:
            instance = section_class.from_dict(yaml_data)
        except Exception as e:
            logger.error(f"Failed to instantiate {section_id}: {e}")
            return None

        meta = SectionMeta(
            section_id=section_id,
            section_class=section_class,
            source_file=yaml_path if yaml_path.exists() else None,
            priority=priority,
            loaded_from_yaml=bool(yaml_data),
        )

        return section_id, instance, meta

    # =========================================================================
    # OLD-STYLE LOADING (single .py file)
    # =========================================================================

    @classmethod
    def _load_old_style_sections(
        cls,
        file_path: Path,
        base_path: Path,
        config_dir: Path,
    ) -> List[Tuple[str, Any, SectionMeta]]:
        """Load old-style sections from a single .py file."""
        results = []

        try:
            # Convert file path to module path
            relative_path = file_path.relative_to(base_path.parent.parent)
            module_name = str(relative_path.with_suffix("")).replace("/", ".")

            module = importlib.import_module(module_name)

            # Find classes with section_id
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if not isinstance(attr, type):
                    continue

                section_id = getattr(attr, "section_id", None)
                if not section_id or not isinstance(section_id, str):
                    continue

                # Check for required methods
                if not hasattr(attr, "from_dict") or not hasattr(attr, "to_dict"):
                    continue

                # Get config file path
                source_file = getattr(attr, "source_file", f"{section_id}.yaml")
                yaml_path = config_dir / source_file
                yaml_data = cls._load_yaml(yaml_path)

                # Get priority
                priority = cls._get_section_priority(attr)

                # Instantiate
                try:
                    instance = attr.from_dict(yaml_data)
                except Exception as e:
                    logger.error(f"Failed to instantiate {section_id}: {e}")
                    continue

                meta = SectionMeta(
                    section_id=section_id,
                    section_class=attr,
                    source_file=yaml_path if yaml_path.exists() else None,
                    priority=priority,
                    loaded_from_yaml=bool(yaml_data),
                )

                results.append((section_id, instance, meta))

        except Exception as e:
            logger.error(f"Failed to load section module {file_path.name}: {e}")

        return results

    # =========================================================================
    # HELPERS
    # =========================================================================

    @classmethod
    def _load_section_class(
        cls,
        entry_path: Path,
        section_id: str,
        class_name: Optional[str] = None,
    ) -> Optional[Type]:
        """Dynamically load a section class from file."""
        import importlib.util

        module_name = f"section_{section_id}"
        spec = importlib.util.spec_from_file_location(module_name, entry_path)

        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find the class
        if class_name:
            return getattr(module, class_name, None)

        # Find class ending with "Config"
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and name.endswith("Config") and obj.__module__ == module_name:
                return obj

        return None

    @classmethod
    def _load_yaml(cls, yaml_path: Path) -> Dict[str, Any]:
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
    def _get_section_priority(cls, section_class: Type) -> int:
        """Get priority from class, with sensible defaults."""
        if hasattr(section_class, "priority"):
            return section_class.priority

        # Default priorities based on section_id
        defaults = {
            "kernel": 0,
            "steward": 5,
            "city": 10,
            "quality": 100,
        }
        section_id = getattr(section_class, "section_id", "")
        return defaults.get(section_id, 100)

    # =========================================================================
    # BACKWARD COMPAT
    # =========================================================================

    @classmethod
    def discover_classes(cls, sections_dir: str = "vibe_core/phoenix/sections") -> SectionRegistry:
        """
        Discover all config section classes (backward compat).

        Returns dict mapping section_id -> class
        """
        if cls._section_registry is not None:
            return cls._section_registry

        sections, metadata = cls.discover(sections_dir=sections_dir)
        cls._section_registry = {sid: meta.section_class for sid, meta in metadata.items()}
        return cls._section_registry

    @classmethod
    def load_yaml(cls, yaml_path: Path) -> Dict[str, Any]:
        """Load a YAML file (backward compat)."""
        return cls._load_yaml(yaml_path)

    @classmethod
    def validate_all(cls, sections: SectionInstances) -> Dict[str, List[str]]:
        """Validate all sections (backward compat)."""
        errors: Dict[str, List[str]] = {}
        for section_id, section in sections.items():
            if hasattr(section, "validate"):
                section_errors = section.validate()
                if section_errors:
                    errors[section_id] = section_errors
        return errors

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the section registry cache."""
        cls._section_registry = None


# Register with LoaderRegistry
LoaderRegistry.register("section", SectionLoader)
