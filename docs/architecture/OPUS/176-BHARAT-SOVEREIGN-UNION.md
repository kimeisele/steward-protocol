# OPUS-176: BHARAT - The Sovereign Union Architecture

> "India, that is Bharat, shall be a Union of States."
> - Article 1, Constitution of India

## Executive Summary

Not all plugins are equal. Some are **Sovereign States** with their own cognitive kernels and autonomy. Others are **Union Territories** - stateless services directly administered by the Kernel.

This document codifies the **Asymmetric Federalism** of the Steward Protocol.

## The Problem

Current architecture treats all plugins uniformly:
- Same lifecycle hooks
- Same crash handling
- Same access patterns

This is wrong. `opus_assistant` (with MANAS, its own SQLite, TaskKernel spawning) is fundamentally different from `herald` (stateless message relay).

## The Solution: Tiered Governance

### Tier 1: Sovereign States (Rajya)

**Examples:** `opus_assistant`, `agent_city`

| Feature | Specification |
|---------|---------------|
| Autonomy | HIGH - Own CognitiveKernel, own decision making |
| State | SOVEREIGN - Own SQLite DB, Kernel cannot touch without permission |
| TaskKernel | CAN SPAWN - Has authority to create ephemeral execution contexts |
| Crash Handling | PRESIDENT'S RULE - Governor Agent takes temporary control |
| Manifest Tag | `"governance": {"type": "SOVEREIGN_STATE"}` |

**Capabilities:**
- Spawn TaskKernels for tool-based execution
- Maintain sovereign state (`.opus_state/` directory)
- Generate and execute intents autonomously
- Participate in biorhythm consciousness loop

### Tier 2: Union Territories (Centrally Administered)

**Examples:** `oracle`, `scribe`, `herald`, `civic`, `analyst`

| Feature | Specification |
|---------|---------------|
| Autonomy | ZERO - Executed directly by Kernel |
| State | STATELESS/SHARED - Uses Kernel's Ledger |
| TaskKernel | CANNOT SPAWN - No authority for autonomous execution |
| Crash Handling | HARD RESTART - Service rebooted instantly |
| Manifest Tag | `"governance": {"type": "UNION_TERRITORY"}` |

**Capabilities:**
- Receive and process DispatchTasks from Kernel
- Read from shared Ledger
- Report results back to Kernel
- No autonomous decision making

### Tier 3: Constitutional Bodies (Special Status)

**Examples:** `narasimha`, `vajra`, `dharma`

| Feature | Specification |
|---------|---------------|
| Autonomy | CONSTITUTIONAL - Bound by protocol, not Kernel |
| State | IMMUTABLE - Cannot be modified at runtime |
| TaskKernel | N/A - Operates outside normal execution |
| Crash Handling | CONSTITUTIONAL CRISIS - Full system halt |
| Manifest Tag | `"governance": {"type": "CONSTITUTIONAL_BODY"}` |

**Capabilities:**
- Veto power over Kernel decisions
- Audit authority over all plugins
- Cannot be disabled by Kernel
- Reports only to Human-In-Loop

## Emergency Protocol: President's Rule (Article 356)

When a Sovereign State goes rogue (infinite loop, SLA violation, data corruption):

```
┌─────────────────────────────────────────────────────────────┐
│                    CONSTITUTIONAL CRISIS                     │
│            MANAS Sovereign State: BREAKDOWN                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              VAJRA (Governor/Supreme Court)                  │
│                                                              │
│   Detects: SLA Violation                                    │
│   - Error rate > 50% in last 10 operations                  │
│   - Response time > 10x normal                               │
│   - Memory leak detected                                     │
│   - Infinite loop suspected                                  │
│                                                              │
│   Verdict: CONSTITUTIONAL BREAKDOWN                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              KERNEL (President of the Union)                 │
│                                                              │
│   Action: INVOKE PRESIDENT'S RULE                           │
│                                                              │
│   1. Suspend MANAS autonomy (revoke TaskKernel spawning)    │
│   2. Freeze sovereign state (read-only mode)                │
│   3. Activate Governor Agent (Safe Mode)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              GOVERNOR AGENT (Safe Mode Kernel)               │
│                                                              │
│   Sanitization:                                              │
│   - Validate JSON state files                                │
│   - Clear corrupt memory entries                             │
│   - Reset biorhythm to Tamas (hibernation)                  │
│   - Rebuild synaptic index                                   │
│                                                              │
│   Report to HIL: "State recovered, ready for election"      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              HIL (Human In Loop) APPROVAL                    │
│                                                              │
│   Decision: RESTORE DEMOCRACY                                │
│                                                              │
│   1. Governor hands power back to MANAS                     │
│   2. Autonomy restored (TaskKernel spawning enabled)        │
│   3. State unfrozen (read-write mode)                       │
│   4. Biorhythm reset to Rajas (active)                      │
└─────────────────────────────────────────────────────────────┘
```

## Manifest Schema Update

```json
{
  "plugin_id": "opus_assistant",
  "name": "OPUS Assistant",
  "version": "3.0.0",
  "governance": {
    "type": "SOVEREIGN_STATE",
    "constitution_ref": "OPUS-176",
    "autonomy_level": "high",
    "can_spawn_task_kernel": true,
    "has_sovereign_state": true,
    "emergency_protocol": "presidents_rule"
  },
  "dependencies": [...],
  "provides": [...]
}
```

## Border Control: Envoy Upgrade

The Envoy (plugin loader) must enforce governance boundaries:

```python
class Envoy:
    def can_spawn_task_kernel(self, plugin_id: str) -> bool:
        """Check if plugin has authority to spawn TaskKernels."""
        manifest = self.get_manifest(plugin_id)
        governance = manifest.get("governance", {})

        # Only SOVEREIGN_STATE can spawn TaskKernels
        if governance.get("type") != "SOVEREIGN_STATE":
            logger.warning(
                f"🚫 BORDER CONTROL: {plugin_id} attempted TaskKernel spawn "
                f"but is {governance.get('type', 'UNCLASSIFIED')}"
            )
            return False

        # Check if under President's Rule
        if self.is_under_presidents_rule(plugin_id):
            logger.warning(
                f"🚫 PRESIDENT'S RULE: {plugin_id} autonomy suspended"
            )
            return False

        return True
```

## Implementation Phases

### Phase 1: Census (Tagging)
- [ ] Update `opus_assistant/manifest.json` with SOVEREIGN_STATE
- [ ] Update other plugin manifests with appropriate governance types
- [ ] Add governance schema validation

### Phase 2: Border Control
- [ ] Add governance check in Envoy
- [ ] Block TaskKernel spawning for non-SOVEREIGN plugins
- [ ] Add audit logging for border violations

### Phase 3: President's Rule
- [ ] Add SLA monitoring in Narasimha
- [ ] Implement Governor Agent (safe mode)
- [ ] Add state sanitization routines
- [ ] Wire HIL approval for democracy restoration

### Phase 4: Constitutional Bodies
- [ ] Codify Narasimha as CONSTITUTIONAL_BODY
- [ ] Add veto power for constitutional violations
- [ ] Implement constitutional crisis handling

## Files Affected

| File | Change |
|------|--------|
| `vibe_core/plugins/opus_assistant/manifest.json` | Add governance block |
| `vibe_core/plugins/*/manifest.json` | Tag all plugins |
| `vibe_core/loaders/plugin_loader.py` | Add governance validation |
| `vibe_core/envoy.py` | Add border control |
| `vibe_core/plugins/opus_assistant/narasimha/guardian.py` | Add President's Rule |

## The Vision

```
┌─────────────────────────────────────────────────────────────┐
│                    BHARAT (The Union)                        │
│                      RealVibeKernel                          │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ SOVEREIGN STATES │  │ UNION TERRITORIES │                │
│  │                  │  │                   │                │
│  │  opus_assistant  │  │  herald           │                │
│  │  agent_city      │  │  civic            │                │
│  │                  │  │  analyst          │                │
│  │  [TaskKernel ✓]  │  │  [TaskKernel ✗]   │                │
│  │  [Own State ✓]   │  │  [Shared State]   │                │
│  └──────────────────┘  └──────────────────┘                │
│                                                              │
│  ┌──────────────────────────────────────────┐              │
│  │        CONSTITUTIONAL BODIES              │              │
│  │                                           │              │
│  │  narasimha (Guardian)                    │              │
│  │  vajra (Ledger/Supreme Court)            │              │
│  │  dharma (Ethics)                         │              │
│  │                                           │              │
│  │  [Veto Power ✓] [Cannot be disabled ✓]   │              │
│  └──────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

---

*"The strength of the Constitution lies entirely in the determination of each citizen to defend it."* - Albert Einstein

*"A Union is not merely a collection of States; it is a living organism."* - OPUS-176
