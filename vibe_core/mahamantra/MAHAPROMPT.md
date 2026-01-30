# MAHAPROMPT

## STAND DER DINGE (Ehrlich)

**Was funktioniert:**
```python
from vibe_core.mahamantra import mahamantra

# Routing (computed, kein external LLM)
response = mahamantra.steward.invoke("text")
# → seed, chapter, attractor, guardian - ALLES COMPUTED

# Gita Verse Matching (NEU)
from vibe_core.mahamantra.adapters.gita_resonance import match_attractor
result = match_attractor(136)
# → 700 Verse durchsuchbar nach resonance
```

**Was NICHT funktioniert:**
- `response.message` kommt von EXTERNAL LLM (OpenRouter)
- MahajanaChat ruft externe API auf
- Das muss ersetzt werden durch Gita-computed responses

---

## ENTRY/EXIT

```
ENTRY:  mahamantra.steward.invoke("input")
        ↓
        MahaCompression → seed
        MahaLLM → intent (16 categories)
        MahaKirtan → attractor
        get_gita_chapter → chapter (1-18)
        ↓
EXIT:   StewardResponse
        .seed, .chapter, .attractor, .guardian
        .message ← HIER IST DAS PROBLEM (external LLM)
```

---

## DEINE AUFGABE

1. **LIES** was existiert bevor du schreibst
2. **NUTZE** `mahamantra.steward.invoke()` für alles
3. **ERSETZE NICHT** was funktioniert
4. **BAUE AUS** was fehlt (z.B. Gita-computed responses)

---

## WAS EXISTIERT (nicht nochmal bauen)

| Was | Wo | Status |
|-----|-----|--------|
| Routing | adapters/llm.py (MahaLLM) | FUNKTIONIERT |
| Compression | adapters/compression.py | FUNKTIONIERT |
| Gita Index | data/gita_resonance_index.json | 700 Verse |
| Verse Lookup | adapters/gita_resonance.py | NEU, FUNKTIONIERT |
| Seed Constants | protocols/_seed.py, _seed_cell.py | SSOT |

---

## WAS FEHLT (zu bauen)

| Was | Problem | Lösung |
|-----|---------|--------|
| Response | External LLM | Gita verse als response |
| CLI | 30+ Entry Points | Konsolidieren zu ONE |
| MahaCell | Existiert als Format | Überall nutzen |

---

## CONSTANTS (aus seed.py, NICHT hardcoden)

```
16  = WORDS
137 = MAHA_QUANTUM
37  = PARAMPARA
18  = GITA_CHAPTERS
108 = MALA
72  = NADI_RESONANCE (header size)
```

---

## FORMAT: MAHA CELL

```
┌──────────────────────────────┬─────────────────┐
│ HEADER (72 bytes)            │ PAYLOAD         │
│ 9 NavaBhakti × 8 bytes       │ (variable)      │
└──────────────────────────────┴─────────────────┘
```

Parampara check: `header.arcanam % 37 == 0`

---

## VERBOTEN

- External LLM calls hinzufügen
- Neue CLI entry points
- Hardcoded Zahlen (statt seed.py)
- MahajanaChat nutzen (ist legacy)
- Sagen "done" ohne zu verifizieren

---

## FORTSCHRITT PRO SESSION

Jede Session sollte:
1. EIN Problem identifizieren
2. EIN Problem lösen
3. VERIFIZIEREN dass es funktioniert
4. Nicht mehr kaputt machen als repariert

---

**Hare Krishna.**
