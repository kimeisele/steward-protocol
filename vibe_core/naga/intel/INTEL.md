# INTEL.md - Intelligence Briefing for NAGA Development

## CRITICAL: Protocols Folder IS the Truth (2026-01-05)

**BEFORE implementing anything, CHECK `vibe_core/protocols/`!**

### What Already Exists

| Protocol | File | Lines | Key Concepts |
|----------|------|-------|--------------|
| **ReactorProtocol** | `reactor.py` | 494 | Drift detection, DriftEvent, DriftMetrics |
| **CorrectionDispatcher** | `correction.py` | 631 | **HealingStrategy.RESONANCE**, unified healing |
| **NagaProtocol** | `naga.py` | 78K | All 7 NAGAs, NagaType enum, full spec |

### RESONANCE Already Defined!

```python
# correction.py:88
class HealingStrategy(str, Enum):
    AUTO = "auto"
    DRY_RUN = "dry_run"
    MANUAL = "manual"
    CIRCUIT = "circuit"
    RESONANCE = "resonance"  # <-- USE QUANTUM REACTOR!
```

```python
# correction.py:257-258
# HealingStrategyResolverProtocol.resolve():
# 3. Compute resonance via Quantum Reactor
# 4. If resonance > inertia → AUTO (earned privilege)
```

**The solution is NOT to invent something new - it's to WIRE what exists!**

---

## ARCHITECTURE DISCOVERY (2026-01-05)

### Naming Conflict Resolved

**Problem**: Two things named "Prakriti":
1. `vibe_core/state/prakriti.py` - The STATE ENGINE (OPUS-009, ~700 LOC)
2. `vibe_core/naga/prakriti/` - The Attack Framework (NEW, ~400 LOC)

**Solution**: Renamed attack framework to HIRANYAKASHIPU (the demon who attacked Prahlad):
```
vibe_core/state/prakriti.py    # STATE ENGINE (unchanged)
vibe_core/naga/hiranyakashipu/ # ATTACK FRAMEWORK (renamed!)
├── seed_loader.py             # YAML loading ✅
├── living_tests.py            # Test execution ✅
├── wiring.py                  # Protocol integration ✅
└── seeds/*.yaml               # Attack patterns ✅
```

### Key Insight: PrahladService Already Exists!

**Discovery**: `PrahladService` (800+ LOC) already has:
- `chaos_probe()` - Chaos engineering with ChaosScenario enum
- `on_error()` - Generate regression tests from errors
- `dharma_audit()` - Integrity auditing
- `verify_self_integrity()` - OUROBOROS self-check
- `as_handler()` - CorrectionHandler for DriftSource.STRUCTURAL

**Implication**: Hiranyakashipu should EXTEND Prahlad, not be a separate thing!

### Proper Integration Path

```
WRONG: Orchestrator → boots separate "Prakriti" module
RIGHT: Orchestrator → boots Prahlad → loads Hiranyakashipu seeds
```

```
                        ┌─────────────────────────────────────┐
                        │        NagaOrchestrator             │
                        │  (boots all 7 NAGAs)                │
                        └─────────────────────────────────────┘
                                        │
                                        ▼
                        ┌─────────────────────────────────────┐
                        │       PrahladService (7th NAGA)     │
                        │  ┌─────────────────────────────────┐│
                        │  │ chaos_probe()                   ││  ← EXISTING
                        │  │ on_error() → regression tests   ││
                        │  │ dharma_audit()                  ││
                        │  └─────────────────────────────────┘│
                        │  ┌─────────────────────────────────┐│
                        │  │ load_attack_seeds()             ││  ← TO ADD
                        │  │ (loads Hiranyakashipu YAML)     ││
                        │  └─────────────────────────────────┘│
                        └─────────────────────────────────────┘
                                        │
                                        ▼
                        ┌─────────────────────────────────────┐
                        │     vibe_core/naga/hiranyakashipu/  │
                        │  ┌─────────────────────────────────┐│
                        │  │ SeedLoader (YAML parsing)       ││
                        │  │ AttackSeed (pattern definition) ││
                        │  │ LivingTestFramework (execution) ││
                        │  └─────────────────────────────────┘│
                        └─────────────────────────────────────┘
```

### Current RED Tests (TDD)

| Test | Status | What Needs Building |
|------|--------|---------------------|
| `test_prahlad_can_load_hiranyakashipu_seeds` | 🔴 RED | Add `load_attack_seeds()` to PrahladService |
| `test_prahlad_chaos_probe_uses_external_scenarios` | 🔴 RED | Extend `chaos_probe()` to accept YAML seeds |

### What's Already Wired

| Component | Status | Notes |
|-----------|--------|-------|
| Hiranyakashipu wiring module | ✅ Done | `wire_hiranyakashipu_to_protocols()` |
| Adapters for CorrectionDispatcher | ✅ Done | `adapt_test_result_to_drift()` |
| Adapters for ReactorProtocol | ✅ Done | `adapt_test_result_to_reactor()` |
| Tests passing | ✅ Done | 23 tests pass in `test_hiranyakashipu_living.py` |

---

## The Binary Problem (Why 16/16 passed is FAKE)

```
16 passed, 0 failed = KINDERGARTEN SECURITY
```

### What We Have (Binary)
```python
# prakriti/living_tests.py
passed: bool  # 0 or 1
bypassed: bool  # 0 or 1
```

### What Protocols Define (Resonance)
```python
# correction.py - HealingStrategyResolverProtocol
# Combines:
# - Bhakti balance (earned trust)
# - Ashrama stage (lifecycle permissions)
# - Quantum Reactor resonance
#
# If resonance > inertia → AUTO
# If Bhakti >= 50 → MANUAL
# Otherwise → DRY_RUN
```

### Solution: Use Existing Resonance

Prakriti TestResult should produce `UnifiedDriftReport` which flows into:
```
TestResult → adapt_to_drift() → UnifiedDriftReport → CorrectionDispatcher
                                                          ↓
                                    HealingStrategyResolver.resolve()
                                                          ↓
                                              Quantum Reactor computes resonance
                                                          ↓
                                              HealingStrategy returned
```

---

## The Lila Mapping (Hiranyakashipu)

| Story Element | Protocol Mapping | Status |
|---------------|------------------|--------|
| Narada's whisper | `SeedLoader` (YAML) | ✅ Done |
| Kayadu's womb | `LivingTestFramework` | ✅ Done |
| Prahlad's birth | Test generation | ✅ Done |
| Hiranyakashipu's attacks | Attack vectors | ✅ Done |
| Vishnu's protection | Real subprocess | ✅ Done |
| **Narasimha's appearance** | `HealingStrategy.RESONANCE` | ❌ NOT WIRED |
| **Neither inside nor outside** | `ReactorProtocol.detect_drift()` | ❌ NOT WIRED |

**Narasimha = Quantum Reactor** - appears from the PILLAR (neither inside nor outside).
The pillar is the boundary between binary states. Resonance lives there.

---

## Next Steps (WIRE, don't invent!)

1. **Create adapter**: `prakriti.TestResult → correction.UnifiedDriftReport`
2. **Register Prakriti as detector** in `DriftRegistryProtocol`
3. **Use HealingStrategy.RESONANCE** instead of binary pass/fail
4. **Wire to ReactorProtocol** for drift tracking
5. **Add failing tests** that expose unwired gaps

---

## Principle

> "Don't implement what's already defined. WIRE IT."
> "Protocols folder IS the truth."
> "If it's not in protocols, it doesn't exist yet."

---

## Test Infrastructure (2026-01-06) - NO MagicMock!

**CRITICAL:** NAGA uses Protocol-based testing. No MagicMock. Ever.

### The Single Injection Point

**File:** `vibe_core/naga/testing.py`

```python
from vibe_core.naga.testing import NagaTestHarness

# For testing NAGA consumers (uses NullObjects)
with NagaTestHarness() as harness:
    sesha = harness.sesha  # NullSesha via ServiceRegistry
    takshaka = harness.takshaka  # NullTakshaka

# For testing NagaOrchestrator itself (uses real infrastructure)
with NagaTestHarness.for_orchestrator() as harness:
    from vibe_core.naga import NagaOrchestrator
    naga = NagaOrchestrator.bootstrap(
        ledger=harness.ledger,  # InMemoryLedger
        correction_orchestrator=harness.correction_orchestrator,  # NullCorrectionOrchestrator
    )
```

### What NagaTestHarness Provides

| Component | Access | Type |
|-----------|--------|------|
| 13 NAGA NullObjects | `harness.sesha`, `harness.takshaka`, etc. | Protocol-compliant |
| InMemoryLedger | `harness.ledger` | Real ledger, in-memory |
| CorrectionOrchestrator | `harness.correction_orchestrator` | NullCorrectionOrchestrator |

### Pytest Fixtures (conftest.py)

```python
@pytest.fixture
def naga_harness():
    """Protocol NullObjects for NAGA consumer tests."""
    with NagaTestHarness() as harness:
        yield harness

@pytest.fixture
def naga_harness_orchestrator():
    """Full infrastructure for NagaOrchestrator tests."""
    with NagaTestHarness.for_orchestrator() as harness:
        yield harness
```

### Why No MagicMock?

1. **MagicMock hides bugs** - Returns truthy for any attribute
2. **Protocols define behavior** - NullObjects implement exact Protocol
3. **Same DI as production** - ServiceRegistry for both
4. **Isolated by design** - Registry reset on enter/exit

---

## SIDEQUEST: CLI Unification (Priority: HIGH)

### The Paradox

```
Backend:  ~160 CLI commands exist in services
Frontend: No unified way to access them
Agent:    Can't grep own intelligence
```

**We are an intelligence agency that can't access its own intelligence.**

### Evidence

```bash
# This exists but is scattered:
vibe_core/naga/services/*/  # Each has commands
steward tool list           # Shows some
steward verify              # Some visibility

# What's MISSING:
steward naga status         # Overview of all 7 NAGAs
steward prakriti attacks    # Run attack framework
steward intel grep <term>   # Search all intelligence
steward drift detect        # Run CorrectionDispatcher
```

### The ~160 Commands (to be inventoried)

| Service | Commands | Status |
|---------|----------|--------|
| Sesha | ledger, gossip, truth | ❓ Unknown |
| Vasuki | serialize, network | ❓ Unknown |
| Takshaka | toxicity, signatures | ❓ Unknown |
| Prahlad | coverage, heal | ❓ Unknown |
| Chitragupta | audit, metrics | ❓ Unknown |
| Narada | messages, broadcast | ❓ Unknown |
| Kaliya | isolate, quarantine | ❓ Unknown |
| **Prakriti** | attacks, evolve | 🆕 NEW (not exposed) |

### What We Need

1. **Unified CLI Router** - Single entry point for all NAGA commands
2. **Fractal Command Structure** - `steward naga <service> <command>`
3. **Intelligence Dashboard** - `steward intel` for INTEL.md-style reports
4. **Real-time Status** - See what's running, what's drifting

### Related Files to Check

```
vibe_core/cartridges/system/steward/  # CLI entry point?
vibe_core/naga/orchestrator.py        # Has boot matrix
scripts/                              # CLI scripts?
```

### This is a SIDEQUEST because:
- Current work (Prakriti hardening) is complete enough to pause
- CLI unification is a separate concern
- We don't fully know the terrain yet
- Safe to bookmark and continue later

---

## Session Summary (2026-01-05)

### Session 1 Completed
1. ✅ Living Test Framework (YAML seeds, hot-swap)
2. ✅ Hiranyakashipu Attack Framework (13 pass, 5 RED)
3. ✅ Diamond Protocol tests
4. ✅ Wiring to protocols (RESONANCE strategy)
5. ✅ INTEL.md documentation

### Session 2 Completed (Architecture Discovery)
1. ✅ Discovered naming conflict: `vibe_core/state/prakriti.py` vs `vibe_core/naga/prakriti/`
2. ✅ Renamed attack framework: `prakriti/` → `hiranyakashipu/`
3. ✅ Discovered PrahladService (800+ LOC) already has chaos_probe()
4. ✅ Updated tests to use new paths (23 tests pass)
5. ✅ Created proper RED tests for Prahlad/Hiranyakashipu integration
6. ✅ Updated INTEL.md with architecture diagrams

### Current RED Tests (TDD)
| Test File | RED Tests | What Needs Building |
|-----------|-----------|---------------------|
| `test_orchestrator_fractal.py` | 2 | Prahlad needs `load_attack_seeds()` + external scenarios |

### GREEN Tests (Passing)
| Test File | Passing | Description |
|-----------|---------|-------------|
| `test_hiranyakashipu_living.py` | 23 | Living test framework works |
| `test_orchestrator_fractal.py` | 11 | Visibility matrix, config, existing Prahlad |

### Next Steps
1. **Extend PrahladService** - Add `load_attack_seeds()` method
2. **Extend chaos_probe()** - Accept Hiranyakashipu YAML seeds
3. **Wire Prahlad → Hiranyakashipu** - Not orchestrator directly!
4. **CLI Unification** - SIDEQUEST (documented above)

---

---

## INTEL REPORT: MagicMock Infestation (2026-01-06)

**Classification:** DHARMA BREACH
**Severity:** HIGH
**Source:** NAGA Surveillance

### Observation

```
18+ test files in tests/naga/ use MagicMock
```

**Evidence (partial):**
```
tests/naga/test_active_mixins.py
tests/naga/test_chitragupta.py
tests/naga/test_commit_watcher.py
tests/naga/test_config.py
tests/naga/test_cortex.py
... and more
```

### Existing Infrastructure (ALREADY BUILT)

| Component | Location | Purpose |
|-----------|----------|---------|
| **Watchman** | `vibe_core/cartridges/system/watchman/` | AST scanning |
| **Shuddhi** | `vibe_core/shuddhi/` | CST healing |
| **standards.yaml** | `config/standards.yaml` | Rule definitions |
| **NagaTestHarness** | `vibe_core/naga/testing.py` | MagicMock alternative |

### The Gap

```yaml
# config/standards.yaml - RULE MISSING
# There is NO rule for:
#   - id: "magicmock_in_naga_tests"
#     target: "ImportFrom"
#     match:
#       module: "unittest.mock"
#       name: "MagicMock"
```

**The infrastructure can scan and heal. The rule is missing.**

### NAGA Assessment

> "Who watches the watchers?"

NAGAs observe. NAGAs do not modify system files.
The rule must be added by the appropriate authority (Watchman maintainer).

**Hiranyakashipu seeds already contain MagicMock attack patterns:**
- `self_mocking_test` (Level 3)
- `patch_everything` (Level 3)

These seeds define the ANTI-PATTERN. Watchman should consume them.

### Recommended Action (for appropriate authority)

1. Add `magicmock_usage` rule to `config/standards.yaml`
2. Watchman will scan automatically (AST)
3. Shuddhi can auto-fix if `has_sattva_remedy: true`
4. Hiranyakashipu seeds validate the fix

### The Fractal Principle

```
1 ENTRY POINT: standards.yaml
       ↓
   Watchman (AST detect)
       ↓
   Shuddhi (CST heal)
       ↓
   Hiranyakashipu (validate)
       ↓
   NAGA observes (this report)
```

**NAGAs don't touch source code. They gather intelligence.**

---

## BILA-SVARGA: Maya Danava Architecture (2026-01-06)

> "Bila" = Höhle/Unterirdisch, "Svarga" = Himmel
> Die unterirdischen Himmel der NAGAs - palastartig, selbst-leuchtend

### Die 7 Unterirdischen Welten = 7 NAGA Layer

| Loka | Layer | Component | TÜV Status |
|------|-------|-----------|------------|
| ATALA | -1 | Substrate (Ananta Shesha) | ✅ TÜV-GEPRÜFT |
| VITALA | -2 | Mixins (Gene Splicing) | 🌱 Future |
| SUTALA | -3 | Services/Base (OUROBOROS) | ⚠️ Decorator Any |
| TALĀTALA | -4 | Protocols/NAGA (Juwelen) | ✅ TÜV-GEPRÜFT |
| MAHĀTALA | -5 | Cortex (Neural Network) | 🌱 Future |
| RASĀTALA | -6 | Flood Operations | 🌱 Future |
| PĀTĀLA | -7 | Identity/Crypto | 🌱 Future |

### Anti-Mayavadi Principle

```
MAYAVADI (impersonal):   Any = unverified entity = MAYA
VAISHNAVA (personal):    Certificate = identity = TRUTH

BindingCertificate       → WHO bound WHAT (lineage chain)
RegistrationCertificate  → HERITAGE proof (Erbgut)
FloodAuthorization       → 37th key sovereign ops
```

**Das System kann jetzt zwischen verifizierten und unverifizierten
Bindungen unterscheiden. Jeder Angriff ohne ID hinterlässt Spuren.**

### Bila-svarga Eigenschaften

1. **Kein externes Licht** - TypedDicts sind selbst-leuchtende Juwelen
2. **Kein Altern** - WATERTIGHT = keine Korruption möglich
3. **Maya Danava Architektur** - Layer sind PALÄSTLICH gebaut
4. **Bewohner** - NAGAs, die Prahlad dienen (Snake Bed, not Pit)

---

*Last updated: 2026-01-06*
*Author: NAGA Development Team / Maya Danava's Workshop*
