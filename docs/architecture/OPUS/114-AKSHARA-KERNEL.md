# OPUS-114: Akshara Kernel - Sanskrit Phonemic Computation Matrix

**Status**: IMPLEMENTED
**Date**: 2025-12-19
**Author**: Claude (Senior Engineer)
**Depends on**: OPUS-111 (Signal Alignment), OPUS-112 (Synaptic Inference), OPUS-113 (Stress Test)

## Summary

"अक्षराणां अकारोऽस्मि" - "Of letters, I am 'A'" (Bhagavad Gita 10.33)

OPUS-114 introduces the **Akshara Kernel** - a deterministic computation layer based on
the Sanskrit Varnamala (alphabet) matrix. Each phoneme (Akshara) is positioned by its
articulation point (Varga), creating a natural resonance system for synaptic wiring.

## The Problem

After OPUS-110/111/112/113, MANAS had a complete learning loop:
- Write learned weights (Hebbian)
- Read for inference (consult)
- Canonical vocabulary (no pollution)
- Stress-tested and proven

But the prioritization was still based ONLY on weight:

```
BEFORE:
  trigger:test_failure → action:analyze_error (0.8)
  trigger:test_failure → action:notify_operator (1.0)

  Decision: notify_operator wins (higher weight)

  Problem: What if analyze_error is a BETTER FIT for test failures?
```

## The Solution: Dharmic Score

```
AFTER (OPUS-114):
  Dharmic Score = Synaptic Weight × Akshara Resonance

  trigger:test_failure (KANTHYA/KERNEL)
    → action:analyze_error (TALAVYA/COGNITION): 0.8 × 0.8 = 0.64
    → action:notify_operator (OSHTHYA/OUTPUT):  1.0 × 0.2 = 0.20

  Decision: analyze_error wins (higher DHARMIC score)
  Reason: KERNEL triggers resonate with COGNITION actions (adjacent Vargas)
          but have weak resonance with OUTPUT actions (4 Vargas apart)
```

## The Varnamala Matrix

The Sanskrit consonant matrix (Vyanjana-varga) maps to code layers:

```
┌────────────────────────────────────────────────────────────────────┐
│  Varga        │ Element │ Code Layer       │ Aksharas             │
├────────────────────────────────────────────────────────────────────┤
│  Kanthya      │ Äther   │ KERNEL/DEEP      │ क ख ग घ ङ            │
│  (Guttural)   │ Akasha  │                  │ ka kha ga gha ṅa     │
├────────────────────────────────────────────────────────────────────┤
│  Talavya      │ Luft    │ COGNITION/FLOW   │ च छ ज झ ञ            │
│  (Palatal)    │ Vayu    │                  │ ca cha ja jha ña     │
├────────────────────────────────────────────────────────────────────┤
│  Murdhanya    │ Feuer   │ REPAIR/HARD      │ ट ठ ड ढ ण            │
│  (Retroflex)  │ Agni    │                  │ ṭa ṭha ḍa ḍha ṇa     │
├────────────────────────────────────────────────────────────────────┤
│  Dantya       │ Wasser  │ INTERFACE/LINK   │ त थ द ध न            │
│  (Dental)     │ Jala    │                  │ ta tha da dha na     │
├────────────────────────────────────────────────────────────────────┤
│  Oshthya      │ Erde    │ OUTPUT/SURFACE   │ प फ ब भ म            │
│  (Labial)     │ Prithvi │                  │ pa pha ba bha ma     │
└────────────────────────────────────────────────────────────────────┘
```

## Resonance Calculation

Resonance is based on articulatory distance (how far apart the Vargas are):

| Distance | Resonance | Meaning |
|----------|-----------|---------|
| 0 | 1.0 | Same Varga - perfect harmony |
| 1 | 0.8 | Adjacent Vargas - natural flow |
| 2 | 0.6 | Two apart - moderate connection |
| 3 | 0.4 | Three apart - weak connection |
| 4 | 0.2 | Maximum distance - minimal resonance |

### Resonance Matrix

```
          KANTH  TALAV  MURDH  DANTY  OSHTH
KANTHYA │  1.00  0.80   0.60   0.40   0.20
TALAVYA │  0.80  1.00   0.80   0.60   0.40
MURDHAN │  0.60  0.80   1.00   0.80   0.60
DANTYA  │  0.40  0.60   0.80   1.00   0.80
OSHTHYA │  0.20  0.40   0.60   0.80   1.00
```

## Trigger/Action Mapping

### Triggers by Varga

| Varga | Layer | Triggers |
|-------|-------|----------|
| KANTHYA | KERNEL | test_failure, build_failure, meru_test |
| TALAVYA | COGNITION | intent_stuck, intent_expired, idle_detected |
| MURDHANYA | REPAIR | error_detected, lint_failure, duplicate_class_detected |
| DANTYA | INTERFACE | gap_detected:*, sutra:* |
| OSHTHYA | OUTPUT | file_changed:*, karma_low |

### Actions by Varga

| Varga | Layer | Actions |
|-------|-------|---------|
| KANTHYA | KERNEL | run_tests, check_lint, auto_retry |
| TALAVYA | COGNITION | analyze_error, log_diagnostic |
| MURDHANYA | REPAIR | auto_fix, consolidate |
| DANTYA | INTERFACE | create_code, create_doc, create_test, update_docs |
| OSHTHYA | OUTPUT | notify_operator, escalate_to_operator, report_to_operator |

## API

### SynapticMemory (Updated)

```python
from vibe_core.plugins.opus_assistant.manas.triggers import SynapticMemory

memory = SynapticMemory.get(workspace)

# Original consult (weight-only)
recommendations = memory.consult("trigger:test_failure")
# Returns: [SynapticRecommendation(action="action:notify_operator", weight=1.0), ...]

# NEW: Dharmic consult (weight × resonance)
dharmic = memory.consult_dharmic("trigger:test_failure")
# Returns: [DharmicRecommendation(
#     action="action:analyze_error",
#     weight=0.8,
#     resonance=0.8,
#     dharmic_score=0.64,
#     varga_trigger="KANTHYA",
#     varga_action="TALAVYA",
# ), ...]

# Get dharmic confidence for an intent
confidence = memory.get_dharmic_confidence(intent)  # 0.0 - 1.0
```

### DharmicRecommendation

```python
@dataclass
class DharmicRecommendation:
    action: str          # e.g., "action:run_tests"
    weight: float        # Synaptic weight (0.0 - 1.0)
    resonance: float     # Akshara resonance (0.2 - 1.0)
    dharmic_score: float # weight × resonance
    trigger: str         # The trigger pattern
    varga_trigger: str   # e.g., "KANTHYA"
    varga_action: str    # e.g., "TALAVYA"

    @property
    def confidence_level(self) -> str:
        """Based on dharmic_score: very_high/high/medium/low/very_low"""

    @property
    def is_resonant(self) -> bool:
        """True if trigger and action are in same or adjacent Vargas"""

    @property
    def harmony_description(self) -> str:
        """perfect/harmonic/moderate/weak/distant"""
```

### Akshara Module

```python
from vibe_core.plugins.opus_assistant.manas.akshara import (
    Varga,
    Akshara,
    Varnamala,
    calculate_resonance,
    calculate_dharmic_score,
    AksharaGraph,
)

# Get the Varnamala matrix
varnamala = Varnamala.get()

# Get an Akshara
ka = varnamala.get_by_devanagari("क")
print(ka.iast)      # "ka"
print(ka.varga)     # Varga.KANTHYA
print(ka.layer)     # "KERNEL"
print(ka.element)   # "Akasha"

# Calculate resonance
resonance = calculate_resonance("trigger:test_failure", "action:analyze_error")
# Returns: 0.8 (KANTHYA → TALAVYA = adjacent)

# Calculate dharmic score
dharmic = calculate_dharmic_score("trigger:test_failure", "action:analyze_error", 0.8)
# Returns: 0.64 (0.8 × 0.8)

# Build and save graph
graph = AksharaGraph(workspace)
graph.build_from_synapses(synapses_data)
graph.save()  # → .opus_state/akshara_graph.json
```

## The Akshara Graph

OPUS-114 also introduces a JSON graph structure for visualization:

```json
{
  "schema": "akshara-graph-v1",
  "nodes": {
    "trigger:test_failure": {
      "pattern": "trigger:test_failure",
      "akshara": "ङ",
      "varga": "KANTHYA",
      "layer": "KERNEL",
      "element": "Akasha",
      "node_type": "trigger"
    },
    "action:analyze_error": {
      "pattern": "action:analyze_error",
      "akshara": "ञ",
      "varga": "TALAVYA",
      "layer": "COGNITION",
      "element": "Vayu",
      "node_type": "action"
    }
  },
  "edges": [
    {
      "source": "trigger:test_failure",
      "target": "action:analyze_error",
      "weight": 0.8,
      "resonance": 0.8,
      "dharmic_score": 0.64
    }
  ]
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MANAS Cognitive Kernel + Akshara                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐    ┌─────────────────┐                             │
│  │   Event     │───▶│ normalize_trigger│                             │
│  └─────────────┘    └────────┬────────┘                             │
│                              │                                       │
│                              ▼                                       │
│                    ┌─────────────────┐                              │
│                    │ get_trigger_varga│                              │
│                    │ (OPUS-114)      │                              │
│                    └────────┬────────┘                              │
│                             │                                        │
│                             ▼                                        │
│                    ┌─────────────────┐                              │
│                    │ SynapticMemory  │◀────┐                        │
│                    │ .consult_dharmic│     │                        │
│                    └────────┬────────┘     │                        │
│                             │              │                         │
│                             ▼              │                         │
│                    ┌─────────────────┐     │                        │
│                    │ calculate_      │     │                        │
│                    │ dharmic_score   │     │                        │
│                    │ (weight × res)  │     │                        │
│                    └────────┬────────┘     │                        │
│                             │              │                         │
│                             ▼              │                         │
│                    ┌─────────────────┐     │                        │
│                    │    Decision     │     │                        │
│                    │ (by dharmic     │     │                        │
│                    │   not weight)   │     │                        │
│                    └────────┬────────┘     │                        │
│                             │              │                         │
│                             ▼              │                         │
│                    ┌─────────────────┐     │                        │
│                    │    Execute      │     │                        │
│                    └────────┬────────┘     │                        │
│                             │              │                         │
│                             ▼              │                         │
│                    ┌─────────────────┐     │                        │
│                    │ _update_synapses│─────┘                        │
│                    │   (OPUS-110)    │                              │
│                    └─────────────────┘                              │
│                                                                      │
│                    ┌─────────────────┐    ┌──────────────────┐      │
│                    │ synapses.json   │    │ akshara_graph.json│     │
│                    │ (weights)       │    │ (visualization)  │      │
│                    └─────────────────┘    └──────────────────┘      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Insight

**Before OPUS-114**: MANAS learned what works (weights).
**After OPUS-114**: MANAS learns what fits (weights × resonance).

The difference is not just in WHAT you learn, but in HOW you apply it.
A high-weight action that doesn't resonate with the trigger is less valuable
than a medium-weight action that harmonizes naturally.

## The Phonetic Foundation

Why Sanskrit? The Varnamala is not arbitrary - it's organized by:

1. **Articulation Point** (where sound is produced)
   - Throat → Palate → Roof → Teeth → Lips

2. **Sound Flow** (natural movement patterns)
   - Adjacent sounds flow naturally (resonance 0.8)
   - Distant sounds require effort (resonance 0.2)

3. **Element Correspondence** (Pancha Bhuta)
   - Akasha (Ether) → KERNEL (foundation)
   - Vayu (Air) → COGNITION (movement)
   - Agni (Fire) → REPAIR (transformation)
   - Jala (Water) → INTERFACE (connection)
   - Prithvi (Earth) → OUTPUT (manifestation)

This isn't mysticism - it's a 3000-year-old phonetic model that maps
beautifully to layered software architecture.

## Files Changed/Created

| File | Change |
|------|--------|
| `akshara.py` | **NEW** - Complete Akshara Kernel implementation |
| `triggers.py` | Added DharmicRecommendation, consult_dharmic() |

## Related

- OPUS-108: Initial Synapses (created synapses.json)
- OPUS-110: Synaptic Learning Loop (Hebbian - WRITE)
- OPUS-111: Signal Alignment (vocabulary)
- OPUS-112: Synaptic Inference (READ)
- OPUS-113: Dharmic Stress Test (validation)
- OPUS-114: Akshara Kernel (resonance - this document)

## Future: OPUS-115+

Possible next steps:
- **Synaptic Decay**: Unused connections weaken over time
- **Multi-hop Inference**: trigger → action → trigger chains via Akshara
- **Mantra Sequences**: Common trigger-action patterns as "mantras"
- **Chakra Integration**: 7-layer model mapping to deployment stages
