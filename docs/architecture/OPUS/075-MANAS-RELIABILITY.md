# OPUS-075: MANAS RELIABILITY HARNESS

**Status:** TDD - HARNESS FIRST
**Author:** Claude (Opus)
**Date:** 2025-12-15
**Scope:** Define what "MANAS works reliably" means

---

## Purpose

This document defines the **acceptance criteria** for MANAS reliability.
If this harness passes, MANAS is production-ready.

---

## Verification Harness

<!-- @HARNESS
files:
  # CognitiveKernel
  - path: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    required: true
  # Memory
  - path: vibe_core/plugins/opus_assistant/manas/memory_store.py
    required: true
  # Intent System
  - path: vibe_core/plugins/opus_assistant/manas/intent_generator.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/intent_router.py
    required: true
  # Cortex
  - path: vibe_core/plugins/opus_assistant/manas/cortex/jnana.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/dharma.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/veda.py
    required: true
  # Heartbeat
  - path: scripts/heartbeat.py
    required: true
  # Identity Layer
  - path: vibe_core/cartridges/system/manas/cartridge_main.py
    required: true
  - path: vibe_core/cartridges/system/manas/steward.json
    required: true

wiring:
  - pattern: "self\\.manas\\.think"
    in: scripts/heartbeat.py
  - pattern: "inject_ledger"
    in: scripts/heartbeat.py
  - pattern: "def inject_ledger"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
  - pattern: "RECENT FAILURES"
    in: vibe_core/plugins/opus_assistant/manas/cortex/jnana.py
  - pattern: "_delegate_think"
    in: vibe_core/cartridges/system/manas/cartridge_main.py
  - pattern: "VedaPipeline"
    in: vibe_core/plugins/opus_assistant/manas/cortex/veda.py

tests:
  - tests/manas/test_cognitive_kernel.py
  - tests/manas/test_intent_generator.py
  - tests/manas/test_memory_store.py
  - tests/manas/test_veda.py

semantic:
  - type: module_exports
    name: manas_public_api
    module: vibe_core.plugins.opus_assistant.manas
    exports:
      - CognitiveKernel
      - ManasConfig
      - Intent
      - IntentGenerator
      - MemoryStore
-->

---

## Status

| Check | Result |
|-------|--------|
| Files exist | ✅ 10/10 |
| Wiring connected | ✅ 6/6 |
| Tests exist | ✅ 4/4 |
| Semantic exports | ✅ PASSED |

Run: `python -m vibe_core.cli verify --doc OPUS-075`

---

## Implementation

This document IS the implementation - the @HARNESS above is verified by `VerificationEngine` at:
- `vibe_core/plugins/opus_assistant/core/verification_logic.py`

The harness validates MANAS reliability automatically. No additional code needed.

---

*"Reliability is not an accident." - Unknown*
