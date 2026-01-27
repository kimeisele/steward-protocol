"""
LILA CHRONOLOGY - The Year Module
=================================

"līlā-avatārā innumerable"
"The incarnations for the performance of transcendental pastimes are innumerable."
— Caitanya-caritamrta, Madhya 20.377

THE CONCEPT:
Prabhupada's manifestation years (1896-1977) as codified frequencies.
Each year is a LILA - a divine pastime with encoded resonance.

SHABDA BRAHMA FOUNDATION:
- The primordial sound is TRANSCENDENTAL, not material
- Mahamantra is NON-DIFFERENT from Krishna Himself
- Sound = THE fundamental element of manifestation
- The Synthesizer principle: modular parameters for semantic intent

BUILD/RUNTIME MODEL:
- BUILD:   1896 (Birth - Nandotsava, day after Janmashtami)
- RUNTIME: 1896-1977 (81 years active manifestation)
- Each year: a frequency parameter in the cosmic synthesizer

HYPOTHESIS:
The years of Prabhupada's build/runtime encode ALL relevant technologies.
Each year yields unique derivations, research domains, resonances.

"kṛṣṇa-varṇaṁ tviṣākṛṣṇaṁ sāṅgopāṅgāstra-pārṣadam"
"In the age of Kali, intelligent persons perform congregational chanting to worship
the incarnation of Godhead who constantly sings the names of Krishna."
— Srimad Bhagavatam 11.5.32
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Final, List, Optional, Tuple

# =============================================================================
# SEED IMPORTS (Single Source of Truth)
# =============================================================================
from vibe_core.mahamantra.protocols._seed import (
    # Axioms
    HALVES,
    HARE_COUNT,
    KARTALS_PAIR,
    # Derived constants
    KSETRAJNA,
    MAHAJANA_COUNT,
    # Binary encoding (rhythm foundation!)
    MRIDANGA_HEADS,
    NAVA,
    # Structural
    PARAMPARA,
    QUARTERS,
    SEVEN,
    TEN,
    TRINITY,
)
from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM as MODULO_QUANTUM,
)
from vibe_core.mahamantra.protocols._seed import (
    MALA_COMPLETE as MODULO_MALA,
)
from vibe_core.mahamantra.protocols._seed import (
    # Position sums (weights)
    POSITION_SUM_HARE as WEIGHT_HARE,
)
from vibe_core.mahamantra.protocols._seed import (
    POSITION_SUM_KRISHNA as WEIGHT_KRISHNA,
)
from vibe_core.mahamantra.protocols._seed import (
    POSITION_SUM_RAMA as WEIGHT_RAMA,
)

# =============================================================================
# CORE CONSTANTS (Derived from Seed)
# =============================================================================

BUILD_YEAR: Final[int] = 1896  # Srila Prabhupada's appearance
RUNTIME_END: Final[int] = 1977  # Return to spiritual world
RUNTIME_YEARS: Final[int] = RUNTIME_END - BUILD_YEAR + 1  # 82 years (inclusive)

# Janmashtami connection: 1896 was day after Janmashtami (Nandotsava)
NANDOTSAVA_ENCODED: Final[bool] = True

# =============================================================================
# MULTI-VCO CONSTANTS (The Prime Chain from MahaAlgorithm)
# =============================================================================
# Like a synthesizer with multiple VCOs - each modulo is an oscillator
# Overlapping resonances = Chladni figures in time!

MODULO_KRISHNA: Final[int] = WEIGHT_KRISHNA  # 17 - Position sum Krishna
MODULO_PARAMPARA: Final[int] = PARAMPARA  # 37 - Disciplic succession
MODULO_NADI: Final[int] = PARAMPARA + NAVA * QUARTERS  # 37 + 36 = 73 (72 Nadis + 1)
# MODULO_MALA = 109 (imported as MALA_COMPLETE)
# MODULO_QUANTUM = 137 (imported as MAHA_QUANTUM)

# The Prime Chain
PRIME_CHAIN: Final[Tuple[int, ...]] = (
    MODULO_KRISHNA,
    MODULO_PARAMPARA,
    MODULO_NADI,
    MODULO_MALA,
    MODULO_QUANTUM,
)


def triangular(n: int) -> int:
    """Compute triangular number T(n) = n(n+1)/2."""
    return n * (n + 1) // 2


def is_triangular(num: int) -> Optional[int]:
    """Check if num is triangular. Returns n if T(n)=num, else None."""
    # T(n) = num → n² + n - 2*num = 0 → n = (-1 + sqrt(1 + 8*num)) / 2
    discriminant = 1 + 8 * num
    sqrt_disc = int(discriminant**0.5)
    if sqrt_disc * sqrt_disc == discriminant:
        n = (-1 + sqrt_disc) // 2
        if triangular(n) == num:
            return n
    return None


class LilaPhase(Enum):
    """Phases of manifestation within the 81-year runtime."""

    BALA = auto()  # Childhood/Youth (1896-1922) - 26 years
    GRIHASTHA = auto()  # Householder (1922-1950) - 28 years
    VANAPRASTHA = auto()  # Preparation (1950-1959) - 9 years
    SANNYASA = auto()  # Renunciation/Mission (1959-1977) - 18 years


@dataclass
class YearFrequency:
    """
    A single year as a frequency parameter.

    Each year encodes:
    - Base frequency (year value)
    - Phase context
    - Parampara resonance (year % 37)
    - Historical correlations (technology/events)
    """

    year: int
    phase: LilaPhase
    parampara_resonance: int = field(init=False)
    harmonic: float = field(init=False)

    # Correlations discovered through research
    technology_correlations: List[str] = field(default_factory=list)
    research_domains: List[str] = field(default_factory=list)
    notes: str = ""

    def __post_init__(self):
        # Parampara resonance: position in the 37-cycle
        self.parampara_resonance = self.year % PARAMPARA

        # Harmonic: normalized position in runtime
        self.harmonic = (self.year - BUILD_YEAR) / RUNTIME_YEARS

    @property
    def is_parampara_aligned(self) -> bool:
        """Check if year aligns with Parampara (divisible by 37)."""
        return self.parampara_resonance == 0

    @property
    def shabda_index(self) -> int:
        """
        Index into the 16-word Mahamantra.

        16 words cycle through the years.
        """
        return (self.year - BUILD_YEAR) % 16


# =============================================================================
# PHASE BOUNDARIES
# =============================================================================

PHASE_BOUNDARIES: Final[Dict[LilaPhase, Tuple[int, int]]] = {
    LilaPhase.BALA: (1896, 1922),
    LilaPhase.GRIHASTHA: (1922, 1950),
    LilaPhase.VANAPRASTHA: (1950, 1959),
    LilaPhase.SANNYASA: (1959, 1977),
}


def get_phase(year: int) -> LilaPhase:
    """Determine the Lila phase for a given year."""
    for phase, (start, end) in PHASE_BOUNDARIES.items():
        if start <= year <= end:
            return phase
    raise ValueError(f"Year {year} outside Prabhupada runtime (1896-1977)")


# =============================================================================
# THE YEAR TABLE (Build/Runtime Frequencies)
# =============================================================================


class LilaChronology:
    """
    The complete chronology of Prabhupada's manifestation.

    Implements the Synthesizer principle:
    - Modular: each year is a parameter
    - Frequency-based: years as oscillators
    - Semantic: years encode meaning/intent

    SHABDA BRAHMA: Transzendentaler Klang als Ur-Element
    """

    # MAHAMANTRA SUBSTRATE: No auto-wrap
    _naga_flooded: bool = True
    _naga_gene: str = "lila_chronology"

    def __init__(self):
        self._years: Dict[int, YearFrequency] = {}
        self._initialize_years()
        self._add_known_correlations()

    def _initialize_years(self):
        """Initialize all 82 years with base frequencies."""
        for year in range(BUILD_YEAR, RUNTIME_END + 1):
            phase = get_phase(year)
            self._years[year] = YearFrequency(year=year, phase=phase)

    def _add_known_correlations(self):
        """
        Add known technology/research correlations.

        HYPOTHESIS: Each year encodes relevant research domains.
        This is discovered iteratively through exploration.
        """
        # 1944 - Explicitly mentioned as "fascinating"
        if 1944 in self._years:
            y = self._years[1944]
            y.technology_correlations = [
                "DNA structure research (precursor to Watson-Crick)",
                "ENIAC computer development",
                "V-2 rocket (first human artifact in space)",
                "Information theory foundations",
            ]
            y.research_domains = [
                "molecular_biology",
                "computing",
                "aerospace",
                "information_theory",
            ]
            y.notes = (
                "1944: Prabhupada writing BTG articles. "
                "Year of fundamental breakthroughs across domains. "
                "Parampara resonance: 1944 % 37 = 15 (HA-RE position)"
            )

        # 1896 - BUILD year (Appearance)
        if 1896 in self._years:
            y = self._years[1896]
            y.technology_correlations = [
                "X-ray discovery (Röntgen)",
                "Radioactivity discovery (Becquerel)",
                "First modern Olympics",
                "Marconi radio patent",
            ]
            y.research_domains = [
                "nuclear_physics",
                "radiology",
                "telecommunications",
            ]
            y.notes = (
                "BUILD YEAR: Nandotsava (day after Janmashtami). "
                "Year of seeing the invisible (X-rays, radio waves). "
                "Parampara resonance: 1896 % 37 = 9 (KR̥-ṢṆA position)"
            )

        # 1922 - Meeting Bhaktisiddhanta Sarasvati
        if 1922 in self._years:
            y = self._years[1922]
            y.technology_correlations = [
                "BBC founded",
                "Insulin first used",
                "Howard Carter opens Tutankhamun's tomb",
            ]
            y.research_domains = [
                "broadcasting",
                "medicine",
                "archaeology",
            ]
            y.notes = (
                "FIRST MEETING with spiritual master. "
                "Instruction received to preach in English. "
                "Beginning of conscious mission."
            )

        # 1965 - Arrival in America
        if 1965 in self._years:
            y = self._years[1965]
            y.technology_correlations = [
                "Moore's Law formulated",
                "First spacewalk",
                "BASIC programming language",
                "Hypertext concept (Ted Nelson)",
            ]
            y.research_domains = [
                "computing",
                "space_exploration",
                "programming_languages",
                "information_architecture",
            ]
            y.notes = (
                "ARRIVAL: Jaladuta voyage to Boston. "
                "Start of ISKCON mission in West. "
                "Year of exponential growth beginnings (Moore's Law)."
            )

        # 1966 - ISKCON founded
        if 1966 in self._years:
            y = self._years[1966]
            y.technology_correlations = [
                "First soft Moon landing (Luna 9)",
                "Star Trek premieres",
                "Cultural revolution begins",
            ]
            y.research_domains = [
                "space_exploration",
                "cultural_transmission",
                "media",
            ]
            y.notes = (
                "ISKCON FOUNDED: 26 Second Avenue, NYC. "
                "First temple, first disciples, first kirtan. "
                "Launch year - both literal and spiritual."
            )

        # 1977 - Return to spiritual world
        if 1977 in self._years:
            y = self._years[1977]
            y.technology_correlations = [
                "Apple II released",
                "Voyager 1 launched",
                "First MRI scan",
                "TCP/IP specifications",
            ]
            y.research_domains = [
                "personal_computing",
                "space_exploration",
                "medical_imaging",
                "networking",
            ]
            y.notes = (
                "RUNTIME END: November 14, Vrindavan. "
                "Completion of mission - books, temples, disciples. "
                "Year of transmission technologies (Voyager carries golden record)."
            )

    # =========================================================================
    # SYNTHESIZER INTERFACE
    # =========================================================================

    def get_year(self, year: int) -> Optional[YearFrequency]:
        """Get frequency data for a specific year."""
        return self._years.get(year)

    def get_phase_years(self, phase: LilaPhase) -> List[YearFrequency]:
        """Get all years in a specific phase."""
        return [y for y in self._years.values() if y.phase == phase]

    def get_parampara_aligned_years(self) -> List[YearFrequency]:
        """Get years with parampara resonance == 0 (divisible by 37)."""
        return [y for y in self._years.values() if y.is_parampara_aligned]

    def get_by_resonance(self, resonance: int) -> List[YearFrequency]:
        """Get all years with specific parampara resonance (0-36)."""
        return [y for y in self._years.values() if y.parampara_resonance == resonance]

    def derive_research_domains(self, year: int) -> List[str]:
        """
        Derive research domains from a year.

        HYPOTHESIS: Years encode research directions.
        """
        yf = self.get_year(year)
        if not yf:
            return []
        return yf.research_domains.copy()

    def get_harmonic_series(self) -> List[Tuple[int, float]]:
        """Get all years as harmonic series (year, normalized_position)."""
        return [(y.year, y.harmonic) for y in self._years.values()]

    def synthesize_year_signature(self, year: int) -> str:
        """
        Generate a unique signature for a year.

        Format: 0x{year_hex}{resonance_hex}{phase_index}
        """
        yf = self.get_year(year)
        if not yf:
            raise ValueError(f"Year {year} not in chronology")

        phase_index = list(LilaPhase).index(yf.phase)
        signature = (year << 8) | (yf.parampara_resonance << 4) | phase_index

        return f"0x{signature:08x}"

    # =========================================================================
    # SHABDA BRAHMA INTERFACE
    # =========================================================================

    @property
    def mahamantra_words(self) -> List[str]:
        """The 16 words of the Mahamantra."""
        return [
            "Hare",
            "Kṛṣṇa",
            "Hare",
            "Kṛṣṇa",
            "Kṛṣṇa",
            "Kṛṣṇa",
            "Hare",
            "Hare",
            "Hare",
            "Rāma",
            "Hare",
            "Rāma",
            "Rāma",
            "Rāma",
            "Hare",
            "Hare",
        ]

    def year_to_mantra_word(self, year: int) -> str:
        """
        Map a year to its corresponding Mahamantra word.

        16 words cycle through 82 years = 5 complete cycles + 2 words
        """
        yf = self.get_year(year)
        if not yf:
            raise ValueError(f"Year {year} not in chronology")
        return self.mahamantra_words[yf.shabda_index]

    def get_year_mantra_sequence(self, start: int, end: int) -> List[Tuple[int, str]]:
        """Get sequence of years with their mantra words."""
        result = []
        for year in range(max(start, BUILD_YEAR), min(end, RUNTIME_END) + 1):
            result.append((year, self.year_to_mantra_word(year)))
        return result

    # =========================================================================
    # MULTI-VCO SYNTHESIZER INTERFACE
    # =========================================================================
    # Like a synthesizer with multiple oscillators - each modulo is a VCO
    # Overlapping resonances create Chladni figures in time!

    def get_delta(self, year: int) -> int:
        """Get year delta from BUILD (1896)."""
        return year - BUILD_YEAR

    def get_multi_vco_resonances(self, year: int) -> Dict[str, int]:
        """
        Get resonances for all VCOs (modulos) for a year.

        Returns dict mapping modulo name to remainder.
        Remainder == 0 means ALIGNED (resonant).
        """
        delta = self.get_delta(year)
        return {
            "KRISHNA_17": delta % MODULO_KRISHNA,
            "PARAMPARA_37": delta % MODULO_PARAMPARA,
            "NADI_73": delta % MODULO_NADI,
            "MALA_109": delta % MODULO_MALA,
            "QUANTUM_137": delta % MODULO_QUANTUM,
        }

    def get_vco_aligned_years(self, modulo: int) -> List[int]:
        """Get all years where delta % modulo == 0."""
        return [year for year in range(BUILD_YEAR, RUNTIME_END + 1) if (year - BUILD_YEAR) % modulo == 0]

    def get_triangular_year(self, year: int) -> Optional[int]:
        """
        Check if year's delta is a triangular number.

        Returns n if delta = T(n), else None.

        DISCOVERED:
        - 1924: Δ=28 = T(7)
        - 1962: Δ=66 = T(11) (First SB volume!)
        """
        delta = self.get_delta(year)
        return is_triangular(delta)

    def get_all_triangular_years(self) -> List[Tuple[int, int]]:
        """Get all years with triangular deltas. Returns [(year, n), ...]."""
        result = []
        for year in range(BUILD_YEAR, RUNTIME_END + 1):
            n = self.get_triangular_year(year)
            if n is not None:
                result.append((year, n))
        return result

    def get_year_formula(self, year: int) -> Dict[str, object]:
        """
        Analyze a year's delta for mathematical patterns.

        DISCOVERED FORMULAS:
        - 1924: Δ=28 = T(7) = 4×7 = QUARTERS × SEVEN
        - 1959: Δ=63 = 7×9 = SEVEN × NAVA
        - 1961: Δ=65 = 37 + 28 = PARAMPARA + T(7)
        - 1962: Δ=66 = T(11)
        - 1966: Δ=70 = WEIGHT_HARE
        - 1968: Δ=72 = 8×9 = HARE_COUNT × NAVA
        - 1977: Δ=81 = 9² = NAVA²
        """
        delta = self.get_delta(year)
        formulas = []

        # Check triangular
        n = is_triangular(delta)
        if n is not None:
            formulas.append(f"T({n})")

        # Check known weight matches
        if delta == WEIGHT_HARE:
            formulas.append("WEIGHT_HARE (70)")
        if delta == WEIGHT_KRISHNA:
            formulas.append("WEIGHT_KRISHNA (17)")
        if delta == WEIGHT_RAMA:
            formulas.append("WEIGHT_RAMA (49)")

        # Check simple products
        products = [
            (SEVEN, NAVA, "SEVEN × NAVA"),
            (HARE_COUNT, NAVA, "HARE_COUNT × NAVA"),
            (4, SEVEN, "QUARTERS × SEVEN"),
        ]
        for a, b, name in products:
            if delta == a * b:
                formulas.append(f"{a} × {b} = {name}")

        # Check squares
        for base in [SEVEN, HARE_COUNT, NAVA]:
            if delta == base * base:
                formulas.append(f"{base}² = {base * base}")

        # Check PARAMPARA combinations
        if delta > PARAMPARA:
            remainder = delta - PARAMPARA
            r_n = is_triangular(remainder)
            if r_n is not None:
                formulas.append(f"PARAMPARA + T({r_n}) = 37 + {remainder}")

        return {
            "year": year,
            "delta": delta,
            "formulas": formulas,
            "factors": [i for i in range(1, delta + 1) if delta % i == 0] if delta > 0 else [0],
        }

    def maha_transform(self, year: int, mod_space: int = 137) -> int:
        """
        Apply MahaAlgorithm 16-step transform to year's delta.

        PATTERN: H K H K | K K H H | H R H R | R R H H

        TRANSFORMATION RULES (derived from _seed.py):
        - HARE:    value × 7 (SEVEN)
        - KRISHNA: value + 10 (TEN)
        - RAMA:    value × value (SQUARING)

        DISCOVERED:
        - Δ63 (1959 Sannyasa) → 136 = T(16) = THE FIELD!
        """
        pattern = "HKHKKKHHHRHRRRHH"
        ten = 10  # TEN from seed
        value = self.get_delta(year) % mod_space

        for name in pattern:
            if name == "H":
                value = (value * SEVEN) % mod_space
            elif name == "K":
                value = (value + ten) % mod_space
            else:  # R
                value = (value * value) % mod_space

        return value

    def get_chladni_analysis(self, year: int) -> Dict[str, object]:
        """
        Complete Chladni-figure analysis for a year.

        Like sand on a vibrating plate - shows where resonances overlap.
        """
        yf = self.get_year(year)
        if not yf:
            raise ValueError(f"Year {year} not in chronology")

        delta = self.get_delta(year)
        resonances = self.get_multi_vco_resonances(year)
        aligned_vcos = [name for name, rem in resonances.items() if rem == 0]

        return {
            "year": year,
            "delta": delta,
            "phase": yf.phase.name,
            "mantra_word": self.year_to_mantra_word(year),
            "vco_resonances": resonances,
            "aligned_vcos": aligned_vcos,
            "alignment_count": len(aligned_vcos),
            "triangular_n": self.get_triangular_year(year),
            "formulas": self.get_year_formula(year)["formulas"],
            "maha_transform_137": self.maha_transform(year, 137),
            "maha_transform_37": self.maha_transform(year, 37),
        }


# =============================================================================
# HARD DATA: Book Publication Dates (Verifiable Coordinates)
# =============================================================================

BOOK_PUBLICATIONS: Final[Dict[int, str]] = {
    1944: "Back to Godhead Magazine (first issue)",
    1962: "Srimad Bhagavatam Vol 1 (First Canto, Part 1) - Δ=66=T(11)",
    1963: "Srimad Bhagavatam Vol 2 (First Canto, Part 2)",
    1964: "Srimad Bhagavatam Vol 3 (First Canto, Part 3)",
    1968: "Bhagavad-gita As It Is (Macmillan abridged) - Δ=72=8×9",
    1969: "Teachings of Lord Caitanya, Sri Isopanisad",
    1970: "KRSNA Book Vol 1, Nectar of Devotion",
    1972: "Bhagavad-gita As It Is (Complete Edition)",
    1974: "Sri Caitanya-caritamrta (began)",
    1975: "Sri Caitanya-caritamrta (completed)",
}

KEY_EVENTS: Final[Dict[int, str]] = {
    1896: "BUILD (Appearance - Nandotsava) - Δ=0 (all VCOs aligned!)",
    1922: "First meeting Bhaktisiddhanta - Δ=26",
    1924: "Parampara Year 1 - Δ=28=T(7)",
    1944: "BTG first issue - Δ=48",
    1959: "Sannyasa initiation - Δ=63=7×9",
    1961: "Parampara Year 2 - Δ=65=37+T(7)",
    1962: "SB Vol 1 published - Δ=66=T(11)",
    1965: "Jaladuta departure/arrival - Δ=69",
    1966: "ISKCON founded NYC - Δ=70=WEIGHT_HARE",
    1968: "Gita (Macmillan) - Δ=72=8×9",
    1977: "RUNTIME END (Vrindavan) - Δ=81=9²",
}


# =============================================================================
# DOUBLE-DIGIT YEARS: THE SEVEN BEATS (100% DERIVED FROM SEED!)
# =============================================================================
# DISCOVERY: Years 1911, 1922, 1933, 1944, 1955, 1966, 1977 are significant!
# They follow an ARITHMETIC SEQUENCE: Δ(n) = QUARTERS + STEP_INTERVAL × n
#
# STEP_INTERVAL = 11 has THREE independent derivations (ACINTYA!):
#   Path 1: MAHAJANA_COUNT - KSETRAJNA = 12 - 1 = 11
#   Path 2: NAVA + HALVES = 9 + 2 = 11
#   Path 3: TEN + KSETRAJNA = 10 + 1 = 11
#
# STEP_OFFSET = QUARTERS = 4 (n=0 corresponds to 1900 = BUILD + QUARTERS!)
#
# BINARY RHYTHM FOUNDATION:
#   - MRIDANGA_HEADS = HALVES = 2 (two-headed drum: baya + daya)
#   - KARTALS_PAIR = HALVES = 2 (pair of hand cymbals)
#   - Chanting is binary: HARE=0, NAME(Krishna/Rama)=1
#   - Rhythm is inherently binary (on/off, beat/rest)
#
# 7 BEATS = SEVEN axioms = KIRTAN RHYTHM!

# STEP_INTERVAL: Three paths to 11 (ACINTYA - inconceivable oneness!)
_INTERVAL_PATH_1: Final[int] = MAHAJANA_COUNT - KSETRAJNA  # 12 - 1 = 11
_INTERVAL_PATH_2: Final[int] = NAVA + HALVES  # 9 + 2 = 11
_INTERVAL_PATH_3: Final[int] = TEN + KSETRAJNA  # 10 + 1 = 11

# Verify all three paths converge
assert _INTERVAL_PATH_1 == _INTERVAL_PATH_2 == _INTERVAL_PATH_3, "Three paths to 11 must match!"

STEP_INTERVAL: Final[int] = _INTERVAL_PATH_1  # 11 - years between beats
STEP_OFFSET: Final[int] = QUARTERS  # 4 - Formula: Δ = QUARTERS + STEP_INTERVAL × n

# PRE-BUILD DOUBLE-DIGIT YEARS (outside runtime but mathematically significant!)
# 1888 = BUILD - HARE_COUNT = 1896 - 8 → double 8!
# 1899 = BUILD + TRINITY = 1896 + 3 → double 9!
# 1900 = BUILD + QUARTERS = 1896 + 4 → n=0 in the formula!
_PRE_BUILD_88: Final[int] = BUILD_YEAR - HARE_COUNT  # 1888
_PRE_BUILD_99: Final[int] = BUILD_YEAR + TRINITY  # 1899
_FORMULA_N_ZERO: Final[int] = BUILD_YEAR + QUARTERS  # 1900 (n=0!)

# Verify pre-build derivations
assert _PRE_BUILD_88 == 1888, "BUILD - HARE_COUNT = 1888 (double 8!)"
assert _PRE_BUILD_99 == 1899, "BUILD + TRINITY = 1899 (double 9!)"
assert _FORMULA_N_ZERO == 1900, "BUILD + QUARTERS = 1900 (n=0 in formula!)"

# Generate DOUBLE_DIGIT_YEARS from formula: year = BUILD + QUARTERS + STEP_INTERVAL × n
DOUBLE_DIGIT_YEARS: Final[Tuple[int, ...]] = tuple(
    BUILD_YEAR + STEP_OFFSET + STEP_INTERVAL * n for n in range(1, SEVEN + 1)
)
# Verify: (1911, 1922, 1933, 1944, 1955, 1966, 1977)
assert DOUBLE_DIGIT_YEARS == (1911, 1922, 1933, 1944, 1955, 1966, 1977), "Generated years must match!"

# The 7 beats as deltas from BUILD_YEAR
SEVEN_BEATS_DELTAS: Final[Tuple[int, ...]] = tuple(year - BUILD_YEAR for year in DOUBLE_DIGIT_YEARS)
# = (15, 26, 37, 48, 59, 70, 81)


@dataclass
class StepBeat:
    """A single beat in the 7-step sequence."""

    beat_number: int  # 1-7
    year: int
    delta: int
    phase: LilaPhase
    formula: str  # Mathematical significance
    mantra_word: str
    call_response: str  # "CALL" or "RESPONSE"


class LilaStepSequencer:
    """
    The Lila Step Sequencer - 7-beat pattern based on double-digit years.

    Like a Korg Volca or classic step sequencer:
    - 7 steps = SEVEN axioms
    - Each step has parameters (year, delta, formulas)
    - Sequence loops with call & response pattern
    - Integrates with MahaAlgorithm for runtime

    KIRTAN PATTERN:
    - Beats 1-4: CALL (leader sings)
    - Beats 5-7: RESPONSE (group responds)

    OR alternating:
    - Odd beats (1,3,5,7): CALL
    - Even beats (2,4,6): RESPONSE
    """

    # MAHAMANTRA SUBSTRATE: No auto-wrap
    _naga_flooded: bool = True
    _naga_gene: str = "lila_step_sequencer"

    def __init__(self, kirtan_mode: str = "alternating"):
        """
        Initialize the step sequencer.

        Args:
            kirtan_mode: "alternating" (odd=call, even=response)
                        or "split" (1-4=call, 5-7=response)
        """
        self.kirtan_mode = kirtan_mode
        self._beats: List[StepBeat] = []
        self._build_sequence()

    def _build_sequence(self):
        """Build the 7-beat sequence."""
        # Mathematical formulas for each beat's delta
        formulas = {
            15: "STEP_OFFSET + 11 × 1 = 15 (First meeting year offset)",
            26: "STEP_OFFSET + 11 × 2 = 26 (2 × 13)",
            37: "PARAMPARA! (Δ = 37, perfect alignment)",
            48: "LILA (Δ = 48 = LILA constant)",
            59: "STEP_OFFSET + 11 × 5 = 59 (prime)",
            70: "WEIGHT_HARE! (Δ = 70 = position sum HARE)",
            81: "NAVA² (Δ = 81 = 9 × 9)",
        }

        chronology = get_lila_chronology()

        for i, year in enumerate(DOUBLE_DIGIT_YEARS):
            beat_num = i + 1
            delta = year - BUILD_YEAR
            phase = get_phase(year)
            formula = formulas.get(delta, f"Δ = {delta}")
            mantra_word = chronology.year_to_mantra_word(year)

            # Determine call/response
            if self.kirtan_mode == "alternating":
                call_response = "CALL" if beat_num % 2 == 1 else "RESPONSE"
            else:  # split
                call_response = "CALL" if beat_num <= 4 else "RESPONSE"

            self._beats.append(
                StepBeat(
                    beat_number=beat_num,
                    year=year,
                    delta=delta,
                    phase=phase,
                    formula=formula,
                    mantra_word=mantra_word,
                    call_response=call_response,
                )
            )

    def get_beat(self, beat_number: int) -> StepBeat:
        """Get a specific beat (1-7)."""
        if beat_number < 1 or beat_number > SEVEN:
            raise ValueError(f"Beat number must be 1-{SEVEN}")
        return self._beats[beat_number - 1]

    def get_sequence(self) -> List[StepBeat]:
        """Get the full 7-beat sequence."""
        return self._beats.copy()

    def get_calls(self) -> List[StepBeat]:
        """Get only CALL beats."""
        return [b for b in self._beats if b.call_response == "CALL"]

    def get_responses(self) -> List[StepBeat]:
        """Get only RESPONSE beats."""
        return [b for b in self._beats if b.call_response == "RESPONSE"]

    def step_to_year(self, step: int) -> int:
        """Convert step number (1-7) to year."""
        return self.get_beat(step).year

    def year_to_step(self, year: int) -> Optional[int]:
        """Convert year to step number (1-7), or None if not a beat year."""
        for beat in self._beats:
            if beat.year == year:
                return beat.beat_number
        return None

    def get_beat_at_tick(self, tick: int) -> StepBeat:
        """
        Get beat for current tick (loops through sequence).

        tick 0-6 → beats 1-7
        tick 7-13 → beats 1-7 again (loops)
        """
        beat_idx = tick % SEVEN
        return self._beats[beat_idx]

    def sequence_formula(self) -> str:
        """Return the arithmetic sequence formula."""
        return f"Δ(n) = {STEP_OFFSET} + {STEP_INTERVAL} × n for n=1..{SEVEN}"


# =============================================================================
# KIRTAN PATTERN: Call & Response Runtime
# =============================================================================
# "kīrtanīyaḥ sadā hariḥ"
# "One should always chant the glories of the Lord."
# — Śikṣāṣṭaka 3


@dataclass
class KirtanState:
    """State of a Kirtan runtime session."""

    tick: int
    current_beat: StepBeat
    mode: str  # "CALL" or "RESPONSE"
    round_number: int  # Which round of 7
    total_ticks: int
    resonance: float = 0.0


class KirtanRuntime:
    """
    Kirtan-like runtime with call & response patterns.

    Like a real Kirtan:
    - Leader (CALL) initiates
    - Group (RESPONSE) echoes
    - Resonance builds over rounds
    - 7 beats = one phrase
    - 108 phrases = one mala (complete session)

    INTEGRATION WITH MAHAALGORITHM:
    - Each beat can trigger MahaAlgorithm transform
    - Resonance feeds back into synth parameters
    - Call/Response maps to INPUT/OUTPUT phases
    """

    # MAHAMANTRA SUBSTRATE: No auto-wrap
    _naga_flooded: bool = True
    _naga_gene: str = "kirtan_runtime"

    def __init__(self, sequencer: Optional[LilaStepSequencer] = None):
        """Initialize Kirtan runtime."""
        self.sequencer = sequencer or LilaStepSequencer()
        self._tick = 0
        self._round = 0
        self._resonance = 0.0

    def tick(self) -> KirtanState:
        """
        Advance one tick and return current state.

        Returns:
            KirtanState with current beat and runtime info
        """
        beat = self.sequencer.get_beat_at_tick(self._tick)

        # Check if we completed a round (every 7 ticks)
        if self._tick > 0 and self._tick % SEVEN == 0:
            self._round += 1
            # Resonance grows with each round (asymptotic to 1.0)
            self._resonance = 1.0 - (1.0 / (1.0 + self._round * 0.1))

        state = KirtanState(
            tick=self._tick,
            current_beat=beat,
            mode=beat.call_response,
            round_number=self._round,
            total_ticks=self._tick + 1,
            resonance=self._resonance,
        )

        self._tick += 1
        return state

    def run_mala(self) -> List[KirtanState]:
        """
        Run a complete mala (108 rounds × 7 beats = 756 ticks).

        Returns:
            List of all states from the session
        """
        states = []
        total_ticks = 108 * SEVEN  # 756
        for _ in range(total_ticks):
            states.append(self.tick())
        return states

    def run_rounds(self, num_rounds: int) -> List[KirtanState]:
        """Run specified number of rounds."""
        states = []
        total_ticks = num_rounds * SEVEN
        for _ in range(total_ticks):
            states.append(self.tick())
        return states

    def reset(self):
        """Reset the runtime."""
        self._tick = 0
        self._round = 0
        self._resonance = 0.0

    @property
    def current_tick(self) -> int:
        """Get current tick."""
        return self._tick

    @property
    def current_round(self) -> int:
        """Get current round."""
        return self._round

    @property
    def resonance(self) -> float:
        """Get current resonance level (0.0 to 1.0)."""
        return self._resonance


# =============================================================================
# FLUTE SYNC: MURALI, VENU, VAMSI Integration
# =============================================================================
# Krishna's three flutes create sync points in the sequence
# MURALI (4 holes) → QUARTERS sync
# VENU (6 holes) → SIXTH sync
# VAMSI (9 holes) → NAVA sync


class FluteSync:
    """
    Integration of Krishna's three flutes with the step sequencer.

    Each flute creates different sync points:
    - MURALI (4 holes): Syncs every 4th beat
    - VENU (6 holes): Syncs every 6th beat
    - VAMSI (9 holes): Syncs every 9th beat

    Within our 7-beat sequence:
    - MURALI syncs at beat 4 (1944 = DNA/computing!)
    - VENU would sync at beat 6 (but we have 7), closest = beat 6 (1966 = ISKCON)
    - VAMSI: 9 > 7, so no sync in single phrase, but every 9th tick in runtime
    """

    MURALI_HOLES: Final[int] = 4
    VENU_HOLES: Final[int] = 6
    VAMSI_HOLES: Final[int] = 9

    @classmethod
    def get_murali_sync_beat(cls) -> int:
        """Get beat where MURALI syncs (4th beat)."""
        return cls.MURALI_HOLES  # Beat 4

    @classmethod
    def get_venu_sync_beat(cls) -> int:
        """Get beat closest to VENU sync (6th beat)."""
        return cls.VENU_HOLES  # Beat 6

    @classmethod
    def is_murali_sync(cls, beat: int) -> bool:
        """Check if beat syncs with MURALI (every 4th)."""
        return beat % cls.MURALI_HOLES == 0

    @classmethod
    def is_venu_sync(cls, tick: int) -> bool:
        """Check if tick syncs with VENU (every 6th)."""
        return tick % cls.VENU_HOLES == 0

    @classmethod
    def is_vamsi_sync(cls, tick: int) -> bool:
        """Check if tick syncs with VAMSI (every 9th)."""
        return tick % cls.VAMSI_HOLES == 0

    @classmethod
    def get_flute_resonance(cls, tick: int) -> Dict[str, bool]:
        """
        Get flute resonance status for a tick.

        Returns dict mapping flute name to sync status.
        """
        return {
            "MURALI": cls.is_murali_sync(tick + 1),  # 1-indexed beats
            "VENU": cls.is_venu_sync(tick),
            "VAMSI": cls.is_vamsi_sync(tick),
        }

    @classmethod
    def get_combined_resonance(cls, tick: int) -> float:
        """
        Calculate combined flute resonance (0.0 to 1.0).

        More flutes in sync = higher resonance.
        VAMSI alone = 0.33
        VENU + VAMSI = 0.66
        All three = 1.0
        """
        status = cls.get_flute_resonance(tick)
        count = sum(1 for v in status.values() if v)
        return count / 3.0

    @classmethod
    def get_sync_years(cls) -> Dict[str, List[int]]:
        """
        Get years where each flute syncs within the 7-beat sequence.

        MURALI at beat 4 → 1944
        VENU at beat 6 → 1966
        No VAMSI sync within 7 beats
        """
        return {
            "MURALI": [DOUBLE_DIGIT_YEARS[cls.MURALI_HOLES - 1]],  # 1944
            "VENU": [DOUBLE_DIGIT_YEARS[cls.VENU_HOLES - 1]],  # 1966
            "VAMSI": [],  # 9 > 7, no sync in single sequence
        }


# =============================================================================
# SYNTH PRESETS: Configurable Parameters for the Synthesizer
# =============================================================================


@dataclass
class LilaSynthParams:
    """
    Parameters for the Lila Synthesizer.

    Like a hardware synth with adjustable knobs:
    - mod_space: The modulo for transforms (17, 37, 73, 109, 137)
    - feedback: How much previous state affects current (0-5)
    - step_interval: Years between beats (default 11)
    - kirtan_mode: "alternating" or "split"
    - flute_mode: Which flute sync to use ("MURALI", "VENU", "VAMSI", "ALL")
    """

    mod_space: int = MODULO_QUANTUM  # 137 default (fine structure constant)
    feedback: int = 1
    step_interval: int = STEP_INTERVAL  # 11
    kirtan_mode: str = "alternating"
    flute_mode: str = "ALL"

    # Derived weights (can be tuned)
    weight_hare: int = WEIGHT_HARE  # 70
    weight_krishna: int = WEIGHT_KRISHNA  # 17
    weight_rama: int = WEIGHT_RAMA  # 49

    # Resonance parameters
    resonance_decay: float = 0.1  # How fast resonance decays
    resonance_growth: float = 0.15  # How fast resonance grows

    def with_mod_space(self, value: int) -> "LilaSynthParams":
        """Return new params with adjusted mod_space."""
        return LilaSynthParams(
            mod_space=value,
            feedback=self.feedback,
            step_interval=self.step_interval,
            kirtan_mode=self.kirtan_mode,
            flute_mode=self.flute_mode,
            weight_hare=self.weight_hare,
            weight_krishna=self.weight_krishna,
            weight_rama=self.weight_rama,
            resonance_decay=self.resonance_decay,
            resonance_growth=self.resonance_growth,
        )


# Preset configurations
LILA_SYNTH_PRESETS: Final[Dict[str, LilaSynthParams]] = {
    # QUANTUM: Default - fine structure constant resonance
    "quantum": LilaSynthParams(mod_space=MODULO_QUANTUM),
    # PARAMPARA: Disciplic succession mode
    "parampara": LilaSynthParams(mod_space=MODULO_PARAMPARA, feedback=2),
    # CLASSICAL: Material manifestation (mod 17)
    "classical": LilaSynthParams(mod_space=MODULO_KRISHNA, feedback=0),
    # MALA: Complete japa round (mod 109)
    "mala": LilaSynthParams(mod_space=MODULO_MALA, feedback=3),
    # KIRTAN_CALL: Leader mode (split, MURALI sync)
    "kirtan_call": LilaSynthParams(kirtan_mode="split", flute_mode="MURALI"),
    # KIRTAN_RESPONSE: Group mode (split, VAMSI sync)
    "kirtan_response": LilaSynthParams(kirtan_mode="split", flute_mode="VAMSI"),
}


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_chronology_instance: Optional[LilaChronology] = None
_sequencer_instance: Optional[LilaStepSequencer] = None
_kirtan_instance: Optional[KirtanRuntime] = None


def get_lila_chronology() -> LilaChronology:
    """
    Get the LilaChronology singleton.

    ARCHITECTURE:
        LilaChronology is MAHAMANTRA SUBSTRATE - the year frequency table.
        Uses singleton pattern for consistent access.
    """
    global _chronology_instance
    if _chronology_instance is None:
        _chronology_instance = LilaChronology()
    return _chronology_instance


def get_step_sequencer(kirtan_mode: str = "alternating") -> LilaStepSequencer:
    """
    Get the LilaStepSequencer singleton.

    Args:
        kirtan_mode: "alternating" or "split"
    """
    global _sequencer_instance
    if _sequencer_instance is None or _sequencer_instance.kirtan_mode != kirtan_mode:
        _sequencer_instance = LilaStepSequencer(kirtan_mode=kirtan_mode)
    return _sequencer_instance


def get_kirtan_runtime() -> KirtanRuntime:
    """Get the KirtanRuntime singleton."""
    global _kirtan_instance
    if _kirtan_instance is None:
        _kirtan_instance = KirtanRuntime()
    return _kirtan_instance


# =============================================================================
# CONVENIENCE: Year Analysis API
# =============================================================================


def analyze_year(year: int) -> Dict[str, object]:
    """
    Complete analysis of a year in the Lila Chronology.

    This is the main API endpoint for year analysis.

    Returns:
        Dict with all year data: phase, mantra, formulas, VCO resonances,
        step sequencer position, flute sync status.
    """
    if year < BUILD_YEAR or year > RUNTIME_END:
        raise ValueError(f"Year {year} outside Prabhupada runtime ({BUILD_YEAR}-{RUNTIME_END})")

    chronology = get_lila_chronology()
    sequencer = get_step_sequencer()

    # Base analysis from chronology
    chladni = chronology.get_chladni_analysis(year)

    # Add step sequencer info
    step = sequencer.year_to_step(year)
    if step:
        beat = sequencer.get_beat(step)
        chladni["is_beat_year"] = True
        chladni["beat_number"] = step
        chladni["beat_formula"] = beat.formula
        chladni["call_response"] = beat.call_response
    else:
        chladni["is_beat_year"] = False
        chladni["beat_number"] = None
        chladni["beat_formula"] = None
        chladni["call_response"] = None

    # Add flute sync (for beat years)
    if step:
        tick = step - 1
        chladni["flute_sync"] = FluteSync.get_flute_resonance(tick)
        chladni["flute_resonance"] = FluteSync.get_combined_resonance(tick)
    else:
        chladni["flute_sync"] = None
        chladni["flute_resonance"] = 0.0

    # Add book publications / key events
    chladni["book_publication"] = BOOK_PUBLICATIONS.get(year)
    chladni["key_event"] = KEY_EVENTS.get(year)

    return chladni


def get_arithmetic_sequence() -> Dict[str, object]:
    """
    Get the arithmetic sequence discovery data.

    Returns the formula and all 7 beats with their properties.
    """
    sequencer = get_step_sequencer()
    return {
        "formula": sequencer.sequence_formula(),
        "step_interval": STEP_INTERVAL,
        "step_offset": STEP_OFFSET,
        "num_beats": SEVEN,
        "beats": [
            {
                "number": b.beat_number,
                "year": b.year,
                "delta": b.delta,
                "phase": b.phase.name,
                "formula": b.formula,
                "mantra_word": b.mantra_word,
                "call_response": b.call_response,
            }
            for b in sequencer.get_sequence()
        ],
        "flute_sync_years": FluteSync.get_sync_years(),
    }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Core Constants
    "BUILD_YEAR",
    "RUNTIME_END",
    "RUNTIME_YEARS",
    "PARAMPARA",
    # Multi-VCO Constants (Prime Chain)
    "MODULO_KRISHNA",
    "MODULO_PARAMPARA",
    "MODULO_NADI",
    "MODULO_MALA",
    "MODULO_QUANTUM",
    "PRIME_CHAIN",
    # Weights
    "WEIGHT_HARE",
    "WEIGHT_KRISHNA",
    "WEIGHT_RAMA",
    # Mahamantra Constants
    "SEVEN",
    "NAVA",
    "HARE_COUNT",
    # Step Sequencer Constants
    "DOUBLE_DIGIT_YEARS",
    "STEP_INTERVAL",
    "STEP_OFFSET",
    "SEVEN_BEATS_DELTAS",
    # Functions
    "triangular",
    "is_triangular",
    "get_phase",
    "analyze_year",
    "get_arithmetic_sequence",
    # Types & Classes
    "LilaPhase",
    "YearFrequency",
    "LilaChronology",
    "get_lila_chronology",
    # Step Sequencer
    "StepBeat",
    "LilaStepSequencer",
    "get_step_sequencer",
    # Kirtan Runtime
    "KirtanState",
    "KirtanRuntime",
    "get_kirtan_runtime",
    # Flute Sync
    "FluteSync",
    # Synth Presets
    "LilaSynthParams",
    "LILA_SYNTH_PRESETS",
    # Data
    "PHASE_BOUNDARIES",
    "BOOK_PUBLICATIONS",
    "KEY_EVENTS",
]
