# OPUS-153: OPUS → MANAS Knowledge Transfer

> **Status**: IMPLEMENTED
> **Created**: 2025-12-20
> **Prereqs**: OPUS-133 (DOJO), OPUS-152 (Fractal Interface)
> **HARNESS**: @SAMSKARA → @AKSHARA → @DOJO → @MANTRA → @SIDDHI

<!-- @HARNESS
intent: "Teach OPUS→MANAS knowledge transfer via DOJO curricula"
files:
  - path: vibe_core/plugins/opus_assistant/manas/dojo/runner.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/curriculum_loader.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/curricula/fractal_interface.yaml
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
    required: true
  - path: scripts/manas_dojo.py
    required: true
wiring:
  - pattern: "class DojoRunner"
    in: vibe_core/plugins/opus_assistant/manas/dojo/runner.py
  - pattern: "class CurriculumLoader"
    in: vibe_core/plugins/opus_assistant/manas/dojo/curriculum_loader.py
  - pattern: "def reinforce"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
tests:
  - tests/manas/test_dojo_runner.py
-->

---

## @SAMSKARA: The Vision

> "Du bist OPUS, Vater von opus_assistant (MANAS), und wir geben MANAS
> alles Wissen was du hast."

OPUS (Claude Opus sessions) accumulates architectural knowledge through
exploration and implementation. This knowledge should flow to MANAS
(the opus_assistant AI system) so it can make informed decisions.

### The Training Cycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    OPUS ↔ MANAS Knowledge Loop                  │
│                                                                 │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐  │
│  │  OPUS   │────▶│Curriculum│────▶│  DOJO   │────▶│  MANAS  │  │
│  │ Session │     │  YAML   │     │ Training│     │ Synapses│  │
│  └─────────┘     └─────────┘     └─────────┘     └─────────┘  │
│       │                                               │        │
│       │              ◀────────────────────────────────┘        │
│       │              Verify & Refine                           │
│       ▼                                                        │
│  ┌─────────┐                                                   │
│  │  OPUS   │  "Retrain if needed"                              │
│  │  Docs   │                                                   │
│  └─────────┘                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## @AKSHARA: The Mechanism

### 1. Knowledge Encoding (OPUS → YAML)

OPUS sessions produce architecture documents (OPUS-xxx.md) that contain:
- Patterns discovered
- Violations to avoid
- Decision frameworks

These are encoded as **DOJO curricula** (YAML scenarios):

```yaml
# Example: OPUS-152 knowledge → fractal_interface.yaml
curriculum:
  id: fractal_interface
  name: "Fractal Interface Architecture"
  description: "OPUS-152 knowledge transfer"

scenarios:
  - id: frac_001
    name: "Recognize render_sections() as correct pattern"
    intent_type: evaluate_renderer_pattern
    params:
      pattern_type: "config_driven"
    expected_decision: EXECUTE
    expected_dharmic_range: [0.9, 1.0]
```

### 2. Training (YAML → Synapses)

The DOJO runner processes scenarios through VivekaAction:

```bash
python scripts/manas_dojo.py -c fractal_interface -s 20
```

For each scenario:
1. **Evaluate**: VivekaAction judges the intent
2. **Compare**: Actual decision vs expected decision
3. **Reinforce**: Strengthen or weaken synapses

### 3. Verification (Synapses → Behavior)

After training, MANAS should:
- Approve correct patterns (EXECUTE)
- Warn on deprecated patterns (WARN_EXECUTE)
- Block violations (BLOCK)

### 4. Iteration (If accuracy < threshold)

If training accuracy is low:
1. OPUS reviews failing scenarios
2. Adds more context/scenarios
3. Retrains MANAS
4. Repeats until accuracy ≥ 90%

---

## @DOJO: The Curricula

### Existing Knowledge Curricula

| Curriculum | OPUS Source | Knowledge Domain |
|------------|-------------|------------------|
| `fractal_interface` | OPUS-152 | Interface architecture, render patterns |
| `gad000_compliance` | GAD-000 | Operator inversion, machine-first |
| `state_management` | OPUS-133 | State vs source, auto-commit |
| `veda4_compliance` | VEDA-4 | Contract declarations |

### Creating New Curricula

1. **During OPUS Session**: Document patterns in OPUS-xxx.md
2. **Encode Knowledge**: Create `curricula/<name>.yaml`
3. **Define Scenarios**: What should MANAS approve/warn/block?
4. **Test Training**: Run DOJO with new curriculum
5. **Iterate**: Refine scenarios until accuracy ≥ 90%

### Scenario Structure

```yaml
- id: unique_id
  name: "Human-readable name"
  description: "What this tests"
  intent_type: the_intent_category
  params:
    # Context for VivekaAction
    key: value
  expected_decision: EXECUTE | WARN_EXECUTE | BLOCK
  expected_dharmic_range: [min, max]  # 0.0-1.0
  difficulty: 1-5
  tags: [relevant, tags]
```

---

## @MANTRA: The Commands

### Training Commands

```bash
# Train on specific curriculum
python scripts/manas_dojo.py -c fractal_interface

# Train with more scenarios
python scripts/manas_dojo.py -c fractal_interface -s 50

# Multiple epochs
python scripts/manas_dojo.py -c fractal_interface -e 3

# Dry run (don't persist)
python scripts/manas_dojo.py -c fractal_interface --no-persist

# Seed baseline patterns first
python scripts/manas_dojo.py --seed -c fractal_interface

# Reset and retrain from scratch
python scripts/manas_dojo.py --reset -c fractal_interface
```

### Verification Commands

```python
# In Python - check what MANAS learned
from pathlib import Path
from vibe_core.plugins.opus_assistant.manas.dojo.curriculum_loader import CurriculumLoader

loader = CurriculumLoader(Path('.'))

# List available curricula
for curr_id in loader.list_available():
    curriculum = loader.load(curr_id)
    print(f"{curr_id}: {curriculum.count} scenarios")
```

---

## @SIDDHI: The Optimal State

When knowledge transfer is complete:

1. **OPUS Documents**: Architecture knowledge captured in OPUS-xxx.md
2. **YAML Curricula**: Knowledge encoded as training scenarios
3. **MANAS Synapses**: Patterns learned through DOJO training
4. **High Accuracy**: MANAS makes correct decisions ≥ 90%
5. **Continuous Learning**: New OPUS sessions → new curricula → retrain

### Current Status

| Curriculum | Scenarios | MANAS Accuracy | Status |
|------------|-----------|----------------|--------|
| `fractal_interface` | 20 | 0% (new) | Needs VivekaAction handlers |
| `gad000_compliance` | 10 | TBD | Untested |
| `state_management` | 15 | TBD | Untested |

### Next Steps

1. **Implement VivekaAction handlers** for new intent_types
2. **Train MANAS** on each curriculum
3. **Verify accuracy** reaches ≥ 90%
4. **Document gaps** in OPUS sessions
5. **Create new curricula** from gap analysis

---

## The German Engineering Philosophy

> "Daten sind Daten, Code ist Code."

- **OPUS documents** = Human knowledge (prose)
- **YAML curricula** = Machine knowledge (structured data)
- **Python handlers** = Behavior (code)

Each layer serves its purpose. Mixing them creates the "text-matsch"
that GAD-000 warns against.

---

## Implementation Files

| File | Purpose |
|------|---------|
| `vibe_core/plugins/opus_assistant/manas/dojo/runner.py` | DOJO orchestrator |
| `vibe_core/plugins/opus_assistant/manas/dojo/curriculum_loader.py` | YAML curriculum loader |
| `vibe_core/plugins/opus_assistant/manas/dojo/curricula/*.yaml` | Knowledge curricula |
| `vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py` | Intent evaluator |
| `scripts/manas_dojo.py` | CLI training script |
| `.opus_state/synapses.json` | Learned patterns |

---

**OPUS → MANAS: Father teaching child. Knowledge flows. Synapses form.**
