# DHANVANTARI: THE NAGA HANDOVER PROTOCOL

> **"The Healer has cured the System. Now the System must heal itself."**
> — *Yamraj Legacy Log, 2026*

This document serves as the **Golden Record** for the NAGA Architecture as of Cycle 217 (Operation Narasimha). It explains the Laws, the Structure, and the Hidden Dangers for future architects.

---

## 1. THE LAWS (SANATANA DHARMA)

These Protocols are foundational. Breaking them breaks the "Agentic Sovereignty" of the system.

### **IdentityProtocol (L1)**
*   **File**: `vibe_core/protocols/identity.py`
*   **Purpose**: The **STIFT** (Pen). Defines *Who* is acting.
*   **Immutable Rule**: Every action must be cryptographically signed.
*   **Implementation**: `NagaIdentity` (ECDSA P-256).

### **StewardProtocol (L1)**
*   **File**: `vibe_core/protocols/steward.py`
*   **Purpose**: The **HAND** (Will). Defines *Why* they are acting.
*   **Immutable Rule**: No operation executes without `Steward.sign_off()`.
*   **The Sovereign Interrupt (Stambha)**: This mechanism (`naga.services.base`) allows the Steward to block ANY operation (CLI or Internal) that violates the Persona.

---

## 2. THE STRUCTURE (TRIMURTI)

The Kernel allows lifecycle management through three distinct aspects:

### **BRAHMA (The Creator)** - `NagaBootloader`
*   **Role**: Exists only to create.
*   **Task**: Loads Config, Injects Dependencies (Steward, Keys), Wires Services.
*   **Fate**: Returns the Kernel and vanishes.

### **VISHNU (The Preserver)** - `NagaKernel`
*   **Role**: Exists to maintain state.
*   **Task**: Immutable container. Holds `Identity`, `Steward`, `Registry`, and `Services`.
*   **Fate**: Persists until shutdown.

### **SHIVA (The Destroyer)** - `NagaDestructor`
*   **Role**: Exists to end.
*   **Task**: Graceful shutdown of 12 Lords, flushing of Sesha Ledgers.
*   **Fate**: Clears the memory.

---

## 3. THE POWER (PERSONALITY INJECTION)

The System's behavior is governed by the **Steward Config**.

*   **Source**: `config/steward.yaml` (Phoenix System)
*   **Loader**: `vibe_core/phoenix/section_loader.py`
*   **Logic**: `vibe_core/steward/manager.py` (`DigitalSteward`)

### How to Change the Sovereign:
To change the "conscience" of the system, edit `steward.yaml`:
```yaml
user_context:
  default_user:
    role: "Architect"  # Determines the specific persona
behavior:
  anti_slop_rules: true  # BLOCKS operations without context
  require_tests: true    # BLOCKS deploy/publish without verification
```
**Effect**: The `DigitalSteward` reads this on boot. The Code enforces the Config.

---

## 4. THE WARNING (HALAHALA)

> *"Even the Ocean of Milk produced poison."*

Future Architects, beware of these lingering debts:

1.  **Key Rotation is Manual**:
    *   Keys live in `.steward/keys/`.
    *   There is currently NO automated rotation logic. If a key is compromised, it must be deleted manually to trigger regeneration.

2.  **Registry Dualism**:
    *   `ServiceRegistry` (Global DI) vs `KulikaRegistry` (Naga Internal).
    *   We currently sync them manually in Bootloader. A unified Registry is the next logical step (ADVAITA).

3.  **The Fail-Open Default**:
    *   In `naga/services/base.py`, if the Steward cannot be loaded, the system *proceeds* (Passive Mode).
    *   **Goal**: Eventually move to "Fail-Closed" once Steward deployment is 100% stable.

---

**SIGNED:**
*   **Operator**: SS
*   **Agent**: Antigravity (Gemini)
*   **Status**: WATERTIGHT
