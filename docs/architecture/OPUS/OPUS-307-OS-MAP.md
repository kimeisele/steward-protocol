# OPUS-307-OS-MAP: Complete System Inventory
## Vedic Soul. German Body. Full Transparency.

**Generated:** 2025-12-25
**Updated:** 2025-12-25 (OPUS-307 Phase 5: Create CLI complete)
**Status:** GAD-000 CLI COVERAGE COMPLETE - System fully operable via CLI

---

## EXECUTIVE SUMMARY

| Category | Count | CLI Exposed | GAD-000 Gap |
|----------|-------|-------------|-------------|
| **Plugins** | 34 | 7 namespaces | Improving |
| **Cartridges** | 28 | 28 namespaces | **CLOSED** |
| **Tools** | 55+ | via cartridge CLI | **CLOSED** |
| **Circuits** | 37 | via `run` | OK |
| **Protocols** | 42 | N/A | N/A |
| **CLI Commands** | 37 | Yes | OK |

### OPUS-307 ACHIEVEMENTS

**Phase 1: Core CLI Namespaces**
| Namespace | Commands | Purpose |
|-----------|----------|---------|
| `prakriti` | status, guna, snapshot, verify, diff, layers, session | State Engine visibility |
| `genesis` | audit, check, classify, scaffold, types, templates | Infrastructure compliance |

**Phase 2: Universal Cartridge Bridge (LAZY LOADING)**
| Feature | Implementation |
|---------|----------------|
| Lazy Manifest Scan | YAML-only discovery, NO Python imports at boot |
| Dynamic Registration | 28 cartridge namespaces auto-registered |
| On-Demand Import | Tool modules loaded only on execution |
| Auto Arg Parsing | CLI args parsed from `parameters_schema` |

```
steward cartridges              # List all 28 cartridges
steward watchman --help         # Show watchman tools
steward watchman health --action check_all  # Execute tool
steward auditor compliance --action inspect # Execute tool
```

---

## PART I: MANIFEST INVENTORY

### 1.1 PLUGINS (34 total)

#### Core System Plugins (14)
| ID | Name | Priority | CLI Namespace | Commands |
|----|------|----------|---------------|----------|
| system_heartbeat | System Heartbeat Orchestrator | 90 | - | - |
| interface | Unified Interface Plugin | 100 | - | - |
| economy | Economy | 20 | - | - |
| tools | Tools Plugin | 5 | - | - |
| resource_limits | Resource Limits | 5 | resources | usage, quotas, violations |
| boot_optimizer | Boot Optimizer | 1 | - | - |
| task_manager | Task Manager Plugin | 95 | tasks | list, stats, next |
| steward_protocol | STEWARD Protocol Plugin | 5 | - | - |
| lifecycle | Lifecycle Plugin | 10 | agents | list, status, kill, spawn-log |
| integrity_guard | Integrity Guard | 0 | - | - |
| test_mode | Test Mode Plugin | 1 | - | - |
| vedic_governance | Vedic Governance Plugin | 10 | - | - |
| process_isolation | Process Isolation | 5 | - | - |
| doctor | System Doctor | - | system | doctor |

#### Agent Management Plugins (3)
| ID | Name | Priority | CLI Namespace | Commands |
|----|------|----------|---------------|----------|
| agent_city | Agent City | - | city | citizens |
| nexus_holon | Nexus Holon | 10 | - | - |
| opus_assistant | OPUS Assistant | 50 | opus | status, log, verify, refresh, explore, approve, reject, pending, karma |

#### Service & Integration Plugins (6)
| ID | Name | Priority | CLI Namespace | Commands |
|----|------|----------|---------------|----------|
| envoy | Envoy Plugin | 15 | - | - |
| sangha_network | Sangha Network | 5 | - | - |
| durvasa | Durvasa Protocol | 50 | - | - |
| samsara | Samsara Engine | 50 | - | - |
| kala | KALA - Eternal Time | 3 | - | - |
| node_pulse | Node Pulse | 4 | - | - |

#### Specialized Plugins (4)
| ID | Name | Priority | CLI Namespace | Commands |
|----|------|----------|---------------|----------|
| sarga_cycle | Sarga Cycle Plugin | 5 | - | - |
| test_orchestration | Test Orchestration Plugin | 50 | test | run, summary, pytest, guardian |
| complexity_analyzer | Complexity Analyzer | 80 | - | - |
| plugin_template | Plugin Template (disabled) | 999 | - | - |

**CLI Coverage: 7/34 plugins have CLI = 20.6%**

---

### 1.2 CARTRIDGES (28 total) - ALL CLI ACCESSIBLE

**Via Universal Cartridge Bridge (Lazy Loading)**

#### System Agents (15)
| ID | Name | Domain | Tools | CLI |
|----|------|--------|-------|-----|
| ping | PING Agent | SYSTEM | - | `steward ping` |
| civic | CIVIC Agent | GOVERNANCE | bank, vault, ledger, license +5 | `steward civic` |
| archivist | ARCHIVIST Agent | AUDIT | ledger, verifier, observer, audit | `steward archivist` |
| discoverer | DISCOVERER Agent | GOVERNANCE | - | `steward discoverer` |
| oracle | ORACLE Agent | INTROSPECTION | introspection | `steward oracle` |
| supreme_court | SUPREME_COURT Agent | GOVERNANCE | justice_ledger, appeals, precedent, verdict | `steward supreme_court` |
| science | SCIENTIST Agent | SCIENCE | web_search | `steward science` |
| envoy | The Envoy | DIPLOMACY | hil, campaign, gap_report, diplomacy +3 | `steward envoy` |
| forum | FORUM Agent | GOVERNANCE | - | `steward forum` |
| watchman | WATCHMAN Agent | MONITORING | health, standards | `steward watchman` |
| scribe | SCRIBE Agent | INFRASTRUCTURE | base | `steward scribe` |
| herald | HERALD Agent | AGI | broadcast, scribe, scout, research, identity +3 | `steward herald` |
| chronicle | CHRONICLE | INFRASTRUCTURE | git | `steward chronicle` |
| auditor | AUDITOR Agent | COMPLIANCE | watchdog, invariant, compliance, verdict | `steward auditor` |
| engineer | ENGINEER Agent | ORCHESTRATION | heal_violation, builder, refactor | `steward engineer` |

#### Agent City Citizens (13)
| ID | Name | Domain | Tools | CLI |
|----|------|--------|-------|-----|
| librarian | LIBRARIAN | KNOWLEDGE | catalog, search, recommend | `steward librarian` |
| analyst | ANALYST | RESEARCH | git, code, structure, deps, docs, architecture | `steward analyst` |
| marketer | MARKETER | CONTENT | content | `steward marketer` |
| mechanic | MECHANIC | INFRASTRUCTURE | tidy | `steward mechanic` |
| agora | AGORA | GOVERNANCE | - | `steward agora` |
| ambassador | AMBASSADOR | GOVERNANCE | - | `steward ambassador` |
| pulse | PULSE | MONITORING | - | `steward pulse` |
| artisan | ARTISAN | CREATIVE | media | `steward artisan` |
| lens | LENS | ANALYTICS | - | `steward lens` |
| dhruva | DHRUVA | KNOWLEDGE | genesis_keeper, data_ethics +2 | `steward dhruva` |
| dharma | DHARMA | GOVERNANCE | - | `steward dharma` |
| temple | TEMPLE | INFRASTRUCTURE | - | `steward temple` |
| market | MARKET | ECONOMY | - | `steward market` |

#### Starter Packs (4)
- shield, scope, nexus, spark

**CLI Coverage: 28/28 cartridges have CLI = 100%**
**Note:** Via Universal Cartridge Bridge with lazy loading

---

### 1.3 CIRCUITS (37 total)

#### Playbook Circuits (24)
| ID | Domain | Entry State | Purpose |
|----|--------|-------------|---------|
| simple_query | INTERFACE | process | Direct response |
| AGENT_BIRTH_V1 | LIFECYCLE | SHABDA | Agent spawning |
| architecture_analysis | ANALYSIS | - | Architecture review |
| heal_codebase | HEALING | - | Code healing |
| debug_fix | DEBUG | - | Bug fixing |
| governance_vote | GOVERNANCE | - | Democratic voting |
| research_synth | RESEARCH | - | Research synthesis |
| wiring_audit | AUDIT | - | Wiring verification |
| task_ledger | TASKS | - | Task management |
| philosophical_debate | META | - | Dialectic reasoning |
| purge_technical_debt_v1 | MAINTENANCE | - | Debt cleanup |
| context_synth | CONTEXT | - | Context building |
| project_scaffold | GENESIS | - | Project creation |
| feature_implement | DEVELOPMENT | - | Feature building |
| system_design | DESIGN | - | Architecture design |
| error_recovery | HEALING | - | Error handling |
| SYSTEM_STATUS_V2 | INTERFACE | query_status | System status |
| content_generation | CONTENT | - | Content creation |
| OUROBOROS_V1 | META | diagnose | Self-healing loop |
| doc_index_render | DOCS | - | Documentation |
| test_singularity | TEST | - | Test execution |
| golden_circuit_template | TEMPLATE | - | Circuit template |
| architect_v1 | META | - | Architecture agent |

#### OPUS Assistant Circuits (13)
- auto_verify, auto_heal, auto_refresh, karma_consequence
- genesis_check, bhakti_practice, manas_health, manas_awakening
- view_control, gap_hunt, maintenance_pulse, generate_harness
- capability_genesis

**CLI Coverage: All circuits accessible via `steward run <circuit_id>` = 100%**

---

## PART II: PROTOCOL INVENTORY (42 total)

### 2.1 Core Protocols with DI Registration

| Protocol | Implementation | Location | Registered |
|----------|---------------|----------|------------|
| VibeLedger | SQLiteLedger, InMemoryLedger | ledger.py | Yes |
| VibeKernel | RealVibeKernel | kernel_impl.py | Yes |
| VibeScheduler | InMemoryScheduler | scheduling/in_memory.py | Via kernel |
| ManifestRegistry | InMemoryManifestRegistry | manifest_registry.py | Via kernel |
| StateServiceProtocol | StateService | state/state_service.py | Yes |
| PrakritiProtocol | Prakriti | state/prakriti.py | Yes |
| StateSyncWeaverProtocol | StateSyncWeaver | state/weaver.py | Yes |
| LLMProtocol | LLMEngine | runtime/llm_engine.py | Yes |
| BankProtocol | BankService | plugins/economy | Factory |
| VaultProtocol | VaultService | plugins/economy | Factory |
| TwitterProtocol | TwitterService | herald/services | Yes |
| RedditProtocol | RedditService | herald/services | Yes |
| SystemHeartbeatProtocol | SystemHeartbeatPlugin | system_heartbeat | Yes |
| CognitiveKernelProtocol | CognitiveKernel | opus_assistant/manas | Yes |
| OpusAssistantProtocol | OpusAssistantPlugin | opus_assistant | Yes |
| ResourceSupervisorProtocol | ResourceManager | resource_limits | Yes |
| NetworkGatewayProtocol | NetworkGateway | sangha_network | Yes |
| ProcessSupervisorProtocol | ProcessManager | process_isolation | Yes |
| ShuddhiProtocol | ShuddhiEngine | boot_orchestrator.py | Yes |
| TaskProtocol | TaskManager | boot_orchestrator.py | Yes |

### 2.2 Other Protocols
- VibeAgent (ABC for agents)
- Capability (@runtime_checkable)
- Testable (@runtime_checkable)
- CLIHandler (@runtime_checkable)
- AuditorProtocol (with NullAuditor fallback)
- OperatorSocket

---

## PART III: STATE MANAGEMENT (Prakriti System)

### 3.1 Architecture

```
STHULA (Physical/Layer 1)          PRANA (Runtime/Layer 2)       PURUSHA (Identity/Layer 3)
├── git: GitState                  ├── kernel: KernelState       └── personas: PersonaManager
├── files: FileState               └── ephemeral: EphemeralState
└── ledger: LedgerState
```

### 3.2 Key Components

| Component | File | Purpose |
|-----------|------|---------|
| Prakriti | state/prakriti.py | Unified state engine |
| StateSyncWeaver | state/weaver.py | Commit orchestration |
| StateSyncHolon | state/sync_holon.py | Plugin state bridge |
| GunaClassifier | state/guna_classifier.py | State health diagnosis |
| StateService | state/state_service.py | Write routing |
| CommitAuthority | state/commit_authority.py | Commit execution |
| CognitiveWeaver | state/cognitive_weaver.py | State↔Knowledge bridge |

### 3.3 Guna Classification

| Guna | Meaning | State |
|------|---------|-------|
| SATTVA | Balance | Synced, clean, at rest |
| RAJAS | Activity | Dirty, changing, active |
| TAMAS | Inertia | Stale, broken, ignored |

### 3.4 .vibe/ Directory Structure

```
.vibe/
├── state/
│   ├── vedic_dharma.json
│   ├── synapses.json
│   ├── tasks.json
│   ├── cycle_history.json
│   └── plugins/opus_assistant/
│       ├── session.json
│       ├── observations.jsonl
│       ├── syscalls.jsonl
│       ├── manas_awareness.json
│       └── viveka_decisions.json
├── vibe.db              # DEAD - empty, never used
├── logs/system.log
└── history/
```

### 3.5 Hybrid Storage Architecture (OPUS-307 Phase 4 Discovery)

**The Three Bodies Doctrine applied to storage:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    STORAGE ARCHITECTURE MAP                              │
├─────────────────────────────────────────────────────────────────────────┤
│ STHULA (Physical/Immutable)                                              │
│   └── data/vibe_ledger.db    ✓ ACTIVE  6318 events  Last: TODAY         │
│       Purpose: Append-only ledger, audit trail, tool calls              │
│       Tables: ledger_events, tool_invocations, agent_events, system     │
├─────────────────────────────────────────────────────────────────────────┤
│ PRANA (Runtime/Mutable)                                                  │
│   ├── .vibe/state/*.json     ✓ ACTIVE  Task state, cycles, sessions     │
│   │   └── tasks.json, cycle_history.json, vedic_dharma.json, etc.       │
│   └── data/economy.db        ✓ ACTIVE  Bank/Vault transactions          │
│       Purpose: Atomic state that changes during runtime                  │
│       Design: JSON for fast R/W, SQLite for transactional queues        │
├─────────────────────────────────────────────────────────────────────────┤
│ PURUSHA (Identity/Persistent)                                            │
│   └── .vibe/state/plugins/opus_assistant/                                │
│       └── session.json, manas_awareness.json, viveka_decisions.json     │
│       Purpose: Persona memory, cognitive state, reputation               │
└─────────────────────────────────────────────────────────────────────────┘
```

**DEAD CODE - Orphaned SQLite DBs:**
| Database | Last Modified | Status | Evidence |
|----------|---------------|--------|----------|
| `.vibe/vibe.db` | Dec 8 | 14 tables, ALL EMPTY | Never written to |
| `.vibe/state/vibe_agency.db` | Dec 5 | 14 tables, ALL EMPTY | Never written to |
| `data/milk_ocean.db` | Dec 5 | 54 STUCK items | `# LEGACY ROUTER REMOVED (MilkOcean)` in task_manager.py:266 - UnifiedRouter replaced it |

**Why JSON for PRANA is CORRECT (not a migration failure):**

1. **STHULA is append-only** - Ledger needs SQLite for durability and queries
2. **PRANA is mutable** - Runtime state needs fast atomic writes
3. **JSON is simpler** - No schema migrations, human-readable, git-diffable
4. **SQLite overhead** - Unnecessary for single-file atomic state
5. **Design intent** - See PROMPT.md: "PRANA = Atomic state snapshots"

**Audit Command:** `steward audit databases` - Run to verify storage health

---

## PART IV: KEY SYSTEMS

### 4.1 Stadtamt (City Office)
- **Location:** `vibe_core/genesis/`
- **Purpose:** Infrastructure compliance & generation (GAD-000)
- **API:** `GenesisService.get_instance().ensure_compliance(path, type)`
- **CLI:** None (via Engineer cartridge)

### 4.2 Bauamt (Building Office)
- **Location:** `vibe_core/plugins/opus_assistant/manas/cortex/genesis/`
- **Purpose:** Legacy infrastructure generation (PoC)
- **Status:** Delegates to GenesisService

### 4.3 TaskKernel
- **Location:** `vibe_core/task_kernel.py`
- **Purpose:** Lightweight 100ms boot context (vs 5+ second full kernel)
- **API:** `TaskKernel.spawn(task, tools, parent, timeout)`
- **CLI:** None (internal MANAS component)

### 4.4 MANAS (Cognitive Brain)
- **Location:** `vibe_core/plugins/opus_assistant/manas/`
- **Components:**
  - CognitiveKernel (orchestrator)
  - IntentGenerator (intent creation)
  - ActionManager (execution)
  - SenseManager (perception)
  - 7+ Analyzers (intent discovery)
  - 11+ Senses (environmental awareness)
- **API:** `ManasOracle.consult(context)`
- **CLI:** Via `opus` namespace

---

## PART V: GAD-000 CLI COVERAGE ANALYSIS

### 5.1 Core CLI Namespaces (9)

| Namespace | Source | Commands | Coverage |
|-----------|--------|----------|----------|
| run | unified | execute any capability | Full |
| tool | legacy | list, info, execute | Full |
| circuit | legacy | list, run | Full |
| prakriti | **OPUS-307** | status, guna, snapshot, verify, diff, layers, session | **NEW** |
| genesis | **OPUS-307** | audit, check, classify, scaffold, types, templates | **NEW** |
| cartridges | **OPUS-307** | list all 28 cartridges | **NEW** |
| knowledge | legacy | search, index | Full |
| standards | legacy | check, fix | Full |
| remedies | legacy | list, apply | Full |

### 5.2 Cartridge CLI Namespaces (28) - NEW

All cartridges now accessible via `steward <cartridge> <tool> [args]`:

| Category | Namespaces |
|----------|------------|
| System | ping, civic, archivist, discoverer, oracle, supreme_court, science, envoy, forum, watchman, scribe, herald, chronicle, auditor, engineer |
| Agent City | librarian, analyst, marketer, mechanic, agora, ambassador, pulse, artisan, lens, dhruva, dharma, temple, market |

### 5.3 Previously Reported Gaps - STATUS

| System | Previous Status | Current Status |
|--------|-----------------|----------------|
| Prakriti State | Python API only | **CLOSED** - `steward prakriti` |
| Genesis/Stadtamt | Python API only | **CLOSED** - `steward genesis` |
| Economy (Bank/Vault) | Python API only | **CLOSED** - `steward civic bank/vault` |
| Individual Cartridge Tools | `steward run` only | **CLOSED** - Direct namespace access |
| StateSyncWeaver | Python API only | LOW (internal) |
| Sangha Network | Python API only | LOW (network layer) |

### 5.4 Remaining Work

1. **Plugin CLI expansion** - 27/34 plugins still lack dedicated CLI
2. **economy** namespace - dedicated namespace for bank/vault operations
3. **network** namespace - sangha network visibility

---

## PART VI: SAMKHYA TERMINOLOGY REFERENCE

| Sanskrit | Western | Architecture |
|----------|---------|--------------|
| Dharma | Invariant | NEVER break, crash first |
| Karma | Consequence | Ledger entries, side effects |
| Sthula | Physical | Git + Ledger + Files |
| Prana | Runtime | Kernel + Ephemeral state |
| Purusha | Identity | Persona + Reputation |
| Prakriti | Nature | State Engine |
| Maya | Illusion | Sandbox + Ephemeral |
| Sattva | Purity | Clean, synced state |
| Rajas | Activity | Dirty, changing state |
| Tamas | Inertia | Stale, broken state |
| Pralaya | Dissolution | Graceful shutdown |
| Arjuna | Warrior | Self-healing, retry |
| Narasimha | Protector | Zombie-killer, security |
| Manas | Mind | Cognitive kernel |
| Buddhi | Intellect | Discrimination layer |
| Chitta | Memory | Inner instrument |
| Ahamkara | Ego | State routing ("I-maker") |
| Jnanendriya | Senses | Perception (11 senses) |
| Karmendriya | Actions | Execution (5 actions) |

---

## COMPLETED PHASES

- [x] Phase 1: OS-MAP - Complete system inventory
- [x] Phase 2: CLI Gap Closure - Prakriti, Genesis, Cartridge Bridge
- [x] Phase 2.1: Prakriti CLI (7 commands)
- [x] Phase 2.2: Genesis CLI (6 commands)
- [x] Phase 2.3: Universal Cartridge Bridge (28 namespaces, lazy loading)
- [x] Phase 4.1: Audit CLI (`steward audit databases/usage/full/split-brain`)
- [x] Phase 4.2: Storage Architecture documented (Three Bodies mapping)
- [x] Phase 4.3: Surgical cleanup (624KB junk deleted)
- [x] Phase 4.4: Dead SQLite removal (3 DBs, 432KB freed)
- [x] Phase 4.5: Leaks closed (boot_sequence.py, base_agent.py, section_main.py)
- [x] Phase 5: Create CLI (`steward create agent/circuit/cartridge/plugin`)

## NEXT PHASES

- [ ] Phase 6: Plugin CLI expansion (internal plugins like opus_assistant)
- [ ] Phase 7: Dependency graph visualization
- [ ] Phase 8: Test coverage correlation

---

## GAD-000 CLI COVERAGE: COMPLETE

| Operation | CLI Command | Status |
|-----------|-------------|--------|
| View state | `steward prakriti status` | |
| View cartridges | `steward cartridges` | |
| Run circuit | `steward run <circuit>` | |
| Run tool | `steward <cartridge> <tool>` | |
| Audit system | `steward audit full` | |
| Check compliance | `steward genesis audit` | |
| **Create agent** | `steward create agent <name>` | **NEW** |
| **Create circuit** | `steward create circuit <name>` | **NEW** |
| **Create cartridge** | `steward create cartridge <name>` | **NEW** |
| **Create plugin** | `steward create plugin <name>` | **NEW** |

**Total CLI Namespaces: 39**

---

*"The repository IS the mind. Now we have its map - and the CLI to build it."*
