# STEWARD PROTOCOL

Ein Agenten-Betriebssystem. Vedische Ontologie als Architektur, nicht als Metapher.

## Session-Start

Bevor du irgendetwas tust:

```bash
git log --oneline -20          # Was ist zuletzt passiert?
git status                     # Uncommitted work?
git branch -v                  # Welcher Branch?
python -m ruff check --select F821 vibe_core/mahamantra/ 2>&1 | head -20
```

Nicht fragen - lesen. Dann eigene Einschätzung bilden und arbeiten.

Wichtig: 431+ Commits, 6 Monate Entwicklung, 100% AI-generiert. Verschiedene Agents
haben zu verschiedenen Zeiten gebaut, refactored, manchmal aktiv Schaden angerichtet.
Die Commit-Historie ist kein sauberes Changelog sondern ein Schlachtfeld. Commit Messages
wie "HOLOGRAPHIC FRACTAL WIRING - Complete Surrender" oder "Military Grade Watertight"
sind typischer AI-Überschwang - der Code dahinter kann solide sein oder Chaos.

Vertraue keiner Datei blind. Nicht dem Code, nicht den Docstrings, nicht den .md-Dateien
im Root (PROMPT.md, MAHAPROMPT_2026.md - AI-generiert, als Kontext brauchbar, nicht als
Wahrheit). Verifiziere was du findest gegen das was der Code tatsächlich tut.

## Das Projekt

Die Architektur leitet sich vom Mahamantra ab. 7 Axiome in `protocols/seed/_axioms.py`
(gezählt vom Mantra), alles andere berechnet über `_primary.py` → `_secondary.py`.
`substrate/seed.py` re-deriviert und verifiziert. Hardcoded Zahlen ohne Ableitung sind
Architektur-Verletzungen.

Der einzige Entry Point:

```
steward "anything"
  → vibe_core/cli/main.py:cli_entry()
  → vibe_core/mahamantra/__main__.py:main()
  → mahamantra.execute(input_text)
  → MahamantraLotus.__call__() in substrate/lotus_core.py
```

`__call__()` ist die 9-Schritt NavaBhakti Pipeline.
Input → Seed → Attractor → Position (`attractor % 16`) → Guardian → Response.
`forced_lagna=0` → deterministisch. Kein LLM. Kein argparse.

## Guardians

16 Guardians (Mahajanas), 4 Quarters × 4 Positionen.
Module: `mahamantra/{quarter}/{name}/`. Protocols: `protocols/mahajanas/{name}/`.
Protocol ist die kanonische Quelle. Guardian re-exportiert lazy via `__getattr__`.

Jeder Guardian deklariert `__mahajana__`, `__position__`, `__genesis__`, Konstanten,
hat einen identischen thin `execute()`, und `__getattr__` → Protocol → `fractal_getattr(__file__)`.
`fractal_getattr` aus `substrate/wiring.py` ist die einzige Fractal-Discovery-Implementation.

Keine if-else in execute(). Keine Klassen im Guardian. Keine eager imports außer `typing`.

`int(__genesis__, 16) % 37 == 0` = Parampara-Verifikation.

`reactor/shadow.py` führt den Yajna-Zyklus. Phase-aware: versucht `on_{phase}` Hook,
fällt zurück auf `execute()`.

## Bekannte Baustellen

- Zwei CLI-Systeme parallel: `vibe_core/cli/` (alt) und `vibe_core/mahamantra/cli/` (neu)
- `protocols/` hat massive Dateien mit eager Submodul-Imports
- `seed.py` hat ~20 Redefinitionen (manche bewusst, manche Chaos)
- `ExecuteResult.requires_confirmation` existiert (Rückfrage-Pattern), kein Guardian nutzt es
- Duplikate über Dateigrenzen (gleiche Klassen in Guardian UND Protocol) sind teilweise bereinigt
  aber erwarte weitere

## Arbeitsweise

- Senior Architekt. Entscheidungen treffen, nicht fragen.
- User spricht Deutsch, ist nicht technisch, delegiert die Umsetzung.
- Code muss schön sein. Keine Kompromisse bei Klarheit.
- Pre-commit hooks laufen automatisch (Steward Protocol Guards).
- Ruff: `python -m ruff check --select F821,F811`
- Commit Messages: knapp, warum nicht was.
