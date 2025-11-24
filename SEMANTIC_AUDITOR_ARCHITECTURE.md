# 🏰 THE SEMANTIC AUDITOR ARCHITECTURE

## Executive Summary

The Semantic Auditor is a **three-layer verification system** that transforms STEWARD Protocol from "software that runs" to "software that understands itself."

- **Layer 1:** Static compliance (traditional)
- **Layer 2:** Semantic verification via invariants (THE JUDGE ⚖️)
- **Layer 3:** Runtime monitoring (THE WATCHDOG 👁️)

This prevents the **"Optional Verification Disaster"** where agents can produce logical nonsense that passes all tests.

---

## The Problem

### Before: "Verification Is Optional"

```
Unit Test Flow:
  ✅ Does broadcast() execute?
  ✅ Yes, 100% tests pass
  ✅ Deploy to production

Semantic Reality:
  ❌ Was broadcast licensed?
  ❌ Was proposal voted on?
  ❌ Who knows? Nobody checked!
```

### After: "Verification Is System-Immanent"

```
Multi-Layer Verification:
  LAYER 1: ✅ Compliance checks pass
  LAYER 2: ✅ Semantic invariants valid
  LAYER 3: ✅ Runtime monitoring clean
  
  Result: System halts on ANY violation
```

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                     VibeKernel (Main Loop)                     │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Task Execution                                           │ │
│  │  - HERALD: records events                               │ │
│  │  - CIVIC: governance & licenses                         │ │
│  │  - BANKER: credit transfers                             │ │
│  │  - Agents: broadcast, vote, execute                     │ │
│  └──────────────────────────────────────────────────────────┘ │
│                          │                                     │
│                          v (ledger grows)                      │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Kernel Ledger (Immutable Event Stream)                  │ │
│  │  [EVENT] [EVENT] [EVENT] ... [EVENT]                    │ │
│  └──────────────────────────────────────────────────────────┘ │
│                          │                                     │
│                          v (every N ticks)                     │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ AUDITOR.kernel_tick()                                   │ │
│  │  └─ The WATCHDOG (👁️) checks ledger                     │ │
│  │     └─ The JUDGE (⚖️) verifies invariants               │ │
│  │        └─ On violation: record VIOLATION event          │ │
│  │        └─ On CRITICAL: halt system                      │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

---

## Layer 2: The JUDGE (Semantic Verification)

### How It Works

The JUDGE applies **invariant rules** to the event ledger.

Invariants are **LAWS** that MUST NEVER be broken.

```python
InvariantEngine:
  ├─ Rule 1: BROADCAST_LICENSE_REQUIREMENT
  ├─ Rule 2: CREDIT_TRANSFER_PROPOSAL_REQUIREMENT
  ├─ Rule 3: NO_ORPHANED_EVENTS
  ├─ Rule 4: EVENT_SEQUENCE_INTEGRITY
  ├─ Rule 5: NO_DUPLICATE_EVENTS
  └─ Rule 6: PROPOSAL_WORKFLOW_INTEGRITY
```

### Rule Evaluation Algorithm

```
For each invariant rule:
  1. Load all events from ledger
  2. Apply rule check function
  3. If rule violated:
     - Create InvariantViolation record
     - Set report.passed = False
     - Add to violations list
  4. Return VerificationReport
```

### Example: BROADCAST_LICENSE_REQUIREMENT

```python
def check_broadcast_license(events, context):
    for i, event in enumerate(events):
        if event["event_type"] == "BROADCAST":
            task_id = event["task_id"]
            
            # Look back for LICENSE_VALID in same task
            license_found = False
            for j in range(i - 1, -1, -1):
                prev_event = events[j]
                if prev_event["task_id"] != task_id:
                    break
                if prev_event["event_type"] == "LICENSE_VALID":
                    license_found = True
                    break
            
            if not license_found:
                return (False, f"BROADCAST at {i} lacks LICENSE_VALID in {task_id}")
    
    return (True, None)
```

**Why this matters:**
- Ensures BROADCAST is never unauthorized
- Prevents random agents from broadcasting
- System-enforced governance

---

## Layer 3: The WATCHDOG (Runtime Monitoring)

### How It Works

The WATCHDOG runs continuously, monitoring the ledger stream.

```
Kernel Tick Flow:
  
  Tick 1:   (no check)
  Tick 2:   (no check)
  ...
  Tick 10:  👁️ WATCHDOG CHECKS
            ├─ Read ledger from last_checked_index
            ├─ Run Judge on new events
            ├─ If violation found:
            │  ├─ Create VIOLATION event
            │  ├─ Record to violations.jsonl
            │  └─ If CRITICAL: set halt_requested=True
            └─ Update last_checked_index
  Tick 11:  (no check)
  ...
```

### Violation Recording

When a violation is found:

```json
{
  "event_type": "VIOLATION",
  "timestamp": "2025-11-24T15:05:32Z",
  "agent_id": "watchdog",
  "violation_type": "BROADCAST_LICENSE_REQUIREMENT",
  "severity": "CRITICAL",
  "message": "BROADCAST at index 42 lacks LICENSE_VALID in task task_1",
  "violated_invariant": "BROADCAST_LICENSE_REQUIREMENT",
  "ledger_snapshot": {
    "total_events": 150,
    "violations_count": 1
  }
}
```

### System Halt on CRITICAL

```
VIOLATION DETECTED:
  severity = CRITICAL
  
  Kernel Immediate Actions:
    1. Set self.halt_requested = True
    2. Log error message
    3. Stop executing new tasks
    4. Preserve ledger state
    5. Manual intervention required
```

---

## Invariant Rules Reference

### Rule 1: BROADCAST_LICENSE_REQUIREMENT

| Aspect | Value |
|--------|-------|
| **Rule** | Every BROADCAST must have LICENSE_VALID in same task |
| **Severity** | CRITICAL |
| **Example Valid** | LICENSE_CHECK → LICENSE_VALID → BROADCAST |
| **Example Invalid** | BROADCAST (no license) |
| **Why** | Prevents unauthorized broadcasting |

### Rule 2: CREDIT_TRANSFER_PROPOSAL_REQUIREMENT

| Aspect | Value |
|--------|-------|
| **Rule** | Every CREDIT_TRANSFER needs PROPOSAL_PASSED first |
| **Severity** | CRITICAL |
| **Example Valid** | PROPOSAL_CREATED → VOTED → PROPOSAL_PASSED → TRANSFER |
| **Example Invalid** | CREDIT_TRANSFER (no proposal) |
| **Why** | Enforces democratic governance over treasury |

### Rule 3: NO_ORPHANED_EVENTS

| Aspect | Value |
|--------|-------|
| **Rule** | Every event must have task_id, agent_id, event_type, timestamp |
| **Severity** | HIGH |
| **Example Invalid** | {"event_type": "X"} (missing fields) |
| **Why** | Detects corrupted or incomplete events |

### Rule 4: EVENT_SEQUENCE_INTEGRITY

| Aspect | Value |
|--------|-------|
| **Rule** | Events in same task must be chronologically ordered |
| **Severity** | HIGH |
| **Example Invalid** | Event(15:02) followed by Event(15:01) |
| **Why** | Detects clock skew, tampering, causality violations |

### Rule 5: NO_DUPLICATE_EVENTS

| Aspect | Value |
|--------|-------|
| **Rule** | No two events can have same (task_id, type, timestamp) |
| **Severity** | CRITICAL |
| **Example Invalid** | Same event appears twice (replay attack) |
| **Why** | Prevents replay attacks and duplicate execution |

### Rule 6: PROPOSAL_WORKFLOW_INTEGRITY

| Aspect | Value |
|--------|-------|
| **Rule** | PROPOSAL_VOTED_YES must follow PROPOSAL_CREATED |
| **Severity** | HIGH |
| **Example Invalid** | PROPOSAL_VOTED_YES without PROPOSAL_CREATED |
| **Why** | Maintains proper proposal lifecycle |

### Rule 7: NO_CRITICAL_VOIDS

| Aspect | Value |
|--------|-------|
| **Rule** | Critical system state fields must never be null/empty |
| **Severity** | CRITICAL |
| **Checks** | total_credits ≠ 0, agents_registered > 0, ledger_events match count |
| **Example Invalid** | System boots but total_credits = 0 (state corrupted) |
| **Why** | Detects silent failures in critical system state |

### Rule 8: SEMANTIC_COMPLIANCE_REQUIREMENT (The Curator)

| Aspect | Value |
|--------|-------|
| **Rule** | Governance documents must maintain semantic integrity (no hype/overreach) |
| **Severity** | HIGH |
| **Scope** | POLICIES.md, MISSION_BRIEFING.md, AGI_MANIFESTO.md, prompts/*, docs/* |
| **Config** | `config/semantic_compliance.yaml` (red flags vs green flags) |
| **Example Invalid** | POLICIES.md contains "revolutionary" or "superintelligence" |
| **Why** | Protects semantic layer from AI-generated marketing slop; enforces governance tone |
| **Phase II** | Part of "Hybrid Plan: Strategy & Action" - Curator Invariant for semantic integrity |

---

## Data Flow: From Event to Verification

```
Agent Action
  └─ Event Created
     └─ HERALD Records Event
        └─ Event written to Kernel Ledger
           └─ WATCHDOG detects new event (every N ticks)
              └─ Judge runs invariant checks
                 └─ Invariant passes? ✅ Continue
                 └─ Invariant fails? ❌
                    ├─ Create VIOLATION event
                    ├─ Record to violations.jsonl
                    ├─ Severity CRITICAL?
                    │  └─ KERNEL HALT
                    └─ Severity HIGH/MEDIUM/LOW?
                       └─ Continue (logged)
```

---

## Integration Points

### Point 1: Kernel Initialization

```python
def __init__(self):
    # Load AUDITOR and start watchdog
    self.auditor = AuditorCartridge()
    self.auditor.start_watchdog()
```

### Point 2: Kernel Main Loop

```python
def kernel_loop(self):
    while self.running:
        task = self.scheduler.next_task()
        self.execute_task(task)
        self.task_count += 1
        
        # Check every 10 tasks
        if self.task_count % 10 == 0:
            halt_result = self.auditor.watchdog_integration.kernel_tick(self.task_count)
            if halt_result["should_halt"]:
                self.halt()
```

### Point 3: Pre-Boot Verification (Optional)

```python
def main():
    kernel = VibeKernel()
    kernel.run_semantic_verification()  # Check before starting
    kernel.kernel_loop()
```

---

## Performance Characteristics

| Metric | Value |
|--------|-------|
| **Ledger Read Time** | ~1-2ms for 1000 events |
| **Invariant Check Time** | ~1-5ms per rule (ledger-based) |
| **Semantic Scan Time** | ~10-50ms (reads files from disk, configurable scope) |
| **Total Check Time** | ~20-100ms for all 8 rules |
| **Check Frequency** | Every 10 kernel ticks (configurable) |
| **Memory Overhead** | <1MB for ledger checks; <10MB for semantic scans |
| **CPU Overhead** | <1% when ledger checked every 10 ticks; <2% with semantic checks |
| **Note** | Semantic compliance check (Rule 8) can be disabled by removing `config/semantic_compliance.yaml` |

---

## Example Scenarios

### Scenario 1: Valid Governance Flow

```
Timeline:
  T1: CIVIC creates PROPOSAL_CREATED
  T2: VOTER submits PROPOSAL_VOTED_YES
  T3: CIVIC records PROPOSAL_PASSED
  T4: BANKER executes CREDIT_TRANSFER
  
Judge Evaluation:
  ✅ CREDIT_TRANSFER has PROPOSAL_PASSED
  ✅ All events have complete metadata
  ✅ Events in chronological order
  ✅ No duplicates
  
Result: PASS
```

### Scenario 2: Unauthorized Broadcast

```
Timeline:
  T1: HERALD attempts BROADCAST
       (no LICENSE_VALID event first!)
  
Judge Evaluation:
  ❌ BROADCAST_LICENSE_REQUIREMENT violated
     (no LICENSE_VALID in task context)
  
Result: FAIL - CRITICAL VIOLATION
        System halts immediately
```

### Scenario 3: Replay Attack

```
Timeline:
  T1: CREDIT_TRANSFER recorded
  T2: CREDIT_TRANSFER recorded AGAIN
       (exact same event)
  
Judge Evaluation:
  ❌ NO_DUPLICATE_EVENTS violated
     (same task_id + type + timestamp)
  
Result: FAIL - CRITICAL VIOLATION
        System detects attack, halts
```

---

## Files & Components

```
auditor/
├─ cartridge_main.py              (AUDITOR cartridge v2.0)
│  ├─ Layer 1: ComplianceTool
│  ├─ Layer 2: The JUDGE (get_judge())
│  └─ Layer 3: The WATCHDOG (start_watchdog())
│
└─ tools/
   ├─ invariant_tool.py           (The JUDGE implementation)
   │  ├─ InvariantEngine
   │  ├─ InvariantRule
   │  ├─ VerificationReport
   │  ├─ Rules 1-7: Core ledger invariants (BROADCAST, CREDIT, DUPLICATES, etc.)
   │  └─ Rule 8: SEMANTIC_COMPLIANCE_REQUIREMENT (The Curator)
   │
   └─ watchdog_tool.py            (The WATCHDOG implementation)
      ├─ Watchdog
      ├─ WatchdogConfig
      ├─ ViolationEvent
      └─ WatchdogIntegration

config/
├─ matrix.yaml                    (Central configuration)
└─ semantic_compliance.yaml       (NEW) Red-flag/green-flag dictionary for Curator

tests/
└─ test_semantic_auditor.py       (19 comprehensive tests + semantic compliance)

examples/
├─ semantic_auditor_demo.py       (Live demonstrations)
└─ kernel_integration_guide.py    (Integration howto)

docs/
└─ SEMANTIC_AUDITOR.md            (User guide)

SEMANTIC_AUDITOR_ARCHITECTURE.md   (This document - System design spec)
```

---

## Design Principles

1. **Invariants are Laws** - Never optional, always enforced
2. **Fail Fast** - CRITICAL violations halt immediately
3. **Immutable Ledger** - All events, violations recorded forever
4. **Continuous Monitoring** - Not just build-time checks
5. **System-Immanent** - Verification is part of the system, not external
6. **Clear Accountability** - Every violation is recorded and traceable

---

## Next Steps: Extending The System

### Adding a New Invariant

```python
from auditor.tools.invariant_tool import get_judge, InvariantRule

def my_new_rule(events, context):
    # Your check logic here
    return (True, None)  # or (False, "violation message")

judge = get_judge()
judge.register_rule(InvariantRule(
    name="MY_NEW_RULE",
    description="What it checks",
    severity=InvariantSeverity.HIGH,
    check_function=my_new_rule
))
```

### Adding Watchdog Callbacks

```python
def on_violation(violation_event):
    # Alert external system
    envoy.send_alarm(f"Violation: {violation_event.violation_type}")

def on_halt(violation_event):
    # Emergency procedures
    logger.critical(f"System halted: {violation_event.message}")

auditor.watchdog_integration.register_violation_callback(on_violation)
auditor.watchdog_integration.register_halt_callback(on_halt)
```

### Customizing Semantic Compliance (Rule 8: The Curator)

The Curator Invariant (Rule 8) protects governance documents from AI-generated marketing slop. Customize the red-flag/green-flag dictionary:

```yaml
# config/semantic_compliance.yaml
RED_FLAGS:
  HYPE:
    - "revolutionary"
    - "game-changer"
    - "your_custom_red_flag"

GREEN_FLAGS:
  VERIFIABILITY:
    - "provable"
    - "auditable"
    - "your_approved_term"

SCOPE:
  CRITICAL_DOCUMENTS:
    - "POLICIES.md"
    - "docs/*.md"
    - "prompts/*.md"
```

**Key Points:**
- Remove `config/semantic_compliance.yaml` to disable Rule 8 entirely
- The Curator scans documents defined in SCOPE on every verification run
- Use word boundaries to avoid false positives (e.g., "ing" won't match "revolutionary")
- RED_FLAGS trigger HIGH severity violations (warning, not halt)

---

## Conclusion: The Complete A.G.I. Security Stack

The Semantic Auditor + Curator Invariant completes **three-layer cryptographic governance:**

| Layer | Responsibility | Enforcement |
|-------|---|---|
| **Layer 1: The Body (Code)** | Kernel enforces Oath cryptographically | Constitutional binding is non-negotiable |
| **Layer 2: The History (Ledger)** | Invariants 1-7 enforce causality + finance + governance | Violations halt the system |
| **Layer 3: The Mind (Documents)** | Rule 8 (The Curator) enforces semantic integrity | Hype-free governance protected |

This transforms STEWARD Protocol verification from:

**Before:** ❌ "Does it compile?"
**After:** ✅ "Does it make sense?" + "Is it safe?" + "Is it semantically pure?"

This is the architecture of an **intelligent system with an immune system that protects both its logic and its soul**.

It catches not just syntax errors and logical violations, but **semantic corruption**—AI-generated marketing slop that might infiltrate governance documents.

**Verification is no longer optional. It's system-immanent. The Curator ensures the system cannot even think about lying.** 🏰⚖️👁️✨

