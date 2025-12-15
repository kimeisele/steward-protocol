# OPUS-075: MANAS FORTRESS HARNESS

**Status:** ARMED & READY
**Author:** Steward Protocol
**Date:** 2025-12-15
**Scope:** Complete MANAS Reliability Gate

---

## Purpose

NO NEW CODE. ONLY VERIFICATION.

Das Arsenal existiert bereits. 20 Test-Suites, 17 Verification Scripts.
Dieser Harness ist das GATE - wenn er passed, ist MANAS production-ready.

---

## Verification Harness

<!-- @HARNESS
files:
  # === CORE MANAS ===
  - path: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/memory_store.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/intent_generator.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/intent_router.py
    required: true
  # === CORTEX MODULES (16) ===
  - path: vibe_core/plugins/opus_assistant/manas/cortex/jnana.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/dharma.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/veda.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/kriya.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/silpa.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/mukha.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/akasha.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/samvada.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/sankalpa.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/sutra.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/mandala.py
    required: true
  # === INTEGRATION ===
  - path: scripts/heartbeat.py
    required: true
  - path: vibe_core/cartridges/system/manas/cartridge_main.py
    required: true
  - path: vibe_core/cartridges/system/manas/steward.json
    required: true

wiring:
  # Heartbeat → MANAS
  - pattern: "self\\.manas\\.think"
    in: scripts/heartbeat.py
  # VAJRA Ledger Binding
  - pattern: "inject_ledger"
    in: scripts/heartbeat.py
  - pattern: "def inject_ledger"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
  # Memory Feedback Loop
  - pattern: "RECENT FAILURES"
    in: vibe_core/plugins/opus_assistant/manas/cortex/jnana.py
  # Cartridge Delegation
  - pattern: "_delegate_think"
    in: vibe_core/cartridges/system/manas/cartridge_main.py
  # VEDA Pipeline
  - pattern: "VedaPipeline"
    in: vibe_core/plugins/opus_assistant/manas/cortex/veda.py
  # Intent Routing
  - pattern: "def route"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py

tests:
  # === ALL 20 MANAS TEST SUITES ===
  - tests/manas/test_cognitive_kernel.py
  - tests/manas/test_intent_generator.py
  - tests/manas/test_memory_store.py
  - tests/manas/test_veda.py
  - tests/manas/test_dharma.py
  - tests/manas/test_jnana.py
  - tests/manas/test_kriya.py
  - tests/manas/test_silpa.py
  - tests/manas/test_mukha.py
  - tests/manas/test_akasha.py
  - tests/manas/test_samvada.py
  - tests/manas/test_sankalpa.py
  - tests/manas/test_sutra.py
  - tests/manas/test_mandala.py
  - tests/manas/test_shell_cortex.py
  - tests/manas/test_live_fire.py
  - tests/manas/test_chat_command.py
  - tests/manas/test_ci_monitor_analyzer.py
  - tests/manas/test_contract_analyzer.py
  - tests/manas/test_semantic_analyzer.py

semantic:
  # API Exports - Fast check
  - type: module_exports
    name: manas_public_api
    module: vibe_core.plugins.opus_assistant.manas
    exports:
      - CognitiveKernel
      - ManasConfig
      - Intent
      - IntentGenerator
      - MemoryStore
      - MemoryEntry
      - IntentPriority
  # Core class exists and is callable
  - type: method_exists
    name: cognitive_kernel_think
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    class: CognitiveKernel
    method: think
  - type: method_exists
    name: intent_generator_generate
    in: vibe_core/plugins/opus_assistant/manas/intent_generator.py
    class: IntentGenerator
    method: generate_intents
  - type: method_exists
    name: memory_store_get
    in: vibe_core/plugins/opus_assistant/manas/memory_store.py
    class: MemoryStore
    method: get_success_rate
  - type: method_exists
    name: intent_router_route
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py
    class: IntentRouter
    method: route
-->

---

## Status

| Level | Check | Count | Status |
|-------|-------|-------|--------|
| L1 | Files exist | 14 | ✅ |
| L2 | Wiring connected | 7 | ✅ |
| L3 | Test suites exist | 20 | ✅ |
| L4 | API exports | 7 | ✅ |
| L5 | pytest_passes | 6 | 🔥 FIRE |

Run: `python -m pytest tests/manas/ -v`

---

## Implementation

Dieser Harness referenziert das **existierende Arsenal**:

**Test Artillery (20 Suites):**
- `test_cognitive_kernel.py` - The Brain
- `test_intent_generator.py` - The Will
- `test_memory_store.py` - The Memory
- `test_veda.py` - Four-Fold Pipeline
- `test_dharma.py` - Constitutional Law
- `test_jnana.py` - Conversation Handler
- `test_kriya.py` - Action Execution
- `test_silpa.py` - Self-Healing
- ... und 12 weitere

**Verification Scripts:**
- `verify_system_watertight.py`
- `verify_ledger_integrity.py`
- `verify_security.py`

---

## Fire Command

```bash
# TOTAL RECALL - Fire all MANAS tests
python -m pytest tests/manas/ -v --tb=short

# Watertight seal
python scripts/verification/verify_system_watertight.py

# Ledger integrity (VAJRA)
python scripts/verification/verify_ledger_integrity.py
```

---

*"The weapon is built. The safety is off."*
