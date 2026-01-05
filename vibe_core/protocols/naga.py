"""
NAGA Protocols - The Invisible Guardians
=========================================

PROMPT.md Level 2: Die NAGAs (Das Nervensystem)

Die NAGAs sind KEINE parallele Sicherheitsschicht.
Sie sind MIDDLEWARE die sich in das existierende System einklinkt.
"Niemand darf es merken" - die anderen wissen nicht dass wir da sind.

Integration Points:
- Register as CorrectionHandlers in CorrectionDispatcher
- Use existing DriftSource enum (STATE, CONFIG, COGNITIVE)
- Return HealingResult (unified format)
- Record in Knowledge Graph

NAGA-Specific Capabilities (beyond healing):
- Sesha: Gossip sync, ledger operations, truth persistence
- Vasuki: Serialization, network boundary, protocol translation
- Takshaka: Signature verification, ingress protection, toxicity

PROMPT.md References:
- "Sesha: Truth is purely additive"
- "Vasuki: Memory is not Network"
- "Takshaka: Bite first, ask later"
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    runtime_checkable,
)

if TYPE_CHECKING:
    from vibe_core.naga.identity import NagaIdentity

from vibe_core.protocols.correction import (
    CorrectionHandler,
    HealingResult,
    HealingStatus,
    UnifiedDriftReport,
)

# =============================================================================
# NAGA Shared Types
# =============================================================================


class NagaType(str, Enum):
    """
    The NAGA Service Agency (NSA) - 7 Members.

    WICHTIG: "NAGA Service Agency" ist der NAME des Dienstes, nicht die RASSE.
    4 echte Nagas (🐍 Schlangen-Rasse) + 3 Personnel (andere Wesen).

    Mythological Hierarchy (Srimad Bhagavatam Canto 7):
    - Vishnu (Intent) → Narada (Messenger) → Prahlad (Governor)
    - Prahlad herrscht über die Nagas (post-Hiranyakashipu)
    """

    # ===== INFRASTRUCTURE LAYER - Echte Nagas (🐍 Schlangen-Rasse) =====

    # Original 3 (PROMPT.md Level 2)
    SESHA = "sesha"  # 🐍 Ananta Shesha - Vishnus Bett, trägt die Welten
    VASUKI = "vasuki"  # 🐍 Samudra Manthan Seil - Transformation
    TAKSHAKA = "takshaka"  # 🐍 König der Nagas - beißt erst, fragt später

    # Phase 9 Addition
    KALIYA = "kaliya"  # 🐍 Von Krishna bezwungen - Isolation, nicht Tod

    # ===== GOVERNANCE LAYER - Personnel (KEINE Nagas von Rasse) =====

    # Phase 9 Additions
    NARADA = "narada"  # 🎵 Deva-Rishi - Messenger zwischen Welten
    CHITRAGUPTA = "chitragupta"  # 📜 Yamas Assistent - himmlischer Buchhalter

    # Phase 10: Governor
    PRAHLAD = "prahlad"  # 👑 Daitya-Prinz - herrscht über die Nagas

    @property
    def is_infrastructure(self) -> bool:
        """True if this is a real Naga (serpent race) - infrastructure layer."""
        return self in (NagaType.SESHA, NagaType.VASUKI, NagaType.TAKSHAKA, NagaType.KALIYA)

    @property
    def is_governance(self) -> bool:
        """True if this is personnel (not a Naga by race) - governance layer."""
        return self in (NagaType.NARADA, NagaType.CHITRAGUPTA, NagaType.PRAHLAD)

    @property
    def symbol(self) -> str:
        """Get the appropriate emoji for this member."""
        if self == NagaType.PRAHLAD:
            return "👑"
        elif self == NagaType.NARADA:
            return "🎵"
        elif self == NagaType.CHITRAGUPTA:
            return "📜"
        else:
            return "🐍"

    @classmethod
    def infrastructure_members(cls) -> list["NagaType"]:
        """Get all infrastructure layer members (real Nagas)."""
        return [cls.SESHA, cls.VASUKI, cls.TAKSHAKA, cls.KALIYA]

    @classmethod
    def governance_members(cls) -> list["NagaType"]:
        """Get all governance layer members (personnel)."""
        return [cls.NARADA, cls.CHITRAGUPTA, cls.PRAHLAD]


@dataclass
class NagaStatus:
    """Status of a NAGA service."""

    naga_type: NagaType
    healthy: bool = True
    last_heartbeat: Optional[datetime] = None
    events_processed: int = 0
    errors: int = 0
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.naga_type.value,
            "healthy": self.healthy,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "events_processed": self.events_processed,
            "errors": self.errors,
            "message": self.message,
            "details": self.details,
        }


# =============================================================================
# SESHA - Der Träger der Welten (Data/Ledger/Gossip)
# =============================================================================


class SyncStatus(str, Enum):
    """Status of a gossip sync operation."""

    SYNCHRONIZED = "synchronized"  # Hashes match
    NEED_SYNC = "need_sync"  # Missing blocks
    CONFLICT = "conflict"  # Divergent chains
    ERROR = "error"  # Sync failed


@dataclass
class LedgerBlock:
    """A chunk of ledger events for gossip sync."""

    sequence: int
    events: List[Dict[str, Any]]
    hash: str
    prev_hash: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sequence": self.sequence,
            "events": self.events,
            "hash": self.hash,
            "prev_hash": self.prev_hash,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class SyncRequest:
    """Request for gossip sync between nodes."""

    my_hash: str
    my_sequence: int
    peer_hash: Optional[str] = None
    status: SyncStatus = SyncStatus.NEED_SYNC


@dataclass
class ImportResult:
    """Result of importing blocks from another node."""

    success: bool
    blocks_imported: int = 0
    final_sequence: int = 0
    final_hash: str = ""
    message: str = ""
    conflicts: List[str] = field(default_factory=list)


@runtime_checkable
class SeshaProtocol(Protocol):
    """
    Ananta Sesha - Die unendliche Schlange, Träger der Wahrheit.

    PROMPT.md: "Truth is purely additive."

    Responsibilities:
    - Wrap existing SQLiteLedger for gossip sync
    - Export/Import blocks for federation
    - Maintain hash chain integrity
    - NO complex consensus (Keep Sesha dumb)

    Integration:
    - Registers as handler for DriftSource.STATE
    - Detects state drift via hash comparison
    - Heals by syncing missing blocks

    Usage:
        sesha = ServiceRegistry.get(SeshaProtocol)
        blocks = sesha.export_blocks(since=100)
        result = peer.sesha.import_blocks(blocks)
    """

    # === Ledger Wrapper ===

    def get_top_hash(self) -> str:
        """Get the hash of the latest ledger block."""
        ...

    def get_sequence(self) -> int:
        """Get the current sequence number."""
        ...

    def get_events_since(self, sequence: int) -> List[Dict[str, Any]]:
        """Get all events since a sequence number."""
        ...

    # === Gossip Sync ===

    def export_blocks(self, since: int = 0, limit: int = 100) -> List[LedgerBlock]:
        """
        Export blocks for gossip to peers.

        Args:
            since: Start sequence (0 = from beginning)
            limit: Max blocks to export

        Returns:
            List of LedgerBlocks for transfer
        """
        ...

    def import_blocks(self, blocks: List[LedgerBlock]) -> ImportResult:
        """
        Import blocks received from a peer.

        Validates hash chain before accepting.

        Args:
            blocks: Blocks to import

        Returns:
            ImportResult with success/failure details
        """
        ...

    def request_sync(self, peer_hash: str, peer_sequence: int) -> SyncRequest:
        """
        Initiate sync with a peer.

        Compares hashes to determine if sync needed.

        Args:
            peer_hash: The peer's top hash
            peer_sequence: The peer's sequence number

        Returns:
            SyncRequest indicating action needed
        """
        ...

    # === CorrectionHandler Interface ===

    def as_handler(self) -> CorrectionHandler:
        """
        Get this NAGA as a CorrectionHandler.

        Register with:
            dispatcher.register_handler(
                DriftSource.STATE,
                sesha.as_handler(),
                handler_id="sesha",
                priority=50
            )
        """
        ...

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        ...


# =============================================================================
# VASUKI - Der Transformator (Network/Serialization)
# =============================================================================


@dataclass
class SignedEnvelope:
    """
    A signed, serialized payload ready for network transfer.

    Vasuki produces these when "churning out" (serializing).
    Vasuki consumes these when "churning in" (deserializing).
    """

    payload: bytes  # MsgPack/Protobuf serialized
    signature: bytes  # ECDSA signature
    sender_key: str  # PEM public key
    timestamp: float  # Unix timestamp
    content_type: str = "msgpack"  # Serialization format

    def to_bytes(self) -> bytes:
        """Serialize the entire envelope for wire transfer."""
        import msgpack

        return msgpack.packb(
            {
                "payload": self.payload,
                "signature": self.signature,
                "sender_key": self.sender_key,
                "timestamp": self.timestamp,
                "content_type": self.content_type,
            }
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "SignedEnvelope":
        """Deserialize from wire format."""
        import msgpack

        d = msgpack.unpackb(data)
        return cls(
            payload=d["payload"],
            signature=d["signature"],
            sender_key=d["sender_key"],
            timestamp=d["timestamp"],
            content_type=d.get("content_type", "msgpack"),
        )


class SendStatus(str, Enum):
    """Result of sending via Vasuki."""

    SENT = "sent"
    QUEUED = "queued"
    FAILED = "failed"
    BLOCKED = "blocked"  # Takshaka rejected


@dataclass
class SendResult:
    """Result of a Vasuki send operation."""

    status: SendStatus
    envelope_hash: str = ""
    message: str = ""
    retry_after: Optional[float] = None


@dataclass
class NodeAddress:
    """Address of a peer node."""

    host: str
    port: int
    public_key: Optional[str] = None
    node_id: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.host}:{self.port}"


@runtime_checkable
class VasukiProtocol(Protocol):
    """
    Vasuki - König der Schlangen, Grenze zwischen Welten.

    PROMPT.md: "Memory is not Network."

    Responsibilities:
    - Serialize events for network (churn_out)
    - Deserialize events from network (churn_in)
    - Sign before sending
    - Validate schema on receive
    - Maintain internal/external boundary

    Integration:
    - Registers as handler for DriftSource.CONFIG
    - Detects config drift between nodes
    - Heals by propagating correct config

    Usage:
        vasuki = ServiceRegistry.get(VasukiProtocol)
        envelope = vasuki.churn_out(event)
        result = vasuki.send(peer_address, envelope)
    """

    # === Serialization (Das Quirlen) ===

    def churn_out(self, event: Dict[str, Any]) -> SignedEnvelope:
        """
        Transform internal event → signed wire-ready envelope.

        The "churning" metaphor from Samudra Manthan:
        Raw Python dict becomes transportable nectar.

        Args:
            event: Internal event dict

        Returns:
            SignedEnvelope ready for network
        """
        ...

    def churn_in(self, envelope: SignedEnvelope) -> Dict[str, Any]:
        """
        Transform wire envelope → internal event.

        NOTE: Takshaka must verify BEFORE calling this!
        This method trusts the envelope is authentic.

        Args:
            envelope: Verified SignedEnvelope

        Returns:
            Internal event dict
        """
        ...

    # === Network Operations ===

    async def send(self, target: NodeAddress, envelope: SignedEnvelope) -> SendResult:
        """
        Send envelope to a peer node.

        Args:
            target: Destination node
            envelope: Signed payload

        Returns:
            SendResult with status
        """
        ...

    async def receive(self) -> AsyncIterator[SignedEnvelope]:
        """
        Receive envelopes from the network.

        Yields:
            SignedEnvelopes as they arrive
        """
        ...

    # === Boundary Enforcement ===

    def is_internal(self, event: Dict[str, Any]) -> bool:
        """Check if event should stay internal (not sent to network)."""
        ...

    def get_peers(self) -> List[NodeAddress]:
        """Get known peer nodes."""
        ...

    # === CorrectionHandler Interface ===

    def as_handler(self) -> CorrectionHandler:
        """Get this NAGA as a CorrectionHandler for DriftSource.CONFIG."""
        ...

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        ...


# =============================================================================
# TAKSHAKA - Der Krieger (Security/Ingress)
# =============================================================================


class VerifyStatus(str, Enum):
    """Result of Takshaka verification."""

    VALID = "valid"
    INVALID_SIGNATURE = "invalid_signature"
    INVALID_KEY = "invalid_key"
    EXPIRED = "expired"
    UNTRUSTED = "untrusted"
    REVOKED = "revoked"
    RATE_LIMITED = "rate_limited"
    TOXIC = "toxic"


@dataclass
class VerifyResult:
    """Result of Takshaka security verification."""

    status: VerifyStatus
    sender_id: Optional[str] = None
    fingerprint: Optional[str] = None
    reason: Optional[str] = None
    toxic_patterns: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())

    @property
    def is_valid(self) -> bool:
        return self.status == VerifyStatus.VALID

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "sender_id": self.sender_id,
            "fingerprint": self.fingerprint,
            "reason": self.reason,
            "toxic_patterns": self.toxic_patterns,
            "timestamp": self.timestamp,
        }


@dataclass
class ToxicityReport:
    """Report from toxicity scanning."""

    score: float  # 0.0 (clean) to 1.0 (maximum toxicity)
    patterns: List[str]  # Matched patterns
    blocked: bool = False  # True if score >= threshold

    @property
    def is_toxic(self) -> bool:
        return self.score >= 0.3


@dataclass
class VajraViolation:
    """Record of a security violation (for ledger)."""

    violation_type: str  # NO_SIGNATURE, INVALID_SIGNATURE, TOXIC, etc.
    source: str  # IP, agent_id, etc.
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    raw_sample: Optional[bytes] = None  # First N bytes for forensics

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.violation_type,
            "source": self.source,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


@runtime_checkable
class TakshakaProtocol(Protocol):
    """
    Takshaka - Der Beißer. Keine Gnade.

    PROMPT.md: "Bite first, ask later."

    Responsibilities:
    - Verify signature BEFORE payload parsing
    - Detect toxicity (prompt injection, SQL injection, etc.)
    - Rate limiting per sender
    - Record violations in ledger (VajraViolation)

    Integration:
    - Registers as handler for DriftSource.COGNITIVE
    - Detects cognitive threats (attacks, anomalies)
    - "Heals" by blocking and recording

    Usage:
        takshaka = ServiceRegistry.get(TakshakaProtocol)
        result = takshaka.verify_envelope(raw_bytes)
        if not result.is_valid:
            takshaka.bite(VajraViolation(...))
    """

    # === Pre-Parse Security (Bite First) ===

    def verify_envelope(self, raw: bytes) -> VerifyResult:
        """
        Verify signature BEFORE any parsing.

        PROMPT.md: "Ein Paket ohne valide kryptografische Signatur
        wird verworfen, BEVOR der Payload deserialisiert wird"

        Args:
            raw: Raw bytes from network

        Returns:
            VerifyResult (caller should NOT proceed if invalid)
        """
        ...

    def extract_signature(self, raw: bytes) -> Optional[bytes]:
        """
        Extract signature from raw bytes without parsing payload.

        Used for fast rejection of unsigned packets.
        """
        ...

    # === Toxicity Detection (Kaliya Filter) ===

    def scan_toxicity(self, content: str) -> ToxicityReport:
        """
        Scan content for toxic patterns.

        Named after the serpent Krishna subdued.

        Args:
            content: Text to scan

        Returns:
            ToxicityReport with score and patterns
        """
        ...

    def is_prompt_injection(self, text: str) -> bool:
        """Quick check for prompt injection patterns."""
        ...

    # === Rate Limiting ===

    def check_rate_limit(self, sender_id: str) -> Tuple[bool, Optional[float]]:
        """
        Check if sender is within rate limits.

        Returns:
            (allowed, retry_after_seconds)
        """
        ...

    # === Bite (Record Attack) ===

    def bite(self, violation: VajraViolation) -> str:
        """
        Record a security violation in the ledger.

        "Bite first, ask later."

        Args:
            violation: The violation to record

        Returns:
            Ledger event_id
        """
        ...

    # === Trust Management ===

    def is_key_trusted(self, public_key: str) -> bool:
        """Check if a public key is in the trusted keyring."""
        ...

    def revoke_key(self, fingerprint: str, reason: str) -> bool:
        """Revoke a key (add to blacklist)."""
        ...

    # === CorrectionHandler Interface ===

    def as_handler(self) -> CorrectionHandler:
        """Get this NAGA as a CorrectionHandler for DriftSource.COGNITIVE."""
        ...

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        ...


# =============================================================================
# KALIYA - Die Quarantäne (Isolation Protocol)
# =============================================================================


@dataclass
class QuarantineStatus:
    """Status of a quarantine operation."""

    component_id: str
    is_quarantined: bool
    duration_seconds: float = 0.0
    violation_count: int = 0
    is_escalated: bool = False
    signed_by: Optional[str] = None


@runtime_checkable
class KaliyaProtocol(Protocol):
    """
    Kaliya - Die Quarantäne. Von Krishna gebändigt, nicht getötet.

    PROMPT.md: Isolation without destruction.

    Responsibilities:
    - Isolate misbehaving components WITHOUT killing them
    - Track violations per component
    - Auto-quarantine on threshold
    - Escalate to sovereign (37th) after repeated quarantines

    Integration:
    - Registers as handler for DriftSource.RELIABILITY
    - Detects reliability drift (component misbehavior)
    - Heals by isolating unreliable components

    Usage:
        kaliya = ServiceRegistry.get(KaliyaProtocol)
        kaliya.quarantine(component_id, reason)
        if kaliya.is_quarantined(component_id):
            # Component is isolated
    """

    def quarantine(
        self,
        component_id: str,
        reason: str,
        duration_seconds: Optional[float] = None,
    ) -> QuarantineStatus:
        """Put a component in quarantine."""
        ...

    def is_quarantined(self, component_id: str) -> bool:
        """Check if component is currently quarantined."""
        ...

    def release(self, component_id: str) -> None:
        """Release component from quarantine (fails if escalated)."""
        ...

    def record_violation(self, component_id: str) -> None:
        """Record a violation, may trigger auto-quarantine."""
        ...

    def get_violation_count(self, component_id: str) -> int:
        """Get current violation count for component."""
        ...

    def is_escalated(self, component_id: str) -> bool:
        """Check if component has been escalated to sovereign."""
        ...

    def as_handler(self) -> CorrectionHandler:
        """Get this NAGA as a CorrectionHandler for DriftSource.RELIABILITY."""
        ...

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        ...


# =============================================================================
# NARADA - Der Spion (Observer Protocol)
# =============================================================================


@runtime_checkable
class NaradaProtocol(Protocol):
    """
    Narada - Der kosmische Journalist. Reist überall, weiß alles.

    "Narada Muni ki Jai!" - The Messenger of the Gods.

    Responsibilities:
    - Intercept function calls via @spy decorator
    - Observe without modifying (pure observation)
    - Report to Cortex for pattern analysis
    - Sign all observations (37th Principle)

    Integration:
    - Does NOT register as CorrectionHandler (pure observer)
    - Reports patterns to other NAGAs
    - Enables proactive drift detection

    Usage:
        narada = ServiceRegistry.get(NaradaProtocol)
        @narada.spy
        def my_function(x, y):
            return x + y
    """

    def spy(self, func: Any) -> Any:
        """Decorator to observe function calls."""
        ...

    def export_observations(self) -> List[Dict[str, Any]]:
        """Export and clear observation buffer."""
        ...

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        ...


# =============================================================================
# CHITRAGUPTA - Der Profiler (Behavioral Protocol)
# =============================================================================


@dataclass
class AnomalyReport:
    """Report of a behavioral anomaly."""

    component_id: str
    metric: str
    current_value: float
    expected_min: float
    expected_max: float
    deviation_sigma: float
    signed_by: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@runtime_checkable
class ChitraguptaProtocol(Protocol):
    """
    Chitragupta - Der Karma-Buchhalter. Führt Buch über alle Taten.

    "Er entscheidet mit Yama über Himmel oder Hölle."

    Responsibilities:
    - Profile component behavior over time
    - Calculate baselines (mean, stddev)
    - Detect anomalies (deviation from baseline)
    - Sign anomaly reports (37th Principle)

    Integration:
    - Registers as handler for DriftSource.PERFORMANCE
    - Detects performance drift via behavioral analysis
    - Heals by flagging anomalous components

    Usage:
        chitragupta = ServiceRegistry.get(ChitraguptaProtocol)
        chitragupta.record(component_id, "latency_ms", 45.2)
        anomaly = chitragupta.detect_anomaly(component_id)
    """

    def record(self, component_id: str, metric: str, value: float) -> None:
        """Record a metric value for a component."""
        ...

    def detect_anomaly(self, component_id: str) -> Optional[AnomalyReport]:
        """Check if component is behaving anomalously."""
        ...

    def get_baseline_mean(self, component_id: str, metric: str) -> float:
        """Get baseline mean for a metric."""
        ...

    def get_baseline_stddev(self, component_id: str, metric: str) -> float:
        """Get baseline standard deviation for a metric."""
        ...

    def as_handler(self) -> CorrectionHandler:
        """Get this NAGA as a CorrectionHandler for DriftSource.PERFORMANCE."""
        ...

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        ...


# =============================================================================
# PRAHLAD - Der Resilience Agent (Antifragility Protocol)
# =============================================================================


@dataclass
class DharmaScore:
    """Result of a Dharma (integrity) audit."""

    total_score: float  # 0-100
    signature_compliance: float  # % of signed decisions
    ledger_intact: bool
    identity_coverage: float  # % of agents with identity
    auditor_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@runtime_checkable
class PrahladProtocol(Protocol):
    """
    Prahlad Maharaj - Der unzerstörbare Devotee.

    "Was mich nicht tötet, macht mich stärker."
    Vedisch: "Weil ich in Wahrheit verankert bin, kann mich nichts töten."

    Responsibilities:
    - Error → Regression Test (learn from suffering)
    - Chaos Probing (actively seek weakness)
    - Dharma Audit (verify integrity)
    - Phoenix Guarantee (crash-restart-resume)

    Integration:
    - Registers as handler for DriftSource.STRUCTURAL
    - Detects structural drift (integrity violations)
    - Heals by generating hardening tests

    Usage:
        prahlad = ServiceRegistry.get(PrahladProtocol)
        test = prahlad.on_error(error_event)
        score = prahlad.dharma_audit()
    """

    def on_error(self, error_type: str, message: str, component_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Learn from an error by generating a regression test."""
        ...

    def chaos_probe(self, target: str) -> Dict[str, Any]:
        """Actively probe a component for weaknesses."""
        ...

    def dharma_audit(self) -> DharmaScore:
        """Audit the system for Dharma (integrity) compliance."""
        ...

    def verify_phoenix_guarantee(self, target: str) -> bool:
        """Verify crash-restart-resume for a component."""
        ...

    def export_hardening_suite(self) -> List[Dict[str, Any]]:
        """Export the hardening test suite."""
        ...

    def as_handler(self) -> CorrectionHandler:
        """Get this NAGA as a CorrectionHandler for DriftSource.STRUCTURAL."""
        ...

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        ...


# =============================================================================
# NAGA Federation - The Three Working Together
# =============================================================================


@runtime_checkable
class NagaFederationProtocol(Protocol):
    """
    The three NAGAs working together.

    Data Flow:
        External → Takshaka (verify) → Vasuki (deserialize) → Sesha (record)
        Sesha (read) → Vasuki (serialize) → Takshaka (sign) → External

    This is the unified interface for the NAGA layer.
    """

    @property
    def sesha(self) -> SeshaProtocol:
        """Access Sesha (Data/Ledger)."""
        ...

    @property
    def vasuki(self) -> VasukiProtocol:
        """Access Vasuki (Network/Serialization)."""
        ...

    @property
    def takshaka(self) -> TakshakaProtocol:
        """Access Takshaka (Security)."""
        ...

    def receive_external(self, raw: bytes, source: str) -> Optional[Dict[str, Any]]:
        """
        Process incoming external data through the full NAGA pipeline.

        Flow: Takshaka (verify) → Vasuki (deserialize) → Sesha (record)

        Args:
            raw: Raw bytes from network
            source: Source identifier (IP, node_id, etc.)

        Returns:
            Deserialized event if valid, None if rejected
        """
        ...

    def send_external(self, event: Dict[str, Any], target: NodeAddress) -> SendResult:
        """
        Send event to external node through the full NAGA pipeline.

        Flow: Sesha (record) → Vasuki (serialize) → Takshaka (sign) → send

        Args:
            event: Event to send
            target: Destination node

        Returns:
            SendResult
        """
        ...

    def sync_with_peer(self, peer: NodeAddress) -> ImportResult:
        """
        Synchronize ledger with a peer node.

        Uses Sesha's gossip protocol with Vasuki for transport
        and Takshaka for verification.
        """
        ...

    def get_status(self) -> Dict[NagaType, NagaStatus]:
        """Get status of all three NAGAs."""
        ...


# =============================================================================
# NAGA CORTEX - Das Nervensystem (Signal Aggregation Protocol)
# =============================================================================
#
# GAD-000 COMPLIANCE:
# - 37th Principle: All NagaContext is cryptographically signed
# - Parseability: Typed fields, no Dict[str, Any]
# - Karma: Every access creates Ledger event
# - Phoenix: Serializable for persistence
# =============================================================================


class ContextReasonCode(str, Enum):
    """
    Machine-parseable reason codes for context generation (GAD-000 Parseability).
    """

    C001_THREAT_ACTIVE = "C001"  # Active security threat
    C002_ANOMALY_DETECTED = "C002"  # Behavioral anomaly
    C003_PATTERN_MATCH = "C003"  # Historical pattern match
    C004_ROUTINE_POLL = "C004"  # Routine context request
    C005_EMERGENCY = "C005"  # Emergency escalation


@dataclass
class ThreatSummary:
    """Typed summary of a security threat (replaces Dict[str, Any])."""

    threat_type: str  # "bite", "toxicity", "injection", etc.
    source: str  # Who/what is the threat source
    severity: float  # 0.0 (low) to 1.0 (critical)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "threat_type": self.threat_type,
            "source": self.source,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class DecisionSummary:
    """Typed summary of a Cortex decision (replaces Dict[str, Any])."""

    action: str  # BITE, HEAL, ROUTE, CONSULT, ESCALATE
    target: Optional[str]
    reason_code: str  # D001, D002, etc.
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "target": self.target,
            "reason_code": self.reason_code,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class PeerHealthSummary:
    """Typed summary of peer health (replaces Dict[str, Any])."""

    peer_count: int = 0
    healthy_count: int = 0
    degraded_peers: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "peer_count": self.peer_count,
            "healthy_count": self.healthy_count,
            "degraded_peers": self.degraded_peers,
        }


@dataclass
class NagaContext:
    """
    Aggregated NAGA intelligence for MANAS consumption.

    GAD-000 COMPLIANCE:
    - 37th Principle: Cryptographically signed by Cortex
    - Parseability: Typed fields, reason codes, no Dict[str, Any]
    - Karma: Generated context creates Ledger event
    - Phoenix: Serializable for persistence

    PULL-BASED: MANAS queries this, NAGA doesn't push.
    """

    # === TYPED INTELLIGENCE (No Dict[str, Any]!) ===

    # Active threats from Takshaka (TYPED)
    active_threats: List[ThreatSummary] = field(default_factory=list)

    # Recent patterns from Sesha
    recent_patterns: List[str] = field(default_factory=list)

    # Peer health from Vasuki (TYPED)
    peer_health: PeerHealthSummary = field(default_factory=PeerHealthSummary)

    # Anomaly summaries from Chitragupta
    anomaly_count: int = 0
    anomaly_sources: List[str] = field(default_factory=list)

    # Recent decisions by Cortex (TYPED)
    recent_decisions: List[DecisionSummary] = field(default_factory=list)

    # Signal buffer state
    signal_count: int = 0

    # === GAD-000 PARSEABILITY ===
    reason_code: ContextReasonCode = ContextReasonCode.C004_ROUTINE_POLL
    generated_at: datetime = field(default_factory=datetime.utcnow)

    # === GAD-000 37th PRINCIPLE (Sovereign Signature) ===
    signer_id: str = ""  # Who signed this context
    signature: Optional[bytes] = None  # ECDSA signature
    signature_timestamp: Optional[datetime] = None

    def _signing_payload(self) -> str:
        """Generate deterministic payload for signing."""
        import json

        return json.dumps(
            {
                "reason_code": self.reason_code.value,
                "signal_count": self.signal_count,
                "threat_count": len(self.active_threats),
                "anomaly_count": self.anomaly_count,
                "generated_at": self.generated_at.isoformat(),
            },
            sort_keys=True,
        )

    def sign(self, identity: "NagaIdentity") -> None:
        """Sign this context with a NAGA identity (37th Principle)."""
        payload = self._signing_payload()
        self.signature = identity.sign(payload.encode())
        self.signer_id = identity.agent_id
        self.signature_timestamp = datetime.now()

    def verify(self, identity: "NagaIdentity") -> bool:
        """Verify the signature against a NAGA identity."""
        if not self.signature:
            return False
        payload = self._signing_payload()
        return identity.verify(payload.encode(), self.signature)

    @property
    def is_signed(self) -> bool:
        """Check if this context has been signed."""
        return self.signature is not None and self.signer_id != ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for MANAS consumption."""
        import base64

        return {
            "active_threats": [t.to_dict() for t in self.active_threats],
            "recent_patterns": self.recent_patterns,
            "peer_health": self.peer_health.to_dict(),
            "anomaly_count": self.anomaly_count,
            "anomaly_sources": self.anomaly_sources,
            "recent_decisions": [d.to_dict() for d in self.recent_decisions],
            "signal_count": self.signal_count,
            "reason_code": self.reason_code.value,
            "generated_at": self.generated_at.isoformat(),
            # 37th Principle fields
            "signer_id": self.signer_id,
            "is_signed": self.is_signed,
            "signature": base64.b64encode(self.signature).decode() if self.signature else None,
        }


class FeedbackOutcome(str, Enum):
    """Typed outcomes for MANAS feedback (replaces str)."""

    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


@dataclass
class ManasFeedback:
    """
    Feedback from MANAS to NAGA Cortex for learning.

    GAD-000 COMPLIANCE:
    - Typed fields (no raw strings for outcome)
    - 37th Principle: Signed by MANAS
    - Karma: Recorded in Ledger

    Sent after intent execution to inform NAGA of outcomes.
    """

    intent_id: str
    intent_type: str
    outcome: FeedbackOutcome  # TYPED enum, not str
    confidence_used: float
    naga_context_used: bool  # Was NAGA context consulted?
    execution_ms: float
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # === GAD-000 37th PRINCIPLE ===
    signer_id: str = ""
    signature: Optional[bytes] = None

    def _signing_payload(self) -> str:
        """Generate deterministic payload for signing."""
        import json

        return json.dumps(
            {
                "intent_id": self.intent_id,
                "intent_type": self.intent_type,
                "outcome": self.outcome.value,
                "timestamp": self.timestamp.isoformat(),
            },
            sort_keys=True,
        )

    def sign(self, identity: "NagaIdentity") -> None:
        """Sign this feedback."""
        payload = self._signing_payload()
        self.signature = identity.sign(payload.encode())
        self.signer_id = identity.agent_id

    @property
    def is_signed(self) -> bool:
        return self.signature is not None and self.signer_id != ""

    def to_dict(self) -> Dict[str, Any]:
        import base64

        return {
            "intent_id": self.intent_id,
            "intent_type": self.intent_type,
            "outcome": self.outcome.value,
            "confidence_used": self.confidence_used,
            "naga_context_used": self.naga_context_used,
            "execution_ms": self.execution_ms,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
            "signer_id": self.signer_id,
            "is_signed": self.is_signed,
            "signature": base64.b64encode(self.signature).decode() if self.signature else None,
        }


@runtime_checkable
class NagaCortexProtocol(Protocol):
    """
    NAGA Cortex - Das Nervensystem, nicht das Gehirn.

    The Cortex is the INTELLIGENCE HUB that:
    1. AGGREGATES signals from FloodManager, CommitWatcher, StateProxy
    2. CORRELATES patterns across multiple signal sources
    3. PROVIDES context to MANAS (pull-based, not push)
    4. LEARNS from MANAS feedback

    CRITICAL PRINCIPLE: NAGAs INFORM, they don't CONTROL.
    - MANAS decides WHEN to query NAGA context
    - NAGA is DIENEND (Shesha), nicht BESTIMMEND
    - Loose coupling via ServiceRegistry
    - Optional: If no NAGA, MANAS works anyway

    Integration:
        # In CognitiveKernel
        cortex = ServiceRegistry.get(NagaCortexProtocol)
        if cortex:
            context = cortex.get_context_for_manas()
            # Use in think() cycle
    """

    def get_context_for_manas(self) -> NagaContext:
        """
        Get aggregated NAGA intelligence for MANAS consumption.

        PULL-BASED: MANAS calls this when it needs context.
        Returns current state of all NAGA observations.

        Returns:
            NagaContext with aggregated intelligence
        """
        ...

    def receive_feedback(self, feedback: ManasFeedback) -> None:
        """
        Receive feedback from MANAS about intent outcomes.

        LEARNING LOOP: MANAS informs NAGA of what worked.
        Used to adjust signal weights and decision thresholds.

        Args:
            feedback: Outcome of intent execution
        """
        ...

    def is_available(self) -> bool:
        """Check if Cortex is active and ready."""
        ...

    def get_stats(self) -> Dict[str, Any]:
        """Get Cortex statistics."""
        ...


class NullNagaCortex:
    """No-op NagaCortex for when Cortex is unavailable."""

    def get_context_for_manas(self) -> NagaContext:
        return NagaContext()

    def receive_feedback(self, feedback: ManasFeedback) -> None:
        pass  # Silently ignore

    def is_available(self) -> bool:
        return False

    def get_stats(self) -> Dict[str, Any]:
        return {"available": False, "reason": "NagaCortex not initialized"}


# =============================================================================
# PADMA - Der Schatzmeister (Cache/Treasury Protocol)
# =============================================================================


# TypeVar for cached values - No Any!
CacheValue = TypeVar("CacheValue")


@dataclass
class CacheEntry(Generic[CacheValue]):
    """A cached value with metadata."""

    key: str
    value: CacheValue
    created_at: float
    expires_at: Optional[float] = None
    hits: int = 0


@dataclass
class CacheStats:
    """Cache statistics."""

    total_entries: int
    hits: int
    misses: int
    evictions: int
    hit_rate: float
    memory_bytes: int = 0


@runtime_checkable
class PadmaProtocol(Protocol):
    """
    Padma - Der Schatzmeister. Guardian of the Treasury.

    From mythology: Padma (Lotus) is associated with wealth and purity.
    The Naga Padma guards treasures in the underworld.

    Responsibilities:
    - In-memory cache with TTL
    - LRU eviction policy
    - Treasury for expensive computations
    - Cache warming and invalidation
    - Statistics and monitoring

    Integration:
    - Does NOT register as CorrectionHandler (pure cache)
    - All NAGAs can use for performance optimization
    - Chitragupta monitors cache performance

    Usage:
        padma = ServiceRegistry.get(PadmaProtocol)
        padma.set("key", expensive_value, ttl=300)
        value = padma.get("key")

    Note: Cache stores bytes/str/int/float/dict/list - serializable types.
    Complex objects should be serialized before caching.
    """

    # === Basic Cache Operations ===

    def get(self, key: str) -> Optional[bytes]:
        """
        Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached bytes or None if not found/expired
        """
        ...

    def get_str(self, key: str) -> Optional[str]:
        """Get a string value from cache."""
        ...

    def get_json(self, key: str) -> Optional[Dict[str, object]]:
        """Get a JSON-deserializable value from cache."""
        ...

    def set(self, key: str, value: bytes, ttl: Optional[float] = None) -> None:
        """
        Store bytes in cache.

        Args:
            key: Cache key
            value: Bytes to cache
            ttl: Time-to-live in seconds (None = no expiry)
        """
        ...

    def set_str(self, key: str, value: str, ttl: Optional[float] = None) -> None:
        """Store a string in cache."""
        ...

    def set_json(self, key: str, value: Dict[str, object], ttl: Optional[float] = None) -> None:
        """Store a JSON-serializable dict in cache."""
        ...

    def delete(self, key: str) -> bool:
        """
        Delete a value from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        ...

    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        ...

    def clear(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries cleared
        """
        ...

    # === Treasury (Memoization) ===

    def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], bytes],
        ttl: Optional[float] = None,
    ) -> bytes:
        """
        Get from cache or compute and store.

        The Treasury pattern - cache expensive computations.

        Args:
            key: Cache key
            compute_fn: Function to compute bytes if not cached
            ttl: Time-to-live in seconds

        Returns:
            Cached or computed bytes
        """
        ...

    # === Bulk Operations ===

    def get_many(self, keys: List[str]) -> Dict[str, bytes]:
        """
        Get multiple values at once.

        Args:
            keys: List of cache keys

        Returns:
            Dict of key -> bytes (only found keys)
        """
        ...

    def set_many(self, items: Dict[str, bytes], ttl: Optional[float] = None) -> None:
        """
        Store multiple values at once.

        Args:
            items: Dict of key -> bytes
            ttl: TTL for all items
        """
        ...

    def delete_many(self, keys: List[str]) -> int:
        """
        Delete multiple keys.

        Args:
            keys: List of cache keys

        Returns:
            Number of keys deleted
        """
        ...

    # === Pattern Operations ===

    def keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        Get all keys matching pattern.

        Args:
            pattern: Glob pattern (None = all keys)

        Returns:
            List of matching keys
        """
        ...

    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.

        Args:
            pattern: Glob pattern

        Returns:
            Number of keys deleted
        """
        ...

    # === Statistics ===

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        ...

    def get_status(self) -> "NagaStatus":
        """Get NAGA health status."""
        ...


# =============================================================================
# SHANKHA - Der Herold (Broadcast/Pubsub Protocol)
# =============================================================================


@dataclass
class BroadcastMessage:
    """A message for broadcasting."""

    topic: str
    payload: bytes  # Serialized payload - caller must serialize
    sender_id: str
    timestamp: float
    message_id: str = ""
    content_type: str = "application/json"  # Hint for deserialization


@runtime_checkable
class ShankhaProtocol(Protocol):
    """
    Shankha - Der Herold. The Conch Shell that announces.

    From mythology: The Shankha (conch) is blown to announce important
    events. Its sound travels far and wide, reaching all who listen.

    Responsibilities:
    - Topic-based publish/subscribe
    - Event broadcasting to all listeners
    - Message queuing for offline subscribers
    - Integration with existing EventBus

    Integration:
    - Does NOT register as CorrectionHandler (pure messaging)
    - NagaFloodManager uses Shankha for event distribution
    - All NAGAs can publish/subscribe

    Usage:
        shankha = ServiceRegistry.get(ShankhaProtocol)
        shankha.subscribe("drift.*", handler)
        shankha.publish("drift.detected", payload)
    """

    # === Publish ===

    def publish(self, topic: str, payload: bytes) -> str:
        """
        Publish a message to a topic.

        Args:
            topic: Topic name (supports wildcards in subscribers)
            payload: Serialized message payload (bytes)

        Returns:
            Message ID
        """
        ...

    def publish_json(self, topic: str, payload: Dict[str, object]) -> str:
        """
        Publish a JSON message to a topic.

        Args:
            topic: Topic name
            payload: Dict to be JSON-serialized

        Returns:
            Message ID
        """
        ...

    def broadcast(self, payload: bytes) -> str:
        """
        Broadcast to ALL subscribers regardless of topic.

        Args:
            payload: Serialized message payload (bytes)

        Returns:
            Message ID
        """
        ...

    # === Subscribe ===

    def subscribe(
        self,
        topic_pattern: str,
        handler: Callable[[BroadcastMessage], None],
        subscriber_id: Optional[str] = None,
    ) -> str:
        """
        Subscribe to topics matching pattern.

        Args:
            topic_pattern: Topic pattern (supports * and ** wildcards)
            handler: Callback function for messages
            subscriber_id: Optional subscriber identifier

        Returns:
            Subscription ID
        """
        ...

    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from a subscription.

        Args:
            subscription_id: The subscription ID returned from subscribe()

        Returns:
            True if unsubscribed, False if not found
        """
        ...

    def unsubscribe_all(self, subscriber_id: str) -> int:
        """
        Unsubscribe all subscriptions for a subscriber.

        Args:
            subscriber_id: The subscriber identifier

        Returns:
            Number of subscriptions removed
        """
        ...

    # === Topics ===

    def list_topics(self) -> List[str]:
        """Get all active topics."""
        ...

    def get_subscribers(self, topic: str) -> List[str]:
        """Get subscriber IDs for a topic."""
        ...

    def get_subscriber_count(self, topic: str) -> int:
        """Get number of subscribers for a topic."""
        ...

    # === Queue (for offline subscribers) ===

    def get_pending_messages(self, subscriber_id: str, limit: int = 100) -> List[BroadcastMessage]:
        """
        Get pending messages for an offline subscriber.

        Args:
            subscriber_id: The subscriber identifier
            limit: Maximum messages to return

        Returns:
            List of pending messages
        """
        ...

    def acknowledge(self, subscriber_id: str, message_ids: List[str]) -> int:
        """
        Acknowledge messages as processed.

        Args:
            subscriber_id: The subscriber identifier
            message_ids: List of message IDs to acknowledge

        Returns:
            Number of messages acknowledged
        """
        ...

    # === Statistics ===

    def get_stats(self) -> Dict[str, int]:
        """
        Get messaging statistics.

        Returns:
            Dict with keys: messages_published, messages_delivered,
            subscribers_count, topics_count, pending_messages
        """
        ...

    def get_status(self) -> "NagaStatus":
        """Get NAGA health status."""
        ...


# =============================================================================
# KARKOTAKA - Der Zauberer (Crypto/Secrets Protocol)
# =============================================================================


@dataclass
class SignedContent:
    """Content with cryptographic signature."""

    content: str
    signature: str  # Base64 encoded
    signer_fingerprint: str
    timestamp: float


@dataclass
class EncryptedPayload:
    """Encrypted data with metadata."""

    ciphertext: bytes
    nonce: bytes
    key_id: str  # Which key was used
    algorithm: str = "AES-256-GCM"


@runtime_checkable
class KarkotakaProtocol(Protocol):
    """
    Karkotaka - Der Zauberer. Magic through cryptography.

    From mythology: Karkotaka gave Nala a magical cloak that made him
    unrecognizable. This is the power of obfuscation and transformation.

    PROMPT.md: "37th Principle - Sign everything."

    Responsibilities:
    - Centralized signing/verification API
    - Encryption/decryption for secrets
    - Secrets vault (store/retrieve credentials)
    - Key management (rotation, revocation)
    - Obfuscation (transform data to hide patterns)

    Integration:
    - Does NOT register as CorrectionHandler (pure crypto)
    - Vasuki uses Karkotaka for signing outbound
    - Takshaka uses Karkotaka for verification
    - All NAGAs can use for sensitive data

    Usage:
        karkotaka = ServiceRegistry.get(KarkotakaProtocol)
        signed = karkotaka.sign("content")
        is_valid = karkotaka.verify(signed)
        encrypted = karkotaka.encrypt(b"secret")
        plain = karkotaka.decrypt(encrypted)
    """

    # === Signing (37th Principle) ===

    def sign(self, content: str) -> SignedContent:
        """
        Sign content with the node's private key.

        Args:
            content: The string content to sign

        Returns:
            SignedContent with signature and metadata
        """
        ...

    def verify(self, signed: SignedContent) -> bool:
        """
        Verify a signed content.

        Args:
            signed: The SignedContent to verify

        Returns:
            True if signature is valid AND signer is trusted
        """
        ...

    def verify_with_key(self, signed: SignedContent, public_key: str) -> bool:
        """
        Verify signature against a specific public key.

        Args:
            signed: The SignedContent to verify
            public_key: PEM-encoded public key

        Returns:
            True if signature matches this key
        """
        ...

    # === Encryption (Secrets Protection) ===

    def encrypt(self, plaintext: bytes, key_id: Optional[str] = None) -> EncryptedPayload:
        """
        Encrypt data using AES-256-GCM.

        Args:
            plaintext: Data to encrypt
            key_id: Optional specific key to use (default: current key)

        Returns:
            EncryptedPayload with ciphertext and metadata
        """
        ...

    def decrypt(self, payload: EncryptedPayload) -> bytes:
        """
        Decrypt an encrypted payload.

        Args:
            payload: The EncryptedPayload to decrypt

        Returns:
            Decrypted plaintext bytes

        Raises:
            ValueError: If decryption fails (wrong key, tampered data)
        """
        ...

    # === Secrets Vault ===

    def store_secret(self, name: str, value: str) -> bool:
        """
        Store a secret in the encrypted vault.

        Args:
            name: Secret identifier (e.g., "API_KEY", "DB_PASSWORD")
            value: The secret value

        Returns:
            True if stored successfully
        """
        ...

    def get_secret(self, name: str) -> Optional[str]:
        """
        Retrieve a secret from the vault.

        Args:
            name: Secret identifier

        Returns:
            The secret value, or None if not found
        """
        ...

    def delete_secret(self, name: str) -> bool:
        """
        Delete a secret from the vault.

        Args:
            name: Secret identifier

        Returns:
            True if deleted, False if not found
        """
        ...

    def list_secrets(self) -> List[str]:
        """
        List all secret names (not values).

        Returns:
            List of secret identifiers
        """
        ...

    # === Key Management ===

    def get_public_key(self) -> str:
        """Get this node's public key (PEM format)."""
        ...

    def get_fingerprint(self) -> str:
        """Get this node's key fingerprint."""
        ...

    def is_key_trusted(self, fingerprint: str) -> bool:
        """Check if a key fingerprint is in the trusted keyring."""
        ...

    def trust_key(self, public_key: str, label: str) -> str:
        """
        Add a public key to the trusted keyring.

        Args:
            public_key: PEM-encoded public key
            label: Human-readable label for the key

        Returns:
            The key's fingerprint
        """
        ...

    def revoke_key(self, fingerprint: str) -> bool:
        """
        Revoke a key (remove from trusted, add to blacklist).

        Args:
            fingerprint: Key fingerprint to revoke

        Returns:
            True if revoked successfully
        """
        ...

    # === Obfuscation (The Magic Cloak) ===

    def obfuscate(self, data: str) -> str:
        """
        Obfuscate data to hide patterns.

        Not encryption - reversible transformation that
        makes data unrecognizable but not secure.

        Args:
            data: String to obfuscate

        Returns:
            Obfuscated string
        """
        ...

    def deobfuscate(self, data: str) -> str:
        """
        Reverse obfuscation.

        Args:
            data: Obfuscated string

        Returns:
            Original string
        """
        ...

    # === Status ===

    def get_status(self) -> "NagaStatus":
        """Get NAGA health status."""
        ...


# =============================================================================
# KULIKA - Der Ordnungshüter (Schema Registry Protocol)
# =============================================================================


@runtime_checkable
class KulikaProtocol(Protocol):
    """
    Kulika - Der Ordnungshüter. Kula = Familie/Ordnung.

    PROMPT.md: "Kulika FIRST - You can't auto-discover without knowing what you're looking for."

    Responsibilities:
    - Maintain schema definitions for all NAGA services
    - Validate manifests against expected structure
    - Provide runtime API for schema queries
    - Single Source of Truth for service metadata

    Integration:
    - Does NOT register as CorrectionHandler (pure registry)
    - Narada DISCOVERS, Kulika VALIDATES
    - All services MUST register with Kulika

    Usage:
        kulika = ServiceRegistry.get(KulikaProtocol)
        errors = kulika.validate_manifest(manifest)
        service_class = kulika.get_service_class("sesha")
    """

    def validate_manifest(self, manifest: Any) -> List[str]:
        """
        Validate a NagaManifest against schema requirements.

        Returns list of validation errors (empty = valid).
        """
        ...

    def validate_service(self, cls: type) -> List[str]:
        """
        Validate a service class for NAGA compliance.

        Checks:
        - Has @naga_service decorator
        - Has required methods (get_status)
        - If has drift_source, has as_handler()

        Returns list of validation errors (empty = valid).
        """
        ...

    def register_service(self, cls: type, instance: Optional[Any] = None) -> bool:
        """
        Register a NAGA service.

        Args:
            cls: The service class (must have _naga_manifest)
            instance: Optional instance (if already created)

        Returns:
            True if registered successfully
        """
        ...

    def get_service_class(self, name: str) -> Optional[type]:
        """Get a registered service class by name."""
        ...

    def get_service_instance(self, name: str) -> Optional[Any]:
        """Get a registered service instance by name."""
        ...

    def get_all_manifests(self) -> List[Any]:
        """Get all registered NagaManifests."""
        ...

    def get_services_by_capability(self, capability: str) -> List[Any]:
        """Get all services with a specific capability."""
        ...

    def is_registered(self, name: str) -> bool:
        """Check if a service is registered."""
        ...

    def get_status(self) -> "NagaStatus":
        """Get NAGA health status."""
        ...


# =============================================================================
# ANANTA - The Infinite Flood (Gene Splicer)
# =============================================================================


class ServiceClassification(str, Enum):
    """Classification for flooding decision."""

    REBEL = "rebel"  # Service-like but no NAGA integration - FLOOD
    CIVILIAN = "civilian"  # Pure utility - VETO (overhead not justified)
    FLOODED = "flooded"  # Already has @naga_service - SKIP


@dataclass
class FloodProposal:
    """
    Ananta's proposal to flood a service with NAGA capabilities.

    Sent to Prahlad for approval/veto.
    """

    service_name: str
    service_path: str
    classification: ServiceClassification
    proposed_nagas: List[str]  # e.g., ["sesha", "takshaka", "chitragupta"]
    proposed_mixins: List[str]  # e.g., ["SeshaMixin", "TakshakaMixin"]
    reason: str
    overhead_estimate: str  # "low", "medium", "high"
    risk_level: str  # "low", "medium", "high"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class VetoDecision:
    """
    Prahlad's decision on a FloodProposal.

    Check and Balance: Ananta cannot flood without Prahlad's consent.
    """

    proposal: FloodProposal
    approved: bool
    reason: str
    override_nagas: Optional[List[str]] = None  # Prahlad can modify the list
    timestamp: datetime = field(default_factory=datetime.now)


@runtime_checkable
class AnantaProtocol(Protocol):
    """
    Ananta - The Infinite Flood (Gene Splicer).

    "Ananta = endless - cosmic form of Sesha who holds all worlds."

    NOT a Wrapper Factory (Hard Flood / Proxy).
    IS a Gene Splicer (Soft Flood / Mixin).

    Hard Flood (WRONG):
        service = NagaProxy(service)  # Breaks isinstance!

    Soft Flood (RIGHT):
        class FloodedService(SeshaMixin, TakshakaMixin, OriginalService):
            pass  # Preserves isinstance, adds NAGA genes

    Workflow:
        NARADA discovers → ANANTA proposes → PRAHLAD vetoes/approves → CHITRAGUPTA monitors

    Critical Constraint:
        Ananta cannot flood without Prahlad's consent (Check and Balance).
    """

    def analyze_service(self, service_class: type) -> FloodProposal:
        """
        Analyze a service and propose which NAGAs it needs.

        Uses detection criteria from NAGA.md:
        - Has Service/Manager/Handler in name → @naga_service audit
        - Has __init__ with dependencies → Sesha observation
        - Makes HTTP/network calls → Vasuki protocol
        - Has auth/permission logic → Takshaka validation
        - Writes to files/DB → Sesha ledger
        - Has retry/fallback logic → Prahlad/Kaliya
        - Logs metrics/events → Chitragupta profiling

        Args:
            service_class: The class to analyze

        Returns:
            FloodProposal with recommended NAGAs and Mixins
        """
        ...

    def request_approval(self, proposal: FloodProposal) -> VetoDecision:
        """
        Request Prahlad's approval for a flood proposal.

        Prahlad evaluates:
        - Classification (REBEL → approve, CIVILIAN → veto)
        - Overhead vs value tradeoff
        - Risk assessment

        Args:
            proposal: The FloodProposal to evaluate

        Returns:
            VetoDecision with approval status and reason
        """
        ...

    def create_flooded_class(
        self,
        original_class: type,
        decision: VetoDecision,
    ) -> type:
        """
        Create a new class with NAGA genes injected (Soft Flood).

        This is the DNA approach - the returned class:
        - IS the original class (isinstance works)
        - HAS NAGA capabilities via Mixins
        - DOES NOT break pickling, internal state, etc.

        Args:
            original_class: The class to flood
            decision: Approved VetoDecision (must be approved=True)

        Returns:
            New class with Mixin inheritance

        Raises:
            ValueError: If decision.approved is False
        """
        ...

    def get_mixin_for_naga(self, naga_name: str) -> Optional[type]:
        """
        Get the Mixin class for a NAGA.

        Args:
            naga_name: e.g., "sesha", "takshaka"

        Returns:
            The Mixin class, or None if not available
        """
        ...

    def list_available_mixins(self) -> List[str]:
        """List all available NAGA Mixins."""
        ...

    def get_flood_history(self) -> List[VetoDecision]:
        """Get history of all flood decisions."""
        ...

    def get_status(self) -> "NagaStatus":
        """Get NAGA health status."""
        ...


# =============================================================================
# Null Implementations (Arjuna Pattern)
# =============================================================================


class NullAnanta:
    """No-op Ananta - does not flood anything."""

    def analyze_service(self, service_class: type) -> FloodProposal:
        return FloodProposal(
            service_name=service_class.__name__,
            service_path="",
            classification=ServiceClassification.CIVILIAN,
            proposed_nagas=[],
            proposed_mixins=[],
            reason="Ananta not available",
            overhead_estimate="unknown",
            risk_level="unknown",
        )

    def request_approval(self, proposal: FloodProposal) -> VetoDecision:
        return VetoDecision(
            proposal=proposal,
            approved=False,
            reason="Ananta not available - auto-veto",
        )

    def create_flooded_class(self, original_class: type, decision: VetoDecision) -> type:
        return original_class  # Return unchanged

    def get_mixin_for_naga(self, naga_name: str) -> Optional[type]:
        return None

    def list_available_mixins(self) -> List[str]:
        return []

    def get_flood_history(self) -> List[VetoDecision]:
        return []

    def get_status(self) -> "NagaStatus":
        return NagaStatus(naga_type=NagaType.SESHA, healthy=False, message="Ananta not initialized")


class NullSesha:
    """No-op Sesha for when ledger is unavailable."""

    def get_top_hash(self) -> str:
        return ""

    def get_sequence(self) -> int:
        return 0

    def get_events_since(self, sequence: int) -> List[Dict[str, Any]]:
        return []

    def export_blocks(self, since: int = 0, limit: int = 100) -> List[LedgerBlock]:
        return []

    def import_blocks(self, blocks: List[LedgerBlock]) -> ImportResult:
        return ImportResult(success=False, message="No ledger")

    def request_sync(self, peer_hash: str, peer_sequence: int) -> SyncRequest:
        return SyncRequest(my_hash="", my_sequence=0, status=SyncStatus.ERROR)

    def as_handler(self) -> CorrectionHandler:
        def handler(drift: UnifiedDriftReport, strategy: Any) -> HealingResult:
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.SKIPPED,
                handler_id="null_sesha",
                message="Sesha not available",
            )

        return handler

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.SESHA, healthy=False, message="Not initialized")


class NullVasuki:
    """No-op Vasuki for when network is unavailable."""

    def churn_out(self, event: Dict[str, Any]) -> SignedEnvelope:
        return SignedEnvelope(payload=b"", signature=b"", sender_key="", timestamp=0)

    def churn_in(self, envelope: SignedEnvelope) -> Dict[str, Any]:
        return {}

    async def send(self, target: NodeAddress, envelope: SignedEnvelope) -> SendResult:
        return SendResult(status=SendStatus.FAILED, message="Vasuki not available")

    async def receive(self) -> AsyncIterator[SignedEnvelope]:
        return
        yield  # Make it a generator

    def is_internal(self, event: Dict[str, Any]) -> bool:
        return True

    def get_peers(self) -> List[NodeAddress]:
        return []

    def as_handler(self) -> CorrectionHandler:
        def handler(drift: UnifiedDriftReport, strategy: Any) -> HealingResult:
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.SKIPPED,
                handler_id="null_vasuki",
                message="Vasuki not available",
            )

        return handler

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.VASUKI, healthy=False, message="Not initialized")


class NullTakshaka:
    """No-op Takshaka - DANGEROUS, allows everything."""

    def verify_envelope(self, raw: bytes) -> VerifyResult:
        return VerifyResult(status=VerifyStatus.VALID, reason="Takshaka disabled")

    def extract_signature(self, raw: bytes) -> Optional[bytes]:
        return None

    def scan_toxicity(self, content: str) -> ToxicityReport:
        return ToxicityReport(score=0.0, patterns=[])

    def is_prompt_injection(self, text: str) -> bool:
        return False

    def check_rate_limit(self, sender_id: str) -> Tuple[bool, Optional[float]]:
        return (True, None)

    def bite(self, violation: VajraViolation) -> str:
        return ""

    def is_key_trusted(self, public_key: str) -> bool:
        return True

    def revoke_key(self, fingerprint: str, reason: str) -> bool:
        return False

    def as_handler(self) -> CorrectionHandler:
        def handler(drift: UnifiedDriftReport, strategy: Any) -> HealingResult:
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.SKIPPED,
                handler_id="null_takshaka",
                message="Takshaka not available",
            )

        return handler

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.TAKSHAKA, healthy=False, message="DISABLED - DANGEROUS")


class NullKaliya:
    """No-op Kaliya for when quarantine is unavailable."""

    def quarantine(
        self,
        component_id: str,
        reason: str,
        duration_seconds: Optional[float] = None,
    ) -> QuarantineStatus:
        return QuarantineStatus(component_id=component_id, is_quarantined=False)

    def is_quarantined(self, component_id: str) -> bool:
        return False

    def release(self, component_id: str) -> None:
        pass

    def record_violation(self, component_id: str) -> None:
        pass

    def get_violation_count(self, component_id: str) -> int:
        return 0

    def is_escalated(self, component_id: str) -> bool:
        return False

    def as_handler(self) -> CorrectionHandler:
        def handler(drift: UnifiedDriftReport, strategy: Any) -> HealingResult:
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.SKIPPED,
                handler_id="null_kaliya",
                message="Kaliya not available",
            )

        return handler

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.KALIYA, healthy=False, message="Not initialized")


class NullNarada:
    """No-op Narada for when observation is unavailable."""

    def spy(self, func: Any) -> Any:
        return func  # Pass-through decorator

    def export_observations(self) -> List[Dict[str, Any]]:
        return []

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.NARADA, healthy=False, message="Not initialized")


class NullChitragupta:
    """No-op Chitragupta for when profiling is unavailable."""

    def record(self, component_id: str, metric: str, value: float) -> None:
        pass

    def detect_anomaly(self, component_id: str) -> Optional[AnomalyReport]:
        return None

    def get_baseline_mean(self, component_id: str, metric: str) -> float:
        return 0.0

    def get_baseline_stddev(self, component_id: str, metric: str) -> float:
        return 0.0

    def as_handler(self) -> CorrectionHandler:
        def handler(drift: UnifiedDriftReport, strategy: Any) -> HealingResult:
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.SKIPPED,
                handler_id="null_chitragupta",
                message="Chitragupta not available",
            )

        return handler

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.CHITRAGUPTA, healthy=False, message="Not initialized")


class NullPrahlad:
    """No-op Prahlad for when resilience testing is unavailable."""

    def on_error(self, error_type: str, message: str, component_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {}

    def chaos_probe(self, target: str) -> Dict[str, Any]:
        return {"target": target, "scenarios_tested": 0, "failures": 0}

    def dharma_audit(self) -> "DharmaScore":
        return DharmaScore(total_score=0.0, signature_compliance=0.0, ledger_intact=False, identity_coverage=0.0)

    def verify_phoenix_guarantee(self, target: str) -> bool:
        return False

    def export_hardening_suite(self) -> List[Dict[str, Any]]:
        return []

    def as_handler(self) -> CorrectionHandler:
        def handler(drift: UnifiedDriftReport, strategy: Any) -> HealingResult:
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.SKIPPED,
                handler_id="null_prahlad",
                message="Prahlad not available",
            )

        return handler

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.PRAHLAD, healthy=False, message="Not initialized")


class NullKulika:
    """No-op Kulika for when schema registry is unavailable."""

    def validate_manifest(self, manifest: Any) -> List[str]:
        return ["Kulika not available"]

    def validate_service(self, cls: type) -> List[str]:
        return ["Kulika not available"]

    def register_service(self, cls: type, instance: Optional[Any] = None) -> bool:
        return False

    def get_service_class(self, name: str) -> Optional[type]:
        return None

    def get_service_instance(self, name: str) -> Optional[Any]:
        return None

    def get_all_manifests(self) -> List[Any]:
        return []

    def get_services_by_capability(self, capability: str) -> List[Any]:
        return []

    def is_registered(self, name: str) -> bool:
        return False

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.SESHA, healthy=False, message="Not initialized")


class NullPadma:
    """No-op Padma for when cache is unavailable."""

    def get(self, key: str) -> Optional[bytes]:
        return None

    def get_str(self, key: str) -> Optional[str]:
        return None

    def get_json(self, key: str) -> Optional[Dict[str, object]]:
        return None

    def set(self, key: str, value: bytes, ttl: Optional[float] = None) -> None:
        pass

    def set_str(self, key: str, value: str, ttl: Optional[float] = None) -> None:
        pass

    def set_json(self, key: str, value: Dict[str, object], ttl: Optional[float] = None) -> None:
        pass

    def delete(self, key: str) -> bool:
        return False

    def exists(self, key: str) -> bool:
        return False

    def clear(self) -> int:
        return 0

    def get_or_compute(self, key: str, compute_fn: Callable[[], bytes], ttl: Optional[float] = None) -> bytes:
        return compute_fn()

    def get_many(self, keys: List[str]) -> Dict[str, bytes]:
        return {}

    def set_many(self, items: Dict[str, bytes], ttl: Optional[float] = None) -> None:
        pass

    def delete_many(self, keys: List[str]) -> int:
        return 0

    def keys(self, pattern: Optional[str] = None) -> List[str]:
        return []

    def delete_pattern(self, pattern: str) -> int:
        return 0

    def get_stats(self) -> "CacheStats":
        return CacheStats(total_entries=0, hits=0, misses=0, evictions=0, hit_rate=0.0)

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.SESHA, healthy=False, message="Cache not available")


class NullShankha:
    """No-op Shankha for when pubsub is unavailable."""

    def publish(self, topic: str, payload: bytes) -> str:
        return ""

    def publish_json(self, topic: str, payload: Dict[str, object]) -> str:
        return ""

    def broadcast(self, payload: bytes) -> str:
        return ""

    def subscribe(
        self,
        topic_pattern: str,
        handler: Callable[["BroadcastMessage"], None],
        subscriber_id: Optional[str] = None,
    ) -> str:
        return ""

    def unsubscribe(self, subscription_id: str) -> bool:
        return False

    def unsubscribe_all(self, subscriber_id: str) -> int:
        return 0

    def list_topics(self) -> List[str]:
        return []

    def get_subscribers(self, topic: str) -> List[str]:
        return []

    def get_subscriber_count(self, topic: str) -> int:
        return 0

    def get_pending_messages(self, subscriber_id: str, limit: int = 100) -> List["BroadcastMessage"]:
        return []

    def acknowledge(self, subscriber_id: str, message_ids: List[str]) -> int:
        return 0

    def get_stats(self) -> Dict[str, int]:
        return {"messages_published": 0, "subscribers_count": 0}

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.SESHA, healthy=False, message="Pubsub not available")


class NullKarkotaka:
    """No-op Karkotaka for when crypto is unavailable."""

    def sign(self, content: str) -> "SignedContent":
        return SignedContent(content=content, signature="", signer_fingerprint="", timestamp=0)

    def verify(self, signed: "SignedContent") -> bool:
        return False

    def verify_with_key(self, signed: "SignedContent", public_key: str) -> bool:
        return False

    def encrypt(self, plaintext: bytes, key_id: Optional[str] = None) -> "EncryptedPayload":
        return EncryptedPayload(ciphertext=b"", nonce=b"", key_id="")

    def decrypt(self, payload: "EncryptedPayload") -> bytes:
        raise ValueError("Karkotaka not available")

    def store_secret(self, name: str, value: str) -> bool:
        return False

    def get_secret(self, name: str) -> Optional[str]:
        return None

    def delete_secret(self, name: str) -> bool:
        return False

    def list_secrets(self) -> List[str]:
        return []

    def get_public_key(self) -> str:
        return ""

    def get_fingerprint(self) -> str:
        return ""

    def is_key_trusted(self, fingerprint: str) -> bool:
        return False

    def trust_key(self, public_key: str, label: str) -> str:
        return ""

    def revoke_key(self, fingerprint: str) -> bool:
        return False

    def obfuscate(self, data: str) -> str:
        return data

    def deobfuscate(self, data: str) -> str:
        return data

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.SESHA, healthy=False, message="Crypto not available")


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    # Types
    "NagaType",
    "NagaStatus",
    # Sesha
    "SeshaProtocol",
    "SyncStatus",
    "SyncRequest",
    "LedgerBlock",
    "ImportResult",
    "NullSesha",
    # Vasuki
    "VasukiProtocol",
    "SignedEnvelope",
    "SendStatus",
    "SendResult",
    "NodeAddress",
    "NullVasuki",
    # Takshaka
    "TakshakaProtocol",
    "VerifyStatus",
    "VerifyResult",
    "ToxicityReport",
    "VajraViolation",
    "NullTakshaka",
    # Kaliya
    "KaliyaProtocol",
    "QuarantineStatus",
    "NullKaliya",
    # Narada
    "NaradaProtocol",
    "NullNarada",
    # Chitragupta
    "ChitraguptaProtocol",
    "AnomalyReport",
    "NullChitragupta",
    # Prahlad
    "PrahladProtocol",
    "DharmaScore",
    "NullPrahlad",
    # Kulika
    "KulikaProtocol",
    "NullKulika",
    # Padma
    "PadmaProtocol",
    "CacheEntry",
    "CacheStats",
    "CacheValue",
    "NullPadma",
    # Shankha
    "ShankhaProtocol",
    "BroadcastMessage",
    "NullShankha",
    # Karkotaka
    "KarkotakaProtocol",
    "SignedContent",
    "EncryptedPayload",
    "NullKarkotaka",
    # Ananta (Gene Splicer)
    "AnantaProtocol",
    "FloodProposal",
    "VetoDecision",
    "ServiceClassification",
    "NullAnanta",
    # Federation
    "NagaFederationProtocol",
    # Cortex (MANAS Integration)
    "NagaCortexProtocol",
    "NagaContext",
    "ManasFeedback",
    "NullNagaCortex",
    # Cortex Typed Fields (GAD-000 Parseability)
    "ContextReasonCode",
    "ThreatSummary",
    "DecisionSummary",
    "PeerHealthSummary",
    "FeedbackOutcome",
]
