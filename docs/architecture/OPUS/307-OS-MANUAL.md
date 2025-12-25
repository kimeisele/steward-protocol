# OPUS-307: STEWARD PROTOCOL OS MANUAL

> **Status**: DRAFT
> **Date**: 2025-12-25
> **Author**: Claude Opus 4.5 (Guardian Steward)
> **Purpose**: Windows 95 → Windows 7 Transformation

---

## EXECUTIVE SUMMARY

The Steward Protocol is an **Agent Operating System**. It has:
- A Kernel (1860 LOC)
- State Engine (Prakriti, 675 LOC)
- Cognitive Layer (MANAS, 62K+ LOC)
- 22+ Plugins, 43+ Tools, 17 Agents
- Unified CLI with 15+ commands

**The Problem**: Many capabilities exist but aren't CLI-accessible.
**GAD-000 Violation**: If an AI can't operate it via CLI, it's not compliant.

---

## PART 0: THE FRAKTAL PATTERN (VERIFIED)

```
Verified 2025-12-25:
- 30 Plugins, only 4 have CLI (15 commands)
- 16 Agents, 0 have CLI
- Only ENVOY has both Agent + Plugin
```

### The Fraktal Architecture

From `envoy/plugin_main.py`:
```
ENVOY is FRAKTAL:
1. The Concept (intent routing, system shell)
2. The Plugin (kernel connection, hooks)   ← CLI, Infrastructure
3. The Avatar (EnvoyCartridge agent)       ← The worker
```

| Component | Role | CLI Access |
|-----------|------|------------|
| Plugin | Kernel integration, hooks, infrastructure | ✅ via manifest.json |
| Agent (cartridge) | The Avatar, task processor | ❌ None |

### Agent → Plugin Coverage

| Agent | Has Plugin? | CLI Commands |
|-------|-------------|--------------|
| envoy | ✅ | (via unified_cli) |
| archivist | ❌ | 0 |
| auditor | ❌ | 0 |
| chronicle | ❌ | 0 |
| civic | ❌ | 0 |
| engineer | ❌ | 0 |
| herald | ❌ | 0 |
| watchman | ❌ | 0 |
| ... (8 more) | ❌ | 0 |

**15 of 16 system agents have NO CLI access.**

---

## PART 1: OS ARCHITECTURE

### The Kernel Layer

```
kernel_impl.py (1860 LOC)
├── pulse()           → Heartbeat
├── manifest()        → Execution request
├── register_agent()  → Add agents
├── get_status()      → System status
├── get_capabilities() → What it can do
└── Economy (Bank, Vault)
```

### The State Layer (Prakriti)

```
state/prakriti.py (675 LOC)
├── begin_session()   → Start state session
├── end_session()     → Commit state
├── get_state()       → Read state
└── Git integration   → Proof of Work
```

### The Cognitive Layer (MANAS)

```
plugins/opus_assistant/ (62K+ LOC)
├── cognitive_kernel.py    → The "consciousness"
├── events/kernel_tick.py  → Heartbeat processing
├── circuits/              → Auto-heal, health monitoring
└── manas/                 → Insight, planning, execution
```

### The CLI Layer

```
cli/unified_cli.py
├── SYSTEM: boot, stop, status, verify, ps
├── PRAKRITI: state, diff, plugins, update
├── MANAS HIL: pending, approve, reject, karma
└── CONDUCTOR: execute (circuits)
```

---

## PART 2: GAD-000 COMPLIANCE AUDIT

### Checklist per Component

| Component | Discoverable | Observable | Parseable | Composable | Idempotent | CLI |
|-----------|-------------|------------|-----------|------------|------------|-----|
| Kernel | ✅ status | ✅ ps | ✅ | ⚠️ | ✅ | ✅ |
| Prakriti | ✅ state | ✅ diff | ✅ | ✅ | ✅ | ✅ |
| MANAS | ✅ pending | ✅ karma | ✅ | ⚠️ | ⚠️ | ✅ |
| **Watchman** | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ |
| **Shuddhi** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Circuits** | ⚠️ | ❌ | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| Agents | ⚠️ | ❌ | ⚠️ | ❌ | ⚠️ | ❌ |

### Critical Gaps

1. **Watchman not in CLI**
   - Currently: `python scripts/ci/run_watchman_inspection.py`
   - Should be: `steward watchman inspect --json`

2. **Shuddhi not in CLI**
   - Currently: Only accessible via Python imports
   - Should be: `steward heal <file> --rule <id>`

3. **Circuits not fully wired**
   - Currently: `steward execute --circuit <path>` exists
   - Missing: Automatic triggering, result observability

4. **Remedies not declarative**
   - Currently: Hardcoded Python CST transformers
   - Should be: YAML-driven transformation rules

---

## PART 3: MISSING WIRING

### Self-Healing Pipeline

**Current State:**
```
Watchman (Python script)
    ↓ JSON file
??? (no connection)
    ↓
heal_codebase.yaml (exists but not triggered)
    ↓
Engineer (shuddhi_tool exists but not declarative)
```

**Target State:**
```
steward watchman inspect --json
    ↓
steward heal --auto (triggers circuit)
    ↓
heal_codebase.yaml (VEDA-4 state machine)
    ↓
Engineer uses YAML remedies from config/
    ↓
steward verify (confirms fix)
```

### Required CLI Commands

```yaml
# Watchman
steward watchman:
  inspect: Get violations as JSON
  status: Show violation counts
  rules: List active rules

# Healing
steward heal:
  auto: Run full pipeline
  file: Heal specific file
  verify: Check if healed

# Remedies
steward remedies:
  list: Show available remedies
  add: Add YAML remedy
  test: Dry-run remedy on file
```

---

## PART 4: DECLARATION

This document declares the Steward Protocol as an **Agent Operating System**.

| Aspect | Status |
|--------|--------|
| Kernel | ✅ Implemented |
| State Engine | ✅ Implemented |
| Cognitive Layer | ✅ Implemented |
| CLI | ⚠️ Partial |
| Self-Healing | ⚠️ Architecture exists, wiring incomplete |
| GAD-000 Compliant | ❌ Not yet |

### Windows 7 Criteria

- [ ] Everything manageable via CLI
- [ ] All capabilities discoverable
- [ ] All state observable
- [ ] All operations composable
- [ ] All errors parseable
- [ ] Self-healing pipeline working

---

## PART 5: THE D PROTOCOL (Windows 7 Roadmap)

### VERIFIED: Plugin/Agent Split is Historical Accident

From Haiku Analysis:
> "The separation between Plugin and Agent is NOT justified architecturally -
> it's HISTORICAL ACCIDENT masquerading as design."

**The Tool Protocol is ALREADY the unified interface.** 43+ tools exist with:
- `name`, `description`, `parameters_schema`
- `validate()`, `execute()`
- Auto-discoverable via `ToolDiscovery`

### THE D PROTOCOL: Incremental Unification

| Phase | Name | What | Result |
|-------|------|------|--------|
| **D** | Tool CLI | `steward tool <name>` | Humans can use all 43+ tools |
| **D+** | Agent CLI | Agents call CLI internally | Agents use same interface as humans |
| **D++** | Circuit CLI | `steward circuit run <name>` | Workflows via CLI |
| **D+++** | Unified Protocol | Everything is a "Tool" | One interface for all |
| **D++++** | Self-Management | System heals via CLI | Windows 7 achieved |

### Phase D: Tool Protocol CLI (~500 LOC, 1.75 days)

**Files to create:**
1. `vibe_core/cli/tool_cli.py` - ToolCLI class
2. `vibe_core/cli/tool_argparse.py` - Auto-generated parser
3. Update `unified_cli.py` - Route "tool" commands

**Commands:**
```bash
steward tool list                              # All 43+ tools
steward tool info watchman.standards           # Show schema
steward tool run watchman.standards --json     # Execute, JSON output
steward tool run civic.bank --interactive      # Prompt for params
```

**Zero manual wiring:** CLI reads directly from Tool Protocol.

### Phase D+: Agents Use CLI

Instead of:
```python
# Current: Direct tool call
result = self.tool_registry.execute("watchman.standards", params)
```

Agents do:
```python
# D+: Via CLI protocol
result = self.system.cli("tool run watchman.standards --json")
```

**Why?** Same interface for humans AND agents. Logs, audit, everything unified.

### Phase D++: Circuit CLI

```bash
steward circuit list                           # All circuits
steward circuit run heal_codebase --violation-file X --rule Y
steward circuit status <execution_id>          # Check progress
```

### Phase D+++: Everything is a Tool

```python
# Plugins expose themselves as tools
class WatchmanPlugin(KernelPlugin):
    def get_tools(self) -> List[Tool]:
        return [
            PatrolTool(),      # From agent
            InspectTool(),     # From agent
            StatusTool(),      # Plugin-level
        ]
```

No more Plugin vs Agent. Just: **Components that provide Tools.**

### Phase D++++: Self-Management (Windows 7)

```bash
# The system manages itself
steward heal --auto                            # Full pipeline
steward health --fix                           # Auto-repair
steward upgrade --safe                         # Self-update
```

**GAD-000 achieved:** AI can operate EVERYTHING via CLI.

---

## IMPLEMENTATION ORDER

1. **NOW: Phase D** - Tool Protocol CLI
2. **NEXT: Phase D++** - Circuit CLI
3. **THEN: Phase D+** - Agents use CLI
4. **FINALLY: D+++/D++++** - Full unification

---

## @HARNESS

```bash
# Phase 4 verification commands (to be implemented)

# Check 1: CLI discoverable
steward --help --json | jq '.commands | length'
# Expected: >= 20

# Check 2: Watchman accessible
steward watchman inspect --json | jq '.violations | length'
# Expected: Returns number

# Check 3: Heal works
steward heal --dry-run --file <test_file> --rule silent_failure
# Expected: Shows what would change

# Check 4: Full pipeline
steward heal --auto --dry-run
# Expected: Lists all fixable violations
```

---

*"Von Windows 95 zu Windows 7. Der Weg ist klar. Die Arbeit beginnt."*
