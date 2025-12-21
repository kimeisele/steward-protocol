"""
OPUS-200: Sanskrit Phonetic Matrix - The Substrate of Computation

"वर्णानां वर्गाः पञ्च" - "The phonemes have five classes"

This is NOT keyword matching. This is PHYSICS.

Each phoneme's properties are determined by where in the mouth it's articulated.
This is truth that cannot be faked. This is the basis of computation.

The Sanskrit Varnamala (alphabet matrix):

         | Unvoiced | Aspirated | Voiced | VoicedAsp | Nasal |
---------|----------|-----------|--------|-----------|-------|
KANTHYA  |    क     |     ख     |   ग    |     घ     |   ङ   | (Throat → Kernel)
TALAVYA  |    च     |     छ     |   ज    |     झ     |   ञ   | (Palate → Flow)
MURDHANYA|    ट     |     ठ     |   ड    |     ढ     |   ण   | (Cerebral → Logic)
DANTYA   |    त     |     थ     |   द    |     ध     |   न   | (Dental → Interface)
OSHTHYA  |    प     |     फ     |   ब    |     भ     |   म   | (Lips → Output)

Position determines ENERGY:
- Unvoiced (0): Pure, minimal energy
- Aspirated (1): Breath added, expansion
- Voiced (2): Vibration, activity
- VoicedAsp (3): Maximum energy
- Nasal (4): Resonance, continuity
"""

import hashlib
from dataclasses import dataclass
from enum import IntEnum
from typing import List, Tuple


class Varga(IntEnum):
    """
    The 5 Articulation Points - WHERE in the mouth.

    This maps to system architecture layers.
    """

    KANTHYA = 0  # कवर्ग - Throat/Guttural → KERNEL (deepest)
    TALAVYA = 1  # चवर्ग - Palate → COGNITION/FLOW
    MURDHANYA = 2  # टवर्ग - Cerebral/Retroflex → LOGIC/REPAIR
    DANTYA = 3  # तवर्ग - Dental → INTERFACE/DATA
    OSHTHYA = 4  # पवर्ग - Labial/Lips → OUTPUT (surface)


class Sthana(IntEnum):
    """
    The 5 Positions within each Varga - HOW it's articulated.

    This maps to energy/intensity levels.
    """

    SPARSHA = 0  # Unvoiced stop - Pure, clean
    MAHAPRANA = 1  # Aspirated - Breath, expansion
    GHOSHAVAT = 2  # Voiced - Active, vibrating
    GHOSHMAHA = 3  # Voiced aspirated - Maximum energy
    ANUNASIKA = 4  # Nasal - Resonant, continuous


class Guna(IntEnum):
    """
    The 3 Modes of Nature - Quality of action.
    """

    TAMAS = -1  # Inertia, storage, read
    SATTVA = 0  # Balance, observe, maintain
    RAJAS = 1  # Activity, execute, transform


# =============================================================================
# THE PHONEME MATRIX - Based on Sanskrit Varnamala
# =============================================================================

# Maps Latin characters to (Varga, Sthana)
# This is the PHYSICS - where the sound originates in the mouth

PHONEME_MATRIX: dict[str, Tuple[Varga, Sthana]] = {
    # KANTHYA (Throat/Guttural) - Maps to KERNEL
    "k": (Varga.KANTHYA, Sthana.SPARSHA),  # क - unvoiced
    "K": (Varga.KANTHYA, Sthana.MAHAPRANA),  # ख - aspirated
    "g": (Varga.KANTHYA, Sthana.GHOSHAVAT),  # ग - voiced
    "G": (Varga.KANTHYA, Sthana.GHOSHMAHA),  # घ - voiced aspirated
    "n": (Varga.KANTHYA, Sthana.ANUNASIKA),  # ङ - nasal (using 'n' for guttural nasal context)
    "h": (Varga.KANTHYA, Sthana.MAHAPRANA),  # ह - aspirate (visarga)
    # TALAVYA (Palate) - Maps to COGNITION/FLOW
    "c": (Varga.TALAVYA, Sthana.SPARSHA),  # च - unvoiced
    "C": (Varga.TALAVYA, Sthana.MAHAPRANA),  # छ - aspirated
    "j": (Varga.TALAVYA, Sthana.GHOSHAVAT),  # ज - voiced
    "J": (Varga.TALAVYA, Sthana.GHOSHMAHA),  # झ - voiced aspirated
    "s": (Varga.TALAVYA, Sthana.SPARSHA),  # श - palatal sibilant
    "y": (Varga.TALAVYA, Sthana.GHOSHAVAT),  # य - semivowel
    # MURDHANYA (Cerebral/Retroflex) - Maps to LOGIC
    "t": (Varga.MURDHANYA, Sthana.SPARSHA),  # ट - unvoiced (retroflex)
    "T": (Varga.MURDHANYA, Sthana.MAHAPRANA),  # ठ - aspirated
    "d": (Varga.MURDHANYA, Sthana.GHOSHAVAT),  # ड - voiced
    "D": (Varga.MURDHANYA, Sthana.GHOSHMAHA),  # ढ - voiced aspirated
    "r": (Varga.MURDHANYA, Sthana.GHOSHAVAT),  # र - retroflex approximant
    # DANTYA (Dental) - Maps to INTERFACE
    # Using alternate chars since t/d taken by MURDHANYA
    "z": (Varga.DANTYA, Sthana.SPARSHA),  # Dental unvoiced (placeholder)
    "x": (Varga.DANTYA, Sthana.GHOSHAVAT),  # Dental voiced (placeholder)
    "l": (Varga.DANTYA, Sthana.GHOSHAVAT),  # ल - lateral
    # OSHTHYA (Labial/Lips) - Maps to OUTPUT
    "p": (Varga.OSHTHYA, Sthana.SPARSHA),  # प - unvoiced
    "P": (Varga.OSHTHYA, Sthana.MAHAPRANA),  # फ - aspirated
    "b": (Varga.OSHTHYA, Sthana.GHOSHAVAT),  # ब - voiced
    "B": (Varga.OSHTHYA, Sthana.GHOSHMAHA),  # भ - voiced aspirated
    "m": (Varga.OSHTHYA, Sthana.ANUNASIKA),  # म - nasal
    "v": (Varga.OSHTHYA, Sthana.GHOSHAVAT),  # व - labial approximant
    "w": (Varga.OSHTHYA, Sthana.GHOSHAVAT),  # व - alternate
    "f": (Varga.OSHTHYA, Sthana.MAHAPRANA),  # फ - labiodental (borrowed)
    # VOWELS - Maps to SHAKTI (Energy)
    "a": (Varga.KANTHYA, Sthana.GHOSHAVAT),  # अ - existence, throat
    "i": (Varga.TALAVYA, Sthana.GHOSHAVAT),  # इ - focus, palate
    "u": (Varga.OSHTHYA, Sthana.GHOSHAVAT),  # उ - output, lips
    "e": (Varga.TALAVYA, Sthana.GHOSHAVAT),  # ए - flow, palate
    "o": (Varga.OSHTHYA, Sthana.GHOSHAVAT),  # ओ - manifestation, lips
}

# Default for unknown phonemes
DEFAULT_PHONEME = (Varga.MURDHANYA, Sthana.GHOSHAVAT)


@dataclass
class VarnaTensor:
    """
    The Multi-Dimensional State Vector.

    Dimensions:
        varga_vector: Distribution across 5 articulation points [K,T,M,D,O]
        sthana_vector: Distribution across 5 positions [S,M,G,GM,A]
        shakti: Total phonetic energy (normalized)
        guna: Mode (-1=Tamas, 0=Sattva, 1=Rajas)
        entropy: Cryptographic mass (hash-derived)

    This is a TRUE multi-dimensional tensor, not a collapsed scalar.
    """

    varga_vector: Tuple[float, float, float, float, float]  # 5D: KTMDO
    sthana_vector: Tuple[float, float, float, float, float]  # 5D: SMGGMA
    shakti: float  # Total energy
    guna: int  # Mode
    entropy: float  # Crypto mass

    # Metadata
    source: str = ""
    phoneme_count: int = 0

    def to_flat_vector(self) -> Tuple[float, ...]:
        """Flatten to 12D vector for similarity computation."""
        return (
            *self.varga_vector,  # 5D
            *self.sthana_vector,  # 5D
            self.shakti,  # 1D
            (self.guna + 1) / 2.0,  # 1D normalized
        )

    def resonance_signature(self) -> str:
        """Compact signature for debugging."""
        v_max = max(range(5), key=lambda i: self.varga_vector[i])
        s_max = max(range(5), key=lambda i: self.sthana_vector[i])
        return f"{Varga(v_max).name[:3]}.{Sthana(s_max).name[:3]}"

    def __repr__(self) -> str:
        sig = self.resonance_signature()
        return f"VarnaTensor({sig}, ψ={self.entropy:.3f}, E={self.shakti:.2f})"


def analyze_phonemes(text: str) -> Tuple[List[Tuple[Varga, Sthana]], int]:
    """
    Analyze text phonetically.

    Returns list of (Varga, Sthana) for each recognized phoneme,
    and total phoneme count.
    """
    phonemes = []
    for char in text.lower():
        if char in PHONEME_MATRIX:
            phonemes.append(PHONEME_MATRIX[char])
        elif char.upper() in PHONEME_MATRIX:
            phonemes.append(PHONEME_MATRIX[char.upper()])
        # Skip non-phonemic characters (numbers, punctuation, etc.)

    return phonemes, len(phonemes) if phonemes else 1


def compute_varga_distribution(phonemes: List[Tuple[Varga, Sthana]]) -> Tuple[float, ...]:
    """
    Compute normalized distribution across Vargas.

    Returns 5D vector: [KANTHYA, TALAVYA, MURDHANYA, DANTYA, OSHTHYA]
    """
    counts = [0.0] * 5
    for varga, _ in phonemes:
        counts[varga] += 1

    total = sum(counts) or 1
    return tuple(c / total for c in counts)


def compute_sthana_distribution(phonemes: List[Tuple[Varga, Sthana]]) -> Tuple[float, ...]:
    """
    Compute normalized distribution across Sthanas (positions).

    Returns 5D vector: [SPARSHA, MAHAPRANA, GHOSHAVAT, GHOSHMAHA, ANUNASIKA]
    """
    counts = [0.0] * 5
    for _, sthana in phonemes:
        counts[sthana] += 1

    total = sum(counts) or 1
    return tuple(c / total for c in counts)


def compute_shakti(phonemes: List[Tuple[Varga, Sthana]]) -> float:
    """
    Compute total phonetic energy.

    Energy increases with:
    - Voiced phonemes (vibration)
    - Aspirated phonemes (breath)
    - More phonemes (length)
    """
    if not phonemes:
        return 0.0

    energy = 0.0
    for _, sthana in phonemes:
        # Energy weights by position
        weights = {
            Sthana.SPARSHA: 0.2,  # Pure, minimal
            Sthana.MAHAPRANA: 0.6,  # Aspirated, breath
            Sthana.GHOSHAVAT: 0.8,  # Voiced, active
            Sthana.GHOSHMAHA: 1.0,  # Maximum
            Sthana.ANUNASIKA: 0.5,  # Resonant
        }
        energy += weights.get(sthana, 0.5)

    # Normalize by length, cap at 1.0
    return min(1.0, energy / len(phonemes))


def infer_guna(text: str) -> Guna:
    """
    Infer mode from phonetic qualities.

    - High voiced energy → RAJAS (active)
    - High nasal/pure → TAMAS (stable)
    - Balanced → SATTVA
    """
    phonemes, _ = analyze_phonemes(text)
    if not phonemes:
        return Guna.SATTVA

    voiced = sum(1 for _, s in phonemes if s in (Sthana.GHOSHAVAT, Sthana.GHOSHMAHA))
    stable = sum(1 for _, s in phonemes if s in (Sthana.SPARSHA, Sthana.ANUNASIKA))

    total = len(phonemes)

    if voiced / total > 0.6:
        return Guna.RAJAS
    elif stable / total > 0.6:
        return Guna.TAMAS
    else:
        return Guna.SATTVA


def compute_entropy(data: bytes) -> float:
    """
    Compute cryptographic entropy as MASS.

    This is not verification - this is a computational dimension.
    High entropy = high mass = more gravitational pull in resonance.
    """
    if not data:
        return 0.0

    # Shannon-like entropy estimation
    byte_counts = [0] * 256
    for b in data:
        byte_counts[b] += 1

    length = len(data)
    entropy = 0.0
    for count in byte_counts:
        if count > 0:
            p = count / length
            entropy -= p * (p if p > 0 else 1)  # Simplified entropy

    # Normalize to 0-1
    return min(1.0, abs(entropy) * 10)


def encode(text: str, salt: str = "") -> VarnaTensor:
    """
    Encode text into a VarnaTensor.

    This is the SANSKRIT COMPILER - text becomes physics.

    Args:
        text: Input text to encode
        salt: Cryptographic salt (session nonce, ledger hash)

    Returns:
        VarnaTensor with phonetic and cryptographic dimensions
    """
    # 1. Phonetic analysis
    phonemes, count = analyze_phonemes(text)

    # 2. Compute distributions
    varga_dist = compute_varga_distribution(phonemes)
    sthana_dist = compute_sthana_distribution(phonemes)

    # 3. Compute energy
    shakti = compute_shakti(phonemes)

    # 4. Compute mode
    guna = infer_guna(text)

    # 5. Compute cryptographic mass
    hash_input = f"{text}:{salt}".encode("utf-8")
    hash_digest = hashlib.sha256(hash_input).digest()
    entropy = compute_entropy(hash_digest)

    return VarnaTensor(
        varga_vector=varga_dist,
        sthana_vector=sthana_dist,
        shakti=shakti,
        guna=guna,
        entropy=entropy,
        source=text,
        phoneme_count=count,
    )


# =============================================================================
# COMPRESSION: Sanskrit can compress meaning into structure
# =============================================================================


def compress_to_akshara(tensor: VarnaTensor) -> str:
    """
    Compress tensor back to Sanskrit syllable.

    This demonstrates the reversibility - structure encodes meaning.
    """
    # Find dominant Varga
    v_idx = max(range(5), key=lambda i: tensor.varga_vector[i])
    # Find dominant Sthana
    s_idx = max(range(5), key=lambda i: tensor.sthana_vector[i])

    # Map back to Devanagari (simplified)
    AKSHARA_MATRIX = [
        ["क", "ख", "ग", "घ", "ङ"],  # KANTHYA
        ["च", "छ", "ज", "झ", "ञ"],  # TALAVYA
        ["ट", "ठ", "ड", "ढ", "ण"],  # MURDHANYA
        ["त", "थ", "द", "ध", "न"],  # DANTYA
        ["प", "फ", "ब", "भ", "म"],  # OSHTHYA
    ]

    return AKSHARA_MATRIX[v_idx][s_idx]


# =============================================================================
# Self-test
# =============================================================================

if __name__ == "__main__":
    print("OPUS-200: Sanskrit Phonetic Matrix\n")
    print("=" * 60)

    test_cases = [
        ("kernel", ""),  # k → KANTHYA (Kernel)
        ("connect", ""),  # c → TALAVYA (Flow)
        ("transform", ""),  # t → MURDHANYA (Logic)
        ("print", ""),  # p → OSHTHYA (Output)
        ("manas", ""),  # m → OSHTHYA, but nasal
        ("boot", "session1"),  # b → OSHTHYA
        ("boot", "session2"),  # Same text, different salt → different entropy
    ]

    print("\nPhonetic Analysis:")
    print("-" * 60)

    for text, salt in test_cases:
        tensor = encode(text, salt)
        akshara = compress_to_akshara(tensor)

        print(f"\n'{text}' (salt='{salt}')")
        print(f"  Tensor: {tensor}")
        print(f"  Varga:  {[f'{v:.2f}' for v in tensor.varga_vector]}")
        print(f"  Sthana: {[f'{s:.2f}' for s in tensor.sthana_vector]}")
        print(f"  Akshara: {akshara}")
