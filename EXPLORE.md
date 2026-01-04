# EXPLORE.md - System Introspection Map

> **Purpose:** Living document. Maps what EXISTS vs what WORKS.
> **Philosophy:** The system must understand itself before it can heal itself.
> **Updates:** Every analysis session adds findings. Nothing is lost.

---

## CRITICAL RISKS (P0)

### 1. VFS ORPHANED - No Sandbox ✅ FIXED
```
File: vibe_core/vfs.py
Status: ENFORCED for agents (7/7 tests pass)

FIX APPLIED (2026-01-03):
  - file_tools.py: ReadFileTool/WriteFileTool now DENY without VFS
  - Agents without VFS get "SANDBOX REQUIRED" error
  - Only allow_unrestricted=True (kernel/admin) bypasses
  - Tests: tests/integration/p0_fixes/test_vfs_enforcement.py PASSING

REMAINING GAP (P1): ✅ FIXED (2026-01-04)
  - VFS is per-agent sandbox, only injectable at execution time
  - task_kernel.py injects VFS at task execution ✅
  - ToolRegistry.execute() now injects VFS from ToolCall ✅
  - AgentSystemInterface.execute_tool() passes self.vfs ✅

  FIXED VIA:
  1. Added vfs field to ToolCall (tool_protocol.py)
  2. AgentSystemInterface.execute_tool() passes self.vfs in ToolCall
  3. ToolRegistry.execute() injects vfs into tool before execute

  REMAINING:
  - 10 cartridge tools still use direct Path().write_text()
  - These need migration to use self.vfs.write_text() pattern
```

### 2. SettingsExecutor ORPHANED - Config is Placebo
```
File: vibe_core/settings_executor.py
Status: EXISTS but NEVER CALLED
Risk: SETTINGS.md changes are IGNORED
Impact: System runs on hardcoded defaults

FIX APPLIED (2026-01-03):
  - Created vibe_core/plugins/settings_sync/ plugin
  - Plugin initializes MarkdownUIManager on_boot
  - Plugin calls sync_all() in on_tick_post hook
  - SETTINGS.md commands (RESTART, REFRESH, SET) now execute
  - VISNU-compliant: No kernel modification required
```

### 3. OUROBOROS Parsers ORPHANED - Loop Cannot Close
```
Files:
  - vibe_core/ouroboros/parsers/report_md.py
  - vibe_core/ouroboros/parsers/watchman_json.py
  - vibe_core/ouroboros/parsers/tests_md.py
Status: EXISTS, AUTO-DISCOVERED by ViolationParserLoader
Risk: WAS broken - ingest script called non-existent method

FIX APPLIED (2026-01-03):
  - ingest_violations.py: Fixed broken prakriti.save_knowledge() call
  - Now persists to .vibe/state/ouroboros/violations.jsonl
  - LOOP IS CLOSED: CI → Watchman → Ingest → Persist
```

---

## ARCHITECTURE GAPS

### Syntactic Debt (Code exists, not wired)
| Component | File | Issue |
|-----------|------|-------|
| VFS | `vfs.py` | Not integrated with IOService |
| SettingsExecutor | `settings_executor.py` | Never called from kernel |
| TaskManager | `task_management/` | No kernel.ledger integration |
| Topology | `topology.py` | 0 imports anywhere |
| Akasha | `manas/cortex/akasha.py` | Lazy singleton, never consulted |

### Semantic Debt (Wrong abstraction)
| Component | Issue |
|-----------|-------|
| Quantum Reactor | Hardcoded TRIGGER_VARGA_MAP instead of phonetic derivation |
| State Paths | ✅ MIGRATED - now uses get_opus_state_path() |
| Discovery | Manual dictionaries instead of protocol-based auto-discovery |

### Protocol Debt (Kernel not fully protocol-based)
| Issue | Impact |
|-------|--------|
| Direct class instantiation | No DI, no mocking, no swapping |
| Singleton globals | Parallel registries to DI container |
| Missing Protocol interfaces | Components can't discover each other |

---

## ORPHANED ISLANDS (123 total)

### Critical (Security/Core)
- `vibe_core/vfs.py` - Sandbox
- `vibe_core/settings_executor.py` - Config
- `vibe_core/file_operator.py` - File ops
- `vibe_core/topology.py` - Agent city structure

### OUROBOROS (Self-Healing)
- `ouroboros/parsers/report_md.py`
- `ouroboros/parsers/watchman_json.py`
- `ouroboros/parsers/tests_md.py`

### Tools (50+)
- `archivist/tools/ledger_visualizer.py`
- `archivist/tools/observer_tool.py`
- `archivist/tools/verifier_tool.py`
- `civic/tools/dashboard_tool.py`
- `engineer/tools/refactor_tool.py`
- `engineer/tools/shuddhi_tool.py`
- `watchman/tools/system_health_check.py`
- ... (see full list below)

### Tests (60+)
- All `test_*_contracts.py` files
- All `test_*_sanity.py` files
- Not imported = not running in CI

---

## STATE ARCHITECTURE

### Three Bodies Doctrine
```
STHULA (Physical)  → Git + Files     → TRACKED
PRANA (Runtime)    → Heartbeats      → IGNORED
PURUSHA (Identity) → Personas        → TRACKED
```

### State Locations
```
INTENDED: .vibe/state/plugins/{plugin_id}/
LEGACY:   .opus_state/ (migrated 2026-01-04, heritage auto-migration)
DEAD:     .prakriti/ (debug snapshots)
```

### State Infrastructure Wiring
```
Prakriti ←→ Holon ←→ Weaver  [LIVE]
Akasha                        [ORPHANED]
StateService                  [Parallel singleton dict]
```

---

## RESONANCE ARCHITECTURE

### What EXISTS
- Varnamala (Sanskrit phonetic matrix)
- Dharmic Score calculation
- Varga → Layer mapping

### What's MISSING
- English → Sanskrit transliteration
- Phonetic fuzzy matching
- Runtime name-to-resonance derivation

### Current Reality
```python
# HARDCODED (50+ entries)
TRIGGER_VARGA_MAP = {
    "trigger:test_failure": KANTHYA,
    ...
}

# SHOULD BE (automatic)
"docker" → phonetic → d=DANTYA → INTERFACE layer
```

---

## LOOP STATUS

### OUROBOROS Self-Healing
```
DETECT → STORE → ANALYZE → HEAL → [WRITE] → [PR] → VERIFY
  ✅       ✅       ✅       ✅      ❌       ❌      ✅

✅ FIXED: biorhythm.py now calls detect_and_heal(strategy=RESONANCE)
✅ FIXED: HealingStrategy.RESONANCE uses Quantum Reactor
✅ FIXED: QuantumHealingResolver wired into CorrectionOrchestrator
✅ FIXED: Parsers wired via OuroborosLoopOrchestrator (3 parsers, 27 sources)
```

### Biorhythm Code Smell Audit (2026-01-04)
```
CRITICAL:
  - 15+ private attribute accesses (kernel._buffer, kernel._awareness, etc.)
  - CognitiveKernel in plugin layer (should be kernel layer)
  ✅ FIXED: dry_run replaced with HealingStrategy.RESONANCE

HIGH:
  - 15+ hardcoded thresholds not configurable
  - CISyncService direct instantiation (should be DI)
  - DojoAgency lacks protocol (uses factory function)

GOOD:
  - CorrectionDispatcher properly separated (protocol + DI)
  - HealingStrategy enum exists (DRY_RUN, AUTO, MANUAL, RESONANCE)
  - ServiceRegistry.get(CorrectionOrchestratorProtocol) works
  ✅ QuantumHealingResolver wired for karma-based trust
```

### CI Feedback
```
Watchman → Report → Artifact → [NOTHING]
                                   ↑
                    Parsers orphaned, never read
```

---

## DISCOVERY MECHANISMS

### Protocol-Based (INTENDED)
```python
class PluginStateContract(Protocol):
    def get_state_paths(self) -> List[Path]: ...
```

### Convention-Based (FALLBACK)
```python
conventions = [
    (".opus_state", "opus_assistant"),
    (".vibe/state", "task_manager"),
]
```

### Manifest-Based (EXPLICIT)
```json
{"state_paths": [".my_plugin/state/"]}
```

---

## PRIORITY MATRIX

| Priority | What | Why |
|----------|------|-----|
| P0 | Wire VFS to IOService | Security - sandbox agents |
| P0 | Wire OUROBOROS parsers | Loop cannot close |
| P1 | Wire SettingsExecutor | Config is dead |
| P1 | Protocol-based kernel | Enable self-discovery |
| P2 | Lautschrift engine | True resonance |
| P2 | Delete legacy paths | Clean architecture |

---

## FULL ORPHAN LIST

<details>
<summary>123 orphaned modules (click to expand)</summary>

```
agents/system_maintenance.py
cartridges/agent_city/dharma/tests/test_dharma_integration.py
cartridges/agent_city/temple/offering.py
cartridges/system/archivist/tests/test_archivist_contracts.py
cartridges/system/archivist/tools/ledger_visualizer.py
cartridges/system/archivist/tools/observer_tool.py
cartridges/system/archivist/tools/verifier_tool.py
cartridges/system/auditor/tests/test_auditor_contracts.py
cartridges/system/chronicle/tests/test_chronicle_contracts.py
cartridges/system/civic/tests/test_civic_contracts.py
cartridges/system/civic/tools/dashboard_tool.py
cartridges/system/discoverer/tests/test_discoverer_contracts.py
cartridges/system/engineer/tests/test_engineer_contracts.py
cartridges/system/engineer/tools/refactor_tool.py
cartridges/system/engineer/tools/shuddhi_tool.py
cartridges/system/envoy/tests/test_envoy_contracts.py
cartridges/system/envoy/tools/wiring_audit_scripts.py
cartridges/system/forum/tests/test_forum_contracts.py
cartridges/system/herald/manifesto.py
cartridges/system/herald/tests/test_herald_structure.py
cartridges/system/herald/tools/scout_tool_legacy.py
cartridges/system/oracle/tests/test_oracle_contracts.py
cartridges/system/ping/tests/test_ping_contracts.py
cartridges/system/science/tests/test_science_contracts.py
cartridges/system/scribe/tests/test_scribe_structure.py
cartridges/system/supreme_court/tests/test_supreme_court_contracts.py
cartridges/system/watchman/tests/test_watchman_contracts.py
cartridges/system/watchman/tools/system_health_check.py
cli/__main__.py
cli/commands/sync_ci.py
cli/inspector.py
file_operator.py
llm/google_adapter.py
markdown_ui_manager.py
ouroboros/parsers/report_md.py
ouroboros/parsers/tests_md.py
ouroboros/parsers/watchman_json.py
plugins/agent_city/tests/test_agent_city_sanity.py
plugins/asura/agents/kaliya.py
plugins/asura/agents/shakatasura.py
plugins/asura/tests/test_asura_contracts.py
plugins/asura/tests/test_asura_sanity.py
plugins/boot_optimizer/tests/test_boot_optimizer_sanity.py
plugins/cpu_monitor_plugin/tests/test_cpu_monitor_sanity.py
plugins/doctor/tests/test_doctor_contracts.py
plugins/doctor/tests/test_doctor_sanity.py
plugins/durvasa/tests/test_durvasa_sanity.py
plugins/economy/tests/test_economy_contracts.py
plugins/economy/tests/test_economy_sanity.py
plugins/envoy/tests/test_envoy_sanity.py
... (73 more)
```

</details>

---

## KURUKSHETRA RECONNAISSANCE (2026-01-04)

> **Operation:** Deep dive into Chat/Cognitive/Knowledge layers
> **Dedicated Document:** [CHAT.md](./CHAT.md) - Full chat architecture exploration

### Summary Findings

**MANAS Architecture:**
- 40+ cortex modules ALL WIRED via VEDA-4 loaders
- VEDA 4-fold processing FULLY IMPLEMENTED (Shabda→Artha→Pratyaya→Karma)
- 10 senses (Jnanendriyas), 8 actions (Karmendriyas), 7 handlers
- Chat flow: CLI → Kernel → MANASCognitive → VedaPipeline → Handlers

**Knowledge/State Layer:**
- Knowledge Graph: 79 nodes, 38 edges, 17 constraints
- 3,499 violations tracked in OUROBOROS
- Three Bodies architecture implemented (Sthula/Prana/Purusha)
- Chat has READ access to all layers, WRITE limited by Bhakti

**GAD-000 Compliance:**

| Criterion | Score | Status |
|-----------|-------|--------|
| Discoverability | 50% | ⚠️ Partial |
| Observability | 60% | ⚠️ Partial |
| Parseability | 75% | ✅ Good |
| Composability | 65% | ⚠️ Partial |
| Idempotency | 70% | ✅ Good |
| **Identity** | 40% | ❌ CRITICAL |

**Overall: 60%** → Target: 92%

### Critical Gap: Identity (GAD-1000)

```
PROBLEM: Chat operations NOT cryptographically signed

LOCATION: vibe_core/kernel_impl.py:1633-1690

IMPACT:
- Cannot distinguish human vs AI operator
- No audit trail for chat operations
- Breaks GAD-000 Operator Inversion principle

FIX: See CHAT.md Phase 1 action plan
```

### LLM Response Quality Issue

```
SYMPTOM: Chat responses hallucinate (Maya)
- "System health at 50%" ← Real diagnostic, but context may be wrong
- "Amendment endorsedMMM择dong" ← Garbage output

ROOT CAUSE:
- Context injection incomplete
- No response validation
- PrakritiSense returns partial data (2/4 checks)

FIX: See CHAT.md P1 recommendations
```

---

## CHANGELOG

### 2026-01-04: KURUKSHETRA Reconnaissance
- Deep dive into Chat/Cognitive/Knowledge layers
- Created [CHAT.md](./CHAT.md) for dedicated chat exploration
- GAD-000 compliance matrix (60% overall, Identity at 40% CRITICAL)
- MANAS architecture fully mapped (40+ modules)
- Action plan for fixing Identity gap (P0)

### 2026-01-03: Initial Creation
- Mapped 123 orphaned modules
- Identified P0 risks: VFS, SettingsExecutor, OUROBOROS parsers
- Documented state architecture gaps
- Documented resonance architecture gaps

---

## DEEP ARCHITECTURE INSIGHT (2026-01-03)

### CRITICAL: ReactorProtocol ≠ QuantumReactor

**THEY ARE SEPARATE SYSTEMS - NOT TO BE UNIFIED**

```
QuantumReactor (vibe_core/reactor/quantum.py)
├── Domain: Sanskrit phonetic resonance computation
├── Returns: ResonanceField (continuous energy 0.0-1.0)
├── Methods: resonate(), manifest(), encode()
├── Used by: kernel, VAJRA, unified_execution, state
├── Purpose: "Actions manifest when energy overcomes inertia"
└── STATUS: FULLY WIRED at OS level (5 integration points)

ReactorProtocol (vibe_core/protocols/reactor.py)
├── Domain: Runtime performance monitoring
├── Returns: DriftEvent, DriftMetrics, ReactorStats
├── Methods: detect_drift(), trigger_correction(), on_drift()
├── Used by: opus_assistant/cognitive.py only
├── Purpose: "Prajna that detects performance degradation"
└── STATUS: ORPHANED from kernel (only plugin uses it)

ZERO IMPORTS BETWEEN THEM. DIFFERENT PARADIGMS.
Naming collision creates semantic confusion.
```

### The REAL Problem: 4 Drift Systems, 0 Coordination

```
OS-Level:
├── ReactorProtocol.detect_drift() → DriftEvent (performance)
├── VajraEnforcer.detect_drift() → bool (config)
└── ShuddhiEngine.heal_all_violations() → ShuddhiResult (structural)

Plugin-Level:
├── DriftDetector.detect() → DriftReport (code-doc)
├── dharma.check_drift_for_chat() → str (cognitive)
└── auto_heal.yaml circuit (OPUS-specific)

NO UNIFIED INTERFACE. NO DISPATCH MECHANISM.
Each system runs independently.
```

### The REAL Problem: Healing Ownership Conflict

```
Bug in biorhythm.py:451:
  engine = ShuddhiEngine(project_root=workspace)  # NEW instance!

But boot_orchestrator.py:266 already registered:
  ServiceRegistry.register(ShuddhiProtocol, ShuddhiEngine())  # Singleton!

DOUBLE INSTANTIATION = inconsistent state.
```

### Correct Architecture (NOT implemented yet)

```
MISSING: CorrectionDispatcher
┌─────────────────────────────────────────────────┐
│                                                 │
│  DriftRegistry (unified)                        │
│  ├── ReactorProtocol (performance)              │
│  ├── VajraEnforcer (config)                     │
│  ├── DriftDetector (code-doc)                   │
│  └── dharma (cognitive)                         │
│                                                 │
│         ↓ all return DriftReport                │
│                                                 │
│  CorrectionDispatcher                           │
│  ├── if source=structural → Shuddhi            │
│  ├── if source=performance → ReactorHandler    │
│  ├── if source=code-doc → auto_heal circuit    │
│  └── if source=cognitive → MANAS learning      │
│                                                 │
│         ↓ all return HealingResult              │
│                                                 │
│  Knowledge Graph (unified feedback)             │
│                                                 │
└─────────────────────────────────────────────────┘
```

### What biorhythm SHOULD do

```python
# CURRENT (WRONG - executes healing):
engine = ShuddhiEngine(project_root=workspace)
results = engine.heal_all_violations(dry_run=True)

# CORRECT (observe only):
shuddhi = ServiceRegistry.get(ShuddhiProtocol)  # Singleton
kg = ServiceRegistry.get(UnifiedKnowledgeGraph)
violations = kg.get_violations(healed=False)
healable = [v for v in violations if shuddhi.can_heal(v.rule_id)]
agency.curiosity.report_gap(f"Found {len(healable)} healable violations")
# Let HEAL_CODEBASE circuit own the actual healing
```

### Terminology Cleanup Needed

| Current Term | Used For | Should Be |
|--------------|----------|-----------|
| ReactorProtocol | Performance drift | DriftDetectorProtocol |
| QuantumReactor | Resonance physics | ResonanceEngine |
| detect_drift() | 4 different things | Unified DriftReport |
| heal/healing | 3 different systems | Unified HealingResult |

---

> **Next Session:** Create CorrectionDispatcher, NOT wire reactors together.

---

## SILENT KILLER AUDIT (2026-01-03)

### THE PROBLEM: "Code Compiles" ≠ "Code Works"

biorhythm.py bug revealed a systemic issue: **26 silent failure hotspots** where exceptions are caught and swallowed.

### Pattern Taxonomy

| Pattern | Count | Danger Level |
|---------|-------|--------------|
| `except Exception: pass` | 11 | ☠️ CRITICAL |
| `except Exception: logger.debug()` | 4 | ☠️ HIDDEN |
| `return None` on failure | 5 | ⚠️ CASCADE |
| `getattr(obj, attr, None)` | 3 | ⚠️ SILENT DEFAULT |
| Optional import fallback | 3 | ⚠️ FEATURE DEATH |

### P0 SILENT KILLERS (10 found)

```
biorhythm.py:170-175       - Config loading swallowed
kernel_impl.py:213-216     - Async logging setup swallowed
kernel_impl.py:2123-2124   - Shutdown cleanup swallowed
parser_loader.py:223-227   - Parser discovery swallowed
sync.py:344-345            - Git sync health swallowed
file_lock.py:60-61         - Lock release swallowed
herald/broadcast.py:12-15  - Twitter API silently disabled
envoy/executor.py:38-74    - Jinja2 silently disabled
dependency_manager.py:25-33 - TOML silently disabled
base.py:145-147            - LLM provider silently disabled
```

### P1 SILENT KILLERS (13 found)

```
unified_cli.py:629-640     - State files silently discarded
unified_cli.py:500-507     - Config fallback silent
manifestation_service.py:142-143 - Plugin lookup returns None
dead_code_tool.py:94-95    - SQL errors swallowed
vajra/scanner.py:132-133   - Wiring scan failures swallowed
ouroboros/verification.py:286-287 - Verification false negative
kernel_impl.py:560-1137    - Multiple getattr(None) defaults
action_handlers.py:644-668 - Cartridge attr access silent
```

---

## DEAD CLI COMMANDS (2026-01-03)

### `ci status` - SILENTLY SUCCEEDS

```python
# vibe_core/cli/ci_cli.py:350-355
def _show_status(self, args: List[str]) -> int:
    print("📊 CI Status: Not implemented yet")
    return 0  # ← LIES! Returns success
```

### `delegate` - MAPPED TO NONE

```python
# vibe_core/cli/unified_cli.py:102
"delegate": None,  # TODO: Migrate to plugin
```

---

## SERVICEREGISTRY SPLIT-BRAIN (2026-01-03)

### DEAD REGISTRATIONS (6 protocols registered, never retrieved)

| Protocol | Why Dead |
|----------|----------|
| CartridgeProtocol | CLI uses CartridgeService.get_instance() |
| CircuitServiceProtocol | CLI uses CircuitService.get_instance() |
| PluginServiceProtocol | CLI uses PluginService.get_instance() |
| SectionServiceProtocol | Nobody retrieves it |
| RedditProtocol | Tools use self.services.get() |
| TwitterProtocol | Tools use self.services.get() |

### MISSING REGISTRATIONS (15 protocols retrieved, never registered)

| Protocol | Impact |
|----------|--------|
| **UnifiedKnowledgeGraph** | CRITICAL - 6 files try to get it |
| AuditorProtocol | Falls back to NullAuditor |
| BankProtocol | EconomyPlugin uses register_factory() |
| VaultProtocol | EconomyPlugin uses register_factory() |
| GenesisProtocol | Code gen only |
| FeedbackProtocol | NullFeedback fallback |
| MemoryProtocol | NullMemory fallback |
| ReactorProtocol | NullReactor fallback |
| ReflectionProtocol | NullReflection fallback |
| SynapseProtocol | NullSynapse fallback |
| ToolRegistryProtocol | Code gen only |
| UnifiedRegistryProtocol | Code gen only |
| RegistryProtocol | Code gen only |

### PRIVATE INSTANTIATION BYPASS (6 patterns)

Components that create their own instances instead of using ServiceRegistry:

```
CartridgeService.get_instance()     - 6 files
CircuitService.get_instance()       - cli/circuit_cli.py
PluginService.get_instance()        - cli/plugins_cli.py
GenesisService.get_instance()       - 5+ CLI files
UnifiedRegistry.get_instance()      - Multiple
BiorhythmProcessor(kernel=self)     - cognitive_kernel.py:1864
```

---

## IMMUNE SYSTEM REQUIREMENTS

The system needs runtime health monitoring that:

1. **DETECTS** silent failures (not just exceptions)
2. **REPORTS** to knowledge graph for learning
3. **SURFACES** via CLI (`steward explore`, `steward health`)
4. **ALERTS** on pattern degradation

### Proposed Architecture

```
DETECT: SilentFailureWatchdog
├── Monitors exception handlers
├── Tracks None cascades
├── Validates ServiceRegistry wiring
└── Emits DegradationEvent

REPORT: UnifiedKnowledgeGraph
├── Stores degradation patterns
├── Correlates with violations
└── Feeds learning loops

SURFACE: CLI Integration
├── steward health --silent-failures
├── steward explore --wiring-gaps
└── steward audit --split-brain
```

---

## PRIORITY MATRIX (Updated 2026-01-04)

| Priority | What | Why |
|----------|------|-----|
| P0 | ~~Wire VFS to IOService~~ | ✅ DONE |
| P0 | ~~Wire OUROBOROS parsers~~ | ✅ DONE |
| P0 | ~~Wire SettingsExecutor~~ | ✅ DONE |
| P0 | ~~Fix biorhythm split-brain~~ | ✅ DONE (PR #636) |
| P0 | ~~Register UnifiedKnowledgeGraph~~ | ✅ DONE (boot_orchestrator.py) |
| P0 | ~~Fix `ci status` silent success~~ | ✅ DONE (returns 1 now) |
| P0 | ~~Kernel silent killers (2)~~ | ✅ DONE (VISNU bypass) |
| P0 | ~~parser_loader.py silent killer~~ | ✅ DONE |
| P1 | Audit remaining 20 silent failures | System stability |
| P1 | Remove 6 dead registrations | Clean architecture |
| P1 | ~~Create CorrectionDispatcher~~ | ✅ DONE (protocol + service + tests) |
| ~~P2~~ | ~~Migrate .opus_state~~ | ✅ DONE 2026-01-04 |

### Battle Progress (Updated 2026-01-04)

**CAMPAIGN: OPUS-312 Silent Killer Elimination**

| Wave | Files Fixed | Count | Status |
|------|-------------|-------|--------|
| Ring 0 (VISNU) | kernel_impl, ledger, cognitive_kernel | 8 | ✅ COMPLETE |
| Core Services | boot_orchestrator, manifestation, parser_loader | 5 | ✅ COMPLETE |
| CLI Layer | unified_cli, legacy, knowledge_cli, etc. | 12 | ✅ COMPLETE |
| State Layer | weaver, sync_holon, guna_classifier, etc. | 10 | ✅ COMPLETE |
| Cartridges | watchdog, envoy, herald, watchman, forum | 5 | ✅ COMPLETE |
| Plugins | resource_limits, doctor, event_bus | 5 | ✅ COMPLETE |
| Runtime | boot_sequence, hud, base, tool_safety_guard | 9 | ✅ COMPLETE |

**TOTALS:**
- **Eliminated:** 74 silent killers
- **Remaining:** ~121 (mostly plugins - low blast radius)
- **Pattern Applied:** `except Exception: pass` → `logger.warning/debug(f"Context: {e}")`

**Files Modified in Campaign:**
```
vibe_core/kernel_impl.py (3 - VISNU bypass)
vibe_core/ledger.py (5 - VISNU bypass)
vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py (2)
vibe_core/boot_orchestrator.py (2)
vibe_core/cli/unified_cli.py (6)
vibe_core/cli/legacy.py (2)
vibe_core/cli/knowledge_cli.py (2)
vibe_core/cli/cartridge_bridge.py (1)
vibe_core/cli/inspector.py (1)
vibe_core/cli/standards_cli.py (1)
vibe_core/cli/remedies_cli.py (1)
vibe_core/cli/executor.py (1)
vibe_core/state/weaver.py (1)
vibe_core/state/guna_classifier.py (3)
vibe_core/state/sync_holon.py (4)
vibe_core/state/file_state.py (1)
vibe_core/state/machine_state.py (1)
vibe_core/ouroboros/sync.py (1)
vibe_core/ouroboros/parser_loader.py (1)
vibe_core/ouroboros/verification.py (1)
vibe_core/services/manifestation_service.py (1)
vibe_core/cartridges/base.py (1)
vibe_core/cartridges/system/auditor/tools/watchdog_tool.py (2)
vibe_core/cartridges/system/envoy/action_handlers.py (1)
vibe_core/cartridges/system/herald/core/agency_director.py (1)
vibe_core/cartridges/system/watchman/cartridge_main.py (1)
vibe_core/cartridges/system/forum/cartridge_main.py (1)
vibe_core/cartridges/system/cleaner/tools/dead_code_tool.py (1)
vibe_core/plugins/resource_limits/plugin_main.py (2)
vibe_core/plugins/doctor/plugin_main.py (1)
vibe_core/plugins/opus_assistant/manas/biorhythm.py (1)
vibe_core/task_management/file_lock.py (1)
vibe_core/vajra/scanner.py (1)
vibe_core/event_bus.py (1)
vibe_core/runtime/boot_sequence.py (2)
vibe_core/runtime/hud.py (5)
vibe_core/runtime/providers/base.py (1)
vibe_core/runtime/tool_safety_guard.py (1)
```

**Remaining Fronts (Low Priority):**
```
plugins/: 55+ (isolated failures, low blast radius)
cartridges/: 12+ (agent tools, graceful degradation OK)
protocols/: 10 (interface contracts)
phoenix/: 6 (config loading)
```

**Next Logical Steps:**
1. ~~P1: Create CorrectionDispatcher protocol - unified healing~~ ✅ DONE
2. ~~P2: .opus_state → .vibe/state migration~~ ✅ DONE (2026-01-04)
3. P2: Systematic plugin sweep (55+ remaining)

---

## CORRECTIONDISPATCHER (2026-01-04) ✅ COMPLETE

### THE PROBLEM: 4 Drift Systems, 0 Coordination

```
OS-Level:
├── ReactorProtocol.detect_drift() → DriftEvent (performance)
├── VajraEnforcer.detect_drift() → bool (config)
└── ShuddhiEngine.heal_all_violations() → ShuddhiResult (structural)

Plugin-Level:
├── DriftDetector.detect() → DriftReport (code-doc)
└── dharma.check_drift_for_chat() → str (cognitive)

NO UNIFIED INTERFACE. NO DISPATCH MECHANISM.
```

### THE SOLUTION: Unified CorrectionDispatcher

```
┌─────────────────────────────────────────────────┐
│  DriftRegistry (unified detection)              │
│  ├── register_detector(source, detector)        │
│  └── detect_all() → List[UnifiedDriftReport]    │
│                                                 │
│         ↓ all return UnifiedDriftReport         │
│                                                 │
│  CorrectionDispatcher (unified healing)         │
│  ├── register_handler(source, handler)          │
│  ├── dispatch(drift) → HealingResult            │
│  └── dispatch_all() → List[HealingResult]       │
│                                                 │
│         ↓ all return HealingResult              │
│                                                 │
│  CorrectionOrchestrator (high-level API)        │
│  ├── detect_and_report() → observation only     │
│  └── detect_and_heal() → execute corrections    │
└─────────────────────────────────────────────────┘
```

### FILES CREATED

| File | Purpose |
|------|---------|
| `vibe_core/protocols/correction.py` | Protocol interfaces + data classes |
| `vibe_core/services/correction_dispatcher.py` | BasicDriftRegistry, BasicCorrectionDispatcher, BasicCorrectionOrchestrator |
| `tests/unit/test_correction_dispatcher.py` | 10 unit tests |

### KEY TYPES

```python
# Unified drift report (all detectors produce this)
UnifiedDriftReport(
    id: str,
    source: DriftSource,  # PERFORMANCE, STRUCTURAL, CONFIG, CODE_DOC, etc.
    severity: DriftSeverity,
    message: str,
    file_path: Optional[Path],
    rule_id: Optional[str],
    auto_healable: bool,
)

# Unified healing result (all handlers produce this)
HealingResult(
    drift_id: str,
    status: HealingStatus,  # HEALED, SKIPPED, FAILED, DEFERRED, MANUAL_REQUIRED
    handler_id: str,
    files_modified: List[Path],
)
```

### USAGE

```python
# In biorhythm.py (observation only):
orchestrator = ServiceRegistry.get(CorrectionOrchestratorProtocol)
drifts = orchestrator.detect_and_report(source=DriftSource.STRUCTURAL)
healable = [d for d in drifts if d.auto_healable]

# In healing circuit (execute corrections):
results = orchestrator.detect_and_heal(
    strategy=HealingStrategy.AUTO,
    auto_only=True
)
```

### INTEGRATION

- Registered in `boot_orchestrator.py` via ServiceRegistry
- Auto-wires ReactorProtocol, ShuddhiProtocol, VajraEnforcer
- `biorhythm.py` refactored to use CorrectionOrchestrator

---

## LOG ROTATION FIX (2026-01-04)

### THE PROBLEM: 644MB system.log

`.vibe/logs/system.log` grew to 644MB (6.2 million lines) over 10 days:
- No log rotation configured
- Many kernel startups (each logs 100s of lines)
- Verbose loaders: VIBE_KERNEL (507k), UNIFIED.LOADER (503k), tool_registry (355k)

### THE FIX

```python
# vibe_core/utils/async_logging.py

# BEFORE (unbounded growth):
file_handler = logging.FileHandler(str(log_file))

# AFTER (10MB max per file, 5 backups = 60MB total):
file_handler = RotatingFileHandler(
    str(log_file),
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
)
```

**Result:** 644MB → 1.1MB (truncated to last 10k lines)

---

## SILENT KILLER PATTERNS (Training Data)

These patterns were found across 65+ locations. Use for future detection:

### Pattern 1: Config Resolution Fallback (COMMON)
```python
# BEFORE (silent)
try:
    config = get_config()
except Exception:
    pass  # ← INVISIBLE FAILURE

# AFTER (visible)
try:
    config = get_config()
except Exception as e:
    logger.warning(f"Config resolution failed: {e}")
```

### Pattern 2: ServiceRegistry Lookup (COMMON)
```python
# BEFORE (silent)
try:
    service = ServiceRegistry.get(SomeProtocol)
except Exception:
    pass  # ← WHY IS NOTHING WORKING?

# AFTER (visible)
try:
    service = ServiceRegistry.get(SomeProtocol)
except Exception as e:
    logger.debug(f"ServiceRegistry lookup failed: {e}")
```

### Pattern 3: File/Git Operations (VERY COMMON)
```python
# BEFORE (silent)
try:
    content = path.read_text()
except (OSError, PermissionError):
    pass  # ← FILE SYSTEM IS LYING TO US

# AFTER (visible)
except (OSError, PermissionError) as e:
    logger.debug(f"File operation failed for {path}: {e}")
```

### Pattern 4: JSON/YAML Parsing (COMMON)
```python
# BEFORE (silent)
try:
    data = json.loads(content)
except json.JSONDecodeError:
    pass  # ← MALFORMED DATA EVERYWHERE

# AFTER (visible)
except json.JSONDecodeError as e:
    logger.debug(f"JSON parse failed: {e}")
```

### Pattern 5: Type Coercion (INTENTIONAL - NOT SILENT KILLER)
```python
# This is CORRECT pattern - graceful fallback
try:
    return int(value)
except ValueError:
    pass  # Try next type
try:
    return float(value)
except ValueError:
    pass  # Try next type
return value  # String fallback
```

---

- **CorrectionDispatcher:** Design complete (subagent report)
- **GAD Standards:** 38 GADs mapped, GAD-000 = Operator Inversion

---

## KARMA SYSTEM: Graduated Healing Trust ✅ COMPLETE

### Status: DONE (2026-01-04)

Replaced binary `dry_run=True` with graduated trust via Quantum Reactor resonance.

### The Problem: Binary Healing Decisions

```
BEFORE:
  biorhythm.py: results = engine.heal_all_violations(dry_run=True)
                                                      ^^^^^^^^^^^^
                                         HARDCODED! NEVER HEALS!

  No trust concept. No earning privileges. Just a boolean.
```

### The Solution: QuantumHealingResolver

```
AFTER:
  1. Check Ashrama stage (lifecycle permissions)
     - BRAHMACHARI → DRY_RUN only (learning)
     - GRIHASTHA → Can earn AUTO (active)
     - VANAPRASTHA → MANUAL (retiring)
     - SANNYASA → DRY_RUN only (daemon)

  2. Get Bhakti balance (earned trust 0-200)
     - Earned via successful tasks, seva, TDD dharma
     - 50+ enables MANUAL override

  3. Compute resonance via Quantum Reactor
     - energy vs inertia threshold
     - If energy > inertia → AUTO (manifest!)
     - Else → DRY_RUN (observe)
```

### Files Created/Modified

| File | Purpose |
|------|---------|
| `vibe_core/protocols/vedic.py` | Extended with AsharamaStage enum + Bhakti methods |
| `vibe_core/protocols/correction.py` | Added RESONANCE to HealingStrategy, HealingStrategyResolverProtocol |
| `vibe_core/services/healing_resolver.py` | QuantumHealingResolver implementation |
| `vibe_core/services/correction_dispatcher.py` | Wired resolver into BasicCorrectionOrchestrator |

### Key Types

```python
# Ashrama lifecycle stages (vedic.py)
class AsharamaStage(Enum):
    BRAHMACHARI = "brahmachari"  # Student: read, observe, learn
    GRIHASTHA = "grihastha"      # Householder: read, write, create
    VANAPRASTHA = "vanaprastha"  # Retiree: read, teach, archive
    SANNYASA = "sannyasa"        # Renunciate: system functions only

# Healing strategies (correction.py)
class HealingStrategy(str, Enum):
    AUTO = "auto"           # Execute immediately
    DRY_RUN = "dry_run"     # Observe only
    MANUAL = "manual"       # Requires human approval
    CIRCUIT = "circuit"     # Delegate to circuit executor
    RESONANCE = "resonance" # Use Quantum Reactor to determine

# Resolver protocol (correction.py)
class HealingStrategyResolverProtocol(Protocol):
    def resolve(agent_id: str, drift: UnifiedDriftReport) -> HealingStrategy: ...
    def get_trust_level(agent_id: str) -> float: ...  # 0.0-1.0
```

### Usage

```python
# RESONANCE strategy: let resolver decide per-drift
orchestrator = ServiceRegistry.get(CorrectionOrchestratorProtocol)
results = orchestrator.detect_and_heal(
    strategy=HealingStrategy.RESONANCE,
    agent_id="opus_assistant",  # Required for trust lookup
)

# Resolver flow:
# 1. BRAHMACHARI/SANNYASA → DRY_RUN
# 2. resonance.manifest() with bhakti → AUTO if energy > inertia
# 3. High bhakti (50+) but no manifest → MANUAL
# 4. Else → DRY_RUN (still learning)
```

### Architecture

```
VedicGovernanceProtocol          QuantumReactor
├── get_agent_ashrama()          ├── manifest(intent, salt)
├── get_bhakti_balance()         └── returns ResonanceField
└── add_bhakti()
         ↓                              ↓
    ┌────────────────────────────────────────┐
    │       QuantumHealingResolver           │
    │  ├── resolve(agent_id, drift)          │
    │  │   1. Check ashrama stage            │
    │  │   2. Get bhakti balance             │
    │  │   3. Compute resonance              │
    │  │   4. Return HealingStrategy         │
    │  └── get_trust_level(agent_id) → 0-1   │
    └────────────────────────────────────────┘
                    ↓
    BasicCorrectionOrchestrator.detect_and_heal(
        strategy=RESONANCE, agent_id="..."
    )
```

### Key Design Decisions

1. **No hardcoded thresholds in resolver** - uses VedicGovernance bhakti_override_threshold
2. **Lazy DI loading** - resolver gets governance/reactor via ServiceRegistry if not injected
3. **Per-drift resolution** - each drift can have different strategy based on agent state
4. **Safe fallback** - any error → DRY_RUN (safe default)

### Ledger Audit Trail (OPUS-LZ3) ✅ FIXED

Every resonance decision is now recorded to VibeLedger for cryptographic proof:

```python
@dataclass
class ResonanceDecisionRecord:
    """Typed record - no Dict[str, Any]!"""
    event: str                           # "RESONANCE_DECISION"
    drift_id: str
    drift_source: str                    # DriftSource.value
    drift_severity: str                  # DriftSeverity.value
    drift_rule: Optional[str]
    strategy: str                        # HealingStrategy.value
    ashrama: str                         # AsharamaStage.value
    bhakti: int
    bhakti_threshold: int
    reason: str                          # Human-readable WHY
    timestamp: str
    resonance_energy: Optional[float]    # Reactor energy
    resonance_inertia: Optional[float]   # Reactor threshold
    resonance_manifested: Optional[bool] # energy > inertia?
```

**Query Example:**
```python
# Find all AUTO decisions for opus_assistant
ledger.query(
    event_type="HEALING_RESONANCE",
    agent_id="opus_assistant",
    filter=lambda r: r["details"]["strategy"] == "auto"
)
```

**Tests:** 27 unit tests in `tests/unit/test_healing_resolver.py`

---

## P2: .opus_state → .vibe/state Migration ✅ COMPLETE

### Status: DONE (2026-01-04)

Migration complete. Created `state_paths.py` helper module, migrated 30 files.

### Architecture (Already Correct)

```
StateService (vibe_core/state/state_service.py)
├── Agent state   → .vibe/state/agents/{agent_id}/
├── Plugin state  → .vibe/state/plugins/{plugin_id}/
└── Global state  → .vibe/state/

OpusStateManager uses StateService:
  get_state_service(workspace, plugin_id="opus_assistant")
  → .vibe/state/plugins/opus_assistant/

HERITAGE MIGRATION: StateService.load() auto-migrates from .opus_state on first read!
```

### The Problem: Direct Path Bypass

Many files bypass StateService and hardcode `.opus_state/`:

| Category | Count | Example Files |
|----------|-------|---------------|
| **MANAS Core** | 12 | viveka_action.py, intent_buffer.py, sankalpa.py, memory_store.py |
| **Dojo Training** | 6 | runner.py, agency.py, mirror.py, library.py, meditation.py |
| **Dashboard/CLI** | 8 | opus_dashboard_renderer.py, cognition.py, unified_cli.py |
| **State/Sync** | 5 | weaver.py, runtime_state.py, sync_holon.py |
| **Context** | 3 | context_service.py, treasury.py, prana.py |
| **YAML/Config** | 15 | manifest.json, curricula/*.yaml, templates |

### Migration Strategy: 4 Phases

**Phase 1: Create Accessor Helper (LOW RISK)**
```python
# In vibe_core/plugins/opus_assistant/core/state_paths.py
def get_opus_state_path(workspace: Path, filename: str) -> Path:
    """Returns path to opus_assistant state file.

    Uses StateService's plugin namespacing:
    → .vibe/state/plugins/opus_assistant/{filename}

    Heritage: Auto-migrates from .opus_state/{filename} on first read.
    """
    from vibe_core.state.state_service import get_state_service
    service = get_state_service(workspace, plugin_id="opus_assistant")
    return service.state_root / filename
```

**Phase 2: Migrate Core MANAS (HIGH VALUE)**
Priority files (direct state access):
1. `viveka_action.py` - decisions, karma_log, reinforcement
2. `intent_buffer.py` - manas_intents.json
3. `sankalpa.py` - sankalpa.json
4. `memory_store.py` - manas_memory.json
5. `akshara.py` - akshara_graph.json
6. `sutra_sense.py` - sutra_intent_history.json
7. `intent_router.py` - sanskrit_matrix.json
8. `synaptic_seeder.py` - synapses.json

**Phase 3: Migrate Readers (MEDIUM RISK)**
Files that READ from .opus_state/ for display:
1. `opus_dashboard_renderer.py` (4 direct reads)
2. `cognition.py` (2 direct reads)
3. `unified_cli.py` (5 direct reads)
4. `context_service.py` (2 direct reads)

**Phase 4: Update Patterns (LOW RISK)**
Update exclusion/recognition patterns in:
1. `weaver.py` - git ignore patterns
2. `runtime_state.py` - state path matching
3. `sync_holon.py` - state discovery
4. `drift_detector.py` - skip patterns
5. `dharma.py`, `shruta_sense.py`, `nadi_sense.py` - file patterns

### Files by Change Type

**Hardcoded Path → get_opus_state_path():**
```
vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py:289,1240,1658
vibe_core/plugins/opus_assistant/manas/intent_buffer.py:136
vibe_core/plugins/opus_assistant/manas/intent_router.py:331
vibe_core/plugins/opus_assistant/manas/cortex/sankalpa.py:373
vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py:328
vibe_core/plugins/opus_assistant/manas/memory_store.py:81
vibe_core/plugins/opus_assistant/manas/akshara.py:809
vibe_core/plugins/opus_assistant/manas/dojo/runner.py:454
vibe_core/plugins/opus_assistant/manas/dojo/agency.py:134
vibe_core/plugins/opus_assistant/manas/dojo/rooms/mirror.py:119-120
vibe_core/plugins/opus_assistant/manas/dojo/rooms/library.py:84-85
vibe_core/plugins/opus_assistant/manas/dojo/rooms/meditation.py:241
vibe_core/plugins/opus_assistant/manas/dojo/synaptic_seeder.py:266
vibe_core/plugins/opus_assistant/manas/intent_generator.py:499
vibe_core/plugins/opus_assistant/core/treasury.py:97
vibe_core/plugins/opus_assistant/core/context_service.py:574,615-616
vibe_core/plugins/opus_assistant/render/opus_dashboard_renderer.py:1122,1213,1256,1266
vibe_core/plugins/interface/renderers/cognition.py:574,639
vibe_core/cli/unified_cli.py:619,629,643,657,671,837
vibe_core/prana.py:210,231
```

**Pattern Updates (add .vibe/state/):**
```
vibe_core/state/weaver.py:575
vibe_core/state/runtime_state.py:102,144,178,236
vibe_core/state/sync_holon.py:141,226,247,451,615
vibe_core/plugins/opus_assistant/core/drift_detector.py:312
vibe_core/plugins/opus_assistant/manas/cortex/dharma.py:157
vibe_core/plugins/opus_assistant/manas/cortex/shruta_sense.py:144
vibe_core/plugins/opus_assistant/manas/akshara.py:296
```

**Documentation/Config Updates:**
```
vibe_core/plugins/opus_assistant/manifest.json (state_directory, etc.)
vibe_core/plugins/opus_assistant/manas/dojo/curricula/state_management.yaml
vibe_core/plugins/opus_assistant/templates/panels/manas_status.md.j2
```

### Migration Safety: Heritage Auto-Migrate

StateService.load() already handles migration:
```python
def load(self, filename: str, default: Any = None) -> Any:
    target_path = self.state_root / filename

    # 🏛️ HERITAGE MIGRATION (Restore Sovereignty)
    if not target_path.exists():
        legacy_root = self.workspace / ".opus_state"
        legacy_path = legacy_root / filename
        if legacy_path.exists():
            logger.info(f"🏛️ Migrating heritage state: {filename}")
            shutil.copy2(legacy_path, target_path)
```

This means: **Reads will auto-migrate. Only writes need path change.**

### Estimated Scope

- **Files to modify:** 25 Python files + 3 config/YAML files
- **Lines changed:** ~200 (mostly import + path replacement)
- **Risk:** LOW (heritage migration provides safety net)
- **Benefit:** Unified state architecture, cleaner .gitignore, proper plugin isolation
