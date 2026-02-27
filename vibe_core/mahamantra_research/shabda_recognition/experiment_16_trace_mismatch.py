"""
EXPERIMENT 16: Trace the EXACT mismatch between audio path and dict path
=========================================================================

For each ARPAbet phoneme, show:
  - What RAMA coord the dict gives (ARPABET_TO_RAMA)
  - What element/sound_class/sub that coord has
  - What element the audio would give (based on varga from centroid)
  - Whether the audio path CAN reach that coord

If the audio path CAN'T reach the right coord, find WHY.
"""
import sys; sys.path.insert(0, ".")

from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import (
    ARPABET_TO_RAMA, ARPABET_TO_VARGA, VargaIndex,
)
from vibe_core.mahamantra.substrate.encoding.pancha_walk import (
    COORD_ELEMENT, COORD_VARGA, COORD_SUB,
)
from vibe_core.mahamantra.sound.shabda_processor import (
    _ELEMENT_VARGA_TO_COORDS, _REPRESENTATIVE,
)
from vibe_core.mahamantra.sound.shabda_intake import ShabdaIntake, unpack_frame
from vibe_core.mahamantra.sound.shabda_processor import (
    frame_to_rama, _classify_sound, _audio_to_sthana, _refine_sub_index,
    stream_to_rama,
)
from vibe_core.mahamantra.sound.shabda_decoder import (
    segment_stream, _dedup_coords, _stable_coords, get_pronunciation_dict,
    ARPABET_TO_RAMA as DECODER_A2R,
)

VARGA_NAMES = ["KANTH", "TALAV", "MURDH", "DANTY", "OSHTH"]
SOUND_CLASS_NAMES = ["SVARA", "SPARS", "SHESH"]

# Part 1: For each ARPAbet phoneme, what coord does dict give and what element is it?
print("=" * 80)
print("ARPABET → RAMA coord → (element, varga_class, sub)")
print("=" * 80)

for arpabet, rama in sorted(ARPABET_TO_RAMA.items(), key=lambda x: x[1]):
    elem = COORD_ELEMENT[rama]
    vc = COORD_VARGA[rama]
    sub = COORD_SUB[rama]
    varga_from_bridge = ARPABET_TO_VARGA.get(arpabet, None)
    varga_val = int(varga_from_bridge) if varga_from_bridge is not None else -1
    
    # Can audio reach this? audio sets element=varga (from centroid)
    # So audio element must equal COORD_ELEMENT of the target coord
    # And sound_class must match COORD_VARGA (0=svara, 1=sparsha, 2=shesha)
    # And sub must match COORD_SUB
    
    # Check if the audio varga (from ARPABET_TO_VARGA) matches the coord element
    match = "✓" if varga_val == elem else "✗"
    
    print(f"  {arpabet:4s} → coord={rama:2d}  elem={VARGA_NAMES[elem]}({elem})  "
          f"vc={SOUND_CLASS_NAMES[vc]}({vc})  sub={sub}  "
          f"bridge_varga={varga_val}  {match}")


# Part 2: For the audio file, trace what frame_to_rama actually does
print()
print("=" * 80)
print("AUDIO TRACE: First segment frame-by-frame")
print("=" * 80)

intake = ShabdaIntake()
stream = intake.process_file("temp/prabhupada-talk.wav")
segments = segment_stream(stream.frames)

pdict = get_pronunciation_dict()
pdict._ensure_loaded()

# Expected: "eh not exactly but i came to preach the gospel..."
# Let's look at segment 3 which should be "but" (970-1110ms)
for seg_idx in [0, 1, 2, 3, 4]:
    seg = segments[seg_idx]
    ms_s = seg.start * 10
    ms_e = seg.end * 10
    
    print(f"\n--- Segment {seg_idx}: [{ms_s}-{ms_e}ms] ---")
    
    # Show first 10 frames
    prev = 0
    for fi, frame in enumerate(seg.frames[:15]):
        rms, varga, f0_x10, cent = unpack_frame(frame)
        if rms < 20:
            prev = frame
            continue
        
        prev_rms, _, prev_f0, prev_cent = unpack_frame(prev) if prev else (0, 0, 0, 0)
        sc = _classify_sound(rms, f0_x10, cent, prev_rms, prev_f0, prev_cent)
        sub = _refine_sub_index(sc, rms, f0_x10, cent, varga)
        rama = frame_to_rama(frame, prev)
        
        sc_name = SOUND_CLASS_NAMES[sc] if sc >= 0 else "SIL"
        elem = COORD_ELEMENT[rama] if rama >= 0 else -1
        
        print(f"  f{fi:2d}: rms={rms:3d} varga={varga} f0={f0_x10:4d} cent={cent:3d} "
              f"→ sc={sc_name}({sc}) sub={sub} → rama={rama:2d} "
              f"(elem={VARGA_NAMES[elem] if elem >= 0 else 'SIL'})")
        prev = frame
    
    # Deduped coords
    raw = stream_to_rama(seg.frames)
    stable = _stable_coords(raw, min_run=2)
    deduped = _dedup_coords(raw)
    print(f"  raw({len(raw)}): {raw[:12]}")
    print(f"  stable:     {stable[:8]}")
    print(f"  deduped:    {deduped[:8]}")

# Part 3: Compare with dict coords for expected words
print()
print("=" * 80)
print("DICT vs AUDIO coords for expected words")
print("=" * 80)

EXPECTED_MAP = {
    0: "eh", 1: "not", 2: "exactly", 3: "but", 4: "i",
    5: "came", 6: "to", 7: "preach",
}

for seg_idx, expected_word in EXPECTED_MAP.items():
    if seg_idx >= len(segments):
        break
    seg = segments[seg_idx]
    ms_s = seg.start * 10
    ms_e = seg.end * 10
    
    raw = stream_to_rama(seg.frames)
    audio_dedup = _dedup_coords(raw)
    
    dict_coords = pdict.lookup(expected_word)
    
    audio_elems = [COORD_ELEMENT[c] for c in audio_dedup] if audio_dedup else []
    dict_elems = [COORD_ELEMENT[c] for c in dict_coords] if dict_coords else []
    
    elem_match = sum(1 for a, d in zip(audio_elems, dict_elems) if a == d)
    total = max(len(audio_elems), len(dict_elems), 1)
    
    print(f"  '{expected_word:12s}' [{ms_s:4d}-{ms_e:4d}ms]")
    print(f"    audio: {str(audio_dedup[:10]):50s} elems={audio_elems[:8]}")
    print(f"    dict:  {str(dict_coords):50s} elems={dict_elems[:8]}")
    print(f"    element overlap: {elem_match}/{total}")
