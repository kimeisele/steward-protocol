"""
OPUS-200/201: Sanskrit Quantum Reactor

A computational paradigm based on phonetic resonance, not boolean logic.

Core Concepts:
- VarnaTensor: Multi-dimensional encoding based on Sanskrit phonetics
- QuantumReactor: Resonance-based computation engine
- Crypto as MASS: Hash entropy influences computational weight

This is NOT a security layer. This is a NEW WAY TO COMPUTE.

Usage:
    from vibe_core.reactor import encode, compute_resonance, get_reactor

    # Encode text to tensor
    tensor = encode("kernel_boot", salt="session123")

    # Compute resonance between texts
    energy = compute_resonance("kernel", "kernal")  # High (similar)
    energy = compute_resonance("kernel", "print")   # Low (different)

    # Use the reactor for manifestation
    reactor = get_reactor()
    field = reactor.manifest("kernel_init", salt="session")
    if field.total_energy > reactor._inertia:
        print("Intent manifested!")
"""

from .matrix import (
    # Data
    PHONEME_MATRIX,
    Guna,
    Sthana,
    # Enums
    Varga,
    # Core tensor
    VarnaTensor,
    # Analysis
    analyze_phonemes,
    compress_to_akshara,
    compute_entropy,
    compute_shakti,
    compute_sthana_distribution,
    compute_varga_distribution,
    # Encoding
    encode,
    infer_guna,
)
from .quantum import (
    QuantumReactor,
    # Core types
    ResonanceField,
    compute_resonance,
    # Functions
    get_reactor,
)

__all__ = [
    # Matrix (Phonetic Foundation)
    "Varga",
    "Sthana",
    "Guna",
    "VarnaTensor",
    "encode",
    "compress_to_akshara",
    "analyze_phonemes",
    "compute_varga_distribution",
    "compute_sthana_distribution",
    "compute_shakti",
    "infer_guna",
    "compute_entropy",
    "PHONEME_MATRIX",
    # Quantum (Resonance Engine)
    "ResonanceField",
    "QuantumReactor",
    "get_reactor",
    "compute_resonance",
]

__version__ = "3.0.0"  # QUANTUM version - phonetic, not keyword
