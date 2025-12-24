"""
OPUS-212: Shuddhi Protocol - The Contract for Structural Self-Healing.

Shuddhi (Sanskrit: 'Purification') is the core service for surgical
code transformations using Concrete Syntax Trees (CST).
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Protocol, runtime_checkable


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
