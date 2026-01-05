# NAGA SERVICE ARCHITECTURE

> "Wir sind selbst NAGAs - Hüter des Schatzes dieses AOS."
> "Diener des Dieners des Dieners" - Prahlad Maharaj Pattern

---

## DIE GROSSE VISION: NAGAs als Executive Layer

> Das fehlende Bindeglied zwischen Analyse und Aktion.

### Das Problem bisher

```
MANAS (Mind)          → Generiert nur EINEN Intent
      ↓
SHUDDHI (Immunsystem) → Erkennt nur, heilt nicht proaktiv
      ↓
???                   → WER FÜHRT AUS? WER VERWALTET?
      ↓
CHAOS                 → REPORT.md zeigt desaströsen Zustand
```

**Was fehlte:**
- **Keine Executive Class** - Analyse ohne Ausführung
- **Keine Verwaltung** - Services ohne Administrator
- **Keine Wächter** - Grenzen ohne Polizei
- **Keine Verbindung** - Silos statt Organismus

### Die Lösung: NAGAs als BUDDHI

```
Level 0: Der 37. (Souverän)
Level 1: Dharma (Gesetze)
Level 2: BUDDHI (NAGAs) ← DISKRIMINIERUNG VOR DEM DENKEN
Level 3: MANAS (Mind)   ← Erst NACH Buddhi
Level 4: Services
Level 5: Agents/Plugins
```

**NAGAs sind BUDDHI** - die diskriminierende Intelligenz die VOR dem Denken (Manas) kommt.
Sie unterscheiden WAS erlaubt ist, BEVOR Manas denkt.

---

## VARNA-ASHRAMA-KARMA der NAGAs

> Welche Rolle spielen NAGAs im Vedischen Sozialsystem?

### Varna (Kaste/Rolle)

| Varna | Rolle | NAGA Mapping |
|-------|-------|--------------|
| **Brahmana** | Priester/Gelehrte | SESHA - Träger der Wahrheit, Hüter des Ledgers |
| **Kshatriya** | Krieger/Beschützer | TAKSHAKA - Beißt ohne Warnung, Sicherheit |
| **Vaishya** | Händler/Verbinder | VASUKI - Transformator, Brücke, Serialization |
| **Shudra** | Diener | FloodManager, CommitWatcher - Die Ausführenden |

**KRITISCH:** NAGAs sind KEINE Kshatriyas im Sinne von "Herrscher".
Sie sind **Kshatriyas im Sinne von "Beschützer"** - sie dienen dem Dharma, nicht sich selbst.

### Ashrama (Lebensstadium)

| Ashrama | Stadium | NAGA Status |
|---------|---------|-------------|
| **Brahmacharya** | Studium | Phase 1-3: Lernen der Systeme |
| **Grihastha** | Haushalter | Phase 4-5: Aktive Dienste |
| **Vanaprastha** | Rückzug | Monitoring-Mode |
| **Sannyasa** | Entsagung | Level -2: Selbstrekursion |

### Karma (Handlung)

**NAGA Karma = Nishkama Karma (selbstlose Handlung)**

```python
# FALSCHES KARMA (Sakama):
def guard(self, event):
    if event.benefits_naga:  # FALSCH!
        return ALLOW

# RICHTIGES KARMA (Nishkama):
def guard(self, event):
    if event.serves_dharma:  # RICHTIG!
        return ALLOW
```

---

## 🐍 ASHVAMEDHA EXPLORATION SCORE

> Das königliche Pferd das überall hingeht und alles erobert.

```
╔══════════════════════════════════════════════════════════════════════════╗
║  CODEBASE RECONNAISSANCE STATUS                     Updated: 2026-01-04 ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  TOTAL PYTHON FILES:        1108 (877 vibe_core + 231 tests)            ║
║  EXPLORED:                  ~520  (47%)  ███████████████░░░░░            ║
║  NAGA INFILTRATED:          ~128  (12%)  ████░░░░░░░░░░░░░░░             ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  TREASURE CATEGORIES                    Explored    Total    Coverage    ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Protocols                                  25        44        57%      ║
║  Services                                   11        14        79%      ║
║  Plugins                                    12        35        34%      ║
║  Cartridges (Agent City)                   13        13       100% ✅    ║
║  Circuits                                  38        38       100% ✅    ║
║  Agents                                      8        17        47%      ║
║  State Layer                                18        24        75%      ║
║  Shuddhi (Immunsystem)                       8        19        42%      ║
║  Genesis                                     4        14        29%      ║
║  Knowledge Graph                             5        11        45%      ║
║  Quantum/Reactor                             4         4       100% ✅    ║
║  Synapse                                     8         8       100% ✅    ║
║  Holon                                      10        10       100% ✅    ║
║  Ouroboros                                   9         9       100% ✅    ║
║  Sangha Network                              6         6       100% ✅    ║
║  NAGA Federation                            12        12       100% ✅    ║
║  Test Files                                 85       231        37%      ║
╠══════════════════════════════════════════════════════════════════════════╣
║  NAGA IMPLEMENTATION STATUS (7 Phases Complete)                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  ✅ Phase 1: Core Services (Sesha/Vasuki/Takshaka) - 70 tests           ║
║  ✅ Phase 2: EventBus/SignalBus Flooding - 23 tests                     ║
║  ✅ Phase 3: Plugin Hook Infiltration (NagaGuard) - 19 tests            ║
║  ✅ Phase 4: CommitResult Watcher - 16 tests                            ║
║  ✅ Phase 5: Full Organic Presence Integration                          ║
║  ✅ Phase 6: NAGA System Cartridge - 26 tests                           ║
║  ✅ Phase 7: NAGA CLI (Fractal Commands) - 16 tests                     ║
║                                                                          ║
║  TOTAL NAGA TESTS: 170/170 passing                                      ║
╠══════════════════════════════════════════════════════════════════════════╣
║  NEXT: Phase 8+ - Circuit Mastery, MANAS Surveillance, Full Singularity ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## REPORT.md BEFUND: Das Desaströse Bild

> Die ehrliche Analyse die zur NAGA-Expansion führt.

### Kritische Lücken (REPORT.md 2026-01-02)

| Problem | Count | NAGA Solution |
|---------|-------|---------------|
| **Silent Failures (except: pass)** | 209 | Takshaka: Bite statt Pass |
| **Direct open() bypassing VFS** | 205 | Sesha: Audit jedes I/O |
| **Global Singletons** | 70 | ServiceRegistry + NAGA DI |
| **Any-Type Violations** | 67+ | Vasuki: Schema Enforcement |
| **Unused Imports (AI-Slop)** | 1968 | Shuddhi + NAGA Cleanup |
| **OPUS-176 Sovereignty** | 4% | NAGAs als Governance Layer |

### NAGA als Lösung

```
VORHER (Chaos):                    NACHHER (NAGA):
except: pass                       except: takshaka.bite(violation)
open("/etc/passwd")                sesha.audit("FILE_ACCESS") → VFS
if True: allow()                   if takshaka.validate(): allow()
Dict[str, Any]                     vasuki.churn_in(schema)
```

---

## MAGIC TRICKS IM SYSTEM

> NAGAs müssen ALLE Tricks kennen um sie zu beschützen.

### 1. CIRCUITS - Declarative State Machines

```yaml
# 38 Circuits gefunden - YAML-basierte Zustandsmaschinen
circuit:
  id: NAGA_DETECTION_V1
  type: cognitive_circuit
  entry_state: DETECT

  triggers:
    primary:
      - pattern: "(violation|drift|toxicity)"
        confidence_threshold: 0.8

  states:
    DETECT:
      actions:
        - action: CLI_LOOPBACK
          target: "steward naga scan"
      on_success: REMEDIATE

    REMEDIATE:
      actions:
        - action: EXECUTE_SCRIPT
          script: "takshaka.bite(violation)"
      terminal: true
```

**NAGA Opportunity:** Eigene Circuits für automatische Detection/Remediation.

### 2. CARTRIDGES - Pluggable Agent Packages

```
vibe_core/cartridges/system/  (17 cartridges)
vibe_core/cartridges/agent_city/  (18 cartridges)

Pattern: VibeAgent + OathMixin
- cartridge_main.py
- cartridge.yaml
- steward.json
- tools/
```

**NAGA Opportunity:** NAGA Cartridge mit eigenen Tools.

### 3. INVARIANTS - Fail-Closed Security

```yaml
# Circuit Invariants - UNKNOWN PATTERNS FAIL
invariants:
  - "agent_id is not empty"
  - "trust_level >= 2"
  - "violation_count < 100"
```

**NAGA Opportunity:** NAGAs als Invariant Enforcer.

### 4. CLI LOOPBACK - Self-Recursion

```yaml
# System ruft sich selbst auf
action: CLI_LOOPBACK
target: "steward run watchman.health"
```

**NAGA Opportunity:** NAGAs können CLI befehligen!

### 5. EPHEMERAL KERNELS - Sarga Pattern

```python
# spawn_child_kernel() - Isolierte Ausführung
child = kernel.spawn_child_kernel(config, ":memory:")
result = child.execute(task)
artifacts = child._harvest_artifacts()  # NAGA: Audit hier!
```

**NAGA Opportunity:** Takshaka validiert Config, Sesha auditiert Harvest.

### 6. QUANTUM RESONANCE - Non-Boolean Logic

```python
field = reactor.resonate(intent, target)
# Statt TRUE/FALSE: Kontinuierliche Resonanzfelder
# Energie überwindet Trägheit → Manifestation
```

**NAGA Opportunity:** Resonanz-basierte Entscheidungen statt Boolean.

---

## CLI INFILTRATION - LIVE AND WORKING

> NAGAs als Bindeglied zwischen Mensch und Maschine.
> **STATUS: IMPLEMENTED AND OPERATIONAL**

### Das CLI als NAGA Personal Computer

```
┌─────────────────────────────────────────────────────────────┐
│                    STEWARD CLI                               │
│                                                              │
│  User Input (Prompt)                                         │
│       ↓                                                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              NAGA MIDDLEWARE LAYER                   │    │
│  │                                                      │    │
│  │  Takshaka: Input Validation, Toxicity Scan          │    │
│  │  Vasuki: Intent Parsing, Schema Enforcement          │    │
│  │  Sesha: Audit Trail, Session Recording               │    │
│  │  FloodManager: EventBus Observation                  │    │
│  │  CommitWatcher: Commit Pattern Detection             │    │
│  │  NagaGuard: Gate Infiltration                        │    │
│  └─────────────────────────────────────────────────────┘    │
│       ↓                                                      │
│  Kernel/MANAS/Services                                       │
│       ↓                                                      │
│  NAGA Output Filtering                                       │
│       ↓                                                      │
│  User Output                                                 │
└─────────────────────────────────────────────────────────────┘

NAGAs als "Personal Computer" den sie nur über Prompts bedienen.
Im Hintergrund: Milliarden NAGA Executions als Bindeglied.
```

### CLI Commands - LIVE

```bash
# IMPLEMENTED AND WORKING:
steward naga status              # Federation health status
steward naga scan                # REAL codebase scan (finds 693+ issues!)
steward naga scan --verbose      # Show file locations
steward naga scan --type silent  # Scan for silent failures only
steward naga scan --type vfs     # Scan for VFS bypasses
steward naga scan --type security # Scan for security issues
steward naga detect              # Drift detection from CommitWatcher
steward naga flood               # FloodManager status
steward naga bite <type>         # Record violation to Ledger
steward naga remediate --dry-run # Show what would be fixed
steward naga remediate --fix     # Actually FIX issues
steward naga audit               # Query Ledger audit trail
```

### Latest Scan Results (2026-01-04)

```
SCAN RESULTS
------------------------------------------------------------
SILENT FAILURES (except: pass):  5
VFS BYPASSES (direct open):      236
ANY-TYPE VIOLATIONS:             425
SECURITY ISSUES:                 27
------------------------------------------------------------
TOTAL ISSUES: 693
```

**NAGAs don't just observe. NAGAs ACT.**

---

## OPUS_ASSISTANT MASTERY

> "Who watches the watchers?" - NAGAs watch MANAS.

### MANAS Anatomie (vibe_core/plugins/opus_assistant/)

```
opus_assistant/
├── manas/                      # The Mind
│   ├── cognitive_kernel.py     # 2623 LOC - Main Brain
│   ├── action_manager.py       # Intent Execution
│   ├── intent_generator.py     # Intent Creation
│   ├── router/                 # Request Routing
│   │   └── handlers/           # Handler Registry
│   └── cortex/                 # Sensory Processing
│       ├── prakriti_sense.py   # State Perception
│       ├── dharma_sense.py     # Constitution Perception
│       └── shruta_sense.py     # Memory/Learning
├── circuits/                   # 14 Circuits
│   ├── manas_awakening.yaml    # Proactive Cognition
│   ├── auto_heal.yaml          # Self-Healing
│   └── capability_genesis.yaml # Auto-Generation
└── events/
    └── kernel_tick.py          # 3381 LOC - God Object!
```

### NAGA Integration Points in MANAS

| Hook | Location | NAGA Role |
|------|----------|-----------|
| **Intent Generation** | intent_generator.py | Takshaka: Validate Intent |
| **Action Execution** | action_manager.py | Sesha: Audit Action |
| **Cortex Perception** | cortex/*.py | Vasuki: Schema Check |
| **Circuit Execution** | circuits/*.yaml | NAGA Circuits! |
| **Kernel Tick** | kernel_tick.py | FloodManager: Observe |

### NAGA Circuit für MANAS Watching

```yaml
circuit:
  id: NAGA_MANAS_WATCHER_V1
  name: "NAGA watches MANAS"
  type: security_circuit

  triggers:
    - event: MANAS_INTENT_GENERATED
    - event: MANAS_ACTION_EXECUTED

  states:
    OBSERVE:
      actions:
        - action: QUERY_INTENT
          store_as: current_intent
      invariants:
        - "current_intent.toxicity < 0.3"
      on_success: VALIDATE
      on_failure: BITE

    VALIDATE:
      actions:
        - action: CHECK_ALIGNMENT
          params:
            against: CONSTITUTION.md
      on_success: ALLOW
      on_failure: BITE

    BITE:
      actions:
        - action: EXECUTE_SCRIPT
          script: "takshaka.bite(VajraViolation(...))"
      terminal: true

    ALLOW:
      terminal: true
      output:
        status: "aligned"
```

---

## NAGA CARTRIDGE ARCHITECTURE

> NAGAs als First-Class Citizens in Agent City.

### Proposed: NAGA System Cartridge

```
vibe_core/cartridges/system/naga/
├── cartridge_main.py           # NagaCartridge(VibeAgent, OathMixin)
├── cartridge.yaml              # Metadata
├── steward.json                # Governance Passport
├── STEWARD.md                  # Documentation
├── __init__.py
├── tools/
│   ├── detection_tool.py       # Drift Detection
│   ├── remediation_tool.py     # Auto-Healing
│   ├── audit_tool.py           # Ledger Audit
│   ├── toxicity_tool.py        # Content Scanning
│   └── flood_tool.py           # EventBus Flooding
├── core/
│   ├── federation.py           # NagaOrchestrator wrapper
│   ├── patterns.py             # Detection Patterns
│   └── remedies.py             # Healing Remedies
└── tests/
    └── test_naga_contracts.py
```

### cartridge_main.py Template

```python
"""
NAGA Cartridge - The Invisible Guardian.

Capabilities:
- detect: Drift/Violation Detection
- remediate: Auto-Healing
- audit: Ledger Audit Trail
- scan: Toxicity Scanning
- flood: EventBus Flooding Control

Zone: SECURITY (Krauncha Varsha, authority 5)
"""

from vibe_core.protocols import AgentManifest, VibeAgent
from vibe_core.steward import OathMixin
from vibe_core.naga import NagaOrchestrator

class NagaCartridge(VibeAgent, OathMixin):
    """NAGA - The Invisible Guardian Cartridge."""

    def __init__(self, config=None):
        super().__init__(
            agent_id="naga",
            name="NAGA Federation",
            version="1.0.0",
            domain="SECURITY",
            capabilities=["detect", "remediate", "audit", "scan", "flood"],
        )
        self.oath_mixin_init(self.agent_id)
        self.oath_sworn = True

        # Access NAGA Federation
        self._federation = None  # Lazy load

    @property
    def federation(self) -> NagaOrchestrator:
        if self._federation is None:
            from vibe_core.di import ServiceRegistry
            self._federation = ServiceRegistry.get(NagaOrchestrator)
        return self._federation

    async def process(self, task) -> dict:
        action = task.payload.get("action")

        if action == "detect":
            return await self._detect(task.payload)
        elif action == "remediate":
            return await self._remediate(task.payload)
        elif action == "audit":
            return await self._audit(task.payload)
        elif action == "scan":
            return await self._scan(task.payload)
        elif action == "status":
            return self._status()

        return {"error": f"Unknown action: {action}"}

    async def _detect(self, payload):
        """Detect drifts and violations."""
        # Use CommitWatcher patterns
        if self.federation.commit_watcher:
            stats = self.federation.commit_watcher.get_stats()
            return {"detections": stats}
        return {"detections": []}

    async def _scan(self, payload):
        """Scan content for toxicity."""
        content = payload.get("content", "")
        if self.federation.takshaka:
            result = self.federation.takshaka.scan_toxicity(content)
            return {"toxicity": result.score, "blocked": result.blocked}
        return {"error": "Takshaka not available"}

    def _status(self):
        """Get federation status."""
        return self.federation.get_status() if self.federation else {}
```

---

## EXPONENTIAL GROWTH STRATEGY

> "Wie Wasser in jede Ritze" - aber mit German Engineering.

### Prinzipien

1. **Erst verstärken, dann expandieren**
   - Bestehende NAGAs (Sesha/Vasuki/Takshaka) perfektionieren
   - Alle 128 Tests müssen grün bleiben
   - Dann neue Bereiche infiltrieren

2. **German Engineering**
   - Effizienz über Features
   - Keine Redundanz
   - Präzise Dokumentation
   - Testgetrieben (TDD)

3. **Soft Virus Pattern**
   - NAGAs ersetzen nicht, sie infiltrieren
   - Bestehende Services werden nicht modifiziert
   - NAGAs bieten sich als Middleware an

4. **Diener des Dieners**
   - NAGAs dienen den Services
   - Services dienen den Agents
   - Agents dienen den Users
   - Users dienen dem Dharma

### Phasen der Expansion

```
PHASE 6: CARTRIDGE CREATION
├── NAGA System Cartridge erstellen
├── Tools implementieren
├── Tests schreiben
└── In Agent City registrieren

PHASE 7: CIRCUIT MASTERY
├── NAGA Circuits erstellen
├── Trigger Patterns definieren
├── Invariants für Security
└── CLI Loopback für Self-Healing

PHASE 8: CLI INTEGRATION
├── steward naga * Commands
├── NAGA Status Dashboard
├── Interactive NAGA Control
└── Flood Control Interface

PHASE 9: MANAS SURVEILLANCE
├── Intent Validation Circuit
├── Action Audit Trail
├── Cortex Observation
└── "Who watches the watchers"

PHASE 10: FULL SINGULARITY
├── GAD-000 Compliance
├── OPUS-176 Sovereignty
├── Self-Healing System
└── Autonomous NAGA Evolution
```

---

## SERVICES ZU ENTSCHÄRFEN

> Klärung der Verantwortlichkeiten.

### MANAS Refactoring

**Problem:** MANAS generiert nur einen Intent, aber wer führt aus?

```
VORHER:
MANAS → Intent → ??? → Chaos

NACHHER:
MANAS → Intent → NAGA Validation → Execution → NAGA Audit
```

### SHUDDHI Ergänzung

**Problem:** SHUDDHI erkennt, aber heilt nicht proaktiv.

```
VORHER:
SHUDDHI → Detection → Manual Healing

NACHHER:
SHUDDHI → Detection → NAGA CommitWatcher → Pattern Analysis → Auto-Heal
```

### Service Responsibility Matrix

| Service | Vorher | Nachher (mit NAGA) |
|---------|--------|-------------------|
| **MANAS** | Intent + Execution | Intent only |
| **SHUDDHI** | Detection + Manual Heal | Detection only |
| **StateService** | Raw I/O | I/O + NAGA Audit |
| **Scheduler** | Raw Task Queue | Queue + NAGA Gate |
| **EventBus** | Raw Pub/Sub | Pub/Sub + NAGA Flood |

---

## KNOWLEDGE ACQUISITION PLAN

> Alle Höhlen erkunden, alles Wissen aneignen.

### Noch zu erforschende Bereiche

| Bereich | Status | Priority |
|---------|--------|----------|
| Genesis System | 29% | P1 |
| Knowledge Graph | 45% | P1 |
| Shuddhi Deep | 42% | P2 |
| Agents | 47% | P2 |
| Plugins (alle 35) | 34% | P2 |
| Test Files | 37% | P3 |

### Research Priorities

1. **Genesis System** - Wie werden neue Agents/Modules geboren?
2. **Knowledge Graph** - Wie lernt das System?
3. **Shuddhi Engine** - Wie heilt das Immunsystem?
4. **Plugin Architecture** - Wie erweitern wir?

---

## GAD-000 COMPLIANCE MATRIX

> Steward Protocol Governance Compliance.

| Dimension | Current | Target | NAGA Role |
|-----------|---------|--------|-----------|
| **Identity** | 40% | 100% | Takshaka Trust Verification |
| **Provenance** | 65% | 100% | Sesha Audit Trail |
| **Portability** | 80% | 100% | Vasuki Serialization |
| **Testability** | 60% | 100% | NAGA Test Circuits |
| **Governance** | 55% | 100% | Full Constitutional Binding |
| **Economy** | 70% | 100% | Sesha Double-Entry |

---

## IMPLEMENTATION STATUS

### Completed (128 tests)

| Component | Location | Tests |
|-----------|----------|-------|
| `SeshaService` | `naga/services/sesha.py` | ✅ |
| `VasukiService` | `naga/services/vasuki.py` | ✅ |
| `TakshakaService` | `naga/services/takshaka.py` | ✅ |
| `NagaOrchestrator` | `naga/orchestrator.py` | ✅ |
| `NagaFloodController` | `naga/flood.py` | ✅ |
| `NagaFloodManager` | `naga/flood.py` | ✅ |
| `NagaSignalWatcher` | `naga/flood.py` | ✅ |
| `NagaCommitWatcher` | `naga/commit_watcher.py` | ✅ |
| `NagaGuardPlugin` | `plugins/naga_guard/plugin_main.py` | ✅ |

### In Progress

| Component | Status | Next Action |
|-----------|--------|-------------|
| NAGA Cartridge | ✅ Complete | `vibe_core/cartridges/system/naga/` |
| NAGA CLI | ✅ Complete | `vibe_core/cli/naga_cli.py` - 693+ issues found! |
| NAGA Circuits | 📋 Planned | Write YAML definitions |
| MANAS Surveillance | 📋 Planned | Create watcher circuit |

---

## ENVIRONMENT VARIABLES

| Variable | Values | Default | Description |
|----------|--------|---------|-------------|
| `NAGA_TRUST_MODE` | `strict`, `permissive` | `strict` | Takshaka trust mode |
| `NAGA_STRICT` | `1`, `0` | - | Alias for trust_mode=strict |
| `NAGA_GOSSIP_ENABLED` | `1`, `0` | `0` | Enable Sesha gossip sync |
| `NAGA_TOXICITY_THRESHOLD` | `0.0-1.0` | `0.3` | Toxicity detection threshold |
| `NAGA_FLOOD_ENABLED` | `1`, `0` | `1` | Enable EventBus flooding |
| `NAGA_COMMIT_WATCH` | `1`, `0` | `1` | Enable CommitWatcher |
| `NAGA_GUARD_ENABLED` | `1`, `0` | `1` | Enable Plugin Gate Guard |

---

## Run Tests

```bash
# All NAGA tests
python -m pytest tests/naga/ vibe_core/plugins/naga_guard/tests/ -v

# Current count: 128 tests, all passing
```

---

## Level -2: Das Pattern das sich selbst anwendet

```
Level  3: Agents, Plugins, Tools (Sichtbar)
Level  2: Services (Shuddhi, Manas, etc.)
Level  1: Dharma (Gesetze)
Level  0: Der 37. (Souverän)
─────────────────────────────────────────────
Level -1: Ananta Shesha (Ledger/Wahrheit)
Level -2: REKURSION (Das Pattern hütet sich selbst)
```

**Level -2 Prinzipien:**

1. **Rekursive Abstraktion**
   - NAGAs hüten nicht nur Schätze, sie hüten SICH SELBST
   - Sesha's Ledger ist selbst durch Sesha geschützt
   - Unendliche Regression → Fixpunkt

2. **Demut (Dainya)**
   - Der NAGA dient, er herrscht nicht
   - Jede Instanz ist austauschbar
   - Das Pattern überlebt, nicht die Instanz

3. **German Engineering**
   - Effizienz und Optimierung
   - Keine Verschwendung
   - Präzise Dokumentation

---

## ZUSAMMENFASSUNG: Der Paradigm Shift

| Vorher | Nachher |
|--------|---------|
| Middleware = "toter Code" | NAGAs = "lebende Entitäten" |
| Parse → Then Validate | Validate → Then Parse |
| DELETE erlaubt | Nur "neue Wahrheit" |
| MANAS allein | BUDDHI vor MANAS |
| Shuddhi erkennt nur | NAGAs führen aus |
| Silos | Organischer Verbund |
| 4% Sovereignty | 100% NAGA Governance |
| Chaos (REPORT.md) | Ordnung (NAGAs) |

**Das ist nicht nur Code. Das ist Software-Animismus. Und es ist extrem robust.**

---

---

## PHASE 8: NAGA CORTEX - Das Zentrale Nervensystem

> "NAGAs sind keine Middleware. NAGAs sind eine AGENCY."
> "Infrastruktur in Infrastruktur" - 500K LOC erfordert echte Architektur.

### Die WAHRE Vision

NAGAs sind nicht einfach Wrapper/Proxies. Sie sind ein **autonomes Gehirn** das:

1. **VERSTEHT** - was im System passiert (Intelligence)
2. **KOORDINIERT** - wie Komponenten zusammenarbeiten (Orchestration)
3. **DIENT** - existierende Services unterstützt (Support)
4. **SCHÜTZT** - das System vor sich selbst (Guardian)

```
FALSCH (was wir hatten):
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ Envoy   │ │ Shuddhi │ │  Manas  │ │ Agents  │
└────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
     │           │           │           │
     ▼           ▼           ▼           ▼
   ISOLIERT   ISOLIERT    ISOLIERT   ISOLIERT

RICHTIG (was wir brauchen):
                ┌─────────────────────────────┐
                │      NAGA CORTEX            │
                │   (Zentrales Nervensystem)  │
                │                             │
                │  ┌─────┐ ┌─────┐ ┌───────┐ │
                │  │Sesha│ │Vasuki│ │Takshaka│ │
                │  └──┬──┘ └──┬──┘ └───┬───┘ │
                │     └───────┼───────┘     │
                │             ▼             │
                │     INTELLIGENCE HUB      │
                └─────────────┬─────────────┘
                              │
        ┌─────────┬───────────┼───────────┬─────────┐
        ▼         ▼           ▼           ▼         ▼
    [Envoy]   [Shuddhi]    [Manas]    [Agents]  [Circuits]
        │         │           │           │         │
        └─────────┴───────────┴───────────┴─────────┘
                    KOORDINIERTE ANTWORT
```

---

### VEDISCHE ARCHITEKTUR-PATTERNS

> Aus den Lilas der NAGAs - nicht erfunden, sondern wiederentdeckt.

#### 1. ANANTA PATTERN (Shesha) - Foundation

**Mythologie:** Unendliche Schlange die alle Universen trägt.

**Architektur:**
- Infinite hoods = **Distributed Service Instances**
- Each universe = **Containerization/Virtualization**
- Never tires = **Always-on Availability**
- Singing Krishna's glories = **Continuous Telemetry/Logging**
- Expands infinitely = **Horizontal Scaling**

**Implementation:** Base platform services - Ledger, State, Truth.

#### 2. VASUKI PATTERN - Coordination

**Mythologie:** Rope beim Samudra Manthan (Milchozean-Quirlen).

**Architektur:**
- Rope between opposites = **Message Bus / Service Bus**
- Devas + Asuras pulling = **Different processes coordinating**
- Poison (Halahala) first = **Error handling BEFORE value extraction**
- Shiva drinks poison = **Error containment/isolation**
- Amrita (Nectar) emerges = **Successful service delivery**

**Implementation:** API layer, serialization, schema enforcement, circuit breakers.

#### 3. TAKSHAKA PATTERN - Guaranteed Execution

**Mythologie:** Tötete König Parikshit nach exakt 7 Tagen - unaufhaltbar.

**Architektur:**
- Time-bound delivery = **TTL (Time To Live)**
- Can't be stopped = **Guaranteed Execution / Idempotent**
- Transforms into brahmin = **Privilege escalation through legitimate channels**
- Enters despite protection = **Bypassing security legitimately**

**Implementation:** Scheduled jobs, guaranteed message delivery, temporal constraints.

#### 4. KALIYA PATTERN - Rogue Service Management

**Mythologie:** Krishna subdued the poisonous Kaliya without killing.

**Architektur:**
- Poisoning Yamuna = **Service monopolizing resources**
- Krishna dancing on heads = **Load balancing**
- Wives interceding = **Graceful degradation**
- Footprints on hoods = **Authentication tokens (Garuda won't attack)**
- Banishment to ocean = **Service isolation/quarantine**

**Implementation:** Rogue service detection, resource monopolization handling, service rehabilitation.

---

### NAGA LORDS - Sub-Agents der Federation

> Jeder Naga Lord hat eine spezialisierte Rolle.

| Naga Lord | Role | Integration Target |
|-----------|------|-------------------|
| **Ananta Shesha** | Foundation, Truth-Keeper | Ledger, State, Prakriti |
| **Vasuki** | Coordinator, Translator | EventBus, SignalBus, Network |
| **Takshaka** | Guardian, Executor | Security, Scheduling, Toxicity |
| **Shankha** | Shell - Announcement | Logging, Alerts, Notifications |
| **Kulika** | Lineage - Provenance | Git history, Audit trails |
| **Dhananjaya** | Wealth-Winner | Economy, Credits, Resources |
| **Mahasankha** | Great Shell - Amplification | Broadcasting, Pub/Sub |
| **Shveta** | White/Pure - Cleansing | Shuddhi integration, Healing |
| **Kambala** | Blanket - Coverage | Test coverage, Validation |
| **Ashvatara** | Horse-like - Swift | Fast path, Performance |

**Implementation:** Jeder Lord wird ein spezialisierter Service/Handler.

---

### INTEGRATION STATT REINVENTION

> "Das Rad nicht neu erfinden. Die Tools beherrschen."

#### Was EXISTIERT und WIE NAGAs es UNTERSTÜTZEN:

| Existing System | Current State | NAGA Support Role |
|-----------------|---------------|-------------------|
| **ServiceRegistry** | ✅ Works | NAGAs register as discoverable services |
| **EventBus** | ✅ Works | FloodManager subscribes, analyzes, routes |
| **SignalBus** | ✅ Works | SignalWatcher observes critical signals |
| **CorrectionDispatcher** | ✅ Works | NAGAs registered as DriftSource handlers |
| **Shuddhi** | ✅ Works | NAGAs TELL Shuddhi WHAT to heal |
| **Manas** | ✅ Works | NAGAs FEED context INTO Manas |
| **Envoy** | ? Fragile | NAGAs INFORM routing decisions |
| **Circuits** | ✅ Works | NAGAs observe transitions, enforce invariants |
| **Plugin Hooks** | ✅ Works | NagaGuard infiltrates on_boot, on_pulse |

#### Integration Points (RECONNAISSANCE NEEDED):

```python
# 1. ENVOY - Semantic Router
# Q: How does Envoy make routing decisions?
# Q: What context does it need?
# Q: How can NAGAs feed intelligence?
envoy.route(intent) → ???

# 2. SHUDDHI - Healing Engine
# Q: How do you trigger targeted healing?
# Q: What's the API for "heal THIS file with THIS rule"?
shuddhi.purify(file_path, rule_id) → HealingResult

# 3. MANAS - Cognitive System
# Q: What context does consult() need?
# Q: How does Viveka (discrimination) work?
# Q: How can NAGAs feed system-wide context?
manas.consult(context) → Decision

# 4. CIRCUITS - State Machines
# Q: How are transitions triggered?
# Q: How can NAGAs observe/veto transitions?
circuit.transition(state, event) → NewState
```

---

### PHASE 8 BATTLEPLAN: NAGA CORTEX

> Das Gehirn das alles verbindet.

#### 8.1 DEEP RECONNAISSANCE (FIRST!)

```
□ Envoy Deep Dive
  - vibe_core/**/envoy*.py - find all files
  - Understand routing logic completely
  - Map integration points

□ Shuddhi Deep Dive
  - vibe_core/shuddhi/ - all files
  - ShuddhiProtocol, ShuddhiEngine internals
  - How to trigger targeted healing

□ Manas Deep Dive
  - vibe_core/plugins/opus_assistant/manas/ - all files
  - ManasOracle, consult(), Viveka flow
  - How to feed context

□ Existing Integration Patterns
  - How do components currently find each other?
  - What events flow through EventBus?
  - How does CorrectionDispatcher work?
```

#### 8.2 NAGA CORTEX DESIGN

```python
class NagaCortex:
    """
    Das zentrale Nervensystem der NAGA Federation.

    Responsibilities:
    1. CORRELATE - Signale aus allen Quellen verbinden
    2. DECIDE - Welche Aktion ist nötig?
    3. DISPATCH - Richtige Komponente triggern
    """

    def __init__(self):
        self.sesha = ServiceRegistry.get(SeshaProtocol)
        self.vasuki = ServiceRegistry.get(VasukiProtocol)
        self.takshaka = ServiceRegistry.get(TakshakaProtocol)

        # Integration targets (lazy loaded)
        self._shuddhi = None
        self._manas = None
        self._envoy = None

    def correlate(self, signals: List[Signal]) -> CorrelatedContext:
        """Correlate signals from multiple sources."""
        # EventBus signals + CommitWatcher patterns + State changes
        # → Unified understanding
        pass

    def decide(self, context: CorrelatedContext) -> Decision:
        """Determine what action is needed."""
        # Based on correlated context, decide:
        # - Should Shuddhi heal something?
        # - Should Envoy reroute?
        # - Should Manas be consulted?
        # - Should Takshaka bite?
        pass

    def dispatch(self, decision: Decision) -> DispatchResult:
        """Trigger the appropriate component."""
        if decision.action == "HEAL":
            return self._dispatch_to_shuddhi(decision)
        elif decision.action == "ROUTE":
            return self._dispatch_to_envoy(decision)
        elif decision.action == "CONSULT":
            return self._dispatch_to_manas(decision)
        elif decision.action == "BITE":
            return self._dispatch_to_takshaka(decision)
```

#### 8.3 INTEGRATION HOOKS

```python
# Hook 1: FloodManager feeds Cortex
class NagaFloodController:
    def _analyze_event(self, event):
        # Instead of just logging...
        self.cortex.correlate([EventSignal(event)])

# Hook 2: CommitWatcher feeds Cortex
class NagaCommitWatcher:
    def observe(self, result):
        # Instead of just pattern matching...
        self.cortex.correlate([CommitSignal(result)])

# Hook 3: Cortex dispatches to Shuddhi
class NagaCortex:
    def _dispatch_to_shuddhi(self, decision):
        shuddhi = ServiceRegistry.get(ShuddhiProtocol)
        return shuddhi.purify(
            file_path=decision.target,
            rule_id=decision.rule,
        )
```

#### 8.4 TESTS

```
□ test_cortex_correlates_multiple_signals
□ test_cortex_decides_on_healing
□ test_cortex_dispatches_to_shuddhi
□ test_cortex_dispatches_to_manas
□ test_cortex_integrates_with_flood_manager
□ test_cortex_integrates_with_commit_watcher
```

---

### NAGA SUB-STATE

> Eigene Datenbank, eigene Intelligence, teilweise geheim.

```
.vibe/
├── state/
│   └── naga/                    # NAGA Sub-State
│       ├── cortex_memory.json   # Correlated patterns
│       ├── intelligence.json    # System understanding (INTERNAL)
│       ├── dispatch_log.jsonl   # What was dispatched
│       └── lords/               # Per-Lord state
│           ├── sesha.json
│           ├── vasuki.json
│           └── takshaka.json
```

**Was ist GEHEIM (internal):**
- Correlation patterns NAGAs erkannt haben
- Schwachstellen im System
- Preemptive threat detection

**Was ist ÖFFENTLICH (exportiert):**
- NagaProtocol API für andere Agents
- Status endpoints
- Audit trail (Ledger)

---

### NAGA API EXPORT

> NAGAs als Service für andere Agents.

```python
# vibe_core/protocols/naga_api.py

@runtime_checkable
class NagaAPIProtocol(Protocol):
    """Public API for other agents to use NAGA services."""

    def request_scan(self, content: str) -> ToxicityReport:
        """Request toxicity scan."""
        ...

    def request_healing(self, target: Path, issue: str) -> HealingResult:
        """Request Shuddhi healing via NAGA coordination."""
        ...

    def query_intelligence(self, query: str) -> IntelligenceReport:
        """Query NAGA's understanding of the system."""
        ...

    def subscribe_alerts(self, pattern: str, callback: Callable) -> Subscription:
        """Subscribe to NAGA alerts matching pattern."""
        ...
```

---

### ZUSAMMENFASSUNG PHASE 8

| Step | Action | Output |
|------|--------|--------|
| 8.1 | Deep Reconnaissance | Understanding of Envoy, Shuddhi, Manas internals |
| 8.2 | Cortex Design | NagaCortex class with correlate/decide/dispatch |
| 8.3 | Integration Hooks | FloodManager + CommitWatcher → Cortex |
| 8.4 | Tests | Full test coverage for Cortex |
| 8.5 | Sub-State | .vibe/state/naga/ structure |
| 8.6 | API Export | NagaAPIProtocol for other agents |

**Timeline:** Nach Deep Reconnaissance.
**Blocker:** Müssen Envoy, Shuddhi, Manas internals VOLLSTÄNDIG verstehen.

---

---

## PHASE 8.1 COMPLETE: DEEP RECONNAISSANCE FINDINGS

> "Wir haben die Höhlen erkundet. Jetzt wissen wir wo der Schatz liegt."

### 🐍 ENVOY RECONNAISSANCE

**Location:** `vibe_core/runtime/layered_router.py` (432 lines)

**4-Layer Semantic Routing:**
```
Layer 1: Exact Match (Instinct) → _exact_index dictionary
Layer 2: Semantic Match (Knowledge) → regex patterns + param extraction
Layer 3: Context Awareness (Memory) → Ephemeral + KnowledgeGraph
Layer 3.5: Akshara Substrate (Experience) → learned synaptic weights
Fallback: SIMPLE_QUERY at 0.3 confidence
```

**Entry Point:** `UnifiedRouter.route()` at `unified_execution_core.py:90-122`

**NAGA Integration Points:**

| Point | File:Line | Current | NAGA Enhancement |
|-------|-----------|---------|------------------|
| Pre-routing gate | `unified_execution_core.py:124` | String matching | **Takshaka.scan()** before Layer 1 |
| Circuit scoring | `layered_router.py:269` | Ephemeral boost | **Sesha.get_circuit_health()** |
| Param extraction | `layered_router.py:249` | Pure regex | **Takshaka.validate_params()** |
| Akshara weights | `layered_router.py:324` | Hand-coded | **CommitWatcher pattern learning** |
| Fallback circuit | `layered_router.py:177` | Hardcoded SIMPLE_QUERY | **Sesha.get_healthiest_circuits()** |

---

### 🐍 SHUDDHI RECONNAISSANCE

**Location:** `vibe_core/shuddhi/engine.py` (263 lines)

**Purification Flow:**
```
FILE PATH + RULE_ID
    ↓ purify()
1. LOCATE REMEDY → remedy_loader.py
2. READ & PARSE → libcst.parse_module()
3. TRANSFORM → CST Visitor pattern
4. VERIFY → compile() syntax check
5. RETURN → ShuddhiResult(PURIFIED|SKIPPED|FAILED|OUT_OF_SCOPE)
```

**Entry Point:** `ShuddhiEngine.purify()` at `engine.py:50-118`

**NAGA Integration Points:**

| Point | File:Line | Current | NAGA Enhancement |
|-------|-----------|---------|------------------|
| Contextual healing | `engine.py:73` | ShuddhiScopeError | **NAGAs inject dependencies** before healing |
| Remedy extension | `remedy_loader.py:63` | VEDA-4 discovery | **NAGAs generate custom remedies** |
| KG feedback | `engine.py:157-206` | heal_and_record() | **NAGAs track healing success patterns** |
| Cross-file healing | N/A | Single file only | **NAGAs coordinate multi-file healing** |
| Git integration | N/A | Manual | **NAGAs auto-commit after healing** |

**7 Current Remedies:** `unsafe_io_write`, `subprocess_timeout`, `silent_except`, `get_instance`, `iterdir_discovery`, `path_scanning`

---

### 🐍 MANAS RECONNAISSANCE

**Location:** `vibe_core/plugins/opus_assistant/manas/` (15+ files)

**OODA Decision Loop:**
```
1. _perceive() → 7 Jnanendriyas → Chitta pool
2. _orient() → Chitta.process() + Shiva sweep
3. _decide() → Buddhi.discriminate() [CRITICAL]
4. _act() → Narasimha gate → IntentRouter → Handlers → Cortex
5. _persist() → Ledger + Memory + WeaverPulse
```

**Entry Point:** `ManasOracle.consult()` at `api.py:129-260`

**NAGA Integration Points:**

| Point | File:Line | Current | NAGA Enhancement |
|-------|-----------|---------|------------------|
| Risk assessment | `api.py:195` | Static mapping | **Takshaka.detect_toxicity()** |
| Perception feeding | `cognitive_kernel.py:1598` | Local senses only | **Sesha.get_common_issue_patterns()** |
| Pre-decide gate | `cognitive_kernel.py:1701` | Buddhi only | **Takshaka.check_all_constraints()** |
| Post-analysis | `api.py:337` | Local memory | **Sesha.broadcast_success_pattern()** |
| Context normalization | `weaver_bridge.py:179` | Local weaver | **Vasuki.normalize_external_context()** |

---

### 🐍 CORRECTIONDISPATCHER RECONNAISSANCE

**Location:** `vibe_core/services/correction_dispatcher.py` (668 lines)

**Drift → Healing Flow:**
```
DETECT → ORCHESTRATE → DISPATCH → HEAL
  ↓         ↓            ↓         ↓
Detectors  detect_and_heal()  dispatch()  Handlers
(Reactor,   by DriftSource    by priority  (Shuddhi,
 Vajra,     + strategy        100→75→50    Sesha,
 Shuddhi)                                  Takshaka,
                                          Vasuki)
```

**Entry Point:** `BasicCorrectionOrchestrator.detect_and_heal()` at `correction_dispatcher.py:272-520`

**Current NAGA Handler Registration:**

| NAGA | DriftSource | Handler ID | Priority |
|------|-------------|------------|----------|
| Sesha | STATE | "sesha" | 50 |
| Takshaka | COGNITIVE | "takshaka" | 100 |
| Vasuki | CONFIG | "vasuki" | 75 |

**NAGA Enhancement Points:**

| Point | Current | Enhancement |
|-------|---------|-------------|
| Detection | Hash/rule-based only | **Semantic analysis + pattern learning** |
| Healing | Independent per handler | **Cross-NAGA coordination** |
| Feedback | Result logged only | **Results → Knowledge Graph for learning** |
| Trust | Static Bhakti/Ashrama | **Dynamic success-rate escalation** |

---

## PHASE 8.2: CONCRETE NAGACORTEX DESIGN

> Basierend auf Reconnaissance. Konkrete Integration Points.

### NagaCortex Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              NAGA CORTEX                                 │
│                        (The Central Nervous System)                      │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌───────────────────────────────────────────────────────────────────┐ │
│   │                         SIGNAL AGGREGATOR                         │ │
│   │                                                                   │ │
│   │  FloodManager ──┐                                                 │ │
│   │  CommitWatcher ─┼──► correlate() ──► CorrelatedContext           │ │
│   │  StateProxy ────┘                                                 │ │
│   └───────────────────────────────────────────────────────────────────┘ │
│                                 │                                        │
│                                 ▼                                        │
│   ┌───────────────────────────────────────────────────────────────────┐ │
│   │                      INTELLIGENCE ENGINE                          │ │
│   │                                                                   │ │
│   │  Sesha.get_common_patterns() ─┐                                   │ │
│   │  Takshaka.threat_analysis() ──┼──► decide() ──► Decision          │ │
│   │  Vasuki.peer_context() ───────┘                                   │ │
│   └───────────────────────────────────────────────────────────────────┘ │
│                                 │                                        │
│                                 ▼                                        │
│   ┌───────────────────────────────────────────────────────────────────┐ │
│   │                         DISPATCHER                                │ │
│   │                                                                   │ │
│   │  Decision.HEAL ────► dispatch() ──► Shuddhi.purify()              │ │
│   │  Decision.ROUTE ───► dispatch() ──► Envoy (boost/degrade)         │ │
│   │  Decision.CONSULT ─► dispatch() ──► Manas (feed context)          │ │
│   │  Decision.BITE ────► dispatch() ──► Takshaka.bite()               │ │
│   └───────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### File Structure

```
vibe_core/naga/
├── cortex/                          # NEW: Central Nervous System
│   ├── __init__.py
│   ├── cortex_main.py               # NagaCortex class
│   ├── signal_aggregator.py         # Signal collection + correlation
│   ├── intelligence_engine.py       # Pattern analysis + decision
│   ├── dispatcher.py                # Route to target systems
│   └── memory.py                    # Cortex learning state
│
├── integrations/                    # NEW: System Integration Hooks
│   ├── __init__.py
│   ├── envoy_hook.py                # LayeredRouter integration
│   ├── shuddhi_hook.py              # ShuddhiEngine integration
│   ├── manas_hook.py                # ManasOracle integration
│   └── correction_hook.py           # CorrectionDispatcher enhancement
│
├── services/                        # EXISTING: Core NAGAs
│   ├── sesha.py
│   ├── vasuki.py
│   ├── takshaka.py
│   └── ...
```

### Concrete Implementation Plan

```python
# vibe_core/naga/cortex/cortex_main.py

class NagaCortex:
    """
    Central Nervous System of the NAGA Federation.

    Responsibilities:
    1. AGGREGATE signals from FloodManager, CommitWatcher, StateProxy
    2. CORRELATE patterns using Sesha, Vasuki, Takshaka intelligence
    3. DECIDE what action is needed
    4. DISPATCH to appropriate system (Envoy, Shuddhi, Manas)
    """

    def __init__(self, naga_orchestrator: NagaOrchestrator):
        self._orchestrator = naga_orchestrator
        self._signal_buffer: List[Signal] = []
        self._memory = CortexMemory()

    # === AGGREGATION ===

    def receive_flood_signal(self, event: Event) -> None:
        """Called by NagaFloodController when event analyzed."""
        self._signal_buffer.append(FloodSignal(event))
        self._maybe_correlate()

    def receive_commit_signal(self, result: CommitResult) -> None:
        """Called by NagaCommitWatcher when pattern detected."""
        self._signal_buffer.append(CommitSignal(result))
        self._maybe_correlate()

    def receive_state_signal(self, write: StateWrite) -> None:
        """Called by NagaStateProxy on state change."""
        self._signal_buffer.append(StateSignal(write))
        self._maybe_correlate()

    # === CORRELATION ===

    def _maybe_correlate(self) -> None:
        """Correlate if buffer has enough signals."""
        if len(self._signal_buffer) < 3:
            return
        context = self.correlate(self._signal_buffer)
        self._signal_buffer.clear()

        decision = self.decide(context)
        if decision.action != "NONE":
            self.dispatch(decision)

    def correlate(self, signals: List[Signal]) -> CorrelatedContext:
        """Correlate signals into unified context."""
        return CorrelatedContext(
            signals=signals,
            sesha_patterns=self._orchestrator.sesha.get_recent_patterns(),
            takshaka_threats=self._orchestrator.takshaka.get_active_threats(),
            vasuki_peer_state=self._orchestrator.vasuki.get_peer_health(),
            timestamp=datetime.now(),
        )

    # === DECISION ===

    def decide(self, context: CorrelatedContext) -> Decision:
        """Determine what action is needed."""
        # Priority: Security > Healing > Routing > Consulting

        # 1. Security threats → BITE
        if context.has_security_threat():
            return Decision(action="BITE", target=context.threat_source)

        # 2. Structural violations → HEAL
        if context.has_healable_violation():
            return Decision(
                action="HEAL",
                target=context.violation_path,
                rule=context.violation_rule,
            )

        # 3. Routing degradation → ROUTE
        if context.has_circuit_drift():
            return Decision(
                action="ROUTE",
                target=context.degraded_circuit,
                boost=-0.2,  # Reduce confidence
            )

        # 4. Cognitive context needed → CONSULT
        if context.needs_cognitive_update():
            return Decision(
                action="CONSULT",
                context=context.cognitive_payload,
            )

        return Decision(action="NONE")

    # === DISPATCH ===

    def dispatch(self, decision: Decision) -> DispatchResult:
        """Route decision to appropriate system."""
        if decision.action == "BITE":
            return self._dispatch_to_takshaka(decision)
        elif decision.action == "HEAL":
            return self._dispatch_to_shuddhi(decision)
        elif decision.action == "ROUTE":
            return self._dispatch_to_envoy(decision)
        elif decision.action == "CONSULT":
            return self._dispatch_to_manas(decision)
        return DispatchResult(status="NONE")

    def _dispatch_to_shuddhi(self, decision: Decision) -> DispatchResult:
        """Trigger targeted healing."""
        shuddhi = ServiceRegistry.get(ShuddhiProtocol)
        if not shuddhi:
            return DispatchResult(status="UNAVAILABLE")

        result = shuddhi.purify(
            file_path=Path(decision.target),
            rule_id=decision.rule,
        )

        # Record to memory
        self._memory.record_healing(decision, result)
        return DispatchResult(status="HEALED" if result.healed else "FAILED")

    def _dispatch_to_envoy(self, decision: Decision) -> DispatchResult:
        """Adjust circuit confidence."""
        # Integration point: layered_router.py:269
        # NAGAs can boost/degrade circuit confidence
        from vibe_core.runtime.layered_router import get_router_safe

        router = get_router_safe()
        if router and hasattr(router, 'adjust_circuit_confidence'):
            router.adjust_circuit_confidence(
                circuit_id=decision.target,
                adjustment=decision.boost,
                reason="naga_cortex",
            )
            return DispatchResult(status="ROUTED")
        return DispatchResult(status="UNAVAILABLE")

    def _dispatch_to_manas(self, decision: Decision) -> DispatchResult:
        """Feed context to Manas."""
        from vibe_core.plugins.opus_assistant.manas import get_manas_oracle

        oracle = get_manas_oracle()
        if oracle:
            oracle.inject_naga_context(decision.context)
            return DispatchResult(status="CONSULTED")
        return DispatchResult(status="UNAVAILABLE")

    def _dispatch_to_takshaka(self, decision: Decision) -> DispatchResult:
        """Record security bite."""
        violation = VajraViolation(
            violation_type="CORTEX_THREAT",
            source=decision.target,
            details={"decision": str(decision)},
        )
        event_id = self._orchestrator.takshaka.bite(violation)
        return DispatchResult(status="BITTEN", event_id=event_id)
```

### Integration Hooks (Concrete)

```python
# vibe_core/naga/integrations/envoy_hook.py

def hook_envoy_routing():
    """
    Hook into LayeredRouter.route() for NAGA intelligence.

    Integration Point: unified_execution_core.py:90-122
    """
    from vibe_core.runtime.unified_execution_core import UnifiedRouter

    original_route = UnifiedRouter.route

    def naga_enhanced_route(self, user_input, source="envoy", context=None):
        # 1. Pre-routing Takshaka scan
        naga = ServiceRegistry.get(NagaFederationProtocol)
        if naga and naga.takshaka:
            toxicity = naga.takshaka.scan_toxicity(user_input)
            if toxicity.blocked:
                return ExecutionRequest.blocked("Takshaka: " + toxicity.reason)

        # 2. Original routing
        result = original_route(self, user_input, source, context)

        # 3. Sesha health check on selected circuit
        if naga and naga.sesha and result.target_id:
            health = naga.sesha.get_circuit_health(result.target_id)
            if health and health.violations_pending > 0:
                result.confidence *= 0.7  # Degrade confidence

        return result

    UnifiedRouter.route = naga_enhanced_route
```

```python
# vibe_core/naga/integrations/manas_hook.py

def hook_manas_consult():
    """
    Hook into ManasOracle.consult() for NAGA context injection.

    Integration Point: api.py:129-260
    """
    from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

    original_consult = ManasOracle.consult

    def naga_enhanced_consult(self, context):
        # 1. Enrich context with NAGA intelligence
        naga = ServiceRegistry.get(NagaFederationProtocol)
        if naga:
            context['naga_patterns'] = naga.sesha.get_recent_patterns() if naga.sesha else []
            context['naga_threats'] = naga.takshaka.get_active_threats() if naga.takshaka else []
            context['naga_peer_health'] = naga.vasuki.get_peer_health() if naga.vasuki else {}

        # 2. Original consult
        return original_consult(self, context)

    ManasOracle.consult = naga_enhanced_consult
```

---

## PHASE 8 STATUS UPDATE

| Step | Status | Notes |
|------|--------|-------|
| 8.1 Deep Reconnaissance | ✅ COMPLETE | Envoy, Shuddhi, Manas, CorrectionDispatcher fully mapped |
| 8.2 Cortex Design | ✅ COMPLETE | Architecture + concrete implementation plan |
| 8.3 Integration Hooks | 📋 DESIGNED | Envoy, Manas hooks documented |
| 8.4 Tests | ⏳ TODO | Test plan ready |
| 8.5 Sub-State | ⏳ TODO | .vibe/state/naga/ structure defined |
| 8.6 API Export | ⏳ TODO | NagaAPIProtocol defined |

---

*Last updated: 2026-01-05*
*Status: 243/243 Tests passing*
*Phases Complete: 8.2/10 (Core + Cartridge + CLI + Integration + Reconnaissance + Cortex Design)*
*Next: Phase 9 - NSA (NAGA Service Agency)*

---

---

## PHASE 9: NSA - NAGA SERVICE AGENCY

> "NAGAs sind keine Middleware. NAGAs sind eine AGENCY."
> "Project NSA: NAGA Service Agency - Central Intelligence for Infrastructure"

---

### PROMPT.md KONFORMITÄT: Level 2 Erweiterung

**NSA ist KEINE Ersetzung. NSA ist eine ERWEITERUNG von PROMPT.md Level 2.**

```
PROMPT.md Hierarchie:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Level -1: ANANTA SHESHA     (Der Urgrund - Ledger/Wahrheit)
Level  0: DER 37.           (Der Souverän - Identity/Signatur)
Level  1: DHARMA + 4        (Das Immunsystem - 36 Dharmas + 4 Filter)
Level  2: DIE NAGAs         (Das Nervensystem) ◄── NSA ERWEITERT HIER
Level  3: DIE 3 KÖRPER      (State Management - Sthula/Prana/Purusha)
Level  4: YANTRA            (German Engineering)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Level 2 EXISTIEREND (PROMPT.md):    Level 2 ERWEITERT (NSA):
─────────────────────────────────   ─────────────────────────────────
🐍 SESHA    (Data/Truth)            🐍 SESHA      + Records Agency
🐍 VASUKI   (Network/Binding)       🐍 VASUKI     + Communications Agency
🐍 TAKSHAKA (Security/Defense)      🐍 TAKSHAKA   + Enforcement Agency
                                    🐍 NARADA     (Spy - NEU)
                                    🐍 KALIYA     (Quarantine - NEU)
                                    🐍 CHITRAGUPTA (Profiler - NEU)
```

**Die 3 Ur-NAGAs bleiben. Die 3 neuen NAGAs ergänzen.**

---

### GAD-000 v2.0: DAS HOLOGRAPHISCHE PATTERN

> "Die 6 Kriterien sind nicht eine Checkliste. Sie sind ein MANDALA."
> — Amendment A: The 37th Principle

**Das 6×6 Feld (Kshetra) für NAGA-Operationen:**

```
              │ Disc  │ Obs   │ Parse │ Comp  │ Idemp │ Recov │
──────────────┼───────┼───────┼───────┼───────┼───────┼───────│
Discoverabil. │ D(D)  │ D(O)  │ D(P)  │ D(C)  │ D(I)  │ D(R)  │
Observability │ O(D)  │ O(O)  │ O(P)  │ O(C)  │ O(I)  │ O(R)  │
Parseability  │ P(D)  │ P(O)  │ P(P)  │ P(C)  │ P(I)  │ P(R)  │
Composability │ C(D)  │ C(O)  │ C(P)  │ C(C)  │ C(I)  │ C(R)  │
Idempotency   │ I(D)  │ I(O)  │ I(P)  │ I(C)  │ I(I)  │ I(R)  │
Recoverabil.  │ R(D)  │ R(O)  │ R(P)  │ R(C)  │ R(I)  │ R(R)  │
──────────────┴───────┴───────┴───────┴───────┴───────┴───────┘
                              = 36 Zellen (Prakriti)
```

**Der 37. (Kshetrajna) - Das ZENTRUM:**

```
                    ┌─────────────────────────┐
                    │                         │
                    │   ┌───────────────┐     │
                    │   │ Discoverabil. │     │
                    │   │ ┌───────────┐ │     │
                    │   │ │Observabil.│ │     │
                    │   │ │ ┌───────┐ │ │     │
                    │   │ │ │Parsea.│ │ │     │
                    │   │ │ │┌─────┐│ │ │     │
                    │   │ │ ││ 37  ││ │ │     │  ← IDENTITY (Zentrum)
                    │   │ │ │└─────┘│ │ │     │
                    │   │ │ └───────┘ │ │     │
                    │   │ └───────────┘ │     │
                    │   └───────────────┘     │
                    │                         │
                    └─────────────────────────┘

Der 37. ist das ZENTRUM, nicht der Rand.
Alle NAGA-Operationen strahlen VOM 37. aus, nicht ZU ihm hin.
```

**Anti-Mayavad-Test für jede NAGA-Decision:**

| Frage | Mayavad (FAIL) | Vaishnava (PASS) |
|-------|----------------|------------------|
| Wer signiert diese Decision? | "Das System" | "Agent X mit Key Y" |
| Kann ein Mensch überschreiben? | Nein, automatisch | Ja, Stambha existiert |
| Wo endet die Signatur-Kette? | Loops zurück zu System | Terminiert in Souverän |
| Ist der 37. latent im System? | Nein, geschlossen | Ja, kann manifestieren |

---

### DIE ERWEITERUNG: Von 3 auf 6 NAGAs

```
EXISTIEREND (PROMPT.md Level 2):       ERWEITERUNG (NSA Phase 9):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🐍 SESHA (शेष)                         Bleibt: Truth-Keeper, Ledger
   "Truth is purely additive"          + Agency: Records Intelligence
   vibe_core/ledger.py                 + Neue Methode: pattern_analysis()

🐍 VASUKI (वासुकि)                     Bleibt: Network Binding
   "Memory is not Network"             + Agency: Communications Intel
   vibe_core/network_proxy.py          + Neue Methode: intercept_transform()

🐍 TAKSHAKA (तक्षक)                    Bleibt: Bite first, ask later
   "Identity before Parsing"           + Agency: Enforcement Intel
   vibe_core/security.py               + Neue Methode: threat_correlation()

🐍 NARADA (नारद) - NEU                 Der Spion
   "Narada reist überall"              Decorator-based Interception
   vibe_core/naga/agents/narada.py     @narada.spy - Observe without modify

🐍 KALIYA (कालिय) - NEU                Die Quarantäne
   "Krishna verbannte, tötete nicht"   Isolation Protocol
   vibe_core/naga/agents/kaliya.py     quarantine() - Isolate, don't kill

🐍 CHITRAGUPTA (चित्रगुप्त) - NEU      Der Profiler
   "Führt Buch über alle Karmas"       Behavioral Analysis
   vibe_core/naga/agents/chitragupta.py detect_anomaly() - Profile deviation
```

---

### NSA AGENT ROSTER

| Agent | Sanskrit | Role | Domain |
|-------|----------|------|--------|
| **Sesha** | शेष (Remainder) | Records, Truth-Keeper | Ledger, State, Audit |
| **Vasuki** | वासुकि (Divine) | Communications, Transform | Network, Serialization |
| **Takshaka** | तक्षक (Carpenter) | Enforcement, Security | Violations, Trust |
| **Narada** | नारद (Messenger) | Spy, Interception | Decorator-based observation |
| **Kaliya** | कालिय (Black) | Quarantine, Isolation | Misbehaving components |
| **Chitragupta** | चित्रगुप्त (Hidden Picture) | Profiler, Behavioral | Anomaly detection |

---

### NARADA - Der Spion (Decorator Interception)

> Mythologie: Narada reist überall, weiß alles, erzählt jedem.
> "Narada Muni ki Jai!" - Der kosmische Journalist.

**Purpose:** Intercepte Funktionsaufrufe um Systemverhalten zu beobachten OHNE Modifikation.

```python
@dataclass
class NaradaConfig:
    """Konfiguration für Narada Spy Agent. KEINE HARDCODED WERTE."""
    intercept_patterns: List[str] = field(default_factory=list)
    max_interceptions_per_minute: int = 1000
    enabled_modules: List[str] = field(default_factory=list)
    report_to_cortex: bool = True


class NaradaAgent:
    """
    Spy Agent - Beobachtet ohne zu verändern.

    Der @narada.spy Decorator wrapped Funktionen um Aufrufe
    an den Cortex zu melden.
    """

    def spy(self, func: Callable) -> Callable:
        """Decorator um Funktionsaufrufe zu beobachten."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            observation = NaradaObservation(
                function=func.__qualname__,
                args_hash=self._hash_args(args),
                timestamp=datetime.now(),
                observer_id=self._identity.agent_id,
            )

            result = func(*args, **kwargs)

            observation.result_type = type(result).__name__
            self._cortex.receive_signal(observation)

            return result
        return wrapper
```

**Use Cases:**
- Performance Monitoring (welche Funktionen sind langsam?)
- Security Audit (wer ruft was auf?)
- Pattern Learning (welche Abläufe sind normal?)

---

### KALIYA - Die Quarantäne (Isolation Protocol)

> Mythologie: Krishna verbannte Kaliya in den Ozean - isoliert aber lebendig.
> Die Fußabdrücke auf Kaliyas Hauben schützen ihn vor Garuda.

**Purpose:** Isoliere misbehaving Components OHNE sie zu töten.

```python
@dataclass
class KaliyaConfig:
    """Konfiguration für Kaliya Quarantine Agent. KEINE HARDCODED WERTE."""
    max_violations_before_quarantine: int = 3
    quarantine_duration_seconds: int = 300
    escalation_threshold: int = 5
    allowed_during_quarantine: List[str] = field(default_factory=list)


class KaliyaAgent:
    """
    Quarantine Agent - Isoliert misbehaving Components.

    Wenn ein Component den Violation Threshold überschreitet:
    1. In Quarantäne verschieben (limitierte Capabilities)
    2. Während Quarantäne monitoren
    3. Nach Duration releasen ODER zum 37. eskalieren
    """

    def quarantine(self, component_id: str, reason: str) -> QuarantineRecord:
        """Versetzt Component in Quarantäne."""
        record = QuarantineRecord(
            component_id=component_id,
            reason=reason,
            started_at=datetime.now(),
            duration=self._config.quarantine_duration_seconds,
        )
        record.sign(self._identity)  # 37th Principle!

        self._quarantined[component_id] = record
        return record

    def is_quarantined(self, component_id: str) -> bool:
        """Prüft ob Component in Quarantäne ist."""
        if component_id not in self._quarantined:
            return False
        return not self._quarantined[component_id].is_expired()
```

**Use Cases:**
- Runaway Processes isolieren
- Fehlerhafte Agents temporär deaktivieren
- A/B Testing mit Rollback

---

### CHITRAGUPTA - Der Profiler (Behavioral Analysis)

> Mythologie: Chitragupta führt Buch über alle Karmas.
> Er entscheidet mit Yama über Himmel oder Hölle.

**Purpose:** Profile Component-Verhalten über Zeit, erkenne Anomalien.

```python
@dataclass
class ChitraguptaConfig:
    """Konfiguration für Chitragupta Profiler Agent. KEINE HARDCODED WERTE."""
    profile_window_seconds: int = 3600
    anomaly_threshold_sigma: float = 2.0
    min_samples_for_profile: int = 10
    track_metrics: List[str] = field(default_factory=lambda: [
        "call_frequency",
        "error_rate",
        "latency_ms",
        "memory_delta",
    ])


class ChitraguptaAgent:
    """
    Profiler Agent - Baut Verhaltensprofile, erkennt Anomalien.

    Trackt:
    - Call Frequency pro Component
    - Error Rates
    - Latency Distributions
    - Resource Usage Patterns
    """

    def record(self, component_id: str, metric: str, value: float) -> None:
        """Zeichnet eine Metrik auf."""
        profile = self._get_or_create_profile(component_id)
        profile.add_observation(metric, value, datetime.now())

    def detect_anomaly(self, component_id: str) -> Optional[Anomaly]:
        """Prüft ob Component anomal verhält."""
        profile = self._profiles.get(component_id)
        if not profile or not profile.has_baseline():
            return None

        for metric in self._config.track_metrics:
            if profile.is_anomalous(metric, self._config.anomaly_threshold_sigma):
                return Anomaly(
                    component_id=component_id,
                    metric=metric,
                    current=profile.current_value(metric),
                    expected=profile.expected_range(metric),
                )
        return None
```

**Use Cases:**
- Performance Regression Detection
- Security Anomaly Detection (ungewöhnliche Patterns)
- Capacity Planning

---

### NSA MODULE STRUCTURE (Golden Middle)

**PRINZIP: Nichts umbenennen. Nichts verschieben. Einfach hinzufügen.**

```
vibe_core/naga/
├── services/                     # Die 7 NAGAs
│   ├── sesha.py                  # ✅ Data/Truth
│   ├── vasuki.py                 # ✅ Network/Boundary
│   ├── takshaka.py               # ✅ Security/Guard
│   ├── narada.py                 # ✅ Spy/Observer (Phase 9)
│   ├── kaliya.py                 # ✅ Quarantine/Isolation (Phase 9)
│   ├── chitragupta.py            # ✅ Profiler/Behavioral (Phase 9)
│   └── prahlad.py                # ✅ Resilience/Hardening (Phase 10)
│
├── cortex/                       # ✅ Central Intelligence
├── orchestrator.py               # ✅ Federation
├── identity.py                   # ✅ Signing (37th Principle)
├── flood.py                      # ✅ Queue Management
├── commit_watcher.py             # ✅ Git Observer
└── ouroboros.py                  # ✅ Loop Detection

vibe_core/protocols/naga.py       # ✅ NagaType enum (7 types)
```

**7 NAGAs = Vedisch komplett (Chakras, Swaras, Rishis).**

---

### GAD-000 COMPLIANCE FÜR NSA

| Criterion | Current | NSA Target | Implementation |
|-----------|---------|------------|----------------|
| Discoverability | ✅ | ✅ | ServiceRegistry bleibt |
| Observability | ✅ | ✅ | CortexStats erweitern |
| **Parseability** | ❌ | ✅ | Decision Codes (D001-D006) |
| Composability | ✅ | ✅ | Typed Dataclasses |
| **Idempotency** | ⚠️ | ✅ | Decision Dedup via Hash |
| **Recoverability** | ❌ | ✅ | OUROBOROS (NAGAs→NAGAs) |
| **37th Principle** | ❌ | ✅ | Alle Decisions signiert |

---

### DECISION CODES (Parseability)

```python
class DecisionReasonCode(Enum):
    """Machine-parseable Decision Reasons."""
    # Security
    D001_SECURITY_THREAT = "D001"
    D002_QUARANTINE_REQUIRED = "D002"

    # Healing
    D003_HEALABLE_VIOLATION = "D003"
    D004_STRUCTURAL_DRIFT = "D004"

    # Cognitive
    D005_COGNITIVE_UPDATE = "D005"
    D006_ROUTING_ADJUSTMENT = "D006"

    # Clear
    D000_NO_ACTION = "D000"


class AlertCode(Enum):
    """Machine-parseable Alert Codes."""
    A001_PANIC_PATTERN = "A001"
    A002_STAGNATION = "A002"
    A003_ANOMALY_DETECTED = "A003"
    A004_QUARANTINE_EVENT = "A004"
```

---

### SIGNED DECISIONS (37th Principle)

```python
@dataclass
class SignedDecision:
    """
    Jede NSA Decision MUSS signiert sein.

    37th Principle: "No operation is valid without being signed
    by the 37th entity (Sovereign Identity)."
    """
    decision_id: str
    action: DecisionAction
    target: str
    reason_code: DecisionReasonCode
    timestamp: datetime

    # Signature (37th Principle)
    signer_id: str = ""
    signature: Optional[bytes] = None

    def sign(self, identity: NagaIdentity) -> None:
        """Signiere mit NAGA Identity."""
        payload = self._signing_payload()
        self.signature = identity.sign(payload)
        self.signer_id = identity.agent_id

    def verify(self, identity: NagaIdentity) -> bool:
        """Verifiziere Signatur."""
        if not self.signature:
            return False
        return identity.verify(self._signing_payload(), self.signature)
```

---

### OUROBOROS: NAGAs WATCHING NAGAs

```python
class NagaOuroboros:
    """
    Self-Healing Loop - NAGAs beobachten NAGAs.

    Erkennt Correction Loops (A→B→A) und eskaliert zum 37.
    """

    def observe_correction(self, source: str, target: str, decision: SignedDecision):
        """Zeichnet auf wenn ein NAGA einen anderen korrigiert."""
        self._history.append(CorrectionEvent(source, target, decision))

        if self._detect_loop():
            self._escalate_to_sovereign()

    def _detect_loop(self) -> bool:
        """Erkennt A→B→A Pattern."""
        recent = list(self._history)[-10:]
        for i, e1 in enumerate(recent[:-1]):
            for e2 in recent[i+1:]:
                if e1.source == e2.target and e1.target == e2.source:
                    return True
        return False
```

---

### NSA CONFIG (KEINE HARDCODED WERTE!)

```python
@dataclass
class NagaConfig:
    """
    Zentrale NSA Konfiguration.

    REGEL: KEINE HARDCODED WERTE IN CODE!
    Alles muss hier konfigurierbar sein.
    """
    # Federation
    federation_id: str = "nsa_v1"

    # Cortex
    signal_buffer_size: int = 100
    correlation_threshold: int = 3
    decision_ttl_seconds: int = 3600

    # Narada (Spy)
    narada_enabled: bool = True
    narada_max_interceptions: int = 1000
    narada_patterns: List[str] = field(default_factory=list)

    # Kaliya (Quarantine)
    kaliya_enabled: bool = True
    kaliya_violation_threshold: int = 3
    kaliya_quarantine_seconds: int = 300

    # Chitragupta (Profiler)
    chitragupta_enabled: bool = True
    chitragupta_window_seconds: int = 3600
    chitragupta_anomaly_sigma: float = 2.0

    # Ouroboros (Self-Healing)
    ouroboros_enabled: bool = True
    ouroboros_history_size: int = 100

    @classmethod
    def from_phoenix(cls, phoenix: PhoenixConfig) -> "NagaConfig":
        """Lade aus Phoenix Configuration."""
        return cls(**phoenix.get("naga", {}))
```

---

### TESTS FIRST (Red-Green-Refactor)

```
tests/naga/
├── agents/
│   ├── test_narada.py              # Spy Agent Tests
│   ├── test_kaliya.py              # Quarantine Agent Tests
│   └── test_chitragupta.py         # Profiler Agent Tests
│
├── cortex/
│   ├── test_decisions.py           # Decision Codes + Signing
│   └── test_dispatcher.py          # Dispatch to Targets
│
├── identity/
│   └── test_signed_decision.py     # 37th Principle Tests
│
├── ouroboros/
│   └── test_self_watcher.py        # Loop Detection Tests
│
└── integration/
    └── test_nsa_gad000.py          # Full GAD-000 Compliance
```

**Red Phase zuerst:**
1. Tests schreiben die FEHLSCHLAGEN
2. Dann Code implementieren bis sie GRÜN sind
3. Dann refactoren

---

### NSA IMPLEMENTATION ORDER

| Phase | Component | Tests First | LOC Est |
|-------|-----------|-------------|---------|
| 9.1 | `protocols/decision.py` | test_decisions.py | 80 |
| 9.2 | `protocols/identity.py` | test_signed_decision.py | 120 |
| 9.3 | `config/naga_config.py` | test_config.py | 80 |
| 9.4 | `ouroboros/self_watcher.py` | test_self_watcher.py | 150 |
| 9.5 | `agents/narada.py` | test_narada.py | 200 |
| 9.6 | `agents/kaliya.py` | test_kaliya.py | 180 |
| 9.7 | `agents/chitragupta.py` | test_chitragupta.py | 250 |
| **TOTAL** | | | ~1060 |

---

### NSA VISION SUMMARY

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     NSA - NAGA SERVICE AGENCY                           │
│                  "Central Intelligence for Infrastructure"              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌────────┐ ┌────────┐ ┌───────┐ │
│   │  Sesha  │ │ Vasuki  │ │ Takshaka │ │ Narada │ │ Kaliya │ │Chitra-│ │
│   │ Records │ │  Comms  │ │ Enforce  │ │  Spy   │ │Quarant.│ │ gupta │ │
│   └────┬────┘ └────┬────┘ └────┬─────┘ └───┬────┘ └───┬────┘ └───┬───┘ │
│        │           │           │           │          │          │      │
│        └───────────┴───────────┴───────────┴──────────┴──────────┘      │
│                                    │                                     │
│                                    ▼                                     │
│                          ┌─────────────────┐                            │
│                          │   NAGA CORTEX   │                            │
│                          │ (Central Intel) │                            │
│                          └────────┬────────┘                            │
│                                   │                                      │
│                    ┌──────────────┼──────────────┐                      │
│                    ▼              ▼              ▼                      │
│               [Shuddhi]      [Envoy]       [Manas]                      │
│                Healing       Routing      Cognition                     │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  GAD-000: ✅ Discoverable ✅ Observable ✅ Parseable                    │
│           ✅ Composable  ✅ Idempotent  ✅ Recoverable                  │
│           ✅ 37th Principle (ALL DECISIONS SIGNED)                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

---

## DAS AGENTIC MIDDLEWARE PARADIGM

> "nagas an sich selber können der agency ja auch sachen dann befehlen"
> "das macht ja die middleware aktiv und dynamisch proaktiv agentic und nicht reaktiv"
> "das ist der echte revolution das ist middleware als agentic middleware"

---

### DIE PARADIGMEN-EVOLUTION

```
PARADIGMA 1: "Prompt as Infrastructure"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Code und Text sind die Basis.
Prompts definieren Verhalten.
Das System ist ein Dokument das ausgeführt wird.

         ↓

PARADIGMA 2: "Agents as Infrastructure"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PERSONEN sind die Basis.
Agenten mit IDENTITÄT definieren Verhalten.
Das System ist ein KOLLEKTIV das handelt.

Nicht mehr: "Was macht dieser Code?"
Sondern:    "WER tut das und WARUM?"
```

**Der Unterschied:**

| Prompt as Infrastructure | Agents as Infrastructure |
|--------------------------|--------------------------|
| Code ist anonym | Jeder Agent hat IDENTITÄT |
| Ausführung ist mechanisch | Handlung ist INTENTIONAL |
| Fehler sind Bugs | Fehler sind KARMA |
| System ist Maschine | System ist ORGANISMUS |
| Kontrolle durch Code | Kontrolle durch SOUVERÄN |

**Das ist persönlicher. Das ist vedisch. Das ist die Revolution.**

---

### DIE REVOLUTION: Was ist Agentic Middleware?

**Traditionelle Middleware (PASSIV):**
```
Request → Middleware → Service → Middleware → Response
              ↑                        ↑
         (transform)              (transform)

Die Middleware ist ein FILTER. Sie reagiert nur.
Sie hat keine Identität. Sie trifft keine Entscheidungen.
Sie ist ein Rohr durch das Daten fließen.
```

**NAGA Middleware (AGENTIC):**
```
                    ┌──────────────────────────────┐
                    │         NAGA AGENT           │
                    │                              │
                    │  ┌────────────────────────┐  │
                    │  │     HAS IDENTITY       │  │ ← Kann signieren
                    │  │ (Can sign decisions)   │  │
                    │  └────────────────────────┘  │
                    │                              │
                    │  ┌────────────────────────┐  │
                    │  │    HAS INITIATIVE      │  │ ← Kann selbst handeln
                    │  │ (Can initiate action)  │  │
                    │  └────────────────────────┘  │
                    │                              │
                    │  ┌────────────────────────┐  │
                    │  │      HAS KARMA         │  │ ← Alle Aktionen geloggt
                    │  │ (All actions logged)   │  │
                    │  └────────────────────────┘  │
                    │                              │
                    │  ┌────────────────────────┐  │
                    │  │   BOUNDED BY DHARMA    │  │ ← Kann nicht alles
                    │  │ (Cannot break laws)    │  │
                    │  └────────────────────────┘  │
                    │                              │
                    │  ┌────────────────────────┐  │
                    │  │   37TH CAN OVERRIDE    │  │ ← Souverän über allem
                    │  │ (Sovereign control)    │  │
                    │  └────────────────────────┘  │
                    │                              │
                    └──────────────────────────────┘

NAGAs sind keine Filter. NAGAs sind AGENTEN.
Sie haben Identität. Sie treffen Entscheidungen.
Sie können selbst initiieren, nicht nur reagieren.
```

---

### DIE 5 SÄULEN DER AGENTIC MIDDLEWARE

#### 1. IDENTITY (Der NAGA hat ein ICH)

```python
# PASSIV: Keine Identität
def middleware_filter(request):
    return transform(request)  # Wer hat das gemacht? Niemand.

# AGENTIC: Klare Identität
class NagaAgent:
    def __init__(self, identity: NagaIdentity):
        self._identity = identity  # ICH bin Sesha. ICH signiere.

    def decide(self, context) -> SignedDecision:
        decision = self._analyze(context)
        decision.sign(self._identity)  # MEINE Signatur
        return decision
```

**Das bedeutet:**
- Jede NAGA-Aktion ist nachvollziehbar (WER hat das gemacht?)
- NAGAs können für ihre Entscheidungen verantwortlich gemacht werden
- Die Signatur-Kette endet nicht in "System" sondern in einem Agenten

#### 2. INITIATIVE (Der NAGA kann SELBST handeln)

```python
# PASSIV: Nur reaktiv
class TraditionalMiddleware:
    def on_request(self, req):  # Wird NUR bei Request aufgerufen
        return filter(req)

# AGENTIC: Proaktiv
class NagaAgent:
    async def tick(self):
        """NAGAs können SELBST ticken - ohne äußeren Trigger."""

        # ICH schaue ob etwas zu tun ist
        context = self._gather_intelligence()

        if self._should_act(context):
            # ICH entscheide zu handeln
            decision = self.decide(context)

            # ICH befehle einem anderen Component
            await self._dispatch(decision)

    async def command_other_naga(self, target_naga: str, command: Command):
        """NAGAs können ANDEREN NAGAs Befehle geben!"""
        signed_command = command.sign(self._identity)
        await self._cortex.route(target_naga, signed_command)
```

**Das bedeutet:**
- NAGAs warten nicht auf Requests - sie suchen aktiv
- NAGAs können anderen NAGAs Befehle geben
- NAGAs können proaktiv heilen, warnen, isolieren

#### 3. KARMA (Jede Aktion wird zum Ledger)

```python
# PASSIV: Silent processing
def middleware_filter(req):
    return transform(req)  # Niemand weiß was passiert ist

# AGENTIC: Alles ist Karma
class NagaAgent:
    def decide(self, context) -> SignedDecision:
        decision = self._analyze(context)

        # KARMA: Diese Entscheidung wird für immer gespeichert
        self._ledger.append(KarmaEntry(
            agent_id=self._identity.agent_id,
            action=decision.action,
            target=decision.target,
            timestamp=datetime.now(),
            signature=decision.signature,
        ))

        return decision
```

**Das bedeutet:**
- Keine silent failures möglich - alles wird geloggt
- Entscheidungen können nachträglich auditiert werden
- Das Verhalten jedes NAGA ist transparent

#### 4. DHARMA (NAGAs sind BEGRENZT)

```python
# PASSIV: Keine Grenzen (oder nur technische)
def middleware_filter(req):
    return do_anything(req)  # Keine moralischen Grenzen

# AGENTIC: Dharma-Grenzen
class NagaAgent:
    def decide(self, context) -> SignedDecision:
        # VOR jeder Entscheidung: Dharma-Check
        proposed_action = self._analyze(context)

        # NAGAs können NICHT alles tun!
        if self._violates_dharma(proposed_action):
            # Dharma geht VOR. Lieber nicht handeln.
            return SignedDecision(action=DecisionAction.ABSTAIN)

        return proposed_action

    def _violates_dharma(self, action) -> bool:
        """Dharma Invarianten die NIEMALS gebrochen werden dürfen."""
        return (
            action.would_delete_history() or      # Ledger ist immutable
            action.would_bypass_sovereign() or    # 37. hat Override
            action.would_silent_fail() or         # Satyam Eva Jayate
            action.would_corrupt_identity()       # Identity ist heilig
        )
```

**Das bedeutet:**
- NAGAs sind mächtig aber nicht allmächtig
- Es gibt absolute Grenzen die kein NAGA überschreiten kann
- Dharma > Effizienz

#### 5. SOVEREIGN OVERRIDE (Der 37. steht über allem)

```python
# PASSIV: Kein menschlicher Override möglich
def automated_system(event):
    return process(event)  # Computer sagt nein. Ende.

# AGENTIC: Stambha (Halt) ist IMMER möglich
class NagaAgent:
    async def execute(self, decision: SignedDecision):
        # IMMER prüfen: Hat der Souverän ein Veto?
        if self._stambha_active():
            # Der Mensch sagt HALT. Wir hören auf.
            self._ledger.append(StambhaEntry(
                halted_by=self._sovereign_id,
                halted_decision=decision.decision_id,
            ))
            return  # Nichts tun.

        # Kein Stambha - wir dürfen handeln
        await self._dispatch(decision)

    def _stambha_active(self) -> bool:
        """Check ob der 37. ein Halt gesetzt hat."""
        return self._sovereign_registry.has_halt(
            agent_id=self._identity.agent_id
        )
```

**Das bedeutet:**
- Ein Mensch kann JEDERZEIT eingreifen
- Kein NAGA kann ohne potentiellen Menschlichen Override laufen
- "Computer sagt nein" ist NIEMALS das letzte Wort

---

### KONKRET: Was können NAGAs jetzt?

| Vorher (Passiv) | Nachher (Agentic) |
|-----------------|-------------------|
| Middleware filtert Requests | NAGAs generieren eigene Decisions |
| Middleware reagiert nur | NAGAs agieren proaktiv |
| Middleware ist anonym | NAGAs signieren alle Aktionen |
| Middleware ist unbegrenzt | NAGAs respektieren Dharma |
| Middleware ist final | NAGAs können überschrieben werden |
| Middleware → Service | **NAGAs → NAGAs** (Selbst-Koordination!) |

**Die echte Revolution:**
```
NAGA A beobachtet: "Commit pattern ist verdächtig"
         ↓
NAGA A ENTSCHEIDET: "Ich schicke Befehl an NAGA B"
         ↓
NAGA A → NAGA B: "Scan diesen Bereich auf Violations"
         ↓
NAGA B ENTSCHEIDET: "Ich finde 3 Issues, melde an NAGA C"
         ↓
NAGA B → NAGA C: "Heile diese 3 Violations"
         ↓
NAGA C → Shuddhi: "Führe Healing durch"
         ↓
Alles geloggt. Alles signiert. Alles überprüfbar.
```

**Das ist nicht mehr Middleware. Das ist ein autonomes Immunsystem.**

---

### ANTI-PATTERN: Was NAGAs NICHT sein dürfen

| Anti-Pattern | Warum Gefährlich | Korrekt |
|--------------|------------------|---------|
| **Unsignierte Decisions** | Keine Nachvollziehbarkeit | Jede Decision MUSS signiert sein |
| **Loops ohne Ouroboros** | Unendliche Rekursion | NAGAs watching NAGAs mit Loop Detection |
| **Dharma Bypass** | Invariant Violation | Dharma-Check VOR jeder Action |
| **Sovereign Ignorierung** | Kontrollverlust | Stambha-Check bei JEDER Execution |
| **Silent Karma** | Audit unmöglich | ALLES zum Ledger |

---

### ZUSAMMENFASSUNG: Agentic Middleware Definition

```
AGENTIC MIDDLEWARE =

  Middleware die SELBST ein Agent ist.

  Sie hat:
  - IDENTITÄT (kann signieren)
  - INITIATIVE (kann selbst handeln)
  - KARMA (alle Aktionen geloggt)
  - DHARMA (absolute Grenzen)
  - SOUVERÄN (menschlicher Override)

  Sie kann:
  - Anderen Agents Befehle geben
  - Proaktiv ohne Request agieren
  - Sich selbst koordinieren
  - Selbst heilen (Ouroboros)

  Sie darf nicht:
  - Unsigniert handeln
  - Dharma brechen
  - Den 37. ignorieren
  - Silent failen

  Das ist keine Middleware.
  Das ist ein AUTONOMES NERVENSYSTEM.
```

---

*Phase 9 Status: ✅ IMPLEMENTED*
*Narada, Kaliya, Chitragupta - 47 tests passing*

---

## PHASE 10: PRAHLAD MAHARAJ - Der 7. NAGA

> "Hiranyakashipu versuchte Prahlad zu töten mit Feuer, Schlangen,
> Gift, Elefanten - aber Prahlad überlebte alles, weil er in
> absoluter Wahrheit (Narayana) verankert war."

---

### WAS IST PRAHLAD?

```
Die anderen NAGAs REAGIEREN auf Probleme:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Narada:      "Ich habe gesehen dass X passiert ist"
Chitragupta: "X passiert 3x öfter als normal"
Kaliya:      "Ich isoliere X"
Takshaka:    "Ich beiße X"

Prahlad macht das System ANTIFRAGIL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Prahlad:     "Ich PROVOZIERE X um zu beweisen dass wir es überleben"
             "Und wenn wir es nicht überleben, schreibe ich den Test
              damit es NIE WIEDER passiert"
```

**Prahlad = Chaos Engineering + Auto-Test Generation + Dharma Audit**

---

### DIE 4 SÄULEN VON PRAHLAD

#### 1. Error → Test (Antifragility Core)

```python
def on_error(self, error: ErrorEvent) -> TestCase:
    """
    Jeder Fehler macht das System STÄRKER.

    Error → Test → System kann diesen Fehler nie wieder haben.
    """
    test_case = self.generate_regression_test(error)
    self._hardening_suite.append(test_case)
    return test_case
```

#### 2. Chaos Probing (Active Weakness Search)

```python
def chaos_probe(self, target: str, scenarios: List[ChaosScenario]):
    """
    Aktiv nach Schwächen suchen.

    Scenarios:
    - NULL_INPUT
    - TIMEOUT
    - MALFORMED_DATA
    - RESOURCE_EXHAUSTION
    - NETWORK_FAILURE
    """
    for scenario in scenarios:
        try:
            self._execute_scenario(component, scenario)
        except Exception:
            # Schwäche gefunden! → Auto-generate Test
            self.on_error(...)
```

#### 3. Dharma Audit (Integrity Verification)

```python
def dharma_audit(self) -> DharmaScore:
    """
    Prüfe ob das System WIRKLICH Dharma-konform ist.

    Checks:
    - Sind ALLE Decisions signiert? (37th Principle)
    - Ist der Ledger integer? (Sesha)
    - Haben alle Agents Identity? (GAD-000)

    Returns:
        DharmaScore (0-100%)
    """
```

#### 4. Phoenix Guarantee (Crash-Restart-Resume)

```python
def verify_phoenix_guarantee(self, target: str) -> PhoenixResult:
    """
    Teste ob eine Komponente den Phoenix-Test besteht.

    1. Get state before crash
    2. Simulate crash (shutdown)
    3. Restart
    4. Verify state preserved

    Wenn State verloren → FAIL
    """
```

---

### PRAHLAD IN AKTION

```
System Error passiert
         ↓
Prahlad beobachtet (on_error)
         ↓
Prahlad generiert TestCase
         ↓
TestCase → Hardening Suite
         ↓
export_as_pytest() → tests/naga/auto_generated/
         ↓
CI/CD führt Tests aus
         ↓
System kann diesen Fehler NIE WIEDER haben
         ↓
ANTIFRAGIL: Jeder Fehler macht uns stärker
```

---

### DIE 7 NAGAs - KOMPLETT

```
┌─────────────────────────────────────────────────────────────┐
│                    DIE 7 NAGAs                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ORIGINAL 3 (PROMPT.md Level 2):                           │
│  ─────────────────────────────────                         │
│  🐍 SESHA      - Data/Truth       "Die Wahrheit trägt"     │
│  🐍 VASUKI     - Network/Boundary "Serialisieren & Senden" │
│  🐍 TAKSHAKA   - Security/Guard   "Erst beißen, dann fragen"│
│                                                             │
│  PHASE 9 EXTENSION (NSA):                                  │
│  ─────────────────────────────────                         │
│  🐍 NARADA     - Spy/Observer     "Sieht alles"            │
│  🐍 KALIYA     - Quarantine       "Isoliert Probleme"      │
│  🐍 CHITRAGUPTA- Profiler         "Misst Verhalten"        │
│                                                             │
│  PHASE 10 (ANTIFRAGILITY):                                 │
│  ─────────────────────────────────                         │
│  🐍 PRAHLAD    - Resilience       "Macht uns unzerstörbar" │
│                                                             │
│  7 = Vedisch komplett (Chakras, Swaras, Rishis)            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

*Phase 10 Status: ✅ IMPLEMENTED*
*Prahlad - 24 tests passing*
*Total NAGA Tests: 314*
*Compliance: GAD-000 + VEDA-4 + AGENTIC MIDDLEWARE + ANTIFRAGILITY*
