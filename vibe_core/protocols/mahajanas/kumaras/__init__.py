"""
KUMARAS - The 4th Mahajana (Purity/Reset)
=========================================
OpCode: reset_ip (Bit 4)
Opulence: Shri (Beauty/Fortune)

The Four Kumaras - Sanaka, Sanandana, Sanatana, Sanat-kumara.
Eternally five years old. Eternally pure.

Kumaras OWN all purity protocols:
- State Reset
- Instruction Pointer Reset
- Sanitization
- Input Validation
- Shuddhi (Purification)

A polluted system cannot function. Kumaras restore purity.
"""

from typing import Protocol, runtime_checkable, Any


@runtime_checkable
class KumarasProtocol(Protocol):
    """
    The Purity Protocol.
    Any system that maintains purity/cleanliness must implement this.
    """

    def reset(self) -> None:
        """Reset to pure/initial state."""
        ...

    def is_pure(self) -> bool:
        """Check if state is pure/uncorrupted."""
        ...

    def purify(self, data: Any) -> Any:
        """
        Purify/sanitize input data.
        Returns cleaned data.
        """
        ...


class NullKumaras:
    """
    The Already Pure.
    No purification needed (for testing pure inputs).
    """

    def reset(self) -> None:
        pass

    def is_pure(self) -> bool:
        return True

    def purify(self, data: Any) -> Any:
        return data  # Already pure


__all__ = ["KumarasProtocol", "NullKumaras"]
