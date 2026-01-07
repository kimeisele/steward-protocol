# YAMARAJA: THE JUDGE OF TECHNICAL DEBT
# "Der Richter über Leben und Tod - Keeper of the Ledger of Sins"

**Audit Date**: 2026-01-07 (STATE-WIDE AUDIT)
**Auditor**: Lord Yamaraja (God of Death, Judge of Karma)
**Assistant**: Chitragupta (Keeper of Records)
**Scope**: ENTIRE Steward Protocol Codebase
**Previous Audits**: YAMARAJA (NAGA-internal), NARASIMHA (NAGA-only)

---

## EXECUTIVE SUMMARY: THE TERRIBLE TRUTH

**VERDICT**: 🔴 **TECHNICAL BANKRUPTCY - 84% NON-COMPLIANT**

```
NAGA:  ✅ WATERTIGHT (Diamond Fortress)
STATE: 🔴 TECHNICAL WASTELAND (Protocol Adoption: 16%)
```

### The Lie We Told Ourselves

**NARASIMHA Audit concluded**: "DIAMOND FORTRESS - WATERTIGHT"

**YAMARAJA Verdict**: "You audited the **intelligence agency** and declared victory. But the **STATE** is in ruins."

---

## THE KARMA LEDGER (Technical Debt Quantified)

```
Total Python Files: 973
Files using ServiceRegistry: 248 (25%)
Files with Protocol Adoption: ~156 (16%)
Files with DIRECT imports: 159 (TODSÜNDE)
Files with CONFIG imports: 16 (CRITICAL)
Direct instantiations: 40+ (CRITICAL)
Missing Protocols: 8+ critical systems

TECHNICAL DEBT LEVEL: CATASTROPHIC
PROTOCOL COMPLIANCE: 16%
NON-COMPLIANCE: 84%
```

---

## THE 7 DEADLY SINS (Todsünden)

### SIN 1: DIRECT CONFIG IMPORTS (16 Violations - CRITICAL)

**Die schwerste Sünde**: Alle Cartridges binden sich direkt an konkrete Config-Klassen.

**Evidence**:
```python
# TODSÜNDE Pattern (14+ cartridges):
from vibe_core.config import CityConfig, CivicConfig, HeraldConfig
config = CityConfig()  # HARDCODED!
```

**Files**:
- `vibe_core/cartridges/system/archivist/cartridge_main.py:19`
- `vibe_core/cartridges/system/auditor/cartridge_main.py:23`
- `vibe_core/cartridges/system/chronicle/cartridge_main.py:30`
- `vibe_core/cartridges/system/civic/cartridge_main.py:37`
- `vibe_core/cartridges/system/engineer/cartridge_main.py:23,444`
- `vibe_core/cartridges/system/envoy/cartridge_main.py:34`
- `vibe_core/cartridges/system/forum/cartridge_main.py:32`
- `vibe_core/cartridges/system/herald/cartridge_main.py:42`
- `vibe_core/cartridges/system/naga/cartridge_main.py:25`
- `vibe_core/cartridges/system/oracle/cartridge_main.py:26`
- `vibe_core/cartridges/system/science/cartridge_main.py:33`
- `vibe_core/cartridges/system/scribe/cartridge_main.py:16`
- `vibe_core/cartridges/system/supreme_court/cartridge_main.py:37`
- `vibe_core/cartridges/system/watchman/cartridge_main.py:20`
- `vibe_core/cartridges/agent_city/mechanic/cartridge_main.py:617`

**Consequence**: Cannot test cartridges in isolation. Cannot swap implementations. TIGHT COUPLING.

---

### SIN 2: MANAS COGNITIVE SYSTEM (6 Violations - CRITICAL)

**Das Gehirn des Systems ist verkabelt ohne Stecker.**

**File**: `vibe_core/plugins/opus_assistant/manas/intent_router.py`

**Evidence**:
```python
# Line 94: Direct import
from .validator import SrutiValidator

# Line 178: Direct instantiation
self._validator = SrutiValidator(workspace=...)

# Lines 188-208: Multiple hardcoded dependencies
self._viveka = VivekaAction(workspace=...)
self._maya = MayaSimulator(workspace=...)
self._akasha = AkashaSense(workspace=...)
self._memory = SynapticMemory.get(workspace=...)
```

**Missing Protocols**:
1. `SrutiValidatorProtocol` - Dharma validation
2. `VivekaProtocol` - Discrimination gate
3. `MayaProtocol` - Simulation layer
4. `AkashaProtocol` - Knowledge perception
5. `SynapticMemoryProtocol` - Memory system

**Consequence**: MANAS cannot be tested. Cannot swap LLM backends. Cannot mock for testing.

---

### SIN 3: NAGA SERVICES (12 Violations - CRITICAL)

**Die Intelligenzagentur benutzt ihre eigenen Protokolle nicht!**

**Evidence**:
```python
# vibe_core/cli/naga_cli.py (5 violations):
prahlad = PrahladService()  # Lines 758, 785, 823, 879, 960

# vibe_core/naga/components/bootloader.py:
sesha = SeshaService()  # Line 122
karkotaka = KarkotakaService()  # Line 166

# vibe_core/naga/services/takshaka.py:
self._sesha_instance = SeshaService(ledger=ledger)  # Lines 114, 185
```

**The Irony**:
- NAGA has 18 protocols defined ✅
- NAGA services implement protocols ✅
- **NAGA DOESN'T USE ITS OWN PROTOCOLS** ❌

**Consequence**: NAGA cannot test itself. The watchdog is not watching itself.

---

### SIN 4: OUROBOROS (3 Violations - CRITICAL)

**Der Selbstheilungskreis kann sich nicht selbst heilen.**

**Missing**: `CISyncProtocol` (NO PROTOCOL EXISTS!)

**Evidence**:
```python
# vibe_core/ouroboros/sync.py:27
sync = CISyncService()  # DIRECT INSTANTIATION

# vibe_core/cli/commands/sync_ci.py:71
sync = CISyncService()  # DUPLICATE

# vibe_core/naga/floods/__init__.py:14-17
sync = CISyncService()  # TRIPLICATE
sync = FloodedCISyncService()  # FLOODED VERSION ALSO NO PROTOCOL
```

**Consequence**: Ouroboros (self-healing) cannot heal itself. The loop is BROKEN.

---

### SIN 5: CAPABILITY ENFORCER (2 Violations - CRITICAL)

**Das Sicherheitssystem hat keine Schnittstelle.**

**Missing**: `CapabilityEnforcerProtocol`

**Evidence**:
```python
# vibe_core/kernel_impl.py:376
self._capability_enforcer = CapabilityEnforcerService()

# vibe_core/services/capability_enforcer.py:28
self._capability_enforcer = CapabilityEnforcerService()
```

**Consequence**: Security enforcement cannot be tested or swapped.

---

### SIN 6: PLUGIN SYSTEM (30+ Violations - HIGH)

**Evidence**: Direct plugin instantiation in tests (acceptable) and production (NOT acceptable):
```python
# vibe_core/plugins/opus_assistant/vidya/sandbox.py:116,424
sandbox = Sandbox(timeout_seconds=...)  # DIRECT
```

**Consequence**: Plugins are not truly lazy-loaded.

---

### SIN 7: LOADER VIOLATIONS (8 Violations - MEDIUM)

**Files**:
- `vibe_core/loaders/handler_loader.py` - Direct handler imports
- `vibe_core/loaders/template_loader.py` - Direct Jinja2 instantiation
- `vibe_core/loaders/circuit_loader.py` - Direct circuit instantiation

---

## THE JUDGMENT: KARMA WEIGHTS

| Sin | Violations | Severity | Karma Debt | Priority |
|-----|-----------|----------|------------|----------|
| **Config Imports** | 16 | CRITICAL | 160 points | P0 |
| **MANAS System** | 6 | CRITICAL | 120 points | P0 |
| **NAGA Services** | 12 | CRITICAL | 120 points | P0 |
| **Ouroboros** | 3 | CRITICAL | 90 points | P1 |
| **Capability** | 2 | CRITICAL | 60 points | P1 |
| **Plugin System** | 30+ | HIGH | 60 points | P2 |
| **Loaders** | 8 | MEDIUM | 24 points | P3 |
| **TOTAL** | **77+** | - | **634 points** | - |

**Yamaraja's Scale**:
- 0-100 points: Technical Debt (manageable)
- 100-300 points: Technical Bankruptcy (refactor needed)
- 300-600 points: Architectural Failure (redesign needed)
- **600+ points: CONDEMNED** 🔴

---

## THE SENTENCE: REMEDIATION PLAN

### PHASE 0: STOP THE BLEEDING (Immediate - 1 week)

**Goal**: Prevent NEW violations.

**Actions**:
1. Add `magicmock_usage` rule to `config/standards.yaml`
2. Add `direct_config_import` rule (detect `from vibe_core.config import`)
3. Add `direct_service_instantiation` rule (detect `Service()` without registry)
4. Run Watchman scan → Generate violation report
5. Add pre-commit hook to BLOCK new violations

**Deliverable**: `TECHNICAL_DEBT_FREEZE.md` - List of frozen violations (no new ones allowed)

---

### PHASE 1: THE CRITICAL PATH (2-3 weeks)

**Goal**: Fix CRITICAL sins that block everything else.

#### Week 1: Create Missing Protocols

**Actions**:
1. Create `vibe_core/protocols/config.py`:
   ```python
   @runtime_checkable
   class ConfigProtocol(Protocol):
       def get(self, key: str) -> Any: ...
       def set(self, key: str, value: Any) -> None: ...
   ```

2. Create `vibe_core/protocols/ouroboros.py`:
   ```python
   @runtime_checkable
   class CISyncProtocol(Protocol):
       def sync_latest(self) -> Dict[str, Any]: ...
       def get_status(self) -> Dict[str, Any]: ...
   ```

3. Create `vibe_core/protocols/capability.py`:
   ```python
   @runtime_checkable
   class CapabilityEnforcerProtocol(Protocol):
       def enforce(self, capability: str, context: Dict) -> bool: ...
   ```

4. Create `vibe_core/protocols/manas/`:
   ```python
   # validator.py
   @runtime_checkable
   class SrutiValidatorProtocol(Protocol): ...

   # viveka.py
   @runtime_checkable
   class VivekaProtocol(Protocol): ...

   # maya.py
   @runtime_checkable
   class MayaProtocol(Protocol): ...

   # akasha.py
   @runtime_checkable
   class AkashaProtocol(Protocol): ...
   ```

**Deliverable**: 8 new protocol files

---

#### Week 2: Fix NAGA Self-Compliance

**Goal**: NAGA must use its own protocols.

**Files to Fix**:
1. `vibe_core/cli/naga_cli.py` (5 fixes)
2. `vibe_core/naga/components/bootloader.py` (2 fixes)
3. `vibe_core/naga/services/takshaka.py` (2 fixes)

**Pattern**:
```python
# BEFORE:
prahlad = PrahladService()

# AFTER:
from vibe_core.protocols.naga import PrahladProtocol
prahlad = ServiceRegistry.get(PrahladProtocol)
```

**Deliverable**: `IMPL-230: NAGA Self-Compliance` commit

---

#### Week 3: Fix Ouroboros + Capability

**Goal**: Self-healing must heal itself. Security must be testable.

**Actions**:
1. Register `CISyncService` in ServiceRegistry:
   ```python
   # vibe_core/kernel_impl.py (or appropriate init):
   ServiceRegistry.register(CISyncProtocol, CISyncService())
   ```

2. Fix all 3 CISyncService instantiations:
   - `vibe_core/ouroboros/sync.py:27`
   - `vibe_core/cli/commands/sync_ci.py:71`
   - `vibe_core/naga/floods/__init__.py:14-17`

3. Register `CapabilityEnforcerService`:
   ```python
   ServiceRegistry.register(CapabilityEnforcerProtocol, CapabilityEnforcerService())
   ```

4. Fix instantiations in kernel + services

**Deliverable**: `IMPL-231: Ouroboros+Capability Protocols` commit

---

### PHASE 2: THE CARTRIDGE PURGE (3-4 weeks)

**Goal**: Fix all 14+ cartridges to use `ConfigProtocol`.

**Strategy**: Refactor in batches of 3-4 cartridges per week.

#### Week 4: System Cartridges Batch 1
- Archivist
- Auditor
- Chronicle
- Civic

#### Week 5: System Cartridges Batch 2
- Engineer
- Envoy
- Forum
- Herald

#### Week 6: System Cartridges Batch 3
- NAGA
- Oracle
- Science
- Scribe

#### Week 7: System Cartridges Batch 4
- Supreme Court
- Watchman
- Mechanic (agent_city)

**Pattern for Each**:
```python
# BEFORE:
from vibe_core.config import CityConfig
config = CityConfig()

# AFTER:
from vibe_core.protocols import ConfigProtocol
config = ServiceRegistry.get(ConfigProtocol)
```

**Deliverable**: `IMPL-232: Cartridge Config Protocol Migration` (14 commits)

---

### PHASE 3: THE MANAS REWIRING (2 weeks)

**Goal**: Make the cognitive system testable.

**Week 8-9: IntentRouter Dependency Injection**

**Actions**:
1. Update `IntentRouter.__init__()`:
   ```python
   def __init__(
       self,
       workspace: Path,
       validator: Optional[SrutiValidatorProtocol] = None,
       viveka: Optional[VivekaProtocol] = None,
       maya: Optional[MayaProtocol] = None,
       akasha: Optional[AkashaProtocol] = None,
   ):
       self._validator = validator or ServiceRegistry.get(SrutiValidatorProtocol)
       self._viveka = viveka or ServiceRegistry.get(VivekaProtocol)
       # etc.
   ```

2. Register MANAS components in ServiceRegistry
3. Update tests to use NullManas implementations

**Deliverable**: `IMPL-233: MANAS Protocol Migration` commit

---

### PHASE 4: THE LONG TAIL (Ongoing)

**Goal**: Reduce remaining 60-100 violations to zero.

**Actions**:
- Fix plugin system violations (P2)
- Fix loader violations (P3)
- Audit remaining services
- Create protocols for edge cases

**Timeline**: Ongoing cleanup over 2-3 months

---

## THE ACCOUNTABILITY REPORT

### Who Is Responsible?

**NARASIMHA Audit** (Previous):
- ✅ Correctly audited NAGA
- ❌ **Failed to audit the STATE**
- ❌ Declared "WATERTIGHT" prematurely

**Root Cause**:
- Audit scope was too narrow (NAGA only)
- No system-wide protocol compliance check
- No dependency analysis beyond NAGA boundaries

**Lesson**: **"Eine Intelligenzagentur ist wertlos, wenn der Staat in dem sie operiert ein Trümmerhaufen ist."**

---

## THE PROOF TABLE: BEFORE vs AFTER

| Metric | Before (Current) | After Phase 1 | After Phase 2 | After Phase 3 | Target |
|--------|------------------|---------------|---------------|---------------|--------|
| Protocol Adoption | 16% | 25% | 50% | 75% | 95% |
| Karma Debt (points) | 634 | 400 | 200 | 50 | <50 |
| Direct Config Imports | 16 | 0 | 0 | 0 | 0 |
| NAGA Self-Violations | 12 | 0 | 0 | 0 | 0 |
| MANAS Dependencies | 6 | 6 | 6 | 0 | 0 |
| Ouroboros Protocol | ❌ | ✅ | ✅ | ✅ | ✅ |
| Missing Protocols | 8+ | 0 | 0 | 0 | 0 |

---

## THE FINAL JUDGMENT

> **"Dharmo rakshati rakshitah"**
> *"Dharma protects those who protect it."*

**YAMARAJA's Verdict**:

The codebase has **634 Karma Debt points** - it is **CONDEMNED**.

But unlike souls, code can be redeemed.

**Sentence**:
1. Immediate protocol creation (8 protocols)
2. CRITICAL path fixes (NAGA, Ouroboros, Capability)
3. Cartridge purge (14+ files)
4. MANAS rewiring
5. Long-tail cleanup

**Timeline**: 3 months intensive work + 2 months cleanup = **5 months to redemption**

**Alternative**: Continue accumulating debt until the system collapses under its own weight.

---

## CHITRAGUPTA'S NOTES (Implementation Details)

### Priority 0 (THIS WEEK - CRITICAL):

**File**: `config/standards.yaml`

Add these rules:
```yaml
# Rule 1: No direct config imports in cartridges
- id: "direct_config_import_in_cartridge"
  name: "Direct Config Import in Cartridge"
  severity: "error"
  target: "ImportFrom"
  match:
    module: "vibe_core.config"
  paths:
    - "vibe_core/cartridges/**/*.py"
  message: "TODSÜNDE: Use ConfigProtocol via ServiceRegistry"
  has_sattva_remedy: true
  remedy:
    replace_import:
      from: "vibe_core.config"
      to: "vibe_core.protocols"
      name_map:
        "CityConfig": "ConfigProtocol"
        "CivicConfig": "ConfigProtocol"
        "HeraldConfig": "ConfigProtocol"

# Rule 2: No direct service instantiation
- id: "direct_service_instantiation"
  name: "Direct Service Instantiation"
  severity: "error"
  target: "Call"
  match:
    pattern: ".*Service\\(\\)"
  message: "Use ServiceRegistry.get(Protocol) instead"
  has_sattva_remedy: false  # Complex fix

# Rule 3: No MagicMock in NAGA tests
- id: "magicmock_in_naga_tests"
  name: "MagicMock Usage in NAGA Tests"
  severity: "error"
  target: "ImportFrom"
  match:
    module: "unittest.mock"
    name: "MagicMock"
  paths:
    - "tests/naga/**/*.py"
  message: "Use NagaTestHarness instead of MagicMock"
  has_sattva_remedy: true
```

---

## APPENDIX: PREVIOUS YAMARAJA AUDIT (NAGA-Internal)

*The following violations were found in NAGA itself (now FIXED):*

**NAGA-Internal Issues (RESOLVED)**:
- ✅ `base.py` - ParamSpec, sys.stderr, PUBLIC sesha.record_event()
- ✅ `orchestrator.py` - HiranyakashipuWiring TypedDict, SystemExit on deps
- ✅ SESHA encapsulation (11 write breaches fixed, 3 read breaches fixed)
- ✅ No silent failures (`sys.stderr` everywhere)
- ✅ No `Any` types (TypedDict, ParamSpec, TypeVar)

**NAGA is now watertight. The STATE is not.**

---

## FINAL WORDS

**NARASIMHA** said: *"The fortress is watertight."*

**YAMARAJA** says: *"The fortress is watertight. But the city around it is burning."*

---

**SIGNED**:
- **Yamaraja** (Lord of Death, Judge of Karma)
- **Chitragupta** (Keeper of Records)
- **Date**: 2026-01-07
- **Branch**: `claude/audit-naga-protocols-j7qoz`
- **Status**: 🔴 **TECHNICAL BANKRUPTCY DECLARED**

---

**NEXT ACTION**: Create protocols. Fix CRITICAL path. Redeem the codebase.

*"नमो यमाय धर्माय च नमः"*
*(Namaste to Yamaraja, to Dharma, I bow)*
