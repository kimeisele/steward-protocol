import sys
import os
import inspect
from typing import get_type_hints

# Add project root to path
sys.path.append(os.getcwd())

from vibe_core.mahamantra.substrate import seed
from vibe_core.mahamantra.protocols import _gad

print("=== RECON AUDIT: Can _gad.py sprout from seed.py? ===\n")

failures = []
successes = []

def check(condition, message):
    if condition:
        successes.append(message)
        print(f"✅ {message}")
    else:
        failures.append(message)
        print(f"❌ {message}")

# 1. Check Numerical Constants
print("--- 1. Numerical Constants ---")

# CRITERIA_COUNT = 6
# Is 6 in seed?
# seed has: 16 (WORDS), 4 (QUARTERS), 3 (TRINITY), 12 (MAHAJANAS), 24 (KSHETRA), 37 (PARAMPARA), 48 (LILA), 64 (QUALITIES), 108 (MALA)
# Can 6 be derived?
# 24 / 4 = 6 (KSHETRA / QUARTERS)
# 12 / 2 = 6 (MAHAJANAS / 2)
# But is it *explicit*?
derived_6 = seed.KSHETRA // seed.QUARTERS
check(_gad.CRITERIA_COUNT == derived_6, f"CRITERIA_COUNT (6) derived from KSHETRA/QUARTERS ({seed.KSHETRA}/{seed.QUARTERS})")

# DHARMA_COUNT = 4
check(_gad.DHARMA_COUNT == seed.QUARTERS, f"DHARMA_COUNT (4) matches QUARTERS ({seed.QUARTERS})")

# KSHETRA_SIZE = 36
# 6*6 = 36. 
# seed.PARAMPARA = 37. 
# _gad defines KSHETRAJNA = PARAMPARA (37). 
# _gad defines KSHETRA_SIZE = 36.
# 36 + 1 = 37. This logic holds.
check(_gad.KSHETRA_SIZE == (derived_6 * derived_6), "KSHETRA_SIZE (36) is CRITERIA^2")
check(_gad.KSHETRAJNA == seed.PARAMPARA, f"KSHETRAJNA matches PARAMPARA ({seed.PARAMPARA})")

# 2. Check Semantic Content (Enums)
print("\n--- 2. Semantic Content (The DNA) ---")

# Sharanagati Enum (The 6 Limbs)
# Does seed know about "Anululya", "Varanam", etc.?
seed_attrs = dir(seed)
has_sharanagati = "SHARANAGATI" in seed_attrs or any("ANUKULYA" in str(x).upper() for x in seed_attrs)
check(has_sharanagati, "Seed contains Sharanagati concepts")

# GADCriterion Enum (The 6 Criteria)
# Does seed know about "Discoverability", "Observability", etc.?
has_criteria = "CRITERIA" in seed_attrs or any("DISCOVERABILITY" in str(x).upper() for x in seed_attrs)
check(has_criteria, "Seed contains GAD Criteria concepts")

# DharmaPrinciple Enum (The 4 Pillars)
# Does seed know about "Daya", "Satyam", etc.?
has_dharma_names = any("SATYAM" in str(x).upper() for x in seed_attrs)
check(has_dharma_names, "Seed contains Dharma Principle names")

# 3. Check Structure
print("\n--- 3. Structural Integrity ---")
# Does GADProtocol derive from MahamantraProtocol?
check(issubclass(_gad.GADProtocolDef, _gad.MahamantraProtocolBase), "GADProtocolDef is a MahamantraProtocol")

print("\n=== AUDIT CONCLUSION ===")
if not failures:
    print("Seed is COMPLETE. _gad.py can be fully derived.")
else:
    print(f"Seed is INCOMPLETE. Found {len(failures)} gaps.")
    print("Missing DNA:")
    for f in failures:
        print(f" - {f}")
