"""
SPEED.md: LineageProtocol - Fast Boot via Merkle Checkpointing

PROMPT.md: "Protocol statt konkrete Klassen (Dependency Inversion)"

The Parampara chain is sacred but verification is slow.
3293 blocks verified on every boot = GAD-000 Principle 6 violation.

This protocol defines the interface for:
1. Fast tip hash lookup (single query)
2. Checkpoint-based verification (skip if unchanged)
3. Delta verification (only new blocks)

Usage:
    lineage = ServiceRegistry.get(LineageProtocol)
    if lineage.verify_chain_fast():
        # Boot continues instantly
    else:
        # Full verification triggered
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Protocol, TypedDict, runtime_checkable

# =============================================================================
# TYPED DATA STRUCTURES (No Any!)
# =============================================================================


class CheckpointData(TypedDict):
    """
    Checkpoint for fast chain verification.

    Stored in .vibe/lineage_checkpoint.json (PRANA level - can regenerate).
    GAD-000 Principle 6: Don't re-verify validated history.
    """

    verified_tip_hash: str  # SHA-256 of last verified block
    verified_index: int  # Index of last verified block
    verified_at: str  # ISO 8601 timestamp
    chain_db_path: str  # For invalidation if DB moves


class VerificationResult(TypedDict):
    """Result of chain verification."""

    valid: bool  # Chain integrity intact
    method: str  # "checkpoint" | "delta" | "full"
    blocks_verified: int  # Number of blocks actually verified
    duration_ms: float  # Time taken
    tip_hash: str  # Current tip hash
    tip_index: int  # Current tip index


class BlockData(TypedDict):
    """Serialized block data for events."""

    index: int
    timestamp: str
    event_type: str
    agent_id: Optional[str]
    data: Dict[str, str]  # Event-specific (typed as str values)
    previous_hash: str
    hash: str


# =============================================================================
# LINEAGE PROTOCOL
# =============================================================================


@runtime_checkable
class LineageProtocol(Protocol):
    """
    Protocol for Parampara Lineage Chain.

    The sacred blockchain of agent lifecycle events.
    Cryptographically chained, immutable, eternal.

    SPEED.md Optimization:
    - get_tip_hash(): O(1) lookup vs O(n) get_all_blocks()
    - verify_chain_fast(): Checkpoint-based, skips if unchanged
    - verify_delta(): Only verify new blocks since checkpoint
    """

    # =========================================================================
    # FAST QUERIES (SPEED.md)
    # =========================================================================

    def get_tip_hash(self) -> str:
        """
        Get hash of latest block (single query).

        This is O(1) vs O(n) for get_all_blocks().
        Used for checkpoint comparison.

        Returns:
            SHA-256 hash of tip block, or empty string if chain empty
        """
        ...

    def get_tip_index(self) -> int:
        """
        Get index of latest block.

        Returns:
            Index of tip block, or -1 if chain empty
        """
        ...

    # =========================================================================
    # VERIFICATION (SPEED.md)
    # =========================================================================

    def verify_chain_fast(self) -> VerificationResult:
        """
        Fast chain verification with checkpoint support.

        Algorithm:
        1. Load checkpoint from .vibe/lineage_checkpoint.json
        2. Compare checkpoint.tip_hash with current tip hash
        3. If match: Skip verification (instant boot)
        4. If mismatch: Verify only delta (new blocks)
        5. If checkpoint missing: Full verification (fallback)

        Returns:
            VerificationResult with method used and timing
        """
        ...

    def verify_chain(self) -> bool:
        """
        Full chain verification (legacy method).

        Verifies ALL blocks from Genesis to tip.
        Use verify_chain_fast() for boot-time verification.

        Returns:
            True if chain valid, False if broken
        """
        ...

    # =========================================================================
    # CHECKPOINT MANAGEMENT
    # =========================================================================

    def save_checkpoint(self) -> bool:
        """
        Save verification checkpoint.

        Called after successful verification.
        Saves tip hash + index to .vibe/lineage_checkpoint.json

        Returns:
            True if saved successfully
        """
        ...

    def load_checkpoint(self) -> Optional[CheckpointData]:
        """
        Load verification checkpoint.

        Returns:
            CheckpointData if exists and valid, None otherwise
        """
        ...

    def clear_checkpoint(self) -> bool:
        """
        Clear checkpoint (force full verification on next boot).

        Returns:
            True if cleared successfully
        """
        ...

    # =========================================================================
    # STANDARD CHAIN OPERATIONS
    # =========================================================================

    def get_chain_length(self) -> int:
        """Get total number of blocks."""
        ...

    def get_latest_block(self) -> Optional[BlockData]:
        """Get most recent block."""
        ...

    def get_genesis_block(self) -> Optional[BlockData]:
        """Get Genesis block (index 0)."""
        ...

    def add_block(
        self,
        event_type: str,
        agent_id: Optional[str],
        data: Dict[str, str],
    ) -> BlockData:
        """
        Add new block to chain.

        Args:
            event_type: Type of event (AGENT_REGISTERED, etc.)
            agent_id: Agent involved (None for system events)
            data: Event-specific data (typed as Dict[str, str])

        Returns:
            The created block
        """
        ...

    def close(self) -> None:
        """Close database connection."""
        ...


# =============================================================================
# NULL IMPLEMENTATION (Arjuna Pattern)
# =============================================================================


class NullLineageChain:
    """
    Arjuna Pattern: No-op implementation.

    Used during testing or when lineage is disabled.
    All operations succeed silently.
    """

    def get_tip_hash(self) -> str:
        return ""

    def get_tip_index(self) -> int:
        return -1

    def verify_chain_fast(self) -> VerificationResult:
        return VerificationResult(
            valid=True,
            method="null",
            blocks_verified=0,
            duration_ms=0.0,
            tip_hash="",
            tip_index=-1,
        )

    def verify_chain(self) -> bool:
        return True

    def save_checkpoint(self) -> bool:
        return True

    def load_checkpoint(self) -> Optional[CheckpointData]:
        return None

    def clear_checkpoint(self) -> bool:
        return True

    def get_chain_length(self) -> int:
        return 0

    def get_latest_block(self) -> Optional[BlockData]:
        return None

    def get_genesis_block(self) -> Optional[BlockData]:
        return None

    def add_block(
        self,
        event_type: str,
        agent_id: Optional[str],
        data: Dict[str, str],
    ) -> BlockData:
        return BlockData(
            index=0,
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            agent_id=agent_id,
            data=data,
            previous_hash="0" * 64,
            hash="0" * 64,
        )

    def close(self) -> None:
        pass
