"""
THE LAYERS COMPONENT (V10 Logic)
================================
"Ananta" - The Infinite Projections.

Responsibility:
- Attractor Projection (Modulo Arithmetic)
- Time Layer (16)
- Space Layer (49)
- Relation Layer (108)
- Quantum Layer (137)
"""

from typing import List, Dict, Final

from typing import List, Dict, Final
from vibe_core.mahamantra.dharma.components.linguist import DEFINITIONS

MANTRA_SEQUENCE: Final[List[str]] = [
    "HARE", "KRISHNA", "HARE", "KRISHNA",
    "KRISHNA", "KRISHNA", "HARE", "HARE",
    "HARE", "RAMA", "HARE", "RAMA",
    "RAMA", "RAMA", "HARE", "HARE"
]

class LayerEngine:
    """Projects the Mantra into specific dimensional layers."""
    
    def _get_seed(self, word: str) -> int:
        """Dynamically calculate seed from derived Akshara indices."""
        indices = DEFINITIONS.get(word, [])
        return sum(indices)

    def unfold(self, attractor: int) -> List[int]:
        """
        Unfold the Mantra using the Attractor Modulo.
        Formula: Value[i] = (Value[i-1] + Seed) % Attractor
        """
        layer_data = []
        current_val = 0
        
        for word in MANTRA_SEQUENCE:
            seed = self._get_seed(word)
            # Integration step (Cumulative)
            current_val = (current_val + seed) % attractor
            layer_data.append(current_val)
            
        return layer_data

    def signature(self, attractor: int) -> str:
        """ascii sparkline of the layer."""
        data = self.unfold(attractor)
        chars = "._-:|#"
        pattern = ""
        for v in data:
            if attractor == 0: idx = 0 
            else: idx = int((v / attractor) * (len(chars)-1))
            pattern += chars[idx]
        return pattern
