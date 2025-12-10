# OPUS-022: Kernel Scaling Architecture

> **Status**: VERIFIED (Pending Tests)
> **Date**: 2025-12-10
> **Author**: Claude Opus
> **Depends On**: 001-KERNEL-EXTRACTION, 010-VERIFICATION-PROTOCOL, 021-TEST-ARCHITECTURE

<!-- @HARNESS
files:
  - path: vibe_core/kernel_impl.py
    required: true
  - path: vibe_core/scheduling/in_memory.py
    required: true
  - path: vibe_core/process_manager.py
    required: true
  - path: vibe_core/ledger.py
    required: true
  - path: vibe_core/playbook/operations/kernel_spawn.py
    required: true
  - path: vibe_core/boot_orchestrator.py
    required: true
  - path: vibe_core/gateway/api.py
    required: true
tests:
  - tests/unit/test_ephemeral_cities.py
  - tests/integration/test_kernel_scaling.py
  - tests/hardening/test_kernel_stress.py
wiring:
  - pattern: "def spawn_child_kernel"
    in: vibe_core/kernel_impl.py
  - pattern: "async def spawn_city"
    in: vibe_core/playbook/operations/kernel_spawn.py
  - pattern: "def next_task"
    in: vibe_core/scheduling/in_memory.py
  - pattern: "def tick"
    in: vibe_core/kernel_impl.py
  - pattern: "class NetworkGateway"
    in: vibe_core/gateway/api.py
absent:
  - pattern: "TODO.*scaling"
    in: vibe_core/kernel_impl.py
  - pattern: "TODO.*ephemeral"
    in: vibe_core/playbook/operations/kernel_spawn.py
-->

---

## Executive Summary

Das Kernel Scaling System ist **architektonisch solide** aber **ungetestet in kritischen Bereichen**.

**TL;DR:**
- Ephemeral Cities = PRODUCTION READY, ZERO TESTS
- Priority Scheduler = FUNKTIONIERT KORREKT
- tick() = SYNCHRON, 1 TASK/TICK
- Federation API = EXISTIERT, TASK ROUTING FEHLT

---

## 1. Verified Architecture

### 1.1 Kernel Core (`kernel_impl.py`)

**File**: `vibe_core/kernel_impl.py` (1490 lines)
**Class**: `RealVibeKernel`

```python
# kernel_impl.py:130
class RealVibeKernel(VibeKernel):
    def __init__(self, ledger_path, config, parent, load_plugins):
        self._scheduler = InMemoryScheduler()      # Line 181
        self._ledger = SQLiteLedger(ledger_path)   # Line 188
        self.process_manager = ProcessManager()     # Line 201
        self.resource_manager = ResourceManager()   # Line 204
        self.gateway = NetworkGateway(self.prakriti)  # Line 337
```

| Component | Location | Status |
|-----------|----------|--------|
| Scheduler | `kernel_impl.py:181` | VERIFIED |
| Ledger | `kernel_impl.py:188` | VERIFIED |
| ProcessManager | `kernel_impl.py:201` | VERIFIED |
| ResourceManager | `kernel_impl.py:204` | VERIFIED |
| Gateway | `kernel_impl.py:337` | VERIFIED |

---

### 1.2 Tick Loop (`kernel_impl.py:942-1039`)

**VERIFIED**: Synchronous, processes ONE task per tick.

```python
# kernel_impl.py:942
def tick(self) -> None:
    """Tick the kernel - process one task from the scheduler"""
    task = self._scheduler.next_task()  # Line 956
    if not task:
        return

    # IPC or in-process execution (Lines 988-1020)
    if has_process:
        self.process_manager.send_task(task.agent_id, task)  # Line 992
    else:
        result = agent.process(task)  # Line 1006
```

**Called From**: `boot_orchestrator.py:447`

```python
# boot_orchestrator.py:447
while self._running:
    self.kernel.tick()  # Synchronous call in async loop
    intent = await self.operator_adapter.get_decision(context)
```

**Implications**:
- Max 1 task dispatched per loop iteration
- Async context exists but tick() is sync
- No batch processing

---

### 1.3 Priority Scheduler (`scheduling/in_memory.py`)

**VERIFIED**: Priority handling WORKS CORRECTLY.

```python
# in_memory.py:36-41
self.queues: Dict[int, deque] = {
    0: deque(),  # Critical
    1: deque(),  # High
    2: deque(),  # Medium
    3: deque(),  # Low
}

# in_memory.py:78-86
def next_task(self) -> Optional[Task]:
    """Pop next task from highest priority queue."""
    for priority in sorted(self.queues.keys()):  # P0 first!
        if self.queues[priority]:
            task = self.queues[priority].popleft()
            return task
    return None
```

| Feature | Status | Location |
|---------|--------|----------|
| Priority Queues (P0-P3) | VERIFIED | `in_memory.py:36-41` |
| FIFO per Priority | VERIFIED | `in_memory.py:83` |
| Priority Iteration | VERIFIED | `in_memory.py:81` |
| Idempotency Cache | VERIFIED | `in_memory.py:44-45` |
| Requeue Support | VERIFIED | `in_memory.py:97-105` |

**NOT Implemented**:
- Persistence (in-memory only)
- Distributed scheduling

---

### 1.4 Ephemeral Cities (4D Hypercube)

**VERIFIED**: FULLY IMPLEMENTED, ZERO TESTS.

#### Core Method (`kernel_impl.py:371-419`)

```python
# kernel_impl.py:371
def spawn_child_kernel(
    self,
    config: "PhoenixConfig",
    ledger_path: str = ":memory:",
) -> "RealVibeKernel":
    """
    SPAWN EPHEMERAL CITY (4D Hypercube Operation)
    """
    child = RealVibeKernel(
        ledger_path=ledger_path,
        config=config,
        parent=self,  # Child knows parent
    )
    self._child_kernels.append(child)
    return child
```

#### Full Operation Module (`playbook/operations/kernel_spawn.py`, 479 lines)

```python
# kernel_spawn.py:209
async def spawn_city(
    task: str,
    circuit: Optional[str] = None,
    config_overrides: Optional[Dict[str, Any]] = None,
    config_factory: Optional[Callable] = None,
    parent_kernel: Optional["RealVibeKernel"] = None,
    timeout_seconds: int = 300,
    artifacts: Optional[List[str]] = None,
    artifacts_destination: Optional[str] = None,
) -> SpawnCityResult:
```

| Feature | Status | Location |
|---------|--------|----------|
| `spawn_child_kernel()` | VERIFIED | `kernel_impl.py:371-419` |
| `spawn_city()` async | VERIFIED | `kernel_spawn.py:209-378` |
| `spawn_city_sync()` | VERIFIED | `kernel_spawn.py:404-426` |
| Airlock (artifact harvest) | VERIFIED | `kernel_spawn.py:91-171` |
| Config Overrides | VERIFIED | `kernel_spawn.py:174-206` |
| `fast_code_config` | VERIFIED | `kernel_spawn.py:430-444` |
| `sandbox_config` | VERIFIED | `kernel_spawn.py:447-461` |
| `research_swarm_config` | VERIFIED | `kernel_spawn.py:464-478` |
| Ledger Hash Proof | VERIFIED | `kernel_impl.py:421-430` |
| Child Merge | VERIFIED | `kernel_impl.py:432-449` |

**CRITICAL GAP**: No tests exist for any of this.

---

### 1.5 Process Isolation (`process_manager.py`)

**VERIFIED**: Real OS process isolation.

```python
# process_manager.py:23
from multiprocessing import Pipe, Process

# process_manager.py:261-268
parent_conn, child_conn = Pipe()
process = Process(
    target=_run_agent_process,
    args=(...),
    name=f"vibe-agent-{agent_id}",
    daemon=True,
)
```

| Feature | Status | Location |
|---------|--------|----------|
| `multiprocessing.Process` | VERIFIED | `process_manager.py:263` |
| IPC via Pipes | VERIFIED | `process_manager.py:261` |
| MAX_MESSAGE_SIZE check | VERIFIED | `process_manager.py:307-309` |
| Health Check | VERIFIED | `process_manager.py:340+` |
| Process Restart | VERIFIED | `process_manager.py:386+` |

---

### 1.6 SQLite Ledger (`ledger.py`)

**VERIFIED**: Single connection, no pooling.

```python
# ledger.py:129
class SQLiteLedger(VibeLedger):
    def __init__(self, db_path: str = "data/vibe_ledger.db"):
        self.db_path = db_path
        self.connection = None  # Single connection
        self._write_lock = threading.Lock()  # Thread safety

# ledger.py:147
self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
```

| Feature | Status | Location |
|---------|--------|----------|
| Single Connection | VERIFIED | `ledger.py:135` |
| No Connection Pool | VERIFIED | (no pool code exists) |
| Write Lock | VERIFIED | `ledger.py:136` |
| WAL Mode | NOT VERIFIED | (check pragma) |

---

### 1.7 Federation API (`gateway/api.py`)

**VERIFIED**: Endpoints exist, task routing NOT implemented.

```python
# gateway/api.py:94-99
def _setup_federation_routes(self):
    self.app.router.add_get("/api/v1/federation/peers", self.handle_list_peers)
    self.app.router.add_post("/api/v1/federation/peers", self.handle_add_peer)
    self.app.router.add_delete("/api/v1/federation/peers/{peer_id}", self.handle_remove_peer)
    self.app.router.add_post("/api/v1/federation/forward/{peer_id}", self.handle_forward)
```

| Endpoint | Status | Purpose |
|----------|--------|---------|
| `GET /federation/peers` | VERIFIED | List peers |
| `POST /federation/peers` | VERIFIED | Add peer |
| `DELETE /federation/peers/{peer_id}` | VERIFIED | Remove peer |
| `POST /federation/forward/{peer_id}` | VERIFIED | Forward request |

**NOT Implemented**:
- Automatic task routing to peers
- Load balancing across kernels
- Fault tolerance / failover

---

### 1.8 Zone Capacity (`config/cities/agent_city/zones.yaml`)

```yaml
general:     { capacity: 20 }
research:    { capacity: 10 }
engineering: { capacity: 10 }
governance:  { capacity: 5 }
temporary:   { capacity: 50 }
# Total: 95 agents
```

---

## 2. What Is NOT Verified (Honest Gaps)

### 2.1 No Performance Data

| Metric | Status |
|--------|--------|
| Tasks/second throughput | NOT MEASURED |
| SQLite writes/second | NOT MEASURED |
| Agent spawn latency | NOT MEASURED |
| IPC message latency | NOT MEASURED |
| Memory per agent | NOT MEASURED |

**Required**: Profiling with real workloads.

### 2.2 No Scaling Tests

| Test | Status |
|------|--------|
| 10 concurrent agents | NOT TESTED |
| 100 concurrent tasks | NOT TESTED |
| 1000 queued tasks | NOT TESTED |
| Ephemeral city spawn/merge | NOT TESTED |
| Federation task routing | NOT TESTED |

### 2.3 Unknown Bottlenecks

The original analysis SPECULATED about bottlenecks:
- "SQLite contention at 10+ agents" - NOT VERIFIED
- "Tick loop at 12 tasks/minute" - NOT VERIFIED
- "IPC at 5 second timeout" - NOT VERIFIED

**We don't know what actually breaks until we test it.**

---

## 3. Required Tests (P0)

### 3.1 Ephemeral Cities (`tests/unit/test_ephemeral_cities.py`)

**Priority**: P0 - CRITICAL (implemented but untested = risk)

```python
# Required test cases:

def test_spawn_child_kernel_creates_isolated_instance():
    """Child kernel should be isolated from parent."""
    pass

def test_spawn_child_kernel_with_memory_ledger():
    """Ephemeral ledger should work."""
    pass

def test_child_kernel_knows_parent():
    """child._parent should reference parent."""
    pass

def test_merge_child_result_records_proof():
    """Merge should record ledger hash."""
    pass

def test_spawn_city_async_executes_task():
    """spawn_city() should execute and return result."""
    pass

def test_spawn_city_with_config_overrides():
    """Config overrides should apply to child."""
    pass

def test_spawn_city_timeout_handling():
    """Timeout should return error, not hang."""
    pass

def test_airlock_harvests_artifacts():
    """Artifacts should be copied before child death."""
    pass

def test_fast_code_config_disables_governance():
    """fast_code_config should set voting_threshold=0."""
    pass

def test_spawn_city_sync_wrapper():
    """Sync wrapper should work from non-async code."""
    pass
```

### 3.2 Kernel Scaling (`tests/integration/test_kernel_scaling.py`)

**Priority**: P1 - HIGH

```python
# Required test cases:

def test_10_concurrent_agents():
    """Kernel should handle 10 agents without deadlock."""
    pass

def test_priority_scheduler_ordering():
    """P0 tasks should execute before P3 tasks."""
    pass

def test_task_queue_100_items():
    """Queue should handle 100 pending tasks."""
    pass

def test_process_manager_spawn_10_processes():
    """Should spawn 10 agent processes."""
    pass

def test_ipc_large_message_rejection():
    """Messages > MAX_MESSAGE_SIZE should be rejected."""
    pass
```

### 3.3 Stress Tests (`tests/hardening/test_kernel_stress.py`)

**Priority**: P2 - MEDIUM (after unit/integration pass)

```python
# Required test cases:

@pytest.mark.slow
def test_stress_1000_tasks():
    """Queue 1000 tasks, verify all complete."""
    pass

@pytest.mark.slow
def test_stress_50_ephemeral_cities():
    """Spawn 50 ephemeral cities in parallel."""
    pass

@pytest.mark.slow
def test_ledger_1000_writes():
    """Write 1000 ledger entries, measure throughput."""
    pass

@pytest.mark.slow
def test_sustained_load_5_minutes():
    """Run kernel under load for 5 minutes."""
    pass
```

---

## 4. Scaling Paths (After Tests Pass)

### Path 1: Use Ephemeral Cities NOW

**Effort**: 0 (already implemented)
**Prerequisite**: Tests from 3.1 pass

```python
from vibe_core.playbook.operations import spawn_city, fast_code_config

# Parallel execution example
async def execute_parallel_tasks(tasks):
    results = await asyncio.gather(*[
        spawn_city(
            task=t,
            config_factory=fast_code_config,
            timeout_seconds=60,
        )
        for t in tasks
    ])
    return results
```

### Path 2: Async Tick Loop

**Effort**: 2-3 days
**Prerequisite**: Tests from 3.2 pass, profiling shows tick() is bottleneck

```python
# BEFORE (current)
def tick(self) -> None:
    task = self._scheduler.next_task()
    # ... synchronous execution

# AFTER (proposed)
async def tick(self) -> None:
    tasks = self._scheduler.next_tasks(batch_size=10)
    await asyncio.gather(*[self._dispatch_task(t) for t in tasks])
```

### Path 3: Ledger Sharding

**Effort**: 3-4 days
**Prerequisite**: Profiling shows SQLite is bottleneck

```python
# Shard by agent_id
class ShardedLedger:
    def __init__(self, base_path):
        self.shards = {}  # agent_id -> SQLiteLedger

    def record_event(self, event_type, agent_id, details):
        shard = self._get_shard(agent_id)
        shard.record_event(event_type, agent_id, details)
```

### Path 4: Federation Task Routing

**Effort**: 1 week
**Prerequisite**: Tests from 3.2 pass, need multi-kernel deployment

```python
# New file: vibe_core/federation_router.py
class FederationRouter:
    async def route_task(self, task):
        if self.local.resource_manager.has_capacity():
            return self.local.submit_task(task)

        for peer in self.peers:
            response = await self.gateway.forward_task(peer['id'], task)
            if response['accepted']:
                return response['task_id']
```

---

## 5. Profiling Protocol

**Run BEFORE implementing scaling paths.**

```bash
# Profile kernel under load
python -m cProfile -o kernel.prof -c "
from vibe_core.boot_orchestrator import quick_boot
kernel = quick_boot()
kernel.boot()
for i in range(100):
    kernel.tick()
"

# Analyze
python -c "
import pstats
p = pstats.Stats('kernel.prof')
p.sort_stats('cumulative')
p.print_stats(20)
"
```

**Metrics to capture:**
- Time in `tick()`
- Time in `send_task()` (IPC)
- Time in `record_event()` (Ledger)
- Time in `next_task()` (Scheduler)

---

## 6. Decision Matrix

| Scenario | Action | Prerequisite |
|----------|--------|--------------|
| Need parallel execution NOW | Use `spawn_city()` | Tests 3.1 pass |
| tick() is bottleneck | Implement async tick | Profiling data |
| SQLite is bottleneck | Implement sharding | Profiling data |
| Single kernel saturated | Federation routing | Multi-kernel setup |
| Unknown bottleneck | Run profiling first | None |

---

## 7. Sign-Off Checklist

Before any scaling implementation:

- [ ] `tests/unit/test_ephemeral_cities.py` passes
- [ ] `tests/integration/test_kernel_scaling.py` passes
- [ ] Profiling data collected
- [ ] Bottleneck identified with evidence
- [ ] Scaling path chosen based on data

---

## Appendix A: File Reference

| File | Lines | Purpose |
|------|-------|---------|
| `vibe_core/kernel_impl.py` | 1490 | Core kernel |
| `vibe_core/scheduling/in_memory.py` | 106 | Priority scheduler |
| `vibe_core/process_manager.py` | 412 | Agent processes |
| `vibe_core/ledger.py` | 510 | SQLite ledger |
| `vibe_core/playbook/operations/kernel_spawn.py` | 479 | Ephemeral cities |
| `vibe_core/boot_orchestrator.py` | 500+ | Boot + main loop |
| `vibe_core/gateway/api.py` | 184 | Federation API |

---

## Appendix B: Corrections to Original Analysis

The document "VibeOS Verified Scaling Architecture" contained errors:

| Claim | Reality |
|-------|---------|
| "Scheduler ignores priorities" | FALSE - `next_task()` iterates P0→P3 correctly |
| "kernel_impl.py ~1200 lines" | FALSE - actual 1490 lines |
| "Ephemeral cities lines 180-260" | INCOMPLETE - full module is 479 lines |
| "Tasks/minute ~12" | SPECULATION - no profiling data |
| "SQLite writes/sec ~1000" | SPECULATION - no profiling data |

---

**Document Status**: VERIFIED ARCHITECTURE, PENDING TESTS
**Next Action**: Implement tests from Section 3
