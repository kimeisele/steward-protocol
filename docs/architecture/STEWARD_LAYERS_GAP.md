# STEWARD Protocol - Implementation Gap Analysis

> **Status:** LIVING DOC - Updated as implementation progresses
> **Date:** 2025-12-05
> **Purpose:** Track gap between SPECIFICATION.md vision and actual implementation

---

## The Trinity (Fractal Architecture)

```
┌─────────────────┬─────────────────┬─────────────────┐
│     KERNEL      │     PHOENIX     │     STEWARD     │
│    (Vishnu)     │    (Config)     │   (Protocol)    │
│   Execution     │   Parameters    │   Agent Meta    │
├─────────────────┼─────────────────┼─────────────────┤
│ plugin_loader   │ section_loader  │ agent_loader    │
│ plugins/        │ sections/       │ system_agents/  │
│ KernelPlugin    │ ConfigSection   │ AgentManifest   │
└─────────────────┴─────────────────┴─────────────────┘
```

---

## Gap Analysis: SPECIFICATION.md vs Implementation

### Layer 1: Agent Manifest (steward.json)

| Feature | Spec Status | Schema Status | Code Status | Notes |
|---------|-------------|---------------|-------------|-------|
| agent.id | ✅ Defined | ✅ Implemented | ✅ Works | |
| agent.name | ✅ Defined | ✅ Implemented | ✅ Works | |
| agent.version | ✅ Defined | ✅ Implemented | ✅ Works | |
| agent.domain | ✅ Defined | ✅ Implemented | ✅ Works | |
| capabilities | ✅ Defined | ✅ Implemented | ✅ Works | |
| governance | ✅ Defined | ✅ Implemented | ✅ Works | |
| credentials | ✅ Defined | ❌ Missing | ❌ Missing | mandate, constraints, prime_directive |
| runtime | ✅ Defined | ❌ Missing | ❌ Missing | introspection_endpoint, state_query |

### Layer 1.5: User & Team Context (NEW)

| Feature | Spec Status | Schema Status | Code Status | Notes |
|---------|-------------|---------------|-------------|-------|
| default_user | ✅ Defined | ❌ Missing | ❌ Missing | workflow_style, verbosity, communication |
| user preferences | ✅ Defined | ❌ Missing | ❌ Missing | Multi-user support |
| team context | ✅ Defined | ❌ Missing | ❌ Missing | development_style, quality_gates |
| boot modes | ✅ Defined | ❌ Missing | ❌ Missing | --user, --team, --auto |

### Layer 1.6: Cognitive Policy (NEW in v1.1.0)

| Feature | Spec Status | Schema Status | Code Status | Notes |
|---------|-------------|---------------|-------------|-------|
| model_preferences | ✅ Defined | ❌ Missing | ❌ Missing | reasoning, efficiency, creative, fallback |
| economic_constraints | ✅ Defined | ❌ Missing | ❌ Missing | max_cost_per_run, max_daily_budget |
| provider_priority | ✅ Defined | ❌ Missing | ❌ Missing | OpenRouter, Anthropic, Google order |

### Layer 2: Registry

| Feature | Spec Status | Code Status | Notes |
|---------|-------------|-------------|-------|
| Agent Index | ✅ Defined | ⚠️ Partial | AgentLoader exists, no central registry |
| Version Store | ✅ Defined | ❌ Missing | |
| Reputation System | ✅ Defined | ❌ Missing | Trust scores not implemented |
| Audit Logs | ✅ Defined | ⚠️ Partial | Ledger exists but not agent-specific |

### Layer 3: Verification

| Feature | Spec Status | Code Status | Notes |
|---------|-------------|-------------|-------|
| Cryptographic signing | ✅ Defined | ✅ Works | constitution.py, ECDSA |
| Capability attestation | ✅ Defined | ⚠️ Partial | Hash verification exists |
| Trust chain | ✅ Defined | ❌ Missing | |

---

## Critical Missing Pieces for System Prompt

The hardcoded system prompt in `boot_sequence.py` exists because:

1. **No cognitive_policy in schema** - Can't configure LLM behavior
2. **No user_context in schema** - Can't personalize prompts
3. **No phoenix section for steward** - Can't load config like kernel/city/quality
4. **No PromptContext resolvers** - Can't dynamically inject

### Current Flow (Broken)
```
boot_sequence.py
    └── _get_system_prompt()  ← HARDCODED STRING (70 lines)
```

### Target Flow (Fractal)
```
config/steward.yaml           ← User writes
    │
vibe_core/phoenix/sections/steward.py  ← Section loads
    │
PhoenixConfig.steward         ← Runtime access
    │
vibe_core/steward/schema/manifest.schema.json  ← Extended with 1.5/1.6
    │
PromptContext resolvers       ← Dynamic injection
    │
boot_sequence.py              ← Uses resolvers, not hardcode
    │
STEWARD.md                    ← Auto-generated from config (hash valid)
```

---

## Implementation Plan

### Phase 1: Extend Schema (manifest.schema.json)

Add to `vibe_core/steward/schema/manifest.schema.json`:

```json
{
  "user_context": {
    "type": "object",
    "properties": {
      "default_user": { ... },
      "users": { ... },
      "team": { ... }
    }
  },
  "cognitive_policy": {
    "type": "object",
    "properties": {
      "model_preferences": { ... },
      "economic_constraints": { ... }
    }
  }
}
```

### Phase 2: Create Phoenix Section

New file: `vibe_core/phoenix/sections/steward.py`

```python
@dataclass
class StewardConfig:
    section_id = "steward"
    source_file = "steward.yaml"

    user_context: UserContext
    cognitive_policy: CognitivePolicy
    behavior: BehaviorConfig  # Genesis Protocol, Anti-Slop rules
```

### Phase 3: Add config/steward.yaml

```yaml
user_context:
  default_user:
    workflow_style: "test_first"
    verbosity: "low"

cognitive_policy:
  model_preferences:
    reasoning: "anthropic/claude-3-opus"
  economic_constraints:
    max_cost_per_run: 1.00

behavior:
  genesis_protocol: true
  anti_slop_rules: true
```

### Phase 4: PromptContext Resolvers

Add to `vibe_core/runtime/prompt_context.py`:

```python
self.register("user_context", self._resolve_user_context)
self.register("cognitive_policy", self._resolve_cognitive_policy)
self.register("behavior_rules", self._resolve_behavior_rules)
```

### Phase 5: Replace Hardcoded System Prompt

In `boot_sequence.py`:

```python
def _get_system_prompt(self, route) -> str:
    resolved = self.prompt_context.resolve([
        'user_context',
        'cognitive_policy',
        'behavior_rules',
        'kernel_capabilities'
    ])
    return self._compose_system_prompt(resolved)
```

### Phase 6: Auto-Generate STEWARD.md

Plugin or ritual that:
1. Reads `config/steward.yaml`
2. Reads `vibe_core/steward/schema/`
3. Generates `STEWARD.md`
4. Signs with ECDSA

---

## Test Deadlock Hypothesis

The infinite test loop may be caused by:

1. **Circular dependency** in boot sequence trying to load config that doesn't exist
2. **PromptContext resolvers** waiting for kernel that's waiting for resolvers
3. **Missing steward config** causing fallback loops

**Investigation path:**
1. Check which test hangs
2. Add timeout/logging to boot sequence
3. Check if missing config causes infinite retry

---

## Open Questions

1. Should `config/steward.yaml` be the SINGLE SOURCE OF TRUTH?
2. How does `STEWARD.md` relate to `steward.json`? Both needed?
3. Hash verification: Sign the config or the generated output?
4. Multi-user: Per-project or global config?

---

## References

- `steward/SPECIFICATION.md` - Vision document (may be stale)
- `steward/templates/STEWARD_TEMPLATE.md` - Full template with all levels
- `vibe_core/steward/schema/manifest.schema.json` - Current schema
- `vibe_core/phoenix/sections/kernel.py` - Pattern to follow
- `docs/architecture/STEWARD_PROTOCOL.md` - Trinity architecture

---

**Last Updated:** 2025-12-05
**Status:** GAP IDENTIFIED - Ready for implementation
