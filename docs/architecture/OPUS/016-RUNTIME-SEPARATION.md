
# OPUS-016: Runtime Separation (The Thin Kernel)

## Status
- **Date**: 2025-12-09
- **Author**: Antigravity
- **Status**: DRAFT
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

## 6. Next Steps
1.  Modify `AgentLoader` / `PluginLoader` to accept a configurable `library_path`.
2.  Verify booting from `library_path` ONLY (simulate by renaming source folders).
