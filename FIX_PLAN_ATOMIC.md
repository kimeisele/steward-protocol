# ATOMIC FIX PLAN - Bombenfest

## STATUS: 4/4 FIXES ERLEDIGT ✓ BOMBENFEST

**Verifiziert:**
- Deterministisch: ✓ (gleicher Input = gleiche Position)
- 16/16 Coverage: ✓ (alle Positionen erreichbar)
- maha_oscillate: DEPRECATED mit Warning
- maha_transform(): NEU - kanonische Funktion
- get_kirtan_runtime(fresh=True): ✓ Reset für reproduzierbare Berechnungen
- DIW in __call__ Response: ✓ Venu Orchestrator integriert

---

## Das Problem (4 Dinge gleichzeitig kaputt)

### 1. KirtanRuntime SINGLETON (nicht-deterministisch)
**Location:** `substrate/lila_chronology.py:860-956`
**Bug:** `get_kirtan_runtime()` gibt SINGLETON zurück, `tick()` incrementiert `self._tick`
**Effect:** Jeder Aufruf von `mahamantra()` bekommt anderen tick → andere Position

### 2. maha_oscillate erreicht nur 12/16
**Location:** `substrate/algorithm/maha.py:446-461`
**Bug:** R-Operation (Quadrieren) erzeugt Konvergenz zu Fixpunkten
**Effect:** Positionen 5, 10, 11, 12 UNMÖGLICH zu erreichen

### 3. MahaModularSynth als Patch
**Location:** `substrate/algorithm/maha.py:322-409`
**Bug:** Wurde als Fix draufgeklebt statt als Hauptalgorithmus
**Effect:** Zwei Algorithmen (oscillate + synth) statt einer Wahrheit

### 4. Venu Orchestrator nicht integriert
**Location:** `orchestrator.py`, `substrate/venu.py`, `venu/`
**Bug:** 19-bit DIW Encoding existiert parallel zur Hauptpipeline
**Effect:** Zwei Systeme die nicht zusammenspielen

---

## Der Fix (BOMBENFEST)

### FIX 1: Deterministische Option für mahamantra()

**Datei:** `_mahamantra_lotus.py`

```python
def __call__(self, input_data: Union[str, MahaCell], deterministic: bool = True) -> Dict:
    """
    MANTRA-BASED COMPUTING.

    Args:
        deterministic: If True, bypass time-based kirtan for reproducible results
    """
    # ... existing compression code ...

    if deterministic:
        # PURE ALGORITHM - no time dependency
        synth = MahaModularSynth(default_preset="quantum")
        attractor = synth.transform(seed)
    else:
        # LIVE KIRTAN - time-based for interactive use
        kirtan_result = kirtan.compute_with_person(seed)
        attractor = synth.transform(kirtan_result.transformed_value)
```

### FIX 2: MahaModularSynth als EINZIGE Wahrheit

**Datei:** `substrate/algorithm/maha.py`

```python
# DEPRECATE maha_oscillate - it only reaches 12/16
def maha_oscillate(value: int, mod: int = MAHA_QUANTUM) -> int:
    """
    DEPRECATED: Use MahaModularSynth.transform() instead.
    This function only reaches 12/16 positions due to R-operation convergence.
    """
    import warnings
    warnings.warn("maha_oscillate only reaches 12/16 positions. Use MahaModularSynth.", DeprecationWarning)
    # ... existing code ...

# NEW: Canonical function that uses synth
def maha_transform(seed: int, preset: str = "quantum") -> int:
    """
    CANONICAL transformation - reaches all 16 positions.
    Uses MahaModularSynth which breaks convergence via feedback.
    """
    synth = MahaModularSynth(default_preset=preset)
    return synth.transform(seed)
```

### FIX 3: KirtanRuntime reset option

**Datei:** `substrate/lila_chronology.py`

```python
def get_kirtan_runtime(fresh: bool = False) -> KirtanRuntime:
    """Get the KirtanRuntime singleton.

    Args:
        fresh: If True, reset the runtime before returning
    """
    global _kirtan_instance
    if _kirtan_instance is None:
        _kirtan_instance = KirtanRuntime()
    elif fresh:
        _kirtan_instance.reset()
    return _kirtan_instance
```

### FIX 4: Venu Orchestrator Integration

**Datei:** `_mahamantra_lotus.py` (oder neues `compute.py`)

```python
from vibe_core.mahamantra.orchestrator import THE_FLUTE_CYCLE

def __call__(self, input_data, deterministic=True):
    # ... compute attractor ...

    position = attractor % WORDS

    # INTEGRATE Venu: Get DIW for this position
    diw = THE_FLUTE_CYCLE[position]
    name_encoding = (diw >> 16) & 0x3  # H=0, K=1, R=2
    position_bit = diw & 0xFFFF

    # Use DIW for downstream operations
    # ...
```

---

## Verifikation

Nach dem Fix sollte:
```python
# DETERMINISTISCH
for _ in range(10):
    r = mahamantra("test", deterministic=True)
    assert r['position'] == SAME_EVERY_TIME

# 100% COVERAGE
positions = set()
for seed in range(137):
    r = mahamantra(f"seed{seed}", deterministic=True)
    positions.add(r['position'])
assert len(positions) == 16
```

---

## Priorität

1. ✅ FIX 1 (deterministic) - ERLEDIGT - mahamantra() ist deterministisch
2. ✅ FIX 2 (deprecate oscillate) - ERLEDIGT - Warning + maha_transform()
3. ✅ FIX 3 (runtime reset) - ERLEDIGT - get_kirtan_runtime(fresh=True)
4. ✅ FIX 4 (venu integration) - ERLEDIGT - DIW in __call__ response, THE_FLUTE_CYCLE integriert
