# ORDNUNG.md - The Stabilization Plan

> **"Ordnung muss sein."**
> A structured path to resolve the current chaos and establish the Universal Protocol.

**Current Status:** UNSTABLE / MESSY
**Goal:** Clean, Verified, Atomic Commits.
**Philosophy:** TDD (Red -> Green), No "Quick Fixes", Protocol-First.

---

## I. INVENTORY (The Artifacts)

We have touched the following components. Each must be verified.

### 1. The Protocols (Layer 1) - *The Law*
*   `vibe_core/protocols/universal/krishna.py` (New) - Identity Protocol.
*   `vibe_core/protocols/universal/rama.py` (New) - Action Protocol.
*   `vibe_core/protocols/universal/om.py` (New) - Unified Field.
*   `vibe_core/protocols/universal/mantra.py` (Modified) - Time/Clock.
*   `vibe_core/protocols/universal/__init__.py` (Modified) - Exports.
*   **Status:** Likely Good. Needs verification of imports/types.

### 2. The Substrate Bridge (Layer 0) - *The Spine*
*   `vibe_core/naga/services/ananta.py` (Modified) - Implements `IAnantaBridge`.
*   **Status:** Needs verification. Added `flood_instance`, `resonate`, `analyze_class`. Critical for "Positive Pathogen".

### 3. The CLI Infrastructure (Layer 0) - *The Nervous System*
*   `vibe_core/protocols/cli_execution.py` (Modified) - Added `handler` to `CLIExecutionContext`.
*   `vibe_core/cli/unified_cli.py` (Modified) - Pass `handler_instance` to context.
*   `vibe_core/naga/hooks/ananta_cli.py` (New) - The Hook that floods the handler.
*   **Status:** Functional but needs review. This was the "Recalibration".

### 4. The Ledger (Layer -1) - *The Memory*
*   `vibe_core/ledger.py` (Modified) - Added `get_meta`/`set_meta` to `InMemoryLedger`.
*   **Status:** Pragmatic fix for tests. Needs strict typing review.

### 5. The Kernel (Layer 2) - *The Heart (Compromised)*
*   `vibe_core/kernel_impl.py` (Modified/Messy) - Attempted wiring of Protocols.
*   **Status:** **CRITICAL MESS.** Potentially duplicated code or partial application. Needs surgical repair or reset.

### 6. The Tests (The Gates)
*   `tests/samkhya/test_protocol_compliance.py` - The Architecture Tests.
*   `tests/samkhya/test_kurukshetra.py` - The Hardening Tests.
*   `tests/samkhya/test_ananta_cli_hook.py` - The Hook Test.
*   **Status:** Mixed. Some Red (Good), some Green (Suspicious).

---

## II. THE PROCEDURE (10 Iterations)

We will execute this plan sequentially. No jumping ahead.

### Iteration 1: Protocol Verification
*   **Task:** Verify all `universal/*.py` files are syntactically correct and type-safe.
*   **Check:** Do they use `Any`? Are imports clean?
*   **Action:** Lint/Fix protocols.

### Iteration 2: Substrate Bridge Validation
*   **Task:** Verify `AnantaService` correctly implements `IAnantaBridge`.
*   **Check:** Does `flood_instance` actually swap the class?
*   **Test:** Run `test_ananta_implements_bridge` (isolated).

### Iteration 3: CLI Infrastructure Audit
*   **Task:** Verify `CLIExecutionContext` change is safe (backward compatible?).
*   **Task:** Verify `UnifiedCLI` passes the handler correctly.
*   **Action:** Review code diffs.

### Iteration 4: The Hook Integration
*   **Task:** Verify `AnantaCLIHook` logic.
*   **Check:** Does it fail gracefully? (It should).
*   **Test:** Run `test_ananta_cli_hook.py`.

### Iteration 5: Ledger Stabilization
*   **Task:** Ensure `InMemoryLedger` matches `SQLiteLedger` interface strictly.
*   **Action:** Clean up `get_meta` typing if needed.

### Iteration 6: KERNEL SURGERY (The Hard Part)
*   **Task:** **RESET** `kernel_impl.py` to cleanliness.
*   **Task:** Apply `KrishnaProtocol` and `RamaProtocol` inheritance **CLEANLY**.
*   **Task:** Implement the methods (`bind_genes`, `perform_dharma`) as **STUBS** first.
*   **Task:** Wire `Mantra` handlers.

### Iteration 7: The Gate Check (Red Phase)
*   **Task:** Run `test_protocol_compliance.py`.
*   **Expectation:** Should pass inheritance checks, might fail logic checks if stubs are empty.
*   **Goal:** ALL GREEN on structure (Inheritance/Signatures).

### Iteration 8: Kurukshetra Hardening (Green Phase)
*   **Task:** Run `test_kurukshetra.py`.
*   **Goal:** Verify `bind_genes` is called (Pathogen works). Verify Identity check (Security works).

### Iteration 9: Atomic Commits
*   **Task:** Group changes into logical commits.
    1.  `feat(protocols): add universal om/krishna/rama protocols`
    2.  `feat(ananta): implement IAnantaBridge in service`
    3.  `feat(cli): enable handler inspection and ananta hook`
    4.  `fix(ledger): update InMemoryLedger interface`
    5.  `feat(kernel): implement universal protocols`
    6.  `test(samkhya): add architectural compliance tests`

### Iteration 10: Final State Verification
*   **Task:** Full system boot test (simulated).
*   **Task:** Check `Mantra` cycle health.

---

## III. NEXT STEPS

We begin with **Iteration 1**.
I await approval of this `ORDNUNG`.
