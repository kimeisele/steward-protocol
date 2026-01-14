"""
TATTVA - The Categories of Reality (Thin Wrapper)
==================================================

SSOT: vibe_core.mahamantra.substrate.tattva

SHASTRA-KONFORM nach Bhagavad Gita Kapitel 7 und 13.
satyam eva jayate - The truth is not dependent on the file.

"mattaḥ parataraṁ nānyat kiñcid asti dhanañjaya"
"O conqueror of wealth, there is no truth superior to Me."
— Bhagavad Gita 7.7
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x66ebda6d"  # GenesisByte: parampara % 37 == 0

# =============================================================================
# RE-EXPORT FROM SSOT (mahamantra.substrate.tattva)
# =============================================================================

from vibe_core.mahamantra.substrate.tattva import (
    # SSOT Constants
    SYSTEM_MANIFESTATION,
    # Apara Prakriti (8 Elements)
    AparaPrakriti,
    PANCHA_MAHABHUTAS,
    SUBTLE_ELEMENTS,
    # Kshetra (24 Elements)
    KshetraElement,
    JNANENDRIYAS,
    KARMENDRIYAS,
    TANMATRAS,
    # Para Prakriti (Jiva)
    ParaPrakriti,
    JIVA,
    # Guru Tattva (Transmission)
    GuruTattva,
    GuruConnection,
    # Purushottama (Krishna as Supreme Person)
    Purushottama,
    PURUSHOTTAMA,
    # Summary
    TATTVA_SUMMARY,
)

__all__ = [
    "SYSTEM_MANIFESTATION",
    "AparaPrakriti",
    "PANCHA_MAHABHUTAS",
    "SUBTLE_ELEMENTS",
    "KshetraElement",
    "JNANENDRIYAS",
    "KARMENDRIYAS",
    "TANMATRAS",
    "ParaPrakriti",
    "JIVA",
    "GuruTattva",
    "GuruConnection",
    "Purushottama",
    "PURUSHOTTAMA",
    "TATTVA_SUMMARY",
]
