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


__all__ = [
    # Varna
    "VarnaType",
    "Varna",
    "SVARA",
    "MATRA",
    "VIRAMA",
    "VYANJANA",
    "get_varna_by_devanagari",
    "get_varna_by_iast",
    "decompose_devanagari",
    # Aksara
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
    # Pada
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
]
