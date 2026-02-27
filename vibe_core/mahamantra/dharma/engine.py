"""
THE DHARMA ENGINE (Unified Facade)
==================================
The Single Source of Truth for Mahamantra Intelligence.

Integrates:
- Linguist (Form)
- Layers (Attractors)
- Matrix (Genesis)
- Hologram (Fractal)
- Shabda (Vibration)

Usage:
    from vibe_core.mahamantra.dharma.engine import DharmaEngine
    engine = DharmaEngine()
    form = engine.get_form("KRISHNA")
    layer = engine.get_layer(108)
    alignment = engine.word_alignment("krishna")
"""

from typing import List

from vibe_core.mahamantra.dharma.components.hologram import HologramEngine
from vibe_core.mahamantra.dharma.components.layers import LayerEngine
from vibe_core.mahamantra.dharma.components.linguist import Linguist
from vibe_core.mahamantra.dharma.components.matrix import MahaMatrix
from vibe_core.mahamantra.dharma.components.shabda import ShabdaEngine, VibrationSignature
from vibe_core.mahamantra.protocols.dharma_protocol import DharmaProtocol, FractalNodeData, SwarupaData


class DharmaEngine:
    """
    The Unified Facade for Mahamantra Research & Execution.
    Implements: DharmaProtocol
    Singleton-style usage recommended.
    """

    def __init__(self):
        self._linguist = Linguist()
        self._layers = LayerEngine()
        self._matrix = MahaMatrix()
        self._hologram = HologramEngine()
        self._shabda = ShabdaEngine()

    # --- LINGUISTICS (V9) ---
    def get_form(self, name: str) -> SwarupaData:
        """Get the Infinite Object (Swarupa) for a name."""
        return self._linguist.reveal(name)

    # --- LAYERS (V10) ---
    def get_layer(self, attractor: int) -> List[int]:
        """Project the Mantra into a dimension (e.g. 16, 49, 108)."""
        return self._layers.unfold(attractor)

    def get_layer_signature(self, attractor: int) -> str:
        """Get ASCII sparkline of a layer."""
        return self._layers.signature(attractor)

    # --- MATRIX (Genesis) ---
    def analyze_field(self) -> List[int]:
        """Get Field Strengths of the 4 Quarters."""
        return self._matrix.analyze_quarters()

    def get_spark(self, q1: int, q2: int) -> int:
        """Get Interaction Spark between two quarters (0-3)."""
        return self._matrix.interact(q1, q2)

    # --- HOLOGRAM (Fractal) ---
    def expand_universe(self, depth: int = 1) -> FractalNodeData:
        """Ignite the Holographic Tree."""
        return self._hologram.ignite(depth)

    # --- SHABDA (Vibration) ---
    def get_vibration(self, phoneme: str) -> VibrationSignature | None:
        """Get VibrationSignature for a Sanskrit phoneme."""
        return self._shabda.get_signature(phoneme)

    def freq_to_id(self, hz: float) -> int:
        """Convert Hz to Mahamantra Vibration ID."""
        return self._shabda.freq_to_id(hz)

    def id_to_freq(self, vib_id: int) -> float:
        """Convert Vibration ID back to Hz."""
        return self._shabda.id_to_freq(vib_id)

    def word_alignment(self, word: str) -> float:
        """Calculate Mahamantra alignment of a word (0.0 - 1.0)."""
        return self._shabda.word_alignment(word)


# Singleton Instance
dharma: DharmaProtocol = DharmaEngine()
