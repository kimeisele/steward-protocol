"""
SYNAPSE PROTOCOL - The Form of Connection.

"The Autobahn of the Mind."

Migrated from: vibe_core/plugins/opus_assistant/core/synapses.json
To: A Universal Protocol.

A Synapse is NOT just data. It is a weighted, directed edge in the Graph of Consciousness.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0x0910aa11"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import Dict, List, Optional, Protocol, runtime_checkable


@dataclass
class SynapseState:
    """The JSON Form of a Synapse (State)."""

    trigger: str
    action: str
    weight: float
    confidence: float
    metadata: Dict[str, str]


@runtime_checkable
class ISynapse(Protocol):
    """
    The Synapse Interface (Behavior).
    """

    @property
    def trigger(self) -> str:
        """The stimulus that fires this synapse."""
        ...

    @property
    def weight(self) -> float:
        """The karmic weight (strength) of connection (0.0 - 1.0)."""
        ...

    def fire(self, context_data: Dict[str, str]) -> float:
        """
        Activates the synapse.
        Returns the signal strength (weight * relevance).
        """
        ...


@runtime_checkable
class ISynapseMemory(Protocol):
    """
    The Memory Store (The State File Manager).
    """

    def consult(self, trigger: str) -> List[ISynapse]:
        """
        Consults memory for synapses matching the trigger.
        """
        ...

    def reinforce(self, trigger: str, action: str, delta: float) -> float:
        """
        Strengthens or weakens a synapse based on outcome.
        Returns new weight.
        """
        ...
