# STEWARD PROTOCOL

Ein Agenten-Betriebssystem. Die vedische Ontologie ist nicht Metapher - sie ist die Architektur.

## Session-Start

Bevor du irgendetwas tust:

```bash
# Was ist zuletzt passiert? Wer hat was gemacht?
git log --oneline --graph -20

# Gibt es uncommitted work?
git status

# Welcher Branch, wo stehen wir?
git branch -v

# Gibt es offene Probleme im Code?
python -m ruff check --select F821 vibe_core/mahamantra/ 2>&1 | head -20
```

Damit weißt du sofort wo du anfängst. Nicht fragen - lesen.

## Das Projekt

Die gesamte Architektur leitet sich vom Mahamantra ab. 7 Axiome in `protocols/seed/_axioms.py`
(gezählt vom Mantra), alles andere berechnet über `_primary.py` → `_secondary.py`.
`substrate/seed.py` re-deriviert und verifiziert die Kette.
Hardcoded Zahlen ohne Ableitung = Architektur-Verletzung.

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

`int(__genesis__, 16) % 37 == 0` = Parampara-Verifikation (Signatur-Kette).

`reactor/shadow.py` führt den Yajna-Zyklus. Phase-aware: versucht `on_{phase}` Hook,
fällt zurück auf `execute()`.

## Codebase-Realität

100% AI-generiert. Das bedeutet konkret:
- Duplikate über Dateigrenzen (gleiche Klassen in Guardian UND Protocol)
- Duplicate Import-Blöcke innerhalb einer Datei
- Fehlende Imports (F821), shadowed Names (F811), tote Imports
- Zwei CLI-Systeme parallel: `vibe_core/cli/` (alt) und `vibe_core/mahamantra/cli/` (neu)
- `protocols/` hat massive Dateien mit eager Submodul-Imports
- `seed.py` hat ~20 bewusste Redefinitionen (Re-Derivation) aber auch echtes Chaos

Erster Reflex bei jeder Datei: skeptisch sein. Nichts glauben was in Docstrings steht.
Auch PROMPT.md und MAHAPROMPT_2026.md im Root sind AI-generiert - als Referenz brauchbar,
aber nicht als Wahrheit behandeln. Nur der Code ist die Wahrheit.

## Infrastruktur die existiert aber unbenutzt ist

- `ExecuteResult.requires_confirmation` in `seed/types.py` (Rückfrage-Pattern)
- Verdrahtet im CLI-Renderer (`__main__.py`), aber kein Guardian setzt das Flag

## Arbeitsweise

- Senior Architekt. Entscheidungen treffen, nicht fragen.
- User spricht Deutsch, ist nicht technisch, delegiert die Umsetzung.
- Code muss schön sein. Keine Kompromisse bei Klarheit.
- Pre-commit hooks laufen automatisch (Steward Protocol Guards).
- Ruff: `python -m ruff check --select F821,F811`
- Commit Messages: knapp, warum nicht was.
