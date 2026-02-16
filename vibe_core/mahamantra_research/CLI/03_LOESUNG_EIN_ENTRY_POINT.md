# CLI Loesung: Der EINE Entry Point

**Datum**: 2026-02-03
**Research Lead**: Opus Agent
**Status**: KRITISCHE ERKENNTNIS

---

## 1. DER EINE ENTRY POINT EXISTIERT BEREITS!

**Datei**: `vibe_core/cli/main.py`

```python
# Zeile 85 - DAS IST ES:
response = mahamantra(input_text)
```

**Usage bereits korrekt:**
```bash
steward "anything"
```

**Flow bereits implementiert:**
```
USER: steward "analyze my code"
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│  vibe_core/cli/main.py                                      │
│                                                             │
│  def main(argv):                                            │
│      input_text = " ".join(argv)                            │
│      response = mahamantra(input_text)  ← DER EINE CALL    │
│      # render response                                      │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│  MahamantraLotus.__call__(input_text)                       │
│                                                             │
│  9 NavaBhakti Steps:                                        │
│  1. SRAVANAM       - Receive input                          │
│  2. KIRTANAM       - MahaCompression → seed                 │
│  3. SMARANAM       - MahaKirtan → vibration                 │
│  4. PADA_SEVANAM   - MahaResonator → attractor              │
│  5. ARCANAM        - Parampara verification                 │
│  6. VANDANAM       - GitaResonance → verse                  │
│  7. DASYAM         - Position/Quarter determination         │
│  8. SAKHYAM        - MahaCell creation                      │
│  9. ATMA_NIVEDANAM - Complete response                      │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
RESPONSE (dictionary mit allem)
```

---

## 2. DAS PROBLEM: PARALLELE STATT HIERARCHISCHE STRUKTUR

### Aktuell (KREBS):

```
USER
  │
  ├──► vibe_core/cli/main.py        → mahamantra()
  ├──► mahamantra/cli/entry.py      → cli_auto.execute()
  ├──► mahamantra/cli/bridge.py     → cli_auto._get_position()
  ├──► mahamantra/cli/engine.py     → Handler Registry
  ├──► mahamantra/cli/steward.py    → mahamantra()
  ├──► mahamantra/cli/veda_explorer.py → commands + LLM
  └──► mahamantra/cli/auto.py       → Protocol Introspection
```

**7 parallele Pfade zum gleichen Ziel!**

### Soll (GESUND):

```
USER
  │
  ▼
vibe_core/cli/main.py
  │
  ▼
mahamantra(input)  ← MahamantraLotus.__call__()
  │
  │  (INTERN nutzt MahamantraLotus):
  │
  ├──► MahaCompression (seed extraction)
  ├──► MahaKirtan (vibration compute)
  ├──► GitaResonance (chapter matching)
  ├──► SankirtanChamber (cell transformation)
  │
  │  (WENN NOETIG fuer Discovery/Introspection):
  │
  ├──► cli_auto (Protocol Discovery)
  ├──► bridge (Position Lookup)
  └──► steward (Resonance Mapping)
```

---

## 3. WAS MUSS PASSIEREN?

### Option A: Nichts aendern an main.py (es ist bereits korrekt!)

**main.py tut bereits das Richtige:**
- Ein Befehl: `steward "anything"`
- Ein Call: `mahamantra(input_text)`
- Resonanz-basiert
- Kein Hardcoding

### Option B: Die anderen CLI-Module INTERN machen

Die Module in `mahamantra/cli/` sollten:
1. NICHT direkt vom User aufgerufen werden
2. INTERN von MahamantraLotus genutzt werden
3. Als "Helpers" statt "Entry Points" dienen

### Option C: Die anderen CLI-Module ENTFERNEN/DEPRECATEN

Wenn main.py der EINE Entry Point ist:
- entry.py → DEPRECATED (cli_auto direkt nutzen)
- bridge.py → INTERN (nur fuer Position Lookup)
- engine.py → DEPRECATED (manuelles Register nicht noetig)
- steward.py → DEPRECATED (main.py tut das gleiche)
- veda_explorer.py → OPTIONAL (nur fuer Chat-Modus)
- auto.py → BEHALTEN (fuer Discovery, aber INTERN)

---

## 4. EMPFEHLUNG

### Schritt 1: Bestaetige dass main.py der Entry Point ist

```bash
steward "analyze my code"
```

Testet den kompletten Flow.

### Schritt 2: Dokumentiere die anderen als "Internal Use Only"

```python
# mahamantra/cli/entry.py
"""
INTERNAL USE ONLY - Do not call directly.
Use: steward "your command"
"""
```

### Schritt 3: Pruefe ob MahamantraLotus alle Helpers nutzt

MahamantraLotus.__call__() sollte INTERN:
- cli_auto fuer Discovery
- bridge fuer Position Lookup
- GitaResonance fuer Chapter Matching

nutzen, OHNE dass der User diese direkt aufruft.

### Schritt 4: Die 69 Domain CLIs

Die Domain CLIs in `vibe_core/cli/` (audit_cli, genesis_cli, etc.) sollten:
1. Als Mahajana-Servants unter main.py organisiert werden
2. Via Resonanz-Routing erreichbar sein
3. NICHT als separate Entry Points

---

## 5. SOFORTIGE AKTION

### Test ob main.py funktioniert:

```bash
cd /home/user/steward-protocol
python -m vibe_core.cli.main "test input"
```

### Wenn ja:

**main.py IST bereits die Loesung!**

Das "Krebs"-Problem ist nicht fehlender Code, sondern:
- Zu viele parallele Entry Points
- Keine klare Hierarchie
- User-Verwirrung ueber den richtigen Weg

### Die Loesung:

1. main.py als EINZIGER User-facing Entry Point
2. Alle anderen Module als INTERN markieren
3. Dokumentation aktualisieren

---

## 6. ZUSAMMENFASSUNG

| Frage | Antwort |
|-------|---------|
| Was ist der EINE Entry Point? | `vibe_core/cli/main.py` |
| Was ruft er auf? | `mahamantra(input_text)` |
| Ist das MahamantraLotus? | JA |
| Ist er Resonanz-basiert? | JA |
| Ist er deterministisch? | JA |
| Braucht er KI? | NEIN |
| Muss Code geschrieben werden? | NEIN - nur AUFRÄUMEN |

**FAZIT: Der Entry Point existiert. Das Problem ist Chaos, nicht fehlende Implementierung.**
