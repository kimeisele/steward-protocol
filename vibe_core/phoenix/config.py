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
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .section_loader import SectionLoader, SectionMeta
from .sections.circuits import CircuitConfig, discover_circuits
from .sections.city import CityConfig
from .sections.kernel import KernelConfig
from .sections.quality import QualityConfig, get_default_quality_config
from .sections.routing import RoutingRule, load_routing_rules, save_routing_rules

logger = logging.getLogger(__name__)


@dataclass
class PhoenixConfig:
    """
    Unified configuration - the Phoenix that never dies.

    Combines all configuration sources into a single typed interface:
    - kernel: System configuration from phoenix.yaml
    - city: Agent City configuration from matrix.yaml
    - quality: Lint/format/test/CI configuration from quality.yaml
    - circuits: Dynamic circuit configs from circuits/*.yaml
    - routing: Hot-swappable routing from MATRIX.md

    FRACTAL: Sections are auto-discovered from vibe_core/phoenix/sections/.
    New section = new file in sections/ with section_id = auto-loaded!
    """

    # Core sections (typed for IDE support)
    kernel: KernelConfig = field(default_factory=KernelConfig)
    city: CityConfig = field(default_factory=CityConfig)
    quality: QualityConfig = field(default_factory=get_default_quality_config)

    # Dynamic collections
    circuits: Dict[str, CircuitConfig] = field(default_factory=dict)
    routing: List[RoutingRule] = field(default_factory=list)

    # Auto-discovered sections (for extensibility)
    # Any NEW section added to sections/ appears here automatically
    _extra_sections: Dict[str, Any] = field(default_factory=dict, repr=False)
    _section_metadata: Dict[str, SectionMeta] = field(default_factory=dict, repr=False)

    # Source file paths (for save/reload)
    _phoenix_path: Optional[Path] = field(default=None, repr=False)
    _matrix_path: Optional[Path] = field(default=None, repr=False)
    _circuits_dir: Optional[Path] = field(default=None, repr=False)
    _routing_path: Optional[Path] = field(default=None, repr=False)
    _quality_path: Optional[Path] = field(default=None, repr=False)
    _config_dir: Optional[Path] = field(default=None, repr=False)

    def __getattr__(self, name: str) -> Any:
        """
        Dynamic access to auto-discovered sections.

        Allows: config.new_section even if new_section was added
        after this code was written.
        """
        # Check extra sections for dynamically discovered ones
        if "_extra_sections" in self.__dict__ and name in self._extra_sections:
            return self._extra_sections[name]
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")

    @classmethod
    def from_files(
        cls,
        phoenix_path: Path = Path("config/phoenix.yaml"),
        matrix_path: Path = Path("config/matrix.yaml"),
        circuits_dir: Path = Path("vibe_core/playbook/circuits"),
        routing_path: Path = Path("MATRIX.md"),
        quality_path: Path = Path("config/quality.yaml"),
        config_dir: Path = Path("config"),
    ) -> "PhoenixConfig":
        """
        Load configuration from all source files.

        Uses SectionLoader for auto-discovery of sections.

        Args:
            phoenix_path: Path to phoenix.yaml (kernel config) - legacy
            matrix_path: Path to matrix.yaml (city config) - legacy
            circuits_dir: Directory containing circuit YAML files
            routing_path: Path to MATRIX.md (routing rules)
            quality_path: Path to quality.yaml (lint/format/CI config) - legacy
            config_dir: Directory containing section YAML files (new auto-discovery)

        Returns:
            Fully loaded PhoenixConfig
        """
        # === AUTO-DISCOVERY: Load sections from config/*.yaml ===
        # Clear cache to ensure fresh discovery
        SectionLoader.clear_cache()
        discovered_sections, section_meta = SectionLoader.discover(config_dir=config_dir)

        # Extract known sections (with fallback to legacy loading)
        kernel = discovered_sections.get("kernel")
        city = discovered_sections.get("city")
        quality = discovered_sections.get("quality")

        # === LEGACY LOADING: Fallback if not discovered from config/*.yaml ===

        # Load kernel config (legacy: phoenix.yaml)
        if kernel is None:
            kernel = KernelConfig()
            if phoenix_path.exists():
                try:
                    with open(phoenix_path) as f:
                        data = yaml.safe_load(f) or {}
                    kernel = KernelConfig.from_dict(data)
                    logger.info(f"Loaded kernel config from {phoenix_path} (legacy)")
                except Exception as e:
                    logger.warning(f"Failed to load {phoenix_path}: {e}")
        else:
            logger.info("Loaded kernel config via auto-discovery")

        # Load city config (legacy: matrix.yaml)
        if city is None:
            city = CityConfig()
            if matrix_path.exists():
                try:
                    with open(matrix_path) as f:
                        data = yaml.safe_load(f) or {}
                    city = CityConfig.from_dict(data)
                    logger.info(f"Loaded city config from {matrix_path} (legacy)")
                except Exception as e:
                    logger.warning(f"Failed to load {matrix_path}: {e}")
        else:
            logger.info("Loaded city config via auto-discovery")

        # Load quality config (legacy: quality.yaml with direct path)
        if quality is None:
            quality = get_default_quality_config()
            if quality_path.exists():
                try:
                    with open(quality_path) as f:
                        data = yaml.safe_load(f) or {}
                    quality = QualityConfig.from_dict(data)
                    logger.info(f"Loaded quality config from {quality_path} (legacy)")
                except Exception as e:
                    logger.warning(f"Failed to load {quality_path}, using defaults: {e}")
        else:
            logger.info("Loaded quality config via auto-discovery")

        # === COLLECTIONS: Circuits and Routing ===

        # Discover circuits
        circuits = discover_circuits(circuits_dir)
        logger.info(f"Discovered {len(circuits)} circuits from {circuits_dir}")

        # Load routing rules
        routing = load_routing_rules(routing_path)
        logger.info(f"Loaded {len(routing)} routing rules from {routing_path}")

        # === EXTRA SECTIONS: Any new sections we don't know about ===
        known_sections = {"kernel", "city", "quality"}
        extra_sections = {
            k: v for k, v in discovered_sections.items() if k not in known_sections
        }
        if extra_sections:
            logger.info(f"Auto-discovered {len(extra_sections)} extra sections: {list(extra_sections.keys())}")

        # === CREATE CONFIG ===
        config = cls(
            kernel=kernel,
            city=city,
            quality=quality,
            circuits=circuits,
            routing=routing,
            _extra_sections=extra_sections,
            _section_metadata=section_meta,
        )

        # Store paths for later save/reload
        config._phoenix_path = phoenix_path
        config._matrix_path = matrix_path
        config._circuits_dir = circuits_dir
        config._routing_path = routing_path
        config._quality_path = quality_path
        config._config_dir = config_dir

        return config

    @classmethod
    def from_env(cls) -> "PhoenixConfig":
        """
        Load configuration from environment variables.

        Environment variables override file defaults.
        """
        import os

        # Start with file-based config
        config = cls.from_files()

        # Override with environment variables
        if os.getenv("PHOENIX_LIVE_FIRE"):
            config.kernel.features.live_fire_enabled = os.getenv("PHOENIX_LIVE_FIRE", "").lower() == "true"

        if os.getenv("PHOENIX_DEBUG"):
            config.kernel.features.debug_mode = os.getenv("PHOENIX_DEBUG", "").lower() == "true"

        if os.getenv("PHOENIX_LLM_PROVIDER"):
            config.kernel.providers.llm_provider = os.getenv("PHOENIX_LLM_PROVIDER", "")

        if os.getenv("PHOENIX_LOG_LEVEL"):
            config.city.monitoring.log_level = os.getenv("PHOENIX_LOG_LEVEL", "INFO")

        return config

    @classmethod
    def create_for_simulation(cls) -> "PhoenixConfig":
        """Factory: Create config for safe simulation mode."""
        config = cls.from_files()
        config.kernel.features.live_fire_enabled = False
        config.kernel.features.debug_mode = True
        return config

    @classmethod
    def create_for_live_fire(cls) -> "PhoenixConfig":
        """Factory: Create config for production/live mode."""
        config = cls.from_files()
        config.kernel.features.live_fire_enabled = True
        config.kernel.features.debug_mode = False
        return config

    def validate(self) -> List[str]:
        """
        Validate all configuration sections.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors: List[str] = []

        # Kernel validation
        if not self.kernel.providers.llm_provider:
            errors.append("kernel.providers.llm_provider is required")

        # City validation
        if self.city.governance.voting_threshold < 0 or self.city.governance.voting_threshold > 1:
            errors.append("city.governance.voting_threshold must be between 0 and 1")

        if self.city.governance.quorum_required < 0 or self.city.governance.quorum_required > 1:
            errors.append("city.governance.quorum_required must be between 0 and 1")

        if self.city.economy.initial_credits < 0:
            errors.append("city.economy.initial_credits must be non-negative")

        # Routing validation
        for i, rule in enumerate(self.routing):
            if not rule.pattern:
                errors.append(f"routing[{i}].pattern is empty")
            if not rule.circuit:
                errors.append(f"routing[{i}].circuit is empty")

        return errors

    def save(self) -> bool:
        """
        Persist configuration back to files.

        Returns:
            True if all saves successful
        """
        success = True

        # Save kernel config
        if self._phoenix_path:
            try:
                self._phoenix_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self._phoenix_path, "w") as f:
                    yaml.dump(self.kernel.to_dict(), f, default_flow_style=False, sort_keys=False)
                logger.info(f"Saved kernel config to {self._phoenix_path}")
            except Exception as e:
                logger.error(f"Failed to save kernel config: {e}")
                success = False

        # Save city config
        if self._matrix_path:
            try:
                self._matrix_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self._matrix_path, "w") as f:
                    yaml.dump(self.city.to_dict(), f, default_flow_style=False, sort_keys=False)
                logger.info(f"Saved city config to {self._matrix_path}")
            except Exception as e:
                logger.error(f"Failed to save city config: {e}")
                success = False

        # Save routing rules
        if self._routing_path:
            if not save_routing_rules(self.routing, self._routing_path):
                logger.error("Failed to save routing rules")
                success = False
            else:
                logger.info(f"Saved routing rules to {self._routing_path}")

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

    # =========================================================================
    # Section Discovery (fractal pattern - mirrors plugin discovery)
    # =========================================================================

    def list_sections(self) -> List[str]:
        """
        List all discovered section IDs.

        Returns:
            List of section identifiers (e.g., ["kernel", "city", "quality"])
        """
        known = ["kernel", "city", "quality"]
        extra = list(self._extra_sections.keys()) if self._extra_sections else []
        return known + extra

    def get_section(self, section_id: str) -> Optional[Any]:
        """
        Get a section by ID (works for both typed and dynamic sections).

        Args:
            section_id: Section identifier (e.g., "kernel", "quality")

        Returns:
            Section instance or None if not found
        """
        if section_id == "kernel":
            return self.kernel
        elif section_id == "city":
            return self.city
        elif section_id == "quality":
            return self.quality
        elif self._extra_sections and section_id in self._extra_sections:
            return self._extra_sections[section_id]
        return None

    def get_section_metadata(self, section_id: str) -> Optional[SectionMeta]:
        """
        Get metadata about a section (source file, priority, etc.).

        Args:
            section_id: Section identifier

        Returns:
            SectionMeta or None if not found
        """
        return self._section_metadata.get(section_id) if self._section_metadata else None

    # =========================================================================
    # Convenience accessors (fractal pattern - same interface at every level)
    # =========================================================================

    @property
    def live_fire_enabled(self) -> bool:
        """Quick access to live fire mode."""
        return self.kernel.features.live_fire_enabled

    @live_fire_enabled.setter
    def live_fire_enabled(self, value: bool) -> None:
        self.kernel.features.live_fire_enabled = value

    @property
    def debug_mode(self) -> bool:
        """Quick access to debug mode."""
        return self.kernel.features.debug_mode

    @debug_mode.setter
    def debug_mode(self, value: bool) -> None:
        self.kernel.features.debug_mode = value

    @property
    def provider_name(self) -> str:
        """Quick access to provider name."""
        return self.kernel.providers.name

    def get_circuit(self, name: str) -> Optional[CircuitConfig]:
        """Get a circuit by name."""
        return self.circuits.get(name)

    def get_active_routes(self) -> List[RoutingRule]:
        """Get only active routing rules."""
        return [r for r in self.routing if r.active]

    def route_intent(self, intent: str) -> Optional[str]:
        """
        Route an intent string to a circuit name.

        Args:
            intent: User intent or input string

        Returns:
            Circuit name if matched, None otherwise
        """
        for rule in self.get_active_routes():
            if rule.matches(intent):
                return rule.circuit
        return None

    # =========================================================================
    # Serialization (for 4D Hypercube / child kernel spawning)
    # =========================================================================

    def to_dict(self) -> Dict:
        """
        Serialize config to dictionary for child kernel spawning.

        Returns:
            Dict representation of entire config
        """
        return {
            "kernel": self.kernel.to_dict(),
            "city": self.city.to_dict(),
            "circuits": {name: circuit.to_dict() for name, circuit in self.circuits.items()},
            "routing": [rule.to_dict() for rule in self.routing],
            "quality": self.quality.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "PhoenixConfig":
        """
        Deserialize config from dictionary.

        Args:
            data: Dict representation of config

        Returns:
            PhoenixConfig instance
        """
        from .sections.circuits import CircuitConfig

        kernel = KernelConfig.from_dict(data.get("kernel", {}))
        city = CityConfig.from_dict(data.get("city", {}))

        circuits = {}
        for name, circuit_data in data.get("circuits", {}).items():
            circuits[name] = CircuitConfig.from_dict(circuit_data)

        routing = []
        for rule_data in data.get("routing", []):
            routing.append(RoutingRule.from_dict(rule_data))

        quality = QualityConfig.from_dict(data.get("quality", {}))

        return cls(
            kernel=kernel,
            city=city,
            circuits=circuits,
            routing=routing,
            quality=quality,
        )

    # =========================================================================
    # Backward compatibility with old phoenix_config API
    # =========================================================================

    def get(self, key: str, default=None):
        """
        Get config value by dotted key path (backward compatibility).

        Maps old-style dotted paths to typed attributes:
        - "providers.llm_provider" -> self.kernel.providers.llm_provider
        - "features.live_fire_enabled" -> self.kernel.features.live_fire_enabled

        Args:
            key: Dotted path like "providers.llm_provider"
            default: Default value if not found

        Returns:
            Config value or default
        """
        # Map old paths to new typed structure
        path_map = {
            "providers.llm_provider": lambda: self.kernel.providers.llm_provider,
            "providers.fallback_provider": lambda: self.kernel.providers.fallback_provider,
            "features.live_fire_enabled": lambda: self.kernel.features.live_fire_enabled,
            "features.debug_mode": lambda: self.kernel.features.debug_mode,
            "features.oauth_enforcement": lambda: self.kernel.features.oauth_enforcement,
            "features.performance_metrics": lambda: self.kernel.features.performance_metrics,
        }

        if key in path_map:
            try:
                return path_map[key]()
            except Exception:
                return default

        return default

    def set(self, key: str, value) -> bool:
        """
        Set config value by dotted key path (backward compatibility).

        Maps old-style dotted paths to typed attributes.

        Args:
            key: Dotted path like "features.live_fire_enabled"
            value: New value to set

        Returns:
            True if successful
        """
        try:
            if key == "providers.llm_provider":
                self.kernel.providers.llm_provider = value
            elif key == "providers.fallback_provider":
                self.kernel.providers.fallback_provider = value
            elif key == "features.live_fire_enabled":
                self.kernel.features.live_fire_enabled = value
            elif key == "features.debug_mode":
                self.kernel.features.debug_mode = value
            elif key == "features.oauth_enforcement":
                self.kernel.features.oauth_enforcement = value
            elif key == "features.performance_metrics":
                self.kernel.features.performance_metrics = value
            else:
                logger.warning(f"Unknown config key: {key}")
                return False

            logger.info(f"Config set: {key} = {value}")
            return True
        except Exception as e:
            logger.error(f"Failed to set {key}: {e}")
            return False


# =========================================================================
# Singleton pattern for global access
# =========================================================================

_config: Optional[PhoenixConfig] = None


def get_config() -> PhoenixConfig:
    """
    Get the global PhoenixConfig instance.

    Lazy-loads from files on first access.

    Returns:
        The PhoenixConfig singleton
    """
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
