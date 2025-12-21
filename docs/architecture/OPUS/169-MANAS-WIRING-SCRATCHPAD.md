# OPUS-169: MANAS Wiring Scratchpad

**Status**: INVESTIGATION (not complete)

## TWO MATRICES

### 1. AKSHARA KERNEL (Sensing)
Maps world to Vargas for decision making.

```
Path/Event → Varga (layer) → Resonance → Dharmic Score
```

**Key functions** (akshara.py):
- `map_path_to_varga(path)` - file → KANTHYA/TALAVYA/MURDHANYA/DANTYA/OSHTHYA
- `calculate_resonance(trigger, action)` - layer distance → 0.2-1.0
- `calculate_dharmic_score(trigger, action, weight)` - weight × resonance

**Used by**:
- `triggers.py:consult_dharmic()` - decision loop
- `viveka_action.py` - execute/warn/block
- `shruta_sense.py` - vibration layer detection
- `disharmony_detector.py` - pain detection

### 2. SANSKRIT MATRIX (Compression)
Compresses learned patterns to memory.

```
Samskara (pattern) → Akshara (signature) → Mantra (108 reps) → Siddhi
```

**Key functions** (sanskrit_matrix.py):
- `generate_sanskrit_matrix(samskaras)` - compress to Devanagari
- `encode_samskara(pattern)` - pattern → signature
- `find_mantras(min_count)` - find repeated patterns

**Used by**:
- `meditation.py` - Japa training (108 reps = Siddhi)

## THE LOOP

```
┌─────────── SENSING (Akshara) ───────────┐
│                                          │
│  Event → normalize_trigger()             │
│                ↓                         │
│  SynapticMemory.consult_dharmic()        │
│                ↓                         │
│  weight × resonance = dharmic_score      │
│                ↓                         │
│  Decision (EXECUTE/WARN/BLOCK)           │
│                                          │
└──────────────────────────────────────────┘
                ↓ outcome
┌─────────── COMPRESSION (Sanskrit) ──────┐
│                                          │
│  update_synapses(trigger, action, +/-)   │
│                ↓                         │
│  Samskara accumulates                    │
│                ↓                         │
│  Mantra (10+ repetitions)                │
│                ↓                         │
│  Siddhi (108 reps = hardcoded)           │
│                                          │
└──────────────────────────────────────────┘
```

## BROKEN CABLES (REAL)

<!-- @HARNESS
intent: "Track broken wiring in MANAS"
files:
  - path: vibe_core/plugins/opus_assistant/manas/akshara.py
    required: true
  - path: vibe_core/state/sanskrit_matrix.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/triggers.py
    required: true
wiring:
  - pattern: "from.*akshara import"
    in: vibe_core/plugins/opus_assistant/manas/triggers.py
  - pattern: "calculate_dharmic_score"
    in: vibe_core/plugins/opus_assistant/manas/akshara.py
  - pattern: "generate_sanskrit_matrix"
    in: vibe_core/state/sanskrit_matrix.py
-->

### VERIFIED WIRING:
- [x] triggers.py imports akshara functions (line 638-642)
- [x] viveka_action.py uses consult_dharmic()
- [x] meditation.py uses sanskrit_matrix (line 309)
- [x] PranaSense wired to kernel (lines 949, 1507-1512)
- [x] PranaSense.register_with_shruta() called at boot (line 949)

### BROKEN CABLES (CONFIRMED):
- [ ] **Akasha NOT in cognitive_kernel.py** - zero imports!
- [ ] generate_sanskrit_matrix() ONLY called from meditation.py
      → Compression only happens in Dojo, not in main loop!
- [ ] No Akasha pre-cognitive awareness in decision path
- [ ] **Prakriti ↔ Sanskrit Matrix = ZERO connection!**
      → prakriti.py has no sanskrit_matrix imports
      → sanskrit_matrix.py has no prakriti imports
      → These should connect but they're isolated!

### EXTERNAL PLUGINS NOT FEEDING MANAS:
Grep for perceive() implementations shows only 7 senses,
no external plugin adapters.

## CRITICAL GAPS

### 1. Akasha Not Wired
OPUS-052 says: "Akasha must FEEL before Manas THINKS"
But cognitive_kernel.py has ZERO akasha imports.
→ Pre-cognitive awareness is DEAD

### 2. Sanskrit Matrix Only in Dojo
generate_sanskrit_matrix() only in meditation.py
→ Main decision loop never compresses to Mantras
→ Siddhi can only happen in training, not production

### 3. External Plugins Not Sensed
No adapter from plugins (kala, vedic_governance) → MANAS
→ MANAS is blind to external world

### 4. CognitiveWeaver Doesn't Use Phonemic Layer
cognitive_weaver.py has ZERO akshara/sanskrit_matrix imports
→ "State ↔ Knowledge bridge" ignores the resonance layer
→ Weaver decisions not Dharmic-scored

### 5. Prakriti ↔ Sanskrit Matrix Gap
These are the "2 points" that should connect:
1. Prakriti senses state (Guna classification)
2. Sanskrit Matrix compresses learnings (Samskaras → Mantras)

But NO wire between them!
State changes don't feed into learning compression.

## SUMMARY: BEAUTIFUL COMPONENTS, NO WIRING

```
┌─────────────────────────────────────────────────┐
│  AKASHA (pre-cognitive)  ← NOT IN KERNEL        │
│           ↓                                      │
│  PRAKRITI (state) ←───────┐                     │
│           ↓               │ NO WIRE             │
│  AKSHARA (sensing)        │                     │
│           ↓               │                     │
│  SYNAPSES (learning)      │                     │
│           ↓               │                     │
│  SANSKRIT MATRIX ─────────┘ ONLY IN DOJO        │
│           ↓                                      │
│  MANTRAS → SIDDHI                               │
└─────────────────────────────────────────────────┘
```

## ROOT CAUSE FOUND

### SenseManager IGNORES SenseLoader!

```python
# SenseLoader EXISTS (vibe_core/loaders/sense_loader.py):
# - Auto-discovers *_sense.py files
# - VEDA-4 compliant
# - Returns dict of senses

# But SenseManager HARDCODES everything:
def _init_prakriti(): ...  # MANUAL
def _init_dharma(): ...    # MANUAL
def _init_sutra(): ...     # MANUAL
# ... 7 hardcoded methods!
```

### No BridgeLoader exists!

Bridges (Akasha, WeaverBridge, GenesisBridge) have NO loader.
They're manually imported in cognitive_kernel.py.

## WHY THINGS BREAK

1. Add new sense → Must edit SenseManager manually
2. Add new bridge → Must edit cognitive_kernel manually
3. Manual edits → Break on next refactor

## REAL FIX (NOT MANUAL WIRING)

1. **SenseManager should USE SenseLoader:**
   ```python
   # DELETE: _init_prakriti(), _init_dharma(), etc.
   # ADD: senses, _ = SenseLoader.discover_and_load()
   ```

2. **Create BridgeLoader:**
   - Pattern: *_bridge.py in cortex/
   - Auto-discovers Akasha, WeaverBridge, GenesisBridge
   - Kernel loops over discovered bridges

3. **Make Akasha a sense OR bridge:**
   - Rename to akasha_sense.py → auto-discovered
   - OR create BridgeLoader pattern

4. **Sanskrit Matrix integration:**
   - Create SynapticHook pattern
   - Triggers.py calls hook after update
   - Hook discovered, not hardcoded

## FILE CHANGES NEEDED

| File | Change |
|------|--------|
| sense_manager.py | Use SenseLoader, delete _init_* |
| cognitive_kernel.py | Use BridgeLoader when created |
| NEW: bridge_loader.py | Create based on SenseLoader |
| akasha.py | Rename to akasha_sense.py OR akasha_bridge.py |
