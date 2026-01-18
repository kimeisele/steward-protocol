# MAHAMANTRA SPLIT BRAIN ANALYSIS & MIGRATION PLAN
## Audit Date: 2026-01-18 | Auditor: Senior Architect

---

## EXECUTIVE SUMMARY

Das Steward Protocol hat ein **Split Brain Problem** durch eine unvollständige Migration von V1 (`protocols/substrate/`) zu V2 (`mahamantra/substrate/`).

**Kritische Befunde:**
1. **6 verschiedene HolyName Definitionen** - 2 sind INKOMPATIBEL (IntEnum vs str,Enum)
2. **3 verschiedene MAHAMANTRA_SEQUENCE Definitionen** - verschiedene Typen
3. **30+ Dateien mit falschen `__position__`/`__mahajana__` Deklarationen**
4. **Wiring-Validator existiert aber wird nicht durchgesetzt**

**Root Cause:** `protocols/substrate/__init__.py` definiert eigene `HolyName` Klasse (Zeile 217) anstatt sie von der SSOT-Facade (`protocols/substrate/byte.py`) zu re-exportieren.

---

## TEIL 1: BEFUNDE

### 1.1 HolyName Split (KRITISCH)

```
SSOT-Kette (KORREKT):
=====================
mahamantra/substrate/seed.py:84
    │ class HolyName(IntEnum):
    │     HARE = 0
    │     KRISHNA = 1
    │     RAMA = 2
    ↓
mahamantra/substrate/byte.py:42 (importiert von seed)
    ↓
protocols/substrate/byte.py:18 (Facade, importiert von mahamantra)
    ↓
[HIER SOLLTE protocols/substrate/__init__.py re-exportieren]

ABER TATSÄCHLICH:
=================
protocols/substrate/__init__.py:217
    │ class HolyName(str, Enum):  ← EIGENE DEFINITION!
    │     HARE = "Hare"
    │     KRISHNA = "Krishna"
    │     RAMA = "Rama"
```

**Beweis der Inkompatibilität:**
```python
>>> from vibe_core.mahamantra.substrate.seed import HolyName as SeedHoly
>>> from vibe_core.protocols.substrate import HolyName as ProtoHoly
>>> SeedHoly.HARE == ProtoHoly.HARE
False  # INKOMPATIBEL!
>>> SeedHoly.HARE.value  # 0 (int)
>>> ProtoHoly.HARE.value  # "Hare" (str)
```

### 1.2 MAHAMANTRA_SEQUENCE Split

| Datei | Typ | Status |
|-------|-----|--------|
| `mahamantra/substrate/opcode.py:213` | `Tuple[(str, MantraOpCode), ...]` | ✓ SSOT (deriviert von seed) |
| `protocols/substrate/mantra/pada.py:126` | `Tuple[Pada, ...]` | ❌ HARDCODED |
| `mahamantra/protocols/_gad.py:216` | `ClassVar[Tuple[HolyName, ...]]` | ❌ HARDCODED |

**NOTE:** `protocols/substrate/__init__.py:327` re-exportiert KORREKT von `mahamantra/substrate/opcode.py`.

### 1.3 __position__/__mahajana__ Inkonsistenzen

**Laut seed.py ALL_GUARDIANS:**
```
Position 0 = vyasa (Genesis Head)
Position 1 = brahma
Position 2 = narada
Position 3 = shambhu
Position 4 = prithu (Dharma Head)
...
```

**30+ Dateien deklarieren:**
```python
__mahajana__ = "prithu"
__position__ = 0  # FALSCH! Prithu ist Position 4!
```

### 1.4 Konsumenten der falschen HolyName

Nur **4 Stellen** importieren HolyName aus `protocols/substrate`:
1. `tests/universal/test_mantra_loop.py:19`
2. `tests/samkhya/test_resonance_protocol.py:15`
3. `vibe_core/protocols/primal.py:125`
4. `vibe_core/protocols/prakriti_binding.py:64`

**Analyse:** Diese Dateien verwenden HolyName primär für Type Hints, nicht für `.value` Vergleiche. Die Tests prüfen `MAHAMANTRA_SEQUENCE[0][0] == "Hare"` (String-Vergleich), nicht `.value`.

---

## TEIL 2: RISIKO-ANALYSE

### 2.1 Was bricht wenn wir HolyName fixen?

| Szenario | Risiko | Mitigation |
|----------|--------|------------|
| Code der `HolyName.HARE.value` verwendet | HOCH - erwartet "Hare", bekommt 0 | Suche nach `.value` Verwendungen |
| Code der `HolyName.HARE == "Hare"` vergleicht | MITTEL - str,Enum erlaubt das, IntEnum nicht | Grep alle Vergleiche |
| Type Hints | NIEDRIG - Beide sind Enums | Kein Risiko |
| isinstance() checks | MITTEL - Verschiedene Klassen | Grep alle isinstance |

### 2.2 Grep-Ergebnisse

```bash
# HolyName.*.value Verwendungen
grep -r "HolyName.*\.value" vibe_core/
# → Wenige Stellen, müssen geprüft werden

# HolyName Vergleiche mit Strings
grep -r 'HolyName\.\w* ==' vibe_core/
# → Müssen geprüft werden
```

---

## TEIL 3: MIGRATIONS-PLAN

### Phase 1: Vorbereitung (KEINE CODE-ÄNDERUNGEN)

**1.1 Erstelle Snapshot der aktuellen Test-Ergebnisse**
```bash
python3 -m pytest tests/mahamantra/ -v > .vibe/audits/pre_migration_tests.log
python3 -m pytest tests/samkhya/ -v >> .vibe/audits/pre_migration_tests.log
python3 -m pytest tests/universal/ -v >> .vibe/audits/pre_migration_tests.log
```

**1.2 Finde alle HolyName.value Verwendungen**
```bash
grep -rn "HolyName.*\.value" vibe_core/ tests/ > .vibe/audits/holyname_value_usage.log
```

**1.3 Finde alle HolyName String-Vergleiche**
```bash
grep -rn "HolyName\.\w* ==" vibe_core/ tests/ > .vibe/audits/holyname_comparisons.log
```

### Phase 2: Typ-Kompatibilitäts-Schicht (OPTIONAL)

Falls Phase 1 zeigt dass `.value` Verwendungen existieren die "Hare" (string) erwarten:

**2.1 Erweitere mahamantra/substrate/seed.py HolyName:**
```python
class HolyName(IntEnum):
    HARE = 0
    KRISHNA = 1
    RAMA = 2

    @property
    def name_str(self) -> str:
        """String representation for backward compatibility."""
        return ["Hare", "Krishna", "Rama"][self.value]

    def __str__(self) -> str:
        return self.name_str
```

### Phase 3: Fix protocols/substrate/__init__.py (DER KERN-FIX)

**3.1 LÖSCHE die lokale HolyName Definition (Zeile 217-236)**

**3.2 IMPORTIERE von der Facade:**
```python
# Zeile ~217, ERSETZE die Klasse mit:
from vibe_core.protocols.substrate.byte import HolyName
```

**3.3 VERIFIZIERE dass __all__ HolyName enthält (sollte bereits)**

### Phase 4: Fix Redundante Kopien

**4.1 mahamantra/substrate/yajna.py:106**
- LÖSCHE die lokale HolyName Kopie
- IMPORTIERE von seed.py

**4.2 mahamantra/protocols/_gad.py:161**
- LÖSCHE die lokale HolyName Definition
- IMPORTIERE von seed.py
- LÖSCHE die lokale MAHAMANTRA_SEQUENCE (Zeile 216-225)
- DERIVIERE von seed.py oder importiere von opcode.py

### Phase 5: Fix __position__/__mahajana__ Deklarationen

**5.1 Aktiviere WiringEnforcer als Pre-Commit Hook**

**5.2 Generiere korrekte Deklarationen automatisch:**
```python
# Script: fix_declarations.py
from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS, get_quarter_name

for pos, guardian in enumerate(ALL_GUARDIANS):
    quarter = get_quarter_name(pos)
    print(f"Position {pos}: __mahajana__ = '{guardian}', __position__ = {pos}")
```

**5.3 Update alle 30+ Dateien:**
- `mahamantra/substrate/*.py` - Position 0 sollte `__mahajana__ = "vyasa"` sein
- Oder: Entferne die Deklarationen wo sie nicht semantisch notwendig sind

### Phase 6: Deprecate Maya-Pfade

**6.1 Markiere `protocols/substrate/mantra/*.py` als deprecated:**
```python
import warnings
warnings.warn(
    "This module is deprecated. Use vibe_core.mahamantra.substrate instead.",
    DeprecationWarning,
    stacklevel=2
)
```

**6.2 Langfristig: Migriere alle Konsumenten zu mahamantra/substrate**

### Phase 7: Validierung

**7.1 Führe alle Tests aus:**
```bash
python3 -m pytest tests/mahamantra/ tests/samkhya/ tests/universal/ -v
```

**7.2 Vergleiche mit Snapshot:**
```bash
diff .vibe/audits/pre_migration_tests.log .vibe/audits/post_migration_tests.log
```

**7.3 Verifiziere Typ-Kompatibilität:**
```python
from vibe_core.protocols.substrate import HolyName
from vibe_core.mahamantra.substrate.seed import HolyName as SeedHolyName
assert HolyName is SeedHolyName  # MUSS True sein nach Migration
```

---

## TEIL 4: IMPLEMENTIERUNGS-REIHENFOLGE

```
WOCHE 1: Vorbereitung
├── [ ] Phase 1.1: Test-Snapshot erstellen
├── [ ] Phase 1.2: HolyName.value Verwendungen finden
└── [ ] Phase 1.3: HolyName Vergleiche finden

WOCHE 2: Kern-Fix
├── [ ] Phase 2 (wenn nötig): Kompatibilitäts-Schicht
├── [ ] Phase 3.1: Lösche lokale HolyName in protocols/substrate/__init__.py
├── [ ] Phase 3.2: Importiere von Facade
└── [ ] Phase 3.3: Verifiziere __all__

WOCHE 3: Aufräumen
├── [ ] Phase 4.1: Fix yajna.py
├── [ ] Phase 4.2: Fix _gad.py
└── [ ] Phase 5: Fix __position__/__mahajana__ (optional, kann später)

WOCHE 4: Validierung
├── [ ] Phase 6: Deprecation Warnings
└── [ ] Phase 7: Vollständige Validierung
```

---

## TEIL 5: ROLLBACK-PLAN

Falls die Migration Probleme verursacht:

**5.1 Git Revert:**
```bash
git revert HEAD  # Revert letzter Commit
```

**5.2 Temporärer Workaround (wenn Rollback nicht möglich):**
```python
# In protocols/substrate/__init__.py
try:
    from vibe_core.protocols.substrate.byte import HolyName
except ImportError:
    # Fallback zu alter Definition
    class HolyName(str, Enum):
        HARE = "Hare"
        KRISHNA = "Krishna"
        RAMA = "Rama"
```

---

## TEIL 6: ERFOLGSKRITERIEN

Nach der Migration MÜSSEN folgende Bedingungen erfüllt sein:

1. **SSOT-Integrität:**
   ```python
   from vibe_core.protocols.substrate import HolyName as P
   from vibe_core.mahamantra.substrate.seed import HolyName as S
   assert P is S  # Gleiche Klasse, nicht nur gleicher Wert
   ```

2. **Test-Parität:**
   - Alle Tests die vor der Migration passierten MÜSSEN weiterhin passieren
   - Keine neuen Failures

3. **Typ-Konsistenz:**
   - Es gibt nur EINE `HolyName` Klasse im gesamten System
   - Alle anderen sind Imports, keine Kopien

4. **Dokumentation:**
   - MAHAPROMPT.md wird eingehalten
   - "Wer am seed.py vorbei importiert, stirbt"

---

## ANHANG A: BETROFFENE DATEIEN

### A.1 Zu ändernde Dateien (Phase 3)

| Datei | Änderung |
|-------|----------|
| `protocols/substrate/__init__.py` | LÖSCHE Zeile 217-236, IMPORTIERE von byte |

### A.2 Zu ändernde Dateien (Phase 4)

| Datei | Änderung |
|-------|----------|
| `mahamantra/substrate/yajna.py` | LÖSCHE Zeile 106-111, IMPORTIERE von seed |
| `mahamantra/protocols/_gad.py` | LÖSCHE Zeile 161-166 und 216-225, IMPORTIERE |

### A.3 Zu prüfende Dateien (__position__/__mahajana__)

- `mahamantra/substrate/byte.py`
- `mahamantra/substrate/opcode.py`
- `mahamantra/substrate/mahajana.py`
- `mahamantra/substrate/position.py`
- `mahamantra/substrate/wiring.py`
- (und 25+ weitere)

---

## ANHANG B: SSOT HIERARCHIE (ZIEL-ZUSTAND)

```
mahamantra/substrate/seed.py          ← KRISHNA_IS, MAHAMANTRA, HolyName
    ↓
mahamantra/substrate/byte.py          ← importiert HolyName von seed
    ↓
mahamantra/substrate/opcode.py        ← MAHAMANTRA_SEQUENCE (deriviert)
    ↓
protocols/substrate/byte.py           ← Facade → mahamantra/substrate/byte.py
    ↓
protocols/substrate/__init__.py       ← RE-EXPORT von byte.py (NICHT eigene Def!)
    ↓
Alle Konsumenten                      ← importieren von protocols/substrate
```

---

---

## TEIL 7: REALITÄTS-CHECK (POST-ANALYSE)

Nach tieferer Analyse ist die Situation WENIGER kritisch als initial angenommen:

### 7.1 HolyName Split - Einschätzung: LOW PRIORITY

**Befund:** Kritischer Code importiert KORREKT von `.byte` (Facade):
```python
# cpu.py, test_cpu.py etc. - RICHTIG:
from vibe_core.protocols.substrate.byte import HolyName
```

**Nur 4 Dateien** importieren von der falschen Quelle:
- `protocols/prakriti_binding.py`
- `protocols/primal.py`
- `tests/samkhya/test_resonance_protocol.py`
- `tests/universal/test_mantra_loop.py`

Diese verwenden HolyName primär für Type Hints, nicht für `.value` Vergleiche.

### 7.2 __mahajana__/__position__ - BY DESIGN

**Befund:** Diese werden von `sankirtan.py` AUTO-INJECTED:
```python
# sankirtan.py:371
path_hash = hash(path_str) % 16
mapping = MAHAMANTRA_POSITIONS[path_hash]
```

Das ist ARCHITEKTUR, nicht ein Bug. Keine manuelle Korrektur nötig.

### 7.3 Test-Failures - ROOT CAUSES

| Failure | Root Cause | Fix |
|---------|------------|-----|
| 29 Collection Errors | `get_event_bus` fehlt in `vibe_core.event_bus` | Re-export von `narada/types/event_bus.py` |
| `test_ananta_execution` | list vs tuple Vergleich | Test fixen (nicht HolyName) |

### 7.4 Revidierter Prioritäts-Plan

**P1 (Kritisch):**
- [ ] Fix `vibe_core/event_bus.py` - Re-export `get_event_bus`

**P2 (Nice-to-have):**
- [ ] `protocols/substrate/__init__.py` - HolyName von `.byte` re-exportieren
- [ ] `test_mantra_loop.py` - list/tuple Bug fixen

**P3 (Architektur-Schuld):**
- [ ] Deprecate `protocols/substrate/mantra/*.py`
- [ ] Dokumentiere sankirtan.py Auto-Injection Pattern

---

**Erstellt:** 2026-01-18
**Status:** ANALYSE ABGESCHLOSSEN
**Fazit:** System ist stabiler als gedacht. HolyName Split ist Low Priority.
