"""
LEDGER - Immutable Commit Ledger
================================

OWNER: BHISHMA (The Grandsire)
POSITION: 11 (KARMA Quarter)
OPCODE: COMMIT_LOG

Bhishma's vow was IMMUTABLE. Once spoken, it could not be undone.
This ledger follows the same principle: append-only, hash-chained, tamper-evident.

SHASTRA BASIS:
    Bhishma took the vow of brahmacharya to allow his father to marry.
    He kept this vow for his ENTIRE LIFE - even when it caused suffering.
    "I will not marry. I will not have children. I will not rule."
    This is PRATJNA - the unbreakable vow.

    The ledger is Bhishma's PRATJNA in code:
    - Once committed, CANNOT be changed
    - Each entry chained to previous (parampara)
    - Tampering is DETECTABLE
    - The chain is the law

ARCHITECTURE:
    Entry₀ ← Entry₁ ← Entry₂ ← ... ← Entry_n
       │        │        │              │
    hash₀ → hash₁ → hash₂ → ... → hash_n

    Each entry contains:
    - payload (the actual data)
    - previous_hash (chain link)
    - timestamp
    - sovereign_id (who committed)

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bhishma"
__position__ = 11
__genesis__ = "0x27025da7"  # GenesisByte: parampara % 37 == 0

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Final, Iterator, List, Optional, Protocol, Tuple, runtime_checkable

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode

# Import types from parent module
from vibe_core.protocols.mahajanas.bhishma import (
    CommitEntry,
    CommitResult,
    VerificationResult,
    CommitState,
)


# =============================================================================
# OWNERSHIP DECLARATION - Bhishma OWNS this protocol
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.BHISHMA
LOTUS_POSITION: Final[int] = 11  # KARMA Quarter, Worker 3
LOTUS_QUARTER: Final[str] = "karma"

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.LEDGER_SIGN,
]

# Genesis hash - the root of all ledgers
GENESIS_HASH: Final[str] = "0" * 64  # 64 zeros = SHA-256 of nothing


# =============================================================================
# LEDGER ENTRY - Single immutable record
# =============================================================================


@dataclass(frozen=True)
class LedgerEntry:
    """
    A single immutable entry in the ledger.

    Frozen dataclass = immutable after creation.
    Like Bhishma's vow - once made, cannot change.
    """

    commit_id: str  # SHA-256 hash of this entry
    previous_id: str  # Hash of previous entry (chain link)
    timestamp: str  # ISO timestamp
    sovereign_id: str  # Who committed this
    payload_type: str  # Type of payload
    payload_repr: str  # String representation of payload
    payload_hash: str  # Hash of payload for integrity
    sequence: int  # Position in ledger (0-indexed)

    @classmethod
    def create(
        cls,
        payload: CommitEntry,
        sovereign_id: str,
        previous_id: str,
        sequence: int,
    ) -> "LedgerEntry":
        """Create a new ledger entry with computed hashes."""
        timestamp = datetime.now().isoformat()
        payload_type = type(payload).__name__
        payload_repr = json.dumps(payload) if isinstance(payload, (dict, list)) else str(payload)
        payload_hash = cls._hash(payload_repr)

        # Compute commit_id from all fields
        commit_data = f"{previous_id}:{timestamp}:{sovereign_id}:{payload_hash}:{sequence}"
        commit_id = cls._hash(commit_data)

        return cls(
            commit_id=commit_id,
            previous_id=previous_id,
            timestamp=timestamp,
            sovereign_id=sovereign_id,
            payload_type=payload_type,
            payload_repr=payload_repr[:1000],  # Truncate for safety
            payload_hash=payload_hash,
            sequence=sequence,
        )

    @staticmethod
    def _hash(data: str) -> str:
        """Compute SHA-256 hash."""
        return hashlib.sha256(data.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify this entry's hash is correct."""
        commit_data = f"{self.previous_id}:{self.timestamp}:{self.sovereign_id}:{self.payload_hash}:{self.sequence}"
        expected_hash = self._hash(commit_data)
        return self.commit_id == expected_hash

    def to_dict(self) -> Dict[str, str | int]:
        """Serialize for storage/transmission."""
        return {
            "commit_id": self.commit_id,
            "previous_id": self.previous_id,
            "timestamp": self.timestamp,
            "sovereign_id": self.sovereign_id,
            "payload_type": self.payload_type,
            "payload_repr": self.payload_repr,
            "payload_hash": self.payload_hash,
            "sequence": self.sequence,
        }


# =============================================================================
# LEDGER PROTOCOL - Immutable Commit Interface
# =============================================================================


@runtime_checkable
class LedgerProtocol(Protocol):
    """
    The Immutable Ledger Protocol - Bhishma's Pratjna.

    OWNER: Mahajana.BHISHMA

    This ledger follows Bhishma's vow:
    - Append-only (no updates, no deletes)
    - Hash-chained (parampara)
    - Tamper-evident (verification)

    ANTI-MAYAVAD:
    - No Any types
    - Bhishma OWNS this ledger
    - Commits are PERSONAL (sovereign_id required)
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.BHISHMA."""
        ...

    @property
    def length(self) -> int:
        """Number of entries in ledger."""
        ...

    @property
    def head(self) -> Optional[str]:
        """Hash of the latest entry (None if empty)."""
        ...

    # =========================================================================
    # Commit Operations (COMMIT_LOG OpCode)
    # =========================================================================

    def commit(self, payload: CommitEntry, sovereign_id: str) -> CommitResult:
        """
        Commit a new entry to the ledger.
        IMMUTABLE: Once committed, cannot be changed.
        """
        ...

    def get(self, commit_id: str) -> Optional[LedgerEntry]:
        """Get an entry by its commit_id."""
        ...

    def get_by_sequence(self, sequence: int) -> Optional[LedgerEntry]:
        """Get an entry by its sequence number."""
        ...

    # =========================================================================
    # Verification (Bhishma's Integrity)
    # =========================================================================

    def verify(self, commit_id: str) -> VerificationResult:
        """Verify a specific entry's integrity."""
        ...

    def verify_chain(self) -> VerificationResult:
        """Verify the entire chain is intact."""
        ...

    # =========================================================================
    # Iteration
    # =========================================================================

    def iterate(self, start: int = 0, limit: int = 100) -> Iterator[LedgerEntry]:
        """Iterate over entries from start."""
        ...

    def get_lineage(self, limit: int = 100) -> List[str]:
        """Get list of commit_ids in order."""
        ...

    # =========================================================================
    # State
    # =========================================================================

    def get_state(self) -> CommitState:
        """Get ledger state for observability."""
        ...


# =============================================================================
# LEDGER IMPLEMENTATION - Immutable Append-Only Log
# =============================================================================


class Ledger:
    """
    Bhishma's Ledger - The Immutable Commit Log.

    OWNER: Mahajana.BHISHMA

    Like Bhishma's vow that lasted his entire life,
    entries in this ledger are PERMANENT.

    Features:
    - Append-only (no updates/deletes)
    - Hash-chained (each entry links to previous)
    - Tamper-evident (verification detects changes)
    - O(1) commit, O(1) lookup by hash
    """

    def __init__(self) -> None:
        """Initialize empty ledger."""
        self._entries: List[LedgerEntry] = []
        self._index: Dict[str, int] = {}  # commit_id -> sequence
        self._chain_hash = GENESIS_HASH

    @property
    def owner(self) -> Mahajana:
        return Mahajana.BHISHMA

    @property
    def length(self) -> int:
        return len(self._entries)

    @property
    def head(self) -> Optional[str]:
        if not self._entries:
            return None
        return self._entries[-1].commit_id

    # =========================================================================
    # Commit Operations
    # =========================================================================

    def commit(self, payload: CommitEntry, sovereign_id: str) -> CommitResult:
        """
        Commit a new entry to the ledger.

        Bhishma's vow: Once committed, CANNOT be undone.
        """
        previous_id = self.head or GENESIS_HASH
        sequence = len(self._entries)

        # Create immutable entry
        entry = LedgerEntry.create(
            payload=payload,
            sovereign_id=sovereign_id,
            previous_id=previous_id,
            sequence=sequence,
        )

        # Append to ledger
        self._entries.append(entry)
        self._index[entry.commit_id] = sequence
        self._chain_hash = entry.commit_id

        return CommitResult(
            success=True,
            commit_id=entry.commit_id,
            timestamp=entry.timestamp,
            previous_id=entry.previous_id,
            error_message="",
        )

    def get(self, commit_id: str) -> Optional[LedgerEntry]:
        """Get entry by commit_id."""
        sequence = self._index.get(commit_id)
        if sequence is None:
            return None
        return self._entries[sequence]

    def get_by_sequence(self, sequence: int) -> Optional[LedgerEntry]:
        """Get entry by sequence number."""
        if 0 <= sequence < len(self._entries):
            return self._entries[sequence]
        return None

    # =========================================================================
    # Verification
    # =========================================================================

    def verify(self, commit_id: str) -> VerificationResult:
        """Verify a specific entry's integrity."""
        entry = self.get(commit_id)
        if entry is None:
            return VerificationResult(
                valid=False,
                commit_id=commit_id,
                lineage_intact=False,
                error_message=f"Entry not found: {commit_id}",
            )

        if not entry.verify_integrity():
            return VerificationResult(
                valid=False,
                commit_id=commit_id,
                lineage_intact=False,
                error_message="Entry hash mismatch - tampering detected",
            )

        # Verify chain link
        if entry.sequence > 0:
            previous = self._entries[entry.sequence - 1]
            if entry.previous_id != previous.commit_id:
                return VerificationResult(
                    valid=False,
                    commit_id=commit_id,
                    lineage_intact=False,
                    error_message="Chain link broken - lineage violated",
                )

        return VerificationResult(
            valid=True,
            commit_id=commit_id,
            lineage_intact=True,
            error_message="",
        )

    def verify_chain(self) -> VerificationResult:
        """Verify the entire chain is intact."""
        if not self._entries:
            return VerificationResult(
                valid=True,
                commit_id="",
                lineage_intact=True,
                error_message="",
            )

        expected_previous = GENESIS_HASH
        for entry in self._entries:
            # Check previous link
            if entry.previous_id != expected_previous:
                return VerificationResult(
                    valid=False,
                    commit_id=entry.commit_id,
                    lineage_intact=False,
                    error_message=f"Chain broken at sequence {entry.sequence}",
                )

            # Check integrity
            if not entry.verify_integrity():
                return VerificationResult(
                    valid=False,
                    commit_id=entry.commit_id,
                    lineage_intact=False,
                    error_message=f"Hash mismatch at sequence {entry.sequence}",
                )

            expected_previous = entry.commit_id

        return VerificationResult(
            valid=True,
            commit_id=self.head or "",
            lineage_intact=True,
            error_message="",
        )

    # =========================================================================
    # Iteration
    # =========================================================================

    def iterate(self, start: int = 0, limit: int = 100) -> Iterator[LedgerEntry]:
        """Iterate over entries."""
        end = min(start + limit, len(self._entries))
        for i in range(start, end):
            yield self._entries[i]

    def get_lineage(self, limit: int = 100) -> List[str]:
        """Get list of commit_ids in order."""
        return [e.commit_id for e in self._entries[-limit:]]

    # =========================================================================
    # State
    # =========================================================================

    def get_state(self) -> CommitState:
        """Get ledger state for observability."""
        return CommitState(
            total_commits=len(self._entries),
            last_commit_id=self.head or "",
            last_commit_time=self._entries[-1].timestamp if self._entries else "",
            lineage_length=len(self._entries),
            lineage_hash=self._chain_hash,
            health="healthy" if self.verify_chain()["valid"] else "degraded",
        )


# =============================================================================
# NULL LEDGER - For testing
# =============================================================================


class NullLedger:
    """
    The Uncommitted Ledger - no persistence.

    Used for testing without actual storage.
    Still owned by BHISHMA.
    """

    @property
    def owner(self) -> Mahajana:
        return Mahajana.BHISHMA

    @property
    def length(self) -> int:
        return 0

    @property
    def head(self) -> Optional[str]:
        return None

    def commit(self, payload: CommitEntry, sovereign_id: str) -> CommitResult:
        return CommitResult(
            success=True,
            commit_id="null_commit",
            timestamp=datetime.now().isoformat(),
            previous_id="",
            error_message="",
        )

    def get(self, commit_id: str) -> Optional[LedgerEntry]:
        return None

    def get_by_sequence(self, sequence: int) -> Optional[LedgerEntry]:
        return None

    def verify(self, commit_id: str) -> VerificationResult:
        return VerificationResult(valid=True, commit_id=commit_id, lineage_intact=True, error_message="")

    def verify_chain(self) -> VerificationResult:
        return VerificationResult(valid=True, commit_id="", lineage_intact=True, error_message="")

    def iterate(self, start: int = 0, limit: int = 100) -> Iterator[LedgerEntry]:
        return iter([])

    def get_lineage(self, limit: int = 100) -> List[str]:
        return []

    def get_state(self) -> CommitState:
        return CommitState(
            total_commits=0,
            last_commit_id="",
            lineage_length=0,
            lineage_hash=GENESIS_HASH,
            health="pristine",
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Ownership
    "OWNER",
    "LOTUS_POSITION",
    "LOTUS_QUARTER",
    "OWNED_OPCODES",
    "GENESIS_HASH",
    # Entry
    "LedgerEntry",
    # Protocol
    "LedgerProtocol",
    # Implementations
    "Ledger",
    "NullLedger",
]
