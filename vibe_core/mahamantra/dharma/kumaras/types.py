"""
KUMARAS TYPES - Shared Purity Definitions
=========================================

Shared types for Kumaras Protocol and Validation.
"""

from enum import Enum
from typing import Dict, List, TypedDict, Union

# =============================================================================
# WATERTIGHT STATE TYPES (No Any!)
# =============================================================================

PurifiableData = Union[str, int, float, bool, Dict[str, str], List[str], bytes]


class PurityLevel(str, Enum):
    """Levels of purity."""

    PRISTINE = "pristine"
    CLEAN = "clean"
    TAINTED = "tainted"
    CORRUPTED = "corrupted"
    MAYAVAD = "mayavad"


class PurificationResult(TypedDict, total=False):
    success: bool
    input_type: str
    output_type: str
    impurities_removed: int
    purity_level: str
    error_message: str


class ResetResult(TypedDict, total=False):
    success: bool
    previous_state_hash: str
    new_state_hash: str
    timestamp: str
    error_message: str


class PurityState(TypedDict, total=False):
    is_pure: bool
    purity_level: str
    total_purifications: int
    total_resets: int
    last_purification: str
    health: str


class PurifyCliResult(TypedDict):
    success: bool
    is_pure: bool
    purity_level: str
    health: str
