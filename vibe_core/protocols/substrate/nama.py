"""
NAMA - The Holy Name (Triple Encoding)
======================================

"The word Hara is the form of addressing the energy of the Lord,
and the words Krishna and Rama are forms of addressing the Lord Himself.
Both Krishna and Rama mean 'the supreme pleasure,'
and Hara is the supreme pleasure energy of the Lord,
changed to Hare in the vocative."
- Srila Prabhupada

TRIPLE ENCODING (Fractal Holographic):
- DEVANAGARI: Original Sanskrit script
- IAST: International Alphabet of Sanskrit Transliteration
- ROMAN: Western/English representation

The Mahamantra:
हरे कृष्ण हरे कृष्ण कृष्ण कृष्ण हरे हरे । हरे राम हरे राम राम राम हरे हरे ॥
hare kṛṣṇa hare kṛṣṇa kṛṣṇa kṛṣṇa hare hare | hare rāma hare rāma rāma rāma hare hare ||
Hare Krishna Hare Krishna Krishna Krishna Hare Hare | Hare Rama Hare Rama Rama Rama Hare Hare
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0xb765fced"  # GenesisByte: parampara % 37 == 0

from typing import Final, Tuple, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .byte import HolyName, MantraByte


# =============================================================================
# ENCODING TABLES
# =============================================================================

# Import HolyName values for indexing (0=HARE, 1=KRISHNA, 2=RAMA, 3=VOID)
DEVANAGARI: Final[Tuple[str, ...]] = (
    "हरे",  # HARE = 0
    "कृष्ण",  # KRISHNA = 1
    "राम",  # RAMA = 2
    "शून्य",  # VOID = 3 (Maya/Error)
)

IAST: Final[Tuple[str, ...]] = (
    "hare",  # HARE = 0
    "kṛṣṇa",  # KRISHNA = 1
    "rāma",  # RAMA = 2
    "śūnya",  # VOID = 3
)

ROMAN: Final[Tuple[str, ...]] = (
    "Hare",  # HARE = 0
    "Krishna",  # KRISHNA = 1
    "Rama",  # RAMA = 2
    "Void",  # VOID = 3
)


# =============================================================================
# THE COMPLETE MAHAMANTRA (16 words)
# =============================================================================

MAHAMANTRA_DEVANAGARI: Final[str] = "हरे कृष्ण हरे कृष्ण कृष्ण कृष्ण हरे हरे । हरे राम हरे राम राम राम हरे हरे ॥"

MAHAMANTRA_IAST: Final[str] = "hare kṛṣṇa hare kṛṣṇa kṛṣṇa kṛṣṇa hare hare | hare rāma hare rāma rāma rāma hare hare ||"

MAHAMANTRA_ROMAN: Final[str] = (
    "Hare Krishna Hare Krishna Krishna Krishna Hare Hare | Hare Rama Hare Rama Rama Rama Hare Hare"
)


# =============================================================================
# ENCODING FUNCTIONS
# =============================================================================


def to_devanagari(value: int) -> str:
    """Convert HolyName value to Devanagari."""
    if 0 <= value < len(DEVANAGARI):
        return DEVANAGARI[value]
    return DEVANAGARI[3]  # VOID


def to_iast(value: int) -> str:
    """Convert HolyName value to IAST."""
    if 0 <= value < len(IAST):
        return IAST[value]
    return IAST[3]  # VOID


def to_roman(value: int) -> str:
    """Convert HolyName value to Roman."""
    if 0 <= value < len(ROMAN):
        return ROMAN[value]
    return ROMAN[3]  # VOID


def encode_sequence(values: List[int], encoding: str = "iast", separator: str = " ") -> str:
    """
    Encode a sequence of HolyName values.

    Args:
        values: List of HolyName integer values (0-3)
        encoding: "devanagari", "iast", or "roman"
        separator: String to join words with

    Returns:
        Encoded string in specified format
    """
    if encoding == "devanagari":
        return separator.join(to_devanagari(v) for v in values)
    elif encoding == "iast":
        return separator.join(to_iast(v) for v in values)
    elif encoding == "roman":
        return separator.join(to_roman(v) for v in values)
    else:
        raise ValueError(f"Unknown encoding: {encoding}")


def get_triple(value: int) -> Tuple[str, str, str]:
    """
    Get all three encodings for a single value.

    Returns: (devanagari, iast, roman)
    """
    return (to_devanagari(value), to_iast(value), to_roman(value))


__all__ = [
    # Encoding Tables
    "DEVANAGARI",
    "IAST",
    "ROMAN",
    # Complete Mahamantra
    "MAHAMANTRA_DEVANAGARI",
    "MAHAMANTRA_IAST",
    "MAHAMANTRA_ROMAN",
    # Functions
    "to_devanagari",
    "to_iast",
    "to_roman",
    "encode_sequence",
    "get_triple",
]
