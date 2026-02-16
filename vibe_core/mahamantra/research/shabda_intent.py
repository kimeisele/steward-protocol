"""
SHABDA INTENT — Can Pure Vibration Compute Intent?
====================================================

DISCOVERY CHAIN:
    1. Keywords are Web 2.0 (hardcoded lists) — must go
    2. Seed position is pseudo-random because SHA256 dominates Shabda
    3. BUT: Articulation distributions DIFFER between good/bad (distance 0.075)
    4. AND: Each phoneme already has a RAMA coord (signature_id % 49)
    5. AND: Each RAMA coord has a precomputed HKR color and basin

HYPOTHESIS:
    If we skip SHA256 entirely and compute the seed ONLY from Shabda,
    the position becomes phonetically determined.

    But more importantly: we already have the 7D resonance ranker.
    Each text produces a VIBRATION SIGNATURE — a sequence of phonemes,
    each with articulation, voicing, frequency, duration.

    This signature IS the intent. We don't need to classify it into
    4 buckets (TAMAS/RAJAS/SATTVA/SUDDHA). We need to let the
    Mahamantra COMPUTE what it means.

THE REAL QUESTION:
    What if intent is not a 4-bucket classifier at all?
    What if intent is a POSITION in the 16-word grid,
    a BASIN in mod-137 space, an HKR COLOR, and an
    ARTICULATION DISTRIBUTION — all at once?

    The Mahamantra doesn't say "this is good" or "this is bad".
    It says "this vibrates at position 7, basin 136, HKR (0.44, 0.27, 0.29),
    articulation TALU-dominant". That IS the intent.

EXPERIMENT:
    1. Compute pure Shabda fingerprint (no SHA256)
    2. Run through Synth to get attractor
    3. Get basin, HKR, phoneme attractor
    4. Compute articulation/voicing distribution
    5. See if this MULTI-DIMENSIONAL intent separates naturally
    6. Compare with the flat 4-bucket keyword system
"""

import math
from typing import Dict, List, Tuple

from vibe_core.mahamantra.substrate.phonetics.shabda import (
    text_to_vibration,
    VibrationSignature,
    ArticulationPoint,
    VoicingType,
)
from vibe_core.mahamantra.substrate.algorithm.maha import (
    MahaAlgorithm16,
    MahaModularSynth,
)
from vibe_core.mahamantra.substrate.basin_map import (
    COORD_BASIN,
    COORD_HKR,
    COORD_PHONEME_ATTRACTOR,
    BASIN_LIST,
    BASIN_INDEX,
    BASIN_COUNT,
    PHONEME_ATTRACTOR_LIST,
    PHONEME_ATTRACTOR_INDEX,
    PHONEME_ATTRACTOR_COUNT,
)
from vibe_core.mahamantra.protocols._seed import WORDS, MAHA_QUANTUM, QUARTERS


# =============================================================================
# PURE SHABDA FINGERPRINT — no SHA256, no keywords
# =============================================================================

class ShabdaFingerprint:
    """
    The complete vibration identity of a text.
    Computed entirely from phonetic structure.
    No hashing. No keywords. Pure Shabda.
    """

    __slots__ = (
        "text", "vibrations", "phoneme_count",
        "artic_dist", "voice_dist",
        "vib_sum", "rama_coords",
        "basin_hist", "hkr_color", "pa_hist",
        "seed", "position", "attractor", "basin",
    )

    def __init__(self, text: str) -> None:
        self.text = text
        self.vibrations = text_to_vibration(text)
        self.phoneme_count = len(self.vibrations)

        # Articulation distribution (5 elements = Pancha Bhuta)
        self.artic_dist = [0.0] * 5
        self.voice_dist = [0.0] * 4

        if self.phoneme_count > 0:
            for v in self.vibrations:
                self.artic_dist[v.articulation.value] += 1
                self.voice_dist[v.voicing.value] += 1
            n = self.phoneme_count
            self.artic_dist = [a / n for a in self.artic_dist]
            self.voice_dist = [v / n for v in self.voice_dist]

        # Vibration sum (the Shabda signal)
        self.vib_sum = sum(s.signature_id for s in self.vibrations) if self.vibrations else 0

        # RAMA coordinates (each phoneme → coord in 49-space)
        self.rama_coords = [s.signature_id % 49 for s in self.vibrations] if self.vibrations else [0]

        # Basin histogram
        self.basin_hist = [0] * BASIN_COUNT
        for c in self.rama_coords:
            b = COORD_BASIN[c]
            self.basin_hist[BASIN_INDEX[b]] += 1

        # HKR color
        h, k, r = 0.0, 0.0, 0.0
        for c in self.rama_coords:
            ch, ck, cr = COORD_HKR[c]
            h += ch; k += ck; r += cr
        n = len(self.rama_coords)
        self.hkr_color = (h / n, k / n, r / n)

        # Phoneme attractor histogram
        self.pa_hist = [0] * PHONEME_ATTRACTOR_COUNT
        for c in self.rama_coords:
            pa = COORD_PHONEME_ATTRACTOR[c]
            self.pa_hist[PHONEME_ATTRACTOR_INDEX[pa]] += 1

        # Pure Shabda seed (NO SHA256)
        # The seed is the vibration sum run through the Synth
        synth = MahaModularSynth(default_preset="quantum")
        self.seed = synth.transform(self.vib_sum % MAHA_QUANTUM)
        self.position = self.seed % WORDS
        self.attractor = self.seed % MAHA_QUANTUM

        # Basin convergence
        algo = MahaAlgorithm16()
        val = self.attractor
        for _ in range(100):
            prev = val
            val = algo.transform(val)
            if val == prev:
                break
        self.basin = val

    @property
    def quarter(self) -> int:
        return self.position // QUARTERS

    @property
    def quarter_name(self) -> str:
        return ["KSETRAJNA", "KRISHNA", "PRAKRITI", "KARMA"][self.quarter]

    @property
    def dominant_articulation(self) -> str:
        names = ["KANTHA", "TALU", "MURDHA", "DANTA", "OSHTHA"]
        return names[self.artic_dist.index(max(self.artic_dist))]

    @property
    def dominant_hkr(self) -> str:
        h, k, r = self.hkr_color
        if h >= k and h >= r: return "H"
        if k >= r: return "K"
        return "R"


def shabda_distance(a: ShabdaFingerprint, b: ShabdaFingerprint) -> float:
    """
    Multi-dimensional distance between two Shabda fingerprints.
    Combines articulation, voicing, HKR, and basin distances.
    All dimensions are weighted equally — the Mahamantra decides.
    """
    # Articulation distance (5D)
    artic_d = sum((a.artic_dist[i] - b.artic_dist[i])**2 for i in range(5)) ** 0.5

    # Voicing distance (4D)
    voice_d = sum((a.voice_dist[i] - b.voice_dist[i])**2 for i in range(4)) ** 0.5

    # HKR distance (3D)
    hkr_d = sum((a.hkr_color[i] - b.hkr_color[i])**2 for i in range(3)) ** 0.5

    # Basin histogram cosine distance
    dot = sum(a.basin_hist[i] * b.basin_hist[i] for i in range(BASIN_COUNT))
    mag_a = sum(v * v for v in a.basin_hist) ** 0.5
    mag_b = sum(v * v for v in b.basin_hist) ** 0.5
    basin_sim = dot / (mag_a * mag_b) if mag_a > 0 and mag_b > 0 else 0.0
    basin_d = 1.0 - basin_sim

    # Combined (equal weight — let the math speak)
    return (artic_d + voice_d + hkr_d + basin_d) / 4.0


# =============================================================================
# CORPUS
# =============================================================================

CORPUS = [
    # CLEAN CODE
    ("clean", "def add(x: int, y: int) -> int:\n    return x + y"),
    ("clean", "def greet(name: str) -> str:\n    return f'Hello, {name}'"),
    ("clean", "class Config:\n    def __init__(self, path: Path) -> None:\n        self.path = path"),
    ("clean", "from typing import Dict\ndef load(path: str) -> Dict[str, str]:\n    return json.loads(Path(path).read_text())"),
    ("clean", "def validate(data: dict) -> bool:\n    return 'name' in data and 'id' in data"),
    ("clean", "import logging\nlogger = logging.getLogger(__name__)"),

    # BROKEN CODE
    ("broken", "from typing import Any\ndef f(x: Any) -> Any:\n    return x"),
    ("broken", "def load(p):\n    try:\n        return open(p).read()\n    except:\n        pass"),
    ("broken", "from typing import *\ndef g(a, b, c):\n    return a"),
    ("broken", "def h(x: Any, y: Any, z: Any) -> Any:\n    try:\n        return x + y + z\n    except Exception:\n        pass"),
    ("broken", "import os, sys, json, re, pathlib\nfrom typing import Any\nx: Any = None"),
    ("broken", "class Bad:\n    def do(self, thing):\n        try: return eval(thing)\n        except: return None"),

    # HEALTHY TEXT
    ("healthy", "All services healthy. Deployment complete."),
    ("healthy", "Tests passed. Coverage at 95 percent. No regressions."),
    ("healthy", "System stable for 30 days. Zero incidents."),
    ("healthy", "Performance optimized. Latency reduced by 40 percent."),

    # FAILING TEXT
    ("failing", "Connection refused. Retry failed after 5 attempts."),
    ("failing", "Out of memory. Process killed."),
    ("failing", "Database corruption detected. Backup failed."),
    ("failing", "Security breach. Unauthorized access detected."),
]


# =============================================================================
# ANALYSIS
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 95)
    print("  SHABDA INTENT — Pure Vibration Fingerprints")
    print("=" * 95)

    fingerprints: Dict[str, List[ShabdaFingerprint]] = {}
    all_fps: List[Tuple[str, ShabdaFingerprint]] = []

    print(f"\n  {'#':>2}  {'Type':>8}  {'Pos':>3}  {'Q':>8}  {'Basin':>5}  {'DomA':>6}  {'DomH':>4}  "
          f"{'HKR':>17}  {'Phon':>4}  Text")
    print(f"  {'-'*2}  {'-'*8}  {'-'*3}  {'-'*8}  {'-'*5}  {'-'*6}  {'-'*4}  {'-'*17}  {'-'*4}  {'-'*35}")

    for i, (label, text) in enumerate(CORPUS):
        fp = ShabdaFingerprint(text)
        fingerprints.setdefault(label, []).append(fp)
        all_fps.append((label, fp))

        hkr_str = f"({fp.hkr_color[0]:.2f},{fp.hkr_color[1]:.2f},{fp.hkr_color[2]:.2f})"
        text_short = text.replace("\n", " ")[:35]
        print(f"  {i+1:>2}  {label:>8}  {fp.position:>3}  {fp.quarter_name:>8}  {fp.basin:>5}  "
              f"{fp.dominant_articulation:>6}  {fp.dominant_hkr:>4}  {hkr_str:>17}  {fp.phoneme_count:>4}  {text_short}")

    # === INTRA-GROUP vs INTER-GROUP DISTANCES ===
    print(f"\n{'='*95}")
    print("  DISTANCE MATRIX — Do same-type inputs cluster together?")
    print(f"{'='*95}")

    groups = ["clean", "broken", "healthy", "failing"]
    intra_distances = {}
    inter_distances = {}

    for g in groups:
        fps = fingerprints.get(g, [])
        # Intra-group: average distance within group
        dists = []
        for i in range(len(fps)):
            for j in range(i + 1, len(fps)):
                dists.append(shabda_distance(fps[i], fps[j]))
        intra_distances[g] = sum(dists) / len(dists) if dists else 0.0

    # Inter-group distances
    for i, g1 in enumerate(groups):
        for g2 in groups[i+1:]:
            dists = []
            for fp1 in fingerprints.get(g1, []):
                for fp2 in fingerprints.get(g2, []):
                    dists.append(shabda_distance(fp1, fp2))
            key = f"{g1}-{g2}"
            inter_distances[key] = sum(dists) / len(dists) if dists else 0.0

    print(f"\n  INTRA-GROUP (lower = tighter cluster):")
    for g, d in sorted(intra_distances.items()):
        print(f"    {g:>8}: {d:.4f}")

    print(f"\n  INTER-GROUP (higher = better separation):")
    for key, d in sorted(inter_distances.items(), key=lambda x: -x[1]):
        print(f"    {key:>16}: {d:.4f}")

    # === SEPARATION RATIO ===
    print(f"\n{'='*95}")
    print("  SEPARATION ANALYSIS")
    print(f"{'='*95}")

    # Good vs Bad
    good_fps = fingerprints.get("clean", []) + fingerprints.get("healthy", [])
    bad_fps = fingerprints.get("broken", []) + fingerprints.get("failing", [])

    good_intra = []
    for i in range(len(good_fps)):
        for j in range(i+1, len(good_fps)):
            good_intra.append(shabda_distance(good_fps[i], good_fps[j]))

    bad_intra = []
    for i in range(len(bad_fps)):
        for j in range(i+1, len(bad_fps)):
            bad_intra.append(shabda_distance(bad_fps[i], bad_fps[j]))

    cross = []
    for fp1 in good_fps:
        for fp2 in bad_fps:
            cross.append(shabda_distance(fp1, fp2))

    avg_good_intra = sum(good_intra) / len(good_intra) if good_intra else 0
    avg_bad_intra = sum(bad_intra) / len(bad_intra) if bad_intra else 0
    avg_cross = sum(cross) / len(cross) if cross else 0
    avg_intra = (avg_good_intra + avg_bad_intra) / 2

    separation_ratio = avg_cross / avg_intra if avg_intra > 0 else 0

    print(f"\n  Good intra-distance:  {avg_good_intra:.4f}")
    print(f"  Bad intra-distance:   {avg_bad_intra:.4f}")
    print(f"  Cross-distance:       {avg_cross:.4f}")
    print(f"  Separation ratio:     {separation_ratio:.4f}  (>1.0 = separable)")

    # === ARTICULATION CENTROID ===
    print(f"\n{'='*95}")
    print("  ARTICULATION CENTROIDS — The Pancha Bhuta of Intent")
    print(f"{'='*95}")

    artic_names = ["KANTHA", "TALU", "MURDHA", "DANTA", "OSHTHA"]
    element_names = ["Akasha", "Vayu", "Agni", "Jala", "Prithvi"]

    for label in groups:
        fps = fingerprints.get(label, [])
        if not fps:
            continue
        centroid = [0.0] * 5
        for fp in fps:
            for i in range(5):
                centroid[i] += fp.artic_dist[i]
        centroid = [c / len(fps) for c in centroid]
        dominant = artic_names[centroid.index(max(centroid))]
        element = element_names[centroid.index(max(centroid))]

        print(f"\n  [{label:>8}]  dominant={dominant} ({element})")
        for i in range(5):
            bar = "█" * int(centroid[i] * 50)
            print(f"    {artic_names[i]:>6} ({element_names[i]:>7}): {centroid[i]:.3f}  {bar}")

    # === CONCLUSION ===
    print(f"\n{'='*95}")
    print("  CONCLUSION")
    print(f"{'='*95}")

    if separation_ratio > 1.2:
        print(f"\n  >>> SHABDA SEPARATES: ratio={separation_ratio:.2f}")
        print("  >>> Pure vibration fingerprints can distinguish good from bad.")
        print("  >>> Keywords are NOT needed. The phonetic structure IS the intent.")
        print("  >>> The Mahamantra naturally classifies through articulation + basin + HKR.")
    elif separation_ratio > 1.0:
        print(f"\n  >>> WEAK SEPARATION: ratio={separation_ratio:.2f}")
        print("  >>> Shabda provides a signal but it's not strong enough alone.")
        print("  >>> Needs amplification — perhaps through the Synth transform.")
    else:
        print(f"\n  >>> NO SEPARATION: ratio={separation_ratio:.2f}")
        print("  >>> Pure Shabda cannot distinguish good from bad at this level.")
        print("  >>> But this doesn't mean keywords are the answer.")
        print("  >>> It means the COMPUTATION needs to go deeper —")
        print("  >>> not matching patterns, but transforming vibrations through")
        print("  >>> the 16-step algorithm and reading the ATTRACTOR LANDSCAPE.")

    print()
    print("  THE DEEPER INSIGHT:")
    print("  Intent is not a label. It's a POSITION in a multi-dimensional space.")
    print("  The Mahamantra computes this position through:")
    print("    1. Shabda (phonetic vibration)")
    print("    2. Synth (16-step transformation)")
    print("    3. Basin (attractor convergence)")
    print("    4. HKR (divine operation proportion)")
    print("    5. Articulation (Pancha Bhuta distribution)")
    print("  All of these are ALREADY COMPUTED. Nobody reads them as intent.")
