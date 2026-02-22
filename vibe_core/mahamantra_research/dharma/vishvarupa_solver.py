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
    "SEVEN": 7,  # HARE multiplier
    "TEN": 10,  # KRISHNA adder
    "WORDS": 16,  # Total words
    "KRISHNA": 17,  # Krishna position sum
    "GITA": 18,  # Chapters
    "KSHETRA": 24,  # Field
    "PRASADAM": 25,  # Grid offset
    "NAKSHATRAS": 27,  # Lunar
    "TEN_3": 30,  # Trinity * Ten
    "PARAMPARA": 37,  # Disciplic line
    "LILA": 48,  # Pastime
    "RAMA": 49,  # The Grid Size (Modulus)
}

# IMPL-PHONETIC-ROUTER: Use the Standard Adapter
from vibe_core.mahamantra.adapters.rama_router import get_phonetic_router

# Get the router service
router = get_phonetic_router()

# Build targets dynamically: (Position, RamaPrimary, Name)
# We recreate the list using the Router's API
# Note: We need the names. For this solver, we can fetch them from the Router
# but the Router is currently pure numeric/phonetic.
# So we import coordinates just for the names, but use Router for calculation.
from vibe_core.mahamantra.substrate.rama_grid import MAHAJANA_COORDINATES, AVATARA_COORDINATES

_ALL_COORDS = sorted(MAHAJANA_COORDINATES + AVATARA_COORDINATES, key=lambda c: c.global_position)

TARGETS = [(c.global_position, router.route_to_rama(c.global_position), c.name.capitalize()) for c in _ALL_COORDS]


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
            best = formulas[:1]  # Take first if no major ones

        print(f"{pos:2} {name:12} [{target}]: {', '.join(best) if best else 'NO EXACT MATCH'}")


if __name__ == "__main__":
    solve()
