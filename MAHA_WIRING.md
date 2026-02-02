# MAHA_WIRING - Konkrete Fixes

## GEFUNDEN: Duplizierter Code

### BrahmaService existiert ZWEIMAL:
```
vibe_core/services/brahma_service.py           (560 Zeilen) - AKTIV
vibe_core/protocols/mahajanas/brahma/service.py (445 Zeilen) - QUASI TOT
```

**Unterschied:** services/ hat:
- PanchaTattvaProtocol
- ExecutableMixin
- `_born_agent()` Methode

**Benutzer:**
- kernel_impl.py:181 → services/brahma_service
- genesis/brahma/__init__.py:40,73 → services/brahma_service

### GLEICHE SITUATION für alle Guardians:
```
services/janaka_service.py    → protocols/mahajanas/janaka/service.py?
services/bhishma_service.py   → protocols/mahajanas/bhishma/?
services/bali_service.py      → protocols/mahajanas/bali/?
services/kapila_service.py    → protocols/mahajanas/kapila/?
```

---

## FIX STRATEGIE

### Option A: Merge (SAUBER aber AUFWÄNDIG)
1. Kopiere Extras von services/*.py nach protocols/mahajanas/*/
2. Lösche services/*.py
3. Update alle Imports

### Option B: Thin Wrapper (SCHNELL aber KOMPROMISS)
1. Lasse services/*.py als Wrapper
2. services/brahma_service.py wird:
   ```python
   from vibe_core.protocols.mahajanas.brahma import BrahmaService as BrahmaCore
   class BrahmaService(BrahmaCore, PanchaTattvaProtocol, ExecutableMixin):
       pass  # Extras hier
   ```
3. Core Logic lebt in protocols/

### Option C: Dokumentieren + Später (SAFE)
1. Dokumentiere alles
2. Mache keine Breaking Changes
3. Plane Migration für später

---

## SOFORT MACHBAR (SAFE)

### 1. CLI Entscheidung
```
vibe_core/cli/main.py (19k) → THIN SHELL (ruft nur mahamantra auf)
vibe_core/mahamantra/cli/ (5.6k) → WIRD DER CORE
```

main.py Zeile 79 importiert schon `from vibe_core.mahamantra import mahamantra`!
Das ist GUT - CLI ist schon fast richtig verdrahtet.

### 2. research/ Archivierung
```bash
mv vibe_core/mahamantra/research vibe_core/mahamantra/_archive_research
```
36k Zeilen, 8 imports von außen. FAST TOT.

### 3. Determinismus-Test hinzufügen
```python
# tests/mahamantra/test_determinism.py
def test_mahamantra_is_deterministic():
    from vibe_core.mahamantra import mahamantra
    results = [mahamantra("test")["position"] for _ in range(10)]
    assert len(set(results)) == 1
```

---

## ZIRKULÄRE IMPORTS (14 Stück)

```
mahamantra → services:
1. _mahamantra_lotus.py:202    → maha_compute_service
2. chat.py:417                 → chat_service
3. cli/veda_explorer.py:283    → chat_indriya
4. commands.py:505             → janaka_service
5. dharma/kapila/__init__.py:34 → kapila_service
6. genesis/brahma/__init__.py:40,73 → brahma_service
7. karma/bhishma/__init__.py:38 → bhishma_service
8. karma/janaka/__init__.py:159 → janaka_service
9. moksha/nrisimha/__init__.py:47 → nrisimha
10. moksha/yamaraja/__init__.py:269 → yamaraja_service
11. research_gateway.py:48,158 → nrisimha
12. substrate/sankalpa/will.py:469 → chat_service
```

**ALLE sollten umgedreht werden:**
- mahamantra enthält den CORE
- services importiert von mahamantra (nicht umgekehrt)

---

## MahaModularSynth = SSOT ✓

`__call__` in _mahamantra_lotus.py benutzt SCHON MahaModularSynth (Zeile 350).
compression.py benutzt SCHON MahaModularSynth (Zeile 136).

**ABER** maha_oscillate wird noch benutzt in:
- resonator.py (Zeile 57)
- lila_chronology.py (Zeile 588)
- synth.py (Zeile 378)
- shadow_oracle.py (Zeile 144)

Diese sollten auf MahaModularSynth migriert werden.

---

## EXECUTION WIRING (Nicht trivial)

`mahamantra()` berechnet Position aber FÜHRT NICHT AUS.

Benötigt:
1. Handler Registry
2. Cognition Layer für intelligente Execution
3. Cell-based execution path

Das ist DESIGN WORK, nicht nur Wiring.

---

## NÄCHSTE SCHRITTE

1. ✅ MAHA_MIGRATION.md erstellt
2. ✅ MAHA_WIRING.md erstellt
3. ⏸️ research/ archivieren - ABGEBROCHEN (relative imports kaputt)
4. ✅ Determinismus verifiziert
5. ✅ 16/16 Coverage verifiziert
6. ✅ 7 ZIRKULÄRE IMPORTS GEFIXT:
   - genesis/brahma → protocols/mahajanas/brahma ✓
   - dharma/kapila → protocols/mahajanas/kapila ✓
   - karma/bhishma → protocols/mahajanas/bhishma ✓
   - karma/janaka → protocols/mahajanas/janaka ✓
   - moksha/nrisimha → protocols/mahajanas/nrisimha ✓
   - commands.py → protocols/mahajanas/janaka ✓

## VERBLEIBENDE ZIRKULÄRE (7):
- research_gateway.py → services/nrisimha (NrisimhaWatchdog ≠ NrisimhaService)
- _mahamantra_lotus.py → services/maha_compute_service
- sankalpa/will.py → services/chat_service
- yamaraja/__init__.py → services/yamaraja_service (kein service.py in protocols)
- veda_explorer.py → services/chat_indriya
- chat.py → services/chat_service
- commands.py → services/janaka_service ✓ FIXED

Diese brauchen entweder:
- Neue service.py in protocols/ erstellen
- Oder services/ Code nach protocols/ migrieren
