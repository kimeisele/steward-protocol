
"""
VISHVARUPA SOLVER - HARDCORE REVERSE ENGINEERING of the MAHAMANTRA
==================================================================
"Finding the hidden coefficients of reality."

Objective: 
    Find f(p) such that f(position) = Ram_Grid_Index(First_Letter)
    Where f(p) is composed ONLY of Mahamantra Constants (7, 10, 16, 17, 37, etc.)
"""

import itertools

# THE CONSTANTS (The "Instruction Set")
CONSTANTS = {
    "SEVEN": 7,       # HARE multiplier
    "TEN": 10,        # KRISHNA adder
    "WORDS": 16,      # Total words
    "KRISHNA": 17,    # Krishna position sum
    "GITA": 18,       # Chapters
    "KSHETRA": 24,    # Field
    "PRASADAM": 25,   # Grid offset
    "NAKSHATRAS": 27, # Lunar
    "TEN_3": 30,      # Trinity * Ten
    "PARAMPARA": 37,  # Disciplic line
    "LILA": 48,       # Pastime
    "RAMA": 49        # The Grid Size (Modulus)
}

# THE TARGETS (The "Observed Reality")
# Position -> RAMA Grid Index of first letter
# Verified against standard Sanskrit Varnamala:
# 0-15 Vowels, 16-40 Consonants (ka-ma), 41-48 Antastha (ya-ha)
TARGETS = [
    (1, 44, "Vyasa"),       # va (44)
    (2, 38, "Brahma"),      # ba (38)
    (3, 35, "Narada"),      # na (35)
    (4, 45, "Shambhu"),     # śa (45)
    (5, 36, "Prithu"),      # pa (36)
    (6, 16, "Kumaras"),     # ka (16)
    (7, 16, "Kapila"),      # ka (16)
    (8, 40, "Manu"),        # ma (40)
    (9, 36, "Parashurama"), # pa (36)
    (10, 36, "Prahlada"),   # pa (36)
    (11, 23, "Janaka"),     # ja (23)
    (12, 39, "Bhishma"),    # bha (39)
    (13, 35, "Nrisimha"),   # na (35) - Nri starts with Na
    (14, 38, "Bali"),       # ba (38)
    (15, 45, "Shuka"),      # śa (45)
    (16, 41, "Yamaraja"),   # ya (41)
]

def solve():
    print("SEARCHING FOR THE CODE...")
    print("Constraint: Formula must use strictly Mahamantra constants.")
    print("-" * 60)
    
    # Simple Linear Search: (Op1 * pos + Op2) % 49
    valid_constants = list(CONSTANTS.items())
    
    found_formulas = {}

    for pos, target, name in TARGETS:
        hits = []
        
        # MODEL 1: LINEAR (A * pos + B) % 49
        for (n1, c1), (n2, c2) in itertools.product(valid_constants, valid_constants):
            # Check (C1 * pos + C2)
            if (c1 * pos + c2) % 49 == target:
                hits.append(f"({n1} * p + {n2})")
            # Check (C1 * pos - C2)
            if (c1 * pos - c2) % 49 == target:
                hits.append(f"({n1} * p - {n2})")
                
        # MODEL 2: SUBTRACTIVE (A - pos) % 49
        for n1, c1 in valid_constants:
            if (c1 - pos) % 49 == target:
                hits.append(f"({n1} - p)")
                
        # MODEL 3: POWER (pos^2 + C) % 49 -- The RAMA operator
        for n1, c1 in valid_constants:
            if (pos * pos + c1) % 49 == target:
                hits.append(f"(p^2 + {n1})")

        found_formulas[name] = hits

    # REPORTING
    for pos, target, name in TARGETS:
        formulas = found_formulas[name]
        
        # Filter for "Cleanest" formulas (using major constants)
        best = [f for f in formulas if "PARAMPARA" in f or "KRISHNA" in f or "SEVEN" in f]
        
        if not best and formulas:
            best = formulas[:1] # Take first if no major ones
            
        print(f"{pos:2} {name:12} [{target}]: {', '.join(best) if best else 'NO EXACT MATCH'}")

if __name__ == "__main__":
    solve()
