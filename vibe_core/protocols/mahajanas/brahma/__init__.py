"""
BRAHMA - The 1st Mahajana (Creation)
====================================
OpCodes: sys_wake (Bit 1), alloc_mem (Bit 2)
Opulence: Aishvarya (Sovereignty/Wealth)

"In the beginning, Brahma created..."

Brahma OWNS all creation protocols:
- Bootstrap / Init
- Memory Allocation
- Resource Creation
- System Wake

Brahma does NOT destroy. That is Shambhu's domain.
"""

from typing import Protocol, runtime_checkable, TypeVar, Generic

T = TypeVar("T")


@runtime_checkable
class BrahmaProtocol(Protocol):
    """
    The Creator Protocol.
    Any system that creates resources must implement this.
    """

    def create(self) -> bool:
        """
        Create/Initialize the resource.
        Returns True if creation succeeded.
        """
        ...

    def is_created(self) -> bool:
        """Check if resource has been created."""
        ...

    def get_creation_timestamp(self) -> float:
        """Returns Unix timestamp of creation."""
        ...


class NullBrahma:
    """
    The Uncreated Creator.
    Used when creation is not the focus of the test.
    """

    def create(self) -> bool:
        return True

    def is_created(self) -> bool:
        return False

    def get_creation_timestamp(self) -> float:
        return 0.0


__all__ = ["BrahmaProtocol", "NullBrahma"]
