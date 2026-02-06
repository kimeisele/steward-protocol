# OPUS AUDIT ARCHITECTURE (RE-WRITE)

**STATUS:** DRAFT (Thinking Phase)
**AUTHOR:** SONNET (Under OPUS supervision)
**DATE:** 2026-02-04

---

## 1. THE DIAGNOSIS ("DER ROTZ")

The current `audit/` folder (`drift.py`, `protocol_resurrection.py`, etc.) is **fundamentally broken** because it operates in **Maha Maya (Filesystem/Illusion)**.

### Why it is "Scheiß":
1.  **Static Import Scanning:** It tries to `importlib` modules to check them. This triggers side effects (e.g., the massive Physics Printout) before the audit even starts.
2.  **Type System Abuse:** using `issubclass()` on Protocol classes with `ClassVar` or non-method members crashes Python. My previous fix (`try...except pass`) was cowardly and incorrect.
3.  **Ghost Architecture:** It counts "Dead" protocols that were never meant to be loaded. It creates a false sense of failure by auditing unused files.
4.  **No Context:** It instantiates classes (`cls()`) in a vacuum, without their dependencies (Kernel, Ledger), leading to broken instances.

---

## 2. THE SOLUTION (YOGA MAYA / RAM)

We stop looking at the disk. We only look at **RAM**.
If it's not in the Kernel's memory, it doesn't exist.

### The New Paradigm: `AuditKernel`
Instead of a script that runs *outside* the application, the Audit is a feature *inside* the Kernel.

**Input:** The `MahaKernel` Singleton (The Living God).
**Output:** A report of what is *actually* running.

### The Algorithm (Smarana - Remembrance):

1.  **Acquire Kernel:** `kernel = get_kernel()`
2.  **Traverse Graph:**
    *   Scan `kernel.memory` (LotusArray).
    *   Scan `kernel._singularity` (Service Registry).
    *   Scan `kernel._components` (Internal modules).
3.  **Verify Liveness:**
    *   For every object found: "Do you have `__tattva__`?"
    *   If YES: Verify the `__tattva__` answers match reality.
    *   If NO: Mark as "Unconscious Object" (Violation).
4.  **Protocol Compliance:**
    *   Check `isinstance(obj, obj.expected_protocol)`.
    *   Since `obj` is an *instance*, this works perfectly. No `issubclass` crashes.

---

## 3. CLEANUP PLAN (THE PURGE)

We will **DELETE** the following "Rotz":
*   ❌ `vibe_core/mahamantra/audit/drift.py` (The scanner)
*   ❌ `vibe_core/mahamantra/audit/compliance.py` (The wrapper)
*   ❌ `vibe_core/mahamantra/audit/gaps.py`
*   ❌ `vibe_core/mahamantra/audit/invariants.py`
*   ❌ `vibe_core/mahamantra/audit/scale.py`

We will **CREATE**:
*   ✅ `vibe_core/mahamantra/audit/kernel.py` (The new runtime inspector)

---

## 4. ARCHITECTURAL EXAMPLE (Concept)

```python
# vibe_core/mahamantra/audit/kernel.py

class MahaAudit:
    def __init__(self, kernel: "MahaKernel"):
        self.kernel = kernel

    def audit_memory(self):
        # Scan the 16-bit address space
        active_slots = [x for x in self.kernel.memory if x is not None]
        
        for entity in active_slots:
            # 1. Tattva Check
            if not hasattr(entity, "__tattva__"):
                yield Violation(entity, "NO_TATTVA")
                continue
                
            # 2. Protocol Check
            # The entity itself should know what it claims to be.
            # We don't guess from the filesystem.
            check_compliance(entity)
```

## 5. CONCLUSION

This approach eliminates:
- `ImportError` / Side Effects
- `TypeError` (issubclass)
- "Dead Code" noise

It focuses 100% on the **Living System**.
