# 🔥 DER TOTALE KRIEG - LEVEL 1 DIMENSION 2
## GEMINI DEEP DIVE MISSION

**Status**: Level 1 Dimension 1 (Strukturkonsolidierung) COMPLETE
**Mission**: Dimension 2 - Dead Code Elimination & Dependency Analysis

---

## 📊 CODEBASE METRICS

```
Total Lines of Code: 94,345
Total Python Files: 200+
System Agents: 17
City Agents: 13
Kernel Size: ~2,500 LOC
Cortex Engines: 3 (Semantic, Circuit, Reflex)
```

---

## 🎯 DEINE MISSION, GEMINI

Analysiere das GESAMTE Repository und liefere:

### 1. DEAD CODE REPORT
Finde ALLE:
- Funktionen die nie aufgerufen werden
- Klassen die nie instanziiert werden
- Imports die nie benutzt werden
- Dateien die von nichts importiert werden
- Variablen die assigned aber nie gelesen werden

### 2. CIRCULAR DEPENDENCY MAP
Finde ALLE Import-Zyklen:
```
A imports B
B imports C
C imports A  ← ZYKLUS!
```

### 3. MISSING IMPLEMENTATIONS
Finde ALLE:
- `pass` statements in Methoden
- `TODO` / `FIXME` Kommentare
- `NotImplementedError` raises
- Leere `__init__.py` die exports haben sollten
- Abstract methods ohne concrete implementation

### 4. ARCHITECTURE VIOLATIONS
Prüfe gegen das CODE/CONFIG/RUNTIME Pattern:
- CODE: `vibe_core/` - Nur Python, immutable
- CONFIG: `knowledge/` - Nur YAML, Git-tracked
- RUNTIME: `data/` - DBs, gitignored

Violations:
- Hardcoded paths zu `data/` in CODE?
- Config in Python statt YAML?
- Runtime state in Git?

### 5. SECURITY AUDIT
- Agents ohne `oath_sworn = True`?
- Unsigned manifests?
- Missing permission checks?
- SQL injection vectors?
- Path traversal risks?

### 6. ORPHANED TESTS
- Tests für gelöschte Dateien?
- Mocked imports die nicht mehr existieren?
- Test fixtures mit alten Pfaden?

---

## 📁 DIRECTORY STRUCTURE TO ANALYZE

```
vibe_core/
├── cartridges/
│   ├── system/           # 17 system agents
│   │   ├── archivist/    # Ledger & audit
│   │   ├── auditor/      # Constitutional compliance
│   │   ├── chronicle/    # Git operations
│   │   ├── civic/        # Economy & lifecycle
│   │   ├── discoverer/   # Agent discovery
│   │   ├── engineer/     # Agent builder
│   │   ├── envoy/        # Orchestrator (MAIN)
│   │   ├── forum/        # Debate & consensus
│   │   ├── herald/       # Content & research
│   │   ├── oracle/       # Introspection
│   │   ├── ping/         # Health checks
│   │   ├── science/      # Web search
│   │   ├── scribe/       # Documentation
│   │   ├── supreme_court/# Appeals & precedent
│   │   └── watchman/     # Standards enforcement
│   └── agent_city/       # 13 city agents
│       ├── agora/        # Public forum
│       ├── ambassador/   # External comms
│       ├── analyst/      # Code analysis
│       ├── artisan/      # Media creation
│       ├── dhruva/       # Truth & ethics
│       ├── lens/         # Observation
│       ├── librarian/    # Knowledge management
│       ├── market/       # Trading
│       ├── marketer/     # Marketing content
│       ├── mechanic/     # Code repair
│       ├── pulse/        # Metrics
│       └── temple/       # Rituals
├── cortex/
│   └── engines/
│       ├── circuit_engine.py   # Playbook execution
│       ├── semantic_engine.py  # Intent routing
│       └── reflex_engine.py    # Fast reactions
├── plugins/
│   ├── interface/        # Renderers (ENVOY.md etc)
│   ├── steward_protocol/ # Main protocol plugin
│   └── test_orchestration/
├── loaders/
│   ├── base.py           # UnifiedLoader
│   └── schema.py         # Manifest validation
├── kernel_impl.py        # THE KERNEL (~2500 LOC)
├── boot_orchestrator.py  # Startup sequence
├── topology.py           # Agent graph
└── tool_discovery.py     # Tool scanning
```

---

## 🔍 SPECIFIC FILES TO DEEP-ANALYZE

### KERNEL (Most Critical)
- `vibe_core/kernel_impl.py` - Is every method used?
- `vibe_core/boot_orchestrator.py` - Startup sequence complete?

### CORTEX (Brain)
- `vibe_core/cortex/engines/circuit_engine.py` (1378 LOC) - Dead paths?
- `vibe_core/cortex/engines/semantic_engine.py` - Knowledge paths correct?

### LOADERS (Discovery)
- `vibe_core/steward/loader.py` - AgentLoader complete?
- `vibe_core/loaders/base.py` - UnifiedLoader used everywhere?

### PROVIDER (Universal Interface)
- `vibe_core/cartridges/system/envoy/provider.py` - All providers work?
- `vibe_core/operator_adapter.py` - Adapter pattern correct?

---

## ⚔️ DER FRAKTALE KRIEG - DIMENSIONS MAP

```
LEVEL 1: CODE QUALITY
├── Dimension 1: Structure Consolidation ✅ DONE
├── Dimension 2: Dead Code Elimination ← YOU ARE HERE
├── Dimension 3: Dependency Graph Optimization
├── Dimension 4: Import Cleanup
└── Dimension 5: Type Annotations

LEVEL 2: TEST COVERAGE
├── Dimension 1: Unit Test Gaps
├── Dimension 2: Integration Test Gaps
├── Dimension 3: E2E Test Scenarios
└── Dimension 4: Fuzzing & Edge Cases

LEVEL 3: SECURITY
├── Dimension 1: Oath System Audit
├── Dimension 2: Permission Model
├── Dimension 3: Crypto Verification
└── Dimension 4: Injection Prevention

LEVEL 4: PERFORMANCE
├── Dimension 1: Startup Time
├── Dimension 2: Memory Usage
├── Dimension 3: Concurrency Model
└── Dimension 4: Database Optimization

LEVEL 5: FEDERATION
├── Dimension 1: Protocol Spec
├── Dimension 2: Discovery Service
├── Dimension 3: Cross-City Communication
└── Dimension 4: Economic Settlement
```

---

## 📋 OUTPUT FORMAT

Liefere deinen Report in diesem Format:

```markdown
# GEMINI ANALYSIS REPORT

## 1. DEAD CODE FOUND
| File | Line | Type | Code |
|------|------|------|------|
| path/to/file.py | 123 | unused_function | def never_called(): |

## 2. CIRCULAR DEPENDENCIES
- Cycle 1: A → B → C → A
- Cycle 2: X → Y → X

## 3. MISSING IMPLEMENTATIONS
| File | Line | Issue |
|------|------|-------|
| file.py | 45 | TODO: implement caching |

## 4. ARCHITECTURE VIOLATIONS
| File | Line | Violation |
|------|------|-----------|
| file.py | 89 | Hardcoded path to data/ |

## 5. SECURITY ISSUES
| Severity | File | Issue |
|----------|------|-------|
| HIGH | file.py | No oath verification |

## 6. RECOMMENDED DELETIONS
Files safe to delete:
- path/to/unused.py (0 imports)

## 7. PRIORITY FIX LIST
1. [HIGH] Fix X because Y
2. [MED] Refactor Z
3. [LOW] Cleanup W
```

---

## 🚀 GO GEMINI GO

Du hast Zugriff auf das GESAMTE Repository.
Scan ALLES. Miss ALLES. Report ALLES.

Wir brauchen eine VOLLSTÄNDIGE Analyse für die nächste Schlacht.

**TOTALER KRIEG. KEINE GNADE. KEIN TOTES CODE ÜBERLEBT.**

---

## 📊 RAW DATA APPENDIX

### A. ALL PYTHON FILES IN VIBE_CORE
```
vibe_core/__init__.py
vibe_core/agent_interface.py
vibe_core/agent_protocol.py
vibe_core/agents/__init__.py
vibe_core/agents/context_aware_agent.py
vibe_core/agents/llm_agent.py
vibe_core/agents/specialist_agent.py
vibe_core/agents/specialist_factory.py
vibe_core/agents/system_maintenance.py
vibe_core/boot_orchestrator.py
vibe_core/bridge.py
vibe_core/capability_registry.py
vibe_core/cartridges/__init__.py
vibe_core/cartridges/agent_city/__init__.py
vibe_core/cartridges/agent_city/agora/__init__.py
vibe_core/cartridges/agent_city/agora/cartridge_main.py
vibe_core/cartridges/agent_city/ambassador/__init__.py
vibe_core/cartridges/agent_city/ambassador/cartridge_main.py
vibe_core/cartridges/agent_city/analyst/__init__.py
vibe_core/cartridges/agent_city/analyst/cartridge_main.py
vibe_core/cartridges/agent_city/analyst/tools/__init__.py
vibe_core/cartridges/agent_city/analyst/tools/architecture_tool.py
vibe_core/cartridges/agent_city/analyst/tools/code_tool.py
vibe_core/cartridges/agent_city/analyst/tools/deps_tool.py
vibe_core/cartridges/agent_city/analyst/tools/docs_tool.py
vibe_core/cartridges/agent_city/analyst/tools/git_tool.py
vibe_core/cartridges/agent_city/analyst/tools/structure_tool.py
vibe_core/cartridges/agent_city/artisan/__init__.py
vibe_core/cartridges/agent_city/artisan/cartridge_main.py
vibe_core/cartridges/agent_city/artisan/tools/__init__.py
vibe_core/cartridges/agent_city/artisan/tools/media_tool.py
vibe_core/cartridges/agent_city/dhruva/__init__.py
vibe_core/cartridges/agent_city/dhruva/cartridge_main.py
vibe_core/cartridges/agent_city/dhruva/tools/__init__.py
vibe_core/cartridges/agent_city/dhruva/tools/data_ethics.py
vibe_core/cartridges/agent_city/dhruva/tools/genesis_keeper.py
vibe_core/cartridges/agent_city/dhruva/tools/reference_resolver.py
vibe_core/cartridges/agent_city/dhruva/tools/truth_matrix.py
vibe_core/cartridges/agent_city/lens/__init__.py
vibe_core/cartridges/agent_city/lens/cartridge_main.py
vibe_core/cartridges/agent_city/librarian/cartridge_main.py
vibe_core/cartridges/agent_city/librarian/tools/__init__.py
vibe_core/cartridges/agent_city/librarian/tools/catalog_tool.py
vibe_core/cartridges/agent_city/librarian/tools/recommend_tool.py
vibe_core/cartridges/agent_city/librarian/tools/search_tool.py
vibe_core/cartridges/agent_city/market/__init__.py
vibe_core/cartridges/agent_city/market/cartridge_main.py
vibe_core/cartridges/agent_city/marketer/cartridge_main.py
vibe_core/cartridges/agent_city/marketer/tools/__init__.py
vibe_core/cartridges/agent_city/marketer/tools/marketer_content_tool.py
vibe_core/cartridges/agent_city/mechanic/__init__.py
vibe_core/cartridges/agent_city/mechanic/cartridge_main.py
vibe_core/cartridges/agent_city/mechanic/tools/__init__.py
vibe_core/cartridges/agent_city/mechanic/tools/tidy_tool.py
vibe_core/cartridges/agent_city/pulse/__init__.py
vibe_core/cartridges/agent_city/pulse/cartridge_main.py
vibe_core/cartridges/agent_city/temple/__init__.py
vibe_core/cartridges/agent_city/temple/cartridge_main.py
vibe_core/cartridges/agent_city/temple/offering.py
vibe_core/cartridges/base.py
vibe_core/cartridges/registry.py
vibe_core/cartridges/system/__init__.py
vibe_core/cartridges/system/archivist/__init__.py
vibe_core/cartridges/system/archivist/cartridge_main.py
vibe_core/cartridges/system/archivist/core/__init__.py
vibe_core/cartridges/system/archivist/tools/__init__.py
vibe_core/cartridges/system/archivist/tools/audit_tool.py
vibe_core/cartridges/system/archivist/tools/ledger.py
vibe_core/cartridges/system/archivist/tools/ledger_tool.py
vibe_core/cartridges/system/archivist/tools/ledger_visualizer.py
vibe_core/cartridges/system/archivist/tools/observer_tool.py
vibe_core/cartridges/system/archivist/tools/verifier_tool.py
vibe_core/cartridges/system/auditor/__init__.py
vibe_core/cartridges/system/auditor/cartridge_main.py
vibe_core/cartridges/system/auditor/tools/__init__.py
vibe_core/cartridges/system/auditor/tools/compliance_tool.py
vibe_core/cartridges/system/auditor/tools/constitutional_verdict.py
vibe_core/cartridges/system/auditor/tools/invariant_tool.py
vibe_core/cartridges/system/auditor/tools/watchdog_tool.py
vibe_core/cartridges/system/chronicle/__init__.py
vibe_core/cartridges/system/chronicle/cartridge_main.py
vibe_core/cartridges/system/chronicle/tools/__init__.py
vibe_core/cartridges/system/chronicle/tools/git_tools.py
vibe_core/cartridges/system/civic/__init__.py
vibe_core/cartridges/system/civic/cartridge_main.py
vibe_core/cartridges/system/civic/economy_agent.py
vibe_core/cartridges/system/civic/lifecycle_agent.py
vibe_core/cartridges/system/civic/registry_agent.py
vibe_core/cartridges/system/civic/tools/__init__.py
vibe_core/cartridges/system/civic/tools/bank_tool.py
vibe_core/cartridges/system/civic/tools/dashboard_tool.py
vibe_core/cartridges/system/civic/tools/economy.py
vibe_core/cartridges/system/civic/tools/ledger_tool.py
vibe_core/cartridges/system/civic/tools/license_tool.py
vibe_core/cartridges/system/civic/tools/lifecycle_enforcer.py
vibe_core/cartridges/system/civic/tools/lifecycle_manager.py
vibe_core/cartridges/system/civic/tools/vault.py
vibe_core/cartridges/system/civic/tools/vault_tool.py
vibe_core/cartridges/system/discoverer/agent.py
vibe_core/cartridges/system/discoverer/cartridge_main.py
vibe_core/cartridges/system/engineer/__init__.py
vibe_core/cartridges/system/engineer/cartridge_main.py
vibe_core/cartridges/system/engineer/templates/agent/cartridge_main.py
vibe_core/cartridges/system/engineer/templates/agent/tools/__init__.py
vibe_core/cartridges/system/engineer/tools/__init__.py
vibe_core/cartridges/system/engineer/tools/builder_tool.py
vibe_core/cartridges/system/envoy/__init__.py
vibe_core/cartridges/system/envoy/action_handlers.py
vibe_core/cartridges/system/envoy/blueprint_generator.py
vibe_core/cartridges/system/envoy/cartridge_main.py
vibe_core/cartridges/system/envoy/deterministic_executor.py
vibe_core/cartridges/system/envoy/provider.py
vibe_core/cartridges/system/envoy/tools/__init__.py
vibe_core/cartridges/system/envoy/tools/city_control_tool.py
vibe_core/cartridges/system/envoy/tools/curator_tool.py
vibe_core/cartridges/system/envoy/tools/diplomacy_tool.py
vibe_core/cartridges/system/envoy/tools/gap_report_tool.py
vibe_core/cartridges/system/envoy/tools/hil_assistant_tool.py
vibe_core/cartridges/system/envoy/tools/milk_ocean.py
vibe_core/cartridges/system/envoy/tools/run_campaign_tool.py
vibe_core/cartridges/system/envoy/tools/wiring_audit_scripts.py
vibe_core/cartridges/system/forum/__init__.py
vibe_core/cartridges/system/forum/cartridge_main.py
vibe_core/cartridges/system/forum/tools/__init__.py
vibe_core/cartridges/system/herald/__init__.py
vibe_core/cartridges/system/herald/capabilities/__init__.py
vibe_core/cartridges/system/herald/capabilities/broadcast.py
vibe_core/cartridges/system/herald/capabilities/creative.py
vibe_core/cartridges/system/herald/capabilities/research.py
vibe_core/cartridges/system/herald/cartridge_main.py
vibe_core/cartridges/system/herald/cli.py
vibe_core/cartridges/system/herald/core/__init__.py
vibe_core/cartridges/system/herald/core/agency_director.py
vibe_core/cartridges/system/herald/core/memory.py
vibe_core/cartridges/system/herald/governance/__init__.py
vibe_core/cartridges/system/herald/governance/constitution.py
vibe_core/cartridges/system/herald/manifesto.py
vibe_core/cartridges/system/herald/tools/__init__.py
vibe_core/cartridges/system/herald/tools/broadcast_tool.py
vibe_core/cartridges/system/herald/tools/governance.py
vibe_core/cartridges/system/herald/tools/identity_tool.py
vibe_core/cartridges/system/herald/tools/research_tool.py
vibe_core/cartridges/system/herald/tools/scout_tool.py
vibe_core/cartridges/system/herald/tools/scout_tool_legacy.py
vibe_core/cartridges/system/herald/tools/scribe_tool.py
vibe_core/cartridges/system/herald/tools/visual_tool.py
vibe_core/cartridges/system/oracle/__init__.py
vibe_core/cartridges/system/oracle/cartridge_main.py
vibe_core/cartridges/system/oracle/tools/__init__.py
vibe_core/cartridges/system/oracle/tools/introspection_tool.py
vibe_core/cartridges/system/ping/__init__.py
vibe_core/cartridges/system/ping/cartridge_main.py
vibe_core/cartridges/system/science/__init__.py
vibe_core/cartridges/system/science/cartridge_main.py
vibe_core/cartridges/system/science/tools/__init__.py
vibe_core/cartridges/system/science/tools/web_search_tool.py
vibe_core/cartridges/system/scribe/__init__.py
vibe_core/cartridges/system/scribe/cartridge_main.py
vibe_core/cartridges/system/scribe/tools/__init__.py
vibe_core/cartridges/system/scribe/tools/agents_renderer.py
vibe_core/cartridges/system/scribe/tools/base.py
vibe_core/cartridges/system/scribe/tools/citymap_renderer.py
vibe_core/cartridges/system/scribe/tools/dashboard_renderer.py
vibe_core/cartridges/system/scribe/tools/help_renderer.py
vibe_core/cartridges/system/scribe/tools/index_renderer.py
vibe_core/cartridges/system/scribe/tools/introspector.py
vibe_core/cartridges/system/scribe/tools/operations_introspector.py
vibe_core/cartridges/system/scribe/tools/project_introspector.py
vibe_core/cartridges/system/scribe/tools/rag_renderer.py
vibe_core/cartridges/system/scribe/tools/readme_renderer.py
vibe_core/cartridges/system/scribe/tools/runtime_inspector.py
vibe_core/cartridges/system/scribe/tools/vibe_introspector.py
vibe_core/cartridges/system/supreme_court/__init__.py
vibe_core/cartridges/system/supreme_court/cartridge_main.py
vibe_core/cartridges/system/supreme_court/tools/__init__.py
vibe_core/cartridges/system/supreme_court/tools/appeals_tool.py
vibe_core/cartridges/system/supreme_court/tools/justice_ledger.py
vibe_core/cartridges/system/supreme_court/tools/precedent_tool.py
vibe_core/cartridges/system/supreme_court/tools/verdict_tool.py
vibe_core/cartridges/system/watchman/__init__.py
vibe_core/cartridges/system/watchman/cartridge_main.py
vibe_core/cartridges/system/watchman/tools/__init__.py
vibe_core/cartridges/system/watchman/tools/standards_inspection.py
vibe_core/cartridges/system/watchman/tools/system_health_check.py
vibe_core/circuit_executor.py
vibe_core/cli.py
vibe_core/config/__init__.py
vibe_core/config/schema.py
vibe_core/cortex/__init__.py
vibe_core/cortex/engines/__init__.py
vibe_core/cortex/engines/circuit_engine.py
vibe_core/cortex/engines/reflex_engine.py
vibe_core/cortex/engines/semantic_engine.py
vibe_core/cortex/protocols/__init__.py
vibe_core/dependency_manager.py
vibe_core/doc_renderer.py
vibe_core/envoy_sync.py
vibe_core/event_bus.py
vibe_core/file_operator.py
vibe_core/governance/__init__.py
vibe_core/governance/invariants.py
vibe_core/identity.py
vibe_core/io_service.py
vibe_core/kernel.py
vibe_core/kernel_impl.py
vibe_core/knowledge/__init__.py
vibe_core/knowledge/graph.py
vibe_core/knowledge/loader.py
vibe_core/knowledge/resolver.py
vibe_core/knowledge/schema.py
vibe_core/ledger.py
vibe_core/lineage.py
vibe_core/llm/__init__.py
vibe_core/llm/chain.py
vibe_core/llm/degradation_chain.py
vibe_core/llm/google_adapter.py
vibe_core/llm/human_provider.py
vibe_core/llm/local_llama_provider.py
vibe_core/llm/provider.py
vibe_core/llm/smart_local_provider.py
vibe_core/llm/steward_provider.py
vibe_core/loaders/__init__.py
vibe_core/loaders/base_loader.py
vibe_core/loaders/schema.py
vibe_core/markdown_ui_manager.py
vibe_core/narasimha.py
vibe_core/network_proxy.py
vibe_core/operator_adapter.py
vibe_core/phoenix/__init__.py
vibe_core/phoenix/config.py
vibe_core/phoenix/section_loader.py
vibe_core/phoenix/sections/__init__.py
vibe_core/phoenix/sections/city/section_main.py
vibe_core/phoenix/sections/kernel/section_main.py
vibe_core/phoenix/sections/quality/section_main.py
vibe_core/phoenix/sections/steward/section_main.py
vibe_core/phoenix/sections/test_governance/__init__.py
vibe_core/phoenix/sections/test_governance/section_main.py
vibe_core/phoenix/utils/__init__.py
vibe_core/phoenix/utils/circuits.py
vibe_core/phoenix/utils/routing.py
vibe_core/playbook/__init__.py
vibe_core/playbook/executor.py
vibe_core/playbook/loader.py
vibe_core/playbook/operations/__init__.py
vibe_core/playbook/operations/kernel_spawn.py
vibe_core/playbook/router.py
vibe_core/playbook/router_bridge.py
vibe_core/playbook/runner.py
vibe_core/plugin_loader.py
vibe_core/plugin_protocol.py
vibe_core/plugins/__init__.py
vibe_core/plugins/crypto/plugin_main.py
vibe_core/plugins/interface/__init__.py
vibe_core/plugins/interface/plugin_main.py
vibe_core/plugins/interface/renderers/__init__.py
vibe_core/plugins/interface/renderers/agents.py
vibe_core/plugins/interface/renderers/base.py
vibe_core/plugins/interface/renderers/citymap.py
vibe_core/plugins/interface/renderers/dashboard.py
vibe_core/plugins/interface/renderers/envoy.py
vibe_core/plugins/interface/renderers/ephemeral.py
vibe_core/plugins/interface/renderers/git.py
vibe_core/plugins/interface/renderers/help.py
vibe_core/plugins/interface/renderers/index.py
vibe_core/plugins/interface/renderers/operations.py
vibe_core/plugins/interface/renderers/proof.py
vibe_core/plugins/interface/renderers/rag.py
vibe_core/plugins/interface/renderers/settings.py
vibe_core/plugins/interface/renderers/tasks.py
vibe_core/plugins/plugin_template/__init__.py
vibe_core/plugins/plugin_template/plugin_main.py
vibe_core/plugins/sarga_cycle/plugin_main.py
vibe_core/plugins/steward_protocol/__init__.py
vibe_core/plugins/steward_protocol/plugin_main.py
vibe_core/plugins/test_mode/__init__.py
vibe_core/plugins/test_mode/plugin_main.py
vibe_core/plugins/test_orchestration/plugin_main.py
vibe_core/plugins/test_orchestration/test_guardian.py
vibe_core/plugins/vedic_governance/plugin_main.py
vibe_core/process_manager.py
vibe_core/protocols/__init__.py
vibe_core/protocols/agent.py
vibe_core/protocols/ledger.py
vibe_core/protocols/operator_protocol.py
vibe_core/protocols/registry.py
vibe_core/protocols/scheduler.py
vibe_core/protocols/testable.py
vibe_core/protocols/testable_registry.py
vibe_core/pulse.py
vibe_core/resource_manager.py
vibe_core/runtime/__init__.py
vibe_core/runtime/boot_sequence.py
vibe_core/runtime/circuit_breaker.py
vibe_core/runtime/context_loader.py
vibe_core/runtime/hud.py
vibe_core/runtime/interface.py
vibe_core/runtime/llm_client.py
vibe_core/runtime/llm_engine.py
vibe_core/runtime/oracle.py
vibe_core/runtime/playbook_router.py
vibe_core/runtime/project_memory.py
vibe_core/runtime/prompt_composer.py
vibe_core/runtime/prompt_context.py
vibe_core/runtime/prompt_registry.py
vibe_core/runtime/prompt_runtime.py
vibe_core/runtime/providers/__init__.py
vibe_core/runtime/providers/anthropic.py
vibe_core/runtime/providers/base.py
vibe_core/runtime/providers/factory.py
vibe_core/runtime/providers/google.py
vibe_core/runtime/quota_manager.py
vibe_core/runtime/semantic_actions.py
vibe_core/runtime/tool_safety_guard.py
vibe_core/sarga.py
vibe_core/scheduling/__init__.py
vibe_core/scheduling/task.py
vibe_core/scripts/__init__.py
vibe_core/semantic_syscalls.py
vibe_core/settings/__init__.py
vibe_core/settings/loader.py
vibe_core/settings/protocol.py
vibe_core/settings/sections/__init__.py
vibe_core/settings/sections/execution_mode.py
vibe_core/settings/sections/provider.py
vibe_core/settings_executor.py
vibe_core/settings_sync.py
vibe_core/specialists/__init__.py
vibe_core/specialists/base_agent.py
vibe_core/specialists/base_specialist.py
vibe_core/specialists/registry.py
vibe_core/steward/__init__.py
vibe_core/steward/constitution.py
vibe_core/steward/loader.py
vibe_core/steward/oath_mixin.py
vibe_core/steward/protocol.py
vibe_core/store/__init__.py
vibe_core/store/sqlite_store.py
vibe_core/task_management/__init__.py
vibe_core/task_management/archive.py
vibe_core/task_management/batch_operations.py
vibe_core/task_management/export_engine.py
vibe_core/task_management/file_lock.py
vibe_core/task_management/metrics.py
vibe_core/task_management/models.py
vibe_core/task_management/next_task_generator.py
vibe_core/task_management/task_manager.py
vibe_core/task_management/validator_registry.py
vibe_core/tool_discovery.py
vibe_core/tools/__init__.py
vibe_core/tools/agenda_tools.py
vibe_core/tools/delegate_tool.py
vibe_core/tools/file_tools.py
vibe_core/tools/inspect_result.py
vibe_core/tools/list_directory.py
vibe_core/tools/search_file.py
vibe_core/tools/tool_protocol.py
vibe_core/tools/tool_registry.py
vibe_core/topology.py
vibe_core/vfs.py
```

### B. FILE SIZE RANKING (Top 30)
```
    1754 vibe_core/kernel_impl.py
    1640 vibe_core/store/sqlite_store.py
    1378 vibe_core/cortex/engines/circuit_engine.py
    1378 vibe_core/circuit_executor.py
    1123 vibe_core/cli.py
    1100 vibe_core/cartridges/system/envoy/deterministic_executor.py
     944 vibe_core/cartridges/system/envoy/tools/milk_ocean.py
     864 vibe_core/cartridges/system/envoy/blueprint_generator.py
     847 vibe_core/cartridges/system/envoy/provider.py
     820 vibe_core/cartridges/system/herald/cartridge_main.py
     811 vibe_core/semantic_syscalls.py
     803 vibe_core/agent_interface.py
     768 vibe_core/cartridges/agent_city/mechanic/cartridge_main.py
     755 vibe_core/plugins/interface/renderers/git.py
     753 vibe_core/protocols/testable.py
     743 vibe_core/doc_renderer.py
     734 vibe_core/cartridges/system/civic/tools/license_tool.py
     729 vibe_core/playbook/executor.py
     721 vibe_core/plugins/steward_protocol/plugin_main.py
     711 vibe_core/runtime/prompt_context.py
     679 vibe_core/cartridges/system/forum/cartridge_main.py
     677 vibe_core/cartridges/system/auditor/tools/invariant_tool.py
     675 vibe_core/runtime/prompt_registry.py
     666 vibe_core/cartridges/system/supreme_court/cartridge_main.py
     665 vibe_core/runtime/prompt_runtime.py
     661 vibe_core/task_management/task_manager.py
     640 vibe_core/specialists/base_agent.py
     635 vibe_core/cartridges/system/civic/tools/ledger_tool.py
     619 vibe_core/topology.py
     613 vibe_core/cartridges/system/envoy/tools/run_campaign_tool.py
```

### C. IMPORT GRAPH (Who imports what)
```
  48 from vibe_core.tools.tool_protocol import Tool, ToolResult
  24 from vibe_core.steward import OathMixin
  16 from vibe_core import Task, VibeAgent
   9 from vibe_core.plugin_protocol import KernelPlugin
   8 from vibe_core.config import CityConfig
   7 from vibe_core.scheduling.task import Task
   7 from vibe_core.cartridges.system.scribe.tools.base import (
   6 from vibe_core.scheduling import Task
   5 from vibe_core.llm.provider import LLMProvider
   4 from vibe_core.store.sqlite_store import SQLiteStore
   4 from vibe_core.protocols import VibeAgent
   4 from vibe_core.protocols import AgentManifest, VibeAgent
   3 from vibe_core.protocols.operator_protocol import (
   3 from vibe_core.protocols import AgentResponse, VibeAgent
   3 from vibe_core.protocols import AgentManifest
   3 from vibe_core.cartridges.system.scribe.tools.introspector import CartridgeIntrospector
   3 from vibe_core import Task
   2 from vibe_core.tools.tool_protocol import Tool, ToolCall, ToolResult
   2 from vibe_core.steward.constitution import ConstitutionalOath
   2 from vibe_core.semantic_syscalls import (
   2 from vibe_core.runtime.tool_safety_guard import ToolSafetyGuard
   2 from vibe_core.runtime.prompt_context import get_prompt_context
   2 from vibe_core.protocols.testable import (
   2 from vibe_core.protocols import VibeLedger
   2 from vibe_core.loaders import ItemMeta, LoaderRegistry, UnifiedLoader
   2 from vibe_core.llm.provider import LLMError, LLMProvider
   2 from vibe_core.cortex.engines.semantic_engine import (
   2 from vibe_core.cortex.engines.reflex_engine import ReflexEngine
   2 from vibe_core.cortex.engines.circuit_engine import (
   2 from vibe_core.config import CivicConfig
   2 from vibe_core.cartridges.system.scribe.tools.runtime_inspector import RuntimeInspector
   2 from vibe_core.cartridges.system.scribe.tools.operations_introspector import (
   2 from vibe_core.cartridges.system.envoy.blueprint_generator import (
   2 from vibe_core.cartridges.system.discoverer.agent import Discoverer
   2 from vibe_core.agents.context_aware_agent import ContextAwareAgent
   2 from vibe_core.agents import ContextAwareAgent
   2 from vibe_core.agent_protocol import VibeAgent
   1 from vibe_core.topology import get_agent_placement
   1 from vibe_core.tools.tool_registry import ToolRegistry
   1 from vibe_core.tools.tool_protocol import Tool
   1 from vibe_core.tools.file_tools import ReadFileTool, WriteFileTool
   1 from vibe_core.tools.delegate_tool import DelegateTool
   1 from vibe_core.tools.agenda_tools import AddTaskTool, CompleteTaskTool, ListTasksTool
   1 from vibe_core.task_management.task_manager import TaskManager
   1 from vibe_core.task_management.models import TaskStatus
   1 from vibe_core.steward.protocol import AgentManifest, is_valid_agent
   1 from vibe_core.steward.protocol import AgentManifest, AgentProtocol, is_valid_agent
   1 from vibe_core.steward.oath_mixin import OathMixin
   1 from vibe_core.steward.loader import AgentLoader, AgentMeta
   1 from vibe_core.steward import AgentLoader, ConstitutionalOath
```

### D. ALL CLASS DEFINITIONS
```
vibe_core/cartridges/registry.py:28:class CartridgeRegistry:
vibe_core/cartridges/system/ping/cartridge_main.py:17:class PingCartridge(ContextAwareAgent, OathMixin):
vibe_core/cartridges/system/civic/registry_agent.py:24:class RegistryAgent(VibeAgent):
vibe_core/cartridges/system/civic/tools/dashboard_tool.py:29:class DashboardMetrics:
vibe_core/cartridges/system/civic/tools/dashboard_tool.py:41:class DashboardGenerator:
vibe_core/cartridges/system/civic/tools/lifecycle_enforcer.py:37:class PermissionResult:
vibe_core/cartridges/system/civic/tools/lifecycle_enforcer.py:48:class LifecycleEnforcer(Tool):
vibe_core/cartridges/system/civic/tools/vault_tool.py:76:class VaultTool(Tool):
vibe_core/cartridges/system/civic/tools/economy.py:33:class InsufficientFundsError(Exception):
vibe_core/cartridges/system/civic/tools/economy.py:39:class CivicBank:
vibe_core/cartridges/system/civic/tools/lifecycle_manager.py:30:class LifecycleStatus(Enum):
vibe_core/cartridges/system/civic/tools/lifecycle_manager.py:50:class LifecycleState:
vibe_core/cartridges/system/civic/tools/lifecycle_manager.py:97:class LifecycleManager:
vibe_core/cartridges/system/civic/tools/bank_tool.py:32:class BankTool(Tool):
vibe_core/cartridges/system/civic/tools/vault.py:72:class VaultError(Exception):
vibe_core/cartridges/system/civic/tools/vault.py:78:class InsufficientFundsError(Exception):
vibe_core/cartridges/system/civic/tools/vault.py:84:class SecretNotFoundError(Exception):
vibe_core/cartridges/system/civic/tools/vault.py:90:class CivicVault:
vibe_core/cartridges/system/civic/tools/license_tool.py:37:class LicenseType(Enum):
vibe_core/cartridges/system/civic/tools/license_tool.py:46:class LicenseStatus(Enum):
vibe_core/cartridges/system/civic/tools/license_tool.py:55:class License:
vibe_core/cartridges/system/civic/tools/license_tool.py:129:class LicenseTool(Tool):
vibe_core/cartridges/system/civic/tools/license_tool.py:670:class LicenseAuthority:
vibe_core/cartridges/system/civic/tools/ledger_tool.py:26:class InsufficientFundsError(Exception):
vibe_core/cartridges/system/civic/tools/ledger_tool.py:33:class LedgerEntry:
vibe_core/cartridges/system/civic/tools/ledger_tool.py:54:class LedgerTool(Tool):
vibe_core/cartridges/system/civic/tools/ledger_tool.py:564:class AgentBank:
vibe_core/cartridges/system/civic/cartridge_main.py:50:class CivicSystemInterface:
vibe_core/cartridges/system/civic/cartridge_main.py:91:class CivicCartridge(VibeAgent, OathMixin):
vibe_core/cartridges/system/civic/lifecycle_agent.py:24:class LifecycleAgent(VibeAgent):
vibe_core/cartridges/system/civic/economy_agent.py:21:class EconomyAgent(VibeAgent):
vibe_core/cartridges/system/archivist/tools/ledger_visualizer.py:24:class LedgerVisualizer:
vibe_core/cartridges/system/archivist/tools/observer_tool.py:13:class ObserverTool:
vibe_core/cartridges/system/archivist/tools/ledger.py:21:class AuditLedger(VibeLedger):
vibe_core/cartridges/system/archivist/tools/audit_tool.py:14:class AuditTool:
vibe_core/cartridges/system/archivist/tools/ledger_tool.py:15:class LedgerTool:
vibe_core/cartridges/system/archivist/tools/verifier_tool.py:37:class VerifierTool:
vibe_core/cartridges/system/archivist/cartridge_main.py:32:class ArchivistCartridge(VibeAgent, OathMixin):
vibe_core/cartridges/system/discoverer/cartridge_main.py:28:class DiscovererCartridge(Discoverer):
vibe_core/cartridges/system/discoverer/agent.py:28:class Discoverer(VibeAgent):
vibe_core/cartridges/system/discoverer/agent.py:182:class GenericAgent(VibeAgent):
vibe_core/cartridges/system/supreme_court/tools/precedent_tool.py:27:class PrecedentCase:
vibe_core/cartridges/system/supreme_court/tools/precedent_tool.py:44:class PrecedentTool(Tool):
vibe_core/cartridges/system/supreme_court/tools/appeals_tool.py:27:class AppealStatus(str, Enum):
vibe_core/cartridges/system/supreme_court/tools/appeals_tool.py:37:class Appeal:
vibe_core/cartridges/system/supreme_court/tools/appeals_tool.py:56:class AppealsTool(Tool):
vibe_core/cartridges/system/supreme_court/tools/verdict_tool.py:27:class VerdictType(str, Enum):
vibe_core/cartridges/system/supreme_court/tools/verdict_tool.py:36:class Verdict:
vibe_core/cartridges/system/supreme_court/tools/verdict_tool.py:53:class VerdictTool(Tool):
vibe_core/cartridges/system/supreme_court/tools/justice_ledger.py:33:class JusticeLedger(VibeLedger, Tool):
vibe_core/cartridges/system/supreme_court/cartridge_main.py:49:class SupremeCourtCartridge(VibeAgent, OathMixin):
vibe_core/cartridges/system/oracle/tools/introspection_tool.py:28:class IntrospectionError(Exception):
vibe_core/cartridges/system/oracle/tools/introspection_tool.py:34:class IntrospectionTool(Tool):
vibe_core/cartridges/system/oracle/cartridge_main.py:36:class OracleCartridge(VibeAgent, OathMixin):
vibe_core/cartridges/system/science/tools/web_search_tool.py:36:class SearchResult:
vibe_core/cartridges/system/science/tools/web_search_tool.py:64:class WebSearchTool(Tool):
vibe_core/cartridges/system/science/cartridge_main.py:47:class ScientistCartridge(ContextAwareAgent, OathMixin):
vibe_core/cartridges/system/envoy/action_handlers.py:26:class ActionHandler(ABC):
vibe_core/cartridges/system/envoy/action_handlers.py:56:class ActionResult:
vibe_core/cartridges/system/envoy/action_handlers.py:78:class ActionContext:
vibe_core/cartridges/system/envoy/action_handlers.py:100:class ActionHandlerRegistry:
vibe_core/cartridges/system/envoy/action_handlers.py:142:class CheckStateHandler(ActionHandler):
vibe_core/cartridges/system/envoy/action_handlers.py:256:class ExecuteScriptHandler(ActionHandler):
vibe_core/cartridges/system/envoy/action_handlers.py:371:class EmitEventHandler(ActionHandler):
vibe_core/cartridges/system/envoy/action_handlers.py:418:class CallAgentHandler(ActionHandler):
vibe_core/cartridges/system/envoy/action_handlers.py:481:class CallPlaybookHandler(ActionHandler):
vibe_core/cartridges/system/envoy/tools/hil_assistant_tool.py:26:class HILAssistantTool(Tool):
vibe_core/cartridges/system/envoy/tools/run_campaign_tool.py:33:class CampaignPhase(Enum):
vibe_core/cartridges/system/envoy/tools/run_campaign_tool.py:43:class RunCampaignTool(Tool):
vibe_core/cartridges/system/envoy/tools/milk_ocean.py:48:class RequestPriority(str, Enum):
vibe_core/cartridges/system/envoy/tools/milk_ocean.py:58:class GateResult:
vibe_core/cartridges/system/envoy/tools/milk_ocean.py:75:class LazyQueue:
vibe_core/cartridges/system/envoy/tools/milk_ocean.py:304:class MilkOceanRouter:
vibe_core/cartridges/system/envoy/tools/gap_report_tool.py:28:class GAPReportTool(Tool):
vibe_core/cartridges/system/envoy/tools/wiring_audit_scripts.py:22:class WiringAuditor:
vibe_core/cartridges/system/envoy/tools/diplomacy_tool.py:21:class DiplomacyTool(Tool):
vibe_core/cartridges/system/envoy/tools/city_control_tool.py:66:class CityControlTool(Tool):
vibe_core/cartridges/system/envoy/tools/curator_tool.py:21:class CuratorTool(Tool):
vibe_core/cartridges/system/envoy/provider.py:72:class DeterministicRouter:
vibe_core/cartridges/system/envoy/provider.py:165:class IntentType(Enum):
vibe_core/cartridges/system/envoy/provider.py:174:class IntentVector:
vibe_core/cartridges/system/envoy/provider.py:184:class UniversalProvider:
vibe_core/cartridges/system/envoy/cartridge_main.py:51:class EnvoyCartridge(ContextAwareAgent, OathMixin):
vibe_core/cartridges/system/envoy/blueprint_generator.py:137:class CompilationResult:
vibe_core/cartridges/system/envoy/blueprint_generator.py:147:class BlueprintGenerator:
vibe_core/cartridges/system/envoy/deterministic_executor.py:79:class PhaseStatus(Enum):
vibe_core/cartridges/system/envoy/deterministic_executor.py:90:class ActionType(Enum):
vibe_core/cartridges/system/envoy/deterministic_executor.py:100:class PlaybookPhase:
vibe_core/cartridges/system/envoy/deterministic_executor.py:117:class PlaybookDefinition:
vibe_core/cartridges/system/envoy/deterministic_executor.py:129:class PlaybookExecution:
vibe_core/cartridges/system/envoy/deterministic_executor.py:148:class DeterministicExecutor:
vibe_core/cartridges/system/forum/cartridge_main.py:51:class ForumCartridge(VibeAgent, OathMixin):
vibe_core/cartridges/system/watchman/tools/system_health_check.py:17:class SystemHealthCheck(Tool):
vibe_core/cartridges/system/watchman/tools/standards_inspection.py:23:class ViolationType(Enum):
vibe_core/cartridges/system/watchman/tools/standards_inspection.py:34:class ViolationSeverity(Enum):
vibe_core/cartridges/system/watchman/tools/standards_inspection.py:44:class Violation:
vibe_core/cartridges/system/watchman/tools/standards_inspection.py:70:class PathCallVisitor(ast.NodeVisitor):
vibe_core/cartridges/system/watchman/tools/standards_inspection.py:110:class InitMethodVisitor(ast.NodeVisitor):
vibe_core/cartridges/system/watchman/tools/standards_inspection.py:163:class DirectToolCallVisitor(ast.NodeVisitor):
vibe_core/cartridges/system/watchman/tools/standards_inspection.py:213:class StandardsInspectionTool(Tool):
```

### E. ALL TODO/FIXME/HACK COMMENTS
```
vibe_core/cartridges/system/archivist/tools/audit_tool.py:78:        # TODO: Implement real verification with public_key when HERALD has STEWARD.md
vibe_core/cartridges/system/oracle/tools/introspection_tool.py:326:                "description": "Placeholder or TODO implementation detected",
vibe_core/cartridges/system/envoy/tools/wiring_audit_scripts.py:221:            "# TODO.*implement": "MEDIUM",
vibe_core/cartridges/system/envoy/tools/wiring_audit_scripts.py:244:            # Templates (TODOs expected)
vibe_core/cartridges/system/watchman/cartridge_main.py:64:            r"TODO.*implement",
vibe_core/cartridges/system/engineer/templates/agent/cartridge_main.py:101:        # TODO: Implement your capability
vibe_core/cartridges/system/engineer/templates/agent/cartridge_main.py:106:        # TODO: Implement your capability
vibe_core/cartridges/agent_city/analyst/tools/code_tool.py:8:- Technical debt indicators (TODO, FIXME, HACK)
vibe_core/cartridges/agent_city/analyst/tools/code_tool.py:198:            (r"\bTODO\b", "todo"),
vibe_core/cartridges/agent_city/analyst/tools/code_tool.py:199:            (r"\bFIXME\b", "fixme"),
vibe_core/cartridges/agent_city/analyst/tools/code_tool.py:200:            (r"\bHACK\b", "hack"),
vibe_core/cartridges/agent_city/analyst/tools/code_tool.py:201:            (r"\bXXX\b", "xxx"),
vibe_core/cortex/engines/__init__.py:8:- playbook_engine: DAG workflows (TODO: migrate)
vibe_core/cortex/protocols/__init__.py:4:TODO: Define CognitiveProcess, Intent, and other protocols here.
vibe_core/playbook/__init__.py:22:# TODO: Remove in v2.0
vibe_core/config/__init__.py:21:# TODO: Remove in v2.0
vibe_core/plugins/steward_protocol/plugin_main.py:307:            "signature_valid": None,  # TODO: implement
vibe_core/plugins/steward_protocol/plugin_main.py:348:            "valid_until": None,  # TODO: implement expiry
vibe_core/plugins/vedic_governance/plugin_main.py:64:        # TODO: Persist to Ledger (currently in-memory)
vibe_core/plugins/vedic_governance/plugin_main.py:68:        # TODO: Persist to Ledger (currently in-memory)
vibe_core/capability_registry.py:17:GAD-XXXX: REVOKE_MANDATE Implementation (Phase 2)
vibe_core/runtime/prompt_composer.py:237:        project_root = Path.cwd()  # TODO: Get from context if available
vibe_core/runtime/prompt_registry.py:443:            # Try to find SOP file with pattern SOP_XXX_*.md
vibe_core/specialists/base_agent.py:571:        2. Create feature branch (feature/TASK-XXX)
vibe_core/store/sqlite_store.py:10:- TODO: Session narrative, artifacts, quality gates (Part 2)
```

### F. ALL PASS STATEMENTS (Potential stubs)
```
vibe_core/cartridges/system/civic/tools/economy.py:36:    pass
vibe_core/cartridges/system/civic/tools/vault.py:75:    pass
vibe_core/cartridges/system/civic/tools/vault.py:81:    pass
vibe_core/cartridges/system/civic/tools/vault.py:87:    pass
vibe_core/cartridges/system/civic/tools/ledger_tool.py:29:    pass
vibe_core/cartridges/system/oracle/tools/introspection_tool.py:31:    pass
vibe_core/cartridges/system/envoy/action_handlers.py:33:        pass
vibe_core/cartridges/system/envoy/action_handlers.py:53:        pass
vibe_core/cartridges/system/envoy/provider.py:444:                    pass
vibe_core/cartridges/system/envoy/deterministic_executor.py:559:                            pass
vibe_core/cartridges/system/forum/cartridge_main.py:673:                pass
vibe_core/cartridges/system/scribe/tools/project_introspector.py:77:            pass
vibe_core/cartridges/system/scribe/tools/project_introspector.py:177:            pass
vibe_core/cartridges/system/scribe/tools/introspector.py:213:                pass
vibe_core/cartridges/system/scribe/tools/introspector.py:233:                pass
vibe_core/cartridges/system/scribe/tools/base.py:124:                pass
vibe_core/cartridges/system/scribe/tools/base.py:127:        pass
vibe_core/cartridges/system/herald/cartridge_main.py:693:                pass
vibe_core/cartridges/system/herald/governance/constitution.py:55:        pass
vibe_core/cartridges/system/herald/governance/constitution.py:60:        pass
vibe_core/cartridges/system/engineer/cartridge_main.py:175:    pass
vibe_core/cartridges/agent_city/librarian/cartridge_main.py:26:            pass
vibe_core/cartridges/agent_city/analyst/tools/deps_tool.py:147:                    pass
vibe_core/cartridges/agent_city/analyst/tools/deps_tool.py:187:                pass
vibe_core/cartridges/agent_city/analyst/tools/deps_tool.py:218:                pass
vibe_core/cartridges/agent_city/analyst/tools/deps_tool.py:262:                    pass
vibe_core/cartridges/agent_city/analyst/tools/git_tool.py:228:                    pass
vibe_core/cartridges/agent_city/analyst/tools/docs_tool.py:152:                    pass
vibe_core/cartridges/agent_city/analyst/tools/docs_tool.py:237:                    pass
vibe_core/cartridges/agent_city/analyst/tools/docs_tool.py:276:                pass
vibe_core/cartridges/agent_city/analyst/tools/architecture_tool.py:300:                pass
vibe_core/cartridges/agent_city/analyst/tools/code_tool.py:176:                    pass
vibe_core/cartridges/agent_city/analyst/tools/code_tool.py:179:                pass
vibe_core/cartridges/agent_city/analyst/tools/code_tool.py:234:                pass
vibe_core/cartridges/agent_city/analyst/tools/code_tool.py:314:                    pass
vibe_core/cartridges/agent_city/analyst/tools/code_tool.py:317:                pass
vibe_core/cartridges/agent_city/analyst/tools/structure_tool.py:152:                            pass
vibe_core/cartridges/base.py:24:            pass
vibe_core/settings/protocol.py:86:        pass
vibe_core/settings/protocol.py:117:        pass
vibe_core/settings/protocol.py:130:        pass
vibe_core/settings/protocol.py:145:        pass
vibe_core/cortex/engines/circuit_engine.py:288:            pass
vibe_core/playbook/runner.py:39:    pass
vibe_core/playbook/runner.py:45:    pass
vibe_core/playbook/runner.py:51:    pass
vibe_core/playbook/runner.py:105:        pass
vibe_core/playbook/operations/kernel_spawn.py:370:            pass
vibe_core/playbook/loader.py:35:    pass
vibe_core/playbook/loader.py:41:    pass
```

### G. ALL AGENT MANIFESTS

#### vibe_core/cartridges/system/ping/steward.json
```json
{
  "agent": {
    "id": "ping",
    "name": "PING"
  },
  "capabilities": {
    "operations": [
      {
        "description": "ping operation",
        "name": "ping"
      },
      {
        "description": "status operation",
        "name": "status"
      }
    ]
  },
  "governance": {
    "compliance_level": 2,
    "constitution_hash": "df4bf7b77c3676432442e3fa21fe392389dd43f57527feded615131856347309",
    "issued_at": "2025-11-29T12:00:00.000000Z",
    "issuer": "passport_office"
  },
  "identity": {
    "agent_id": "ping",
    "name": "PING"
  },
  "specs": {
    "description": "Minimal test agent",
    "domain": "SYSTEM",
    "version": "1.0.0"
  }
}
```

#### vibe_core/cartridges/system/civic/steward.json
```json
{
  "capabilities": {
    "operations": [
      {
        "description": "registry operation",
        "name": "registry"
      },
      {
        "description": "licensing operation",
        "name": "licensing"
      },
      {
        "description": "ledger operation",
        "name": "ledger"
      },
      {
        "description": "governance operation",
        "name": "governance"
      }
    ]
  },
  "governance": {
    "compliance_level": 2,
    "constitution_hash": "df4bf7b77c3676432442e3fa21fe392389dd43f57527feded615131856347309",
    "issued_at": "2025-11-29T08:57:39.430540Z",
    "issuer": "passport_office"
  },
  "identity": {
    "agent_id": "civic",
    "name": "CIVIC"
  },
  "specs": {
    "description": "Governance agent: enforces rules, manages licenses, audits credits",
    "domain": "GOVERNANCE",
    "version": "2.0.0"
  }
}
```

#### vibe_core/cartridges/system/archivist/steward.json
```json
{
  "capabilities": {
    "operations": [
      {
        "description": "event_monitoring operation",
        "name": "event_monitoring"
      },
      {
        "description": "verification operation",
        "name": "verification"
      },
      {
        "description": "audit_trail operation",
        "name": "audit_trail"
      }
    ]
  },
  "governance": {
    "compliance_level": 2,
    "constitution_hash": "df4bf7b77c3676432442e3fa21fe392389dd43f57527feded615131856347309",
    "issued_at": "2025-11-29T08:57:39.398111Z",
    "issuer": "passport_office"
  },
  "identity": {
    "agent_id": "archivist",
    "name": "ARCHIVIST"
  },
  "specs": {
    "description": "Event verification and audit trail agent",
    "domain": "SYSTEM",
    "version": "1.0.0"
  }
}
```

#### vibe_core/cartridges/system/discoverer/steward.json
```json
{
  "capabilities": {
    "operations": [
      {
        "description": "discovery operation",
        "name": "discovery"
      },
      {
        "description": "registration operation",
        "name": "registration"
      },
      {
        "description": "governance operation",
        "name": "governance"
      }
    ]
  },
  "governance": {
    "compliance_level": 2,
    "constitution_hash": "df4bf7b77c3676432442e3fa21fe392389dd43f57527feded615131856347309",
    "issued_at": "2025-11-29T08:57:39.441204Z",
    "issuer": "passport_office"
  },
  "identity": {
    "agent_id": "discoverer",
    "name": "The Discoverer"
  },
  "specs": {
    "description": "Agent discovery, verification, and registration",
    "domain": "GOVERNANCE",
    "version": "1.0.0"
  }
}
```

#### vibe_core/cartridges/system/supreme_court/steward.json
```json
{
  "capabilities": {
    "operations": [
      {
        "description": "governance operation",
        "name": "governance"
      },
      {
        "description": "auditing operation",
        "name": "auditing"
      }
    ]
  },
  "governance": {
    "compliance_level": 2,
    "constitution_hash": "df4bf7b77c3676432442e3fa21fe392389dd43f57527feded615131856347309",
    "issued_at": "2025-11-29T08:57:39.530038Z",
    "issuer": "passport_office"
  },
  "identity": {
    "agent_id": "supreme_court",
    "name": "SUPREME_COURT"
  },
  "specs": {
    "description": "Appellate justice system with mercy protocol",
    "domain": "JUSTICE",
    "version": "1.0.0"
  }
}
```

#### vibe_core/cartridges/system/oracle/steward.json
```json
{
  "capabilities": {
    "operations": [
      {
        "description": "introspection operation",
        "name": "introspection"
      },
      {
        "description": "audit_trail operation",
        "name": "audit_trail"
      },
      {
        "description": "system_health operation",
        "name": "system_health"
      }
    ]
  },
  "governance": {
    "compliance_level": 2,
    "constitution_hash": "df4bf7b77c3676432442e3fa21fe392389dd43f57527feded615131856347309",
    "issued_at": "2025-11-29T08:57:39.496189Z",
    "issuer": "passport_office"
  },
  "identity": {
    "agent_id": "oracle",
    "name": "ORACLE"
  },
  "specs": {
    "description": "System introspection and explanation agent",
    "domain": "SYSTEM",
    "version": "1.0.0"
  }
}
```

#### vibe_core/cartridges/system/science/steward.json
```json
{
  "agent": {
    "id": "science",
    "name": "SCIENCE"
  },
  "capabilities": {
    "operations": [
      {
        "description": "research operation",
        "name": "research"
      },
      {
        "description": "web_search operation",
        "name": "web_search"
      },
      {
        "description": "fact_synthesis operation",
        "name": "fact_synthesis"
      }
    ]
  },
  "governance": {
    "compliance_level": 2,
    "constitution_hash": "df4bf7b77c3676432442e3fa21fe392389dd43f57527feded615131856347309",
    "issued_at": "2025-11-29T08:57:39.507065Z",
    "issuer": "passport_office"
  },
  "identity": {
    "agent_id": "science",
    "name": "SCIENCE"
  },
  "specs": {
    "description": "External intelligence module via web research",
    "domain": "INTELLIGENCE",
    "version": "1.0.0"
  }
}
```

#### vibe_core/cartridges/system/envoy/steward.json
```json
{
  "agent": {
    "id": "envoy",
    "name": "ENVOY"
  },
  "capabilities": {
    "operations": [
      {
        "description": "orchestration operation",
        "name": "orchestration"
      },
      {
        "description": "governance operation",
        "name": "governance"
      },
      {
        "description": "broadcasting operation",
        "name": "broadcasting"
      },
      {
        "description": "registry operation",
        "name": "registry"
      },
      {
        "description": "auditing operation",
        "name": "auditing"
      }
    ]
  },
  "governance": {
    "compliance_level": 2,
    "constitution_hash": "df4bf7b77c3676432442e3fa21fe392389dd43f57527feded615131856347309",
    "issued_at": "2025-11-29T08:57:39.463665Z",
    "issuer": "passport_office"
  },
  "identity": {
    "agent_id": "envoy",
    "name": "ENVOY"
  },
  "specs": {
    "description": "Universal operator interface agent",
    "domain": "INTERFACE",
    "version": "1.0.0"
  }
}
```

#### vibe_core/cartridges/system/forum/steward.json
```json
{
  "capabilities": {
    "operations": [
      {
        "description": "governance operation",
        "name": "governance"
      },
      {
        "description": "voting operation",
        "name": "voting"
      },
      {
        "description": "proposal_management operation",
        "name": "proposal_management"
      }
    ]
  },
  "governance": {
    "compliance_level": 2,
    "constitution_hash": "df4bf7b77c3676432442e3fa21fe392389dd43f57527feded615131856347309",
    "issued_at": "2025-11-29T08:57:39.474530Z",
    "issuer": "passport_office"
  },
  "identity": {
    "agent_id": "forum",
    "name": "FORUM"
  },
  "specs": {
    "description": "Democratic decision layer for governance",
    "domain": "COMMUNITY",
    "version": "1.0.0"
  }
}
```

#### vibe_core/cartridges/system/watchman/steward.json
```json
{
  "capabilities": {
    "operations": [
      {
        "description": "monitoring operation",
        "name": "monitoring"
      },
      {
        "description": "alerting operation",
        "name": "alerting"
      }
    ]
  },
  "governance": {
    "compliance_level": 2,
    "constitution_hash": "df4bf7b77c3676432442e3fa21fe392389dd43f57527feded615131856347309",
    "issued_at": "2025-11-29T08:57:39.541003Z",
    "issuer": "passport_office"
  },
  "identity": {
    "agent_id": "watchman",
    "name": "WATCHMAN"
  },
  "specs": {
    "description": "System integrity and monitoring agent",
    "domain": "SYSTEM",
    "version": "1.0.0"
  }
}
```

#### vibe_core/cartridges/system/scribe/steward.json
```json
{
  "capabilities": {
    "operations": [
      {
        "description": "documentation operation",
        "name": "documentation"
      },
      {
        "description": "introspection operation",
        "name": "introspection"
      },
      {
        "description": "publishing operation",
        "name": "publishing"
      }
    ]
  },
  "governance": {
    "compliance_level": 2,
    "constitution_hash": "df4bf7b77c3676432442e3fa21fe392389dd43f57527feded615131856347309",
    "issued_at": "2025-11-29T08:57:39.518225Z",
    "issuer": "passport_office"
  },
  "identity": {
    "agent_id": "scribe",
    "name": "SCRIBE"
  },
  "specs": {
    "description": "Autonomous documentation generation agent",
    "domain": "INFRASTRUCTURE",
    "version": "1.0.0"
  }
}
```

#### vibe_core/cartridges/system/herald/steward.json
```json
{
  "capabilities": {
    "operations": [
      {
        "description": "Publish content to social media (Twitter, Reddit)",
        "name": "herald.broadcast"
      },
      {
        "description": "Research topics via external search APIs",
        "name": "herald.research"
      },
      {
        "description": "Generate and refine written content",
        "name": "herald.scribe"
      },
      {
        "description": "Detect bots and analyze users for recruitment",
        "name": "herald.scout"
      },
      {
        "description": "Cryptographic identity and signature operations",
        "name": "herald.identity"
      }
    ]
  },
  "governance": {
    "compliance_level": 2,
    "constitution_hash": "df4bf7b77c3676432442e3fa21fe392389dd43f57527feded615131856347309",
    "issued_at": "2025-11-29T08:57:39.485270Z",
    "issuer": "passport_office"
  },
  "identity": {
    "agent_id": "herald",
    "name": "HERALD"
  },
  "specs": {
    "description": "Protocol communications and identity verification agent (A.G.I.)",
    "domain": "COMMUNICATIONS",
    "version": "1.0.0"
  }
}
```

#### vibe_core/cartridges/system/chronicle/steward.json
```json
{
  "capabilities": {
    "operations": [
      {
        "description": "Git operations - commits, branches, history, repository management",
        "name": "chronicle.git"
      }
    ]
  },
  "governance": {
    "compliance_level": 2,
    "constitution_hash": "df4bf7b77c3676432442e3fa21fe392389dd43f57527feded615131856347309",
    "issued_at": "2025-11-29T08:57:39.420117Z",
    "issuer": "passport_office"
  },
  "identity": {
    "agent_id": "chronicle",
    "name": "CHRONICLE"
  },
  "specs": {
    "description": "Temporal operations and event tracking",
    "domain": "SYSTEM",
    "version": "1.0.0"
  }
}
```

#### vibe_core/cartridges/system/auditor/steward.json
```json
{
  "capabilities": {
    "operations": [
      {
        "description": "compliance_enforcement operation",
        "name": "compliance_enforcement"
      },
      {
        "description": "identity_verification operation",
        "name": "identity_verification"
      },
      {
        "description": "documentation_sync operation",
        "name": "documentation_sync"
      }
    ]
  },
  "governance": {
    "compliance_level": 2,
    "constitution_hash": "df4bf7b77c3676432442e3fa21fe392389dd43f57527feded615131856347309",
    "issued_at": "2025-11-29T08:57:39.409155Z",
    "issuer": "passport_office"
  },
  "identity": {
    "agent_id": "auditor",
    "name": "AUDITOR"
  },
  "specs": {
    "description": "GAD-000 compliance enforcement agent",
    "domain": "SECURITY",
    "version": "1.0.0"
  }
}
```

#### vibe_core/cartridges/system/engineer/templates/agent/steward.json
```json
{
  "capabilities": {
    "operations": [
      {
        "description": "YOUR_TOOL_DESCRIPTION_HERE",
        "name": "YOUR_AGENT_ID.YOUR_TOOL_NAME"
      }
    ]
  },
  "governance": {
    "compliance_level": 1,
    "constitution_hash": "WILL_BE_COMPUTED_AT_BOOT",
    "issued_at": "WILL_BE_SET_AT_REGISTRATION",
    "issuer": "passport_office"
  },
  "identity": {
    "agent_id": "YOUR_AGENT_ID",
    "name": "YOUR_AGENT_NAME"
  },
  "specs": {
    "description": "YOUR_AGENT_DESCRIPTION",
    "domain": "YOUR_DOMAIN",
    "version": "1.0.0"
  }
}
```

#### vibe_core/cartridges/system/engineer/steward.json
```json
{
  "capabilities": {
    "operations": [
      {
        "description": "code_generation operation",
        "name": "code_generation"
      },
      {
        "description": "scaffolding operation",
        "name": "scaffolding"
      },
      {
        "description": "automation operation",
        "name": "automation"
      }
    ]
  },
  "governance": {
    "compliance_level": 2,
    "constitution_hash": "df4bf7b77c3676432442e3fa21fe392389dd43f57527feded615131856347309",
    "issued_at": "2025-11-29T08:57:39.452796Z",
    "issuer": "passport_office"
  },
  "identity": {
    "agent_id": "engineer",
    "name": "ENGINEER"
  },
  "specs": {
    "description": "Meta-agent for building new agents and code",
    "domain": "INFRASTRUCTURE",
    "version": "1.0.0"
  }
}
```

#### vibe_core/cartridges/agent_city/librarian/steward.json
```json
{
  "identity": {
    "agent_id": "librarian",
    "name": "LIBRARIAN",
    "version": "1.0.0",
    "author": "Universal Tool Registry Initiative"
  },
  "specs": {
    "domain": "KNOWLEDGE",
    "description": "Knowledge management: catalog, search, recommend books",
    "capabilities": [
      "catalog_books",
      "search_books",
      "recommend_books"
    ]
  },
  "operations": [
    {
      "name": "catalog",
      "description": "Add a book to the catalog",
      "parameters": {
        "title": "string",
        "author": "string",
        "genre": "string (optional)",
        "year": "integer (optional)"
      }
    },
    {
      "name": "search",
      "description": "Search books in catalog",
      "parameters": {
        "query": "string",
        "genre": "string (optional)",
        "limit": "integer (optional)"
      }
    },
    {
      "name": "recommend",
      "description": "Get book recommendations",
      "parameters": {
        "genre": "string (optional)",
        "count": "integer (optional)"
      }
    }
  ],
  "governance": {
    "constitutional_oath": "optional",
    "risk_level": "LOW"
  }
}
```

#### vibe_core/cartridges/agent_city/analyst/steward.json
```json
{
  "capabilities": {
    "operations": [
      {
        "description": "Git history analysis (velocity, patterns, commits)",
        "name": "git_analysis",
        "tool": "analyst.git"
      },
      {
        "description": "Code analysis (AST, complexity, tech debt)",
        "name": "code_analysis",
        "tool": "analyst.code"
      },
      {
        "description": "Structure analysis (modules, coupling, hotspots)",
        "name": "structure_analysis",
        "tool": "analyst.structure"
      },
      {
        "description": "Dependency analysis (imports, requirements)",
        "name": "dependency_analysis",
        "tool": "analyst.deps"
      },
      {
        "description": "Documentation analysis (coverage, quality)",
        "name": "docs_analysis",
        "tool": "analyst.docs"
      },
      {
        "description": "Multi-source context synthesis (VEDA-4 circuit)",
        "name": "context_synthesis"
      }
    ]
  },
  "governance": {
    "compliance_level": 2,
    "constitution_hash": "df4bf7b77c3676432442e3fa21fe392389dd43f57527feded615131856347309",
    "issued_at": "2025-12-02T22:45:00.000000Z",
    "issuer": "passport_office"
  },
  "identity": {
    "agent_id": "analyst",
    "name": "ANALYST"
  },
  "specs": {
    "description": "Multi-Source Repository Analysis (Realtime Architecture Guide)",
    "domain": "RESEARCH",
    "version": "2.0.0"
  },
  "tools": [
    "analyst.git",
    "analyst.code",
    "analyst.structure",
    "analyst.deps",
    "analyst.docs"
  ]
}
```

#### vibe_core/cartridges/agent_city/marketer/steward.json
```json
{
  "identity": {
    "agent_id": "marketer",
    "name": "MARKETER",
    "version": "1.0.0",
    "author": "Steward Protocol - Citizen Sovereignty Initiative"
  },
  "specs": {
    "domain": "CONTENT",
    "description": "Autonomous content strategist and generator for social media",
    "capabilities": [
      "tweet_generation",
      "reddit_posts",
      "reply_generation",
      "recruitment_pitches"
    ]
  },
  "operations": [
    {
      "name": "generate_tweet",
      "description": "Generate a tweet with governance validation",
      "parameters": {
        "context": "string (optional)"
      }
    },
    {
      "name": "generate_reddit_post",
      "description": "Generate long-form Reddit post",
      "parameters": {
        "subreddit": "string (optional, default: r/LocalLLaMA)"
      }
    },
    {
      "name": "generate_reply",
      "description": "Generate reply to a mention",
      "parameters": {
        "original_text": "string (required)",
        "author": "string (required)"
      }
    },
    {
      "name": "generate_recruitment",
      "description": "Generate recruitment pitch for wild agent",
      "parameters": {
        "author": "string (required)",
        "original_text": "string (optional)"
      }
    }
  ],
  "governance": {
    "constitutional_oath": "optional",
    "risk_level": "MEDIUM",
    "notes": "Uses HeraldConstitution for content validation"
  },
  "architecture": {
    "separation_of_concerns": "MARKETER thinks (generates content), HERALD speaks (broadcasts content)",
    "moved_from": "steward/system_agents/herald (2025-11-29)",
    "reason": "Content generation is business logic, not infrastructure"
  }
}
```

#### vibe_core/cartridges/agent_city/mechanic/steward.json
```json
{
  "capabilities": {
    "operations": [
      {
        "description": "maintenance operation",
        "name": "maintenance"
      }
    ]
  },
  "governance": {
    "compliance_level": 2,
    "constitution_hash": "df4bf7b77c3676432442e3fa21fe392389dd43f57527feded615131856347309",
    "issued_at": "2025-11-29T08:57:39.364618Z",
    "issuer": "passport_office"
  },
  "identity": {
    "agent_id": "mechanic",
    "name": "MECHANIC"
  },
  "specs": {
    "description": "System maintenance and repairs",
    "domain": "MAINTENANCE",
    "version": "1.0.0"
  }
}
```
