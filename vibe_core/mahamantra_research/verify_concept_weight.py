"""
CONCEPT WEIGHT APPROACH: Instead of aggregating all Sanskrit words into
one spell_cycle, we WEIGHT the resonating concepts by their Guna nature.

Key insight: The Gita lexicon meanings already CARRY intent information.
"death", "destroy", "fear" are TAMAS concepts.
"success", "victory", "peace" are SATTVA concepts.
"fight", "work", "act" are RAJAS concepts.
"supreme", "transcendental", "divine" are SUDDHA concepts.

We don't need spell_cycle or mod 17. We need to measure which
GUNA DOMAIN the resonating Sanskrit words belong to.

But we do this through PHONETICS, not keywords:
- Each Sanskrit word has a 4D signature (Element, Varga, Harmonic, Shruti)
- Words in the same semantic domain share phonetic patterns
  (dharma<->adharma similarity = 1.0, proven in 7D Ranker research)
- The ELEMENT DISTRIBUTION of the resonating words IS the intent signal

The 5 Elements map to energetic qualities:
  AKASHA (0) = Space/Ether = potential, unmanifest = SUDDHA tendency
  VAYU (1)   = Air = movement, change = RAJAS tendency
  AGNI (2)   = Fire = transformation, destruction = TAMAS tendency (errors burn)
  JALA (3)   = Water = flow, connection = SATTVA tendency
  PRITHVI (4)= Earth = stability, grounding = SATTVA tendency
"""

import re
from collections import Counter
from vibe_core.mahamantra.substrate.semantic_index import get_index
from vibe_core.mahamantra.substrate.pancha_walk import COORD_ELEMENT, Element

idx = get_index()
idx._ensure_loaded()

# Dhatu bridge (same as before, abbreviated)
DHATU_BRIDGE = {
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
    "broken": ["destroy", "fall", "loss"],
    "invalid": ["wrong", "fault", "illusion"],
    "timeout": ["death", "end", "loss"],
    "warning": ["fear", "danger", "distress"],
    "warn": ["fear", "danger"],
    "slow": ["bondage", "material"],
    "retry": ["again", "repeated"],
    "deprecated": ["temporary", "changing", "end"],
    "degraded": ["fall", "loss", "material"],
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
    "optimal": ["supreme", "perfect", "transcendental"],
    "unified": ["one", "supreme", "eternal"],
    "harmonious": ["peace", "transcendental", "bliss"],
    "perfect": ["perfect", "supreme", "transcendental"],
    "pure": ["pure", "transcendental", "divine"],
    "achieved": ["success", "liberation", "transcendental"],
    "fix": ["fix", "control", "steady"],
    "todo": ["work", "activities", "perform"],
    "database": ["knowledge", "material", "nature"],
    "system": ["system", "nature", "material"],
    "memory": ["memory", "mind", "consciousness"],
    "application": ["activities", "work", "nature"],
    "service": ["service", "devotional", "engaged"],
    "services": ["service", "devotional", "engaged"],
    "everything": ["everything", "all"],
    "issue": ["distress", "fault", "wrong"],
    "minor": ["material", "nature"],
    "critical": ["death", "destroy", "fear"],
    "connection": ["connection", "engaged"],
    "progress": ["activities", "work"],
    "query": ["knowledge", "know", "see"],
    "detected": ["knowledge", "see", "know"],
    "workaround": ["work", "activities"],
    "later": ["temporary", "changing"],
    "tests": ["knowledge", "know"],
    "deployment": ["situated", "engaged"],
    "occurred": ["activities", "manifest"],
    "partial": ["material", "nature"],
    "segfault": ["destroy", "death"],
}


def tokenize(text):
    return [w for w in re.findall(r"[a-zA-Z]+", text.lower()) if len(w) >= 2]


def english_to_sanskrit(text):
    tokens = tokenize(text)
    seen = set()
    resonant = []
    for tok in tokens:
        direct = idx._by_meaning_word.get(tok, [])
        if direct:
            for w in direct:
                wid = id(w)
                if wid not in seen:
                    seen.add(wid)
                    resonant.append(w)
            continue
        bridge_tokens = DHATU_BRIDGE.get(tok, [])
        for bt in bridge_tokens:
            for w in idx._by_meaning_word.get(bt, []):
                wid = id(w)
                if wid not in seen:
                    seen.add(wid)
                    resonant.append(w)
    return resonant


def element_distribution(words):
    """Get normalized element distribution from Sanskrit words."""
    if not words:
        return [0.0] * 5
    counts = [0] * 5
    total = 0
    for w in words:
        for c in w.coords:
            counts[COORD_ELEMENT[c]] += 1
            total += 1
    if total == 0:
        return [0.0] * 5
    return [c / total for c in counts]


def hkr_distribution(words):
    """Get H/K/R distribution from Sanskrit words."""
    from vibe_core.mahamantra.substrate.basin_map import COORD_HKR

    if not words:
        return (0.0, 0.0, 0.0)
    h_sum = k_sum = r_sum = 0.0
    total = 0
    for w in words:
        for c in w.coords:
            hkr = COORD_HKR[c]
            h_sum += hkr[0]
            k_sum += hkr[1]
            r_sum += hkr[2]
            total += 1
    if total == 0:
        return (0.0, 0.0, 0.0)
    return (h_sum / total, k_sum / total, r_sum / total)


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

print("=" * 100)
print("ELEMENT + HKR DISTRIBUTION OF RESONATING SANSKRIT WORDS")
print("Elements: Ak=Akasha Va=Vayu Ag=Agni Ja=Jala Pr=Prithvi")
print("HKR: H=Hare K=Krishna R=Rama")
print("=" * 100)

header = (
    f"{'Text':<40} {'Ak':>5} {'Va':>5} {'Ag':>5} {'Ja':>5} {'Pr':>5} | {'H':>5} {'K':>5} {'R':>5} | {'N':>3} {'Exp':<7}"
)
print(header)
print("-" * 100)

data_by_guna = {"tamas": [], "rajas": [], "sattva": [], "suddha": []}

for text, expected in tests:
    resonant = english_to_sanskrit(text)
    elem = element_distribution(resonant)
    hkr = hkr_distribution(resonant)
    data_by_guna[expected].append({"elem": elem, "hkr": hkr, "n": len(resonant)})

    print(
        f"{text[:38]:<40} "
        f"{elem[0]:>5.2f} {elem[1]:>5.2f} {elem[2]:>5.2f} {elem[3]:>5.2f} {elem[4]:>5.2f} | "
        f"{hkr[0]:>5.2f} {hkr[1]:>5.2f} {hkr[2]:>5.2f} | "
        f"{len(resonant):>3} {expected:<7}"
    )

print("\n" + "=" * 100)
print("AVERAGE BY GUNA")
print("=" * 100)

for guna in ["tamas", "rajas", "sattva", "suddha"]:
    entries = data_by_guna[guna]
    if not entries:
        continue
    n = len(entries)
    avg_elem = [sum(e["elem"][i] for e in entries) / n for i in range(5)]
    avg_hkr = tuple(sum(e["hkr"][i] for e in entries) / n for i in range(3))
    avg_n = sum(e["n"] for e in entries) / n

    print(
        f"  {guna:>7} (n={n}): "
        f"Ak={avg_elem[0]:.3f} Va={avg_elem[1]:.3f} Ag={avg_elem[2]:.3f} "
        f"Ja={avg_elem[3]:.3f} Pr={avg_elem[4]:.3f} | "
        f"H={avg_hkr[0]:.3f} K={avg_hkr[1]:.3f} R={avg_hkr[2]:.3f} | "
        f"avg_words={avg_n:.0f}"
    )

# Check: is there ANY dimension that separates the gunas?
print("\n" + "=" * 100)
print("DISCRIMINATION ANALYSIS: Which dimension separates gunas best?")
print("=" * 100)

for dim_name, dim_idx in [("Akasha", 0), ("Vayu", 1), ("Agni", 2), ("Jala", 3), ("Prithvi", 4)]:
    vals = {}
    for guna in ["tamas", "rajas", "sattva", "suddha"]:
        entries = data_by_guna[guna]
        if entries:
            vals[guna] = [e["elem"][dim_idx] for e in entries]
    ranges = {g: (min(v), max(v)) for g, v in vals.items() if v}
    print(f"  {dim_name:>8}: ", end="")
    for g in ["tamas", "rajas", "sattva", "suddha"]:
        if g in ranges:
            lo, hi = ranges[g]
            print(f"{g}=[{lo:.3f}-{hi:.3f}] ", end="")
    print()

for dim_name, dim_idx in [("H", 0), ("K", 1), ("R", 2)]:
    vals = {}
    for guna in ["tamas", "rajas", "sattva", "suddha"]:
        entries = data_by_guna[guna]
        if entries:
            vals[guna] = [e["hkr"][dim_idx] for e in entries]
    ranges = {g: (min(v), max(v)) for g, v in vals.items() if v}
    print(f"  {dim_name:>8}: ", end="")
    for g in ["tamas", "rajas", "sattva", "suddha"]:
        if g in ranges:
            lo, hi = ranges[g]
            print(f"{g}=[{lo:.3f}-{hi:.3f}] ", end="")
    print()
