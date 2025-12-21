"""
🕉️ OPUS-200: VarnaTensor - The Atom of Sanskrit Computation

"अक्षराणां अकारोऽस्मि" - "Of letters, I am 'A'" (Bhagavad Gita 10.33)

This module defines the VarnaTensor - a 4-dimensional vector that encodes
meaning, energy, mode, and cryptographic integrity as computational coordinates.

This is NOT a metaphor. This is the physics of the reactor.
"""

import hashlib
from dataclasses import dataclass
from enum import IntEnum
from typing import Tuple

# Try numpy, fallback to pure Python
try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class Varga(IntEnum):
    """
    The 5 Layers of Reality (Vargas) mapped to System Architecture.

    Based on Sanskrit phonetic articulation points - this is physical truth.
    """

    KAVARGA = 0  # [क ख ग घ ङ] -> KERNEL / STORAGE (Throat/Base)
    CAVARGA = 1  # [च छ ज झ ञ] -> CONNECTION / I/O (Palate/Link)
    TAVARGA = 2  # [ट ठ ड ढ ण] -> LOGIC / COMPUTE (Cerebral/Structure)
    PAVARGA = 3  # [प फ ब भ म] -> UI / RENDER (Lips/Manifestation)
    ANTARSTHA = 4  # [य र ल व]   -> AGENT / AVATAR (Inner/Consciousness)


class Guna(IntEnum):
    """
    The 3 Modes of Nature (Gunas) mapped to Operation Types.
    """

    TAMAS = -1  # Inertia, Storage, Read-Only
    SATTVA = 0  # Balance, Observe, Pure
    RAJAS = 1  # Activity, Write, Execute


# Phonetic mapping: First character -> Varga
# Based on Sanskrit Varnamala (alphabet matrix)
PHONEME_VARGA_MAP = {
    # KAVARGA: Gutturals (Kernel operations)
    "k": Varga.KAVARGA,
    "g": Varga.KAVARGA,
    "h": Varga.KAVARGA,
    "q": Varga.KAVARGA,  # quasi-guttural
    # CAVARGA: Palatals (Connection/Socket operations)
    "c": Varga.CAVARGA,
    "j": Varga.CAVARGA,
    "s": Varga.CAVARGA,
    "z": Varga.CAVARGA,
    "x": Varga.CAVARGA,
    # TAVARGA: Cerebrals/Dentals (Data/Logic operations)
    "t": Varga.TAVARGA,
    "d": Varga.TAVARGA,
    "n": Varga.TAVARGA,
    "l": Varga.TAVARGA,
    # PAVARGA: Labials (Print/Make/Output operations)
    "p": Varga.PAVARGA,
    "b": Varga.PAVARGA,
    "m": Varga.PAVARGA,
    "f": Varga.PAVARGA,
    "v": Varga.PAVARGA,
    "w": Varga.PAVARGA,
    # ANTARSTHA: Semi-vowels (Agent/System operations)
    "a": Varga.ANTARSTHA,
    "e": Varga.ANTARSTHA,
    "i": Varga.ANTARSTHA,
    "o": Varga.ANTARSTHA,
    "u": Varga.ANTARSTHA,
    "y": Varga.ANTARSTHA,
    "r": Varga.ANTARSTHA,
}


@dataclass
class VarnaTensor:
    """
    The 4D State Vector - The Atom of Sanskrit Computation.

    Replaces ASCII strings with meaning coordinates.

    Dimensions:
        varga:   Layer (Where are we in the system?)
        shakti:  Energy (0.0=Idle, 1.0=Full Load)
        guna:    Mode (-1=Tamas/Read, 0=Sattva/Observe, 1=Rajas/Write)
        entropy: Crypto integrity (Hash density)
    """

    varga: int  # D1: Layer (0-4)
    shakti: float  # D2: Energy (0.0-1.0)
    guna: int  # D3: Mode (-1, 0, 1)
    entropy: float  # D4: Crypto density (0.0-1.0)

    # Original text for debugging
    source: str = ""

    def to_vector(self) -> Tuple[float, float, float, float]:
        """
        Normalized 4D vector for interference calculation.
        All values normalized to 0.0-1.0 range.
        """
        return (
            self.varga / 4.0,  # D1: 0.0 - 1.0
            self.shakti,  # D2: 0.0 - 1.0
            (self.guna + 1) / 2.0,  # D3: 0.0 - 1.0 (maps -1..1 to 0..1)
            self.entropy,  # D4: 0.0 - 1.0
        )

    def to_numpy(self):
        """Convert to numpy array if available."""
        if HAS_NUMPY:
            return np.array(self.to_vector())
        return self.to_vector()

    def __repr__(self) -> str:
        varga_name = Varga(self.varga).name if 0 <= self.varga <= 4 else "UNKNOWN"
        guna_name = Guna(self.guna).name if -1 <= self.guna <= 1 else "UNKNOWN"
        return f"VarnaTensor({varga_name}, शक्ति={self.shakti:.2f}, {guna_name}, ψ={self.entropy:.3f})"


def calculate_entropy(data: bytes) -> float:
    """
    Calculate cryptographic entropy (information density).

    Returns a value between 0.0 (no entropy) and 1.0 (max entropy).
    """
    if not data:
        return 0.0
    return sum(data) / (len(data) * 255)


def infer_varga(text: str) -> Varga:
    """
    Infer the Varga from the first phoneme of the text.

    This is the Sanskrit Compiler's first pass.
    """
    if not text:
        return Varga.ANTARSTHA

    first_char = text[0].lower()
    return PHONEME_VARGA_MAP.get(first_char, Varga.ANTARSTHA)


def infer_guna(text: str) -> Guna:
    """
    Infer the Guna (mode) from the text semantics.

    Simple heuristic - can be extended.
    """
    text_lower = text.lower()

    # RAJAS: Active/Write operations
    if any(verb in text_lower for verb in ["write", "create", "deploy", "run", "execute", "delete", "modify"]):
        return Guna.RAJAS

    # TAMAS: Passive/Read operations
    if any(verb in text_lower for verb in ["read", "get", "load", "fetch", "query", "list", "show"]):
        return Guna.TAMAS

    # SATTVA: Observational/Balanced
    return Guna.SATTVA


def encode_intent(intent_str: str, secret_salt: str = "") -> VarnaTensor:
    """
    Compile text + crypto into a VarnaTensor.

    This is the 'Sanskrit Compiler' - the bridge from language to physics.

    Args:
        intent_str: The intent/instruction text
        secret_salt: Cryptographic salt (session nonce, etc.)

    Returns:
        VarnaTensor with computed dimensions
    """
    # 1. Phonetic analysis -> Varga
    varga = infer_varga(intent_str)

    # 2. Semantic analysis -> Guna
    guna = infer_guna(intent_str)

    # 3. Energy (default to active, can be computed from context)
    shakti = 0.8  # Default active energy

    # 4. Crypto dimension (The Causality Chain)
    hash_input = f"{intent_str}:{secret_salt}".encode("utf-8")
    hash_digest = hashlib.sha256(hash_input).digest()
    entropy = calculate_entropy(hash_digest)

    return VarnaTensor(varga=varga, shakti=shakti, guna=guna, entropy=entropy, source=intent_str)


def encode_context(context_data: dict, salt: str = "") -> VarnaTensor:
    """
    Encode a context dictionary as a VarnaTensor.

    Useful for encoding system state, permissions, etc.
    """
    # Serialize context to string
    import json

    context_str = json.dumps(context_data, sort_keys=True)

    # Use context type for varga inference
    context_type = context_data.get("type", "system")

    return encode_intent(context_type + ":" + context_str, salt)


# =============================================================================
# Self-test
# =============================================================================

if __name__ == "__main__":
    print("🕉️ VarnaTensor Self-Test\n")

    test_intents = [
        ("kernel_boot", "session123"),
        ("create_file", "session123"),
        ("read_config", "session123"),
        ("deploy_production", "session123"),
        ("analyze_logs", "session123"),
    ]

    for intent, salt in test_intents:
        tensor = encode_intent(intent, salt)
        print(f"  '{intent}' -> {tensor}")
        print(f"    Vector: {tensor.to_vector()}\n")
