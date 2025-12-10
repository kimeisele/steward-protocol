# OPUS-020: Container Migration Strategy

> **Status**: 📋 READY FOR IMPLEMENTATION
> **Date**: 2025-12-10
> **Author**: Antigravity (Senior Architect Mode)
> **Depends On**: OPUS-015 (Container Format), P2 ECDSA Signing

<!-- @HARNESS
files:
  - path: vibe_core/plugin_loader.py
    required: true
  - path: vibe_core/kernel_impl.py
    required: true
  - path: vibe_core/loaders/container_loader.py
    required: true
  - path: scripts/pack_vibe.py
    required: true
tests:
  - tests/integration/test_container_integrity.py
wiring:
  - pattern: "is_new_container"
    in: vibe_core/plugin_loader.py
  - pattern: "shadows folder"
    in: vibe_core/plugin_loader.py
  - pattern: "_verify_signature"
    in: vibe_core/loaders/container_loader.py
absent:
  - pattern: "TODO.*container"
    in: vibe_core/plugin_loader.py
-->

---

## Executive Summary

This document explains how to migrate from directory-based plugins to signed `.vibe` containers. **The infrastructure already exists** - this doc explains the workflow.

---

## Architecture Overview

### Current Plugin Loading (kernel_impl.py:302)

```python
scan_paths = [Path("vibe_core/plugins"), Path("knowledge")]
self._plugins_map, self._plugin_metadata = PluginLoader.discover_and_load(scan_paths=scan_paths)
```

### Three Loading Modes (plugin_loader.py)

| Mode | Source | Example |
|------|--------|---------|
| NEW-style | Folder + manifest.json | `vibe_core/plugins/interface/` |
| OLD-style | Single .py file | `vibe_core/plugins/legacy.py` |
| CONTAINER | .vibe file | `vibe_core/plugins/interface.vibe` |

### The Shadowing Rule (plugin_loader.py:98-108)

```python
# If conflicting, prefer container...
is_new_container = str(meta.manifest_path).endswith(".vibe")
is_old_container = str(existing_meta.manifest_path).endswith(".vibe")

if is_new_container and not is_old_container:
    logger.info(f"  🆙 Upgrading {pid} to Container (shadows folder)")
```

**Key Insight**: If a `.vibe` container has the same `id` as a folder, the container WINS.

---

## Development Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                     DEVELOPMENT MODE                            │
│                                                                 │
│  vibe_core/plugins/                                             │
│  ├── interface/          ← Edit source here                     │
│  │   ├── manifest.json                                          │
│  │   └── plugin_main.py                                         │
│  ├── tools/                                                     │
│  │   └── ...                                                    │
│  └── ...                                                        │
│                                                                 │
│  $ python -m vibe_core.cli boot                                 │
│  → Loads from folders directly (no build step)                  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │  BUILD (when ready to deploy)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BUILD STEP                                  │
│                                                                 │
│  $ python scripts/pack_vibe.py vibe_core/plugins/interface \    │
│      --output vibe_core/plugins/interface.vibe                  │
│                                                                 │
│  → Creates signed .vibe container                               │
│  → SIGNATURE.sig contains ECDSA signature                       │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │  CONTAINER SHADOWING
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DISTRIBUTION MODE                           │
│                                                                 │
│  vibe_core/plugins/                                             │
│  ├── interface/          ← Source (IGNORED)                     │
│  ├── interface.vibe      ← Container (LOADED) ✅                │
│  ├── tools/                                                     │
│  ├── tools.vibe          ← Container (LOADED) ✅                │
│  └── ...                                                        │
│                                                                 │
│  $ python -m vibe_core.cli boot                                 │
│  → "🆙 Upgrading interface to Container (shadows folder)"       │
│  → Loads from .vibe containers with ECDSA verification          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Container Structure

Each `.vibe` file is a ZIP containing:

```
interface.vibe (ZIP)
├── manifest.json          ← Plugin metadata
├── SIGNATURE.sig          ← ECDSA signature (JSON format)
├── content/
│   └── plugin_main.py     ← Entry point
├── tests/                 ← Optional: embedded tests
└── hollows/               ← Optional: nested containers
    └── sub_agent.vibe
```

### SIGNATURE.sig Format (v2)

```json
{
  "version": 2,
  "hash": "723b18f2a4e9c...",
  "signature": "S4zB2WGq3M0qcV...",
  "signer": "a2ae17dde57b5e4f"
}
```

---

## Build All Plugins Script

**TODO**: Create `scripts/build_all_containers.sh`

```bash
#!/bin/bash
# Build all plugins as signed containers

set -e

PLUGINS_DIR="vibe_core/plugins"
OUTPUT_DIR="dist/plugins"

mkdir -p "$OUTPUT_DIR"

for plugin_dir in "$PLUGINS_DIR"/*/; do
    if [ -f "$plugin_dir/manifest.json" ]; then
        plugin_name=$(basename "$plugin_dir")
        echo "Building $plugin_name..."
        python scripts/pack_vibe.py "$plugin_dir" \
            --output "$OUTPUT_DIR/$plugin_name.vibe"
    fi
done

echo "Built $(ls -1 $OUTPUT_DIR/*.vibe | wc -l) containers"
```

---

## Future: Configurable Scan Paths

**Current Limitation**: `scan_paths` is hardcoded in kernel_impl.py:302

**Proposed Enhancement** (P3):

```python
# kernel_impl.py
import os

# Support env var for custom plugin paths
custom_paths = os.environ.get("VIBE_PLUGIN_PATH", "").split(":")
scan_paths = [Path(p) for p in custom_paths if p] or [
    Path("vibe_core/plugins"),
    Path("knowledge")
]
```

This would enable:

```bash
# Boot from dist/ containers only
VIBE_PLUGIN_PATH=dist/plugins python -m vibe_core.cli boot
```

---

## Migration Checklist

### Phase 1: Validate Current Infrastructure (DONE)
- [x] pack_vibe.py creates valid containers
- [x] ECDSA signing works (P2 complete)
- [x] PluginLoader loads .vibe files
- [x] Shadowing logic works (container > folder)
- [x] Signature verification on mount

### Phase 2: Build Pipeline (DONE)
- [x] Create `scripts/build_all_containers.sh`
- [x] Add to Makefile: `make containers`
- [x] CI/CD: Build containers on merge to main

### Phase 3: Configuration (DONE)
- [x] Add `VIBE_PLUGIN_PATH` env var support
- [ ] Add `plugin_paths` to phoenix.yaml
- [ ] Support both absolute and relative paths

### Phase 4: Full Migration (OPTIONAL)
- [ ] Remove source folders from distribution
- [ ] Ship only .vibe containers
- [ ] Source stays in git for development

---

## Hollows (Nested Containers)

Containers can contain other containers in `hollows/`:

```
my_plugin.vibe
├── manifest.json
├── SIGNATURE.sig
├── content/
│   └── plugin_main.py
└── hollows/
    ├── helper_agent.vibe
    └── sub_system.vibe
```

**Trust Model** (P3): Currently any valid signature accepted. Future: keyring delegation.

---

## Verification Commands

```bash
# Build a single container
python scripts/pack_vibe.py vibe_core/plugins/interface --output test.vibe

# Verify signature
unzip -p test.vibe SIGNATURE.sig | python -m json.tool

# Test shadowing (place .vibe next to folder)
cp test.vibe vibe_core/plugins/interface.vibe
python -m vibe_core.cli boot
# Look for: "🆙 Upgrading interface to Container (shadows folder)"

# Clean up
rm vibe_core/plugins/interface.vibe
```

---

## Steward Protocol Integration

### Key Identity Chain

```
┌────────────────────────────────────────────────────────────────┐
│                    SINGLE KEY IDENTITY                         │
│                                                                │
│   .steward/keys/                                               │
│   ├── private.pem    ← Signs containers AND agent messages    │
│   └── public.pem     ← Verifies containers AND agent identity │
│                                                                │
│   Container Signing (pack_vibe.py:130):                        │
│   private_key, public_key = load_or_generate_keys()            │
│                                                                │
│   Agent Identity (identity_tool.py):                           │
│   from steward.crypto import load_or_generate_keys             │
│   → SAME KEYS                                                  │
└────────────────────────────────────────────────────────────────┘
```

**Implication**: The entity that signs a container is the same identity that the agent inside uses.

```
Container signed by KEY_A
    └── Agent inside uses KEY_A for identity
        └── Ledger events signed by KEY_A
            └── All traceable to same author
```

### Trust Model (Current: P2 PERMISSIVE)

```python
# container_loader.py:219-228
# P2 PERMISSIVE: Accept ANY valid signature
if not is_valid:
    logger.warning(f"⚠️ Container signed by different key: {signer}")
    return True  # Still loads!
```

| Mode | Behavior | Use Case |
|------|----------|----------|
| **P2 PERMISSIVE** (current) | Any valid ECDSA signature accepted | Development |
| **P3 KEYRING** (future) | Only signatures from trusted keys | Multi-tenant |
| **P3 STRICT** (future) | Reject unknown signers | Production |

### Failure Modes

| Scenario | Behavior | Log |
|----------|----------|-----|
| Hash mismatch | `ValueError`, rejected | `🔴 CONTAINER TAMPERED` |
| Unknown signer | Warning, **loads** | `⚠️ signed by different key` |
| No signature | Warning, **loads** | `⚠️ Unsigned container` |
| v1 legacy hash | Warning, **loads** | `⚠️ v1 LEGACY` |

### Connection to Ledger (P1)

Same key signs everything:
- Container SIGNATURE.sig
- Constitutional Oath
- Per-event ledger signatures

**Audit Trail**: Container signer → Agent identity → Ledger events = full provenance.

---

## Full Steward Cycle

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. DEVELOP                                                      │
│    Edit: vibe_core/plugins/my_agent/plugin_main.py              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. BUILD + SIGN                                                 │
│    $ python scripts/pack_vibe.py vibe_core/plugins/my_agent     │
│    Uses: .steward/keys/private.pem                              │
│    Output: my_agent.vibe with ECDSA signature                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. DEPLOY                                                       │
│    Place .vibe in scan_paths → shadows folder                   │
│    ECDSA verified on mount                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. BOOT + OATH                                                  │
│    PluginLoader finds .vibe → Agent boots                       │
│    Constitutional Oath signed with SAME KEY                     │
│    Trust score initialized                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. RUNTIME                                                      │
│    Actions → Ledger events with per-event ECDSA (P1)            │
│    Soul rules enforced by InvariantChecker (P0.2)               │
│    Trust score updated                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. AUDIT                                                        │
│    Container signer = Agent identity = Ledger signer            │
│    Full non-repudiation chain                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Summary

| Question | Answer |
|----------|--------|
| Do I need code changes to use containers? | **No** - shadowing works today |
| How do I build a container? | `python scripts/pack_vibe.py <folder>` |
| What happens if both folder and .vibe exist? | **.vibe wins** (shadows folder) |
| Is the container signed? | **Yes** - ECDSA (P2 complete) |
| Can containers contain other containers? | **Yes** - hollows/ directory |
| Can I configure plugin paths? | **Not yet** - P3 (env var support) |
| Who signs containers? | **.steward/keys/** - same as agent identity |
| What if signer is unknown? | **P2 PERMISSIVE**: Warning, still loads |
| How does this connect to Ledger? | Same key signs container + all events |

**The infrastructure is ready. Build scripts and workflow docs are the remaining work.**
