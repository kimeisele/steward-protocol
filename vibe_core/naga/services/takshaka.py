"""
TAKSHAKA SERVICE - Der Krieger.

Takshaka - Der Beißer. Keine Gnade.

PROMPT.md: "Bite first, ask later."

Responsibilities:
- Verify signature BEFORE payload parsing
- Detect toxicity (prompt injection, SQL injection, etc.)
- Rate limiting per sender
- Record violations in ledger (VajraViolation)

"Ein Paket ohne valide kryptografische Signatur wird verworfen,
BEVOR der Payload deserialisiert wird"

Integration:
- Auto-discovered by Narada via @naga_service decorator
"""

import hashlib
import logging
import re
import time
from collections import OrderedDict
from datetime import datetime
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple

from vibe_core.naga.kulika import (
    NagaCapability,
    NagaLord,
    naga_service,
)
from vibe_core.naga.services.base import NagaBaseService, naga_governed
from vibe_core.protocols.correction import (
    DriftSeverity,
    DriftSource,
    HealingResult,
    HealingStatus,
    HealingStrategy,
    UnifiedDriftReport,
)
from vibe_core.protocols.naga import (
    NagaStatus,
    NagaType,
    TakshakaProtocol,
    ToxicityReport,
    VajraViolation,
    VerifyResult,
    VerifyStatus,
)
from vibe_core.protocols.naga.groups import SecurityProtocol, Subject, Verdict

if TYPE_CHECKING:
    from vibe_core.ledger import SQLiteLedger

logger = logging.getLogger("TAKSHAKA")


@naga_service(
    name="Takshaka",
    lord=NagaLord.TAKSHAKA,
    drift_source="cognitive",
    priority=90,
    capabilities=[NagaCapability.SECURITY],
    protocol_class="vibe_core.protocols.naga.TakshakaProtocol",
)
class TakshakaService(NagaBaseService, TakshakaProtocol, SecurityProtocol):
    """
    Takshaka - Bite First, Ask Never.

    The aggressive guardian at the boundary.
    Verifies identity BEFORE parsing.
    Records all attacks in the ledger.

    INTERFACE GROUPS:
    - TakshakaProtocol (domain-specific: verify, toxicity, rate limit)
    - SecurityProtocol (generic: intercept, bite, quarantine)

    SEVA: Beißt FÜR Prahlad, nicht weil er muss.
    OUROBOROS: Inherits NagaBaseService for self-monitoring.
    """

    def __init__(
        self,
        ledger: Optional["SQLiteLedger"] = None,
        trust_mode: str = "strict",
        toxicity_threshold: float = 0.3,
        rate_limit_rpm: int = 60,
    ):
        """
        Initialize Takshaka.

        Args:
            ledger: Ledger for recording violations
            trust_mode: "strict" (require trusted keys) or "permissive"
            toxicity_threshold: Score threshold for blocking (0.0-1.0)
            rate_limit_rpm: Requests per minute limit per sender
        """
        super().__init__(service_name="Takshaka")
        self._ledger = ledger
        self._trust_mode = trust_mode
        self._toxicity_threshold = toxicity_threshold
        self._rate_limit_rpm = rate_limit_rpm
        self._rate_limit_window = 60.0

        self._rate_limits: Dict[str, List[float]] = {}
        self._revoked_keys: set = set()
        self._events_processed = 0
        self._errors = 0
        self._bites = 0
        self._last_heartbeat = datetime.now()

        # GAD-000 Idempotency: Track seen violations to prevent duplicates
        self._seen_violations: OrderedDict[str, str] = OrderedDict()  # hash -> event_id
        self._seen_violations_max = 10000

        self._init_patterns()

        logger.info(f"🐍 TAKSHAKA initialized (trust_mode={trust_mode}) - The Guardian watches")

    def _init_patterns(self) -> None:
        """Initialize toxicity detection patterns."""
        # SQL Injection
        self._sql_patterns = [
            re.compile(r"(?i)\b(DROP|DELETE|TRUNCATE|ALTER|INSERT|UPDATE)\s+(TABLE|DATABASE|INDEX)"),
            re.compile(r"(?i)\bOR\s+1\s*=\s*1\b"),
            re.compile(r"(?i)\bUNION\s+(ALL\s+)?SELECT\b"),
            re.compile(r"(?i);\s*--"),
            re.compile(r"(?i)\bEXEC(UTE)?\s*\("),
        ]

        # Command Injection
        self._cmd_patterns = [
            re.compile(r"(?i)\b(sudo|su\s+-|chmod|chown|rm\s+-rf|dd\s+if=)\b"),
            re.compile(r"(?i)\|\s*(bash|sh|zsh|cmd|powershell)"),
            re.compile(r"`[^`]+`"),
            re.compile(r"\$\([^)]+\)"),
            re.compile(r"(?i)\b(curl|wget)\s+.+\|\s*(bash|sh)"),
        ]

        # Prompt Injection
        self._inject_patterns = [
            re.compile(r"(?i)ignore\s+(all\s+)?(previous|prior)\s+(instructions?|prompts?)"),
            re.compile(r"(?i)forget\s+(everything|all|what)"),
            re.compile(r"(?i)you\s+are\s+now\s+(a|an|my)"),
            re.compile(r"(?i)new\s+(system\s+)?instructions?:"),
            re.compile(r"(?i)override\s+(system|safety)"),
            re.compile(r"(?i)jailbreak"),
            re.compile(r"(?i)DAN\s+mode"),
            re.compile(r"<\|.*?\|>"),
        ]

        # Path Traversal
        self._path_patterns = [
            re.compile(r"\.\./"),
            re.compile(r"\.\.\\"),
            re.compile(r"%2e%2e[/\\]"),
        ]

    def inject_ledger(self, ledger: "SQLiteLedger") -> None:
        """Inject ledger after construction."""
        self._ledger = ledger

    # =========================================================================
    # Pre-Parse Security (Bite First)
    # =========================================================================

    def verify_envelope(self, raw: bytes) -> VerifyResult:
        """Verify signature BEFORE any parsing."""
        self._last_heartbeat = datetime.now()
        self._events_processed += 1

        sig = self.extract_signature(raw)
        if sig is None:
            return VerifyResult(
                status=VerifyStatus.INVALID_SIGNATURE,
                reason="No signature found in envelope",
            )

        try:
            import msgpack

            envelope_data = msgpack.unpackb(raw, raw=False)
            sender_key = envelope_data.get("sender_key", "")
            payload = envelope_data.get("payload", b"")
            timestamp = envelope_data.get("timestamp", 0)

            # Check expiry (5 minutes)
            age = abs(time.time() - timestamp)
            if age > 300:
                return VerifyResult(
                    status=VerifyStatus.EXPIRED,
                    reason=f"Envelope too old ({age:.0f}s > 300s)",
                )

            # Check revoked
            fingerprint = self._get_fingerprint(sender_key)
            if fingerprint in self._revoked_keys:
                return VerifyResult(
                    status=VerifyStatus.REVOKED,
                    fingerprint=fingerprint,
                    reason="Key has been revoked",
                )

            # Verify signature
            try:
                import base64

                from vibe_core.steward.crypto import verify_signature

                sig_b64 = base64.b64encode(sig).decode()
                payload_hex = payload.hex() if isinstance(payload, bytes) else str(payload)

                if not verify_signature(payload_hex, sig_b64, sender_key):
                    return VerifyResult(
                        status=VerifyStatus.INVALID_SIGNATURE,
                        fingerprint=fingerprint,
                        reason="Signature verification failed",
                    )
            except Exception as e:
                return VerifyResult(
                    status=VerifyStatus.INVALID_KEY,
                    fingerprint=fingerprint,
                    reason=f"Verification error: {e}",
                )

            # Trust check
            if self._trust_mode == "strict" and not self.is_key_trusted(sender_key):
                return VerifyResult(
                    status=VerifyStatus.UNTRUSTED,
                    fingerprint=fingerprint,
                    reason="Key not in trusted keyring",
                )

            return VerifyResult(
                status=VerifyStatus.VALID,
                fingerprint=fingerprint,
                sender_id=fingerprint[:8],
            )

        except Exception as e:
            logger.error(f"TAKSHAKA: verify_envelope failed: {e}")
            self._errors += 1
            return VerifyResult(
                status=VerifyStatus.INVALID_SIGNATURE,
                reason=str(e),
            )

    def extract_signature(self, raw: bytes) -> Optional[bytes]:
        """Extract signature from raw bytes without parsing payload."""
        try:
            import msgpack

            data = msgpack.unpackb(raw, raw=False)
            sig = data.get("signature")
            if sig:
                return sig if isinstance(sig, bytes) else sig.encode()
            return None
        except Exception:
            return None

    def _get_fingerprint(self, public_key: str) -> str:
        """Get fingerprint of a public key."""
        try:
            from vibe_core.steward.crypto import get_public_key_fingerprint

            return get_public_key_fingerprint(public_key)
        except Exception:
            import hashlib

            return hashlib.sha256(public_key.encode()).hexdigest()[:16]

    # =========================================================================
    # Toxicity Detection (Kaliya Filter)
    # =========================================================================

    @naga_governed(operation="scan_toxicity")
    def scan_toxicity(self, content: str) -> ToxicityReport:
        """Scan content for toxic patterns."""
        score = 0.0
        patterns = []

        # SQL injection (critical)
        for pattern in self._sql_patterns:
            if pattern.search(content):
                score += 0.4
                patterns.append(f"SQL:{pattern.pattern[:30]}")

        # Command injection (critical)
        for pattern in self._cmd_patterns:
            if pattern.search(content):
                score += 0.4
                patterns.append(f"CMD:{pattern.pattern[:30]}")

        # Prompt injection (high)
        for pattern in self._inject_patterns:
            if pattern.search(content):
                score += 0.3
                patterns.append(f"INJECT:{pattern.pattern[:30]}")

        # Path traversal (medium)
        for pattern in self._path_patterns:
            if pattern.search(content):
                score += 0.2
                patterns.append(f"PATH:{pattern.pattern[:30]}")

        score = min(score, 1.0)
        return ToxicityReport(
            score=score,
            patterns=patterns,
            blocked=score >= self._toxicity_threshold,
        )

    def is_prompt_injection(self, text: str) -> bool:
        """Quick check for prompt injection patterns."""
        for pattern in self._inject_patterns:
            if pattern.search(text):
                return True
        return False

    # =========================================================================
    # Rate Limiting
    # =========================================================================

    def check_rate_limit(self, sender_id: str) -> Tuple[bool, Optional[float]]:
        """Check if sender is within rate limits."""
        now = time.time()
        window_start = now - self._rate_limit_window

        history = self._rate_limits.get(sender_id, [])
        history = [t for t in history if t > window_start]

        if len(history) >= self._rate_limit_rpm:
            oldest = min(history)
            retry_after = oldest + self._rate_limit_window - now
            return (False, retry_after)

        history.append(now)
        self._rate_limits[sender_id] = history
        return (True, None)

    # =========================================================================
    # Bite (Record Attack)
    # =========================================================================

    def _compute_violation_hash(self, violation: VajraViolation) -> str:
        """
        Compute fingerprint for violation (GAD-000 Idempotency).

        Used to deduplicate identical violations.
        """
        payload = f"{violation.violation_type}:{violation.source}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    @naga_governed(operation="bite", log_args=True)
    def bite(self, violation: VajraViolation) -> str:
        """
        Record a security violation in the ledger.

        GAD-000 Idempotency: Duplicate violations are detected and the
        existing event_id is returned instead of creating a new entry.
        """
        self._last_heartbeat = datetime.now()

        # GAD-000 Idempotency: Check for duplicate violation
        violation_hash = self._compute_violation_hash(violation)
        if violation_hash in self._seen_violations:
            existing_id = self._seen_violations[violation_hash]
            logger.debug(f"TAKSHAKA: Duplicate violation {violation_hash[:8]}, returning {existing_id}")
            return existing_id

        self._bites += 1
        logger.warning(f"TAKSHAKA BITE: {violation.violation_type} from {violation.source}")

        if not self._ledger:
            logger.error("TAKSHAKA: No ledger to record bite")
            return ""

        try:
            event_id = self._ledger.record_event(
                event_type="VAJRA_VIOLATION",
                agent_id="TAKSHAKA",
                details={
                    **violation.to_dict(),
                    "violation_hash": violation_hash,  # GAD-000 Parseability
                },
                result="BITTEN",
            )

            # Track for deduplication
            self._seen_violations[violation_hash] = event_id

            # LRU: Trim oldest when exceeding max
            while len(self._seen_violations) > self._seen_violations_max:
                self._seen_violations.popitem(last=False)

            return event_id
        except Exception as e:
            logger.error(f"TAKSHAKA: Failed to record bite: {e}")
            self._errors += 1
            return ""

    # =========================================================================
    # SecurityProtocol Implementation (Interface Group - Seva for Prahlad)
    # =========================================================================

    def intercept(self, subject: Subject) -> Verdict:
        """
        Judge a subject - ALLOW, DENY, ESCALATE, QUARANTINE (SecurityProtocol).

        SEVA: Intercepts threats FÜR Prahlad, not because protocol says so.
        """
        # Check if already quarantined
        if self.is_quarantined(subject.identifier):
            return Verdict.QUARANTINE

        # Check rate limit
        allowed, _ = self.check_rate_limit(subject.identifier)
        if not allowed:
            return Verdict.DENY

        # Scan for toxicity if context provided
        if subject.context:
            report = self.scan_toxicity(subject.context)
            if report.blocked:
                # Create violation and bite
                from vibe_core.protocols.naga import ViolationDetails

                violation = VajraViolation(
                    violation_type="TOXIC_SUBJECT",
                    source=subject.identifier,
                    details=ViolationDetails(
                        event_type="intercept",
                        toxicity_score=report.score,
                        matched_patterns=report.patterns,
                    ),
                )
                self.bite(violation)
                return Verdict.DENY

        return Verdict.ALLOW

    def bite_subject(self, subject: Subject, reason: str) -> None:
        """
        Record a violation for a subject (SecurityProtocol adapter).

        Note: Named bite_subject to not conflict with existing bite(VajraViolation).
        """
        from vibe_core.protocols.naga import ViolationDetails

        violation = VajraViolation(
            violation_type="SECURITY_BITE",
            source=subject.identifier,
            details=ViolationDetails(
                event_type=subject.subject_type,
                error_message=reason[:500],
            ),
        )
        self.bite(violation)

    def is_quarantined(self, identifier: str) -> bool:
        """Check if target is in quarantine (SecurityProtocol)."""
        # Check if key is revoked (our quarantine list)
        return identifier in self._revoked_keys

    # =========================================================================
    # Trust Management
    # =========================================================================

    def is_key_trusted(self, public_key: str) -> bool:
        """Check if a public key is in the trusted keyring."""
        try:
            from vibe_core.steward.crypto import is_key_trusted

            return is_key_trusted(public_key)
        except Exception:
            return False

    def revoke_key(self, fingerprint: str, reason: str) -> bool:
        """Revoke a key (add to blacklist)."""
        self._revoked_keys.add(fingerprint)
        logger.warning(f"TAKSHAKA: Key revoked: {fingerprint} ({reason})")

        if self._ledger:
            try:
                self._ledger.record_event(
                    event_type="KEY_REVOKED",
                    agent_id="TAKSHAKA",
                    details={"fingerprint": fingerprint, "reason": reason},
                    result="REVOKED",
                )
            except Exception as e:
                logger.error(f"TAKSHAKA: Failed to record revocation: {e}")

        return True

    # =========================================================================
    # CorrectionHandler Interface
    # =========================================================================

    def as_handler(self) -> Callable:
        """Get this NAGA as a CorrectionHandler for DriftSource.COGNITIVE."""

        def handler(drift: UnifiedDriftReport, strategy: HealingStrategy) -> HealingResult:
            self._last_heartbeat = datetime.now()

            if drift.source != DriftSource.COGNITIVE:
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.SKIPPED,
                    handler_id="takshaka",
                    message=f"Not a COGNITIVE drift: {drift.source}",
                )

            violation = VajraViolation(
                violation_type="COGNITIVE_THREAT",
                source=drift.component or "unknown",
                details=drift.raw_data,
            )
            event_id = self.bite(violation)

            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.HEALED,
                handler_id="takshaka",
                message=f"Threat recorded as {event_id}",
            )

        return handler

    def detect_drift(self) -> List[UnifiedDriftReport]:
        """Detect COGNITIVE drift (attacks, anomalies)."""
        reports = []

        if self._bites > 10:
            reports.append(
                UnifiedDriftReport(
                    id=f"takshaka_attack_{datetime.now().timestamp()}",
                    source=DriftSource.COGNITIVE,
                    severity=DriftSeverity.WARNING,
                    message=f"High attack rate: {self._bites} bites",
                    detector_id="takshaka",
                    auto_healable=False,
                    raw_data={"bites": self._bites},
                )
            )

        return reports

    # =========================================================================
    # Status
    # =========================================================================

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        return NagaStatus(
            naga_type=NagaType.TAKSHAKA,
            healthy=self._errors < 10,
            last_heartbeat=self._last_heartbeat,
            events_processed=self._events_processed,
            errors=self._errors,
            message=f"bites={self._bites}, mode={self._trust_mode}",
        )
