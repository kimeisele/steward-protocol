# CLI SPLIT-BRAIN AUDIT
## Date: 2025-02-21
## Status: ACTIVE — Consolidation in progress

## THE KING (Source of Truth)

| Component | File | Lines | Role |
|-----------|------|-------|------|
| Entry Point | `__main__.py` | 222 | `mahamantra.execute(input)` → render |
| VM Engine | `substrate/vm/mantra_vm.py` | 365 | 9-step NavaBhakti dispatch, branchless |
| Lotus Core | `substrate/lotus_core.py` | 1260 | `__call__()` → `execute_cycle()`, gates at boundary |

**The correct flow:**
```
input → MahaCompression → seed → MahaModularSynth.transform(seed) → attractor → attractor % 16 → position → guardian → 9 NavaBhakti → 27-key result
```

## SPLIT-BRAIN PATHS (must die)

### SB-1: cli/auto.py `_get_position()` — CRITICAL
- **Bug**: Uses `(seed >> 24) & 0xF` instead of `attractor % 16`
- **Impact**: Same input → different position than `__call__()`
- **No synth transform**, no attractor computation
- **Also**: Builds its own discovery engine (687 lines) that duplicates VM routing
- **Fix**: Delete `_get_position()`, route through `mahamantra.execute()`

### SB-2: cli/engine.py — REDUNDANT
- **488 lines** of ANOTHER registry/routing engine
- `register()`, handlers, capabilities — all manual wiring
- **Contradicts**: "ZERO MANUAL WIRING" principle
- **Fix**: Delete entirely. VM handles routing.

### SB-3: cli/cell_wrapper.py — DUPLICATE
- **107 lines** doing its own `MahaCompression().compress()` + `MahaCellUnified.create()`
- **Duplicates**: `kirtanam()` + `sakhyam()` from the VM pipeline
- Called in `entry.py:150-153` BEFORE `cli_auto.execute()` — double work
- **Fix**: Delete. VM creates cells in `sakhyam()`.

### SB-4: cli/entry.py — KEYWORD ROUTING
- **312 lines** with if-else chains: `if command == "chat"`, `if command == "capabilities"`
- **Contradicts**: "NO HARDCODED COMMANDS" principle from `__main__.py`
- **Fix**: Replace with `mahamantra.execute(input)` like `__main__.py` already does.

### SB-5: chat.py — PARALLEL UNIVERSE
- **886 lines** with own routing (`get_guardian_for_message()` via `ChatService._compute_resonance()`)
- **3 hardcoded dicts**: `GUARDIAN_DHARMA`, `GUARDIAN_WORDS`, `GUARDIAN_QUARTERS` — SSOT duplication
- **Never touches `__call__()`** — goes directly to LLM provider
- **Fix**: Use `mahamantra.execute(message)` for position/guardian, then LLM as I/O side-effect

### SB-6: commands.py — MIXED
- `cli_chant` → `lotus.execute()` ✅ CORRECT
- `cli_listen` → `lotus.execute()` ✅ CORRECT
- `cli_resolve` → `lotus.execute()` ✅ CORRECT
- `cli_serve` → `lotus.execute()` ✅ CORRECT
- `cli_veda` → `lotus.execute()` ✅ CORRECT
- `cli_vimana_serve` → own `SankirtanChamber.create()` ⚠️ (server = different concern)
- **Problem**: These are hardcoded command NAMES. The system should discover capabilities, not register commands.

### SB-7: cli/protocol.py — OVERENGINEERED
- **802 lines** of types (CLIResult, CLIOutput, CLICapability, CLIState, CLIHealth, CLIError, CLIParameter...)
- The VM already returns a 27-key result dict. Why does CLI need its own type system?
- **Fix**: Use VM result dict directly. Render it.

## WHAT SHOULD REMAIN (I/O concerns)

| File | Lines | Role | Keep? |
|------|-------|------|-------|
| `__main__.py` | 222 | THE entry point | ✅ YES — this IS the CLI |
| `cli/map.py` | 342 | System visualization | ✅ YES — pure I/O rendering |
| `cli/observe.py` | 280 | Monitoring/observability | ✅ YES — pure I/O |
| `cli/event_bridge.py` | 193 | Event fetching | ✅ YES — pure I/O |
| `cli/samskara.py` | 153 | State persistence | ✅ YES — pure I/O |
| `cli/bridge.py` | 234 | Gateway bridge | ⚠️ REVIEW |

## TARGET ARCHITECTURE

```
User Input (text/voice)
    │
    ▼
__main__.py (thin shell, ~50 lines)
    │
    ▼
mahamantra.execute(input)  ← THE ONE CALL
    │
    ▼
mantra_vm.execute_cycle()  ← 9 NavaBhakti, branchless
    │
    ├── position/guardian/verse/cell (computation)
    ├── guardian_result (execution via ShadowReactor)
    └── I/O side-effects triggered by gates:
        ├── LLM chat (if guardian has chat capability)
        ├── Audio synthesis (if DIW output requested)
        ├── Network streaming (if vimana destination)
        └── Healing (if dharma quarter + violations)
    │
    ▼
render(result)  ← Format 27-key dict for terminal
    │
    ▼
stdout
```

## METRICS
- Current CLI layer: **7505 lines** across 16 files
- Target CLI layer: **~300 lines** (thin shell + renderers)
- VM (already correct): **365 lines**
- Ratio improvement: 20:1 → 1:1
