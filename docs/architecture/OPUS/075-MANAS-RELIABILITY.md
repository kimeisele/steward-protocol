# OPUS-075: MANAS FORTRESS HARNESS

**Scope:** Complete MANAS Reliability Gate
**Philosophy:** The harness IS the truth. No manual status. Dynamic verification.

---

## The Harness

This document contains NO manual status reporting. The `@HARNESS` below is the ONLY source of truth. Run it to know the state.

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
  # === CORTEX MODULES (all 11) ===
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
  - path: vibe_core/cli/unified_cli.py
    required: true
  # === GITHUB ACTIONS ===
  - path: .github/workflows/heartbeat.yml
    required: true

wiring:
  # === BATCH MODE ===
  # Heartbeat instantiates CognitiveKernel directly
  - pattern: "CognitiveKernel\\("
    in: scripts/heartbeat.py
  # Heartbeat calls manas.think()
  - pattern: "self\\.manas\\.think"
    in: scripts/heartbeat.py
  # VAJRA Ledger injected
  - pattern: "inject_ledger"
    in: scripts/heartbeat.py
  - pattern: "def inject_ledger"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py

  # === CLI MODE (headless) ===
  # CLI uses JnanaHandler directly (NOT socket!)
  - pattern: "JnanaHandler"
    in: vibe_core/cli/unified_cli.py
  # CLI does NOT use chat_sync (socket-based - BROKEN)
  # If this pattern is found, CLI is still broken!

  # === MEMORY FEEDBACK ===
  - pattern: "RECENT FAILURES"
    in: vibe_core/plugins/opus_assistant/manas/cortex/jnana.py

  # === CARTRIDGE DELEGATION ===
  - pattern: "_delegate_think"
    in: vibe_core/cartridges/system/manas/cartridge_main.py

  # === VEDA PIPELINE ===
  - pattern: "VedaPipeline"
    in: vibe_core/plugins/opus_assistant/manas/cortex/veda.py

  # === INTENT ROUTING ===
  - pattern: "def route"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py

  # === GITHUB ACTIONS ===
  - pattern: "cron.*15"
    in: .github/workflows/heartbeat.yml

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
  # === API EXPORTS ===
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

  # === CORE METHODS ===
  - type: method_exists
    name: cognitive_kernel_think
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    class: CognitiveKernel
    method: think

  - type: method_exists
    name: jnana_handler
    in: vibe_core/plugins/opus_assistant/manas/cortex/jnana.py
    class: JnanaHandler
    method: handle

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

  # === HOLISTIC RUNTIME CHECKS ===
  - type: execution_mode
    name: not_in_simulation
    expected: live_fire
    rationale: "MANAS must be in live_fire mode to actually DO work"

  - type: file_writable
    name: manas_can_write
    path: .vibe/state/
    rationale: "MANAS needs write access to persist state"

  - type: ledger_healthy
    name: vajra_ledger_intact
    min_events: 100
    rationale: "VAJRA should have significant history"

  # === ANTI-SPAGHETTI CHECKS ===
  - type: state_sync
    name: opus_state_synced
    source: config/providers.yaml
    source_key: live_fire_enabled
    target: vibe_core/plugins/opus_assistant/.opus_state/session.json
    target_key: simulation_mode
    inverted: true
    rationale: "opus_assistant state must reflect actual config (inverted: live_fire=true means simulation_mode=false)"
-->

---

## Fire Commands

```bash
# Verify harness (the ONLY truth)
steward verify 075

# Run all MANAS tests
python -m pytest tests/manas/ -v --tb=short

# Batch mode pulse
python scripts/heartbeat.py

# CLI mode (headless)
steward chat "status"
```

---

## Architecture Notes

**Why Headless?**
- Socket daemon (`samvada.sock`) requires a running process
- Headless mode instantiates `JnanaHandler` directly
- Both batch (`heartbeat.py`) and CLI (`steward chat`) use headless

**Why No Manual Status?**
- Manual status lies the moment code changes
- The harness verifies dynamically
- If harness passes, system works. Period.

---

*"The map is not the territory. The harness is."*
