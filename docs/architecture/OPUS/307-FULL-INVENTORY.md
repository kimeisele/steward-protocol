# OPUS-307: FULL INVENTORY & CONSOLIDATION

> **Status**: 🔥 READY FOR HAIKU (Pre-Analysis)
> **Date**: 2025-12-25
> **Author**: Claude Opus 4.5 (Senior Steward)
> **Priority**: P1 - Foundation for OS-Level Operations
> **Depends on**: OPUS-306 ✅ COMPLETE (Boot: 97s → 7.4s)

---

## THE VISION

We built **Windows 95 for Agents**. But we're still using it like DOS.

```
Current state:                      Target state:
─────────────────                   ─────────────────
Manual violations fix               → Watchman → Circuit → Engineer → Archivist
Manual task creation                → MANAS cognitive planning
Manual deployment                   → Self-organizing agent swarm
```

Before we can leverage the OS, we need a **full inventory**.

---

## PHASE 1: HAIKU PRE-ANALYSIS

### Task H1: Plugin Inventory
```bash
# For each plugin in vibe_core/plugins/:
# - Read manifest.json + plugin_main.py
# - Document: ID, purpose, dependencies, circuits
```

**Output**: `docs/architecture/OPUS/307-PREP-plugins.md`

### Task H2: Circuit Inventory
```bash
# For each .yaml in vibe_core/playbook/circuits/ and plugins/**/circuits/:
# - Document: ID, trigger, states, actions
```

**Output**: `docs/architecture/OPUS/307-PREP-circuits.md`

### Task H3: Agent Inventory
```bash
# For each agent in vibe_core/cartridges/system/ and agent_city/:
# - Document: ID, tools, capabilities
```

**Output**: `docs/architecture/OPUS/307-PREP-agents.md`

### Task H4: Redundancy Analysis
```bash
# Compare inventories:
# - Which agents overlap in function?
# - Which circuits are never triggered?
# - Which plugins are dormant?
```

**Output**: `docs/architecture/OPUS/307-PREP-redundancy.md`

---

## PHASE 2: SONNET EXECUTION

After Haiku prep, Sonnet executes:

### Task S1: Create Unified Capability Map
- Merge all PREP files into `CAPABILITY_MAP.md`
- Create visual diagram (mermaid) of agent relationships

### Task S2: Wire Watchman → heal_codebase Circuit
- Verify the 802 violations can trigger the circuit
- Test one violation end-to-end

### Task S3: Document Missing Wiring
- List which capabilities are NOT connected
- Create TODO for each missing wire

### Task S4: Create MANAS Integration Plan
- How should MANAS orchestrate healing?
- What circuits should MANAS know about?

---

## PHASE 3: OPUS REVIEW

Senior reviews Sonnet's work, then:

1. **Approve** capability map
2. **Decide** on redundancy elimination
3. **Plan** OPUS-308: Self-Healing Pipeline

---

## KNOWN COMPONENTS (Starting Point)

### Core Plugins (~35)
- opus_assistant (MANAS cognitive kernel)
- interface (rendering)
- agent_city (agent spawning)
- samsara (reincarnation)
- durvasa (triage)
- test_orchestration
- ... (Haiku to enumerate)

### Circuits
- heal_codebase.yaml (VEDA-4 state machine)
- auto_heal.yaml (MANAS drift response)
- manas_health.yaml
- ... (Haiku to enumerate)

### Agents (Watchman, Engineer, Archivist, Herald, Envoy, ...)
- ~30 in cartridges/system/
- More in agent_city

---

## SUCCESS CRITERIA

- [ ] All plugins documented with purpose
- [ ] All circuits documented with triggers
- [ ] All agents documented with tools
- [ ] Redundancy report created
- [ ] At least ONE end-to-end healing test passes
- [ ] CAPABILITY_MAP.md created and reviewed

---

## HANDOFF: OPUS → HAIKU

```markdown
## HAIKU: Pre-analyze OPUS-307

You are a Junior Analyst preparing context for Senior Steward.

Tasks (create 4 files):

### 1. Plugin Inventory (307-PREP-plugins.md)
For each directory in vibe_core/plugins/:
- Read manifest.json (if exists)
- Read first 50 lines of plugin_main.py
- Document: id, name, purpose (1 sentence), has_circuits (yes/no)

### 2. Circuit Inventory (307-PREP-circuits.md)
Find all .yaml files:
- vibe_core/playbook/circuits/*.yaml
- vibe_core/plugins/**/circuits/*.yaml
For each: document id, entry_state, triggers (if any)

### 3. Agent Inventory (307-PREP-agents.md)
For each directory in vibe_core/cartridges/system/:
- Read cartridge_main.py or tools/*.py
- Document: id, tools (list names), purpose (1 sentence)

### 4. Redundancy Analysis (307-PREP-redundancy.md)
Look for:
- Agents with similar tool names
- Plugins with overlapping capabilities
- Circuits that might be duplicates

Output to: docs/architecture/OPUS/307-PREP-*.md
```

---

*"Know thy tools before wielding them. The Agent OS awaits." - OPUS-307*
