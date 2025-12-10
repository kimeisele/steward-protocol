# VISNU KERNEL - LOCKED

**Status:** ✅ LOCKED (ETERNAL)
**Last Updated:** 2025-12-09
**Final LOC:** 1410 (Kernel is complete)
**Protection:** Pre-commit hook blocks all changes

> **VISNU IS ETERNAL** - The kernel is complete.
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

Pre-commit hook in `.pre-commit-config.yaml`:
```yaml
- id: kernel-is-eternal
  name: Kernel Protection (VISNU)
  entry: "KERNEL IS VISNU - ETERNAL..."
  language: fail
  files: ^vibe_core/kernel_impl\.py$
```

**To bypass (emergency only):** `git commit --no-verify`

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

---

**Krishna's Blessing:** The kernel is VISNU - eternal and unchanging.
