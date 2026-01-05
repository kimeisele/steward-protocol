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
    Any,
    AsyncIterator,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    runtime_checkable,
)

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
# Null Implementations (Arjuna Pattern)
# =============================================================================


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
    # Federation
    "NagaFederationProtocol",
]
