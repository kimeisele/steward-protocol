# OPUS-087: PRANA - Plugin Pulse Architecture

**Scope:** Refactor Heartbeat to be "dumb" like the Kernel  
**Philosophy:** Heartbeat receives, Plugins execute. No business logic in scheduler.  
**Status:** 🚧 PLANNED (Technical Debt acknowledged)

---

## The Vision

```
┌─────────────────────────────────────────────────┐
│  HEARTBEAT.PY  (currently 605 LOC)              │
│  ❌ Contains: MANAS, TaskManager, Git, Paper UI │
└─────────────────────────────────────────────────┘
                     ▼ REFACTOR
┌─────────────────────────────────────────────────┐
│  PRANA  (~50 LOC - like Kernel)                 │
│  ✅ Only: for plugin in plugins: plugin.on_pulse()
└─────────────────────────────────────────────────┘
```

---

## The Harness

<!-- @HARNESS
files:
  # === PRANA CORE ===
  - path: scripts/heartbeat.py
    required: true
  - path: vibe_core/plugin_protocol.py
    required: true
  - path: vibe_core/prana.py
    required: true
  - path: .github/workflows/heartbeat.yml
    required: true

wiring:
  # === PLUGIN PROTOCOL ===
  # on_pulse must exist in plugin protocol
  - pattern: "def on_pulse"
    in: vibe_core/plugin_protocol.py
  
  # === HEARTBEAT DELEGATION ===
  # Heartbeat must call plugin.on_pulse(), NOT do work itself
  - pattern: "on_pulse"
    in: scripts/heartbeat.py
  
  # === PLUGIN IMPLEMENTATIONS ===
  # OPUS Assistant must implement on_pulse
  - pattern: "def on_pulse"
    in: vibe_core/plugins/opus_assistant/plugin_main.py
  
  # Vedic Governance must implement on_pulse (for Bhakti decay)
  - pattern: "def on_pulse"
    in: vibe_core/plugins/vedic_governance/plugin_main.py

tests:
  - tests/integration/test_prana.py

semantic:
  - type: method_exists
    name: plugin_on_pulse
    in: vibe_core/plugin_protocol.py
    class: KernelPlugin
    method: on_pulse

  - type: execution_mode
    name: heartbeat_is_dumb
    expected: delegates_to_plugins
    rationale: "Heartbeat should have <100 LOC, all business logic in plugins"
-->

---

## Migration Plan (Incremental)

| Phase | Task | Risk |
|-------|------|------|
| 1 | Add `on_pulse` to PluginProtocol | LOW |
| 2 | Implement `on_pulse` in opus_assistant | LOW |
| 3 | Move `_manas_think()` from heartbeat to plugin | MEDIUM |
| 4 | Move `_execute_tasks()` to task_manager plugin | HIGH |
| 5 | Slim heartbeat.py to ~50 LOC | HIGH |

---

## Dynamic Frequency (Future)

Plugins can request faster pulses:

```python
def on_pulse(self, kernel) -> HookResult:
    if self._is_critical_phase():
        return HookResult.ok(data={"frequency_hint": 5})  # 5 min instead of 15
    return HookResult.ok()
```

---

*"प्राण - The vital life force that animates all beings."*
