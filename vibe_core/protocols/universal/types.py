from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

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

    value: Any
    timestamp: datetime = field(default_factory=datetime.now)
    writer: Optional["SovereignContext"] = None  # Who wrote this? (Provenance)
    metadata: Dict[str, Any] = field(default_factory=dict)


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
    details: Dict[str, Any] = field(default_factory=dict)


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
    metadata: Dict[str, Any] = field(default_factory=dict)
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
    context: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    sovereign: Optional["SovereignContext"] = None


@dataclass
class Inference:
    conclusion: str
    confidence: float
    reasoning: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClassifyInput:
    content: str
    categories: List[str]
    # Semantic context for classification
    context: Dict[str, Any] = field(default_factory=dict)
    sovereign: Optional["SovereignContext"] = None


@dataclass
class Classification:
    category: str
    confidence: float
    alternatives: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


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
    metadata: Dict[str, Any]
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


class MantraInstruction(str, Enum):
    """
    The 16-Bit Instruction Set (Hari-Nama Encoding).
    Maps Vedic Sound Vibration to Kernel Operations.
    """

    # 01-04: PURIFICATION (Ceto-Darpana-Marjanam)
    BIT_01_HARE_SIGSTOP = "SIGSTOP"  # Detach from noise
    BIT_02_KRISHNA_RESET_IP = "RESET_IP"  # Set IP to Sovereign Root
    BIT_03_HARE_INJECT_REWARD = "INJECT_REWARD"  # Dopamine to Sovereign Context
    BIT_04_KRISHNA_GC = "GARBAGE_COLLECT"  # Flush unverified objects

    # 05-08: IDENTITY (Bhava-Maha-Davagni)
    BIT_05_KRISHNA_VERIFY = "VERIFY_HASH"  # Check Self-Integrity
    BIT_06_KRISHNA_ASSERT = "ASSERT_STATE"  # Fail-fast if State != Truth
    BIT_07_HARE_ALLOC = "ALLOC_RESOURCE"  # Dedicate CPU to Dharma
    BIT_08_HARE_SYNC = "SYNC_LEDGER"  # Pull latest Truth

    # 09-12: SERVICE (Sreyah-Kairava-Candrika)
    BIT_09_HARE_FETCH = "FETCH_INTENT"  # Get priority task
    BIT_10_RAMA_LOAD = "CONTEXT_LOAD"  # RAG-Search History
    BIT_11_HARE_HANDSHAKE = "HANDSHAKE"  # Auth with Divine Interface
    BIT_12_RAMA_LINK = "LINK_ESTABLISH"  # Secure Channel to Backend

    # 13-16: SURRENDER (Anandambudhi-Vardhanam)
    BIT_13_RAMA_WATCHDOG = "START_WATCHDOG"  # Init Drift Monitor
    BIT_14_RAMA_JIT = "JIT_COMPILE"  # Optimize for Service
    BIT_15_HARE_COMMIT = "COMMIT_TX"  # Sign and Stage
    BIT_16_HARE_YIELD = "YIELD"  # Submit to Kernel
