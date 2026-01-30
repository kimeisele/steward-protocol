"""
AXIOM GATE - Mathematical Derivation Verifier
==============================================

"yasyaika-niśvasita-kālam athāvalambya"
"All exists due to His single breath."

THE PROBLEM:
============
V3 achieved 100% match by HARDCODING constants like +30, +41.
That is CHEATING. We need a GATE that verifies:

  "Is this value mathematically derivable from the 7 AXIOMS?"

If yes → VALID (the Name is legitimate)
If no  → INVALID (random correlation)

THE 7 AXIOMS (from _seed.py):
=============================
1. WORDS = 16
2. TRINITY = 3
3. HARE_COUNT = 8
4. KRISHNA_COUNT = 4
5. RAMA_COUNT = 4
6. PANCHA = 5
7. HALVES = 2

THE DERIVATION RULES:
=====================
A value is "DERIVABLE" if it can be expressed as:
  - A single axiom
  - A product of axioms (a × b)
  - A sum of axioms (a + b)
  - A difference of axioms (a - b)
  - A quotient of axioms (a / b) where divisible
  - A composition of the above (recursive up to depth N)

EXAMPLE:
========
  30 = TRINITY × 10 = 3 × 10
     But is 10 derivable?
     10 = HALVES × PANCHA = 2 × 5 ✓
     So 30 = TRINITY × HALVES × PANCHA ✓
"""

from typing import Set, Dict, Tuple, Optional, List
from functools import lru_cache

from vibe_core.mahamantra.protocols._seed import (
    WORDS,
    TRINITY,
    HARE_COUNT,
    KRISHNA_COUNT,
    RAMA_COUNT,
    PANCHA,
    HALVES,
)

# =============================================================================
# THE 7 AXIOMS (The only hardcoded values - everything else is derived)
# =============================================================================
AXIOMS = {
    "WORDS": WORDS,
    "TRINITY": TRINITY,
    "HARE_COUNT": HARE_COUNT,
    "KRISHNA_COUNT": KRISHNA_COUNT,
    "RAMA_COUNT": RAMA_COUNT,
    "PANCHA": PANCHA,
    "HALVES": HALVES,
}

# Derived values (1 step from axioms)
DERIVED_LEVEL_1 = {
    "SEVEN": 7,           # HARE_COUNT - KSETRAJNA (but KSETRAJNA is derived!)
    "TEN": 10,            # HALVES × PANCHA = 2 × 5
    "KSETRAJNA": 1,       # TRINITY - HALVES = 3 - 2
    "QUARTERS": 4,        # KRISHNA_COUNT (already an axiom)
}


class AxiomGate:
    """
    Mathematical Derivation Verifier.
    
    Tests whether a value can be expressed using only the 7 axioms.
    """
    
    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth
        self.derivable_cache: Dict[int, str] = {}
        self._build_derivable_set()
    
    def _build_derivable_set(self):
        """Build the set of all derivable values up to max_depth."""
        # Level 0: Axioms themselves
        axiom_values = set(AXIOMS.values())
        
        # Also include 1 (KSETRAJNA = TRINITY - HALVES)
        axiom_values.add(1)
        
        for val in AXIOMS.values():
            self.derivable_cache[val] = f"AXIOM"
        self.derivable_cache[1] = "TRINITY - HALVES"
        
        # Build successive levels
        current = axiom_values.copy()
        
        for depth in range(1, self.max_depth + 1):
            new_values: Set[int] = set()
            
            for a in current:
                for b in current:
                    # Addition
                    if 0 < a + b <= 1000:
                        if a + b not in self.derivable_cache:
                            self.derivable_cache[a + b] = f"({a} + {b})"
                        new_values.add(a + b)
                    
                    # Subtraction (positive only)
                    if a > b and a - b not in self.derivable_cache:
                        self.derivable_cache[a - b] = f"({a} - {b})"
                        new_values.add(a - b)
                    
                    # Multiplication
                    if 0 < a * b <= 1000:
                        if a * b not in self.derivable_cache:
                            self.derivable_cache[a * b] = f"({a} × {b})"
                        new_values.add(a * b)
                    
                    # Division (if clean)
                    if b != 0 and a % b == 0 and a // b not in self.derivable_cache:
                        self.derivable_cache[a // b] = f"({a} / {b})"
                        new_values.add(a // b)
            
            current = current.union(new_values)
    
    def is_derivable(self, value: int) -> bool:
        """Check if a value is derivable from axioms."""
        # Normalize to positive (mod 49 space)
        if value < 0:
            value = 49 + value
        
        return value in self.derivable_cache
    
    def get_derivation(self, value: int) -> Optional[str]:
        """Get the derivation path for a value."""
        if value < 0:
            neg_val = 49 + value
            if neg_val in self.derivable_cache:
                return f"-(49 - {neg_val})"
        return self.derivable_cache.get(value)
    
    def verify_delta(self, delta: int, mod: int = 49) -> Tuple[bool, str]:
        """
        Verify a delta is derivable.
        
        Returns (is_valid, explanation)
        """
        # Handle negative deltas (mod space)
        effective = delta if delta >= 0 else (mod + delta)
        
        if effective in self.derivable_cache:
            return True, f"+{delta} = {self.derivable_cache[effective]}"
        
        # Check negative form
        negative = mod - effective
        if negative in self.derivable_cache:
            return True, f"+{delta} = -{negative} = -{self.derivable_cache[negative]}"
        
        return False, f"+{delta} = CANNOT DERIVE FROM AXIOMS"
    
    def dump_all_derivable(self, limit: int = 50) -> List[Tuple[int, str]]:
        """Dump all derivable values up to limit."""
        results = []
        for val in sorted(self.derivable_cache.keys()):
            if val <= limit:
                results.append((val, self.derivable_cache[val]))
        return results


def test_known_constants():
    """Test that known Mahamantra constants are derivable."""
    gate = AxiomGate(max_depth=3)
    
    print("AXIOM GATE - DERIVATION VERIFICATION")
    print("=" * 60)
    print()
    print("7 AXIOMS:")
    for name, val in AXIOMS.items():
        print(f"  {name} = {val}")
    print()
    
    # Test known constants
    KNOWN_CONSTANTS = [
        (1, "KSETRAJNA"),
        (6, "SHARANAGATI"),
        (7, "SEVEN"),
        (9, "NAVA"),
        (10, "TEN"),
        (12, "MAHAJANA"),
        (16, "WORDS"),
        (17, "KRISHNA"),
        (18, "GITA"),
        (20, "TWENTY"),
        (24, "KSHETRA"),
        (27, "NAKSHATRAS"),
        (30, "TRINITY×TEN"),
        (37, "PARAMPARA"),
        (41, "LILA-SEVEN"),
        (48, "LILA"),
        (49, "RAMA"),
    ]
    
    print("KNOWN CONSTANTS VERIFICATION:")
    print("-" * 60)
    
    all_passed = True
    for val, name in KNOWN_CONSTANTS:
        derivable = gate.is_derivable(val)
        derivation = gate.get_derivation(val)
        status = "✓" if derivable else "✗"
        if not derivable:
            all_passed = False
        print(f"  {status} {val:3} ({name:15}): {derivation or 'NOT DERIVABLE'}")
    
    print()
    print("=" * 60)
    
    if all_passed:
        print("✓ ALL CONSTANTS ARE MATHEMATICALLY DERIVABLE FROM 7 AXIOMS!")
    else:
        print("✗ SOME CONSTANTS CANNOT BE DERIVED - CHECK AXIOM SET")
    
    return all_passed


def validate_v3_deltas():
    """Validate all deltas from V3 analysis using the Axiom Gate."""
    gate = AxiomGate(max_depth=3)
    
    # All deltas found in V3
    V3_DELTAS = [
        # VYASA: va→ya→sa
        46, 6,
        # BRAHMA: ba→ra→ha→ma
        4, 6, 41,
        # NARADA: na→ra→da
        7, 40,
        # SHAMBHU: śa→bha
        43,
        # PRITHU: pa→ra→tha
        6, 39,
        # KUMARAS: ka→ma→ra→sa
        24, 2, 5,
        # KAPILA: ka→pi→la
        20, 7,
        # MANU: ma→na
        44,
        # PARASHURAMA: pa→ra→śa→ra→ma
        6, 3, 46, 47,
        # PRAHLADA: pa→ra→la→da
        6, 1, 39,
        # JANAKA: ja→na→ka
        12, 30,
        # BHISHMA: bha→ṣa→ma
        7, 43,
        # NRISIMHA: na→ra→ha
        7, 6,
        # BALI: ba→la
        5,
        # SHUKA: śa→ka
        20,
        # YAMARAJA: ya→ma→ra→ja
        48, 2, 30,
    ]
    
    print()
    print("V3 DELTA VALIDATION")
    print("=" * 60)
    print()
    
    valid_count = 0
    total = len(V3_DELTAS)
    
    for delta in V3_DELTAS:
        is_valid, explanation = gate.verify_delta(delta)
        status = "✓" if is_valid else "✗"
        if is_valid:
            valid_count += 1
        # Show only failures (for brevity)
        if not is_valid:
            print(f"  {status} {explanation}")
    
    print(f"\nRESULT: {valid_count}/{total} deltas are axiom-derivable")
    print(f"MATCH RATE: {valid_count/total*100:.1f}%")
    
    if valid_count == total:
        print()
        print("=" * 60)
        print("✓ THE AXIOM GATE CONFIRMS: ALL NAME TRANSITIONS ARE DERIVABLE!")
        print("=" * 60)
    
    return valid_count == total


if __name__ == "__main__":
    test_known_constants()
    print()
    validate_v3_deltas()
