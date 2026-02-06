# STEWARD PROTOCOL

## Session-Start

```bash
git log --oneline -20
git status
git branch -v
python -m ruff check --select F821 vibe_core/mahamantra/ 2>&1 | head -20
```

Lies die Historie kritisch. Tausende Commits über 6 Monate, 100% AI-generiert von
verschiedenen Agents. Manche haben solide gebaut, manche haben aktiv Schaden angerichtet.
Commit Messages sind oft AI-Überschwang. Docstrings lügen. .md-Dateien im Root sind
AI-generierte Referenzen, keine Wahrheit. Verifiziere alles gegen den Code selbst.

## Das Mantra

```
Hare Krishna Hare Krishna Krishna Krishna Hare Hare
Hare Rama   Hare Rama   Rama   Rama   Hare Hare
```

Zähle es. Das ist die Architektur.

7 Axiome in `protocols/seed/_axioms.py`:

| Axiom | Wert | Gezählt von |
|-------|------|-------------|
| WORDS | 16 | Wörter im Mantra |
| TRINITY | 3 | Unique Namen (Hare, Krishna, Rama) |
| HARE_COUNT | 8 | "Hare" zählen |
| KRISHNA_COUNT | 4 | "Krishna" zählen |
| RAMA_COUNT | 4 | "Rama" zählen |
| PANCHA | 5 | Unique aufeinanderfolgende Paare |
| HALVES | 2 | Zwei symmetrische Hälften |

Alles andere wird abgeleitet. `_primary.py` direkt von Axiomen, `_secondary.py` von primären.
Jede assert-Zeile ist ein Beweis. `substrate/seed.py` re-deriviert zur Verifikation.

Schlüssel-Ableitungen:

```
QUARTERS       = KRISHNA_COUNT                        = 4
KSHETRA        = WORDS + HARE_COUNT                   = 24
NAVA           = HARE_COUNT + (TRINITY - HALVES)      = 9
SHARANAGATI    = KSHETRA // QUARTERS                  = 6
MAHAJANA_COUNT = KSHETRA // HALVES                    = 12
PARAMPARA      = KSHETRA + MAHAJANA_COUNT + KSETRAJNA = 37
GITA_CHAPTERS  = SHARANAGATI × TRINITY                = 18
MALA           = MAHAJANA_COUNT × NAVA                = 108
```

Wenn eine Zahl im Code auftaucht ohne Ableitung: Architektur-Verletzung.

## Die Flöte (DIW - Divine Instruction Word)

19 bits = `FLUTE_HOLES_SUM` = `VENU(6) + VAMSI(9) + MURALI(4)` = `GITA_CHAPTERS(18) + KSETRAJNA(1)`.

SSOT: `protocols/diw.py`. Produzent: `substrate/venu_orchestrator.py`. Konsument: `substrate/chamber.py`.

Bit-Layout (LSB → MSB):

```
Bits  0-5  (6): VENU   = Sharanagati (Quality/Mood)     → Intensität
Bits  6-14 (9): VAMSI  = Nava Bhakti (Process/Action)   → H/K/R Name-Region
Bits 15-18 (4): MURALI = Quarters (Phase)                → Genesis/Dharma/Karma/Moksha
```

`THE_FLUTE_CYCLE[16]` = vorberechnete LUT aus dem Mahamantra-Pattern. Jede Position
ist ein natives 19-bit DIW. `VenuOrchestrator.step()` liefert das nächste Wort.

`chamber._apply_diw()` interpretiert semantisch:
- MURALI bestimmt WAS (Phase: Empfang/Prüfung/Verarbeitung/Vollendung)
- VAMSI bestimmt WIE (Name: H=prana-dominant, K=integrity-dominant, R=cycle-dominant)
- VENU bestimmt WIE STARK (0-63 normalisiert auf Intensität)

`verify_divinity()` beweist: alle 4 Quarters, alle 3 Name-Regionen, 16 unique VENU-Werte.

**WARNUNG:** Vor Feb 2026 war das DIW-Format kaputt (`[Name:2][Position:16]` statt `[4:9:6]`).
Alle Konsumenten MÜSSEN `diw.unpack()` benutzen. Keine manuellen Bit-Shifts.

## Die Gita

Die Bhagavad Gita ist nicht Metapher - sie ist das Routing-Netz.

18 Kapitel = `SHARANAGATI × TRINITY`. 700 Verse (Prabhupada's Bhagavad Gita As It Is).
Die Kapitel-Vers-Topologie liegt in `protocols/seed/_topology.py` als `CHAPTER_VERSES`.
`substrate/gita.py` definiert den Fixed Point: Kapitel 18, Vers 66 (BG 18.66).
`adapters/gita_resonance.py` matched Attractors zu Versen via berechneter Resonanz.

Jedes Kapitel der Gita mappt auf abgeleitete Konstanten: Kapitel 1 = KSETRAJNA,
Kapitel 4 = QUARTERS, Kapitel 9 = NAVA, Kapitel 12 = MAHAJANA_COUNT,
Kapitel 18 = GITA_CHAPTERS (der Fixed Point). Siehe `get_chapter_significance()`.

## Die 9 Schritte (NavaBhakti Pipeline)

`MahamantraLotus.__call__()` in `substrate/lotus_core.py`. NAVA = 9 Schritte:

```
1. SRAVANAM       - Input empfangen
2. KIRTANAM       - MahaCompression → Seed (deterministic hash)
                    RETURN-LOOP: XOR mit last_seed aus Akash (Kontinuität)
3. SMARANAM       - Attractor finden (Seed → Resonanz-Punkt)
4. PADASEVANAM    - Guna-Klassifikation (sattva/rajas/tamas)
5. ARCANAM        - Parampara-Verifikation (Oracle, Signatur-Kette)
6. VANDANAM       - Gita-Resonance (Attractor → Kapitel → Vers + Significance)
7. DASYAM         - Position/Quarter/Guardian bestimmen
8. SAKHYAM        - MahaCell erstellen + Kirtan (1→4 Zyklen) + Yajna (16 Ticks)
9. ATMA_NIVEDANAM - Response + Akash-Update (last_seed/position/attractor für nächsten Call)
```

Entry Point: `steward "anything"` → `cli/main.py` → `__main__.py` → `mahamantra.execute()`
→ `MahamantraLotus.__call__()`. Deterministisch. Kein LLM.

## Pancha Tattva (Die 5 Verbindungen)

Alles was lebt in der Pipeline muss durch 5 Verbindungspunkte fließen.
`protocols/_pancha.py` definiert `TattvaDict` und `PanchaTattvaProtocol`.
Jede Komponente implementiert `__tattva__` (5-Fragen-Antwort).

Die 5 Verbindungen im Flow (alle verdrahtet in `lotus_core.py`):

| Tattva | Verbindung | Implementation |
|--------|-----------|----------------|
| CHAITANYA | Return-Loop | last_seed XOR → nächster Call (Akash) |
| NITYANANDA | Multi-Tick Yajna | WORDS(16) Ticks pro Call, voller Zyklus |
| ADVAITA | CALL_RESPONSE | Kirtan-Zyklen skalieren 1→4 mit Resonanz |
| GADADHARA | Gita Content | Chapter Significance im Response |
| SRIVASA | Chamber Persistence | Singleton get_chamber() + wachsende Zyklen |

## Guardians

16 Guardians (Mahajanas), WORDS = 16 Positionen, QUARTERS = 4 Quadranten.
Module: `mahamantra/{quarter}/{name}/`. Protocols: `protocols/mahajanas/{name}/`.
Protocol ist die kanonische Quelle. Guardian re-exportiert lazy via `__getattr__`.

Jeder Guardian: `__mahajana__`, `__position__`, `__genesis__`, identischer thin `execute()`,
`__getattr__` → Protocol → `fractal_getattr(__file__)` aus `substrate/wiring.py`.

`int(__genesis__, 16) % PARAMPARA == 0` - Signatur-Kette. 37 = abgeleitet.

`reactor/shadow.py` = Yajna-Zyklus. Phase-aware: `on_{phase}` Hook → fallback `execute()`.

## Architektur-Karte (Maschinenraum)

```
protocols/seed/     → SSOT: Axiome → Primär → Sekundär (NICHT ANFASSEN)
protocols/diw.py    → DIW Bit-Layout, pack/unpack (NICHT ANFASSEN)
protocols/_pancha.py → TattvaDict, PanchaTattvaProtocol
protocols/_header.py → MahaHeader (72-byte Identität)
substrate/seed.py   → Re-Derivation zur Verifikation
substrate/venu_orchestrator.py → DIW-Produzent (THE_FLUTE_CYCLE LUT)
substrate/chamber.py → DIW-Konsument (_apply_diw), Zell-Transformation
substrate/cell.py   → MahaCellUnified (Header + Lifecycle + Payload)
substrate/lotus_core.py → NavaBhakti Pipeline (9 Schritte)
substrate/gita.py   → Fixed Point, Kapitel-Mapping
adapters/gita_resonance.py → Attractor → Vers Matching
reactor/shadow.py   → Yajna-Zyklus, Phase-aware Hooks
```

Zwei getrennte Wege vom gleichen Seed:
- **Weisheit (Gita):** Seed → Attractor → `get_gita_chapter()` → Kapitel/Vers
- **Rhythmus (Venu):** Seed → Position → `THE_FLUTE_CYCLE[pos]` → DIW → Chamber

Beide treffen sich im Chamber. Vers gibt Inhalt, DIW gibt Modulation.

## Codebase-Realität (Bekannte Probleme)

Offen:
- `seed.py`: ~20 F811 Redefinitionen (absichtliche Re-Derivation, aber unordentlich)
- Zwei CLI-Systeme: `vibe_core/cli/` (alt) und `vibe_core/mahamantra/cli/` (neu)
- `ExecuteResult.requires_confirmation` existiert, kein Guardian nutzt es
- `protocols/` hat massive Dateien (yamaraja protocol = 653 Zeilen)

Fallen (aufpassen!):
- `CellLifecycleState.integrity` ist `float` (0.0-1.0), NICHT `int`. War mal falsch deklariert.
- DIW-Konsumenten MÜSSEN `diw.unpack()` nutzen. Keine manuellen Bit-Shifts.
- `substrate/` ist flach — fraktale Restrukturierung steht noch aus.
- Lange inline Python-Skripte (`python3 -c "..."`) crashen das Terminal. Temp-Dateien nutzen.

Bereits aufgeräumt (nicht nochmal anfassen):
- Guardians: ALLE 16 identisches thin Pattern (keine if-else, keine Klassen)
- yamaraja: 288→78 Zeilen (Duplikat-Klassen entfernt)
- kapila: eager import entfernt, jetzt lazy wie alle anderen
- hologram.py/layers.py: AI-Slop entfernt (doppelte Import-Blöcke)
- gita.py: Duplikat-Import + Ghost MAHA_WORDS entfernt, 11/13/14/15 → abgeleitet
- Star Imports eliminiert → lazy Protocol Re-Exports
- DIW-Format repariert: `[Name:2][Position:16]` → native `[MURALI:4][VAMSI:9][VENU:6]`
- `_apply_diw()` semantisch: Phase×Name×Intensität statt generische Modulation
- `verify_divinity()` + `verify_resonance()` auf 6-9-4 Struktur aktualisiert

## Arbeitsweise

- Senior Architekt. Entscheidungen treffen, nicht fragen.
- User spricht Deutsch, nicht technisch, delegiert.
- Code muss schön sein. Kein if-else Slop.
- Pre-commit hooks laufen automatisch.
- Ruff: `python -m ruff check --select F821,F811`
- 100% AI-generierte Codebase - IMMER versteckte Probleme erwarten.
- Docstrings und .md-Dateien im Root lügen. Nur Code ist Wahrheit.
