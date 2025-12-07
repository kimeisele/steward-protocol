# REAL TECH DEBT AUDIT: The "Half-Baked" Reality
> **Date:** 2025-12-07
> **Scope:** Entire Codebase (Legacy & Modern)
> **Auditor:** Antigravity (Senior Agent)
> **Status:** UNVARNISHED TRUTH

## 1. THE VERDICT
You are correct. While `vibe_core` is maturing, the codebase handles "legacy rot" by ignoring it rather than removing it. The "Phoenix Migration" is only fixing the *Configuration* layer, but the *Application* layer is rife with unfinished business.

**The "Half-Baked" List:**
1.  **The `steward/` Directory:** A 47-file zombie.
2.  **The API Monolith (`gateway/api.py`):** 777 lines of extensive logic that should be broken into plugins.
3.  **The Twin CLIs:** `steward-cli` (Admin) and `scripts/vibe_cli.py` (Client) - completely disconnected.
4.  **The "Ritual" Code:** `daily_ritual.py` exists but is likely not integrated into the Kernel's event loop.

---

## 2. DETAILED FINDINGS

### A. The `steward/` Graveyard (CRITICAL DEBT)
The `steward/` directory contains substantial logic that *appears* to be legacy code from a previous architectural iteration ("Project Iron Shell"?).

*   **Evidence:**
    *   `steward/daily_ritual.py` (521 lines): Implements complex "Sunrise/Midday/Sunset/Archive" phases. **Likely Dead Code**: Unless `vibe_core` imports this, it's just a fantasy script.
    *   `steward/agent_metadata.py`: Likely superseded by `vibe_core/phoenix/sections/agents/` manifests.
    *   `steward/vibe_launcher.py`: Another boot script? We already have `boot.py`.

*   **Action:** This entire directory must be audited for salvageable logic (e.g., the ritual phases) and then **DELETED**. The logic should ideally be a `SargaPlugin` in `vibe_core/plugins/sarga_cycle/`.

### B. The Gateway Monolith (`gateway/api.py`)
This file is doing too much. It is NOT following the fractal architecture.

*   **Violations:**
    *   **Path Hacking:** `sys.path.insert(0, str(PROJECT_ROOT))` (Line 24). This is fragile.
    *   **Hardcoded Imports:** Imports `UniversalProvider` directly (Line 30).
    *   **Mixed Concerns:** Handles WebSocket connection management, Visa application logic, Yagya rituals, and Static file serving all in one file.
    *   **Implicit Auth:** Authorization logic (Lines 129-132) is hardcoded, not a middleware.

*   **Action:**
    *   Move `gateway/` to `interface/gateway`.
    *   Refactor `api.py` to use `Kernel.get_plugin("interface").register_routes()`.
    *   Extract `WebSocketManager` to `vibe_core/io/websocket.py`.

### C. The Tale of Two CLIs
We have two "interfaces" that don't talk to each other.

1.  **`steward-cli` (The Real One):**
    *   Wraps `vibe_core/cli.py`.
    *   Admin tool.
    *   Status: **Healthy**.

2.  **`scripts/vibe_cli.py` (The Toy):**
    *   "Project Iron Shell" branding.
    *   Talks to `localhost:8000`.
    *   Hardcoded "Vedic Palette" colors.
    *   Status: **Half-Baked Legacy**.

*   **Action:** Delete `scripts/vibe_cli.py` or promote it to `interface/cli/client.py` if a remote client is actually needed.

### D. Code Rot Indicators
*   **TODO Count:** 46 TODOs in `vibe_core`. This is acceptable but indicates unfinished refactors.
*   **Testing Gaps:** `tests/` exists, but does it cover `gateway/api.py`? Does it cover `daily_ritual.py`? Unlikely.

---

## 3. REMEDIATION PLAN (The Real Work)

The Master Plan mentioned "Battles", but missed the "Cleanup Wars".

### Immediate Actions (Next 24 Hours)
1.  **Audit `steward/daily_ritual.py`:** Confirm if any logic is unique/valuable. If so, move to `vibe_core/plugins/sarga_cycle/`.
2.  **Delete `steward/`:** Once verified, `rm -rf steward/`. This cleans up 47 files of noise.
3.  **Delete `scripts/vibe_cli.py`:** Use `steward-cli` or `curl` for testing. We don't need a maintenance burden client script.
4.  **Refactor `gateway/api.py`:** This is a larger task (Battle 8), but we should start by moving the folder to `interface/gateway` to match the architecture map.

### Strategic Shift
Stop treating `steward/` as a valid part of the codebase. It is an archive. The only source of truth is `vibe_core/`.
