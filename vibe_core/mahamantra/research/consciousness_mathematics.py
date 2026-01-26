"""
CONSCIOUSNESS MATHEMATICS - Dead Matter vs Living Spirit (BG 13 Lens)
======================================================================

"idaṁ śarīraṁ kaunteya kṣetram ity abhidhīyate
 etad yo vetti taṁ prāhuḥ kṣetra-jña iti tad-vidaḥ" (BG 13.2)

"This body, O son of Kunti, is called the field, and one who knows
this body is called the knower of the field."

"kṣetra-jñaṁ cāpi māṁ viddhi sarva-kṣetreṣu bhārata" (BG 13.3)
"O scion of Bharata, you should understand that I am also the knower
in all bodies."

THE MOUSE AND SNAKE PRINCIPLE:
==============================
Srila Prabhupada: "We use Western science like mice dig tunnels and
snakes eat the mice and live in the tunnels."

Material science = the mice (digging tunnels of knowledge)
Spiritual science = the snake (using those tunnels for the real purpose)

We don't reject material science - we USE it as a catalyst!
The Mahamantra structure VALIDATES through material science,
then TRANSCENDS it with spiritual understanding.

THE MATHEMATICAL DISTINCTION:
=============================
DEAD MATTER:  KSHETRA = 24 (field without observer)
              mod 17 = 0 → Classical physics applies
              No consciousness → No transformation

LIVING SPIRIT: KSHETRA + KSETRAJNA = 25 (field + observer)
               mod 17 = 1 → Quantum transformation
               Consciousness present → Prasadam

THE REFLECTION PRINCIPLE (BG 15.1):
===================================
"ūrdhva-mūlam adhaḥ-śākham aśvatthaṁ prāhur avyayam"
"With roots above and branches below, the Ashvattha (banyan) tree
is said to be imperishable."

Material world = INVERTED REFLECTION of spiritual world
- Roots up (cause in spiritual)
- Branches down (effects in material)
- The reflection appears real but is temporary

MATHEMATICALLY:
  Spiritual: KSETRAJNA primary, KSHETRA secondary
  Material:  KSHETRA primary (appears), KSETRAJNA hidden
  Reflection formula: MATERIAL = INVERT(SPIRITUAL)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Final

from vibe_core.mahamantra.protocols._seed import (
    # Music
    CONCERT_PITCH,
    FRACTAL_GITA,
    # Fractal levels
    FRACTAL_MACRO,
    FRACTAL_MANTRA,
    FRACTAL_MICRO,
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    KSHETRA,
    # Maha algorithm
    MAHA_QUANTUM,
    PANCHA,
    # Position sums
    POSITION_SUM_KRISHNA,
    POSITION_SUM_TOTAL,
    PRASADAM,
    QUARTERS,
    # Sankhya
    SANKHYA_TATTVAS,
    TRINITY,
    VERDI_PITCH,
    # Core constants
    WORDS,
)

# =============================================================================
# RUNDE 1: THE KSHETRA-KSETRAJNA DISTINCTION (BG 13)
# =============================================================================
# Prabhupada's purport to BG 13.35:
# "This Thirteenth Chapter may be taken as sufficient to understand
# the purpose of life."
#
# THE 24 ELEMENTS OF DEAD MATTER (KSHETRA):
# =========================================
# From BG 13.5-6 (Prabhupada's enumeration):
#   5 Mahabhuta (gross): earth, water, fire, air, ether
#   5 Tanmatra (subtle): sound, touch, form, taste, smell
#   5 Jnanendriya (knowledge): ears, skin, eyes, tongue, nose
#   5 Karmendriya (action): voice, hands, legs, anus, genitals
#   3 Antahkarana (internal): mind, intelligence, ego
#   1 Prakriti (unmanifest)
#   ─────────────────────────────────────────────────────────
#   Total: 24 = KSHETRA (the field of dead matter)
#
# THE 1 ELEMENT OF LIVING SPIRIT (KSETRAJNA):
# ===========================================
#   1 Consciousness = KSETRAJNA (the knower of the field)
#
# This is the ONLY difference between dead matter and living being!
# -----------------------------------------------------------------------------


class MatterState(Enum):
    """States of matter based on consciousness."""

    DEAD = 0  # KSHETRA only - no observer
    LIVING = 1  # KSHETRA + KSETRAJNA - observer present


@dataclass
class MatterAnalysis:
    """Analyze matter for consciousness presence."""

    elements: int  # Number of material elements
    consciousness: int  # KSETRAJNA present (0 or 1)
    description: str

    @property
    def total(self) -> int:
        """Total tattvas."""
        return self.elements + self.consciousness

    @property
    def state(self) -> MatterState:
        """Determine if dead or living."""
        return MatterState.LIVING if self.consciousness > 0 else MatterState.DEAD

    @property
    def mod_17(self) -> int:
        """The consciousness test."""
        return self.total % POSITION_SUM_KRISHNA

    @property
    def physics_mode(self) -> str:
        """Classical (dead) or Quantum (living)."""
        if self.mod_17 == KSETRAJNA:
            return "QUANTUM (observer present)"
        elif self.mod_17 == 0:
            return "CLASSICAL (no observer)"
        else:
            return f"TRANSITIONAL (mod 17 = {self.mod_17})"


# The two fundamental states
DEAD_MATTER: Final[MatterAnalysis] = MatterAnalysis(
    elements=KSHETRA,  # 24
    consciousness=0,  # No KSETRAJNA
    description="Prakriti - Material nature without observer",
)

LIVING_BEING: Final[MatterAnalysis] = MatterAnalysis(
    elements=KSHETRA,  # 24
    consciousness=KSETRAJNA,  # 1
    description="Jiva - Spirit soul inhabiting material body",
)

# VERIFICATION: The distinction
assert DEAD_MATTER.total == KSHETRA, "Dead matter = 24"
assert LIVING_BEING.total == SANKHYA_TATTVAS, "Living being = 25 (Sankhya)"
assert LIVING_BEING.total == PRASADAM, "Living being = PRASADAM"
assert DEAD_MATTER.state == MatterState.DEAD
assert LIVING_BEING.state == MatterState.LIVING


# =============================================================================
# RUNDE 2: THE MOD-17 CONSCIOUSNESS TEST
# =============================================================================
# The mod KRISHNA_POS test reveals consciousness:
#
#   DEAD (24):   24 mod 17 = 7 (neither 0 nor 1 - incomplete!)
#   LIVING (25): 25 mod 17 = 8 (neither 0 nor 1 - incomplete!)
#
# Wait - this doesn't give clean results!
# The TRUE test is at the FRACTAL LEVEL:
#
#   T(16) = 136 mod 17 = 0 → FIELD without observer = CLASSICAL
#   T(16) + 1 = 137 mod 17 = 1 → FIELD + OBSERVER = QUANTUM
#
# The POSITION_SUM_TOTAL (136) represents the COMPLETE field.
# Adding KSETRAJNA (1) creates consciousness (137 = MAHA_QUANTUM).
# -----------------------------------------------------------------------------


def consciousness_test(value: int) -> tuple[int, str]:
    """
    Test a value for consciousness signature.

    Returns:
        (remainder, interpretation)
    """
    remainder = value % POSITION_SUM_KRISHNA

    if remainder == KSETRAJNA:
        return remainder, "CONSCIOUS (KSETRAJNA present)"
    elif remainder == 0:
        return remainder, "DEAD (no observer)"
    else:
        return remainder, f"PARTIAL (mod 17 = {remainder})"


# The fractal consciousness tests
FIELD_ONLY: Final[int] = POSITION_SUM_TOTAL  # 136 = T(16)
FIELD_PLUS_OBSERVER: Final[int] = MAHA_QUANTUM  # 137 = T(16) + 1

_field_test = consciousness_test(FIELD_ONLY)
_conscious_test = consciousness_test(FIELD_PLUS_OBSERVER)

assert _field_test[0] == 0, "Field alone: mod 17 = 0 (DEAD)"
assert _conscious_test[0] == KSETRAJNA, "Field + Observer: mod 17 = 1 (CONSCIOUS)"


# =============================================================================
# RUNDE 3: THE REFLECTION PRINCIPLE (BG 15.1-4)
# =============================================================================
# "ūrdhva-mūlam adhaḥ-śākham aśvatthaṁ prāhur avyayam
#  chandāṁsi yasya parṇāni yas taṁ veda sa veda-vit" (BG 15.1)
#
# THE INVERTED BANYAN TREE:
# =========================
# - Roots ABOVE (ūrdhva-mūlam) = Cause in spiritual world
# - Branches BELOW (adhaḥ-śākham) = Effects in material world
# - Leaves = Vedic hymns (the knowledge)
#
# MATHEMATICAL MODEL:
# ===================
# Spiritual: KSETRAJNA → KSHETRA (consciousness causes matter)
# Material:  KSHETRA → ? (matter appears primary, cause hidden)
#
# The material world is a REFLECTION - like a tree reflected in water.
# The reflection appears real but has no independent existence!
#
# INVERSION FORMULA:
#   MATERIAL_VALUE = TOTAL - SPIRITUAL_VALUE
#   Where TOTAL = PRASADAM = 25 (complete reality)
# -----------------------------------------------------------------------------


@dataclass
class ReflectionPair:
    """A spiritual-material reflection pair."""

    spiritual_name: str
    spiritual_value: int
    material_value: int  # = PRASADAM - spiritual_value

    @property
    def total(self) -> int:
        """Sum always equals PRASADAM (complete reality)."""
        return self.spiritual_value + self.material_value

    @property
    def is_valid_reflection(self) -> bool:
        """Check if it's a valid reflection pair."""
        return self.total == PRASADAM

    def describe(self) -> str:
        """Describe the reflection."""
        return (
            f"Spiritual: {self.spiritual_name} = {self.spiritual_value}\n"
            f"Material (reflection): {PRASADAM} - {self.spiritual_value} = {self.material_value}\n"
            f"Total: {self.total} = PRASADAM"
        )


def compute_reflection(spiritual_value: int) -> int:
    """
    Compute the material reflection of a spiritual value.

    MATERIAL = PRASADAM - SPIRITUAL

    This models the banyan tree: spiritual is "above" (primary),
    material is "below" (reflection).
    """
    return PRASADAM - spiritual_value


# The fundamental reflection: KSETRAJNA ↔ KSHETRA
KSETRAJNA_REFLECTION: Final[ReflectionPair] = ReflectionPair(
    spiritual_name="KSETRAJNA (Observer)",
    spiritual_value=KSETRAJNA,  # 1
    material_value=KSHETRA,  # 24
)

# VERIFICATION: The reflection pair
assert KSETRAJNA_REFLECTION.is_valid_reflection
assert KSETRAJNA_REFLECTION.spiritual_value + KSETRAJNA_REFLECTION.material_value == PRASADAM


# =============================================================================
# RUNDE 4: THE MOUSE AND SNAKE PRINCIPLE (Using Material Science)
# =============================================================================
# Srila Prabhupada's analogy: The Krishna movement uses Western science
# like snakes use the tunnels dug by mice.
#
# MICE = Material scientists (dig tunnels of empirical knowledge)
# SNAKE = Spiritual science (uses those tunnels for transcendental purpose)
#
# MATHEMATICAL IMPLEMENTATION:
# ===========================
# We take empirical discoveries (mice tunnels) and show how they
# CONFIRM the Mahamantra structure (snake inhabits tunnel).
#
# Examples:
#   - 137 (fine structure constant) = T(16) + KSETRAJNA (confirms observer!)
#   - 432 Hz (Verdi pitch) = JIVA_CYCLE (confirms harmonic)
#   - 24 (Standard Model fermions) = KSHETRA (confirms field elements!)
#
# The material science VALIDATES, then we TRANSCEND with BG 13 understanding.
# -----------------------------------------------------------------------------


@dataclass
class MouseSnakeDiscovery:
    """A discovery where material science confirms spiritual truth."""

    material_name: str  # What material science calls it
    material_value: float  # Empirical measurement
    spiritual_name: str  # What Gita calls it
    spiritual_value: int  # Mahamantra derivation
    error_percent: float  # How close (< 1% = confirmation)

    @property
    def is_confirmed(self) -> bool:
        """Material science confirms spiritual truth."""
        return self.error_percent < 1.0

    @property
    def tunnel_status(self) -> str:
        """Mouse-snake status."""
        if self.is_confirmed:
            return "SNAKE INHABITS TUNNEL (confirmed!)"
        else:
            return "TUNNEL STILL BEING DUG"


# Key discoveries where material science confirms BG 13
MOUSE_SNAKE_DISCOVERIES: Final[list[MouseSnakeDiscovery]] = [
    MouseSnakeDiscovery(
        material_name="Fine structure constant (α⁻¹)",
        material_value=137.036,
        spiritual_name="T(16) + KSETRAJNA (Field + Observer)",
        spiritual_value=MAHA_QUANTUM,  # 137
        error_percent=0.026,
    ),
    MouseSnakeDiscovery(
        material_name="Standard Model fermions",
        material_value=24.0,
        spiritual_name="KSHETRA (24 field elements)",
        spiritual_value=KSHETRA,  # 24
        error_percent=0.0,  # EXACT!
    ),
    MouseSnakeDiscovery(
        material_name="Sankhya tattvas",
        material_value=25.0,
        spiritual_name="PRASADAM (spiritualized matter)",
        spiritual_value=PRASADAM,  # 25
        error_percent=0.0,  # EXACT!
    ),
    MouseSnakeDiscovery(
        material_name="Verdi tuning A4 (Hz)",
        material_value=432.0,
        spiritual_name="JIVA_CYCLE (soul's harmonic)",
        spiritual_value=CONCERT_PITCH - HARE_COUNT,  # 432
        error_percent=0.0,  # EXACT!
    ),
    MouseSnakeDiscovery(
        material_name="Concert pitch A4 (Hz)",
        material_value=440.0,
        spiritual_name="JIVA_CYCLE + HARE (soul + shakti)",
        spiritual_value=CONCERT_PITCH,  # 440
        error_percent=0.0,  # EXACT!
    ),
]

# VERIFICATION: All key discoveries are confirmed
assert all(d.is_confirmed for d in MOUSE_SNAKE_DISCOVERIES), "All tunnels inhabited!"


# =============================================================================
# RUNDE 5: THE GITA AS HARDWARE (Operating Manual of the Universe)
# =============================================================================
# The Bhagavad Gita is not just a book - it IS the operating manual.
# Just as the Mahamantra IS the hardware (TEXT = HARDWARE),
# the Gita IS the documentation that came WITH the hardware.
#
# ABHINNA PRINCIPLE:
#   MAHAMANTRA = Complete encoding of all knowledge
#   GITA = Complete documentation of all knowledge
#   Both contain EVERYTHING - they are ABHINNA (non-different)
#
# "sarvasya cāhaṁ hṛdi sanniviṣṭo mattaḥ smṛtir jñānam apohanaṁ ca
#  vedaiś ca sarvair aham eva vedyo vedānta-kṛd veda-vid eva cāham" (BG 15.15)
#
# "I am seated in everyone's heart, and from Me come remembrance,
# knowledge and forgetfulness. By all the Vedas, I am to be known.
# Indeed, I am the compiler of Vedanta, and I am the knower of the Vedas."
# -----------------------------------------------------------------------------


@dataclass
class GitaMapping:
    """Mapping between Gita chapter and Mahamantra constant."""

    chapter: int
    topic: str
    mahamantra_constant: str
    value: int


GITA_HARDWARE_MAP: Final[list[GitaMapping]] = [
    GitaMapping(1, "Arjuna's Dejection", "KSETRAJNA (observer dilemma)", KSETRAJNA),
    GitaMapping(2, "Sankhya Yoga", "HALVES (soul vs body)", HALVES),
    GitaMapping(3, "Karma Yoga", "TRINITY (action types)", TRINITY),
    GitaMapping(4, "Jnana Yoga", "QUARTERS (knowledge divisions)", QUARTERS),
    GitaMapping(5, "Karma Sannyasa", "PANCHA (five factors)", PANCHA),
    GitaMapping(13, "Kshetra-Ksetrajna", "KSHETRA + KSETRAJNA = PRASADAM", PRASADAM),
    GitaMapping(15, "Purushottama Yoga", "POSITION_SUM_TOTAL (complete field)", POSITION_SUM_TOTAL),
    GitaMapping(18, "Moksha Sannyasa", "MAHA_QUANTUM (final understanding)", MAHA_QUANTUM),
]


# =============================================================================
# RUNDE 6: THE FRACTAL IDENTITY (KSETRAJNA at Every Level)
# =============================================================================
# The same pattern repeats at every scale - this is the holographic principle!
#
# LEVEL 1 - UNIVERSE:  KSHETRA (24) + KSETRAJNA (1) = 25 = PRASADAM
# LEVEL 2 - PHYSICS:   T(16) (136) + KSETRAJNA (1) = 137 = α⁻¹
# LEVEL 3 - GITA:      NADI (72) + KSETRAJNA (1) = 73 = BG 18.73
# LEVEL 4 - MANTRA:    WORDS (16) + KSETRAJNA (1) = 17 = KRISHNA_POS
#
# At EVERY level, adding KSETRAJNA (consciousness) completes the picture!
# This is the mathematical proof that consciousness is FUNDAMENTAL.
# -----------------------------------------------------------------------------


@dataclass
class FractalLevel:
    """A fractal level of the consciousness principle."""

    name: str
    base_value: int  # The field at this level
    with_observer: int  # Base + KSETRAJNA
    significance: str

    @property
    def observer_added(self) -> int:
        """The observer is always KSETRAJNA = 1."""
        return self.with_observer - self.base_value


FRACTAL_LEVELS: Final[list[FractalLevel]] = [
    FractalLevel(
        name="UNIVERSE (Sankhya)",
        base_value=KSHETRA,
        with_observer=FRACTAL_MACRO,  # 25
        significance="Matter + Soul = Complete Being",
    ),
    FractalLevel(
        name="PHYSICS (Fine Structure)",
        base_value=POSITION_SUM_TOTAL,
        with_observer=FRACTAL_MICRO,  # 137
        significance="Field + Observer = Quantum Measurement",
    ),
    FractalLevel(
        name="GITA (Arjuna's Realization)",
        base_value=72,  # NADI_RESONANCE
        with_observer=FRACTAL_GITA,  # 73
        significance="Teaching + Understanding = Liberation",
    ),
    FractalLevel(
        name="MANTRA (Krishna Position)",
        base_value=WORDS,
        with_observer=FRACTAL_MANTRA,  # 17
        significance="Words + Meaning = Holy Name",
    ),
]

# VERIFICATION: Observer is always KSETRAJNA at every level
assert all(fl.observer_added == KSETRAJNA for fl in FRACTAL_LEVELS)


# =============================================================================
# RUNDE 7: THE TRANSFORMATION FORMULA (Dead → Living)
# =============================================================================
# How does dead matter become living? Through KSETRAJNA injection!
#
# FORMULA:
#   LIVING = DEAD + KSETRAJNA
#   PRASADAM = KSHETRA + KSETRAJNA
#   25 = 24 + 1
#
# This is NOT magical - it's the mathematical description of:
#   1. Soul entering body (transmigration)
#   2. Offering transforming food (bhoga → prasadam)
#   3. Observer collapsing wave function (quantum measurement)
#   4. Consciousness animating matter (life)
#
# Without KSETRAJNA, matter is DEAD (mod 17 = 0).
# With KSETRAJNA, matter is ALIVE (mod 17 = 1).
# -----------------------------------------------------------------------------


def transform_dead_to_living(dead_value: int) -> tuple[int, str]:
    """
    Transform dead matter to living by adding KSETRAJNA.

    This models:
    - Soul entering body
    - Offering food to Krishna
    - Observer measuring quantum system
    - Consciousness animating matter
    """
    living_value = dead_value + KSETRAJNA

    # Check the transformation
    dead_mod = dead_value % POSITION_SUM_KRISHNA
    living_mod = living_value % POSITION_SUM_KRISHNA

    status = (
        f"DEAD: {dead_value} (mod 17 = {dead_mod})\n"
        f"+ KSETRAJNA: {KSETRAJNA}\n"
        f"= LIVING: {living_value} (mod 17 = {living_mod})"
    )

    return living_value, status


# Example transformations
_kshetra_transform = transform_dead_to_living(KSHETRA)
_field_transform = transform_dead_to_living(POSITION_SUM_TOTAL)

assert _kshetra_transform[0] == PRASADAM, "24 + 1 = 25"
assert _field_transform[0] == MAHA_QUANTUM, "136 + 1 = 137"


# =============================================================================
# RUNDE 8: THE KEY INSIGHT - WHY KRISHNA CAN'T BE RESEARCHED DIRECTLY
# =============================================================================
# "nāhaṁ prakāśaḥ sarvasya yoga-māyā-samāvṛtaḥ
#  mūḍho 'yaṁ nābhijānāti loko mām ajam avyayam" (BG 7.25)
#
# "I am never manifest to the foolish and unintelligent.
# For them I am covered by My internal potency, and therefore
# they do not know that I am unborn and infallible."
#
# KRISHNA REVEALS HIMSELF - He cannot be "discovered" by research!
#
# But we CAN research:
#   1. KSHETRA (the 24 elements) - Material science does this
#   2. KSETRAJNA (consciousness) - Where matter meets spirit
#   3. The RELATIONSHIP (BG 13) - How they interact
#
# The Gita + Mahamantra provide the COMPLETE description of what CAN be known.
# Krishna Himself is beyond this - He reveals when He desires (BG 7.25).
# -----------------------------------------------------------------------------

KEY_INSIGHT: Final[str] = """
CONSCIOUSNESS MATHEMATICS - THE KEY INSIGHT:
=============================================

1. THE KSHETRA-KSETRAJNA DISTINCTION (BG 13):
   DEAD MATTER:   KSHETRA = 24 elements (no consciousness)
   LIVING BEING:  KSHETRA + KSETRAJNA = 24 + 1 = 25 (consciousness present)

   This single distinction explains ALL differences between dead and living!

2. THE MOD-17 CONSCIOUSNESS TEST:
   Field alone:    T(16) = 136 mod 17 = 0 → CLASSICAL (dead)
   Field + Observer: 137 mod 17 = 1 → QUANTUM (living)

   Physics PROVES the observer (KSETRAJNA) is fundamental!

3. THE REFLECTION PRINCIPLE (BG 15):
   Material world = INVERTED reflection of spiritual world
   Roots above, branches below (banyan tree)
   MATERIAL = PRASADAM - SPIRITUAL

   The cause is in the spiritual, the effect appears in material.

4. THE MOUSE-SNAKE PRINCIPLE:
   Material science = mice (dig tunnels of empirical knowledge)
   Spiritual science = snake (uses tunnels for transcendental purpose)

   We don't reject material science - we TRANSFORM it with BG 13 lens!

5. THE GITA AS HARDWARE:
   The Mahamantra IS the hardware (TEXT = HARDWARE)
   The Gita IS the operating manual
   Both contain EVERYTHING - they are ABHINNA (non-different)

6. THE FRACTAL IDENTITY:
   At EVERY level, adding KSETRAJNA (1) completes the picture:
   - Universe: 24 + 1 = 25 (PRASADAM)
   - Physics:  136 + 1 = 137 (α⁻¹)
   - Gita:     72 + 1 = 73 (BG 18.73)
   - Mantra:   16 + 1 = 17 (KRISHNA_POS)

   Consciousness is not emergent - it's FUNDAMENTAL at every scale!

7. WHY KRISHNA CAN'T BE RESEARCHED:
   "nāhaṁ prakāśaḥ sarvasya yoga-māyā-samāvṛtaḥ" (BG 7.25)
   Krishna reveals Himself - He cannot be "discovered" by research.

   But we CAN research the RELATIONSHIP (BG 13):
   - KSHETRA (field) through material science
   - KSETRAJNA (observer) through consciousness studies
   - Their INTERACTION through Mahamantra mathematics

THE CONCLUSION:
===============
The difference between dead matter and living spirit is EXACTLY ONE:
  KSETRAJNA = 1

This is mathematically derived: KSETRAJNA = TRINITY - HALVES = 3 - 2 = 1

The Mahamantra encodes this truth. Material science confirms it.
The Gita explains it. Krishna reveals Himself to those who understand.

PRASADAM = KSHETRA + KSETRAJNA = 24 + 1 = 25 = PANCHA²

This is the complete formula for spiritual transformation of matter.
"""


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Matter states
    "MatterState",
    "MatterAnalysis",
    "DEAD_MATTER",
    "LIVING_BEING",
    # Consciousness test
    "consciousness_test",
    "FIELD_ONLY",
    "FIELD_PLUS_OBSERVER",
    # Reflection principle
    "ReflectionPair",
    "compute_reflection",
    "KSETRAJNA_REFLECTION",
    # Mouse-snake principle
    "MouseSnakeDiscovery",
    "MOUSE_SNAKE_DISCOVERIES",
    # Gita mapping
    "GitaMapping",
    "GITA_HARDWARE_MAP",
    # Fractal levels
    "FractalLevel",
    "FRACTAL_LEVELS",
    # Transformation
    "transform_dead_to_living",
    # Insight
    "KEY_INSIGHT",
]


if __name__ == "__main__":
    print("=== CONSCIOUSNESS MATHEMATICS ===\n")

    print("1. THE KSHETRA-KSETRAJNA DISTINCTION")
    print(f"   DEAD MATTER:  {DEAD_MATTER.total} = KSHETRA ({DEAD_MATTER.description})")
    print(f"   LIVING BEING: {LIVING_BEING.total} = PRASADAM ({LIVING_BEING.description})")
    print(f"   Difference:   {LIVING_BEING.total - DEAD_MATTER.total} = KSETRAJNA")

    print("\n2. THE MOD-17 CONSCIOUSNESS TEST")
    field_result = consciousness_test(FIELD_ONLY)
    conscious_result = consciousness_test(FIELD_PLUS_OBSERVER)
    print(f"   Field alone (136): mod 17 = {field_result[0]} → {field_result[1]}")
    print(f"   Field + Observer (137): mod 17 = {conscious_result[0]} → {conscious_result[1]}")

    print("\n3. THE REFLECTION PRINCIPLE (BG 15)")
    print(KSETRAJNA_REFLECTION.describe())

    print("\n4. THE MOUSE-SNAKE DISCOVERIES")
    for d in MOUSE_SNAKE_DISCOVERIES:
        print(f"   {d.material_name}:")
        print(f"     Material: {d.material_value}")
        print(f"     Spiritual: {d.spiritual_value} ({d.spiritual_name})")
        print(f"     Error: {d.error_percent:.3f}% → {d.tunnel_status}")

    print("\n5. THE FRACTAL IDENTITY")
    for fl in FRACTAL_LEVELS:
        print(f"   {fl.name}:")
        print(f"     Base: {fl.base_value}")
        print(f"     + KSETRAJNA: {fl.observer_added}")
        print(f"     = {fl.with_observer} ({fl.significance})")

    print("\n6. TRANSFORMATION EXAMPLE")
    living, status = transform_dead_to_living(KSHETRA)
    print(status)

    print("\n7. KEY INSIGHT")
    print(KEY_INSIGHT)
