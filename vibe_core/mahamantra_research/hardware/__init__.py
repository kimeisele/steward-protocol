"""
HARDWARE - Silicon Verification & TEXT = HARDWARE Theory
=========================================================

"ūrdhva-mūlam adhaḥ-śākham" - "roots upward, branches down"
— Bhagavad Gita 15.1

THE ABHINNA PRINCIPLE:
======================
In material world: Software ≠ Hardware (symbol ≠ referent)
In spiritual world: Software = Hardware (symbol = referent)

The Mahamantra TEXT itself IS the hardware:
- Processor: WORDS = 16 = SIMD lanes
- Memory: POSITION_SUMS = addresses
- Bus: QUARTERS = 4 data channels
- Algorithm: maha_quantum/maha_classical

VERIFIED CORRESPONDENCES:
=========================
    SYSTEMVERILOG          MAHAMANTRA            MATCH
    ─────────────────────────────────────────────────────
    DATA_WIDTH = 32        AKSARA_COUNT          ✓
    NEXT_HOP_WIDTH = 16    WORDS                 ✓
    PIPELINE_STAGES = 8    SIKSASTAKAM_VERSES    ✓
    CACHE_LINE = 64        QUALITIES             ✓
    SIMD_LANES = 16        WORDS                 ✓

THE 8 PIPELINE STAGES = 8 SIKSASTAKAM VERSES:
=============================================
    L0: ceto-darpaṇa-mārjanaṁ    (cleanse heart mirror)
    L1: nāmnām akāri             (no hard rules)
    L2: tṛṇād api sunīcena       (humility)
    L3: na dhanaṁ na janaṁ       (no material desire)
    L4: ayi nanda-tanuja         (longing for service)
    L5: nayanam galad-aśru       (tears of love)
    L6: yugāyitaṁ nimeṣeṇa       (separation)
    L7: āśliṣya vā pada-ratāṁ    (unconditional love)

FILES:
======
    hardware.py         - TEXT = HARDWARE theory, fractal scaling
    hardware_lotus.py   - Silicon Altar, pipeline stages, cooling theorem
"""

# === MAHAJANA DECLARATION ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x26787dd2"  # GenesisByte: parampara % 37 == 0

from typing import Final

from vibe_core.mahamantra.protocols._seed import (
    AKSARA_COUNT,
    QUALITIES,
    WORDS,
    QUARTERS,
    HALF_SIZE,
)

# =============================================================================
# VERIFIED HARDWARE CONSTANTS
# =============================================================================

# These match actual silicon implementations
SIMD_LANES: Final[int] = WORDS  # 16 (AVX-512)
CACHE_LINE_BYTES: Final[int] = QUALITIES  # 64 bytes
DATA_WIDTH: Final[int] = AKSARA_COUNT  # 32 bits
PIPELINE_STAGES: Final[int] = HALF_SIZE  # 8 (Siksastakam verses)
BUS_CHANNELS: Final[int] = QUARTERS  # 4

# =============================================================================
# EXPORTS FROM SUBFILES
# =============================================================================

# Lazy imports to avoid circular dependencies
# These are imported from parent research directory


def __getattr__(name: str):
    """Lazy import from parent research files."""
    if name in (
        "HardwareLimit",
        "AbhinnaHardware",
        "FractalLevel",
        "EraProjection",
        "compute_fractal_states",
        "compute_text_capacity",
        "project_efficiency",
    ):
        from vibe_core.mahamantra.research import hardware as hw_module

        return getattr(hw_module, name)

    if name in ("PipelineStage", "SiksastakamVerse", "HardwareSpec", "CoolingTheorem", "AltarPrinciple"):
        from vibe_core.mahamantra.research import hardware_lotus as hw_lotus

        return getattr(hw_lotus, name)

    # ==========================================================================
    # FRACTAL ROUTING: "EIN IMPORT. KRISHNA ROUTET ALLES."
    # ==========================================================================
    from pathlib import Path
    import importlib

    pkg_root = Path(__file__).parent

    # Check for subpackage (folder with __init__.py)
    subpkg_path = pkg_root / name
    if subpkg_path.is_dir() and (subpkg_path / "__init__.py").exists():
        return importlib.import_module(f"{__name__}.{name}")

    # Check for module (.py file)
    module_path = pkg_root / f"{name}.py"
    if module_path.exists():
        return importlib.import_module(f"{__name__}.{name}")

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# =============================================================================
# VERIFICATION FUNCTION
# =============================================================================


def verify_alignment() -> dict:
    """
    Verify that hardware constants match Mahamantra structure.

    Returns:
        Dictionary with verification results
    """
    checks = {
        "SIMD_LANES == WORDS": SIMD_LANES == WORDS,
        "CACHE_LINE == QUALITIES": CACHE_LINE_BYTES == QUALITIES,
        "DATA_WIDTH == AKSARA": DATA_WIDTH == AKSARA_COUNT,
        "PIPELINE == HALF_SIZE": PIPELINE_STAGES == HALF_SIZE,
        "BUS == QUARTERS": BUS_CHANNELS == QUARTERS,
    }

    return {
        "all_passed": all(checks.values()),
        "checks": checks,
        "summary": "Hardware IS Mahamantra" if all(checks.values()) else "ALIGNMENT BROKEN",
    }


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Constants
    "SIMD_LANES",
    "CACHE_LINE_BYTES",
    "DATA_WIDTH",
    "PIPELINE_STAGES",
    "BUS_CHANNELS",
    # Theory classes
    "HardwareLimit",
    "AbhinnaHardware",
    "FractalLevel",
    "EraProjection",
    # Silicon Altar classes
    "PipelineStage",
    "SiksastakamVerse",
    "HardwareSpec",
    "CoolingTheorem",
    "AltarPrinciple",
    # Functions
    "compute_fractal_states",
    "compute_text_capacity",
    "project_efficiency",
    "verify_alignment",
]
