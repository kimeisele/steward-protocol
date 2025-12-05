# Technical Debt Registry

> "Know thy debt, or it shall consume thee" - Srimad Debugging Purana

This document tracks all technical debt in the Steward Protocol codebase.
Each item is prioritized by **SEVERITY** (P0 = fix NOW, P1 = soon, P2 = when possible).

---

## P0: CRITICAL - Test Suite Performance Crisis

**Status**: OPEN
**Impact**: Tests take 4+ minutes, causing development slowdown
**Root Cause**: No kernel isolation, real initialization in every test

### Symptoms
- `pytest tests/` hangs for 4+ minutes
- Individual test files timeout after 20 seconds
- CI becomes unusable as test count grows

### Affected Files
| File | Problem | Time |
|------|---------|------|
| `tests/hardening/test_ledger_acid.py` | 50 threads × 100 writes = 5000 SQLite ops | TIMEOUT |
| `tests/integration/test_event_bus_integration.py` | 12× `RealVibeKernel()` init, many `sleep(0.1)` | TIMEOUT |
| `tests/integration/test_system_boot.py` | `discover_agents()` imports 22+ agents | TIMEOUT |
| `tests/integration/test_kernel_markdown_interfaces.py` | Kernel init per test × 36 tests | TIMEOUT |

### Root Cause Analysis
1. **No Test Kernel**: Tests use `RealVibeKernel()` which:
   - Initializes SQLite ledger
   - Loads 5+ plugins
   - Sets up ProcessManager, ResourceManager
   - Creates NetworkProxy, ToolRegistry
   - This happens PER TEST

2. **Agent Discovery in Tests**: `discover_agents()` dynamically imports 22+ agent classes, each with:
   - Own SQLite connections
   - Oath verification
   - Tool registration

3. **Stress Tests Without Isolation**: `test_ledger_acid.py` is a real stress test (50 threads) that should be marked as `@pytest.mark.slow`

### Proposed Solution: Fractal Test Architecture

```
TIER 1: Unit Tests (< 10ms each)
├── No kernel initialization
├── Mock all external dependencies
└── Test pure functions only

TIER 2: Integration Tests (< 500ms each)
├── Use LightweightTestKernel (no plugins)
├── In-memory SQLite only
└── No agent discovery

TIER 3: System Tests (< 5s each)
├── Full kernel, but cached
├── Lazy agent discovery
└── Mark with @pytest.mark.slow

TIER 4: Stress Tests (unbounded)
├── Real 50-thread stress
├── Mark with @pytest.mark.stress
└── Run only in CI nightly
```

### Action Items
- [ ] Create `LightweightTestKernel` that skips plugin loading
- [ ] Add `@pytest.mark.slow` to stress tests
- [ ] Cache kernel instances in test fixtures
- [ ] Create test plugin that disables slow initialization

---

## P1: Kernel Plugin Extraction Incomplete

**Status**: IN PROGRESS
**Impact**: Some domain logic still hardcoded in kernel

### Completed Extractions
- [x] VedicGovernancePlugin (Varna/Ashrama/Paused agents)
- [x] SargaCyclePlugin (DAY/NIGHT_OF_BRAHMA)
- [x] SettingsUIPlugin (SETTINGS.md sync)
- [x] EnvoyUIPlugin (ENVOY.md sync)

### Remaining Candidates
| Component | Lines in kernel | Priority | Notes |
|-----------|-----------------|----------|-------|
| Economic Substrate (Bank/Vault) | 464-496 | P2 | Lazy-loaded, works fine |
| Immune System (Auditor) | 1249-1286 | P2 | Health checks |
| Pulse/Heartbeat | 1681-1723 | P2 | Observation only |
| Tool Discovery | 629-688 | P2 | Boot-time only |

**Decision**: Lower priority - these don't affect kernel stability.

---

## P2: Herald Agent Config Access Pattern

**Status**: FIXED
**Fix Date**: 2025-12-05

Herald agent was accessing `CityConfig.posting_frequency_hours` but config structure changed to nested `herald` section.

**Fix**: Detect nested config and extract herald-specific settings.

---

## P2: Duplicate Class Definitions ("Treibsand")

**Status**: DOCUMENTED
**Impact**: Confusing codebase, potential import conflicts

Multiple locations define similar classes:
- `VibeAgent` defined in multiple places
- `AgentManifest` has overlapping definitions

**Solution**: Use canonical imports from `vibe_core.protocols`.

---

## P2: Boot.py Errors

**Status**: PARTIALLY FIXED
**Impact**: Boot sequence may fail silently

Some agents fail to import during boot. Need better error handling and fallback.

---

## Architecture Notes

### Kernel Stability
The kernel is now structured as:
- **CORE**: Scheduler (pure FIFO), Registry, Ledger, Lineage
- **SECURITY**: Narasimha, CapabilityRegistry (MUST stay in kernel)
- **PLUGINS**: All domain logic (governance, cycles, UI)

### Plugin Hook Order
```
1. on_boot (kernel init)
2. on_task_submit (COSMIC GATE - Sarga)
3. on_task_pre_assign (GOVERNANCE GATE - Varna/Ashrama)
4. on_tick_pre/post (UI sync)
5. on_task_completed/failed (lifecycle)
6. on_shutdown (cleanup)
```

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2025-12-05 | Claude | Created document, documented test performance crisis |
| 2025-12-05 | Claude | Extracted SargaCyclePlugin from kernel |
| 2025-12-05 | Claude | Extracted VedicGovernancePlugin from kernel |
