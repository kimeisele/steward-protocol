# OPUS-085: VEDIC EXTENSIONS - Karma, Bhakti, Triguna

**Scope:** Complete Vedic Governance Extensions - Real Enforcement with Grace  
**Philosophy:** The harness IS the truth. A system that can forgive is more resilient.  
**Goal:** Living governance that judges HOW you act (Guna), not just WHAT happened (Karma).

---

## The Harness

This document contains NO manual status. The `@HARNESS` below is the ONLY source of truth.

<!-- @HARNESS
files:
  # === CORE VEDIC GOVERNANCE ===
  - path: vibe_core/plugins/vedic_governance/plugin_main.py
    required: true
  - path: vibe_core/plugins/vedic_governance/ashrama.py
    required: true
  - path: vibe_core/plugins/vedic_governance/varna.py
    required: true
  - path: vibe_core/plugins/vedic_governance/state_manager.py
    required: true

  # === OPUS ASSISTANT CIRCUITS ===
  - path: vibe_core/plugins/opus_assistant/circuits/karma_consequence.yaml
    required: true
  - path: vibe_core/plugins/opus_assistant/circuits/bhakti_practice.yaml
    required: true

  # === INTEGRATION ===
  - path: vibe_core/plugins/opus_assistant/events/kernel_tick.py
    required: true

wiring:
  # === OPUS-084: KARMA ENFORCEMENT ===
  # Promotion/Demotion API
  - pattern: "def demote_agent"
    in: vibe_core/plugins/vedic_governance/plugin_main.py
  - pattern: "def promote_agent"
    in: vibe_core/plugins/vedic_governance/plugin_main.py

  # === OPUS-085: BHAKTI GRACE ===
  # Bhakti balance management
  - pattern: "def get_bhakti_balance"
    in: vibe_core/plugins/vedic_governance/plugin_main.py
  - pattern: "def add_bhakti"
    in: vibe_core/plugins/vedic_governance/plugin_main.py
  - pattern: "def consume_bhakti"
    in: vibe_core/plugins/vedic_governance/plugin_main.py
  - pattern: "def should_grant_grace"
    in: vibe_core/plugins/vedic_governance/plugin_main.py
  - pattern: "def decay_bhakti"
    in: vibe_core/plugins/vedic_governance/plugin_main.py

  # Grace check in karma circuit
  - pattern: "check_grace_eligibility"
    in: vibe_core/plugins/opus_assistant/circuits/karma_consequence.yaml
  - pattern: "COMPLETE_GRACED"
    in: vibe_core/plugins/opus_assistant/circuits/karma_consequence.yaml

  # === TRIGUNA: AGENT HEALTH ===
  # Guna classification
  - pattern: "def determine_guna"
    in: vibe_core/plugins/vedic_governance/plugin_main.py
  - pattern: "def _is_tamasic"
    in: vibe_core/plugins/vedic_governance/plugin_main.py
  - pattern: "def _is_rajasic"
    in: vibe_core/plugins/vedic_governance/plugin_main.py

  # Guna restrictions in on_task_pre_assign
  - pattern: "TAMASIC.*cannot perform"
    in: vibe_core/plugins/vedic_governance/plugin_main.py

  # === STATE PERSISTENCE (AKSHAYA PATRA) ===
  - pattern: "class VedicStateManager"
    in: vibe_core/plugins/vedic_governance/state_manager.py
  - pattern: "_flush_to_disk"
    in: vibe_core/plugins/vedic_governance/state_manager.py

tests:
  # === ALL VEDIC GOVERNANCE TESTS ===
  - tests/integration/test_vedic_enforcement.py
  - tests/integration/test_bhakti_grace.py
  - tests/integration/test_triguna.py

semantic:
  # === API EXPORTS ===
  - type: module_exports
    name: vedic_public_api
    module: vibe_core.plugins.vedic_governance.plugin_main
    exports:
      - demote_agent
      - promote_agent
      - get_bhakti_balance
      - add_bhakti
      - consume_bhakti
      - should_grant_grace
      - determine_guna
      - get_agent_guna

  - type: module_exports
    name: vedic_state_manager
    module: vibe_core.plugins.vedic_governance.state_manager
    exports:
      - VedicStateManager

  # === CORE METHODS ===
  - type: method_exists
    name: grace_check
    in: vibe_core/plugins/vedic_governance/plugin_main.py
    class: VedicGovernancePlugin
    method: should_grant_grace

  - type: method_exists
    name: guna_classifier
    in: vibe_core/plugins/vedic_governance/plugin_main.py
    class: VedicGovernancePlugin
    method: determine_guna

  # === PERSISTENCE CHECKS ===
  - type: file_writable
    name: vedic_state_writable
    path: .vibe/state/
    rationale: "Vedic state needs persistence"
-->

---

## Fire Commands

```bash
# Verify harness (the ONLY truth)
steward verify 085

# Run all Vedic tests
python -m pytest tests/integration/test_vedic_enforcement.py tests/integration/test_bhakti_grace.py tests/integration/test_triguna.py -v

# Check agent Guna
python -c "from vibe_core.plugins.vedic_governance.plugin_main import VedicGovernancePlugin; g = VedicGovernancePlugin(); print(g.get_agent_guna('opus_assistant'))"
```

---

## The Vedic Stack

```
┌─────────────────────────────────────────────────────────────┐
│  TRIGUNA (Guna)      - HOW you act                          │
│  tamas/rajas/sattva → dynamic task restrictions             │
├─────────────────────────────────────────────────────────────┤
│  SAMSARA (Bhakti)    - Grace buffer                         │
│  60 Bhakti → saves from demotion (costs 50)                 │
├─────────────────────────────────────────────────────────────┤
│  ASHRAMA (Stage)     - WHAT you can do                      │
│  BRAHMACHARI → GRIHASTHA → VANAPRASTHA → SANNYASA          │
├─────────────────────────────────────────────────────────────┤
│  KARMA (Score)       - Tracking + Ledger                    │
├─────────────────────────────────────────────────────────────┤
│  AKSHAYA PATRA       - Persistent State (JSON, Atomic)      │
│  VedicStateManager → .vibe/state/vedic_dharma.json         │
└─────────────────────────────────────────────────────────────┘
```

---

## Features

### 1. Karma Enforcement (OPUS-084)
- `demote_agent()` / `promote_agent()` formal API
- Wired to `kernel_tick.py` via circuits

### 2. Bhakti Grace (Samsara Loop)
- Bhakti accumulates from devotional practices
- Grace costs Bhakti (not free forgiveness)
- 1% decay per maintenance pulse (use it or lose it)

| Bhakti Required | Saves From | Cost |
|-----------------|------------|------|
| 30 | Warning | 15 |
| 60 | Demotion | 50 |
| 100 | Critical | 80 |

### 3. Triguna Classification
- **Tamas**: High error rate → self-check tasks only
- **Rajas**: High churn → no critical writes
- **Sattva**: Stable flow → full access

### 4. Akshaya Patra (Persistent State)
- Atomic writes (tmp → rename)
- Graceful degradation (corrupt file → safe default)
- Self-healing (missing file → create)

---

*"संसार - The modes of material nature bind the eternal soul."*
