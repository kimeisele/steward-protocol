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

## PART 5: ACTION PLAN

### FUNDAMENTAL DECISION REQUIRED

**The Problem:** 15/16 agents have no CLI → not GAD-000 compliant.

**Options:**

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A: Individual plugins | Create 15 new plugins wrapping each agent | Clean separation | 15 more plugins, maintenance |
| B: system_agents plugin | One plugin wrapping all agents | Single point of entry | Tight coupling, huge plugin |
| C: CLI Bridge | Add direct CLI in unified_cli.py | Minimal change | Bypasses plugin architecture |
| D: Tool Protocol CLI | Auto-generate CLI from Tool registry | Elegant, scalable | Requires new infrastructure |

**Recommendation:** Option D (Tool Protocol CLI)
- Every Tool already has `name`, `description`, `parameters_schema`
- CLI could auto-discover: `steward tool <tool_name> [args]`
- Example: `steward tool watchman.standards --action inspect_all`

### Phase 1: Tool Protocol CLI (D)
1. Add `steward tool list` - show all 43 tools
2. Add `steward tool <name> [--params JSON]` - execute any tool
3. Auto-generate --help from parameters_schema

### Phase 2: Declarative Remedies
1. Create `config/remedies.yaml` schema
2. Move CST patterns to YAML definitions
3. Make Engineer read from config, not hardcode

### Phase 3: Self-Healing Wiring
1. `steward tool watchman.standards` → Get violations
2. `steward execute --circuit heal_codebase.yaml` → Trigger healing
3. Chain them: `steward heal --auto`

### Phase 4: Verification
1. Add @HARNESS sections to this doc
2. Create automated GAD-000 compliance tests
3. Run and document results

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
