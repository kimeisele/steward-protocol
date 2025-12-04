# STUB CLEANUP ROADMAP

> **For:** Sonnet (parallel execution)
> **Created:** Opus Senior Audit
> **Priority:** P1 (after Vishnu Kernel stabilization)

---

## Overview

19 stubs detected by WIRING_AUDIT:
- 10 LOW priority
- 9 MEDIUM priority
- 0 CRITICAL

Most are in `agent_city/registry/` (citizen agents, not system agents).

---

## Category 1: Abstract Base Classes (KEEP - Not Bugs)

These are intentional design patterns:

```
steward/system_agents/scribe/tools/base.py:38-52
- NotImplementedError in abstract methods
- Status: CORRECT - abstract base class pattern
- Action: NONE
```

---

## Category 2: Templates (KEEP - Expected TODOs)

```
steward/system_agents/engineer/templates/agent/cartridge_main.py:101,106
- "# TODO: Implement your capability"
- Status: CORRECT - template for new agents
- Action: NONE
```

---

## Category 3: Citizen Agent Stubs (FIX or REMOVE)

These are in `agent_city/registry/` - example/citizen agents:

### LENS Agent (Marketing Analytics)
```
agent_city/registry/lens/cartridge_main.py:149  # TODO: Implement report generation
agent_city/registry/lens/cartridge_main.py:167  # TODO: Implement trend analysis
agent_city/registry/lens/cartridge_main.py:199  # TODO: Implement campaign benchmarking
agent_city/registry/lens/cartridge_main.py:215  # TODO: Implement predictive analysis
```
**Action:** Either implement or mark as "coming_soon" in manifest

### TEMPLE Agent (Content Auditing)
```
agent_city/registry/temple/cartridge_main.py:225  # TODO: Implement deep audit
agent_city/registry/temple/cartridge_main.py:277  # TODO: Implement real purity check
```
**Action:** Either implement or mark as "coming_soon"

### PULSE Agent (Social Media)
```
agent_city/registry/pulse/cartridge_main.py:123  # TODO: Implement governance validation
agent_city/registry/pulse/cartridge_main.py:139  # TODO: Implement Twitter API integration
agent_city/registry/pulse/cartridge_main.py:157  # TODO: Implement Twitter Metrics API integration
agent_city/registry/pulse/cartridge_main.py:171  # TODO: Implement trend analysis
```
**Action:** Either implement or mark as "coming_soon"

### MARKET Agent (DEX Integration)
```
agent_city/registry/market/cartridge_main.py:217  # TODO: Verify provider authorization
```
**Action:** Implement authorization check

### DHRUVA Agent (Genesis)
```
agent_city/registry/dhruva/tools/genesis_keeper.py:116  # TODO: Implement actual reset logic
```
**Action:** Implement or remove if not needed

---

## Category 4: System Agent Stubs (FIX)

### ARCHIVIST
```
steward/system_agents/archivist/tools/audit_tool.py:78
# TODO: Implement real verification with public_key when HERALD has STEWARD.md
```
**Action:** Check if HERALD now has STEWARD.md and implement

---

## Category 5: Governance Scripts (FIX)

```
scripts/governance/apply_for_visa.py:102
return "[PLACEHOLDER_PUBLIC_KEY]", None
```
**Action:** Implement real key generation or link to existing key system

---

## Execution Plan for Sonnet

### Phase 1: Quick Wins
1. Mark citizen agent TODOs as "coming_soon" in their manifests
2. Add `capabilities: ["coming_soon"]` to indicate work in progress

### Phase 2: Implement Critical
1. `apply_for_visa.py` - fix PLACEHOLDER_PUBLIC_KEY
2. `archivist/audit_tool.py` - implement verification if HERALD ready

### Phase 3: Optional Enhancements
1. Implement LENS analytics (if needed)
2. Implement PULSE Twitter integration (if needed)
3. Implement TEMPLE deep audit (if needed)

---

## Success Criteria

```bash
python steward/system_agents/envoy/tools/wiring_audit_scripts.py --scope full
# Target: <10 stubs (only templates and intentional abstracts)
```

---

*"Stubs are technical debt. Pay it down before it compounds."*
