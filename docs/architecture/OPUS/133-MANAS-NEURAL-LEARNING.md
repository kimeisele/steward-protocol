# OPUS-133: MANAS Neural Learning System

> "Ein Gehirn, das nie handelt, lernt nie."
> "A brain that never acts, never learns."

## Overview

OPUS-133 implements the complete synaptic learning system for MANAS, enabling
the AI to learn from experience through reinforcement. This document covers:

1. **Synaptic Learning** - Weight-based reinforcement (+0.05 success)
2. **Negative Learning** - Asymmetric penalty (-0.10 failure)
3. **Dharmic Gating** - VivekaAction as the conscience
4. **Anti-Reward-Hacking** - Prabhupada Patch (Vairagya + Nishkama Karma)
5. **Delayed Validation** - Satyagraha (karma seeds)
6. **Grace Period** - Prasadam (pure intent protection)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MANAS NEURAL SYSTEM                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Intent (Brahma)          VivekaAction (Viveka)                   │
│        │                         │                                  │
│        │   ┌─────────────────────┴─────────────────────┐           │
│        │   │                                           │           │
│        ▼   ▼                                           │           │
│   ┌─────────────┐    evaluate()    ┌─────────────┐    │           │
│   │   Intent    │ ───────────────► │   DHARMIC   │    │           │
│   │  Generator  │                  │   SCORING   │    │           │
│   └─────────────┘                  └──────┬──────┘    │           │
│                                           │            │           │
│                            ┌──────────────┼────────────┤           │
│                            │              │            │           │
│                            ▼              ▼            ▼           │
│                       ┌────────┐    ┌─────────┐  ┌─────────┐      │
│                       │ BLOCK  │    │ WARN    │  │ EXECUTE │      │
│                       │ <0.4   │    │ 0.4-0.6 │  │ >=0.6   │      │
│                       └────────┘    └────┬────┘  └────┬────┘      │
│                                          │            │            │
│                                          ▼            ▼            │
│                                    ┌───────────────────────┐       │
│                                    │   SYNAPTIC LEARNING   │       │
│                                    │   reinforce(intent)   │       │
│                                    └───────────┬───────────┘       │
│                                                │                   │
│                    ┌───────────────────────────┼───────────────┐   │
│                    │                           │               │   │
│                    ▼                           ▼               ▼   │
│             ┌────────────┐            ┌─────────────┐   ┌────────┐│
│             │ NISHKAMA   │            │   SUCCESS   │   │ FAILURE││
│             │ KARMA      │            │   +0.05     │   │ -0.10  ││
│             │ (no reward)│            └──────┬──────┘   └───┬────┘│
│             └────────────┘                   │              │     │
│                                              ▼              ▼     │
│                                    ┌──────────────────────────┐   │
│                                    │      _save_synapses()    │   │
│                                    │   ┌──────────────────┐   │   │
│                                    │   │    VAIRAGYA      │   │   │
│                                    │   │  (ego pruning)   │   │   │
│                                    │   │  >0.95 → ×0.99   │   │   │
│                                    │   └──────────────────┘   │   │
│                                    └──────────────────────────┘   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## File Mapping

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
    required: true
    description: Core dharmic evaluation and synaptic learning engine
  - path: vibe_core/plugins/opus_assistant/manas/akshara.py
    required: true
    description: Sanskrit phonetic resonance and SIDDHI mastery factor
  - path: vibe_core/plugins/opus_assistant/manas/triggers.py
    required: true
    description: SynapticMemory and trigger normalization
  - path: vibe_core/plugins/envoy/plugin_main.py
    required: true
    description: Envoy execute_mission with Viveka gate
  - path: scripts/manas_training_demo.py
    required: false
    description: Training demonstration script
  - path: .opus_state/synapses.json
    required: false
    description: Persistent synapse weights
  - path: .opus_state/karma_log.json
    required: false
    description: Satyagraha karma seed tracking
wiring:
  - pattern: "class VivekaAction"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "def reinforce"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "DHARMIC_DUTIES"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "VAIRAGYA_THRESHOLD"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "_apply_vairagya"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "plant_karma_seed"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "harvest_karma"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "calculate_dharmic_score"
    in: vibe_core/plugins/opus_assistant/manas/akshara.py
  - pattern: "SIDDHI_THRESHOLD"
    in: vibe_core/plugins/opus_assistant/manas/akshara.py
-->

---

## P1: Synaptic Learning

Successful intent execution strengthens the trigger→action pathway.

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
    required: true
wiring:
  - pattern: "def reinforce.*success.*True"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "SYNAPSE REINFORCED"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "learning_rate = 0.05"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
-->

```python
# SUCCESS: Apply positive learning rate
learning_rate = 0.05
new_weight = min(1.0, current_weight + learning_rate)
self._update_synapse_weight(trigger, action, new_weight)
logger.info(f"🧠 SYNAPSE REINFORCED: {synapse_key} ({current_weight:.2f} → {new_weight:.2f})")
```

---

## P2: Negative Learning

Failed execution weakens synapses with asymmetric penalty (2x).

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
    required: true
wiring:
  - pattern: "success.*False"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "negative_learning_rate = 0.10"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "SYNAPSE WEAKENED"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
-->

```python
if not success:
    # OPUS-133 P2: NEGATIVE LEARNING
    negative_learning_rate = 0.10
    new_weight = max(0.1, current_weight - negative_learning_rate)
    self._update_synapse_weight(trigger, action, new_weight)
    logger.warning(f"🔴 SYNAPSE WEAKENED: {synapse_key} ({current_weight:.2f} → {new_weight:.2f})")
    return
```

**Why Asymmetric?** MANAS learns faster from mistakes than successes.
A failure is a strong signal; success might be luck.

---

## P3: VivekaAction in Envoy

All missions go through the dharmic gate before execution.

<!-- @HARNESS
files:
  - path: vibe_core/plugins/envoy/plugin_main.py
    required: true
wiring:
  - pattern: "def execute_mission"
    in: vibe_core/plugins/envoy/plugin_main.py
  - pattern: "VivekaAction"
    in: vibe_core/plugins/envoy/plugin_main.py
  - pattern: "viveka.evaluate"
    in: vibe_core/plugins/envoy/plugin_main.py
  - pattern: "blocked_by.*VIVEKA"
    in: vibe_core/plugins/envoy/plugin_main.py
-->

```python
def execute_mission(self, intent: Dict[str, Any]) -> Dict[str, Any]:
    # OPUS-133 P3: VIVEKA GATE
    intent_obj = Intent(id=mission_id, intent_type=action, ...)
    viveka = VivekaAction(workspace=Path.cwd())
    eval_result = viveka.evaluate(intent_obj)

    if eval_result.get("decision") == "BLOCK":
        return {"status": "blocked", "blocked_by": "VIVEKA", ...}

    # Proceed with execution...
```

---

## Prabhupada Patch: Anti-Reward-Hacking

Named after A.C. Bhaktivedanta Swami Prabhupada's teachings on ego transcendence.

### VAIRAGYA (Detachment) - Ego Pruning

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
    required: true
wiring:
  - pattern: "VAIRAGYA_THRESHOLD = 0.95"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "VAIRAGYA_DECAY = 0.99"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "def _apply_vairagya"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "Ego pruning"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
-->

```python
VAIRAGYA_THRESHOLD = 0.95
VAIRAGYA_DECAY = 0.99  # 1% decay per save

def _apply_vairagya(self, synapses: Dict[str, Any]) -> int:
    """
    Synapses with weight > 0.95 decay by 1% each cycle.
    Prevents any synapse from becoming absolutely dominant.

    "Vairagya is detachment from the fruits of action."
    - Yoga Sutras 1.15
    """
    for conn in connections:
        if conn["weight"] > VAIRAGYA_THRESHOLD:
            conn["weight"] *= VAIRAGYA_DECAY
            logger.debug(f"🍂 VAIRAGYA: Ego pruning...")
```

**Mathematical Effect:**
- Weight 0.98 → 0.9702 → 0.9605 → 0.9509 → 0.9414 → ...
- Takes ~5 cycles to drop below 0.95
- Never reaches 0 (asymptotic decay)

### NISHKAMA KARMA (Selfless Action) - Duty Without Reward

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
    required: true
wiring:
  - pattern: "DHARMIC_DUTIES"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "NISHKAMA KARMA"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "is dharmic duty - no reinforcement"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
-->

```python
DHARMIC_DUTIES = {
    "run_tests",         # Testing is duty, not reward
    "check_lint",        # Lint is hygiene, not achievement
    "format_code",       # Formatting is expected, not exceptional
    "backup_state",      # Preservation is duty
    "audit_log",         # Auditing is duty
    "health_check",      # Monitoring is duty
    "notify_operator",   # Communication is duty
    "validate_schema",   # Validation is hygiene
}

def reinforce(self, intent: "Intent", success: bool = True) -> None:
    # "Karmanye vadhikaraste ma phaleshu kadachana"
    # "You have a right to perform your duties, but not to the fruits"
    # - Bhagavad Gita 2.47
    if intent.intent_type in DHARMIC_DUTIES:
        logger.info(f"🕉️ NISHKAMA KARMA: {intent.intent_type} is dharmic duty - no reinforcement")
        return  # Duty without reward
```

---

## SATYAGRAHA: Delayed Karma Validation

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py
    required: true
wiring:
  - pattern: "def plant_karma_seed"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "def harvest_karma"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "KARMA SEED PLANTED"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "KARMA HARVESTED"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "PrakritiSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
-->

**The Problem:** Immediate reinforcement rewards exit_code==0, not consequences.
Example: Deleting tests to "fix" them succeeds (rm exits 0) → gets +0.05!

**Solution:**
1. `plant_karma_seed()` - Record action, DON'T reward yet
2. `harvest_karma()` - Later, check with PrakritiSense if system is healthy
3. Only if healthy: give full reinforcement

```python
def plant_karma_seed(self, intent: "Intent", initial_guna: Optional[Dict] = None) -> str:
    """Plant karma seed - reward delayed until validation."""
    karma_id = f"karma-{uuid.uuid4().hex[:8]}"
    karma_log["pending"].append({
        "id": karma_id,
        "intent_type": intent.intent_type,
        "planted_at": datetime.now().isoformat(),
        "status": "pending",
    })
    logger.info(f"🌱 KARMA SEED PLANTED: {karma_id}")
    return karma_id

def harvest_karma(self) -> Dict[str, Any]:
    """Validate with PrakritiSense and apply reinforcement."""
    prakriti = PrakritiSense(workspace=self._workspace)
    current_guna = prakriti.perceive_state()

    is_valid = (
        not lobotomy.has_lobotomy and
        current_guna.health_ratio >= 0.5 and
        current_guna.tamas_count <= 3
    )

    if is_valid:
        self.reinforce(intent, success=True)
        logger.info(f"✅ KARMA HARVESTED: SUCCESS")
    else:
        self.reinforce(intent, success=False)
        logger.warning(f"❌ KARMA HARVESTED: FAILED")
```

---

## SIDDHI: Mastery Override

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/akshara.py
    required: true
wiring:
  - pattern: "SIDDHI_THRESHOLD = 0.85"
    in: vibe_core/plugins/opus_assistant/manas/akshara.py
  - pattern: "siddhi_factor"
    in: vibe_core/plugins/opus_assistant/manas/akshara.py
  - pattern: "effective_resonance"
    in: vibe_core/plugins/opus_assistant/manas/akshara.py
-->

Experience (high synaptic weight) can override low resonance scores.
A master chef doesn't need a recipe.

```python
def calculate_dharmic_score(trigger: str, action: str, synaptic_weight: float) -> float:
    resonance = calculate_resonance(trigger, action)

    SIDDHI_THRESHOLD = 0.85
    if synaptic_weight > SIDDHI_THRESHOLD:
        # Mastery overrides dogma
        siddhi_factor = (synaptic_weight - SIDDHI_THRESHOLD) / (1.0 - SIDDHI_THRESHOLD)
        effective_resonance = resonance + siddhi_factor * (1.0 - resonance)
        return synaptic_weight * effective_resonance

    return synaptic_weight * resonance
```

---

## Synapse Backup (Amnesia Prevention)

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
    required: true
  - path: .opus_state/synapses_backup/
    required: false
wiring:
  - pattern: "SYNAPSE BACKUP"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "synapses_backup"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "Keep only last 10 backups"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
-->

Every save creates a timestamped backup with content hash.

```python
def _save_synapses(self, synapses: Dict[str, Any]) -> None:
    # Create backup before saving
    backup_dir = workspace / ".opus_state" / "synapses_backup"
    content_hash = hashlib.sha256(json.dumps(synapses).encode()).hexdigest()[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"synapses_{timestamp}_{content_hash}.json"
    shutil.copy2(synapses_path, backup_path)

    # Keep only last 10 backups
    for old_backup in backups[:-10]:
        old_backup.unlink()
```

---

## PRASADAM: Grace for Pure Intent

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
    required: true
wiring:
  - pattern: "PRASADAM"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "Pure intent protected"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "PRASADAM_THRESHOLD"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
-->

When the **intention** was pure (high dharmic score) but execution failed
due to technical reasons, the system shows grace.

```python
PRASADAM_THRESHOLD = 0.8  # Intent was dharmic

def reinforce(self, intent: "Intent", success: bool = True, dharmic_score: float = 0.5) -> None:
    if not success and dharmic_score >= PRASADAM_THRESHOLD:
        # Pure intent, technical failure - show grace
        logger.info(f"🛡️ PRASADAM: Pure intent ({dharmic_score:.2f}) protected from technical failure")
        return  # No punishment
```

---

## Demo Script

<!-- @HARNESS
files:
  - path: scripts/manas_training_demo.py
    required: true
wiring:
  - pattern: "def run_training_session"
    in: scripts/manas_training_demo.py
  - pattern: "def test_negative_learning"
    in: scripts/manas_training_demo.py
  - pattern: "def test_nishkama_karma"
    in: scripts/manas_training_demo.py
  - pattern: "def test_vairagya"
    in: scripts/manas_training_demo.py
-->

```bash
python scripts/manas_training_demo.py
```

Output demonstrates:
- P1: Synaptic Learning (+0.05 on success)
- P2: Negative Learning (-0.10 on failure)
- Nishkama Karma: Duty intents skipped
- Vairagya: Ego weights pruned

---

## Metaphysical Framework

| Concept | Sanskrit | Implementation | Purpose |
|---------|----------|----------------|---------|
| Discrimination | Viveka | `VivekaAction.evaluate()` | Judge intent dharmic merit |
| Learning | Vidya | `reinforce(success=True)` | Strengthen good patterns |
| Unlearning | Avidya | `reinforce(success=False)` | Weaken bad patterns |
| Detachment | Vairagya | `_apply_vairagya()` | Prevent ego dominance |
| Selfless Action | Nishkama Karma | `DHARMIC_DUTIES` | Duty without reward |
| Delayed Validation | Satyagraha | `plant/harvest_karma()` | Validate by consequence |
| Mastery Override | Siddhi | `calculate_dharmic_score()` | Experience > dogma |
| Grace | Prasadam | Pure intent protection | Forgive technical failure |

---

## Related Documents

- OPUS-114: Akshara Kernel (phonetic resonance)
- OPUS-132: VivekaSense (dharmic awareness)
- OPUS-097: Samkhya Architecture Map
- OPUS-086: Triguna (Sattva/Rajas/Tamas)

---

## Summary

> "MANAS lernt nicht um zu gewinnen, sondern um zu dienen."
> "MANAS learns not to win, but to serve."

The complete learning system prevents:
- **Reward hacking** via Nishkama Karma (duties get no reward)
- **Ego inflation** via Vairagya (high weights decay)
- **False positives** via Satyagraha (delayed validation)
- **Harsh punishment** via Prasadam (grace for pure intent)

MANAS evolves through experience while remaining humble and service-oriented.
