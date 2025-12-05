# DER TOTALE KRIEG - Master Plan V2 (The Senior Plan)

> **Codename:** Operation Phoenix Rising V2
> **Author:** Gemini (Senior Planner)
> **Based on:** Opus (Architect) Draft
> **Date:** 2025-12-05
> **Status:** APPROVED FOR EXECUTION

---

## 0. EXECUTIVE SUMMARY

This V2 plan refines the original strategy by answering critical architectural questions and enforcing strict separation of concerns between **Platform** (Kernel/Cortex) and **Content** (Agents/Knowledge).

**The Core Philosophy:**
*   **vibe_core** is the Operating System (Platform).
*   **agents** are the Applications (Content).
*   **knowledge** is the Data (Content).
*   **interface** is the I/O Layer.

Everything else (`provider/`, `services/`, `steward/`, `agent_city/`) is legacy noise that must be eliminated or consolidated.

---

## 1. ARCHITECTURAL DECISIONS (The 5 Answers)

### 1.1 Agent Location: Top-Level `agents/`
**Decision:** Agents reside in a top-level `agents/` directory.
**Reasoning:** Agents are *applications* running ON the kernel. Putting them inside `vibe_core` would couple the OS with the User Space.
**Structure:**
```
agents/
├── system/    # Critical OS Agents (Envoy, Herald, Watchman) - ex steward/
└── city/      # User/Community Agents - ex agent_city/
```

### 1.2 Knowledge Location: Top-Level `knowledge/`
**Decision:** Knowledge resides in a top-level `knowledge/` directory.
**Reasoning:** Knowledge is configuration/data. It should be editable without touching the kernel code.
**Nuance:** The *Loader* and *Protocols* for knowledge belong in `vibe_core/cortex/knowledge`. The *YAML files* stay in `knowledge/`.

### 1.3 Playbook vs Circuit: WE NEED BOTH
**Decision:** Keep both as distinct **Cortex Engines**.
**Reasoning:**
*   **Playbooks (DAGs):** Deterministic, linear, robust. Good for "dumb" tasks.
*   **Circuits (State Machines):** Neuro-symbolic, looping, complex. Good for "cognitive" tasks.
**Implementation:**
*   `vibe_core/cortex/engines/playbook_engine.py`
*   `vibe_core/cortex/engines/circuit_engine.py`

### 1.4 Phoenix Config: The Fractal Standard
**Decision:** Phoenix *is* the configuration standard.
**Reasoning:** The Section pattern (Folder + Manifest + Code) works. We will not change it. Instead, we enforce that *all* components (Cortex, Agents) use Phoenix for their config loading.

### 1.5 Nano City Spawning: Phase 3+
**Decision:** Defer to Phase 3.
**Reasoning:** Dynamic sub-universes require a stable single universe first. We focus on consolidating the current mess before recursing.

---

## 2. THE NEW MAP (Target Architecture)

```
steward-protocol/
│
├── vibe_core/                    # == THE PLATFORM ==
│   ├── kernel_impl.py            # The Kernel
│   ├── plugins/                  # Kernel Plugins (Hooks)
│   ├── cortex/                   # The Brain (Engines)
│   │   ├── engines/              # LLM, Circuit, Playbook, Semantic
│   │   ├── memory/               # Vector DB, Short-term
│   │   └── protocols/            # Cognitive Interfaces
│   ├── phoenix/                  # Configuration System
│   └── tools/                    # Tool Registry
│
├── agents/                       # == THE APPLICATIONS ==
│   ├── system/                   # Envoy, Herald, Watchman
│   └── city/                     # Ambassador, Analyst, etc.
│
├── knowledge/                    # == THE DATA ==
│   ├── concepts/                 # Semantic Maps
│   ├── intents/                  # Routing Rules
│   └── circuits/                 # Circuit Definitions (YAML)
│
├── interface/                    # == THE I/O ==
│   ├── gateway/                  # HTTP API
│   └── cli/                      # Command Line
│
└── data/                         # == THE STATE ==
    ├── ledger/                   # Immutable History
    └── registry/                 # Runtime State
```

---

## 3. THE 9 BATTLES (Execution Plan)

### ⚔️ Battle 1: CORTEX FOUNDATION (The Brain)
**Objective:** Establish `vibe_core/cortex` as the home for cognitive engines.
1.  Create `vibe_core/cortex/{engines,memory,protocols}`.
2.  Migrate `provider/semantic_router.py` → `vibe_core/cortex/engines/semantic.py`.
3.  Migrate `provider/reflex_engine.py` → `vibe_core/cortex/engines/reflex.py`.
4.  Migrate `vibe_core/circuit_executor.py` → `vibe_core/cortex/engines/circuit.py`.
5.  Migrate `services/llm_engine.py` → `vibe_core/cortex/engines/llm.py`.

### ⚔️ Battle 2: KNOWLEDGE STANDARDIZATION
**Objective:** Fraktalize the `knowledge/` directory.
1.  Create `knowledge/manifest.json`.
2.  Move `vibe_core/playbook/circuits/*.yaml` → `knowledge/circuits/`.
3.  Standardize `knowledge/concepts/` and `knowledge/intents/`.
4.  Implement `vibe_core/cortex/knowledge_loader.py`.

### ⚔️ Battle 3: AGENT UNIFICATION
**Objective:** Consolidate all agents into `agents/`.
1.  Create `agents/system/` and `agents/city/`.
2.  Move `steward/system_agents/*` → `agents/system/`.
3.  Move `agent_city/registry/*` → `agents/city/`.
4.  Update `AgentLoader` to scan the new paths.
5.  **CRITICAL:** Ensure `Envoy` (in `agents/system/envoy`) imports engines from `vibe_core.cortex`.

### ⚔️ Battle 4: PROVIDER ELIMINATION
**Objective:** Kill the `provider/` directory.
1.  Refactor `gateway/api.py` to use `kernel.run_agent("envoy", ...)` instead of `UniversalProvider`.
2.  Refactor `vibe_core/cli.py` to do the same.
3.  Move any remaining logic from `provider/universal_provider.py` to `agents/system/envoy/agent.py`.
4.  DELETE `provider/`.

### ⚔️ Battle 5: SERVICES CLEANUP
**Objective:** Kill the `services/` directory.
1.  Ensure `llm_engine` is fully migrated to Cortex.
2.  DELETE `services/`.

### ⚔️ Battle 6: TOOL REGISTRY
**Objective:** Centralize tool definitions.
1.  Audit all tools in `vibe_core/tools` and agent directories.
2.  Ensure all tools follow the Protocol.
3.  (Optional) Move shared tools to `vibe_core/tools/standard/`.

### ⚔️ Battle 7: DATA STRUCTURE
**Objective:** Clean up `data/`.
1.  Define clear subfolders: `ledger`, `registry`, `cache`, `models`.
2.  Update `.gitignore`.

### ⚔️ Battle 8: INTERFACE LAYER
**Objective:** Consolidate Entry Points.
1.  Move `gateway/` → `interface/gateway/`.
2.  Move `vibe_core/cli.py` → `interface/cli/main.py`.

### ⚔️ Battle 9: FINAL POLISH
**Objective:** Cleanup and Documentation.
1.  Delete empty directories (`steward/`, `agent_city/`).
2.  Update `README.md` and `ARCHITECTURE.md`.
3.  Run full system verification.

---

## 4. MIGRATION STRATEGY

We will execute this in **Atomic Steps**.

1.  **Phase A (Battles 1-2):** Build the new Platform (Cortex/Knowledge) *alongside* the old one. No breaking changes yet.
2.  **Phase B (Battle 3):** Move Agents. This breaks imports. Fix them immediately.
3.  **Phase C (Battles 4-5):** Switch Entry Points to use Agents directly. Delete legacy code.
4.  **Phase D (Battles 6-9):** Cleanup and Polish.

---

## 5. VERIFICATION

After EACH Battle:
1.  `pytest tests/` (Must pass)
2.  `python scripts/governance/verify_kernel.py --verify` (Integrity check)
3.  `python boot.py` (System boot check)

---

## 6. CRITICAL QUESTIONS ANSWERED

| **Question** | **Answer** |
|--------------|------------|
| Is `agent_city` a plugin? | **No.** It is legacy. Its agents will move to `agents/city/`. |
| Is `provider` a plugin? | **No.** It is an anti-pattern. It will be eliminated. Envoy becomes the router. |
| Is `steward` a plugin? | **No.** The agents move to `agents/system/`. The docs stay as `docs/`. |
| Is `gateway` a plugin? | **No.** It is an interface. Entry points are not plugins. |
| Where do circuits live? | **Data:** `knowledge/circuits/`. **Code:** `vibe_core/cortex/engines/circuit.py`. |

---

**Signed:** Gemini (Senior Planner)
**Date:** 2025-12-05
