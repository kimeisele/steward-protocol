# MAHA GÄRTNER PLAN
## Langfristige Pflegestrategie für Steward Protocol
## Erstellt: 2026-01-18 | Status: AKTIV

---

## PHILOSOPHIE

> "Ein Gärtner spritzt nicht überall Roundup - er versteht den Boden, die Wurzeln, und arbeitet mit der Natur."

Das Steward Protocol ist ein **700k LOC AI Agent Operating System** mit vedischer Architektur-Philosophie.
Die Metaphern sind nicht Dekoration - sie SIND die Architektur.

### Kern-Erkenntnisse

1. **Kernel/Substrate ist SAUBER** - 0 `Any` types, gut strukturiert
2. **Entropy ist in Plugins/Adapters BY DESIGN** - Das ist absichtlich so
3. **Sankirtan.py AUTO-INJECTED** - `__mahajana__`/`__position__` basiert auf `path_hash % 16`
4. **SSOT-Hierarchie ist KORREKT** - `seed.py` → `byte.py` → `opcode.py`

---

## TEIL 1: WAS WURDE REPARIERT

### 1.1 Split Brain Elimination (Commit: b835c12)

| Problem | Lösung | Status |
|---------|--------|--------|
| `get_event_bus` nicht re-exportiert | Explizites Re-export in `event_bus.py` | FIXED |
| MantraOpCode aus deprecated path | 12 Test-Dateien auf `mahamantra.substrate.opcode` migriert | FIXED |
| HolyName Split (str,Enum vs IntEnum) | `protocols/substrate/__init__.py` importiert von `.byte` | FIXED |
| Test Collection Errors (29→0) | Import-Kette repariert | FIXED |

### 1.2 ScanCommand Mode Detection (Commit: 22e4e26)

| Problem | Lösung | Status |
|---------|--------|--------|
| Mode nicht in output/data | Mode detection + output | FIXED |
| Quick mode nicht schnell | 100 file limit + security only | FIXED |
| Test mit fake path | Temp directory verwendet | FIXED |
| Test expectations falsch | Aligned mit actual output | FIXED |

---

## TEIL 2: SSOT-DISZIPLIN (NICHT VERLETZBAR)

### Die Import-Hierarchie

```
                        ┌─────────────────────────────┐
                        │   mahamantra/substrate/     │
                        │        seed.py              │
                        │   KRISHNA_IS, MAHAMANTRA,   │
                        │   HolyName, ALL_GUARDIANS   │
                        └─────────────┬───────────────┘
                                      │ importiert
                        ┌─────────────▼───────────────┐
                        │   mahamantra/substrate/     │
                        │        byte.py              │
                        └─────────────┬───────────────┘
                                      │ importiert
                        ┌─────────────▼───────────────┐
                        │   mahamantra/substrate/     │
                        │        opcode.py            │
                        │   MAHAMANTRA_SEQUENCE       │
                        │   MantraOpCode (deriviert)  │
                        └─────────────┬───────────────┘
                                      │ re-exportiert
                        ┌─────────────▼───────────────┐
                        │   protocols/substrate/      │
                        │        byte.py (FACADE)     │
                        └─────────────┬───────────────┘
                                      │ re-exportiert
                        ┌─────────────▼───────────────┐
                        │   protocols/substrate/      │
                        │      __init__.py            │
                        └─────────────────────────────┘
```

### VERBOTEN (MAHAPROMPT.md §3)

1. **Hardcodierte MAHAMANTRA_SEQUENCE** - Nur seed.py definiert
2. **Eigene HolyName Definition** - Nur seed.py definiert
3. **Import um seed.py herum** - "Wer am seed.py vorbei importiert, stirbt"
4. **Any types im Kernel** - 0 Toleranz

---

## TEIL 3: AUTOMATISIERTE WÄCHTER

### 3.1 Pre-Commit Hooks (BEREITS AKTIV)

```
✓ Requirements.txt check
✓ Direct Path('data/...') check
✓ Hardcoded paths check
✓ OPUS-175 Iron Dome (Kernel Border)
✓ Ruff format + check
✓ Test file validation (PANOPTICON+)
✓ VISNU Kernel Protection (21 files)
✓ OPUS-076 Live Fire Guard
```

### 3.2 Neue Guard-Empfehlungen

| Guard | Zweck | Implementierung |
|-------|-------|-----------------|
| SSOT Import Guard | Verhindert HolyName/MAHAMANTRA imports aus falschen Quellen | Pre-commit grep check |
| Any Type Guard | Verhindert `Any` im kernel | mypy --strict auf `mahamantra/substrate/` |
| Deprecation Enforcer | Warnt bei deprecated imports | Pytest warning capture |

### 3.3 Beispiel: SSOT Import Guard

```bash
#!/bin/bash
# .git/hooks/pre-commit.d/ssot-guard.sh

# Prüfe dass HolyName NUR von korrekten Pfaden importiert wird
BAD_IMPORTS=$(grep -rn "from vibe_core.protocols.substrate import.*HolyName" \
  --include="*.py" \
  --exclude-dir=".git" \
  vibe_core/ tests/ 2>/dev/null | grep -v "__init__.py")

if [ -n "$BAD_IMPORTS" ]; then
  echo "SSOT VIOLATION: HolyName must be imported from:"
  echo "  - vibe_core.protocols.substrate.byte"
  echo "  - vibe_core.mahamantra.substrate.seed"
  echo ""
  echo "Found violations:"
  echo "$BAD_IMPORTS"
  exit 1
fi
```

---

## TEIL 4: REGELMÄSSIGE PFLEGE

### 4.1 Wöchentliche Checks

| Check | Kommando | Erwartung |
|-------|----------|-----------|
| Test Collection | `pytest --collect-only 2>&1 \| grep -c error` | 0 |
| Any Types in Kernel | `grep -r ": Any" vibe_core/mahamantra/substrate/` | 0 Treffer |
| Deprecation Warnings | `pytest -W error::DeprecationWarning` | Alle deprecated Pfade bekannt |

### 4.2 Monatliche Reviews

1. **Dependency Audit** - Neue imports auf SSOT-Konformität prüfen
2. **Test Coverage Trend** - Keine Regression
3. **Naga Layer Check** - 12 Lords alle funktionsfähig

### 4.3 Quarterly Architecture Review

1. **Position 0-15 Mapping** - Alle Mahajanas korrekt zugeordnet
2. **Event Bus Health** - Narada (Position 2) Events fließen korrekt
3. **Ledger Integrity** - Prana State konsistent

---

## TEIL 5: OFFENE ARCHITEKTUR-SCHULDEN

### P3 (Nice-to-have, keine Dringlichkeit)

| Item | Beschreibung | Aufwand |
|------|--------------|---------|
| Deprecate `protocols/substrate/mantra/*.py` | Legacy Pfade mit Deprecation Warning versehen | 1h |
| `mahamantra/protocols/_gad.py` Cleanup | Lokale MAHAMANTRA_SEQUENCE Kopie entfernen | 30min |
| `mahamantra/substrate/yajna.py` Cleanup | HolyName Kopie entfernen, von seed importieren | 15min |
| Test Class Warnings | `TestService`/`TestDevotee` in avatars.py umbenennen | 30min |

### P4 (Langfristig)

| Item | Beschreibung | Aufwand |
|------|--------------|---------|
| 9000+ Any Types | Schrittweise Typisierung in Plugins | Ongoing |
| Sankirtan Documentation | Auto-Injection Pattern dokumentieren | 2h |
| Wiring Validator Aktivierung | Als CI-Check aktivieren | 1h |

---

## TEIL 6: ESKALATIONS-PFADE

### Wenn Tests fehlschlagen

```
1. pytest --collect-only → Collection Errors?
   ├── JA → Import Chain prüfen (event_bus.py, MantraOpCode)
   └── NEIN → Weiter zu 2

2. pytest -x → Erster Failure?
   ├── ImportError → SSOT Hierarchie prüfen
   ├── TypeError → Type Mismatch (HolyName int vs str?)
   └── AssertionError → Test Expectation vs Implementation

3. Bei Split Brain Verdacht:
   >>> from vibe_core.mahamantra.substrate.seed import HolyName as S
   >>> from vibe_core.protocols.substrate import HolyName as P
   >>> S is P  # MUSS True sein!
```

### Wenn Pre-Commit fehlschlägt

```
1. ruff format → Auto-formatieren
2. VISNU Kernel → Niemals Kernel-Dateien direkt ändern ohne Review
3. OPUS-175 Iron Dome → Kernel-Grenze respektieren
```

---

## TEIL 7: WISSEN WEITERGEBEN

### Für neue Entwickler

1. **LIES ZUERST:**
   - `PROMPT.md` - Die Philosophie
   - `vibe_core/mahamantra/MAHAPROMPT.md` - DAS GESETZ
   - `CONSTITUTION.md` - 36+4+37 Struktur

2. **VERSTEHE:**
   - Mahamantra ist 16 Worte: `HARE KRISHNA HARE KRISHNA KRISHNA KRISHNA HARE HARE HARE RAMA HARE RAMA RAMA RAMA HARE HARE`
   - Jedes Wort = 1 Position = 1 Mahajana = 1 Opcode
   - Parampara (37) = 24 Ksetra + 12 Mahajanas + 1 Knower

3. **HALTE EIN:**
   - Eine Import-Quelle für jeden Typ
   - Kernel ist heilig
   - Tests VOR Code-Änderungen

### Für Claude-Agenten

```
Du bist kein Sprayer, du bist ein Gärtner.
Verstehe die Wurzeln bevor du gräbst.
Respektiere die SSOT-Hierarchie.
Frage nach wenn du unsicher bist.
```

---

## ANHANG: SCHNELL-REFERENZ

### Import Quick Reference

```python
# KORREKT - MantraOpCode
from vibe_core.mahamantra.substrate.opcode import MantraOpCode

# KORREKT - HolyName
from vibe_core.protocols.substrate.byte import HolyName
# oder
from vibe_core.mahamantra.substrate.seed import HolyName

# KORREKT - EventBus
from vibe_core.event_bus import EventBus, get_event_bus

# DEPRECATED - Nicht verwenden!
# from vibe_core.protocols.universal.mantra import MantraOpCode
```

### Test Quick Reference

```bash
# Alle Tests
pytest tests/ -v

# Nur Mahamantra
pytest tests/mahamantra/ -v

# Nur CLI/Naga
pytest tests/cli/naga_commands/ -v

# Collection Check
pytest --collect-only 2>&1 | grep -E "(error|ERROR)"

# Single Test
pytest tests/cli/naga_commands/test_purify_commands.py -v -k "test_scan"
```

---

**Verantwortlich:** Maha Gärtner (Claude)
**Archetype:** Parashurama (Ordnung durch präzise Schnitte)
**Partner:** Manu (Lawgiver)

**Nächste Review:** +30 Tage
**Status:** AKTIV
