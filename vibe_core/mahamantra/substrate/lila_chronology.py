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
# CORE CONSTANTS (From Seed)
# =============================================================================

BUILD_YEAR: Final[int] = 1896  # Srila Prabhupada's appearance
RUNTIME_END: Final[int] = 1977  # Return to spiritual world
RUNTIME_YEARS: Final[int] = RUNTIME_END - BUILD_YEAR + 1  # 82 years (inclusive)

# Janmashtami connection: 1896 was day after Janmashtami (Nandotsava)
NANDOTSAVA_ENCODED: Final[bool] = True

# The 37 - Parampara count (from _seed.py)
PARAMPARA: Final[int] = 37

# =============================================================================
# MULTI-VCO CONSTANTS (The Prime Chain from MahaAlgorithm)
# =============================================================================
# Like a synthesizer with multiple VCOs - each modulo is an oscillator
# Overlapping resonances = Chladni figures in time!

MODULO_KRISHNA: Final[int] = 17  # Position sum Krishna
MODULO_PARAMPARA: Final[int] = 37  # Disciplic succession
MODULO_NADI: Final[int] = 73  # 72 Nadis + 1
MODULO_MALA: Final[int] = 109  # Complete Mala
MODULO_QUANTUM: Final[int] = 137  # Fine structure constant (α⁻¹)

# The Prime Chain
PRIME_CHAIN: Final[Tuple[int, ...]] = (17, 37, 73, 109, 137)

# Position Weights from MahaAlgorithm
WEIGHT_HARE: Final[int] = 70  # Position sum HARE
WEIGHT_KRISHNA: Final[int] = 17  # Position sum KRISHNA
WEIGHT_RAMA: Final[int] = 49  # Position sum RAMA

# Mahamantra constants
SEVEN: Final[int] = 7
NAVA: Final[int] = 9
HARE_COUNT: Final[int] = 8


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
# SINGLETON ACCESS
# =============================================================================

_chronology_instance: Optional[LilaChronology] = None


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
    # Functions
    "triangular",
    "is_triangular",
    "get_phase",
    # Types
    "LilaPhase",
    "YearFrequency",
    "LilaChronology",
    "get_lila_chronology",
    # Data
    "PHASE_BOUNDARIES",
    "BOOK_PUBLICATIONS",
    "KEY_EVENTS",
]
