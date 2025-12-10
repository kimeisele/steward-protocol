# SONNET EXECUTION PLAN: EnvoyCartridge Router Migration

> **Erstellt:** 2025-12-07 by Opus 4.5
> **Problem:** EnvoyCartridge verwendet MilkOceanRouter direkt statt UnifiedRouter
> **Priorität:** HIGH - Architectural Inconsistency

---

## DAS PROBLEM

```
EnvoyPlugin (plugin_main.py:118-120)
  └── self._unified_router = UnifiedRouter()  ✅ KORREKT

EnvoyCartridge (cartridge_main.py:107)
  └── self.router = MilkOceanRouter()  ❌ INKONSISTENT
```

**Warum ist das ein Problem?**
1. Zwei verschiedene Router für denselben Intent
2. UnifiedRouter hat ALLE OPUS Fixes (BREAK 1-8)
3. MilkOceanRouter ist der ALTE Code
4. EnvoyCartridge.process() routet falsch

---

## DIE LÖSUNG

EnvoyCartridge soll den UnifiedRouter vom EnvoyPlugin nutzen.

### Phase 1: EnvoyCartridge Router-Zugriff ändern

**Datei:** `vibe_core/cartridges/system/envoy/cartridge_main.py`

**Änderung 1: Remove MilkOceanRouter import**
```python
# ENTFERNEN (Line 29):
from vibe_core.cartridges.system.envoy.tools.milk_ocean import MilkOceanRouter
```

**Änderung 2: Remove self.router = MilkOceanRouter()**
```python
# ENTFERNEN (Line 107):
self.router = MilkOceanRouter()
```

**Änderung 3: Router via Kernel holen**
```python
# In __init__ nach super().__init__:
# Router wird vom EnvoyPlugin bereitgestellt
self._router = None  # Lazy - set when kernel available

# Neue Property:
@property
def router(self):
    """Get UnifiedRouter from EnvoyPlugin."""
    if self._router is None and self.kernel:
        if hasattr(self.kernel, 'envoy') and self.kernel.envoy:
            self._router = self.kernel.envoy._unified_router
    return self._router
```

**Änderung 4: process() anpassen (Line 153-206)**
```python
# ALT (Line 153-155):
if self.kernel and not self.router.kernel:
    self.router.set_kernel(self.kernel)
    logger.debug("🔗 Kernel injected into MilkOceanRouter")

# NEU:
# Router kommt vom EnvoyPlugin - keine manuelle Injection nötig
```

```python
# ALT (Line 205-206):
routing_decision = self.router.process_prayer(user_input=user_input, agent_id="envoy", critical=False)

# NEU - UnifiedRouter API:
if not self.router:
    logger.error("❌ UnifiedRouter not available - EnvoyPlugin not loaded?")
    return {"status": "error", "error": "Router not initialized"}

from vibe_core.runtime.unified_execution import ExecutionRequest
request = self.router.route(user_input, source="cartridge")
routing_decision = {
    "status": "routing" if request.gate_decision.value == "allow" else request.gate_decision.value,
    "path": request.execution_path.value,
    "details": {"confidence": request.confidence, "target": request.target_id}
}
```

---

### Phase 2: Remove Logger Message

**Datei:** `vibe_core/cartridges/system/envoy/cartridge_main.py`

```python
# ENTFERNEN (Line 109):
logger.info("🧠 MilkOcean Router initialized (Classifier)")
```

---

### Phase 3: Tests prüfen (KEINE ÄNDERUNGEN NÖTIG)

Tests die MilkOceanRouter nutzen:
```
tests/integration/test_gajendra_moksha.py:23  - testet MilkOceanRouter STANDALONE ✅
tests/integration/test_gajendra_moksha.py:35  - router = MilkOceanRouter() ✅
tests/integration/test_complete_wiring.py:218 - testet MilkOceanRouter STANDALONE ✅
tests/integration/test_phase3_integration.py:90 - mock MilkOceanRouter ✅
```

**KEINE Tests müssen geändert werden** weil:
- Tests testen MilkOceanRouter als eigenständige Klasse (bleibt erhalten)
- NICHT als Teil von EnvoyCartridge.router

---

## VERIFICATION

```bash
# 1. Kernel boots
python -c "
from vibe_core.kernel_impl import RealVibeKernel
k = RealVibeKernel(ledger_path=':memory:')
k.boot()
print(f'Status: {k.status}')

# Check EnvoyCartridge uses UnifiedRouter
envoy = k._agent_registry.get('envoy')
print(f'Envoy router type: {type(envoy.router).__name__}')
# Expected: UnifiedRouter (NOT MilkOceanRouter)
"

# 2. Status command works
python -c "
import asyncio
from vibe_core.kernel_impl import RealVibeKernel
from vibe_core import Task

k = RealVibeKernel(ledger_path=':memory:')
k.boot()

envoy = k._agent_registry.get('envoy')
task = Task(agent_id='envoy', payload={'input': 'status'})
result = asyncio.run(envoy.process(task))
print(f'Result: {result}')
assert result.get('status') != 'error'
"

# 3. Tests pass
python -m pytest tests/ -k "envoy" -v --timeout=30
```

---

## WAS BLEIBT

**MilkOceanRouter bleibt erhalten** als:
- Standalone tool für Lazy Queue Worker (`milk_ocean.py --worker`)
- Security Gates (Watchman regex filtering)
- CLI demo

**UnifiedRouter** ist der EINZIGE Router für:
- EnvoyPlugin (kernel.envoy.route())
- EnvoyCartridge (via kernel.envoy._unified_router)

---

## COMMIT MESSAGE

```
fix: Migrate EnvoyCartridge to use UnifiedRouter

EnvoyCartridge was using MilkOceanRouter directly, bypassing
the OPUS-unified routing in EnvoyPlugin.

Changes:
- Remove direct MilkOceanRouter instantiation from EnvoyCartridge
- Add router property that gets UnifiedRouter from EnvoyPlugin
- Update process() to use UnifiedRouter API
- Keep MilkOceanRouter for standalone CLI and lazy queue worker

This ensures consistent routing through UnifiedRouter which
contains all OPUS architectural improvements (BREAK 1-8 fixes).
```

---

## NICHT ÄNDERN (Architecture Docs)

Die OPUS Architecture Docs sind **INSTITUTIONAL KNOWLEDGE**:
- `OPUS_RUNTIME_SEPARATION.md` - Dokumentiert die 8 BREAKs
- `VERIFIED_DELTA_PLAN.md` - Audit history
- `001-KERNEL-EXTRACTION.md`, `002-PHOENIX-CONFIG.md` - Entscheidungen

**Diese Docs werden NICHT gelöscht.**

---

**Signed:** Opus 4.5
**Date:** 2025-12-07
**Status:** ✅ COMPLETED (PR #353 merged 2025-12-07T19:34:34Z)

---

## VERIFICATION RESULT

```
EnvoyCartridge Router: UnifiedRouter ✅
PR #353: Merged ✅
```

---

## MISSION: UnifyEverything

### Phase 1: EnvoyCartridge Router ✅ DONE
- EnvoyCartridge now uses UnifiedRouter from EnvoyPlugin

### Remaining MilkOceanRouter Usages (INTENTIONAL):
| File | Purpose | Migration Needed? |
|------|---------|-------------------|
| task_manager.py | Fallback routing (no kernel) | NO |
| gateway/api.py | Standalone API mode | NO |
| milk_ocean.py | Original implementation | NO (library) |
| Tests | Standalone class testing | NO |

**Conclusion:** UnifyEverything Phase 1 complete. Remaining usages are intentional for non-kernel scenarios.
