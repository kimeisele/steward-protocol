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

import math
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
    "BUILD_YEAR",
    "RUNTIME_END",
    "RUNTIME_YEARS",
    "PARAMPARA",
    "LilaPhase",
    "YearFrequency",
    "LilaChronology",
    "get_lila_chronology",
    "get_phase",
    "PHASE_BOUNDARIES",
]
