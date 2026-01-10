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

## GAPS WIRED (All Complete)

All 4 gaps have been wired in `tests/conftest.py`:

### Gap 1: Mahamantra Lifecycle in Pytest (WIRED)

```python
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Phase 1: GENESIS (H K H K) - Steps 1-4"""

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_call(item):
    """Phase 2: DHARMA (K K H H) - Steps 5-8
       Phase 3: KARMA (H R H R) - Steps 9-12"""

@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item, nextitem):
    """Phase 4: MOKSHA (R R H H) - Steps 13-16"""
```

Every test now runs the 16-step Mahamantra cycle.

### Gap 2: Gene Injection in Tests (WIRED)

```python
@pytest.fixture
def test_gene(request):
    """Auto-entropy based on markers:
       hardening → 0.8, integration → 0.5, slow → 0.6, smoke → 0.1"""

@pytest.fixture
def chaos_gene(request):  # entropy = 0.9 (near fatal)

@pytest.fixture
def sattva_gene(request):  # entropy = 0.1 (stable)
```

Tests are BORN with iGene. if `entropy_load > mantra_shield.coherence` → FATAL.

### Gap 3: TÜV Badge for Tests (WIRED)

```python
def _issue_tuv_badge(test_id, duration, gene_data):
    """Score: 0.5 (passed) + 0.3 (sattva) + 0.2 (speed<1s)
       Levels: GOLD (≥0.9), SILVER (≥0.7), BRONZE (<0.7)"""

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Prints TÜV badge distribution at session end."""
```

Every passing test receives a TuvBadge. Session ends with badge summary.

### Gap 4: TestableRegistry → Pytest Bridge (WIRED)

```python
def pytest_generate_tests(metafunc):
    """If test uses 'registry_test_case' fixture, parametrize with
       all discovered TestCases from TestableRegistry."""

@pytest.fixture
def run_registry_test(fresh_kernel, test_gene):
    """Execute a TestCase with kernel + gene context."""
```

TestableRegistry discovers components (ledger, scheduler, event_bus).
Each TestCase becomes a real pytest test via parametrization.

**Verified**: 8 discovered tests pass (3 ledger, 3 scheduler, 2 event_bus).

## THE CHAIN (Fully Wired)

```
config/quality.yaml
    ↓
tests/conftest.py
    ├── pytest_runtest_setup → GENESIS (steps 1-4)
    ├── pytest_runtest_call → DHARMA + KARMA (steps 5-12)
    ├── pytest_runtest_teardown → MOKSHA (steps 13-16)
    ├── test_gene fixture → iGene injection
    ├── _issue_tuv_badge → TuvBadge on pass
    └── pytest_generate_tests → TestableRegistry bridge
    ↓
protocols/testable.py (6 Adapters)
    ↓
protocols/testable_registry.py (auto-discovery)
    ↓
protocols/substrate/gene.py (iGene lifecycle)
    ↓
protocols/naga/tuv.py (TuvBadge certification)
```

## VERIFICATION TEST

```bash
pytest tests/protocols/test_registry_bridge.py -v
# 12 passed, Average TÜV Score: 0.81
```

## VERDICT

**Verkabelt.** The wiring is complete:
- Protocol = substrate (Mahamantra lifecycle)
- Gene = iGene (injected per test)
- TÜV = TuvBadge (issued on pass)
- Test = Testable → Registry → Pytest (bridge complete)

---

*"Tests are BORN, not written. They live, execute, and die by the Mahamantra."*
