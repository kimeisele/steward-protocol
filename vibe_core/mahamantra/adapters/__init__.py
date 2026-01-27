"""
MAHAMANTRA ADAPTERS - Enterprise/Science Interface Layer
=========================================================

"yad yad ācarati śreṣṭhas tat tad evetaro janaḥ"
"Whatever action a great man performs, common men follow."
— Bhagavad Gita 3.21

THE ADAPTER PATTERN:
====================
Core (maha_algorithm.py) = Pure Vedic Logic, spiritual nomenclature
Adapter (this module)    = Standard CS/ML interface, enterprise compatibility

PRINCIPLE: The essence is unchanged. Only the presentation adapts.
           Like water in different vessels - same H2O, different shapes.

USAGE:
    # Standard CS interface (what enterprise engineers expect)
    from vibe_core.mahamantra.adapters import MahaTransform

    transform = MahaTransform()
    result = transform.compute(seed=42)
    hash_val = transform.deterministic_hash("my_intent")

    # Same algorithm, different vocabulary.
    # Under the hood: MahaKirtan.compute(), MahaOracle.consult()
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"  # Position 3 - The Divine Messenger (bridges realms)
__position__ = 3
__genesis__ = "0xADAPT37"  # Adapter layer, parampara aligned

# Core Compute
from vibe_core.mahamantra.adapters.transform import MahaTransform
from vibe_core.mahamantra.adapters.hash import DeterministicHash
from vibe_core.mahamantra.adapters.routing import HolographicRouter
from vibe_core.mahamantra.adapters.orchestrator import Orchestrator

# Pipeline
from vibe_core.mahamantra.adapters.pipeline import (
    MahamantraPipeline,
    PipelineResult,
    GenesisResult,
    DharmaResult,
    KarmaResult,
    MokshaResult,
)

# AI/Agents
from vibe_core.mahamantra.adapters.attention import MahaAttention, AttentionResult

# Field-Specific
from vibe_core.mahamantra.adapters.bio import LotusBio, KmerResult
from vibe_core.mahamantra.adapters.network import LotusIPRouter, RouteResult

# Synth (Step Sequencer)
from vibe_core.mahamantra.adapters.synth import (
    MahaSynth,
    SynthParams,
    StepResult as SynthStepResult,
    CycleResult as SynthCycleResult,
    ResonanceResult,
    SpectrumResult,
    SYNTH_PRESETS,
)

# Classification (Cold Engineering Analysis)
from vibe_core.mahamantra.adapters.classification import (
    MahaClassifier,
    ClassificationResult,
    ComparisonResult,
)

__all__ = [
    # Core Compute
    "MahaTransform",
    "DeterministicHash",
    "HolographicRouter",
    "Orchestrator",
    # Pipeline
    "MahamantraPipeline",
    "PipelineResult",
    "GenesisResult",
    "DharmaResult",
    "KarmaResult",
    "MokshaResult",
    # AI/Agents
    "MahaAttention",
    "AttentionResult",
    # Field-Specific
    "LotusBio",
    "KmerResult",
    "LotusIPRouter",
    "RouteResult",
    # Synth (Step Sequencer)
    "MahaSynth",
    "SynthParams",
    "SynthStepResult",
    "SynthCycleResult",
    "ResonanceResult",
    "SpectrumResult",
    "SYNTH_PRESETS",
    # Classification
    "MahaClassifier",
    "ClassificationResult",
    "ComparisonResult",
]
