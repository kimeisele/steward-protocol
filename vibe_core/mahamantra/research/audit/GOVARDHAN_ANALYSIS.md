# GOVARDHAN ANALYSIS — Why Protection Isn't Automatic (And How To Fix It)

**Date**: 2026-02-16
**Branch**: mahamantra/split-brain-healing
**Status**: ANALYSIS — No code changes yet

---

## The Metaphor (Why It Matters)

Krishna lifts Govardhan Hill. ALL living entities underneath are protected.
Not opt-in. Not manual registration. Not "if you happen to be discovered at boot time."
**Automatic. Permanent. Universal.**

The codebase has the TECH for this. But the WIRING is manual.
That's why it doesn't scale. That's why every agent adds more fragmentation.

---

## What EXISTS (The Weapons Already Built)

| Component | File | What It Does |
|-----------|------|-------------|
| `BalaramaProxy` | `substrate/proxy.py` | Wraps a module: injects `mahamantra`, replaces `Path` → `_GovernedPath`, attaches to heartbeat gated per position |
| `_GovernedPath` | `substrate/proxy.py` | Replaces `pathlib.Path` — all `write_text()`/`write_bytes()` route through `bridge.offer()` |
| `bridge.offer()` | `substrate/bridge.py` | THE ONE CHANNEL. Purpose → Position → Mahajana → Reactor Loop → Execution. Fires PARSE + SYNC gates. |
| `wrap_cell()` | `substrate/bridge.py` | Auto-wraps ANY content → MahaCell (72-byte header + typed payload) |
| `io_sentinel` | `substrate/io_sentinel.py` | Runtime monkey-patch on `json.dump` — detects rogue writers, logs them |
| `TattvaRegistry` | `substrate/tattva_registry.py` | Gate providers with capability check. Rejected = violation logged. |
| `TattvaGate` | `substrate/pancha_tattva.py` | 5 Gates: PARSE → VALIDATE → EXECUTE → RESULT → SYNC |
| `assert_watertight()` | `substrate/wiring.py` | Military grade validator — FAIL FAST if anything is wrong |
| `__call__()` | `substrate/lotus_core.py` | Pure Functional Core. 9 NavaBhakti steps. Deterministic. THE heart. |

**All of this works.** The tech is real. It's tested. It's production-ready.

---

## What's MISSING (The One Gap)

### Current: Manual Wrapping at Boot Time

```python
# boot_orchestrator.py line 584-611
for pos, guardian, instance in kernel_positions.all_active():
    mod_name = getattr(instance, "__module__", None)
    if mod_name:
        proxy = wrap_service(mod_name, silent=True)
```

**Problems:**
1. Only modules discovered at boot are wrapped
2. Anything imported AFTER boot bypasses the proxy
3. New files added to the repo are NOT automatically covered
4. 16+ files import `get_mahamantra()` directly, bypassing all governance
5. 27+ files do ungoverned I/O (no `_GovernedPath`, no `bridge.offer()`)

### What's Needed: Automatic Protection via Python Import Hook

Python has `sys.meta_path` — a list of "finders" that intercept EVERY `import` statement.
When you do `import vibe_core.anything`, Python asks each finder: "Can you handle this?"

**The Govardhan Finder** would:
1. Intercept every `import` within `vibe_core/`
2. Let Python load the module normally
3. AFTER loading, automatically apply the BalaramaProxy treatment:
   - Replace `Path` with `_GovernedPath` in the module's namespace
   - Inject `mahamantra` reference
   - Register with TattvaRegistry
   - Derive identity from folder structure (already implemented in `_extract_identity()`)
4. No manual wrapping needed. No boot-time discovery needed. **Every module, automatically.**

---

## Design: GovardhanFinder

```
sys.meta_path.insert(0, GovardhanFinder())

                    ┌─────────────────────────────────┐
                    │         GOVARDHAN HILL           │
                    │    (sys.meta_path import hook)   │
                    │                                  │
   import X ───────►  1. Let Python load module        │
                    │  2. Post-load: inject governance  │
                    │     - Path → _GovernedPath       │
                    │     - inject mahamantra ref       │
                    │     - register in TattvaRegistry  │
                    │     - derive identity from folder │
                    │  3. Return governed module        │
                    │                                  │
                    └─────────────────────────────────┘

Result: EVERY module under vibe_core/ is automatically governed.
New file? Governed on first import. No manual step needed.
```

### What It Uses (ALL EXISTING Tech)

- `_GovernedPath` from `proxy.py` — already built
- `bridge.offer()` from `bridge.py` — already built
- `_extract_identity()` logic from `BalaramaProxy` — already built
- `TattvaRegistry` from `tattva_registry.py` — already built
- `io_sentinel` from `io_sentinel.py` — already built

### What It Does NOT Do

- Does NOT create a new abstraction layer
- Does NOT require changes to existing modules
- Does NOT break existing imports
- Does NOT add new dependencies

### Risks

1. **Circular imports**: The hook itself imports from `mahamantra.substrate`. Must be careful about import order. Solution: lazy initialization — hook activates only after mahamantra core is loaded.
2. **Performance**: Post-import processing adds ~1ms per module. For 1734 files, that's ~1.7s total at first boot. Acceptable.
3. **Debugging**: Stack traces may show proxy frames. Solution: `__wrapped__` attribute for transparency.
4. **Opt-out**: Some modules (seed, protocols, core substrate) should NOT be wrapped (they ARE the governance). Solution: allowlist of "sacred" paths that pass through unchanged.

### Sacred Paths (Not Wrapped — They ARE the Governance)

```
vibe_core/mahamantra/protocols/_seed.py      # THE axioms
vibe_core/mahamantra/protocols/_seed_cell.py # Cell format
vibe_core/mahamantra/substrate/proxy.py      # The proxy itself
vibe_core/mahamantra/substrate/bridge.py     # The bridge itself
vibe_core/mahamantra/substrate/lotus_core.py # The pure core
vibe_core/mahamantra/substrate/wiring.py     # The wiring itself
vibe_core/mahamantra/substrate/pancha_tattva.py # The gates
vibe_core/mahamantra/substrate/io_sentinel.py   # The sentinel
```

---

## Implementation Plan

### Step 1: Build GovardhanFinder (sys.meta_path hook)
- Single file: `vibe_core/mahamantra/substrate/govardhan.py`
- Uses `importlib.abc.MetaPathFinder` + `importlib.abc.Loader`
- Post-import processing: inject `_GovernedPath`, `mahamantra`, register identity
- Sacred path exclusion list
- Lazy activation (only after mahamantra core is loaded)

### Step 2: Activate at Boot
- `boot_orchestrator.py`: ONE LINE — `from vibe_core.mahamantra.substrate.govardhan import raise_hill; raise_hill()`
- Replaces the manual `wrap_service()` loop (lines 584-611)
- BalaramaProxy wrapping becomes automatic, not manual

### Step 3: Upgrade io_sentinel
- Currently: observation only (logs rogue writers)
- Upgrade: enforcement mode (block + redirect through bridge.offer())
- Gated: starts in observation, switches to enforcement after boot completes

### Step 4: Verify
- `assert_watertight()` already exists — run it after boot
- Add: `assert_governed()` — verify ALL loaded modules have governance
- CI check: any module without governance = build failure

---

## The Result

```
BEFORE (Manual):
  1734 files → ~20 manually wrapped at boot → 1714 ungoverned
  New file added → ungoverned until someone manually wraps it
  Agent adds code → more fragmentation

AFTER (Govardhan):
  1734 files → ALL automatically governed on import
  New file added → governed on first import, zero manual steps
  Agent adds code → automatically governed, zero fragmentation
```

**Krishna lifts the hill. Everyone underneath is protected.**
**Not opt-in. Automatic. Permanent. Universal.**

---

## Decision Needed

This analysis describes the architecture. Implementation requires:
1. Confirmation that this is the right direction
2. Decision on enforcement mode (observation vs blocking for io_sentinel)
3. Decision on sacred paths list

No code changes have been made. This is analysis only.
