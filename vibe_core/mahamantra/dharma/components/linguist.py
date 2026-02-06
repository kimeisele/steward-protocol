"""
THE LINGUIST COMPONENT (V9 Logic)
=================================
"Swarupa" - The Definition of Form.

Responsibility:
- Akshara Objects (The Atom)
- Sandhi Engine (Grammar)
- Definition Lookup (V7-based Axiom Trace)
"""

from dataclasses import dataclass
from typing import Dict, Final, List, Optional, Tuple

from vibe_core.mahamantra.protocols._seed import (
    HALVES, HARE_COUNT, KRISHNA_COUNT, KSHETRA, KSETRAJNA,
    LILA, RAMA_COUNT, SHARANAGATI, TEN, TRINITY, WORDS,
)
from vibe_core.mahamantra.protocols.dharma_protocol import AksharaData, SwarupaData, LinguistProtocol

# --- THE GRAMMAR ---
class SandhiEngine:
    """Devanagari Sandhi Logic."""
    
    MATRA_MAP: Final[Dict[int, str]] = {
        0: "", 1: "ा", 2: "ि", 3: "ी", 4: "ु", 5: "ू", 6: "ृ",
        10: "े", 11: "ै", 12: "ो", 13: "ौ", 14: "ं", 15: "ः"
    }

    CONSONANTS: Final[Dict[int, Tuple[str, str]]] = {
        16: ("k", "क"), 17: ("kh", "ख"), 18: ("g", "ग"),
        21: ("c", "च"), 23: ("j", "ज"),
        30: ("ṇ", "ण"), 31: ("t", "त"), 33: ("d", "द"), 35: ("n", "न"),
        36: ("p", "प"), 38: ("b", "ब"), 39: ("bh", "भ"), 40: ("m", "म"),
        41: ("y", "य"), 42: ("r", "र"), 43: ("l", "ल"), 44: ("v", "व"),
        46: ("ṣ", "ष"), 47: ("s", "स"), 48: ("h", "ह")
    }

    @classmethod
    def compose(cls, ax: List[AksharaData]) -> Tuple[str, str]:
        res_iast, res_deva = "", ""
        i = 0
        while i < len(ax):
            curr = ax[i]
            next_ax = ax[i+1] if i + 1 < len(ax) else None
            
            # Simple check for vowel/consonant based on index range
            is_consonant = 16 <= curr.index <= 48
            
            if is_consonant:
                # Use default if not in map (safe fallback)
                root_i, root_d = cls.CONSONANTS.get(curr.index, (curr.iast, curr.deva))
                
                next_is_vowel = next_ax and (0 <= next_ax.index <= 15)
                
                if next_is_vowel:
                    # Apply Vowel as Matra
                    matra = cls.MATRA_MAP.get(next_ax.index, "")
                    res_deva += (root_d + matra)
                    res_iast += (root_i + next_ax.iast)
                    i += 2
                    continue
                else:
                    res_deva += curr.deva; res_iast += curr.iast
                    i += 1
            else:
                res_deva += curr.deva; res_iast += curr.iast
                i += 1
        return res_iast, res_deva

# --- THE DEFINITIONS (AXIOMATICALLY DERIVED) ---
def _derive_definitions() -> Dict[str, List[int]]:
    return {
        "HARE": [LILA, LILA - SHARANAGATI, TEN],
        "KRISHNA": [WORDS, SHARANAGATI, LILA - HALVES, KSHETRA + SHARANAGATI, 0],
        "RAMA": [LILA - SHARANAGATI, KSETRAJNA, WORDS + KSHETRA, 0]
    }

DEFINITIONS: Final[Dict[str, List[int]]] = _derive_definitions()

class Linguist:
    """The Provider of Swarupa (Protocol Compliant)."""
    
    def reveal(self, name: str) -> SwarupaData:
        indices = DEFINITIONS.get(name, [])
        chain = []
        for idx in indices:
            d, i, t = self._lookup(idx)
            # Create Protocol-Compliant AksharaData
            chain.append(AksharaData(
                index=idx, iast=i, deva=d, vtype=t, derivation="AXIOM"
            ))
            
        # Compose final forms
        final_iast, final_deva = SandhiEngine.compose(chain)
        
        return SwarupaData(
            key=name,
            aksharas=chain,
            iast=final_iast,
            deva=final_deva
        )

    def _lookup(self, idx: int) -> Tuple[str, str, str]:
        # Minimal map for the Mantra words
        LUT = {
            48: ("ह", "h", "Usman"), 42: ("र", "r", "Antastha"), 10: ("ए", "e", "Svara"),
            16: ("क", "k", "Sparsha"), 6: ("ृ", "ṛ", "Svara"), 46: ("ष", "ṣ", "Usman"),
            30: ("ण", "ṇ", "Sparsha"), 0: ("अ", "a", "Svara"),
            1: ("आ", "ā", "Svara"), 40: ("म", "m", "Sparsha")
        }
        return LUT.get(idx, ("?", "?", "?"))
