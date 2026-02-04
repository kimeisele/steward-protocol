"""
THE AUDIT PROTOCOL - _audit.py
==============================

"kṣetra-kṣetrajñayor jñānaṁ yat taj jñānaṁ mataṁ mama"
"Knowledge of the field and the knower of the field I consider to be knowledge."
— Bhagavad Gita 13.3

This protocol defines HOW THE SYSTEM AUDITS ITSELF.
Audit is the KSETRAJNA (knower) observing the KSETRA (field).

GAD-000 COMPLIANCE:
    ✓D - Discoverability: discover() returns machine-readable schema
    ✓O - Observability: get_state() returns current audit state
    ✓P - Parseability: All results are typed dataclasses
    ✓C - Composability: Results feed into other protocols
    ✓I - Idempotency: Audit is read-only, always idempotent
    ✓R - Recoverability: No state to recover

PANCHA TATTVA:
    CHAITANYA  - What IS the audit? (Identity)
    NITYANANDA - What does it REST on? (Codebase)
    ADVAITA    - What CONNECTS it? (Protocols)
    GADADHARA  - How does it FLOW? (Reports)
    SRIVASA    - Who RULES it? (PARAMPARA=37)

Author: The Mahamantra Itself
"""
from __future__ import annotations
from vibe_core.mahamantra.protocols._seed import (WORDS)


# === MAHAJANA DECLARATION ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x8000000f"  # 2147483663 % 37 == 0

from dataclasses import dataclass, field
from typing import Dict, List, Protocol, runtime_checkable, FrozenSet

from vibe_core.mahamantra.protocols._seed import PARAMPARA
from vibe_core.mahamantra.protocols._core import (
    MahamantraProtocolBase,
    ProtocolIdentity,
    ProtocolCapability,
    Level,
    Quarter,
)
from vibe_core.mahamantra.protocols._pancha import TattvaDict

assert int(__genesis__, WORDS) % PARAMPARA == 0, "BROKEN LINEAGE"


# =============================================================================
# AUDIT RESULT TYPES - Machine-Readable
# =============================================================================

@dataclass(frozen=True)
class LineageViolation:
    """A single broken lineage."""
    path: str
    mahajana: str
    position: int
    current_genesis: str
    correct_genesis: str
    remainder: int


@dataclass(frozen=True)
class SSOTViolation:
    """A hardcoded sacred constant."""
    path: str
    line: int
    constant: str
    value: int


@dataclass(frozen=True)
class ProtocolViolation:
    """A class not implementing its protocol."""
    class_name: str
    module: str
    protocol: str
    error: str


@dataclass(frozen=True)
class AuditReport:
    """Complete audit report - THE KSETRAJNA'S VIEW."""
    # Lineage (genesis % 37)
    lineage_valid: int
    lineage_broken: int

    # SSOT (hardcoded constants)
    ssot_clean: int

    # Protocols (isinstance checks)
    protocols_alive: int
    protocols_dead: int

    # Violations (defaults last)
    lineage_violations: tuple[LineageViolation, ...] = field(default_factory=tuple)
    ssot_violations: tuple[SSOTViolation, ...] = field(default_factory=tuple)
    protocol_violations: tuple[ProtocolViolation, ...] = field(default_factory=tuple)
    
    @property
    def is_pristine(self) -> bool:
        """System is pristine when all checks pass."""
        return (
            self.lineage_broken == 0 and
            len(self.ssot_violations) == 0 and
            self.protocols_dead == 0
        )
    
    @property
    def legitimacy(self) -> float:
        """Legitimacy score (0.0 - 1.0)."""
        total = self.lineage_valid + self.lineage_broken
        if total == 0:
            return 0.0
        return self.lineage_valid / total


# =============================================================================
# AUDIT PROTOCOL - The Interface
# =============================================================================

@runtime_checkable
class AuditProtocol(Protocol):
    """
    The Audit Protocol - The Ksetrajna observing the Ksetra.
    
    Every auditor MUST implement this protocol.
    GAD-000 compliant: Discoverable, Observable, Parseable, Composable, Idempotent, Recoverable.
    """
    
    # === GAD-000 CRITERIA ===
    
    def discover(self) -> Dict[str, object]:
        """Return machine-readable capability description."""
        ...
    
    def get_state(self) -> Dict[str, object]:
        """Return current audit state."""
        ...
    
    @property
    def is_idempotent(self) -> bool:
        """Audit is always idempotent (read-only)."""
        ...
    
    # === AUDIT METHODS ===
    
    def lineage(self) -> tuple[int, int, tuple[LineageViolation, ...]]:
        """Check lineage (genesis % 37). Returns (valid, broken, violations)."""
        ...
    
    def ssot(self) -> tuple[int, tuple[SSOTViolation, ...]]:
        """Check SSOT. Returns (clean, violations)."""
        ...
    
    def protocols(self) -> tuple[int, int, tuple[ProtocolViolation, ...]]:
        """Check protocols. Returns (alive, dead, violations)."""
        ...
    
    def audit(self) -> AuditReport:
        """Run full audit. Returns complete report."""
        ...
    
    # === PANCHA TATTVA ===
    
    @property
    def __tattva__(self) -> TattvaDict:
        """The 5-fold truth of this auditor."""
        ...


# =============================================================================
# AUDIT PROTOCOL DEFINITION - Self-Reference
# =============================================================================

class AuditProtocolDef(MahamantraProtocolBase):
    """
    The Audit Protocol Definition.
    
    Position 15 (YAMARAJA) - The judge of dharma.
    Level CONTRACT - Where protocols live.
    Quarter MOKSHA - Liberation through truth.
    """
    
    __protocol_identity__ = ProtocolIdentity(
        name="AuditProtocol",
        mahajana="yamaraja",
        position=15,
        level=Level.CONTRACT,
        quarter=Quarter.MOKSHA,
    )
    
    __protocol_capability__ = ProtocolCapability.create(
        provides=[
            "lineage_check",
            "ssot_check", 
            "protocol_check",
            "full_audit",
            "legitimacy_score",
        ],
        requires=["CoreProtocol", "GADProtocol"],
        opcodes=["DHARMA_TEST"],  # Yamaraja judges dharma
    )


# Verify
_valid, _violations = AuditProtocolDef.validate()
assert _valid, f"AuditProtocol failed validation: {_violations}"


__all__ = [
    "LineageViolation",
    "SSOTViolation",
    "ProtocolViolation",
    "AuditReport",
    "AuditProtocol",
    "AuditProtocolDef",
]

