"""
TEST WATERTIGHT - The Turning Test for Protocols.

"Protocol First defines Contract."

This test defines the LAW for what constitutes a "Watertight" Protocol.
It will also SCAN the existing codebase to report the "Real Score" (User suspects 8%).

THE LAW:
1. No 'Any' (Form).
2. Docstrings mandatory (Meaning).
3. Runtime Checkable (Integrity).
"""

import importlib
import inspect
import pkgutil
from typing import Any, Protocol, runtime_checkable

import pytest

from vibe_core.protocols.universal.watertight import WatertightValidator

# =============================================================================
# DEFINING THE CONTRACT (Test Data)
# =============================================================================


@runtime_checkable
class LeakyProtocol(Protocol):
    """I have a leak."""

    def leak(self, x: Any) -> Any: ...  # LEAK!


@runtime_checkable
class LazyProtocol(Protocol):
    # No Docstring = No Meaning
    def work(self, x: int) -> int: ...


@runtime_checkable
class SealedProtocol(Protocol):
    """
    I am Watertight - the perfect protocol.

    Demonstrates all 6 Opulences:
    - JNANA: Full docstrings
    - SHRI: No Any types
    - YASHAS: Identity context
    - VIRYA: Raises/Returns spec
    - VAIRAGYA: Cleanup method
    - AISHVARYA: Implicit
    """

    def clean(self, x: int, context: str = "") -> int:
        """
        Clean operation with identity.

        Args:
            x: The value to clean
            context: The caller identity

        Returns:
            int: The cleaned value

        Raises:
            ValueError: If x is negative
        """
        ...

    def close(self) -> None:
        """Release resources (VAIRAGYA)."""
        ...


# =============================================================================
# THE TEST ITSELF
# =============================================================================


def test_watertight_validator_logic():
    """Verify the Validator correctly judges Law."""

    # 1. Leaky
    result_leaky = WatertightValidator.inspect(LeakyProtocol)
    assert result_leaky["sealed"] is False
    assert any("leaks detected" in msg for msg in result_leaky["leaks"])

    # 2. Lazy (No Docstring)
    result_lazy = WatertightValidator.inspect(LazyProtocol)
    assert result_lazy["sealed"] is False
    assert any("missing" in msg.lower() for msg in result_lazy["leaks"])

    # 3. Sealed
    result_sealed = WatertightValidator.inspect(SealedProtocol)
    assert result_sealed["sealed"] is True
    assert len(result_sealed["leaks"]) == 0


def test_codebase_reality_check():
    """
    SCANS THE REAL CODEBASE.
    Calculates the % of Watertight Protocols.
    """
    import vibe_core.protocols.universal as universal_protocols

    total = 0
    watertight = 0
    leaky_list = []

    # Walk through universal protocols
    path = list(universal_protocols.__path__)[0]
    for _, name, _ in pkgutil.iter_modules([path]):
        try:
            module = importlib.import_module(f"vibe_core.protocols.universal.{name}")
            for item_name, item in inspect.getmembers(module):
                if inspect.isclass(item) and issubclass(item, Protocol) and item.__module__ == module.__name__:
                    # Found a Protocol!
                    total += 1
                    result = WatertightValidator.inspect(item)
                    if result["sealed"]:
                        watertight += 1
                    else:
                        leaky_list.append(f"{item_name}: {result['leaks']}")
        except Exception as e:
            print(f"Skipping {name}: {e}")

    # Calculate Score
    score = (watertight / total * 100) if total > 0 else 0.0

    print("\n\n🛡️ WATERTIGHT SCAN REPORT")
    print(f"Total Protocols Scanned: {total}")
    print(f"Fully Watertight: {watertight}")
    print(f"REAL SCORE: {score:.1f}% (User predicted 8%)")
    print("\nTop Leaks:")
    for leak in leaky_list[:5]:
        print(f"- {leak}")

    # We assert > 0 just to ensure test runs, but the PRINT is what matters for the user
    assert total > 0
