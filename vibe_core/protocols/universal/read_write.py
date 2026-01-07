from typing import Any, Optional, Protocol, runtime_checkable


@runtime_checkable
class ReadWriteProtocol(Protocol):
    """
    Atomic protocol for read/write operations.
    Focuses on simple key-value or addressable access.
    """

    def read(self, key: str) -> Any:
        """Read value by key."""
        ...

    def write(self, key: str, value: Any) -> None:
        """Write value by key."""
        ...

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        ...
