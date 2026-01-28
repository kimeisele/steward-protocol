"""
MAHAMANTRA ADAPTERS - Enterprise/Science Interface Layer
=========================================================

"yad yad ācarati śreṣṭhas tat tad evetaro janaḥ"
"Whatever action a great man performs, common men follow."
— Bhagavad Gita 3.21

FOLDER IS WIRING - No manual imports needed.
Use __getattr__ for lazy loading.

USAGE:
    from vibe_core.mahamantra.adapters import MahaTransform
    from vibe_core.mahamantra.adapters import MahaClassifier
    # etc. - all discovered automatically
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"  # Position 3 - The Divine Messenger
__position__ = 3
__genesis__ = "0xADAPT37"  # Adapter layer

# =============================================================================
# LAZY IMPORT REGISTRY - Folder IS wiring
# =============================================================================

_LAZY_IMPORTS = {
    # transform.py
    "MahaTransform": "transform",
    # hash.py
    "DeterministicHash": "hash",
    # routing.py
    "HolographicRouter": "routing",
    # orchestrator.py
    "Orchestrator": "orchestrator",
    # pipeline.py
    "MahamantraPipeline": "pipeline",
    "PipelineResult": "pipeline",
    "GenesisResult": "pipeline",
    "DharmaResult": "pipeline",
    "KarmaResult": "pipeline",
    "MokshaResult": "pipeline",
    # attention.py
    "MahaAttention": "attention",
    "AttentionResult": "attention",
    # bio.py
    "LotusBio": "bio",
    "KmerResult": "bio",
    # network.py
    "LotusIPRouter": "network",
    "RouteResult": "network",
    # synth.py
    "MahaSynth": "synth",
    "SynthParams": "synth",
    "StepResult": "synth",
    "CycleResult": "synth",
    "ResonanceResult": "synth",
    "SpectrumResult": "synth",
    "SYNTH_PRESETS": "synth",
    # classification.py
    "MahaClassifier": "classification",
    "ClassificationResult": "classification",
    "ComparisonResult": "classification",
    # compute.py
    "MahaCompute": "compute",
    "DataAnalysis": "compute",
    "ComputeUnit": "compute",
    "MemoryTier": "compute",
    # hardware.py
    "MahaHardware": "hardware",
    "HardwareSpec": "hardware",
    "PipelineStageInfo": "hardware",
    "VerificationResult": "hardware",
    "PipelineStage": "hardware",
    # compression.py
    "MahaCompression": "compression",
    "CompressionResult": "compression",
    "SamskaraResult": "compression",
    "PhysicsVerification": "compression",
    "IntentLevel": "compression",
    "IntentGuna": "compression",
    "SamskaraLevel": "compression",
    "SamskaraScope": "compression",
    # japa.py
    "MahaJapa": "japa",
    "RoundResult": "japa",
    "MalaResult": "japa",
    "GoldenAgeStatus": "japa",
    "CollapseResult": "japa",
    "JapaState": "japa",
    # llm.py
    "MahaLLM": "llm",
    "RouteResult": "llm",
    "RegistrationResult": "llm",
    "RouterStats": "llm",
    "IntentCategory": "llm",
    # vibrational_engine.py - THE BIDIRECTIONAL LOOP
    "VibrationalEngine": "vibrational_engine",
    "VibrationalResult": "vibrational_engine",
    "VibrationalState": "vibrational_engine",
    "vibrate": "vibrational_engine",
    "vibrate_batch": "vibrational_engine",
    "get_engine": "vibrational_engine",
}


def __getattr__(name: str):
    """Lazy import on attribute access. Folder IS wiring."""
    if name in _LAZY_IMPORTS:
        import importlib
        module_name = _LAZY_IMPORTS[name]
        module = importlib.import_module(f".{module_name}", __package__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = list(_LAZY_IMPORTS.keys())
