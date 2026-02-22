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
__genesis__ = "0x141280cf"  # GenesisByte: parampara % 37 == 0  # Adapter layer

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
    # llm.py (RouteResult omitted — conflicts with network.RouteResult; import from llm directly)
    "MahaLLM": "llm",
    "RegistrationResult": "llm",
    "IntentCategory": "llm",
}


def __getattr__(name: str):
    """Lazy import on attribute access. Folder IS wiring."""
    # 1. Check explicit class/function exports
    if name in _LAZY_IMPORTS:
        import importlib
        module_name = _LAZY_IMPORTS[name]
        module = importlib.import_module(f".{module_name}", __package__)
        return getattr(module, name)

    # ==========================================================================
    # FRACTAL ROUTING: "EIN IMPORT. KRISHNA ROUTET ALLES."
    # Any .py file or subpackage in adapters/ is auto-discoverable
    # ==========================================================================
    from pathlib import Path
    import importlib

    adapters_root = Path(__file__).parent

    # 2. Check for subpackage (folder with __init__.py)
    subpkg_path = adapters_root / name
    if subpkg_path.is_dir() and (subpkg_path / "__init__.py").exists():
        return importlib.import_module(f"{__name__}.{name}")

    # 3. Check for module (.py file)
    module_path = adapters_root / f"{name}.py"
    if module_path.exists():
        return importlib.import_module(f"{__name__}.{name}")

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = list(_LAZY_IMPORTS.keys())
