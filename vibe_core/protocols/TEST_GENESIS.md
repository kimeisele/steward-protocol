# TEST_GENESIS - What Already Exists

> "Don't build what's already there."

## THE FORMULA (ALREADY IMPLEMENTED)

```
PROTOCOL + GENE + TÜV = TEST
    ↓        ↓      ↓      ↓
substrate  iGene  tuv.py  Testable
```

## WHAT EXISTS

### 1. PROTOCOLS (Layer -1: substrate/__init__.py)

```
vibe_core/protocols/substrate/__init__.py  (1500+ lines)
├── MantraOpCode (16 steps)
├── MAHAMANTRA_SEQUENCE
├── IGene, IGeneHost
├── GeneManifest, GeneStatus, GeneActivationState
├── GeneMetrics (TypedDict)
└── All pure interfaces, ZERO imports
```

### 2. GENES (substrate/gene.py)

```python
@dataclass(frozen=True)
class iGene:
    entropy_load: float       # Kali Yuga stress (0.0-1.0)
    mantra_shield: MantraByte # Protection via coherence
    mutation_vector: int      # Bitflips allowed

    @property
    def is_fatal(self) -> bool:
        return self.entropy_load > self.mantra_shield.coherence
```

**Gene Host**: `AnantaShesha` in `ouroboros/ananta_shesha.py` implements `IGeneHost`

### 3. TÜV (protocols/naga/tuv.py)

```python
@runtime_checkable
class TÜVProtocol(Protocol):
    def register_leak(leak: Leak) -> str
    def scan_file(filepath: str) -> List[Leak]
    def audit_protocol(protocol_name, service_name) -> ProtocolAudit
    def issue_badge(target: str) -> TuvBadge
    def verify_badge(badge: TuvBadge) -> bool
```

**Data**: `Leak`, `ProtocolGap`, `TuvBadge`, `FindingRegistry[F]`

### 4. TESTABLE PROTOCOL (protocols/testable.py - 827 lines)

```python
@runtime_checkable
class Testable(Protocol):
    @property
    def testable_id(self) -> str: ...
    @property
    def testable_type(self) -> TestableType: ...
    def get_test_cases(self) -> List[TestCase]: ...
```

**TestableType enum**:
- AGENT, PLUGIN, TOOL, SYSCALL
- LEDGER, SCHEDULER, EVENT_BUS, ROUTER
- GOVERNANCE, SECURITY, RUNTIME, CORE

**Adapters** (auto-wrap components):
- `AgentTestableAdapter`
- `PluginTestableAdapter`
- `ToolTestableAdapter`
- `LedgerTestableAdapter`
- `SchedulerTestableAdapter`
- `EventBusTestableAdapter`

### 5. TESTABLE REGISTRY (protocols/testable_registry.py)

```python
class TestableRegistry:
    def discover_from_kernel(kernel) -> None:
        # Auto-discovers from:
        # - kernel.agent_registry → AgentTestableAdapter
        # - kernel._plugins → PluginTestableAdapter
        # - kernel.tool_registry → ToolTestableAdapter
        # - kernel.ledger → LedgerTestableAdapter
        # - kernel.scheduler → SchedulerTestableAdapter
        # - EventBus singleton → EventBusTestableAdapter

    def get_all_test_cases() -> List[TestCase]
    def get_test_cases_by_type(testable_type) -> List[TestCase]
    def get_summary() -> Dict  # total_testables, total_tests, by_type
```

### 6. TEST ORCHESTRATION PLUGIN (plugins/test_orchestration/)

```python
class OrchestrationPlugin:
    priority = 200  # Runs after all other plugins

    def on_boot(self):
        # Auto-discovers ALL testable components
        # Generates tests dynamically
        # Records results to ledger
```

**Fixtures** (`fixtures.py` - MINIATURWUNDERLAND):
- `TestAgents`: compliant, no_oath, false_oath
- `TestKernel`: minimal, permissive, with_governance
- `TestContext`: isolation + cleanup
- `TestTasks`, `TestPlugins`

### 7. MAHAJANA ROUTING (mahajanas/protocol.py)

```python
class MahajanaProtocol(Protocol):
    @property
    def identity(self) -> Mahajana: ...
    def get_opcodes(self) -> List[MantraOpCode]: ...
    def can_handle(self, opcode: MantraOpCode) -> bool: ...
    def handle(opcode, context, payload) -> MahajanaResult: ...
```

**12 Mahajanas own 12 Worker OpCodes** (router.py):
| Mahajana | OpCode(s) | Role |
|----------|-----------|------|
| BRAHMA | SYS_WAKE, LOAD_ROOT, ALLOC_MEM | Creator |
| SHAMBHU | GARBAGE_COLLECT | Destroyer |
| YAMARAJA | ASSERT_TRUTH | Judge |
| KAPILA | RESOLVE_REQ, OPTIMIZE | Analyst |
| MANU | BIND_CTX, CHECK_DHARMA | Lawgiver |
| NARADA | PULSE_SYNC | Messenger |
| PRAHLADA | FETCH_RES | Resilient |
| JANAKA | EXEC_SERVICE | Dutiful |
| BHISHMA | COMMIT_LOG | Vow-keeper |
| BALI | YIELD_CPU | Surrenderer |
| SHUKA | CACHE_STATE | Visionary |
| KUMARAS | RESET_IP | Pure |

### 8. PYTEST INTEGRATION (tests/conftest.py + config/quality.yaml)

```yaml
# config/quality.yaml
test:
  tool: pytest
  profiles:
    fast: exclude slow/integration/e2e (120s)
    full: all tests with coverage (300s)
    ci: parallel, fail-fast
    smoke: quick sanity (10s)
```

```python
# tests/conftest.py
def pytest_collection_modifyitems(items):
    # Auto-marks tests by directory:
    # hardening/ → @pytest.mark.hardening + slow
    # integration/ → @pytest.mark.integration
```

## THE CHAIN (Already Wired)

```
config/quality.yaml
    ↓
tests/conftest.py (hooks)
    ↓
protocols/testable.py (Testable + 6 Adapters)
    ↓
protocols/testable_registry.py (auto-discovery)
    ↓
plugins/test_orchestration/ (dynamic generation)
    ↓
protocols/substrate/gene.py (iGene with entropy/coherence)
    ↓
ouroboros/ananta_shesha.py (IGeneHost)
    ↓
protocols/mahajanas/ (12 judges route by OpCode)
    ↓
tests/mahajanas/ (12 test folders)
```

## WHAT'S MISSING (Gap Analysis)

### Gap 1: Mahamantra Lifecycle in Pytest
The 16-step cycle exists in `MAHAMANTRA_SEQUENCE` but pytest doesn't USE it.

**Current**: pytest runs setup → test → teardown (3 phases)
**Vision**: pytest runs 16-step Mahamantra cycle (4 phases × 4 steps)

### Gap 2: Gene Injection in Tests
`iGene` exists but tests don't spawn with genes.

**Current**: Tests are static functions
**Vision**: Tests are born with `entropy_load`, `mantra_shield`, `mutation_vector`

### Gap 3: TÜV Badge for Tests
`TuvBadge` exists but tests don't get certified.

**Current**: Tests pass/fail
**Vision**: Tests get TÜV certification (Bronze/Silver/Gold)

### Gap 4: TestableRegistry → Pytest Bridge
Registry discovers tests but doesn't feed pytest.

**Current**: Two separate systems
**Vision**: One system where discovered tests ARE pytest tests

## NEXT STEPS

1. **Bridge TestableRegistry to pytest**
   - `pytest_generate_tests` hook reads from TestableRegistry
   - Each discovered `TestCase` becomes a pytest test

2. **Mahamantra Test Lifecycle**
   - Custom pytest plugin that wraps test execution in 16-step cycle
   - Each phase triggers appropriate Mahajana

3. **Gene-Based Test Spawning**
   - Tests instantiated with `iGene`
   - `entropy_load` determines chaos injection
   - `mantra_shield.coherence` determines pass threshold

4. **TÜV Integration**
   - Tests that pass get `TuvBadge`
   - Badge level based on coverage + resilience

## FILES TO MODIFY

| File | Change |
|------|--------|
| `tests/conftest.py` | Add Mahamantra hooks |
| `protocols/testable_registry.py` | Expose to pytest |
| `plugins/test_orchestration/plugin_main.py` | Gene injection |
| `protocols/naga/tuv.py` | Badge tests on pass |

## VERDICT

**Du hast recht.** The architecture IS in place:
- Protocol = substrate
- Gene = iGene
- TÜV = tuv.py
- Test = Testable + Adapters + Registry

**Was fehlt**: Die VERKABELUNG zwischen den Teilen.
The pieces exist but don't talk to each other in the test lifecycle.

---

*"The building blocks are there. We just need to wire them."*
