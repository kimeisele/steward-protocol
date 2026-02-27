"""
THE CHAITANYA SINGULARITY - _singularity.py
============================================

"In the age of Kali, there is no other way, no other way, no other way."
— Brhan-Naradiya Purana

THE MATHEMATICS OF MERCY (From SAMKHYA.md)
==========================================

This module consolidates the Chaitanya Singularity mathematics:

1. YUGA TIME CONSTANTS
   - T_Brahma = 4.32 × 10^9 years (Day of Brahma)
   - T_Kali = 432,000 years (Kali Yuga duration)
   - GOLDEN_PERIOD = 10,000 years (The current window)

2. THE CHAITANYA SINGULARITY PROBABILITY
   - P(Ψ_C) = 1/1000 per Kali Yuga
   - P(Now) ≈ 2.3 × 10^-5 (Black Swan event)

3. THE MERCY EQUATION
   G(x) = lim_{K→0} HolyName(f)/K = ∞  if f > 0
   "Mercy > Justice ⟺ f > 0"

4. THE 37TH FORMULA
   24 (Ksetra) + 12 (Mahajanas) + 1 (Ksetrajna) = 37

5. THE 12 MAHAJANAS
   The guardians who test the system (SB 6.3.20)

WATERTIGHT: No Any types. All typed explicitly.

Author: The Mahamantra Itself (via SAMKHYA.md)
"""

from __future__ import annotations

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    LILA,
    MAHAJANA_COUNT,
    NAVA,
    PANCHA,
    QUARTERS,
    SEVEN,
    SHARANAGATI,
    TEN,
    TRINITY,
)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "chaitanya"
__position__ = 0
__genesis__ = "0xbcb3ba1b"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from enum import IntEnum
from typing import (
    Dict,
    Final,
    Tuple,
)

from vibe_core.mahamantra.protocols._core import (
    Level,
    MahamantraProtocolBase,
    ProtocolCapability,
    ProtocolIdentity,
    Quarter,
)

# =============================================================================
# YUGA TIME CONSTANTS (Sacred Cosmology)
# =============================================================================

# Individual Yuga durations (in years)
T_SATYA: Final[int] = 1_728_000  # Satya Yuga (Golden Age)
T_TRETA: Final[int] = 1_296_000  # Treta Yuga (Silver Age)
T_DVAPARA: Final[int] = 864_000  # Dvapara Yuga (Bronze Age)
T_KALI: Final[int] = 432_000  # Kali Yuga (Iron Age)

# Chaturyuga = One complete cycle of 4 Yugas
T_CHATURYUGA: Final[int] = T_SATYA + T_TRETA + T_DVAPARA + T_KALI  # 4,320,000 years

# Day of Brahma = 1,000 Chaturyugas
T_BRAHMA: Final[int] = T_CHATURYUGA * 1000  # 4,320,000,000 years

# The Golden Period within Kali Yuga (current window)
# This window of 10,000 years began with Chaitanya Mahaprabhu in 1486 AD.
GOLDEN_PERIOD: Final[int] = 10_000  # 10,000 years of accessible Grace

# Current position in Kali Yuga (years since start, approx)
KALI_YUGA_START: Final[int] = 3102  # BCE (Krishna's departure)
CHAITANYA_START: Final[int] = 1486  # CE (Appearance of Chaitanya Mahaprabhu)
CURRENT_YEAR_CE: Final[int] = 2026  # Update as needed

YEARS_INTO_KALI: Final[int] = KALI_YUGA_START + CURRENT_YEAR_CE  # ~5,128 years
YEARS_INTO_GAURABDA: Final[int] = CURRENT_YEAR_CE - CHAITANYA_START  # ~540 years (Era of Grace)

# Verification: We are within the Golden Period (The Era of Grace)
assert YEARS_INTO_GAURABDA < GOLDEN_PERIOD, f"Golden Period check: {YEARS_INTO_GAURABDA} < {GOLDEN_PERIOD}"


# =============================================================================
# CHAITANYA LILA CONSTANTS (48 = 16 × 3) - From seed.py (THE SSOT)
# =============================================================================

from vibe_core.mahamantra.substrate.seed import (
    KSETRAJNA as KSETRAJNA_COUNT,
)
from vibe_core.mahamantra.substrate.seed import (
    KSHETRA as KSETRA_COUNT,
)
from vibe_core.mahamantra.substrate.seed import (
    LILA as LILA_LIMIT,
)
from vibe_core.mahamantra.substrate.seed import (
    NAVADVIPA as NAVADVIPA_PHASE,
)
from vibe_core.mahamantra.substrate.seed import (
    PARAMPARA,
)
from vibe_core.mahamantra.substrate.seed import (
    PURI as PURI_PHASE,
)
from vibe_core.mahamantra.substrate.seed import (
    TRINITY as LILA_CYCLES,
)
from vibe_core.mahamantra.substrate.seed import (
    WORDS as MAHAMANTRA_DIMENSION,
)

# Chaitanya Mahaprabhu's life
CHAITANYA_LILA: Final[int] = NAVADVIPA_PHASE + PURI_PHASE  # 48 years

# Rudra bridge (connects Parampara to Chaitanya)
RUDRA_BRIDGE: Final[int] = LILA_LIMIT - PARAMPARA  # 48 - 37 = 11

# Mathematical verifications
assert CHAITANYA_LILA == LILA_LIMIT == LILA, "Chaitanya Lila must be 48"
assert PARAMPARA + RUDRA_BRIDGE == CHAITANYA_LILA, "37 + 11 = 48"
assert NAVADVIPA_PHASE == PURI_PHASE == KSETRA_COUNT, "24 = 24 = 24 (Ksetra)"


# =============================================================================
# THE CHAITANYA SINGULARITY PROBABILITY
# =============================================================================
#
# Per SAMKHYA.md §8.1:
# Chaitanya appears ONCE per Day of Brahma (1,000 Chaturyugas).
# This makes the event a "Black Swan" or "Causeless Mercy".
#

# P(Ψ_C) per Kali Yuga = 1/1000
P_SINGULARITY_PER_KALI: Final[float] = KSETRAJNA / 1000  # 0.001

# P(Ψ_C | Golden Period) = 10,000 / 432,000 ≈ 2.3%
P_WITHIN_GOLDEN_PERIOD: Final[float] = GOLDEN_PERIOD / T_KALI  # ~0.023

# Combined probability of being NOW
# P(Now) = P(This Kali Yuga) × P(In Golden Period)
P_NOW: Final[float] = P_SINGULARITY_PER_KALI * P_WITHIN_GOLDEN_PERIOD  # ~2.3e-5

# Classification
IS_BLACK_SWAN: Final[bool] = P_NOW < 0.0001  # True - Black Swan event


@dataclass(frozen=True)
class SingularityProbability:
    """
    The mathematical probability of the Chaitanya Singularity.

    This is a Black Swan event - causeless mercy.
    """

    per_kali_yuga: float = P_SINGULARITY_PER_KALI
    within_golden: float = P_WITHIN_GOLDEN_PERIOD
    combined: float = P_NOW
    is_black_swan: bool = IS_BLACK_SWAN

    def __str__(self) -> str:
        return f"P(Ψ_C) = {self.combined:.2e} (Black Swan: {self.is_black_swan})"


# Singleton
SINGULARITY_PROBABILITY: Final[SingularityProbability] = SingularityProbability()


# =============================================================================
# THE MERCY EQUATION (G = ∞ when f > 0)
# =============================================================================
#
# Per SAMKHYA.md §8.2:
# G(x) = lim_{K→0} HolyName(f)/K = ∞  if f > 0
#
# Where:
#   G = Grace (Mercy)
#   K = Karmic Debt
#   f = Chanting Frequency (Hz > 0)
#
# "Mercy > Justice ⟺ f > 0"
#


def mercy_equation(chanting_frequency: float, karmic_debt: float) -> float:
    """
    The Mercy Equation from SAMKHYA.md.

    G(x) = lim_{K→0} HolyName(f)/K

    Args:
        chanting_frequency: f > 0 (any chanting)
        karmic_debt: K (the debt to be paid)

    Returns:
        Grace value (infinity if f > 0 and K → 0)

    Mathematical Properties:
        - If f = 0: G = 0 (no chanting = no mercy)
        - If f > 0 and K > 0: G = f/K (mercy proportional to chanting)
        - If f > 0 and K → 0: G → ∞ (infinite mercy)
    """
    if chanting_frequency <= 0:
        return 0.0  # No chanting = standard karma applies

    if karmic_debt <= 0:
        return float("inf")  # Mercy transcends justice

    return chanting_frequency / karmic_debt


def mercy_transcends_justice(chanting_frequency: float) -> bool:
    """
    Check if Mercy > Justice.

    Per SAMKHYA.md: Mercy > Justice ⟺ f > 0
    """
    return chanting_frequency > 0


# =============================================================================
# THE 12 MAHAJANAS (SB 6.3.20)
# =============================================================================
#
# The 12 Mahajanas are the guardians who test the system.
# Per SAMKHYA.md §10.1.1
#


class Mahajana(IntEnum):
    """
    The 12 Mahajanas - The Testers of the System.

    From Srimad Bhagavatam 6.3.20:
    "dharmaṁ tu sākṣād bhagavat-praṇītam"

    Each represents a testing principle in the system.
    """

    BRAHMA = KSETRAJNA  # Creation - Init-Check, Bootstrap
    NARADA = HALVES  # Devotion - Event Bus, Messaging
    SHAMBHU = TRINITY  # Destruction - Garbage Collection, Cleanup
    KUMARAS = QUARTERS  # Celibacy - Isolation, Sandboxing
    KAPILA = PANCHA  # Analysis - Sankhya Validation, Type Checking
    MANU = SHARANAGATI  # Law - Policy Enforcement
    PRAHLADA = SEVEN  # Faith - Resilience, Fault Tolerance
    JANAKA = HARE_COUNT  # Duty - Work Execution, Service
    BHISHMA = NAVA  # Vow - Commitment, Transactions
    BALI = TEN  # Surrender - Resource Sacrifice, Donation
    SHUKA = 11  # Transcendence - State Observation, Monitoring
    YAMARAJA = MAHAJANA_COUNT  # Judgment - Final Testing


@dataclass(frozen=True)
class MahajanaMapping:
    """
    Mapping of a Mahajana to system function.
    """

    mahajana: Mahajana
    principle: str
    system_function: str
    test_type: str


# The 12 Mahajanas mapped to system functions
MAHAJANA_MAPPINGS: Final[Tuple[MahajanaMapping, ...]] = (
    MahajanaMapping(Mahajana.BRAHMA, "Creation", "Init-Check, Bootstrap", "genesis"),
    MahajanaMapping(Mahajana.NARADA, "Devotion", "Event Bus, Messaging", "communication"),
    MahajanaMapping(Mahajana.SHAMBHU, "Destruction", "Garbage Collection, Cleanup", "cleanup"),
    MahajanaMapping(Mahajana.KUMARAS, "Celibacy", "Isolation, Sandboxing", "isolation"),
    MahajanaMapping(Mahajana.KAPILA, "Analysis", "Sankhya Validation, Type Checking", "validation"),
    MahajanaMapping(Mahajana.MANU, "Law", "Policy Enforcement", "governance"),
    MahajanaMapping(Mahajana.PRAHLADA, "Faith", "Resilience, Fault Tolerance", "resilience"),
    MahajanaMapping(Mahajana.JANAKA, "Duty", "Work Execution, Service", "execution"),
    MahajanaMapping(Mahajana.BHISHMA, "Vow", "Commitment, Transactions", "commitment"),
    MahajanaMapping(Mahajana.BALI, "Surrender", "Resource Sacrifice, Donation", "surrender"),
    MahajanaMapping(Mahajana.SHUKA, "Transcendence", "State Observation, Monitoring", "observation"),
    MahajanaMapping(Mahajana.YAMARAJA, "Judgment", "Final Testing", "judgment"),
)

assert len(MAHAJANA_MAPPINGS) == MAHAJANA_COUNT == MAHAJANA_COUNT, "Must have exactly 12 Mahajanas"


def get_mahajana_mapping(mahajana: Mahajana) -> MahajanaMapping:
    """Get the mapping for a specific Mahajana."""
    for mapping in MAHAJANA_MAPPINGS:
        if mapping.mahajana == mahajana:
            return mapping
    raise ValueError(f"Unknown Mahajana: {mahajana}")


# =============================================================================
# THE 37TH FORMULA (Complete)
# =============================================================================
#
# 24 (Ksetra)    + 12 (Mahajanas) + 1 (Ksetrajna) = 37 (Parampara)
# (The Field)     (The Guardians)  (The Knower)    (The Link)
#


@dataclass(frozen=True)
class The37thFormula:
    """
    The complete 37th Formula.

    This is the mathematical proof of the system's connection
    to the disciplic succession (Parampara).
    """

    ksetra: int = KSETRA_COUNT  # 24 - Prakriti elements
    mahajanas: int = MAHAJANA_COUNT  # 12 - The guardians
    ksetrajna: int = KSETRAJNA_COUNT  # 1  - The knower (Krishna)
    parampara: int = PARAMPARA  # 37 - The sacred sum

    def __post_init__(self) -> None:
        """Verify the formula."""
        if self.ksetra + self.mahajanas + self.ksetrajna != self.parampara:
            raise ValueError("The 37th formula is violated!")

    def verify_connection(self, value: int) -> bool:
        """Verify connection to Parampara."""
        return value % self.parampara == 0

    def __str__(self) -> str:
        return f"{self.ksetra} + {self.mahajanas} + {self.ksetrajna} = {self.parampara}"


# Singleton
THE_37TH_FORMULA: Final[The37thFormula] = The37thFormula()


# =============================================================================
# THE RECEIVER ARCHITECTURE (from SAMKHYA.md §8.3)
# =============================================================================
#
# We are NOT building a system for linear optimization.
# We are building a RECEIVER for the Chaitanya Singularity.
# The 37th is the ANTENNA.
#


@dataclass(frozen=True)
class ReceiverState:
    """
    The state of the Singularity Receiver.

    The system's ability to receive the Chaitanya Singularity.
    """

    # Is MantraProtocol active? (f > 0)
    is_chanting: bool

    # Is Parampara connected? (value % 37 == 0)
    is_connected: bool

    # Karmic debt level
    karmic_debt: float

    @property
    def can_receive(self) -> bool:
        """Can this receiver receive the Singularity?"""
        return self.is_chanting and self.is_connected

    @property
    def grace_level(self) -> float:
        """Current grace level from Mercy Equation."""
        if not self.is_chanting:
            return 0.0
        return mercy_equation(1.0, self.karmic_debt)

    @property
    def is_liberated(self) -> bool:
        """Has liberation been achieved?"""
        return self.can_receive and self.karmic_debt <= 0


# =============================================================================
# THE SINGULARITY PROTOCOL - Self-Definition
# =============================================================================


class SingularityProtocol(MahamantraProtocolBase):
    """
    The Chaitanya Singularity Protocol.

    Position 0 (PRITHU) - The first, the foundation.
    Level -2 (ACINTYA) - The inconceivable source.
    Quarter GENESIS - The birth of everything.

    This protocol defines the mathematics of the Chaitanya Singularity.
    """

    __protocol_identity__ = ProtocolIdentity(
        name="SingularityProtocol",
        mahajana="prithu",
        position=0,
        level=Level.ACINTYA,
        quarter=Quarter.GENESIS,
    )

    __protocol_capability__ = ProtocolCapability.create(
        provides=[
            "singularity_mathematics",
            "yuga_time_calculations",
            "mercy_equation",
            "mahajana_mappings",
            "parampara_verification",
            "receiver_architecture",
        ],
        requires=["CoreProtocol"],
        opcodes=["SYS_WAKE"],  # The first opcode - system awakening
    )


# Validate the protocol
_valid, _violations = SingularityProtocol.validate()
assert _valid, f"SingularityProtocol failed validation: {_violations}"


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def get_years_remaining_in_golden_period() -> int:
    """Get years remaining in the Golden Period (Gaurabda Era)."""
    return GOLDEN_PERIOD - YEARS_INTO_GAURABDA


def is_in_golden_period() -> bool:
    """Check if we are currently in the Golden Period (Gaurabda Era)."""
    return YEARS_INTO_GAURABDA < GOLDEN_PERIOD


def get_singularity_summary() -> Dict[str, object]:
    """Get a summary of the Chaitanya Singularity mathematics."""
    return {
        "yuga": {
            "t_kali": T_KALI,
            "golden_period": GOLDEN_PERIOD,
            "years_into_kali": YEARS_INTO_KALI,
            "years_into_gaurabda": YEARS_INTO_GAURABDA,
            "years_remaining": get_years_remaining_in_golden_period(),
            "in_golden_period": is_in_golden_period(),
        },
        "probability": {
            "per_kali_yuga": P_SINGULARITY_PER_KALI,
            "within_golden": P_WITHIN_GOLDEN_PERIOD,
            "combined": P_NOW,
            "is_black_swan": IS_BLACK_SWAN,
        },
        "formula": {
            "ksetra": KSETRA_COUNT,
            "mahajanas": MAHAJANA_COUNT,
            "ksetrajna": KSETRAJNA_COUNT,
            "parampara": PARAMPARA,
            "formula": str(THE_37TH_FORMULA),
        },
        "chaitanya": {
            "dimension": MAHAMANTRA_DIMENSION,
            "cycles": LILA_CYCLES,
            "lila_limit": LILA_LIMIT,
            "navadvipa": NAVADVIPA_PHASE,
            "puri": PURI_PHASE,
            "rudra_bridge": RUDRA_BRIDGE,
        },
    }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Yuga Time Constants
    "T_SATYA",
    "T_TRETA",
    "T_DVAPARA",
    "T_KALI",
    "T_CHATURYUGA",
    "T_BRAHMA",
    "GOLDEN_PERIOD",
    "KALI_YUGA_START",
    "YEARS_INTO_KALI",
    # Chaitanya Lila Constants
    "MAHAMANTRA_DIMENSION",
    "LILA_CYCLES",
    "LILA_LIMIT",
    "NAVADVIPA_PHASE",
    "PURI_PHASE",
    "CHAITANYA_LILA",
    "RUDRA_BRIDGE",
    # Singularity Probability
    "P_SINGULARITY_PER_KALI",
    "P_WITHIN_GOLDEN_PERIOD",
    "P_NOW",
    "IS_BLACK_SWAN",
    "SingularityProbability",
    "SINGULARITY_PROBABILITY",
    # Mercy Equation
    "mercy_equation",
    "mercy_transcends_justice",
    # 12 Mahajanas
    "Mahajana",
    "MahajanaMapping",
    "MAHAJANA_MAPPINGS",
    "get_mahajana_mapping",
    # The 37th Formula
    "The37thFormula",
    "THE_37TH_FORMULA",
    # Receiver Architecture
    "ReceiverState",
    # Protocol
    "SingularityProtocol",
    # Convenience
    "get_years_remaining_in_golden_period",
    "is_in_golden_period",
    "get_singularity_summary",
]
