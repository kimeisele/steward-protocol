"""
DHATU BRIDGE: Tech-Jargon -> Gita-Konzepte -> Sanskrit -> 4D -> Intent

The Gita lexicon covers 88-94% of human concepts but only 25% of tech jargon.
The missing tech words are NOT new concepts — they are PROJECTIONS of existing
Gita concepts into the technical domain.

"error" is not a new idea. It's doṣa (fault), vighna (obstacle), moha (confusion).
"warning" is not new. It's bhaya (fear), āpatti (danger).
"crash" is not new. It's vināśa (destruction), patana (fall).

This bridge is NOT keyword matching. It's a DHATU ROOT MAPPING:
each tech concept maps to its Sanskrit ROOT MEANING, not to a string.
The Sanskrit root then flows through the full Shabda pipeline.

Think of it as: English has a "Guna-Blaustich" (color cast).
This bridge removes the cast to reveal the underlying vibration.
"""

import re
from vibe_core.mahamantra.substrate.semantic_index import get_index, LexiconWord
from vibe_core.mahamantra.substrate.pancha_walk import (
    COORD_ELEMENT, COORD_VARGA, COORD_HARMONIC, IS_SHRUTI,
)
from vibe_core.mahamantra.adapters.synth import MahaSynth
from vibe_core.mahamantra.protocols._seed import (
    POSITION_SUM_KRISHNA, KSETRAJNA, TRINITY, NAVA, SEVEN, WORDS, QUARTERS,
)

KRISHNA = POSITION_SUM_KRISHNA  # 17

# =============================================================================
# DHATU BRIDGE: Tech concepts -> Gita meaning tokens
# =============================================================================
# This is NOT keyword matching. This is CONCEPT DECONVOLUTION.
# Each tech word maps to its Vedic ROOT CONCEPT(s) that exist in the Gita.
# The mapping is SEMANTIC, not string-based.
#
# Structure: tech_word -> [gita_meaning_tokens]
# These tokens are looked up in SemanticIndex.by_meaning()

DHATU_BRIDGE = {
    # Error/Failure domain -> doṣa, vighna, moha
    "error": ["fault", "wrong", "failure", "bewildered"],
    "errors": ["fault", "wrong", "failure"],
    "fail": ["failure", "fall", "loss"],
    "failed": ["failure", "fall", "loss"],
    "failure": ["failure", "fall", "loss"],
    "fatal": ["death", "destroy", "end"],
    "crash": ["destroy", "fall", "death"],
    "crashed": ["destroy", "fall", "death"],
    "bug": ["fault", "wrong", "illusion"],
    "exception": ["fault", "distress", "bewildered"],
    "panic": ["fear", "distress", "bewildered"],
    "corrupt": ["sin", "evil", "illusion"],
    "broken": ["destroy", "fall", "loss"],
    "invalid": ["wrong", "fault", "illusion"],
    "timeout": ["death", "end", "loss"],
    "abort": ["death", "end", "destroy"],

    # Warning/Caution domain -> bhaya, sāvadhāna
    "warning": ["fear", "danger", "distress"],
    "warn": ["fear", "danger"],
    "caution": ["fear", "danger"],
    "deprecated": ["temporary", "changing", "end"],
    "slow": ["bondage", "material", "heavy"],
    "retry": ["again", "repeated"],
    "degraded": ["fall", "loss", "material"],

    # Success/Positive domain -> siddhi, vijaya
    "success": ["success", "victory", "perfect"],
    "succeeded": ["success", "victory"],
    "passed": ["success", "passed", "transcendental"],
    "complete": ["complete", "perfect", "all"],
    "completed": ["complete", "perfect"],
    "done": ["done", "complete", "perfect"],
    "healthy": ["living", "nature", "good"],
    "stable": ["stable", "fixed", "steady"],
    "verified": ["knowledge", "know", "fixed"],
    "green": ["auspicious", "nature", "good"],
    "deployed": ["situated", "engaged", "work"],
    "running": ["living", "engaged", "activities"],
    "active": ["living", "engaged", "activities"],
    "ready": ["fixed", "steady", "situated"],

    # Transcendental/Pure domain -> śuddha, divya
    "optimal": ["supreme", "perfect", "transcendental"],
    "unified": ["one", "supreme", "eternal"],
    "harmonious": ["peace", "transcendental", "bliss"],
    "perfect": ["perfect", "supreme", "transcendental"],
    "pure": ["pure", "transcendental", "divine"],
    "achieved": ["success", "liberation", "transcendental"],

    # Action domain -> karma, kriyā
    "create": ["create", "birth", "manifest"],
    "delete": ["destroy", "death", "end"],
    "update": ["changing", "work", "activities"],
    "read": ["knowledge", "see", "know"],
    "write": ["work", "activities", "create"],
    "connect": ["connection", "engaged"],
    "disconnect": ["without", "bondage", "loss"],
    "build": ["create", "work", "manifest"],
    "test": ["knowledge", "know", "see"],
    "deploy": ["situated", "engaged", "work"],
    "start": ["birth", "manifest", "begin"],
    "stop": ["stop", "end", "death"],
    "run": ["activities", "work", "engaged"],
    "process": ["process", "activities", "work"],
    "query": ["knowledge", "know", "see"],
    "execute": ["act", "perform", "work"],
    "fix": ["fix", "control", "steady"],

    # System domain
    "system": ["system", "nature", "material"],
    "database": ["knowledge", "material", "nature"],
    "memory": ["memory", "mind", "consciousness"],
    "thread": ["thread", "activities", "engaged"],
    "queue": ["activities", "work", "engaged"],
    "network": ["connection", "material", "nature"],
    "server": ["service", "work", "engaged"],
    "application": ["activities", "work", "nature"],
    "service": ["service", "devotional", "engaged"],
    "configuration": ["nature", "material", "mode"],
}

idx = get_index()
idx._ensure_loaded()


def tokenize(text):
    return [w for w in re.findall(r'[a-zA-Z]+', text.lower()) if len(w) >= 2]


def english_to_sanskrit(text):
    """
    Full Dhatu Bridge pipeline:
    1. Tokenize English text
    2. For each token: check direct meaning match OR dhatu bridge
    3. Collect all resonating Sanskrit words
    4. Deduplicate
    """
    tokens = tokenize(text)
    seen = set()
    resonant = []
    matched_via = {}  # token -> "direct" or "bridge"

    for tok in tokens:
        # Direct meaning match first
        direct = idx._by_meaning_word.get(tok, [])
        if direct:
            for w in direct:
                wid = id(w)
                if wid not in seen:
                    seen.add(wid)
                    resonant.append(w)
            matched_via[tok] = "direct"
            continue

        # Dhatu bridge: expand to Gita concepts
        bridge_tokens = DHATU_BRIDGE.get(tok, [])
        if bridge_tokens:
            for bt in bridge_tokens:
                for w in idx._by_meaning_word.get(bt, []):
                    wid = id(w)
                    if wid not in seen:
                        seen.add(wid)
                        resonant.append(w)
            matched_via[tok] = f"bridge->{bridge_tokens}"

    return resonant, matched_via


def compute_intent_from_sanskrit(words):
    """
    Sanskrit words -> 4D phonetic energy -> spell_cycle -> intent.

    Uses spell_cycle (not just energy sum) because spell_cycle treats
    each phoneme as a MODULATION INSTRUCTION through the synth.
    """
    if not words:
        return None, 0, 0

    # Collect ALL RAMA coords from resonating words (limit to top SEVEN)
    # Top 7 = SEVEN, the axiom number for effects
    top_words = words[:SEVEN * 3]  # Take more, then use their coords
    all_coords = []
    for w in top_words:
        all_coords.extend(w.coords)

    if not all_coords:
        return None, 0, 0

    # spell_cycle: treat the aggregate coords as a phoneme program
    synth = MahaSynth(preset="quantum")
    spell = synth.spell_cycle(tuple(all_coords), seed=0)

    # 4D energy sum
    energy = sum(all_coords)

    # Remnant theorem on spell_cycle result
    attractor = spell.final_value
    remnant = attractor % KRISHNA

    # Also compute category from attractor
    category = attractor % WORDS  # 0-15
    quarter = category // QUARTERS  # 0-3

    return {
        "attractor": attractor,
        "remnant_17": remnant,
        "category_16": category,
        "quarter": quarter,
        "energy": energy,
        "n_coords": len(all_coords),
        "n_words": len(top_words),
    }


# =============================================================================
# TEST
# =============================================================================

tests = [
    ("ERROR: Database connection failed", "tamas"),
    ("FATAL: Application crashed with segfault", "tamas"),
    ("WARNING: Slow query detected, retry in progress", "rajas"),
    ("TODO: Fix this workaround later", "rajas"),
    ("SUCCESS: All tests passed, deployment complete", "sattva"),
    ("System healthy and stable, all services verified", "sattva"),
    ("Unified system achieved optimal harmonious state", "suddha"),
    ("Error occurred but partial success achieved", "tamas"),
    ("Error: fail", "tamas"),
    ("Warning: slow", "rajas"),
    ("Success: done", "sattva"),
    ("Everything is healthy", "sattva"),
    ("Warning: minor issue", "rajas"),
    ("Error: critical failure", "tamas"),
]

gunas = ["tamas", "rajas", "sattva", "suddha"]

print("=" * 90)
print("DHATU BRIDGE INTENT CLASSIFICATION")
print("English -> Dhatu Bridge -> Sanskrit -> spell_cycle -> mod 17 -> Intent")
print("=" * 90)

# First pass: see what remnants each guna produces
remnant_by_guna = {g: [] for g in gunas}
quarter_by_guna = {g: [] for g in gunas}
results = []

for text, expected in tests:
    resonant, matched = english_to_sanskrit(text)
    intent = compute_intent_from_sanskrit(resonant)

    if intent:
        remnant_by_guna[expected].append(intent["remnant_17"])
        quarter_by_guna[expected].append(intent["quarter"])

    results.append((text, expected, resonant, matched, intent))

# Print results
for text, expected, resonant, matched, intent in results:
    print(f"\n  Text: {text}")
    print(f"  Matched: {dict(matched)}")
    print(f"  Sanskrit: {len(resonant)} words -> {[w.sanskrit for w in resonant[:5]]}")
    if intent:
        print(f"  Attractor={intent['attractor']} cat={intent['category_16']} q={intent['quarter']} "
              f"rem17={intent['remnant_17']} energy={intent['energy']} "
              f"({intent['n_coords']} coords from {intent['n_words']} words)")
    else:
        print(f"  NO RESONANCE")
    print(f"  Expected: {expected}")

print("\n" + "=" * 90)
print("CLUSTERING ANALYSIS")
print("=" * 90)
for g in gunas:
    print(f"  {g:>7}: remnants={str(sorted(remnant_by_guna[g])):30s} quarters={sorted(quarter_by_guna[g])}")

# Can we find a mapping from remnant/quarter to guna?
print("\n" + "=" * 90)
print("QUARTER -> GUNA ACCURACY (category // 4)")
print("=" * 90)
correct = 0
total = len(tests)
for text, expected, resonant, matched, intent in results:
    if intent:
        q = intent["quarter"]
        got = gunas[q]
        ok = (got == expected)
        if ok:
            correct += 1
        mark = "OK" if ok else "XX"
        print(f"  {mark}  q={q} got={got:>7} exp={expected:>6}  | {text[:50]}")
    else:
        print(f"  --  NO DATA  exp={expected:>6}  | {text[:50]}")
print(f"\nQuarter accuracy: {correct}/{total} = {100*correct/total:.0f}%")
