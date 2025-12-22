# OPUS-176: Biorhythm Extraction

<!-- @HARNESS
intent: "Extract biorhythm tick logic from cognitive_kernel.py into dedicated module"
files:
  - path: vibe_core/plugins/opus_assistant/manas/biorhythm.py
    required: true
    rationale: "New module containing BiorhythmProcessor class"
  - path: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    required: true
    rationale: "Reduced from 2570 to 2332 lines, delegates tick() to BiorhythmProcessor"
tests:
  - tests/reactor/test_kernel_manifestation.py
  - tests/reactor/test_fragility.py
  - tests/integration/test_manas_oracle_heartbeat.py
wiring:
  - pattern: "from .biorhythm import BiorhythmProcessor"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
  - pattern: "self._biorhythm = BiorhythmProcessor"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
  - pattern: "return self._biorhythm.tick\\(\\)"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
-->

## STATUS: COMPLETED

## Summary

Extracted biorhythm tick logic from `cognitive_kernel.py` (2570 lines → 2332 lines)
into dedicated `biorhythm.py` module (303 lines).

## What Changed

### New Module: `biorhythm.py`

- `BiorhythmState` dataclass - holds tick state
- `BiorhythmProcessor` class with:
  - `tick()` - main biorhythm loop
  - `_compute_consciousness_level()` - weighted inputs
  - `_tamas_tick()`, `_rajas_tick()`, `_sattva_tick()`, `_turiya_tick()` - guna states
  - `_persist_awareness()` - state persistence
  - `get_awareness()` - dashboard access

### CognitiveKernel Changes

- `tick()` now delegates to `self._biorhythm.tick()`
- `get_awareness()` now delegates to `self._biorhythm.get_awareness()`
- Removed ~250 lines of inline biorhythm logic

## Test Results

```
40 passed in 10.89s
```

All reactor and MANAS integration tests pass.
