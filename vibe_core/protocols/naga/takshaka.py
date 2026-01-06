"""
TAKSHAKA Protocol - Der Krieger (Security/Ingress)

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
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Tuple, TypedDict, runtime_checkable

from vibe_core.protocols.correction import (
    CorrectionHandler,
    HealingResult,
    HealingStatus,
    UnifiedDriftReport,
)
from vibe_core.protocols.naga.types import NagaStatus, NagaType


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


class ViolationDetails(TypedDict, total=False):
    """
    Typed violation details - STAMBHA (The Pillar).

    Replaces Dict[str, Any] to prevent Halahala poison:
    - SQL injection in arbitrary keys
    - Memory bombs in arbitrary values
    - Null byte attacks
    - Type confusion

    Prahlad's DNA: Explicit fields, no surprises.
    """

    # Core violation info
    event_type: str  # What event triggered the violation
    toxicity_score: float  # 0.0-1.0 from Takshaka
    matched_patterns: List[str]  # What patterns were detected

    # Context (bounded strings, not arbitrary)
    agent_id: str  # Max 64 chars enforced by creator
    operation: str  # What operation was attempted
    error_message: str  # Max 500 chars enforced by creator

    # Forensics (bounded)
    sample_hash: str  # SHA256 of raw payload, not the payload itself
    sample_size: int  # Size in bytes of original payload


@dataclass
class VajraViolation:
    """
    Record of a security violation (for ledger).

    HALAHALA HARDENED: Uses ViolationDetails TypedDict instead of Dict[str, Any].
    This is Prahlad's gift - the type safety DNA that prevents poison injection.
    """

    violation_type: str  # NO_SIGNATURE, INVALID_SIGNATURE, TOXIC, etc.
    source: str  # IP, agent_id, etc.
    details: ViolationDetails = field(default_factory=lambda: ViolationDetails())
    timestamp: datetime = field(default_factory=datetime.now)
    raw_sample: Optional[bytes] = None  # First N bytes for forensics

    def to_dict(self) -> Dict[str, object]:
        """Serialize to dict. Returns Dict[str, object] not Dict[str, Any]."""
        return {
            "type": self.violation_type,
            "source": self.source,
            "details": dict(self.details),
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
# NULL IMPLEMENTATION (Arjuna Pattern)
# =============================================================================


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
