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
class FloodConfig:
    """FloodManager - EventBus/SignalBus observation configuration."""

    enabled: bool = True
    # Analysis queue settings
    max_analysis_queue: int = 1000
    analysis_timeout_ms: int = 50
    queue_wait_timeout_seconds: float = 5.0
    # Seen events deduplication
    seen_events_max: int = 10000
    seen_events_trim_size: int = 5000
    # Content extraction
    max_content_size: int = 10000

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FloodConfig":
        return cls(
            enabled=data.get("enabled", True),
            max_analysis_queue=data.get("max_analysis_queue", 1000),
            analysis_timeout_ms=data.get("analysis_timeout_ms", 50),
            queue_wait_timeout_seconds=data.get("queue_wait_timeout_seconds", 5.0),
            seen_events_max=data.get("seen_events_max", 10000),
            seen_events_trim_size=data.get("seen_events_trim_size", 5000),
            max_content_size=data.get("max_content_size", 10000),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "max_analysis_queue": self.max_analysis_queue,
            "analysis_timeout_ms": self.analysis_timeout_ms,
            "queue_wait_timeout_seconds": self.queue_wait_timeout_seconds,
            "seen_events_max": self.seen_events_max,
            "seen_events_trim_size": self.seen_events_trim_size,
            "max_content_size": self.max_content_size,
        }


@dataclass
class CommitWatcherConfig:
    """CommitWatcher - Git pattern detection configuration."""

    enabled: bool = True
    # Pattern detection thresholds
    panic_threshold: int = 3
    panic_window_seconds: int = 300
    stagnation_seconds: int = 600
    deferral_threshold: int = 5
    conflict_rate_threshold: float = 0.5
    # Rolling window
    rolling_window_size: int = 100

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CommitWatcherConfig":
        return cls(
            enabled=data.get("enabled", True),
            panic_threshold=data.get("panic_threshold", 3),
            panic_window_seconds=data.get("panic_window_seconds", 300),
            stagnation_seconds=data.get("stagnation_seconds", 600),
            deferral_threshold=data.get("deferral_threshold", 5),
            conflict_rate_threshold=data.get("conflict_rate_threshold", 0.5),
            rolling_window_size=data.get("rolling_window_size", 100),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "panic_threshold": self.panic_threshold,
            "panic_window_seconds": self.panic_window_seconds,
            "stagnation_seconds": self.stagnation_seconds,
            "deferral_threshold": self.deferral_threshold,
            "conflict_rate_threshold": self.conflict_rate_threshold,
            "rolling_window_size": self.rolling_window_size,
        }


# =============================================================================
# GOVERNANCE LAYER CONFIGS (Phase 9/10 - NOT Nagas by race)
# =============================================================================


@dataclass
class NaradaConfig:
    """🎵 Narada - Deva-Rishi Messenger/Spy configuration."""

    enabled: bool = True
    # Interception limits
    max_interceptions_per_minute: int = 1000
    # Observation depth
    observe_args: bool = True
    observe_return: bool = True
    observe_duration: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NaradaConfig":
        return cls(
            enabled=data.get("enabled", True),
            max_interceptions_per_minute=data.get("max_interceptions_per_minute", 1000),
            observe_args=data.get("observe_args", True),
            observe_return=data.get("observe_return", True),
            observe_duration=data.get("observe_duration", True),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "max_interceptions_per_minute": self.max_interceptions_per_minute,
            "observe_args": self.observe_args,
            "observe_return": self.observe_return,
            "observe_duration": self.observe_duration,
        }


@dataclass
class KaliyaConfig:
    """🐍 Kaliya - Quarantine/Isolation configuration."""

    enabled: bool = True
    # Quarantine settings
    default_quarantine_duration_seconds: int = 3600  # 1 hour
    max_violations_before_quarantine: int = 3
    escalation_threshold: int = 5  # Violations before escalating to 37th

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KaliyaConfig":
        return cls(
            enabled=data.get("enabled", True),
            default_quarantine_duration_seconds=data.get("default_quarantine_duration_seconds", 3600),
            max_violations_before_quarantine=data.get("max_violations_before_quarantine", 3),
            escalation_threshold=data.get("escalation_threshold", 5),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "default_quarantine_duration_seconds": self.default_quarantine_duration_seconds,
            "max_violations_before_quarantine": self.max_violations_before_quarantine,
            "escalation_threshold": self.escalation_threshold,
        }


@dataclass
class ChitraguptaConfig:
    """📜 Chitragupta - Yama's Accountant/Profiler configuration."""

    enabled: bool = True
    # Profiling settings
    baseline_window_size: int = 100  # Samples for baseline calculation
    anomaly_threshold_std: float = 2.0  # Standard deviations for anomaly
    max_profiles: int = 1000  # Max component profiles to track

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChitraguptaConfig":
        return cls(
            enabled=data.get("enabled", True),
            baseline_window_size=data.get("baseline_window_size", 100),
            anomaly_threshold_std=data.get("anomaly_threshold_std", 2.0),
            max_profiles=data.get("max_profiles", 1000),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "baseline_window_size": self.baseline_window_size,
            "anomaly_threshold_std": self.anomaly_threshold_std,
            "max_profiles": self.max_profiles,
        }


@dataclass
class PrahladConfig:
    """👑 Prahlad - Daitya Governor/Resilience configuration."""

    enabled: bool = True
    # Antifragility settings
    auto_generate_tests: bool = True
    chaos_probe_enabled: bool = True
    dharma_audit_interval_seconds: int = 3600  # 1 hour
    # Phoenix guarantee
    verify_state_preservation: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PrahladConfig":
        return cls(
            enabled=data.get("enabled", True),
            auto_generate_tests=data.get("auto_generate_tests", True),
            chaos_probe_enabled=data.get("chaos_probe_enabled", True),
            dharma_audit_interval_seconds=data.get("dharma_audit_interval_seconds", 3600),
            verify_state_preservation=data.get("verify_state_preservation", True),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "auto_generate_tests": self.auto_generate_tests,
            "chaos_probe_enabled": self.chaos_probe_enabled,
            "dharma_audit_interval_seconds": self.dharma_audit_interval_seconds,
            "verify_state_preservation": self.verify_state_preservation,
        }


@dataclass
class AnantaConfig:
    """♾️ Ananta - Gene Splicer + Loader Governor configuration."""

    enabled: bool = True
    # Loader governance settings
    wrap_manifest_registry: bool = True
    max_load_events: int = 10000  # LRU limit for load event tracking

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnantaConfig":
        return cls(
            enabled=data.get("enabled", True),
            wrap_manifest_registry=data.get("wrap_manifest_registry", True),
            max_load_events=data.get("max_load_events", 10000),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "wrap_manifest_registry": self.wrap_manifest_registry,
            "max_load_events": self.max_load_events,
        }


@dataclass
class VisibilityConfig:
    """
    Visibility Matrix configuration.

    "Erst sehen, dann handeln" - No hardcoded values.
    All thresholds are configurable for fractal scalability.
    """

    enabled: bool = True

    # Coverage targets (what counts as 100%)
    target_naga_tests: int = 600  # Total NAGA test target
    tests_per_component: int = 10  # Tests per component for 100%

    # Status thresholds (percentage)
    protected_threshold: float = 70.0  # >= this = Protected
    monitoring_threshold: float = 30.0  # >= this = Monitoring, below = Blind

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VisibilityConfig":
        return cls(
            enabled=data.get("enabled", True),
            target_naga_tests=data.get("target_naga_tests", 600),
            tests_per_component=data.get("tests_per_component", 10),
            protected_threshold=data.get("protected_threshold", 70.0),
            monitoring_threshold=data.get("monitoring_threshold", 30.0),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "target_naga_tests": self.target_naga_tests,
            "tests_per_component": self.tests_per_component,
            "protected_threshold": self.protected_threshold,
            "monitoring_threshold": self.monitoring_threshold,
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

    # ===== INFRASTRUCTURE LAYER (Real Nagas - 🐍) =====
    sesha: SeshaConfig = field(default_factory=SeshaConfig)
    vasuki: VasukiConfig = field(default_factory=VasukiConfig)
    takshaka: TakshakaConfig = field(default_factory=TakshakaConfig)
    kaliya: KaliyaConfig = field(default_factory=KaliyaConfig)

    # ===== GOVERNANCE LAYER (Personnel - NOT Nagas) =====
    narada: NaradaConfig = field(default_factory=NaradaConfig)
    chitragupta: ChitraguptaConfig = field(default_factory=ChitraguptaConfig)
    prahlad: PrahladConfig = field(default_factory=PrahladConfig)
    ananta: AnantaConfig = field(default_factory=AnantaConfig)

    # ===== INFRASTRUCTURE COMPONENTS =====
    cortex: CortexConfig = field(default_factory=CortexConfig)
    flood: FloodConfig = field(default_factory=FloodConfig)
    commit_watcher: CommitWatcherConfig = field(default_factory=CommitWatcherConfig)

    # ===== VISIBILITY MATRIX =====
    visibility: VisibilityConfig = field(default_factory=VisibilityConfig)

    # ===== OUROBOROS SELF-GOVERNANCE =====
    verify_on_boot: bool = True  # Run Prahlad self-check at boot

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
            # Infrastructure Layer (Real Nagas)
            sesha=SeshaConfig.from_dict(data.get("sesha", {})),
            vasuki=VasukiConfig.from_dict(data.get("vasuki", {})),
            takshaka=TakshakaConfig.from_dict(data.get("takshaka", {})),
            kaliya=KaliyaConfig.from_dict(data.get("kaliya", {})),
            # Governance Layer (Personnel)
            narada=NaradaConfig.from_dict(data.get("narada", {})),
            chitragupta=ChitraguptaConfig.from_dict(data.get("chitragupta", {})),
            prahlad=PrahladConfig.from_dict(data.get("prahlad", {})),
            # Infrastructure Components
            cortex=CortexConfig.from_dict(data.get("cortex", {})),
            flood=FloodConfig.from_dict(data.get("flood", {})),
            commit_watcher=CommitWatcherConfig.from_dict(data.get("commit_watcher", {})),
            # Visibility Matrix
            visibility=VisibilityConfig.from_dict(data.get("visibility", {})),
        )
        config._loaded_from_yaml = True
        return config

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to YAML-compatible dict."""
        return {
            # Infrastructure Layer (Real Nagas)
            "sesha": self.sesha.to_dict(),
            "vasuki": self.vasuki.to_dict(),
            "takshaka": self.takshaka.to_dict(),
            "kaliya": self.kaliya.to_dict(),
            # Governance Layer (Personnel)
            "narada": self.narada.to_dict(),
            "chitragupta": self.chitragupta.to_dict(),
            "prahlad": self.prahlad.to_dict(),
            # Infrastructure Components
            "cortex": self.cortex.to_dict(),
            "flood": self.flood.to_dict(),
            "commit_watcher": self.commit_watcher.to_dict(),
            # Visibility Matrix
            "visibility": self.visibility.to_dict(),
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
        # Infrastructure Layer
        config.sesha.enabled = False
        config.vasuki.enabled = False
        config.takshaka.enabled = False
        config.kaliya.enabled = False
        # Governance Layer
        config.narada.enabled = False
        config.chitragupta.enabled = False
        config.prahlad.enabled = False
        # Infrastructure Components
        config.cortex.enabled = False
        config.flood.enabled = False
        config.commit_watcher.enabled = False
        return config
