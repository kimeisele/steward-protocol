"""
SESHA PROTOCOL - The Infinite Bed (Layer 0.8)

"Ananta Sesha" - The Endless One. The Bed of Vishnu.
He holds the state (Storage) but refuses corruption.

Responsibilities:
1. STORE: Persist data (Thread-safe).
2. RECALL: Retrieve data.
3. UNSHAKABLE: Verify integrity via Vasuki before accepting burden.

INHERITANCE:
- Inherits from NagaBase (Devotee).
- Protected by Balarama (Shield).

STATUS: DEVOTEE / ACTIVE STORAGE
"""

import threading
from typing import Any, Dict, Optional, Tuple, TypedDict, List

from vibe_core.protocols.naga.base import NagaBase

# Re-export types
from vibe_core.protocols.naga.types import NagaStatus, NagaType
from vibe_core.protocols.naga.vasuki import IntegrityError, Vasuki

SESHA_CAPS = ("store", "recall", "persist")


class SyncStatus(TypedDict):
    """Status of synchronization."""
    synced: bool
    last_block: int
    pending_blocks: int


class SyncRequest(TypedDict):
    """Request to sync ledger."""
    start_block: int
    max_blocks: int


class LedgerBlock(TypedDict):
    """A block in the ledger."""
    index: int
    timestamp: str
    events: List[Dict[str, Any]]
    hash: str
    prev_hash: str


class ImportResult(TypedDict):
    """Result of importing a block."""
    success: bool
    blocks_imported: int
    error: Optional[str]


class Sesha(NagaBase):
    """
    The Sesha Service (Storage Engine).

    A Devotee Naga that:
    - Holds the Universe (Data).
    - Uses Locks (Stability).
    - Demands Purity (Vasuki Verification).
    """

    def __init__(self, vasuki: Vasuki):
        """
        Initialize Sesha.

        Args:
            vasuki: The Binding Rope (Required for verification).
        """
        super().__init__(name="sesha", capabilities=SESHA_CAPS)
        self._vasuki = vasuki
        self._store: Dict[str, Any] = {}
        self._lock = threading.RLock()  # Reentrant Lock for stability

    # =========================================================================
    # GENERIC SERVICE (SEVA)
    # =========================================================================

    def serve(self, request: Any) -> Any:
        """Generic entry point."""
        if not isinstance(request, dict):
            return "UNKNOWN REQUEST"

        action = request.get("action")
        key = request.get("key")
        value = request.get("value")
        signature = request.get("signature")

        if action == "store":
            return self.store(key, value, signature)
        elif action == "recall":
            return self.recall(key)

        return "UNKNOWN ACTION"

    # =========================================================================
    # CAPABILITY 1: STORE (THE BURDEN)
    # =========================================================================

    def store(self, key: str, value: Any, signature: str) -> bool:
        """
        Store data on the Infinite Bed.

        CONSTRAINT:
        Sesha REFUSES to hold unsigned/corrupted data.
        He consults Vasuki first.
        """
        # 1. Verify Purity (Integrity Check)
        try:
            self._vasuki.verify_data(value, signature)
        except IntegrityError:
            # Sesha rejects the burden
            return False

        # 2. Accept Burden (Thread-safe Write)
        with self._lock:
            self._store[key] = value

        return True

    # =========================================================================
    # CAPABILITY 2: RECALL (THE MEMORY)
    # =========================================================================

    def recall(self, key: str) -> Optional[Any]:
        """Retrieve data from the Infinite Bed."""
        with self._lock:
            return self._store.get(key)

    # =========================================================================
    # STATE MANAGEMENT
    # =========================================================================

    def get_stats(self) -> Dict[str, int]:
        """Report load."""
        with self._lock:
            return {"items": len(self._store), "bytes_approx": len(str(self._store))}


# =============================================================================
# NULL IMPLEMENTATION (The Silent Witness)
# =============================================================================


class NullSesha:
    """
    The Void Beneath.
    Accepts all history, remembers nothing.
    Used for stateless testing.
    """

    def record_event(self, event_type: str, data: Any, signature: str = "") -> str:
        return "0x00_NULL_EVENT_HASH"  # Akarma

    def store(self, key: str, value: Any, signature: str) -> bool:
        return True  # Accept without storing

    def recall(self, key: str) -> Optional[Any]:
        return None  # Only Silence

    def get_stats(self) -> Dict[str, int]:
        return {"items": 0, "bytes_approx": 0}

    def get_top_hash(self) -> str:
        return ""

    def serve(self, request: Any) -> Any:
        return "NULL_SESHA_RESPONSE"


SeshaProtocol = Sesha
