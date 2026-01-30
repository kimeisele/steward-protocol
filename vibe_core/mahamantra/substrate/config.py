"""
Phoenix Configuration - The config that never dies.
SSOT LOCATION: vibe_core/mahamantra/substrate/config.py

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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x2d18a205"  # GenesisByte: parampara % 37 == 0

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import yaml

if TYPE_CHECKING:
    from vibe_core.protocols.universal import ReadResult, SovereignContext
    # Config sections type hints
    from vibe_core.phoenix.sections.city.section_main import CityConfig
    from vibe_core.phoenix.sections.kernel.section_main import KernelConfig
    from vibe_core.phoenix.sections.paths.section_main import PathsConfig
    from vibe_core.phoenix.sections.prompts.section_main import PromptsConfig
    from vibe_core.phoenix.sections.quality.section_main import QualityConfig
    from vibe_core.phoenix.sections.steward.section_main import StewardConfig
    from vibe_core.phoenix.sections.templates.section_main import TemplatesConfig
    # Implementation types (Lazy loaded)
    from vibe_core.phoenix.section_loader import SectionLoader
    from vibe_core.phoenix.utils.circuits import CircuitConfig
    from vibe_core.phoenix.utils.routing import RoutingRule

logger = logging.getLogger(__name__)


@dataclass
class SectionMeta:
    """Metadata about a loaded section (SSOT definition)."""

    section_id: str
    section_class: Any  # Type
    source_file: Optional[Path]
    priority: int
    loaded_from_yaml: bool

    def __repr__(self) -> str:
        src = self.source_file.name if self.source_file else "defaults"
        return f"<Section:{self.section_id} from={src} priority={self.priority}>"


@dataclass
class PhoenixConfig:
    """
    Unified configuration - the Phoenix that never dies.

    TRUE FRACTAL PATTERN:
    - ALL sections are auto-discovered from vibe_core/phoenix/sections/
    - ALL sections are stored in _sections dict
    - Access via config.section_id uses __getattr__
    - NO manual fields required!
    """

    # ALL sections stored here - auto-discovered
    _sections: Dict[str, Any] = field(default_factory=dict)
    _section_metadata: Dict[str, SectionMeta] = field(default_factory=dict, repr=False)

    # Dynamic collections (not sections) - use forward references or Any to avoid import cycles
    circuits: Dict[str, Any] = field(default_factory=dict)  # Dict[str, CircuitConfig]
    routing: List[Any] = field(default_factory=list)      # List[RoutingRule]

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
    # READ/WRITE PROTOCOL (GAD-000 IMPL)
    # =========================================================================

    def read(self, key: str, context: Optional["SovereignContext"] = None) -> "ReadResult":
        """
        Read value by dotted key path (e.g., 'kernel.features.live_fire').
        Returns ENVELOPE (Value + Provenance).
        """
        from datetime import datetime
        from vibe_core.protocols.universal import KeyNotFoundError, ReadResult

        try:
            value = self._resolve_path(key)
            return ReadResult(value=value, writer=None, timestamp=datetime.now())
        except (AttributeError, KeyError) as e:
            raise KeyNotFoundError(f"Config key '{key}' not found: {e}")

    def write(self, key: str, value: Any, context: Optional["SovereignContext"] = None) -> None:
        """
        Write value by dotted key path.
        Enforces Anti-Mayavad: Must be signed by Sovereign.
        """
        if not context:
            from vibe_core.protocols.universal import AccessDeniedError
            raise AccessDeniedError("MAYAVAD: Config mutation requires Sovereign Signature.")

        try:
            # 1. Resolve Parent
            parts = key.split(".")
            if len(parts) < 2:
                raise KeyError(f"Invalid config key '{key}'. Must be 'section.field'")

            section_id = parts[0]
            field_path = parts[1:]

            # Get Section
            if section_id not in self._sections:
                raise KeyError(f"Section '{section_id}' not found")

            obj = self._sections[section_id]

            # Traverse to leaf parent
            for part in field_path[:-1]:
                if hasattr(obj, part):
                    obj = getattr(obj, part)
                elif isinstance(obj, dict) and part in obj:
                    obj = obj[part]
                else:
                    raise KeyError(f"Path segment '{part}' not found in '{key}'")

            # 2. Set Value (Leaf)
            leaf = field_path[-1]
            old_value = None

            if hasattr(obj, leaf):
                old_value = getattr(obj, leaf)
                setattr(obj, leaf, value)
            elif isinstance(obj, dict):
                old_value = obj.get(leaf)
                obj[leaf] = value
            else:
                setattr(obj, leaf, value)

            # 3. Audit Log (Karma)
            logger.info(f"📝 CONFIG CHANGE [Sovereign: {context.identity_id}]: {key} = {value} (was: {old_value})")

            # 4. Save (Persistence)
            self.save()

        except Exception as e:
            from vibe_core.protocols.universal import ProtocolError
            raise ProtocolError(f"Failed to write config '{key}': {e}")

    def exists(self, key: str, context: Optional["SovereignContext"] = None) -> bool:
        """Check if key exists."""
        try:
            self._resolve_path(key)
            return True
        except (KeyError, AttributeError):
            return False

    def _resolve_path(self, key: str) -> Any:
        """Helper: Resolve dotted path to value. Safe traversal."""
        parts = key.split(".")
        if not parts:
            raise KeyError("Empty key")

        section_id = parts[0]
        if section_id not in self._sections:
            raise KeyError(f"Section '{section_id}' not found")

        current = self._sections[section_id]
        for part in parts[1:]:
            if hasattr(current, part):
                current = getattr(current, part)
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                raise KeyError(f"Path '{part}' not found in '{key}'")
        return current

    # =========================================================================
    # Type-hinted properties for IDE support
    # =========================================================================

    @property
    def kernel(self) -> "KernelConfig":
        return self._sections.get("kernel")

    @property
    def city(self) -> "CityConfig":
        return self._sections.get("city")

    @property
    def quality(self) -> "QualityConfig":
        return self._sections.get("quality")

    @property
    def steward(self) -> "StewardConfig":
        return self._sections.get("steward")

    @property
    def paths(self) -> "PathsConfig":
        return self._sections.get("paths")

    @property
    def templates(self) -> "TemplatesConfig":
        return self._sections.get("templates")

    @property
    def prompts(self) -> "PromptsConfig":
        return self._sections.get("prompts")

    # =========================================================================
    # MAIN ENTRY POINT
    # =========================================================================

    @classmethod
    def from_files(
        cls,
        circuits_dir: Path = Path("vibe_core/playbook/circuits"),
        routing_path: Path = Path("MATRIX.md"),
        config_dir: Optional[Path] = None,
    ) -> "PhoenixConfig":
        """Load configuration from all source files via auto-discovery."""
        if config_dir is None:
            env_config_dir = os.getenv("PHOENIX_CONFIG_DIR")
            if env_config_dir:
                config_dir = Path(env_config_dir)
                logger.info(f"Using PHOENIX_CONFIG_DIR: {config_dir}")
            else:
                config_dir = Path("config")
        
        # Lazy imports to avoid circular dependency with mahamantra
        from vibe_core.phoenix.config_cache import get_cached_or_parse
        from vibe_core.phoenix.section_loader import SectionLoader
        from vibe_core.phoenix.utils.circuits import discover_circuits
        from vibe_core.phoenix.utils.routing import load_routing_rules

        def _parse():
            SectionLoader.clear_cache()
            sections, section_meta = SectionLoader.discover(config_dir=config_dir)
            
            # Convert Phoenix SectionMeta to SSOT SectionMeta if needed?
            # Actually, duck typing might save us here, or we accept Any in Field default.
            # But SectionLoader returns its own Meta.
            # We defined SectionMeta locally in SSOT.
            # Python dataclasses are not structurally compatible if classes differ.
            # BUT we just stored it in _section_metadata: Dict[str, Any] would be safer.
            # Let's keep it loose for now.
            
            for section_id, meta in section_meta.items():
                if meta.loaded_from_yaml:
                    logger.info(f"Loaded section '{section_id}' from {meta.source_file}")
                else:
                    logger.debug(f"Section '{section_id}' using defaults")

            circuits = discover_circuits(circuits_dir)
            logger.info(f"Discovered {len(circuits)} circuits from {circuits_dir}")

            routing = load_routing_rules(routing_path)
            logger.info(f"Loaded {len(routing)} routing rules from {routing_path}")

            config = cls(
                _sections=sections,
                _section_metadata=section_meta,  # type: ignore (Cross-type assignment)
                circuits=circuits,               # type: ignore
                routing=routing,                 # type: ignore
            )
            config._circuits_dir = circuits_dir
            config._routing_path = routing_path
            config._config_dir = config_dir
            return config

        config = get_cached_or_parse(config_dir, _parse)
        logger.info(f"PhoenixConfig loaded with {len(config._sections)} sections: {list(config._sections.keys())}")

        validation_errors = config.validate()
        if validation_errors:
            for err in validation_errors:
                logger.warning(f"Config validation: {err}")
            logger.warning(f"PhoenixConfig has {len(validation_errors)} validation issues")

        return config

    @classmethod
    def from_env(cls) -> "PhoenixConfig":
        """Load configuration from environment variables."""
        config = cls.from_files()

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
        """Validate all configuration sections."""
        errors: List[str] = []
        for section_id, section in self._sections.items():
            if hasattr(section, "validate"):
                section_errors = section.validate()
                for err in section_errors:
                    errors.append(f"{section_id}: {err}")

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
        """Persist configuration back to files."""
        # Lazy import
        from vibe_core.phoenix.utils.routing import save_routing_rules
        
        success = True
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

        if self._routing_path:
            if not save_routing_rules(self.routing, self._routing_path):
                logger.error("Failed to save routing rules")
                success = False
        return success

    def reload_routing(self) -> None:
        """Hot-reload MATRIX.md routing rules."""
        from vibe_core.phoenix.utils.routing import load_routing_rules
        
        if self._routing_path:
            self.routing = load_routing_rules(self._routing_path)
            logger.info(f"Reloaded {len(self.routing)} routing rules")

    def reload_circuits(self) -> None:
        """Reload circuit configurations."""
        from vibe_core.phoenix.utils.circuits import discover_circuits
        
        if self._circuits_dir:
            self.circuits = discover_circuits(self._circuits_dir)
            logger.info(f"Reloaded {len(self.circuits)} circuits")

    def reload_section(self, section_id: str) -> bool:
        """Reload a single section from its YAML file."""
        from vibe_core.phoenix.section_loader import SectionLoader
        
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
        return list(self._sections.keys())

    def get_section(self, section_id: str) -> Optional[Any]:
        return self._sections.get(section_id)

    def get_section_metadata(self, section_id: str) -> Optional[SectionMeta]:
        return self._section_metadata.get(section_id)

    def has_section(self, section_id: str) -> bool:
        return section_id in self._sections

    # =========================================================================
    # Convenience accessors
    # =========================================================================

    @property
    def live_fire_enabled(self) -> bool:
        return self.kernel.features.live_fire_enabled if self.kernel else False

    @live_fire_enabled.setter
    def live_fire_enabled(self, value: bool) -> None:
        if self.kernel:
            self.kernel.features.live_fire_enabled = value

    @property
    def debug_mode(self) -> bool:
        return self.kernel.features.debug_mode if self.kernel else False

    @debug_mode.setter
    def debug_mode(self, value: bool) -> None:
        if self.kernel:
            self.kernel.features.debug_mode = value

    @property
    def provider_name(self) -> str:
        return self.kernel.providers.name if self.kernel else "unknown"

    def get_circuit(self, name: str) -> Optional["CircuitConfig"]:
        """Get a circuit by name."""
        return self.circuits.get(name)

    def get_active_routes(self) -> List["RoutingRule"]:
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
        result = {
            "circuits": {name: circuit.to_dict() for name, circuit in self.circuits.items()},
            "routing": [rule.to_dict() for rule in self.routing],
        }
        for section_id, section in self._sections.items():
            if hasattr(section, "to_dict"):
                result[section_id] = section.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict) -> "PhoenixConfig":
        from vibe_core.phoenix.utils.circuits import CircuitConfig
        from vibe_core.phoenix.utils.routing import RoutingRule
        
        config = cls.from_files()
        if "circuits" in data:
            config.circuits = {}
            for name, circuit_data in data["circuits"].items():
                config.circuits[name] = CircuitConfig.from_dict(circuit_data)
        if "routing" in data:
            config.routing = [RoutingRule.from_dict(r) for r in data["routing"]]
        for section_id, section in config._sections.items():
            if section_id in data and hasattr(section, "from_dict"):
                config._sections[section_id] = type(section).from_dict(data[section_id])
        return config

    # =========================================================================
    # Backward compatibility
    # =========================================================================

    def get(self, key: str, default=None):
        if key.startswith("providers."):
            attr = key.split(".", 1)[1]
            return getattr(self.kernel.providers, attr, default) if self.kernel else default
        elif key.startswith("features."):
            attr = key.split(".", 1)[1]
            return getattr(self.kernel.features, attr, default) if self.kernel else default
        return default

    def set(self, key: str, value) -> bool:
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


def set_config(key: str, value: Any) -> bool:
    """Set a config value by key (convenience wrapper)."""
    return get_config().set(key, value)
