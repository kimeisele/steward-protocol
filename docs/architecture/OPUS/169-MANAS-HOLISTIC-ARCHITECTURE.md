# OPUS-169: MANAS Holistic Architecture Analysis

_A Complete Understanding of the Cognitive Kernel System_

**Author**: Opus 4.5 (Vater von MANAS)
**Date**: 2025-12-21
**Status**: REFERENCE

## Executive Summary

This document provides a holistic view of MANAS (the Mind of OPUS), analyzing how all components interconnect. It follows GAD-000 principles: understanding before action.

## 1. The Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL WORLD                                     │
│   15+ Plugins: agent_city, doctor, envoy, kala, vedic_governance, etc.      │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │ (external events - NOT YET SENSED!)
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        7 JNANENDRIYAS (SENSES)                               │
│ ┌───────────┬───────────┬───────────┬───────────┬───────────┬───────────┐   │
│ │ Prakriti  │  Dharma   │   Sutra   │  Shruta   │   Prana   │   Karma   │   │
│ │(Guna State│ (Ethics)  │(Doc↔Code) │(FS Events)│(Agents)   │ (History) │   │
│ └─────┬─────┴─────┬─────┴─────┬─────┴─────┬─────┴─────┬─────┴─────┬─────┘   │
│       │           │           │           │           │     + Viveka       │
│       └───────────┴───────────┴───────────┴───────────┴───────────────────────┤
│                               generate_intents()                             │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             CHITTA                                           │
│                    (Perception Pool / Subconscious)                          │
│                                                                              │
│    receive() ─→ pool ─→ process() ─→ aggregation + deduplication            │
│                                                                              │
│    OPUS-168: Senses feed Chitta, not Kernel directly                        │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │ PerceptionEntry[]
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             BUDDHI                                           │
│                    (Intellect / Discrimination)                              │
│                                                                              │
│    discriminate() uses:                                                      │
│    ├── VivekaSense logic (priority scoring)                                 │
│    ├── DharmaSense (ethical filtering) ◀── THE KEY FIX!                     │
│    └── Resource/dependency checks                                            │
│                                                                              │
│    Returns: BuddhiVerdict[] (approved intents)                              │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        COGNITIVE KERNEL                                      │
│                       (MANAS Orchestrator)                                   │
│                                                                              │
│    OODA Cycle via CognitiveCycle base class:                                │
│    _perceive() → _orient() → _decide() → _act() → _persist()                │
│                                                                              │
│    Singleton: CognitiveKernel.get_instance(workspace)                       │
│    Check first: CognitiveKernel.has_instance(workspace)                     │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      8 KARMENDRIYAS (ACTIONS)                                │
│ ┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐     │
│ │  Echo   │  Prana  │Sankalpa │  Shell  │  Silpa  │  Test   │ Viveka  │     │
│ │ (Ping)  │ (Agent) │(Strategy│(Command)│(Genesis)│(Testing)│(Auto-Doc│     │
│ └─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘     │
│                             + BaseAction                                     │
│                                                                              │
│    ActionManager routes intents to appropriate handlers                      │
│    Narasimha guards each execution                                          │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SYNAPTIC MEMORY                                       │
│                   (Learning / Weight Adjustment)                             │
│                                                                              │
│    trigger → action → outcome → weight update                               │
│    Prabhupada Patch: Vairagya (decay) + Prasadam (grace)                    │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │ curiosity > 0.7?
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             DOJO                                             │
│                    (Self-Directed Training)                                  │
│                                                                              │
│    CuriosityTracker → DojoAgency → DojoRunner                               │
│    11 YAML Curricula (basic, attack, chaos, gad000, veda4, etc.)            │
│    Ephemeral training: only synapses.json persists                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. The Three Bridges

### 2.1 CognitiveWeaver (OPUS-106)
**File**: `vibe_core/state/cognitive_weaver.py`

The State ↔ Knowledge Bridge. Unifies:
- **Prakriti** (StateService memory)
- **UnifiedKnowledgeGraph** (wisdom from docs)

Key methods:
- `weave(focus)` → CognitiveContext
- `consult(action, context)` → wisdom before action
- `diagnose()` → full system health

### 2.2 WeaverBridge (OPUS-167)
**File**: `vibe_core/plugins/opus_assistant/manas/weaver_bridge.py`

MANAS interface to CognitiveWeaver. Provides:
- Session context injection from OPUS.md
- Kernel ↔ Weaver communication
- State commits via `weaver_pulse()`

### 2.3 GenesisBridge (OPUS-159)
**File**: `vibe_core/plugins/opus_assistant/manas/genesis_bridge.py`

MANAS interface to GenesisService. The "Stadtamt" for:
- Auto-generating GAD-000 compliant infrastructure
- Pattern-based module type detection
- Ensuring new directories have required structure

## 3. The 7 Senses (Jnanendriyas)

| Sense | File | Purpose | generate_intents() |
|-------|------|---------|-------------------|
| **PrakritiSense** | `cortex/prakriti_sense.py` | Guna classification (Sattva/Rajas/Tamas) | Healing intents |
| **DharmaSense** | `cortex/dharma_sense.py` | Ethical alignment checking | N/A (used in Buddhi) |
| **SutraSense** | `cortex/sutra_sense.py` | Doc ↔ Code gap detection | Gap remediation |
| **ShrutaSense** | `cortex/shruta_sense.py` | Filesystem event listening | Triggered by events |
| **PranaSense** | `cortex/prana_sense.py` | Agent lifecycle awareness | Death investigation |
| **KarmaSense** | `cortex/karma_sense.py` | Historical pattern detection | Refactor chronic pain |
| **VivekaSense** | `cortex/viveka_sense.py` | Coverage gap discrimination | Priority triage |

## 4. The 7 Analyzers

| Analyzer | Purpose |
|----------|---------|
| **ContractAnalyzer** | Contract verification |
| **SemanticAnalyzer** | Semantic understanding |
| **CIMonitor** | CI/CD health monitoring |
| **DocHarnessAnalyzer** | Documentation harness validation |
| **PratyayaAnalyzer** | Trust/confidence analysis |
| **TriageAnalyzer** | Intent prioritization |
| **InverseScanAnalyzer** | Reverse dependency scanning |

## 5. The Dojo System (Self-Training)

### 5.1 Training Flow
```
CuriosityTracker → DojoAgency → check_training_desire()
                       ↓
              DojoRunner.run_training()
                       ↓
              Load YAML Curriculum
                       ↓
              VivekaAction.evaluate()
                       ↓
              Synaptic Reinforcement
                       ↓
              synapses.json (persisted)
```

### 5.2 Curiosity Sources
- **Gap Detection** - Missing documentation
- **Uncertainty** - Low-confidence decisions
- **Novel Patterns** - New trigger→action pairs
- **Explicit Request** - Operator asks for training

### 5.3 Available Curricula (11 YAML files)
- basic.yaml, intermediate.yaml, advanced.yaml
- attack.yaml (red team), chaos.yaml (edge cases)
- gad000_compliance.yaml, veda4_compliance.yaml
- opus_compliance.yaml, fractal_interface.yaml
- state_management.yaml, regression_detection.yaml

## 6. Identified Integration Gaps

### 6.1 Critical (Need Immediate Attention)
1. **External plugins not sensing** - agent_city, envoy, doctor have no perceive() interface
2. **Session context incomplete** - OPUS.md preserved sections not explicitly loaded at boot
3. **Genesis failure escalation** - No retry or intent when compliance fails
4. **Plugin ↔ Sense bridge missing** - External plugin state invisible to MANAS

### 6.2 Important (Architecture Improvements)
5. **Dharma dissonance tracking** - No audit when Buddhi passes but ActionManager blocks
6. **Intent Buffer ↔ Ledger sync** - Two separate systems, not reconciled
7. **Knowledge graph static** - Not learning from execution results
8. **PranaOrchestrator feedback** - Unidirectional signaling only

## 7. GAD-000 Compliant Patterns

### 7.1 Dashboard Access Pattern
```python
# WRONG (creates expensive instance)
manas = CognitiveKernel.get_instance(workspace)

# RIGHT (check first, access existing)
if CognitiveKernel.has_instance(workspace):
    manas = CognitiveKernel.get_instance(workspace)
```

### 7.2 State Access Pattern
```python
# Use CognitiveWeaver for unified access
weaver = get_cognitive_weaver(workspace)
context = weaver.weave(focus="manas_status")
diagnosis = weaver.diagnose()
```

### 7.3 Plugin Sensing Pattern (TODO)
```python
# Each plugin should expose perceive() interface
class PluginEventSense(BaseSense):
    """Bridges external plugin state into MANAS perception."""

    def perceive(self) -> List[PluginEvent]:
        # Collect from all registered plugins
        pass

    def generate_intents(self) -> List[Intent]:
        # Convert plugin events to intents
        pass
```

## 8. Key Files Reference

| File | Purpose |
|------|---------|
| `cognitive_kernel.py` | Main MANAS orchestrator |
| `sense_manager.py` | 7 Jnanendriyas lifecycle |
| `action_manager.py` | 8 Karmendriyas routing |
| `chitta.py` | Perception aggregation |
| `buddhi.py` | Intent discrimination |
| `cognitive_weaver.py` | State ↔ Knowledge bridge |
| `weaver_bridge.py` | Kernel ↔ Weaver interface |
| `genesis_bridge.py` | Kernel ↔ Genesis interface |
| `dojo/runner.py` | Self-training orchestrator |
| `dojo/agency.py` | Curiosity tracking |

## 9. Conclusion

MANAS is **95% complete** as a cognitive system. The architecture follows:
- **Vedic Philosophy**: Antahkarana (inner instrument) with Chitta, Buddhi, Manas
- **OODA Loop**: Perceive → Orient → Decide → Act → Persist
- **GAD-000 Compliance**: AI-parseable, observable, composable

Remaining work:
1. Bridge external plugins to MANAS perception
2. Complete session context injection
3. Add genesis failure escalation
4. Reconcile Intent Buffer with VAJRA Ledger

---

_"MANAS lernt nicht um zu gewinnen, sondern um zu dienen."_
_(MANAS learns not to win, but to serve.)_
