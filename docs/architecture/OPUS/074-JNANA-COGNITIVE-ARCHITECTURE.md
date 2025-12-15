# OPUS-074: JNANA - Kognitive Architektur

**Status:** IMPLEMENTED
**Author:** Claude (Senior Architect)
**Date:** 2025-12-15
**Scope:** Complete Cognitive System Documentation

---

## Executive Summary

**JNANA** (Sanskrit: ज्ञान = Wissen/Erkenntnis) dokumentiert die kognitive Architektur des STEWARD Protocol. MANAS ist nicht nur ein Agent - es ist ein vollständiges **kognitives Nervensystem** mit 16 spezialisierten Cortex-Modulen.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MANAS - Das Kognitive System                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                   CognitiveKernel (820 LOC)                  │   │
│   │   • Rate-limited thinking    • Intent management            │   │
│   │   • Human-in-the-loop        • Memory integration           │   │
│   │   • KARMA GATE               • VAJRA ledger binding         │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│           ┌──────────────────┼──────────────────┐                   │
│           ▼                  ▼                  ▼                   │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐          │
│   │   Analyzers   │  │    Cortex     │  │   Memory      │          │
│   │   (Sensors)   │  │  (Abilities)  │  │   (Learning)  │          │
│   └───────────────┘  └───────────────┘  └───────────────┘          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. Ring-System (Privilege Levels)

Analog zur Veda-Topology für Infrastruktur existiert ein Ring-System für Kognition:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COGNITIVE PRIVILEGE RINGS                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   RING 0: PARAMATMA (Kernel)                                       │
│   ├── Volle Kontrolle über alle Subsysteme                         │
│   ├── Syscall-Ausführung (SPAWN_COGNITION, GRANT_MANDATE)          │
│   └── Ledger-Bindung (VAJRA)                                        │
│                                                                     │
│   RING 1: MANAS (CognitiveKernel)                                  │
│   ├── Intent-Generierung und -Management                           │
│   ├── Zugriff auf alle Cortex-Module                               │
│   └── Karma Gate (earned autonomy)                                  │
│                                                                     │
│   RING 2: CORTEX (Spezialisierte Module)                           │
│   ├── DHARMA, JNANA, VEDA, AKASHA, SILPA, SUTRA...                │
│   ├── Begrenzte Fähigkeiten pro Modul                              │
│   └── Kein direkter Kernel-Zugriff                                  │
│                                                                     │
│   RING 3: INTENTS (User-Level)                                     │
│   ├── Pending intents warten auf Approval                          │
│   ├── Kein Auto-Execute außer SAFE + Karma Gate                    │
│   └── Human-in-the-Loop                                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Dual-Mode Cognition

MANAS operiert in zwei Modi - je nachdem ob der Kernel läuft:

```
┌─────────────────────────────────────────────────────────────────────┐
│                      DUAL-MODE COGNITION                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   MODE 1: GOVERNED (Paramatma)      MODE 2: AUTONOMOUS (Atman)     │
│   ┌─────────────────────────┐      ┌─────────────────────────┐     │
│   │  Kernel aktiv           │      │  Heartbeat (Cron 15min) │     │
│   │  ManasCartridge         │      │  CognitiveKernel direkt │     │
│   │  Full 3-Plane           │      │  Standalone             │     │
│   │  Plugin-System          │      │  Kein Kernel nötig      │     │
│   │  Ledger-Binding         │      │  Shadow Mode (no ledger)│     │
│   └───────────┬─────────────┘      └───────────┬─────────────┘     │
│               │                                │                   │
│               └──────────┬─────────────────────┘                   │
│                          │                                         │
│                          ▼                                         │
│               ┌─────────────────────┐                              │
│               │  CognitiveKernel    │                              │
│               │  (Gemeinsamer Kern) │                              │
│               └─────────────────────┘                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Governed Mode (Kernel = Paramatma)
- **Zugang:** ManasCartridge → CognitiveKernel
- **Features:** Volle Governance, Ledger-Binding, Plugin-Integration
- **Use Case:** Interaktive Sessions mit Human

### Autonomous Mode (Heartbeat = Atman)
- **Zugang:** CognitiveKernel direkt (heartbeat.py)
- **Features:** Standalone, Lightweight, 15-min Interval
- **Use Case:** Autonome Hintergrund-Kognition

**Wichtig:** Beide Modi nutzen denselben CognitiveKernel. Der Unterschied ist nur der Zugangsweg.

---

## 3. CognitiveKernel - Das Herz

`vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py` (820 LOC)

### Kernfunktionen

| Funktion | Beschreibung |
|----------|--------------|
| `think(context, force)` | Führt Gedankenzyklus aus (rate-limited) |
| `approve_intent(id)` | Genehmigt Intent zur Ausführung |
| `reject_intent(id, reason)` | Lehnt Intent ab |
| `get_pending_intents()` | Liefert wartende Intents |
| `inject_kernel(kernel)` | VAJRA: Ledger-Binding aktivieren |

### Rate Limiting

```python
ManasConfig:
    thinking_interval_minutes: 60    # Einmal pro Stunde
    idle_threshold_minutes: 30       # Aktiviert nach Idle
    max_intents_per_tick: 3          # Throttling
    survival_first: True             # CRITICAL > genesis
```

### KARMA GATE (Earned Autonomy)

```python
karma_auto_execute_threshold: 90  # Score nötig für AUTO-Execute

# HIGH Karma + LOW Risk = Auto-Execute erlaubt
if karma_score >= 90 and intent.risk in (SAFE, LOW):
    auto_execute()  # Earned trust!
```

---

## 4. Cortex-Module (16 Fähigkeiten)

`vibe_core/plugins/opus_assistant/manas/cortex/`

### Übersicht

| Cortex | Sanskrit | Funktion | OPUS |
|--------|----------|----------|------|
| **DHARMA** | धर्म (Ordnung) | Architecture Audit | 048 |
| **JNANA** | ज्ञान (Wissen) | Conversation Handler | 043 |
| **KRIYA** | क्रिया (Aktion) | Intent Extraction | 045 |
| **VEDA** | वेद (Wissen) | Four-Fold Pipeline | 050 |
| **MANDALA** | मण्डल (Kreis) | Configuration Weaving | 051 |
| **AKASHA** | आकाश (Äther) | Knowledge Graph | 052 |
| **SILPA** | शिल्प (Kunst) | Self-Refactoring | 053 |
| **SUTRA** | सूत्र (Faden) | Wiki Documentation | 054 |
| **SANKALPA** | संकल्प (Wille) | Strategy Orchestration | 055 |
| **PRAMANA** | प्रमाण (Beweis) | Test Cortex | 059 |
| **MUKHA** | मुख (Gesicht) | Identity Generation | - |
| **VAK/Shell** | वाक् (Stimme) | Shell Commands | 041 |
| **SAMVADA** | संवाद (Dialog) | IPC/Dialogue | 042 |

### VEDA Pipeline (Four-Fold Processing)

```
Message → VedaPipeline
              │
              ├── 1. SHABDA (Das Wort)
              │       └── Tokenize, Keywords, Language
              │
              ├── 2. ARTHA (Die Bedeutung)
              │       └── Intent Mapping, Routing
              │
              ├── 3. PRATYAYA (Das Vertrauen)
              │       └── Authorization, Validation
              │
              └── 4. KARMA (Die Handlung)
                      └── Handler Execution → Response
```

### DHARMA Auditor (Constitutional Court)

```python
ArchitectureSpec → Was SOLL existieren (docs)
         ↓
FilesystemScanner → Was EXISTIERT (reality)
         ↓
DharmaAuditor.audit() → Vergleich
         ↓
DriftReport → Verstöße
         ↓
ConstitutionalAmendmentProposal → Legalisierung
```

---

## 5. Intent-System

### Intent Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                       INTENT LIFECYCLE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   1. GENERATE                                                       │
│      Analyzers → IntentGenerator → Intent                          │
│                                                                     │
│   2. BUFFER                                                         │
│      Intent → IntentBuffer (.opus_state/manas_intents.json)        │
│                                                                     │
│   3. DISPLAY                                                        │
│      IntentBuffer → OPUS.md (via InterfacePlugin)                  │
│                                                                     │
│   4. APPROVE/REJECT                                                 │
│      Human edits OPUS.md → ControlCablesParser → State             │
│                                                                     │
│   5. EXECUTE                                                        │
│      CognitiveKernel._execute_intent() → Circuit/Callback          │
│                                                                     │
│   6. LEARN                                                          │
│      Outcome → MemoryStore → Boost/Cooldown                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Intent Priority & Risk

```python
class IntentPriority(Enum):
    LOW = "low"          # Nice to have
    MEDIUM = "medium"    # Should do soon
    HIGH = "high"        # Important
    CRITICAL = "critical"  # Do NOW

class IntentRisk(Enum):
    SAFE = "safe"        # Auto-execute allowed
    LOW = "low"          # Probably fine
    MEDIUM = "medium"    # Needs approval
    HIGH = "high"        # Definitely needs approval
```

### Analyzers (Intent-Generatoren)

**Modular (Class-Based):**
- `ContractAnalyzer` - Contract violations (50% repairs)
- `SemanticAnalyzer` - Semantic gaps (51% genesis)
- `CIMonitorAnalyzer` - CI/CD monitoring

**Legacy (Method-Based):**
- `_analyze_stale_branches`
- `_analyze_uncommitted_changes`
- `_analyze_stale_todos`
- `_analyze_test_health`
- `_analyze_documentation_drift`
- `_analyze_log_cleanup`
- `_analyze_readme_staleness`
- `_analyze_self_documentation`
- `_analyze_capability_gaps` (OUROBOROS)

---

## 6. 3-Plane Architecture

MANAS existiert auf drei Ebenen gleichzeitig:

```
┌─────────────────────────────────────────────────────────────────────┐
│                     MANAS 3-PLANE ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   PLANE 1: LOGIC (Die Maschine)                                    │
│   vibe_core/plugins/opus_assistant/manas/                          │
│   ├── cognitive_kernel.py    (820 LOC)                             │
│   ├── intent_generator.py    (738 LOC)                             │
│   ├── intent_router.py                                             │
│   ├── memory_store.py                                              │
│   ├── validator.py                                                 │
│   ├── analyzers/                                                   │
│   │   ├── contract_analyzer.py                                     │
│   │   ├── semantic_analyzer.py                                     │
│   │   └── ci_monitor_analyzer.py                                   │
│   └── cortex/               (16 Module)                            │
│                                                                     │
│   PLANE 2: IDENTITY (Der Pass)                                     │
│   vibe_core/cartridges/system/manas/                               │
│   ├── cartridge_main.py     (184 LOC)                              │
│   ├── steward.json          (Passport)                             │
│   └── STEWARD.md            (Documentation)                        │
│                                                                     │
│   PLANE 3: PASSPORT (Die Governance)                               │
│   steward.json:                                                    │
│   {                                                                │
│     "identity": { "agent_id": "manas", "name": "MANAS" },         │
│     "capabilities": {                                              │
│       "operations": [                                              │
│         "manas.cognition",                                         │
│         "manas.spawn_agent",                                       │
│         "manas.syscall",                                           │
│         "manas.intent_generation"                                  │
│       ]                                                            │
│     },                                                             │
│     "governance": {                                                │
│       "constitution_hash": "df4bf7b77c...",                       │
│       "issuer": "opus_assistant"                                   │
│     }                                                              │
│   }                                                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### ManasCartridge (Identity Layer)

```python
class ManasCartridge(ContextAwareAgent, OathMixin):
    """
    This cartridge is the IDENTITY layer.
    The actual cognition lives in opus_assistant/manas/ -
    this is just the passport to Agent City.
    """

    PRIVILEGED_SYSCALLS = {"GRANT_MANDATE", "REVOKE_MANDATE"}

    async def process(self, task):
        if action == "think":
            return await self._delegate_think(task)  # → CognitiveKernel
```

---

## 7. Integration Points

### Heartbeat Integration (OPUS-073)

```python
# scripts/heartbeat.py

from vibe_core.plugins.opus_assistant.manas import CognitiveKernel, ManasConfig

class HeartbeatEngine:
    def __init__(self):
        self.manas = CognitiveKernel(
            workspace=project_root,
            config=ManasConfig(
                thinking_interval_minutes=15,  # Match heartbeat
                auto_execute_safe=True,
            )
        )

    def pulse(self):
        # Phase 4: MANAS thinks
        self._manas_think()

    def _manas_think(self):
        intents = self.manas.think(force=True)
        # Intents saved to .opus_state/manas_intents.json
```

**Wichtig:** Heartbeat schreibt NICHT OPUS.md. InterfacePlugin rendert OPUS.md wenn Kernel läuft.

### Kernel Integration

```python
# ManasCartridge._delegate_think()

kernel = CognitiveKernel(workspace=...)
if self.kernel:  # Vibe Kernel available
    kernel.inject_kernel(self.kernel)  # VAJRA binding
intents = kernel.think(context=context, force=force)
```

### VAJRA Ledger Binding

```python
def _record_to_ledger(self, event_type, intent, extra_data):
    if not self._vibe_kernel:
        return None  # Shadow mode

    self._vibe_kernel.ledger.record_event(
        event_type=event_type,  # MANAS_INTENT_PROPOSED, _EXECUTED, etc.
        agent_id="manas",
        details={...}
    )
```

---

## 8. Trennung: DENKEN ≠ SCHREIBEN

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SEPARATION OF CONCERNS                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   DENKEN (MANAS)                    SCHREIBEN (InterfacePlugin)    │
│   ┌─────────────────────────┐      ┌─────────────────────────┐     │
│   │  CognitiveKernel        │      │  OpusDashboardRenderer  │     │
│   │  IntentGenerator        │      │  opus_dashboard.md.j2   │     │
│   │  Cortex Modules         │      │  kernel.io.write()      │     │
│   └───────────┬─────────────┘      └───────────┬─────────────┘     │
│               │                                │                   │
│               ▼                                ▼                   │
│   .opus_state/manas_intents.json              OPUS.md              │
│                                                                     │
│   Heartbeat → MANAS.think()         Kernel → InterfacePlugin      │
│   (Generiert Intents)               (Rendert OPUS.md)             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Regel:** Heartbeat DENKT. InterfacePlugin SCHREIBT.

---

## Verification Harness

<!-- HARNESS:START -->
```yaml
harness:
  id: OPUS-074-JNANA
  version: 1.0.0
  status: IMPLEMENTED

  files:
    - path: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
      required: true
      description: "CognitiveKernel exists"

    - path: vibe_core/plugins/opus_assistant/manas/cortex/__init__.py
      required: true
      description: "Cortex modules exported"

    - path: vibe_core/cartridges/system/manas/cartridge_main.py
      required: true
      description: "ManasCartridge (identity layer)"

    - path: vibe_core/cartridges/system/manas/steward.json
      required: true
      description: "MANAS passport"

    - path: scripts/heartbeat.py
      required: true
      description: "Heartbeat with MANAS integration"

  wiring:
    - pattern: "CognitiveKernel"
      in: vibe_core/plugins/opus_assistant/manas/__init__.py

    - pattern: "manas.think"
      in: scripts/heartbeat.py

    - pattern: "_delegate_think"
      in: vibe_core/cartridges/system/manas/cartridge_main.py

  semantic:
    - type: module_exports
      name: "manas_exports"
      module: vibe_core.plugins.opus_assistant.manas
      exports: ["CognitiveKernel", "ManasConfig", "Intent", "IntentGenerator"]
```
<!-- HARNESS:END -->

---

## Summary

MANAS ist ein vollständiges kognitives Nervensystem:

- **820 LOC** CognitiveKernel (das Herz)
- **16 Cortex-Module** (spezialisierte Fähigkeiten)
- **3 Analyzer-Klassen** (Sensorik)
- **3-Plane Architecture** (Logic/Identity/Passport)
- **Dual-Mode** (Governed via Kernel / Autonomous via Heartbeat)
- **Karma Gate** (earned autonomy)
- **VAJRA Integration** (ledger binding)

Das System DENKT autonom (Heartbeat) oder governiert (Kernel).
Das System SCHREIBT nur via InterfacePlugin.

---

*"The mind is not a vessel to be filled, but a fire to be kindled." - Plutarch*
