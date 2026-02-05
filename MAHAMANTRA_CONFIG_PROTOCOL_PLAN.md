# MAHAMANTRA CONFIG PROTOCOL PLAN
**Date:** 2026-02-05  
**Mode:** PLAN ONLY - No implementation yet  
**Principle:** Protocol-first, no concrete classes, Mahamantra is KING

---

## EXECUTIVE SUMMARY

**Problem:**
- Config files (filesystem/Maya) control Kernel (consciousness) — BACKWARDS
- Services try to instantiate themselves — BACKWARDS
- Legacy code imports Mahamantra as utility — BACKWARDS
- Everything OUTSIDE Mahamantra treats it as a tool

**Solution:**
- **Mahamantra = PROTOCOL KING** (declares what must exist)
- **Everything OUTSIDE = Legacy adapters** (implement Mahamantra protocols)
- **Config = Protocol implementation holder** (not controller)
- **Flow:** Mahamantra protocols → Config respects them → Kernel reads once → Runtime frozen

---

## SECTION 1: WHAT MAHAMANTRA ALREADY DECLARES

### A. The Law Is Already Written

**Location:** `vibe_core/mahamantra/protocols/`

Mahamantra already defines:

1. **PanchaTattvaProtocol** (`_pancha.py`)
   ```
   EVERY entity must answer 5 questions:
   - chaitanya: IDENTITY (What am I?)
   - nityananda: SUBSTRATE (What do I depend on?)
   - advaita: CAUSALITY (Why do I exist?)
   - gadadhara: ENERGY (How do I flow?)
   - srivasa: GOVERNANCE (Who controls me?)
   ```

2. **MantraProtocol** (`substrate/protocol.py`)
   ```
   PRINCIPLE: Position index is the ONLY configuration.
   All properties derive from truth table.
   Kein Duplikat mehr. Nur diese Datei.
   ```

3. **Other Protocols Already Declared:**
   - AuditProtocol
   - BlueprintProtocol
   - BridgeProtocol
   - SankirtanProtocol
   - BhavaProtocol
   - AdhikaraProtocol (Authorization)
   - And 15+ more

### B. What This Means

**Mahamantra is declaring:**
> "I am the source of protocols. Everything that touches consciousness must implement my protocols. No exceptions. No legacy code."

---

## SECTION 2: OPERATION SCOPE & PHASES

### PHASE 0: DECLARATION (What We're Building)
**Status:** This document  
**Time:** 0 hours (planning)  
**Risk:** None

Create the **ConfigInjectionProtocol** in Mahamantra that says:
> "Any system that provides configuration values MUST implement this protocol"

**New Protocol to Add:**
```python
# vibe_core/mahamantra/protocols/_config_injection.py

@runtime_checkable
class ConfigValueProtocol(Protocol):
    """A value holder that can be injected into the kernel."""
    
    @property
    def __tattva__(self) -> TattvaDict:
        """Every config value answers the 5 questions."""
        ...
    
    def validate(self) -> bool:
        """Prove you comply with the protocol."""
        ...

@runtime_checkable
class ConfigInjectionProtocol(Protocol):
    """
    A system that provides configuration values.
    
    CONTRACT:
    1. Read from filesystem ONCE at boot
    2. Validate all values against ConfigValueProtocol
    3. Provide immutable view to Kernel
    4. Never mutate after kernel boot
    5. Track all values that came from where
    """
    
    @property
    def __tattva__(self) -> TattvaDict:
        """Who are we, what we depend on, why we exist."""
        ...
    
    def provide_values(self) -> Dict[str, Any]:
        """Return all config values."""
        ...
    
    def validate_all(self) -> AuditReport:
        """Prove all values are protocol-compliant."""
        ...
    
    def freeze(self) -> None:
        """Lock configuration after kernel initialization."""
        ...
```

### PHASE 1: CONFIG LAYER ADAPTATION (Filesystem → Protocol)
**What:** Make existing config layers implement the new protocol  
**Where:** `vibe_core/mahamantra/substrate/config.py` + `vibe_core/phoenix/`  
**Time:** 4-6 hours  
**Risk:** MEDIUM (config is foundational)  

**Scope:**

1. **Add ConfigInjectionProtocol declaration**
   - Config must implement it (not concrete class, PROTOCOL)
   - No new classes needed, just add methods
   - Everything derives from the protocol, not vice versa

2. **Adaptation Points:**
   - `config.py`: Add `__tattva__`, `validate_all()`, `freeze()`
   - `section_loader.py`: All sections must implement ConfigValueProtocol
   - `steward.yaml`: Add metadata describing which protocol each value satisfies

3. **What DOESN'T Change:**
   - Existing code continues to read config normally
   - No backwards-breaking changes
   - Legacy adapters can still use old patterns

4. **Implications:**
   - Config now declares "I am protocol-compliant" (not "I am the king")
   - Every value traceable to protocol it satisfies
   - Config becomes auditability

---

### PHASE 2: KERNEL ADAPTATION (Config Slave Pattern)
**What:** Kernel accepts config as protocol implementation, not as master  
**Where:** `vibe_core/mahamantra/kernel/maha_kernel.py`  
**Time:** 2-3 hours  
**Risk:** LOW (kernel reads config, doesn't write it)  

**Scope:**

1. **Add KernelInjectionProtocol**
   ```python
   @runtime_checkable
   class KernelInjectionProtocol(Protocol):
       """Kernel accepts protocol-compliant config, never reads it again."""
       
       def inject_config(self, config: ConfigInjectionProtocol) -> None:
           """Accept config once, validate it, freeze it."""
           ...
       
       def get_frozen_value(self, key: str) -> Any:
           """Get value that was injected at boot time."""
           ...
   ```

2. **Kernel Boot Process:**
   - `__init__`: Accept ConfigInjectionProtocol
   - Call `config.validate_all()` — get AuditReport
   - If invalid, raise ProtocolViolation
   - If valid, copy values to kernel's own memory
   - Call `config.freeze()` — prevent further writes
   - Never read config again

3. **What DOESN'T Change:**
   - Kernel's decision logic
   - Kernel's protocols
   - Services that query kernel

4. **Implications:**
   - Config is NOW a PROTOCOL IMPLEMENTATION, not a controller
   - Kernel proves it validated everything before using it
   - Runtime cannot change config anymore

---

### PHASE 3: SERVICE LAYER REVERSAL (Services as Adapters, Not Masters)
**What:** Services must stop importing from Mahamantra, start implementing Mahamantra  
**Where:** All files outside `mahamantra/`  
**Time:** 8-12 hours  
**Risk:** HIGH (breaks service assumptions)  

**Scope:**

1. **Create ServiceImplementationProtocol** (IN Mahamantra)
   ```python
   # vibe_core/mahamantra/protocols/_service_adapter.py
   
   @runtime_checkable
   class ServiceAdapterProtocol(Protocol):
       """
       Legacy services MUST implement this to work with Mahamantra kernel.
       
       CONTRACT:
       1. Never import from mahamantra.mahajanas (circular!)
       2. Never instantiate yourself
       3. Wait to be injected by kernel
       4. Implement __tattva__ so kernel understands you
       """
       
       @property
       def __tattva__(self) -> TattvaDict:
           """What are you, why do you exist."""
           ...
       
       def accept_kernel(self, kernel: KernelInjectionProtocol) -> None:
           """Kernel injects itself into you."""
           ...
   ```

2. **Identify Backwards Imports** (HIGH PRIORITY)
   - `sankalpa/will.py`: Imports `chat_service` — SHOULD NOT
   - `adapters/llm.py`: Imports from mahajanas — SHOULD NOT
   - `dharma/kapila/`: Imports `KapilaService` — SHOULD NOT
   - `genesis/brahma/`: Imports `BrahmaService` — SHOULD NOT
   - `moksha/yamaraja/`: Imports `yamaraja_service` — SHOULD NOT
   - **Count: 19 critical backwards imports**

3. **Reversal Pattern:**
   ```
   BEFORE (Service is master):
   service = MyService()
   service.mahamantra_component = get_from_mahamantra()
   service.run()
   
   AFTER (Mahamantra kernel injects):
   kernel = MahaKernel(config)
   service = MyService()  # No imports from mahamantra
   kernel.inject_into_service(service)  # Kernel injects itself
   service.run()
   ```

4. **What DOESN'T Change:**
   - Service behavior
   - Service logic
   - External APIs

5. **Implications:**
   - Services become protocol implementations
   - Services can work with ANY kernel that implements KernelInjectionProtocol
   - No circular imports
   - Mahamantra controls the narrative

---

### PHASE 4: WILL/SANKALPA REWRITE (CRITICAL)
**What:** Will must not depend on services, must receive kernel context  
**Where:** `vibe_core/mahamantra/sankalpa/will.py`  
**Time:** 2-4 hours  
**Risk:** HIGH (will is core)  

**Scope:**

1. **Create WillExecutionProtocol** (IN Mahamantra)
   ```python
   # vibe_core/mahamantra/protocols/_will_execution.py
   
   @runtime_checkable
   class WillExecutionProtocol(Protocol):
       """
       Will/Intention execution MUST follow this protocol.
       
       Will is the BRIDGE between Sankalpa (intention) and Karma (action).
       Will MUST NOT depend on services.
       Will MUST be pure decision logic.
       """
       
       @property
       def __tattva__(self) -> TattvaDict:
           # chaitanya: "Executor of intention"
           # nityananda: "Context from kernel"
           # advaita: "Protocol of action"
           # gadadhara: "Decision flow"
           # srivasa: "Kernel governance"
           ...
       
       def can_execute(self, context: SankirtnContext) -> bool:
           """Do we have permission from kernel?"""
           ...
       
       def execute(self, context: SankirtnContext) -> Result:
           """Execute with kernel-provided resources only."""
           ...
   ```

2. **Will's Current Problem:**
   - Line 1: `from vibe_core.chat_service import ...` ← BACKWARDS
   - Imports service, tries to instantiate
   - Should receive chat capability from kernel context

3. **Will's New Pattern:**
   ```python
   class WillManifesto:
       """Pure will, no service imports."""
       
       def execute(self, context: SankirtnContext):
           # Get everything from context.kernel:
           llm = context.kernel.get_frozen_value("llm_provider")
           cache = context.kernel.get_frozen_value("cache_backend")
           audit = context.kernel.get_frozen_value("audit_mixin")
           
           # Execute pure logic
           return self._decide_and_act(llm, cache, audit)
   ```

4. **Implications:**
   - Will becomes protocol-compliant
   - Will is testable without services
   - Will is provably safe (audit trail)

---

### PHASE 5: ADAPTER LAYER (Legacy to Protocol)
**What:** Create adapters that bridge legacy services to Mahamantra protocols  
**Where:** `vibe_core/mahamantra/adapters/`  
**Time:** 6-8 hours  
**Risk:** MEDIUM (adapters are new)  

**Scope:**

1. **Create AdapterProtocol** (IN Mahamantra)
   ```python
   # vibe_core/mahamantra/protocols/_adapter.py
   
   @runtime_checkable
   class AdapterProtocol(Protocol):
       """
       Adapters bridge legacy code to Mahamantra.
       
       Adapters are TRANSLATORS, not implementations.
       They never drive the narrative.
       They only speak the Mahamantra language.
       """
       
       @property
       def __tattva__(self) -> TattvaDict:
           # chaitanya: "Bridge to legacy X"
           # nityananda: "Legacy system Y"
           # advaita: "Mahamantra protocol Z"
           # gadadhara: "Translation flow"
           # srivasa: "Kernel control"
           ...
       
       def translate_to_protocol(self, legacy_input: Any) -> ProtocolCompliantValue:
           """Convert legacy format to protocol format."""
           ...
       
       def translate_to_legacy(self, protocol_output: ProtocolCompliantValue) -> Any:
           """Convert protocol output back to legacy format."""
           ...
   ```

2. **Adapter Examples:**
   - `adapters/llm.py`: Bridge LLMProviderMixin to legacy LLM services
   - `adapters/cache.py`: Bridge CacheMixin to legacy cache services
   - `adapters/audit.py`: Bridge DriftAuditMixin to legacy audit services

3. **Implications:**
   - Legacy services can keep running
   - No immediate rewrite needed
   - Clear migration path

---

### PHASE 6: AUDIT & ATTESTATION (Trust & Verification)
**What:** Prove all layers implement all protocols  
**Where:** `vibe_core/mahamantra/audit/`  
**Time:** 3-4 hours  
**Risk:** LOW (audit is observation)  

**Scope:**

1. **Create ProtocolComplianceAudit**
   ```python
   # vibe_core/mahamantra/audit/protocol_compliance.py
   
   @runtime_checkable
   class ProtocolComplianceAuditProtocol(Protocol):
       """Audit that all layers implement declared protocols."""
       
       def audit_config_layer(self) -> ComplianceReport:
           """Does config implement ConfigInjectionProtocol?"""
           ...
       
       def audit_kernel_layer(self) -> ComplianceReport:
           """Does kernel implement KernelInjectionProtocol?"""
           ...
       
       def audit_services(self) -> ComplianceReport:
           """Do services implement ServiceAdapterProtocol?"""
           ...
       
       def audit_all(self) -> ComplianceReport:
           """Full system audit."""
           ...
   ```

2. **Audit Report Structure:**
   - ✓ COMPLIANT: Implementation matches protocol
   - ⚠️ PARTIAL: Some aspects missing
   - ✗ VIOLATION: Backwards import or protocol breach
   - → MIGRATION: Path to compliance

3. **Implications:**
   - Trust is verifiable, not assumed
   - Regressions are detectable
   - Mahamantra controls the truth

---

## SECTION 3: HIERARCHY & FLOW

### The Law (Mahamantra Protocols) Flows Down

```
LEVEL 0: MAHAMANTRA PROTOCOLS (The King)
  └─ ConfigInjectionProtocol
  └─ KernelInjectionProtocol
  └─ ServiceAdapterProtocol
  └─ WillExecutionProtocol
  └─ AdapterProtocol
  └─ ProtocolComplianceAuditProtocol
  └─ And all 50+ existing protocols

LEVEL 1: CONFIG IMPLEMENTATION (Protocol Slave)
  └─ vibe_core/mahamantra/substrate/config.py
  └─ vibe_core/phoenix/sections/
  └─ steward.yaml
  └─ IMPLEMENTS: ConfigInjectionProtocol
  └─ NEVER controls kernel

LEVEL 2: KERNEL IMPLEMENTATION (Consciousness)
  └─ vibe_core/mahamantra/kernel/maha_kernel.py
  └─ IMPLEMENTS: KernelInjectionProtocol
  └─ Reads config ONCE
  └─ Injects into services
  └─ Frozen at boot

LEVEL 3: SERVICE LAYER (Protocol Implementers)
  └─ All legacy services (outside mahamantra/)
  └─ IMPLEMENTS: ServiceAdapterProtocol
  └─ Accepts kernel injection
  └─ No circular imports
  └─ No self-instantiation

LEVEL 4: ADAPTER LAYER (Bridges)
  └─ vibe_core/mahamantra/adapters/
  └─ IMPLEMENTS: AdapterProtocol
  └─ Translates legacy to protocol
  └─ Never drives narrative

LEVEL 5: AUDIT LAYER (Trust)
  └─ vibe_core/mahamantra/audit/
  └─ IMPLEMENTS: ProtocolComplianceAuditProtocol
  └─ Verifies all layers
  └─ Reports violations
```

### Information Flow (Never Backwards)

```
Boot Time:
  1. Mahamantra declares protocols
  2. Config loads from filesystem
  3. Config proves it's ConfigInjectionProtocol-compliant
  4. Kernel accepts config
  5. Kernel freezes config
  6. Kernel injects itself into services
  7. Services accept injection
  8. Everything is locked

Runtime:
  1. Services query kernel for frozen values
  2. Kernel returns values set at boot
  3. Audit trails are written
  4. NO ONE mutates config
  5. NO ONE reads filesystem (except audit logs)
```

---

## SECTION 4: IMPLEMENTATION TIMELINE & DEPENDENCIES

### Critical Path Analysis

```
PREREQUISITES (Before starting):
  - Read Mahamantra protocols (already exist)
  - Understand PanchaTattvaProtocol (already defined)
  - Agree on ConfigInjectionProtocol (Phase 0)

PHASE 0: DECLARATION
  ├─ Create ConfigInjectionProtocol (2 hours)
  ├─ Create KernelInjectionProtocol (1 hour)
  ├─ Create ServiceAdapterProtocol (1 hour)
  ├─ Create WillExecutionProtocol (1 hour)
  ├─ Create AdapterProtocol (1 hour)
  ├─ Create ProtocolComplianceAuditProtocol (1 hour)
  └─ Total: 7 hours (PARALLELIZABLE)

PHASE 1: CONFIG ADAPTATION
  ├─ Depends on: Phase 0 complete
  ├─ Add methods to config.py (3 hours)
  ├─ Update all sections to implement ConfigValueProtocol (2 hours)
  ├─ Update steward.yaml metadata (1 hour)
  └─ Total: 6 hours (SEQUENTIAL)

PHASE 2: KERNEL ADAPTATION
  ├─ Depends on: Phase 0 complete, Phase 1 progress
  ├─ Update maha_kernel.py (2 hours)
  ├─ Add injection mechanism (1 hour)
  └─ Total: 3 hours (SEQUENTIAL)

PHASE 3: SERVICE REVERSAL
  ├─ Depends on: Phase 0, 1, 2 complete
  ├─ Identify 19 backwards imports (1 hour)
  ├─ Create migration tickets for each (2 hours)
  ├─ Update each service to implement ServiceAdapterProtocol (8 hours, PARALLELIZABLE)
  ├─ Remove backwards imports (4 hours, PARALLELIZABLE)
  └─ Total: 15 hours (MOSTLY PARALLELIZABLE)

PHASE 4: WILL/SANKALPA REWRITE
  ├─ Depends on: Phase 2 complete
  ├─ Create WillExecutionProtocol (1 hour, included in Phase 0)
  ├─ Rewrite will.py (3 hours)
  └─ Total: 3 hours (CRITICAL PATH)

PHASE 5: ADAPTER LAYER
  ├─ Depends on: Phase 0, 1, 2, 3 complete
  ├─ Create adapters/ structure (1 hour)
  ├─ Write LLM adapter (2 hours)
  ├─ Write cache adapter (2 hours)
  ├─ Write audit adapter (2 hours)
  ├─ Write other adapters (2 hours)
  └─ Total: 9 hours (PARALLELIZABLE)

PHASE 6: AUDIT & ATTESTATION
  ├─ Depends on: All phases complete
  ├─ Write compliance audit logic (3 hours)
  ├─ Run audit against codebase (1 hour)
  └─ Total: 4 hours (SEQUENTIAL)

CRITICAL PATH (Sequential Must-Dos):
  Phase 0 (7h) → Phase 1 (6h) → Phase 2 (3h) → Phase 4 (3h) → Phase 6 (4h)
  = 23 hours minimum (if no bugs)

TOTAL EFFORT:
  Sequential: 23 hours
  With parallelization: ~14-16 hours (overlapping Phase 3, 5)
```

---

## SECTION 5: RISKS & MITIGATIONS

### RISK 1: Config is Foundational (CRITICAL)
**Impact:** If config breaks, everything breaks  
**Mitigation:**
- Add protocol validation BEFORE kernel reads anything
- Kernel must call `config.validate_all()` and check AuditReport
- Fallback to in-memory defaults if validation fails
- Phase 1 must have comprehensive tests

### RISK 2: Backwards Imports Are Circular (HIGH)
**Impact:** Services try to import from Mahamantra, Mahamantra needs services  
**Mitigation:**
- Never import service code in Mahamantra
- Services implement protocols (no inheritance needed)
- Kernel injects instances at runtime
- Phase 3 must be surgical about import removal

### RISK 3: Will/Sankalpa is Core (HIGH)
**Impact:** If will breaks, all action breaks  
**Mitigation:**
- Will receives kernel context, not service imports
- Will must be testable in isolation
- Phase 4 must have integration tests with real kernel
- Gradual rollout with feature flags

### RISK 4: Legacy Code Still References Old Patterns (MEDIUM)
**Impact:** Code keeps reading config directly instead of asking kernel  
**Mitigation:**
- Phase 5 adapters bridge old and new code
- Old code works until migrated
- Audit logs warn about backwards reads
- No hard cutoff, gradual migration

### RISK 5: Protocol Compliance Checking is Expensive (LOW)
**Impact:** Audit on every boot could slow startup  
**Mitigation:**
- Compliance check happens ONCE at boot
- Cache compliance result
- Lazy evaluation of subprotocols
- Phase 6 audit can be optional in prod

---

## SECTION 6: WHAT THIS ACCOMPLISHES

### Trust Model (Why You Can Trust This)

**Before This Plan:**
- Filesystem controls consciousness (backwards)
- Circular imports everywhere
- No way to verify compliance
- Services are authorities
- Hard to test without full stack

**After This Plan:**
- Mahamantra protocols are AUTHORITY
- Every layer implements a protocol (verifiable)
- Config proves compliance with audit
- Kernel injects everything (services are servants)
- Each layer testable in isolation
- Backwards reads are detectable as violations

### How to Verify Trust

```python
# After Phase 0-6 complete:

# 1. Audit system
audit = ProtocolComplianceAudit()
report = audit.audit_all()

# 2. Verify each layer
assert report.config_layer == "COMPLIANT"
assert report.kernel_layer == "COMPLIANT"
assert report.services_layer == "COMPLIANT"  # 19 formerly backwards services

# 3. Verify protocols
assert isinstance(config, ConfigInjectionProtocol)
assert isinstance(kernel, KernelInjectionProtocol)
assert all(isinstance(s, ServiceAdapterProtocol) for s in services)

# 4. Verify freezing
config.freeze()
with pytest.raises(ConfigMutationViolation):
    config.set_value("foo", "bar")  # After freeze, forbidden
```

### Pancha Tattva Alignment

Every protocol we create answers the 5 questions:

```
ConfigInjectionProtocol:
  chaitanya: "Configuration provider"
  nityananda: "Filesystem + YAML substrate"
  advaita: "Protocol invokes config loading"
  gadadhara: "Values flow to kernel"
  srivasa: "Kernel governs what config can do"

KernelInjectionProtocol:
  chaitanya: "Consciousness/Decision maker"
  nityananda: "Config-provided values"
  advaita: "Protocol of consciousness"
  gadadhara: "Kernel energy flows to services"
  srivasa: "Kernel controls all injection"

ServiceAdapterProtocol:
  chaitanya: "Service/Tool"
  nityananda: "Kernel provides resources"
  advaita: "Mahamantra protocol requires this"
  gadadhara: "Service performs action"
  srivasa: "Kernel controls invocation"
```

---

## SECTION 7: IMMEDIATE DECISION POINTS

**Question 1:** Should Phase 0 (declaring new protocols) happen first?
- ✓ YES: Must declare before implementation
- Timeline: 7 hours (can parallel most)

**Question 2:** Can we keep legacy services working during migration?
- ✓ YES: Phase 5 (adapters) allows gradual transition
- No hard cutoff needed

**Question 3:** Is will.py rewrite blocking other work?
- ⚠️ PARTIAL: Will is on critical path
- But Phase 1-2 can progress in parallel
- Will rewrite happens Phase 4

**Question 4:** Should audit be mandatory or optional?
- ✓ MANDATORY on boot: Proves compliance
- Optional on request: For detailed forensics
- Phase 6 defines both

**Question 5:** How do we handle config hot-reload (if needed)?
- ✗ FORBIDDEN in this protocol
- Config freezes at kernel boot
- For hot-reload, would need separate layer (future)

---

## SECTION 8: WHAT HAPPENS AFTER

### Mahamantra Becomes Observable

```
Before:
  Config controls kernel (black box)
  Services are chaotic (no protocol)
  Will is hidden (imports everything)
  Trust is assumed

After:
  All layers declare what they are
  All imports are verifiable
  All flows trace to protocol
  Trust is verified by audit
```

### Backwards Imports Become Violations

```
Before:
  will.py: from vibe_core.chat_service import ... ✓ (works but backwards)

After:
  will.py: from vibe_core.chat_service import ... ✗ (PROTOCOL VIOLATION)
  Audit report: "VIOLATION: WillExecutionProtocol violated"
  Fix: "Remove import, accept kernel.get_frozen_value('chat_service')"
```

### Everything is Traceable

```
Before:
  "Where did llm_provider come from?"
  → Check config.yaml
  → Check environment
  → Check service registry
  → ???

After:
  kernel.get_frozen_value("llm_provider")
  → Trace back: came from config
  → Trace back: config said it came from ConfigInjectionProtocol
  → Trace back: protocol requires ConfigValueProtocol compliance
  → Audit shows: "ConfigValueProtocol validated at 2026-02-05 02:08:59"
```

---

## SECTION 9: DECISION: PROCEED?

This plan is:
- ✓ **Protocol-based** (no concrete classes until implementation)
- ✓ **Trust-verifiable** (audit proves compliance)
- ✓ **Backwards-compatible** (Phase 5 adapters allow gradual migration)
- ✓ **Hierarchical** (Mahamantra protocols are unquestionable king)
- ✓ **Traceable** (all flows point to protocol)
- ✓ **Pancha-Tattva aligned** (every protocol answers 5 questions)
- ✓ **No temp files** (protocol document is in repo)

**Critical Path:** 23 hours sequential, ~14-16 hours with parallelization

**Highest Risk:** Will/Sankalpa rewrite and backwards import removal

**Highest Value:** After completion, system becomes auditable and trustworthy

---

**Awaiting your direction:**
1. Approve Phase 0 declaration of protocols?
2. Should we start with Phase 1 (config adaptation) or Phase 4 (will rewrite)?
3. Do you want audit to be mandatory on every boot, or configurable?
