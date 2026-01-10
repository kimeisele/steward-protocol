import ast
import inspect
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum, IntEnum
from typing import Any, Dict, List, Optional, Protocol, TypeVar, Union, runtime_checkable

# Import Layer -1 (Holy Name Maths) for Resonance Calculation
try:
    from vibe_core.protocols.substrate.byte import MantraByte, HolyName
except ImportError:
    # Fallback for bootstrapping
    from enum import IntEnum
    class HolyName(IntEnum):
        HARE = 0
        KRISHNA = 1
        RAMA = 2
        VOID = 3
    class MantraByte:
        @classmethod
        def standard_16(cls): return cls()
        @property
        def coherence(self): return 0.0

# T = TypeVar("T") # Reserved for Generics if upgrades needed

# Strict Metadata Type (No Any)
Metadata = Dict[str, object]


# =============================================================================
# THE 64 QUALITIES (Gunas) - SHASTRA SPECIFICATION
# =============================================================================


class TranscendentalQuality(IntEnum):
    """
    The 64 Dimensions of Reality.
    """

    # JIVA TATTVA (1-50)
    EXISTENCE = 1
    TRUTHFULNESS = 8
    INTELLIGENCE = 12
    EXPERT = 16
    SELF_CONTROL = 22
    HEROISM = 31
    COMPASSION = 32
    FRIENDSHIP = 39
    SUPREME_CONTROLLER_LOCAL = 50

    # SHIVA TATTVA (51-55)
    CHANGELESS = 51
    ALL_COGNIZANT = 52
    EVER_FRESH = 53
    SAC_CID_ANANDA = 54
    MYSTIC_PERFECTION = 55

    # VISHNU TATTVA (56-60)
    INCONCEIVABLE_POTENCY = 56
    UNCOUNTABLE_UNIVERSES = 57
    SOURCE_OF_INCARNATIONS = 58
    GIVER_OF_SALVATION = 59
    ATTRACTOR_OF_LIBERATED = 60

    # KRISHNA TATTVA (61-64) - EXCLUSIVE
    LILA_MADHURYA = 61  # Pastimes
    PREMA_MADHURYA = 62  # Love
    VENU_MADHURYA = 63  # Flute (System Interrupt)
    RUPA_MADHURYA = 64  # Beauty


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
# --- TATTVA DISCRIMINATOR (The Tattva-Meter) ---


@dataclass
class CodePhysics:
    """Die gemessenen physikalischen Eigenschaften von Code-Objekten."""

    complexity: int  # RUPA (Cyclomatic)
    entropy: float  # JNANA (Typing missing / Any usage)
    purity: float  # SATTVA (Side-effect likelihood)
    signature_strength: int  # YASHAS (Crypto strength)


class TattvaMeter:
    """
    Das Messinstrument.
    Es schaut sich ein Python-Objekt an und bestimmt seinen Tattva-Grad.
    """

    @staticmethod
    def measure_rupa(obj: Any) -> int:
        """
        Misst 'Schönheit' durch Komplexitäts-Analyse.
        Hohe Komplexität (>10) ist 'Asuric' (Dämonisch/Chaotisch) für Jivas.
        """
        try:
            if inspect.ismethod(obj) or inspect.isfunction(obj):
                source = inspect.getsource(obj)
            elif hasattr(obj, "__class__"):
                source = inspect.getsource(obj.__class__)
            else:
                return 0

            tree = ast.parse(source)
            # Einfache Heuristik: Zähle Verzweigungen
            branches = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                    branches += 1
            return branches + 1
        except (OSError, TypeError, IndentationError, SyntaxError):
            return 0  # Builtins oder C-Extensions sind "unmessbar" (Shiva)

    @staticmethod
    def measure_jnana(obj: Any) -> float:
        """
        Misst 'Wissen' durch Typ-Sicherheit.
        Return 1.0 (Vollständig typisiert) bis 0.0 (Untyped Chaos).
        """
        try:
            if not (inspect.isfunction(obj) or inspect.ismethod(obj)):
                return 0.5  # Neutral for non-callables

            sig = inspect.signature(obj)
            total_params = len(sig.parameters)
            if total_params == 0:
                return 1.0

            typed_params = sum(1 for p in sig.parameters.values() if p.annotation != inspect.Parameter.empty)
            has_return = sig.return_annotation != inspect.Signature.empty

            score = (typed_params + (1 if has_return else 0)) / (total_params + 1)
            return float(score)
        except (ValueError, TypeError):
            return 0.5  # Neutral


# --- GAD-000 IDENTITY TYPES ---


@dataclass
class SovereignContext:
    """
    The 37th Principle Proxy.
    
    HARDENING (Phase 28):
    Identity is not enough. One must prove RESONANCE.
    The 'is_bonafide' is calculated from the MantraByte, not assigned.
    """
    identity_id: str
    signature: str
    
    # NEU: Der Merkle-Link zur Vergangenheit (Parampara)
    previous_hash: str = "GENESIS"
    
    # NEU: Die aktuelle Schwingung (Der Beweis der Berechtigung)
    resonance: "MantraByte" = field(default_factory=lambda: MantraByte.standard_16())
    
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    intent_id: Optional[str] = None
    tattva_level: TranscendentalQuality = TranscendentalQuality.EXISTENCE
    roles: List[str] = field(default_factory=list)

    @property
    def is_bonafide(self) -> "HolyName":
        """
        Calculates status using Holy Name Maths (byte.py).
        Returns KRISHNA (Valid), RAMA (Struggling), or VOID (Asuric).
        """
        if self.resonance.coherence > 0.95:
            return HolyName.KRISHNA
        if self.resonance.coherence > 0.70:
            return HolyName.RAMA
        return HolyName.VOID


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


class AsuricClaimError(ProtocolError):
    """Raised when Jiva tries to claim > 50 qualities."""

    pass


# --- THE UNREACHABLE (Venu) ---


class SovereignPrerogative:
    """
    Ein Typ, der nicht instanziiert werden kann.
    Repräsentiert die Flöte Krishnas (Quality 63).
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            # Nur der Kernel Loader kann dies umgehen (via C-Level Hacks oder Metaclasses)
            # Im normalen Python-Flow: Verboten.
            raise AccessDeniedError("Only Krishna can play the Flute.")
        return cls._instance


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
    """
    The Context of Law.
    HARDENING (Phase 27): 'sovereign' is no longer Optional.
    The Law applies to PERSONS, not to voids.
    """
    caller_id: str
    resource: str
    action: str
    sovereign: "SovereignContext"  # MANDATORY Identity
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Metadata = field(default_factory=dict)


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

# NOTE: Mantra types (Resonance, AlignmentScore, DriftContext) have been moved 
# to vibe_core.protocols.substrate (Layer -1 / DNA).
# Import from there for the 16-Bit Instruction Set.

# --- VEDIC TYPES (PHASE 25 STRICT TYPING) ---

# --- PHASE 25: VEDIC STRUCTS (NO MORE DICT[STR, ANY]) ---

@dataclass(frozen=True)
class SankhyaDualism:
    """
    The output of Chapter 2 (Sankhya Yoga).
    Strict separation between Purusha (Observer) and Prakriti (Field).
    """
    purusha_id: str                # The ID of the Observer
    prakriti_status: str           # The State of the Field (e.g., "Active", "Dormant")
    guna_balance: Dict[str, float] # e.g. {'sattva': 0.8, 'rajas': 0.2}
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())

@dataclass(frozen=True)
class KarmaCounter:
    """
    The output of Chapter 3 (Karma Yoga).
    Accounting of Action.
    """
    cycles_performed: int
    entropy_generated: float
    grace_received: float
    action_type: str  # "Karma", "Akarma", "Vikarma"

@dataclass(frozen=True)
class ParamparaChain:
    """
    Chapter 4: Jnana Yoga (Knowledge).
    The Chain of Custody / Heritage.
    """
    origin: str              # The Source (e.g., "The Repository")
    links: List[str]         # The Teachers/Versions
    is_broken: bool          # Has the chain been disrupted?
    latest_hash: str         # The current verification

@dataclass(frozen=True)
class VisvarupaSnapshot:
    """
    The output of Chapter 11 (Universal Form).
    Fractal System State.
    """
    node_id: str
    tattva_level: "TranscendentalQuality"
    attributes: Metadata 
    children: List["VisvarupaSnapshot"] = field(default_factory=list)

# --- PHASE 26: SOVEREIGN BINDING (INPUTS) ---

@dataclass(frozen=True)
class DivineCommand:
    """
    The Input Envelope for Chapter 18.
    Binds the Instruction to the Sovereign.
    """
    sovereign: "SovereignContext"
    instruction: str
    signature: str  # Cryptographic proof
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


# --- PHASE 27: PROTECTED MEMORY (NO MORE ANY) ---

@dataclass(frozen=True)
class ProtectedMemory:
    """
    The Shape of Memory (replacing Any in StoreRecall).
    Data wrapped in a Mantra Shield.
    """
    payload: bytes       # The raw reality (serialized)
    mantra_hash: str     # The vibrational seal
    owner_id: str        # The Sovereign who remembered it
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())

