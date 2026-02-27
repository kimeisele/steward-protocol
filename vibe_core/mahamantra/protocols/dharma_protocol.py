"""
THE DHARMA PROTOCOL
===================
The Watertight Definitions of the Mahamantra Intelligence.

"vidya-vinaya-sampanne"
"By education and gentleness (one sees with equal vision)." - BG 5.18

These Protocols define the Contracts for the Dharma Engine components.
No concrete classes in signatures. Only Protocols.
"""

from dataclasses import dataclass
from typing import List, Protocol


# --- SHARED DATA STRUCTURES ---
@dataclass(frozen=True)
class AksharaData:
    """Protocol-compliant data transfer object for Atoms."""

    index: int
    iast: str
    deva: str
    vtype: str
    derivation: str


@dataclass(frozen=True)
class SwarupaData:
    """Protocol-compliant data transfer object for Forms."""

    key: str
    aksharas: List[AksharaData]
    deva: str
    iast: str


@dataclass
class FractalNodeData:
    """Protocol-compliant DTO for Holographic Nodes."""

    value: str
    level: int
    children: List["FractalNodeData"]


# --- THE PROTOCOLS ---


class LinguistProtocol(Protocol):
    """
    Contract for the Entity that reveals the Form (Swarupa).
    Must provide Akshara-level details and Sandhi rendering.
    """

    def reveal(self, name: str) -> SwarupaData:
        """Reveal the Form of a Name."""
        ...


class LayerProtocol(Protocol):
    """
    Contract for the Entity that projects the Mantra into Dimensions.
    Must support modulation by Attractors.
    """

    def unfold(self, attractor: int) -> List[int]:
        """Project the Mantra Sequence into a modulo layer."""
        ...

    def signature(self, attractor: int) -> str:
        """Return the ASCII Sparkline signature of the layer."""
        ...


class MatrixProtocol(Protocol):
    """
    Contract for the Entity that manages the 4x4 Grid Interaction.
    Must provide Field Strength analysis and Spark generation.
    """

    def analyze_quarters(self) -> List[int]:
        """Return the Field Strength of the 4 Quarters."""
        ...

    def interact(self, q_idx_1: int, q_idx_2: int) -> int:
        """Generate a Spark from two Quarters."""
        ...


class HologramProtocol(Protocol):
    """
    Contract for the Entity that manages Infinite Recursion.
    """

    def ignite(self, max_depth: int) -> FractalNodeData:
        """Ignite the Holographic Tree up to max_depth."""
        ...


class DharmaProtocol(Protocol):
    """
    The Unified Facade Protocol.
    This is what the System (Steward) interacts with.
    """

    def get_form(self, name: str) -> SwarupaData: ...
    def get_layer(self, attractor: int) -> List[int]: ...
    def get_layer_signature(self, attractor: int) -> str: ...
    def analyze_field(self) -> List[int]: ...
    def get_spark(self, q1: int, q2: int) -> int: ...
    def expand_universe(self, depth: int) -> FractalNodeData: ...
