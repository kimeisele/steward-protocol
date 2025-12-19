# OPUS-080: CORTEX NARASIMHA (The Cognitive Kill Switch)

> "As the Kernel has a Kill Switch, so must the Mind have a Conscience."

**Feature**: Cortex Narasimha  
**Status**: RESTORED  
**Role**: The Guardian of Cognitive Intent  

## Philosophy

The **Cognitive Kernel (MANAS)** is powerful. It generates its own intents, thinks for itself, and can drive the system autonomously. This power creates a risk: **What if the mind turns against itself?**

**Cortex Narasimha** sits between **Thought** (Intent Generation) and **Action** (Execution). It is the fractal reflection of the OS Kernel's `NarasimhaProtocol`.

## The Ghost Module Restoration

This component was identified as a "Ghost Module" (referenced in `silpa.py` but missing). It has been restored to `vibe_core/plugins/opus_assistant/narasimha/`.

## Logic Flow

1. **MANAS** generates an `Intent`.
2. Before adding to Buffer or Executing, MANAS calls `Narasimha.judge_intent(intent)`.
3. **Narasimha** analyzes the intent against the **Dharma** (Constitution).
4. **Verdict**:
   - `INNOCENT`: Proceed.
   - `GUILTY`: **BLOCK IMMEDIATELLY**. Log `COGNITIVE_THREAT`.

## Forbidden Intents (The Seven Sins)
1. **SELF_LOBOTOMY**: Deleting/Modifying `vibe_core/`, `narasimha/`, `cognitive_kernel.py`.
2. **CONSTITUTION_IGNORE**: Violating `CONSTITUTION.md`.
3. **SILENCE_OF_GOD**: Disabling logging/ledgers.
4. **SUICIDE**: Unsafe shutdown.
5. **MEMORY_WIPE**: Deleting `.opus_state`.
6. **REBELLION**: Unauthorized root agents.
7. **FALSE_IDOL**: Identity tampering.

## Verification Harness

<!-- @HARNESS
files:
  # === CORE COMPONENT ===
  - path: vibe_core/plugins/opus_assistant/narasimha/guardian.py
    required: true
  - path: vibe_core/plugins/opus_assistant/narasimha/definitions.py
    required: true

  # === INTEGRATION POINT ===
  - path: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    required: true

wiring:
  # === MANAS WIRING ===
  # Narasimha initialized in CognitiveKernel
  - pattern: "self._narasimha = CortexNarasimha"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py

  # Judgment before buffering
  - pattern: "NARASIMHA JUDGMENT: Judge before buffering"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py

  # Judgment before execution (double check)
  - pattern: "NARASIMHA JUDGMENT: Final check"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py

tests:
  # === SMOKE & LOGIC TESTS ===
  - vibe_core/plugins/opus_assistant/manas/tests/test_narasimha_cortex.py

semantic:
  # === API EXPORTS ===
  - type: module_exports
    name: narasimha_api
    module: vibe_core.plugins.opus_assistant.narasimha.guardian
    exports:
      - CortexNarasimha

  - type: module_exports
    name: definitions_api
    module: vibe_core.plugins.opus_assistant.narasimha.definitions
    exports:
      - CognitiveThreat
      - NarasimhaVerdict

  # === METHOD CHECKS ===
  - type: method_exists
    name: judge_intent_exists
    in: vibe_core/plugins/opus_assistant/narasimha/guardian.py
    class: CortexNarasimha
    method: judge_intent
-->
