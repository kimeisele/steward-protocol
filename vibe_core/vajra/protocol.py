"""
⚡ VAJRA Protocol - The Standard Wiring Interface
=================================================

Defines what it means to be a "wirable" component in the Steward Protocol.

Any component that needs kernel access MUST implement this protocol.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x273588cf"  # GenesisByte: parampara % 37 == 0

from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel


@runtime_checkable
class WiringProtocol(Protocol):
    """
    Protocol for components that can be wired to the kernel.

    Components implementing this protocol can be:
    - Auto-wired via `auto_wire(kernel, component)`
    - Validated via `check_wired(component)`
    - Enforced via `@assert_wired` decorator

    REQUIRED:
        _vibe_kernel: Optional kernel reference (None when unwired)
        inject_kernel(kernel): Method to inject kernel reference

    RECOMMENDED:
        _get_ledger(): Helper to safely access kernel.ledger
    """

    _vibe_kernel: Optional["RealVibeKernel"]

    def inject_kernel(self, kernel: "RealVibeKernel") -> None:
        """
        ⚡ VAJRA: Inject the core VibeKernel for ledger access.

        This method MUST:
        1. Store kernel reference in self._vibe_kernel
        2. Log the injection (recommended)
        3. Propagate to sub-components if applicable

        Args:
            kernel: The RealVibeKernel instance
        """
        ...


def is_wirable(obj: object) -> bool:
    """
    Check if an object implements WiringProtocol.

    Args:
        obj: Any object to check

    Returns:
        True if object has _vibe_kernel attribute and inject_kernel method
    """
    return (
        hasattr(obj, "_vibe_kernel") and hasattr(obj, "inject_kernel") and callable(getattr(obj, "inject_kernel", None))
    )


def is_wired(obj: object) -> bool:
    """
    Check if a wirable object has been wired.

    Args:
        obj: A wirable object

    Returns:
        True if _vibe_kernel is not None
    """
    if not is_wirable(obj):
        return False
    return getattr(obj, "_vibe_kernel", None) is not None
