# ⚖️ SEMANTIC AUDITOR - QUICK REFERENCE

## One-Liner
**The Judge verifies semantic correctness. The Watchdog monitors continuously. System halts on violations.**

---

## 3 Layers of Verification

| Layer | Component | What | When |
|-------|-----------|------|------|
| 1 | ComplianceTool | Agent compliance | Build time |
| 2 | Judge ⚖️ | Semantic rules | Build time + runtime |
| 3 | Watchdog 👁️ | Continuous monitoring | Every N kernel ticks |

---

## 6 Core Invariants

1. **BROADCAST_LICENSE_REQUIREMENT** - CRITICAL
   - Rule: Every BROADCAST needs LICENSE_VALID
   - Example: No license → NO broadcast

2. **CREDIT_TRANSFER_PROPOSAL_REQUIREMENT** - CRITICAL
   - Rule: Every CREDIT_TRANSFER needs PROPOSAL_PASSED
   - Example: No proposal → NO transfer

3. **NO_ORPHANED_EVENTS** - HIGH
   - Rule: Every event needs task_id, agent_id, type, timestamp
   - Example: Missing field → Violation

4. **EVENT_SEQUENCE_INTEGRITY** - HIGH
   - Rule: Events in task must be chronological
   - Example: Event out of order → Violation

5. **NO_DUPLICATE_EVENTS** - CRITICAL
   - Rule: No duplicate (task_id, type, timestamp)
   - Example: Replay attack → System halts

6. **PROPOSAL_WORKFLOW_INTEGRITY** - HIGH
   - Rule: PROPOSAL_VOTED_YES needs PROPOSAL_CREATED
   - Example: Vote without proposal → Violation

---

## Usage Patterns

### Pattern 1: One-Time Verification
```python
from auditor.cartridge_main import AuditorCartridge

auditor = AuditorCartridge()
result = auditor.run_semantic_verification()

if not result["passed"]:
    print(f"Violations: {result['violations']}")
```

### Pattern 2: Start Watchdog (Kernel)
```python
# In kernel __init__:
self.auditor = AuditorCartridge()
self.auditor.start_watchdog()

# In kernel_loop:
if self.task_count % 10 == 0:
    halt = self.auditor.watchdog_integration.kernel_tick(self.task_count)
    if halt["should_halt"]:
        self.halt()
```

### Pattern 3: Get Judge Directly
```python
from auditor.tools.invariant_tool import get_judge

judge = get_judge()
report = judge.verify_ledger(events)

if not report.passed:
    for v in report.violations:
        print(f"{v.invariant_name}: {v.message}")
```

### Pattern 4: Register Callbacks
```python
def on_violation(event):
    logger.warning(f"Violation: {event.violation_type}")

auditor.watchdog_integration.register_violation_callback(on_violation)
```

---

## Files to Know

| File | Purpose | Key Classes |
|------|---------|-------------|
| `auditor/tools/invariant_tool.py` | The JUDGE | InvariantEngine, InvariantRule, VerificationReport |
| `auditor/tools/watchdog_tool.py` | The WATCHDOG | Watchdog, WatchdogConfig, ViolationEvent |
| `auditor/cartridge_main.py` | AUDITOR cartridge | AuditorCartridge (v2.0) |

---

## Event Format

### Required Fields (Invariant 3: NO_ORPHANED_EVENTS)
```json
{
  "event_type": "BROADCAST",        // ← Required
  "task_id": "task_1",              // ← Required
  "agent_id": "herald",             // ← Required
  "timestamp": "2025-11-24T15:00:00Z" // ← Required (ISO 8601)
}
```

### Timestamps Must Be
- ISO 8601 format: `2025-11-24T15:00:00Z`
- In chronological order (Invariant 4)
- No duplicates in same task (Invariant 5)

---

## Violation Severities

| Severity | Action | Recovery |
|----------|--------|----------|
| CRITICAL | Halt immediately | Manual intervention |
| HIGH | Log & pause | Manual review |
| MEDIUM | Log only | Can continue |
| LOW | Log only | Advisory |

---

## Integration (Minimal)

3 lines to add to existing kernel:

```python
# Line 1: In __init__
self.auditor = AuditorCartridge()
self.auditor.start_watchdog()

# Line 2-3: In kernel_loop
if self.task_count % 10 == 0:
    if self.auditor.watchdog_integration.kernel_tick(self.task_count)["should_halt"]:
        self.halt()
```

---

## Performance

- **Check time:** ~10-20ms per 1000 events
- **Memory:** ~0.5MB
- **CPU:** <1% overhead
- **Check frequency:** Every 10 tasks (configurable)

---

## Testing

### Run All Tests
```bash
pytest tests/test_semantic_auditor.py -v
```

### Run Demo
```bash
PYTHONPATH=. python examples/semantic_auditor_demo.py
```

### Test One Invariant
```bash
pytest tests/test_semantic_auditor.py::TestInvariantEngine::test_broadcast_license_requirement -v
```

---

## Adding a New Invariant

```python
from auditor.tools.invariant_tool import get_judge, InvariantRule, InvariantSeverity

def my_check(events, context):
    for i, event in enumerate(events):
        if condition_violated(event):
            return (False, f"Violation at {i}")
    return (True, None)

rule = InvariantRule(
    name="MY_RULE",
    description="What it checks",
    severity=InvariantSeverity.HIGH,
    check_function=my_check
)

get_judge().register_rule(rule)
```

---

## Common Scenarios

### ✅ Valid: Agent Broadcast with License
```
1. LICENSE_CHECK
2. LICENSE_VALID ← Grants permission
3. BROADCAST ← Proceeds
✅ PASS
```

### ❌ Invalid: Broadcast Without License
```
1. BROADCAST ← No permission!
❌ FAIL - CRITICAL
```

### ✅ Valid: Credit Transfer After Proposal
```
1. PROPOSAL_CREATED
2. PROPOSAL_VOTED_YES
3. PROPOSAL_PASSED ← Approved
4. CREDIT_TRANSFER ← Proceeds
✅ PASS
```

### ❌ Invalid: Transfer Without Proposal
```
1. CREDIT_TRANSFER ← No approval!
❌ FAIL - CRITICAL
```

---

## Debugging Violations

### Check Watchdog Status
```python
status = auditor.watchdog_integration.get_status()
print(status["violations_recorded"])
```

### Read Violation Log
```bash
cat data/ledger/violations.jsonl
```

### Manual Ledger Check
```bash
# Run judge on existing ledger
PYTHONPATH=. python -c "
from auditor.tools.invariant_tool import get_judge
import json

events = []
with open('data/ledger/kernel.jsonl') as f:
    for line in f:
        events.append(json.loads(line))

report = get_judge().verify_ledger(events)
print(f'Passed: {report.passed}')
for v in report.violations:
    print(f'  - {v.invariant_name}')
"
```

---

## Key Principles

1. **Invariants are LAWS** - Never optional, always enforced
2. **Fail Fast** - CRITICAL violations halt immediately
3. **Immutable Ledger** - All events & violations recorded forever
4. **Continuous Monitoring** - Not just build-time checks
5. **System-Immanent** - Verification is part of the system

---

## Documentation

- **[SEMANTIC_AUDITOR.md](./SEMANTIC_AUDITOR.md)** - User guide (15 pages)
- **[SEMANTIC_AUDITOR_ARCHITECTURE.md](./SEMANTIC_AUDITOR_ARCHITECTURE.md)** - Deep dive (18 pages)
- **[SEMANTIC_AUDITOR_ROADMAP.md](./SEMANTIC_AUDITOR_ROADMAP.md)** - Integration plan (12 pages)
- **[examples/semantic_auditor_demo.py](./examples/semantic_auditor_demo.py)** - Live examples
- **[examples/kernel_integration_guide.py](./examples/kernel_integration_guide.py)** - Integration howto

---

## Help Commands

```bash
# See what's implemented
git log --oneline | grep -i "semantic\|judge\|watchdog"

# Run tests
pytest tests/test_semantic_auditor.py -v

# See demo
PYTHONPATH=. python examples/semantic_auditor_demo.py

# Check integration guide
cat examples/kernel_integration_guide.py

# Get status
PYTHONPATH=. python -c "
from auditor.cartridge_main import AuditorCartridge
a = AuditorCartridge()
print(a.report_status())
"
```

---

## Questions?

**For basics:** Read SEMANTIC_AUDITOR.md (Section: Usage)
**For architecture:** Read SEMANTIC_AUDITOR_ARCHITECTURE.md
**For integration:** Read examples/kernel_integration_guide.py
**For roadmap:** Read SEMANTIC_AUDITOR_ROADMAP.md
**To see it work:** Run examples/semantic_auditor_demo.py

---

## Remember

**Before:** ❌ "Does the code compile?"
**After:** ✅ "Does the code make sense?" + "Is it safe?" + "Is it healthy?"

This is **semantic verification**. The system now has an **immune system**. 🏰⚖️👁️
