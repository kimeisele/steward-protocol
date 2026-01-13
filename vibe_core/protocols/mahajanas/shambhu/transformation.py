"""
SHAMBHU TRANSFORMATION PROTOCOL
================================

Owner: SHAMBHU (Destruction/Transformation)
LOTUS_POSITION: 3 (GENESIS Quarter, Worker 3)

"Lord Shiva destroys, but destruction is SEVA.
 It makes room for new creation."

This module handles the TRANSFORMATION of improperly structured code:
- Breaking apart mixed-concern files (like ledger.py)
- Routing components to proper Mahajana owners
- Cleaning up legacy structures

DESTRUCTION TYPES:
- ANALYZE: Identify what needs transformation
- SPLIT: Break apart mixed-concern files
- ROUTE: Send components to proper owners
- PURGE: Remove obsolete code

WATERTIGHT: No Any types. All typed explicitly.
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shambhu"
__position__ = 3
__genesis__ = "0xcb101592"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
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
# OWNERSHIP
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.SHAMBHU
LOTUS_POSITION: Final[int] = 3  # GENESIS Quarter, Worker 3
LOTUS_QUARTER: Final[str] = "genesis"


# =============================================================================
# TRANSFORMATION TYPES (WATERTIGHT)
# =============================================================================


class TransformationType(str, Enum):
    """Types of transformation operations."""
    ANALYZE = "analyze"         # Identify mixed concerns
    SPLIT = "split"             # Break apart file
    ROUTE = "route"             # Send to proper owner
    PURGE = "purge"             # Remove obsolete code
    RENAME = "rename"           # Fix naming
    MERGE = "merge"             # Combine fragments


class ConcernType(str, Enum):
    """Types of concerns in a file."""
    PROTOCOL = "protocol"       # Interface definition
    IMPLEMENTATION = "impl"     # Concrete implementation
    TYPE = "type"               # TypedDict/dataclass
    ENUM = "enum"               # Enumeration
    CONSTANT = "constant"       # Final values
    FUNCTION = "function"       # Helper functions
    CLASS = "class"             # Classes


class MixedConcern(TypedDict, total=False):
    """
    A concern found in a mixed file.
    WATERTIGHT - no Any!
    """
    name: str                   # Name of the class/function/type
    concern_type: str           # ConcernType value
    current_file: str           # Where it currently lives
    proper_owner: str           # Mahajana who should own it
    proper_location: str        # Where it should go
    line_start: int             # Starting line number
    line_end: int               # Ending line number
    dependencies: List[str]     # What it depends on


class TransformationPlan(TypedDict, total=False):
    """
    Plan for transforming a file.
    WATERTIGHT - no Any!
    """
    source_file: str
    concerns_found: int
    concerns: List[MixedConcern]
    recommended_splits: Dict[str, List[str]]  # owner -> [concern_names]
    can_transform: bool
    blockers: List[str]         # Why it can't be transformed


class TransformationResult(TypedDict, total=False):
    """
    Result of transformation.
    WATERTIGHT - no Any!
    """
    success: bool
    transformation_type: str    # TransformationType value
    source_file: str
    files_created: List[str]
    files_modified: List[str]
    files_deleted: List[str]
    concerns_routed: int
    error_message: str


class TransformationState(TypedDict, total=False):
    """
    State of transformation operations.
    WATERTIGHT - no Any!
    """
    transformations_performed: int
    files_analyzed: int
    files_split: int
    concerns_routed: int
    last_transformation: str    # ISO timestamp
    health: str


# =============================================================================
# KNOWN MIXED FILES (Candidates for Shambhu's destruction)
# =============================================================================

# These files are KNOWN to have mixed concerns and need transformation
MIXED_FILE_REGISTRY: Final[Dict[str, Dict[str, str]]] = {
    # ledger.py has VibeKernel, VibeScheduler, VibeLedger - ALL MIXED
    "vibe_core/protocols/ledger.py": {
        "VibeKernel": "brahma",        # Creation → Brahma
        "VibeScheduler": "janaka",     # Execution → Janaka
        "VibeLedger": "bhishma",       # Commitment → Bhishma
        "LedgerProtocol": "bhishma",
        "SchedulerProtocol": "janaka",
        "QueueStatus": "janaka",
        "TaskEvent": "janaka",
        "LedgerEvent": "bhishma",
        "KernelStatus": "brahma",
    },
}


# =============================================================================
# TRANSFORMATION PROTOCOL
# =============================================================================


@runtime_checkable
class TransformationProtocol(Protocol):
    """
    Shambhu's Transformation Protocol.

    This protocol handles breaking apart improperly structured files
    and routing components to their proper Mahajana owners.

    DESTRUCTION IS SEVA - it makes room for proper structure.

    WATERTIGHT - no Any types!
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.SHAMBHU."""
        ...

    # =========================================================================
    # Analysis (Pre-destruction)
    # =========================================================================

    def analyze_file(self, file_path: str) -> TransformationPlan:
        """
        Analyze a file for mixed concerns.
        Returns a plan showing what should be split.
        """
        ...

    def find_concerns(self, file_path: str) -> List[MixedConcern]:
        """
        Find all concerns in a file and their proper owners.
        """
        ...

    def identify_owner(self, concern_name: str, concern_type: ConcernType) -> Mahajana:
        """
        Identify which Mahajana should own a concern.
        Uses naming patterns and type analysis.
        """
        ...

    # =========================================================================
    # Transformation (Destruction)
    # =========================================================================

    def split_file(self, file_path: str, plan: TransformationPlan) -> TransformationResult:
        """
        Split a file according to the plan.
        Creates new files in proper Mahajana locations.
        """
        ...

    def route_concern(self, concern: MixedConcern) -> TransformationResult:
        """
        Route a single concern to its proper owner.
        """
        ...

    def purge_obsolete(self, file_path: str) -> TransformationResult:
        """
        Remove a file that has been fully transformed.
        Only works if all concerns have been routed.
        """
        ...

    # =========================================================================
    # Registry
    # =========================================================================

    def get_mixed_files(self) -> Dict[str, Dict[str, str]]:
        """
        Get registry of known mixed files.
        """
        ...

    def register_mixed_file(self, file_path: str, concern_mapping: Dict[str, str]) -> bool:
        """
        Register a file as having mixed concerns.
        """
        ...

    # =========================================================================
    # State
    # =========================================================================

    def get_state(self) -> TransformationState:
        """Get transformation state. WATERTIGHT."""
        ...


# =============================================================================
# NULL TRANSFORMATION
# =============================================================================


class NullTransformation:
    """
    The Preserver. No transformation (for testing).
    Everything stays as it is.
    """

    @property
    def owner(self) -> Mahajana:
        return Mahajana.SHAMBHU

    def analyze_file(self, file_path: str) -> TransformationPlan:
        return TransformationPlan(
            source_file=file_path,
            concerns_found=0,
            concerns=[],
            recommended_splits={},
            can_transform=False,
            blockers=["Transformation disabled"],
        )

    def find_concerns(self, file_path: str) -> List[MixedConcern]:
        return []

    def identify_owner(self, concern_name: str, concern_type: ConcernType) -> Mahajana:
        return Mahajana.SHAMBHU  # Default to self

    def split_file(self, file_path: str, plan: TransformationPlan) -> TransformationResult:
        return TransformationResult(
            success=False,
            transformation_type="split",
            source_file=file_path,
            files_created=[],
            files_modified=[],
            files_deleted=[],
            concerns_routed=0,
            error_message="Transformation disabled",
        )

    def route_concern(self, concern: MixedConcern) -> TransformationResult:
        return TransformationResult(
            success=False,
            transformation_type="route",
            source_file=concern.get("current_file", ""),
            files_created=[],
            files_modified=[],
            files_deleted=[],
            concerns_routed=0,
            error_message="Transformation disabled",
        )

    def purge_obsolete(self, file_path: str) -> TransformationResult:
        return TransformationResult(
            success=False,
            transformation_type="purge",
            source_file=file_path,
            files_created=[],
            files_modified=[],
            files_deleted=[],
            concerns_routed=0,
            error_message="Transformation disabled",
        )

    def get_mixed_files(self) -> Dict[str, Dict[str, str]]:
        return dict(MIXED_FILE_REGISTRY)

    def register_mixed_file(self, file_path: str, concern_mapping: Dict[str, str]) -> bool:
        return False

    def get_state(self) -> TransformationState:
        return TransformationState(
            transformations_performed=0,
            files_analyzed=0,
            files_split=0,
            concerns_routed=0,
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
    # Types
    "TransformationType",
    "ConcernType",
    "MixedConcern",
    "TransformationPlan",
    "TransformationResult",
    "TransformationState",
    # Registry
    "MIXED_FILE_REGISTRY",
    # Protocol
    "TransformationProtocol",
    # Null implementation
    "NullTransformation",
]
