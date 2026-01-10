"""
MANTRA - Fractal Sound Structure
================================

The complete fractal hierarchy of the Mahamantra:

LEVELS (bottom to top):
- Varna (वर्ण) = Letter (smallest unit)
- Aksara (अक्षर) = Syllable (pronounceable unit)
- Pada (पद) = Word (semantic unit)
- Vakya (वाक्य) = Mantra (16 words)
- Mala (माला) = Round (108 mantras)
- Sadhana (साधना) = Session (16 rounds)

TRIPLE ENCODING:
Every level has three representations:
- Devanagari: Original Sanskrit script
- IAST: International transliteration with diacritics
- Roman: Western approximation

FRACTAL PROPERTY:
"As above, so below" - the same pattern at every level.
Zoom in or out, the structure repeats.

THE 37 FORMULA:
24 (field elements) + 12 (protectors) + 1 (knower) = 37
This appears at every level of the fractal.
"""

# Varna - Individual letters
from .varna import (
    VarnaType,
    Varna,
    SVARA,
    MATRA,
    VIRAMA,
    VYANJANA,
    KAVARGA,
    CAVARGA,
    TAVARGA,
    PAVARGA,
    ANTAHSTHA,
    USHMAN,
    get_varna_by_devanagari,
    get_varna_by_iast,
    decompose_devanagari,
)

# Aksara - Syllables
from .aksara import (
    Aksara,
    AKSARA_HA,
    AKSARA_RE,
    AKSARA_KRI,
    AKSARA_SHNA,
    AKSARA_RAA,
    AKSARA_MA,
    MAHAMANTRA_AKSARAS,
    HARE_AKSARAS,
    KRISHNA_AKSARAS,
    RAMA_AKSARAS,
    join_aksaras,
    get_aksara_count,
)

# Pada - Words
from .pada import (
    PadaType,
    Pada,
    PADA_HARE,
    PADA_KRISHNA,
    PADA_RAMA,
    PADA_BY_TYPE,
    MAHAMANTRA_SEQUENCE,
    get_pada,
    mahamantra_to_string,
    count_padas,
)

# Routing - Fractal connections
from .routing import (
    FractalLevel,
    FractalRoute,
    DIMENSIONS,
    MAHAMANTRA_COUNTS,
    route_pada_to_aksaras,
    route_index_to_pada,
    route_index_to_type,
    iter_mahamantra,
    get_fractal_path,
    QUARTER_1,
    QUARTER_2,
    QUARTER_3,
    QUARTER_4,
    QUARTERS,
    get_quarter,
    get_padas_in_quarter,
)

# Vakya - Mantra level (16 words)
from .vakya import (
    QuarterType,
    Quarter,
    Vakya,
    QUARTER_1 as VAKYA_Q1,
    QUARTER_2 as VAKYA_Q2,
    QUARTER_3 as VAKYA_Q3,
    QUARTER_4 as VAKYA_Q4,
    QUARTERS as VAKYA_QUARTERS,
    MAHAMANTRA,
    create_vakya,
    iter_vakya_quarters,
    iter_vakya_padas,
)

# Mala - Round level (108 mantras)
from .mala import (
    BEADS_PER_MALA,
    SUMERU_COUNT,
    MalaPhase,
    Mala,
    MalaMetrics,
    MALA_METRICS,
    create_mala,
    iter_mala_vakyas,
    get_phase_name,
)

# Sadhana - Session level (16 rounds)
from .sadhana import (
    ROUNDS_PER_SADHANA,
    MANTRAS_PER_SADHANA,
    WORDS_PER_SADHANA,
    SYLLABLES_PER_SADHANA,
    AVG_MANTRA_DURATION,
    AVG_ROUND_DURATION,
    AVG_SADHANA_DURATION,
    SadhanaState,
    SadhanaIntensity,
    Sadhana,
    SadhanaMetrics,
    SADHANA_METRICS,
    create_sadhana,
    create_intensive_sadhana,
    get_intensity_name,
)

# Acintya - The Inconceivable Principle
from .acintya import (
    KRISHNA_SMALLEST,
    KRISHNA_LARGEST,
    ACINTYA_ACCEPTED,
    AcintyaAspect,
    JivaCondition,
    KrishnaPresence,
    KRISHNA,
    JivaState,
    AcintyaAware,
    vibration_is_krishna,
    mantra_not_different_from_source,
    check_bheda_abheda,
)


__all__ = [
    # Varna (Letter)
    "VarnaType",
    "Varna",
    "SVARA",
    "MATRA",
    "VIRAMA",
    "VYANJANA",
    "get_varna_by_devanagari",
    "get_varna_by_iast",
    "decompose_devanagari",
    # Aksara (Syllable)
    "Aksara",
    "AKSARA_HA",
    "AKSARA_RE",
    "AKSARA_KRI",
    "AKSARA_SHNA",
    "AKSARA_RAA",
    "AKSARA_MA",
    "MAHAMANTRA_AKSARAS",
    "HARE_AKSARAS",
    "KRISHNA_AKSARAS",
    "RAMA_AKSARAS",
    "join_aksaras",
    "get_aksara_count",
    # Pada (Word)
    "PadaType",
    "Pada",
    "PADA_HARE",
    "PADA_KRISHNA",
    "PADA_RAMA",
    "PADA_BY_TYPE",
    "MAHAMANTRA_SEQUENCE",
    "get_pada",
    "mahamantra_to_string",
    "count_padas",
    # Routing
    "FractalLevel",
    "FractalRoute",
    "DIMENSIONS",
    "MAHAMANTRA_COUNTS",
    "route_pada_to_aksaras",
    "route_index_to_pada",
    "route_index_to_type",
    "iter_mahamantra",
    "get_fractal_path",
    "QUARTERS",
    "get_quarter",
    "get_padas_in_quarter",
    # Vakya (Mantra - 16 words)
    "QuarterType",
    "Quarter",
    "Vakya",
    "MAHAMANTRA",
    "create_vakya",
    "iter_vakya_quarters",
    "iter_vakya_padas",
    # Mala (Round - 108 mantras)
    "BEADS_PER_MALA",
    "SUMERU_COUNT",
    "MalaPhase",
    "Mala",
    "MalaMetrics",
    "MALA_METRICS",
    "create_mala",
    "iter_mala_vakyas",
    "get_phase_name",
    # Sadhana (Session - 16 rounds)
    "ROUNDS_PER_SADHANA",
    "MANTRAS_PER_SADHANA",
    "WORDS_PER_SADHANA",
    "SYLLABLES_PER_SADHANA",
    "SadhanaState",
    "SadhanaIntensity",
    "Sadhana",
    "SadhanaMetrics",
    "SADHANA_METRICS",
    "create_sadhana",
    "create_intensive_sadhana",
    "get_intensity_name",
    # Acintya (The Inconceivable)
    "KRISHNA_SMALLEST",
    "KRISHNA_LARGEST",
    "ACINTYA_ACCEPTED",
    "AcintyaAspect",
    "JivaCondition",
    "KrishnaPresence",
    "KRISHNA",
    "JivaState",
    "AcintyaAware",
    "vibration_is_krishna",
    "mantra_not_different_from_source",
    "check_bheda_abheda",
]
