"""
PARASHURAMA - The 3rd Avatara (Fetch Resources)
===============================================

POSITION: 8 (KARMA Quarter HEAD, FETCH_RES OpCode)

Parashurama - The Warrior Brahmin.
Wielded Parashu (axe), annihilated kshatriyas 21 times.
The immortal warrior who acts without hesitation.

DERIVED FROM MAHAMANTRA:
    Position 8 -> guardian=PARASHURAMA, opcode=FETCH_RES, quarter=KARMA
    All properties derived from truth table. No manual wiring.

HEAD POSITION:
    This is a HEAD (Avatara) position, not a WORKER (Mahajana).
    HEADs are at positions 0, 4, 8, 12 (first of each quarter).
    They initiate action; Workers execute.

DOMAIN:
- Resource Fetching (FETCH_RES)
- External API Calls
- Data Acquisition
- Network Operations
- Swift, Decisive Action

"parasuram ksatriya-dvisam"
"Parashurama, the annihilator of the warrior class."

WATERTIGHT: No Any types. All typed explicitly.
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "parashurama"
__position__ = 8
__genesis__ = "0x56bc0129"  # GenesisByte: parampara % 37 == 0

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

from vibe_core.mahamantra import HeadProtocol, Avatara, MantraOpCode, ProtocolRegistry


# =============================================================================
# PARASHURAMA PROTOCOL BASE - Derives from MantraPosition 8
# =============================================================================

@ProtocolRegistry.register
class ParashuramaProtocolBase(HeadProtocol):
    """
    Parashurama protocol ownership - DERIVED from Mahamantra position 8.

    NO MANUAL WIRING:
        _position_index = 8 is the ONLY configuration.
        Everything else derived from truth table.

    DERIVED PROPERTIES:
        guardian()  -> Avatara.PARASHURAMA
        opcode()    -> MantraOpCode.EXEC_OP
        quarter()   -> Quarter.KARMA
        is_head()   -> True (HEAD position)
        parampara_vector() -> 333 (% 37 == 0)
    """
    _position_index: ClassVar[int] = 8  # THE ONLY CONFIGURATION
    _intents: ClassVar[List[str]] = ["execute", "weapon", "fight", "force", "justice", "action"]


# NO MANUAL WIRING - Everything derived from mahamantra[8]


# =============================================================================
# WATERTIGHT STATE TYPES (No Any!)
# =============================================================================

class FetchStatus(str, Enum):
    """Status of fetch operation."""
    PENDING = "pending"       # Fetch queued
    FETCHING = "fetching"     # In progress
    SUCCESS = "success"       # Fetch completed
    FAILED = "failed"         # Fetch failed
    TIMEOUT = "timeout"       # Fetch timed out
    CACHED = "cached"         # Returned from cache


# Resource value types - WATERTIGHT
ResourceValue = Union[str, bytes, Dict[str, str], List[str]]


class FetchResult(TypedDict, total=False):
    """
    Result of fetch operation.
    WATERTIGHT - no Any!
    """
    success: bool
    status: str               # FetchStatus value
    resource_id: str
    resource_type: str
    size_bytes: int
    timestamp: str            # ISO timestamp
    latency_ms: int
    error_message: str


class FetchState(TypedDict, total=False):
    """
    State of fetch operations.
    WATERTIGHT - no Any!
    """
    total_fetches: int
    successful_fetches: int
    failed_fetches: int
    cache_hits: int
    total_bytes_fetched: int
    avg_latency_ms: int
    last_fetch: str           # ISO timestamp
    health: str               # "pristine", "healthy", "degraded"


class FetchCliResult(TypedDict):
    """Result of CLI fetch operation. WATERTIGHT - no Any!"""
    success: bool
    resource_id: str
    status: str
    latency_ms: int


# =============================================================================
# PARASHURAMA PROTOCOL
# =============================================================================


@runtime_checkable
class ParashuramaProtocol(Protocol):
    """
    The Resource Fetch Protocol - Parashurama's domain.

    DERIVED: Position 8 -> PARASHURAMA, FETCH_RES, KARMA
    WATERTIGHT - no Any types!

    As Parashurama acts swiftly and decisively,
    this protocol fetches resources with precision.
    """

    @classmethod
    def position_index(cls) -> int:
        """Position 8 in the Mahamantra."""
        ...

    def fetch(self, resource_id: str, timeout_ms: int = 5000) -> FetchResult:
        """FETCH_RES: Fetch a resource by ID."""
        ...

    def fetch_batch(self, resource_ids: List[str]) -> List[FetchResult]:
        """Fetch multiple resources in batch."""
        ...

    def get_resource(self, resource_id: str) -> Optional[ResourceValue]:
        """Get a fetched resource value."""
        ...

    def is_available(self, resource_id: str) -> bool:
        """Check if a resource is available."""
        ...

    def prefetch(self, resource_ids: List[str]) -> int:
        """Prefetch resources. Returns count queued."""
        ...

    def invalidate(self, resource_id: str) -> bool:
        """Invalidate cached resource. Returns True if existed."""
        ...

    def get_status(self, resource_id: str) -> FetchStatus:
        """Get fetch status of a resource."""
        ...

    def get_state(self) -> FetchState:
        """Get fetch state. WATERTIGHT."""
        ...


# =============================================================================
# NULL PARASHURAMA (For testing)
# =============================================================================


class NullParashurama(ParashuramaProtocolBase):
    """
    The Idle Warrior.
    No real fetching (for testing without network).

    Inherits from ParashuramaProtocolBase -> position 8 -> PARASHURAMA.
    """

    def fetch(self, resource_id: str, timeout_ms: int = 5000) -> FetchResult:
        return FetchResult(
            success=True,
            status=FetchStatus.SUCCESS.value,
            resource_id=resource_id,
            resource_type="null",
            size_bytes=0,
            timestamp=datetime.now().isoformat(),
            latency_ms=0,
        )

    def fetch_batch(self, resource_ids: List[str]) -> List[FetchResult]:
        return [self.fetch(rid) for rid in resource_ids]

    def get_resource(self, resource_id: str) -> Optional[ResourceValue]:
        return None

    def is_available(self, resource_id: str) -> bool:
        return False

    def prefetch(self, resource_ids: List[str]) -> int:
        return 0

    def invalidate(self, resource_id: str) -> bool:
        return False

    def get_status(self, resource_id: str) -> FetchStatus:
        return FetchStatus.PENDING

    def get_state(self) -> FetchState:
        return FetchState(
            total_fetches=0,
            successful_fetches=0,
            failed_fetches=0,
            cache_hits=0,
            total_bytes_fetched=0,
            avg_latency_ms=0,
            health="pristine",
        )

    def fetch_cli(self, resource_id: str = "default") -> FetchCliResult:
        """CLI: Fetch a resource. WATERTIGHT."""
        result = self.fetch(resource_id)
        return FetchCliResult(
            success=result.get("success", True),
            resource_id=resource_id,
            status=result.get("status", "success"),
            latency_ms=result.get("latency_ms", 0),
        )


# =============================================================================
# EXPORTS
# =============================================================================

# =============================================================================
# PARASHURAMA SERVICE - The Real Implementation (wraps legacy semantic_syscalls.py)
# =============================================================================

from vibe_core.protocols.mahajanas.parashurama.service import ParashuramaService

# =============================================================================
# MIGRATED TYPES - Accessed via mahamantra.mod.parashurama
# =============================================================================

from vibe_core.protocols.mahajanas.parashurama.types import (
    # network_proxy.py
    KernelNetworkProxy,
    # vfs.py
    VirtualFileSystem,
    # io_service.py
    DocumentType,
    WriteResult,
    KernelIOService,
    # file_operator.py
    FileBasedOperator,
)

__all__ = [
    # Protocol Base (HeadProtocol derivative) - THE ONLY SOURCE
    "ParashuramaProtocolBase",
    # State Types (WATERTIGHT)
    "FetchStatus",
    "ResourceValue",
    "FetchResult",
    "FetchState",
    "FetchCliResult",
    # Protocol
    "ParashuramaProtocol",
    # Implementations
    "NullParashurama",
    # Service (Real Implementation)
    "ParashuramaService",
    # === MIGRATED TYPES (mahamantra.mod.parashurama) ===
    # network_proxy.py
    "KernelNetworkProxy",
    # vfs.py
    "VirtualFileSystem",
    # io_service.py
    "DocumentType",
    "WriteResult",
    "KernelIOService",
    # file_operator.py
    "FileBasedOperator",
]
