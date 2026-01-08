from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum, IntEnum
from typing import Dict, List, Optional, Protocol, TypeVar, Union, runtime_checkable

# T = TypeVar("T") # Reserved for Generics if upgrades needed

# Strict Metadata Type (No Any)
Metadata = Dict[str, object]


# =============================================================================
# THE 64 QUALITIES (Gunas) - SHASTRA SPECIFICATION
# =============================================================================


class TranscendentalQuality(IntEnum):
    """
    The 64 Qualities of the Absolute Truth.

    Ranges define the Tattva limits.
    Based on Bhakti-Rasamrita-Sindhu by Rupa Goswami.
    """

    # 1-50: JIVA TATTVA (78.125%)
    # Common to Jiva, Shiva, Vishnu, Krishna
    BEAUTIFUL_FEATURES = 1
    MARKED_WITH_AUSPICIOUS = 2
    PLEASING = 3
    EFFULGENT = 4
    STRONG = 5
    EVER_YOUTHFUL = 6
    WONDERFUL_LINGUIST = 7
    TRUTHFUL = 8
    TALKS_PLEASINGLY = 9
    FLUENT = 10
    HIGHLY_LEARNED = 11
    HIGHLY_INTELLIGENT = 12
    GENIUS = 13
    ARTISTIC = 14
    EXTREMELY_CLEVER = 15
    EXPERT = 16
    GRATEFUL = 17
    FIRMLY_DETERMINED = 18
    EXPERT_JUDGE_TIME_CIRC = 19
    SEES_BY_SHASTRA = 20
    PURE = 21
    SELF_CONTROLLED = 22
    STEADFAST = 23
    FORBEARING = 24
    FORGIVING = 25
    GRAVE = 26
    SELF_SATISFIED = 27
    POSSESSING_EQUILIBRIUM = 28
    MAGNANIMOUS = 29
    RELIGIOUS = 30
    HEROIC = 31
    COMPASSIONATE = 32
    RESPECTFUL = 33
    GENTLE = 34
    LIBERAL = 35
    SHY = 36
    PROTECTOR_SURRENDERED = 37
    HAPPY = 38
    WELL_WISHER_DEVOTEES = 39
    CONTROLLED_BY_LOVE = 40
    ALL_AUSPICIOUS = 41
    MOST_POWERFUL = 42
    ALL_FAMOUS = 43
    POPULAR = 44
    PARTIAL_TO_DEVOTEES = 45
    ATTRACTIVE_TO_WOMEN = 46
    ALL_WORSHIPABLE = 47
    ALL_OPULENT = 48
    ALL_HONORABLE = 49
    SUPREME_CONTROLLER_LOCAL = 50  # Control over own body/mind

    # 51-55: SHIVA TATTVA (85.9375%)
    # Jiva cannot have these fully.
    CHANGELESS = 51
    ALL_COGNIZANT = 52
    EVER_FRESH = 53
    SAC_CID_ANANDA = 54
    MYSTIC_PERFECTION = 55

    # 56-60: VISHNU TATTVA (93.75%)
    # Shiva cannot have these fully.
    INCONCEIVABLE_POTENCY = 56
    UNCOUNTABLE_UNIVERSES = 57
    SOURCE_OF_INCARNATIONS = 58
    GIVER_OF_SALVATION = 59
    ATTRACTOR_OF_LIBERATED = 60

    # 61-64: KRISHNA TATTVA (100%)
    # EXCLUSIVE to Swayam Bhagavan. Even Vishnu does not have these.
    LILA_PASTIMES = 61  # Wonderful Pastimes (Childhood)
    PREMA_MADHURYA = 62  # Surrounded by Loving Devotees
    VENU_MADHURYA = 63  # The Flute (Attracts Universe)
    RUPA_MADHURYA = 64  # Unrivaled Beauty


# =============================================================================
# TATTVA LIMITS (The Hard Ceilings)
# =============================================================================


@dataclass(frozen=True)
class TattvaLimit:
    """
    The ontological ceiling for each category of being.

    A Jiva can NEVER exceed 50 qualities (78.125%).
    Any attempt to do so is the Hiranyakashipu Error.
    """

    level: str
    max_qualities: int
    percentage: Decimal

    def check_limit(self, quality: int) -> bool:
        """Returns True if quality is within this Tattva's limit."""
        return quality <= self.max_qualities


# The four categories (hard-coded immutable truth)
JIVA_LIMIT = TattvaLimit("JIVA", 50, Decimal("78.125"))
SHIVA_LIMIT = TattvaLimit("SHIVA", 55, Decimal("85.9375"))
VISHNU_LIMIT = TattvaLimit("VISHNU", 60, Decimal("93.75"))
KRISHNA_LIMIT = TattvaLimit("KRISHNA", 64, Decimal("100.0"))


# --- GAD-000 IDENTITY TYPES ---


@dataclass
class SovereignContext:
    """
    The 37th Principle: Identity Context for all operations.
    Passing this proves the operation is not 'Mayavad' (Illusion).
    """

    identity_id: str  # Who is acting? (Purusha)
    signature: str  # Cryptographic proof (Satyam)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    intent_id: Optional[str] = None  # Traceability to Sankalpa (Will)
    roles: List[str] = field(default_factory=list)  # Claims (e.g. ['admin', 'naga'])


# --- EXCEPTIONS (THE LAW) ---


class ProtocolError(Exception):
    """Base class for protocol violations."""

    pass


class KeyNotFoundError(ProtocolError):
    """The requested key does not exist in the field."""

    pass


class AccessDeniedError(ProtocolError):
    """The Sovereign lacks the Dharma (permission) for this action."""

    pass


# --- READ/WRITE TYPES ---


@dataclass
class ReadResult:
    """
    Envelope for read operations.
    Preserves the Chain of Custody (Provenance).
    """

    value: object
    timestamp: datetime = field(default_factory=datetime.now)
    writer: Optional["SovereignContext"] = None  # Who wrote this? (Provenance)
    metadata: Metadata = field(default_factory=dict)


# --- SYNC TYPES ---


@dataclass
class SyncResult:
    success: bool
    items_synced: int
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SyncStatus:
    is_synced: bool
    last_sync: Optional[datetime]
    pending_items: int
    details: Metadata = field(default_factory=dict)


# --- ENFORCE TYPES ---


class Verdict(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"
    AUDIT = "audit"


@dataclass
class EnforceContext:
    caller_id: str
    resource: str
    action: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Metadata = field(default_factory=dict)
    sovereign: Optional["SovereignContext"] = None  # The Identity claiming rights


@dataclass
class Rule:
    id: str
    pattern: str
    verdict: Verdict
    priority: int
    description: str = ""


# --- INFER TYPES ---


@dataclass
class InferenceInput:
    content: str
    context: Metadata = field(default_factory=dict)
    source: Optional[str] = None
    sovereign: Optional["SovereignContext"] = None


@dataclass
class Inference:
    conclusion: str
    confidence: float
    reasoning: List[str]
    metadata: Metadata = field(default_factory=dict)


@dataclass
class ClassifyInput:
    content: str
    categories: List[str]
    # Semantic context for classification
    context: Metadata = field(default_factory=dict)
    sovereign: Optional["SovereignContext"] = None


@dataclass
class Classification:
    category: str
    confidence: float
    alternatives: List[str]
    metadata: Metadata = field(default_factory=dict)


@dataclass
class Evaluation:
    valid: bool
    score: float
    violations: List[str]
    notes: List[str] = field(default_factory=list)


# --- MEMORY TYPES ---


@dataclass
class MemoryValue:
    content: str
    metadata: Metadata
    timestamp: datetime
    ttl: Optional[int] = None
    embedding: Optional[List[float]] = None


# --- MANTRA TYPES (THE 634 FIX) ---


@dataclass
class Resonance:
    """The 16-Bit Instruction Set Signal (Heartbeat)."""

    frequency: float  # The Japa frequency (Hz)
    amplitude: float  # Signal strength (Alignment)
    signature: str  # Sovereign Hash
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DriftContext:
    """Snapshot of Agentic Drift state."""

    drift_magnitude: float  # Error vector magnitude
    last_anchor_timestamp: float  # Last confirmed Sovereign interaction
    hallucination_index: float  # Mayavad likelihood (0.0 - 1.0)
    process_tree_depth: int  # Recursion depth (Samsara check)


@dataclass
class AlignmentScore:
    """The measure of alignment with Sovereign Will."""

    score: float  # 1.0 = Perfect Alignment, 0.0 = Mayavad
    status: str  # "ALIGNED", "DRIFTING", "LOST"
    corrections_applied: int


# NOTE: MantraInstruction has been moved to vibe_core.protocols.substrate.MantraOpCode
# This is Layer -1 (DNA). Import from there for the 16-Bit Instruction Set.
