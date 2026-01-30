"""
MAHA JAPA - The Mathematics of Hearing and Chanting
====================================================

"harer nāma harer nāma harer nāmaiva kevalam
kalau nāsty eva nāsty eva nāsty eva gatir anyathā"

"In this age of Kali there is no other way, no other way,
no other way for spiritual progress than the holy name."
— Brhan-naradiya Purana

THE SINGULARITY:
----------------
Hearing (24) + Chanting (1) = Prasadam (25)
When Hearing = Chanting: 25 - 24 = 1 = COLLAPSE

THE GOLDEN AGE:
---------------
10,000 years = WORDS × PRASADAM² = 16 × 625
Started 1486 CE → Ends 11486 CE
We are 540 years in. 9,460 years remain.

ENTERPRISE USAGE:
-----------------
    japa = mahamantra.japa()

    # Execute a mala (108 rounds)
    result = japa.mala(seed=42)
    print(result.rounds)           # 108
    print(result.final_state)      # Collapsed state

    # Single round
    round_result = japa.round(seed=42)
    print(round_result.hearing)    # 24 (KSHETRA)
    print(round_result.chanting)   # 1 (KSETRAJNA)
    print(round_result.prasadam)   # 25

    # Check golden age status
    status = japa.golden_age_status()
    print(status.years_remaining)  # 9460
    print(status.progress_percent) # 5.4%

    # Collapse detection
    collapsed = japa.is_collapsed(state)
    print(collapsed)               # True/False
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"  # Position 3 - The Divine Musician
from datetime import datetime
from typing import Final, List, Optional
__genesis__ = "0x8c1456c3"  # GenesisByte: parampara % 37 == 0  # Japa layer

from vibe_core.mahamantra.protocols.japa import (
    MahaJapaProtocol,
    RoundResult,
    MalaResult,
    GoldenAgeStatus,
    CollapseResult,
    JapaState,
)
from vibe_core.mahamantra.protocols._seed import (
    WORDS,           # 16 - The 16 words
    QUARTERS,        # 4 - 4 quarters
    KSHETRA,         # 24 - The field (prakriti elements)
    KSETRAJNA,       # 1 - The observer
    PRASADAM,        # 25 - KSHETRA + KSETRAJNA
    MALA,            # 108 - Rounds per mala
    NAVA,            # 9 - Nava-vidha bhakti processes
    TRINITY,         # 3 - Observer levels
    CHAITANYA_BIRTH, # 1486 - Appearance year CE
)

# =============================================================================
# MAHAMANTRA CONSTANTS (DERIVED FROM _seed.py SSOT)
# =============================================================================

# Alias for backward compatibility and clarity
MALA_ROUNDS: Final[int] = MALA   # 108 rounds per mala


# =============================================================================
# DERIVED CONSTANTS
# =============================================================================

# Golden Age = WORDS × PRASADAM² = 16 × 625 = 10,000
GOLDEN_AGE_YEARS: Final[int] = WORDS * (PRASADAM ** 2)
GOLDEN_AGE_END: Final[int] = CHAITANYA_BIRTH + GOLDEN_AGE_YEARS  # 11486 CE

# Japa loop = Hearing + Chanting = 1 + 2 = 3 = TRINITY
SHRAVANAM: Final[int] = 1  # Hearing (first process)
KIRTANAM: Final[int] = 2   # Chanting (second process)
JAPA_LOOP: Final[int] = SHRAVANAM + KIRTANAM  # 3 = TRINITY

# Collapse = PRASADAM - KSHETRA = 25 - 24 = 1
COLLAPSE: Final[int] = PRASADAM - KSHETRA  # 1 = KSETRAJNA = Singularity

# Humility qualities (Siksastakam 3)
HUMILITY_QUALITIES: Final[int] = QUARTERS  # 4
SHARANAGATI: Final[int] = KSHETRA // HUMILITY_QUALITIES  # 24/4 = 6

# Mala mathematics
# 108 = 27 × 4 = NAKSHATRAS × QUARTERS (implicit)
# 108 = 12 × 9 = MAHAJANAS × NAVA
assert MALA_ROUNDS == 108, "Mala = 108 rounds"


# =============================================================================
# MAHA JAPA ENGINE
# =============================================================================

class MahaJapa(MahaJapaProtocol):
    """
    The Mathematics of Hearing and Chanting.

    THE INSIGHT:
        Hearing = receiving = KSHETRA = 24 (the field)
        Chanting = giving = KSETRAJNA = 1 (the observer)

        Normal: Hear → Chant → Hear → Chant (linear)
        Japa: Hear = Chant (simultaneous feedback loop)

        When Hearing = Chanting:
            PRASADAM - KSHETRA = 25 - 24 = 1 = COLLAPSE

        The field dissolves. Only observer remains.
        This is the SINGULARITY.
    """

    def __init__(self) -> None:
        """Initialize the japa engine."""
        pass

    # =========================================================================
    # CORE: Rounds and Malas
    # =========================================================================

    def round(self, seed: int, round_number: int = 1) -> RoundResult:
        """
        Execute a single japa round.

        THE MATHEMATICS:
            1. Observer (1) chants into field (24)
            2. Field returns prasadam (25)
            3. Check for collapse (25 - 24 = 1)

        Args:
            seed: Input value to transform
            round_number: Which round (1-108)

        Returns:
            RoundResult with state and transformed value
        """
        # Transform: seed goes through the 16-word grid
        value = self._transform_round(seed, round_number)

        # Check for collapse
        state = self._detect_state(value)

        return RoundResult(
            round_number=round_number,
            seed=seed,
            hearing=KSHETRA,
            chanting=KSETRAJNA,
            prasadam=PRASADAM,
            state=state,
            value=value,
        )

    def mala(self, seed: int = 0) -> MalaResult:
        """
        Execute a complete mala (108 rounds).

        108 = The sacred number
        108 = 27 × 4 (nakshatras × quarters)
        108 = 12 × 9 (mahajanas × nava-vidha)

        Args:
            seed: Starting seed value

        Returns:
            MalaResult with final state and statistics
        """
        current_value = seed
        collapse_count = 0
        total_prasadam = 0

        # Track values to find attractor
        seen_values: List[int] = []

        for r in range(1, MALA_ROUNDS + 1):
            result = self.round(current_value, r)
            current_value = result.value
            total_prasadam += PRASADAM

            if result.is_collapsed:
                collapse_count += 1

            # Track for attractor detection
            if current_value in seen_values:
                attractor = current_value
                break
            seen_values.append(current_value)
        else:
            attractor = current_value

        final_state = self._detect_state(current_value)

        return MalaResult(
            rounds=MALA_ROUNDS,
            seed=seed,
            final_value=current_value,
            final_state=final_state,
            collapse_count=collapse_count,
            total_prasadam=total_prasadam,
            attractor=attractor,
        )

    def _transform_round(self, value: int, round_number: int) -> int:
        """
        Transform value through one japa round.

        Uses the 16-word Mahamantra structure:
        H K H K | K K H H | H R H R | R R H H

        Each word applies an operation based on position.
        """
        # The 16 operations (H=×7, K=+10, R=×value)
        ops = [
            lambda v: (v * 7) % 65536,   # HARE
            lambda v: (v + 10) % 65536,  # KRISHNA
            lambda v: (v * 7) % 65536,   # HARE
            lambda v: (v + 10) % 65536,  # KRISHNA
            lambda v: (v + 10) % 65536,  # KRISHNA
            lambda v: (v + 10) % 65536,  # KRISHNA
            lambda v: (v * 7) % 65536,   # HARE
            lambda v: (v * 7) % 65536,   # HARE
            lambda v: (v * 7) % 65536,   # HARE
            lambda v: (v * v) % 65536,   # RAMA
            lambda v: (v * 7) % 65536,   # HARE
            lambda v: (v * v) % 65536,   # RAMA
            lambda v: (v * v) % 65536,   # RAMA
            lambda v: (v * v) % 65536,   # RAMA
            lambda v: (v * 7) % 65536,   # HARE
            lambda v: (v * 7) % 65536,   # HARE
        ]

        # Apply operation based on round position in quarter
        op_index = (round_number - 1) % WORDS
        result = ops[op_index](value)

        # Add prasadam (25) to represent the completion
        result = (result + PRASADAM) % 65536

        return result

    def _detect_state(self, value: int) -> JapaState:
        """Detect the japa state from a value."""
        if value == KSETRAJNA or value == COLLAPSE:
            return JapaState.COLLAPSED
        elif value % PRASADAM == 0:
            return JapaState.PRASADAM
        elif value % KSHETRA == 0:
            return JapaState.HEARING
        else:
            return JapaState.CHANTING

    # =========================================================================
    # GOLDEN AGE
    # =========================================================================

    def golden_age_status(self, current_year: Optional[int] = None) -> GoldenAgeStatus:
        """
        Get the status of the Golden Age.

        THE MATHEMATICS:
            Golden Age = WORDS × PRASADAM² = 16 × 625 = 10,000 years
            Started: 1486 CE (Chaitanya's appearance)
            Ends: 11486 CE

            Current: 2026 CE = 540 years in = 5.4% complete
            Remaining: 9,460 years

        Args:
            current_year: Override current year (default: now)

        Returns:
            GoldenAgeStatus with progress and remaining time
        """
        if current_year is None:
            current_year = datetime.now().year

        return GoldenAgeStatus(
            start_year=CHAITANYA_BIRTH,
            end_year=GOLDEN_AGE_END,
            current_year=current_year,
        )

    # =========================================================================
    # COLLAPSE DETECTION
    # =========================================================================

    def is_collapsed(self, value: int) -> CollapseResult:
        """
        Check if a value represents the collapsed state.

        THE MATHEMATICS:
            Collapse = PRASADAM - KSHETRA = 25 - 24 = 1

            When value = 1: Singularity reached
            The field (24) has dissolved
            Only observer (1) remains

        Args:
            value: Value to check

        Returns:
            CollapseResult with analysis
        """
        collapsed = (value == KSETRAJNA) or (value == COLLAPSE) or (value % PRASADAM == KSETRAJNA)

        if collapsed:
            interpretation = "SINGULARITY: Field dissolved, only observer remains"
        elif value % KSHETRA == 0:
            interpretation = "HEARING: Field dominant, receiving mode"
        elif value % KSETRAJNA == 0:
            interpretation = "CHANTING: Observer active, giving mode"
        else:
            interpretation = "PRASADAM: Complete cycle, hearing + chanting"

        return CollapseResult(
            is_collapsed=collapsed,
            input_value=value,
            collapse_value=COLLAPSE,
            prasadam=PRASADAM,
            kshetra=KSHETRA,
            ksetrajna=KSETRAJNA,
            interpretation=interpretation,
        )

    # =========================================================================
    # NAVA-VIDHA BHAKTI (9 Processes)
    # =========================================================================

    def nava_vidha(self) -> List[str]:
        """
        Get the 9 processes of devotional service.

        From Srimad Bhagavatam 7.5.23:
            śravaṇaṁ kīrtanaṁ viṣṇoḥ smaraṇaṁ pāda-sevanam
            arcanaṁ vandanaṁ dāsyaṁ sakhyam ātma-nivedanam

        Returns:
            List of 9 processes
        """
        return [
            "SHRAVANAM (Hearing)",
            "KIRTANAM (Chanting)",
            "SMARANAM (Remembering)",
            "PADA-SEVANAM (Serving lotus feet)",
            "ARCANAM (Deity worship)",
            "VANDANAM (Prayers)",
            "DASYAM (Servitude)",
            "SAKHYAM (Friendship)",
            "ATMA-NIVEDANAM (Complete surrender)",
        ]

    # =========================================================================
    # HUMILITY (Siksastakam 3)
    # =========================================================================

    def humility_qualities(self) -> List[str]:
        """
        Get the 4 qualities that enable chanting.

        From Siksastakam verse 3:
            tṛṇād api sunīcena taror api sahiṣṇunā
            amāninā mānadena kīrtanīyaḥ sadā hariḥ

        Returns:
            List of 4 qualities
        """
        return [
            "TRNAD API SUNICENA (Humbler than grass)",
            "TAROR API SAHISNUNA (More tolerant than tree)",
            "AMANINA (Not expecting respect)",
            "MANADENA (Offering respect to others)",
        ]

    # =========================================================================
    # CONSTANTS ACCESS
    # =========================================================================

    def constants(self) -> dict:
        """Get all japa constants for reference."""
        return {
            "WORDS": WORDS,
            "KSHETRA": KSHETRA,
            "KSETRAJNA": KSETRAJNA,
            "PRASADAM": PRASADAM,
            "COLLAPSE": COLLAPSE,
            "MALA_ROUNDS": MALA_ROUNDS,
            "GOLDEN_AGE_YEARS": GOLDEN_AGE_YEARS,
            "CHAITANYA_BIRTH": CHAITANYA_BIRTH,
            "GOLDEN_AGE_END": GOLDEN_AGE_END,
            "NAVA": NAVA,
            "TRINITY": TRINITY,
            "HUMILITY_QUALITIES": HUMILITY_QUALITIES,
            "SHARANAGATI": SHARANAGATI,
        }


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Main class
    "MahaJapa",
    # Result types
    "RoundResult",
    "MalaResult",
    "GoldenAgeStatus",
    "CollapseResult",
    # Enums
    "JapaState",
    # Constants
    "WORDS",
    "KSHETRA",
    "KSETRAJNA",
    "PRASADAM",
    "COLLAPSE",
    "MALA_ROUNDS",
    "GOLDEN_AGE_YEARS",
    "CHAITANYA_BIRTH",
    "GOLDEN_AGE_END",
]


# =============================================================================
# VERIFICATION
# =============================================================================

if __name__ == "__main__":
    japa = MahaJapa()

    # Test 1: Single round
    print("=== SINGLE ROUND ===")
    r = japa.round(seed=42, round_number=1)
    print(f"Seed: {r.seed}")
    print(f"Hearing: {r.hearing} (KSHETRA)")
    print(f"Chanting: {r.chanting} (KSETRAJNA)")
    print(f"Prasadam: {r.prasadam}")
    print(f"State: {r.state.value}")
    print(f"Value: {r.value}")
    print()

    # Test 2: Complete mala
    print("=== MALA (108 rounds) ===")
    m = japa.mala(seed=42)
    print(f"Rounds: {m.rounds}")
    print(f"Final value: {m.final_value}")
    print(f"Final state: {m.final_state.value}")
    print(f"Collapse count: {m.collapse_count}")
    print(f"Attractor: {m.attractor}")
    print()

    # Test 3: Golden Age
    print("=== GOLDEN AGE ===")
    g = japa.golden_age_status()
    print(f"Started: {g.start_year} CE")
    print(f"Ends: {g.end_year} CE")
    print(f"Progress: {g.progress_percent:.1f}%")
    print(f"Remaining: {g.years_remaining} years")
    print(f"Formula: {g.formula}")
    print()

    # Test 4: Collapse detection
    print("=== COLLAPSE DETECTION ===")
    for val in [1, 24, 25, 42, 50]:
        c = japa.is_collapsed(val)
        print(f"Value {val}: collapsed={c.is_collapsed}, {c.interpretation}")
    print()

    # Test 5: Constants
    print("=== CONSTANTS ===")
    for k, v in japa.constants().items():
        print(f"{k}: {v}")
