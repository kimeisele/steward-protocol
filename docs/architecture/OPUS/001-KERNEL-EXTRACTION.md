# VISNU KERNEL - LOCKED

**Status:** ✅ LOCKED (ETERNAL)
**Last Updated:** 2025-12-11
**Security Ring 0:** 3399 LOC (7 files)
**Protection:** Pre-commit auto-restore + CI hash verification

> **SECURITY RING 0** - Life, Death, and Rights are protected.
> All new features MUST be plugins. No exceptions.

<!-- @HARNESS
files:
  - path: vibe_core/kernel_impl.py
    required: true
  - path: .pre-commit-config.yaml
    required: true
wiring:
  - pattern: "register_agent"
    in: vibe_core/kernel_impl.py
  - pattern: "submit_task"
    in: vibe_core/kernel_impl.py
  - pattern: "grant_capability"
    in: vibe_core/kernel_impl.py
  - pattern: "broadcast_event"
    in: vibe_core/kernel_impl.py
  - pattern: "get_capabilities"
    in: vibe_core/kernel_impl.py
absent:
  - pattern: "TODO.*kernel"
    in: vibe_core/kernel_impl.py
config:
  - section: kernel
semantic:
  - type: method_exists
    name: "kernel_boot_method"
    class: RealVibeKernel
    method: boot
    in: vibe_core/kernel_impl.py
  - type: method_exists
    name: "kernel_register_agent"
    class: RealVibeKernel
    method: register_agent
    in: vibe_core/kernel_impl.py
-->

---

## Status

| Aspect | Status | Evidence |
|--------|--------|----------|
| Kernel Locked | ✅ | `KERNEL_IS_LOCKED` constant in `kernel_impl.py` |
| Pre-commit Hook | ✅ | `.pre-commit-config.yaml` rule |
| No New Features | ✅ | Manual verification of recent commits |

## Implementation

The kernel is now strictly limited to core orchestration logic. All new features are implemented as plugins.

---

## Protection Mechanism

Pre-commit hook in `.pre-commit-config.yaml` **AUTO-RESTORES** Ring 0 files:
```yaml
- id: kernel-is-eternal
  name: Kernel Auto-Restore (VISNU)
  entry: scripts/governance/restore_kernel.sh
  language: script
  files: ^vibe_core/(kernel_impl|kernel_ops|plugin_protocol|plugin_loader|narasimha|capability_registry|bridge)\.py$
```

### Security Ring 0 Files

| Category | File | LOC | Purpose |
|----------|------|-----|---------|
| Core | `kernel_impl.py` | 1505 | Kernel orchestration |
| Core | `kernel_ops.py` | 326 | Delegated operations |
| Plugins | `plugin_protocol.py` | 402 | Plugin interface |
| Plugins | `plugin_loader.py` | 381 | Plugin loading |
| Security | `narasimha.py` | 414 | Kill-Switch (Sword) |
| Security | `capability_registry.py` | 343 | Permissions (Shield) |
| Security | `bridge.py` | 28 | Constitution (Gate) |
| **TOTAL** | | **3399** | |

CI also runs `verify_kernel.py --verify` as backup hash check.

**To bypass (emergency only):** `git commit --no-verify`

See: `docs/architecture/OPUS/024-KERNEL-PROTECTION-AUDIT.md`

---

## What Kernel Provides (Eternally)

| Feature | Method/Property |
|---------|-----------------|
| Agent Registration | `register_agent()` |
| Task Scheduling | `submit_task()`, `tick()` |
| Plugin Attachment | `kernel.X = self` in on_boot() |
| Capability Management | `grant_capability()`, `revoke_capability()` |
| Event Subscription | `subscribe_to_events()`, `broadcast_event()` |
| GAD-000 Compliance | `get_capabilities()`, `get_system_status()` |
| Lifecycle Hooks | `boot()`, `tick()`, `shutdown()` |
| State Access | `ledger`, `scheduler`, `agent_registry` |

---

## How to Add New Features

**Create a plugin:**
```
vibe_core/plugins/your_feature/
├── manifest.json
├── __init__.py
└── plugin_main.py
```

**Attach to kernel:**
```python
def on_boot(self, kernel):
    kernel.your_feature = self
```

---

## Extraction History

| Date | Phase | LOC Before | LOC After |
|------|-------|------------|-----------|
| 2025-12-06 | Governance wrappers | 1705 | 1662 |
| 2025-12-06 | ToolsPlugin | 1662 | 1553 |
| 2025-12-09 | Final audit | 1553 | 1410 |
| 2025-12-09 | **LOCKED** | 1410 | **ETERNAL** |
| 2025-12-11 | Protection audit | 2614 | 2614 (4 files) |
| 2025-12-11 | **SECURITY RING 0** | 2614 | **3399 (7 files)** |

---

**Krishna's Blessing:** The kernel is VISNU - eternal and unchanging.
