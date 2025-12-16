# OPUS-087: PRANA - Plugin Pulse Architecture

**Scope:** Refactor Heartbeat to be "dumb" like the Kernel  
**Philosophy:** Heartbeat receives, Plugins execute. No business logic in scheduler.  
**Status:** 🚧 PLANNED (Pending Senior Approval)

---

## The Vision

```
CURRENT: heartbeat.py = 605 LOC of business logic
TARGET:  prana.py = ~50 LOC (just orchestration)
```

---

## ⚠️ CRITICAL SAFETY REQUIREMENTS (Senior Review)

### 1. Isolation Wrappers (Bad Apple Problem)
```python
# WRONG (Naiv)
for plugin in plugins:
    plugin.on_pulse(kernel)  # One crash = ALL dead

# CORRECT (Senior)
for plugin in plugins:
    try:
        result = plugin.on_pulse(kernel)
        self.log_pulse_success(plugin.name, result)
    except Exception as e:
        self.log_pulse_failure(plugin.name, e)
        self.quarantine_plugin(plugin.name)
        # Loop continues! Heart keeps beating.
```

### 2. Deterministic Sequence (Varna System)
Plugins MUST declare execution phase. Random order = race conditions.

```python
class PulsePhase(Enum):
    SENSORS = 1    # Drishti - Collect data first
    COGNITION = 2  # Manas - Then think  
    ACTUATORS = 3  # Karma - Then act
    CLEANUP = 4    # Shuddhi - Finally cleanup

class KernelPlugin:
    @property
    def pulse_phase(self) -> PulsePhase:
        return PulsePhase.ACTUATORS  # Override in subclass
```

### 3. Adrenaline Governor (Rate Limiting)
Plugins can REQUEST faster pulses. PRANA decides.

```python
@dataclass
class PranaConfig:
    min_pulse_interval: int = 60  # NEVER faster than 60s
    default_interval: int = 900   # 15 min
    
def resolve_frequency(votes: List[int]) -> int:
    """Conservative voting: use max(votes, min_limit)"""
    requested = min(votes) if votes else self.default_interval
    return max(requested, self.min_pulse_interval)
```

### 4. Atomic State Commit (Git Lock Problem)
Plugins MUST NOT commit to Git during `on_pulse`.

```python
def on_pulse(self, kernel) -> HookResult:
    # Return MUTATIONS, don't apply them
    return HookResult.ok(data={
        "state_mutations": [
            {"type": "bhakti_decay", "agent_id": "x", "delta": -1}
        ]
    })

# PRANA applies all mutations ONCE at end of cycle
def pulse(self):
    all_mutations = []
    for plugin in sorted_plugins:
        result = self._safe_call(plugin.on_pulse, kernel)
        if result.data and "state_mutations" in result.data:
            all_mutations.extend(result.data["state_mutations"])
    
    # Single atomic commit
    self._apply_mutations(all_mutations)
    self._git_commit()  # ONE commit, not N
```

---

## The Harness

<!-- @HARNESS
files:
  - path: scripts/heartbeat.py
    required: true
  - path: vibe_core/plugin_protocol.py
    required: true
  - path: vibe_core/prana.py
    required: true

wiring:
  # === PLUGIN PROTOCOL ===
  - pattern: "def on_pulse"
    in: vibe_core/plugin_protocol.py
  - pattern: "def pulse_phase"
    in: vibe_core/plugin_protocol.py
  
  # === ISOLATION WRAPPERS ===
  - pattern: "try:.*on_pulse.*except"
    in: scripts/heartbeat.py
  
  # === VARNA SORTING ===
  - pattern: "sorted.*pulse_phase"
    in: scripts/heartbeat.py
  
  # === RATE LIMITING ===
  - pattern: "min_pulse_interval"
    in: vibe_core/prana.py

semantic:
  - type: method_exists
    name: plugin_on_pulse
    in: vibe_core/plugin_protocol.py
    class: KernelPlugin
    method: on_pulse

  - type: method_exists
    name: plugin_pulse_phase
    in: vibe_core/plugin_protocol.py
    class: KernelPlugin
    method: pulse_phase

  - type: config_exists
    name: prana_min_interval
    in: vibe_core/prana.py
    field: min_pulse_interval
    rationale: "Rate limiting MUST be enforced"

tests:
  - tests/integration/test_prana.py
-->

---

## Migration Plan (Incremental)

| Phase | Task | Risk | Safety |
|-------|------|------|--------|
| 1 | Add `on_pulse` + `pulse_phase` to PluginProtocol | LOW | N/A |
| 2 | Create `vibe_core/prana.py` with safety wrappers | LOW | ✅ |
| 3 | Implement `on_pulse` in opus_assistant | LOW | ✅ |
| 4 | Implement `on_pulse` in vedic_governance | LOW | ✅ |
| 5 | Migrate heartbeat.py to use PRANA | MEDIUM | ✅ |

---

## Semantic Checks (Pre-Implementation)

- [ ] `on_pulse` is wrapped in try/except in heartbeat
- [ ] Plugins are sorted by `pulse_phase` before execution
- [ ] `min_pulse_interval` exists and is >= 60
- [ ] No `git commit` inside plugin `on_pulse` methods
- [ ] State mutations are collected and applied atomically

---

*"प्राण - The vital life force must be protected from chaos."*
