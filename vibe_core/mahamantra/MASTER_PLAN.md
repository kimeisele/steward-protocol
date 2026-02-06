# MAHAMANTRA MASTER PLAN: HOLISTIC CONSOLIDATION (REVISED)

**STATUS:** APPROVED FOR EXECUTION
**TARGET:** O(1) Architecture, Zero Fragmentation, Vedic Cohesion
**METHOD:** Fractal Discovery (Folder = Existence)

---

## 1. THE DIAGNOSIS (The "Rotz" Analysis)

The `vibe_core/mahamantra` folder has become a dumping ground.
*   **Routing Complexity:** `__init__.py` contains ~300 lines of `if/elif` chains.
*   **Shadowed Logic:** The robust `fractal_getattr` in `wiring.py` is blocked by manual legacy code.
*   **Top-Level Pollution:** Logic files (`_mahamantra_lotus.py`) sit at the root level.

## 2. THE ARCHITECTURE (Soll-Zustand)

We enforce **Fractal Discovery** using `vibe_core.mahamantra.substrate.wiring`.

### RULE: FOLDER = EXISTENCE
*   If a module is in a folder (e.g. `genesis/brahma`), it is automatically discoverable as `mahamantra.genesis.brahma`.
*   NO manual imports in `__init__.py`.

### RULE: HYBRID BACKWARDS COMPATIBILITY
*   Legacy exports (constants like `WORDS`, aliases like `MahamantraLotus`) are defined in a **local dictionary** in `__init__.py`.
*   `__getattr__` uses `wiring.create_hybrid_getattr` to check:
    1.  Fractal Discovery (Folder Scan)
    2.  Legacy Lookup (Dictionary)

---

## 3. EXECUTION PLAN

### PHASE 1: CLEAN THE ROOT (The Switch)
*   **Action:** Rewrite `vibe_core/mahamantra/__init__.py`.
*   **Logic:**
    *   Define `LEGACY_EXPORTS` dictionary (explicit mapping).
    *   Replace manual `__getattr__` with `wiring.create_hybrid_getattr(__file__, LEGACY_EXPORTS)`.
*   **Result:** ~300 lines of code become ~50 lines of configuration. O(1) lookup + Dynamic Discovery.

### PHASE 2: TOP-LEVEL CLEANUP (De-clutter)
*   Move `_mahamantra_lotus.py` -> `substrate/lotus_core.py`.
*   Move `_lotus.py` -> `substrate/lotus_types.py`.
*   Move `_types.py` -> `seed/types.py`.
*   *Note:* The Registry/Wiring handles these moves automatically if we update `LEGACY_EXPORTS`.

### PHASE 3: PROTOCOL PURITY
*   Ensure every Protocol in `protocols/` has a living implementation.
*   (This is covered by the Audit Loop).

---

## 4. IMMEDIATE NEXT STEP

I will execute **PHASE 1** immediately:
1.  Analyze `__init__.py` to build the `LEGACY_EXPORTS` map.
2.  Rewrite `__init__.py`.