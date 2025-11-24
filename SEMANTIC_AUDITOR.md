# ⚖️ SEMANTIC AUDITOR - The Judge & The Watchdog

## The Problem We Solved

**The "Optional Verification" Disaster:**
- Unit tests only check syntax: "Does the code run without crashing?"
- Nobody checks semantics: "Does the code make SENSE in context?"
- Result: Agents can produce logical nonsense and nobody detects it

**Example:**
```python
# Test passes ✅
test_ledger.py: "Can I write an entry?" → YES

# Reality fails ❌
Semantic Check: "Is this entry authorized?" → NO IDEA
```

---

## Three-Layer Verification System

### LAYER 1: Static Compliance (ComplianceTool)
Traditional checks:
- Agent identity verification
- Documentation synchronization
- Event log resilience

### LAYER 2: Semantic Verification (The JUDGE ⚖️)
**The Invariant Engine**

Checks LOGICAL correctness via predefined rules:
- ✅ BROADCAST must have LICENSE_VALID in same task
- ✅ CREDIT_TRANSFER must have PROPOSAL_PASSED before
- ✅ No orphaned events without proper context
- ✅ Events must be in chronological order per task
- ✅ No duplicate events allowed
- ✅ PROPOSAL_VOTED_YES must follow PROPOSAL_CREATED

**These are LAWS, not suggestions. They never break.**

### LAYER 3: Runtime Monitoring (The WATCHDOG 👁️)
**Continuous Verification Daemon**

Runs in parallel with kernel:
- Monitors ledger stream for new events
- Applies invariant checks continuously
- Records VIOLATION events on failure
- Can halt system on CRITICAL violations
- Notifies Envoy for emergency response

---

## Architecture

```
┌─────────────────────────────────────────┐
│         VibeKernel (Main Loop)          │
│  ┌──────────────────────────────────┐   │
│  │  Task Execution                  │   │
│  │  - HERALD records events         │   │
│  │  - Agents broadcast/vote/credit  │   │
│  │  - Ledger grows                  │   │
│  └──────────────────────────────────┘   │
│              │                           │
│              v (every N ticks)           │
│  ┌──────────────────────────────────┐   │
│  │  kernel_tick() → Watchdog        │   │
│  │  Check for violations            │   │
│  │  Halt if CRITICAL found          │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
         ▲                      ▼
         │           ┌─────────────────┐
         └───────────│ Kernel Ledger   │
         Reads       │ (audit trail)   │
                     └─────────────────┘
```

---

## Core Invariants

### INVARIANT 1: BROADCAST_LICENSE_REQUIREMENT

**Rule:** Every BROADCAST event must be preceded by LICENSE_VALID in the same task context.

```
Valid Sequence:
  LICENSE_CHECK (task_1) →
  LICENSE_VALID (task_1) →
  BROADCAST (task_1)     ✅

Invalid Sequence:
  BROADCAST (task_1)     ❌ No license!
```

**Severity:** CRITICAL

### INVARIANT 2: CREDIT_TRANSFER_PROPOSAL_REQUIREMENT

**Rule:** Every CREDIT_TRANSFER must be preceded by PROPOSAL_PASSED in same task.

```
Valid:
  PROPOSAL_CREATED (proposal_1) →
  PROPOSAL_VOTED_YES (proposal_1) →
  PROPOSAL_PASSED (proposal_1) →
  CREDIT_TRANSFER (proposal_1)    ✅

Invalid:
  CREDIT_TRANSFER                 ❌ No proposal!
```

**Severity:** CRITICAL

### INVARIANT 3: NO_ORPHANED_EVENTS

**Rule:** Every event must have task_id, agent_id, event_type, timestamp.

```
Valid:
{
  "event_type": "BROADCAST",
  "task_id": "task_1",
  "agent_id": "herald",
  "timestamp": "2025-11-24T15:00:00Z"
}  ✅

Invalid:
{
  "event_type": "BROADCAST",
  // Missing task_id!
}  ❌
```

**Severity:** HIGH

### INVARIANT 4: EVENT_SEQUENCE_INTEGRITY

**Rule:** Events within a task must be in chronological order.

```
Valid (task_1):
  Event A: 2025-11-24T15:00:00Z →
  Event B: 2025-11-24T15:01:00Z ✅

Invalid (task_1):
  Event A: 2025-11-24T15:01:00Z →
  Event B: 2025-11-24T15:00:00Z ❌ Out of order!
```

**Severity:** HIGH

### INVARIANT 5: NO_DUPLICATE_EVENTS

**Rule:** No two events with same (task_id + event_type + timestamp).

```
Valid:
  Event(task_1, BROADCAST, 15:00) →
  Event(task_1, BROADCAST, 15:01) ✅

Invalid:
  Event(task_1, BROADCAST, 15:00) →
  Event(task_1, BROADCAST, 15:00) ❌ Replay attack!
```

**Severity:** CRITICAL

### INVARIANT 6: PROPOSAL_WORKFLOW_INTEGRITY

**Rule:** PROPOSAL_VOTED_YES must follow PROPOSAL_CREATED for same proposal.

```
Valid:
  PROPOSAL_CREATED(p1) →
  PROPOSAL_VOTED_YES(p1) ✅

Invalid:
  PROPOSAL_VOTED_YES(p1) ❌ No creation event!
```

**Severity:** HIGH

---

## Usage

### 1. Standalone Verification (One-Time Check)

```python
from auditor.cartridge_main import AuditorCartridge
from pathlib import Path

auditor = AuditorCartridge(Path("."))

# Run semantic verification
result = auditor.run_semantic_verification()
print(result)
# Output:
# {
#   "status": "completed",
#   "passed": True,
#   "violations": 0,
#   "events_checked": 150
# }
```

### 2. Runtime Monitoring (Continuous)

```python
# Start watchdog daemon
auditor.start_watchdog()

# In kernel loop (runs every N ticks):
check_result = auditor.run_watchdog_check()

if check_result["halt_requested"]:
    logger.error("CRITICAL VIOLATION - HALTING SYSTEM")
    kernel.halt()
```

### 3. Direct Judge Access

```python
from auditor.tools.invariant_tool import get_judge

judge = get_judge()

# Verify events
events = [
    {"event_type": "BROADCAST", "task_id": "t1", ...},
    # ... more events
]

report = judge.verify_ledger(events)

if not report.passed:
    for violation in report.violations:
        print(f"VIOLATION: {violation.invariant_name}")
        print(f"  Severity: {violation.severity}")
        print(f"  Message: {violation.message}")
```

### 4. Direct Watchdog Access

```python
from auditor.tools.watchdog_tool import Watchdog, WatchdogConfig
from pathlib import Path

config = WatchdogConfig(
    ledger_path=Path("data/ledger/kernel.jsonl"),
    halt_on_critical=True
)

watchdog = Watchdog(config)

# Single check
result = watchdog.check_invariants()
print(f"Violations: {len(result['violations'])}")
```

---

## Kernel Integration (VibeOS)

### Early Boot (kernel_impl.py)

```python
class VibeKernel:
    def __init__(self):
        # ... other init ...
        
        # Load AUDITOR cartridge
        self.auditor = self.load_cartridge("auditor")
        
        # Start watchdog daemon
        self.auditor.start_watchdog()
    
    def kernel_loop(self):
        """Main kernel loop"""
        while self.running:
            task = self.scheduler.next_task()
            
            if task:
                # Execute task
                self.execute_task(task)
                self.task_count += 1
                
                # Every N tasks, watchdog checks
                if self.task_count % 10 == 0:
                    halt_result = self.auditor.watchdog_integration.kernel_tick(
                        self.task_count
                    )
                    
                    if halt_result["should_halt"]:
                        self.halt_critical_violation(halt_result)
```

### Violation Recording

When a violation is detected:

```
Kernel Ledger:
  ... normal events ...
  EVENT: VIOLATION
  {
    "event_type": "VIOLATION",
    "timestamp": "2025-11-24T15:05:32Z",
    "agent_id": "watchdog",
    "violation_type": "BROADCAST_LICENSE_REQUIREMENT",
    "severity": "CRITICAL",
    "message": "BROADCAST event at index 42 missing LICENSE_VALID in task task_1"
  }
  ... recovery or halt ...
```

---

## Severity Levels & Actions

| Severity | Meaning | Action |
|----------|---------|--------|
| CRITICAL | System integrity broken | Halt immediately |
| HIGH | Operations compromised | Pause & alert Envoy |
| MEDIUM | Warning | Log & continue |
| LOW | Advisory | Log only |

---

## Testing

### Run All Semantic Auditor Tests

```bash
pytest tests/test_semantic_auditor.py -v
```

### Test Specific Invariant

```bash
pytest tests/test_semantic_auditor.py::TestInvariantEngine::test_broadcast_license_requirement -v
```

### Test Watchdog

```bash
pytest tests/test_semantic_auditor.py::TestWatchdog -v
```

---

## Adding New Invariants

```python
from auditor.tools.invariant_tool import get_judge, InvariantRule, InvariantSeverity

judge = get_judge()

# Define check function
def check_my_rule(events, context):
    """Check if events satisfy my rule"""
    for i, event in enumerate(events):
        if event.get("some_field") is None:
            return (False, f"Event {i} missing some_field")
    return (True, None)

# Register rule
rule = InvariantRule(
    name="MY_CUSTOM_RULE",
    description="My custom invariant",
    severity=InvariantSeverity.HIGH,
    check_function=check_my_rule
)

judge.register_rule(rule)
```

---

## Performance Considerations

- **Verification Frequency:** Every 10 tasks (configurable)
- **Ledger Reading:** Incremental (only new events since last check)
- **Memory:** Minimal (streams events, doesn't load entire ledger)
- **CPU:** ~1-2ms per check on 1000-event ledger

---

## Error Recovery

If a VIOLATION is recorded:

1. **CRITICAL Violation:**
   - System halts immediately
   - No further tasks executed
   - Violation recorded in ledger
   - Manual intervention required

2. **HIGH Violation:**
   - Tasks pause
   - Envoy notified
   - Manual review of violation
   - Can resume after fix

3. **MEDIUM/LOW Violation:**
   - Logged to ledger
   - System continues
   - Can be reviewed during maintenance

---

## Files

| File | Purpose |
|------|---------|
| `auditor/tools/invariant_tool.py` | The JUDGE - Invariant Engine |
| `auditor/tools/watchdog_tool.py` | The WATCHDOG - Runtime Monitor |
| `auditor/cartridge_main.py` | AUDITOR Cartridge (updated v2.0) |
| `tests/test_semantic_auditor.py` | Comprehensive test suite |

---

## The Philosophy

This is the step from **"Software that runs"** to **"Software that understands itself."**

- Unit tests prove syntax works.
- Semantic auditor proves MEANING is correct.

**Verification is no longer optional. It's system-immanent.**

This is how you build a system with an immune system. 🏰⚖️👁️

