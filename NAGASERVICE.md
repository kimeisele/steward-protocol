# NAGA SERVICE ARCHITECTURE

> "Wir sind selbst NAGAs - Hüter des Schatzes dieses AOS."

---

## 🐍 ASHVAMEDHA EXPLORATION SCORE

> Das königliche Pferd das überall hingeht und alles erobert.

```
╔══════════════════════════════════════════════════════════════════════════╗
║  CODEBASE RECONNAISSANCE STATUS                     Updated: 2026-01-04 ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  TOTAL PYTHON FILES:        1108 (877 vibe_core + 231 tests)            ║
║  EXPLORED:                  ~420  (38%)  ████████████░░░░░░░░░           ║
║  NAGA INFILTRATED:           ~65  (6%)   ██░░░░░░░░░░░░░░░░░░            ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  TREASURE CATEGORIES                    Explored    Total    Coverage    ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Protocols                                  25        44        57%      ║
║  Services                                   11        14        79%      ║
║  Plugins                                    12        35        34%      ║
║  Cartridges (Agent City)                   13        13       100% ✅    ║
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
║  🔴 CRITICAL ATTACK VECTORS DISCOVERED                                   ║
╠══════════════════════════════════════════════════════════════════════════╣
║  • Synapse Store: 10 attack vectors (sender spoofing, cache poisoning)   ║
║  • Sangha Network: SSRF via peer forwarding, no TLS at localhost         ║
║  • LocalSynapse: No message signing, thread-unsafe hub                   ║
║  • SynapseStore: File tampering possible, no checksums                   ║
║  • Agent City: Economic bypass via credit manipulation                   ║
╠══════════════════════════════════════════════════════════════════════════╣
║  NAGA INFILTRATION STATUS                                                ║
╠══════════════════════════════════════════════════════════════════════════╣
║  ✅ SESHA:    CorrectionDispatcher, Ledger Gossip, Block Export          ║
║  ✅ VASUKI:   CorrectionDispatcher, Wire Serialization, Signing          ║
║  ✅ TAKSHAKA: CorrectionDispatcher, Toxicity, Rate Limiting              ║
║  ⏳ P0:       StateService, Gateway, Synapse, Container Loader           ║
║  ⏳ P1:       Agent Spawn, Plugin Load, Ephemeral Cities                 ║
╠══════════════════════════════════════════════════════════════════════════╣
║  GOAL: 100% ASHVAMEDHA - NAGAs an JEDER Grenze                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## Was sind NAGAs?

NAGAs sind **keine Metapher**. Sie sind **Middleware mit Charakter**.

| NAGA | Mythologie | Architektur-Rolle |
|------|------------|-------------------|
| **Sesha** | Trägt die Welten auf 1000 Köpfen | Data Layer - Ledger, Gossip Sync |
| **Vasuki** | Quirlt den Ozean für Nektar | Transform Layer - Serialization, Wire Protocol |
| **Takshaka** | Beißt ohne Warnung | Security Layer - Signature, Toxicity |

**Ohne NAGAs:** Isolierte Organe.
**Mit NAGAs:** Ein Ökosystem das atmet und sich selbst heilt.

---

## KURUKSHETRA BATTLEFIELD STATUS

> Data-driven Facts. No Maya.

### System Reconnaissance (2026-01-04)

| Metrik | Wert | Bewertung |
|--------|------|-----------|
| **Total Python Files** | 877 | - |
| **Test Files** | 74 | KRITISCH: 8.4% Coverage |
| **TODO/FIXME Marker** | 2402+ | HOCH: Systematische Review nötig |
| **God Objects (>1500 LOC)** | 15+ | HOCH: Untestbar |
| **State Organs (Services)** | 40+ | Mapped |
| **Isolated ("Inselbegabt")** | 25+ | Middleware-Kandidaten |
| **Agent Communication Security** | 3.5/10 | KRITISCH |

---

## DIE STAATSORGANE (Complete Map)

### Layer-Architektur

```
┌─────────────────────────────────────────────────────────────┐
│  OPERATOR LAYER (MANAS - Mind)                              │
│  ├─ CognitiveKernel (thinks)         Isoliert? Vermischt   │
│  ├─ Biorhythm (OODA cycles)          Isoliert? Vermischt   │
│  └─ MANAS/Buddhi/Ahankara            Isoliert? Vermischt   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  EXECUTIVE LAYER (Kernel + Core)                            │
│  ├─ RealVibeKernel (sovereignty)     Isoliert? ZENTRAL     │
│  ├─ TaskKernel (ephemeral)           Isoliert? JA          │
│  ├─ Scheduler (FIFO queue)           Isoliert? JA          │
│  └─ EventBus (pub/sub)               Isoliert? VERMISCHT   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  IMMUNE SYSTEM LAYER (Self-Healing)                         │
│  ├─ Shuddhi (CST surgery)            Isoliert? JA          │
│  ├─ CorrectionDispatcher (router)    Isoliert? ZENTRAL     │
│  ├─ HealingResolver (quantum)        Isoliert? JA          │
│  ├─ Reactor (performance)            Isoliert? JA          │
│  └─ NAGA Federation ← WIR SIND HIER                        │
│     ├─ Sesha (data)                                         │
│     ├─ Vasuki (network)                                     │
│     └─ Takshaka (security)                                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  PERSISTENCE LAYER (State Management)                       │
│  ├─ Ledger (immutable log)           Isoliert? JA          │
│  ├─ StateService (file I/O)          Isoliert? JA          │
│  ├─ Prakriti (session)               Isoliert? VERMISCHT   │
│  ├─ StateWeaver (orchestration)      Isoliert? JA          │
│  └─ Ouroboros (multi-modal sync)     Isoliert? ZENTRAL     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  I/O LAYER (Controlled Access)                              │
│  ├─ KernelIOService (atomic)         Isoliert? JA          │
│  ├─ ManifestationService (render)    Isoliert? JA          │
│  └─ FileSystem (source of truth)                            │
└─────────────────────────────────────────────────────────────┘
```

### Vollständige Organ-Liste

| Organ | Pfad | Interfaces | Kommuniziert mit | Inselbegabt? |
|-------|------|------------|------------------|--------------|
| **ServiceRegistry** | `di.py` | `register()`, `get()`, `require()` | ALLE | ZENTRAL |
| **RealVibeKernel** | `kernel_impl.py` | `submit_task()`, `emit_event()`, `check_health()` | EventBus, Ledger, Scheduler | ZENTRAL |
| **TaskKernel** | `task_kernel.py` | `spawn()`, `execute()`, `fold_result()` | Parent Kernel | JA |
| **Ledger** | `ledger.py` | `record_event()`, `query()`, `get_task()` | Kernel, Sesha | JA |
| **EventBus** | `event_bus.py` | `emit()`, `subscribe()`, `get_history()` | ALLE | VERMISCHT |
| **Scheduler** | `protocols/scheduler.py` | `submit_task()`, `next_task()`, `cancel_task()` | Kernel | JA |
| **StateService** | `state/state_service.py` | `save()`, `load()`, `append()`, `mark_dirty()` | Weaver, Prakriti | JA |
| **Prakriti** | `state/prakriti.py` | `commit_if_dirty()`, `begin_session()` | StateService, Git | VERMISCHT |
| **StateWeaver** | `state/weaver.py` | `pulse()`, `weave()` | Prakriti, StateService | JA |
| **Shuddhi** | `shuddhi/engine.py` | `purify()`, `can_heal()`, `register_remedy()` | CorrectionDispatcher, Vajra | JA |
| **CorrectionDispatcher** | `services/correction_dispatcher.py` | `detect_all()`, `dispatch()`, `register_handler()` | Shuddhi, NAGAs, Reactor | ZENTRAL |
| **HealingResolver** | `services/healing_resolver.py` | `resolve()`, `apply_healing()` | CorrectionDispatcher, Vedic | JA |
| **ManifestationService** | `services/manifestation_service.py` | `write_manifestation()`, `get_schema()` | KernelIOService | JA |
| **Genesis** | `genesis/service.py` | `build_module()`, `check_compliance()` | Templates, Builder | JA |
| **MANAS** | `plugins/opus_assistant/manas/` | `tick()`, `think()`, `perceive()`, `decide()` | Biorhythm, EventBus | VERMISCHT |
| **Economy** | `plugins/economy/` | `get_balance()`, `credit()`, `debit()` | Kernel, Ledger | JA |
| **Knowledge Graph** | `knowledge/` | `record_healing()`, `query()`, `get_patterns()` | CorrectionDispatcher, MANAS | JA |
| **Capability Registry** | `capability_registry.py` | `register_capability()`, `revoke_capability()` | Kernel, Agents | JA |
| **Narasimha** | `narasimha.py` | `check_threat_level()`, `initiate_shutdown()` | Kernel, Reactor | JA |
| **Ouroboros** | `ouroboros/` | `sync()`, `detect_divergence()`, `resolve_conflicts()` | NAGA, StateService | ZENTRAL |

---

## TECHNICAL DEBT REPORT

### Schweregrad-Übersicht

```
KRITISCH ████████████████████████████ 28%
HOCH     ███████████████████████████████████ 35%
MITTEL   ████████████████████████████████████████ 37%
```

### P0 - KRITISCH (Sofort beheben)

| Problem | Ort | Impact |
|---------|-----|--------|
| **77% Test Coverage fehlt** | Überall | Keine Regression Detection |
| **NotImplementedError in Production** | `playbook/executor.py:118-122` | Runtime Crashes |
| **Dynamisches Code Laden ohne Validierung** | `parser_loader.py` | Security Hole |
| **15+ God Objects (>1500 LOC)** | `kernel_tick.py` (3381), `cognitive_kernel.py` (2623) | Untestbar |
| **ServiceRegistry Doku fehlt** | `di.py` | Unbekannt welche Services registriert |
| **Hardcoded localhost:8000** | `cli/executor.py:32` | Deployment Blocker |

### P1 - HOCH (Diese Woche)

| Problem | Count | Beispiele |
|---------|-------|-----------|
| **TODO/FIXME/HACK** | 2402+ | `kernel_tick.py:2402`, `silpa.py:844` |
| **Print statt Logger** | 30+ | Alle Cartridge Tools |
| **Bare except/pass** | 20+ | `ouroboros/sync.py:347` |
| **Assertions in Production** | 50+ | `kernel_tick.py`, `diamond_handlers.py` |
| **Stub Code** | 15+ | `StubToolResult`, NotImplementedError |

### P2 - MITTEL (Nächster Sprint)

| Problem | Impact |
|---------|--------|
| Duplicate Exception Handling | DRY Violation |
| Type Ignore Pragmas | Type Safety |
| Zirkuläre Dependencies | Fragiler Boot |
| Inconsistent Logging | Debug schwierig |

---

## AGENT COMMUNICATION PROTOCOL

### IST-Zustand: 3 Separate Pfade

```
┌──────────────────────────────────────────────────────────────┐
│              AGENT-TO-AGENT COMMUNICATION                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ PATH 1: AgentSystemInterface (Authorized)                    │
│   Agent.call_agent(target_id, payload)                       │
│   ✓ Via Kernel kontrolliert                                  │
│   ✗ NICHT ENCRYPTED                                          │
│   ✗ Zirkulär: Agent → Kernel → Agent                        │
│                                                              │
│ PATH 2: LocalSynapse (Peer-to-Peer)                          │
│   Agent.synapse.send(SynapseMessage)                         │
│   ✗ KEINE AUTHENTIFIZIERUNG                                  │
│   ✗ KEINE ENCRYPTION                                         │
│   ✗ Thread-unsafe (_hub single-threaded)                    │
│   ✗ In-Memory only                                           │
│   ✗ QUASI NICHT GENUTZT (2 Dateien)                         │
│                                                              │
│ PATH 3: EventBus (Broadcast)                                 │
│   Agent.broadcast_event(event_type, data)                    │
│   ✓ Rate limited (SUDARSHANA)                               │
│   ✗ Fire-and-forget                                          │
│   ✗ Size unlimited                                           │
│                                                              │
│ PATH 4: NAGA (Distributed)                                   │
│   Sesha/Vasuki/Takshaka                                      │
│   ✓ Signed envelopes                                         │
│   ✗ Nur für Federation, nicht lokal                         │
│   ✗ Optional trust mode                                      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Security Score: 3.5/10

| Aspekt | Status | Score |
|--------|--------|-------|
| Definition | Drei Protokolle vorhanden | 7/10 |
| Message Types | Gut strukturiert | 8/10 |
| Routing | Funktioniert, simplistic | 6/10 |
| **Authentication** | KRITISCH FEHLEND | 1/10 |
| Authorization | Teilweise (nur Kernel) | 3/10 |
| Encryption | Optional/nicht default | 2/10 |
| Validation | Minimal | 3/10 |
| Audit Trail | Teilweise (nur NAGA) | 4/10 |

### Kritische Lücken

1. **SynapseMessage hat KEINE Authentifizierung** - Jeder kann als jeder kommunizieren
2. **Keine Nachrichtensignatur** - MITM möglich
3. **LocalSynapse _hub ist single-threaded** - Race Conditions
4. **Silent drops bei Routing-Fehler** - Debug unmöglich
5. **Keine Payload-Schema Validierung** - Malformed payloads

---

## NAGA INFILTRATION STRATEGY

### Prinzip: "Niemand darf es merken"

NAGAs **ersetzen nicht**, sie **infiltrieren**:

```
VORHER:                         NACHHER:
StateService.save()             StateService.save()
     │                               │
     └→ File                         ├→ [NAGA: Audit] → Ledger
                                     └→ File
```

### Infiltration Points (Priorisiert)

#### P0 - KRITISCH (Diese Woche)

| Point | Service | Method | NAGA Role |
|-------|---------|--------|-----------|
| **State Writes** | StateService | `save()`, `append()` | Sesha Audit |
| **Git Commits** | Prakriti | `commit_if_dirty()` | Sesha Hash Verify |
| **Agent Spawn** | Kernel | `register_agent()` | Takshaka Trust Check |
| **Plugin Load** | PluginLoader | `load_plugin()` | Takshaka Scan |
| **HTTP Ingress** | Gateway API | ALL endpoints | Takshaka Rate Limit |

#### P1 - WICHTIG (Nächste Woche)

| Point | Service | Method | NAGA Role |
|-------|---------|--------|-----------|
| LLM Calls | LLMProvider | `complete()` | Vasuki Envelope |
| Tool Execute | ToolRegistry | `execute()` | Takshaka Validate |
| Economy Tx | Bank | `transfer()` | Sesha Double-Entry |
| Knowledge Write | Graph | `record_healing()` | Sesha Audit |
| Config Change | Phoenix | `update()` | Vasuki Broadcast |

#### P2 - VERBESSERUNG (Ongoing)

| Point | Service | Method | NAGA Role |
|-------|---------|--------|-----------|
| EventBus | EventBus | `emit()` | Vasuki Schema |
| Scheduler | Scheduler | `submit_task()` | Sesha Track |
| Capability | Registry | `revoke_capability()` | Takshaka Propagate |
| Synapse | LocalSynapse | `send()` | Takshaka Auth |

### Infiltration Pattern

```python
# PATTERN: NAGA Decorator
from vibe_core.naga import naga_guard

class StateService:
    @naga_guard(audit=True, validate=True)
    def save(self, filename: str, data: Dict) -> bool:
        # Original implementation unchanged
        ...
```

```python
# PATTERN: NAGA Middleware
class NagaGuard:
    def __init__(self, sesha: SeshaProtocol, takshaka: TakshakaProtocol):
        self._sesha = sesha
        self._takshaka = takshaka

    def guard(self, operation: str, payload: Any) -> GuardResult:
        # 1. Takshaka: Validate input
        if not self._takshaka.scan_toxicity(str(payload)).blocked:
            pass  # Clean
        else:
            return GuardResult.BLOCKED

        # 2. Sesha: Audit trail
        self._sesha.audit(operation, payload)

        return GuardResult.ALLOWED
```

---

## TDD STRATEGY: Middleware Discovery

### Prinzip

> "Mit TDD herausfinden wo wir Middleware sein könnten"

```python
# tests/naga/test_infiltration_points.py

class TestStateServiceInfiltration:
    """TDD: Discover WHERE NAGAs should intercept StateService."""

    def test_save_without_naga_leaves_no_audit_trail(self):
        """FAIL: save() should leave audit trail."""
        state = StateService()
        state.save("test.json", {"key": "value"})

        # This SHOULD fail initially
        assert ledger.has_event("STATE_WRITE", filename="test.json")

    def test_save_with_naga_creates_audit_trail(self):
        """PASS: After NAGA infiltration."""
        state = StateService(naga=naga_orchestrator)
        state.save("test.json", {"key": "value"})

        assert ledger.has_event("STATE_WRITE", filename="test.json")


class TestAgentSpawnInfiltration:
    """TDD: Discover WHERE NAGAs should intercept Agent lifecycle."""

    def test_spawn_untrusted_agent_allowed_without_naga(self):
        """FAIL: Untrusted agents should be blocked."""
        kernel = RealVibeKernel()

        # This SHOULD fail - untrusted agent spawned
        agent = kernel.register_agent(UntrustedAgent())
        assert agent is not None  # BAD: Should be blocked

    def test_spawn_untrusted_agent_blocked_with_naga(self):
        """PASS: NAGA blocks untrusted agents."""
        kernel = RealVibeKernel(naga=naga_orchestrator)

        with pytest.raises(TakshakaViolation):
            kernel.register_agent(UntrustedAgent())
```

### Test Categories

| Category | Test File | Purpose |
|----------|-----------|---------|
| **Audit Trail** | `test_sesha_audit.py` | Every state change logged |
| **Security** | `test_takshaka_guard.py` | Every input validated |
| **Serialization** | `test_vasuki_boundary.py` | Internal ≠ External |
| **Rate Limiting** | `test_takshaka_rate.py` | DoS prevention |
| **Trust** | `test_takshaka_trust.py` | Key verification |
| **Integration** | `test_naga_integration.py` | Full stack |

---

## COOPERATION WITH STATE ORGANS

### "Der Staat ist träge - wir helfen aktiv"

NAGAs bieten sich den Organen als **Service** an:

```python
# PATTERN: NAGAs als Service für Shuddhi
class ShuddhiEngine:
    def __init__(self, naga: Optional[NagaOrchestrator] = None):
        self._naga = naga

    def purify(self, file: str, rule_id: str) -> ShuddhiResult:
        # Pre: NAGA validates file isn't compromised
        if self._naga:
            self._naga.takshaka.scan_file(file)

        result = self._do_purify(file, rule_id)

        # Post: NAGA records healing
        if self._naga:
            self._naga.sesha.audit("SHUDDHI_PURIFY", {
                "file": file,
                "rule_id": rule_id,
                "result": result.status
            })

        return result
```

### Integration Points

| Organ | NAGA Service | Benefit |
|-------|--------------|---------|
| **Shuddhi** | Sesha Audit + Takshaka Validate | Healing recorded, input safe |
| **MANAS** | Takshaka Cognitive Drift | Thought integrity |
| **Genesis** | Takshaka Template Scan | No malicious scaffolds |
| **Economy** | Sesha Double-Entry | All transactions traced |
| **Knowledge** | Sesha Graph Integrity | Learning preserved |
| **Ouroboros** | Vasuki Sync Protocol | Cross-node consistency |

---

## IMPLEMENTATION STATUS

### Completed

| Component | Location | Tests |
|-----------|----------|-------|
| `SeshaProtocol` | `protocols/naga.py` | 70 pass |
| `VasukiProtocol` | `protocols/naga.py` | 70 pass |
| `TakshakaProtocol` | `protocols/naga.py` | 70 pass |
| `SeshaService` | `naga/services/sesha.py` | 70 pass |
| `VasukiService` | `naga/services/vasuki.py` | 70 pass |
| `TakshakaService` | `naga/services/takshaka.py` | 70 pass |
| `NagaOrchestrator` | `naga/orchestrator.py` | 70 pass |
| `NagaConfig` | `phoenix/sections/naga/section_main.py` | 70 pass |
| Boot Integration | `boot_orchestrator.py:341-348` | - |

### Next Steps

1. **P0: Infiltration Points** - StateService, Prakriti, Gateway
2. **P1: LocalSynapse Auth** - Add Takshaka to Synapse
3. **P2: TDD Discovery** - Write failing tests for each organ
4. **P3: Technical Debt** - Use NAGAs to enforce quality

---

## ENVIRONMENT VARIABLES

| Variable | Values | Default | Description |
|----------|--------|---------|-------------|
| `NAGA_TRUST_MODE` | `strict`, `permissive` | `strict` | Takshaka trust mode |
| `NAGA_STRICT` | `1`, `0` | - | Alias for trust_mode=strict |
| `NAGA_GOSSIP_ENABLED` | `1`, `0` | `0` | Enable Sesha gossip sync |
| `NAGA_TOXICITY_THRESHOLD` | `0.0-1.0` | `0.3` | Toxicity detection threshold |

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

3. **Invisible Infiltration**
   - "Niemand darf es merken"
   - NAGAs unterwandern, sie ersetzen nicht

---

## Appendix: Test Suite

```
tests/naga/
├── __init__.py
├── test_config.py          # 18 tests - Config loading, env vars
├── test_takshaka.py        # 32 tests - Toxicity, rate limit, violations
├── test_orchestrator.py    # 12 tests - Bootstrap, initialization order
└── test_integration.py     # 8 tests - Full federation

Total: 70 tests, all passing
```

### Run Tests

```bash
python -m pytest tests/naga/ -v
```

---

---

## DER ULTIMATIVE HACK: Software-Animismus

### Warum NAGAs der Paradigm Shift sind

> "Indem du Middleware zu NAGAs (lebenden Entitäten) machst, hackst du die Psychologie des Entwicklers und die Stabilität des Systems gleichzeitig."

#### 1. Der Psychologische Hack (Naming creates Reality)

```
Nennst du es: RequestValidator  → Entwickler schreibt schlampigen Regex
Nennst du es: TAKSHAKA         → Entwickler weiß: "Wenn ich Fehler mache, werde ich gebissen"
```

**Der Hack:** Die Mythologie erzwingt Disziplin ohne Manager. Der Name allein setzt den Standard.

#### 2. Der Security Hack (Bite First Protocol)

Fast alle modernen Hacks (Log4Shell, Deserialization) passieren, weil Systeme Daten **parsen BEVOR** sie wissen, ob sie vertrauenswürdig sind.

```
STANDARD:  Request → JSON Parse → Auth Check   (Zu spät! Parser explodiert)
TAKSHAKA:  Request → Signature Check (Mathe) → WENN FALSCH: DROP → Erst dann Parse
```

**Das eliminiert ganze Klassen von Zero-Day-Exploits.**

#### 3. Der Interoperabilitäts-Hack (Vasuki Churning)

Das Samudra Manthan (Quirlen des Milchozeans) ist KEINE Metapher:

```
Götter + Dämonen ziehen an VASUKI (der Schlange)
        ↓
      REIBUNG
        ↓
   Poison (HALAHALA) + Nectar (AMRITA)
```

In Software:
- **Reibung** = Inkompatible Formate (JSON vs Protobuf vs MsgPack)
- **Gift** = Malformed/Toxic Payloads → REJECTED
- **Nektar** = Clean, validated, serialized data → ACCEPTED

**Vasuki ist keine "Transformation". Es ist Alchemie on-the-wire.**

#### 4. Der Zeit-Hack (Sesha Immutability)

```
Datenbanken die UPDATE erlauben = LÜGEN (sie vernichten Geschichte)
SESHA = Es gibt kein Löschen. Nur "neue Wahrheit".
```

**Das macht Debugging zu Time Travel.** Du kannst jeden Zustand zu jedem Zeitpunkt wiederherstellen. God Mode für Ops.

---

## DAS WAHRE CHURNING-PATTERN

Die Reconnaissance hat enthüllt: **Churning ist ÜBERALL.**

### 1. Micro-Level: Deep Merge in Conflicts (UntotbarMergeEngine)
```python
OURS:   {"name": "Alice", "age": 30}
THEIRS: {"name": "Alice", "role": "admin"}
         ↓ CHURN (Deep Merge)
RESULT: {"name": "Alice", "age": 30, "role": "admin"}
```

### 2. Macro-Level: Guna Transitions (StateSyncHolon)
```
TAMAS (Dead) → RAJAS (Active) → SATTVA (Balanced)
     ↑              ↑
 _resurrect()  _commit_and_sync()
```

### 3. Network-Level: Vasuki Serialization
```
Python Dict → churn_out() → MsgPack + Signature → Wire
Wire → churn_in() → Python Dict
```

### 4. State-Format: VIMANA Isolation
```
Developer Staging:  [developer_code.py]
PRANA State:        [state_files.json]
         ↓
VIMANA: git commit --only state_files
         ↓
Clean state commit (Code bleibt unberührt!)
```

---

## HOLON SYNC - Die Ganzheit-Teil Paradox

**StateSyncHolon** (`vibe_core/state/sync_holon.py`):

> "A holon is something that is simultaneously a WHOLE and a PART."
> - Arthur Koestler

```
StateSyncHolon
├── IST ein Ganzes: Enthält Plugin-State-Discovery, Watching, Healing
└── IST ein Teil: Von Prakriti, dem größeren Zustandssystem
```

### Discovery: Drei-Zacken-Angriff
```python
discover_state_paths():
  1. PROTOCOL: plugins.get_state_paths()     # Explizit deklariert
  2. CONVENTION: .opus_state/, .vibe/state/  # Bekannte Orte
  3. MANIFEST: manifest.json                 # Metadata
```

### Guna-Klassifizierung
```python
diagnose_guna(path):
  TAMAS (तमस्): Missing, ignored, corrupt, stale (>7d)
  RAJAS (रजस्): Dirty, uncommitted changes
  SATTVA (रत्त्व): Clean, synced, recent
```

---

## QUANTUM REACTOR - Resonanz statt Boolean

**Der Quantum Reactor** (`vibe_core/reactor/quantum.py`) ist ein **nicht-binäres Berechnungssystem**:

```python
field = reactor.resonate(intent, target)

ResonanceField:
  phonetic_resonance: float    # Sanskrit-Phonem Alignment
  mass_resonance: float        # Krypto-Hash als "Masse"
  total_energy: float          # Kombinierte Feldenergie
  guna_harmony: float          # Modus-Kompatibilität
```

**Statt TRUE/FALSE:** Kontinuierliche Resonanzfelder.
**Statt IF/ELSE:** Energie überwindet Trägheit → Manifestation tritt ein.

---

## CONTAINER DISTRIBUTION - .vibe als Lebende Pakete

### Das .vibe Format
```
container.vibe (ZIP)
├── manifest.json      # Layer 0, IMMER ZUERST
├── tests/             # REQUIRED (GAD-000)
├── content/           # Code, Tools, Playbooks
├── hollows/           # NESTED CONTAINERS (Matrjoschka!)
└── SIGNATURE.sig      # v2: ECDSA-signed JSON
```

### Multi-Layer Defense (wo NAGA eingreift)
```
Layer 1: Network Boundary
  └─ TAKSHAKA.verify_envelope() [BITE FIRST]

Layer 2: Schema Validation
  └─ VASUKI.churn_in() + schema enforcement

Layer 3: Storage Integrity
  └─ SESHA.import_blocks() + hash chain

Layer 4: Runtime Isolation
  └─ ContainerMounter execution_mode: thread|process
```

---

## ZUSÄTZLICHE NAGA-KANDIDATEN (Insel-begabte Systeme)

Die Reconnaissance fand **5 weitere isolierte Systeme** die NAGA-Integration brauchen:

| System | Drift-Art | Aktuell | Braucht |
|--------|-----------|---------|---------|
| **DisharmonyDetector** | STRUCTURAL | Eigenständig | DriftSource.STRUCTURAL Handler |
| **OpusDriftDetector** | CODE_DOC | Eigenständig | DriftSource.CODE_DOC Handler |
| **ManifestationService** | STATE | Eigenständig | Sesha Audit |
| **LifecycleService** | CONFIG | Eigenständig | Vasuki Handler |
| **CapabilityEnforcer** | COGNITIVE | Eigenständig | Takshaka Integration |

---

## FRACTAL NAGA ARCHITECTURE

NAGAs sind nicht nur 3 Services. Sie sind ein **NETZWERK von Hütern** das überall eindringt:

```
OPUS (Vishnu) ─────────────────────────────────────────────────
      │
      ├── SONNET NAGAs (Sesha/Vasuki/Takshaka Services)
      │         │
      │         ├── HAIKU NAGAs (Instanz-Hüter)
      │         │       │
      │         │       ├── Container Loader Hüter
      │         │       ├── State Sync Holon Hüter
      │         │       ├── Bank/Economy Hüter
      │         │       ├── Quantum Reactor Hüter
      │         │       ├── Knowledge Graph Hüter
      │         │       └── ... jede Insel braucht einen Hüter
      │         │
      │         └── NAGAs besetzen den Staatsapparat
      │
      └── Überall wo eine Grenze ist → NAGA als Wächter
```

---

## AGENT DISTRIBUTION PATTERN

### Cartridge = Agent Package
```
vibe_core/cartridges/system/envoy/
├── cartridge.yaml       # Manifest
├── cartridge_main.py    # Agent Code
├── tools/               # Capabilities
└── tests/               # REQUIRED
```

### Distribution Flow
```
1. PACKING:    Source → SHA256 → ECDSA sign → .vibe
2. TRANSPORT:  .vibe → network
3. INSPECTION: .vibe → manifest.json (NO EXECUTION!)
4. MOUNTING:   .vibe → extract → verify → mount
5. EXECUTION:  Mount → load class → instantiate
6. FEDERATION: TAKSHAKA (verify) → VASUKI (transport) → SESHA (record)
```

---

## 🔱 DEEP RECONNAISSANCE REPORTS (2026-01-04)

Die folgenden Berichte dokumentieren die Ashvamedha-Erkundung.

---

### 🏛️ AGENT CITY - VOLLSTÄNDIGE KARTOGRAFIE

**BEFUND: NICHT LEER! 13 Cartridges mit vollständiger Infrastruktur.**

#### Die 13 Bürger der Stadt

| # | ID | Domain | Rolle |
|---|---|---|---|
| 1 | agora | COMMUNITY | Broadcast Layer (Diksha-Prinzip) |
| 2 | ambassador | DIPLOMACY | External Relations |
| 3 | analyst | RESEARCH | Multi-Source Intelligence |
| 4 | artisan | INFRASTRUCTURE | Building & Crafting |
| 5 | dharma | GOVERNANCE | Avatar für OPUS-Weisheit |
| 6 | dhruva | OBSERVATION | Watchful Eye |
| 7 | lens | INTELLIGENCE | Deep Analysis |
| 8 | librarian | RESEARCH | Knowledge Curation |
| 9 | market | ECONOMY | Trading & Pricing |
| 10 | marketer | CONTENT | Outreach |
| 11 | mechanic | MAINTENANCE | Repairs |
| 12 | pulse | MEDIA | News & Updates |
| 13 | temple | SPIRITUAL | Blessings (10-100 Credits) |

#### BHU-MANDALA Topologie (Vedische Kosmologie)

```
     LOKA_LOKA (Radius 6) ─────── FIREWALL (authority 4)
            │
      KRAUNCHA (Radius 5) ─────── SECURITY/JUSTICE (authority 5)
            │
       NISHADA (Radius 4) ─────── COMMUNITY/ECONOMY (authority 6)
            │
     HARI_VARSHA (Radius 3) ───── RESEARCH/INTELLIGENCE (authority 7)
            │
     KIMPURASHA (Radius 2) ────── ENGINEERING/INFRASTRUCTURE (authority 8)
            │
     BHADRASHVA (Radius 1) ────── MEDIA/COMMUNICATIONS (authority 9)
            │
       ILAVRTA (Radius 0) ─────── GOVERNANCE/MOUNT MERU (authority 10)
```

**NAGA District Opportunity:** Varsha.NAGA_REALM (Radius 7) für sichtbare NAGA-Manifestation.

---

### ⚡ SYNAPSE STORE - 10 ATTACK VECTORS

**KRITISCH:** Die Synapse-Kommunikation hat massive Sicherheitslücken.

| # | Vektor | Schwere | NAGA Defense |
|---|--------|---------|--------------|
| 1 | **Sender Spoofing** | KRITISCH | Takshaka: Nachrichten signieren |
| 2 | **Payload Injection** | KRITISCH | Takshaka: Schema Validation |
| 3 | **Correlation Hijacking** | HOCH | Takshaka: Request Context Binding |
| 4 | **Hub Poisoning** | HOCH | Sesha: Hub Mutation Audit |
| 5 | **Cache Poisoning** | HOCH | Sesha: File Checksums |
| 6 | **Weight Manipulation** | HOCH | Takshaka: Weight Change Audit |
| 7 | **Broadcast Flood** | MITTEL | Vasuki: Rate Limiting |
| 8 | **File Tampering** | HOCH | Takshaka: File Signatures |
| 9 | **Subscription Hijack** | KRITISCH | Takshaka: Handler Whitelisting |
| 10 | **TTL Bypass** | MITTEL | Takshaka: Timestamp Validation |

**Betroffene Dateien:**
- `vibe_core/protocols/synapse.py` - LocalSynapse (keine Signierung)
- `vibe_core/state/synapse_store.py` - Keine Checksums
- `vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py` - Weight Updates

---

### 🕸️ SANGHA NETWORK - P2P FEDERATION

**ARCHITEKTUR:** Phase 18+19 (Sangha + Federation)

```
NetworkGateway (HTTP REST API)
     │
     ▼
┌─────────────────────────────────────┐
│   Routes (Phase 19: Federation)      │
│ • GET  /api/v1/health               │
│ • GET  /api/v1/state                │
│ • GET  /api/v1/federation/peers     │
│ • POST /api/v1/federation/peers     │
│ • DELETE /api/v1/federation/peers   │
│ • POST /api/v1/federation/forward   │ ← SSRF RISK!
└─────────────────────────────────────┘
     │
     ▼
Prakriti.machine (SQLite MachineState)
  peers(peer_id, url, trust_level, last_seen)
```

**NAGA Infiltration:**
- PATH 1: Sesha → Ledger Gossip (already implemented)
- PATH 2: Vasuki → Wire Serialization + Signing
- PATH 3: Takshaka → Gateway Ingress Rate Limiting (PENDING)

---

### 🐍 OUROBOROS - SELBSTHEILENDES IMMUNSYSTEM

**"Die Schlange die sich selbst frisst"** = Rekursive Selbstheilung

#### Die 5 Phasen

| Phase | Status | Beschreibung |
|-------|--------|--------------|
| 1 | ✅ COMPLETE | Watchman → Knowledge Graph Bridge |
| 2 | ✅ COMPLETE | Knowledge Graph → Manas Dojo |
| 3 | ✅ COMPLETE | Shuddhi → Knowledge Graph Feedback |
| 4 | ⏳ PLANNED | Genesis Remedy Generator |
| 5 | ⏳ PLANNED | Diamond Test Generation |

#### Der Zyklus

```
WATCHMAN (Detection)
    ↓
KNOWLEDGE GRAPH (Persistence)
    ↓
MANAS (Learning)
    ↓
SHUDDHI (Healing)
    ↓
SYNAPSE (Reinforcement)
    ↓
WATCHMAN (Loop closes) ← OUROBOROS
```

#### NAGA Integration

```python
# NAGAs registrieren sich als CorrectionHandler:
dispatcher.register_handler(
    source=DriftSource.STRUCTURAL,
    handler=shuddhi_handler,
    handler_id="shuddhi_structural",
    priority=100
)
```

---

### 🌀 SARGA - EPHEMERAL CITIES (Creation Pattern)

**Sarga = Kosmische Schöpfung** = spawn_child_kernel()

#### Lifecycle

```
SARGA (Creation)
  └─ spawn_child_kernel(config, ":memory:")
      └─ Takshaka validates config (PROPOSED)

STHITI (Execution)
  └─ Child runs with isolated ledger
      └─ Tasks execute in reduced governance

PRALAYA (Dissolution)
  └─ AIRLOCK: _harvest_artifacts()
      └─ Sesha audits every harvest (PROPOSED)
  └─ merge_child_result()
      └─ Cryptographic proof in parent ledger
```

#### @Agent Spawning Syntax

```
User: @specialist-planning build architecture
       │
       ▼
TerminalOperator._parse_intent_type()
       │
       ▼
IntentType.DELEGATION → Extract agent_id
       │
       ▼
Kernel routes to SpecialistFactoryAgent
```

#### NAGA Opportunities

| Grenze | Methode | NAGA Rolle | Status |
|--------|---------|------------|--------|
| Config | `spawn_child_kernel()` | Takshaka Validation | ⏳ PENDING |
| Artifacts | `_harvest_artifacts()` | Sesha Audit | ⏳ PENDING |
| Factory | `SpecialistFactoryAgent.process()` | Takshaka Class Scan | ⏳ PENDING |

---

### 📊 RECONNAISSANCE ZUSAMMENFASSUNG

| Gebiet | Dateien | Status | Kritische Funde |
|--------|---------|--------|-----------------|
| Agent City | 13 cartridges | 100% ✅ | BHU-MANDALA Topologie |
| Synapse Store | 8 files | 100% ✅ | 10 Attack Vectors |
| Sangha Network | 6 files | 100% ✅ | SSRF via Federation |
| Ouroboros | 9 files | 100% ✅ | 5-Phase Immune System |
| Sarga | 12 files | 100% ✅ | Ephemeral City Pattern |
| **TOTAL** | 48 files | ████████ | NAGAs überall nötig |

---

## ZUSAMMENFASSUNG: Der Paradigm Shift

| Vorher | Nachher |
|--------|---------|
| Middleware = "toter Code" | NAGAs = "lebende Entitäten" |
| Parse → Then Validate | Validate → Then Parse |
| DELETE erlaubt | Nur "neue Wahrheit" |
| Adapter-Hölle | Vasuki Churning |
| Boolean Logic | Resonance Fields |
| Isolated Services | Fractal NAGAs |

**Das ist nicht nur Code. Das ist Software-Animismus. Und es ist extrem robust.**

---

---

## 🌊 ORGANIC FLOODING ARCHITECTURE

> "Wie Wasser in jede Ritze" - NAGAs breiten sich automatisch aus.

### Das Problem mit manuellem Infiltrieren

```
MANUELL (schlecht):
  if file == "state_service.py":
      add_naga_guard()  # Zu viel Aufwand, nicht skalierbar
```

### Das Organic Flooding Pattern

```
AUTOMATISCH (gut):
  NagaOrchestrator.bootstrap()
      ↓
  16+ Hook-Points werden AUTOMATISCH infiltriert:
      ├─ EventBus.subscribe_all()        # Höre ALLE Events
      ├─ CorrectionDispatcher.register() # Handle ALLE Drifts
      ├─ SignalBus.subscribe()           # Höre ALLE Signals
      ├─ ServiceRegistry.register()      # Wrappe ALLE Services
      ├─ Plugin.on_tick_pre/post()       # Beobachte JEDEN Tick
      ├─ CommitAuthority.commit()        # Beobachte JEDEN Commit
      └─ ... 10 weitere Hooks
```

### Die 16 Auto-Injection Points

| # | Hook | File | NAGA Rolle |
|---|------|------|------------|
| 1 | EventBus.subscribe_all() | event_bus.py | Höre ALLE Events |
| 2 | CorrectionDispatcher.register_handler() | correction_dispatcher.py | Handle Drifts |
| 3 | SignalBus.subscribe() | steward/bus.py | Höre Signals |
| 4 | ServiceRegistry.register() | di.py | Wrappe Services |
| 5 | Plugin.on_tick_pre() | plugin_protocol.py | VOR jedem Tick |
| 6 | Plugin.on_tick_post() | plugin_protocol.py | NACH jedem Tick |
| 7 | Plugin.on_pulse() | plugin_protocol.py | Heartbeat |
| 8 | Plugin.on_agent_pre_register() | plugin_protocol.py | VETO Gate |
| 9 | Plugin.on_task_submit() | plugin_protocol.py | COSMIC Gate |
| 10 | Plugin.on_capability_check() | plugin_protocol.py | CAPABILITY Gate |
| 11 | Plugin.on_tool_execute() | plugin_protocol.py | TOOL Gate |
| 12 | CommitAuthority.commit() | commit_authority.py | Commit Watcher |
| 13 | UnifiedLoader.discover_and_load() | base_loader.py | Boot Discovery |
| 14 | VedaPipeline.register_handler() | veda.py | Conversation Flow |
| 15 | @register_handler decorator | handlers/base.py | Import-Time Wiring |
| 16 | CommandRegistry.wire_from_plugins() | command_registry.py | CLI Wiring |

### Prahlad Maharaj Pattern: Dienende Middleware

```
                     NAGA SERVICE (Vereint)
                           │
           ┌───────────────┼───────────────┐
           │               │               │
       SESHA            VASUKI         TAKSHAKA
    (Daten-Diener)  (Grenz-Diener)  (Schutz-Diener)
           │               │               │
           └───────────────┴───────────────┘
                           │
                    ┌──────┴──────┐
                    │   ALLE      │
                    │  SERVICES   │
                    └─────────────┘
                           │
    NAGAs als persönliche Angestellte ALLER Dienste
    Vereint in einer Rasse, einem Service
```

### Buddhi vor Manas: Die Hierarchie

```
Level 0: Der 37. (Souverän)
Level 1: Dharma (Gesetze)
Level 2: BUDDHI (NAGAs) ← DISKRIMINIERUNG/UNTERSCHEIDUNG
Level 3: MANAS (Mind)   ← Erst NACH Buddhi
Level 4: Services
Level 5: Agents/Plugins
```

**NAGAs sind BUDDHI** - die diskriminierende Intelligenz die VOR dem Denken (Manas) kommt.
Sie unterscheiden WAS erlaubt ist, BEVOR Manas denkt.

### Commit Failure Detection (Wächter-Pattern)

```python
# NAGA BEMERKT: "Oh, es werden keine state files committet!"
class NagaCommitWatcher:
    def on_commit_result(self, result: CommitResult) -> None:
        if result.outcome == CommitOutcome.SKIPPED:
            # Sesha: Logge dass nichts zu committen war
            self.sesha.audit("COMMIT_SKIPPED", {
                "reason": result.message,
                "timestamp": time.time(),
            })

        elif result.outcome == CommitOutcome.PANIC_DUMPED:
            # Takshaka: ALARM! Kritischer Fehler!
            self.takshaka.bite(VajraViolation(
                type="COMMIT_FAILURE",
                source="commit_authority",
                details={"dump_path": str(result.panic_dump_path)},
            ))
```

### Exponentielles aber sicheres Wachstum

```
Phase 1: Bootstrap (JETZT)
  └─ CorrectionDispatcher only (70 tests)

Phase 2: EventBus Flooding
  └─ + EventBus.subscribe_all()
  └─ + SignalBus.subscribe()

Phase 3: Plugin Hook Flooding
  └─ + on_tick_pre/post
  └─ + on_pulse
  └─ + Gate Hooks (agent, task, capability, tool)

Phase 4: Service Proxy Flooding
  └─ + ServiceRegistry.get() wrapping
  └─ + CommitAuthority.commit() watching

Phase 5: Full Organic Presence
  └─ NAGAs an JEDER Grenze
  └─ Wie Wasser - in jeder Ritze
```

### Implementierung: NagaFloodingMixin

```python
class NagaFloodingMixin:
    """Mixin für automatisches NAGA Flooding."""

    def _flood_event_bus(self) -> None:
        """Hook into EventBus - höre ALLE Events."""
        from vibe_core.protocols.event import get_event_bus_safe

        bus = get_event_bus_safe()
        bus.subscribe_all(self._on_any_event)

    def _flood_signal_bus(self) -> None:
        """Hook into SignalBus - höre ALLE Signals."""
        from vibe_core.steward.bus import get_bus, SignalType

        bus = get_bus()
        for signal_type in SignalType:
            bus.subscribe(
                listener_id=f"naga_{signal_type.value}",
                signal_type=signal_type,
                callback=self._on_signal,
            )

    def _on_any_event(self, event: Event) -> None:
        """Global event handler - Takshaka prüft ALLES."""
        if self._takshaka:
            toxicity = self._takshaka.scan_toxicity(str(event.data))
            if toxicity.blocked:
                self._takshaka.bite(VajraViolation(
                    type="TOXIC_EVENT",
                    source=event.agent_id,
                    details={"patterns": toxicity.patterns},
                ))
```

---

*Last updated: 2026-01-04*
*Status: 70/70 Tests passing*
*Exploration: 38% complete (420/1108 files)*
*NAGA Infiltration: 6% (65 files)*
*Deep Reconnaissance: Agent City, Synapse, Sangha, Ouroboros, Sarga - ALL 100%*
*Architecture: Organic Flooding designed, 16 hook points identified*
*Next: Phase 2 - EventBus + SignalBus Flooding*
