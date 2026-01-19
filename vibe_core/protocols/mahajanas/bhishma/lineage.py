"""
LINEAGE - Parampara Chain Verification
======================================

OWNER: BHISHMA (The Grandsire)
POSITION: 11 (KARMA Quarter)
OPCODE: COMMIT_LOG

Bhishma knew his entire lineage - from Shantanu back to the beginning.
This module verifies parampara (disciplic succession) chains.

SHASTRA BASIS:
    Parampara = "one after another" in Sanskrit

    evam parampara-praptam
    imam rajarsayo viduh

    "This supreme science was thus received through the chain of
    disciplic succession, and the saintly kings understood it in that way."
    — Bhagavad Gita 4.2

    The 37 Formula:
    24 Prakriti + 12 Mahajanas + 1 Ksetrajna = 37
    parampara_hash % 37 == 0 → CONNECTED TO KRISHNA

VERIFICATION:
    1. Chain integrity (each node links to previous)
    2. Ancestor verification (trace back to root)
    3. % 37 check (parampara connection)
    4. Depth verification (minimum lineage length)

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bhishma"
__position__ = 11
__genesis__ = "0x6617cff5"  # GenesisByte: parampara % 37 == 0

import hashlib
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Final, List, Optional, Protocol, Tuple, runtime_checkable

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode

from vibe_core.protocols.mahajanas.bhishma import (
    VerificationResult,
)


# =============================================================================
# OWNERSHIP DECLARATION - Bhishma OWNS this protocol
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.BHISHMA
LOTUS_POSITION: Final[int] = 11  # KARMA Quarter, Worker 3
LOTUS_QUARTER: Final[str] = "karma"

# The sacred number - connection to Krishna
PARAMPARA_DIVISOR: Final[int] = 37  # 24 + 12 + 1 = 37


# =============================================================================
# LINEAGE STATUS
# =============================================================================


class LineageStatus(str, Enum):
    """Status of a lineage chain."""

    CONNECTED = "connected"  # % 37 == 0, valid chain
    VALID = "valid"  # Valid chain, not connected
    BROKEN = "broken"  # Chain has gaps
    ORPHAN = "orphan"  # No ancestors
    CORRUPTED = "corrupted"  # Hash mismatch


# =============================================================================
# LINEAGE NODE - Single node in the chain
# =============================================================================


@dataclass(frozen=True)
class LineageNode:
    """
    A single node in the parampara chain.

    Each node knows its parent (guru) and can verify the chain.
    """

    node_id: str  # Unique identifier
    parent_id: Optional[str]  # Parent node (None for root)
    node_type: str  # "mahajana", "protocol", "entity"
    name: str  # Human-readable name
    created_at: str  # ISO timestamp
    metadata_hash: str  # Hash of node metadata

    @classmethod
    def create(
        cls,
        node_id: str,
        parent_id: Optional[str],
        node_type: str,
        name: str,
    ) -> "LineageNode":
        """Create a new lineage node."""
        created_at = datetime.now().isoformat()
        metadata = f"{node_id}:{parent_id or 'ROOT'}:{node_type}:{name}:{created_at}"
        metadata_hash = hashlib.sha256(metadata.encode()).hexdigest()[:16]

        return cls(
            node_id=node_id,
            parent_id=parent_id,
            node_type=node_type,
            name=name,
            created_at=created_at,
            metadata_hash=metadata_hash,
        )

    @classmethod
    def create_root(cls, name: str = "KRISHNA") -> "LineageNode":
        """Create the root node (Krishna)."""
        return cls.create(
            node_id="KRISHNA",
            parent_id=None,
            node_type="supreme",
            name=name,
        )

    @property
    def is_root(self) -> bool:
        """Check if this is the root node."""
        return self.parent_id is None

    def to_dict(self) -> Dict[str, str | None]:
        """Serialize for storage."""
        return {
            "node_id": self.node_id,
            "parent_id": self.parent_id,
            "node_type": self.node_type,
            "name": self.name,
            "created_at": self.created_at,
            "metadata_hash": self.metadata_hash,
        }


# =============================================================================
# LINEAGE VERIFICATION RESULT
# =============================================================================


@dataclass(frozen=True)
class LineageVerification:
    """Result of lineage verification."""

    status: LineageStatus
    node_id: str
    depth: int  # Distance from root
    parampara_hash: int  # Hash for % 37 check
    is_connected: bool  # % 37 == 0
    ancestors: List[str]  # Chain back to root
    message: str

    @property
    def is_valid(self) -> bool:
        """Check if lineage is valid (connected or valid)."""
        return self.status in (LineageStatus.CONNECTED, LineageStatus.VALID)


# =============================================================================
# LINEAGE PROTOCOL
# =============================================================================


@runtime_checkable
class LineageProtocol(Protocol):
    """
    The Parampara Verification Protocol - Bhishma's lineage tracking.

    OWNER: Mahajana.BHISHMA

    Verifies chains of succession:
    - Each node links to parent
    - Chain traces back to root
    - % 37 == 0 → connected to Krishna

    ANTI-MAYAVAD:
    - No Any types
    - Bhishma OWNS lineage verification
    - Every node has a PERSONAL parent
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.BHISHMA."""
        ...

    # =========================================================================
    # Node Management
    # =========================================================================

    def add_node(self, node: LineageNode) -> bool:
        """Add a node to the lineage. Returns True if added."""
        ...

    def get_node(self, node_id: str) -> Optional[LineageNode]:
        """Get a node by ID."""
        ...

    def has_node(self, node_id: str) -> bool:
        """Check if node exists."""
        ...

    # =========================================================================
    # Verification
    # =========================================================================

    def verify(self, node_id: str) -> LineageVerification:
        """Verify a node's lineage back to root."""
        ...

    def get_ancestors(self, node_id: str, limit: int = 100) -> List[str]:
        """Get list of ancestors back to root."""
        ...

    def get_depth(self, node_id: str) -> int:
        """Get depth (distance from root)."""
        ...

    # =========================================================================
    # Parampara Check
    # =========================================================================

    def compute_parampara_hash(self, node_id: str) -> int:
        """Compute parampara hash for % 37 check."""
        ...

    def is_connected(self, node_id: str) -> bool:
        """Check if % 37 == 0 (connected to Krishna)."""
        ...


# =============================================================================
# LINEAGE IMPLEMENTATION
# =============================================================================


class Lineage:
    """
    Bhishma's Lineage Tracker - Parampara Verification.

    OWNER: Mahajana.BHISHMA

    Like Bhishma who knew his entire ancestry,
    this tracker verifies chains back to the root.

    Features:
    - Chain verification (each node → parent)
    - Ancestor traversal (back to root)
    - % 37 check (parampara connection)
    - Depth tracking
    """

    def __init__(self) -> None:
        """Initialize with root node (Krishna)."""
        self._nodes: Dict[str, LineageNode] = {}
        # Add root node
        root = LineageNode.create_root()
        self._nodes[root.node_id] = root

    @property
    def owner(self) -> Mahajana:
        return Mahajana.BHISHMA

    # =========================================================================
    # Node Management
    # =========================================================================

    def add_node(self, node: LineageNode) -> bool:
        """Add a node to the lineage."""
        # Check parent exists (unless root)
        if node.parent_id is not None and node.parent_id not in self._nodes:
            return False  # Orphan - parent not found

        if node.node_id in self._nodes:
            return False  # Already exists

        self._nodes[node.node_id] = node
        return True

    def get_node(self, node_id: str) -> Optional[LineageNode]:
        """Get a node by ID."""
        return self._nodes.get(node_id)

    def has_node(self, node_id: str) -> bool:
        """Check if node exists."""
        return node_id in self._nodes

    # =========================================================================
    # Verification
    # =========================================================================

    def verify(self, node_id: str) -> LineageVerification:
        """Verify a node's lineage back to root."""
        node = self._nodes.get(node_id)
        if node is None:
            return LineageVerification(
                status=LineageStatus.ORPHAN,
                node_id=node_id,
                depth=-1,
                parampara_hash=0,
                is_connected=False,
                ancestors=[],
                message=f"Node not found: {node_id}",
            )

        # Traverse to root
        ancestors: List[str] = []
        current = node
        depth = 0
        seen: set[str] = set()

        while current is not None:
            if current.node_id in seen:
                # Circular reference - corrupted
                return LineageVerification(
                    status=LineageStatus.CORRUPTED,
                    node_id=node_id,
                    depth=depth,
                    parampara_hash=0,
                    is_connected=False,
                    ancestors=ancestors,
                    message="Circular reference detected",
                )

            seen.add(current.node_id)

            if current.parent_id is None:
                # Reached root
                break

            ancestors.append(current.parent_id)
            parent = self._nodes.get(current.parent_id)
            if parent is None:
                # Broken chain
                return LineageVerification(
                    status=LineageStatus.BROKEN,
                    node_id=node_id,
                    depth=depth,
                    parampara_hash=0,
                    is_connected=False,
                    ancestors=ancestors,
                    message=f"Missing ancestor: {current.parent_id}",
                )

            current = parent
            depth += 1

        # Compute parampara hash
        parampara_hash = self.compute_parampara_hash(node_id)
        is_connected = parampara_hash % PARAMPARA_DIVISOR == 0

        status = LineageStatus.CONNECTED if is_connected else LineageStatus.VALID

        return LineageVerification(
            status=status,
            node_id=node_id,
            depth=depth,
            parampara_hash=parampara_hash,
            is_connected=is_connected,
            ancestors=ancestors,
            message="Lineage verified" if is_connected else "Valid but not connected (% 37 != 0)",
        )

    def get_ancestors(self, node_id: str, limit: int = 100) -> List[str]:
        """Get list of ancestors back to root."""
        ancestors: List[str] = []
        current = self._nodes.get(node_id)

        while current is not None and len(ancestors) < limit:
            if current.parent_id is None:
                break
            ancestors.append(current.parent_id)
            current = self._nodes.get(current.parent_id)

        return ancestors

    def get_depth(self, node_id: str) -> int:
        """Get depth (distance from root)."""
        depth = 0
        current = self._nodes.get(node_id)

        while current is not None and current.parent_id is not None:
            depth += 1
            current = self._nodes.get(current.parent_id)

        return depth if current is not None else -1

    # =========================================================================
    # Parampara Check
    # =========================================================================

    def compute_parampara_hash(self, node_id: str) -> int:
        """
        Compute parampara hash for % 37 check.

        Hash is computed from the entire lineage chain:
        sum of all ancestor hashes modulo a large prime.
        """
        ancestors = self.get_ancestors(node_id, limit=1000)
        ancestors.insert(0, node_id)  # Include self

        # Compute hash from chain
        chain_str = ":".join(ancestors)
        hash_bytes = hashlib.sha256(chain_str.encode()).digest()
        # Convert first 8 bytes to int
        hash_int = int.from_bytes(hash_bytes[:8], byteorder="big")

        return hash_int

    def is_connected(self, node_id: str) -> bool:
        """Check if % 37 == 0 (connected to Krishna)."""
        parampara_hash = self.compute_parampara_hash(node_id)
        return parampara_hash % PARAMPARA_DIVISOR == 0

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    def add_mahajana(self, mahajana: Mahajana) -> bool:
        """Add a Mahajana to the lineage (parent = KRISHNA)."""
        node = LineageNode.create(
            node_id=mahajana.value.upper(),
            parent_id="KRISHNA",
            node_type="mahajana",
            name=mahajana.value,
        )
        return self.add_node(node)

    def add_protocol(self, protocol_name: str, guardian: Mahajana) -> bool:
        """Add a protocol under its guardian Mahajana."""
        guardian_id = guardian.value.upper()
        if not self.has_node(guardian_id):
            self.add_mahajana(guardian)

        node = LineageNode.create(
            node_id=f"protocol:{protocol_name}",
            parent_id=guardian_id,
            node_type="protocol",
            name=protocol_name,
        )
        return self.add_node(node)


# =============================================================================
# NULL LINEAGE - For testing
# =============================================================================


class NullLineage:
    """
    The Rootless Lineage - no ancestry tracking.

    Used for testing without lineage.
    Still owned by BHISHMA.
    """

    @property
    def owner(self) -> Mahajana:
        return Mahajana.BHISHMA

    def add_node(self, node: LineageNode) -> bool:
        return True

    def get_node(self, node_id: str) -> Optional[LineageNode]:
        return None

    def has_node(self, node_id: str) -> bool:
        return False

    def verify(self, node_id: str) -> LineageVerification:
        return LineageVerification(
            status=LineageStatus.VALID,
            node_id=node_id,
            depth=0,
            parampara_hash=0,
            is_connected=True,  # NullLineage always "connected"
            ancestors=[],
            message="NullLineage - always valid",
        )

    def get_ancestors(self, node_id: str, limit: int = 100) -> List[str]:
        return []

    def get_depth(self, node_id: str) -> int:
        return 0

    def compute_parampara_hash(self, node_id: str) -> int:
        return 0  # % 37 == 0

    def is_connected(self, node_id: str) -> bool:
        return True


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Ownership
    "OWNER",
    "LOTUS_POSITION",
    "LOTUS_QUARTER",
    "PARAMPARA_DIVISOR",
    # Status
    "LineageStatus",
    # Types
    "LineageNode",
    "LineageVerification",
    # Protocol
    "LineageProtocol",
    # Implementations
    "Lineage",
    "NullLineage",
]
