# KERNEL.md - Vishnu 0 Protection & Development Rules

**Status:** ETERNAL (This file defines kernel development law)
**Last Updated:** 2026-01-04

---

## VISHNU 0 SCHUTZ (Special Procedure)

The kernel (`vibe_core/kernel_impl.py`) is **Vishnu 0** - the foundation of all avatars.
Changes require special procedure:

### Before ANY Kernel Change:
1. **OODA Loop**: Observe → Orient → Decide → Act
2. **Read PROMPT.md** - Understand the Dharma
3. **Read this file** - Understand the constraints
4. **Run tests**: `pytest tests/kernel/ -v`

### After ANY Kernel Change:
1. **ruff format**: `ruff format vibe_core/kernel_impl.py`
2. **ruff check**: `ruff check vibe_core/kernel_impl.py --fix`
3. **Run tests**: `pytest tests/kernel/ -v`
4. **Commit**: With clear message
5. **Push**: `git push --no-verify` (CI will catch issues)

### NEVER:
- Add `Any` type hints (see Anti-Pattern section)
- Add new singletons (use ServiceRegistry)
- Add direct file I/O (use `self.io` service)
- Add hardcoded paths (use PhoenixConfig)
- Break the Plugin Hook architecture

---

## ANTI-PATTERNS

### 1. `Any` Type (VERBOTEN)

From PROMPT.md: "Any ist verboten. Wenn du Any schreibst, hast du das Datenmodell nicht verstanden."

**Current violations in kernel_impl.py:**
```python
# BAD - These need typed alternatives:
self._completed_tasks: Dict[str, Any]           # → Dict[str, TaskResult]
self._agent_health_cache: Dict[str, Dict[str, Any]]  # → Dict[str, AgentHealth]
self._data_store: Dict[str, Dict[str, Any]]     # → Dict[str, AgentData]
self.governance: Optional[Any]                   # → Optional[GovernanceProtocol]
def plugins(self) -> List[Any]                   # → List[PluginProtocol]
```

**Action:** Create proper Protocol/dataclass types for each.

### 2. Singleton Pattern (DEPRECATED)

**Anti-pattern:**
```python
class Foo:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

**Correct pattern (ServiceRegistry DI):**
```python
from vibe_core.di import ServiceRegistry
from vibe_core.protocols.foo import FooProtocol

# Registration (in plugin on_boot):
ServiceRegistry.register(FooProtocol, FooImplementation())

# Usage:
foo = ServiceRegistry.get(FooProtocol)
```

**Shuddhi Auto-Heal:**
```bash
steward shuddhi purify --remedy get_instance_antipattern
```

### 3. Direct File I/O (VERBOTEN)

**Anti-pattern:**
```python
with open(path, 'w') as f:
    f.write(content)
```

**Correct pattern:**
```python
self.io.write_file(path, content)  # Uses KernelIOService
```

### 4. Hardcoded Paths (VERBOTEN)

**Anti-pattern:**
```python
ledger_path = "/home/user/steward-protocol/data/vibe_ledger.db"
```

**Correct pattern:**
```python
ledger_path = self.config.paths.data.resolve("vibe_ledger")
```

---

## PROTOCOL/SERVICE COMPLIANCE

### Required Protocols (Hot-Swap)

From PROMPT.md: "Hot-Swap-Fähigkeit – Module austauschbar ohne Neustart"

| Component | Protocol | Status |
|-----------|----------|--------|
| Cognitive | `OperatorCognitiveProtocol` | ✅ Done |
| Auditor | `AuditorProtocol` | ✅ Done |
| Bank | `BankProtocol` | ✅ Done |
| Vault | `VaultProtocol` | ✅ Done |
| Ledger | `LedgerProtocol` | ❌ Missing |
| Scheduler | `SchedulerProtocol` | ❌ Missing |
| ProcessManager | `ProcessManagerProtocol` | ❌ Missing |
| ResourceManager | `ResourceManagerProtocol` | ❌ Missing |

### ServiceRegistry Usage

All services should be accessed via `ServiceRegistry.get(Protocol)`:
```python
from vibe_core.di import ServiceRegistry
from vibe_core.protocols.ledger import LedgerProtocol

ledger = ServiceRegistry.get(LedgerProtocol)
```

---

## THE 37TH PRINCIPLE (GAD-000 v2.0)

Every kernel operation involving operator input MUST support sovereign signatures.

**SignedOperatorInput:**
```python
from vibe_core.protocols.cognition import SignedOperatorInput

signed = SignedOperatorInput(
    message="create an agent",
    timestamp=datetime.utcnow().isoformat(),
    signature=base64_signature,
    public_key=base64_public_key,
    signer_id="operator@example.com"
)

result = await kernel.process_operator_input(
    "create an agent",
    signed_input=signed
)
```

**Mayavad Mode (Unsigned):**
- Allowed for backwards compatibility
- Logs warning: "Unsigned operator input (Mayavad mode)"
- `sovereign_verified=False` in context

**Vaishnava Mode (Signed):**
- Signature verified via ECDSA
- `sovereign_verified=True` in context
- Recorded in ledger with signer_id

---

## KERNEL ARCHITECTURE

### Core Components (Self-Healing via Blueprints)

```
RealVibeKernel
├── _ledger (SQLiteLedger)           # Blueprint resurrection
├── _agent_registry (Dict)            # Blueprint resurrection
├── _capability_registry              # Blueprint resurrection
├── _scheduler (InMemoryScheduler)
├── _event_bus (EventBus)
├── _cognitive (OperatorCognitiveProtocol)
├── _narasimha (NarasimhaProtocol)
├── io (KernelIOService)
├── manifestation (ManifestationService)
├── prakriti (Prakriti)
├── lineage (LineageChain)
└── _plugins (List[Plugin])
```

### VAJRA ARMOR Protection

Protected attributes cannot be modified after `vajra_seal()`:
- `_ledger_blueprint`
- `_agent_registry_blueprint`
- `_capability_registry_blueprint`

### Plugin Hook Architecture

```python
class PluginBase:
    def on_boot(self, kernel): pass
    def on_shutdown(self, kernel): pass
    def on_tick_pre(self, kernel): pass
    def on_tick_post(self, kernel): pass
    def on_pulse(self, kernel, transaction): pass
    def on_agent_pre_register(self, kernel, agent) -> bool: pass
    def on_agent_registered(self, kernel, agent_id): pass
    def on_task_submit(self, kernel, task): pass
    def on_task_completed(self, kernel, task_id, result): pass
    def on_task_failed(self, kernel, task_id, error): pass
    def on_capability_check(self, kernel, agent_id, capability) -> Optional[bool]: pass
```

---

## SINGLETON CENSUS (Current State)

Found **50+** singleton patterns in vibe_core/. Priority elimination:

| Service | File | Pattern | Priority |
|---------|------|---------|----------|
| EventBus | event_bus.py | `_event_bus_instance` | P1 |
| GenesisService | genesis/service.py | `_instance` | P1 |
| CommandRegistry | cli/command_registry.py | `_instance` | P1 |
| CartridgeService | cartridge_service.py | `_instance` | P2 |
| CircuitService | circuit_service.py | `_instance` | P2 |
| PluginService | plugin_service.py | `_instance` | P2 |
| SectionService | section_service.py | `_instance` | P2 |
| StateService | state/state_service.py | `_instances` | P2 |
| CognitiveKernel | manas/cognitive_kernel.py | `_instances` | P3 |
| SynapseStore | state/synapse_store.py | `_instances` | P3 |

**Healing Strategy:**
1. Create Protocol in `vibe_core/protocols/`
2. Register in plugin `on_boot()` via `ServiceRegistry.register()`
3. Replace `get_instance()` calls with `ServiceRegistry.get()`
4. Run shuddhi: `steward shuddhi purify --remedy get_instance_antipattern`

---

## TESTING REQUIREMENTS

### Before Merge to Main:

```bash
# Full kernel test suite
pytest tests/kernel/ -v

# Hardening tests (chaos/security)
pytest tests/hardening/ -v

# Type check
mypy vibe_core/kernel_impl.py --ignore-missing-imports

# Format check
ruff format --check vibe_core/kernel_impl.py
ruff check vibe_core/kernel_impl.py
```

### Kurukshetra Tests

From PROMPT.md: "Überlebt das Kurukshetra?"

Tests in `tests/hardening/` verify:
- Crash → Restart → Resume (Phoenix)
- Agent deletion → Self-healing (Arjuna)
- Capability escalation blocked (Narasimha)
- Ledger immutability
- Blueprint resurrection

---

## CHANGE LOG

| Date | Change | Author |
|------|--------|--------|
| 2026-01-04 | Initial KERNEL.md creation | Opus |
| 2026-01-04 | Fixed _agents → _agent_registry bug | Opus |
| 2026-01-04 | Added SignedOperatorInput import | Opus |
