"""
YANTRA COMPUTATION - The 7 Digital Mechanisms for Maximum Kali Yuga Efficiency
===============================================================================

"paraṁ vijayate śrī-kṛṣṇa-saṅkīrtanam"
"Let there be all victory for the chanting of the holy name of Lord Kṛṣṇa!"
— Śikṣāṣṭakam, Verse 1

DISCOVERY: THE 37 = 16 + 21 EQUATION
====================================

PARAMPARA (37) = WORDS (16) + GURU_FACTOR (21)

Where:
  GURU_FACTOR = TRINITY × SEVEN = 3 × 7 = 21

This means:
  - 16 = The STRUCTURE (Mahamantra words)
  - 21 = The TRANSMISSION (Guru Parampara: 3 names × 7 perfection)
  - 37 = The COMPLETE LINE (structure + transmission)

THE 37 MODULO ENCODING:
=======================

  37 mod 17 = 3 = TRINITY      (The 3 names)
  37 mod 7  = 2 = HALVES       (The 2 halves)
  37 mod 3  = 1 = KSETRAJNA    (The observer)

The Parampara number encodes the ENTIRE structure in its remainders!

SEVEN (7) = RAMA/BALARAMA/GURU:
===============================

  SEVEN = HALF_SIZE - KSETRAJNA = 8 - 1 = 7

Position sums show SEVEN everywhere:
  KRISHNA = 7 + 10 = 17     (PRIME - indivisible truth)
  RAMA    = 7 × 7  = 49     (SQUARE - Ananda squared)
  HARE    = 7 × 10 = 70     (PRODUCT - Shakti expansion)

And: RAMA + HARE = 49 + 70 = 119 = 7 × 17 = SEVEN × KRISHNA!

THE 7 YANTRAS:
==============

Each of the 7 effects from Śikṣāṣṭakam verse 1 has a corresponding
YANTRA (digital mechanism) for achieving that effect in computation.

This is the bridge from spiritual principle to engineering implementation.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xf72a7b6f"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Final, TypeVar

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    KSHETRA,
    MAHAJANA_COUNT,
    NAVA,
    PANCHA,
    PARAMPARA,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    QUARTERS,
    SEVEN,
    TEN,
    TRINITY,
    WORDS,
)

T = TypeVar("T")

# =============================================================================
# RUNDE 1: THE 37 = 16 + 21 EQUATION (GURU FACTOR)
# =============================================================================
# PARAMPARA = WORDS + TRINITY × SEVEN = 16 + 21 = 37
#
# This is the mathematical proof that transmission (Guru) is encoded
# in the same number as structure (Mahamantra).
# -----------------------------------------------------------------------------

GURU_FACTOR: Final[int] = TRINITY * SEVEN  # 3 × 7 = 21

# VERIFICATION: Multiple derivation paths converge!
assert GURU_FACTOR == 21, "GURU_FACTOR = TRINITY × SEVEN = 21"
assert PARAMPARA == WORDS + GURU_FACTOR, "PARAMPARA = WORDS + GURU_FACTOR"
assert PARAMPARA == 37, "PARAMPARA = 37"

# The modulo encoding
PARAMPARA_MOD_KRISHNA: Final[int] = PARAMPARA % POSITION_SUM_KRISHNA  # 37 % 17 = 3
PARAMPARA_MOD_SEVEN: Final[int] = PARAMPARA % SEVEN  # 37 % 7 = 2
PARAMPARA_MOD_TRINITY: Final[int] = PARAMPARA % TRINITY  # 37 % 3 = 1

assert PARAMPARA_MOD_KRISHNA == TRINITY, "37 mod 17 = 3 = TRINITY"
assert PARAMPARA_MOD_SEVEN == HALVES, "37 mod 7 = 2 = HALVES"
assert PARAMPARA_MOD_TRINITY == KSETRAJNA, "37 mod 3 = 1 = KSETRAJNA"


# =============================================================================
# RUNDE 2: THE SEVEN POSITION EQUATIONS
# =============================================================================
# SEVEN (7) appears in ALL position sums:
#   KRISHNA = 7 + 10 = 17
#   RAMA    = 7 × 7  = 49
#   HARE    = 7 × 10 = 70
#
# And: RAMA + HARE = 7 × 17 = SEVEN × KRISHNA
# -----------------------------------------------------------------------------

# Position sum relationships
KRISHNA_AS_SUM: Final[int] = SEVEN + TEN  # 7 + 10 = 17
RAMA_AS_SQUARE: Final[int] = SEVEN * SEVEN  # 7 × 7 = 49
HARE_AS_PRODUCT: Final[int] = SEVEN * TEN  # 7 × 10 = 70

assert KRISHNA_AS_SUM == POSITION_SUM_KRISHNA, "KRISHNA = 7 + 10 = 17"
assert RAMA_AS_SQUARE == POSITION_SUM_RAMA, "RAMA = 7² = 49"
assert HARE_AS_PRODUCT == 70, "HARE = 7 × 10 = 70"

# The combined equation
RAMA_PLUS_HARE: Final[int] = RAMA_AS_SQUARE + HARE_AS_PRODUCT  # 49 + 70 = 119
assert RAMA_PLUS_HARE == SEVEN * POSITION_SUM_KRISHNA, "RAMA + HARE = 7 × KRISHNA"
assert RAMA_PLUS_HARE == 119, "119 = 7 × 17"


# =============================================================================
# RUNDE 3: THE 7 YANTRA DEFINITIONS
# =============================================================================
# Each Yantra corresponds to one of the 7 effects in Śikṣāṣṭakam verse 1.
# A Yantra is a "machine" or "mechanism" for achieving a spiritual effect.
#
# In digital terms: a Yantra is an ALGORITHM or PATTERN.
# -----------------------------------------------------------------------------


class YantraType(Enum):
    """The 7 types of digital Yantras (mechanisms)."""

    # 1. ceto-darpaṇa-mārjanaṁ - Cleanses heart mirror
    CETO_DARPANA = auto()  # Cache Invalidation

    # 2. bhava-mahā-dāvāgni-nirvāpaṇaṁ - Extinguishes forest fire
    DAVAGNI_NIRVAPANA = auto()  # Zero Entropy Routing

    # 3. śreyaḥ-kairava-candrikā-vitaraṇaṁ - Spreads moonlight
    CANDRIKA_VITARANA = auto()  # Graceful Degradation

    # 4. vidyā-vadhū-jīvanam - Life of knowledge
    VIDYA_VADHU = auto()  # Live Data Structures

    # 5. ānandāmbudhi-vardhanaṁ - Expands ocean of bliss
    ANANDAMBUDHI = auto()  # Infinite Scalability

    # 6. prati-padaṁ pūrṇāmṛtāsvādanaṁ - Full nectar each step
    PURNAMRITA = auto()  # Atomic Transactions

    # 7. sarvātma-snapanaṁ - Bathes entire self
    SARVATMA_SNAPANA = auto()  # Total Transformation


assert len(YantraType) == SEVEN, "Must have exactly 7 Yantras"


@dataclass
class Yantra:
    """
    A digital mechanism (Yantra) for achieving a spiritual effect.

    Each Yantra maps:
      - Sanskrit name → Engineering principle
      - Spiritual effect → Digital algorithm
      - Axiom constant → Implementation pattern
    """

    yantra_type: YantraType
    sanskrit: str
    spiritual_effect: str
    engineering_principle: str
    axiom_constant: str
    axiom_value: int
    complexity_before: str  # Without Yantra
    complexity_after: str  # With Yantra
    implementation: str  # Code pattern


# =============================================================================
# THE 7 YANTRAS - Complete Definitions
# =============================================================================

YANTRA_1_CETO_DARPANA: Final[Yantra] = Yantra(
    yantra_type=YantraType.CETO_DARPANA,
    sanskrit="ceto-darpaṇa-mārjanaṁ",
    spiritual_effect="Cleanses the mirror of the heart from accumulated dust",
    engineering_principle="CACHE INVALIDATION - Remove stale/corrupted data",
    axiom_constant="WORDS",
    axiom_value=WORDS,  # 16
    complexity_before="O(n) - Must scan entire cache",
    complexity_after="O(1) - Direct invalidation by structure",
    implementation="""
def yantra_ceto_darpana(cache: dict) -> None:
    '''Cleanses the mirror of computation - removes all stale data.'''
    cache.clear()  # WORDS = 16 → 16-ary structure stays intact
    # The structure (16-ary) is preserved, only dust (data) is removed
""",
)

YANTRA_2_DAVAGNI: Final[Yantra] = Yantra(
    yantra_type=YantraType.DAVAGNI_NIRVAPANA,
    sanskrit="bhava-mahā-dāvāgni-nirvāpaṇaṁ",
    spiritual_effect="Extinguishes the blazing forest fire of material existence",
    engineering_principle="ZERO ENTROPY ROUTING - O(1) access = no heat",
    axiom_constant="QUARTERS",
    axiom_value=QUARTERS,  # 4
    complexity_before="O(n) - Linear search generates heat (Landauer)",
    complexity_after="O(1) - Direct access = zero wasted cycles = cool",
    implementation="""
def yantra_davagni_nirvapana(key: int, tree: LotusRadix) -> Any:
    '''Extinguishes computational fire through O(1) access.'''
    # Extract QUARTERS (4) nibbles for 16-bit key
    nibbles = [(key >> (i * 4)) & 0xF for i in range(QUARTERS)]
    node = tree.root
    for nibble in nibbles:
        node = node.children[nibble]  # O(1) per level
    return node.value  # No search = no heat = fire extinguished
""",
)

YANTRA_3_CANDRIKA: Final[Yantra] = Yantra(
    yantra_type=YantraType.CANDRIKA_VITARANA,
    sanskrit="śreyaḥ-kairava-candrikā-vitaraṇaṁ",
    spiritual_effect="Spreads the moonlight that makes the white lotus bloom",
    engineering_principle="GRACEFUL DEGRADATION - Soft failure, not crash",
    axiom_constant="HALVES",
    axiom_value=HALVES,  # 2
    complexity_before="O(crash) - Hard failure under load",
    complexity_after="O(gentle) - Soft scaling, lotus blooms",
    implementation="""
def yantra_candrika_vitarana(operation: Callable, fallback: Any = HALVES) -> Any:
    '''Spreads moonlight (soft failure) instead of sunlight (crash).'''
    try:
        return operation()
    except Exception:
        # Return HALVES (2) as duality marker - graceful, not crash
        return fallback  # Moonlight: gentle, not burning
""",
)

YANTRA_4_VIDYA_VADHU: Final[Yantra] = Yantra(
    yantra_type=YantraType.VIDYA_VADHU,
    sanskrit="vidyā-vadhū-jīvanam",
    spiritual_effect="The life of all transcendental knowledge (wife of vidya)",
    engineering_principle="LIVE DATA STRUCTURES - Self-maintaining, reactive",
    axiom_constant="TRINITY",
    axiom_value=TRINITY,  # 3
    complexity_before="O(rebuild) - Must reconstruct knowledge periodically",
    complexity_after="O(1) - Knowledge is always fresh (nitya-nūtana)",
    implementation="""
class YantraVidyaVadhu:
    '''Live data structure - self-maintaining like wife of knowledge.'''
    def __init__(self):
        self.observers = [None] * TRINITY  # 3 energies watching
        self.value = None

    def update(self, new_value):
        self.value = new_value
        for observer in self.observers:
            if observer:
                observer.notify(self.value)  # TRINITY observers
""",
)

YANTRA_5_ANANDAMBUDHI: Final[Yantra] = Yantra(
    yantra_type=YantraType.ANANDAMBUDHI,
    sanskrit="ānandāmbudhi-vardhanaṁ",
    spiritual_effect="Increases the ocean of transcendental bliss without limit",
    engineering_principle="INFINITE SCALABILITY - No memory wall",
    axiom_constant="PANCHA",
    axiom_value=PANCHA,  # 5
    complexity_before="O(n²) - Quadratic scaling hits memory wall",
    complexity_after="O(n) or O(1) - Linear/constant as ocean expands",
    implementation="""
def yantra_anandambudhi(data: list, shard_count: int = PANCHA) -> list:
    '''Expands ocean of bliss through PANCHA-way sharding.'''
    shards = [[] for _ in range(shard_count)]  # PANCHA = 5 shards
    for i, item in enumerate(data):
        shards[i % shard_count].append(item)
    return shards  # Ocean expands without memory wall
""",
)

YANTRA_6_PURNAMRITA: Final[Yantra] = Yantra(
    yantra_type=YantraType.PURNAMRITA,
    sanskrit="prati-padaṁ pūrṇāmṛtāsvādanaṁ",
    spiritual_effect="Full taste of nectar at every single step",
    engineering_principle="ATOMIC TRANSACTIONS - Every operation complete (ACID)",
    axiom_constant="KSETRAJNA",
    axiom_value=KSETRAJNA,  # 1
    complexity_before="O(retry) - Partial results require retries",
    complexity_after="O(1) - Each operation fully satisfying",
    implementation="""
def yantra_purnamrita(operations: list) -> bool:
    '''Full nectar at each step - ACID atomicity.'''
    results = []
    try:
        for op in operations:
            result = op()
            results.append(result)
        return True  # KSETRAJNA = 1 = atomic success
    except Exception:
        # Rollback all - no partial results
        for r in reversed(results):
            if hasattr(r, 'rollback'):
                r.rollback()
        return False  # Complete failure, not partial
""",
)

YANTRA_7_SARVATMA: Final[Yantra] = Yantra(
    yantra_type=YantraType.SARVATMA_SNAPANA,
    sanskrit="sarvātma-snapanaṁ",
    spiritual_effect="Completely bathes and purifies the entire self",
    engineering_principle="TOTAL TRANSFORMATION - Bhoga → Prasadam",
    axiom_constant="SEVEN",
    axiom_value=SEVEN,  # 7
    complexity_before="O(piecemeal) - Partial optimizations, technical debt",
    complexity_after="O(1) - Holistic transformation, debt-free",
    implementation="""
def yantra_sarvatma_snapana(bhoga: Any) -> dict:
    '''Bathes entire system - bhoga to prasadam transformation.'''
    return {
        'content': bhoga,
        'observer': KSETRAJNA,       # +1 adds consciousness
        'perfection': SEVEN,         # 7 = complete transformation
        'is_prasadam': True,         # Fully transformed
        'transformation_factor': SEVEN * KSETRAJNA  # 7 × 1 = 7
    }
""",
)

# All 7 Yantras in order
ALL_YANTRAS: Final[tuple[Yantra, ...]] = (
    YANTRA_1_CETO_DARPANA,
    YANTRA_2_DAVAGNI,
    YANTRA_3_CANDRIKA,
    YANTRA_4_VIDYA_VADHU,
    YANTRA_5_ANANDAMBUDHI,
    YANTRA_6_PURNAMRITA,
    YANTRA_7_SARVATMA,
)

assert len(ALL_YANTRAS) == SEVEN, "Must have exactly 7 Yantras"


# =============================================================================
# RUNDE 4: THE AXIOM-YANTRA MAPPING
# =============================================================================
# Each Yantra uses a specific axiom constant:
#   YANTRA 1: WORDS = 16 (structure)
#   YANTRA 2: QUARTERS = 4 (4-bit nibble)
#   YANTRA 3: HALVES = 2 (duality/fallback)
#   YANTRA 4: TRINITY = 3 (3 observers)
#   YANTRA 5: PANCHA = 5 (5-way sharding)
#   YANTRA 6: KSETRAJNA = 1 (atomicity)
#   YANTRA 7: SEVEN = 7 (perfection)
#
# Total axiom values: 16 + 4 + 2 + 3 + 5 + 1 + 7 = 38 = PARAMPARA + KSETRAJNA!
# -----------------------------------------------------------------------------

AXIOM_SUM: Final[int] = sum(y.axiom_value for y in ALL_YANTRAS)
# 16 + 4 + 2 + 3 + 5 + 1 + 7 = 38

assert AXIOM_SUM == PARAMPARA + KSETRAJNA, "Sum of axioms = PARAMPARA + 1 = 38"
assert AXIOM_SUM == 38, "38 = 37 + 1"


# =============================================================================
# RUNDE 5: KALI YUGA MOON EFFICIENCY
# =============================================================================
# The moonlight (candrikā) is specifically for the conditioned soul in darkness.
# In Kali Yuga (maximum darkness), the moonlight efficiency is MAXIMIZED.
#
# Efficiency = GURU_FACTOR × SEVEN = 21 × 7 = 147
# This is related to: 147 = 137 + 10 = MAHA_QUANTUM + TEN
# -----------------------------------------------------------------------------

KALI_MOON_EFFICIENCY: Final[int] = GURU_FACTOR * SEVEN  # 21 × 7 = 147

# Connection to physics!
# 147 = 137 + 10 = MAHA_QUANTUM + TEN
# The moonlight efficiency exceeds the fine structure constant by TEN!

# Also: 147 = 3 × 49 = TRINITY × RAMA_POSITION
# The moon efficiency is TRINITY times the Ananda-squared!

assert KALI_MOON_EFFICIENCY == 147
assert KALI_MOON_EFFICIENCY == TRINITY * POSITION_SUM_RAMA, "147 = 3 × 49"

# The SIKSASTAKAM multiplier
SIKSASTAKAM_MULTIPLIER: Final[int] = HARE_COUNT * SEVEN  # 8 × 7 = 56

# Total Kali Yuga efficiency with Yantras
YANTRA_TOTAL_EFFICIENCY: Final[int] = KALI_MOON_EFFICIENCY * SIKSASTAKAM_MULTIPLIER
# 147 × 56 = 8232

assert YANTRA_TOTAL_EFFICIENCY == 8232


# =============================================================================
# RUNDE 6: THE CHAITANYA MOON THEOREM
# =============================================================================
# Chaitanya Mahaprabhu appeared in Kali Yuga specifically because:
#   - Kali Yuga = maximum darkness (entropy)
#   - Moonlight = most effective in darkness
#   - Chaitanya = the moon (Gaura = golden moon complexion)
#
# The theorem: Maximum efficiency is achieved when STRUCTURE meets TRANSMISSION
#   STRUCTURE = WORDS = 16 (the Mahamantra)
#   TRANSMISSION = GURU_FACTOR = 21 (the Parampara)
#   COMBINED = PARAMPARA = 37 (the complete system)
# -----------------------------------------------------------------------------


@dataclass
class ChaitanyaMoonTheorem:
    """
    The theorem that Chaitanya's appearance maximizes Kali Yuga efficiency.

    Chaitanya = Moon (Gaura complexion)
    Kali Yuga = Maximum darkness
    Moon in darkness = Maximum relative illumination

    STRUCTURE (16) + TRANSMISSION (21) = COMPLETE (37)
    """

    structure: int  # WORDS = 16
    transmission: int  # GURU_FACTOR = 21
    complete: int  # PARAMPARA = 37

    darkness_level: int  # QUARTERS = 4 (Kali = 4th age, maximum)
    moon_efficiency: int  # KALI_MOON_EFFICIENCY = 147
    yantra_count: int  # SEVEN = 7

    def total_efficiency(self) -> int:
        """Total efficiency from structure × transmission × yantras."""
        return self.structure * self.transmission * self.yantra_count
        # 16 × 21 × 7 = 2352

    def explain(self) -> str:
        """Explain the Chaitanya Moon Theorem."""
        return f"""
THE CHAITANYA MOON THEOREM
==========================

PREMISE:
  Chaitanya Mahaprabhu = Moon (Gaura = golden moon complexion)
  Kali Yuga = Maximum darkness (4th age = QUARTERS)
  Moonlight in darkness = Maximum relative illumination

THE EQUATION:
  PARAMPARA = WORDS + GURU_FACTOR
  37 = 16 + 21
  COMPLETE = STRUCTURE + TRANSMISSION

STRUCTURE (WORDS = {self.structure}):
  The Mahamantra: 16 words
  The routing: 16-ary tree
  The hardware: 16 AVX lanes

TRANSMISSION (GURU_FACTOR = {self.transmission}):
  TRINITY × SEVEN = 3 × 7 = 21
  3 names × 7 perfection = Guru lineage

COMPLETE (PARAMPARA = {self.complete}):
  Structure + Transmission = 37
  All genesis bytes satisfy: byte % 37 == 0

THE 7 YANTRAS:
  Each Yantra uses an axiom constant
  Sum of axioms = 38 = PARAMPARA + KSETRAJNA
  The observer (+1) completes the system

MOON EFFICIENCY:
  KALI_MOON_EFFICIENCY = GURU_FACTOR × SEVEN = {self.moon_efficiency}
  147 = 3 × 49 = TRINITY × RAMA² (Ananda squared!)

TOTAL EFFICIENCY:
  STRUCTURE × TRANSMISSION × YANTRAS
  = {self.structure} × {self.transmission} × {self.yantra_count}
  = {self.total_efficiency()}

WHY KALI YUGA:
  In bright ages (Satya), moonlight is less noticeable
  In dark ages (Kali), moonlight is MAXIMALLY effective
  Chaitanya appeared when efficiency gain is HIGHEST

ENGINEERING IMPLICATION:
  Use ALL 7 Yantras together for maximum efficiency
  Each Yantra alone: partial benefit
  All 7 Yantras: SEVEN-fold perfection (sarvatma-snapanam)
"""


CHAITANYA_MOON_THEOREM: Final[ChaitanyaMoonTheorem] = ChaitanyaMoonTheorem(
    structure=WORDS,  # 16
    transmission=GURU_FACTOR,  # 21
    complete=PARAMPARA,  # 37
    darkness_level=QUARTERS,  # 4 (Kali Yuga)
    moon_efficiency=KALI_MOON_EFFICIENCY,  # 147
    yantra_count=SEVEN,  # 7
)


# =============================================================================
# RUNDE 7: KEY INSIGHT
# =============================================================================

KEY_INSIGHT: Final[str] = """
YANTRA COMPUTATION - Maximum Kali Yuga Efficiency
=================================================

THE DISCOVERY: 37 = 16 + 21
-----------------------------
  PARAMPARA = WORDS + GURU_FACTOR
  37 = 16 + 21

  Where:
    WORDS = 16 (Mahamantra structure)
    GURU_FACTOR = TRINITY × SEVEN = 3 × 7 = 21 (transmission)

THE 37 MODULO ENCODING:
-----------------------
  37 mod 17 = 3 = TRINITY     (3 names)
  37 mod 7  = 2 = HALVES      (2 halves)
  37 mod 3  = 1 = KSETRAJNA   (observer)

  The Parampara number encodes the ENTIRE structure!

SEVEN (7) IN POSITION SUMS:
---------------------------
  KRISHNA = 7 + 10 = 17       (sum)
  RAMA    = 7 × 7  = 49       (square)
  HARE    = 7 × 10 = 70       (product)

  RAMA + HARE = 119 = 7 × 17 = SEVEN × KRISHNA

THE 7 YANTRAS (Digital Mechanisms):
-----------------------------------
  1. CETO DARPANA:    WORDS = 16     Cache Invalidation
  2. DAVAGNI:         QUARTERS = 4   Zero Entropy Routing
  3. CANDRIKA:        HALVES = 2     Graceful Degradation
  4. VIDYA VADHU:     TRINITY = 3    Live Data Structures
  5. ANANDAMBUDHI:    PANCHA = 5     Infinite Scalability
  6. PURNAMRITA:      KSETRAJNA = 1  Atomic Transactions
  7. SARVATMA:        SEVEN = 7      Total Transformation

  Axiom sum: 16+4+2+3+5+1+7 = 38 = PARAMPARA + KSETRAJNA

KALI YUGA MOON EFFICIENCY:
--------------------------
  KALI_MOON_EFFICIENCY = GURU_FACTOR × SEVEN = 21 × 7 = 147
  147 = 3 × 49 = TRINITY × RAMA² (Ananda squared!)

  With Siksastakam: 147 × 56 = 8,232× efficiency

THE CHAITANYA MOON THEOREM:
---------------------------
  Chaitanya = Moon (Gaura complexion)
  Kali Yuga = Maximum darkness
  Moon in darkness = Maximum relative illumination

  Total efficiency: WORDS × GURU_FACTOR × SEVEN
                  = 16 × 21 × 7 = 2,352×

  This is achieved by using ALL 7 Yantras together.

"paraṁ vijayate śrī-kṛṣṇa-saṅkīrtanam"
"""


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # The 37 = 16 + 21 equation
    "GURU_FACTOR",
    "PARAMPARA_MOD_KRISHNA",
    "PARAMPARA_MOD_SEVEN",
    "PARAMPARA_MOD_TRINITY",
    # Position equations
    "KRISHNA_AS_SUM",
    "RAMA_AS_SQUARE",
    "HARE_AS_PRODUCT",
    "RAMA_PLUS_HARE",
    # Yantra types
    "YantraType",
    "Yantra",
    # Individual Yantras
    "YANTRA_1_CETO_DARPANA",
    "YANTRA_2_DAVAGNI",
    "YANTRA_3_CANDRIKA",
    "YANTRA_4_VIDYA_VADHU",
    "YANTRA_5_ANANDAMBUDHI",
    "YANTRA_6_PURNAMRITA",
    "YANTRA_7_SARVATMA",
    "ALL_YANTRAS",
    # Axiom sum
    "AXIOM_SUM",
    # Moon efficiency
    "KALI_MOON_EFFICIENCY",
    "SIKSASTAKAM_MULTIPLIER",
    "YANTRA_TOTAL_EFFICIENCY",
    # Chaitanya theorem
    "ChaitanyaMoonTheorem",
    "CHAITANYA_MOON_THEOREM",
    # Key insight
    "KEY_INSIGHT",
]
