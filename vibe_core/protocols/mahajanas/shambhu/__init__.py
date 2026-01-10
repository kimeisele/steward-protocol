"""
SHAMBHU - The 3rd Mahajana (Destruction/GC)
===========================================
OpCode: garbage_collect (Bit 7)
Opulence: Vairagya (Renunciation)

"I am Time, the great destroyer of the world."
- Bhagavad Gita 11.32

Shambhu OWNS all destruction protocols:
- Garbage Collection
- Resource Cleanup
- Memory Deallocation
- Graceful Shutdown
- The Tandava (Destruction Dance)

Without Shambhu, the system accumulates ZOMBIES.
A system that creates but cannot destroy = Hiranyakashipu.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ShambhuProtocol(Protocol):
    """
    The Destroyer Protocol.
    Any system that manages lifecycle/cleanup must implement this.
    """

    def destroy(self) -> None:
        """
        Execute graceful destruction.
        Must release all resources.
        """
        ...

    def is_destroyed(self) -> bool:
        """Check if resource has been destroyed."""
        ...

    def can_destroy(self) -> bool:
        """
        Check if destruction is allowed.
        Some resources may be protected.
        """
        ...


class NullShambhu:
    """
    The Eternal One.
    Cannot be destroyed (for testing protected resources).
    """

    def destroy(self) -> None:
        pass  # No-op

    def is_destroyed(self) -> bool:
        return False

    def can_destroy(self) -> bool:
        return False


__all__ = ["ShambhuProtocol", "NullShambhu"]
