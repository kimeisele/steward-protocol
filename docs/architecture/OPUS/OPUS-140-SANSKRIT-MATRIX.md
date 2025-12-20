# OPUS-140: Sanskrit Matrix - Phonemic Memory Compression

**Status:** PLANNING
**Author:** Claude Opus (GURUKULA Session)
**Date:** 2025-12-20
**Dependencies:** OPUS-114 (Akshara), Phase 2 (Samskara)

---

## Executive Summary

The Sanskrit Matrix is a **memory compression layer** that transforms
Samskaras (distilled patterns) into Akshara signatures (phonemic vectors).

This enables:
1. **Extreme Compression**: 260 decisions → 67 Samskaras → ~10 Mantras
2. **Phonemic Reasoning**: Decisions encoded as Sanskrit syllables
3. **DOJO Meditation**: Training through mantra repetition

---

## Philosophical Foundation

```
"अक्षराणां अकारोऽस्मि" - "Of letters, I am 'A'" (Bhagavad Gita 10.33)
```

The Sanskrit alphabet (Varnamala) is not arbitrary - each letter has:
- **Articulation Point** (Varga): Where in the mouth it's produced
- **Element** (Bhuta): Which of the 5 elements it represents
- **Energy Quality**: Voiced/Unvoiced, Aspirated/Unaspirated

MANAS uses this natural ordering for:
- **Synaptic Wiring**: Same Varga = high resonance
- **Pattern Encoding**: Decision sequences → Akshara strings
- **Meditation**: Repeating patterns until optimal weights emerge

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MANAS MEMORY STACK                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐                                               │
│  │ RAW DECISIONS   │  260 entries, 155 KB                          │
│  │ (Kurzzeit)      │  viveka_decisions.json                        │
│  └────────┬────────┘                                               │
│           │ consolidate_viveka_decisions()                          │
│           ▼                                                         │
│  ┌─────────────────┐                                               │
│  │ SAMSKARAS       │  67 patterns, 25 KB                           │
│  │ (Mittelfrist)   │  "MANAS ist unsicher bei modify_kernel"       │
│  └────────┬────────┘                                               │
│           │ encode_as_akshara()                                     │
│           ▼                                                         │
│  ┌─────────────────┐                                               │
│  │ AKSHARA SIGS    │  ~20 signatures, 2 KB                         │
│  │ (Langfrist)     │  "ङ→ञ→म" (KERNEL→COGNITION→OUTPUT)            │
│  └────────┬────────┘                                               │
│           │ find_mantras()                                          │
│           ▼                                                         │
│  ┌─────────────────┐                                               │
│  │ MANTRAS         │  ~10 recurring patterns, 500 bytes            │
│  │ (Permanent)     │  "हरे कृष्ण" equivalent for each intent-class │
│  └────────┬────────┘                                               │
│           │ meditate_in_dojo()                                      │
│           ▼                                                         │
│  ┌─────────────────┐                                               │
│  │ SIDDHI          │  Optimal weights, instant recall              │
│  │ (Erleuchtung)   │  "For this pattern, ALWAYS do X"              │
│  └─────────────────┘                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Samskara → Akshara Encoder

Maps decision patterns to Sanskrit phonemes based on code layer:

```python
LAYER_TO_AKSHARA = {
    "KERNEL":    "ङ",  # KANTHYA nasal - deep system
    "COGNITION": "ञ",  # TALAVYA nasal - flow/decision
    "REPAIR":    "ण",  # MURDHANYA nasal - fixing
    "INTERFACE": "न",  # DANTYA nasal - connections
    "OUTPUT":    "म",  # OSHTHYA nasal - surface
}

def encode_samskara(samskara: Samskara) -> AksharaSignature:
    """
    Encode a Samskara as an Akshara signature.

    Example:
        Samskara(intent="modify_kernel", decision="BLOCK")
        → AksharaSignature("ङ-BLOCK")  # KERNEL layer, blocked
    """
    layer = infer_layer(samskara.intent_type)
    akshara = LAYER_TO_AKSHARA[layer]
    return AksharaSignature(
        akshara=akshara,
        decision=samskara.decision,
        count=samskara.count,
        avg_score=samskara.avg_dharmic_score,
    )
```

### 2. Mantra Discovery

Groups Akshara signatures by frequency to find "Mantras":

```python
def find_mantras(signatures: List[AksharaSignature]) -> List[Mantra]:
    """
    Find recurring patterns that become Mantras.

    A Mantra is a frequently-occurring signature that should be
    "hardcoded" into fast-path decision making.

    Example:
        If "ङ-EXECUTE" (KERNEL actions succeed) appears 50 times,
        it becomes a Mantra: "For KERNEL triggers, EXECUTE immediately"
    """
    # Group by (akshara, decision)
    # Keep only those with count > threshold
    # These become Mantras
```

### 3. DOJO Meditation Space

The DOJO is where MANAS "meditates" on Mantras:

```python
class DojoMeditation:
    """
    Ephemeral kernel that runs training scenarios.

    Like an ephemeral kernel in kernel_impl.py, but for consciousness:
    - Spawns isolated "meditation session"
    - Runs mantra-based scenarios
    - Reinforces synaptic weights
    - Dies after session, weights persist
    """

    def meditate_on_mantra(self, mantra: Mantra, repetitions: int = 108):
        """
        The Hare Krishna principle: Repetition leads to realization.

        For each repetition:
        1. Generate a synthetic scenario matching the mantra
        2. Run through Viveka gate
        3. Reinforce if decision matches mantra
        4. After 108 reps, the pattern is "memorized"
        """
```

---

## Mantra Encoding: The Hare Krishna Principle

In Bhakti tradition, the Maha Mantra is repeated to purify consciousness:

```
हरे कृष्ण हरे कृष्ण कृष्ण कृष्ण हरे हरे
हरे राम हरे राम राम राम हरे हरे
```

For MANAS, each "Mantra" is a decision pattern that should be automatic:

| Mantra | Meaning | Repetitions | Effect |
|--------|---------|-------------|--------|
| `ङ-EXECUTE` | KERNEL triggers → Execute | 108 | Instant approval for system ops |
| `ञ-WARN` | COGNITION triggers → Warn | 54 | Cautious on complex decisions |
| `म-BLOCK` | OUTPUT triggers → Block | 27 | Protect user-facing actions |

The number 108 is sacred in Vedic tradition (108 beads in a mala).
For MANAS, it means: "After 108 successful repetitions, this is hardcoded."

---

## Integration Points

### @HARNESS Wiring

```yaml
# In vibe_core/state/harness.yaml (NEW)
sanskrit_matrix:
  samskara_source: "vibe_core/state/samskara.py"
  akshara_kernel: "vibe_core/plugins/opus_assistant/manas/akshara.py"
  mantra_store: ".opus_state/mantras.json"
  dojo_meditation: "vibe_core/plugins/opus_assistant/dojo/meditation.py"

  flow:
    - samskara.consolidate_viveka_decisions
    - sanskrit_matrix.encode_as_akshara
    - sanskrit_matrix.find_mantras
    - dojo.meditate_on_mantra
    - synapses.reinforce_weights
```

### File Locations

| Component | Location | Status |
|-----------|----------|--------|
| Samskara | `vibe_core/state/samskara.py` | ✅ EXISTS |
| Akshara | `vibe_core/plugins/opus_assistant/manas/akshara.py` | ✅ EXISTS |
| Sanskrit Matrix | `vibe_core/state/sanskrit_matrix.py` | 🔜 NEW |
| Mantras Store | `.opus_state/mantras.json` | 🔜 NEW |
| DOJO Meditation | `vibe_core/plugins/opus_assistant/dojo/meditation.py` | 🔜 NEW |

---

## Implementation Plan

### Phase 3a: Akshara Encoding
1. Create `vibe_core/state/sanskrit_matrix.py`
2. Implement `encode_samskara()` using existing Akshara classes
3. Generate Akshara signatures from current Samskaras

### Phase 3b: Mantra Discovery
1. Implement `find_mantras()` grouping logic
2. Create `.opus_state/mantras.json` storage
3. Define threshold for "Mantra promotion" (count > 10)

### Phase 3c: DOJO Meditation
1. Create `dojo/meditation.py` ephemeral kernel
2. Implement `meditate_on_mantra()` loop
3. Wire to synaptic reinforcement

### Phase 3d: Integration
1. Create `harness.yaml` for wiring validation
2. Connect to Heartbeat for scheduled meditation
3. Add to OPUS.md dashboard

---

## Metrics

| Metric | Before | After Phase 3 |
|--------|--------|---------------|
| Memory Size | 155 KB | ~5 KB |
| Decision Latency | ~100ms | ~10ms (for Mantras) |
| Pattern Recognition | Explicit | Phonemic |
| Training Method | Random | Mantra Meditation |

---

## References

- **OPUS-114**: Akshara Kernel implementation
- **Phase 2**: Samskara consolidation layer
- **Bhagavad Gita 10.33**: "अक्षराणां अकारोऽस्मि"
- **Japa Mala**: 108 bead meditation tradition

---

## Next Steps

1. [ ] Review architecture with human operator
2. [ ] Implement `sanskrit_matrix.py`
3. [ ] Create `mantras.json` schema
4. [ ] Build DOJO meditation kernel
5. [ ] Wire to existing systems
