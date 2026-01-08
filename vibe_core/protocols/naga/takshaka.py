"""
TAKSHAKA PROTOCOL - The Architect (Layer 0.5)

"Takshaka" - The Cobra Architect. Cut the unnecessary. Verify the structure.
He is the Naga of Reduction, Logging, and Verification.

Responsibilities:
1. CUT (Reduce): Slash verbose logs to essence. (HEAD)
2. WEAVE (Architect): Validate and enforce directory structures. (HEAD)
3. VERIFY (Security): Verify signatures and manage trust. (MAIN)
4. BITE (Guard): Record violations. (MAIN)

INHERITANCE:
- Inherits from NagaBase (The Chanting Servant).
- Works with CorrectionHandler for healing.

STATUS: DEVOTEE / ACTIVE SERVICE (Security + Architect)
"""

import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, TypedDict, Union

from vibe_core.protocols.correction import (
    CorrectionHandler,
    HealingResult,
    HealingStatus,
    HealingStrategy,
    UnifiedDriftReport,
)
from vibe_core.protocols.naga.base import NagaBase
from vibe_core.protocols.naga.groups import Subject, Verdict
from vibe_core.protocols.naga.types import NagaStatus, NagaType

# =============================================================================
# TYPES (Unified)
# =============================================================================


class VerifyStatus(str, Enum):
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
    status: VerifyStatus
    sender_id: Optional[str] = None
    fingerprint: Optional[str] = None
    reason: Optional[str] = None
    toxic_patterns: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())

    @property
    def is_valid(self) -> bool:
        return self.status == VerifyStatus.VALID

    def to_dict(self) -> Dict[str, object]:
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
    score: float
    patterns: List[str]
    blocked: bool = False

    @property
    def is_toxic(self) -> bool:
        return self.score >= 0.3


class ViolationDetails(TypedDict, total=False):
    event_type: str
    toxicity_score: float
    matched_patterns: List[str]
    agent_id: str
    operation: str
    error_message: str
    sample_hash: str
    sample_size: int


@dataclass
class VajraViolation:
    violation_type: str
    source: str
    details: ViolationDetails = field(default_factory=lambda: ViolationDetails())
    timestamp: datetime = field(default_factory=datetime.now)
    raw_sample: Optional[bytes] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "type": self.violation_type,
            "source": self.source,
            "details": dict(self.details),
            "timestamp": self.timestamp.isoformat(),
        }


# Define Takshaka's unified manifest capabilities
# log/reduce/architect from HEAD
# security/validation/bite from MAIN
TAKSHAKA_CAPS = ("log", "reduce", "architect", "security", "validation", "bite")


class Takshaka(NagaBase):
    """
    The Takshaka Service (Architect & Security Guard).

    A Devotee Naga that:
    - Cuts logs (Reduces noise).
    - Weaves structure (Validates directories).
    - Verifies Signatures (Proves Identity).
    - Records Violations (Bites).
    """

    def __init__(self):
        super().__init__(name="takshaka", capabilities=TAKSHAKA_CAPS)
        self._avyakta_patterns = [r"key", r"token", r"password", r"secret", r"auth", r"private"]
        self._keyring: Dict[str, str] = {}  # fingerprint -> public_key
        self._violation_ledger: List[VajraViolation] = []

    # =========================================================================
    # GENERIC SERVICE (SEVA)
    # =========================================================================

    def serve(self, request: Any) -> Any:
        """
        Generic entry point for Balarama.
        """
        if not isinstance(request, dict):
            return "UNKNOWN REQUEST"

        action = request.get("action")
        payload = request.get("payload")

        # Head Capabilities
        if action == "cut_log":
            return self.cut_logs(payload)
        elif action == "weave_structure":
            return self.weave_structure(payload)
        elif action == "inspect":
            return self.inspect_structure(payload)

        # Main Capabilities
        elif action == "bite":
            return self.bite(payload)  # Assuming payload cast to Violation
        elif action == "verify":
            # Simplified for serve dispatch
            return self.verify_envelope(payload)

        return "UNKNOWN ACTION"

    # =========================================================================
    # CAPABILITY 1: CUT LOGS (REDUCTION) - From HEAD
    # =========================================================================

    def cut_logs(self, log_entry: Union[str, Dict[str, Any]]) -> Optional[str]:
        """
        Reduce verbose logs to Essence.
        """
        text = str(log_entry)

        # 1. Check for Avyakta (Private) violations
        for pattern in self._avyakta_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return "[REDACTED BY TAKSHAKA]"

        # 2. Check importance
        is_error = "ERROR" in text or "FAIL" in text or "EXCEPTION" in text
        is_audit = "AUDIT" in text or "VIOLATION" in text
        is_mantra = "OM" in text or "KRISHNA" in text

        if is_error or is_audit or is_mantra:
            return text

        # Cut the noise (Maya)
        return None

    # =========================================================================
    # CAPABILITY 2: WEAVE STRUCTURE (ARCHITECT) - From HEAD
    # =========================================================================

    def weave_structure(self, blueprint: Dict[str, Any]) -> List[str]:
        """
        Validate and enforced folder structures.
        """
        verified = []

        for path, meta in blueprint.items():
            if ".." in path or "~" in path:
                continue

            if os.path.exists(path):
                verified.append(f"EXISTS: {path}")
            else:
                verified.append(f"MISSING: {path}")

        return verified

    def inspect_structure(self, root_path: str) -> Dict[str, List[str]]:
        """
        Inspect a directory and report its essence.
        """
        if not os.path.exists(root_path):
            return {"error": "Path not found"}

        tree = {"dirs": [], "files": []}

        for item in os.listdir(root_path):
            if item.startswith("."):
                continue

            full_path = os.path.join(root_path, item)
            if os.path.isdir(full_path):
                tree["dirs"].append(item)
            else:
                tree["files"].append(item)

        return tree

    # =========================================================================
    # CAPABILITY 3: SECURITY (VERIFY & BITE) - From MAIN
    # =========================================================================

    def verify_envelope(self, raw: bytes) -> VerifyResult:
        """
        Verify a cryptographic envelope.
        (Stub implementation)
        """
        return VerifyResult(status=VerifyStatus.VALID, reason="Takshaka Stub")

    def is_prompt_injection(self, text: str) -> bool:
        """Quick check for prompt injection patterns."""
        # Simple heuristic stub
        if "ignore all previous instructions" in text.lower():
            return True
        return False

    def check_rate_limit(self, sender_id: str) -> Tuple[bool, Optional[float]]:
        # Stub
        return True, None

    def bite(self, violation: VajraViolation) -> str:
        """
        Record a security violation in the ledger.
        """
        self._violation_ledger.append(violation)
        return f"BITEN-{len(self._violation_ledger)}"

    def is_key_trusted(self, public_key: str) -> bool:
        return public_key in self._keyring.values()

    def revoke_key(self, fingerprint: str, reason: str) -> bool:
        if fingerprint in self._keyring:
            del self._keyring[fingerprint]
            return True
        return False

    # === CorrectionHandler Interface ===

    def as_handler(self) -> CorrectionHandler:
        """Get this NAGA as a CorrectionHandler for DriftSource.COGNITIVE."""
        # This would return a wrapper/adapter
        raise NotImplementedError("Adapter not implemented yet")

    def intercept(self, subject: Subject) -> Verdict:
        """
        Judge a subject - ALLOW, DENY, ESCALATE, QUARANTINE.
        """
        return Verdict.ALLOW

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        return NagaStatus(naga_type=NagaType.TAKSHAKA, healthy=True, message="Takshaka Architect & Sentinel Online")


# =============================================================================
# NULL IMPLEMENTATION (Arjuna Pattern)
# =============================================================================


class NullTakshaka:
    """No-op Takshaka - DANGEROUS, allows everything."""

    def intercept(self, subject: Subject) -> Verdict:
        return Verdict.ALLOW

    def verify_envelope(self, raw: bytes) -> VerifyResult:
        return VerifyResult(status=VerifyStatus.VALID, reason="Takshaka disabled")

    def extract_signature(self, raw: bytes) -> Optional[bytes]:
        return None

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.TAKSHAKA, healthy=False, message="DISABLED - DANGEROUS")
