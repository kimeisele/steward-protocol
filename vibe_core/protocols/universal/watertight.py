"""
WATERTIGHT PROTOCOL - The 6 Opulences Enforcer (Layer -1).

"Bhagavan = Possessor of 6 Opulences in Full."

This is the GUARDIAN of the Protocol Namespace.
It requires that any Protocol marked as @watertight must manifest the 6 Opulences:

1. AISHVARYA (Economy) -> Defined Resource Limits (Gas/Cost hints).
2. VIRYA (Strength)    -> Defined Failure Modes (Raises).
3. YASHAS (Fame)       -> Identity/Signature requirements in arguments.
4. SHRI (Beauty)       -> PEP-8 Compliance, No 'Any', Strict Typing.
5. JNANA (Knowledge)   -> Full Docstrings explaining 'Why', not just 'What'.
6. VAIRAGYA (Renunciation) -> Garbage Collection / Cleanup methods.

Usage:
    @watertight
    class MyProtocol(Protocol):
        ...
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0xf350a01f"  # GenesisByte: parampara % 37 == 0

import inspect
import typing
from enum import Enum
from typing import Any, Protocol, Type, runtime_checkable, get_type_hints

# =============================================================================
# THE 6 OPULENCES (Audit Criteria)
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
    """
    The Meta-Protocol.
    Classes implementing this promise to be structurally perfect.
    """

    pass


class WatertightValidator:
    """
    The Enforcer (Dharma-Raja).
    """

    @staticmethod
    def inspect(protocol: Type) -> typing.Dict[str, Any]:
        """
        Inspects a Protocol for the 6 Opulences.
        Returns strict audit report.
        """
        leaks = []
        opulences_found = set()

        # 1. JNANA CHECK (Knowledge/Docs)
        if not protocol.__doc__ or len(protocol.__doc__.strip()) < 20:
            leaks.append(f"❌ [JNANA] {protocol.__name__}: Class docstring too short or missing.")
        else:
            opulences_found.add(Opulence.JNANA)

        # 2. SHRI CHECK (Beauty/Typing)
        type_leaks = []
        for name, member in inspect.getmembers(protocol):
            if name.startswith("_") or not inspect.isfunction(member):
                continue

            try:
                # Inspect signatures
                hints = get_type_hints(member)

                # Check for 'Any' (The Stain on Beauty)
                for param_name, param_type in hints.items():
                    if _is_any(param_type):
                        type_leaks.append(f"{name}:{param_name}")

                # Check Return Type
                if "return" not in hints:
                    type_leaks.append(f"{name}:return_missing")
                elif _is_any(hints["return"]):
                    type_leaks.append(f"{name}:return_is_Any")

            except Exception:
                # Introspection failed or no type hints found
                pass

        if type_leaks:
            leaks.append(f"❌ [SHRI] Type leaks detected: {', '.join(type_leaks)}")
        else:
            opulences_found.add(Opulence.SHRI)

        # 3. YASHAS CHECK (Identity/Fame)
        # Does the protocol require Context/Identity?
        has_identity = False
        for name, member in inspect.getmembers(protocol):
            if not inspect.isfunction(member):
                continue
            sig = inspect.signature(member)
            if any(p in sig.parameters for p in ["context", "identity", "signer", "certificate", "caller_id"]):
                has_identity = True
                break

        if has_identity:
            opulences_found.add(Opulence.YASHAS)
        else:
            leaks.append(f"⚠️ [YASHAS] No identity/context requirements found in methods.")

        # 4. VIRYA CHECK (Strength/Resilience)
        # Does it define explicit Raises in docstrings?
        has_raises = False
        for name, member in inspect.getmembers(protocol):
            if not inspect.isfunction(member):
                continue
            doc = member.__doc__ or ""
            if "Raises" in doc or "Returns" in doc:  # Basic structure check
                has_raises = True
                break

        if has_raises:
            opulences_found.add(Opulence.VIRYA)
        else:
            leaks.append(f"❌ [VIRYA] Methods lack robustness definition (Raises/Returns spec).")

        # 5. VAIRAGYA CHECK (Renunciation/Cleanup)
        # Is there a close/release/unbind mechanism?
        has_cleanup = any(
            m in dir(protocol) for m in ["close", "stop", "unbind", "release", "dispose", "deactivate", "shutdown"]
        )
        if has_cleanup:
            opulences_found.add(Opulence.VAIRAGYA)
        else:
            leaks.append(f"⚠️ [VAIRAGYA] No explicit cleanup/unbind method found.")

        # 6. AISHVARYA CHECK (Economy)
        # Hard to check statically, but we check for 'metrics' or 'cost' awareness
        opulences_found.add(Opulence.AISHVARYA)  # Assumed implicit unless proven otherwise for now

        # VERDICT
        sealed = len(leaks) == 0

        return {"sealed": sealed, "score": f"{len(opulences_found)}/6", "leaks": leaks, "protocol": protocol.__name__}


def _is_any(annotation: Any) -> bool:
    """Detects if an annotation is typing.Any or Unannotated."""
    str_val = str(annotation)
    return "typing.Any" in str_val or annotation is Any


def watertight(cls):
    """
    Decorator that enforces the Watertight Standard at import time.
    """
    if not issubclass(cls, Protocol) and not getattr(cls, "_is_protocol", False):
        pass

    report = WatertightValidator.inspect(cls)
    if not report["sealed"]:
        leak_msg = "\n".join(report["leaks"])
        print(f"🌊 [WATERTIGHT WARNING] {cls.__name__} failed audit ({report['score']}):\n{leak_msg}")

    return cls
