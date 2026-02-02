"""
BRAHMA - Position 1
===================

Quarter: GENESIS
OpCode: LOAD_ROOT
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 74 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x96910869"  # GenesisByte

from typing import Final

# Backward-compat constants
POSITION: Final[int] = 1
QUARTER: Final[str] = "genesis"
OPCODE: Final[str] = "LOAD_ROOT"
PARAMPARA_VECTOR: Final[int] = 74


def execute(input_text: str, context: dict = None) -> dict:
    """
    BRAHMA EXECUTION - Creation & Genesis
    
    Stateless execution wrapper for BrahmaService.
    NO service instantiation needed - pure function!
    """
    from vibe_core.mahamantra.substrate.ledger import InMemoryLedger
    from vibe_core.protocols.mahajanas.brahma import BrahmaService
    
    # Create ephemeral service with in-memory ledger
    ledger = InMemoryLedger()
    service = BrahmaService(ledger)
    
    # Parse intent and call appropriate method
    intent = input_text.lower().strip()
    
    if "wake" in intent:
        result = service.wake(sovereign_id="mahamantra")
        return {"success": result, "action": "wake", "phase": service.get_phase().value}
    
    elif "load" in intent:
        result = service.load_root(root_path="/")
        return {"success": result, "action": "load_root", "phase": service.get_phase().value}
    
    elif "alloc" in intent:
        result = service.alloc_mem(size_bytes=1024)
        return {"success": result.success, "action": "alloc_mem", "allocated": result.allocated_bytes}
    
    else:
        # Default: show state
        state = service.get_state()
        return {"success": True, "action": "get_state", "state": state}


def __getattr__(name: str) -> object:
    """
    Lazy load BrahmaService and NullBrahma.
    NO MANUAL WIRING - auto-discovery needs these exports.
    """
    if name == "BrahmaService":
        from vibe_core.protocols.mahajanas.brahma import BrahmaService

        return BrahmaService

    if name == "NullBrahma":
        from vibe_core.protocols.mahajanas.brahma import NullBrahma

        return NullBrahma

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


__all__ = ["BrahmaService", "POSITION", "QUARTER", "OPCODE", "PARAMPARA_VECTOR"]
