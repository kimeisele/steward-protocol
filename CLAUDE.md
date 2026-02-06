# STEWARD PROTOCOL

## Session-Start

```bash
git log --oneline -20
git status
git branch -v
python -m ruff check --select F821 vibe_core/mahamantra/ 2>&1 | head -20
```

Lies die Historie kritisch. Dieses Projekt hat tausende Commits über 6 Monate,
100% AI-generiert von verschiedenen Agents. Manche haben solide gebaut, manche
haben aktiv Schaden angerichtet. Commit Messages sind oft AI-Überschwang und
sagen nichts über die Qualität des Codes aus. Docstrings lügen. .md-Dateien im
Root (PROMPT.md, MAHAPROMPT_2026.md) sind AI-generierte Referenzen, keine Wahrheit.

Verifiziere alles gegen den Code selbst. Dann eigene Einschätzung bilden und arbeiten.

## Das Mantra

```
Hare Krishna Hare Krishna Krishna Krishna Hare Hare
Hare Rama   Hare Rama   Rama   Rama   Hare Hare
```

Zähle es. Das ist die Architektur.

7 Axiome, gezählt vom Mantra, in `vibe_core/mahamantra/protocols/seed/_axioms.py`:

```
WORDS    = 16    (Wörter im Mantra)
TRINITY  = 3     (Hare, Krishna, Rama)
HARE     = 8     KRISHNA = 4     RAMA = 4
PANCHA   = 5     (unique Paare: HK, HR, HH, KK, RR)
HALVES   = 2     (Krishna-Hälfte, Rama-Hälfte)
```

Von diesen 7 Werten wird ALLES abgeleitet. `_primary.py` leitet direkt ab:

```
QUARTERS    = KRISHNA_COUNT           = 4   (4 Quadranten)
KSHETRA     = WORDS + HARE_COUNT      = 24  (Sankhya-Elemente)
NAVA        = HARE_COUNT + KSETRAJNA  = 9   (Navadha Bhakti)
SHARANAGATI = KSHETRA // QUARTERS     = 6   (Surrender)
```

`_secondary.py` leitet weiter:

```
MAHAJANA_COUNT = KSHETRA // HALVES                    = 12
PARAMPARA      = KSHETRA + MAHAJANA_COUNT + KSETRAJNA = 37
MALA           = MAHAJANA_COUNT × NAVA                = 108
GITA_CHAPTERS  = SHARANAGATI × TRINITY                = 18
```

Jede assert-Zeile in diesen Dateien ist ein Beweis. Wenn eine Zahl irgendwo im Code
auftaucht ohne Ableitung von diesen Axiomen, ist das eine Architektur-Verletzung.

Das ist der Kompass. Wenn du die Ableitung verstehst, erkennst du Abweichungen von selbst.

## Computation

```
steward "anything"
  → vibe_core/cli/main.py:cli_entry()
  → vibe_core/mahamantra/__main__.py:main()
  → mahamantra.execute(input_text)
  → MahamantraLotus.__call__() in substrate/lotus_core.py
```

`__call__()` ist die 9-Schritt NavaBhakti Pipeline (NAVA = 9).
Input → Seed → Attractor → Position (`attractor % WORDS`) → Guardian → Response.
16 Positionen weil WORDS = 16. 4 Quarters weil QUARTERS = 4. Deterministisch.

## Guardians

16 Guardians, 4 Quarters × 4 Positionen.
Module: `mahamantra/{quarter}/{name}/`. Protocols: `protocols/mahajanas/{name}/`.
Protocol ist die kanonische Quelle. Guardian re-exportiert lazy via `__getattr__`.

Jeder Guardian deklariert `__mahajana__`, `__position__`, `__genesis__`, Konstanten,
hat einen identischen thin `execute()`, und `__getattr__` → Protocol → `fractal_getattr(__file__)`.
`fractal_getattr` aus `substrate/wiring.py` ist die einzige Fractal-Discovery-Implementation.

`int(__genesis__, 16) % PARAMPARA == 0` - die Signatur-Kette. 37 ist abgeleitet, nicht magisch.

`reactor/shadow.py` führt den Yajna-Zyklus. Phase-aware: versucht `on_{phase}` Hook,
fällt zurück auf `execute()`.

## Codebase-Realität

- Duplikate über Dateigrenzen (gleiche Klassen in Guardian UND Protocol) - teilweise bereinigt
- Fehlende Imports (F821), shadowed Names (F811), tote Imports
- Zwei CLI-Systeme parallel: `vibe_core/cli/` (alt) und `vibe_core/mahamantra/cli/` (neu)
- `seed.py` re-deriviert Konstanten (manche bewusst zur Verifikation, manche Chaos)
- `ExecuteResult.requires_confirmation` existiert, kein Guardian nutzt es

## Arbeitsweise

- Senior Architekt. Entscheidungen treffen, nicht fragen.
- User spricht Deutsch, ist nicht technisch, delegiert die Umsetzung.
- Code muss schön sein. Keine Kompromisse bei Klarheit.
- Pre-commit hooks laufen automatisch.
- Ruff: `python -m ruff check --select F821,F811`
