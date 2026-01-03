"""
OPUS-212: Shuddhi Protocol - The Contract for Structural Self-Healing.

Shuddhi (Sanskrit: 'Purification') is the core service for surgical
code transformations using Concrete Syntax Trees (CST).

Protocols:
- ShuddhiProtocol: Engine service interface
- RemedyProtocol: Individual remedy interface (VEDA-4 compliant)
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Protocol, runtime_checkable


class ShuddhiStatus(str, Enum):
    """The state of a purification attempt."""

    PURIFIED = "purified"  # Transformation successful and verified
    SKIPPED = "skipped"  # No violation found in the file
    FAILED = "failed"  # Error during transformation or verification
    OUT_OF_SCOPE = "out_of_scope"  # Heuristic: Required context (self.system) missing


@dataclass
class ShuddhiResult:
    """The outcome of a Shuddhi operation."""

    status: ShuddhiStatus
    file_path: Path
    rule_id: str
    message: str = ""
    diff: str = ""
    purified_code: Optional[str] = None

    @property
    def success(self) -> bool:
        """True if the file is clean (either purified or already clean)."""
        return self.status in (ShuddhiStatus.PURIFIED, ShuddhiStatus.SKIPPED)


@runtime_checkable
class ShuddhiProtocol(Protocol):
    """
    The surgical self-healing interface of the Kernel.

    Dharma: Shuddhi does not 'replace text'. It performs structural surgery
    on the Concrete Syntax Tree, preserving comments and formatting.
    """

    def purify(self, file_path: Path, rule_id: str) -> ShuddhiResult:
        """
        Heals a specific structural violation in a file.

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


@runtime_checkable
class RemedyProtocol(Protocol):
    """
    The contract for individual Shuddhi remedies.

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
