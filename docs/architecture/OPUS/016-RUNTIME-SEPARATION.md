
# OPUS-016: Runtime Separation (The Thin Kernel)

## Status
- **Date**: 2025-12-11
- **Author**: Antigravity
- **Status**: ACTIVE (Binary/AI Paradox Documented)
- **Preceded By**: OPUS-015 (Container Format)

<!-- @HARNESS
files:
  - path: vibe_core/kernel_impl.py
    required: true
  - path: vibe_core/plugin_loader.py
    required: true
  - path: vibe_core/loaders/container_loader.py
    required: true
tests:
  - tests/integration/test_kernel_boot.py
wiring:
  - pattern: "RealVibeKernel"
    in: vibe_core/kernel_impl.py
  - pattern: "PluginLoader"
    in: vibe_core/plugin_loader.py
  - pattern: "ContainerMounter"
    in: vibe_core/loaders/container_loader.py
-->

## 1. The Problem: Source-Based Execution
Currently, VibeOS runs directly from the source code (`vibe_core/`). To "install" the system, a user must `git clone` the repository. This exposes the entire brain, internal organs, and development tools to the end user. It violates the "Product" principle.

## 2. The Goal: Artifact-Based Execution
We want a separation between:
1.  **The Factory** (Source Code, Build System): Where Holons are born.
2.  **The Runtime** (Thin Kernel): A minimal runner that executes Holons.

The Runtime should be a single executable (or minimal pip package) that:
- Does NOT contain `vibe_core/cartridges/system/*` (Source).
- EXPECTS to find `.vibe` containers in a `dist/` or `library/` folder.
- Can be upgraded by simply replacing the `.vibe` files.

## 3. The Architecture: "The Cassette Player"
The Kernel (`vibe_core`) becomes the "Cassette Player".
The Agents/Plugins (`.vibe`) become the "Cassettes".

### 3.1 The Distribution Folder (`dist/`)
Ideally, a user's installation looks like this:

```text
~/vibe-os/
├── vibe_kernel         # The executable (runner)
├── config.yaml         # User configuration
└── library/            # The Holon Library
    ├── herald.vibe     # System Agent
    ├── scribe.vibe     # System Agent
    ├── genesis.vibe    # Cognitive Pack
    └── my_plugin.vibe  # User Plugin
```

### 3.2 The Boot Process
1.  **Kernel Start**: `vibe_kernel` starts up.
2.  **Library Scan**: Kernel scans `library/*.vibe`.
3.  **Mounting**: Kernel mounts found Holons (lazy loading).
4.  **Discovery**: Kernel discovers Agents and Plugins from manifests.
5.  **Execution**: System comes alive.

## 4. Migration Plan

### Phase 1: The Build (Factory)
Ensure all System Agents and Core Plugins are packable into `.vibe` (Completed in OPUS-015).

### Phase 2: The Loader (Runtime)
Update `UnifiedLoader` to *prefer* external `library/` path over internal `vibe_core/cartridges/` path.
Actually, enforcing "Runtime Separation" means the Kernel shouldn't even *have* the internal cartridges in its distribution.

### Phase 3: The Installer
Create a script that:
1.  Installs the Kernel (pip install vibe-core?).
2.  Downloads the "System Holons" (Herald, Scribe, Genesis) from a release registry.
3.  Places them in `~/.vibe/library`.

## 5. Decision Points
- **Distribution Method**: PyPI? Binary (PyInstaller)? Docker?
    - *Decision*: Start with PyPI package + `vibe init` command to download default Holons.
- **Versioning**: How do we ensure Kernel v2.0 doesn't break Herald v1.0?
    - *Answer*: Semantic Versioning in `manifest.json`. Kernel checks `min_kernel_version`.

## 6. The Binary/AI Paradox (RESOLVED)

### The Paradox
The system needs offline AI intelligence (LLM inference, semantic search, embeddings) but also needs to be:
1. **Fast to start** - No 30-second load times
2. **Small to distribute** - Not a 2GB binary
3. **Portable** - Works on any system without GPU/CUDA setup

Heavy dependencies like `torch`, `transformers`, `sentence-transformers` conflict with these goals.

### The Solution: Separation of Concerns

```text
┌─────────────────────────────────────────────────────────────┐
│                    THIN KERNEL (Binary)                      │
│  - Fast boot (~2 seconds)                                    │
│  - Small size (~50MB)                                        │
│  - Core scheduling, routing, execution                       │
│  - NO ML dependencies (torch, numpy excluded)                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    FAT HOLONS (Containers)                   │
│  - semantic.vibe     → Sentence Transformers + Embeddings   │
│  - llm_local.vibe    → llama-cpp for local inference        │
│  - vision.vibe       → Image understanding                  │
│  - Each holon declares its own dependencies                  │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Status

| Component | Location | Dependencies | Status |
|-----------|----------|--------------|--------|
| Kernel Binary | `scripts/build_binary.py` | Minimal (excludes ML) | ✅ Working |
| Container Loader | `vibe_core/loaders/container_loader.py` | None | ✅ Working |
| PROJECT JNANA | `pyproject.toml:43-45` | sentence-transformers (commented) | 📋 Deferred |
| Local LLM | `[project.optional-dependencies]` | llama-cpp-python | 📋 Optional |

### Why Dependencies Are Commented Out

In `pyproject.toml`:
```python
# Semantic AI (PROJECT JNANA) - Not yet implemented, commented out for now
# "sentence-transformers>=2.2.0",
# "numpy>=1.24.0",
```

**This is BY DESIGN, not a bug.**

The kernel doesn't need these dependencies because:
1. AI capabilities will be packaged in `.vibe` containers
2. Users who need semantic search can install `semantic.vibe`
3. Users who don't need it get a fast, lean kernel

### How to Add AI Capabilities

1. Create a `.vibe` container with the AI capability
2. Include dependencies in the container's `manifest.json`
3. Use `execution.mode: "process"` for isolation
4. The kernel loads the container on-demand

Example `semantic.vibe/manifest.json`:
```json
{
  "id": "semantic",
  "type": "plugin",
  "execution": {
    "mode": "process",
    "runtime": "python3.11"
  },
  "dependencies": {
    "sentence-transformers": ">=2.2.0",
    "numpy": ">=1.24.0"
  }
}
```

## 7. Next Steps
1.  Modify `AgentLoader` / `PluginLoader` to accept a configurable `library_path`.
2.  Verify booting from `library_path` ONLY (simulate by renaming source folders).
3.  Implement PROJECT JNANA as a `.vibe` container (not kernel dependency).
