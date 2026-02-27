"""
EXPERIMENT 2: Compare coordinate spaces
=========================================

The decoder has TWO coordinate paths. They must produce the SAME coords
for the same word, or matching is impossible. Let's see what happens.

PATH 1: Audio → stream_to_rama() → RAMA coords (articulatory)
PATH 2: Text  → encode_text()    → RAMA coords (letter-by-letter)
PATH 3: Text  → CMU dict → ARPAbet → ARPABET_TO_RAMA → RAMA coords

For a known word, all three should produce SIMILAR coord sequences.
If they don't, we found the bug.
"""
import sys; sys.path.insert(0, ".")

from vibe_core.mahamantra.substrate.encoding.phonetic_encoder import encode_text
from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import ARPABET_TO_RAMA
from vibe_core.mahamantra.substrate.encoding.pancha_walk import (
    COORD_ELEMENT, COORD_VARGA, COORD_SUB,
)

# Load CMU dict
try:
    import nltk
    cmu = nltk.corpus.cmudict.dict()
except Exception:
    cmu = {}

def cmu_to_rama(word):
    """CMU dict → ARPAbet → ARPABET_TO_RAMA."""
    prons = cmu.get(word.lower())
    if not prons:
        return None
    # Strip stress digits
    phonemes = []
    for p in prons[0]:
        clean = ''.join(c for c in p if not c.isdigit())
        phonemes.append(clean)
    coords = []
    for p in phonemes:
        r = ARPABET_TO_RAMA.get(p)
        if r is not None:
            coords.append(r)
    return tuple(coords) if coords else None


words = ["not", "exactly", "but", "came", "preach", "gospel",
         "consciousness", "boys", "girls", "the", "of", "eh"]

print(f"{'WORD':15s} {'encode_text':30s} {'CMU→RAMA':30s}")
print("-" * 75)

for w in words:
    et = encode_text(w)
    cr = cmu_to_rama(w)
    
    def fmt(coords):
        if coords is None:
            return "None"
        return str(coords)
    
    print(f"{w:15s} {fmt(et):30s} {fmt(cr):30s}")

print()
print("LEGEND: Each int is a RAMA coordinate (0-48)")
print("  0-15  = SVARA (vowels)")
print("  16-40 = SPARSHA (consonants)")  
print("  41-48 = SHESHA (semivowels/sibilants)")
print()

# Now show what stream_to_rama produces per element
print("COORD ANATOMY:")
print(f"{'COORD':6s} {'ELEM':6s} {'VARGA':6s} {'SUB':5s}")
for c in range(49):
    print(f"  {c:3d}    {COORD_ELEMENT[c]:3d}    {COORD_VARGA[c]:3d}    {COORD_SUB[c]:3d}")
