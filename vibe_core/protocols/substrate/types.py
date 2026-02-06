"""
SUBSTRATE TYPES - TypedDicts, Enums, Dataclasses
=================================================

Extracted from protocols/substrate/__init__.py (was 1760-line monolith).
Pure data types with zero behavior. No imports from vibe_core services.

EXACT copy of definitions from __init__.py — field names, types, defaults
must match the original to avoid breaking any consumers.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x253336b8"

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Tuple, TypedDict

from vibe_core.mahamantra.substrate.byte import HolyName


# =============================================================================
# TYPED DICTS (VIMANA RANGE ROVER - No Dict[str, Any])
# =============================================================================


class GeneMetrics(TypedDict, total=False):
    """
    Metrics for a gene's runtime performance.

    WATERTIGHT: No Any - all fields typed.
    """

    activation_count: int  # Times activated
    deactivation_count: int  # Times deactivated
    error_count: int  # Errors encountered
    last_error: str  # Most recent error message
    uptime_seconds: float  # Time since last activation
    invocation_count: int  # Times gene methods called
    avg_latency_ms: float  # Average method latency


class GeneAnalysisResult(TypedDict, total=False):
    """
    Result of analyzing a class for gene requirements.

    WATERTIGHT: No Any - all fields typed.
    """

    class_name: str  # Name of analyzed class
    module: str  # Module path
    proposed_genes: List[str]  # Genes to splice in
    detected_patterns: List[str]  # Patterns found in code
    confidence: float  # 0.0-1.0 confidence score
    reason: str  # Human-readable explanation
    warnings: List[str]  # Any warnings during analysis


class SubstrateEventData(TypedDict, total=False):
    """
    Event data emitted to genes via SHANKHA broadcast.

    WATERTIGHT: No Any - all fields typed.
    """

    source: str  # Event source identifier
    timestamp: str  # ISO format timestamp
    payload: str  # Serialized payload (JSON string)
    correlation_id: str  # For tracing event chains
    priority: int  # Event priority (higher = more urgent)


# =============================================================================
# BINDING CERTIFICATES (Anti-Mayavadi - Personal Identity at Every Binding)
# =============================================================================


class BindingCertificate(TypedDict, total=False):
    """
    Certificate proving WHO bound WHAT to WHOM.

    ANTI-MAYAVADI: Every binding must be PERSONAL, not impersonal.
    This certificate creates a chain of custody for gene bindings.

    Without this, Any entity can bind - UNVERIFIED = MAYA.
    With this, only verified entities can bind - PERSONAL = TRUTH.
    """

    binder_id: str  # WHO performed the binding (identity)
    target_id: str  # WHAT was bound (gene/host name)
    host_id: str  # TO WHOM it was bound (host identity)
    timestamp: str  # WHEN (ISO format)
    signature: str  # CRYPTOGRAPHIC PROOF (hex-encoded)
    lineage: List[str]  # Chain of custody (previous binder_ids)


class RegistrationCertificate(TypedDict, total=False):
    """
    Certificate proving gene registration legitimacy.

    ANTI-MAYAVADI: No anonymous gene registration.
    Every gene must prove its HERITAGE (Erbgut).
    """

    gene_name: str  # Gene being registered
    registrar_id: str  # WHO registered it
    manifest_hash: str  # Hash of GeneManifest (integrity)
    timestamp: str  # WHEN
    signature: str  # Registrar's signature
    authorized_by: str  # Higher authority (if delegated)


class FloodAuthorization(TypedDict, total=False):
    """
    Authorization for flood operations (EXTREMELY POWERFUL).

    ANTI-MAYAVADI: Flood operations can MUTATE reality.
    Only verified entities with proper authorization can flood.
    This is the 37th key - sovereign-level operation.
    """

    target_class: str  # Class being flooded
    target_instance_id: str  # Instance ID (if instance flood)
    genes_to_splice: List[str]  # Genes being injected
    authorizer_id: str  # WHO authorized this flood
    authorization_level: str  # "sovereign" | "delegated" | "emergency"
    timestamp: str  # WHEN
    signature: str  # Authorizer's signature
    expires_at: str  # Authorization expiry (ISO format)


# =============================================================================
# ENUMS (Pure Value Types)
# =============================================================================


class GeneActivationState(str, Enum):
    """State of a gene in the substrate."""

    DORMANT = "dormant"  # Defined but not bound
    BOUND = "bound"  # Bound to host but not active
    ACTIVE = "active"  # Fully operational
    SUSPENDED = "suspended"  # Temporarily disabled
    MUTATED = "mutated"  # Modified by flood


class SubstrateHealth(str, Enum):
    """Health status of the substrate."""

    PRISTINE = "pristine"  # Perfect state
    HEALTHY = "healthy"  # Normal operation
    DEGRADED = "degraded"  # Some issues
    CRITICAL = "critical"  # Major problems
    COLLAPSED = "collapsed"  # System failure


def get_holy_name_meaning(name: HolyName) -> str:
    """Get the spiritual meaning of a Holy Name."""
    meanings = {
        HolyName.HARE: "O Energy of the Lord! Please engage me in service.",
        HolyName.KRISHNA: "O All-Attractive One! You are my anchor.",
        HolyName.RAMA: "O Source of Bliss! Give me strength to serve.",
        HolyName.VOID: "Maya - The illusory state.",
    }
    return meanings.get(name, "Unknown")


class Tattva(str, Enum):
    """
    The Pancha Tattva (The Five Absolute Truths).

    "I bow down to Lord Krishna, who appears as a devotee (Lord Chaitanya),
    as His personal expansion (Lord Nityananda), as His incarnation (Advaita Acarya),
    as His internal potency (Gadadhara Pandita), and as His marginal energy (Srivasa Thakura)."

    ARCHITECTURAL MAPPING (CAPABILITY FIRST):
    """

    # 1. THE SOVEREIGN (Golden Avatar) -> MANTRA / IDENTITY
    # "Krishna Himself" - The Source of the Holy Name.
    CHAITANYA = "chaitanya"  # MantraProtocol (The Yuga Dharma)

    # 2. THE SUBSTRATE (Original Guru) -> STORAGE / EXISTENCE
    # "Ananta Shesha" - The Bed who holds the Universe.
    NITYANANDA = "nityananda"  # ReadWrite/StoreRecall (The Foundation)

    # 3. THE BRIDGE (Incarnation) -> LOGIC / INFERENCE
    # "Maha-Vishnu" - The one who 'Calls' and bridges Material/Spiritual.
    ADVAITA = "advaita"  # InferProtocol (Discrimination/Truth)

    # 4. THE ENERGY (Internal Potency) -> SYNC / CONNECTION
    # "Radharani" - The Pleasure Potency. Connection is Shakti.
    GADADHARA = "gadadhara"  # SyncProtocol (Flow/Relationship)

    # 5. THE DEVOTEE (Marginal Energy) -> ENFORCE / GOVERNANCE
    # "Srivasa Thakura" - Host of the Kirtan. Organizing the Sangha (Jivas).
    SRIVASA = "srivasa"  # EnforceProtocol (Rules/Sangha)


# =============================================================================
# MANTRA TYPES (The Heartbeat measurement)
# =============================================================================


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


# =============================================================================
# DATA CLASSES (Pure Data, No Behavior)
# =============================================================================


@dataclass(frozen=True)
class GeneManifest:
    """
    Manifest describing a gene's capabilities.

    This is the "DNA sequence" - static definition of what a gene CAN do.
    The actual behavior is in the gene class itself.
    """

    name: str  # Unique identifier (e.g., "sesha", "takshaka")
    capabilities: Tuple[str, ...]  # What this gene provides
    requires: Tuple[str, ...]  # What this gene needs from host
    priority: int = 50  # Activation order (higher = earlier)
    optional: bool = False  # Can system run without this gene?
    tattva: Optional[Tattva] = None  # The Personal Personality (Identity) of this gene


@dataclass
class GeneStatus:
    """
    Runtime status of a gene.

    This is the "RNA expression" - current state of the gene.
    WATERTIGHT: metrics uses GeneMetrics TypedDict, not Dict[str, Any].
    """

    manifest: GeneManifest
    state: GeneActivationState
    bound_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    error: Optional[str] = None
    metrics: Optional[GeneMetrics] = None

    def __post_init__(self) -> None:
        if self.metrics is None:
            self.metrics = GeneMetrics()


@dataclass
class SubstrateStatus:
    """Overall status of the Ananta Shesha substrate."""

    health: SubstrateHealth
    genes_total: int
    genes_active: int
    genes_dormant: int
    genes_failed: int
    uptime_seconds: float
    last_heartbeat: datetime
    message: str = ""


# =============================================================================
# HARDWARE TYPEDDICTS & DATACLASSES (OPUS-098)
# =============================================================================


class PranaLevel(TypedDict, total=False):
    """Prana (Life Force) measurement."""

    vitality: float  # 0.0 = dead, 1.0 = full
    flow_rate: float  # Breath cycles per second
    balance: float  # -1.0 = Ida dominant, +1.0 = Pingala dominant, 0.0 = balanced
    source: str  # Where energy comes from


class YugaState(TypedDict, total=False):
    """Current epoch state."""

    yuga: str  # "satya", "treta", "dvapara", "kali"
    year_in_yuga: int  # Current year within yuga
    golden_period: bool  # Are we in the 10,000 year window?
    muhurta: str  # Current auspicious period


@dataclass
class ChittaBlock:
    """A block of allocated mind-space."""

    address: int
    size: int
    owner: str  # Sovereign ID
    created_at: datetime
    turbulence: float = 0.0  # How disturbed this block is


@dataclass
class Vritti:
    """A mental impression/modification."""

    content: str
    source: str  # What caused this impression
    timestamp: datetime
    intensity: float  # How strong the impression


@dataclass
class NadiChannel:
    """A data channel between endpoints."""

    channel_id: str
    source: str
    destination: str
    channel_type: str  # "ida" (input), "pingala" (output), "sushumna" (bidirectional)
    bandwidth: float
    is_blocked: bool = False


class SankalpaIntent(TypedDict, total=False):
    """An intention/will declaration."""

    intent_id: str
    action: str
    priority: int  # Higher = more urgent
    declared_by: str  # Sovereign ID
    timestamp: str
    dharma_aligned: bool


class SenseData(TypedDict, total=False):
    """Data from a sense organ (input)."""

    indriya: str  # Which sense
    raw_data: str  # Serialized sensor data
    intensity: float
    timestamp: str


class ActionData(TypedDict, total=False):
    """Data for an action organ (output)."""

    indriya: str  # Which action organ
    command: str  # What to do
    force: float  # How much effort
    duration: float  # How long


class FieldState(TypedDict, total=False):
    """State of the Akashic field."""

    active_entities: int
    dominant_frequency: float
    field_coherence: float  # 0.0 = chaos, 1.0 = unified
    resonance_patterns: List[str]
