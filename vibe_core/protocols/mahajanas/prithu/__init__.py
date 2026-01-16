"""
PRITHU - The 2nd Avatara (Assert Truth)
======================================

POSITION: 4 (DHARMA Quarter HEAD, ASSERT_TRUTH OpCode)

King Prithu - The Protector of Dharma.
Verifies the Truth and Upholds the Law (Dharma).
The Sovereign who ensures the integrity of the realm.

DERIVED FROM MAHAMANTRA:
    Position 4 -> guardian=PRITHU, opcode=ASSERT_TRUTH, quarter=DHARMA
    All properties derived from truth table. No manual wiring.

HEAD POSITION:
    This is a HEAD (Avatara) position, not a WORKER (Mahajana).
    HEADs are at positions 0, 4, 8, 12 (first of each quarter).
    They initiate action; Workers execute.

DOMAIN:
- Truth Verification (Checking Compliance)
- Schema Validation (The Law)
- Dharma Enforcement (Ruling)
- Knowledge Protection

WATERTIGHT: No Any types. All typed explicitly.
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 4
__genesis__ = "0x94644443"  # GenesisByte: parampara % 37 == 0

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
    runtime_checkable,
)

from vibe_core.mahamantra import HeadProtocol, Avatara, MantraOpCode, ProtocolRegistry


# =============================================================================
# PRITHU PROTOCOL BASE - Derives from MantraPosition 4
# =============================================================================

@ProtocolRegistry.register
class PrithuProtocolBase(HeadProtocol):
    """
    Prithu protocol ownership - DERIVED from Mahamantra position 4.

    NO MANUAL WIRING:
        _position_index = 4 is the ONLY configuration.
        Everything else derived from truth table.

    DERIVED PROPERTIES:
        guardian()  -> Avatara.PRITHU
        opcode()    -> MantraOpCode.COMPILE_AST
        quarter()   -> Quarter.DHARMA
        is_head()   -> True (HEAD position)
        parampara_vector() -> 185 (% 37 == 0)
    """
    _position_index: ClassVar[int] = 4  # THE ONLY CONFIGURATION


# NO MANUAL WIRING - Everything derived from mahamantra[4]


# =============================================================================
# WATERTIGHT STATE TYPES (No Any!)
# =============================================================================

class TruthLevel(str, Enum):
    """Levels of truth assertion."""
    ABSOLUTE = "absolute"     # Vedic truth - cannot be questioned
    VERIFIED = "verified"     # Verified against schema
    ASSERTED = "asserted"     # Asserted but not verified
    DISPUTED = "disputed"     # Multiple conflicting claims
    FALSE = "false"           # Proven false


class AssertionResult(TypedDict, total=False):
    """
    Result of truth assertion.
    WATERTIGHT - no Any!
    """
    valid: bool
    truth_level: str          # TruthLevel value
    timestamp: str            # ISO timestamp
    assertion_id: str
    violations: List[str]
    error_message: str


class TruthState(TypedDict, total=False):
    """
    State of truth assertions.
    WATERTIGHT - no Any!
    """
    total_assertions: int
    valid_assertions: int
    invalid_assertions: int
    last_assertion: str       # ISO timestamp
    truth_coverage: float     # 0.0-1.0
    health: str               # "pristine", "healthy", "degraded"


class AssertCliResult(TypedDict):
    """Result of CLI assert operation. WATERTIGHT - no Any!"""
    success: bool
    claim: str
    truth_level: str
    health: str


# =============================================================================
# PRITHU PROTOCOL
# =============================================================================


@runtime_checkable
class PrithuProtocol(Protocol):
    """
    The Truth Assertion Protocol - Prithu's domain.

    DERIVED: Position 4 -> PRITHU, ASSERT_TRUTH, DHARMA
    WATERTIGHT - no Any types!

    As Prithu compiled and divided Vedic knowledge,
    this protocol asserts and validates truth.
    """

    @classmethod
    def position_index(cls) -> int:
        """Position 4 in the Mahamantra."""
        ...

    def assert_truth(self, claim: str, evidence: str) -> AssertionResult:
        """ASSERT_TRUTH: Assert a truth claim with evidence."""
        ...

    def verify(self, assertion_id: str) -> AssertionResult:
        """Verify a previous assertion."""
        ...

    def compile(self, truths: List[str]) -> str:
        """Compile multiple truths (like Prithu compiled Vedas). Returns compilation ID."""
        ...

    def divide(self, compilation_id: str) -> List[str]:
        """Divide compiled truths (like Prithu divided Vedas). Returns parts."""
        ...

    def get_truth_level(self, assertion_id: str) -> TruthLevel:
        """Get the truth level of an assertion."""
        ...

    def challenge(self, assertion_id: str, counter_evidence: str) -> AssertionResult:
        """Challenge an existing assertion with counter-evidence."""
        ...

    def get_state(self) -> TruthState:
        """Get truth assertion state. WATERTIGHT."""
        ...


# =============================================================================
# NULL PRITHU (For testing)
# =============================================================================


class NullPrithu(PrithuProtocolBase):
    """
    The Unverified.
    Accepts all truths without verification (for testing).

    Inherits from PrithuProtocolBase -> position 4 -> PRITHU.
    """

    def assert_truth(self, claim: str, evidence: str) -> AssertionResult:
        return AssertionResult(
            valid=True,
            truth_level=TruthLevel.ASSERTED.value,
            timestamp=datetime.now().isoformat(),
            assertion_id="null_assertion",
            violations=[],
        )

    def verify(self, assertion_id: str) -> AssertionResult:
        return AssertionResult(
            valid=True,
            truth_level=TruthLevel.VERIFIED.value,
            timestamp=datetime.now().isoformat(),
            assertion_id=assertion_id,
            violations=[],
        )

    def compile(self, truths: List[str]) -> str:
        return "null_compilation"

    def divide(self, compilation_id: str) -> List[str]:
        return []

    def get_truth_level(self, assertion_id: str) -> TruthLevel:
        return TruthLevel.ASSERTED

    def challenge(self, assertion_id: str, counter_evidence: str) -> AssertionResult:
        return AssertionResult(
            valid=True,  # Challenge always accepted in null mode
            truth_level=TruthLevel.DISPUTED.value,
            timestamp=datetime.now().isoformat(),
            assertion_id=assertion_id,
        )

    def get_state(self) -> TruthState:
        return TruthState(
            total_assertions=0,
            valid_assertions=0,
            invalid_assertions=0,
            truth_coverage=1.0,
            health="pristine",
        )

    def assert_cli(self, claim: str = "truth") -> AssertCliResult:
        """CLI: Assert a truth claim. WATERTIGHT."""
        result = self.assert_truth(claim, "cli_evidence")
        state = self.get_state()
        return AssertCliResult(
            success=result.get("valid", True),
            claim=claim,
            truth_level=result.get("truth_level", "asserted"),
            health=state.get("health", "pristine"),
        )


# =============================================================================
# EXPORTS
# =============================================================================

# =============================================================================
# PRITHU SERVICE - The Real Implementation (wraps legacy compliance/auditor)
# =============================================================================

from vibe_core.protocols.mahajanas.prithu.service import PrithuService

# =============================================================================
# MIGRATED TYPES - Accessed via mahamantra.mod.prithu
# =============================================================================

from vibe_core.protocols.mahajanas.prithu.types import (
    # errors.py
    ErrorCategory,
    ErrorCode,
    StructuredError,
    # lineage.py (lazy loaded)
    LineageBlock,
    LineageChain,
    LineageEventType,
    # ledger.py (lazy loaded)
    InMemoryLedger,
    SQLiteLedger,
    ArchiveAttachment,
)

# =============================================================================
# KNOWLEDGE GRAPH PROTOCOL - Universal Knowledge Interface
# =============================================================================

from vibe_core.protocols.mahajanas.prithu.knowledge import (
    KnowledgeGraphProtocolBase,
    KnowledgeGraphProtocol,
    NullKnowledgeGraph,
    NodeType as KGNodeType,
    RelationType as KGRelationType,
    ViolationNode,
)

__all__ = [
    # Protocol Base (HeadProtocol derivative) - THE ONLY SOURCE
    "PrithuProtocolBase",
    # State Types (WATERTIGHT)
    "TruthLevel",
    "AssertionResult",
    "TruthState",
    "AssertCliResult",
    # Protocol
    "PrithuProtocol",
    # Implementations
    "NullPrithu",
    # Service (Real Implementation)
    "PrithuService",
    # === MIGRATED TYPES (mahamantra.mod.prithu) ===
    # errors.py
    "ErrorCategory",
    "ErrorCode",
    "StructuredError",
    # lineage.py
    "LineageBlock",
    "LineageChain",
    "LineageEventType",
    # ledger.py
    "InMemoryLedger",
    "SQLiteLedger",
    "ArchiveAttachment",
    # === KNOWLEDGE GRAPH PROTOCOL ===
    "KnowledgeGraphProtocolBase",
    "KnowledgeGraphProtocol",
    "NullKnowledgeGraph",
    "KGNodeType",
    "KGRelationType",
    "ViolationNode",
]
