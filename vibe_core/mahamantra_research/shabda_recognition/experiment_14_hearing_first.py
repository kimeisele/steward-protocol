"""
EXPERIMENT 14: HEARING FIRST — Let sound hit the Antaranga membrane
=====================================================================

The missing step: we try to CLASSIFY before we HEAR.

Current: audio frame → score_frame() → phoneme → word
Should:  audio frame → HIT RESONANCE GRID → imprint forms → READ imprint

The Antaranga IS the drum membrane:
  - 512 slots × 32 bytes = 16KB contiguous RAM
  - Collision: same slot → prana ADDS (resonance builds up)
  - Shabda salt: acoustic features modulate how the membrane responds
  - integrity = membrane health (how well it received the sound)

Concept: Each audio frame "drops" onto the Antaranga.
  - WHICH SLOT it hits = determined by audio features
  - HOW HARD = prana from RMS
  - WHAT KIND = operation from varga/voicing
  - Over time, the prana pattern across 512 slots IS the imprint

Then we READ the imprint pattern and match it against known word imprints.

Also: measure the dialect gap (what coords does audio produce vs dict).
"""
import sys; sys.path.insert(0, ".")

from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake, unpack_frame
from vibe_core.mahamantra.sound.shabda_processor import stream_to_rama
from vibe_core.mahamantra.sound.shabda_decoder import (
    segment_stream, _dedup_coords, _stable_coords, get_pronunciation_dict,
)
from vibe_core.mahamantra.substrate.cell_system.antaranga import (
    AntarangaRegistry, ANTARANGA_SLOTS,
)
from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth

synth = MahaModularSynth(default_preset="quantum")

# Load audio
intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)

pdict = get_pronunciation_dict()
pdict._ensure_loaded()

EXPECTED_WORDS = [
    "eh", "not", "exactly", "but", "i", "came", "to", "preach",
    "the", "gospel", "of", "krishna", "consciousness", "and",
    "fortunately", "i", "met", "some", "enthusiastic", "young",
    "boys", "and", "girls",
]

print(f"Segments: {len(segments)}, Expected words: {len(EXPECTED_WORDS)}")

# === Part 1: Dialect gap — audio coords vs dict coords ===
print()
print("=" * 70)
print("PART 1: DIALECT GAP — How far are audio coords from dict coords?")
print("=" * 70)

from vibe_core.mahamantra.substrate.encoding.pancha_walk import COORD_ELEMENT

ELEM_NAMES = ["S", "J", "A", "V", "K"]  # short names

for word in ["exactly", "came", "preach", "gospel", "krishna", "consciousness", "boys", "girls", "the", "and"]:
    dict_coords = pdict.lookup(word)
    if dict_coords:
        dict_elems = "".join(ELEM_NAMES[COORD_ELEMENT[c]] for c in dict_coords)
        print(f"  '{word:15s}' dict_coords={str(dict_coords):40s} elems={dict_elems}")

print()
print("  First 5 segments → audio coords + elements:")
for si, seg in enumerate(segments[:5]):
    ms_s = seg.start * 10
    ms_e = seg.end * 10
    raw = stream_to_rama(seg.frames)
    stable = _stable_coords(raw, min_run=2)
    if not stable:
        stable = _dedup_coords(raw)
    elems = "".join(ELEM_NAMES[COORD_ELEMENT[c]] for c in stable[:10]) if stable else "?"
    print(f"  [{ms_s:5d}-{ms_e:5d}ms] coords={str(stable[:10]):50s} elems={elems}")


# === Part 2: Let audio HIT the Antaranga — imprint formation ===
print()
print("=" * 70)
print("PART 2: HEARING — Audio frames hit the Antaranga membrane")
print("=" * 70)

def audio_to_slot(packed: int) -> int:
    """Map audio frame to Antaranga slot (0-511).
    
    Uses ALL 4 acoustic dimensions to determine WHERE on the membrane
    the sound lands:
        slot = (varga * 100 + centroid_100) % 512
    
    This means: same articulation + same timbre → same slot.
    Different sounds → different slots.
    The collision pattern IS the hearing imprint.
    """
    rms, varga, f0_x10, centroid_100 = unpack_frame(packed)
    # Combine varga (articulation) and centroid (timbre) for slot address
    # Add f0 influence for pitch separation
    f0_contrib = (f0_x10 // 100) & 0x1F  # 0-31 from pitch
    slot = (varga * 103 + centroid_100 * 2 + f0_contrib) % ANTARANGA_SLOTS
    return slot


def make_imprint(frames, segment_idx=0):
    """Let audio frames hit the Antaranga. Return the prana pattern."""
    chamber = AntarangaRegistry()
    
    for packed in frames:
        rms, varga, f0_x10, centroid_100 = unpack_frame(packed)
        if rms < 20:
            continue  # silence doesn't hit the membrane
        
        slot = audio_to_slot(packed)
        
        # Frame hits the membrane:
        # - source = varga (articulation point)
        # - target = centroid_100 (timbre)
        # - operation = f0_x10 (pitch)
        # - prana = rms * rms (energy proportional to amplitude squared)
        # - integrity = 65535 (fresh hit, full integrity)
        chamber.collide(
            slot=slot,
            v_source=varga,
            v_target=centroid_100,
            v_operation=f0_x10,
            v_arcanam=0,
            v_atma=0,
            v_prana=rms * rms,  # energy ∝ amplitude²
            v_integrity=65535,
            v_cycle=0,
        )
    
    # Read the imprint: prana pattern across all slots
    prana_pattern = []
    for i in range(ANTARANGA_SLOTS):
        prana_pattern.append(chamber.prana_at(i))
    
    return prana_pattern, chamber


def imprint_fingerprint(prana_pattern):
    """Reduce 512-slot prana pattern to a compact fingerprint."""
    # Top-K slots by prana (the strongest resonance points)
    indexed = [(p, i) for i, p in enumerate(prana_pattern) if p > 0]
    indexed.sort(reverse=True)
    
    # Return: (active_slots, total_prana, top_5_slots, top_5_pranas)
    active = len(indexed)
    total = sum(p for p, _ in indexed)
    top_5_slots = tuple(i for _, i in indexed[:5])
    top_5_pranas = tuple(p for p, _ in indexed[:5])
    
    return {
        "active": active,
        "total_prana": total,
        "top_5_slots": top_5_slots,
        "top_5_pranas": top_5_pranas,
    }


def compare_imprints(p1, p2):
    """Cosine similarity between two prana patterns (512-dim vectors)."""
    import math
    dot = sum(a * b for a, b in zip(p1, p2))
    na = math.sqrt(sum(a * a for a in p1))
    nb = math.sqrt(sum(b * b for b in p2))
    if na < 1e-10 or nb < 1e-10:
        return 0.0
    return dot / (na * nb)


# Make imprints for audio segments
print("\nAudio segment imprints:")
audio_imprints = []
for si, seg in enumerate(segments[:10]):
    ms_s = seg.start * 10
    ms_e = seg.end * 10
    pattern, _ = make_imprint(seg.frames, si)
    fp = imprint_fingerprint(pattern)
    audio_imprints.append((pattern, fp, ms_s, ms_e))
    print(f"  [{ms_s:5d}-{ms_e:5d}ms] active={fp['active']:3d} total_prana={fp['total_prana']:10d} "
          f"top_slots={fp['top_5_slots']}")


# === Part 3: Make imprints for KNOWN WORDS (from audio of known position) ===
# Since we know the expected transcript, we can generate "reference" imprints
# by feeding known text through ShabdaIntake as synthetic audio.
# But we don't have isolated word audio — so instead, generate reference patterns
# by synthesizing audio features from the pronunciation dict.

print()
print("=" * 70)
print("PART 3: Word imprint from pronunciation coords → synthetic features")
print("=" * 70)

# For each dict word, create a synthetic "what it would sound like" imprint
# by mapping RAMA coords back to approximate audio features.
from vibe_core.mahamantra.substrate.encoding.pancha_walk import COORD_VARGA, COORD_SUB
from vibe_core.mahamantra.sound.shabda_intake import pack_frame

def coords_to_synthetic_frames(coords):
    """Convert RAMA coords to synthetic packed audio frames.
    
    Reverse of stream_to_rama: coords → approximate (rms, varga, f0, centroid).
    """
    frames = []
    for c in coords:
        varga = COORD_VARGA[c]
        sub = COORD_SUB[c]
        
        # Vowels (coords 0-15): high RMS, voiced, centroid by varga
        if c < 16:
            rms = 120
            f0_x10 = 1200  # voiced
            centroid_100 = 40 + varga * 30  # varies by articulation
        # Consonants (16-40): lower RMS, voicing by sub
        elif c < 41:
            rms = 60
            f0_x10 = 1000 if sub >= 2 else 0  # voiced if sub >= 2
            centroid_100 = 30 + varga * 25
        # Sibilants (41-48): medium RMS, high centroid
        else:
            rms = 80
            f0_x10 = 500 if sub == 0 else 0
            centroid_100 = 150 + varga * 20
        
        # Each phoneme = ~8 frames (80ms at 10ms/frame)
        for _ in range(8):
            frames.append(pack_frame(rms, varga, f0_x10, centroid_100))
    
    return frames


word_imprints = {}
for word in ["exactly", "came", "preach", "gospel", "krishna", "consciousness",
             "boys", "girls", "the", "and", "not", "but", "of", "some"]:
    coords = pdict.lookup(word)
    if not coords:
        continue
    syn_frames = coords_to_synthetic_frames(coords)
    pattern, _ = make_imprint(syn_frames)
    fp = imprint_fingerprint(pattern)
    word_imprints[word] = pattern
    print(f"  '{word:15s}' active={fp['active']:3d} total_prana={fp['total_prana']:10d} "
          f"top_slots={fp['top_5_slots']}")


# === Part 4: Match audio imprints to word imprints ===
print()
print("=" * 70)
print("PART 4: Match audio imprints → word imprints (cosine similarity)")
print("=" * 70)

for ai, (pattern, fp, ms_s, ms_e) in enumerate(audio_imprints):
    best_word = ""
    best_sim = -1.0
    for word, word_pattern in word_imprints.items():
        sim = compare_imprints(pattern, word_pattern)
        if sim > best_sim:
            best_sim = sim
            best_word = word
    
    expected = EXPECTED_WORDS[ai] if ai < len(EXPECTED_WORDS) else "?"
    match = "✓" if best_word == expected else " "
    print(f"  [{ms_s:5d}-{ms_e:5d}ms] {best_word:15s} sim={best_sim:.4f} {match}  (expected: {expected})")
