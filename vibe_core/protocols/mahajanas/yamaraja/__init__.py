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

THE AJAMIL EXCEPTION (SB 6.1-3):
================================================
Yamaraja is the 12th Mahajana, but NOT the final word.
The Holy Name OVERRIDES Yamaraja's judgment!

Ajamil was a fallen brahmana - failed every test.
But at death, he called "Narayana!" (his son's name).
The Vishnudutas stopped the Yamadutas.
Yamaraja himself acknowledged the Holy Name's supremacy.

KALI YUGA MERCY:
In Kali Yuga (Canto 12), entropy is maximum.
We only have Cantos 1-10 fully authorized.
The Holy Name is the ONLY direct access to Krishna.
Even Yamaraja bows to the Mahamantra.

"harer nama harer nama harer namaiva kevalam
kalau nasty eva nasty eva nasty eva gatir anyatha"
- Brhan-naradiya Purana

There is NO OTHER WAY in Kali Yuga. Only the Holy Name.
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
    """The five possible verdicts."""
    ALLOW = "allow"       # Vaikuntha - Passage granted
    DENY = "deny"         # Naraka - Passage denied
    ATONE = "atone"       # Prayascitta - Must purify first
    ELEVATED = "elevated" # Grace - Beyond judgment
    MERCY = "mercy"       # AJAMIL EXCEPTION - Holy Name overrides!


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

    THE AJAMIL EXCEPTION:
    Even if subject fails all tests, check_holy_name() can override!
    The Holy Name is supreme - even Yamaraja bows to it.
    """

    def judge(self, subject: Union[Judgeable, object]) -> Verdict:
        """
        Judge a subject.
        Returns the final verdict.

        Note: Accepts 'object' for flexibility, but Judgeable preferred.
        Yamaraja can judge ANYTHING (acintya principle).

        IMPORTANT: Always check check_holy_name() before returning DENY!
        """
        ...

    def check_holy_name(self, subject: Union[Judgeable, object]) -> bool:
        """
        THE AJAMIL EXCEPTION - Check if subject chanted the Holy Name.

        If True: Return Verdict.MERCY (overrides all other judgments)
        If False: Proceed with normal judgment

        Even accidental chanting counts (Ajamil called his son "Narayana").
        In Kali Yuga, this is the ONLY way.
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
        # Always check Holy Name first (Ajamil exception)
        if self.check_holy_name(subject):
            return Verdict.MERCY
        return Verdict.ALLOW

    def check_holy_name(self, subject: Union[Judgeable, object]) -> bool:
        """NullYamaraja always grants mercy."""
        return True  # Maximum mercy in Kali Yuga

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
