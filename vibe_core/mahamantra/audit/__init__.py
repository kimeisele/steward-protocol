"""
AUDIT - Atomic Granular On-Demand System Intelligence
======================================================

PANCHA TATTVA ARCHITECTURE:
audit/
|-- __init__.py     # KSETRAJNA = 1 entry point (this file)
|-- scale.py        # NITYANANDA - measure_scale(), file counts
|-- gaps.py         # ADVAITA - find_gaps(), gap analysis
|-- compliance.py   # SRIVASA - GAD-000, invariants
|-- drift.py        # GADADHARA - broken_lineage, ssot violations
|-- semantic.py     # CHAITANYA - LLM-based logic error detection

USES (NO REINVENTING):
    - project_introspection (research/)
    - InvariantEngine (auditor cartridge)
    - ComplianceTool (auditor cartridge)
    - Watchdog (auditor cartridge)

ATOMIC API:
    audit.scale()      -> Dict[str, int]
    audit.gaps()       -> List[Gap]
    audit.compliance() -> ComplianceReport
    audit.drift()      -> List[DriftItem]
    audit.semantic(file) -> SemanticReport
"""

# === MAHAJANA DECLARATION ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x8000000f"  # 2147483663 % 37 == 0

from vibe_core.mahamantra.protocols._seed import PARAMPARA, KSETRAJNA

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"
assert KSETRAJNA == 1, "KSETRAJNA must be 1"


def __getattr__(name: str):
    """Fractal routing: folder IS wiring."""
    from pathlib import Path
    import importlib

    pkg_root = Path(__file__).parent

    # Subpackage
    subpkg = pkg_root / name
    if subpkg.is_dir() and (subpkg / "__init__.py").exists():
        return importlib.import_module(f"{__name__}.{name}")

    # Module
    module = pkg_root / f"{name}.py"
    if module.exists():
        return importlib.import_module(f"{__name__}.{name}")

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Atomic functions will be added as modules are created
]

