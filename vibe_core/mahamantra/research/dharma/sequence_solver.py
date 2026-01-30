
"""
SEQUENCE SOLVER - The Mahamantra as a State Machine (REAL FILE)
===================================================

Hypothesis: 
The names are not derived from Position via a formula f(pos).
They are derived from the STATE of the system as it executes the Mantra sequentially.

Transition: Target[i] -> Target[i+1] must be explained by Op[i+1] (H/K/R).
"""

from typing import List

# SSOT IMPORTS - NO HARDCODING!
from vibe_core.mahamantra.protocols._seed import (
    MAHAMANTRA_WORD_PATTERN,
    SEVEN,
    TEN,
    POSITION_SUM_KRISHNA,
    GITA_CHAPTERS,
    KSHETRA,
    PRASADAM,
    NAKSHATRAS,
    PARAMPARA,
)

# Target indices in RAMA grid (49)
TARGETS = [
    44, # 1: Vyasa (va)
    38, # 2: Brahma (ba)
    35, # 3: Narada (na)
    45, # 4: Shambhu (śa)
    36, # 5: Prithu (pa)
    16, # 6: Kumaras (ka)
    16, # 7: Kapila (ka)
    40, # 8: Manu (ma)
    36, # 9: Parashurama (pa)
    36, # 10: Prahlada (pa)
    23, # 11: Janaka (ja)
    39, # 12: Bhishma (bha)
    35, # 13: Nrisimha (na)
    38, # 14: Bali (ba)
    45, # 15: Shuka (śa)
    41  # 16: Yamaraja (ya)
]

# The Mantra Pattern - DERIVED FROM SSOT!
PATTERN = "".join(MAHAMANTRA_WORD_PATTERN)

# Candidate Constants - FROM _seed.py SSOT!
CONSTANTS = {
    "SEVEN": SEVEN,  # 7
    "TEN": TEN,  # 10
    "KRISHNA": POSITION_SUM_KRISHNA,  # 17
    "GITA": GITA_CHAPTERS,  # 18
    "KSHETRA": KSHETRA,  # 24
    "PRASADAM": PRASADAM,  # 25
    "NAKSHATRA": NAKSHATRAS,  # 27
    "TEN_3": TEN * 3,  # 30 = 10 × 3
    "PARAMPARA": PARAMPARA,  # 37
    "LILA": SEVEN * SEVEN - 1,  # 48 = 7² - 1
}

def analyze_transitions():
    print("ANALYZING SEQUENTIAL TRANSITIONS (Mod 49)")
    print("=" * 60)
    
    # We look at transition from Target[i] to Target[i+1]
    # This corresponds to Step i+2 in the sequence (Pos 2, 3...)
    
    for i in range(len(TARGETS) - 1):
        prev = TARGETS[i]
        curr = TARGETS[i+1]
        step_pos = i + 2
        op_char = PATTERN[step_pos - 1] # 0-indexed pattern
        
        diff = (curr - prev) % 49
        
        matches = []
        
        # Additive Check (prev + C = curr)
        for name, val in CONSTANTS.items():
            if diff == val:
                matches.append(f"+{name}")
            if diff == (49 - val):
                matches.append(f"-{name}")
                
        # Multiplicative Check (prev * C = curr)
        # Only feasible if prev has inverse or we brute force
        for name, val in CONSTANTS.items():
            if (prev * val) % 49 == curr:
                matches.append(f"*{name}")
                
        # Special Ops
        if (prev * prev) % 49 == curr:
            matches.append("SQUARE")
            
        match_str = ", ".join(matches) if matches else "-"
        print(f"[{op_char}] {prev:2} -> {curr:2} (Pos {step_pos:2}): Diff {diff:2} | {match_str}")

if __name__ == "__main__":
    analyze_transitions()
