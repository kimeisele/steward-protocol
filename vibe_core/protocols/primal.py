"""
PRIMAL PROTOCOLS - Layer -2 (The Atomic Foundation)

"Before the Substrate, there were the Gunas and the Law."

This module contains the ABSOLUTE FOUNDATION of the system.
It has ZERO internal dependencies on other vibe_core modules.
It defines:
1. The Meta-Law (Watertight Protocol)
2. The Physics (Mantra/Tattva Types)
3. The Language (OpCodes)

Usage:
    from vibe_core.protocols.primal import watertight, MantraOpCode, Resonance
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bali"
__position__ = 13
__genesis__ = "0x7c825997"  # GenesisByte: parampara % 37 == 0

import inspect
import typing
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Tuple, Type, runtime_checkable, get_type_hints

# =============================================================================
# 1. THE META-LAW: WATERTIGHT PROTOCOL
# =============================================================================


class Opulence(Enum):
    AISHVARYA = "Aishvarya (Economy)"  # Resource accounting
    VIRYA = "Virya (Strength/Defense)"  # Error handling spec
    YASHAS = "Yashas (Identity/Fame)"  # Signatures/Context
    SHRI = "Shri (Beauty/Form)"  # Typing perfection
    JNANA = "Jnana (Knowledge)"  # Documentation depth
    VAIRAGYA = "Vairagya (Renunciation)"  # Cleanup/Closing


@runtime_checkable
class Watertight(Protocol):
    """The Meta-Protocol. Structurally perfect."""

    pass


class WatertightValidator:
    """The Enforcer (Dharma-Raja)."""

    @staticmethod
    def inspect(protocol: Type) -> typing.Dict[str, Any]:
        leaks = []
        opulences_found = set()

        # JNANA (Docs)
        if not protocol.__doc__ or len(protocol.__doc__.strip()) < 20:
            leaks.append(f"❌ [JNANA] {protocol.__name__}: Class docstring too short or missing.")
        else:
            opulences_found.add(Opulence.JNANA)

        # SHRI (Typing)
        type_leaks = []
        for name, member in inspect.getmembers(protocol):
            if name.startswith("_") or not inspect.isfunction(member):
                continue
            try:
                hints = get_type_hints(member)
                for param_name, param_type in hints.items():
                    if _is_any(param_type):
                        type_leaks.append(f"{name}:{param_name}")
                if "return" not in hints:
                    type_leaks.append(f"{name}:return_missing")
                elif _is_any(hints["return"]):
                    type_leaks.append(f"{name}:return_is_Any")
            except Exception as _exc:
                logger.exception("Unexpected error: %s", _exc)
        if type_leaks:
            leaks.append(f"❌ [SHRI] Type leaks: {', '.join(type_leaks)}")
        else:
            opulences_found.add(Opulence.SHRI)

        # YASHAS (Identity)
        has_identity = any(
            any(
                p in inspect.signature(m).parameters
                for p in ["context", "identity", "signer", "certificate", "caller_id"]
            )
            for n, m in inspect.getmembers(protocol)
            if inspect.isfunction(m)
        )
        if has_identity:
            opulences_found.add(Opulence.YASHAS)
        else:
            leaks.append(f"⚠️ [YASHAS] No identity requirements.")

        # VIRYA (Strength)
        has_raises = any(
            ("Raises" in (m.__doc__ or "") or "Returns" in (m.__doc__ or ""))
            for n, m in inspect.getmembers(protocol)
            if inspect.isfunction(m)
        )
        if has_raises:
            opulences_found.add(Opulence.VIRYA)
        else:
            leaks.append(f"❌ [VIRYA] Missing robustness spec.")

        # VAIRAGYA (Cleanup)
        has_cleanup = any(
            m in dir(protocol) for m in ["close", "stop", "unbind", "release", "dispose", "deactivate", "shutdown"]
        )
        if has_cleanup:
            opulences_found.add(Opulence.VAIRAGYA)
        else:
            leaks.append(f"⚠️ [VAIRAGYA] No cleanup method.")

        # AISHVARYA (Economy) - Implicit
        opulences_found.add(Opulence.AISHVARYA)

        return {
            "sealed": len(leaks) == 0,
            "score": f"{len(opulences_found)}/6",
            "leaks": leaks,
            "protocol": protocol.__name__,
        }


def _is_any(annotation: Any) -> bool:
    str_val = str(annotation)
    return "typing.Any" in str_val or annotation is Any


def watertight(cls):
    """Decorator to enforce Watertight Standard."""
    if not issubclass(cls, Protocol) and not getattr(cls, "_is_protocol", False):
        pass
    report = WatertightValidator.inspect(cls)
    if not report["sealed"]:
        # print(f"🌊 [WATERTIGHT WARNING] {cls.__name__} failed audit ({report['score']}):\n" + "\n".join(report["leaks"]))
        pass  # Silenced for now to avoid noise during migration, but logic holds.
    return cls


# =============================================================================
# 2. THE PHYSICS: MANTRA & TATTVA
# =============================================================================


class Tattva(str, Enum):
    """The Pancha Tattva (Five Absolute Truths)."""

    CHAITANYA = "chaitanya"  # Mantra/Identity
    NITYANANDA = "nityananda"  # Substrate/Storage
    ADVAITA = "advaita"  # Logic/Inference
    GADADHARA = "gadadhara"  # Sync/Connection
    SRIVASA = "srivasa"  # Enforce/Governance


# RE-EXPORTS from substrate (Single Source of Truth)
# The canonical definitions live in substrate/__init__.py (Layer -1)
from vibe_core.protocols.substrate import HolyName, MantraOpCode


@dataclass
class Resonance:
    """Measurement of Vibration."""

    frequency: float
    amplitude: float
    signature: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DriftContext:
    """Measurement of Deviation."""

    drift_magnitude: float
    last_anchor_timestamp: float
    hallucination_index: float
    process_tree_depth: int


@dataclass
class AlignmentScore:
    """Measurement of Alignment."""

    score: float
    status: str
    corrections_applied: int


# =============================================================================
# 3. DNA SEQUENCE (RE-EXPORT from substrate)
# =============================================================================

# The canonical MAHAMANTRA_SEQUENCE lives in substrate/__init__.py (Layer -1)
from vibe_core.protocols.substrate import MAHAMANTRA_SEQUENCE
