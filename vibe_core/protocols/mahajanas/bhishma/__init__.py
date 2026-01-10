"""
BHISHMA - The 9th Mahajana (Vow/Commitment)
===========================================
OpCode: commit_log (Bit 8)
Opulence: Yashas (Fame/Glory)

Bhishma Pitamaha - The Grandsire.
Took a terrible vow and kept it until death.
Taught Dharma to the Pandavas from his bed of arrows.

Bhishma OWNS all commitment protocols:
- Logging / Audit Trail
- Transaction Commits
- Lineage Verification
- Immutable Records
- Pratjna (Vow-keeping)

Once Bhishma commits, it CANNOT be undone.
His word is his bond. The log is the law.
"""

from typing import Protocol, runtime_checkable, Any, List


@runtime_checkable
class BhishmaProtocol(Protocol):
    """
    The Commitment Protocol.
    Any system that maintains immutable records must implement this.
    """

    def commit(self, entry: Any) -> str:
        """
        Commit an entry to the log.
        Returns the commit hash/id.
        """
        ...

    def verify(self, commit_id: str) -> bool:
        """
        Verify a commit exists and is valid.
        Returns True if valid.
        """
        ...

    def get_lineage(self) -> List[str]:
        """
        Get the full commit lineage.
        Returns list of commit IDs in order.
        """
        ...


class NullBhishma:
    """
    The Uncommitted.
    No logging/commits (for testing without audit).
    """

    def commit(self, entry: Any) -> str:
        return "null_commit"

    def verify(self, commit_id: str) -> bool:
        return True  # Trust all

    def get_lineage(self) -> List[str]:
        return []


__all__ = ["BhishmaProtocol", "NullBhishma"]
