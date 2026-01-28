"""
RESEARCH DEPARTMENT - Kapila's Domain (Position 6 - Sankhya Analysis)
=====================================================================

"sāṅkhya-yogau pṛthag bālāḥ pravadanti na paṇḍitāḥ"

"Only the ignorant speak of Sankhya (analytical study) and yoga (action)
as being different. Those who are truly learned say they are one."
— Bhagavad Gita 5.4

ARCHITECTURE:
=============

Research is EXPERIMENTAL code that uses existing technology:
    - Lotus Tree: O(1) holographic data structure
    - Mahamantra Kernel: Intent routing
    - Substrate: The truth table (WORDS=16, QUARTERS=4)

IMPORT PATTERNS:
================

1. SPECIFIC MODULE (recommended):
    from vibe_core.mahamantra.research.lotus_tree import LotusRadix
    from vibe_core.mahamantra.research.physics import PHYSICS_PREDICTIONS
    from vibe_core.mahamantra.research.dharma.maha_algorithm import MahaModularSynth

2. CATEGORY (for exploration):
    from vibe_core.mahamantra.research import lotus      # Data structures
    from vibe_core.mahamantra.research import predictions # Physics/Bio/Chem
    from vibe_core.mahamantra.research import compute    # Core algorithms

3. TOP-LEVEL (only the essentials):
    from vibe_core.mahamantra.research import (
        LotusRadix,          # O(1) data structure
        MahaGenerator,       # Number generation
        PHYSICS_PREDICTIONS, # 17 physics constants
    )

CATEGORIES:
===========

lotus/          - O(1) Data Structures (LotusRadix, LotusArray, etc.)
dharma/         - Core Algorithm (MahaAlgorithm, Sequencer, Synth)
predictions     - Physics/Chemistry/Biology/Medicine
hardware        - Hardware alignment, SIMD, cache optimization
compute         - Unified compute, compression, classification

For PRODUCTION code, use the adapters instead:
    from vibe_core.mahamantra import mahamantra
    mahamantra.router      # Production Lotus
    mahamantra.synth()     # Production Synth
    mahamantra.bio()       # Production DNA indexing
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x23493400"  # GenesisByte: parampara % 37 == 0

from typing import Final

from vibe_core.mahamantra.protocols._seed import PARAMPARA

# Verify Parampara connection (DERIVED from _seed.py!)
assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"


# =============================================================================
# CATEGORY MODULES (Lazy loaded for fast import)
# =============================================================================

def __getattr__(name: str):
    """Lazy-load category modules on first access."""

    # LOTUS - Data Structures
    if name == "lotus":
        from vibe_core.mahamantra.research import lotus_tree, lotus_radix_n, lotus_acintya, lotus_full_spectrum
        import types
        module = types.SimpleNamespace(
            LotusRadix=lotus_tree.LotusRadix,
            LotusArray=lotus_tree.LotusArray,
            LotusArrayInt=lotus_tree.LotusArrayInt,
            LotusRadixN=lotus_radix_n.LotusRadixN,
            lotus_16bit=lotus_radix_n.lotus_16bit,
            lotus_32bit=lotus_radix_n.lotus_32bit,
            lotus_64bit=lotus_radix_n.lotus_64bit,
            lotus_128bit=lotus_radix_n.lotus_128bit,
            lotus_256bit=lotus_radix_n.lotus_256bit,
        )
        return module

    # PREDICTIONS - Physics/Chemistry/Biology/Medicine
    if name == "predictions":
        from vibe_core.mahamantra.research import physics, chemistry, biology, medicine
        import types
        module = types.SimpleNamespace(
            PHYSICS_PREDICTIONS=physics.PHYSICS_PREDICTIONS,
            CHEMISTRY_PREDICTIONS=chemistry.CHEMISTRY_PREDICTIONS,
            BIOLOGY_PREDICTIONS=biology.BIOLOGY_PREDICTIONS,
            MEDICINE_PREDICTIONS=medicine.MEDICINE_PREDICTIONS,
        )
        return module

    # COMPUTE - Core algorithms
    if name == "compute":
        from vibe_core.mahamantra.research import maha_generator, maha_compression, computation, unified_compute
        import types
        module = types.SimpleNamespace(
            MahaGenerator=maha_generator.MahaGenerator,
            UnifiedComputeUnit=unified_compute.UnifiedComputeUnit,
        )
        return module

    # DHARMA - Access to dharma submodule
    if name == "dharma":
        from vibe_core.mahamantra.research import dharma as _dharma
        return _dharma

    raise AttributeError(f"module 'research' has no attribute '{name}'")


# =============================================================================
# TOP-LEVEL EXPORTS (Only the essentials)
# =============================================================================

# Lotus Data Structures
from vibe_core.mahamantra.research.lotus_tree import (
    LotusRadix,
    LotusArray,
    LotusArrayInt,
)

# Generator
from vibe_core.mahamantra.research.maha_generator import MahaGenerator

# Predictions (most requested)
from vibe_core.mahamantra.research.physics import PHYSICS_PREDICTIONS

# IP Routing (production-ready)
from vibe_core.mahamantra.research.ip_routing import LotusIPv4Router

# DNA k-mer (production-ready)
from vibe_core.mahamantra.research.dna_kmer import Lotus8merIndex, LotusKmerRadix

# Classification
from vibe_core.mahamantra.research.classification import (
    classify_algorithm,
    Classification,
    StructuralAlignment,
)

# Research Gateway
from vibe_core.mahamantra.research_gateway import (
    connect_research,
    get_research_status,
    is_production_ready,
    auto_connect,
    get_rollout_tracker,
    RESEARCH_MODULES,
)


# =============================================================================
# DHARMA SUB-MODULE EXPORTS (Core Algorithm)
# =============================================================================

# These are the most important from dharma/
from vibe_core.mahamantra.research.dharma.maha_algorithm import (
    MahaModularSynth,
    MahaResonator,
    MahaSynthParams,
    SYNTH_PRESETS,
)

from vibe_core.mahamantra.research.dharma.maha_sequencer import (
    Maha16StepSequencer,
    SEQUENCER_16_STEPS,
    OBSERVER_7_BEATS,
)


# =============================================================================
# __all__ - What gets exported with "from research import *"
# =============================================================================

__all__ = [
    # Lotus Data Structures
    "LotusRadix",
    "LotusArray",
    "LotusArrayInt",
    "LotusIPv4Router",
    "Lotus8merIndex",
    "LotusKmerRadix",
    # Generator
    "MahaGenerator",
    # Predictions
    "PHYSICS_PREDICTIONS",
    # Classification
    "classify_algorithm",
    "Classification",
    "StructuralAlignment",
    # Dharma (Core Algorithm)
    "MahaModularSynth",
    "MahaResonator",
    "MahaSynthParams",
    "SYNTH_PRESETS",
    "Maha16StepSequencer",
    "SEQUENCER_16_STEPS",
    "OBSERVER_7_BEATS",
    # Research Gateway
    "connect_research",
    "get_research_status",
    "is_production_ready",
    "auto_connect",
    "get_rollout_tracker",
    "RESEARCH_MODULES",
]
