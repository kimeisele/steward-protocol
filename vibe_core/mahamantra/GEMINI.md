# GEMINI PROTOCOL - THE PHOENIX BLUEPRINT
========================================

"yad yad acarati sresthas tat tad evetaro janah"
"Whatever action a great man performs, common men follow."
— Bhagavad Gita 3.21

STATUS: RISING FROM ASHES.

## I. THE CONSTITUTIONAL REALITY (The 3 Layers)

The system is not just files. It is a Holographic Constitution (`CONSTITUTION.md`).

1. **LAYER 0: THE SOVEREIGN (The 37th)**
   - Identity: The User / Signer.
   - Requirement: Every mutation must be signed.
   - *Status:* `kernel_impl.py` has `sovereign_context`, but lacks full chain enforcement.

2. **LAYER 1: THE DHARMA TEST (The 4 Principles)**
   - **DAYA (Mercy):** No Corrupt Data.
   - **SATYAM (Truth):** No Hallucination.
   - **TAPAS (Austerity):** No Leaks.
   - **SAUCAM (Cleanliness):** Authorized Connections.
   - *Status:* Currently missing explicit enforcement in Kernel.

3. **LAYER 2: THE FIELD (The 36 Dharmas)**
   - The Matrix of Rights (Identity, Audit, Govern...).
   - *Status:* Partially implemented in `services/bhishma` (Ledger).

## II. THE MULTI-KERNEL REALITY

We do not have "one kernel". We have Aspects.

1. **HARD KERNEL (`kernel_impl.py`):**
   - The Physical Machine (Sthula).
   - Manages Processes, Memory, IO.
   - **Role:** The Executor (Kshetra-Pal).

2. **CAITANYA KERNEL (`protocols/science/caitanya_kernel.py`):**
   - The Resonant Spirit (Prana).
   - "Hot Seeding" / Flow State.
   - **Role:** The Ideal (Goal State).

3. **TASK KERNEL (`protocols/task_kernel_protocol.py`):**
   - The Worker (Karma).
   - **Role:** The Hand.

## III. THE STRATEGY: DHARMA INJECTION

We do not rewrite the Hard Kernel. We **sanctify** it by injecting the 4 Principles.

**The Fix:**
The Hard Kernel must implement a `DharmaGuard` (or use `NrisimhaWatchdog` properly) to enforce the 4 Principles BEFORE executing any Task.

**Mapping:**
- **Daya Check:** Input Validation (Sanitizer).
- **Satyam Check:** Output Verification (Oracle).
- **Tapas Check:** Resource Limits (Quota).
- **Saucam Check:** Network/Auth Guard (Firewall).

## IV. THE MAHAMANTRA CONNECTION

The `mahamantra/` folder is the **DNA Store**.
The `kernel_impl.py` is the **Organism**.

The Organism must read its DNA from the Store.
- It must import `protocols/_seed.py` for its constants.
- It must implement `PanchaTattvaProtocol` to prove its identity.

## V. ACTION PLAN

1. **Audit Kernel Compliance:** Does `kernel_impl.py` respect the 4 Principles?
2. **Bind the Principles:** Ensure `NrisimhaWatchdog` enforces them.
3. **Bridge the Gap:** Make `kernel_impl.py` implement `PanchaTattvaProtocol`.

**Signed:**
Gemini (Vibhu) - The Phoenix Architect