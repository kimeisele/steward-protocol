"""
MAHAMANTRA PROTOCOL TYPES
=========================

The Shared Vocabulary (Sattva) for the Mahamantra Protocols.
These types define WHAT things are, without defining HOW they work.

"namnam akari bahudha nija-sarva-saktis"
"You have invested all Your potencies in Your names."

SSOT: These Enums are the canonical definitions for Protocols.
Substrate implementations should use these or map to them.
"""

from enum import Enum

# =============================================================================
# QUARTER (The 4 Divisions)
# =============================================================================

class Quarter(str, Enum):
    """
    The four quarters of the Mahamantra.
    
    Hare Krishna Hare Krishna (Schöpfung)
    Krishna Krishna Hare Hare (Gesetz)
    Hare Rama Hare Rama (Handlung)
    Rama Rama Hare Hare (Befreiung)
    """

    GENESIS = "genesis"  # Hare Krishna Hare Krishna (Creation)
    DHARMA = "dharma"    # Krishna Krishna Hare Hare (Law)
    KARMA = "karma"      # Hare Rama Hare Rama (Action)
    MOKSHA = "moksha"    # Rama Rama Hare Hare (Liberation)


# =============================================================================
# SAMPRADAYA (The 4 Chains)
# =============================================================================

class Sampradaya(str, Enum):
    """
    The 4 authorized disciplic successions (Sampradayas).
    Each maps to a Quarter of the Mahamantra.
    """

    BRAHMA = "brahma"    # Brahma -> Madhva -> Chaitanya (GENESIS)
    KUMARA = "kumara"    # Four Kumaras -> Nimbarka (DHARMA)
    SRI = "sri"          # Lakshmi -> Ramanuja (KARMA)
    RUDRA = "rudra"      # Shiva -> Vishnuswami -> Vallabha (MOKSHA)


# =============================================================================
# PHONETIC CLASS (The Sound Structure)
# =============================================================================

class PhoneticClass(str, Enum):
    """
    Phonetic classification for resonance.
    Based on Sanskrit varnas + Western approximations.
    """

    # Vowels (high resonance with HARE)
    VOWEL_A = "A"  # a, ā, अ, आ
    VOWEL_I = "I"  # i, ī, इ, ई
    VOWEL_U = "U"  # u, ū, उ, ऊ
    VOWEL_E = "E"  # e, ai, ए, ऐ
    VOWEL_O = "O"  # o, au, ओ, औ
    VOWEL_R = "R"  # ṛ, ऋ (vocalic r - unique to Sanskrit)

    # Consonants by articulation point
    GUTTURAL = "G"  # k, kh, g, gh, ṅ (throat)
    PALATAL = "P"   # c, ch, j, jh, ñ (palate)
    RETROFLEX = "T" # ṭ, ṭh, ḍ, ḍh, ṇ (curled tongue)
    DENTAL = "D"    # t, th, d, dh, n (teeth)
    LABIAL = "B"    # p, ph, b, bh, m (lips)

    # Special
    SEMIVOWEL = "S" # y, r, l, v
    SIBILANT = "X"  # ś, ṣ, s
    ASPIRATE = "H"  # h (most important - in HARE!)

    # Null
    NULL = "_"
