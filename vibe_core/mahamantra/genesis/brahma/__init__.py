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
        phase = service.get_phase().value
        return {
            "success": result,
            "action": "wake",
            "phase": phase,
            "message": f"Brahma [{OPCODE}]: wake (phase={phase})",
        }

    elif "load" in intent:
        result = service.load_root(root_path="/")
        phase = service.get_phase().value
        return {
            "success": result,
            "action": "load_root",
            "phase": phase,
            "message": f"Brahma [{OPCODE}]: load_root (phase={phase})",
        }

    elif "alloc" in intent:
        result = service.alloc_mem(size_bytes=1024)
        return {
            "success": result.success,
            "action": "alloc_mem",
            "allocated": result.allocated_bytes,
            "message": f"Brahma [{OPCODE}]: alloc_mem ({result.allocated_bytes}b)",
        }

    else:
        # Default: show state
        state = service.get_state()
        return {"success": True, "action": "get_state", "state": state, "message": f"Brahma [{OPCODE}]: '{input_text}'"}


_fractal_getattr_fn = None


def __getattr__(name: str) -> object:
    """Explicit exports + fractal discovery fallback."""
    if name == "BrahmaService":
        from vibe_core.protocols.mahajanas.brahma import BrahmaService

        return BrahmaService

    if name == "NullBrahma":
        from vibe_core.protocols.mahajanas.brahma import NullBrahma

        return NullBrahma

    global _fractal_getattr_fn
    if _fractal_getattr_fn is None:
        from vibe_core.mahamantra.substrate.wiring import fractal_getattr

        _fractal_getattr_fn = fractal_getattr(__file__)
    return _fractal_getattr_fn(name)


__all__ = ["BrahmaService", "POSITION", "QUARTER", "OPCODE", "PARAMPARA_VECTOR"]
