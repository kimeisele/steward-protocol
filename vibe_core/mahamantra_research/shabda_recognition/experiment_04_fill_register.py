"""
EXPERIMENT 4: Fill missing phonemes via acoustic interpolation
===============================================================

Missing: AW, F, HH, JH, OW, SH, UH, W, ZH

Acoustic similarity rules:
  AW ~ (AA + UW) / 2    (diphthong: starts like AA, ends like UW)
  F  ~ V with less voicing energy (same place, unvoiced)
  HH ~ low energy version of AH  (glottal fricative)
  JH ~ (CH + DH) / 2    (voiced affricate, between CH and DH)
  OW ~ (AO + UW) / 2    (diphthong: starts like AO, ends like UW)
  SH ~ S shifted         (same manner, different place)
  UH ~ (UW + AH) / 2    (between UW and AH)
  W  ~ UW onset          (labial glide = short UW)
  ZH ~ Z shifted         (same manner as Z, different place like SH)
"""

import sys

sys.path.insert(0, ".")
import json
import numpy as np

# Load existing register
with open("vibe_core/mahamantra_research/shabda_recognition/mfcc_register.json") as f:
    register = json.load(f)


def avg(*keys):
    """Average the MFCC vectors of given phonemes."""
    vecs = [np.array(register[k], dtype=float) for k in keys if k in register]
    if not vecs:
        return None
    return [int(round(x)) for x in np.mean(vecs, axis=0)]


def scale(key, factor):
    """Scale a phoneme's MFCC (e.g., reduce energy for unvoiced variant)."""
    if key not in register:
        return None
    vec = np.array(register[key], dtype=float)
    # Scale non-c0 coefficients (c0 = energy)
    result = vec.copy()
    result[0] = int(result[0] * factor)  # energy scaling
    return [int(round(x)) for x in result]


# Fill missing phonemes
fills = {
    "AW": avg("AA", "UW"),
    "F": scale("V", 0.7),  # unvoiced version of V
    "HH": scale("AH", 0.5),  # weak glottal
    "JH": avg("CH", "DH"),  # voiced affricate
    "OW": avg("AO", "UW"),
    "SH": avg("S", "CH"),  # palatal fricative
    "UH": avg("UW", "AH"),
    "W": avg("UW", "V"),  # labial glide
    "ZH": avg("Z", "DH"),  # voiced palatal fricative
}

print("FILLING MISSING PHONEMES:")
for phoneme, vec in fills.items():
    if vec is not None:
        register[phoneme] = vec
        print(f"  {phoneme:4s}: interpolated -> {vec[1:5]}")
    else:
        print(f"  {phoneme:4s}: FAILED (missing dependencies)")

# Save complete register
output = "vibe_core/mahamantra_research/shabda_recognition/mfcc_register.json"
with open(output, "w") as f:
    json.dump(register, f, indent=2, sort_keys=True)

print(f"\nComplete register: {len(register)} phonemes")
print(f"Saved to: {output}")

# Verify all ARPABET covered
from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import ARPABET_TO_RAMA

all_arpabet = set(ARPABET_TO_RAMA.keys())
covered = set(register.keys())
missing = all_arpabet - covered
print(f"Coverage: {len(covered & all_arpabet)}/{len(all_arpabet)} ARPAbet phonemes")
if missing:
    print(f"Still missing: {sorted(missing)}")
else:
    print("COMPLETE COVERAGE!")
