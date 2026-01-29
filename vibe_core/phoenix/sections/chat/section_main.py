"""
CHAT CONFIGURATION - Fractal Phoenix Section for Chat Operations.

VEDA-4 Pattern:
    SHABDA: Auto-discovered from vibe_core/phoenix/sections/chat/
    ARTHA: Parsed from config/chat.yaml
    PRATYAYA: Validated (thresholds must be float, modes must be str)
    KARMA: Instantiated as ChatSectionConfig dataclass

FRACTAL PRINCIPLE:
    Chat is a SEPARATE concern from Mahamantra.
    - Mahamantra = The sacred names, quarters, opcodes (WHAT)
    - Chat = How the system routes/handles conversations (HOW)

SSOT PRINCIPLE:
    This config is the SINGLE SOURCE for all chat-related settings.
    - ChatSubstrateBridge reads from here
    - ChatService reads from here
    - CLI chat command reads from here

Usage:
    from vibe_core.phoenix import get_config
    config = get_config()

    # Get chat inertia
    inertia = config.chat.substrate.inertia

    # Check routing mode
    if config.chat.routing.mode == "mahajana":
        ...
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xce76c154"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SubstrateBridgeConfig:
    """
    Configuration for ChatSubstrateBridge.

    Controls how vibration (text) is converted to substrate routing.
    """

    # Energy thresholds (derived from Mahamantra harmonics)
    inertia: float = 0.3  # Minimum energy for manifestation

    # Threshold overrides (if different from mahamantra.resonance)
    # None = use mahamantra defaults
    threshold_manifest: Optional[float] = None  # Default: NADI/MALA = 72/108 ≈ 0.667
    threshold_negotiate: Optional[float] = None  # Default: LILA/MALA = 48/108 ≈ 0.444

    # Tensor settings
    digraph_priority: bool = True  # Check digraphs (ch, th) before single chars
    normalize_vectors: bool = True  # Normalize varga/sthana vectors to sum=1

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SubstrateBridgeConfig":
        return cls(
            inertia=float(data.get("inertia", 0.3)),
            threshold_manifest=data.get("threshold_manifest"),
            threshold_negotiate=data.get("threshold_negotiate"),
            digraph_priority=bool(data.get("digraph_priority", True)),
            normalize_vectors=bool(data.get("normalize_vectors", True)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inertia": self.inertia,
            "threshold_manifest": self.threshold_manifest,
            "threshold_negotiate": self.threshold_negotiate,
            "digraph_priority": self.digraph_priority,
            "normalize_vectors": self.normalize_vectors,
        }


@dataclass
class RoutingConfig:
    """
    Configuration for chat routing decisions.
    """

    # Routing mode: "mahajana" (substrate-based) or "direct" (bypass)
    mode: str = "mahajana"

    # Default Mahajana for fallback
    default_mahajana: str = "narada"
    default_position: int = 2

    # Confidence thresholds
    min_routing_confidence: float = 0.6
    fallback_on_low_confidence: bool = True

    # Alternative routes
    max_alternatives: int = 3
    alternative_energy_factor: float = 0.8  # Alternatives get 80% of primary energy

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoutingConfig":
        return cls(
            mode=str(data.get("mode", "mahajana")),
            default_mahajana=str(data.get("default_mahajana", "narada")),
            default_position=int(data.get("default_position", 2)),
            min_routing_confidence=float(data.get("min_routing_confidence", 0.6)),
            fallback_on_low_confidence=bool(data.get("fallback_on_low_confidence", True)),
            max_alternatives=int(data.get("max_alternatives", 3)),
            alternative_energy_factor=float(data.get("alternative_energy_factor", 0.8)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "default_mahajana": self.default_mahajana,
            "default_position": self.default_position,
            "min_routing_confidence": self.min_routing_confidence,
            "fallback_on_low_confidence": self.fallback_on_low_confidence,
            "max_alternatives": self.max_alternatives,
            "alternative_energy_factor": self.alternative_energy_factor,
        }


@dataclass
class PhoneticConfig:
    """
    Configuration for phonetic analysis (VarnaTensor).
    """

    # Enable/disable phonetic routing
    enabled: bool = True

    # Varga (WHERE) settings
    varga_weight: float = 0.6  # Weight of varga in routing decision

    # Sthana (HOW) settings
    sthana_weight: float = 0.4  # Weight of sthana in routing decision

    # Energy calculation
    energy_formula: str = "weighted"  # "weighted" or "dominant"

    # Language hints
    default_language: Optional[str] = None  # None = auto-detect
    supported_languages: List[str] = field(default_factory=lambda: ["en", "de", "sa", "hi"])

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PhoneticConfig":
        return cls(
            enabled=bool(data.get("enabled", True)),
            varga_weight=float(data.get("varga_weight", 0.6)),
            sthana_weight=float(data.get("sthana_weight", 0.4)),
            energy_formula=str(data.get("energy_formula", "weighted")),
            default_language=data.get("default_language"),
            supported_languages=list(data.get("supported_languages", ["en", "de", "sa", "hi"])),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "varga_weight": self.varga_weight,
            "sthana_weight": self.sthana_weight,
            "energy_formula": self.energy_formula,
            "default_language": self.default_language,
            "supported_languages": self.supported_languages,
        }


@dataclass
class RefinementConfig:
    """
    Configuration for chat refinement (gray zone handling).
    """

    # Enable refinement prompts in gray zone
    enabled: bool = True

    # Maximum refinement attempts before fallback
    max_attempts: int = 3

    # Refinement strategy
    strategy: str = "clarify"  # "clarify", "alternatives", "escalate"

    # Timeout (seconds) for user response
    timeout_seconds: float = 30.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RefinementConfig":
        return cls(
            enabled=bool(data.get("enabled", True)),
            max_attempts=int(data.get("max_attempts", 3)),
            strategy=str(data.get("strategy", "clarify")),
            timeout_seconds=float(data.get("timeout_seconds", 30.0)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "max_attempts": self.max_attempts,
            "strategy": self.strategy,
            "timeout_seconds": self.timeout_seconds,
        }


@dataclass
class ProviderConfig:
    """
    Configuration for chat LLM provider.
    """

    # Provider selection (None = use default from llm section)
    provider: Optional[str] = None
    model: Optional[str] = None

    # Generation settings
    temperature: float = 0.7
    max_tokens: int = 4096

    # Streaming
    stream: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProviderConfig":
        return cls(
            provider=data.get("provider"),
            model=data.get("model"),
            temperature=float(data.get("temperature", 0.7)),
            max_tokens=int(data.get("max_tokens", 4096)),
            stream=bool(data.get("stream", True)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": self.stream,
        }


@dataclass
class ChatSectionConfig:
    """
    Chat Configuration - SSOT for all chat operations.

    Auto-discovered by SectionLoader -> loads from config/chat.yaml

    FRACTAL STRUCTURE:
        chat:
            substrate: SubstrateBridgeConfig
            routing: RoutingConfig
            phonetic: PhoneticConfig
            refinement: RefinementConfig
            provider: ProviderConfig

    Usage:
        from vibe_core.phoenix import get_config
        config = get_config()

        # Access chat config
        inertia = config.chat.substrate.inertia
        mode = config.chat.routing.mode
    """

    substrate: SubstrateBridgeConfig = field(default_factory=SubstrateBridgeConfig)
    routing: RoutingConfig = field(default_factory=RoutingConfig)
    phonetic: PhoneticConfig = field(default_factory=PhoneticConfig)
    refinement: RefinementConfig = field(default_factory=RefinementConfig)
    provider: ProviderConfig = field(default_factory=ProviderConfig)

    # Section protocol requirement
    section_id: str = "chat"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatSectionConfig":
        """Load from config/chat.yaml."""
        return cls(
            substrate=SubstrateBridgeConfig.from_dict(data.get("substrate", {})),
            routing=RoutingConfig.from_dict(data.get("routing", {})),
            phonetic=PhoneticConfig.from_dict(data.get("phonetic", {})),
            refinement=RefinementConfig.from_dict(data.get("refinement", {})),
            provider=ProviderConfig.from_dict(data.get("provider", {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for saving."""
        return {
            "substrate": self.substrate.to_dict(),
            "routing": self.routing.to_dict(),
            "phonetic": self.phonetic.to_dict(),
            "refinement": self.refinement.to_dict(),
            "provider": self.provider.to_dict(),
        }

    # =========================================================================
    # CONVENIENCE METHODS
    # =========================================================================

    def get_effective_inertia(self) -> float:
        """Get the effective inertia threshold."""
        return self.substrate.inertia

    def is_phonetic_enabled(self) -> bool:
        """Check if phonetic routing is enabled."""
        return self.phonetic.enabled

    def should_refine(self, energy: float) -> bool:
        """Check if energy is in refinement zone."""
        manifest = self.substrate.threshold_manifest or 0.667
        negotiate = self.substrate.threshold_negotiate or 0.444
        return negotiate <= energy < manifest

    def get_routing_mode(self) -> str:
        """Get the current routing mode."""
        return self.routing.mode


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_chat_config: Optional[ChatSectionConfig] = None


def get_chat_config() -> ChatSectionConfig:
    """
    Get ChatSectionConfig instance.

    Prefer using get_config().chat for unified access.
    This function is for cases where only chat config is needed.
    """
    global _chat_config
    if _chat_config is None:
        try:
            from vibe_core.phoenix import get_config

            config = get_config()
            _chat_config = config.chat
        except Exception:
            # Fallback to defaults
            _chat_config = ChatSectionConfig()
    return _chat_config


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ChatSectionConfig",
    "SubstrateBridgeConfig",
    "RoutingConfig",
    "PhoneticConfig",
    "RefinementConfig",
    "ProviderConfig",
    "get_chat_config",
]
