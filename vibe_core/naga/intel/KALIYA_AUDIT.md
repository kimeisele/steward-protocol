# KALIYA AUDIT - The Taming of the Snake

> "Krishna verbannte Kaliya in den Ozean - isoliert aber lebendig."

## Status: HARDENED (State Persistence)

---

## I. FINDINGS

### A. STATE-LOSS ON RESTART (CRITICAL)
**Diagnosis:** Kaliya stored quarantine records and violation counts only in memory (`self._quarantine_registry`).
**Impact:** A toxic agent could crash the service (or wait for a restart) to escape quarantine or reset its violation count. This is **Fail-Open across restarts**.
**Fix:** Implemented persistence via `StateService` (Prana). Kaliya now saves its state to `kaliya_registry.json` on every change (`quarantine`, `release`, `record_violation`, `escalate`) and reloads it on boot.

### B. ARCHITECTURAL VIOLATION (DIRECT I/O)
**Diagnosis:** Initial attempt used `import json` and direct file writes.
**Correction:** Refactored to use **StateServiceProtocol** via Dependency Injection. Kaliya now acts as a proper citizen of the architecture, delegating persistence to the Ahamkara layer (`StateService`).

### C. TEST INTEGRITY (MOCKS)
**Diagnosis:** Tests used `MagicMock` to bypass persistence logic.
**Correction:** Removed mocks. Tests now use a real `StateService` instance wired to a temporary directory (`temp_dir` fixture). This ensures the integration code actually works.

---

## II. IMPLEMENTATION DETAILS

### 1. Persistence via StateService
```python
    def _save_state(self) -> None:
        try:
            state = { ... }
            self._state.save("kaliya_registry.json", state)
        except Exception as e:
            logger.warning(f"Failed to save state: {e}")
```

### 2. Dependency Injection
```python
    def __init__(self, ..., state_service: Optional[StateServiceProtocol] = None):
        if state_service:
            self._state = state_service
        else:
            self._state = get_state_service()
        self._load_state()
```

---

## III. VERIFICATION

### Tests Updated (`tests/naga/test_kaliya.py`)
- **No Mocks:** Uses `state_service` fixture (real instance).
- **Persistence Verified:** 17/17 tests passed with full state saving/loading active.

### Status
- **Kaliya:** ✅ HARDENED (Persistent Quarantine)

**Dharma is restored in the Quarantine Layer.**
