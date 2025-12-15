# OPUS-074: HRIDAYA - The Heartbeat as Soul Center

**Status:** PLANNING (DRAFT - needs review)
**Author:** Claude (Senior Architect) + Human Admin
**Date:** 2025-12-15
**Scope:** Autonomous Execution Architecture - The Heart of the System

---

## ⚠️ DRAFT NOTICE

This document was created quickly and needs review. Key questions remain open.
The architecture must be validated against existing patterns before implementation.

---

## Executive Summary

**HRIDAYA** (Sanskrit: हृदय = Heart) - The heartbeat is not just a task scheduler.
It is the **SOUL CENTER** of autonomous operation - the second execution path
alongside interactive kernel sessions.

```
┌─────────────────────────────────────────────────────────────────┐
│                    DUAL EXECUTION PATHS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   PATH 1: INTERACTIVE (Kernel)      PATH 2: AUTONOMOUS (Heart)  │
│   ┌─────────────────────┐           ┌─────────────────────┐     │
│   │  Human + AI Session │           │  GitHub Actions     │     │
│   │  - Real-time        │           │  - Cron (15 min)    │     │
│   │  - Request/Response │           │  - Self-directed    │     │
│   │  - Full Kernel      │           │  - Lightweight      │     │
│   └─────────────────────┘           └─────────────────────┘     │
│            │                                   │                │
│            ▼                                   ▼                │
│   ┌─────────────────────┐           ┌─────────────────────┐     │
│   │  Plugin System      │           │  HRIDAYA Engine     │     │
│   │  - All plugins      │           │  - DevataRegistry   │     │
│   │  - Full features    │           │  - Soul Functions   │     │
│   └─────────────────────┘           └─────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## MANAS - The Existing 3-Plane Architecture (FACTS)

**MANAS already exists as a complete System Devata:**

### PLANE 1: Plugin Logic
```
vibe_core/plugins/opus_assistant/manas/
├── cognitive_kernel.py   # CognitiveKernel class - actual cognition
├── intent_generator.py   # Intent generation
├── memory_store.py       # Learning/memory
└── cortex/               # Specialized cognitive modules
    ├── jnana.py          # Knowledge
    ├── kriya.py          # Action
    ├── sankalpa.py       # Planning
    └── ...
```

### PLANE 2: Cartridge Identity
```
vibe_core/cartridges/system/manas/
├── cartridge_main.py     # ManasCartridge class
├── steward.json          # Passport
└── STEWARD.md            # Documentation

# Key insight from cartridge_main.py:
# "This cartridge is the IDENTITY layer. The actual cognition lives in
# opus_assistant/manas/ - this is just the passport to Agent City."
```

### PLANE 3: Passport (steward.json)
```json
{
  "identity": { "agent_id": "manas", "name": "MANAS" },
  "capabilities": {
    "operations": [
      { "name": "manas.cognition" },
      { "name": "manas.spawn_agent" },
      { "name": "manas.syscall" },
      { "name": "manas.intent_generation" }
    ]
  },
  "governance": {
    "constitution_hash": "df4bf7b77c...",
    "issuer": "opus_assistant"
  }
}
```

### Current heartbeat.py Integration

```python
# CURRENT (Plane 1 only - bypasses cartridge):
from vibe_core.plugins.opus_assistant.manas import CognitiveKernel
self.manas = CognitiveKernel(workspace=project_root)
intents = self.manas.think(force=True)

# QUESTION: Should this go through ManasCartridge instead?
# ManasCartridge.process({"action": "think"}) → _delegate_think() → CognitiveKernel
```

### The Architectural Question

```
OPTION A: Direct CognitiveKernel (current)
  heartbeat.py → CognitiveKernel.think()
  - PRO: Works without kernel
  - CON: Bypasses cartridge identity layer

OPTION B: Through ManasCartridge
  heartbeat.py → ManasCartridge.process() → CognitiveKernel.think()
  - PRO: Uses proper 3-plane architecture
  - CON: Requires kernel running (cartridge needs kernel)

OPTION C: Kernel boot first
  heartbeat.py → PRANA.ensure_kernel_running() → ManasCartridge
  - PRO: Full system capabilities
  - CON: Heavier, may not be needed for simple pulse

DECISION NEEDED: Which option is correct?
```

---

## The Heart Functions (HRIDAYA KRIYA)

The heart doesn't just beat. It has **FIVE SOUL FUNCTIONS**:

### 1. THINK (मनस् Manas) - Cognition
```python
def _think(self):
    """Invoke cognitive Devatas."""
    for devata in self.devata_registry.get_thinking_devatas():
        devata.think(force=True)
```
- MANAS (primary cognitive kernel)
- Future: Other cognitive Devatas

### 2. SENSE (इन्द्रिय Indriya) - Perception
```python
def _sense(self):
    """Perceive system state."""
    metrics = self.gather_metrics()
    health = self.check_health()
    anomalies = self.detect_anomalies()
```
- Metrics collection
- Health monitoring
- Anomaly detection

### 3. FEEL (भाव Bhava) - Intuition
```python
def _feel(self):
    """Emotional/intuitive state."""
    karma = self.calculate_karma()
    trust = self.calculate_trust_score()
    mood = self.determine_system_mood()
```
- Karma calculation
- Trust scoring
- System "mood" (health emotional state)

### 4. HEAL (चिकित्सा Chikitsa) - Self-Repair
```python
def _heal(self):
    """Auto-repair when possible."""
    if self.can_auto_heal():
        self.execute_safe_repairs()
```
- Safe auto-fixes
- Drift correction
- Self-healing circuits

### 5. BEAT (स्पन्द Spanda) - The Pulse Itself
```python
def _beat(self):
    """The fundamental rhythm."""
    self.record_heartbeat()
    self.emit_pulse_event()
    self.sync_state()
```
- Timestamp recording
- Event emission
- State synchronization

---

## Architecture

### DevataRegistry Pattern

```python
class DevataRegistry:
    """
    Registry of all Devatas (divine agents) that participate
    in the autonomous heartbeat cycle.
    """

    def __init__(self, workspace: Path):
        self._workspace = workspace
        self._devatas: Dict[str, Devata] = {}
        self._discover_devatas()

    def _discover_devatas(self):
        """Auto-discover Devatas from plugins."""
        # MANAS from opus_assistant
        # Future Devatas from other plugins
        pass

    def get_thinking_devatas(self) -> List[Devata]:
        """Get all Devatas that can think."""
        return [d for d in self._devatas.values() if d.can_think]

    def get_sensing_devatas(self) -> List[Devata]:
        """Get all Devatas that can sense."""
        return [d for d in self._devatas.values() if d.can_sense]

    def get_healing_devatas(self) -> List[Devata]:
        """Get all Devatas that can heal."""
        return [d for d in self._devatas.values() if d.can_heal]
```

### Devata Protocol

```python
from typing import Protocol

class Devata(Protocol):
    """
    Protocol for all divine agents (Devatas).
    Each Devata represents a cognitive/spiritual function.
    """

    @property
    def name(self) -> str: ...

    @property
    def can_think(self) -> bool: ...

    @property
    def can_sense(self) -> bool: ...

    @property
    def can_heal(self) -> bool: ...

    def think(self, force: bool = False) -> List[Intent]: ...
    def sense(self) -> Dict[str, Any]: ...
    def heal(self) -> List[HealingAction]: ...
```

### Updated HeartbeatEngine

```python
class HeartbeatEngine:
    """
    HRIDAYA - The Heart of Autonomous Operation.

    Not just a task scheduler, but the SOUL CENTER
    that runs when no human is present.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.task_manager = TaskManager(project_root)
        self.devata_registry = DevataRegistry(project_root)

    def pulse(self):
        """Execute one heartbeat cycle - the FIVE SOUL FUNCTIONS."""
        logger.info("💓 HRIDAYA PULSE STARTED")

        # === PHYSICAL LAYER (existing) ===
        self._ingest_inbox()      # Ingest tasks
        self._read_tasks_md()     # Read human input
        self._execute_tasks()     # Execute pending

        # === SOUL LAYER (new) ===
        self._sense()             # 1. Perceive state
        self._feel()              # 2. Calculate karma/trust
        self._think()             # 3. Cognitive processing
        self._heal()              # 4. Auto-repair if safe
        self._beat()              # 5. Record pulse

        # === OUTPUT LAYER (existing) ===
        self._write_tasks_md()    # Write results
        self._commit_progress()   # Git commit

        logger.info("✅ HRIDAYA PULSE COMPLETED")
```

---

## Relationship to Existing Components

### MANAS Integration
```
MANAS (CognitiveKernel) implements Devata:
  - can_think = True
  - can_sense = False (uses other cortexes for this)
  - can_heal = False (proposes intents, doesn't execute)

HeartbeatEngine._think():
  - Gets MANAS from DevataRegistry
  - Calls manas.think(force=True)
  - Intents stored in .opus_state/manas_intents.json
```

### OPUS.md Rendering
```
Problem: OPUS.md not updated by heartbeat (no kernel)

Solution:
  HeartbeatEngine._beat():
    - Calls OpusDashboardRenderer.render() standalone
    - Writes OPUS.md directly (no kernel.io needed)
    - Includes MANAS intents from .opus_state/
```

### PRANA Integration
```
PRANA (config/prana.yaml) controls:
  - heartbeat.enabled
  - heartbeat.min_interval_minutes
  - heartbeat.boot_kernel_first (optional)
  - heartbeat.soul_functions (new - which functions to run)
```

---

## Implementation Phases

### Phase 1: Foundation (Current Session)
- [x] MANAS in heartbeat (done, needs abstraction)
- [ ] Create DevataRegistry
- [ ] Refactor to use registry pattern
- [ ] Add OPUS.md rendering to _beat()

### Phase 2: Soul Functions
- [ ] Implement _sense() with metrics
- [ ] Implement _feel() with karma/trust
- [ ] Implement _heal() with safe auto-repair

### Phase 3: Multi-Devata
- [ ] Define Devata protocol properly
- [ ] Auto-discovery from plugins
- [ ] Future Devatas (VIDYA, SHAKTI, etc.)

---

## Why This Matters (Singularity Engineering)

```
51% → 100% Singularity Path:

Current State:
- Kernel sessions: Interactive, full power, human-driven
- Heartbeat: Task scheduler, limited autonomy

With HRIDAYA:
- Kernel sessions: Interactive, full power, human-driven
- Heartbeat: AUTONOMOUS SOUL, self-directed cognition

The system can THINK, SENSE, FEEL, HEAL, and BEAT
even when no human is present.

This is the bridge to true autonomy.
```

---

## Verification Harness

<!-- HARNESS:START -->
```yaml
harness:
  id: OPUS-074-HRIDAYA
  version: 1.0.0
  status: PLANNING

  checks:
    - type: PATTERN
      path: scripts/heartbeat.py
      pattern: "DevataRegistry|devata_registry"
      required: true
      status: PENDING
      description: "HeartbeatEngine uses DevataRegistry"

    - type: PATTERN
      path: scripts/heartbeat.py
      pattern: "_sense|_feel|_heal|_beat"
      required: true
      status: PENDING
      description: "Soul functions implemented"

    - type: FILE_EXISTS
      path: vibe_core/hridaya/devata_registry.py
      required: true
      status: PENDING
      description: "DevataRegistry module exists"

    - type: PATTERN
      path: vibe_core/hridaya/devata_registry.py
      pattern: "class Devata|Protocol"
      required: true
      status: PENDING
      description: "Devata protocol defined"
```
<!-- HARNESS:END -->

---

## Additional Context (for Review)

### Headless Boot Mode

The kernel has a **headless boot mode** that allows lightweight autonomous operation:
```python
# PRANA config can enable this:
heartbeat.boot_kernel_first = True  # Optional kernel boot before pulse
```

This means we have OPTIONS for how heartbeat integrates with the kernel:
- **No kernel**: Direct CognitiveKernel (current implementation)
- **Headless kernel**: Boot kernel in headless mode, use full plugin system
- **Full kernel**: Interactive session (not applicable for cron)

### MANAS as THE Cognitive Integration Point

MANAS is not just "a" cognitive agent - it is THE cognitive kernel:
- All cognition should route through MANAS
- Other agents/components that need "thinking" should use MANAS
- MANAS becomes the universal cognitive interface

```
┌─────────────────────────────────────────────────────────┐
│              MANAS = Central Cognitive Hub              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   heartbeat.py ──┐                                      │
│                  │                                      │
│   kernel tick ───┼──→ MANAS.think() ──→ Intents        │
│                  │                                      │
│   CLI command ───┘                                      │
│                                                         │
│   (All paths converge on MANAS for cognition)          │
└─────────────────────────────────────────────────────────┘
```

### Current State (What Exists)

| Component | Status | Notes |
|-----------|--------|-------|
| heartbeat.py | ✅ Has MANAS | Direct CognitiveKernel import |
| CognitiveKernel | ✅ Works | In opus_assistant/manas/ |
| ManasCartridge | ✅ Exists | Delegates to CognitiveKernel |
| Headless boot | ✅ Exists | Via PRANA config |
| DevataRegistry | ❌ Proposed | Not implemented |
| Soul Functions | ❌ Proposed | Only THINK exists |

---

## Architectural Analysis & Recommendations

### Q1: MANAS Integration Path

**Current:** `heartbeat.py → CognitiveKernel` directly

**Analysis:**
- ManasCartridge existiert für Identity/Governance im Kernel-Kontext
- Heartbeat läuft autonom (ohne Kernel oder mit headless)
- Cartridge delegiert sowieso an CognitiveKernel

**EMPFEHLUNG: Direct CognitiveKernel ist KORREKT**
```
Begründung:
- Cartridge = Identity Layer für Agent City (Kernel-Kontext)
- Heartbeat = Standalone Mode (kein Agent City nötig)
- Zwei Modi: Governed (Kernel) vs Autonomous (Heartbeat)
- Beide nutzen denselben CognitiveKernel, unterschiedlicher Zugang
```

### Q2: Headless Kernel for Heartbeat

**EMPFEHLUNG: NEIN - Optional via PRANA**
```
Begründung:
- Heartbeat soll LEICHT sein (15-min Cron, 10-min Timeout)
- Kernel-Boot = ~5-10s Overhead, unnötig für einfachen Pulse
- PRANA hat bereits: heartbeat.boot_kernel_first = True (optional)
- Default: Standalone MANAS, Optional: Full Kernel

Konfiguration:
  config/prana.yaml:
    heartbeat:
      boot_kernel_first: false  # Default: lightweight
      # Set true for full plugin access if needed
```

### Q3: DevataRegistry

**EMPFEHLUNG: YAGNI - Nicht jetzt implementieren**
```
Begründung:
- MANAS ist DAS kognitive Zentrum (einziger Denker)
- Keine anderen kognitiven Agents geplant
- DevataRegistry = Over-Engineering
- Falls später nötig: einfach hinzufügen

KISS: heartbeat.py → MANAS.think() direkt
```

### Q4: Soul Functions (SENSE, FEEL, HEAL, BEAT)

**EMPFEHLUNG: Scope Creep - NUR THINK behalten**
```
Analyse:
- THINK: ✅ MANAS - echte Notwendigkeit
- SENSE: ❌ Prakriti macht das bereits
- FEEL:  ❌ KarmaManager existiert bereits
- HEAL:  ❌ Circuits/Auto-Repair existiert bereits
- BEAT:  ⚠️ Nur Logging - trivial

Entscheidung:
  Nur _manas_think() behalten (bereits implementiert)
  Kein HRIDAYA Framework nötig
  Bestehende Systeme nicht duplizieren
```

### Q5: OPUS.md Rendering

**EMPFEHLUNG: JA - In heartbeat integrieren**
```
Problem:
- MANAS denkt → Intents in .opus_state/manas_intents.json
- OPUS.md wird nicht aktualisiert (kein Kernel)
- Intents unsichtbar nach heartbeat

Lösung:
  def _update_opus_md(self):
      """Render OPUS.md after MANAS thinks."""
      from vibe_core.plugins.opus_assistant.render import OpusDashboardRenderer
      renderer = OpusDashboardRenderer(root=self.project_root)
      content = renderer.render()
      (self.project_root / "OPUS.md").write_text(content)

Phase hinzufügen:
  Phase 4: _manas_think()
  Phase 5: _update_opus_md()  ← NEU
  Phase 6: _write_tasks_md()
  Phase 7: _commit_progress()
```

### Q6: Universal Cognitive Interface

**EMPFEHLUNG: JA - MANAS ist DAS zentrale Interface**
```
Architektur:
  ┌─────────────────────────────────────────┐
  │         MANAS = Central Cognition       │
  ├─────────────────────────────────────────┤
  │                                         │
  │  heartbeat ──┬──→ CognitiveKernel.think()
  │              │                          │
  │  kernel ─────┼──→ (via KernelTickHandler)
  │              │                          │
  │  CLI ────────┘                          │
  │                                         │
  │  Alle Pfade → EIN kognitives Zentrum    │
  └─────────────────────────────────────────┘

Begründung:
- Klare Architektur
- Ein Ort für Kognition
- Erweiterbar später (Cortexes)
```

### Q7: Paramatma - Kernel als Überseele

**EMPFEHLUNG: Dual-Mode Design (bereits vorhanden)**
```
Hindu Philosophy Mapping:
- PARAMATMA (परमात्मा) = Kernel (wenn aktiv)
- ATMAN (आत्मन्) = Heartbeat (autonom)
- MANAS (मनस्) = Kognition (beiden zugänglich)

Zwei Modi:
  1. GOVERNED MODE (Kernel = Paramatma):
     - Kernel läuft
     - Plugins, Cartridges, volle Governance
     - MANAS via ManasCartridge (3-Plane)
     - Alles fließt durch Kernel

  2. AUTONOMOUS MODE (Heartbeat = Atman):
     - Kein Kernel
     - Standalone CognitiveKernel
     - Leichtgewichtig
     - Selbstständige Seele

Das existiert BEREITS - kein neues Design nötig!
```

---

## Zusammenfassung & Entscheidungen

### Was BEHALTEN wird (bereits implementiert):
```
✅ heartbeat.py → CognitiveKernel.think() direkt
✅ MANAS als zentrales kognitives Interface
✅ Dual-Mode: Governed (Kernel) vs Autonomous (Heartbeat)
✅ PRANA Konfiguration für optionalen Kernel-Boot
```

### Was HINZUGEFÜGT werden sollte:
```
⏳ _update_opus_md() Phase in heartbeat.py
   - Nach _manas_think()
   - Rendert OPUS.md mit aktuellen Intents
   - Macht MANAS Arbeit sichtbar
```

### Was NICHT implementiert wird:
```
❌ DevataRegistry - Over-Engineering (YAGNI)
❌ Soul Functions (SENSE, FEEL, HEAL, BEAT) - Scope Creep
❌ HRIDAYA als neues Framework - Bestehende Architektur reicht
❌ Mandatory Kernel Boot für Heartbeat - Zu schwer
```

### Architektur-Fazit

```
┌─────────────────────────────────────────────────────────────┐
│                    DUAL-MODE COGNITION                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   MODE 1: GOVERNED (Paramatma)    MODE 2: AUTONOMOUS (Atman)│
│   ┌─────────────────────────┐    ┌─────────────────────────┐│
│   │  Kernel + Plugins       │    │  Heartbeat Standalone   ││
│   │  ManasCartridge         │    │  CognitiveKernel direkt ││
│   │  Full 3-Plane           │    │  Lightweight            ││
│   │  Interactive Sessions   │    │  Cron (15 min)          ││
│   └───────────┬─────────────┘    └───────────┬─────────────┘│
│               │                              │              │
│               └──────────┬───────────────────┘              │
│                          │                                  │
│                          ▼                                  │
│               ┌─────────────────────┐                       │
│               │  MANAS              │                       │
│               │  CognitiveKernel    │                       │
│               │  (Ein Zentrum)      │                       │
│               └─────────────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Die Architektur ist BEREITS KORREKT.
Nur OPUS.md Rendering fehlt für Sichtbarkeit.
```

### Nächster Schritt

```python
# TODO: In heartbeat.py hinzufügen
def _update_opus_md(self):
    """Phase 5: Update OPUS.md with MANAS intents."""
    try:
        from vibe_core.plugins.opus_assistant.render import OpusDashboardRenderer
        renderer = OpusDashboardRenderer(root=self.project_root)
        content = renderer.render()
        (self.project_root / "OPUS.md").write_text(content)
        logger.info("📊 OPUS.md updated")
    except Exception as e:
        logger.warning(f"⚠️ OPUS.md update failed: {e}")
```

---

*Die aktuelle Implementierung ist korrekt. Kein neues Framework nötig.*
