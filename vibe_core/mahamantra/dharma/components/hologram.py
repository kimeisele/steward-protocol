"""
THE HOLOGRAM COMPONENT (Fractal Logic)
======================================
"Purnam" - The Holographic Whole.

Responsibility:
- Recursive Expansion
- Tree Structure (Node -> Mantra)
"""

from vibe_core.mahamantra.dharma.components.linguist import Linguist
from vibe_core.mahamantra.protocols.dharma_protocol import FractalNodeData, SwarupaData

SEED_MANTRA = [
    "HARE",
    "KRISHNA",
    "HARE",
    "KRISHNA",
    "KRISHNA",
    "KRISHNA",
    "HARE",
    "HARE",
    "HARE",
    "RAMA",
    "HARE",
    "RAMA",
    "RAMA",
    "RAMA",
    "HARE",
    "HARE",
]


class HologramEngine:
    """Recursively expands every atom into a universe (Protocol Compliant)."""

    def __init__(self):
        self.linguist = Linguist()

    def ignite(self, max_depth: int = 1) -> FractalNodeData:
        root = FractalNodeData(value="ADI-SEED", level=0, children=[])
        self._expand_node(root, max_depth)
        return root

    def _expand_node(self, node: FractalNodeData, remaining_depth: int):
        if remaining_depth <= 0:
            return

        # Every node spawns the Mantra
        for word in SEED_MANTRA:
            w_node = FractalNodeData(value=f"WORD:{word}", level=node.level + 1, children=[])
            node.children.append(w_node)

            # Expand Word into Atoms
            swarupa: SwarupaData = self.linguist.reveal(word)
            for atom in swarupa.aksharas:
                a_node = FractalNodeData(value=f"ATOM:{atom.deva}", level=node.level + 2, children=[])
                w_node.children.append(a_node)

                # RECURSION
                self._expand_node(a_node, remaining_depth - 1)
