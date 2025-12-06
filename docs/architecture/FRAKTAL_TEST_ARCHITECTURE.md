# Fraktal Test Architecture (PANOPTICON+)

> "Every component knows its own tests." - Fractal Testing Principle
> "Quis custodiet ipsos custodes?" - Who watches the watchers?
> "Who watches the watchers who watch the watchers?" - 4D Hypercube

## Status: 4D ARCHITECTURE

The test architecture has **4 dimensions** - each layer adds intelligence:

```
┌─────────────────────────────────────────────────────────────────┐
│                      4D HYPERCUBE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Layer 4: AGENT INTELLIGENCE                                   │
│  └─ TestWriterAgent understands code, writes intelligent tests │
│                           ↓                                     │
│  Layer 3: PLAYBOOK ORCHESTRATION                               │
│  └─ Multi-agent coordination: analyst → engineer → mechanic    │
│  └─ File: knowledge/playbooks/test_suite_generation.yaml       │
│                           ↓                                     │
│  Layer 2: CIRCUIT VALIDATION                                   │
│  └─ State machine validates test quality, loops until good     │
│  └─ File: knowledge/circuits/test_validation.yaml              │
│                           ↓                                     │
│  Layer 1: CODE FIXTURES (Miniaturwunderland)                   │
│  └─ Standardized TestAgents, TestKernel, TestPlugins           │
│  └─ File: vibe_core/plugins/test_orchestration/fixtures.py     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Why 4D?

| Layer | Problem Solved | Without It |
|-------|----------------|------------|
| 1 (Fixtures) | Standardized mocks | Wild mock classes everywhere |
| 2 (Circuit) | Quality validation | GIGO - garbage tests pass |
| 3 (Playbook) | Multi-perspective | Single-agent blind spots |
| 4 (Agent) | Intelligent design | Dumb template expansion |

**All 4 layers check each other. None alone is sufficient.**

## Philosophy

Tests are **part of the system**, not external observers. Each component carries its own tests - when you add a new agent, its tests come with it. This is the **Miniaturwunderland** pattern: a miniature version of the real system for testing.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    TESTABLE PROTOCOL                            │
│                    vibe_core/protocols/testable.py              │
├─────────────────────────────────────────────────────────────────┤
│  Testable Protocol    ← Any component can self-test            │
│  TestCase Dataclass   ← Standardized test definition           │
│  TestableType Enum    ← agent, plugin, tool, ledger, etc.      │
│                                                                 │
│  ADAPTERS (wrap legacy components):                            │
│  ├─ AgentTestableAdapter   ← Wraps VibeAgent                   │
│  ├─ PluginTestableAdapter  ← Wraps KernelPlugin                │
│  ├─ ToolTestableAdapter    ← Wraps Tool                        │
│  ├─ LedgerTestableAdapter  ← Wraps Ledger                      │
│  ├─ SchedulerTestableAdapter                                   │
│  └─ EventBusTestableAdapter                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  TESTABLE REGISTRY                              │
│                  vibe_core/protocols/testable_registry.py       │
├─────────────────────────────────────────────────────────────────┤
│  discover_from_kernel()  ← Auto-finds ALL testable components  │
│  get_all_test_cases()    ← Returns every test from every comp  │
│  get_test_cases_by_type()← Filter by component type            │
│  get_testables_by_type() ← Get components by category          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              TEST ORCHESTRATION PLUGIN                          │
│              vibe_core/plugins/test_orchestration/              │
├─────────────────────────────────────────────────────────────────┤
│  plugin_main.py:                                                │
│  ├─ run_all_tests()      ← Execute all discovered tests        │
│  ├─ run_tests_by_type()  ← Run specific categories             │
│  ├─ run_tests_by_tag()   ← Filter by tags (fast, security)     │
│  ├─ run_pytest()         ← Integration with pytest             │
│  └─ Results → Ledger     ← Immutable recording                 │
│                                                                 │
│  test_guardian.py:                                              │
│  ├─ Records test hashes at "birth"                             │
│  ├─ Detects mutations before execution                         │
│  ├─ BLOCKS AI from modifying tests                             │
│  └─ Logs all mutation attempts to lineage                      │
└─────────────────────────────────────────────────────────────────┘
```

## Key Differences from pytest

| pytest | Fraktal Test Architecture |
|--------|---------------------------|
| Tests external in `tests/` folder | Tests TRAVEL WITH components |
| AI can modify tests to hide bugs | TestGuardian BLOCKS AI modifications |
| Static, runs before deployment | Can test at RUNTIME |
| No governance integration | Results recorded to immutable Ledger |
| Manual test discovery | Auto-discovery via adapters |
| Add tests manually per component | Plug-and-Play: new agent = new tests |

## Component Types Supported

```python
class TestableType(str, Enum):
    AGENT = "agent"        # VibeAgent implementations
    PLUGIN = "plugin"      # KernelPlugin implementations
    TOOL = "tool"          # Tool implementations
    SYSCALL = "syscall"    # SyscallType handlers
    LEDGER = "ledger"      # Ledger implementations
    SCHEDULER = "scheduler" # Task schedulers
    EVENT_BUS = "event_bus" # Event routing
    ROUTER = "router"      # Playbook routing
    GOVERNANCE = "governance" # Varna, Ashrama, Constitutional
    SECURITY = "security"  # Security components
    RUNTIME = "runtime"    # Runtime components
    CORE = "core"          # Core infrastructure
```

## How It Works

### 1. Component Declares Tests (Testable Protocol)

```python
class MyTool(Tool, Testable):
    @property
    def testable_id(self) -> str:
        return f"tool::{self.name}"

    @property
    def testable_type(self) -> TestableType:
        return TestableType.TOOL

    def get_test_cases(self) -> List[TestCase]:
        return [
            TestCase(
                name="test_execute_basic",
                test_func=self._test_execute_basic,
                description="Tool executes basic operation",
                tags=["fast", "basic"],
            ),
        ]

    def _test_execute_basic(self, kernel, comp) -> bool:
        result = self.execute({"param": "value"})
        return result.success
```

### 2. Legacy Components Use Adapters

```python
# Wrap existing agent without modifying its code
adapter = AgentTestableAdapter(my_agent)
test_cases = adapter.get_test_cases()  # Auto-generated tests!
```

### 3. Registry Auto-Discovers Everything

```python
registry = TestableRegistry()
counts = registry.discover_from_kernel(kernel)
# Returns: {"agents": 34, "plugins": 7, "tools": 70, ...}

all_tests = registry.get_all_test_cases()
# Returns: 300+ TestCase objects
```

### 4. Plugin Runs Tests

```python
# Via kernel plugin
plugin = TestOrchestrationPlugin()
results = plugin.run_all_tests()  # <2ms for 300+ tests!

# Or filter by type
agent_results = plugin.run_tests_by_type(TestableType.AGENT)

# Or by tag
security_results = plugin.run_tests_by_tag("security")
```

### 5. TestGuardian Protects Test Integrity

```python
# Before running tests
validation = plugin.validate_tests_before_run()
if validation["mutated"] > 0:
    # AI tried to modify tests - BLOCKED!
    logger.error("TEST MUTATION DETECTED")

# Check if test can be modified
can_modify, reason = plugin.can_modify_test("tests/test_foo.py", modifier="ai")
# Returns: (False, "AI modification blocked by policy")
```

## Test Results Flow

```
Component.get_test_cases()
         ↓
TestableRegistry.discover_from_kernel()
         ↓
TestOrchestrationPlugin.run_all_tests()
         ↓
    ┌────────────────┐
    │  TestResult    │
    │  ├─ test_id    │
    │  ├─ passed     │
    │  ├─ duration   │
    │  └─ error      │
    └────────────────┘
         ↓
Kernel.ledger.record_event("TEST_RESULT", ...)
         ↓
    IMMUTABLE RECORD
```

## MINIATURWUNDERLAND - Standardized Test Fixtures (IMPLEMENTED)

**Location:** `vibe_core/plugins/test_orchestration/fixtures.py`

All tests MUST use these fixtures instead of defining custom mock classes.

### TestAgents - Standardized Agent Fixtures

```python
from vibe_core.plugins.test_orchestration import TestAgents

# Agent WITHOUT oath (governance gate MUST reject)
bad = TestAgents.without_oath("bad-agent")
# has oath_sworn: False

# Agent with oath_sworn = False (governance gate MUST reject)
false = TestAgents.with_false_oath("false-agent")
# oath_sworn = False, oath_event = None

# Agent with INVALID signature (crypto verification MUST fail)
invalid = TestAgents.with_invalid_oath("invalid-agent")
# oath_sworn = True, but signature is fake

# Fully COMPLIANT agent (governance gate MUST accept)
good = TestAgents.compliant("good-agent")
# oath_sworn = True, valid oath_event

# Agent with specific capabilities
cap = TestAgents.with_capabilities("cap-agent", ["read", "write"])
```

### TestPlugins - Standardized Plugin Fixtures

```python
from vibe_core.plugins.test_orchestration import TestPlugins

# Plugin that does nothing (default returns)
noop = TestPlugins.noop()

# Plugin that ALLOWS all operations
allow = TestPlugins.allow_all()

# Plugin that DENIES all operations
deny = TestPlugins.deny_all()

# Plugin that RECORDS all hook calls
recorder = TestPlugins.recording()
# Later: recorder.get_calls("on_agent_registered")
```

### TestKernel - Standardized Kernel Fixtures

```python
from vibe_core.plugins.test_orchestration import TestKernel

# Minimal kernel - NO plugins (isolated tests)
kernel = TestKernel.minimal()

# Kernel with specific plugins
kernel = TestKernel.with_plugins([my_plugin])

# Kernel that allows everything (no governance)
kernel = TestKernel.permissive()

# Kernel with full governance stack
kernel = TestKernel.with_governance()

# Kernel with recorder for assertions
kernel, recorder = TestKernel.with_recording()
```

### TestTasks - Standardized Task Fixtures

```python
from vibe_core.plugins.test_orchestration import TestTasks

# Simple task
task = TestTasks.simple("herald")

# Task with payload
task = TestTasks.with_payload("oracle", {"query": "test"})

# Batch of tasks (load testing)
tasks = TestTasks.batch("agent", count=100)
```

### TestContext - Full Test Isolation

```python
from vibe_core.plugins.test_orchestration import TestContext

# Context manager for complete isolation
with TestContext() as ctx:
    # Register compliant agent
    ctx.register_compliant_agent("my-agent")
    ctx.kernel.boot()

    # Assert hook was called
    assert len(ctx.recorder.get_calls("on_agent_registered")) == 1

# Auto-cleanup on context exit
```

## Files

| File | Purpose |
|------|---------|
| `vibe_core/protocols/testable.py` | Testable protocol + adapters |
| `vibe_core/protocols/testable_registry.py` | Auto-discovery registry |
| `vibe_core/plugins/test_orchestration/plugin_main.py` | Test runner plugin |
| `vibe_core/plugins/test_orchestration/test_guardian.py` | Test mutation protection |
| `vibe_core/plugins/test_orchestration/fixtures.py` | **MINIATURWUNDERLAND** - Standardized test fixtures |

## Performance

- **300+ tests** auto-generated from component adapters
- **<2ms** total execution time
- **Zero manual test writing** for basic sanity checks
- Tests run at kernel boot (optional) or on-demand

## Security Properties

1. **Tests are immutable contracts** - recorded hash at "birth"
2. **AI cannot modify tests** - TestGuardian blocks modifications
3. **All results recorded to ledger** - immutable audit trail
4. **Human approval required** for test changes (configurable)

## Conclusion

This architecture is **SOUND** and **production-ready**. The key insight is that tests become first-class citizens of the system, traveling with their components and protected from manipulation. The Miniaturwunderland pattern ensures consistent test infrastructure across all components.
