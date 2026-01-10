"""
YAMARAJA - The 12th Mahajana (Judgment/Testing)
===============================================
OpCode: assert_truth (Bit 5)
Opulence: ALL 6 (The Final Audit)

The Lord of Death. The Final Judge.
Every soul must face Yamaraja.
"Logic cannot save you." - ramanujan.py

Yamaraja OWNS all judgment protocols:
- Testing / Assertions
- Final Validation
- Performance Judgment
- Governance Gates
- The Ramanujan Proof

Yamaraja is the LAST Mahajana.
If you pass Yamaraja, you pass EVERYTHING.
If you fail Yamaraja, NOTHING ELSE MATTERS.

Existing: protocols/governance/yamaraja.py (to be migrated)
"""

from typing import Protocol, runtime_checkable, Any
from enum import Enum


class Verdict(str, Enum):
    """The four possible verdicts."""
    ALLOW = "allow"       # Vaikuntha - Passage granted
    DENY = "deny"         # Naraka - Passage denied
    ATONE = "atone"       # Prayascitta - Must purify first
    ELEVATED = "elevated" # Grace - Beyond judgment


@runtime_checkable
class YamarajaProtocol(Protocol):
    """
    The Judgment Protocol.
    Any system that makes final decisions must implement this.
    """

    def judge(self, subject: Any) -> Verdict:
        """
        Judge a subject.
        Returns the final verdict.
        """
        ...

    def assert_truth(self, condition: bool, reason: str) -> None:
        """
        Assert truth. Raises if false.
        This is the OpCode.
        """
        ...

    def get_karma_balance(self) -> float:
        """
        Get the subject's karma balance.
        Positive = good karma. Negative = bad karma.
        """
        ...


class NullYamaraja:
    """
    The Merciful Judge.
    All pass (for testing without judgment).
    """

    def judge(self, subject: Any) -> Verdict:
        return Verdict.ALLOW

    def assert_truth(self, condition: bool, reason: str) -> None:
        pass  # No assertion

    def get_karma_balance(self) -> float:
        return 0.0  # Neutral


__all__ = ["YamarajaProtocol", "NullYamaraja", "Verdict"]
