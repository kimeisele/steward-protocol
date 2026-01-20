"""
Mahamantra Configuration - Holy Names, Resonance, Chat Defaults.

VEDA-4 Pattern:
    SHABDA: Auto-discovered from vibe_core/phoenix/sections/mahamantra/
    ARTHA: Parsed from config/mahamantra.yaml
    PRATYAYA: Validated (holy names must be Set[str], thresholds must be float)
    KARMA: Instantiated as MahamantraConfig dataclass

ANANTA-NAMA PRINCIPLE:
    Krishna has infinite names. This config provides the SEED set.
    KnowledgeGraph can extend this dynamically via learning.

SIMPLE INJECTION POINT, MAX EFFECT:
    - One place to configure holy names
    - ChatService, resonance, routing - ALL read from here
    - No hardcoding anywhere else
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x5e8c9a12"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class HolyNamesConfig:
    """
    Holy Names configuration - ananta-nama (infinite names).

    seed: Initial set of holy names (always highest resonance)
    resonance: Resonance score for holy names (default 1.0)
    learnable: Whether KnowledgeGraph can extend this
    knowledge_domain: Domain in KnowledgeGraph for learned names
    """

    seed: Set[str] = field(default_factory=lambda: {
        "hare", "krishna", "rama", "om", "hari", "govinda", "madhava"
    })
    resonance: float = 1.0
    learnable: bool = True
    knowledge_domain: str = "sacred_names"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HolyNamesConfig":
        seed = set(data.get("seed", []))
        return cls(
            seed=seed if seed else cls().seed,
            resonance=float(data.get("resonance", 1.0)),
            learnable=bool(data.get("learnable", True)),
            knowledge_domain=str(data.get("knowledge_domain", "sacred_names")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seed": list(self.seed),
            "resonance": self.resonance,
            "learnable": self.learnable,
            "knowledge_domain": self.knowledge_domain,
        }

    def is_sacred(self, word: str) -> bool:
        """Check if a word is a holy name (case-insensitive)."""
        return word.lower() in self.seed

    def get_all_names(self) -> Set[str]:
        """
        Get all holy names (seed + learned from KnowledgeGraph).

        TODO: Query KnowledgeGraph for learned names if learnable=True.
        For now, just returns seed.
        """
        return self.seed.copy()


@dataclass
class ResonanceConfig:
    """Resonance thresholds for Starship Command I/O."""

    auto_execute: float = 0.7  # > this: auto-proceed
    refinement: float = 0.4   # > this: ask user to clarify
    silence: float = 0.0       # < refinement: no resonance (disabled for chat)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResonanceConfig":
        return cls(
            auto_execute=float(data.get("auto_execute", 0.7)),
            refinement=float(data.get("refinement", 0.4)),
            silence=float(data.get("silence", 0.0)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "auto_execute": self.auto_execute,
            "refinement": self.refinement,
            "silence": self.silence,
        }


@dataclass
class ChatConfig:
    """Default configuration for chat operations."""

    default_mahajana: str = "narada"
    default_position: int = 2
    fallback_mode: str = "direct"
    min_routing_confidence: float = 0.6

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatConfig":
        return cls(
            default_mahajana=str(data.get("default_mahajana", "narada")),
            default_position=int(data.get("default_position", 2)),
            fallback_mode=str(data.get("fallback_mode", "direct")),
            min_routing_confidence=float(data.get("min_routing_confidence", 0.6)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "default_mahajana": self.default_mahajana,
            "default_position": self.default_position,
            "fallback_mode": self.fallback_mode,
            "min_routing_confidence": self.min_routing_confidence,
        }


@dataclass
class QuarterConfig:
    """Configuration for a single quarter."""

    positions: List[int] = field(default_factory=list)
    dominant: str = "hare"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuarterConfig":
        return cls(
            positions=list(data.get("positions", [])),
            dominant=str(data.get("dominant", "hare")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "positions": self.positions,
            "dominant": self.dominant,
        }


@dataclass
class MahamantraConfig:
    """
    Mahamantra Configuration - SSOT for holy names, resonance, chat.

    Auto-discovered by SectionLoader -> loads from config/mahamantra.yaml

    PRINCIPLE: Simple injection point, max effect.
    - Configure here, use everywhere
    - No hardcoding of holy names, thresholds, etc.
    - KnowledgeGraph can extend holy names dynamically

    Usage:
        from vibe_core.phoenix import get_config
        config = get_config()

        # Check if word is sacred
        if config.mahamantra.holy_names.is_sacred("krishna"):
            ...

        # Get resonance threshold
        if magnitude > config.mahamantra.resonance.auto_execute:
            ...

        # Get all holy names (including learned)
        names = config.mahamantra.holy_names.get_all_names()
    """

    holy_names: HolyNamesConfig = field(default_factory=HolyNamesConfig)
    resonance: ResonanceConfig = field(default_factory=ResonanceConfig)
    chat: ChatConfig = field(default_factory=ChatConfig)
    quarters: Dict[str, QuarterConfig] = field(default_factory=dict)
    opcodes: Dict[str, str] = field(default_factory=dict)

    # Section protocol requirement
    section_id: str = "mahamantra"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MahamantraConfig":
        """Load from config/mahamantra.yaml."""

        # Parse quarters
        quarters_raw = data.get("quarters", {})
        quarters = {
            name: QuarterConfig.from_dict(qdata)
            for name, qdata in quarters_raw.items()
        }

        # Default quarters if not provided
        if not quarters:
            quarters = {
                "genesis": QuarterConfig(positions=[0, 1, 2, 3], dominant="hare"),
                "dharma": QuarterConfig(positions=[4, 5, 6, 7], dominant="krishna"),
                "karma": QuarterConfig(positions=[8, 9, 10, 11], dominant="rama"),
                "moksha": QuarterConfig(positions=[12, 13, 14, 15], dominant="rama"),
            }

        # Default opcodes if not provided
        opcodes = data.get("opcodes", {
            "genesis": "SYS_WAKE",
            "dharma": "COMPILE_AST",
            "karma": "EXEC_OP",
            "moksha": "YIELD_CPU",
        })

        return cls(
            holy_names=HolyNamesConfig.from_dict(data.get("holy_names", {})),
            resonance=ResonanceConfig.from_dict(data.get("resonance", {})),
            chat=ChatConfig.from_dict(data.get("chat", {})),
            quarters=quarters,
            opcodes=opcodes,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for saving."""
        return {
            "holy_names": self.holy_names.to_dict(),
            "resonance": self.resonance.to_dict(),
            "chat": self.chat.to_dict(),
            "quarters": {name: q.to_dict() for name, q in self.quarters.items()},
            "opcodes": self.opcodes,
        }

    # =========================================================================
    # CONVENIENCE METHODS (Simple injection point, max effect)
    # =========================================================================

    def is_sacred(self, word: str) -> bool:
        """Check if word is a holy name."""
        return self.holy_names.is_sacred(word)

    def get_sacred_resonance(self) -> float:
        """Get resonance score for holy names."""
        return self.holy_names.resonance

    def should_auto_execute(self, magnitude: float) -> bool:
        """Check if magnitude is high enough for auto-execution."""
        return magnitude >= self.resonance.auto_execute

    def needs_refinement(self, magnitude: float) -> bool:
        """Check if magnitude is in the refinement zone."""
        return self.resonance.refinement <= magnitude < self.resonance.auto_execute

    def get_quarter_dominant(self, quarter_name: str) -> str:
        """Get dominant holy name for a quarter."""
        quarter = self.quarters.get(quarter_name.lower())
        return quarter.dominant if quarter else "hare"

    def get_quarter_for_position(self, position: int) -> str:
        """Get quarter name for a position."""
        for name, q in self.quarters.items():
            if position in q.positions:
                return name
        return "genesis"

    def get_opcode_for_quarter(self, quarter_name: str) -> str:
        """Get opcode for a quarter."""
        return self.opcodes.get(quarter_name.lower(), "SYS_WAKE")


# =============================================================================
# SINGLETON ACCESS (for protocol compliance)
# =============================================================================

_mahamantra_config: Optional[MahamantraConfig] = None


def get_mahamantra_config() -> MahamantraConfig:
    """
    Get MahamantraConfig instance.

    Prefer using get_config().mahamantra for unified access.
    This function is for cases where only mahamantra config is needed.
    """
    global _mahamantra_config
    if _mahamantra_config is None:
        try:
            from vibe_core.phoenix import get_config
            config = get_config()
            _mahamantra_config = config.mahamantra
        except Exception:
            # Fallback to defaults
            _mahamantra_config = MahamantraConfig()
    return _mahamantra_config


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MahamantraConfig",
    "HolyNamesConfig",
    "ResonanceConfig",
    "ChatConfig",
    "QuarterConfig",
    "get_mahamantra_config",
]
