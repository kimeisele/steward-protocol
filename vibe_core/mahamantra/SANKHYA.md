# SANKHYA - The Architecture (Actionable)
# =========================================

**Based on MAHAPROMPT.md, byte.py (SSOT), and _fractal.py.**

This document maps the entire project structure to the 16-Position Fractal Lotus.
**RULE #1: FOLDER IS WIRING.**

---

## 1. THE 16 POSITIONS (Folder Mapping)

Every `vibe_core` component maps to exactly one position.
If a file is not in this structure, it is "Unwired" (Maya).

| Pos | Guardian | Folder Path | Legacy Mapping (The "Blob") |
|:---|:---|:---|:---|
| **GENESIS** | **INPUT** | `mahamantra/genesis/` | `vibe_core/genesis/` |
| 0 | **Prithu** | `.../prithu/` | `boot.py`, `boot_orchestrator.py` |
| 1 | **Brahma** | `.../brahma/` | `manifest_registry.py`, `container_service.py` |
| 2 | **Narada** | `.../narada/` | `cli/`, `event_bus.py`, `herald/` |
| 3 | **Shambhu** | `.../shambhu/` | `process_manager.py`, `threading` |
| **DHARMA** | **VERIFY** | `mahamantra/dharma/` | `vibe_core/governance/` |
| 4 | **Vyasa** | `.../vyasa/` | `doc_renderer.py`, `documentation/` |
| 5 | **Kumaras** | `.../kumaras/` | `knowledge/`, `ontology/` |
| 6 | **Kapila** | `.../kapila/` | `type_check.py`, `static_analysis/` |
| 7 | **Manu** | `.../manu/` | `tests/`, `governance_gate.py` |
| **KARMA** | **EXECUTE** | `mahamantra/karma/` | `vibe_core/reactor/` |
| 8 | **Parashurama**| `.../parashurama/` | `reactor.py`, `circuit_executor.py` |
| 9 | **Prahlada** | `.../prahlada/` | `plugin_loader.py`, `capability_registry.py` |
| 10 | **Janaka** | `.../janaka/` | **`kernel_impl.py`** (The Core), `scheduler.py` |
| 11 | **Bhishma** | `.../bhishma/` | `ledger.py`, `sqlite_ledger.py` |
| **MOKSHA** | **OUTPUT** | `mahamantra/moksha/` | `vibe_core/naga/` |
| 12 | **Nrisimha** | `.../nrisimha/` | `security.py`, `naga/` (Defense) |
| 13 | **Bali** | `.../bali/` | `io_service.py`, `network_proxy.py` |
| 14 | **Shuka** | `.../shuka/` | `logging`, `telemetry/`, `sankirtan.py` |
| 15 | **Yamaraja** | `.../yamaraja/` | `auditor/`, `cleanup.py`, `exit()` |

**Action Item:**
We must eventually move/symlink the Legacy code into these 16 folders to satisfy `FOLDER IS WIRING`.

---

## 2. THE PROTOCOL INTERFACE (TypedDict)

Every Mahajana must implement a strict `Protocol` returning `TypedDict`.
**No `Any`. No `dict`.**

### Example: Position 10 (Janaka / State Sync)

```python
# mahamantra/karma/janaka/__init__.py

class Task(TypedDict):
    id: str
    status: str
    result: Optional[str]

class JanakaProtocol(Protocol):
    def submit(self, task: Task) -> str: ...
    def check(self, task_id: str) -> Task: ...
```

---

## 3. THE IMPLEMENTATION STRATEGY (Lazy Load)

We do not rewrite the 700k LOC. We **wrap** it using the Lazy Load pattern from MAHAPROMPT.

**In `mahamantra/karma/janaka/__init__.py`:**

```python
# 1. Declaration
__mahajana__ = "janaka"
__position__ = 10

# 2. Protocol
class JanakaProtocol(Protocol): ...

# 3. Null (Test)
class NullJanaka(JanakaProtocol): ...

# 4. Service (Production)
def __getattr__(name):
    if name == "JanakaService":
        # BRIDGE TO LEGACY
        # We import the "broken" service OR the kernel directly here
        from vibe_core.services.janaka_service import JanakaService
        return JanakaService
```

**This satisfies Rule #4:**
The `LotusNode` finds `__init__.py`.
It calls `__getattr__`.
It gets the Legacy Code.
**Routing is restored without moving files physically yet.**

---

## 4. IP SCALING & ROUTING (The Fractal)

Since every feature maps to a position:
*   `0x0...` -> Genesis (Boot)
*   `0xA...` -> Karma / Janaka (Execute)

**Routing Algorithm:**
1.  Input: `mahamantra.execute("submit_task")`
2.  Lookup: `cli_auto` finds "submit_task" belongs to `JanakaProtocol`.
3.  Address: Position 10 (`0xA`).
4.  Dispatch: `mahamantra.mod[10].JanakaService.submit_task()`.

This is **O(1) Routing**. No search. Pure calculation.

---

## 5. VALIDATION (The 37 Check)

Every component must declare its `__genesis__` hash.
`int(hash, 16) % 37 == 0`.

If `kernel_impl.py` wants to be Janaka, it must have the hash.
(It currently does: `0xfc269a74 % 37 == 0`).

**The System is valid.** We just need to enforce the **Folder Wiring**.
