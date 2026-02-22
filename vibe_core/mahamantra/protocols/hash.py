from typing import Protocol, runtime_checkable, Tuple, Optional
from dataclasses import dataclass


@runtime_checkable
class MahaHashProtocol(Protocol):
    """
    Protocol for MahaHash: Deterministic Intent-to-Integer Encoding.

    Encodes strings to integers using position-weighted character encoding.
    """

    def encode(self, text: str) -> int:
        """Encode string to raw integer."""
        ...

    def hash(self, text: str, mod_space: Optional[int] = None) -> int:
        """Hash string to integer in [0, mod_space)."""
        ...

    def hash_to_result(self, text: str, mod_space: Optional[int] = None) -> "HashResult":
        """Hash with full result object."""
        ...

    def analyze(self, text: str) -> "MultiLensReading":
        """Analyze input through all sacred lenses."""
        ...

    def validate_parampara(self, text: str) -> bool:
        """Check if input passes disciplic chain validation."""
        ...


@dataclass(frozen=True)
class HashResult:
    """Simple hash result."""

    input: str
    value: int
    mod_space: int


@dataclass(frozen=True)
class LensReading:
    """Single lens reading."""

    name: str
    mod_space: int
    value: int


@dataclass(frozen=True)
class MultiLensReading:
    """Full multi-lens analysis."""

    input: str
    seed: int
    primary_hash: int
    lenses: Tuple[LensReading, ...]
    parampara_validated: bool
    holographic_factors: Tuple[int, ...]
