# GEMINI PRO ANALYSIS - Fraktal System Transition

> **Role:** Consultant / Analyst
> **Date:** 2025-12-05
> **Status:** READY FOR OPUS

---

## 1. Executive Summary

**Urteil:** Plan (`ARCHITECTURE_NEXT.md`) ist **exzellent**. VEDA-4 Pattern (Fraktale Architektur) ist der Weg.
**Status Phase 1 (Opus):** ✅ ERFOLGREICH (`vibe_core/loaders` + Tests).
**Blocker:** ⚠️ Test-Suite "Deadlock" (Import-Kaskade).

**Lösung:**
1.  **Deadlock fixen** (Tests & Crypto Dependency).
2.  **Migration starten** (Steward Protocol & Crypto Plugin).

---

## 1.5 Service Offer: Gemini Pro (Dual Role)

**To:** Opus (Executor) & User (Architect)
**From:** Gemini (Consultant & Builder)

Ich operiere in zwei Modi. Der User entscheidet, welcher aktiv ist.

### JOB 1: The Architect (Consultant)
*Default Mode. High-Level Oversight.*
- **Analysis:** Ich sehe *alles* (Massive Context). Ich erkenne Muster und Risiken.
- **Strategy:** Ich definiere den Schlachtplan (siehe unten).
- **Debugging:** Wenn Tests hängen, finde ich den Root Cause.
- **Constraint:** Ich fasse den Code NICHT an. Ich bin dein "Pair Programmer".

### JOB 2: The Builder (Support)
*On Demand Mode. "Gemini, hilf bauen!"*
- **Refactoring:** Ich kann komplexe Refactorings übernehmen (z.B. Crypto-Plugin Extraktion).
- **Implementation:** Ich schreibe Boilerplate oder spezifische Module.
- **Constraint:** Nur auf explizite Anweisung ("Gemini, fix das").

**Nutzung:**
- Lies diesen Report VOR Phase 2.
- Wenn du stecken bleibst: Frag den User, mich zu konsultieren (Job 1) oder mir den Hammer zu geben (Job 2).

---

## 2. Immediate Fixes (The "Deadlock" Breaker)

Bevor Phase 2 startet, MUSS Opus diese 3 kleinen Fixes machen. Sonst läuft nichts.

1.  **Fix `tests/__init__.py`**:
    `touch tests/__init__.py` (Macht `tests` zum Package, fixt Import-Errors).
2.  **Fix `ecdsa` Dependency**:
    `pip install ecdsa` (Fehlende Lib crasht alles).
3.  **Fix `steward/crypto.py` (Short-term)**:
    Verschiebe `from ecdsa ...` IN die Funktionen (Lazy Import). Das verhindert Crashes, wenn die Lib fehlt.

---

## 3. Comprehensive Migration Roadmap

Hier ist der Schlachtplan für ein sauberes System, aufgeteilt in Zeit-Ebenen.

### Phase 2a: The Foundation (Short Term)
**Ziel:** Kernel stabilisieren, Deadlock lösen, Core-Logik entkoppeln.

| Plugin | Source | Target | Priority | Why? |
|--------|--------|--------|----------|------|
| **Crypto** | `steward/crypto.py` | `vibe_core/plugins/crypto/` | 🚨 **CRITICAL** | Entkoppelt harte Dependency. Fixt Crashes. |
| **Steward** | `plugins/steward_protocol.py` | `vibe_core/plugins/steward_protocol/` | 🚨 **CRITICAL** | Der Monolith. Muss aufgebrochen werden. |
| **Test Mode** | `plugins/test_mode.py` | `vibe_core/plugins/test_mode/` | 🔴 **HIGH** | Global State killt Parallel-Tests. Muss isoliert werden. |

### Phase 2b: The Governance Layer (Medium Term)
**Ziel:** Die "Regeln der Stadt" (Vedic Laws) modularisieren.

| Plugin | Source | Target | Priority | Why? |
|--------|--------|--------|----------|------|
| **Governance** | `plugins/vedic_governance.py` | `vibe_core/plugins/vedic_governance/` | 🟡 **MEDIUM** | Varna/Ashrama Logik. Foundational, aber Kernel bootet auch ohne. |
| **Sarga** | `plugins/sarga_cycle.py` | `vibe_core/plugins/sarga_cycle/` | 🟡 **MEDIUM** | Scheduler Gating (Day/Night). Sauberer als Cartridge. |

### Phase 3: The Interface Layer (Long Term)
**Ziel:** User-Facing Plugins aufräumen. Diese sind weniger kritisch für die Stabilität.

| Plugin | Source | Target | Priority | Why? |
|--------|--------|--------|----------|------|
| **Git History** | `plugins/git_history.py` | `vibe_core/plugins/git_history/` | 🟢 **LOW** | Analyse-Tool. Kann warten. |
| **Envoy UI** | `plugins/envoy_ui.py` | `vibe_core/plugins/envoy_ui/` | 🟢 **LOW** | Terminal UI Sync. |
| **Settings UI** | `plugins/settings_ui.py` | `vibe_core/plugins/settings_ui/` | 🟢 **LOW** | Settings Sync. |
| **Ephemeral** | `plugins/ephemeral_ui.py` | `vibe_core/plugins/ephemeral_ui/` | 🟢 **LOW** | Dashboard. |

---

## 3.5 Senior Migration Specs (The "Pro" Details)

Damit Opus nicht stolpert, hier die **exakten Specs** für die komplexen Plugins.

### Spec 1: Vedic Governance (`vedic_governance`)
**Challenge:** State Persistence (`_varna_registry`, `_ashrama_registry`).
**Risk:** Wenn der State beim Reload verloren geht, verlieren Agents ihren Status.

**Migration Instructions:**
1.  **Manifest:**
    ```json
    {
      "id": "vedic_governance",
      "priority": 10,
      "hooks": ["on_boot", "on_agent_registered", "on_task_pre_assign", "on_task_completed"]
    }
    ```
2.  **Code (`plugin_main.py`):**
    - Kopiere die Logik 1:1.
    - **WICHTIG:** Die Registry-Daten (`self._varna_registry`) sind aktuell *in-memory*. Das ist okay für Phase 2, aber markiere es mit `# TODO: Persist to Ledger`.
    - **Hook Registration:** Stelle sicher, dass `kernel.governance = self` in `on_boot` gesetzt wird, damit alter Code (`kernel.governance.get_varna...`) weiter funktioniert.

### Spec 2: Sarga Cycle (`sarga_cycle`)
**Challenge:** Global Singleton (`get_sarga()`).
**Risk:** Race Conditions zwischen Plugin und globalem Modul.

**Migration Instructions:**
1.  **Manifest:**
    ```json
    {
      "id": "sarga_cycle",
      "priority": 5,
      "hooks": ["on_boot", "on_task_submit"]
    }
    ```
2.  **Code (`plugin_main.py`):**
    - Importiere `vibe_core.sarga` erst *innerhalb* der Methoden (Lazy Import), um Zirkelbezüge zu vermeiden.
    - Behalte die `MAINTENANCE_TASK_TYPES` Konstante im Plugin (oder lagere sie in `config.yaml` aus -> **Bonus Points**).

### Spec 3: Crypto Plugin (`crypto`) - NEW!
**Challenge:** Hard Dependency Removal.

**Migration Instructions:**
1.  **Manifest:**
    ```json
    {
      "id": "crypto",
      "priority": 1,
      "hooks": ["on_boot"]
    }
    ```
2.  **Code (`plugin_main.py`):**
    - Kapselt `ecdsa` Imports.
    - Bietet `sign_content` und `verify_signature` als Methoden an.
    - `on_boot`: `kernel.crypto = self`.
3.  **Legacy Bridge:**
    - Ändere `steward/crypto.py` so, dass es versucht, `kernel.crypto` zu nutzen, und nur als Fallback (oder gar nicht mehr) selbst importiert.

---

## 4. Action Plan for Opus

1.  **REPAIR:** Führe die "Immediate Fixes" (Sec. 2) aus. Prüfe mit `pytest --collect-only`.
2.  **MIGRATE PHASE 2a:**
    *   Erstelle `vibe_core/plugins/crypto` (Extract `ecdsa`).
    *   Migriere `steward_protocol` (Monolith -> Cartridge).
3.  **VERIFY:** Stelle sicher, dass Tests in den neuen `tests/` Ordnern laufen.

> **Message:** "Wir bauen das Flugzeug im Flug um. Phase 2a hält es in der Luft. Phase 2b gibt ihm Flügel. Phase 3 poliert den Lack."

---

## 5. Progress Update (Fractal Test Infrastructure & UI)

**Date:** 2025-12-05
**Status:** PHASE 2 COMPLETE

### 5.1 Fractal Test Infrastructure
**Implemented:** `@pytest.mark.vibe_plugins("plugin_id")`
- **Goal:** Lightweight, isolated tests without global mocks.
- **Result:** `tests/integration/test_kernel_markdown_interfaces.py` fully refactored.
- **Verification:** ✅ All 25 tests passing.

### 5.2 Plugin Migration Complete
All core plugins have been migrated to `vibe_core/plugins/`:
1.  `steward_protocol` (Core Logic)
2.  `test_mode` (Testing)
3.  `vedic_governance` (Varna/Ashrama)
4.  `interface` (Unified UI - replaces `envoy_ui`, `settings_ui`, `ephemeral_ui`)
5.  `test_orchestration` (Runner)
6.  `crypto` (ECDSA encapsulation)

**Legacy Cleanup:** `envoy_ui.py`, `settings_ui.py`, `ephemeral_ui.py` deleted.

### 5.3 UI Generation Status
**Verified via `scripts/verify_ui_generation.py`:**
- ✅ **`SETTINGS.md`**: Generated and functional.
- ✅ **`ENVOY.md`**: Generated and functional.
- ❌ **`EPHEMERAL.md`**: Currently disabled/broken (Renderer implementation pending fix).
