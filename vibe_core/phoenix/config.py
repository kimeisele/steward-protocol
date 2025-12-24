"""
Phoenix Configuration - The config that never dies.

Unified, typed, fractal configuration system for steward-protocol.

FRACTAL ARCHITECTURE:
    Kernel (Vishnu)              Phoenix Config
    ───────────────              ──────────────
    plugin_protocol.py    ↔      section_protocol.py
    plugin_loader.py      ↔      section_loader.py
    vibe_core/plugins/    ↔      vibe_core/phoenix/sections/

Sections are auto-discovered from vibe_core/phoenix/sections/.
Any class with section_id, from_dict(), to_dict() is a valid section.

ZERO MANUAL REGISTRATION:
    Add folder to sections/ with manifest.json → auto-loaded!
    Add config/section_id.yaml → auto-populated!
    Access via config.section_id → works!
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import yaml

from .section_loader import SectionLoader, SectionMeta
from .utils.circuits import CircuitConfig, discover_circuits
from .utils.routing import RoutingRule, load_routing_rules, save_routing_rules

# Type imports for IDE support (no runtime dependency)
if TYPE_CHECKING:
    from .sections.city.section_main import CityConfig
    from .sections.kernel.section_main import KernelConfig
    from .sections.paths.section_main import PathsConfig
    from .sections.prompts.section_main import PromptsConfig
    from .sections.quality.section_main import QualityConfig
    from .sections.steward.section_main import StewardConfig
    from .sections.templates.section_main import TemplatesConfig

logger = logging.getLogger(__name__)


@dataclass
class PhoenixConfig:
    """
    Unified configuration - the Phoenix that never dies.

    TRUE FRACTAL PATTERN:
    - ALL sections are auto-discovered from vibe_core/phoenix/sections/
    - ALL sections are stored in _sections dict
    - Access via config.section_id uses __getattr__
    - NO manual field registration required!

    Legacy compatibility:
    - config.kernel, config.city, etc. still work via __getattr__
    - Type hints available via TYPE_CHECKING imports

    Usage:
        config = PhoenixConfig.from_files()
        config.kernel.features.live_fire_enabled
        config.paths.data.resolve("economy_db")
        config.templates.render("status_summary", ...)
        config.prompts.get_prompt("system_boot", ...)
    """

    # ALL sections stored here - auto-discovered
    _sections: Dict[str, Any] = field(default_factory=dict)
    _section_metadata: Dict[str, SectionMeta] = field(default_factory=dict, repr=False)

    # Dynamic collections (not sections)
    circuits: Dict[str, CircuitConfig] = field(default_factory=dict)
    routing: List[RoutingRule] = field(default_factory=list)

    # Source paths (for save/reload)
    _circuits_dir: Optional[Path] = field(default=None, repr=False)
    _routing_path: Optional[Path] = field(default=None, repr=False)
    _config_dir: Optional[Path] = field(default=None, repr=False)

    def __getattr__(self, name: str) -> Any:
        """
        Dynamic access to ALL auto-discovered sections.

        This is the ONLY way sections are accessed - no manual fields!
        """
        if "_sections" in self.__dict__ and name in self._sections:
            return self._sections[name]
        raise AttributeError(f"'{type(self).__name__}' has no section '{name}'")

    # =========================================================================
    # Type-hinted properties for IDE support (optional, for core sections only)
    # These don't add manual fields - they just provide type hints
    # =========================================================================

    @property
    def kernel(self) -> "KernelConfig":
        """Kernel configuration (type-hinted for IDE)."""
        return self._sections.get("kernel")

    @property
    def city(self) -> "CityConfig":
        """City configuration (type-hinted for IDE)."""
        return self._sections.get("city")

    @property
    def quality(self) -> "QualityConfig":
        """Quality configuration (type-hinted for IDE)."""
        return self._sections.get("quality")

    @property
    def steward(self) -> "StewardConfig":
        """Steward configuration (type-hinted for IDE)."""
        return self._sections.get("steward")

    @property
    def paths(self) -> "PathsConfig":
        """Paths configuration (type-hinted for IDE)."""
        return self._sections.get("paths")

    @property
    def templates(self) -> "TemplatesConfig":
        """Templates configuration (type-hinted for IDE)."""
        return self._sections.get("templates")

    @property
    def prompts(self) -> "PromptsConfig":
        """Prompts configuration (type-hinted for IDE)."""
        return self._sections.get("prompts")

    # =========================================================================
    # MAIN ENTRY POINT
    # =========================================================================

    @classmethod
    def from_files(
        cls,
        circuits_dir: Path = Path("vibe_core/playbook/circuits"),
        routing_path: Path = Path("MATRIX.md"),
        config_dir: Path = Path("config"),
    ) -> "PhoenixConfig":
        """
        Load configuration from all source files via auto-discovery.

        ZERO MANUAL REGISTRATION:
        - SectionLoader.discover() finds ALL sections in sections/
        - Each section has manifest.json defining config_file
        - YAML from config/ is loaded and passed to from_dict()
        - Result stored in _sections dict

        Args:
            circuits_dir: Directory containing circuit YAML files
            routing_path: Path to MATRIX.md (routing rules)
            config_dir: Directory containing section YAML files

        Returns:
            Fully loaded PhoenixConfig
        """
        from .config_cache import get_cached_or_parse

        def _parse():
            # === AUTO-DISCOVERY: Load ALL sections ===
            SectionLoader.clear_cache()
            sections, section_meta = SectionLoader.discover(config_dir=config_dir)

            # Log what was loaded
            for section_id, meta in section_meta.items():
                if meta.loaded_from_yaml:
                    logger.info(f"Loaded section '{section_id}' from {meta.source_file}")
                else:
                    logger.debug(f"Section '{section_id}' using defaults")

            # === COLLECTIONS: Circuits and Routing ===
            circuits = discover_circuits(circuits_dir)
            logger.info(f"Discovered {len(circuits)} circuits from {circuits_dir}")

            routing = load_routing_rules(routing_path)
            logger.info(f"Loaded {len(routing)} routing rules from {routing_path}")

            # === CREATE CONFIG ===
            config = cls(
                _sections=sections,
                _section_metadata=section_meta,
                circuits=circuits,
                routing=routing,
            )

            # Store paths for reload
            config._circuits_dir = circuits_dir
            config._routing_path = routing_path
            config._config_dir = config_dir
            
            return config

        config = get_cached_or_parse(config_dir, _parse)
        logger.info(f"PhoenixConfig loaded with {len(config._sections)} sections: {list(config._sections.keys())}")

        return config

    @classmethod
    def from_env(cls) -> "PhoenixConfig":
        """
        Load configuration from environment variables.

        Environment variables override file defaults.
        """
        import os

        config = cls.from_files()

        # Override with environment variables
        if config.kernel and os.getenv("PHOENIX_LIVE_FIRE"):
            config.kernel.features.live_fire_enabled = os.getenv("PHOENIX_LIVE_FIRE", "").lower() == "true"

        if config.kernel and os.getenv("PHOENIX_DEBUG"):
            config.kernel.features.debug_mode = os.getenv("PHOENIX_DEBUG", "").lower() == "true"

        if config.kernel and os.getenv("PHOENIX_LLM_PROVIDER"):
            config.kernel.providers.llm_provider = os.getenv("PHOENIX_LLM_PROVIDER", "")

        if config.city and os.getenv("PHOENIX_LOG_LEVEL"):
            config.city.monitoring.log_level = os.getenv("PHOENIX_LOG_LEVEL", "INFO")

        return config

    @classmethod
    def create_for_simulation(cls) -> "PhoenixConfig":
        """Factory: Create config for safe simulation mode."""
        config = cls.from_files()
        if config.kernel:
            config.kernel.features.live_fire_enabled = False
            config.kernel.features.debug_mode = True
        return config

    @classmethod
    def create_for_live_fire(cls) -> "PhoenixConfig":
        """Factory: Create config for production/live mode."""
        config = cls.from_files()
        if config.kernel:
            config.kernel.features.live_fire_enabled = True
            config.kernel.features.debug_mode = False
        return config

    # =========================================================================
    # Validation
    # =========================================================================

    def validate(self) -> List[str]:
        """
        Validate all configuration sections.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors: List[str] = []

        # Validate each section that has a validate() method
        for section_id, section in self._sections.items():
            if hasattr(section, "validate"):
                section_errors = section.validate()
                for err in section_errors:
                    errors.append(f"{section_id}: {err}")

        # Routing validation
        for i, rule in enumerate(self.routing):
            if not rule.pattern:
                errors.append(f"routing[{i}].pattern is empty")
            if not rule.circuit:
                errors.append(f"routing[{i}].circuit is empty")

        return errors

    # =========================================================================
    # Save/Reload
    # =========================================================================

    def save(self) -> bool:
        """
        Persist configuration back to files.

        Returns:
            True if all saves successful
        """
        success = True

        # Save each section that has source file
        for section_id, meta in self._section_metadata.items():
            if meta.source_file and meta.source_file.exists():
                section = self._sections.get(section_id)
                if section and hasattr(section, "to_dict"):
                    try:
                        meta.source_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(meta.source_file, "w") as f:
                            yaml.dump(section.to_dict(), f, default_flow_style=False, sort_keys=False)
                        logger.info(f"Saved {section_id} to {meta.source_file}")
                    except Exception as e:
                        logger.error(f"Failed to save {section_id}: {e}")
                        success = False

        # Save routing rules
        if self._routing_path:
            if not save_routing_rules(self.routing, self._routing_path):
                logger.error("Failed to save routing rules")
                success = False

        return success

    def reload_routing(self) -> None:
        """Hot-reload MATRIX.md routing rules."""
        if self._routing_path:
            self.routing = load_routing_rules(self._routing_path)
            logger.info(f"Reloaded {len(self.routing)} routing rules")

    def reload_circuits(self) -> None:
        """Reload circuit configurations."""
        if self._circuits_dir:
            self.circuits = discover_circuits(self._circuits_dir)
            logger.info(f"Reloaded {len(self.circuits)} circuits")

    def reload_section(self, section_id: str) -> bool:
        """
        Reload a single section from its YAML file.

        Args:
            section_id: Section to reload

        Returns:
            True if successful
        """
        meta = self._section_metadata.get(section_id)
        if not meta or not meta.source_file:
            logger.warning(f"Cannot reload {section_id}: no source file")
            return False

        try:
            yaml_data = SectionLoader._load_yaml(meta.source_file)
            new_instance = meta.section_class.from_dict(yaml_data)
            self._sections[section_id] = new_instance
            logger.info(f"Reloaded {section_id} from {meta.source_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to reload {section_id}: {e}")
            return False

    # =========================================================================
    # Section Discovery
    # =========================================================================

    def list_sections(self) -> List[str]:
        """List all discovered section IDs."""
        return list(self._sections.keys())

    def get_section(self, section_id: str) -> Optional[Any]:
        """Get a section by ID."""
        return self._sections.get(section_id)

    def get_section_metadata(self, section_id: str) -> Optional[SectionMeta]:
        """Get metadata about a section (source file, priority, etc.)."""
        return self._section_metadata.get(section_id)

    def has_section(self, section_id: str) -> bool:
        """Check if a section exists."""
        return section_id in self._sections

    # =========================================================================
    # Convenience accessors
    # =========================================================================

    @property
    def live_fire_enabled(self) -> bool:
        """Quick access to live fire mode."""
        return self.kernel.features.live_fire_enabled if self.kernel else False

    @live_fire_enabled.setter
    def live_fire_enabled(self, value: bool) -> None:
        if self.kernel:
            self.kernel.features.live_fire_enabled = value

    @property
    def debug_mode(self) -> bool:
        """Quick access to debug mode."""
        return self.kernel.features.debug_mode if self.kernel else False

    @debug_mode.setter
    def debug_mode(self, value: bool) -> None:
        if self.kernel:
            self.kernel.features.debug_mode = value

    @property
    def provider_name(self) -> str:
        """Quick access to provider name."""
        return self.kernel.providers.name if self.kernel else "unknown"

    def get_circuit(self, name: str) -> Optional[CircuitConfig]:
        """Get a circuit by name."""
        return self.circuits.get(name)

    def get_active_routes(self) -> List[RoutingRule]:
        """Get only active routing rules."""
        return [r for r in self.routing if r.active]

    def route_intent(self, intent: str) -> Optional[str]:
        """Route an intent string to a circuit name."""
        for rule in self.get_active_routes():
            if rule.matches(intent):
                return rule.circuit
        return None

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> Dict:
        """Serialize config to dictionary for child kernel spawning."""
        result = {
            "circuits": {name: circuit.to_dict() for name, circuit in self.circuits.items()},
            "routing": [rule.to_dict() for rule in self.routing],
        }
        # Add all sections
        for section_id, section in self._sections.items():
            if hasattr(section, "to_dict"):
                result[section_id] = section.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict) -> "PhoenixConfig":
        """Deserialize config from dictionary."""
        # This is more complex - need to know section classes
        # For now, just load from files and override
        config = cls.from_files()

        # Override circuits
        if "circuits" in data:
            config.circuits = {}
            for name, circuit_data in data["circuits"].items():
                config.circuits[name] = CircuitConfig.from_dict(circuit_data)

        # Override routing
        if "routing" in data:
            config.routing = [RoutingRule.from_dict(r) for r in data["routing"]]

        # Override sections
        for section_id, section in config._sections.items():
            if section_id in data and hasattr(section, "from_dict"):
                config._sections[section_id] = type(section).from_dict(data[section_id])

        return config

    # =========================================================================
    # Backward compatibility
    # =========================================================================

    def get(self, key: str, default=None):
        """Get config value by dotted key path (backward compatibility)."""
        # Map old paths to new structure
        if key.startswith("providers."):
            attr = key.split(".", 1)[1]
            return getattr(self.kernel.providers, attr, default) if self.kernel else default
        elif key.startswith("features."):
            attr = key.split(".", 1)[1]
            return getattr(self.kernel.features, attr, default) if self.kernel else default
        return default

    def set(self, key: str, value) -> bool:
        """Set config value by dotted key path (backward compatibility)."""
        try:
            if key.startswith("providers.") and self.kernel:
                attr = key.split(".", 1)[1]
                setattr(self.kernel.providers, attr, value)
                return True
            elif key.startswith("features.") and self.kernel:
                attr = key.split(".", 1)[1]
                setattr(self.kernel.features, attr, value)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to set {key}: {e}")
            return False


# =========================================================================
# Singleton pattern for global access
# =========================================================================

_config: Optional[PhoenixConfig] = None


def get_config() -> PhoenixConfig:
    """Get the global PhoenixConfig instance."""
    global _config
    if _config is None:
        _config = PhoenixConfig.from_files()
    return _config


def reset_config() -> None:
    """Reset the singleton (mainly for testing)."""
    global _config
    _config = None


def set_config(config: PhoenixConfig) -> None:
    """Set the global config instance (for testing or custom initialization)."""
    global _config
    _config = config
