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


def on_bhoga(state: dict) -> None:
    """
    Reactor Hook: Called when ShadowReactor executes index 1 (Brahma).

    CONNECTS THE EARS (ShadowReactor) TO THE BRAIN (Service).
    """
    # 1. Access Payload (The Intent)
    payload_bytes = state.get("payload")
    if not payload_bytes:
        state["execution_result"] = {"error": "No payload provided to on_bhoga"}
        return

    try:
        # 2. Decode Intent
        intent_text = payload_bytes.decode("utf-8")

        # 3. Execute Service (Reuse existing logic)
        result = execute(intent_text)

        # 4. Return Result (Phase 1 Bridge)
        state["execution_result"] = result

    except Exception as e:
        state["execution_result"] = {"error": f"Brahma execution failed: {str(e)}"}


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
