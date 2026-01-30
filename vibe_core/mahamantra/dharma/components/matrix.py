"""
THE MATRIX COMPONENT (Genesis Logic)
====================================
"Chatur-vyuha" - The 4-Split Reality.

Responsibility:
- 4x4 Grid Analysis
- Quarter Interactions (Sparks)
- Field Strength Calculation
"""

from typing import List, Tuple, Final
from vibe_core.mahamantra.dharma.components.linguist import Linguist

class MahaMatrix:
    """The 4x4 Reality Matrix."""
    
    def __init__(self):
        self.linguist = Linguist()
        self.quarters = [
            ["HARE", "KRISHNA", "HARE", "KRISHNA"],      # Q1: Bhu
            ["KRISHNA", "KRISHNA", "HARE", "HARE"],      # Q2: Bhuvah
            ["HARE", "RAMA", "HARE", "RAMA"],            # Q3: Svah
            ["RAMA", "RAMA", "HARE", "HARE"]             # Q4: Mahar
        ]
        
    def _get_val(self, word: str) -> int:
        # Using Akshara Index Sum mod 49 (RAMA Grid)
        swarupa = self.linguist.reveal(word)
        total = sum(a.index for a in swarupa.aksharas)
        return total % 49

    def analyze_quarters(self) -> List[int]:
        """Returns Field Strength of each Quarter."""
        return [
            sum(self._get_val(w) for w in row) % 49
            for row in self.quarters
        ]

    def interact(self, q_idx_1: int, q_idx_2: int) -> int:
        """Interact two quarters."""
        vals = self.analyze_quarters()
        return (vals[q_idx_1] + vals[q_idx_2]) % 49
