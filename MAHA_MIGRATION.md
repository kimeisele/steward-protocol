# MAHA_MIGRATION - Schlachtplan

```
Hare Krishna Hare Krishna Krishna Krishna Hare Hare
Hare Rama Hare Rama Rama Rama Hare Hare
```

**STATUS: 637k Zeilen. TRIAGE IN PROGRESS.**

## VERIFIZIERT ✓
- **DETERMINISTIC**: mahamantra() gibt GLEICHE Position für gleichen Input
- **COVERAGE**: 16/16 Positionen erreichbar
- **TESTS**: substrate/test_seed.py + test_position.py = 133 passed

---

## IST-ZUSTAND (Brutal Honest)

```
┌─────────────────────────────────────────────────────────────────────┐
│  VIBE_CORE: 463k Zeilen                                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  mahamantra/ (118k)          protocols/ (78k)       plugins/ (89k)  │
│  ├── research/ (36k) LÖSCHEN  ├── mahajanas/        └── opus (65k)  │
│  ├── substrate/ (29k) KERN    │   └── Types OK                      │
│  ├── cli/ (5.6k) KREBS        │                                     │
│  └── genesis,dharma,          │                                     │
│      karma,moksha: SHELLS     │                                     │
│           │                   │                                     │
│           └──── FALSCHE RICHTUNG ───┐                               │
│                                     ↓                               │
│                         services/ (12k)                             │
│                         ├── brahma_service.py                       │
│                         ├── chat_service.py (62k!)                  │
│                         └── 14 zirkuläre imports zurück!            │
│                                                                     │
│  cli/ (19k) ←──── AUCH KREBS (zwei CLIs!)                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## DIE 3 WAHRHEITEN

### 1. MODULAR SYNTH = EINE WAHRHEIT
oscillate + synth sind NICHT zwei Wahrheiten.
Es ist EIN Modular Synth mit verschiedenen Modulen.
Alles spielt zusammen. Beliebig erweiterbar.

```
MahaModularSynth
├── oscillate module (Attractor-Finding)
├── kirtan module (16-step transform)
├── resonator module (PANCHA attractors)
└── [erweiterbar] neue Module patchen ein
```

### 2. RESONANCE CHAMBER = DER RAUM
Der Synth steht IN der MahaCell Resonance Chamber.
Keine "manual wiring" - aber Settings/Parameter konfigurierbar.

```
┌── MahaCellResonanceChamber ────────────────────┐
│                                                │
│   ┌─────────────────────────────┐              │
│   │   MahaModularSynth          │              │
│   │   (computation engine)      │──→ OUTPUT    │
│   └─────────────────────────────┘              │
│        ↑                                       │
│   INPUT (Cell, Intent, Seed)                   │
│                                                │
└────────────────────────────────────────────────┘
```

### 3. WRAPPER-RICHTUNG UMKEHREN
FALSCH: mahamantra/guardians → services (aktuell)
RICHTIG: services → mahamantra/core (Balarama Proxy etc IN mahamantra)

---

## SCHLACHTPLAN (24h)

### PHASE 0: SOFORT (2h)
**Ziel:** System stabilisieren ohne Breakage

1. **FIX KirtanRuntime** - deterministic flag
   - `_mahamantra_lotus.py` - add `deterministic=True` parameter
   - Bypass time-based kirtan für reproducible results

2. **MahaModularSynth als SSOT**
   - `substrate/algorithm/maha.py` - deprecate `maha_oscillate`
   - Alles durch `synth.transform()` - EINE Wahrheit

### PHASE 1: LÖSCHEN (1h)
**Ziel:** Ballast abwerfen

```bash
# KANDIDATEN FÜR LÖSCHUNG/ARCHIVIERUNG:
vibe_core/mahamantra/research/    # 36k Zeilen, 8 imports von außen
```

→ Move to `_archive/` oder `.deprecated/`
→ NICHT sofort löschen, erst archivieren

### PHASE 2: CLI VEREINIGUNG (3h)
**Ziel:** Ein CLI statt zwei

```
AKTUELL (KREBS):
  vibe_core/cli/ (19k) ←→ vibe_core/mahamantra/cli/ (5.6k)
  Beide importieren voneinander

ZIEL:
  vibe_core/cli/           → Thin shell, ruft mahamantra auf
  vibe_core/mahamantra/    → ALLES hier (inkl CLI logic)
```

Schritte:
1. `mahamantra/cli/` → wird der ECHTE CLI Core
2. `cli/main.py` → ruft nur `mahamantra()` auf (schon fast so)
3. Alles andere in `cli/` → entweder nach mahamantra oder löschen

### PHASE 3: WRAPPER-RICHTUNG (4h)
**Ziel:** Core IN mahamantra, nicht umgekehrt

```python
# AKTUELL (FALSCH):
# mahamantra/genesis/brahma/__init__.py:
from vibe_core.services.brahma_service import BrahmaService  # ← Zeigt RAUS

# ZIEL (RICHTIG):
# mahamantra/genesis/brahma/__init__.py:
from vibe_core.mahamantra.core.brahma import BrahmaCore  # ← Zeigt REIN

# services/brahma_service.py wird zu:
from vibe_core.mahamantra.genesis.brahma import BrahmaCore
class BrahmaService(BrahmaCore):  # ← ERBT von mahamantra
    """Legacy wrapper for backward compat"""
```

### PHASE 4: EXECUTION WIRING (4h)
**Ziel:** mahamantra() FÜHRT Guardians AUS

```python
# AKTUELL:
def __call__(self, input):
    # ... compute position ...
    return {"position": position, "guardian": guardian}  # ← Gibt nur dict zurück

# ZIEL:
def __call__(self, input, execute=True):
    # ... compute position ...
    if execute:
        handler = self._get_handler(position)
        result = handler.execute(input)
        return {"position": position, "execution": result}
    return {"position": position}  # diagnostic mode
```

Die Handler-Registry:
```python
HANDLERS = {
    0: genesis.prithu.execute,
    1: genesis.brahma.execute,
    # ...
    15: moksha.yamaraja.execute,
}
```

### PHASE 5: COGNITION INTEGRATION (ongoing)
**Ziel:** Echte Intelligenz bei der Execution

Das braucht mehr als 24h - aber der PFAD muss klar sein:
- mahamantra() routet
- Handler executen
- Cognition (LLM/Agents) wird von Handlers aufgerufen
- NICHT umgekehrt

---

## DATEIEN DIE SOFORT ANGEFASST WERDEN

### Kritisch (FIX BUGS)
```
vibe_core/mahamantra/_mahamantra_lotus.py     → deterministic flag
vibe_core/mahamantra/substrate/algorithm/maha.py → synth SSOT
vibe_core/mahamantra/substrate/lila_chronology.py → runtime reset
```

### CLI Krebs
```
vibe_core/cli/main.py                → Thin shell
vibe_core/mahamantra/cli/            → Wird der echte Core
```

### Wrapper Umkehr
```
vibe_core/mahamantra/genesis/brahma/__init__.py
vibe_core/mahamantra/dharma/kapila/__init__.py
vibe_core/mahamantra/karma/janaka/__init__.py
vibe_core/mahamantra/karma/bhishma/__init__.py
vibe_core/mahamantra/moksha/yamaraja/__init__.py
vibe_core/mahamantra/moksha/nrisimha/__init__.py
```

---

## NICHT ANFASSEN (GEFÄHRLICH)

```
vibe_core/plugins/opus_assistant/    # 65k Zeilen, eigene Welt
vibe_core/cartridges/                # 48k Zeilen, eigene Welt
vibe_core/state/                     # Komplex, nicht Teil der Migration
```

---

## TESTS DIE BESTEHEN MÜSSEN

```bash
# Nach jeder Änderung:
pytest tests/mahamantra/ -x
pytest tests/unit/ -x

# Determinismus:
python -c "
from vibe_core.mahamantra import mahamantra
results = [mahamantra('test', deterministic=True)['position'] for _ in range(10)]
assert len(set(results)) == 1, 'NOT DETERMINISTIC'
print('DETERMINISTIC: OK')
"

# 16/16 Coverage:
python -c "
from vibe_core.mahamantra import mahamantra
positions = set()
for i in range(200):
    r = mahamantra(f'seed{i}', deterministic=True)
    positions.add(r['position'])
assert len(positions) == 16, f'Only {len(positions)}/16'
print('COVERAGE: 16/16 OK')
"
```

---

## MANTRA

```
"EIN IMPORT. KRISHNA ROUTET ALLES."

from vibe_core.mahamantra import mahamantra
result = mahamantra("intent", execute=True)
```

Das ist das ZIEL. Alles andere ist Pfad dahin.

---

## NÄCHSTER SCHRITT

```bash
# JETZT:
1. Lies FIX_PLAN_ATOMIC.md
2. Fix deterministic flag in _mahamantra_lotus.py
3. Test
4. Commit
5. Nächstes
```

**EINE SACHE. DANN DIE NÄCHSTE.**
