# STEWARD PROTOCOL

Ein Agenten-Betriebssystem. Die vedische Ontologie ist nicht Metapher - sie ist die Architektur.

## Seed-Derivation

7 Axiome in `protocols/seed/_axioms.py`, gezählt vom Mahamantra.
Primäre Ableitungen in `_primary.py`, sekundäre in `_secondary.py`.
`substrate/seed.py` re-deriviert und verifiziert die Kette.
Hardcoded Zahlen ohne Ableitung = Architektur-Verletzung.

## Computation

```
steward "anything"
  → vibe_core/cli/main.py:cli_entry()
  → vibe_core/mahamantra/__main__.py:main()
  → mahamantra.execute(input_text)
  → MahamantraLotus.__call__() in substrate/lotus_core.py
```

`__call__()` ist die 9-Schritt NavaBhakti Pipeline. Kein argparse, keine Subcommands.
Input → Seed → Attractor → Position (`attractor % 16`) → Guardian → Response.
`forced_lagna=0` → deterministisch. Kein LLM.

## 16 Guardians (Mahajanas)

4 Quarters × 4 Positionen. Guardian-Module leben in `mahamantra/{quarter}/{name}/`.
Protocol-Definitionen leben in `protocols/mahajanas/{name}/` - das ist die kanonische Quelle.

Jeder Guardian:
- Deklariert `__mahajana__`, `__position__`, `__genesis__`, Konstanten (`POSITION`, `QUARTER`, `OPCODE`, `PARAMPARA_VECTOR`)
- Hat einen identischen thin `execute(input_text, context=None) → dict`
- Exportiert alles andere lazy via `__getattr__` → Protocol-Modul → `fractal_getattr(__file__)`
- `fractal_getattr` aus `substrate/wiring.py` ist die einzige Fractal-Discovery-Implementation

Keine if-else-Logik in execute(). Keine Klassen im Guardian. Keine eager imports außer `typing`.

## Parampara

`int(__genesis__, 16) % 37 == 0` verbindet jeden Guardian zur Kette.
Die Verifikation läuft in `lotus_core.py` beim Routing.

## ShadowReactor

`reactor/shadow.py` führt den Yajna-Zyklus. Phase-aware: versucht `on_{phase}` Hook,
fällt zurück auf `execute()`. Das ist der Mechanismus der Guardian-Execution im NavaBhakti-Flow.

## Codebase-Realität

100% AI-generiert. Das bedeutet konkret:
- Duplikate über Dateigrenzen hinweg (gleiche Klassen in Guardian UND Protocol)
- Duplicate Import-Blöcke innerhalb einer Datei
- Tote Imports, fehlende Imports (F821), shadowed Names (F811)
- `seed.py` hat ~20 bewusste Redefinitionen (Re-Derivation), aber auch echtes Chaos
- Zwei CLI-Systeme existieren parallel: `vibe_core/cli/` (alt) und `vibe_core/mahamantra/cli/` (neu)
- `protocols/` hat massive Dateien mit eager Submodul-Imports

Erster Reflex bei jeder Datei: skeptisch sein. `ruff check --select F821` laufen lassen.

## Rückfrage-Infrastruktur

`ExecuteResult.requires_confirmation` existiert (`seed/types.py`).
Verdrahtet im CLI-Renderer (`__main__.py`). Kein Guardian setzt das Flag bisher.

## Arbeitsweise

- Senior Architekt. Entscheidungen treffen, nicht fragen.
- User spricht Deutsch, ist nicht technisch, delegiert die Umsetzung.
- Code muss schön sein. Keine Kompromisse bei Klarheit.
- Pre-commit hooks laufen automatisch (Steward Protocol Guards).
- Ruff ist der Linter. `python -m ruff check --select F821,F811`
