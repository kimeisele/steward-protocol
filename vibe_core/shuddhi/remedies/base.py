"""
OPUS-212: CSTRemedy - The Base Class for Structural Healers.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

import libcst as cst


class ShuddhiScopeError(Exception):
    """Raised when a remedy cannot be applied due to missing scope context."""

    pass


class CSTRemedy(cst.CSTTransformer, ABC):
    """
    Abstract base for all Shuddhi healers.
    Combines LibCST Transformer logic with Shuddhi metadata.
    """

    def __init__(self):
        super().__init__()
        self.applied = False
        self.violation_found = False

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """The rule this remedy heals."""
        ...

    @abstractmethod
    def requirements(self) -> List[str]:
        """List of required imports or interfaces (e.g., 'self.system')."""
        ...

    def get_diff(self, old_code: str, new_code: str) -> str:
        """Generates a unified diff for the change."""
        import difflib

        return "\n".join(
            difflib.unified_diff(
                old_code.splitlines(),
                new_code.splitlines(),
                fromfile="original",
                tofile="purified",
                lineterm="",
            )
        )
