"""
NAGA Federation Configuration.

"Niemand darf es merken" - they infiltrate invisibly.

Environment Variables:
    NAGA_TRUST_MODE: "strict" | "permissive" (default: strict)
    NAGA_STRICT: "1" | "0" - alias for NAGA_TRUST_MODE=strict
    NAGA_GOSSIP_ENABLED: "1" | "0" (default: 0)
    NAGA_TOXICITY_THRESHOLD: float (default: 0.3)
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal

logger = logging.getLogger(__name__)

TrustMode = Literal["strict", "permissive"]


@dataclass
class SeshaConfig:
    """Sesha - Data Layer configuration."""

    enabled: bool = True
    gossip_enabled: bool = False  # Disabled until federation ready
    block_size: int = 100
    sync_interval_seconds: int = 60

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SeshaConfig":
        return cls(
            enabled=data.get("enabled", True),
            gossip_enabled=data.get("gossip_enabled", False),
            block_size=data.get("block_size", 100),
            sync_interval_seconds=data.get("sync_interval_seconds", 60),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "gossip_enabled": self.gossip_enabled,
            "block_size": self.block_size,
            "sync_interval_seconds": self.sync_interval_seconds,
        }


@dataclass
class VasukiConfig:
    """Vasuki - Transform Layer configuration."""

    enabled: bool = True
    serialization_format: str = "msgpack"  # "msgpack" | "json"
    sign_outbound: bool = True
    validate_schema: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VasukiConfig":
        return cls(
            enabled=data.get("enabled", True),
            serialization_format=data.get("serialization_format", "msgpack"),
            sign_outbound=data.get("sign_outbound", True),
            validate_schema=data.get("validate_schema", True),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "serialization_format": self.serialization_format,
            "sign_outbound": self.sign_outbound,
            "validate_schema": self.validate_schema,
        }


@dataclass
class TakshakaConfig:
    """Takshaka - Security Layer configuration."""

    enabled: bool = True
    trust_mode: TrustMode = "strict"
    toxicity_threshold: float = 0.3
    rate_limit_rpm: int = 60
    rate_limit_window: float = 60.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TakshakaConfig":
        return cls(
            enabled=data.get("enabled", True),
            trust_mode=data.get("trust_mode", "strict"),
            toxicity_threshold=data.get("toxicity_threshold", 0.3),
            rate_limit_rpm=data.get("rate_limit_rpm", 60),
            rate_limit_window=data.get("rate_limit_window", 60.0),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "trust_mode": self.trust_mode,
            "toxicity_threshold": self.toxicity_threshold,
            "rate_limit_rpm": self.rate_limit_rpm,
            "rate_limit_window": self.rate_limit_window,
        }


@dataclass
class CortexConfig:
    """Cortex - Central Nervous System configuration."""

    enabled: bool = True
    signal_buffer_size: int = 100
    correlation_threshold: int = 3
    max_signal_age_seconds: float = 300.0
    auto_dispatch: bool = True
    log_decisions: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CortexConfig":
        return cls(
            enabled=data.get("enabled", True),
            signal_buffer_size=data.get("signal_buffer_size", 100),
            correlation_threshold=data.get("correlation_threshold", 3),
            max_signal_age_seconds=data.get("max_signal_age_seconds", 300.0),
            auto_dispatch=data.get("auto_dispatch", True),
            log_decisions=data.get("log_decisions", True),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "signal_buffer_size": self.signal_buffer_size,
            "correlation_threshold": self.correlation_threshold,
            "max_signal_age_seconds": self.max_signal_age_seconds,
            "auto_dispatch": self.auto_dispatch,
            "log_decisions": self.log_decisions,
        }


@dataclass
class NagaConfig:
    """
    NAGA Federation Configuration.

    Auto-discovered by Phoenix SectionLoader.
    Environment variables override YAML values.

    Usage:
        from vibe_core.phoenix import get_config
        config = get_config()
        config.naga.takshaka.trust_mode  # "strict" or "permissive"
    """

    section_id = "naga"
    source_file = "naga.yaml"

    sesha: SeshaConfig = field(default_factory=SeshaConfig)
    vasuki: VasukiConfig = field(default_factory=VasukiConfig)
    takshaka: TakshakaConfig = field(default_factory=TakshakaConfig)
    cortex: CortexConfig = field(default_factory=CortexConfig)

    # Track if loaded from YAML vs defaults
    _loaded_from_yaml: bool = field(default=False, repr=False)

    def __post_init__(self):
        """Apply environment variable overrides."""
        self._apply_env_overrides()

    def _apply_env_overrides(self) -> None:
        """Override config from environment variables."""
        # NAGA_STRICT=1 is an alias for trust_mode=strict
        if os.getenv("NAGA_STRICT", "").lower() in ("1", "true", "yes"):
            self.takshaka.trust_mode = "strict"
            logger.info("NAGA: NAGA_STRICT=1 -> trust_mode=strict")

        # NAGA_TRUST_MODE overrides directly
        trust_mode = os.getenv("NAGA_TRUST_MODE")
        if trust_mode in ("strict", "permissive"):
            self.takshaka.trust_mode = trust_mode
            logger.info(f"NAGA: NAGA_TRUST_MODE={trust_mode}")

        # NAGA_GOSSIP_ENABLED
        if os.getenv("NAGA_GOSSIP_ENABLED", "").lower() in ("1", "true", "yes"):
            self.sesha.gossip_enabled = True
            logger.info("NAGA: NAGA_GOSSIP_ENABLED=1")

        # NAGA_TOXICITY_THRESHOLD
        toxicity_str = os.getenv("NAGA_TOXICITY_THRESHOLD")
        if toxicity_str:
            try:
                self.takshaka.toxicity_threshold = float(toxicity_str)
                logger.info(f"NAGA: NAGA_TOXICITY_THRESHOLD={self.takshaka.toxicity_threshold}")
            except ValueError:
                logger.warning(f"NAGA: Invalid NAGA_TOXICITY_THRESHOLD: {toxicity_str}")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NagaConfig":
        """Create from parsed YAML dict."""
        config = cls(
            sesha=SeshaConfig.from_dict(data.get("sesha", {})),
            vasuki=VasukiConfig.from_dict(data.get("vasuki", {})),
            takshaka=TakshakaConfig.from_dict(data.get("takshaka", {})),
            cortex=CortexConfig.from_dict(data.get("cortex", {})),
        )
        config._loaded_from_yaml = True
        return config

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to YAML-compatible dict."""
        return {
            "sesha": self.sesha.to_dict(),
            "vasuki": self.vasuki.to_dict(),
            "takshaka": self.takshaka.to_dict(),
            "cortex": self.cortex.to_dict(),
        }

    def validate(self) -> List[str]:
        """Validate configuration."""
        errors = []

        # Trust mode validation
        if self.takshaka.trust_mode not in ("strict", "permissive"):
            errors.append(f"takshaka.trust_mode must be 'strict' or 'permissive', got '{self.takshaka.trust_mode}'")

        # Toxicity threshold validation
        if not 0.0 <= self.takshaka.toxicity_threshold <= 1.0:
            errors.append(f"takshaka.toxicity_threshold must be 0.0-1.0, got {self.takshaka.toxicity_threshold}")

        # Serialization format validation
        if self.vasuki.serialization_format not in ("msgpack", "json"):
            errors.append("vasuki.serialization_format must be 'msgpack' or 'json'")

        return errors

    # =========================================================================
    # Factory methods
    # =========================================================================

    @classmethod
    def permissive(cls) -> "NagaConfig":
        """Development mode - relaxed security."""
        config = cls()
        config.takshaka.trust_mode = "permissive"
        config.sesha.gossip_enabled = False
        return config

    @classmethod
    def production(cls) -> "NagaConfig":
        """Production mode - strict security."""
        config = cls()
        config.takshaka.trust_mode = "strict"
        config.vasuki.sign_outbound = True
        return config

    @classmethod
    def disabled(cls) -> "NagaConfig":
        """All NAGAs disabled."""
        config = cls()
        config.sesha.enabled = False
        config.vasuki.enabled = False
        config.takshaka.enabled = False
        return config
