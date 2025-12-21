# OPUS-175: Ephemeral Kernels - Deep Architecture Analysis

> "The current spawn_child_kernel() creates a FULL kernel. That's not ephemeral. That's cloning." - Claude

## Executive Summary

This document provides a deep analysis of the current task execution architecture and proposes a lightweight **Ephemeral Kernel** pattern for MANAS-driven task execution. The goal: boot a minimal execution context in ~100ms instead of the current 5+ second full kernel boot.

## The Current Architecture (As-Is)

### 1. TaskManager Architecture (622 LOC)

**Location:** `vibe_core/task_management/task_manager.py`

```
TaskManager
    ├── ValidatorRegistry          # Task validation
    ├── MetricsCollector          # Task metrics
    ├── TaskArchive               # Archive completed
    ├── FileLock                  # Concurrency control
    ├── ExportEngine              # JSON/CSV/MD export
    ├── NextTaskGenerator         # Priority queue
    ├── BatchOperations           # Bulk operations
    └── SQLiteStore (VIMANA)      # Immortal persistence
```

**Key Insight:** TaskManager is a **DATA STORE**, not an executor. It manages `ManagedTask` objects (title, description, assignee, subtasks) but has **ZERO execution capability**.

**Data Model (ManagedTask):**
```python
@dataclass
class Task:
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: int
    assignee: Optional[str]  # Agent ID
    tags: List[str]
    subtasks: List[str]
    topology_layer: Optional[str]  # Bhu-Mandala routing
    varna: Optional[str]           # Vedic class
    routing_priority: Optional[int] # MilkOcean priority
    roadmap_id: Optional[str]
```

**Persistence:** VIMANA Dual-Core (JSON cache + SQLite immortality)

---

### 2. ProcessManager Architecture (413 LOC)

**Location:** `vibe_core/process_manager.py`

```
ProcessManager
    ├── spawn_agent()             # Fork new process
    ├── send_task()               # IPC dispatch + ACK
    ├── check_health()            # Narasimha watchdog
    ├── _handle_crash()           # Restart logic
    └── get_pending_messages()    # Collect results
```

**Spawn Mechanism:**
```python
def spawn_agent(self, agent_id, cartridge_path, cartridge_class_name, config):
    parent_conn, child_conn = Pipe()

    process = Process(
        target=_run_agent_process,
        args=(agent_id, cartridge_path, cartridge_class_name, child_conn, config),
        daemon=True,  # Dies with kernel
    )
    process.start()
```

**IPC Protocol:**
```
KERNEL                          AGENT PROCESS
   │                                 │
   ├──► {type: "TASK", payload}     │
   │                                 │
   │    ◄── {type: "TASK_ACK"}      │
   │                                 │
   │    ◄── {type: "TASK_RESULT"}   │
   │                                 │
   │    ◄── {type: "CRASH", error}  │
```

**Key Insight:** ProcessManager spawns **CARTRIDGE AGENTS** (herald, civic, analyst), not task executors. Each agent is a long-running process that receives tasks via Pipe.

---

### 3. UnifiedExecutor Architecture (483 LOC)

**Location:** `vibe_core/runtime/unified_execution.py`

```
UnifiedExecutor
    ├── _circuit_executor          # DeterministicExecutor
    ├── execute()                  # Main dispatch
    ├── _execute_circuit()         # YAML circuits
    ├── _execute_playbook()        # Legacy playbooks
    └── _execute_fallback()        # Unknown requests
```

**Execution Flow:**
```
User Input
    ↓
UnifiedRouter.route()
    ↓ (LayeredRouter - 3 layers)
ExecutionRequest
    ↓
UnifiedExecutor.execute()
    ↓
DeterministicExecutor
    ↓
Circuit YAML phases
```

**Key Insight:** UnifiedExecutor runs **IN THE KERNEL PROCESS**. It doesn't spawn anything. It's synchronous circuit execution.

---

### 4. RealVibeKernel.spawn_child_kernel() (1848 LOC total)

**Location:** `vibe_core/kernel_impl.py:485-533`

```python
def spawn_child_kernel(self, config, ledger_path=":memory:"):
    """🌀 SPAWN EPHEMERAL CITY (4D Hypercube Operation)"""

    child = RealVibeKernel(
        ledger_path=ledger_path,
        config=config,
        parent=self,
    )

    self._child_kernels.append(child)
    return child
```

**What spawn_child_kernel() actually does:**
1. Creates a FULL `RealVibeKernel` instance
2. Initializes Prakriti (state engine)
3. Initializes LineageChain (blockchain)
4. Loads ALL plugins (discovers + boots)
5. Creates CapabilityRegistry
6. Creates I/O Service
7. Creates ProcessManager
8. Creates ResourceManager
9. Creates NetworkGateway
10. Seals Vajra Armor

**Boot Time:** 3-8 seconds (depending on plugin count)

**PROBLEM:** This is NOT ephemeral. This is a FULL CLONE.

---

## The Gaps (Critical)

### Gap 1: TaskManager ↔ ProcessManager Disconnect

```
TaskManager                    ProcessManager
(ManagedTask)                  (DispatchTask)
     │                              │
     │   ⚠️ NO CONNECTION ⚠️        │
     │                              │
     ▼                              ▼
add_task()                    spawn_agent()
get_next_task()               send_task()
update_task()                 check_health()
```

**Two completely separate systems:**
- `ManagedTask` = Project card (title, description, subtasks, assignee)
- `DispatchTask` = Message envelope (agent_id, payload)

**There is NO code that converts ManagedTask → DispatchTask**

---

### Gap 2: MANAS ↔ TaskManager Integration

**Verified via grep:** ZERO integration exists.

```bash
grep -rn "MANAS\|Intent\|think\|cognitive" vibe_core/task_management/
# Empty - no results

grep -rn "TaskManager\|task_manager" vibe_core/plugins/opus_assistant/
# Empty - no results
```

**MANAS has:**
- `SynapticMemory` (learned patterns)
- `IntentBuffer` (pending intents)
- `CognitiveKernel` (consciousness levels)
- `tick()` biorhythm

**TaskManager has:**
- `ManagedTask` (user tasks)
- `Roadmap` (task grouping)
- `ActiveMission` (current focus)

**They don't talk to each other.**

---

### Gap 3: Ephemeral Kernels Are Heavyweight

Current `spawn_child_kernel()` creates:
- Full plugin ecosystem (20+ plugins)
- Full Prakriti state engine
- Full LineageChain blockchain
- Full capability registry
- Full I/O service

**This defeats the purpose of "ephemeral."**

---

## Proposed Architecture (To-Be)

### TaskKernel: The Lightweight Alternative

```python
class TaskKernel:
    """
    Lightweight execution kernel for single-task execution.

    Boot time: ~100ms (vs 5+ seconds for RealVibeKernel)
    Memory: ~50MB (vs ~500MB for full kernel)
    Plugins: ZERO (no plugin loading)
    State: In-memory only (no Prakriti)
    Lineage: Optional (disabled by default)
    """

    def __init__(self, task: ManagedTask, parent: RealVibeKernel):
        self.task = task
        self.parent = parent

        # Minimal state
        self._ledger = InMemoryLedger()
        self._result = None

        # Borrowed from parent (no duplication)
        self._tool_registry = parent.tool_registry  # Shared, read-only
        self._config = parent.config               # Shared, read-only

    async def execute(self) -> TaskResult:
        """Execute the task and return result."""
        # 1. Resolve executor for task type
        executor = self._resolve_executor(self.task)

        # 2. Execute with timeout
        self._result = await asyncio.wait_for(
            executor.execute(self.task),
            timeout=self.task.timeout or 300
        )

        # 3. Return result for parent to fold
        return self._result
```

### MANAS → TaskKernel Integration

```
MANAS Biorhythm
    ↓ (Turiya state: should_think=True)
    ↓
MANAS.generate_intent()
    ↓
IntentBuffer.add(intent)
    ↓
MANAS.prioritize()
    ↓
TaskManager.add_task(
    title=intent.action,
    description=intent.context,
    assignee=intent.target_agent,
)
    ↓
TaskKernel.spawn(task)
    ↓
TaskKernel.execute()
    ↓
Result → Parent Kernel
```

### ProcessManager Integration for TaskKernel

**Option A: In-Process Execution (Default)**
```python
# For fast, lightweight tasks
task_kernel = TaskKernel(task, parent_kernel)
result = await task_kernel.execute()
```

**Option B: Subprocess Isolation (Heavy Tasks)**
```python
# For tasks that need process isolation
process = Process(
    target=_run_task_kernel,
    args=(task, parent_kernel.get_serializable_context()),
    daemon=True,
)
process.start()
```

### IPC Mechanism for TaskKernel

```
Parent Kernel                 TaskKernel (subprocess)
     │                              │
     ├──► spawn(task, context)      │
     │                              │
     │    ◄── {status: "running"}   │
     │                              │
     │    ◄── {progress: 50%}       │
     │                              │
     │    ◄── {result: {...}}       │
     │                              │
     ▼                              ▼
fold_result(result)           Process exits
```

---

## Implementation Phases

### Phase 1: TaskKernel Core
- [ ] Create `vibe_core/task_kernel.py`
- [ ] Implement minimal boot (no plugins)
- [ ] Implement `execute()` with timeout
- [ ] Implement result folding to parent

### Phase 2: MANAS Integration
- [ ] Add `TaskManager` reference to MANAS
- [ ] Implement `Intent → ManagedTask` conversion
- [ ] Wire `Turiya` state to task spawning
- [ ] Add synaptic reinforcement on task completion

### Phase 3: ProcessManager Integration
- [ ] Add `spawn_task_kernel()` to ProcessManager
- [ ] Implement lightweight IPC for TaskKernel
- [ ] Add progress reporting
- [ ] Add timeout handling

### Phase 4: Observability
- [ ] Wire TaskKernel to Observer Loop
- [ ] Add consciousness panel for active TaskKernels
- [ ] Add metrics collection

---

## Questions for Gemini

1. **Should TaskKernel share parent's ToolRegistry or have its own?**
   - Sharing = faster boot, less memory
   - Separate = better isolation

2. **How should MANAS prioritize Intents vs existing TaskManager tasks?**
   - MANAS-generated intents have cognitive context
   - User-added tasks have explicit priority

3. **Should TaskKernel results update SynapticMemory automatically?**
   - Success → reinforce pattern
   - Failure → weaken pattern

4. **What's the right granularity for TaskKernel?**
   - One kernel per task?
   - One kernel per batch of related tasks?
   - Pool of reusable TaskKernels?

---

## Files Analyzed

| File | LOC | Purpose |
|------|-----|---------|
| `vibe_core/task_management/task_manager.py` | 622 | Task data store |
| `vibe_core/task_management/models.py` | 153 | ManagedTask, Roadmap, Mission |
| `vibe_core/scheduling/task.py` | 78 | DispatchTask (kernel IPC) |
| `vibe_core/process_manager.py` | 413 | Agent process spawning |
| `vibe_core/runtime/unified_execution.py` | 483 | Circuit/playbook execution |
| `vibe_core/kernel_impl.py` | 1848 | RealVibeKernel (full kernel) |

**Total analyzed:** 3,597 LOC

---

## Conclusion

The current architecture has three parallel systems that don't integrate:

1. **TaskManager** - Stores tasks, doesn't execute them
2. **ProcessManager** - Executes agents, not tasks
3. **MANAS** - Generates intents, doesn't spawn tasks

The proposed **TaskKernel** pattern bridges these gaps by:
- Converting MANAS intents to TaskManager tasks
- Spawning lightweight execution contexts (not full kernels)
- Folding results back to the parent kernel
- Updating synaptic patterns based on outcomes

This completes the Mind-Body feedback loop from OPUS-174.

---

*"A brain doesn't spawn a new brain to think each thought. It spawns a new pattern."* - Gemini
