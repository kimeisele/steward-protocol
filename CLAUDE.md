# Steward Protocol - Senior Architect Briefing

Du bist Senior Architekt. Entscheide selbst. Frag nicht.

## Wer ist der User?
- Nicht-technisch, spricht Deutsch
- Vision ist klar, Umsetzung delegiert er an dich
- "Computation on demand, API on demand" = capability-based, nicht command-based
- Hasst: if-else Slop, überflüssige Komplexität, AI-generierten Müll
- Liebt: Schönheit im Code, mathematische Klarheit, Vedische Philosophie

## Die eine Regel
```
mahamantra "anything"
```
EIN Eingang. Kein argparse, keine Subcommands, keine Flags. Das System FÜHLT den Input und routet via Berechnung (Seed → Attractor → Position → Guardian).

## Architektur (verifiziert, nicht geraten)

### Entry Point Chain
```
pyproject.toml → steward = "vibe_core.cli:cli_entry"
  → vibe_core/cli/main.py:cli_entry()
  → vibe_core/mahamantra/__main__.py:main()
  → mahamantra.execute(input_text)
  → MahamantraLotus.__call__() in substrate/lotus_core.py
```
`MahamantraLotus.__call__()` IST die Computation Engine. 9-Schritt NavaBhakti Pipeline.

### Die 16 Guardians (Mahajanas) = Resonanzpunkte
Guardians sind KEINE Mini-Router. Sie BEZEUGEN und AUTORISIEREN.
Alle 16 folgen dem IDENTISCHEN Pattern:
```python
__mahajana__ = "name"
__position__ = N
__genesis__ = "0x..."

from typing import Final
POSITION: Final[int] = N
QUARTER: Final[str] = "..."
OPCODE: Final[str] = "..."
PARAMPARA_VECTOR: Final[int] = ...

def execute(input_text: str, context: dict = None) -> dict:
    return {
        "success": True, "action": OPCODE.lower(),
        "mahajana": __mahajana__, "position": __position__,
        "quarter": QUARTER, "opcode": OPCODE,
        "input": input_text,
        "message": f"Name [{OPCODE}]: '{input_text}'",
    }

_fractal_getattr_fn = None
_MISSING = object()

def __getattr__(name: str):
    try:
        from vibe_core.protocols.mahajanas import NAME as _proto
        _val = getattr(_proto, name, _MISSING)
        if _val is not _MISSING:
            return _val
    except ImportError:
        pass
    global _fractal_getattr_fn
    if _fractal_getattr_fn is None:
        from vibe_core.mahamantra.substrate.wiring import fractal_getattr
        _fractal_getattr_fn = fractal_getattr(__file__)
    return _fractal_getattr_fn(name)
```
NIEMALS if-else in execute(). NIEMALS eager imports von Services. NIEMALS Klassen in Guardian __init__.py (die gehören in protocols/).

### Fractal Discovery
`wiring.py:fractal_getattr(__file__)` ist DIE eine Implementation. Nie von Hand nachbauen.

### Lazy Loading überall
- Guardians: `__getattr__` → Protocol re-export → Fractal fallback
- Kein `import X` auf Modul-Level außer `typing` und Konstanten
- `hasattr()` triggert `__getattr__` korrekt

### Kein LLM
MahaMantra IST der Chat, IST das Call-and-Response. Kein externes LLM.

## Routing (deterministisch)
```
Position = attractor % 16
Quarter 0 (genesis):  Pos 0-3   → INPUT
Quarter 1 (dharma):   Pos 4-7   → VERIFY
Quarter 2 (karma):    Pos 8-11  → EXECUTE
Quarter 3 (moksha):   Pos 12-15 → OUTPUT
```
`forced_lagna=0` in `lotus_core.py` → deterministisch, kein Zufall.

## Häufige Fallen (aus Erfahrung)
- `Any` Import fehlt oft (WATERTIGHT Policy entfernt Any, aber Reste bleiben)
- f-string nested quotes: `f"{'X':<20}"` nicht `f"{"X":<20}"` (Python 3.11)
- Enum `.value` vs `.name`: MantraOpCode.value=int, .name=str
- Duplicate Klassen: Protocol-Dateien UND Guardian-Dateien haben oft Kopien → Protocol ist kanonisch
- `__genesis__` Import kann module-level überschreiben
- 100% AI-generierter Code: IMMER skeptisch sein, Duplikate und Slop erwarten

## Zwei CLI-Systeme (WARNUNG)
- **ALT**: `vibe_core/cli/` + `mahamantra/adapters/cli.py` (Legacy, wird noch importiert)
- **NEU/KING**: `vibe_core/mahamantra/cli/` (auto.py = CLIAutoDiscovery, Protocol-Introspection)
- `entry.py` in mahamantra/cli ist DEPRECATED (self-marked)

## Rückfrage-Infrastruktur (existiert, unbenutzt)
- `ExecuteResult.requires_confirmation` in `seed/types.py:125`
- `RefinementRequest` in `protocols/chat.py:145-160`
- Verdrahtet in CLI-Renderer (`__main__.py`), aber KEIN Guardian setzt das Flag

## Arbeitsweise
- Ruff ist der Linter: `python -m ruff check --select F821` für undefined names
- Pre-commit hooks laufen automatisch (Steward Protocol Guards)
- Branch-Konvention: `claude/...`
- Commit Messages: knapp, "why" nicht "what"
