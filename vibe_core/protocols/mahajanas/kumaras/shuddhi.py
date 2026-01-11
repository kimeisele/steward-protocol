"""
SHUDDHI - The Surgical Self-Healing Protocol
=============================================

POSITION: 5 (KUMARAS, DHARMA Quarter, RESOLVE_REQ)

Shuddhi (Sanskrit: 'Purification') is the core service for surgical
code transformations using Concrete Syntax Trees (CST).

DERIVED FROM MAHAMANTRA:
    Position 5 → guardian=KUMARAS, opcode=RESOLVE_REQ, quarter=DHARMA
    All properties derived from truth table. No manual wiring.

ANTI-MAYAVAD:
    - No Any types (that's spiritual pollution!)
    - All types explicit and WATERTIGHT
    - The protocol IS the purification, not a wrapper

ORIGINAL: protocols/shuddhi.py
MIGRATED: protocols/mahajanas/kumaras/shuddhi.py
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import ClassVar, List, Optional, Protocol, runtime_checkable

from vibe_core.mahamantra import WorkerProtocol, Mahajana, MantraOpCode


# =============================================================================
# SHUDDHI PROTOCOL BASE - Derives from MantraPosition 5
# =============================================================================

class ShuddhiProtocolBase(WorkerProtocol):
    """
    Shuddhi protocol ownership - DERIVED from Mahamantra position 5.

    NO MANUAL WIRING:
        _position_index = 5 is the ONLY configuration.
        Everything else derived from truth table.

    DERIVED PROPERTIES:
        guardian()  → Mahajana.KUMARAS
        opcode()    → MantraOpCode.RESOLVE_REQ
        quarter()   → Quarter.DHARMA
        is_head()   → False (Worker position)
        parampara_vector() → 222 (% 37 == 0)
    """
    _position_index: ClassVar[int] = 5  # THE ONLY CONFIGURATION


# =============================================================================
# BACKWARD COMPATIBILITY - Derived from ShuddhiProtocolBase
# =============================================================================

# These are DERIVED, not hardcoded
OWNER = ShuddhiProtocolBase.mahajana()
LOTUS_POSITION = ShuddhiProtocolBase.lotus_position()
LOTUS_QUARTER = ShuddhiProtocolBase.lotus_quarter()
OWNED_OPCODES: List[MantraOpCode] = [ShuddhiProtocolBase.opcode()]


# =============================================================================
# SHUDDHI STATUS - The state of purification
# =============================================================================

class ShuddhiStatus(str, Enum):
    """The state of a purification attempt."""

    PURIFIED = "purified"        # Transformation successful and verified
    SKIPPED = "skipped"          # No violation found in the file
    FAILED = "failed"            # Error during transformation or verification
    OUT_OF_SCOPE = "out_of_scope"  # Heuristic: Required context missing


# =============================================================================
# SHUDDHI RESULT - WATERTIGHT (no Any!)
# =============================================================================

@dataclass
class ShuddhiResult:
    """The outcome of a Shuddhi operation. WATERTIGHT."""

    status: ShuddhiStatus
    file_path: Path
    rule_id: str
    message: str = ""
    diff: str = ""
    purified_code: Optional[str] = None

    # DERIVED FROM MAHAMANTRA (not hardcoded)
    @property
    def owner(self) -> Mahajana:
        """Owner derived from ShuddhiProtocolBase."""
        return ShuddhiProtocolBase.mahajana()

    @property
    def lotus_position(self) -> int:
        """Position derived from ShuddhiProtocolBase."""
        return ShuddhiProtocolBase.lotus_position()

    @property
    def success(self) -> bool:
        """True if the file is clean (either purified or already clean)."""
        return self.status in (ShuddhiStatus.PURIFIED, ShuddhiStatus.SKIPPED)

    @property
    def is_kumaras_blessed(self) -> bool:
        """True if Kumaras have blessed this purification."""
        return self.owner == Mahajana.KUMARAS and self.success

    @property
    def parampara_vector(self) -> int:
        """Parampara connection vector (always % 37 == 0)."""
        return ShuddhiProtocolBase.parampara_vector()


# =============================================================================
# SHUDDHI PROTOCOL - The surgical self-healing interface
# =============================================================================

@runtime_checkable
class ShuddhiProtocol(Protocol):
    """
    The surgical self-healing interface of the Kernel.

    DERIVED: Position 5 → KUMARAS, RESOLVE_REQ, DHARMA

    Dharma: Shuddhi does not 'replace text'. It performs structural surgery
    on the Concrete Syntax Tree, preserving comments and formatting.

    ANTI-MAYAVAD:
    - No Any types in parameters or returns
    - All operations are PERSONAL (Kumaras do the work)
    - The protocol IS the purification, not mere text replacement
    """

    @classmethod
    def position_index(cls) -> int:
        """Position 5 in the Mahamantra."""
        ...

    def purify(self, file_path: Path, rule_id: str) -> ShuddhiResult:
        """
        Heals a specific structural violation in a file.

        This is KUMARAS' primary operation:
        - CST surgery, not text replacement
        - Preserves comments and formatting
        - Returns ShuddhiResult (WATERTIGHT)

        Args:
            file_path: Path to the target file.
            rule_id: The ID of the violation (e.g., 'unsafe_io_write').

        Returns:
            ShuddhiResult indicating the outcome of the surgery.
        """
        ...

    def list_remedies(self) -> List[str]:
        """Returns list of registered remedy rule_ids."""
        ...

    def can_heal(self, rule_id: str) -> bool:
        """Returns True if a remedy is registered for this rule_id."""
        ...


# =============================================================================
# REMEDY PROTOCOL - Individual healing operations
# =============================================================================

@runtime_checkable
class RemedyProtocol(Protocol):
    """
    The contract for individual Shuddhi remedies.

    OWNER: Inherits from ShuddhiProtocol → Mahajana.KUMARAS

    Each remedy heals a specific violation type identified by rule_id.
    The rule_id MUST match an entry in standards.yaml with has_sattva_remedy: true.

    VEDA-4 Pattern:
        SHABDA   → rule_id (what violation this heals)
        ARTHA    → requirements (what the remedy needs)
        PRATYAYA → applied/violation_found (state tracking)
        KARMA    → CST transformation (the healing action)
    """

    @property
    def rule_id(self) -> str:
        """
        The rule this remedy heals.

        MUST match an id in standards.yaml with has_sattva_remedy: true.
        """
        ...

    @property
    def applied(self) -> bool:
        """True if the remedy made any changes."""
        ...

    @property
    def violation_found(self) -> bool:
        """True if a violation was detected (may not be healable)."""
        ...

    def requirements(self) -> List[str]:
        """
        List of required imports or interfaces.

        Example: ['vibe_core.di.ServiceRegistry', 'self.system']
        """
        ...

    def get_diff(self, old_code: str, new_code: str) -> str:
        """Generates a unified diff for the change."""
        ...


# =============================================================================
# NULL SHUDDHI - Already pure (for testing)
# =============================================================================

class NullShuddhi(ShuddhiProtocolBase):
    """
    The Already Pure Shuddhi - no purification needed.

    Used for testing and for code that is already pure.
    Inherits from ShuddhiProtocolBase → position 5 → KUMARAS.
    """

    def purify(self, file_path: Path, rule_id: str) -> ShuddhiResult:
        """No purification needed - already pure."""
        return ShuddhiResult(
            status=ShuddhiStatus.SKIPPED,
            file_path=file_path,
            rule_id=rule_id,
            message="Already pure (NullShuddhi)",
        )

    def list_remedies(self) -> List[str]:
        return []

    def can_heal(self, rule_id: str) -> bool:
        return True  # Everything is already healed


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Protocol Base (MantraProtocol derivative)
    "ShuddhiProtocolBase",
    # Backward compat (derived from base)
    "OWNER",
    "LOTUS_POSITION",
    "LOTUS_QUARTER",
    "OWNED_OPCODES",
    # Status
    "ShuddhiStatus",
    # Result (WATERTIGHT)
    "ShuddhiResult",
    # Protocols
    "ShuddhiProtocol",
    "RemedyProtocol",
    # Null implementation
    "NullShuddhi",
]
