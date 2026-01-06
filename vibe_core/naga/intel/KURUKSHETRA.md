# KURUKSHETRA - The War on Any (Tamas)

> "Ignorance (Tamas) manifests as `Any`. Knowledge (Sattva) manifests as `Type`.
> In Naga Loka, we do not guess. We KNOW."
> — *Prahlad Maharaj*

## 🎯 Mission Objective
**Target:** Eliminate `Any` from `vibe_core/protocols/naga/*.py`
**Current Status:** 54 Violations (Dharma Breach)
**Goal:** 0 Violations (Sattva)

---

## ⚔️ Battle Plan (Execution Steps)

### Phase 1: Forging the Weapons (Define Types)
**File:** `vibe_core/protocols/naga/types.py`

Implement these `TypedDict` definitions to replace loose Dicts.

```python
from typing import TypedDict, Any, List, Dict # Start migration, eventually remove Any

# For Sesha / Vasuki
class EventDict(TypedDict, total=False):
    event_type: str
    agent_id: str
    timestamp: str
    details: Dict[str, object]  # object is safer than Any
    signature: str

# For Prahlad
class ErrorContext(TypedDict, total=False):
    traceback: str
    locals: Dict[str, str]
    input_data: str
    user_id: str

# For Kulika
class ManifestDict(TypedDict):
    name: str
    version: str
    capabilities: List[str]
    # ... other manifest fields
```

### Phase 2: The Attack (File by File)

#### 1. `kulika.py` (The Registry)
*   **Target:** `validate_manifest(manifest: Any)`
*   **Weapon:** `validate_manifest(manifest: AgentManifest)`
    *   *Import:* `from vibe_core.protocols.agent import AgentManifest`
*   **Target:** `instance: Optional[Any]`
*   **Weapon:** `instance: Optional[object]` (or `ServiceProtocol` if available)

#### 2. `vasuki.py` (The Snake)
*   **Target:** `churn_out(event: Dict[str, Any])`
*   **Weapon:** `churn_out(event: EventDict)`
*   **Target:** `churn_in(...) -> Dict[str, Any]`
*   **Weapon:** `churn_in(...) -> EventDict`

#### 3. `cortex.py` (The Brain)
*   **Target:** `to_dict(self) -> Dict[str, Any]`
*   **Weapon:** `to_dict(self) -> Dict[str, object]`
*   **Note:** Use `object` for JSON-serializable values instead of `Any`.

#### 4. `narada.py` (The Spy)
*   **Target:** `spy(self, func: Any) -> Any`
*   **Weapon:** ParamSpec & TypeVar!
    ```python
    from typing import Callable, TypeVar, ParamSpec
    P = ParamSpec("P")
    R = TypeVar("R")
    
    def spy(self, func: Callable[P, R]) -> Callable[P, R]: ...
    ```

#### 5. `prahlad.py` (The Governor)
*   **Target:** `context: Dict[str, Any]`
*   **Weapon:** `context: ErrorContext`
*   **Target:** `export_hardening_suite() -> List[Dict[str, Any]]`
*   **Weapon:** `export_hardening_suite() -> List[TestCaseDict]` (Define new TypedDict)

---

## 🛡️ Rules of Engagement
1.  **No `Any`.** If you must, use `object` (implies "I don't know the type, but I won't assume operations on it").
2.  **Imports:** If a type exists in `vibe_core.protocols`, import it. Don't redefine.
3.  **TypedDict:** Use `total=False` if fields are optional.
4.  **Generics:** Use `T`, `P`, `R` for decorators/wrappers.

**Execute Order 66 on `Any`. Haribol.**