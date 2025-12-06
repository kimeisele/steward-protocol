# MARKDOWN UI ANALYSIS REPORT

## 1. Executive Summary
The "Markdown UI" system is currently split between two architectures:
1.  **Direct Rendering** (Robust): Used by `ENVOY.md`. The renderer generates content and writes it directly (via `EnvoySync`).
2.  **Delegated Rendering** (Fragile): Used by `AGENTS.md`, `CITYMAP.md`, `HELP.md`, etc. The renderer submits a task to the `scribe` agent, which then asynchronously generates and publishes the file.

**Current Status**: The "Direct" files likely work well, while the "Delegated" files are prone to staleness or failure if the `scribe` agent is not running, the scheduler is backed up, or the complex sandbox/publish logic fails.

## 2. Architecture Overview

### A. The Interface Plugin (`vibe_core/plugins/interface/`)
The `InterfacePlugin` acts as the "Window Manager". It loads renderers from `renderers/` and triggers their `render()` method on every kernel tick (`on_tick_post`).

### B. Renderer Types

#### Type 1: Direct Renderers
*   **Example**: `EnvoyRenderer` (`renderers/envoy.py`)
*   **Mechanism**:
    1.  `render()` called by Plugin.
    2.  Renderer reads state (pending tasks, history).
    3.  Renderer generates Markdown string.
    4.  Renderer writes file using `EnvoySync`.
*   **Pros**: Synchronous, reliable, immediate feedback.
*   **Cons**: Blocks kernel tick if generation is slow (though currently fast).

#### Type 2: Scribe Delegating Renderers
*   **Example**: `AgentsRenderer` (`renderers/agents.py`)
*   **Mechanism**:
    1.  `render()` called by Plugin.
    2.  Renderer checks `update_interval` (default 1h).
    3.  Renderer **submits a task** to the `scribe` agent.
    4.  `scribe` agent picks up task (asynchronously).
    5.  `scribe` executes tool (e.g., `scribe.agents_renderer`).
    6.  Tool writes to **sandbox** (`/tmp/...`).
    7.  `scribe` calls `publish_artifact` to copy to root.
*   **Pros**: Offloads work from kernel tick.
*   **Cons**:
    *   High latency.
    *   Fails if `scribe` is dead.
    *   Fails if scheduler is full.
    *   Fails if file permissions/sandbox logic breaks.
    *   Hard to debug (silent failures).

## 3. File Inventory & Status

| File | Renderer | Type | Status Risk |
|------|----------|------|-------------|
| `ENVOY.md` | `EnvoyRenderer` | **Direct** | LOW |
| `SETTINGS.md` | `SettingsRenderer` | **Direct** | LOW (likely) |
| `DASHBOARD.md` | `DashboardRenderer` | **Direct** | LOW (likely) |
| `AGENTS.md` | `AgentsRenderer` | Delegated | **HIGH** |
| `CITYMAP.md` | `CityMapRenderer` | Delegated | **HIGH** |
| `HELP.md` | `HelpRenderer` | Delegated | **HIGH** |
| `INDEX.md` | `IndexRenderer` | Delegated | **HIGH** |
| `RAG.md` | `RagRenderer` | Delegated | **HIGH** |
| `README.md` | `ReadmeRenderer` | Delegated | **HIGH** |

## 4. Findings & Issues

1.  **Scribe Dependency**: The "Delegated" files are not true UI; they are "periodic reports". If the user wants a responsive UI, delegation is the wrong pattern.
2.  **Deprecated Code**: `MarkdownUIManager` in `vibe_core/markdown_ui_manager.py` is deprecated but still exists. It duplicates some logic for `SETTINGS.md` and `ENVOY.md`.
3.  **Agent Writes**: The `scribe` agent writes to files via `publish_artifact`. This is a valid pattern for *content*, but for *UI* (which needs to reflect system state immediately), it is too slow.

## 5. Architectural Decision: Holistic Plugin-Only UI
**Concept**: "Plugins ARE System Agents."

We are moving to a **Holistic Plugin Architecture** where the `InterfacePlugin` encapsulates the entire UI domain. It does not delegate to worker agents. It *is* the UI Agent.

### The "Plugin as Agent" Model
*   **Synchronous & Privileged**: Unlike standard agents, Plugins run inside the Kernel process. They have direct, synchronous access to memory (Registry, Topology, Ledger).
*   **Robustness**: They don't die. They don't get stuck in queues. They execute on every tick (or scheduled interval).
*   **Scalability**: By decoupling UI from the "Worker Agent" pool, the UI remains responsive even if the system is under heavy load (1000 agents working).

### The New Boundary
1.  **UI (The Dashboard)**: Owned by `InterfacePlugin`.
    *   Renders `AGENTS.md`, `CITYMAP.md`, `ENVOY.md` directly.
    *   Reads state directly from Kernel.
    *   **Zero dependency on Scribe.**
2.  **Work (The Factory)**: Owned by Agents.
    *   Agents (like `analyst`) do the heavy lifting (reading 100k LOC).
    *   Agents report results to the Ledger/Memory.
    *   The UI Plugin *reads* those results and displays them.

## 6. Migration Plan

1.  **Refactor Renderers**: Move logic from `vibe_core/cartridges/system/scribe/tools/*_renderer.py` directly into `vibe_core/plugins/interface/renderers/*.py`.
2.  **Remove Delegation**: Delete `ScribeDelegatingRenderer` and make all renderers inherit from `BaseRenderer` directly.
3.  **Direct State Access**: Ensure renderers have access to `kernel.agent_registry`, `kernel.topology`, etc.
4.  **Cleanup**: Remove the now-redundant renderer tools from `scribe`.

## 7. Next Steps (Analyst Role)
*   Verify `SettingsRenderer` and `DashboardRenderer` implementation to confirm they are Direct.
*   Deep dive into `scribe`'s `publish_artifact` to understand why it might be failing (permissions?).
