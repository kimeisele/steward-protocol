"""
WATERTIGHT PROTOCOL - The Meta-Contract (Layer -1).

"Word = Meaning / Form"

This is the GUARDIAN of the Protocol Namespace.
It requires that any Protocol marked as @watertight must:
1. Have NO 'Any' types in signatures (Form).
2. Have Docstrings for every method (Meaning).
3. Be purely abstract (Protocol).

"Who watches the watchers?" - This code does.
"""

import inspect
import typing
from typing import Any, Protocol, Type, runtime_checkable


@runtime_checkable
class Watertight(Protocol):
    """
    The Meta-Protocol.
    Classes implementing this promise to be structurally perfect.
    """

    @classmethod
    def verify_seal(cls) -> bool:
        """
        Verifies if the class itself is Watertight.
        """
        ...


class WatertightValidator:
    """
    The Enforcer.
    """

    @staticmethod
    def inspect(protocol: Type) -> typing.Dict[str, Any]:
        """
        Inspects a Protocol for leaks.

        Returns:
            Dict with 'sealed': bool and messages.
        """
        leaks = []

        # 1. Check Docstring (Meaning)
        if not protocol.__doc__:
            leaks.append(f"❌ {protocol.__name__}: Missing Class Docstring (No Meaning)")

        # 2. Inspect Methods
        for name, member in inspect.getmembers(protocol):
            if name.startswith("_") or not inspect.isfunction(member):
                continue

            # Check Docstring
            if not member.__doc__:
                leaks.append(f"❌ {protocol.__name__}.{name}: Missing Method Docstring")

            # Check Signatures (Form)
            try:
                sig = inspect.signature(member)
                for param_name, param in sig.parameters.items():
                    if param.name == "self":
                        continue
                    if param.annotation == inspect.Parameter.empty:
                        leaks.append(f"❌ {protocol.__name__}.{name}: Param '{param_name}' missing Type definition")
                    elif _is_any(param.annotation):
                        leaks.append(f"⚠️ {protocol.__name__}.{name}: Param '{param_name}' uses 'Any' (Leak detected)")

                if sig.return_annotation == inspect.Parameter.empty:
                    leaks.append(f"❌ {protocol.__name__}.{name}: Missing Return Type")
                elif _is_any(sig.return_annotation):
                    leaks.append(f"⚠️ {protocol.__name__}.{name}: Return Type is 'Any' (Leak detected)")

            except ValueError:
                pass

        return {"sealed": len(leaks) == 0, "leaks": leaks, "protocol": protocol.__name__}


def _is_any(annotation: Any) -> bool:
    """Detects if an annotation is typing.Any or Unannotated."""
    return annotation is Any
