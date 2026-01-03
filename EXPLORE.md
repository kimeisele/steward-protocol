# EXPLORE.md - System Introspection Map

> **Purpose:** Living document. Maps what EXISTS vs what WORKS.
> **Philosophy:** The system must understand itself before it can heal itself.
> **Updates:** Every analysis session adds findings. Nothing is lost.

---

## CRITICAL RISKS (P0)

### 1. VFS ORPHANED - No Sandbox
```
File: vibe_core/vfs.py
Status: EXISTS, IMPORTED, but NOT ENFORCED
Risk: Agents write DIRECTLY to host filesystem
Impact: rm -rf / has no guard

FIX APPLIED (2026-01-03):
  - file_tools.py: ReadFileTool/WriteFileTool now DENY without VFS
  - Agents without VFS get "SANDBOX REQUIRED" error
  - Only allow_unrestricted=True (kernel/admin) bypasses
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
| State Paths | 40+ hardcoded `.opus_state/` references |
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
LEGACY:   .opus_state/ (40+ hardcoded refs)
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

Gap: dry_run=True always (biorhythm.py:454)
Gap: Parsers not imported (loop can't ingest)
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

## CHANGELOG

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
