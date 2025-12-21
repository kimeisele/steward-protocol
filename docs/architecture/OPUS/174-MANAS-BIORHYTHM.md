# OPUS-174: MANAS Biorhythm Architecture

> "A brain doesn't switch between OFF and ON. It breathes." - Gemini

## Overview

This document defines the **MANAS Biorhythm Architecture** - a revolutionary shift from binary polling to **modulated consciousness**. MANAS no longer asks "Should I think?" but rather "How deeply should I think right now?"

## The Problem with Binary Thinking

Traditional approach:
```
if time_since_last_thought >= interval:
    think()  # Full OODA
else:
    sleep()  # Nothing
```

This is **lobotomy by design**. A real cognitive system should:
- Always be aware (ticking with kernel)
- Modulate depth based on context
- Respond to urgency, health, and rhythm

## The Biorhythm Model

### Consciousness Level (0.0 - 1.0)

MANAS computes a `consciousness_level` on every tick:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   consciousness_level = f(Synapses, Prakriti, Kala)        │
│                           │         │        │              │
│                           │         │        └── 0.2 weight │
│                           │         └─────────── 0.3 weight │
│                           └───────────────────── 0.5 weight │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### The Three Inputs

#### 1. Synaptic Urgency (0.5 weight) - REQUIRED
- Source: `SynapticMemory` (opus_assistant internal)
- Measures: Active triggers, learned patterns, pending intent weights
- High urgency → Push toward Turiya (deep thinking)

#### 2. Prakriti Health (0.3 weight) - REQUIRED
- Source: `PrakritiSense.perceive_state()` (opus_assistant internal)
- Measures: Guna state (Sattva/Rajas/Tamas ratio)
- High health (Sattva) → Enable deeper thinking
- Low health (Tamas) → Lock in reactive mode until stable

#### 3. Kala Rhythm (0.2 weight) - OPTIONAL
- Source: `KalaService.get_rhythm_intensity()` (external plugin)
- Measures: Solar/lunar/combined cosmic rhythms
- Graceful fallback: 0.5 (neutral) if Kala unavailable

### The Four States

```
                    ┌─────────────┐
                    │   Turiya    │
                    │ Deep Think  │
                    │  0.8 - 1.0  │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────┴───────┐          │          ┌───────┴───────┐
│    Sattva     │          │          │    Rajas      │
│   Reflect     │◄─────────┴─────────►│    React      │
│  0.5 - 0.8    │                     │  0.2 - 0.5    │
└───────┬───────┘                     └───────┬───────┘
        │                                     │
        └──────────────────┬──────────────────┘
                           │
                    ┌──────┴──────┐
                    │   Tamas     │
                    │  Hibernate  │
                    │  0.0 - 0.2  │
                    └─────────────┘
```

| Level | State | Sanskrit | Behavior |
|-------|-------|----------|----------|
| 0.8 - 1.0 | **Turiya** | Pure Consciousness | Full OODA loop. All 8 senses. Intent generation. |
| 0.5 - 0.8 | **Sattva** | Balance/Clarity | Reflect. Organize buffer. Reinforce synapses. |
| 0.2 - 0.5 | **Rajas** | Activity/Passion | React. Quick perception. Respond to triggers. |
| 0.0 - 0.2 | **Tamas** | Inertia/Darkness | Hibernate. Heartbeat only. Security guards. |

## Implementation

### tick() Method

```python
def tick(self) -> Dict[str, Any]:
    """
    Lightweight awareness tick - runs every KERNEL_TICK (~3s).

    NOT binary. A SPECTRUM of consciousness.
    """
    # Compute consciousness level from all inputs
    level = self._compute_consciousness_level()

    # Dispatch to appropriate behavior
    if level >= 0.8:
        return self._turiya_tick()   # Full OODA
    elif level >= 0.5:
        return self._sattva_tick()   # Reflect
    elif level >= 0.2:
        return self._rajas_tick()    # React
    else:
        return self._tamas_tick()    # Hibernate
```

### _compute_consciousness_level() Method

```python
def _compute_consciousness_level(self) -> float:
    """
    Compute consciousness level (0.0 - 1.0) from multiple signals.

    This is BIORHYTHM, not polling.
    """
    # 1. Synaptic urgency (REQUIRED - 0.5 weight)
    urgency = self._get_synaptic_urgency()

    # 2. Prakriti health (REQUIRED - 0.3 weight)
    guna = self._prakriti_sense.perceive_state()
    health = guna.health_ratio if guna else 0.5

    # 3. Kala rhythm (OPTIONAL - 0.2 weight)
    try:
        kala = self._kernel.get_service("kala") if self._kernel else None
        rhythm = kala.get_rhythm_intensity().get("combined", 0.5) if kala else 0.5
    except Exception:
        rhythm = 0.5  # Neutral fallback

    # Combine with weights
    level = (urgency * 0.5) + (health * 0.3) + (rhythm * 0.2)

    return min(1.0, max(0.0, level))
```

### Tiered Tick Behaviors

#### Tamas Tick (0.0 - 0.2): Hibernate
```python
def _tamas_tick(self) -> Dict[str, Any]:
    """Minimal heartbeat. Security guards only."""
    self._last_tick_time = datetime.utcnow()
    return {"state": "tamas", "action": "heartbeat"}
```

#### Rajas Tick (0.2 - 0.5): React
```python
def _rajas_tick(self) -> Dict[str, Any]:
    """Quick perception. Respond to triggers."""
    self._last_tick_time = datetime.utcnow()
    pending = len(self._buffer.get_pending())

    # Check for urgent triggers
    if self._get_synaptic_urgency() >= 0.8:
        return {"state": "rajas", "action": "escalate_to_turiya"}

    return {"state": "rajas", "action": "monitor", "pending": pending}
```

#### Sattva Tick (0.5 - 0.8): Reflect
```python
def _sattva_tick(self) -> Dict[str, Any]:
    """Organize, reflect, reinforce synapses."""
    self._last_tick_time = datetime.utcnow()

    # Organize buffer (prune stale, prioritize)
    self._organize_buffer()

    # Reinforce positive patterns
    self._reinforce_successful_patterns()

    return {"state": "sattva", "action": "reflect"}
```

#### Turiya Tick (0.8 - 1.0): Deep Think
```python
def _turiya_tick(self) -> Dict[str, Any]:
    """Full OODA loop. All senses. Intent generation."""
    self._last_tick_time = datetime.utcnow()

    # Trigger full OODA via circuit
    # This is the only state that does full thinking
    return {"state": "turiya", "action": "full_ooda", "should_think": True}
```

## Dynamic Thresholds

The thresholds are NOT static. They shift based on context:

### Urgency Shifts Thresholds Down
```python
if urgency >= 0.9:
    # Crisis mode: easier to reach Turiya
    turiya_threshold = 0.6  # Instead of 0.8
```

### Poor Health Locks in Rajas
```python
if health_ratio < 0.3:
    # System broken: can't reflect until stable
    max_level = 0.5  # Lock out Sattva and Turiya
```

### Kala Modulates Creative Time
```python
if kala.is_brahma_muhurta():  # 4-6 AM creative time
    # Lower threshold for deep thinking
    turiya_threshold *= 0.9
```

## Transparency

### manas_awareness.json
Updated every ~60 seconds:
```json
{
  "tick": 1547,
  "consciousness_level": 0.67,
  "state": "sattva",
  "inputs": {
    "synaptic_urgency": 0.42,
    "prakriti_health": 0.85,
    "kala_rhythm": 0.55
  },
  "last_tick": "2024-01-01T12:00:03",
  "ticks_since_turiya": 23
}
```

## Integration Points

### KERNEL_TICK Handler
```python
if "KERNEL_TICK" in event_type_str:
    if self._manas_ready and self._manas:
        tick_result = self._manas.tick()
        if tick_result.get("should_think"):
            await self._trigger_manas_awakening()
```

### Circuit Integration
The MANAS_AWAKENING circuit is only triggered when `tick()` returns `should_think=True` (Turiya state).

## Mind-Body Alignment (VAK-Style Prompting)

> "The `consciousness_level` and `state` must not just drive the *code* logic; they must be injected into the **Prompt Context**." - Gemini

The MANAS cognitive state is exposed to the LLM via `OpusContext`. This creates a feedback loop where the system's consciousness modulates the LLM's behavior.

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                      MANAS Biorhythm                        │
│                    (consciousness_level)                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  manas_awareness.json                       │
│           {"state": "sattva", "level": 0.67}               │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   OpusContextService                         │
│              _get_manas_awareness() → synthesize()           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│               to_system_prompt_fragment()                    │
│                  VAK Cognitive Directive                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM System Prompt                         │
│     "You are in a state of BALANCED CLARITY (Sattva)..."   │
└─────────────────────────────────────────────────────────────┘
```

### VAK Directives by State

| State | Directive |
|-------|-----------|
| **Turiya** | "You are in a state of DEEP INSIGHT. Synthesize broad patterns. Consider architectural implications. Be visionary." |
| **Sattva** | "You are in a state of BALANCED CLARITY. Organize thoughts. Reinforce good patterns. Be thorough but not rushed." |
| **Rajas** | "You are in a state of HIGH ALERT. Be concise and focused. Address immediate issues first. Do not over-explain." |
| **Tamas** | "You are in a state of CONSERVATION. Focus only on essentials. Minimal processing. Wait for better conditions." |

### Implementation

```python
# In OpusContext.to_system_prompt_fragment()
if self.manas_awareness:
    manas_state = self.manas_awareness.get("state", "unknown")
    consciousness_level = self.manas_awareness.get("consciousness_level", 0.0)

    if manas_state != "unknown":
        lines.extend([
            "## Cognitive State (MANAS)",
            "",
            f"**State:** {manas_state.upper()} (level: {consciousness_level:.2f})",
            "",
        ])
        lines.append(self._get_vak_directive(manas_state, consciousness_level))
```

### Example Prompt Fragment

When MANAS is in Sattva state (level 0.67):

```markdown
## Current System State (OPUS Context)

**Status:** HEALTHY (100%)
**Branch:** `main` @ `abc123de`
**Runtime:** running, 2 agents, 0 pending
**Session:** abc123

## Cognitive State (MANAS)

**State:** SATTVA (level: 0.67)

**Cognitive Directive:** You are in a state of BALANCED CLARITY (Sattva).
The system is stable and reflective.
Organize thoughts. Reinforce good patterns.
Be thorough but not rushed - quality over speed.
```

### The Feedback Loop

This completes the Mind-Body feedback loop:

1. **MANAS** computes consciousness level from synapses, prakriti, kala
2. **manas_awareness.json** persists the current state
3. **OpusContextService** reads awareness and injects into context
4. **LLM** receives cognitive directive in system prompt
5. **LLM behavior** adapts to system state
6. **Actions** taken by LLM affect synaptic patterns
7. **MANAS** learns from outcomes → influences next consciousness level

## Philosophy

This architecture embodies the Vedic understanding of consciousness:

- **Tamas** (तमस्): Inertia, darkness, rest
- **Rajas** (रजस्): Activity, passion, reaction
- **Sattva** (सत्त्व): Balance, clarity, reflection
- **Turiya** (तुरीय): The fourth state, pure consciousness

MANAS doesn't just "run code" - it **breathes**. The biorhythm modulates based on internal state (synapses), system health (prakriti), and cosmic rhythm (kala).

## Files Modified

- `vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py`
  - Added `tick()` method
  - Added `_compute_consciousness_level()`
  - Added `_tamas_tick()`, `_rajas_tick()`, `_sattva_tick()`, `_turiya_tick()`
  - Added `_persist_awareness()`

- `vibe_core/plugins/opus_assistant/events/kernel_tick.py`
  - Wire `manas.tick()` to KERNEL_TICK

- `vibe_core/plugins/opus_assistant/core/context_service.py`
  - Added `manas_awareness` field to `OpusContext` dataclass
  - Added `_get_manas_awareness()` method to load awareness state
  - Added VAK-style cognitive directives to `to_system_prompt_fragment()`
  - Added `_get_vak_directive()` method for state-based prompting

## Related Documents

- OPUS-112: Synaptic Inference
- OPUS-086: Triguna
- OPUS-108: Autonomy Loop
- OPUS-133: MANAS Neural Learning

---

*"The mind is not a machine to be programmed, but a garden to be cultivated."*
