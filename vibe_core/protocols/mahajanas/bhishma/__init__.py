"""
BHISHMA - The 9th Mahajana (Vow/Commitment)
===========================================

POSITION: 11 (KARMA Quarter, COMMIT_LOG OpCode)

Bhishma Pitamaha - The Grandsire.
Took a terrible vow and kept it until death.
Taught Dharma to the Pandavas from his bed of arrows.

DERIVED FROM MAHAMANTRA:
    Position 11 → guardian=BHISHMA, opcode=COMMIT_LOG, quarter=KARMA
    All properties derived from truth table. No manual wiring.

Once Bhishma commits, it CANNOT be undone.
His word is his bond. The log is the law.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import (
    ClassVar,
    Dict,
    List,
    Optional,
    Protocol,
    TypedDict,
    Union,
    runtime_checkable,
)

from vibe_core.mahamantra import WorkerProtocol, Mahajana, MantraOpCode


# =============================================================================
# BHISHMA PROTOCOL BASE - Derives from MantraPosition 11
# =============================================================================

class BhishmaProtocolBase(WorkerProtocol):
    """
    Bhishma protocol ownership - DERIVED from Mahamantra position 11.

    NO MANUAL WIRING:
        _position_index = 11 is the ONLY configuration.
        Everything else derived from truth table.

    DERIVED PROPERTIES:
        guardian()  → Mahajana.BHISHMA
        opcode()    → MantraOpCode.COMMIT_LOG
        quarter()   → Quarter.KARMA
        is_head()   → False (Worker position)
        parampara_vector() → 444 (% 37 == 0)
    """
    _position_index: ClassVar[int] = 11  # THE ONLY CONFIGURATION


# NO MANUAL WIRING - Everything derived from mahamantra[11]


# =============================================================================
# WATERTIGHT STATE TYPES (No Any!)
# =============================================================================

# The union of allowed commit entry types - WATERTIGHT
CommitEntry = Union[str, int, float, bool, Dict[str, str], List[str]]


class CommitResult(TypedDict, total=False):
    """
    Result of a commit operation.
    WATERTIGHT - no Any!
    """
    success: bool
    commit_id: str            # Hash/ID of the commit
    timestamp: str            # ISO timestamp
    previous_id: str          # Hash of previous commit (for lineage)
    error_message: str


class VerificationResult(TypedDict, total=False):
    """
    Result of lineage verification.
    WATERTIGHT - no Any!
    """
    valid: bool
    commit_id: str
    lineage_intact: bool
    error_message: str


class CommitState(TypedDict, total=False):
    """
    State of commitment/ledger.
    WATERTIGHT - no Any!
    """
    total_commits: int
    last_commit_id: str
    last_commit_time: str     # ISO timestamp
    lineage_length: int
    lineage_hash: str         # Hash of entire lineage
    health: str               # "pristine", "healthy", "degraded"


class CommitCliResult(TypedDict):
    """Result of CLI commit operation. WATERTIGHT - no Any!"""
    success: bool
    commit_id: str
    timestamp: str
    message: str


# =============================================================================
# BHISHMA PROTOCOL
# =============================================================================


@runtime_checkable
class BhishmaProtocol(Protocol):
    """
    The Commitment/Ledger Protocol - Bhishma's domain.

    DERIVED: Position 11 → BHISHMA, COMMIT_LOG, KARMA
    WATERTIGHT - no Any types!
    """

    @classmethod
    def position_index(cls) -> int:
        """Position 11 in the Mahamantra."""
        ...

    def commit(self, entry: CommitEntry, sovereign_id: str) -> CommitResult:
        """
        COMMIT_LOG: Commit an entry to the ledger.
        WATERTIGHT: entry is CommitEntry union, not Any.
        """
        ...

    def verify(self, commit_id: str) -> VerificationResult:
        """Verify a commit exists and is valid."""
        ...

    def get_lineage(self, limit: int = 100) -> List[str]:
        """Get the commit lineage (list of commit IDs)."""
        ...

    def verify_lineage(self) -> VerificationResult:
        """Verify the entire lineage is intact."""
        ...

    def get_state(self) -> CommitState:
        """Get commitment state. WATERTIGHT."""
        ...


# =============================================================================
# NULL BHISHMA
# =============================================================================


class NullBhishma(BhishmaProtocolBase):
    """
    The Uncommitted. No logging (for testing).

    Inherits from BhishmaProtocolBase → position 11 → BHISHMA.
    """

    def commit(self, entry: CommitEntry, sovereign_id: str) -> CommitResult:
        return CommitResult(
            success=True,
            commit_id="null_commit",
            timestamp=datetime.now().isoformat(),
            previous_id="",
            error_message="",
        )

    def verify(self, commit_id: str) -> VerificationResult:
        return VerificationResult(
            valid=True,
            commit_id=commit_id,
            lineage_intact=True,
            error_message="",
        )

    def get_lineage(self, limit: int = 100) -> List[str]:
        return []

    def verify_lineage(self) -> VerificationResult:
        return VerificationResult(
            valid=True,
            commit_id="",
            lineage_intact=True,
            error_message="",
        )

    def get_state(self) -> CommitState:
        return CommitState(
            total_commits=0,
            last_commit_id="",
            lineage_length=0,
            lineage_hash="",
            health="pristine",
        )

    def commit_cli(self, message: str = "null commit", sovereign: str = "cli") -> CommitCliResult:
        """CLI: Commit with simple string args. WATERTIGHT."""
        # CommitEntry is a Union type - pass a dict as the entry
        entry: Dict[str, str] = {
            "action": "cli_commit",
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "author": sovereign,
        }
        result = self.commit(entry, sovereign)
        # CommitResult is TypedDict - access via dict keys
        return CommitCliResult(
            success=result.get("success", True),
            commit_id=result.get("commit_id", "null"),
            timestamp=result.get("timestamp", ""),
            message=message,
        )


# =============================================================================
# LEDGER - Immutable Commit Log
# =============================================================================

from vibe_core.protocols.mahajanas.bhishma.ledger import (
    GENESIS_HASH,
    LedgerEntry,
    LedgerProtocol,
    Ledger,
    NullLedger,
    LOTUS_POSITION as LEDGER_POSITION,
)

# =============================================================================
# LINEAGE - Parampara Chain Verification
# =============================================================================

from vibe_core.protocols.mahajanas.bhishma.lineage import (
    PARAMPARA_DIVISOR,
    LineageStatus,
    LineageNode,
    LineageVerification,
    LineageProtocol,
    Lineage,
    NullLineage,
    LOTUS_POSITION as LINEAGE_POSITION,
)


__all__ = [
    # Protocol Base (MantraProtocol derivative) - THE ONLY SOURCE
    "BhishmaProtocolBase",
    # Bhishma Protocol (WATERTIGHT)
    "CommitEntry", "CommitResult", "VerificationResult", "CommitState",
    "CommitCliResult",
    "BhishmaProtocol", "NullBhishma",
    # Ledger
    "GENESIS_HASH",
    "LedgerEntry",
    "LedgerProtocol",
    "Ledger",
    "NullLedger",
    # Lineage
    "PARAMPARA_DIVISOR",
    "LineageStatus",
    "LineageNode",
    "LineageVerification",
    "LineageProtocol",
    "Lineage",
    "NullLineage",
]
