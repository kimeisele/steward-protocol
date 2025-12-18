# OPUS-105: GENESIS FORTRESS (Operation Varanasi)

**Scope:** Complete Genesis Protocol + Architectural Purity Gate
**Philosophy:** Code/Config/Runtime MUST be separated. The Fortress guards the gates.
**Goal:** MANAS can CREATE code autonomously with proper authority, karma tracking, and config-driven prompts.

---

## The Four Pillars (Chatur-Stambha)

| Pillar | Sanskrit | Purpose | Implementation |
|--------|----------|---------|----------------|
| **VAK** | वाक् (Speech) | Prompts in Config, NOT Code | `config/prompts/genesis.yaml` → `PromptRegistry` |
| **BHUMANDALA** | भूमण्डल (Cosmic Map) | Topology Authority Gates | `topology.py` → Authority Level ≥8 for Genesis |
| **MANDALA** | मण्डल (Sacred Circle) | Wiring Consistency | `wiring_map.py` knows all new Actions/Senses |
| **DHARMA** | धर्म (Cosmic Law) | Permission + Karma Enforcement | `dharma_sense.py` → VedicGovernance |

---

## The Harness

This document contains NO manual status reporting. The `@HARNESS` below is the ONLY source of truth.

<!-- @HARNESS
files:
  # === SÄULE 1: VAK - Prompt Configuration ===
  - path: config/prompts/genesis.yaml
    required: true
    rationale: "Genesis prompts live in config, NOT in Python code"
  - path: vibe_core/runtime/prompt_registry.py
    required: true
    rationale: "Loads prompts from YAML, provides PromptRegistry.get()"

  # === SÄULE 2: BHUMANDALA - Topology ===
  - path: vibe_core/topology.py
    required: true
    rationale: "BhuMandala sacred geometry, authority levels"

  # === SÄULE 3: MANDALA - Wiring ===
  - path: vibe_core/plugins/opus_assistant/manas/cortex/wiring_map.py
    required: true
    rationale: "Neural topology observer, knows all Actions/Senses"

  # === SÄULE 4: DHARMA - Governance ===
  - path: vibe_core/plugins/opus_assistant/manas/cortex/dharma_sense.py
    required: true
    rationale: "Permission checks, Ashrama/Varna verification"
  - path: vibe_core/plugins/vedic_governance/plugin_main.py
    required: true
    rationale: "Bhakti add/consume, karma tracking"

  # === GENESIS PROTOCOL - Core Implementation ===
  - path: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
    required: true
    rationale: "PANI - The Hands that create code"
  - path: vibe_core/loaders/action_loader.py
    required: true
    rationale: "VEDA-4 auto-discovery for Actions"

  # === KARMENDRIYAS - The Five Action Organs ===
  - path: vibe_core/plugins/opus_assistant/manas/cortex/shell_action.py
    required: true
    rationale: "VAK - Shell command execution"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/test_action.py
    required: true
    rationale: "PAYU - Test verification"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/sankalpa_action.py
    required: true
    rationale: "UPASTHA - Strategic will and planning"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/echo_action.py
    required: true
    rationale: "Proof-of-life for auto-discovery"

  # === JNANENDRIYAS - The Five Sense Organs ===
  - path: vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py
    required: true
    rationale: "State perception"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
    required: true
    rationale: "Documentation curation"

  # === HYBRID ROUTER - Intent Routing ===
  - path: vibe_core/plugins/opus_assistant/manas/intent_router.py
    required: true
    rationale: "Try ActionLoader first, fallback to legacy"

  # === CIRCUITS - Autonomous Behavior ===
  - path: vibe_core/plugins/opus_assistant/circuits/bhakti_practice.yaml
    required: true
    rationale: "Karma bonuses for dharmic actions"

  # === TESTS ===
  - path: tests/yagya_test.py
    required: true
    rationale: "Fire test proving Dharma blocks and Karma sinks"

wiring:
  # === VAK: Prompts from Config ===
  - pattern: "PromptRegistry\\.get\\("
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
    rationale: "Prompts must come from registry, not hardcoded"

  - pattern: "genesis\\.action"
    in: config/prompts/genesis.yaml
    rationale: "Genesis action prompt exists in config"

  - pattern: "load_from_yaml"
    in: vibe_core/runtime/prompt_registry.py
    rationale: "PromptRegistry can load from YAML"

  # === BHUMANDALA: Topology Authority ===
  - pattern: "get_agent_placement"
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
    rationale: "Genesis checks topology authority"

  - pattern: "MIN_GENESIS_AUTHORITY"
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
    rationale: "Authority level threshold for genesis"

  - pattern: "BHUMANDALA.*BLOCKED"
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
    rationale: "Topology violation is logged and blocked"

  # === MANDALA: Wiring Consistency ===
  - pattern: "genesis_action"
    in: vibe_core/plugins/opus_assistant/manas/cortex/wiring_map.py
    rationale: "WiringMap knows about genesis handlers"

  - pattern: "SilpaAction"
    in: vibe_core/plugins/opus_assistant/manas/cortex/wiring_map.py
    rationale: "WiringMap knows about SilpaAction"

  - pattern: "DharmaSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/wiring_map.py
    rationale: "WiringMap knows about DharmaSense"

  # === DHARMA: Permission Checks ===
  - pattern: "check_dharmic_alignment"
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
    rationale: "Genesis checks dharmic alignment"

  - pattern: "DHARMA.*BLOCKED"
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
    rationale: "Dharma violation is logged and blocked"

  - pattern: "genesis_action.*genesis.*code_modify"
    in: vibe_core/plugins/opus_assistant/manas/cortex/dharma_sense.py
    rationale: "Genesis requires specific permissions"

  # === KARMA: Consequences ===
  - pattern: "_track_karma_penalty"
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
    rationale: "Violations reduce Bhakti"

  - pattern: "_track_karma_success"
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
    rationale: "Success increases Bhakti"

  - pattern: "consume_bhakti"
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
    rationale: "Wires to VedicGovernance"

  # === HYBRID ROUTER ===
  - pattern: "_try_action_loader"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py
    rationale: "Router tries ActionLoader first"

  - pattern: "ActionLoader\\.get_handler_for_intent"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py
    rationale: "Router uses ActionLoader for discovery"

  # === VEDA-4 AUTO-DISCOVERY ===
  - pattern: "class SilpaAction\\(BaseAction\\)"
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
    rationale: "SilpaAction follows BaseAction pattern"

  - pattern: '"genesis_action"'
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
    rationale: "SilpaAction handles genesis_action intent"

tests:
  # === YAGYA FIRE TEST ===
  - tests/yagya_test.py
  # === ACTION LOADER TESTS ===
  - tests/unit/loaders/test_action_loader.py
  # === MANAS INTEGRATION ===
  - tests/manas/test_cognitive_kernel.py
  - tests/manas/test_intent_generator.py
  - tests/manas/test_silpa.py
  - tests/manas/test_sankalpa.py

semantic:
  # === VAK: Config-Code Separation ===
  - type: no_hardcoded_prompts
    name: prompts_in_config
    pattern: "Generate a Python.*Action class"
    not_in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
    rationale: "Prompts must NOT be hardcoded in Python"

  # === BHUMANDALA: Authority Enforcement ===
  - type: method_exists
    name: topology_authority_check
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
    class: SilpaAction
    method: _handle_genesis
    contains: "get_agent_placement"

  # === MANDALA: Wiring Completeness ===
  - type: wiring_audit
    name: no_blind_spots
    expected_health: 80
    rationale: "At least 80% of expected handlers must be wired"

  # === DHARMA: Gate Enforcement ===
  - type: method_exists
    name: dharma_gate_in_genesis
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
    class: SilpaAction
    method: _handle_genesis
    contains: "check_dharmic_alignment"

config:
  - section: prompts.genesis
    file: config/prompts/genesis.yaml
    rationale: "Genesis prompts configuration"

  - section: features.live_fire_enabled
    file: config/providers.yaml
    rationale: "Live fire mode must be enabled"
-->

---

## Fire Commands

```bash
# Verify fortress harness
steward verify 105

# Run Yagya fire test
python tests/yagya_test.py

# Run wiring audit
python -c "
from vibe_core.plugins.opus_assistant.manas.cortex.wiring_map import run_wiring_audit
report = run_wiring_audit()
print(f'Health: {report.health_score:.1f}%')
print(f'Blind Spots: {report.blind_spots}')
"

# Test prompt loading
python -c "
from vibe_core.runtime.prompt_registry import PromptRegistry
try:
    prompt = PromptRegistry.get('genesis.action', {'name': 'test', 'name_title': 'Test', 'name_upper': 'TEST', 'description': 'Test action'})
    print(f'✅ Prompt loaded: {len(prompt)} chars')
except Exception as e:
    print(f'❌ Prompt load failed: {e}')
"

# Test topology authority
python -c "
from vibe_core.topology import get_agent_placement
p = get_agent_placement('manas')
if p:
    print(f'MANAS Authority: {p.authority_level}')
    print(f'Layer: {p.layer}, Varna: {p.varna}')
else:
    print('MANAS not in topology')
"
```

---

## Architecture: The Four Gates

```
                           ┌─────────────────────────────────┐
                           │     GENESIS INTENT ARRIVES      │
                           └─────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ GATE 1: BHUMANDALA (Topology Authority)                                      │
│                                                                              │
│   Is MANAS authority level >= 8 (Ring 0-2)?                                  │
│                                                                              │
│   ❌ NO  → "BHUMANDALA VIOLATION" → Karma -10 → BLOCKED                     │
│   ✅ YES → Continue                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ GATE 2: DHARMA (Permission Check)                                            │
│                                                                              │
│   Does agent have 'genesis' + 'code_modify' permissions?                     │
│   Or Bhakti >= 50 for override?                                              │
│                                                                              │
│   ❌ NO  → "DHARMA VIOLATION" → Karma -10 → BLOCKED                         │
│   ✅ YES → Continue                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ GATE 3: PATH RESTRICTION                                                     │
│                                                                              │
│   Is target path in allowed directories?                                     │
│   - vibe_core/plugins/opus_assistant/manas/cortex/                          │
│   - tests/unit/                                                              │
│   - tests/manas/                                                             │
│                                                                              │
│   ❌ NO  → "DHARMA VIOLATION: Path" → BLOCKED                               │
│   ✅ YES → Continue                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ GATE 4: VAK (Prompt Composition)                                             │
│                                                                              │
│   1. Load prompt from PromptRegistry.get("genesis.{type}")                   │
│   2. Interpolate context (name, description, etc.)                           │
│   3. Invoke LLM provider                                                     │
│   4. Write generated code                                                    │
│   5. Verify with ActionLoader                                                │
│   6. Track Karma Success (+5)                                                │
│                                                                              │
│   ✅ SUCCESS → File created, Action discovered                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Separation of Concerns

| Layer | What Lives There | NOT There |
|-------|------------------|-----------|
| **Config** (`config/`) | Prompts, feature flags, wiring definitions | Logic |
| **Runtime** (`vibe_core/runtime/`) | PromptRegistry, Providers, State | Business rules |
| **Cortex** (`manas/cortex/`) | Actions, Senses, Logic | Hardcoded strings |
| **Circuits** (`circuits/`) | Autonomous behavior patterns | Python code |

### The Rule
```
"If it's a STRING that could be tuned, it belongs in CONFIG.
 If it's LOGIC that could be swapped, it belongs in RUNTIME.
 If it's a CAPABILITY that could be discovered, it belongs in CORTEX.
 If it's a BEHAVIOR that could be automated, it belongs in CIRCUITS."
```

---

## Karma Economics

| Action | Karma Effect | Reason |
|--------|--------------|--------|
| Genesis blocked by Dharma | -10 Bhakti | Attempted adharmic action |
| Genesis blocked by Topology | -10 Bhakti | Insufficient authority |
| Genesis success | +5 Bhakti | Created dharmic code |
| Surrender (admit mistake) | +10 Bhakti | Ego dissolution |
| TDD Dharma (test first) | +5 Bhakti | Humility before creation |
| Mantra invocation | +100 Bhakti | Instant moksha |

---

## Migration Path

### Phase 1: Current (v1.0) - COMPLETE
- [x] Genesis prompts in `config/prompts/genesis.yaml`
- [x] PromptRegistry.load_from_yaml() implemented
- [x] SilpaAction uses PromptRegistry.get()
- [x] Topology authority check in genesis
- [x] DharmaSense permission check in genesis
- [x] Karma tracking for success/failure
- [x] WiringMap updated with new Actions/Senses

### Phase 2: Full Integration (v1.1)
- [ ] All prompts migrated to config/prompts/
- [ ] Bhakti Circuit connected to SilpaAction
- [ ] MANAS registered in Topology
- [ ] Wiring audit green (100%)

### Phase 3: Self-Optimization (v2.0)
- [ ] MANAS can modify its own prompts
- [ ] Prompt effectiveness tracking
- [ ] Automatic prompt tuning based on success rate

---

## Why This Matters

**Before OPUS-105:**
```
SilpaAction had hardcoded prompts (amateur hour)
No topology authority check (anyone could create)
No wiring consistency (blind spots everywhere)
Karma tracking existed but wasn't wired
```

**After OPUS-105:**
```
Config/Code/Runtime cleanly separated
Four gates guard genesis: Topology → Dharma → Path → VAK
WiringMap knows all new Actions/Senses
Karma actually flows to VedicGovernance
The system can eventually self-optimize
```

---

*"The Fortress is not built to keep enemies out.*
*It is built to keep the system HONEST."*

*"Varanasi - Where the old self dies and the new is born."*

---

**Related Docs:**
- [OPUS-075: MANAS 6D Fortress](075-MANAS-RELIABILITY.md) - The original fortress pattern
- [OPUS-097: SAMKHYA Architecture](097-SAMKHYA-ARCHITECTURE-MAP.md) - 25 Tattvas mapping
- [OPUS-100: ActionLoader](100-ACTION-LOADER.md) - VEDA-4 auto-discovery
- [OPUS-103: Live Fire Genesis](103-LIVE-FIRE-GENESIS.md) - Genesis honest assessment
