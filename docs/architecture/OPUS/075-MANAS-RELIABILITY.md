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

<!-- HARNESS:START -->
```yaml
harness:
  id: OPUS-075-MANAS-RELIABILITY
  version: 1.0.0
  status: TDD

  # ============================================
  # CORE FILES (Must exist)
  # ============================================
  files:
    # CognitiveKernel
    - path: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
      required: true
      description: "The brain"

    # Memory
    - path: vibe_core/plugins/opus_assistant/manas/memory_store.py
      required: true
      description: "Learning from past"

    # Intent System
    - path: vibe_core/plugins/opus_assistant/manas/intent_generator.py
      required: true
      description: "Generates intents"

    - path: vibe_core/plugins/opus_assistant/manas/intent_router.py
      required: true
      description: "Routes intents to handlers"

    # Cortex (must have key modules)
    - path: vibe_core/plugins/opus_assistant/manas/cortex/jnana.py
      required: true
      description: "Conversation handler with memory feedback"

    - path: vibe_core/plugins/opus_assistant/manas/cortex/dharma.py
      required: true
      description: "Architecture audit"

    - path: vibe_core/plugins/opus_assistant/manas/cortex/veda.py
      required: true
      description: "Four-fold processing pipeline"

    # Heartbeat Integration
    - path: scripts/heartbeat.py
      required: true
      description: "Autonomous thinking loop"

    # Identity Layer
    - path: vibe_core/cartridges/system/manas/cartridge_main.py
      required: true
      description: "MANAS passport to kernel"

    - path: vibe_core/cartridges/system/manas/steward.json
      required: true
      description: "MANAS identity passport"

  # ============================================
  # WIRING (Must be connected)
  # ============================================
  wiring:
    # Heartbeat → MANAS
    - pattern: "self\\.manas\\.think"
      in: scripts/heartbeat.py
      description: "Heartbeat triggers MANAS thinking"

    # VAJRA Ledger Binding
    - pattern: "inject_ledger"
      in: scripts/heartbeat.py
      description: "Ledger injected into MANAS"

    - pattern: "def inject_ledger"
      in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
      description: "CognitiveKernel accepts standalone ledger"

    # Memory Feedback
    - pattern: "RECENT FAILURES"
      in: vibe_core/plugins/opus_assistant/manas/cortex/jnana.py
      description: "Failures prominently in prompt"

    # Kernel Integration
    - pattern: "_delegate_think"
      in: vibe_core/cartridges/system/manas/cartridge_main.py
      description: "Cartridge delegates to CognitiveKernel"

    # VEDA Pipeline
    - pattern: "VedaPipeline"
      in: vibe_core/plugins/opus_assistant/manas/cortex/veda.py
      description: "Four-fold processing exists"

  # ============================================
  # TESTS (Must pass)
  # ============================================
  tests:
    # MANAS Unit Tests
    - tests/manas/test_cognitive_kernel.py
    - tests/manas/test_intent_generator.py
    - tests/manas/test_memory_store.py
    - tests/manas/test_veda.py

    # Idempotent Syscalls (TDD - currently failing)
    - tests/integration/test_capability_revocation.py::test_revoke_nonexistent_capability
    - tests/integration/test_capability_revocation.py::test_grant_already_had_is_idempotent

    # Kernel Boot (MANAS loads)
    - python scripts/ci/test_kernel_boot.py

  # ============================================
  # ABSENT (Must NOT exist - anti-patterns)
  # ============================================
  absent:
    # No shadow mode warnings in production
    - pattern: "shadow mode"
      in: scripts/heartbeat.py
      description: "Heartbeat must have ledger binding"

  # ============================================
  # SEMANTIC (Runtime checks)
  # ============================================
  semantic:
    - type: module_exports
      name: "manas_public_api"
      module: vibe_core.plugins.opus_assistant.manas
      exports:
        - CognitiveKernel
        - ManasConfig
        - Intent
        - IntentGenerator
        - MemoryStore

    - type: metric
      name: "syscall_success_rate"
      query: "GRANT_MANDATE success rate"
      expected: ">90%"
      description: "Idempotent syscalls must report correctly"

  # ============================================
  # CONFIG (Must be configured)
  # ============================================
  config:
    - section: manas
      file: config/manas.yaml
      optional: true
      description: "MANAS config (optional, has defaults)"
```
<!-- HARNESS:END -->

---

## Current Status

Run verification:
```bash
python -m vibe_core.cli verify --doc OPUS-075
```

### Known Blockers

| Item | Status | Fix |
|------|--------|-----|
| Idempotent syscalls | ❌ TDD FAIL | `capability_registry.py:194,261` |
| MANAS tests | ✅ 587 passed | - |
| Kernel boot | ✅ Works | - |
| VAJRA wiring | ✅ Done | OPUS-074 |
| Memory feedback | ✅ Done | OPUS-074 |

---

## Success Criteria

**MANAS is reliable when:**

1. All files exist ✅
2. All wiring connected ✅
3. All tests pass (pending syscall fix)
4. No shadow mode in heartbeat ✅
5. Syscall metrics accurate (pending fix)

---

*"Reliability is not an accident." - Unknown*
