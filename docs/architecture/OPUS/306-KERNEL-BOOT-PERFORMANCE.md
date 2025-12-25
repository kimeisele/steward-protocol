# OPUS-306: KERNEL BOOT PERFORMANCE - CRITICAL

> **Status**: READY FOR SONNET
> **Date**: 2025-12-25
> **Author**: Claude Opus 4.5 (Senior Steward)
> **Priority**: P0 - BLOCKING ALL TEST SUITES
> **Next**: OPUS-307 (CI/CD Restoration)

---

## THE PROBLEM

Kernel boot takes **102 seconds**. Target: **< 5 seconds**.

This is causing:
- All kernel-dependent tests to timeout (default: 30s)
- 13 test "errors" that are actually just timeouts
- Slow development cycle
- CI/CD blocked

### Boot Profile (2025-12-25)

```
10:19:04.920 - SARGA Boot Sequence start
10:19:08.739 - MANAS booting cognitive systems     (+4s)
10:19:32.908 - Sense Manager booting              (+28s total)
10:19:58.605 - Sync Holon complete                (+54s total)
10:19:58.785 - PranaSense registered              (+54s total)
10:20:34.387 - Boot optimizer plugin active       (+90s total)
10:20:46.???  - Boot complete                     (~102s total)
```

### Bottleneck Analysis

| Phase | Duration | % of Boot | Issue |
|-------|----------|-----------|-------|
| Initial boot → MANAS | 4s | 4% | OK |
| MANAS → Sense Manager | 24s | 24% | **SLOW** |
| Sense Manager boot | 26s | 25% | **SLOW** |
| Plugin boot phase | 36s | 35% | **SLOW** |
| Finalization | 12s | 12% | Slow |

---

## ROOT CAUSES (Hypotheses)

### H1: Synchronous Plugin Loading
Each plugin boots sequentially. With 20+ plugins at ~2s each = 40s+

### H2: Eager Initialization
Components initialize fully at boot instead of on-demand.
Especially: Senses, Analyzers, Tools

### H3: Repeated File I/O
Config files, YAML manifests read multiple times during boot.

### H4: Network/External Dependencies
LLM providers, API checks during boot instead of lazy.

---

## SONNET TASKS

### T1: Profile Boot Sequence (DIAGNOSTIC)
```bash
# Add timing instrumentation to key boot phases
# Files to instrument:
- vibe_core/boot_orchestrator.py
- vibe_core/kernel_impl.py
- vibe_core/plugins/opus_assistant/manas/kernel_tick.py
- vibe_core/loaders/base_loader.py
```

**Goal**: Identify exact bottlenecks with millisecond precision.

### T2: Parallel Plugin Loading
```python
# Current (sequential):
for plugin in plugins:
    plugin.on_boot(kernel)

# Target (parallel for IO-bound plugins):
async def boot_plugins():
    await asyncio.gather(*[p.on_boot_async(kernel) for p in plugins])
```

**Files**:
- `vibe_core/kernel_impl.py` (boot_plugins method)
- `vibe_core/loaders/plugin_loader.py`

### T3: Lazy Sense/Analyzer Loading
```python
# Current: Load all 10 senses at boot
# Target: Load sense on first access

class LazySenseLoader:
    def __getattr__(self, name):
        if name not in self._loaded:
            self._loaded[name] = self._load_sense(name)
        return self._loaded[name]
```

**Files**:
- `vibe_core/plugins/opus_assistant/manas/sense_manager.py`
- `vibe_core/loaders/module_loader.py`

### T4: Config Singleton Enforcement
Already done in OPUS-304, but verify no regressions.
```bash
grep -r "PhoenixConfig.from_files" vibe_core/ --include="*.py"
# Should return ZERO results
```

### T5: Increase Test Timeout (IMMEDIATE WORKAROUND)
```yaml
# config/quality.yaml - fast profile
fast:
  timeout: 120  # Was: 30
```

This is a workaround, not a fix. The boot time must still be reduced.

---

## SUCCESS CRITERIA

| Metric | Current | Target |
|--------|---------|--------|
| Cold boot | 102s | <10s |
| Warm boot | ~30s | <3s |
| Test suite (unit) | TIMEOUT | <120s total |
| Test errors | 13 | 0 |

---

## VERIFICATION COMMANDS

```bash
# Measure boot time
time python3 -c "from vibe_core.kernel_impl import RealVibeKernel; RealVibeKernel(':memory:')"

# Run kernel-dependent tests with current timeout
python -m pytest tests/unit/test_vajra_wiring.py --timeout=120 -v

# Run full unit suite
python -m pytest tests/unit/ --timeout=120 -q
```

---

## WHEN DONE

1. Commit all changes with `OPUS-306: Boot performance optimization`
2. Verify boot time < 10s
3. Verify test errors = 0
4. Spawn Haiku for OPUS-307 prep (CI/CD restoration)

---

## COMMITS SO FAR (This Session)

```
888a1743 - fix(boot): Add missing logger to boot_optimizer plugin
581d9bbf - fix(tests): Update LayeredRouter tests to match RouteResult schema
```

---

*Speed is a feature. A 102-second boot is a broken system.*
