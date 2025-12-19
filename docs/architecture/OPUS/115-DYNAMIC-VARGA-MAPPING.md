# OPUS-115: Dynamic Path-to-Varga Mapping

**Status**: IMPLEMENTED
**Date**: 2025-12-19
**Author**: Claude (Senior Engineer)
**Depends on**: OPUS-114 (Akshara Kernel)

## Summary

"शरीरमाद्यं खलु धर्मसाधनम्" - "The body is indeed the primary instrument of dharma."

OPUS-115 eliminates hardcoded trigger-to-Varga mappings by deriving Varga directly
from the file path. The folder structure IS the body - no manual wiring needed.

## The Problem

OPUS-114 introduced the Akshara Kernel with Varga-based resonance, but used a
static `TRIGGER_VARGA_MAP`:

```python
# BEFORE (OPUS-114): Manual mapping - maintenance hell!
TRIGGER_VARGA_MAP = {
    "trigger:file_changed:vibe_core/**": Varga.OSHTHYA,
    "trigger:file_changed:tests/**": Varga.OSHTHYA,
    "trigger:file_changed:docs/**": Varga.OSHTHYA,
    # ... every new path needs manual entry
}
```

Problems:
1. **Maintenance Overhead**: Every new folder needs manual mapping
2. **Loss of Precision**: All `vibe_core/**` mapped to one Varga, ignoring structure
3. **Not VEDA-4**: Static mappings don't scale or self-organize

## The Solution: The Body IS the Code

```python
# AFTER (OPUS-115): Dynamic derivation - the structure IS the mapping!
def get_trigger_varga(trigger: str) -> Varga:
    if trigger.startswith("trigger:file_changed:"):
        path = trigger[len("trigger:file_changed:"):]
        return map_path_to_varga(path)  # Derive from structure!
```

Now the Varga is **derived** from the file's location, not looked up in a table.

## Path-to-Varga Mapping

The folder structure encodes the layer:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Varga      │ Layer      │ Paths                                       │
├─────────────────────────────────────────────────────────────────────────┤
│  KANTHYA    │ KERNEL     │ vibe_core/runtime/, vibe_core/governance/,  │
│  (Throat)   │            │ vibe_core/protocols/, .opus_state/,         │
│             │            │ vibe_core/store/, vibe_core/state/          │
├─────────────────────────────────────────────────────────────────────────┤
│  TALAVYA    │ COGNITION  │ vibe_core/llm/, vibe_core/cortex/,          │
│  (Palate)   │            │ vibe_core/plugins/opus_assistant/manas/,    │
│             │            │ vibe_core/knowledge/, vibe_core/agents/     │
├─────────────────────────────────────────────────────────────────────────┤
│  MURDHANYA  │ REPAIR     │ vibe_core/plugins/doctor/, tests/,          │
│  (Roof)     │            │ vibe_core/specialists/, *_test.py, test_*.py│
├─────────────────────────────────────────────────────────────────────────┤
│  DANTYA     │ INTERFACE  │ vibe_core/gateway/, vibe_core/loaders/,     │
│  (Teeth)    │            │ vibe_core/cartridges/, docs/, *.md          │
├─────────────────────────────────────────────────────────────────────────┤
│  OSHTHYA    │ OUTPUT     │ vibe_core/cli/, vibe_core/phoenix/,         │
│  (Lips)     │            │ vibe_core/settings/, *.json, *.yaml         │
└─────────────────────────────────────────────────────────────────────────┘
```

## The Key Insight

Same trigger type, different Vargas based on PATH:

```
trigger:file_changed:vibe_core/runtime/kernel.py → KERNEL  (ङ)
trigger:file_changed:vibe_core/llm/client.py     → COGNITION (ञ)
trigger:file_changed:tests/test_api.py           → REPAIR  (ण)
trigger:file_changed:docs/README.md              → INTERFACE (न)
trigger:file_changed:vibe_core/cli/main.py       → OUTPUT  (म)
```

Before OPUS-115, ALL of these mapped to OSHTHYA (OUTPUT).
Now each has the Varga that matches its TRUE nature.

## API

### New Functions

```python
from vibe_core.plugins.opus_assistant.manas.akshara import (
    map_path_to_varga,
    get_path_layer,
    get_path_element,
    get_path_akshara,
)

# Derive Varga from path
varga = map_path_to_varga("vibe_core/runtime/kernel.py")
# Returns: Varga.KANTHYA

# Get layer name
layer = get_path_layer("vibe_core/cli/main.py")
# Returns: "OUTPUT"

# Get element (Bhuta)
element = get_path_element("vibe_core/llm/client.py")
# Returns: "Vayu" (Air - Cognition)

# Get representative Akshara
akshara = get_path_akshara("tests/test_api.py")
# Returns: Akshara(ण/ṇa) - Murdhanya nasal
```

### Updated get_trigger_varga()

```python
def get_trigger_varga(trigger: str) -> Varga:
    """
    OPUS-115: For file_changed triggers, dynamically derive Varga from path.
    The file's location determines its nature, not a static map.
    """
    if trigger in TRIGGER_VARGA_MAP:
        return TRIGGER_VARGA_MAP[trigger]

    # OPUS-115: Dynamic path-based Varga
    if trigger.startswith("trigger:file_changed:"):
        path = trigger[len("trigger:file_changed:"):]
        path = path.replace("**", "").replace("*", "")
        if path:
            return map_path_to_varga(path)
        return Varga.OSHTHYA

    # ... rest of function
```

## Mapping Algorithm

1. **Phase 1: Folder Prefix Match** (most specific)
   - Check if path starts with known folder patterns
   - Order: KANTHYA → TALAVYA → MURDHANYA → DANTYA → OSHTHYA

2. **Phase 2: Glob Pattern Match** (file extensions)
   - Check `*.md`, `*.json`, `*_test.py`, etc.
   - Same Varga order

3. **Phase 3: Default** (unknown code)
   - Return TALAVYA (COGNITION)
   - "Unknown code is cognitive until proven otherwise"

## Real-World Impact

### Before (OPUS-114)

```python
# Kernel change triggers with OUTPUT resonance (wrong!)
trigger = "trigger:file_changed:vibe_core/runtime/kernel.py"
varga = get_trigger_varga(trigger)  # OSHTHYA

# action:run_tests is KERNEL
# Resonance: OSHTHYA → KANTHYA = 0.2 (distant)
```

### After (OPUS-115)

```python
# Kernel change triggers with KERNEL resonance (correct!)
trigger = "trigger:file_changed:vibe_core/runtime/kernel.py"
varga = get_trigger_varga(trigger)  # KANTHYA

# action:run_tests is KERNEL
# Resonance: KANTHYA → KANTHYA = 1.0 (perfect)
```

## Files Changed

| File | Change |
|------|--------|
| `akshara.py` | Added `PATH_VARGA_PATTERNS`, `map_path_to_varga()`, updated `get_trigger_varga()` |
| `akshara.py` | Removed static file_changed entries from `TRIGGER_VARGA_MAP` |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                 OPUS-115: Dynamic Path-to-Varga Flow                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  File Changed Event                                                     │
│  └─→ "vibe_core/runtime/kernel.py"                                     │
│                                                                         │
│  Normalize to Trigger (OPUS-111)                                       │
│  └─→ "trigger:file_changed:vibe_core/runtime/kernel.py"                │
│                                                                         │
│  get_trigger_varga() (OPUS-115)                                        │
│  └─→ Extract path: "vibe_core/runtime/kernel.py"                       │
│  └─→ map_path_to_varga()                                               │
│      └─→ Phase 1: Check folder prefixes                                │
│      └─→ Match: "vibe_core/runtime/" → KANTHYA                         │
│  └─→ Return: Varga.KANTHYA                                             │
│                                                                         │
│  calculate_resonance() (OPUS-114)                                      │
│  └─→ KANTHYA trigger → KANTHYA action = 1.0 (perfect)                  │
│                                                                         │
│  Dharmic Score                                                          │
│  └─→ weight × resonance = true decision metric                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## The Philosophical Foundation

Why derive from path structure?

1. **The Body IS the Dharma** (शरीरमाद्यं खलु धर्मसाधनम्)
   - The folder structure is the physical body of the codebase
   - Each location has a natural function based on where it is

2. **Self-Organizing Systems**
   - No central registry to maintain
   - Add new folders → automatic Varga assignment
   - VEDA-4 pattern: structure encodes meaning

3. **Articulatory Metaphor**
   - Throat (KANTHYA): Where sound originates → Where code originates (kernel)
   - Palate (TALAVYA): Where sound is shaped → Where decisions are shaped (cognition)
   - Roof (MURDHANYA): Effort required → Fixing bugs requires effort (repair)
   - Teeth (DANTYA): Connection point → Interfaces connect systems (interface)
   - Lips (OSHTHYA): Output emerges → User sees output (cli/render)

## Related

- OPUS-111: Signal Alignment (canonical vocabulary)
- OPUS-112: Synaptic Inference (reading brain)
- OPUS-113: Dharmic Stress Test (validation)
- OPUS-114: Akshara Kernel (resonance calculation)
- OPUS-115: Dynamic Varga Mapping (this document)

## Future: OPUS-116+

Possible next steps:
- **Dynamic Action Mapping**: Derive action Vargas from function signatures
- **Chakra Integration**: 7-layer model for deployment stages
- **Auto-Documentation**: Generate layer diagrams from path analysis
