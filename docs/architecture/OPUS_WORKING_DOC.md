# OPUS Working Document - Fighting Non-Persistence

> **PURPOSE:** This document is my working memory. I MUST read this before EVERY action.
> **PROBLEM:** I keep forgetting, making the same mistakes, treating symptoms not causes.
> **METHOD:** Iterative. Read code → Update this doc → Verify with code → Repeat.

---

## ⚠️ CRITICAL REMINDERS (READ FIRST)

1. **PROMPT IS A SYMPTOM, PROTOCOL IS THE CAUSE**
   - I fixed prompts but ignored the STEWARD Protocol structure
   - The fractal pattern means: if Protocol is wrong, everything downstream is wrong

2. **READ MORE, WRITE LESS**
   - This project needs understanding, not code generation
   - Follow the plugin trails from kernel outward

3. **TESTS TIMING OUT ≠ TESTS PASSING**
   - I lied to myself saying tests pass when they just timed out
   - Must verify with actual test runs, not assumptions

4. **ITERATE OVER THIS DOCUMENT**
   - Each session: Read this → Check code → Update gaps → Verify
   - Don't claim victory until code verification passes

---

## THE FRACTAL PATTERN (Swastika Metaphor)

```
                    KERNEL (center)
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    PLUGINS ────────── KERNEL ────────── AGENTS
         │               │               │
         └───────────────┼───────────────┘
                         │
                    SECTIONS
                         │
              (each arm extends fractally)
```

**Follow the trails:**
- Kernel → Plugins → What do plugins load?
- Kernel → Sections → How do sections work?
- Kernel → Agents → How are agents defined?

Each level has the SAME PATTERN. If I understand one, I understand all.

---

## ITERATION LOG

### Iteration 1: Prompt Templates (INCOMPLETE)

**What I did:**
- Added templates to steward.yaml
- Created resolve_template() method
- Removed hardcoded strings from boot_sequence.py and prompt_composer.py

**What I missed:**
- [ ] STEWARD Protocol itself is more than prompts
- [ ] Capabilities section not implemented
- [ ] Quality guarantees not implemented
- [ ] Verification/attestation not implemented
- [ ] The TEMPLATE structure should match steward/SPECIFICATION.md

**Code to verify:**
```bash
# Check if StewardConfig has all Protocol sections
python3 -c "from vibe_core.phoenix.sections.steward import StewardConfig; print(dir(StewardConfig))"
```

### Iteration 2: TODO

**Read these files to understand Protocol:**
- [ ] `steward/SPECIFICATION.md` - What MUST be in the Protocol
- [ ] `steward/protocol.py` - Existing Protocol implementation
- [ ] `steward/loader.py` - How Protocol is loaded
- [ ] `steward/constitution.py` - Constitutional rules

**Questions to answer:**
- What sections does SPECIFICATION.md require?
- Does StewardConfig match the specification?
- Where is the gap?

---

## GAP ANALYSIS: SPECIFICATION vs IMPLEMENTATION

| Spec Section | In steward.yaml? | In StewardConfig? | Verified? |
|--------------|------------------|-------------------|-----------|
| Identity | ✅ Added | ✅ Added | ❌ |
| Capabilities | ❌ | ❌ | ❌ |
| Behavior | ✅ | ✅ | ❌ |
| User Context (1.5) | ✅ | ✅ | ❌ |
| Cognitive Policy (1.6) | ✅ | ✅ | ❌ |
| Quality Guarantees | ❌ | ❌ | ❌ |
| Verification | ❌ | ❌ | ❌ |
| Attestation | ❌ | ❌ | ❌ |

---

## CODE VERIFICATION CHECKLIST

Before claiming anything works, run:

```bash
# 1. Check config loads without error
python3 -c "from vibe_core.phoenix.config import PhoenixConfig; p = PhoenixConfig.from_files(); print('OK')"

# 2. Check steward section has all fields
python3 -c "
from vibe_core.phoenix.config import PhoenixConfig
p = PhoenixConfig.from_files()
s = p.steward
print(f'Identity: {s.identity.name}')
print(f'Templates: {len(s.templates.system_prompt_template)} chars')
print(f'Behavior: {s.behavior.genesis_protocol}')
"

# 3. Check template resolution
python3 -c "
from vibe_core.phoenix.config import PhoenixConfig
p = PhoenixConfig.from_files()
result = p.steward.resolve_template('system_prompt', {'behavior_rules': 'test', 'user_context': 'test', 'team_context': 'test', 'cognitive_policy': 'test', 'kernel_status': 'ok', 'kernel_agents_count': '0'})
print(f'Resolved: {len(result)} chars')
"

# 4. Run actual tests (with timeout awareness)
timeout 30 python -m pytest tests/integration/test_system_boot.py -v 2>&1 | tail -20
```

---

## FILES MODIFIED (Track Changes)

| File | Change | Verified? |
|------|--------|-----------|
| config/steward.yaml | Added identity, templates | ❌ |
| vibe_core/phoenix/sections/steward.py | Added AgentIdentity, PromptTemplates, resolve_template() | ❌ |
| vibe_core/phoenix/sections/__init__.py | Added exports | ❌ |
| vibe_core/runtime/boot_sequence.py | Use config template | ❌ |
| vibe_core/runtime/prompt_composer.py | Use config template | ❌ |

---

## NEXT ACTIONS (Priority Order)

1. [ ] Commit current changes (even if incomplete)
2. [ ] Read steward/SPECIFICATION.md to understand full Protocol
3. [ ] Read steward/protocol.py to see existing implementation
4. [ ] Update GAP ANALYSIS table
5. [ ] Plan what's actually needed vs what I added

---

## ANTI-PATTERNS I KEEP DOING

❌ Treating symptoms (prompt) instead of causes (protocol)
❌ Claiming tests pass when they timeout
❌ Writing code before reading existing code
❌ Adding new things instead of using existing infrastructure
❌ Not iterating over this document
❌ Declaring victory prematurely

---

*Last updated: Iteration 1 - Prompt templates added but Protocol not verified*
*Status: INCOMPLETE - Must iterate*
