"""
BHISHMA PROTOCOL - The Vow (Ledger & History)
=============================================

"pratijnayate visva-sakshi"
"The Witness of the Universe promises..."

POSITION: 11 (Karma Quarter)
FUNCTION: Ledger, Commitment, Lineage, Immutable History.

This protocol defines the Ledger interface.
It replaces the legacy `BhishmaProtocol` in `vibe_core/protocols/mahajanas`.

LOCATION: vibe_core.mahamantra.karma.bhishma.protocol
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bhishma"
__position__ = 11
__genesis__ = "0xad738708"  # GenesisByte: parampara % 37 == 0

from typing import Protocol, runtime_checkable, Dict, List, Optional, TypedDict
from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol, TattvaDict


class CommitEntry(TypedDict):
    """A single entry in the ledger."""

    event_type: str
    agent_id: str
    details: Dict[str, str]  # Strict typing: values must be strings/serialized
    timestamp: str
    signature: str


class CommitResult(TypedDict):
    success: bool
    commit_id: str
    timestamp: str
    previous_id: str
    error_message: str


class VerificationResult(TypedDict):
    valid: bool
    commit_id: str
    lineage_intact: bool
    error_message: str


class CommitState(TypedDict):
    """Current state of the commitment ledger."""

    total_commits: int
    last_commit_id: str
    last_commit_time: str
    lineage_length: int
    lineage_hash: str
    health: str


@runtime_checkable
class BhishmaProtocol(PanchaTattvaProtocol, Protocol):
    """
    The Grandsire Protocol (Ledger).
    Responsible for maintaining the immutable history.
    """

    @property
    def __tattva__(self) -> TattvaDict:
        return {
            "chaitanya": "Ledger Protocol",
            "nityananda": "Storage Substrate",
            "advaita": "Commit Logic",
            "gadadhara": "Event Flow",
            "srivasa": "Lineage Governance",
        }

    def commit(self, entry: CommitEntry, sovereign_id: str) -> CommitResult:
        """
        COMMIT_LOG: Write to the eternal ledger.
        Must be signed by sovereign_id (The 37th).
        """
        ...

    def verify(self, commit_id: str) -> VerificationResult:
        """
        Verify a specific commit exists and is valid.
        """
        ...

    def get_lineage(self, limit: int = 100) -> List[str]:
        """
        Get the chain of custody.
        """
        ...


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "BhishmaProtocol",
    "CommitEntry",
    "CommitResult",
    "CommitState",
    "VerificationResult",
]
