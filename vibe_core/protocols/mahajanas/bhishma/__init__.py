"""
BHISHMA - The 9th Mahajana (Vow/Commitment)
===========================================
OpCode: COMMIT_LOG (Bit 12, Position 12 in Mahamantra)
Opulence: Yashas (Fame/Glory)

Bhishma Pitamaha - The Grandsire.
Took a terrible vow and kept it until death.
Taught Dharma to the Pandavas from his bed of arrows.

PROTOCOL OWNERSHIP (Anti-Mayavad):
Bhishma is the PERSON responsible for all commitments.
Not abstract "logging" - PERSONAL vow-keeping by Bhishma.

OWNED PROTOCOLS:
- Commit Logging (COMMIT_LOG OpCode)
- Transaction Commits
- Lineage Verification
- Immutable Records
- Pratjna (Vow-keeping)
- Ledger Management

Once Bhishma commits, it CANNOT be undone.
His word is his bond. The log is the law.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import (
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    TypedDict,
    Union,
    runtime_checkable,
)

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode


# =============================================================================
# PROTOCOL OWNERSHIP
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.BHISHMA
LOTUS_POSITION: Final[int] = 11  # KARMA Quarter, Worker 3
LOTUS_QUARTER: Final[str] = "karma"

OWNED_PROTOCOLS: Final[List[str]] = [
    "bhishma",
    "commitment",
    "ledger",
    "logging",
    "audit",
    "lineage",
]

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.COMMIT_LOG,
]


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


# =============================================================================
# BHISHMA PROTOCOL
# =============================================================================


@runtime_checkable
class BhishmaProtocol(Protocol):
    """
    The Commitment/Ledger Protocol - Bhishma's domain.
    WATERTIGHT - no Any types!
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.BHISHMA."""
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


class NullBhishma:
    """The Uncommitted. No logging (for testing)."""

    @property
    def owner(self) -> Mahajana:
        return Mahajana.BHISHMA

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


__all__ = [
    "OWNER", "LOTUS_POSITION", "LOTUS_QUARTER", "OWNED_PROTOCOLS", "OWNED_OPCODES",
    "CommitEntry", "CommitResult", "VerificationResult", "CommitState",
    "BhishmaProtocol", "NullBhishma",
]
