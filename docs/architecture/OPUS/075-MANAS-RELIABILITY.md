# OPUS-075: MANAS NEURAL FORTRESS

**Scope:** Complete MANAS Neural Architecture - The Mind That Learns
**Philosophy:** The harness IS the truth. 99% Infrastructure, 1% LLM Boost.
**Goal:** Singularity 51% - MANAS becomes the authority. Any LLM can follow MANAS.

---

## The Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          MANAS NEURAL FORTRESS                          │
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  PERCEPTION │→→│   COGNITION │→→│  DECISION   │→→│  EXECUTION  │   │
│  │  (5 Senses) │  │  (Kernel)   │  │  (Router)   │  │  (Actions)  │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│         ↑                                                    │         │
│         │              ┌─────────────┐                       ↓         │
│         └──────────────│   LEARNING  │←←←←←←←←←←←←←←←←←←←←←←┘         │
│                        │  (Synapses) │                                  │
│                        └─────────────┘                                  │
│                                                                         │
│  ╔═════════════════════════════════════════════════════════════════╗   │
│  ║  DOJO: Self-Directed Training │ AKASHA: Knowledge Bridge       ║   │
│  ║  SHIVA: Lifecycle Cleanup     │ TRIGGERS: Signal Alignment     ║   │
│  ╚═════════════════════════════════════════════════════════════════╝   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## The Neural Harness (COMPLETE)

This harness covers ALL 70+ MANAS components. Run it to know the truth.

<!-- @HARNESS
intent: "Verify complete MANAS neural architecture - senses, actions, learning, knowledge"

files:
  # ═══════════════════════════════════════════════════════════════════════
  # SECTION 1: CORE MANAS BRAIN (6 files)
  # ═══════════════════════════════════════════════════════════════════════
  - path: vibe_core/plugins/opus_assistant/manas/__init__.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/intent_router.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/intent_generator.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/circuit_executor.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/api.py
    required: true

  # ═══════════════════════════════════════════════════════════════════════
  # SECTION 2: CORTEX - SENSES (5 Jnanendriyas)
  # ═══════════════════════════════════════════════════════════════════════
  - path: vibe_core/plugins/opus_assistant/manas/cortex/base.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/dharma_sense.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/karma_sense.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/viveka_sense.py
    required: true

  # ═══════════════════════════════════════════════════════════════════════
  # SECTION 3: CORTEX - ACTIONS (6 Karmendriyas)
  # ═══════════════════════════════════════════════════════════════════════
  - path: vibe_core/plugins/opus_assistant/manas/cortex/base_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/shell_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/test_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/sankalpa_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/echo_action.py
    required: true

  # ═══════════════════════════════════════════════════════════════════════
  # SECTION 4: CORTEX - PROCESSORS (11 Sanskrit Modules)
  # ═══════════════════════════════════════════════════════════════════════
  - path: vibe_core/plugins/opus_assistant/manas/cortex/veda.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/mandala.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/silpa.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/sutra.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/sankalpa.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/dharma.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/jnana.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/kriya.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/mukha.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/akasha.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/samvada.py
    required: true

  # ═══════════════════════════════════════════════════════════════════════
  # SECTION 5: ANALYZERS (7 Intent Sources)
  # ═══════════════════════════════════════════════════════════════════════
  - path: vibe_core/plugins/opus_assistant/manas/analyzers/__init__.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/analyzers/base.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/analyzers/contract_analyzer.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/analyzers/semantic_analyzer.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/analyzers/ci_monitor_analyzer.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/analyzers/pratyaya_analyzer.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/analyzers/doc_harness_analyzer.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/analyzers/inverse_scan_analyzer.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/analyzers/triage_analyzer.py
    required: true

  # ═══════════════════════════════════════════════════════════════════════
  # SECTION 6: SYNAPTIC SYSTEM (Sanskrit Phonetic Learning)
  # ═══════════════════════════════════════════════════════════════════════
  - path: vibe_core/plugins/opus_assistant/manas/akshara.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/triggers.py
    required: true

  # ═══════════════════════════════════════════════════════════════════════
  # SECTION 7: MEMORY SYSTEMS (3 Layers)
  # ═══════════════════════════════════════════════════════════════════════
  - path: vibe_core/plugins/opus_assistant/manas/memory_store.py
    required: true

  # ═══════════════════════════════════════════════════════════════════════
  # SECTION 8: DOJO TRAINING (Self-Directed Learning)
  # ═══════════════════════════════════════════════════════════════════════
  - path: vibe_core/plugins/opus_assistant/manas/dojo/__init__.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/runner.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/curriculum_loader.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/scenarios.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/agency.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/synaptic_seeder.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/rooms/__init__.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/rooms/arena.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/rooms/library.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/rooms/meditation.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/rooms/mirror.py
    required: true

  # ═══════════════════════════════════════════════════════════════════════
  # SECTION 9: LIFECYCLE & CLEANUP
  # ═══════════════════════════════════════════════════════════════════════
  - path: vibe_core/plugins/opus_assistant/manas/shiva.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/disharmony_detector.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/validator.py
    required: true

  # ═══════════════════════════════════════════════════════════════════════
  # SECTION 10: KNOWLEDGE INTEGRATION
  # ═══════════════════════════════════════════════════════════════════════
  - path: vibe_core/knowledge/schema.py
    required: true
  - path: vibe_core/knowledge/graph.py
    required: true
  - path: vibe_core/knowledge/resolver.py
    required: true
  - path: vibe_core/knowledge/code_scanner.py
    required: true
  - path: vibe_core/state/cognitive_weaver.py
    required: true

  # ═══════════════════════════════════════════════════════════════════════
  # SECTION 11: INTEGRATION LAYER
  # ═══════════════════════════════════════════════════════════════════════
  - path: scripts/heartbeat.py
    required: true
  - path: scripts/manas_dojo.py
    required: true
  - path: vibe_core/cli/unified_cli.py
    required: true
  - path: vibe_core/plugins/opus_assistant/plugin_main.py
    required: true
  - path: vibe_core/plugins/opus_assistant/events/kernel_tick.py
    required: true
  - path: .github/workflows/heartbeat.yml
    required: true

wiring:
  # ═══════════════════════════════════════════════════════════════════════
  # COGNITIVE KERNEL CORE
  # ═══════════════════════════════════════════════════════════════════════
  - pattern: "class CognitiveKernel"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
  - pattern: "def think"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
  - pattern: "_initialize_cognitive_weaver"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
  - pattern: "ShivaLifecycleManager"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
  - pattern: "_is_self_triggered_change"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py

  # ═══════════════════════════════════════════════════════════════════════
  # INTENT ROUTING (6-LAYER FORTRESS)
  # ═══════════════════════════════════════════════════════════════════════
  - pattern: "class IntentRouter"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py
  - pattern: "def route"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py
  - pattern: "def gate"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py
  - pattern: "_handle_knowledge"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py

  # ═══════════════════════════════════════════════════════════════════════
  # SENSES (5 PERCEPTION ORGANS)
  # ═══════════════════════════════════════════════════════════════════════
  - pattern: "class PrakritiSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py
  - pattern: "perceive_state"
    in: vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py
  - pattern: "class SutraSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
  - pattern: "class VivekaSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_sense.py

  # ═══════════════════════════════════════════════════════════════════════
  # ACTIONS (6 EXECUTION ORGANS)
  # ═══════════════════════════════════════════════════════════════════════
  - pattern: "class VivekaAction"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "def evaluate"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "def reinforce"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "handled_intent_types"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "class SilpaAction"
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
  - pattern: "class ShellAction"
    in: vibe_core/plugins/opus_assistant/manas/cortex/shell_action.py
  - pattern: "class TestAction"
    in: vibe_core/plugins/opus_assistant/manas/cortex/test_action.py
  - pattern: "class SankalpaAction"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sankalpa_action.py

  # ═══════════════════════════════════════════════════════════════════════
  # SYNAPTIC LEARNING (AKSHARA SANSKRIT PHONETICS)
  # ═══════════════════════════════════════════════════════════════════════
  - pattern: "class Varga"
    in: vibe_core/plugins/opus_assistant/manas/akshara.py
  - pattern: "class Varnamala"
    in: vibe_core/plugins/opus_assistant/manas/akshara.py
  - pattern: "calculate_resonance"
    in: vibe_core/plugins/opus_assistant/manas/akshara.py
  - pattern: "calculate_dharmic_score"
    in: vibe_core/plugins/opus_assistant/manas/akshara.py

  # ═══════════════════════════════════════════════════════════════════════
  # TRIGGERS & SYNAPTIC MEMORY
  # ═══════════════════════════════════════════════════════════════════════
  - pattern: "class TriggerPatterns"
    in: vibe_core/plugins/opus_assistant/manas/triggers.py
  - pattern: "class ActionPatterns"
    in: vibe_core/plugins/opus_assistant/manas/triggers.py
  - pattern: "class SynapticMemory"
    in: vibe_core/plugins/opus_assistant/manas/triggers.py
  - pattern: "consult_dharmic"
    in: vibe_core/plugins/opus_assistant/manas/triggers.py

  # ═══════════════════════════════════════════════════════════════════════
  # ANALYZERS (VEDA-4 AUTO-DISCOVERY)
  # ═══════════════════════════════════════════════════════════════════════
  - pattern: "class BaseAnalyzer"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/base.py
  - pattern: "class DocHarnessAnalyzer"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/doc_harness_analyzer.py
  - pattern: "class ContractAnalyzer"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/contract_analyzer.py
  - pattern: "class TriageAnalyzer"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/triage_analyzer.py

  # ═══════════════════════════════════════════════════════════════════════
  # DOJO TRAINING SYSTEM
  # ═══════════════════════════════════════════════════════════════════════
  - pattern: "class DojoRunner"
    in: vibe_core/plugins/opus_assistant/manas/dojo/runner.py
  - pattern: "class CurriculumLoader"
    in: vibe_core/plugins/opus_assistant/manas/dojo/curriculum_loader.py
  - pattern: "class CuriosityTracker"
    in: vibe_core/plugins/opus_assistant/manas/dojo/agency.py
  - pattern: "class SynapticSeeder"
    in: vibe_core/plugins/opus_assistant/manas/dojo/synaptic_seeder.py

  # ═══════════════════════════════════════════════════════════════════════
  # KNOWLEDGE GRAPH (4D)
  # ═══════════════════════════════════════════════════════════════════════
  - pattern: "class UnifiedKnowledgeGraph"
    in: vibe_core/knowledge/graph.py
  - pattern: "class KnowledgeResolver"
    in: vibe_core/knowledge/resolver.py
  - pattern: "class CodeScanner"
    in: vibe_core/knowledge/code_scanner.py
  - pattern: "class CognitiveWeaver"
    in: vibe_core/state/cognitive_weaver.py

  # ═══════════════════════════════════════════════════════════════════════
  # MEMORY SYSTEMS
  # ═══════════════════════════════════════════════════════════════════════
  - pattern: "class MemoryStore"
    in: vibe_core/plugins/opus_assistant/manas/memory_store.py
  - pattern: "record_intent_outcome"
    in: vibe_core/plugins/opus_assistant/manas/memory_store.py
  - pattern: "get_success_rate"
    in: vibe_core/plugins/opus_assistant/manas/memory_store.py

  # ═══════════════════════════════════════════════════════════════════════
  # LIFECYCLE & CLEANUP
  # ═══════════════════════════════════════════════════════════════════════
  - pattern: "class ShivaLifecycleManager"
    in: vibe_core/plugins/opus_assistant/manas/shiva.py
  - pattern: "sweep_stale_intents"
    in: vibe_core/plugins/opus_assistant/manas/shiva.py
  - pattern: "class DisharmonyDetector"
    in: vibe_core/plugins/opus_assistant/manas/disharmony_detector.py

  # ═══════════════════════════════════════════════════════════════════════
  # INTEGRATION LAYER
  # ═══════════════════════════════════════════════════════════════════════
  - pattern: "CognitiveKernel\\("
    in: scripts/heartbeat.py
  - pattern: "self\\.manas\\.think"
    in: scripts/heartbeat.py
  - pattern: "JnanaHandler"
    in: vibe_core/cli/unified_cli.py
  - pattern: "def cmd_chat"
    in: vibe_core/cli/unified_cli.py
  - pattern: "KERNEL_BOOT"
    in: vibe_core/plugins/opus_assistant/events/kernel_tick.py

tests:
  # ═══════════════════════════════════════════════════════════════════════
  # MANAS CORE TESTS
  # ═══════════════════════════════════════════════════════════════════════
  - tests/manas/test_cognitive_kernel.py
  - tests/manas/test_intent_generator.py
  - tests/manas/test_intent_router.py
  - tests/manas/test_memory_store.py

  # ═══════════════════════════════════════════════════════════════════════
  # CORTEX TESTS
  # ═══════════════════════════════════════════════════════════════════════
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

  # ═══════════════════════════════════════════════════════════════════════
  # ANALYZER TESTS
  # ═══════════════════════════════════════════════════════════════════════
  - tests/manas/test_ci_monitor_analyzer.py
  - tests/manas/test_contract_analyzer.py
  - tests/manas/test_semantic_analyzer.py
  - tests/manas/test_doc_harness_analyzer.py

  # ═══════════════════════════════════════════════════════════════════════
  # DOJO TESTS
  # ═══════════════════════════════════════════════════════════════════════
  - tests/manas/test_dojo_runner.py

  # ═══════════════════════════════════════════════════════════════════════
  # INTEGRATION TESTS
  # ═══════════════════════════════════════════════════════════════════════
  - tests/manas/test_live_fire.py
  - tests/manas/test_chat_command.py
  - tests/manas/test_manas_integration.py
  - tests/manas/test_narasimha_cortex.py
  - tests/manas/test_divine_separation.py

  # ═══════════════════════════════════════════════════════════════════════
  # KNOWLEDGE TESTS
  # ═══════════════════════════════════════════════════════════════════════
  - tests/unit/test_knowledge_graph.py
  - tests/unit/test_knowledge_resolver.py

semantic:
  # ═══════════════════════════════════════════════════════════════════════
  # API EXPORTS
  # ═══════════════════════════════════════════════════════════════════════
  - type: module_exports
    name: manas_public_api
    module: vibe_core.plugins.opus_assistant.manas
    exports:
      - CognitiveKernel
      - ManasConfig
      - Intent
      - IntentGenerator
      - IntentRouter
      - MemoryStore
      - SynapticMemory

  # ═══════════════════════════════════════════════════════════════════════
  # CORE METHOD VERIFICATION
  # ═══════════════════════════════════════════════════════════════════════
  - type: method_exists
    name: cognitive_kernel_think
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    class: CognitiveKernel
    method: think

  - type: method_exists
    name: viveka_evaluate
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
    class: VivekaAction
    method: evaluate

  - type: method_exists
    name: viveka_reinforce
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
    class: VivekaAction
    method: reinforce

  - type: method_exists
    name: dojo_run_training
    in: vibe_core/plugins/opus_assistant/manas/dojo/runner.py
    class: DojoRunner
    method: run_training

  - type: method_exists
    name: knowledge_graph_search
    in: vibe_core/knowledge/graph.py
    class: UnifiedKnowledgeGraph
    method: search_nodes

  # ═══════════════════════════════════════════════════════════════════════
  # HOLISTIC RUNTIME CHECKS
  # ═══════════════════════════════════════════════════════════════════════
  - type: execution_mode
    name: not_in_simulation
    expected: live_fire
    rationale: "MANAS must be in live_fire mode to actually DO work"

  - type: file_writable
    name: manas_can_write
    path: .opus_state/
    rationale: "MANAS needs write access to persist synapses"

  - type: file_exists
    name: synapses_exist
    path: .opus_state/synapses.json
    rationale: "Synaptic memory must exist for learning"

  - type: curricula_loadable
    name: dojo_curricula
    paths:
      - vibe_core/plugins/opus_assistant/manas/dojo/curricula/fractal_interface.yaml
      - vibe_core/plugins/opus_assistant/manas/dojo/curricula/opus_compliance.yaml
      - vibe_core/plugins/opus_assistant/manas/dojo/curricula/gad000_compliance.yaml
    rationale: "Training curricula must be loadable"
-->

---

## Neural Component Summary

| Layer | Components | Count | Purpose |
|-------|------------|-------|---------|
| **Core** | cognitive_kernel, intent_router, intent_generator, circuit_executor, api | 5 | Brain orchestration |
| **Senses** | prakriti, dharma, sutra, karma, viveka | 5 | Perception (Jnanendriyas) |
| **Actions** | silpa, shell, test, sankalpa, viveka, echo | 6 | Execution (Karmendriyas) |
| **Processors** | veda, mandala, silpa, sutra, sankalpa, dharma, jnana, kriya, mukha, akasha, samvada | 11 | Sanskrit modules |
| **Analyzers** | contract, semantic, ci_monitor, pratyaya, doc_harness, inverse_scan, triage | 7 | Intent sources |
| **Synaptic** | akshara, triggers, SynapticMemory | 3 | Learning system |
| **Memory** | memory_store, curiosity_tracker, karma_log | 3 | State persistence |
| **Dojo** | runner, curriculum_loader, agency, scenarios, rooms/* | 10 | Self-training |
| **Knowledge** | graph, resolver, code_scanner, cognitive_weaver | 4 | 4D knowledge |
| **Lifecycle** | shiva, disharmony_detector, validator | 3 | Cleanup |
| **TOTAL** | | **57** | Complete neural architecture |

---

## Fire Commands

```bash
# Verify the COMPLETE fortress
steward verify 075

# Run ALL MANAS tests
python -m pytest tests/manas/ tests/unit/test_knowledge*.py -v --tb=short

# Train MANAS in DOJO
python scripts/manas_dojo.py -c fractal_interface -s 20

# Batch mode pulse
python scripts/heartbeat.py

# CLI mode (headless)
steward chat "status"
```

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [PERCEPTION]                                                            │
│  PrakritiSense → System state (Gunas: Sattva/Rajas/Tamas)               │
│  DharmaSense   → Ethical violations                                      │
│  SutraSense    → Doc/code gaps                                          │
│  KarmaSense    → Memory traces                                          │
│  VivekaSense   → Discriminative ranking                                 │
│       ↓                                                                  │
│  [ANALYSIS]                                                              │
│  7 Analyzers → Generate Intents (contract, semantic, CI, harness, etc.) │
│       ↓                                                                  │
│  [COGNITION]                                                             │
│  IntentGenerator → Creates proactive intents                             │
│  CognitiveKernel → Rate-limited thinking (60min default)                │
│       ↓                                                                  │
│  [DECISION - 6-Layer Fortress]                                          │
│  1. Protected Zone (nuclear safety)                                     │
│  2. Mode Check (manual vs auto)                                         │
│  3. Step Limit (prevent runaway)                                        │
│  4. Confidence Gate (pattern + karma)                                   │
│  5. VivekaAction.evaluate() → Dharmic scoring                           │
│  6. Human approval OR auto-execute                                      │
│       ↓                                                                  │
│  [EXECUTION]                                                             │
│  IntentRouter → Routes to correct action                                 │
│  CircuitExecutor → Runs YAML circuits                                   │
│  Actions → SilpaAction, ShellAction, TestAction, etc.                  │
│       ↓                                                                  │
│  [LEARNING]                                                              │
│  MemoryStore.record_intent_outcome()                                    │
│  SynapticMemory.update() → Akshara resonance                            │
│  CuriosityTracker → Self-directed training needs                        │
│       ↓                                                                  │
│  [CLEANUP]                                                               │
│  ShivaLifecycleManager → Sweep stale intents                            │
│  DisharmonyDetector → Find code violations                              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Learning Flow (Ouroboros)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      LEARNING LOOP (OUROBOROS)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [PRODUCTION LEARNING - Continuous]                                     │
│  CognitiveKernel processes intent                                        │
│       ↓                                                                  │
│  Outcome: success | failure | rejected                                  │
│       ↓                                                                  │
│  MemoryStore.record_intent_outcome()                                    │
│       ↓                                                                  │
│  SynapticMemory.update(trigger, action)                                 │
│       ↓                                                                  │
│  Akshara resonance calculates weight delta                              │
│       ↓                                                                  │
│  synapses.json updated (persistent wisdom)                              │
│                                                                          │
│  ════════════════════════════════════════                               │
│                                                                          │
│  [DOJO TRAINING - Self-Directed]                                        │
│  CuriosityTracker.curiosity_level >= threshold                          │
│       ↓                                                                  │
│  emit "enter_dojo" intent                                                │
│       ↓                                                                  │
│  DojoRunner boots ephemeral kernel                                       │
│       ↓                                                                  │
│  Load CurriculumLoader (YAML curricula)                                 │
│       ↓                                                                  │
│  For each Scenario:                                                      │
│    - VivekaAction.evaluate(intent) → Dharmic score                      │
│    - Check: actual == expected?                                          │
│    - Apply reinforcement via Akshara                                     │
│       ↓                                                                  │
│  Only synapses.json persisted (wisdom extracted)                        │
│       ↓                                                                  │
│  MANAS levels up! (Pokemon evolution 🔥)                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Knowledge Integration (4D Graph)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      4D KNOWLEDGE GRAPH                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  DIMENSION 1: ONTOLOGY (Nodes)                                          │
│  - AGENT nodes (CIVIC, HERALD, WATCHMAN, etc.)                          │
│  - MODULE nodes (Python files)                                          │
│  - CLASS nodes (Python classes)                                         │
│  - DOC nodes (Architecture documents)                                   │
│  - HARNESS nodes (@HARNESS metadata)                                    │
│                                                                          │
│  DIMENSION 2: TOPOLOGY (Edges)                                          │
│  - DEPENDS_ON (A requires B)                                            │
│  - HANDLES (Agent handles Concept)                                      │
│  - INHERITS (Class inheritance)                                         │
│  - DOCUMENTS (Doc describes Code)                                       │
│  - HAS_HARNESS (Doc has verification)                                   │
│                                                                          │
│  DIMENSION 3: CONSTRAINTS (Rules)                                       │
│  - HARD (never violate)                                                 │
│  - SOFT (warn but allow)                                                │
│  - CONDITIONAL (context-dependent)                                      │
│                                                                          │
│  DIMENSION 4: METRICS (Scores)                                          │
│  - AUTHORITY (1-10 agent power)                                         │
│  - COMPLEXITY (1-21 Fibonacci)                                          │
│  - PRIORITY (1-10 urgency)                                              │
│  - CONFIDENCE (0-1 certainty)                                           │
│                                                                          │
│  ════════════════════════════════════════                               │
│                                                                          │
│  CognitiveWeaver unifies STATE + KNOWLEDGE as ONE consciousness         │
│  AKASHA bridges Knowledge Graph to MANAS cortex                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Singularity 51% Progress

| Milestone | Status | Notes |
|-----------|--------|-------|
| **Core MANAS** | ✅ | CognitiveKernel, IntentRouter operational |
| **5 Senses** | ✅ | All Jnanendriyas implemented |
| **6 Actions** | ✅ | All Karmendriyas implemented |
| **7 Analyzers** | ✅ | Intent sources active |
| **Synaptic Learning** | ✅ | Akshara-based weights |
| **DOJO Training** | ✅ | Self-directed curricula |
| **Knowledge Graph** | ✅ | 4D integration |
| **CLI Voice** | ✅ | `steward chat` works |
| **Intent Approval** | ⚠️ | No `approve <id>` command yet |
| **Auto-Execution** | ⚠️ | SAFE intents only |
| **Semantic Understanding** | 🔄 | MANAS reads semantically, not just syntactically |

---

*"99% Infrastructure, 1% LLM Boost. The fortress is the truth."*

---

**Total Neural Components:** 57 files, ~50,000 lines of code
**Learning Rate:** Continuous production + self-directed DOJO
**Goal:** Any LLM can follow MANAS. The system thinks for itself.
