# TASK 01: ROOT FILES AUDIT

**Status:** DONE
**Estimated Time:** 1-2 hours
**Priority:** CRITICAL (These are the core files)

---

## QUESTION

What are the root-level files in mahamantra/ and what do they do?
Are there redundancies between them?

---

## FILES TO READ

```
vibe_core/mahamantra/
├── __init__.py         # Main exports (Lazy Loading Facade)
├── __main__.py         # CLI Entry Point
├── _lotus.py           # Base LotusNode/LotusPath infrastructure
├── _mahamantra_lotus.py # Root node implementation (MahamantraLotus)
├── _types.py           # TypedDict definitions (Watertight)
├── cell.py             # MahaCellUnified (Header + Lifecycle)
├── chamber.py          # SankirtanChamber (Resonance Space)
├── chat.py             # MahajanaChat (Guardian Chat Infrastructure)
├── commands.py         # CLI Command Logic (Stateless Handlers)
├── orchestrator.py     # VenuOrchestrator (Musical Logic)
├── research_gateway.py # Bridge to Nrisimha Heartbeat
```

---

## CHECKLIST

For each file, answer:

### __init__.py
- [x] What does it export? `MahamantraLotus`, `mahamantra` singleton, constants, types.
- [x] Does it re-export from subfolders? Yes, extensively via `__getattr__` for lazy loading.
- [x] Is there a `mahamantra` singleton here? Yes, `mahamantra` (via `get_mahamantra()`).

### __main__.py
- [x] What happens when you run `python -m vibe_core.mahamantra`? Runs `main()`, parses args, calls `commands.py`.
- [x] Does it duplicate cli/entry.py? No, it's a dedicated entry point for the `mahamantra` module context.

### _lotus.py vs _mahamantra_lotus.py
- [x] What is the difference between these two? `_lotus.py` is the generic fractal tree infrastructure. `_mahamantra_lotus.py` is the specific Root implementation.
- [x] Are they redundant? No, clean separation of concerns (Base vs Implementation).
- [x] Which one is used? `_mahamantra_lotus.py` uses `_lotus.py`.

### _types.py
- [x] What types are defined here? `TickState`, `RouteResult`, `VibrationState`, `AkashState`, `ExecuteResult`, `LilaState`, `GitaRoute`.
- [x] Are they used elsewhere? Yes, throughout the module.
- [x] Do they overlap with protocols/? No, `protocols/` has Interfaces, this has Data Structures (`TypedDict`).

### cell.py
- [x] MahaCellUnified structure? Composition of `MahaHeader`, `CellLifecycleState`, and generic `Payload`.
- [x] Header + Lifecycle pattern? Yes.
- [x] How does it relate to chamber.py? Chamber transforms Cell instances via `dance()`.

### chamber.py
- [x] SankirtanChamber structure? Owns `VenuOrchestrator` and `SiksastakamRegistry`.
- [x] Does it own the Orchestrator? Yes.
- [x] dance(), kirtan(), sankirtan() methods? Yes, all implemented.

### chat.py
- [x] What is this for? Infrastructure for Guardian-specific chat (`MahajanaChat`), routing to `runtime.providers`.
- [x] Does it duplicate cli/chat functionality? It serves as the backend logic for Guardian chat, likely used by CLI or Services.
- [x] Gateway integration? Yes, integrates with `vibe_core.runtime.providers`.

### commands.py
- [x] What commands are defined? `cli_chant`, `cli_listen`, `cli_resolve`, `cli_serve`, `cli_veda`.
- [x] How do they relate to cli/? These are the implementation handlers.
- [x] Are there duplicate command definitions? No, these are the stateless logic blocks.

### orchestrator.py
- [x] VenuOrchestrator with 19-bit DIW? Yes.
- [x] THE_FLUTE_CYCLE LUT? Yes, pre-computed.
- [x] route(), harmonize(), verify_divinity()? Yes.

### research_gateway.py
- [x] What is this? Bridge connecting research tracking to `NrisimhaWatchdog` (Heartbeat).
- [x] Is it production or experimental? Production infrastructure to manage the lifecycle of research modules ("Rollout").

---

## FINDINGS

(Fill in as you read each file)

### __init__.py
```
VERDICT: [x] Essential [ ] Redundant [ ] Unknown
NOTES: Critical facade. Implements the "Siksastakam Architecture" (Pure Lazy Loading). Import time optimization (<20ms). Purified of research dependencies. ✓
```

### __main__.py
```
VERDICT: [x] Essential [ ] Redundant [ ] Unknown
NOTES: Standard entry point. Thin wrapper around `commands.py`.
```

### _lotus.py
```
VERDICT: [x] Essential [ ] Redundant [ ] Unknown
NOTES: Core infrastructure for the "Lotus" pattern (Directory-as-Object auto-discovery).
```

### _mahamantra_lotus.py
```
VERDICT: [x] Essential [ ] Redundant [ ] Unknown
NOTES: The Root Object. Implements `__call__` (The Mantra), `vibrate`, `tick`. Separated from `_lotus.py` to keep `__init__.py` clean. Purified: Now uses `substrate.mantra` instead of experimental research logic. ✓
```

### _types.py
```
VERDICT: [x] Essential [ ] Redundant [ ] Unknown
NOTES: "Watertight" TypedDicts. Ensures type safety without `Any`.
```

### cell.py
```
VERDICT: [x] Essential [ ] Redundant [ ] Unknown
NOTES: Defines `MahaCellUnified`. The fundamental unit. Clean composition pattern.
```

### chamber.py
```
VERDICT: [x] Essential [ ] Redundant [ ] Unknown
NOTES: The Engine. `SankirtanChamber`. Orchestrates the interaction between Time (`Orchestrator`) and Space (`Registry`).
```

### chat.py
```
VERDICT: [x] Essential [ ] Redundant [ ] Unknown
NOTES: Provides `MahajanaChat` and `FloodedMahajanaChat`. Necessary for Guardian persona implementation.
```

### commands.py
```
VERDICT: [x] Essential [ ] Redundant [ ] Unknown
NOTES: The Logic Library for CLI commands. Stateless and separated from argument parsing.
```

### orchestrator.py
```
VERDICT: [x] Essential [ ] Redundant [ ] Unknown
NOTES: `VenuOrchestrator`. Implements the math/music logic. LUT-based for O(1) performance.
```

### research_gateway.py
```
VERDICT: [x] Essential [ ] Redundant [ ] Unknown
NOTES: Essential bridge for the "Research -> Production" pipeline. Connects to Kernel Heartbeat.
```

---

## RELATIONSHIPS

Draw connections between files:

```
orchestrator.py (Time/Logic)
     ↓
chamber.py (Owns Orchestrator & Registry)
     ↓ transforms
cell.py (Unit of Computation)

_mahamantra_lotus.py (Root) --lazy-loads--> chamber.py
commands.py (Handlers) --uses--> chamber.py, cell.py
```

---

## REDUNDANCY CHECK

| File A | File B | Overlap? | Action |
|--------|--------|----------|--------|
| _lotus.py | _mahamantra_lotus.py | No | Distinct roles (Base vs Root Implementor) |
| chat.py | cli/? | Distinct | chat.py is Domain Logic, cli/ is interface |
| commands.py | cli/? | Distinct | commands.py is Logic, cli/ is routing |

---

## SUMMARY

(Write after completing audit)

**Essential Files:**
- All 11 files in the root are essential.
- The structure follows a clear pattern:
    - **Core Data**: `cell.py`, `_types.py`
    - **Core Logic**: `orchestrator.py`, `chamber.py`
    - **Infrastructure**: `_lotus.py`, `_mahamantra_lotus.py`, `__init__.py`
    - **Interface**: `commands.py`, `__main__.py`, `chat.py`, `research_gateway.py`

**Redundant Files:**
- None found.

**Unknown/Needs More Investigation:**
- None.

---

*Last updated: 2026-01-31*
