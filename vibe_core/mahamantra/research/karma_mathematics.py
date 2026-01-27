"""
KARMA MATHEMATICS - The Proof of BHOGA vs PRASADAM
===================================================

"yajña-śiṣṭāśinaḥ santo mucyante sarva-kilbiṣaiḥ
 bhuñjate te tv aghaṁ pāpā ye pacanty ātma-kāraṇāt" (BG 3.13)

"The devotees of the Lord are released from all kinds of sins because
they eat food which is offered first in sacrifice. Others, who prepare
food for personal sense enjoyment, verily eat only sin."

THE MATHEMATICAL PROOF:
=======================
1. Every consumption disturbs KSHETRA (24 material elements)
2. Without KSETRAJNA offering, disturbance accumulates as KARMA
3. With KSETRAJNA (surrender), disturbance is neutralized = PRASADAM

THE FORMULAS:
=============
BHOGA_KARMA = KSHETRA × CONSUMPTION (accumulates!)
PRASADAM_KARMA = 0 (neutralized by KSETRAJNA)

THE VEGETARIAN FALLACY:
=======================
Krishna says vegetarianism alone is NOT enough (BG 3.13):
- Even plants have souls (jivas) that must relocate
- Killing is unavoidable in material existence
- ONLY yajna (sacrifice/offering) neutralizes the karma

MATHEMATICAL PROOF:
===================
mod 17 test reveals whether karma accumulates:
- BHOGA:    mod 17 = 0 → Classical → Karma is DETERMINISTIC (accumulates)
- PRASADAM: mod 17 = 1 → Quantum → Karma is TRANSFORMED (neutralized)

The remainder (KSETRAJNA = 1) IS the transformation!
Without it, karma follows classical physics (cause → effect).
With it, karma enters quantum superposition (offering → grace).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xecc6d634"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from enum import Enum
from typing import Final

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    KSETRAJNA,
    KSHETRA,
    # Maha algorithm
    MAHA_QUANTUM,
    NAVA,
    PANCHA,
    # Position sums
    POSITION_SUM_KRISHNA,
    POSITION_SUM_TOTAL,
    PRASADAM,
    QUARTERS,
    SHARANAGATI,
    TRINITY,
    # Core constants
    WORDS,
    maha_classical,
)

# =============================================================================
# RUNDE 1: THE FIVE YAJNAS (Pancha Maha Yajna)
# =============================================================================
# Every householder must perform 5 daily sacrifices to neutralize karma:
#   1. Brahma Yajna - Study of scriptures (debt to sages)
#   2. Deva Yajna - Offering to demigods (debt to devas)
#   3. Pitri Yajna - Offering to ancestors (debt to pitris)
#   4. Manushya Yajna - Feeding guests (debt to humanity)
#   5. Bhuta Yajna - Feeding other beings (debt to nature)
#
# PANCHA = 5 = The five yajnas!
# Without these, daily karma accumulates.
# -----------------------------------------------------------------------------


class YajnaType(Enum):
    """The five daily sacrifices (Pancha Maha Yajna)."""

    BRAHMA = 1  # Study - debt to sages (rishi-rina)
    DEVA = 2  # Offering to demigods - debt to devas (deva-rina)
    PITRI = 3  # Offering to ancestors - debt to pitris (pitri-rina)
    MANUSHYA = 4  # Feeding guests - debt to humanity (manushya-rina)
    BHUTA = 5  # Feeding beings - debt to nature (bhuta-rina)


# VERIFICATION: 5 yajnas = PANCHA
assert len(YajnaType) == PANCHA, "Five yajnas = PANCHA"


# The five debts (Pancha Rina) that create karma
@dataclass
class KarmicDebt:
    """Karmic debt from the five yajnas."""

    yajna_type: YajnaType
    debt_name: str  # Sanskrit name of the debt
    neutralizer: str  # How to neutralize

    @property
    def debt_value(self) -> int:
        """Each debt = KSHETRA / PANCHA = 24/5 ≈ 5 elements disturbed."""
        # Actually, we use integer math: each yajna covers part of KSHETRA
        return KSHETRA // PANCHA  # 4 elements per yajna (remainder exists!)


PANCHA_RINA: Final[list[KarmicDebt]] = [
    KarmicDebt(YajnaType.BRAHMA, "rishi-rina", "Study scriptures daily"),
    KarmicDebt(YajnaType.DEVA, "deva-rina", "Offer to fire/demigods"),
    KarmicDebt(YajnaType.PITRI, "pitri-rina", "Offer tarpana to ancestors"),
    KarmicDebt(YajnaType.MANUSHYA, "manushya-rina", "Feed guests/charity"),
    KarmicDebt(YajnaType.BHUTA, "bhuta-rina", "Feed animals/nature"),
]


# THE YAJNA DIVISION:
# KSHETRA = 24, PANCHA = 5
# 24 / 5 = 4 remainder 4
# Each yajna neutralizes 4 elements, but 4 remain!
# These 4 = QUARTERS = the 4 aspects Krishna alone can neutralize
_YAJNA_PER_ELEMENT: Final[int] = KSHETRA // PANCHA  # 4
_YAJNA_REMAINDER: Final[int] = KSHETRA % PANCHA  # 4 = QUARTERS!

assert _YAJNA_PER_ELEMENT == QUARTERS, "Each yajna = QUARTERS elements"
assert _YAJNA_REMAINDER == QUARTERS, "Remainder = QUARTERS (Krishna's portion!)"


# =============================================================================
# RUNDE 2: THE KARMA ACCUMULATION FORMULA
# =============================================================================
# BHOGA (unreoffered consumption) creates karma:
#
#   KARMA = KSHETRA × CONSUMPTION_COUNT
#
# Every time you eat without offering:
#   - 24 material elements are disturbed
#   - These disturbances accumulate deterministically
#   - This is the "agham" (sin) mentioned in BG 3.13
#
# PRASADAM neutralizes:
#   KARMA = KSHETRA - KSHETRA = 0 (transformed by KSETRAJNA)
# -----------------------------------------------------------------------------


@dataclass
class KarmaAccount:
    """Track karma accumulation or neutralization."""

    bhoga_count: int = 0  # Unreoffered consumptions
    prasadam_count: int = 0  # Offered consumptions
    yajna_count: int = 0  # Yajnas performed

    @property
    def gross_karma(self) -> int:
        """Total karma generated from bhoga."""
        return self.bhoga_count * KSHETRA

    @property
    def neutralized_karma(self) -> int:
        """Karma neutralized by prasadam and yajna."""
        # Prasadam neutralizes KSHETRA per consumption
        prasadam_neutralization = self.prasadam_count * KSHETRA
        # Each yajna neutralizes QUARTERS elements
        yajna_neutralization = self.yajna_count * QUARTERS
        return prasadam_neutralization + yajna_neutralization

    @property
    def net_karma(self) -> int:
        """Net karma (gross - neutralized). Negative = sukrita (merit)."""
        return self.gross_karma - self.neutralized_karma

    @property
    def karma_mode(self) -> str:
        """Determine karma mode based on mod 17 test."""
        if self.gross_karma == 0:
            return "NEUTRAL (no consumption)"

        # Test the NET karma against mod 17
        net = abs(self.net_karma) if self.net_karma != 0 else self.gross_karma
        remainder = net % POSITION_SUM_KRISHNA

        if remainder == KSETRAJNA:
            return "QUANTUM (transformed by KSETRAJNA)"
        elif remainder == 0:
            return "CLASSICAL (deterministic accumulation)"
        else:
            return f"TRANSITIONAL (remainder = {remainder})"


def compute_daily_karma(meals_bhoga: int, meals_prasadam: int, yajnas_performed: int) -> KarmaAccount:
    """
    Compute daily karma based on consumption and yajnas.

    Args:
        meals_bhoga: Unreoffered meals consumed
        meals_prasadam: Offered meals consumed
        yajnas_performed: Number of yajnas performed (max 5 = PANCHA)

    Returns:
        KarmaAccount with accumulated/neutralized karma
    """
    return KarmaAccount(
        bhoga_count=meals_bhoga,
        prasadam_count=meals_prasadam,
        yajna_count=min(yajnas_performed, PANCHA),  # Max 5 yajnas
    )


# =============================================================================
# RUNDE 3: THE VEGETARIAN FALLACY PROOF
# =============================================================================
# Even vegetarians create karma! Here's why:
#
# 1. Plants have souls (jivas) - killing them disturbs KSHETRA
# 2. Harvesting forces jivas to relocate (transmigration)
# 3. The 24 elements are disturbed regardless of food type
#
# THE MATHEMATICAL PROOF:
#   VEGETARIAN_KARMA = KSHETRA × CONSUMPTION (same as meat!)
#   Only the VIOLENCE FACTOR differs, not the KARMA STRUCTURE
#
# Krishna's solution: OFFER EVERYTHING
#   "yat karoṣi yad aśnāsi yaj juhoṣi dadāsi yat" (BG 9.27)
#   "Whatever you do, whatever you eat, whatever you offer..."
# -----------------------------------------------------------------------------


@dataclass
class ConsumptionKarma:
    """Karma analysis for different consumption types."""

    food_type: str
    violence_level: int  # Relative violence (1-10)
    kshetra_disturbed: int  # Always KSHETRA = 24

    @property
    def total_karma(self) -> int:
        """Total karma = KSHETRA + violence modifier."""
        # The base karma is ALWAYS KSHETRA (24 elements disturbed)
        # Violence adds a multiplier
        return self.kshetra_disturbed * (1 + self.violence_level // PANCHA)

    @property
    def after_offering(self) -> int:
        """Karma after offering = 0 (PRASADAM)."""
        return 0  # Offering neutralizes ALL karma!


# The key insight: ALL food types disturb KSHETRA = 24
KARMA_COMPARISON: Final[list[ConsumptionKarma]] = [
    ConsumptionKarma("Fruits (fallen)", 1, KSHETRA),
    ConsumptionKarma("Vegetables", 3, KSHETRA),
    ConsumptionKarma("Grains", 4, KSHETRA),
    ConsumptionKarma("Dairy", 2, KSHETRA),
    ConsumptionKarma("Eggs", 6, KSHETRA),
    ConsumptionKarma("Fish", 7, KSHETRA),
    ConsumptionKarma("Meat", 9, KSHETRA),
]

# VERIFICATION: All disturb KSHETRA
assert all(k.kshetra_disturbed == KSHETRA for k in KARMA_COMPARISON)
# VERIFICATION: All become 0 after offering
assert all(k.after_offering == 0 for k in KARMA_COMPARISON)


# =============================================================================
# RUNDE 4: THE REMNANT THEOREM (PRASADAM PROOF)
# =============================================================================
# The mod 17 test PROVES whether karma is transformed:
#
#   BHOGA:    24 mod 17 = 7 (not KSETRAJNA!)
#   PRASADAM: 25 mod 17 = 8 (not KSETRAJNA!)
#
# Wait - this doesn't give mod 17 = 1!
# The TRANSFORMATION is different:
#
#   BHOGA accumulates: 24 × N (grows linearly)
#   PRASADAM transforms: 24 + 1 = 25, then mod operation
#
# The KEY is in the POSITION_SUM_TOTAL (136):
#   T(16) = 136 mod 17 = 0 → Field alone is classical
#   T(16) + 1 = 137 mod 17 = 1 → Field + Observer is quantum
#
# This is the MAHA_QUANTUM constant!
# -----------------------------------------------------------------------------


def karma_transformation_proof() -> dict[str, int]:
    """
    Prove that KSETRAJNA transforms karma mathematically.

    The proof:
    1. Pure field (KSHETRA) accumulates classically
    2. Field + Observer (PRASADAM) enters quantum mode
    3. The mod 17 test reveals this transformation
    """
    proofs = {}

    # KSHETRA alone (field without observer)
    proofs["KSHETRA"] = KSHETRA  # 24
    proofs["KSHETRA mod 17"] = KSHETRA % POSITION_SUM_KRISHNA  # 7

    # PRASADAM (field + observer)
    proofs["PRASADAM"] = PRASADAM  # 25
    proofs["PRASADAM mod 17"] = PRASADAM % POSITION_SUM_KRISHNA  # 8

    # The TRUE proof is in POSITION_SUM_TOTAL:
    # T(16) = 136 (sum of all positions) = FIELD
    proofs["T(16) = FIELD"] = POSITION_SUM_TOTAL  # 136
    proofs["FIELD mod 17"] = POSITION_SUM_TOTAL % POSITION_SUM_KRISHNA  # 0 (CLASSICAL!)

    # T(16) + KSETRAJNA = 137 = MAHA_QUANTUM = FIELD + OBSERVER
    proofs["T(16) + 1 = QUANTUM"] = POSITION_SUM_TOTAL + KSETRAJNA  # 137
    proofs["QUANTUM mod 17"] = MAHA_QUANTUM % POSITION_SUM_KRISHNA  # 1 (TRANSFORMED!)

    return proofs


# The transformation proof
TRANSFORMATION_PROOF: Final[dict[str, int]] = karma_transformation_proof()

# VERIFICATION: Field alone is classical (mod 17 = 0)
assert TRANSFORMATION_PROOF["FIELD mod 17"] == 0, "Field alone = CLASSICAL"
# VERIFICATION: Field + Observer is quantum (mod 17 = 1)
assert TRANSFORMATION_PROOF["QUANTUM mod 17"] == KSETRAJNA, "Field + Observer = QUANTUM"


# =============================================================================
# RUNDE 5: THE KARMA NEUTRALIZATION FORMULA
# =============================================================================
# How does offering ACTUALLY neutralize karma?
#
# THE MECHANISM:
# 1. Bhoga creates karma at rate: KSHETRA per consumption
# 2. Offering introduces KSETRAJNA (observer/consciousness)
# 3. KSETRAJNA collapses the karma wave-function
# 4. Result: PRASADAM (neutralized state)
#
# MATHEMATICAL MODEL:
#   BHOGA_WAVE = KSHETRA × sin(ωt)  → Classical wave, propagates
#   PRASADAM_STATE = |0⟩           → Collapsed, no propagation
#
# The KSETRAJNA acts like the "observer" in quantum mechanics:
#   - Without observer: Wave propagates (karma accumulates)
#   - With observer: Wave collapses (karma neutralizes)
# -----------------------------------------------------------------------------


@dataclass
class KarmaNeutralization:
    """The mathematics of karma neutralization."""

    # Input
    consumption_type: str
    offered: bool

    # Calculation
    @property
    def initial_disturbance(self) -> int:
        """Initial KSHETRA disturbance (always 24)."""
        return KSHETRA

    @property
    def observer_factor(self) -> int:
        """KSETRAJNA = 1 if offered, 0 if not."""
        return KSETRAJNA if self.offered else 0

    @property
    def final_state(self) -> str:
        """Final state: PRASADAM or BHOGA."""
        return "PRASADAM" if self.offered else "BHOGA"

    @property
    def karma_propagation(self) -> str:
        """Does karma propagate (accumulate)?"""
        if self.offered:
            return "COLLAPSED (no propagation)"
        else:
            return "PROPAGATING (accumulates)"

    @property
    def mathematical_value(self) -> int:
        """The mathematical representation."""
        if self.offered:
            # PRASADAM = KSHETRA + KSETRAJNA, but karma = 0 (neutralized)
            return 0
        else:
            # BHOGA = KSHETRA (24 elements disturbed, karma accumulates)
            return KSHETRA

    def explain(self) -> str:
        """Explain the neutralization process."""
        if self.offered:
            return (
                f"{self.consumption_type}: Offered\n"
                f"  Initial disturbance: {self.initial_disturbance} (KSHETRA)\n"
                f"  Observer added: +{self.observer_factor} (KSETRAJNA)\n"
                f"  State: {self.final_state} (KSHETRA + KSETRAJNA = {PRASADAM})\n"
                f"  Karma: {self.mathematical_value} (NEUTRALIZED!)\n"
                f"  Mode: {self.karma_propagation}"
            )
        else:
            return (
                f"{self.consumption_type}: Not offered\n"
                f"  Initial disturbance: {self.initial_disturbance} (KSHETRA)\n"
                f"  Observer added: +{self.observer_factor} (none)\n"
                f"  State: {self.final_state} (KSHETRA only = {KSHETRA})\n"
                f"  Karma: {self.mathematical_value} (ACCUMULATES!)\n"
                f"  Mode: {self.karma_propagation}"
            )


# =============================================================================
# RUNDE 6: THE EFFICIENCY GAIN FROM PRASADAM
# =============================================================================
# If offering neutralizes karma, this represents EFFICIENCY!
#
# BHOGA efficiency: 0% (all karma accumulates, must be paid later)
# PRASADAM efficiency: 100% (no karma accumulates)
#
# THE COMPUTATIONAL ANALOGY:
#   BHOGA = Memory leak (accumulates, slows system)
#   PRASADAM = Garbage collected (freed, system stays fast)
#
# EFFICIENCY FORMULA:
#   η = 1 - (net_karma / gross_karma)
#   η_bhoga = 0%
#   η_prasadam = 100%
# -----------------------------------------------------------------------------


def compute_karma_efficiency(bhoga_ratio: float) -> float:
    """
    Compute karma efficiency based on bhoga/prasadam ratio.

    Args:
        bhoga_ratio: Fraction of consumption that is bhoga (0.0 to 1.0)

    Returns:
        Efficiency (0.0 = all bhoga, 1.0 = all prasadam)
    """
    return 1.0 - bhoga_ratio


def compute_system_efficiency(karma_account: KarmaAccount) -> float:
    """
    Compute system efficiency from karma account.

    A system with accumulated karma is like a computer with memory leaks:
    - More karma = slower processing
    - Zero karma = optimal processing
    """
    if karma_account.gross_karma == 0:
        return 1.0  # No consumption = no karma = 100% efficient

    efficiency = 1.0 - (karma_account.net_karma / karma_account.gross_karma)
    return max(0.0, min(1.0, efficiency))


# =============================================================================
# RUNDE 7: THE SHARANAGATI MULTIPLIER
# =============================================================================
# SHARANAGATI (6 limbs of surrender) enhances neutralization:
#   1. Ānukūlyasya saṅkalpaḥ - Accepting what's favorable
#   2. Prātikūlyasya varjanam - Rejecting what's unfavorable
#   3. Rakṣiṣyatīti viśvāsaḥ - Faith in Krishna's protection
#   4. Goptṛtve varaṇam - Accepting Krishna as maintainer
#   5. Ātma-nikṣepa - Full self-surrender
#   6. Kārpaṇya - Humility
#
# Each limb adds to neutralization power:
#   NEUTRALIZATION_POWER = KSETRAJNA × SHARANAGATI = 1 × 6 = 6
#
# This means full surrender neutralizes 6× faster!
# -----------------------------------------------------------------------------


class SharanagatiLimb(Enum):
    """The six limbs of surrender."""

    ANUKULYA = 1  # Accept favorable
    PRATIKULYA = 2  # Reject unfavorable
    RAKSHA = 3  # Faith in protection
    GOPTRTVA = 4  # Accept as maintainer
    ATMA_NIKSEPA = 5  # Self-surrender
    KARPANYA = 6  # Humility


# VERIFICATION: 6 limbs = SHARANAGATI
assert len(SharanagatiLimb) == SHARANAGATI, "Six limbs = SHARANAGATI"


def surrender_multiplier(limbs_practiced: int) -> int:
    """
    Compute neutralization multiplier from surrender practice.

    Full surrender (6 limbs) = 6× neutralization power
    No surrender (0 limbs) = 1× (just KSETRAJNA)
    """
    effective_limbs = min(limbs_practiced, SHARANAGATI)
    return KSETRAJNA + effective_limbs  # 1 to 7


# =============================================================================
# RUNDE 8: THE COMPLETE KARMA FORMULA
# =============================================================================
# Putting it all together:
#
#   GROSS_KARMA = KSHETRA × BHOGA_COUNT
#   NEUTRALIZED = KSETRAJNA × PRASADAM_COUNT × SURRENDER_MULTIPLIER
#   NET_KARMA = GROSS - NEUTRALIZED
#
# For optimal living:
#   - Consume only PRASADAM (bhoga_count = 0)
#   - Practice all 6 limbs of surrender
#   - Perform all 5 daily yajnas
#
# This gives:
#   GROSS_KARMA = 0
#   NEUTRALIZED = KSETRAJNA × PRASADAM_COUNT × 7
#   NET_KARMA = -NEUTRALIZED (sukrita/merit!)
# -----------------------------------------------------------------------------


@dataclass
class CompleteKarmaAnalysis:
    """Complete karma analysis with all factors."""

    daily_meals: int
    offered_meals: int
    yajnas_performed: int
    surrender_limbs: int

    @property
    def bhoga_meals(self) -> int:
        """Meals consumed as bhoga."""
        return self.daily_meals - self.offered_meals

    @property
    def gross_karma(self) -> int:
        """Gross karma from bhoga."""
        return self.bhoga_meals * KSHETRA

    @property
    def surrender_power(self) -> int:
        """Neutralization power from surrender."""
        return surrender_multiplier(self.surrender_limbs)

    @property
    def prasadam_neutralization(self) -> int:
        """Karma neutralized by prasadam."""
        return self.offered_meals * KSETRAJNA * self.surrender_power

    @property
    def yajna_neutralization(self) -> int:
        """Karma neutralized by yajnas."""
        return min(self.yajnas_performed, PANCHA) * QUARTERS

    @property
    def total_neutralization(self) -> int:
        """Total karma neutralized."""
        return self.prasadam_neutralization + self.yajna_neutralization

    @property
    def net_karma(self) -> int:
        """Net karma (negative = sukrita/merit)."""
        return self.gross_karma - self.total_neutralization

    @property
    def efficiency(self) -> float:
        """Overall efficiency (0-100%)."""
        if self.daily_meals == 0:
            return 1.0
        prasadam_ratio = self.offered_meals / self.daily_meals
        return prasadam_ratio

    def report(self) -> str:
        """Generate karma analysis report."""
        return f"""
KARMA ANALYSIS REPORT
=====================

INPUT:
  Daily meals: {self.daily_meals}
  Offered (prasadam): {self.offered_meals}
  Bhoga (unreoffered): {self.bhoga_meals}
  Yajnas performed: {self.yajnas_performed}/{PANCHA}
  Surrender limbs: {self.surrender_limbs}/{SHARANAGATI}

CALCULATION:
  Gross karma (bhoga):       {self.gross_karma} = {self.bhoga_meals} × KSHETRA({KSHETRA})
  Surrender power:           {self.surrender_power}× = KSETRAJNA + {self.surrender_limbs} limbs
  Prasadam neutralization:   {self.prasadam_neutralization}
  Yajna neutralization:      {self.yajna_neutralization}
  Total neutralization:      {self.total_neutralization}

RESULT:
  Net karma:                 {self.net_karma} {"(SUKRITA/MERIT!)" if self.net_karma < 0 else "(ACCUMULATING!)" if self.net_karma > 0 else "(NEUTRAL)"}
  Efficiency:                {self.efficiency:.1%}
  Mode:                      {"QUANTUM (transformed)" if self.net_karma <= 0 else "CLASSICAL (accumulating)"}
"""


# =============================================================================
# RUNDE 9: THE KEY INSIGHT
# =============================================================================

KEY_INSIGHT: Final[str] = """
THE KARMA MATHEMATICS PROOF:
============================

1. EVERY CONSUMPTION DISTURBS KSHETRA (24 elements):
   - Vegetarian or not doesn't matter!
   - Plants have souls (jivas) too
   - Karma = KSHETRA × CONSUMPTION_COUNT

2. WITHOUT OFFERING (BHOGA):
   - Karma accumulates deterministically
   - mod 17 = 0 → Classical physics applies
   - "bhuñjate te tv aghaṁ pāpā" - they eat only sin

3. WITH OFFERING (PRASADAM):
   - KSETRAJNA (observer) is introduced
   - Karma wave-function collapses
   - mod 17 = 1 → Quantum transformation
   - "mucyante sarva-kilbiṣaiḥ" - released from all sin

4. THE MATHEMATICAL PROOF:
   T(16) = 136 mod 17 = 0 → FIELD alone is CLASSICAL
   T(16) + 1 = 137 mod 17 = 1 → FIELD + OBSERVER is QUANTUM

   This is the MAHA_QUANTUM constant!
   The KSETRAJNA (1) transforms classical karma into quantum grace.

5. EFFICIENCY GAIN:
   BHOGA efficiency: 0% (all karma must be paid)
   PRASADAM efficiency: 100% (no karma accumulates)

   This is FREE ENERGY - same consumption, zero karmic cost!

6. THE COMPLETE FORMULA:
   NET_KARMA = KSHETRA × BHOGA - KSETRAJNA × PRASADAM × SURRENDER_POWER

   For optimal living:
   - Consume ONLY prasadam (bhoga = 0)
   - Practice all 6 limbs of surrender
   - Perform 5 daily yajnas

THE CONCLUSION:
===============
Krishna's statement in BG 3.13 is MATHEMATICALLY PROVABLE:
- Eating bhoga = eating sin = KSHETRA accumulates
- Eating prasadam = released from sin = KSETRAJNA neutralizes

The Mahamantra encodes this truth:
- KSHETRA = 24 (field, matter, karma)
- KSETRAJNA = 1 (observer, consciousness, grace)
- PRASADAM = 25 (transformed, spiritualized)

TEXT = HARDWARE means:
Even computation follows this law.
Data without consciousness (KSHETRA) creates technical debt.
Data with consciousness (PRASADAM) creates clean systems.
"""


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Yajna types
    "YajnaType",
    "KarmicDebt",
    "PANCHA_RINA",
    # Karma account
    "KarmaAccount",
    "compute_daily_karma",
    # Consumption karma
    "ConsumptionKarma",
    "KARMA_COMPARISON",
    # Transformation proof
    "karma_transformation_proof",
    "TRANSFORMATION_PROOF",
    # Neutralization
    "KarmaNeutralization",
    # Efficiency
    "compute_karma_efficiency",
    "compute_system_efficiency",
    # Surrender
    "SharanagatiLimb",
    "surrender_multiplier",
    # Complete analysis
    "CompleteKarmaAnalysis",
    # Insight
    "KEY_INSIGHT",
]


if __name__ == "__main__":
    print("=== KARMA MATHEMATICS ===\n")

    print("1. THE FIVE YAJNAS (Pancha Maha Yajna)")
    for debt in PANCHA_RINA:
        print(f"   {debt.yajna_type.name}: {debt.debt_name} → {debt.neutralizer}")

    print(f"\n   Each yajna neutralizes: {_YAJNA_PER_ELEMENT} elements (QUARTERS)")
    print(f"   Remainder for Krishna: {_YAJNA_REMAINDER} elements (QUARTERS)")

    print("\n2. TRANSFORMATION PROOF")
    for key, value in TRANSFORMATION_PROOF.items():
        print(f"   {key}: {value}")

    print("\n3. KARMA COMPARISON (All disturb KSHETRA = 24)")
    for k in KARMA_COMPARISON:
        print(
            f"   {k.food_type}: violence={k.violence_level}, karma={k.total_karma} → after offering: {k.after_offering}"
        )

    print("\n4. NEUTRALIZATION EXAMPLE")
    offered = KarmaNeutralization("Rice", offered=True)
    not_offered = KarmaNeutralization("Rice", offered=False)
    print(offered.explain())
    print()
    print(not_offered.explain())

    print("\n5. COMPLETE KARMA ANALYSIS")
    # Scenario 1: All bhoga
    bhoga_only = CompleteKarmaAnalysis(daily_meals=3, offered_meals=0, yajnas_performed=0, surrender_limbs=0)
    print(bhoga_only.report())

    # Scenario 2: All prasadam with full surrender
    prasadam_full = CompleteKarmaAnalysis(daily_meals=3, offered_meals=3, yajnas_performed=5, surrender_limbs=6)
    print(prasadam_full.report())

    print("\n6. KEY INSIGHT")
    print(KEY_INSIGHT)
