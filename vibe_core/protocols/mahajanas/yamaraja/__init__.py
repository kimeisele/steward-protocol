"""
YAMARAJA - The 12th Mahajana (Judgment/Testing)
===============================================
OpCode: assert_truth (Bit 5)
Opulence: ALL 6 (The Final Audit)

The Lord of Death. The Final Judge.
Every soul must face Yamaraja.
"Logic cannot save you." - ramanujan.py

PROTOCOL OWNERSHIP (Anti-Mayavad):
Yamaraja is the PERSON responsible for all judgment.
Not abstract "testing" - PERSONAL judgment by Yamaraja.

OWNED PROTOCOLS:
- testable.py - Test framework
- bhagavan.py - The 6 opulence tests
- ramanujan.py - Mathematical proof
- kurukshetra.py - Battle testing
- governance/yamaraja.py - Gate keeping

Yamaraja is the LAST Mahajana.
If you pass Yamaraja, you pass EVERYTHING.
If you fail Yamaraja, NOTHING ELSE MATTERS.
"""

from typing import Protocol, runtime_checkable, List, Final, Union
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# PROTOCOL OWNERSHIP - Yamaraja's Domain
# =============================================================================

OWNED_PROTOCOLS: Final[List[str]] = [
    "testable",
    "bhagavan",
    "ramanujan",
    "kurukshetra",
    "governance/yamaraja",
    "mahajanas/yamaraja",
]

OWNED_OPCODES: Final[List[str]] = [
    "ASSERT_TRUTH",  # The truth check
]


# =============================================================================
# JUDGMENT TYPES
# =============================================================================

class Verdict(str, Enum):
    """The four possible verdicts."""
    ALLOW = "allow"       # Vaikuntha - Passage granted
    DENY = "deny"         # Naraka - Passage denied
    ATONE = "atone"       # Prayascitta - Must purify first
    ELEVATED = "elevated" # Grace - Beyond judgment


@dataclass(frozen=True)
class Judgeable:
    """
    Anything that can be judged by Yamaraja.
    Replaces 'Any' with explicit judgeable structure.

    Note: Yamaraja CAN judge anything (acintya),
    but we provide structure for type safety.
    """
    subject_type: str  # "code", "action", "entity", "soul"
    subject_id: str
    karma_history: List[str] = None  # type: ignore

    def __post_init__(self) -> None:
        if self.karma_history is None:
            object.__setattr__(self, 'karma_history', [])


@dataclass(frozen=True)
class JudgmentRecord:
    """The record of Yamaraja's judgment."""
    subject: Judgeable
    verdict: Verdict
    reason: str
    karma_delta: float  # Change to karma balance


# =============================================================================
# PROTOCOL DEFINITION
# =============================================================================

@runtime_checkable
class YamarajaProtocol(Protocol):
    """
    The Judgment Protocol.
    Any system that makes final decisions must implement this.

    ANTI-MAYAVAD: This is not abstract "testing".
    YAMARAJA (the Person) judges. He is the Lord of Death.
    """

    def judge(self, subject: Union[Judgeable, object]) -> Verdict:
        """
        Judge a subject.
        Returns the final verdict.

        Note: Accepts 'object' for flexibility, but Judgeable preferred.
        Yamaraja can judge ANYTHING (acintya principle).
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

    def judge(self, subject: Union[Judgeable, object]) -> Verdict:
        return Verdict.ALLOW

    def assert_truth(self, condition: bool, reason: str) -> None:
        pass  # No assertion

    def get_karma_balance(self) -> float:
        return 0.0  # Neutral


__all__ = [
    # Protocol
    "YamarajaProtocol",
    "NullYamaraja",
    # Types
    "Verdict",
    "Judgeable",
    "JudgmentRecord",
    # Ownership
    "OWNED_PROTOCOLS",
    "OWNED_OPCODES",
]
