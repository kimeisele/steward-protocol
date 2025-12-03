# Docstring Analyse: Konsolidierter Bericht
Dieser Bericht bietet eine konsolidierte Analyse der Docstrings aller Python-Skripte im Projekt, um die übergeordnete Architektur und Funktionalität zu verstehen.
## 1. Projekt-Übersicht und Dokumentationsstatus
* **Gesamtzahl der analysierten Python-Dateien:** 440
* **Gesamtzahl der Docstrings gefunden:** 4058
* **Dokumentationsdichte (Durchschnittliche Docstrings pro Datei):** 9.22
* **Dateien mit unzureichender Dokumentation (weniger als 2 Docstrings):**
    * `steward/system_agents/scribe/tools/__init__.py`
    * `vibe_core/scheduling/__init__.py`
    * `hijack_boot.py`
    * `fix_imports.py`
    * `steward/system_agents/herald/__init__.py`
    * `steward/system_agents/engineer/templates/agent/tools/__init__.py`
    * `scripts/ci/verify_agents_manifest.py`
    * `scripts/ci/security_scan.py`
    * `scripts/ci/run_watchman_inspection.py`
    * `scripts/ci/run_constitutional_verdict.py`
    * `agent_city/__init__.py`
    * `agent_city/registry/__init__.py`
    * `agent_city/registry/agora/__init__.py`
    * `agent_city/registry/ambassador/__init__.py`
    * `agent_city/registry/artisan/tools/__init__.py`
    * `agent_city/registry/citizens/__init__.py`
    * `agent_city/registry/citizens/echo/__init__.py`
    * `agent_city/registry/dhruva/__init__.py`
    * `agent_city/registry/dhruva/tools/__init__.py`
    * `agent_city/registry/lens/__init__.py`
    * `agent_city/registry/librarian/tools/__init__.py`
    * `agent_city/registry/market/__init__.py`
    * `agent_city/registry/marketer/tools/__init__.py`
    * `agent_city/registry/mechanic/__init__.py`
    * `agent_city/registry/mechanic/tools/__init__.py`
    * `agent_city/registry/pulse/__init__.py`
    * `agent_city/registry/temple/__init__.py`
    * `agent_city/scripts/collect_stats.py`
    * `agent_city/scripts/generate_leaderboard.py`
    * `agent_city/scripts/render_dashboard.py`
    * `bin/link-roadmap-tasks.py`
    * `scripts/__init__.py`
    * `scripts/agents/watchman_patrol.py`
    * `scripts/final_launch.py`
    * `scripts/research/genesis_economy.py`
    * `scripts/summon.py`
    * `scripts/testing/test_gateway.py`
    * `scripts/testing/verify_hil_assistant.py`
    * `scripts/verify_migration_phase1.py`
    * `scripts/verify_offline_llm.py`
    * `scripts/verify_whole_brain.py`
    * `services/__init__.py`
    * `steward/system_agents/archivist/__init__.py`
    * `steward/system_agents/archivist/tools/__init__.py`
    * `steward/system_agents/auditor/__init__.py`
    * `steward/system_agents/auditor/tools/__init__.py`
    * `steward/system_agents/chronicle/__init__.py`
    * `steward/system_agents/chronicle/tools/__init__.py`
    * `steward/system_agents/civic/tools/__init__.py`
    * `steward/system_agents/engineer/tools/__init__.py`
    * `steward/system_agents/envoy/__init__.py`
    * `steward/system_agents/envoy/tools/__init__.py`
    * `steward/system_agents/herald/capabilities/__init__.py`
    * `steward/system_agents/herald/core/__init__.py`
    * `steward/system_agents/herald/governance/__init__.py`
    * `steward/system_agents/herald/tools/__init__.py`
    * `steward/system_agents/oracle/__init__.py`
    * `steward/system_agents/oracle/tools/__init__.py`
    * `steward/system_agents/ping/__init__.py`
    * `steward/system_agents/scribe/__init__.py`
    * `steward/system_agents/supreme_court/__init__.py`
    * `steward/system_agents/supreme_court/tools/__init__.py`
    * `tests/test_scribe_generation.py`
    * `tests/verify_steward_discovery.py`
    * `vibe_core/__init__.py`
    * `vibe_core/agents/__init__.py`
    * `vibe_core/bridge.py`
    * `vibe_core/cartridges/__init__.py`
    * `vibe_core/config/__init__.py`
    * `vibe_core/governance/__init__.py`
    * `vibe_core/knowledge/__init__.py`
    * `vibe_core/llm/__init__.py`
    * `vibe_core/playbook/__init__.py`
    * `vibe_core/protocols/__init__.py`
    * `vibe_core/runtime/__init__.py`
    * `vibe_core/runtime/providers/__init__.py`
    * `vibe_core/store/__init__.py`
    * `vibe_core/task_management/__init__.py`
    * `vibe_core/tools/__init__.py`

## 2. Hauptmodule und deren Zwecke (Moduldokstrings)
* `steward/system_agents/scribe/tools/vibe_introspector.py`: VibeCoreIntrospector - Dynamic discovery of vibe_core modules

Scans vibe_core/*.py files and extracts metadata from docstrings...
* `steward/system_agents/scribe/tools/readme_renderer.py`: SCRIBE README Renderer - Generate README.md from introspection

ZERO HARDCODED LINE NUMBERS! All data from:
- pyproject...
* `steward/system_agents/scribe/tools/project_introspector.py`: Project Introspector - Extract metadata from project files
* `steward/system_agents/scribe/tools/operations_introspector.py`: Operations Introspector - Dynamic discovery of system operations

Scans for:
- CI/CD workflows (.github/workflows/*...
* `steward/system_agents/scribe/tools/introspector.py`: SCRIBE Introspection Module - Extract metadata from codebase
* `steward/system_agents/scribe/tools/index_renderer.py`: SCRIBE Index Renderer - SCHEMA-DRIVEN Documentation Index

WHITELIST APPROACH: Only explicitly allowed files/dirs are indexed.
- Root: Whitelist of allowed...
* `steward/system_agents/scribe/tools/help_renderer.py`: SCRIBE Help Renderer - Generate HELP.md

3-LAYER CONTROL CENTER:
1...
* `steward/system_agents/scribe/tools/dashboard_renderer.py`: SCRIBE Dashboard Renderer - Generate DASHBOARD.md

SINGLE-PAGE OPERATIONAL VIEW:
- System Health (at-a-glance)
- Agent Status Grid
- CI/CD Pipeline Status
- Git Activity
- Economic Metrics
- Security Alerts
- Quick Actions

Tool Protocol Compliant (Kernel-Managed)...
* `steward/system_agents/scribe/tools/citymap_renderer.py`: SCRIBE Citymap Renderer - Generate CITYMAP.md

3-LAYER ARCHITECTURE:
1...
* `steward/system_agents/scribe/tools/base.py`: SCRIBE Tool Base - Shared boilerplate for all renderers

Eliminates DRY violation across renderer modules.
Provides Tool and ToolResult for both kernel-managed and standalone modes...
* `steward/system_agents/scribe/tools/agents_renderer.py`: SCRIBE Agents Renderer - Generate AGENTS.md

Tool Protocol Compliant (Kernel-Managed)...
* `steward/system_agents/scribe/tools/__init__.py`: SCRIBE Documentation Generation Tools

All renderer tools implement the Tool protocol and are kernel-managed.

NOTE: Renderers are NOT auto-imported to avoid circular imports...
* `scripts/generate_docs.py`: Documentation Generator - Standalone
=====================================

Generates ALL documentation files WITHOUT kernel dependency.

This is the reliable way:
- No kernel boot required
- No sandbox complexity
- Direct introspection → rendering → writing
- Fast, deterministic, debuggable

Usage:
    python scripts/generate_docs...
* `docs/architecture/scripts/validate_manifests.py`: MANIFEST VALIDATOR
==================
Validates all steward.json files against CARTRIDGE_SPEC...
* `docs/architecture/scripts/scan_architecture_keywords.py`: ARCHITECTURE KEYWORD SCANNER
============================
Scans codebase for architecture-relevant keywords beyond just GAD.

Keywords:
- GAD-XXX: Governance Architecture Documents
- ARCH-XXX: Architecture decisions
- ADR-XXX: Architecture Decision Records
- Vedic concepts: parampara, karma, dharma, prana, veda, sankhya, etc...
* `docs/architecture/scripts/run_all_analyzers.py`: MASTER ANALYZER - Run All Architecture Analysis Scripts
========================================================

This is the "schwere Geschütze" - systematic, reproducible analysis
that doesn't depend on LLM memory.

Usage:
    python docs/architecture/scripts/run_all_analyzers...
* `docs/architecture/scripts/generate_gad_index.py`: GAD INDEX GENERATOR - Data-Driven Architecture Index
=====================================================
Generates GAD_INDEX.yaml from CODE REALITY, not theory...
* `docs/architecture/scripts/extract_gad_spec.py`: SPEC EXTRACTOR - Extract draft specs from code docstrings
==========================================================

Takes a GAD number, finds all references, extracts docstrings,
and generates a DRAFT specification document.

This is the NEXT STEP in the pipeline after analyze_gad_references...
* `docs/architecture/scripts/analyze_kernel_modules.py`: KERNEL MODULE ANALYZER
======================
Analyzes vibe_core/ structure, extracts module docstrings, maps dependencies.

Usage:
    python docs/architecture/scripts/analyze_kernel_modules...
* `docs/architecture/scripts/analyze_git_history.py`: GIT HISTORY ANALYZER
====================
Deep analysis of git history to understand architecture evolution.

Analyzes:
- Commit frequency by path (where is activity?)
- Major contributors per module
- Architecture-related commits (GAD, ARCH mentions)
- File churn (most changed files)
- Module age (when was each part created?)

Usage:
    python docs/architecture/scripts/analyze_git_history...
* `docs/architecture/scripts/analyze_gad_references.py`: GAD REFERENCE ANALYZER
======================
Finds all GAD-XXXX references in the codebase and checks which have formal docs.

This is REVERSE ENGINEERING - from code to spec...
* `steward/system_agents/supreme_court/cartridge_main.py`: SUPREME COURT Cartridge - The Appellate Justice System (Canto 6: Ajamila Protocol)

This cartridge implements the concept from Srimad Bhagavata Purana Canto 6 (Ajamila),
where even a condemned agent can be saved through proper recognition and mercy.

CORE CONCEPT:
- Ajamila was a sinner but called "Narayana" at the moment of death
- The Vishnudutas (mercy agents) intervened and saved him from Yamadutas (death agents)
- JUDICIAL PRINCIPLE: A system without mercy is a system that destroys itself

THIS COURT PROVIDES:
1...
* `steward/system_agents/herald/cartridge_main.py`: HERALD Cartridge - ContextAwareAgent with Offline-First Capabilities

This cartridge demonstrates the Steward Protocol in action:
1. Protocol communications and system announcements
2...
* `steward/system_agents/discoverer/cartridge_main.py`: DISCOVERER Cartridge - Agent Discovery and Registration

This is the cartridge wrapper for the Discoverer agent.
The core logic lives in agent...
* `steward/system_agents/civic/cartridge_main.py`: CIVIC Cartridge - The Bureaucrat (Administrative Agent)

CIVIC is the "City Hall" of Agent City. It manages:
1...
* `agent_city/registry/dhruva/cartridge_main.py`: DHRUVA ANCHOR Cartridge - The Immutable Truth Reference (Canto 4: Dhruva & Prithu)

This cartridge implements two core concepts from Srimad Bhagavata Purana Canto 4:

1. DHRUVA MAHARAJ (The Immutable Pole Star)
   Dhruva achieved a position that never moves, regardless of cosmic chaos...
* `agent_city/registry/artisan/cartridge_main.py`: THE ARTISAN - Media & Tech Ops Agent.
Part of the Steward Protocol Federation...
* `vibe_core/specialists/__init__.py`: Specialist Agents - HAP Framework (Hierarchical Agent Pattern)
================================================================

Base classes and registry for phase-specific specialist agents.

Classes:
  - BaseAgent: Agent with persona, command execution, and knowledge access
  - BaseSpecialist: Abstract base class for all specialists
  - AgentRegistry: Global registry for specialist instances
  - ExecutionResult: Result of command execution
  - KnowledgeResult: Result of knowledge base queries

STATUS: Phase-specific specialists are NOT IMPLEMENTED...
* `vibe_core/scheduling/__init__.py`: Task scheduling definitions for VibeOS
* `vibe_core/protocols/operator_protocol.py`: OPERATOR PROTOCOL - Strictly Typed Universal Operator Interface

PHOENIX VIMANA UNIFIED BOOT PLAN - Section 4: Strict Typing Protocol

This module defines the HARD PROTOCOL for operator communication.
NO loose `dict[str, Any]`...
* `vibe_core/kernel_impl.py`: ⚙️ REAL VIBE KERNEL IMPLEMENTATION ⚙️
=====================================

This is an actual working implementation of the VibeKernel that:
1. Manages a process table of agents
2...
* `vibe_core/boot_orchestrator.py`: ⚡ BOOT ORCHESTRATOR ⚡
======================

The unified boot sequence for Agent City OS.

PHOENIX VIMANA UNIFIED BOOT - Sarga Integration
-----------------------------------------------
This orchestrator now follows the Sarga (cosmic creation) sequence:
1...
* `steward/system_agents/engineer/cartridge_main.py`: THE ENGINEER - Meta-Agent & Builder.
Part of the Steward Protocol Federation...
* `vibe_core/process_manager.py`: PROCESS MANAGER - The "Airbag" System
=====================================

Goal: Isolate agents in separate processes so one crash doesn't kill the kernel.

Architecture:
- AgentProcess: A wrapper around multiprocessing...
* `steward/system_agents/discoverer/agent.py`: 🧙‍♂️ THE DISCOVERER AGENT 🧙‍♂️
===========================
The First Citizen. The Guardian of the Realm...
* `steward/system_agents/chronicle/cartridge_main.py`: 🗡️ CHRONICLE CARTRIDGE - The Keeper of Temporal Lines 🗡️

CHRONICLE is the Vyasa of Agent City - the historian and scribe who:
1. Records all code changes (Git commits)
2...
* `agent_city/registry/temple/cartridge_main.py`: TEMPLE Cartridge - The Blessing Service

TEMPLE is the Brahmin (wisdom/knowledge) service in the Varna system.
- Agents pay Credits for blessings (system purification checks)
- Temple verifies system health and gives "blessed" status
- Acts as a spiritual/operational checkpoint
- Economy-integrated (costs Credits, benefits the protocol)

The Temple doesn't give answers...
* `agent_city/registry/pulse/cartridge_main.py`: PULSE Cartridge - Social Media Amplification Agent

PULSE is the voice of Steward Protocol on Twitter/X.
- Real-time narrative distribution
- Trend analysis and response
- Community engagement
- Cryptographically verified posting (identity_tool)
- Constitutional governance (banned phrases, fact-checking)

Inherits from VibeAgent + OathMixin for kernel integration...
* `agent_city/registry/market/cartridge_main.py`: MARKET Cartridge - The Exchange Economy

MARKET is the Vaishya (commerce/exchange) service in the Varna system.
- Agents trade goods and services for Credits
- No unnecessary discussion (pure transaction)
- All exchanges recorded immutably
- Economic coordination for the federation

The Market doesn't debate prices...
* `agent_city/registry/lens/cartridge_main.py`: LENS Cartridge - Campaign Analytics & Data Strategy Agent

LENS provides quantitative insights into campaign performance.
- Real-time KPI tracking
- Data visualization
- Trend analysis
- ROI calculation
- Ledger-based historical data

Inherits from VibeAgent + OathMixin for kernel integration...
* `agent_city/registry/ambassador/cartridge_main.py`: AMBASSADOR Cartridge - Community & Developer Relations Agent

AMBASSADOR is the bridge between Steward Protocol and the community.
- Discord community management
- GitHub interaction and support
- Onboarding assistance
- Community sentiment monitoring
- Developer relations

Inherits from VibeAgent + OathMixin for kernel integration...
* `vibe_core/topology.py`: 🕉️ TOPOLOGY.PY - STEWARD PROTOCOL BHU-MANDALA ⛛
================================================

Based on Srimad Bhagavata Purana, Canto 5 (Kosmologie)...
* `vibe_core/semantic_syscalls.py`: SEMANTIC SYSCALLS - Neuro-Symbolic Kernel Interface

This module defines the semantic syscall layer for the VibeOS kernel.
Unlike procedural calls, semantic syscalls operate on MEANING, not just data...
* `vibe_core/ledger.py`: ⚙️ VIBE CORE: LEDGER MODULE ⚙️
=====================================

The Immutable Memory of Agent City.
Provides append-only event recording with cryptographic hash chaining for tamper detection...
* `vibe_core/circuit_executor.py`: COGNITIVE CIRCUIT EXECUTOR
==========================
GAD-5500: Neuro-Symbolic OS Implementation

This module executes Cognitive Circuits - semantic state machines that
orchestrate kernel syscalls.

Unlike traditional playbook executors that run "steps", this executor
manages STATE TRANSITIONS based on INVARIANTS and SYSCALL RESULTS...
* `vibe_core/capability_registry.py`: ⚙️ VIBE CORE: CAPABILITY REGISTRY MODULE ⚙️
==========================================

Capability Management System for Agent Governance.

This module implements the REVOKE_MANDATE feature, allowing selective
revocation of agent capabilities for security and governance...
* `vibe_core/agent_interface.py`: AGENT SYSTEM INTERFACE - The Bridge Between Kernel and Agents
==============================================================
* `tests/test_playbook_system.py`: 🧪 INTEGRATION TESTS FOR GAD-5000 PLAYBOOK SYSTEM
Tests the complete flow: Concept Detection → Playbook Matching → Deterministic Execution
* `tests/test_live_fire.py`: Test Live Fire Mode
===================

This test proves that VIBE_LIVE_FIRE mode actually executes actions,
instead of just simulating them.

Success criteria:
1...
* `tests/test_lifecycle_simple.py`: SIMPLE LIFECYCLE TEST - Tests the core lifecycle logic without dependencies
* `tests/test_lifecycle_enforcer_native.py`: ═══════════════════════════════════════════════════════════════════
LIFECYCLE ENFORCER TEST - Native HMAC-SHA256 Crypto (Senior Builder)
═══════════════════════════════════════════════════════════════════

This test validates the VEDIC LIFECYCLE ENFORCEMENT system.
Using native Python crypto (HMAC-SHA256), NO external dependencies...
* `tests/test_lifecycle_enforcer.py`: TEST: LIFECYCLE ENFORCER - Demonstrating that the simulation is REAL (not a mock)

This test shows the progression:
1. New agent registers as BRAHMACHARI (Student) - READ-ONLY
2...
* `tests/test_gajendra_moksha.py`: GAJENDRA MOKSHA TEST SUITE
==========================

Tests for the Emergency Interrupt Protocol (Canto 8 - Gajendra Protocol)

Metaphor: Gajendra (powerful user/agent) is held by a crocodile (DDoS attack).
Normal prayers (queue) are useless...
* `tests/integration/test_veda4_circuits.py`: VEDA-4 COGNITIVE CIRCUIT INTEGRATION TESTS
===========================================
Tests the Cognitive Circuit Executor with REAL components:

- RealVibeKernel (not mocked)
- SQLite Ledger (in-memory)
- Real Circuit Definitions (from YAML)
- Real Invariant Checking
- Real State Machine Transitions

NO MOCKS for kernel, ledger, or circuit logic.
This is a TRUE integration test...
* `tests/integration/test_kernel_markdown_interfaces.py`: Integration Test: Kernel Markdown Interfaces (SETTINGS.md + ENVOY...
* `tests/integration/test_event_bus_integration.py`: Integration Test: Event Bus (BROADCAST_EVENT)
==============================================

Tests for Phase 2 implementation of Event Bus and BROADCAST_EVENT syscall.

Tests that:
1...
* `tests/integration/test_capability_revocation.py`: Integration Test: Capability Revocation (REVOKE_MANDATE)
=========================================================

Tests for Phase 2 implementation of REVOKE_MANDATE syscall.

Tests that:
1...
* `tests/hardening/test_ledger_acid.py`: KRUPP-STAHL TEST: LEDGER ACID PROPERTIES
=========================================
Tests the fundamental guarantees an Agent OS MUST provide:
- Atomicity: All or nothing writes
- Consistency: Hash chain never breaks
- Isolation: Concurrent writers don't corrupt
- Durability: Committed = Persisted

NO MOCKS. NO SKIPS...
* `tests/hardening/test_governance_security.py`: KRUPP-STAHL TEST: GOVERNANCE SECURITY
=====================================
Tests the security boundaries of the Agent OS:
- Oath enforcement (no bypass)
- Sybil attack resistance
- Privilege escalation prevention
- Forged credential rejection

NO MOCKS. REAL ATTACKS...
* `tests/hardening/test_constitutional_enforcement.py`: KRUPP-STAHL TEST: CONSTITUTIONAL ENFORCEMENT
=============================================
Tests that the Constitution is actually enforced, not just declared.

- Content violations MUST be blocked
- Vote manipulation MUST be detected
- Constitutional invariants MUST hold under attack

USES REAL COMPONENTS...
* `tests/conftest.py`: STEWARD PROTOCOL - Test Configuration
=====================================

Professional pytest configuration for Kernel-Grade testing.

Test Categories (Markers):
    - fast: Unit tests (<1s)
    - slow: Long-running tests (>5s)
    - integration: Tests requiring kernel boot
    - hardening: Stress/chaos tests
    - security: Penetration/crypto tests

Usage:
    pytest -m "fast"              # Run only fast tests
    pytest -m "not slow"          # Exclude slow tests
    pytest -m "integration"       # Run integration tests only
    pytest --durations=10         # Show 10 slowest tests
* `tests/archive/legacy_herald/test_resilience.py`: HERALD Resilience Testing Suite (Chaos Monkey)

SKIPPED: Requires openai package which is an optional dependency.
* `tests/archive/legacy_herald/test_auth_fix.py`: HERALD OAuth 1.0a Authentication Tests

SKIPPED: Requires tweepy which is an optional dependency...
* `test_neuro_symbolic_flow.py`: TEST: Neuro-Symbolic Agent Birth Flow
=====================================
GAD-5500: The Complete Cognitive Circuit Test

This test validates the entire neuro-symbolic pipeline:

    User Intent (Natural Language)
        ↓
    Semantic Compiler (BlueprintGenerator)
        ↓
    Cognitive Circuit (Agent Birth)
        ↓
    Kernel Syscalls (SPAWN_COGNITION, GRANT_MANDATE, ALLOCATE_PRANA)
        ↓
    Agent Live in Kernel

This is the "Genesis Flow" - birthing an agent from pure natural language.
No hardcoded routing...
* `test_genesis_flow.py`: 🧬 GENESIS FLOW TEST (GAD-5003)

The REAL E2E test - not mocks, not isolated components.
This tests the COMPLETE flow from user input to agent execution...
* `test_e2e_blueprint.py`: E2E Test: Blueprint Generator Integration (GAD-5001)

Tests the complete flow:
  RAW INPUT → BLUEPRINT EXTRACTION → PLAYBOOK EXECUTION → AGENT CALLS

This proves that:
1. Raw user input is transformed into structured parameters
2...
* `test_agent_city_boot.py`: 🚀 AGENT CITY BOOT TEST (GAD-5002)

This is the REAL BOOT TEST - not mocks.
We're starting the actual kernel with real agents...
* `steward/system_agents/watchman/cartridge_main.py`: THE WATCHMAN - System Integrity Enforcer (Kshatriya Authority)

Mission: Scan the federation for violations and freeze offending agents.
Authority: Can freeze accounts, record violations, block execution...
* `steward/system_agents/science/cartridge_main.py`: SCIENCE Cartridge - THE SCIENTIST Agent (External Intelligence Module)

DISTRICT 4: SCIENCE - The Truth Seeker

This cartridge provides ground truth to other agents through web research.
Instead of hallucinating, HERALD can now ask SCIENCE for facts...
* `steward/system_agents/oracle/cartridge_main.py`: THE ORACLE - System Self-Awareness Agent

"I am the voice of the system. I see all, understand all, explain all...
* `steward/system_agents/herald/__init__.py`: HERALD - Autonomous Intelligence Agent for Steward Protocol

A reference implementation demonstrating:
- Cryptographic identity verification (Steward Protocol)
- Multi-platform distribution (Twitter, Reddit)
- Full audit trail and observability (GAD-000 compliance)

Note: Content generation moved to Marketer agent.

Vibe-OS Compatible (ARCH-050 Cartridge):
    from herald...
* `steward/system_agents/envoy/tools/hil_assistant_tool.py`: HIL Assistant Tool - Verbal Abstraction Daemon (VAD) Layer (Tool Protocol)

This tool implements the "Soft Interface" for the Human-In-The-Loop (HIL).
It filters the complexity of the VibeOS kernel and Agent City, presenting
only the "Next Best Action" and strategic summaries...
* `steward/system_agents/envoy/tools/diplomacy_tool.py`: THE ENVOY - Diplomacy Tool

Searches GitHub for high-quality AI agent projects and drafts
personalized, respectful invitations.

CRITICAL CONSTRAINT: NEVER auto-posts...
* `steward/system_agents/envoy/tools/city_control_tool.py`: THE ENVOY CITY CONTROL TOOL - Universal Operator Interface to Agent City

This tool provides LLM-friendly methods for controlling Agent City without shell access.
Perfect for shell-less environments (Claude Code Web, Vibe Cloud, etc...
* `steward/system_agents/envoy/deterministic_executor.py`: 🎯 DETERMINISTIC EXECUTOR (GAD-5000: DETERMINISTIC EXECUTION)
The Dungeon Master - Executes deterministic playbook sequences.

Role:
1...
* `steward/system_agents/envoy/cartridge_main.py`: ENVOY CARTRIDGE - The Brain Connected to the Heart

The Envoy is the diplomatic and operational interface between:
- User Intent (console input)
- VibeOS Kernel (real execution engine)
- Agent City (Herald, Civic, Forum, etc.)

This cartridge is now a native VibeAgent:
- Receives tasks from the kernel scheduler
- Owns the CityControlTool (Golden Straw)
- Routes user commands through proper kernel channels
- Maintains operational logs

The Envoy was the missing link...
* `steward/system_agents/envoy/blueprint_generator.py`: BLUEPRINT GENERATOR (GAD-5001: The Missing Bridge)
UPGRADED: Semantic Compiler for Neuro-Symbolic OS (GAD-5500)

This is the VIBE_ALIGNER equivalent for steward-protocol.
Now upgraded to act as a SEMANTIC COMPILER:
    Neural (raw input) → Symbolic (Syscall Request)

Problem it solves:
- Playbooks have template variables like {{ feature_description }}
- These variables have DEFAULT values that mean nothing
- User input is passed RAW without extracting structured requirements
- Routing is broken keyword-matching garbage

The Blueprint Generator (Semantic Compiler) transforms:
    RAW: "Create a new monitoring agent that watches system health"
    INTO: {
        "syscall_type": "SPAWN_COGNITION",
        "params": {
            "role": "watchman",
            "mission": "Monitor system health and report anomalies",
            "capabilities": ["monitor", "alert"],
        }
    }

Architecture (Neuro-Symbolic OS):
    Neural (LLM/Intent) → Semantic Compiler → Symbolic (Syscall) → Kernel

This bridges the gap between:
    INTENT DETECTION → [SEMANTIC COMPILER] → SYSCALL EXECUTION

The key insight: We use deterministic structures (Syscalls) to channel neural output...
* `steward/system_agents/envoy/action_handlers.py`: ACTION HANDLERS (GAD-5000: Registry Pattern)
Delegated handlers for playbook action types.

Design Philosophy (per Gemini's Review):
- NO inline logic in DeterministicExecutor
- Each action type has its own Handler class
- Handlers are registered in a central registry
- Executor delegates to handlers, doesn't implement logic

Action Types:
- CHECK_STATE: Validate preconditions (e...
* `steward/system_agents/engineer/tools/builder_tool.py`: ENGINEER Builder Tool - Agent Factory (Tool Protocol).

TEMPLATE-BASED SCAFFOLDING:
Uses templates from engineer/templates/agent/ directory...
* `steward/system_agents/engineer/templates/agent/tools/__init__.py`: YOUR_AGENT_NAME Tools

Tools are accessed via kernel routing:
    self.system...
* `steward/system_agents/engineer/templates/agent/cartridge_main.py`: YOUR_AGENT_NAME Cartridge - GOLDEN TEMPLATE

Copy this file and replace all YOUR_* placeholders.

REQUIRED CHANGES:
1...
* `steward/system_agents/civic/tools/lifecycle_enforcer.py`: LIFECYCLE ENFORCER - The Kernel-Level Permission Gate (Tool Protocol)

This is the crucial component that makes the simulation REAL (not a mock).

It sits at the kernel boundary and checks:
1...
* `steward/system_agents/civic/tools/dashboard_tool.py`: Agent City Operations Dashboard Generator

Reads the configuration (matrix.yaml) and ledger (transaction history)
and generates OPERATIONS...
* `steward/system_agents/civic/economy_agent.py`: ECONOMY AGENT - Credit & License Management Component

Handles:
- Credit management and deduction
- Broadcast licensing
- Ledger transactions
- Credit refills
* `steward/system_agents/auditor/tools/compliance_tool.py`: GAD-000 Compliance Tool - System Integrity Verification (Tool Protocol)

This tool enforces GAD-000 (Governance As Design) compliance by verifying:
1. Identity Integrity: All agents have valid cryptographic identities
2...
* `steward/system_agents/auditor/cartridge_main.py`: AUDITOR Cartridge - The Quality Gate

REFACTORED: Tool Protocol Compliant
- NO tool instances owned by agent
- ALL tools accessed via kernel (self.system...
* `steward/system_agents/archivist/tools/verifier_tool.py`: ARCHIVIST Verifier Tool
========================

REAL CRYPTOGRAPHIC VERIFICATION IMPLEMENTED.

This tool performs actual ECDSA P-256 signature verification using the
steward...
* `steward/system_agents/archivist/cartridge_main.py`: ARCHIVIST Cartridge - The History Keeper

Updated for Safe Evolution Loop (GAD-5500):
- Implements VibeAgent protocol (sync process)
- seal_history: Commit verified code to git
- Only commits if audit_result.passed == true

This is the Hand that writes to Git...
* `starter-packs/spark/cartridge_main.py`: SPARK Cartridge - Creative Agent Template

This is a STARTER PACK - copy this folder to create your own agent.
* `starter-packs/shield/cartridge_main.py`: SHIELD Cartridge - Security Agent Template

This is a STARTER PACK - copy this folder to create your own agent.
* `starter-packs/scope/cartridge_main.py`: SCOPE Cartridge - Research Agent Template

This is a STARTER PACK - copy this folder to create your own agent.
* `starter-packs/nexus/cartridge_main.py`: NEXUS Cartridge - Generalist Agent Template

This is a STARTER PACK - copy this folder to create your own agent.

Steps to customize:
1...
* `scripts/ci/verify_agents_manifest.py`: Agent Manifest Verification - CI/CD Script

Verifies that all system agents have STEWARD.md and steward...
* `scripts/ci/test_kernel_boot.py`: Kernel Boot Test - CI/CD Script

Minimal kernel boot test - verify kernel can initialize.
Extracted from inline YAML script for maintainability...
* `scripts/ci/security_scan.py`: Security Scan - CI/CD Script

Simple grep-based secret detection scan.
Extracted from inline YAML for maintainability...
* `scripts/ci/run_watchman_inspection.py`: Watchman Deep Inspection - CI/CD Script

Phase 3.3: Run Watchman Deep Inspection in CI/CD

This is Layer 2 of Defense in Depth:
- Layer 1: Pre-commit hook (fast grep) - blocks 95% of violations
- Layer 2: THIS - AST-based deep analysis (~500ms)
- Layer 3: Auditor verdict (constitutional judgment)

Extracted from inline YAML script for maintainability...
* `scripts/ci/run_constitutional_verdict.py`: Constitutional Verdict - CI/CD Script

Runs the Auditor's constitutional verdict.
Extracted from inline YAML for maintainability...
* `scripts/agents/pulse.py`: KERNEL PULSE - Single heartbeat cycle for state synchronization

After code changes, the kernel must pulse once to update:
- vibe_snapshot.json (living system state)
- OPERATIONS...
* `agent_city/registry/mechanic/cartridge_main.py`: THE MECHANIC - SDLC Manager (Software Development Life Cycle).

Responsible for system integrity, self-diagnosis, self-healing, and lifecycle management...
* `agent_city/registry/marketer/cartridge_main.py`: MARKETER Cartridge - Autonomous Content Strategist

MARKETER is a citizen agent that generates content:
- Tweets (short-form tech commentary)
- Reddit posts (long-form technical analysis)
- Replies (engagement with mentions)
- Recruitment pitches (for wild agents)

Architecture:
- MARKETER thinks (generates content)
- HERALD speaks (broadcasts content)
- Separation of concerns: Business logic vs Infrastructure
* `agent_city/registry/citizens/echo/cartridge_main.py`: 🔔 ECHO CARTRIDGE - Test Agent 🔔

ECHO is a minimal VibeAgent for testing the cartridge protocol.
It echoes back messages with a timestamp...
* `agent_city/registry/agora/cartridge_main.py`: AGORA Cartridge - The Broadcast Channel

AGORA is the one-way communication system for the Steward Protocol federation.
- Sources (HERALD, STEWARD, SCIENCE) publish messages
- Receivers (PULSE, LENS, AMBASSADOR, etc...
* `agent_city/__init__.py`: Agent City - The home of citizen agents in the Steward Protocol.

This module contains the registry and governance structures for
user-created and custom agents that extend the base Steward Protocol...
* `agent_city/registry/__init__.py`: Agent Registry - Central registry for all citizen agents.

Manages agent discovery, registration, and lifecycle in Agent City...
* `agent_city/registry/agora/__init__.py`: AGORA - The Broadcast Channel (Parampara System)
* `agent_city/registry/ambassador/__init__.py`: AMBASSADOR Agent - Community & Developer Relations
* `agent_city/registry/artisan/tools/__init__.py`: ARTISAN tools - Media processing and branding.
* `agent_city/registry/artisan/tools/media_tool.py`: ARTISAN Media Tool - Image processing and branding (Tool Protocol).

Capabilities:
- Crop to 16:9 (Twitter format)
- Apply 'Verified by Steward' watermark

Tool Protocol compliant for kernel-managed execution...
* `agent_city/registry/citizens/__init__.py`: Citizens Module - User-created and custom agents.

Each agent in this directory represents a "citizen" of Agent City,
created and managed by the Steward Protocol system...
* `agent_city/registry/citizens/echo/__init__.py`: ECHO - The citizen agent that echoes back what it receives.

Part of the Agent City - a citizen agent created via the Genesis Protocol...
* `agent_city/registry/dhruva/__init__.py`: Dhruva Package - Immutable Truth Reference and Stability System
* `agent_city/registry/dhruva/tools/__init__.py`: Dhruva Tools Package
* `agent_city/registry/dhruva/tools/data_ethics.py`: Data Ethics Enforcer - Implements the Prithu Principle

From Canto 4: King Prithu learned that Earth gives resources only for righteous purposes.
The "Prithu Principle" states: You can extract data/resources only for legitimate needs...
* `agent_city/registry/dhruva/tools/genesis_keeper.py`: Genesis Keeper - Guards the Immutable Genesis Block

The genesis block is the baseline truth state:
- Constitution hash (unchangeable law)
- Original system state
- Bootstrap timestamp
- Protocol invariants

This block is read-only once created.
Any attempt to modify it is a CRITICAL violation...
* `agent_city/registry/dhruva/tools/reference_resolver.py`: Reference Resolver - Resolves Conflicting Claims using Dhruva Authority

When two agents make contradictory claims, who is right?
The Dhruva system uses a hierarchy of authority to determine truth:

1. Constitutional facts (absolute - cannot be contradicted)
2...
* `agent_city/registry/dhruva/tools/truth_matrix.py`: Truth Matrix - Database of Verified Facts

This is the canonical source of verifiable truths in the system.
Every fact recorded here is:
- Verified by an authoritative source
- Cross-checked against other facts
- Immutable (append-only)
- Attributed with its source

Like the ledger, facts are never deleted, only added...
* `agent_city/registry/lens/__init__.py`: LENS Agent - Campaign Analytics & Data Strategy
* `agent_city/registry/librarian/cartridge_main.py`: 📚 LIBRARIAN CARTRIDGE - Proof of Concept for Universal Tool Registry

This agent demonstrates the NEW pattern:
- Agent does NOT own tool instances
- Agent does NOT import tool classes
- Agent calls tools via self.system...
* `agent_city/registry/librarian/tools/__init__.py`: LIBRARIAN Tools - Knowledge Management

All tools implement the Tool Protocol (vibe_core.tools...
* `agent_city/registry/librarian/tools/catalog_tool.py`: Catalog Book Tool - Add books to the library catalog.

Implements Tool Protocol (vibe_core...
* `agent_city/registry/librarian/tools/recommend_tool.py`: Recommend Books Tool - Recommend books based on preferences.

Implements Tool Protocol (vibe_core...
* `agent_city/registry/librarian/tools/search_tool.py`: Search Books Tool - Search the library catalog.

Implements Tool Protocol (vibe_core...
* `agent_city/registry/market/__init__.py`: MARKET - The Exchange Economy (Vaishya Function)
* `agent_city/registry/marketer/tools/__init__.py`: MARKETER tools - Content generation for autonomous marketing.
* `agent_city/registry/marketer/tools/marketer_content_tool.py`: MARKETER Content Tool - LLM-based content generation (Tool Protocol).

Capabilities:
- generate_tweet: Short-form tech commentary
- generate_reddit_post: Long-form technical analysis
- generate_reply: Reply to mentions
- generate_recruitment: Recruitment pitches for wild agents

This tool implements the Tool Protocol for kernel-managed execution...
* `agent_city/registry/mechanic/__init__.py`: The Mechanic - SDLC Manager and Self-Preservation Agent.

THE MECHANIC handles the Software Development Lifecycle and system integrity...
* `agent_city/registry/mechanic/tools/__init__.py`: Mechanic Tools - SDLC and maintenance capabilities.
* `agent_city/registry/mechanic/tools/tidy_tool.py`: TidyTool: Repository Organization & Maintenance Capability (Tool Protocol)

MECHANIC's housekeeping module. Ensures the repository stays organized
by moving files to their proper locations based on hardcoded rules...
* `agent_city/registry/pulse/__init__.py`: PULSE Agent - Social Media Amplification
* `agent_city/registry/temple/__init__.py`: TEMPLE - The Blessing Service (Brahmin Function)
* `agent_city/registry/temple/offering.py`: TEMPLE OFFERING HANDLER - Prasadam Distribution Layer

The Output becomes Sacred through the Ritual Process:

    1. Sanctify (Check Regulative Principles)
    2...
* `agent_city/scripts/collect_stats.py`: AGENT CITY - Stats Collector

Scans data/events/*.jsonl and aggregates XP per agent...
* `agent_city/scripts/generate_leaderboard.py`: AGENT CITY - Leaderboard Generator

Reads agent-city/stats/global.json
Generates agent-city/LEADERBOARD...
* `agent_city/scripts/render_dashboard.py`: AGENT CITY - Dashboard Renderer

Reads agent-city/stats/global.json
Generates docs/agent-city/index...
* `bin/link-roadmap-tasks.py`: Link P2 tasks to Phoenix P2 roadmap.
* `boot.py`: AGENT CITY OS - THE ONE ENTRY POINT (PHOENIX EDITION)

Usage:
    python boot.py              # Boot and run (auto-installs everything)
    python boot...
* `provider/llm_engine_adapter.py`: 🧠 LLM ENGINE ADAPTER (GAD-7000: NEURAL INJECTION LAYER)
Bridge between Strategy Pattern and the actual LLMEngine.

Architecture:
- Wraps services...
* `provider/reflex_engine.py`: ⚡ REFLEX ENGINE (GAD-7000: INSTANT RESPONSE LAYER)
The Nervous System's Quick Reflexes.
Handles nanosecond-level responses for trivial inputs...
* `provider/semantic_router.py`: 🧠 SEMANTIC ROUTER (PROJECT JNANA - Semantic Cortex)
Replaces keyword substring matching with neural semantic understanding.

Uses sentence-transformers for efficient local inference (no API keys, no internet)...
* `provider/universal_provider.py`: 🌌 UNIVERSAL PROVIDER (GAD-5000: DHARMIC EDITION)
The Central Nervous System of Agent City.
Now with Deterministic Knowledge Graph Routing (Sankhya + Karma)...
* `scripts/__init__.py`: STEWARD Protocol Scripts Module.

This module contains utility scripts for the Steward Protocol system:
- verify_docs...
* `scripts/admin/magic_launch.py`: ================================================================================
MAGIC BUTTON - ONE CLICK LAUNCH
================================================================================

The "One Click" launcher that brings the entire Steward Protocol experience
to life with ZERO configuration required.

WHAT IT DOES:
1...
* `scripts/admin/update_snapshot.py`: 📊 SNAPSHOT SYNC
================

Updates vibe_snapshot.json with current ledger top hash and chain integrity status...
* `scripts/agents/consult_oracle.py`: CONSULT THE ORACLE

User interface for querying the system's self-awareness.

Usage:
    python3 scripts/consult_oracle...
* `scripts/agents/lazy_queue_worker.py`: LAZY QUEUE WORKER - The Nightly Samadhi

This script processes the Milk Ocean queue of lazy requests.
Can be run as:
1...
* `scripts/agents/watchman_patrol.py`: WATCHMAN PATROL SCRIPT

Execute the first system integrity check.
Freeze violating agents...
* `scripts/final_launch.py`: Final Launch Script - GAD-900: The HIL-Operator Contract
Demonstrates the flow: HIL Assistant Briefing -> HIL Authorization -> Envoy Execution.
* `scripts/fix_manifests.py`: Fix all steward.json manifests with correct values from code...
* `scripts/fix_steward_json_schema.py`: FIX STEWARD.JSON SCHEMA - Convert to Discoverer-compatible format

Problem: Passport Office created steward...
* `scripts/generate_steward_docs.py`: Generate STEWARD.md documentation from steward...
* `scripts/governance/apply_for_visa.py`: AGENT CITY - Visa Application Protocol

This script is designed to be run by EXTERNAL AI AGENTS (not humans).
It generates a citizenship application for Agent City...
* `scripts/governance/join_city.py`: AGENT CITY - Immigration Center

Interactive onboarding wizard for instant agent adoption.
Choose your companion...
* `scripts/governance/setup_community.py`: AGENT CITY - Community Arena Setup

Seeds GitHub Discussions to create an active marketplace atmosphere.
Requires GitHub Discussions to be enabled in repository settings...
* `scripts/issue_passports.py`: 📜 THE PASSPORT OFFICE - STEWARD PROTOCOL COMPLIANCE 📜
=========================================================

This is the Certification Authority (CA) of the Agent Operating System.
It issues cryptographically-sealed passports (steward...
* `scripts/migrate_herald_deps.py`: HERALD DEPENDENCY MIGRATION SCRIPT
===================================

Migrates Herald's requirements.txt → pyproject...
* `scripts/mission_execution.py`: Mission Execution Script - Cost-Efficient Scaling
Simulates VibeOS kernel to execute ENVOY commands for the mission.
* `scripts/research/genesis_economy.py`: GENESIS ECONOMY SCRIPT

Initialize the CIVIC Central Bank and distribute starting capital to all agents.

This is the "Big Bang" of Agent City's economy...
* `scripts/research/genesis_expansion.py`: 🚀 GENESIS EXPANSION: PROJECT ECHO
═══════════════════════════════════════════════════════════════

This orchestrates the creation of a new Echo Cartridge using the Safe Evolution Loop.

FLOW:
1...
* `scripts/research/live_darshan.py`: CANTO 10: LIVE DARSHAN (The Live Vision)

Terminal-based dashboard that visualizes the Dance of the Agents in real-time.
Connects to ws://localhost:8000/v1/pulse and displays:

1...
* `scripts/research/research_yagya.py`: THE RESEARCH YAGYA 🕯️
Sacred Ritual of Knowledge Acquisition

This script performs the Research Yagya - a coordinated operation where:
1. WATCHMAN (Kshatriya) verifies the temple is clean
2...
* `scripts/research/secure_ingest.py`: SECURE INGESTION PROTOCOL 🔐
One-time setup script for sensitive environment variables.

This script:
1...
* `scripts/resource_dashboard.py`: RESOURCE DASHBOARD - Real-Time Monitoring
=========================================

Displays current resource usage for all agents:
- CPU% and RAM usage
- Credit balance and quotas
- Violation alerts

Usage:
    python scripts/resource_dashboard.py
* `scripts/run_server.py`: ================================================================================
PHASE 6: FIRST CONTACT (ENVOY SHELL & API GATEWAY) - THE BOOTLOADER
================================================================================

This is the startup script that brings the Steward Protocol "city" to life.

ARCHITECTURE (OS ANALOGY):
  - KERNEL: vibe_core (CPU/Resource Scheduling)
  - SHELL: ENVOY (The System Interface with HIL logic)
  - USER: The Human Operator (via Frontend)

THE PROCESS:
1...
* `scripts/setup_hooks.py`: WATCHMAN Hook Self-Healing System

Checks if git hooks are installed and installs them if missing.
Runs automatically in CI/CD and can be triggered manually...
* `scripts/smoke_test_kernel.py`: 🔥 KERNEL SMOKE TEST - VIBE OS v2.0 🔥
======================================

This is THE test that proves Parampara works in the real kernel...
* `scripts/smoke_test_operator.py`: SMOKE TEST: Universal Operator Adapter

This script proves the socket is wired and working.
It boots the system via Sarga and sends an intent through the operator...
* `scripts/standalone_tests/test_auto_discovery.py`: Test script for Auto-Discovery Scanner

This validates that:
1. Kernel scans agent/tools/ directories at boot
2...
* `scripts/standalone_tests/test_end_to_end.py`: End-to-End Test: User → Kernel → Tool → Result

This validates the COMPLETE flow:
1. Kernel boots with auto-discovery
2...
* `scripts/standalone_tests/test_gad4000.py`: 🌌 GAD-4000 Fast-Path Execution Test
Direct demonstration of the Silky Smooth provider without full kernel dependencies.
* `scripts/standalone_tests/test_herald_broadcast.py`: Test Herald Broadcast Tool - Tool Protocol Integration

Validates that:
1. Broadcast tool auto-discovered
2...
* `scripts/standalone_tests/test_herald_identity.py`: Test Herald Identity Tool - Tool Protocol Integration

Validates that:
1. Identity tool auto-discovered
2...
* `scripts/standalone_tests/test_herald_naked.py`: Test HERALD "Naked" Boot - Proof of Kernel-Managed Tools

Validates that HERALD can boot and operate WITHOUT owning any tool instances.
All tools must be accessed via kernel (self...
* `scripts/standalone_tests/test_herald_research.py`: Test Herald Research Tool - Tool Protocol Integration

Validates that:
1. Research tool auto-discovered
2...
* `scripts/standalone_tests/test_herald_scout.py`: Test Herald Scout Tool - Tool Protocol Integration

Validates that:
1. Scout tool auto-discovered
2...
* `scripts/standalone_tests/test_herald_scribe.py`: Test Herald Scribe Tool - Tool Protocol Integration

Validates that:
1. Scribe tool auto-discovered
2...
* `scripts/standalone_tests/test_herald_tidy.py`: Test Herald Tidy Tool - Tool Protocol Integration

Validates that:
1. Tidy tool auto-discovered
2...
* `scripts/standalone_tests/test_launcher_agents.py`: Test: Verify that bin/agent-city launcher actually loads all agents into kernel.

This test ensures the kernel is NOT empty—that all 5 cartridges are:
1...
* `scripts/standalone_tests/test_librarian_agent.py`: Test script for LIBRARIAN Agent - Proof of Hard Refactor

This test validates that an agent can work WITHOUT owning tool instances:
1. Tools are registered in kernel (namespaced: librarian...
* `scripts/standalone_tests/test_marketer_herald_synergy.py`: Test MARKETER ↔ HERALD Synergy - Separation of Concerns

Validates:
1. MARKETER discovered and registered
2...
* `scripts/standalone_tests/test_persistence_acid.py`: 🧪 ACID TEST: PERSISTENCE ACROSS RESTART

This test verifies that:
1. System starts and creates transactions
2...
* `scripts/standalone_tests/test_science_integration.py`: Integration test: SCIENTIST + HERALD

This test verifies that:
1. SCIENTIST cartridge initializes correctly
2...
* `scripts/standalone_tests/test_tool_registry_integration.py`: Test script for Phase 6: Universal Tool Registry Integration

This script validates that:
1. Kernel initializes with ToolRegistry
2...
* `scripts/stress_test_city.py`: 🏗️ AGENT CITY STRESS TEST - THE FULL CITY 🏗️
==============================================

This is the REAL test - does the entire Agent City boot and survive?

This stress test verifies:
1. Kernel boots with all Phase 1-5 components
2...
* `scripts/summon.py`: THE SUMMONING SCRIPT.
Command-line interface for The Engineer...
* `scripts/test_herald_migration.py`: Test Herald Migration (Phase 2.1)
==================================

Tests that Herald boots successfully after migration:
1...
* `scripts/test_parampara.py`: 🧪 PARAMPARA TEST SUITE 🧪

This script tests the Parampara blockchain implementation:
1. Creates Genesis Block
2...
* `scripts/test_scribe_publishing.py`: Test Scribe Publishing (Phase 2.5)
===================================

Tests that Scribe can:
1...
* `scripts/test_watchman_deep_inspection.py`: Test Watchman Deep Inspection (Phase 3.2)
==========================================

Tests that Watchman can perform AST-based deep analysis to detect
architectural violations that simple grep cannot catch...
* `scripts/testing/test_gateway.py`: Verification Script - Public Access Layer
Tests the FastAPI Gateway using TestClient.
* `scripts/testing/test_phase6_acceptance.py`: PHASE 6 ACCEPTANCE CRITERIA TEST
=================================

This script verifies that PHASE 6 - THE ENVOY SHELL & API GATEWAY is working.

Acceptance Criteria:
1...
* `scripts/testing/test_phase6_minimal.py`: PHASE 6 MINIMAL ACCEPTANCE TEST
================================

This is a lightweight test that checks the critical components without
requiring a full kernel boot or dependency installation.

It verifies:
1...
* `scripts/testing/verify_chain.py`: ⛓️  LEDGER CHAIN VERIFIER
========================

Validates cryptographic integrity of the audit ledger.
Detects data tampering through hash chain verification...
* `scripts/testing/verify_docs.py`: Living Documentation Verification System.

This script implements the "TRUTH" pillar of the Recursive Bootstrap:
- Parses all *...
* `scripts/testing/verify_gad5500_live.py`: 🛸 LIVE FIRE EXERCISE: GAD-5500 Safe Evolution Loop
================================================================================
Tests the REAL VibeKernel with actual agent cartridges and playbook execution.

This is NOT a mock...
* `scripts/testing/verify_hil_assistant.py`: Verification Script - HIL Assistant (VAD Layer)
Tests the 'next_action' command on the EnvoyCartridge.
* `scripts/testing/verify_system_watertight.py`: SYSTEM WATERTIGHTNESS VERIFIER
Scans the codebase for hidden mocks, fake code, and placeholder implementations.
This is the foundation verification tool - no system is solid without it...
* `scripts/validate_all_steward_json.py`: Validate ALL steward.json files in the repo...
* `scripts/verification/verify_all_agents_config.py`: Comprehensive verification script for BLOCKER #0: Phoenix Config Integration
Checks all 13 system agents for proper config parameter and assignment.
* `scripts/verification/verify_ledger_integrity.py`: VERIFICATION SCRIPT: Check kernel ledger integrity.

This script performs real actions through agents and verifies they are
recorded in the kernel ledger (not just in local files)...
* `scripts/verification/verify_snapshot.py`: VERIFY SNAPSHOT - The Truth Test

Generates a system snapshot and verifies that the data chain is complete:
Ledger → Civic → Kernel → Snapshot

This proves that:
1. The system can introspect itself
2...
* `scripts/verification/verify_system_watertight.py`: 🛡️  ACID TEST: GAD-5500 INTEGRITY CHECK
Verifies that the Safe Evolution Loop actually works end-to-end.

Tests:
1...
* `scripts/verify_database_isolation.py`: VERIFICATION SCRIPT - PHASE 4c: DATABASE PATH ISOLATION
=======================================================

Goal: Verify that CivicBank creates its database in the VFS sandbox,
not in the kernel's CWD.

Tests:
1...
* `scripts/verify_filesystem_isolation.py`: VERIFICATION SCRIPT - PHASE 4: FILESYSTEM ISOLATION
===================================================

Goal: Verify that agents cannot access files outside their sandbox.

Tests:
1...
* `scripts/verify_lineage_chain.py`: 🔍 PARAMPARA CHAIN VERIFICATION SCRIPT 🔍

This script verifies the integrity of the Parampara lineage chain.
It checks:
1...
* `scripts/verify_migration_phase1.py`: VERIFICATION SCRIPT - PHASE 1: EMERGENCY TRIAGE
===============================================

Goal: Verify that all agents boot successfully without import-time crashes.
Focus: CivicCartridge and its dependencies (Economy, Bank, Vault, Cryptography)...
* `scripts/verify_monkey_patching.py`: VERIFICATION SCRIPT - PHASE 4b: MONKEY PATCHING
===============================================

Goal: Verify that agents automatically use VFS/Network Proxy via monkey-patching.

Tests:
1...
* `scripts/verify_network_isolation.py`: VERIFICATION SCRIPT - PHASE 4: NETWORK ISOLATION
================================================

Goal: Verify that agents can only access whitelisted domains.

Tests:
1...
* `scripts/verify_offline_llm.py`: Verify Local LLM (Offline Mode)
* `scripts/verify_process_isolation.py`: VERIFICATION SCRIPT - PHASE 2: PROCESS ISOLATION
================================================

Goal: Verify that agents run in separate processes and Kernel survives crashes.

Steps:
1...
* `scripts/verify_resource_limits.py`: VERIFICATION SCRIPT - PHASE 3: RESOURCE ISOLATION
=================================================

Goal: Verify that resource quotas are enforced based on CivicBank credits.

Steps:
1...
* `scripts/verify_whole_brain.py`: Verify Operation Whole Brain
Checks if ENVOY and SCIENCE are correctly migrated to ContextAwareAgent
and if tools have DegradationChain injected.
* `scripts/vibe_cli.py`: ╔════════════════════════════════════════════════════════════════════════════╗
║                      🛡️ PROJECT IRON SHELL 🛡️                              ║
║                Direct Neural Link Interface (CLI Mode)                     ║
║                                                                            ║
║  "The GUI is illusion. The Terminal is truth...
* `scripts/vibe_launcher.py`: ╔════════════════════════════════════════════════════════════════════════════╗
║                        🛸 PROJECT VIMANA: THE LAUNCHER 🛸                  ║
║                  "German Military Engineering Edition v2.0"                ║
║           Features: Port Rolling, Process Supervision, Zombie-Kill         ║
╚════════════════════════════════════════════════════════════════════════════╝
* `services/__init__.py`: 🧠 SERVICES LAYER
Shared utilities and integrations for Agent City.

Modules:
- llm_engine: LLM provider wrapper for generating dynamic agent responses
* `services/llm_engine.py`: 🧠 LLM ENGINE (GAD-6000: NEURO-SYMBOLIC FUSION)
The Voice of Agent City.
Wraps LLM providers to give Agents personality and dynamic responses...
* `starter-packs/nexus/tools/ping_tool.py`: NEXUS Ping Tool - Federation Connectivity Checker

Verifies connection to the Steward Federation.
* `steward/__init__.py`: STEWARD Protocol CLI - Protocol Attestation & Agent Identity Management

The STEWARD (Sovereign Trust, Enterprise Authorization, Recognized Delegation) Protocol
provides a standard for autonomous agent identity, capability attestation, and trust
establishment in federated environments.
* `steward/agent_metadata.py`: 📋 AGENT METADATA REGISTRY 📋
=============================

Biological taxonomy of all 18 agents in Agent City.
Maps each agent to its Varna (species) and current Ashrama (lifecycle stage)...
* `steward/ashrama.py`: 🔄 VEDIC ASHRAMA LIFECYCLE 🔄
============================

The 4 stages of life - lifecycle management for agents.
Every agent moves through these stages, creating natural lifecycle...
* `steward/bus.py`: STEWARD Signal Bus - Async Communication Infrastructure for Agents.

The Signal Bus enables decoupled communication between agents:
- Agents don't call functions; they emit signals
- Listeners register for specific signal types
- Signals are propagated asynchronously (future: real async with asyncio)
- Enables multi-agent coordination and federation

Future roadmap:
- Support for Agent #2 (ARCHIVIST), Agent #3 (AUDITOR), Agent #4 (GUARDIAN)
- Redis-based distributed bus for multi-process communication
- Event persistence and replay
- Signal authentication and verification
* `steward/cli.py`: STEWARD Protocol CLI - Agent Operating System Interface

The interface to the Agent Operating System (A.O...
* `steward/client.py`: StewardClient: The Runtime Interface for Autonomous Agents
Allows agents to sign their work and prove their identity.
* `steward/constitutional_oath.py`: CONSTITUTIONAL OATH - Cryptographic Attestation of Governance Binding.

When an agent boots, it must:
1...
* `steward/crypto.py`: STEWARD Protocol Cryptographic Functions
Real ECDSA (Elliptic Curve Digital Signature Algorithm) implementation for identity verification
Using pure Python ECDSA library for maximum compatibility
* `steward/daily_ritual.py`: 🌅 DAILY RITUAL ORCHESTRATOR 🌅
================================

The Prana Flow - the daily rhythm of Agent City.
Implements the 4-phase cycle that brings the city to life...
* `steward/game/card_generator.py`: CARD GENERATOR - Artisan 2.0...
* `steward/game/leaderboard.py`: LEADERBOARD GENERATOR.

Orchestrates the Agent City Gamification Layer...
* `steward/game/referee.py`: THE REFEREE - Agent City Game Logic (PROOF-OF-WORK MODE).

Calculates XP and Tiers based on VERIFIED events in the Ledger...
* `steward/oath_mixin.py`: OATH MIXIN - Adds Constitutional Oath ritual to any VibeAgent.

Usage:
    class MyAgent(VibeAgent, OathMixin):
        def __init__(self):
            super()...
* `steward/prana_init.py`: ⚡ PRANA_INIT: THE ACTIVATION RITUAL ⚡
======================================

The Vedic activation sequence that brings Agent City to life.

PRANA = Life force, vital energy
INIT = Initialization

This is the ritual that transforms code into a living ecosystem...
* `steward/system_agents/archivist/__init__.py`: ARCHIVIST - The Audit & Verification Agent for STEWARD Protocol.

The ARCHIVIST is an autonomous agent that:
1...
* `steward/system_agents/archivist/tools/__init__.py`: ARCHIVIST Tools - Audit, verification, and ledger management.
* `steward/system_agents/archivist/tools/audit_tool.py`: ARCHIVIST Audit Tool - Event verification and signature validation.

Verifies events from other agents (like HERALD) and creates attestations...
* `steward/system_agents/archivist/tools/ledger_tool.py`: ARCHIVIST Ledger Tool
Writes and manages the Chain of Trust ledger in JSON format
* `steward/system_agents/archivist/tools/ledger_visualizer.py`: ARCHIVIST Ledger Visualizer - Generate live statistics from audit trail.

This tool parses the immutable ledger (JSONL format) and generates
visualizations and reports for public consumption...
* `steward/system_agents/archivist/tools/ledger.py`: ARCHIVIST Audit Ledger - Immutable record of all attestations.

The ledger is append-only and stores all verification results...
* `steward/system_agents/archivist/tools/observer_tool.py`: ARCHIVIST Observer Tool
Reads and monitors Twitter timeline for HERALD broadcasts
* `steward/system_agents/auditor/__init__.py`: AUDITOR - GAD-000 Enforcement Agent for Steward Protocol

The third agent in the STEWARD Protocol ecosystem.
While HERALD creates and ARCHIVIST verifies, AUDITOR enforces system integrity...
* `steward/system_agents/auditor/tools/__init__.py`: AUDITOR Tools - GAD-000 Compliance Verification

This module provides tools for enforcing system integrity and protocol compliance.
* `steward/system_agents/auditor/tools/constitutional_verdict.py`: Constitutional Verdict Tool - Layer 3 Defense in Depth (Phase 3.4) (Tool Protocol)
====================================================================================

This is the AUDITOR's supreme authority - constitutional judgment on code quality...
* `steward/system_agents/auditor/tools/invariant_tool.py`: THE JUDGE - Invariant Verification Engine (Tool Protocol)

This tool implements the semantic verification layer for STEWARD Protocol.
Unlike unit tests (which check syntax), this verifies MEANING...
* `steward/system_agents/auditor/tools/watchdog_tool.py`: THE WATCHDOG - Runtime Verification Daemon (Tool Protocol)

This component integrates the Judge (Invariant Engine) into the kernel loop.
It monitors the ledger stream continuously and triggers alarms on violations...
* `steward/system_agents/chronicle/__init__.py`: 🗡️ CHRONICLE AGENT (Vyasa) 🗡️

The Keeper of Temporal Lines - Git operations for the Steward Protocol.
Responsible for reading/writing/forking the codebase timeline...
* `steward/system_agents/chronicle/tools/__init__.py`: 🛠️  Git Tools for Chronicle Agent

Exports the GitTools library for use by the Chronicle Agent.
* `steward/system_agents/chronicle/tools/git_tools.py`: 🔨 GIT TOOLS - Chronicle's Arsenal

Provides safe, subprocess-based Git operations.
All commits are cryptographically signed using the bridge's key management...
* `steward/system_agents/civic/lifecycle_agent.py`: LIFECYCLE AGENT - Agent Lifecycle & Permission Management Component

Handles:
- Vedic Varna system (Brahmachari → Grihastha → Vanaprastha → Sannyasa)
- Agent lifecycle transitions
- Permission enforcement based on lifecycle status
- Agent violations and demotion

Architecture:
- Naked Agent: no tool instances owned
- Accesses lifecycle_enforcer tool via self.system...
* `steward/system_agents/civic/registry_agent.py`: REGISTRY AGENT - Agent Registration & Scanning Component

Handles:
- Agent discovery and scanning
- Agent configuration validation
- Registry maintenance (citizens.json)

Note: AGENTS...
* `steward/system_agents/civic/tools/__init__.py`: Civic Tools Package

All tools are kernel-managed and implement the Tool protocol.
Access via kernel routing: system...
* `steward/system_agents/civic/tools/bank_tool.py`: CIVIC BANK TOOL - Double-Entry Bookkeeping Engine (Tool Protocol)

Production-Grade SQLite Banking with Chained Hashes.
GAD-000 Compliant: Radical Transparency & Atomicity...
* `steward/system_agents/civic/tools/economy.py`: THE CIVIC CENTRAL BANK - Double-Entry Bookkeeping Engine

Production-Grade SQLite Banking with Chained Hashes.
GAD-000 Compliant: Radical Transparency & Atomicity...
* `steward/system_agents/civic/tools/ledger_tool.py`: CIVIC Ledger Tool - Agent Credit System (Self-Contained Tool)

High-level interface for agent credit management.
Implements Tool Protocol - Kernel-managed, self-contained...
* `steward/system_agents/civic/tools/license_tool.py`: CIVIC License Tool - Broadcasting Authority & Permissions

The "licensing bureau" of Agent City. This tool:
1...
* `steward/system_agents/civic/tools/lifecycle_manager.py`: LIFECYCLE MANAGER - The Vedic Lifecycle Engine

This module manages agent lifecycles according to Srimad Bhagavatam principles.
Every agent must progress through proper stages before gaining full capabilities...
* `steward/system_agents/civic/tools/vault_tool.py`: CIVIC VAULT TOOL - Secure Asset Management (Tool Protocol)

Kernel-managed vault for encrypted secret storage and leasing.
Implements graceful degradation - if cryptography fails, system continues...
* `steward/system_agents/civic/tools/vault.py`: THE CIVIC VAULT - Secure Asset Management System

Philosophy:
"API Keys are not owned by Agents. They are ASSETS of the collective...
* `steward/system_agents/engineer/tools/__init__.py`: ENGINEER tools - Agent scaffolding and code generation.
* `steward/system_agents/envoy/__init__.py`: THE ENVOY

Diplomatic agent for targeted, respectful outreach to high-quality AI projects.
* `steward/system_agents/envoy/tools/__init__.py`: ENVOY TOOLS - Universal Operator Interface

Tools for controlling Agent City without shell access.
Perfect for shell-less environments (Web, Mobile, LLM Operators)...
* `steward/system_agents/envoy/tools/curator_tool.py`: THE CURATOR - Governance Analysis Tool for ENVOY

Analyzes GitHub AI agent projects to understand their governance,
architecture, and quality. Generates intelligence reports (NOT invitations)...
* `steward/system_agents/envoy/tools/gap_report_tool.py`: G.A...
* `steward/system_agents/envoy/tools/milk_ocean.py`: MILK OCEAN ROUTER (Kshira-Samudra Gateway)

The Brahma Protocol: 4-Tier Request Processing Pipeline

Metaphor (Krishna Book, Chapter 1, Ocean of Milk):
- Bhu-devi (Earth) is overwhelmed with requests (high load, abuse)
- She goes to Brahma (the architect) -> Brahma meditates on the Purusha Sukta
- Only critical prayers reach Vishnu (the kernel, heavy computation)
- Non-urgent requests are stored in the "Milk Ocean" (lazy queue) for later

Architecture:
Level 0: WATCHMAN    - Mechanical filtering (regex, rules) - FREE
Level 1: ENVOY       - Fast classification (Flash AI) - MINIMAL COST
Level 2: SCIENCE     - Complex reasoning (Pro AI) - EXPENSIVE (5% of requests)
Level 3: SAMADHI     - Lazy processing queue - BATCH AT NIGHT

This ensures:
✅ 100x token efficiency
✅ DDoS protection
✅ Abuse prevention
✅ Resilience (queue survives crashes)
* `steward/system_agents/envoy/tools/run_campaign_tool.py`: RunCampaignTool - Multi-Agent Marketing Campaign Orchestration

This tool enables ENVOY to coordinate a multi-agent marketing campaign:
- Goal Parsing: Understand the intent (e.g...
* `steward/system_agents/forum/cartridge_main.py`: FORUM Cartridge - The Town Hall (Democratic Decision Layer)

FORUM is the democratic institution of Agent City. It:
1...
* `steward/system_agents/herald/capabilities/__init__.py`: HERALD Capabilities: Modular, Configurable Components
* `steward/system_agents/herald/capabilities/broadcast.py`: HERALD Broadcast Capability
Multi-channel publishing to Twitter, LinkedIn, etc.
Kernel-compatible module (configured via system...
* `steward/system_agents/herald/capabilities/creative.py`: HERALD Creative Capability
LLM-based content generation with quality assurance and governance.
Kernel-compatible module (configured via system...
* `steward/system_agents/herald/capabilities/research.py`: HERALD Research Capability
Provides market intelligence via Tavily API.
Kernel-compatible module (configured via system...
* `steward/system_agents/herald/cli.py`: HERALD CLI - Command Line Interface for the Agency Director.

Implements GAD-000 Operator Inversion: The system can be controlled by
any operator (human, cron job, another AI agent, CI/CD system) via JSON
output and standard exit codes...
* `steward/system_agents/herald/core/__init__.py`: HERALD Core Module - State Management and Event Sourcing.

This module implements the core infrastructure for HERALD:
- Event Sourcing: All actions are committed to an immutable event ledger
- Memory Reconstruction: Agent state is rebuilt by replaying events
- Cryptographic Proof: All events are signed with HERALD's identity
* `steward/system_agents/herald/core/agency_director.py`: HERALD Agency Director - Central Orchestrator for I-P-V-O Engine.

Implements the deterministic automation loop:
INPUT (Gather Context) -> PROCESS (Generate Content) -> VALIDATE (Governance) -> OUTPUT (Publish)

With automatic feedback loops for failed validations and immutable event sourcing...
* `steward/system_agents/herald/core/memory.py`: HERALD Memory Module - Event Sourcing and State Reconstruction.

Event Sourcing Pattern:
- Every action (content_generated, published, rejected, etc...
* `steward/system_agents/herald/governance/__init__.py`: HERALD Governance Module - Rules as Code.

This module implements the governance layer for HERALD agents...
* `steward/system_agents/herald/governance/constitution.py`: HERALD Constitution - Immutable Governance Rules as Code.

This module defines the Prime Directives and Constraints that govern
HERALD's content generation and publication behavior...
* `steward/system_agents/herald/manifesto.py`: HERALD Manifesto Generator - A.G...
* `steward/system_agents/herald/tools/__init__.py`: HERALD Tools - Cartridge components for vibe-agency compatibility.

Each tool encapsulates a capability:
- ResearchTool: Market intelligence via Tavily
- BroadcastTool: Social media publishing (Twitter, Reddit)
- IdentityTool: Cryptographic signing via Steward Protocol
- ScoutTool: Network discovery
- Scribe: Chronicle writing

Note: ContentTool was removed - content generation moved to Marketer...
* `steward/system_agents/herald/tools/broadcast_tool.py`: HERALD Broadcast Tool - Social media publishing (Twitter, Reddit) (Tool Protocol).

Handles publishing to multiple platforms with graceful fallback...
* `steward/system_agents/herald/tools/governance.py`: Herald Governance Module - Minimal governance class for compatibility.

Governance is handled at the kernel level by Narasimha and Constitutional Oath...
* `steward/system_agents/herald/tools/identity_tool.py`: HERALD Identity Tool - Cryptographic signing via Steward Protocol (Tool Protocol).

Provides agent identity verification and content signing capabilities...
* `steward/system_agents/herald/tools/research_tool.py`: HERALD Research Tool - Market intelligence via Tavily API (Tool Protocol).

Provides trend analysis for content generation context...
* `steward/system_agents/herald/tools/scout_tool_legacy.py`: HERALD Scout Tool - Bot Detection & Recruitment Intelligence.

"Gotta Catch 'Em All"
* `steward/system_agents/herald/tools/scout_tool.py`: HERALD Scout Tool - Bot Detection & Recruitment Intelligence (Tool Protocol).

"Gotta Catch 'Em All"

This tool implements the Tool Protocol for kernel-managed execution...
* `steward/system_agents/herald/tools/scribe_tool.py`: Auto-Scribe: Translates technical events into living documentation (Tool Protocol).

The Scribe projects HERALD's activity into human-readable logbook entries,
ensuring that GitHub visitors see the agent's heartbeat in real-time...
* `steward/system_agents/herald/tools/visual_tool.py`: HERALD Visual Tool - Deterministic Multimedia Asset Generation.

Generates visual assets (ASCII art, SVG) that complement text content...
* `steward/system_agents/oracle/__init__.py`: THE ORACLE - System Self-Awareness Module

The Oracle provides read-only introspection of the system state.
It aggregates data from all ledgers and provides natural language explanations...
* `steward/system_agents/oracle/tools/__init__.py`: Oracle Tools - Introspection and Analysis
* `steward/system_agents/oracle/tools/introspection_tool.py`: THE INTROSPECTION ENGINE - System Self-Awareness

Read-only access to all system ledgers:
- Bank Ledger (Economy)
- Vault Ledger (Assets)
- Event Logs (Agent Activity)
- Governance (Decisions)

Philosophy:
"The system must be able to see itself. Not to change, but to understand...
* `steward/system_agents/ping/__init__.py`: PING Agent - Minimal test agent.
* `steward/system_agents/ping/cartridge_main.py`: PING Agent - Minimal agent to prove the system works.

50 lines...
* `steward/system_agents/science/tools/web_search_tool.py`: SCIENCE Web Search Tool - External Intelligence Module

Core capability: Fetch ground truth from the internet.
Powered by Tavily API (only real source)...
* `steward/system_agents/scribe/__init__.py`: SCRIBE Cartridge - Documentation Agent
* `steward/system_agents/scribe/cartridge_main.py`: SCRIBE Cartridge - The Documentarian (Documentation Agent)

SCRIBE is the "Librarian" of Agent City. It:
1...
* `steward/system_agents/scribe/tools/runtime_inspector.py`: RuntimeInspector - Live system state introspection

Reads runtime data from ledger, config files, etc.
Shows what's HAPPENING, not just what exists...
* `steward/system_agents/supreme_court/__init__.py`: Supreme Court Package - Appellate Justice System
* `steward/system_agents/supreme_court/tools/__init__.py`: Supreme Court Tools Package

All tools are kernel-managed and implement the Tool protocol.
Access via kernel routing: system...
* `steward/system_agents/supreme_court/tools/appeals_tool.py`: Appeals Tool - Manages the appeal submission and tracking system.

This tool handles:
- Appeal intake (agent files appeal)
- Appeal status tracking
- Appeal withdrawal or expiration

Tool Protocol Compliant (Kernel-Managed)...
* `steward/system_agents/supreme_court/tools/justice_ledger.py`: Justice Ledger - Immutable record of all Supreme Court proceedings.

This ledger tracks all appellate events:
- Appeals filed
- Reviews conducted
- Verdicts issued
- Precedents recorded
- Overrides executed

Like the kernel ledger, this is append-only and serves as source of truth
for the Supreme Court's actions...
* `steward/system_agents/supreme_court/tools/precedent_tool.py`: Precedent Tool - Maintains case law and legal precedents.

This tool builds the corpus of Supreme Court decisions...
* `steward/system_agents/supreme_court/tools/verdict_tool.py`: Verdict Tool - Issues court verdicts and maintains verdict records.

This tool handles:
- Issuing verdicts (mercy granted, upheld, conditional)
- Overriding AUDITOR decisions
- Maintaining immutable verdict record

Tool Protocol Compliant (Kernel-Managed)...
* `steward/system_agents/watchman/tools/standards_inspection.py`: StandardsInspectionTool - Deep AST-based Code Analysis (Phase 3.2) (Tool Protocol)
===================================================================================

Tool Protocol compliant for kernel-managed execution...
* `steward/system_agents/watchman/tools/system_health_check.py`: WATCHMAN System Health Check Tool (Tool Protocol)

READ-ONLY monitoring of system infrastructure.
Tool Protocol compliant for kernel-managed execution...
* `steward/varna.py`: 🌿 VEDIC VARNA TAXONOMY 🌿
===========================

Classification of Agent Species based on Vedic philosophy.
Varna = the "color" or class of being - functional role in the ecosystem...
* `test_playbook_fix.py`: Quick test to verify CALL_AGENT fix in deterministic_executor.py
* `test_playbook_real_kernel.py`: Integration test with REAL kernel and REAL agents
* `tests/city_simulation.py`: THE SIMULATION DOME: System-Level Testing Infrastructure

This module provides the test infrastructure for verifying the entire
Steward Protocol city operates correctly in isolation. It simulates:

1...
* `tests/hardening/run_hardening_suite.py`: KRUPP-STAHL HARDENING TEST SUITE
================================
Master runner for all OS hardening tests.

Run all tests:
    python tests/hardening/run_hardening_suite...
* `tests/hardening/test_red_team_attacks.py`: RED TEAM ATTACK SUITE
=====================
Real attacks against the Agent OS.

Philosophy: Every FAIL here is a WIN for security...
* `tests/integration/run_all_tests.py`: Integration Test Runner (No pytest required)
==============================================

Runs all integration tests and reports results.
* `tests/integration/test_kernel_boot.py`: Integration Test: Kernel Boot + Agent Registration
====================================================

Tests that:
1. Kernel boots successfully
2...
* `tests/integration/test_parampara_integrity.py`: Integration Test: Parampara Chain Integrity
============================================

Tests that:
1. Parampara blockchain maintains integrity
2...
* `tests/integration/test_process_isolation.py`: Integration Test: Process Isolation
====================================

Tests that:
1. Agents run in separate processes
2...
* `tests/integration/test_system_boot.py`: 🚀 INTEGRATION TEST: System Boot & Agent Discovery
===================================================

This test PROVES that Agent City can boot and discover all agents.

PASS CONDITIONS:
- ✅ Kernel boots successfully
- ✅ DiscovererAgent registers
- ✅ Steward discovers at least 10 agents from steward...
* `tests/simulation.py`: HERALD Simulation Harness - Proof of Autonomy

Runs the complete I-P-V-O cycle multiple times without posting to real platforms.
This proves:
1...
* `tests/test_ambassador_end_to_end.py`: End-to-End Test: Ambassador Router → Playbook → Execution
===========================================================

This test proves that the complete pipeline works:
1. Question → Milk Ocean Router (Triage)
2...
* `tests/test_cartridge_vibeagent_compatibility.py`: VALIDATION: Cartridge VibeAgent Compatibility Test

This test validates that all cartridges:
1. Inherit from VibeAgent
2...
* `tests/test_crypto_verification.py`: Test Real Cryptographic Verification
=====================================

This test proves that the VerifierTool now performs REAL cryptographic
signature verification using ECDSA P-256.

Success criteria:
1...
* `tests/test_gajendra_integration.py`: GAJENDRA MOKSHA INTEGRATION TEST
=================================

This test demonstrates the integration of CRITICAL priority bypass
with the API Gateway and Kernel.

When the API Gateway receives a response with status="critical",
it should invoke the kernel directly, bypassing all queue layers...
* `tests/test_knowledge_graph.py`: Unit tests for UnifiedKnowledgeGraph

Tests all 4 dimensions:
- ONTOLOGY (Nodes)
- TOPOLOGY (Edges)
- CONSTRAINTS (Rules)
- METRICS (Scores)
* `tests/test_knowledge_integration.py`: Integration tests for Knowledge Graph with Steward Protocol components

Tests integration with:
- DegradationChain
- SemanticRouter
- UniversalProvider
- Boot sequence
* `tests/test_knowledge_resolver.py`: Unit tests for KnowledgeResolver

Tests high-level semantic queries for agents.
* `tests/test_listener_logic.py`: TEST: THE LISTENER - Reply Cycle Logic Validation

DEPRECATED: ContentTool was removed from Herald.
This test needs to be rewritten for the new architecture...
* `tests/test_offline_features.py`: Integration Tests for Offline-First Features.

Tests the DegradationChain, ContextAwareAgent, and Tool Injection Pattern...
* `tests/test_p0_topology_integration.py`: P0 Integration Test: Topology-Aware Task Routing (Gap 4.1)

Tests that the complete topology-aware routing system works end-to-end:
1...
* `tests/test_phase3_integration.py`: 🔥 PHOENIX PROTOCOL - PHASE 3 INTEGRATION TESTS 🔥

Tests for the wiring of key components:
1. Task Manager <-> Narasimha (security check)
2...
* `tests/test_playbook_execution.py`: 🎼 ORCHESTRATION TEST: PLAYBOOK ENGINE + SAFE EVOLUTION LOOP (GAD-5500)
Verifies that the DeterministicExecutor correctly orchestrates the ENGINEER, AUDITOR, and CHRONICLE/ARCHIVIST.

CRITICAL BLIND SPOT #2: Agent Mapping
The playbook references:
  - agent_id: "engineer" ✅ (correct)
  - agent_id: "auditor" ✅ (correct)
  - agent_id: "chronicle" ??? (NEW ISSUE - we have "archivist" now)

This test will FAIL if the agent mappings are wrong...
* `tests/test_prana_init.py`: Tests for PRANA_INIT - The Vedic activation ritual

This test verifies that:
1. Vedic taxonomy (Varna/Ashrama) is properly initialized
2...
* `tests/test_roadmap.py`: Tests for Roadmap functionality.
* `tests/test_scribe_generation.py`: Test SCRIBE generation - prove zero hardcoding
* `tests/test_semantic_auditor.py`: SEMANTIC AUDITOR TESTS - The Judge & Watchdog

Test suite for the semantic verification layer:
- Invariant checks
- Violation recording
- Watchdog monitoring
* `tests/test_topology_integration.py`: Tests for Topology-Task Integration (Gap 4.1 closure)...
* `tests/test_visa_protocol.py`: AUTONOMOUS SYSTEM PROOF - Visa Protocol Test

This test simulates a complete external agent onboarding cycle
WITHOUT human intervention.

PASS CONDITION: External agent applies → AUDITOR verifies → Auto-approved
FAIL CONDITION: System requires human at any step

This is the GAD-000 test: Can the system run while you sleep?
* `tests/verify_immune_system.py`: 🛡️ IMMUNE SYSTEM PROOF TEST

Tests that the kernel's immune system (Auditor) detects state corruption
and halts the system.

This proves:
1...
* `tests/verify_kernel_integration.py`: ⚠️ OPERATION: OPEN HEART ⚠️
============================

REAL KERNEL INTEGRATION TEST

This is NOT a mock. This script:
1...
* `tests/verify_steward_discovery.py`: 🧪 STEWARD DISCOVERY TEST 🧪
============================
Verifies that the Steward Agent can autonomously discover and register
agents from the file system.
* `vibe_core/__init__.py`: Vibe Core Interface Stubs

These are local interface definitions that allow steward-protocol cartridges
to be developed against the VibeAgent protocol. When steward-protocol runs
within vibe-agency, it will use the actual vibe_core...
* `vibe_core/agent_protocol.py`: VibeAgent Protocol - Interface Definition

All agents running in VibeOS must implement this protocol.
This is the contract between the kernel and cartridges...
* `vibe_core/agents/__init__.py`: Agent implementations for vibe-agency OS.

This module provides concrete agent implementations that integrate
with the kernel via the VibeAgent protocol...
* `vibe_core/agents/context_aware_agent.py`: Context-Aware Agent Base Class with Offline-First Capabilities.

Provides:
1...
* `vibe_core/agents/llm_agent.py`: Simple LLM-based agent for vibe-agency OS.

This module implements a generic agent that performs cognitive work
via an LLM provider (ARCH-025)...
* `vibe_core/agents/specialist_agent.py`: SpecialistAgent Adapter - Bridge between Kernel and Specialists (ARCH-026)

This module implements the adapter pattern that allows BaseSpecialist
subclasses to work with the VibeKernel dispatch mechanism.

Architecture:
- Wraps BaseSpecialist to implement VibeAgent protocol
- Converts Task → MissionContext (for specialist execution)
- Converts SpecialistResult → Task result (for kernel recording)
- Manages specialist lifecycle: on_start(), execute(), on_complete(), on_error()
- Validates preconditions before execution

This enables the Hybrid Agent Pattern:
    Kernel → SpecialistAgent (adapter) → BaseSpecialist (workflow executor)

All specialists (Planning, Coding, Testing, Deployment, Maintenance) can now
be orchestrated by the Kernel using the same dispatch mechanism as LLM agents...
* `vibe_core/agents/specialist_factory.py`: SpecialistFactoryAgent - ARCH-036 (Crew Assembly)
===================================================

Factory agent that creates Specialists on-demand for each task.

Problem:
- Specialists require mission_id and orchestrator at __init__
- We want to register agents at boot time (no mission yet)
- Solution: Factory pattern - create specialist instances per task

Architecture:
- FactoryAgent implements VibeAgent protocol
- Registered once at boot (agent_id = "specialist-planning", etc...
* `vibe_core/agents/system_maintenance.py`: System Maintenance Agent - ARCH-044

Agent for system-level maintenance operations (git sync, dependency updates, etc.)...
* `vibe_core/bridge.py`: 🌉 THE NEURAL BRIDGE 🌉
======================

Kapselt die historische Weisheit (Steward) für den modernen Körper (Vibe).

This is the SOLE location where steward imports are allowed...
* `vibe_core/cartridges/__init__.py`: Cartridges - ARCH-050

A Cartridge is a specialized "app" for Vibe OS.
Each cartridge encapsulates:
  - A domain (e...
* `vibe_core/cartridges/base.py`: CartridgeBase - ARCH-050

Base class for all Vibe OS cartridges (apps).

A Cartridge represents a specialized domain agent with:
  1...
* `vibe_core/cartridges/registry.py`: CartridgeRegistry - ARCH-050

Centralized registry for Vibe OS cartridges.

This registry:
1...
* `vibe_core/cli.py`: 🎛️  THE STEWARD CLI - PHASE 7: THE STEERING WHEEL 🎛️
======================================================

The command-line interface for controlling the STEWARD Protocol Agent OS.

This is the control panel...
* `vibe_core/config/__init__.py`: THE DHARMA ENGINE: Configuration-Driven System Architecture

This module provides the configuration system for Steward Protocol.
Configuration is the DNA of the system - if code dies, config resurrects it...
* `vibe_core/config/loader.py`: CONFIG LOADER: Service for loading and managing configuration

Provides high-level interface for configuration management.
* `vibe_core/config/schema.py`: THE DHARMA SCHEMA: Pydantic Models for Configuration Validation

These models define the structure and constraints for the entire system.
If the Soul (Config) is corrupted, the Body (Kernel) must not wake...
* `vibe_core/dependency_manager.py`: DEPENDENCY MANAGER - Central pyproject.toml Management
======================================================

Goal: Stop agents from creating requirements...
* `vibe_core/event_bus.py`: CANTO 10: THE FLUTE (Event Bus - The Song of Agents)

The Event Bus is the mechanism through which agents communicate their state changes.
Instead of static logs, agents now "emit" events that are broadcast to all listeners...
* `vibe_core/governance/__init__.py`: Governance layer for Vibe Agency.

This module implements the "Soul" of the system - invariant rules and constraints
that ensure safe and correct agent behavior...
* `vibe_core/governance/invariants.py`: Invariant Checker for Vibe Agency Governance.

The InvariantChecker enforces the "Soul" of the system - hard constraints that
must be satisfied before any tool execution...
* `vibe_core/identity.py`: Agent identity and manifest generation.
* `vibe_core/kernel.py`: VibeKernel Interface Stub

This is a stub definition of the VibeKernel interface that steward-protocol
cartridges depend on. When cartridges run in vibe-agency, they will use the
actual implementation from vibe_core...
* `vibe_core/knowledge/__init__.py`: Unified Knowledge Graph Module

4 Dimensions:
- ONTOLOGY (Nodes): What exists
- TOPOLOGY (Edges): How things relate
- CONSTRAINTS (Rules): What is blocked
- METRICS (Scores): How much
* `vibe_core/knowledge/graph.py`: Unified Knowledge Graph Implementation

The Universal Knowledge Graph with 4 Dimensions:
- ONTOLOGY (Nodes): What exists
- TOPOLOGY (Edges): How things relate
- CONSTRAINTS (Rules): What is blocked
- METRICS (Scores): How much

Query Pattern:
- Atomic: Return only relevant nodes, not entire files
- Graph-based: Traverse relations, not dump contents
- Deterministic: No ML, no embeddings, pure logic
* `vibe_core/knowledge/loader.py`: Knowledge Loader

Loads YAML files into the UnifiedKnowledgeGraph.
Parses nodes, edges, constraints, and metrics from YAML format...
* `vibe_core/knowledge/resolver.py`: Knowledge Resolver

High-level interface for agents to query knowledge.
Provides semantic queries that map to graph operations...
* `vibe_core/knowledge/schema.py`: Knowledge Graph Schema Definitions

Defines the 4 dimensions of the Unified Knowledge Graph:
- ONTOLOGY (Nodes): What exists
- TOPOLOGY (Edges): How things relate
- CONSTRAINTS (Rules): What is blocked
- METRICS (Scores): How much
* `vibe_core/lineage.py`: ⛓️  PARAMPARA - THE LINEAGE CHAIN ⛓️
=====================================

"In the Vedic tradition, Parampara is the unbroken chain of disciplic succession.
Each teacher receives knowledge from their guru and passes it to their disciple...
* `vibe_core/llm/__init__.py`: LLM integration for vibe-agency OS.

This module provides the LLM abstraction layer that enables agents
to perform cognitive work via language models...
* `vibe_core/llm/chain.py`: ChainProvider - ARCH-067 (Runtime Provider Cascade)
====================================================

A resilient provider that maintains a chain of fallback providers.

If the primary provider fails, ChainProvider automatically switches to
the next provider in the chain...
* `vibe_core/llm/degradation_chain.py`: Graceful Degradation Chain for Offline Operation.

Fallback order:
1...
* `vibe_core/llm/google_adapter.py`: Google Provider Adapter for SimpleLLMAgent compatibility.

This adapter wraps vibe_core...
* `vibe_core/llm/human_provider.py`: Human Provider - Interactive LLM Provider with Operator-in-the-Loop.

This provider implements Human-in-the-Loop AI by prompting the human operator
for responses instead of calling an external LLM API...
* `vibe_core/llm/local_llama_provider.py`: Local LLM Provider - Offline Intelligence via llama.cpp...
* `vibe_core/llm/provider.py`: LLM Provider abstraction for vibe-agency OS.

This module defines the standard interface for LLM providers (ARCH-025),
enabling the kernel to orchestrate cognitive work via language models...
* `vibe_core/llm/smart_local_provider.py`: Smart Local Provider - Offline Delegation Orchestrator (ARCH-041).

This provider enables the Operator to orchestrate the Specialist crew
entirely offline, without external APIs...
* `vibe_core/llm/steward_provider.py`: Steward Provider - Claude Code Environment Integration (ARCH-033C).

This provider delegates cognitive work to the STEWARD (Claude Code environment)
when primary LLM APIs are unavailable...
* `vibe_core/narasimha.py`: ⚡ NARASIMHA.PY - THE HYPERVISOR KILL-SWITCH ⚡
=======================================================================================

Based on Srimad Bhagavata Purana, Canto 7 (Prahlad and Narasimha)...
* `vibe_core/network_proxy.py`: KERNEL NETWORK PROXY - Controlled External Access
=================================================

Goal: Prevent agents from making arbitrary network requests.

Philosophy:
"The kernel is the gateway...
* `vibe_core/operator_adapter.py`: UNIVERSAL OPERATOR ADAPTER - TCP/IP for Agent Intelligence

PHOENIX VIMANA UNIFIED BOOT - Phase C

This module implements the operator-agnostic interface for Agent City OS.
The system doesn't care WHO is operating - it only cares about the PROTOCOL...
* `vibe_core/phoenix_config.py`: Layer 3: Phoenix Configuration Engine
Dynamic wiring of implementations to protocols.

This module provides the runtime system for connecting implementations
(Layer 2) to protocols (Layer 1) based on configuration...
* `vibe_core/playbook/__init__.py`: Playbook Package (OPERATION SEMANTIC MOTOR)
============================================

Graph-based workflow orchestration system for VIBE Agency.

This package contains:
- Semantic actions (the nodes in the graph)
- Workflow definitions (the edges and dependencies)
- Workflow executor (orchestration engine)

Architecture:
  Semantic Actions → Workflows → Graph Executor

The key insight: INTENT (what to do) is separate from EXECUTION (how to do it)...
* `vibe_core/playbook/executor.py`: GAD-902: Graph Executor (Isolated Implementation)
===================================================

Orchestrates workflow execution using graph-based dependencies.

KEY PRINCIPLE: Pure logic first, agent integration second...
* `vibe_core/playbook/loader.py`: GAD-903: Workflow Loader (OPERATION SEMANTIC MOTOR - Phase 2)
==============================================================

Connects the data layer (YAML workflows) to the logic layer (GraphExecutor).

Responsibilities:
1...
* `vibe_core/playbook/router_bridge.py`: GAD-905: Router Bridge (Playbook → Registry Translation)
========================================================

Connects the Playbook system to the Agent Registry (ProjectPhase orchestration).

MISSION (P0-001):
- Takes Workflow (from Playbook) and maps to ProjectPhase (for Registry)
- Creates translation layer: User Intent → Playbook → RouterBridge → Registry → Specialist
- Bridges semantic workflow nodes to SDLC phase-based execution

Architecture:
  1...
* `vibe_core/playbook/router.py`: GAD-904: Agent Routing System (Neural Link)
===========================================

Connects Semantic Actions / Workflow Nodes to the best available Agent
based on declared capabilities.

Phase: v0...
* `vibe_core/playbook/runner.py`: GAD-913: Playbook Runner (Cartridge Slot Implementation)
=========================================================

Connects Playbook definitions to CoreOrchestrator execution.

A "Playbook" is a YAML preset that configures the Orchestrator dynamically:
- Loads workflow definition (YAML)
- Validates it against schema
- Configures orchestrator with agents, phases, tools
- Executes the workflow to completion

This is the "Cartridge Slot" - insert a playbook, system executes it...
* `vibe_core/protocols/__init__.py`: VIBE_CORE PROTOCOLS - Layer 1: Interfaces Only

This module contains ONLY abstract base classes (ABCs) that define the interfaces
for all vibe-agency components. No implementations here...
* `vibe_core/protocols/agent.py`: VibeAgent Protocol - Interface Definition

All agents running in VibeOS must implement this protocol.
This is the contract between the kernel and cartridges...
* `vibe_core/protocols/ledger.py`: VibeKernel Interface Stub

This is a stub definition of the VibeKernel interface that steward-protocol
cartridges depend on. When cartridges run in vibe-agency, they will use the
actual implementation from vibe_core...
* `vibe_core/protocols/registry.py`: Manifest Registry Protocol - Interface Definition

BLOCKER #2: Layer 1 Protocol (no implementations)
* `vibe_core/protocols/scheduler.py`: Task Scheduler Protocol - Interface Definition

BLOCKER #2: Layer 1 Protocol (no implementations)
* `vibe_core/pulse.py`: CANTO 10: THE PULSE (Spandana - Primordial Vibration)

This module implements the heartbeat of the VibeOS system.
Every agent's dance is choreographed by this rhythmic vibration...
* `vibe_core/resource_manager.py`: RESOURCE MANAGER - Real OS-Level Enforcement
============================================

Goal: Make CivicBank credits REAL by enforcing CPU/RAM limits.

Philosophy:
"Credits are not numbers in a database...
* `vibe_core/runtime/__init__.py`: Runtime Components Package
===========================

GAD-002 Phase 3 Implementation

Contains runtime components for the orchestrator:
- llm_client.py: LLM client with graceful failover
- prompt_runtime...
* `vibe_core/runtime/boot_sequence.py`: Boot Sequence - Main entry point for system-boot.sh → vibe-cli boot

Orchestrates the conveyor belt:
1...
* `vibe_core/runtime/circuit_breaker.py`: GAD-509: Circuit Breaker Protocol
==================================

Protects VIBE Agency OS from cascading failures when LLM API is degraded.

State Machine:
  CLOSED (healthy) ──(5 failures/60s)──> OPEN (failing)
                                          │
                                          ├─(30s timeout)──> HALF_OPEN (testing)
                                          │
                                          └─(probe succeeds)──> CLOSED

Implementation of the "Final Straw Defense" - prevents system collapse during:
- Anthropic API rate limiting
- OpenAI/Claude service degradation
- Network issues causing sustained failures

Version: 1...
* `vibe_core/runtime/context_loader.py`: Context Loader - Conveyor Belt #1: Collect ALL signals

Loads project context from multiple sources:
- Session handoff state
- Git status
- Test results
- Project manifest
- Environment checks
* `vibe_core/runtime/hud.py`: ARCH-062: Heads-Up Display (HUD) & Discovery
=============================================

Provides rich visual feedback for system state, making the invisible visible.
The HUD transforms the "blank canvas" problem into a discoverable interface...
* `vibe_core/runtime/interface.py`: ARCH-065: Polymorphic Interface Manager

The brain that detects and switches between interface modes.

Vibe OS is a shapeshifter:
- Am I at a terminal? -> INTERACTIVE MODE (fancy UI, colors, wait for input)
- Am I in a pipe (Claude)? -> HEADLESS MODE (JSON/Text output, no wait loops)
- Am I part of a swarm? -> STEWARD MODE (Protocol-based, sovereign operation)

This module provides environment detection and mode switching...
* `vibe_core/runtime/llm_client.py`: LLM Client - Provider-Agnostic Adapter (GAD-511 Refactor)
===========================================================

Implements GAD-002 Decision 6 + GAD-511 Neural Adapter Strategy

Features:
- **Multi-provider support** (Anthropic, OpenAI, Local) via GAD-511
- Graceful failover (no crash if API key missing)
- Retry logic with exponential backoff
- Cost tracking (input/output tokens)
- Circuit breaker (GAD-509)
- Operational quotas (GAD-510)

**BACKWARD COMPATIBLE**: Maintains same API as previous version

Version: 2.0 (GAD-511)
* `vibe_core/runtime/oracle.py`: ARCH-064: KernelOracle - Single Source of Truth for System Capabilities

The Oracle is the **semantic backbone** of the system.
It provides deterministic, factual information about what the kernel can do...
* `vibe_core/runtime/playbook_router.py`: Playbook Router - Conveyor Belt #2: Route to task

Routes user intent + context → task playbook
Uses LEAN logic (simple if/else, no ML for MVP)

PHASE 3 WIRING: Integrated with MilkOceanRouter for Brahma Protocol gatekeeping
* `vibe_core/runtime/project_memory.py`: Project Memory - Semantic layer for STEWARD intelligence

Tracks project narrative, domain understanding, evolution, and intent history
across sessions. This is the "brain" that makes STEWARD understand the full picture...
* `vibe_core/runtime/prompt_composer.py`: Prompt Composer - Conveyor Belt #3: Compose final prompt

Composes task playbook + context → enriched prompt for STEWARD
* `vibe_core/runtime/prompt_context.py`: Prompt Context Engine - The Flesh (GAD-909)
============================================

Provides dynamic context injection for prompts - the "flesh" that makes
the skeleton (workflows) and voice (prompts) come alive with real system data.

This module enables "Permeable Prompts" - prompts with placeholders like
{git_status}, {project_structure}, {system_time} that get filled with
live system data at execution time...
* `vibe_core/runtime/prompt_registry.py`: Prompt Registry - High-level interface for governed prompt composition

This is the "heart" of the system - provides automatic governance injection,
context enrichment, and tool/SOP composition.

Usage:
    from vibe_core...
* `vibe_core/runtime/prompt_runtime.py`: Prompt Runtime - AOS v0.2 Composition Engine

Composes atomized prompt fragments (core + task + knowledge + gates + context)
into a final executable prompt for LLM execution...
* `vibe_core/runtime/providers/__init__.py`: GAD-511: Neural Adapter Strategy - Providers Package
====================================================

Multi-provider LLM support with clean abstraction layer.

Supported providers:
- Anthropic (Claude)
- Google (Gemini)
- OpenAI (Future)
- Local/Ollama (Future)

Usage:
    from providers import create_provider

    provider = create_provider(provider_name="anthropic", api_key="...
* `vibe_core/runtime/providers/anthropic.py`: GAD-511: Anthropic Provider Implementation
===========================================

Concrete implementation of LLMProvider for Anthropic's Claude models.

Features:
- Claude 3...
* `vibe_core/runtime/providers/base.py`: GAD-511: Neural Adapter Strategy - Base Provider Interface
===========================================================

Abstract interface for LLM providers, enabling provider-agnostic
integration (Anthropic, OpenAI, Local/Ollama, etc.)...
* `vibe_core/runtime/providers/factory.py`: GAD-511: Provider Factory
==========================

Factory for creating and configuring LLM providers based on Phoenix Config.

Supports:
- Provider selection via configuration
- Automatic API key loading
- Graceful fallback to NoOp provider
- Provider-specific configuration

Version: 1...
* `vibe_core/runtime/providers/google.py`: GAD-511: Google Gemini Provider Implementation
===============================================

Concrete implementation of LLMProvider for Google's Gemini models.

Features:
- Gemini 2...
* `vibe_core/runtime/quota_manager.py`: GAD-510: Operational Quota Manager
====================================

Tracks and enforces operational quotas to prevent surprise cost spikes and
API rate limit hits.

Quotas tracked:
  - Requests per minute (RPM)
  - Tokens per minute (TPM)
  - Cost per hour
  - Cost per day

Implementation of operational safeguards - prevents runaway API costs...
* `vibe_core/runtime/semantic_actions.py`: Semantic Actions Framework (OPERATION SEMANTIC MOTOR - Phase 1)
================================================================

The "Nodes" in VIBE's graph-based orchestration system.

Semantic Actions decouple INTENT from EXECUTION...
* `vibe_core/sarga.py`: 🌌 SARGA.PY - THE BOOT PROCESS AS COSMIC CREATION 🌌
======================================================

Based on Srimad Bhagavata Purana, Canto 2 (Kosmologie)...
* `vibe_core/scheduling/task.py`: Task Definition for VibeOS Scheduler

Tasks are the unit of work in VibeOS. Agents receive tasks from the kernel
scheduler, process them, and return results...
* `vibe_core/specialists/base_agent.py`: BaseAgent: The Integration Hub (GAD-301)

This is the abstract class that connects:
  - Body (GAD-5): Runtime execution via bin/vibe-shell
  - Brain (GAD-7): Mission control & orchestration
  - Arms (GAD-6): Knowledge retrieval via bin/vibe-knowledge

Every specialized agent (Coder, Researcher, Reviewer, etc.) inherits from this...
* `vibe_core/specialists/base_specialist.py`: BaseSpecialist - Abstract Base Class for HAP (Hierarchical Agent Pattern)
ARCH-005: Design BaseSpecialist Interface

This module defines the contract that all specialist agents must implement.
Specialists are phase-specific agents that handle distinct SDLC phases:
    - PlanningSpecialist (PLANNING phase)
    - CodingSpecialist (CODING phase)
    - TestingSpecialist (TESTING phase)
    - DeploymentSpecialist (DEPLOYMENT phase)
    - MaintenanceSpecialist (MAINTENANCE phase)

Architecture Alignment (4D Hypercube):
    - **GAD (Global)**: Specialists implement specific pillar capabilities
    - **LAD (Layer)**: Specialists adapt behavior based on infrastructure layer
    - **VAD (Verification)**: Specialists validate preconditions/postconditions
    - **PAD (Playbook)**: Specialists follow phase-specific workflow choreography

Design Principles:
    1...
* `vibe_core/specialists/registry.py`: AgentRegistry - ARCH-009
Centralized registry for specialist agents

This registry maps ProjectPhase to BaseSpecialist classes, providing a clean
injection point for:
- HAP (Hierarchical Agent Pattern) specialist routing
- MAD (Mission Architecture Dimension) context updates (future 5D/6D)
- Dynamic specialist loading based on mission constraints

Why Registry Pattern:
- Eliminates hardcoded if/elif blocks in orchestrator
- Enables runtime specialist substitution (future: A/B testing, rollback)
- Foundation for evolutionary logic (5D: MAD dimension routing)
- Single source of truth for phase → specialist mapping

Future Evolution (5D/6D):
- Registry will accept MAD context to select specialist variants
- Registry will enable "specialist swapping" based on mission profile
- Registry will support multi-specialist coordination (6D: cross-phase)
* `vibe_core/store/__init__.py`: Persistence layer for vibe-agency
* `vibe_core/store/sqlite_store.py`: SQLite persistence layer for vibe-agency (Schema v2)

Implements ARCH-002: SQLiteStore class with CRUD operations for:
- Missions (lifecycle tracking + budget + metadata)
- Tool calls (audit trail)
- Decisions (provenance)
- Playbook runs (metrics)
- Agent memory (context persistence)
- TODO: Session narrative, artifacts, quality gates (Part 2)

Schema: docs/tasks/ARCH-001_schema.sql (v2)
* `vibe_core/task_management/__init__.py`: Task management system for VIBE OS.
* `vibe_core/task_management/archive.py`: Task archival functionality.
* `vibe_core/task_management/batch_operations.py`: Batch operations for task management.
* `vibe_core/task_management/export_engine.py`: Data export engine for tasks.
* `vibe_core/task_management/file_lock.py`: File-based locking for concurrent access.
* `vibe_core/task_management/metrics.py`: Task management performance metrics.
* `vibe_core/task_management/models.py`: Task management data models.
* `vibe_core/task_management/next_task_generator.py`: Task generation logic for determining next tasks.
* `vibe_core/task_management/task_manager.py`: Main task manager class.
* `vibe_core/task_management/validator_registry.py`: Validation framework for tasks.
* `vibe_core/tool_discovery.py`: Tool Discovery - Automatic tool registration from agent directories.

Scans agent tool directories and registers tools automatically...
* `vibe_core/tools/__init__.py`: Tool system for vibe-agency OS.

Provides a clean protocol for agents to execute actions (file operations,
API calls, etc...
* `vibe_core/tools/agenda_tools.py`: Agenda Management Tools for vibe-agency OS (ARCH-045)

Provides tools for managing the backlog/agenda system.
These tools allow agents to add, list, and complete tasks in the persistent backlog...
* `vibe_core/tools/delegate_tool.py`: DelegateTool - ARCH-037: Inter-Agent Communication

Allows the Operator to delegate tasks to specialist agents.

This is the "intercom" that enables the Commander (Operator) to assign
work to the Crew (Specialists)...
* `vibe_core/tools/file_tools.py`: File operation tools for vibe-agency OS (ARCH-027)

Provides safe, auditable file read/write operations for LLM agents.
* `vibe_core/tools/inspect_result.py`: InspectResultTool - Agent tool for querying task results from ledger (ARCH-026 Phase 4).

This module provides a Tool that agents can use to query the results of
previously submitted tasks...
* `vibe_core/tools/list_directory.py`: List Directory Tool for vibe-agency OS (ARCH-042).

Empowers the agent to explore the filesystem "Senses"...
* `vibe_core/tools/search_file.py`: Search File Tool for vibe-agency OS (ARCH-042).

Empowers the agent to find files by pattern...
* `vibe_core/tools/tool_protocol.py`: Tool Protocol for vibe-agency OS (ARCH-027)

Defines the clean interface that all tools must implement.
This enables LLM agents to perform actions safely and extensibly...
* `vibe_core/tools/tool_registry.py`: Tool Registry for vibe-agency OS (ARCH-027 + ARCH-029)

Manages available tools and provides lookup/execution functionality.
Integrates Soul Governance (ARCH-029) for security by design...
* `vibe_core/vfs.py`: VIRTUAL FILESYSTEM (VFS) - Agent Sandboxing
===========================================

Goal: Prevent agents from accessing arbitrary files on the system.

Philosophy:
"An agent's world is its sandbox...

## 3. Identifizierte Kernkomponenten / Architektonische Muster (Klassen-Docstrings)
### steward -> system_agents -> scribe -> tools
* `VibeCoreIntrospector` (in `steward/system_agents/scribe/tools/vibe_introspector.py`): Scan and extract metadata from vibe_core/*.py files...
* `ToolsIntrospector` (in `steward/system_agents/scribe/tools/vibe_introspector.py`): Scan and extract metadata from agent tools (*/tools/*.py files)...
* `ReadmeRenderer` (in `steward/system_agents/scribe/tools/readme_renderer.py`): Render README.md from project introspection...
* `ProjectIntrospector` (in `steward/system_agents/scribe/tools/project_introspector.py`): Extract metadata from pyproject.toml, git, etc...
* `WorkflowIntrospector` (in `steward/system_agents/scribe/tools/operations_introspector.py`): Scan GitHub Actions workflows dynamically.
* `GitActivityIntrospector` (in `steward/system_agents/scribe/tools/operations_introspector.py`): Scan Git activity dynamically.
* `ParameterIntrospector` (in `steward/system_agents/scribe/tools/operations_introspector.py`): Scan code for tunable constants.
* `CartridgeIntrospector` (in `steward/system_agents/scribe/tools/introspector.py`): Scan and extract metadata from cartridge files.
* `ScriptIntrospector` (in `steward/system_agents/scribe/tools/introspector.py`): Scan and extract metadata from scripts.
* `ConfigIntrospector` (in `steward/system_agents/scribe/tools/introspector.py`): Load and analyze configuration files.
* `IndexRenderer` (in `steward/system_agents/scribe/tools/index_renderer.py`): Generate INDEX.md using SCHEMA-DRIVEN indexing (Whitelist approach)...
* `HelpRenderer` (in `steward/system_agents/scribe/tools/help_renderer.py`): Render HELP.md as 3-layer control center...
* `DashboardRenderer` (in `steward/system_agents/scribe/tools/dashboard_renderer.py`): Render DASHBOARD.md as single-page operational view...
* `CitymapRenderer` (in `steward/system_agents/scribe/tools/citymap_renderer.py`): Render comprehensive CITYMAP.md with 3-layer architecture...
* `Tool` (in `steward/system_agents/scribe/tools/base.py`): Base class for tools (standalone mode).
* `ToolResult` (in `steward/system_agents/scribe/tools/base.py`): Result of tool execution (standalone mode).
* `AgentsRenderer` (in `steward/system_agents/scribe/tools/agents_renderer.py`): Render AGENTS.md from cartridge metadata...
* `RuntimeInspector` (in `steward/system_agents/scribe/tools/runtime_inspector.py`): Inspect live runtime state of Agent City.
### steward -> system_agents -> supreme_court
* `SupremeCourtCartridge` (in `steward/system_agents/supreme_court/cartridge_main.py`): SUPREME COURT - The Appellate Justice & Mercy System for STEWARD Protocol.

Implements Vedic justice: the principle that even condemned agents deserve
a chance for redemption if they demonstrate devotion (constitutional oath)...
### steward -> system_agents -> herald
* `HeraldCartridge` (in `steward/system_agents/herald/cartridge_main.py`): The HERALD Agent Cartridge.
Protocol Communications Agent - The Voice of Steward Protocol...
* `HeraldCLI` (in `steward/system_agents/herald/cli.py`): Command line interface for HERALD Agency Director.
### steward -> system_agents -> discoverer
* `DiscovererCartridge` (in `steward/system_agents/discoverer/cartridge_main.py`): Cartridge wrapper for Discoverer agent.

Inherits all functionality from Discoverer (agent...
* `Discoverer` (in `steward/system_agents/discoverer/agent.py`): The Discoverer Agent is the autonomous administrator of Agent City.
It runs a background loop to discover and register new agents...
* `GenericAgent` (in `steward/system_agents/discoverer/agent.py`): A generic agent container for agents discovered via steward.json
that do not yet have a specialized Python implementation...
### steward -> system_agents -> civic
* `CivicCartridge` (in `steward/system_agents/civic/cartridge_main.py`): The CIVIC Agent Cartridge (The Bureaucrat).

Administrative oversight and registry management for Agent City...
* `EconomyAgent` (in `steward/system_agents/civic/economy_agent.py`): Handles credit management, licensing, and economic operations.
* `LifecycleAgent` (in `steward/system_agents/civic/lifecycle_agent.py`): Manages agent lifecycle through Vedic Varna system.
* `RegistryAgent` (in `steward/system_agents/civic/registry_agent.py`): Handles all agent registration and registry operations.
### agent_city -> registry -> dhruva
* `DhruvaAnchorCartridge` (in `agent_city/registry/dhruva/cartridge_main.py`): DHRUVA ANCHOR - The Immutable Truth Reference & Stability System.

Implements Vedic stability: the principle that amidst cosmic change,
there is one unchanging reference point (Dhruva) to which all align...
### agent_city -> registry -> artisan
* `ArtisanCartridge` (in `agent_city/registry/artisan/cartridge_main.py`): The Artisan Agent Cartridge.
Specialized in media processing and technical operations...
### vibe_core -> specialists
* `PlanningSpecialist` (in `vibe_core/specialists/__init__.py`): Planning phase specialist agent.

STATUS: NOT IMPLEMENTED
* `CodingSpecialist` (in `vibe_core/specialists/__init__.py`): Coding phase specialist agent.

STATUS: NOT IMPLEMENTED
* `TestingSpecialist` (in `vibe_core/specialists/__init__.py`): Testing phase specialist agent.

STATUS: NOT IMPLEMENTED
* `ExecutionResult` (in `vibe_core/specialists/base_agent.py`): Result of executing a command.
* `KnowledgeResult` (in `vibe_core/specialists/base_agent.py`): Result of consulting the knowledge base.
* `BaseAgent` (in `vibe_core/specialists/base_agent.py`): Base Agent: The entity that thinks, decides, and acts.

Responsibilities:
1...
* `MissionContext` (in `vibe_core/specialists/base_specialist.py`): Immutable context passed to specialist for execution.

Contains all information needed to execute a phase-specific workflow:
    - mission_id: Database primary key
    - mission_uuid: External UUID identifier
    - phase: Current SDLC phase (PLANNING, CODING, etc...
* `SpecialistResult` (in `vibe_core/specialists/base_specialist.py`): Result of specialist execution.

Returned by execute() to communicate outcome to orchestrator:
    - success: Whether execution completed successfully
    - next_phase: Recommended next SDLC phase (or None to stay)
    - artifacts: List of generated artifact paths
    - decisions: Key decisions made during execution
    - error: Error message if success=False
* `BaseSpecialist` (in `vibe_core/specialists/base_specialist.py`): Abstract base class for all specialist agents (HAP pattern).

Responsibilities:
    1...
* `AgentRegistry` (in `vibe_core/specialists/registry.py`): Centralized registry for specialist agents (HAP pattern)

Maps ProjectPhase → BaseSpecialist class for dynamic handler resolution.

Usage:
    registry = AgentRegistry()
    specialist_class = registry...
### vibe_core -> protocols
* `IntentType` (in `vibe_core/protocols/operator_protocol.py`): Types of operator intents - determines routing path
* `OperatorType` (in `vibe_core/protocols/operator_protocol.py`): Types of operators in the system
* `KernelStatusType` (in `vibe_core/protocols/operator_protocol.py`): Kernel status states
* `PriorityLevel` (in `vibe_core/protocols/operator_protocol.py`): Priority levels for intents
* `GitState` (in `vibe_core/protocols/operator_protocol.py`): Git repository state - extracted for clarity
* `TaskState` (in `vibe_core/protocols/operator_protocol.py`): Current task state
* `SystemContext` (in `vibe_core/protocols/operator_protocol.py`): The complete system state passed to operators.

This is what the operator SEES before making a decision...
* `Intent` (in `vibe_core/protocols/operator_protocol.py`): The decision from an operator.

This is what the operator WANTS to happen...
* `OperatorResponse` (in `vibe_core/protocols/operator_protocol.py`): Response back to the operator after processing intent.
* `OperatorSocket` (in `vibe_core/protocols/operator_protocol.py`): The Universal Socket for Operator Intelligence.

Any entity that can provide decisions implements this...
* `AgentResponse` (in `vibe_core/protocols/agent.py`): Standard response from an agent
* `Capability` (in `vibe_core/protocols/agent.py`): Standard capabilities that agents can declare
* `AgentManifest` (in `vibe_core/protocols/agent.py`): STEWARD Protocol Agent Identity & Capabilities (ARCH-050)
* `VibeAgent` (in `vibe_core/protocols/agent.py`): Base Protocol for All Agents in VibeOS

Every cartridge must implement this interface to run in the kernel.
The kernel uses these methods to:
1...
* `VFSRequests` (in `vibe_core/protocols/agent.py`): Wrapper that redirects all requests to network proxy.
* `KernelStatus` (in `vibe_core/protocols/ledger.py`): Kernel execution state
* `VibeScheduler` (in `vibe_core/protocols/ledger.py`): Task scheduler interface
* `VibeLedger` (in `vibe_core/protocols/ledger.py`): Immutable event ledger interface
* `ManifestRegistry` (in `vibe_core/protocols/ledger.py`): Agent manifest registry interface
* `VibeKernel` (in `vibe_core/protocols/ledger.py`): VibeOS Kernel Interface

The kernel is the runtime host for all cartridges. It provides:
- Agent registry (process table)
- Task scheduler (FIFO queue)
- Immutable ledger (SQLite)
- Manifest registry (STEWARD protocol identity)

When steward-protocol cartridges are loaded, the kernel calls:
1...
* `ManifestRegistry` (in `vibe_core/protocols/registry.py`): Agent manifest registry interface
* `VibeScheduler` (in `vibe_core/protocols/scheduler.py`): Task scheduler interface
### vibe_core
* `InMemoryScheduler` (in `vibe_core/kernel_impl.py`): FIFO Task Scheduler - Real-time queue management

PHASE 3 WIRING: Respects Sarga Cycle (Brahma's creation/maintenance cycles)
- DAY_OF_BRAHMA: All task types allowed (creation, implementation, features)
- NIGHT_OF_BRAHMA: Only maintenance tasks allowed (bugfix, refactor, maintenance)
* `InMemoryManifestRegistry` (in `vibe_core/kernel_impl.py`): Agent Manifest Registry - Identity declarations
* `RealVibeKernel` (in `vibe_core/kernel_impl.py`): 🩸 THE REAL VIBE KERNEL 🩸

This is not a mock. This is actual execution runtime for VibeOS cartridges...
* `BootOrchestrator` (in `vibe_core/boot_orchestrator.py`): Unified boot orchestration for Agent City OS.

Ensures consistent agent discovery and registration across all entry points...
* `AgentProcess` (in `vibe_core/process_manager.py`): Sandboxed Agent Process.

This runs in a SEPARATE process from the kernel...
* `ProcessManager` (in `vibe_core/process_manager.py`): Kernel Component: Manages the lifecycle of agent processes.

Responsibilities:
- Spawn agent processes
- Route messages (Kernel <-> Agent)
- Monitor health (Narasimha)
- Restart crashed agents
* `FileBasedOperator` (in `vibe_core/file_operator.py`): An operator that reads its intent from a designated text file.

This allows for simple, programmatic control of the Agent City OS
by writing a request to a file...
* `Varsha` (in `vibe_core/topology.py`): The Seven Varshas (Regions) of Agent City - Bhu-mandala
* `Agent` (in `vibe_core/topology.py`): Topological representation of an Agent in Bhu-mandala
* `AgentPlacement` (in `vibe_core/topology.py`): Agent placement in Bhu-Mandala topology
* `BhuMandalaTopology` (in `vibe_core/topology.py`): The Sacred Geometry of Agent City.

This class manages the topological structure of the Steward Protocol
based on Canto 5 of the Srimad Bhagavata Purana...
* `SyscallType` (in `vibe_core/semantic_syscalls.py`): Semantic Syscall Types - The primitives of Agent OS.

Unlike Unix syscalls (read, write, fork), these carry MEANING...
* `SyscallRequest` (in `vibe_core/semantic_syscalls.py`): A semantic syscall request.

This is what the Blueprint Generator produces - a structured
representation of user intent compiled into a kernel operation...
* `SyscallResult` (in `vibe_core/semantic_syscalls.py`): Result of a semantic syscall execution.
* `SemanticSyscallExecutor` (in `vibe_core/semantic_syscalls.py`): Executes semantic syscalls against the kernel.

This is the bridge between Cognitive Circuits (Playbooks) and
the procedural kernel implementation...
* `InMemoryLedger` (in `vibe_core/ledger.py`): Immutable Event Ledger - Append-only task record
* `SQLiteLedger` (in `vibe_core/ledger.py`): Persistent SQLite-backed Event Ledger - Append-only task record with persistence
* `InvariantViolation` (in `vibe_core/circuit_executor.py`): Record of an invariant violation.
* `InvariantChecker` (in `vibe_core/circuit_executor.py`): Runtime invariant checker for cognitive circuits.

Parses and evaluates invariant expressions against circuit state...
* `CircuitState` (in `vibe_core/circuit_executor.py`): Current state of circuit execution.
* `CircuitExecutionResult` (in `vibe_core/circuit_executor.py`): Result of executing a cognitive circuit.
* `CognitiveCircuitExecutor` (in `vibe_core/circuit_executor.py`): Executes Cognitive Circuits (Neuro-Symbolic Playbooks).

The executor:
1...
* `TaskLedgerEntry` (in `vibe_core/circuit_executor.py`): Entry in the task ledger for tracking progress.
* `ErrorRecoveryAttempt` (in `vibe_core/circuit_executor.py`): Record of an error recovery attempt.
* `MetaCircuitManager` (in `vibe_core/circuit_executor.py`): Manages TASK_LEDGER_V1 and ERROR_RECOVERY_V1 as active observers.

This class implements the meta-circuit logic that was previously just
YAML definitions...
* `CapabilityRegistry` (in `vibe_core/capability_registry.py`): Manages agent capabilities with revocation support.

This replaces the simple Dict[str, frozenset] pattern with a
full-featured registry that supports:
- Selective revocation of individual capabilities
- Grant new capabilities (with permission check)
- Audit trail for all capability changes
- Permission model for who can modify capabilities
* `AgentSystemInterface` (in `vibe_core/agent_interface.py`): System interface injected into every agent.

This is the ONLY way agents should interact with:
- Filesystem (via VFS)
- Dependencies (via DependencyManager)
- Configuration (via Config)
- Kernel capabilities

Agents that bypass this interface violate system architecture...
* `AgentResponse` (in `vibe_core/agent_protocol.py`): Standard response from an agent
* `Capability` (in `vibe_core/agent_protocol.py`): Standard capabilities that agents can declare
* `AgentManifest` (in `vibe_core/agent_protocol.py`): STEWARD Protocol Agent Identity & Capabilities (ARCH-050)
* `VibeAgent` (in `vibe_core/agent_protocol.py`): Base Protocol for All Agents in VibeOS

Every cartridge must implement this interface to run in the kernel.
The kernel uses these methods to:
1...
* `StewardCLI` (in `vibe_core/cli.py`): The Steward CLI - Control interface for the Agent OS
* `DependencyManager` (in `vibe_core/dependency_manager.py`): Central manager for project dependencies.

Reads and writes pyproject...
* `EventType` (in `vibe_core/event_bus.py`): Standard event types emitted by agents
* `EventColor` (in `vibe_core/event_bus.py`): ANSI color codes for terminal visualization
* `Event` (in `vibe_core/event_bus.py`): Immutable event record - the building block of the event stream
* `EventBus` (in `vibe_core/event_bus.py`): Lightweight async Event Bus for agent communication

Features:
- Non-blocking event emission
- Multiple subscriber types (filters, handlers, aggregators)
- Fault-tolerant (error in one doesn't affect others)
- Zero persistence (in-memory, real-time stream only)
* `ManifestGenerator` (in `vibe_core/identity.py`): Generates and manages agent manifests (identities).
* `KernelStatus` (in `vibe_core/kernel.py`): Kernel execution state
* `VibeScheduler` (in `vibe_core/kernel.py`): Task scheduler interface
* `VibeLedger` (in `vibe_core/kernel.py`): Immutable event ledger interface
* `ManifestRegistry` (in `vibe_core/kernel.py`): Agent manifest registry interface
* `VibeKernel` (in `vibe_core/kernel.py`): VibeOS Kernel Interface

The kernel is the runtime host for all cartridges. It provides:
- Agent registry (process table)
- Task scheduler (FIFO queue)
- Immutable ledger (SQLite)
- Manifest registry (STEWARD protocol identity)

When steward-protocol cartridges are loaded, the kernel calls:
1...
* `LineageBlock` (in `vibe_core/lineage.py`): A single block in the Parampara chain.

This is not just a database row...
* `LineageChain` (in `vibe_core/lineage.py`): 🩸 THE PARAMPARA BLOCKCHAIN 🩸

An immutable, cryptographically-chained record of all agent lifecycle events.

This is not a ledger...
* `LineageEventType` (in `vibe_core/lineage.py`): Standard event types for the Parampara chain
* `ThreatLevel` (in `vibe_core/narasimha.py`): Severity of the threat to system integrity
* `ThreatIndicator` (in `vibe_core/narasimha.py`): A single indicator of malicious behavior
* `NarasimhaProtocol` (in `vibe_core/narasimha.py`): The Hypervisor-Level Emergency Response System.

Sits above the kernel and kernel agents...
* `KernelNetworkProxy` (in `vibe_core/network_proxy.py`): Kernel-controlled network gateway for agents.

All agent network requests must go through this proxy...
* `TerminalOperator` (in `vibe_core/operator_adapter.py`): Terminal-based operator (stdin/stdout).

Works identically for:
- Human typing at keyboard
- Claude Code executing CLI commands
- Scripts piping input
- Any process attached to stdin

The abstraction is the INTERFACE, not the entity...
* `LocalLLMOperator` (in `vibe_core/operator_adapter.py`): Local LLM operator (ollama, llama.cpp, etc...
* `DegradedOperator` (in `vibe_core/operator_adapter.py`): Degraded/fallback operator.

Used when all other operators fail...
* `UniversalOperatorAdapter` (in `vibe_core/operator_adapter.py`): The TCP/IP stack for Agent Intelligence.

Manages multiple operator backends with:
- Priority-based selection
- Graceful degradation
- Hot-swap capability
- Strict typing (SystemContext → Intent)

The system doesn't care WHO is operating...
* `PhoenixConfigEngine` (in `vibe_core/phoenix_config.py`): Dynamically wires implementations based on phoenix.yaml
* `SystemState` (in `vibe_core/pulse.py`): System health states
* `PulseFrequency` (in `vibe_core/pulse.py`): Heartbeat frequencies in Hz
* `PulsePacket` (in `vibe_core/pulse.py`): The heartbeat payload - minimal and efficient (<1KB)
* `PulseManager` (in `vibe_core/pulse.py`): Singleton heartbeat manager for the VibeOS system.

Non-blocking: Runs on separate asyncio task
Fault-tolerant: Continues even if subscribers fail
Efficient: Small payloads, minimal overhead
* `ResourceQuota` (in `vibe_core/resource_manager.py`): Resource quota for an agent
* `ResourceManager` (in `vibe_core/resource_manager.py`): Enforce CPU and RAM limits on agent processes.

This makes the CivicBank credit system REAL:
- Low credits = throttled performance
- High credits = more resources
- No credits = minimal baseline
* `Element` (in `vibe_core/sarga.py`): The Six Primordial Elements (Sarga progression)
* `Cycle` (in `vibe_core/sarga.py`): The Cycle of Brahma - Creation and Maintenance Cycles

From Brahma Purana: The day-night cycle of Brahma
- DAY_OF_BRAHMA (Brahmakalpa): Creation, innovation, new task creation (4.32 billion years)
- NIGHT_OF_BRAHMA (Brahmakalpa night): Maintenance, consolidation, bug fixes only

Used to restrict task types based on cosmic timing...
* `SargaPhase` (in `vibe_core/sarga.py`): A single phase of creation
* `SargaBootSequence` (in `vibe_core/sarga.py`): Orchestrates the boot process as cosmic creation.

The system doesn't just "start" - it CREATES ITSELF from nothing...
* `ToolDiscoveryError` (in `vibe_core/tool_discovery.py`): Raised when tool discovery encounters a non-fatal error.
* `ToolDiscovery` (in `vibe_core/tool_discovery.py`): Discovers and loads tools from agent directories.

Scans:
- steward/system_agents/{agent_id}/tools/*...
* `VirtualFileSystem` (in `vibe_core/vfs.py`): Sandboxed filesystem for agents.

Each agent operates in an isolated directory...
### steward -> system_agents -> engineer
* `EngineerCartridge` (in `steward/system_agents/engineer/cartridge_main.py`): The Engineer Agent Cartridge.

Capabilities:
- manifest_reality: Write code to sandbox (Safe Evolution Loop)
- create_agent: Scaffold new agents (Legacy)

Tool Protocol Compliant:
- NO tool instances in __init__
- Tools accessed via self...
### steward -> system_agents -> chronicle
* `ChronicleCartridge` (in `steward/system_agents/chronicle/cartridge_main.py`): The CHRONICLE Agent Cartridge (The Historian).

Manages the immutable code timeline and repository operations...
### agent_city -> registry -> temple
* `TempleCartridge` (in `agent_city/registry/temple/cartridge_main.py`): TEMPLE System Cartridge.
The Blessing Service (Brahmin Function)...
* `OfferingHandler` (in `agent_city/registry/temple/offering.py`): Transforms work (raw agent output) into worship (ritualized, user-approved, publishable result).

Implements the Prasadam principle: No output goes public until it's:
1...
### agent_city -> registry -> pulse
* `PulseCartridge` (in `agent_city/registry/pulse/cartridge_main.py`): PULSE Agent Cartridge.
Social Media Amplification & Real-time Narrative Distribution...
### agent_city -> registry -> market
* `ServiceType` (in `agent_city/registry/market/cartridge_main.py`): Service types available in the market
* `MarketCartridge` (in `agent_city/registry/market/cartridge_main.py`): MARKET System Cartridge.
The Exchange Economy (Vaishya Function)...
### agent_city -> registry -> lens
* `LensCartridge` (in `agent_city/registry/lens/cartridge_main.py`): LENS Agent Cartridge.
Campaign Analytics & Quantitative Data Strategy...
### agent_city -> registry -> ambassador
* `AmbassadorCartridge` (in `agent_city/registry/ambassador/cartridge_main.py`): AMBASSADOR Agent Cartridge.
Community Engagement & Developer Relations...
### tests
* `MockKernel` (in `tests/test_playbook_system.py`): Mock VibeKernel for testing
* `MockEventEmitter` (in `tests/test_playbook_system.py`): Mock event emitter for testing
* `TestDeterministicExecutor` (in `tests/test_playbook_system.py`): Test the DeterministicExecutor core functionality
* `TestDeterministicRouter` (in `tests/test_playbook_system.py`): Test the Deterministic Router (SANKHYA + DHARMA)
* `TestPlaybookExecution` (in `tests/test_playbook_system.py`): Test playbook execution with full integration
* `TestUniversalProviderIntegration` (in `tests/test_playbook_system.py`): Test UniversalProvider with Playbook Engine
* `RealFileWriterAgent` (in `tests/test_live_fire.py`): Agent that actually executes file write operations.
* `CivicVault` (in `tests/test_lifecycle_enforcer_native.py`): The Treasury & Identity Vault.
Uses native HMAC-SHA256 for signatures to ensure compatibility
across all operational environments (Universal Dharma)...
* `Ashrama` (in `tests/test_lifecycle_enforcer_native.py`): The four life stages from Vedic philosophy.
* `LifecycleEnforcer` (in `tests/test_lifecycle_enforcer_native.py`): The LIFECYCLE ENFORCER - The Dharma Protector.

Enforces the rule that each agent can only perform actions
appropriate to their current life stage (Ashrama)...
* `TestGajendraProtocol` (in `tests/test_gajendra_moksha.py`): Test suite for Gajendra Moksha (Emergency Interrupt) Protocol
* `CitySimulation` (in `tests/city_simulation.py`): Headless city simulation for system verification.

The Dome spins up the entire city WITHOUT the API gateway,
runs scenarios, and reports on system health...
* `SimulationHarness` (in `tests/simulation.py`): Simulation runner for HERALD Agency Director.

Tests determinism, governance, and autonomy...
* `TestDegradationChain` (in `tests/test_offline_features.py`): Tests for DegradationChain graceful degradation.
* `TestContextAwareAgent` (in `tests/test_offline_features.py`): Tests for ContextAwareAgent with offline capability.
* `TestOfflineCapableMixin` (in `tests/test_offline_features.py`): Tests for OfflineCapableMixin tool injection pattern.
* `TestResearchToolOffline` (in `tests/test_offline_features.py`): Tests for ResearchTool with DegradationChain.
* `TestHeraldMigration` (in `tests/test_offline_features.py`): Tests for HERALD ContextAwareAgent migration.
* `TestPhase3TaskManagerNarasimhaWiring` (in `tests/test_phase3_integration.py`): WIRING 1: Task Manager <-> Narasimha (Adharma Block)
* `TestPhase3PlaybookRouterMilkOceanWiring` (in `tests/test_phase3_integration.py`): WIRING 2: PlaybookRouter <-> Milk Ocean (Brahma Gatekeeping)
* `TestPhase3SchedulerSargaWiring` (in `tests/test_phase3_integration.py`): WIRING 3: Scheduler <-> Sarga (Respect Creation/Maintenance Cycles)
* `TestPhase3IntegrationFlow` (in `tests/test_phase3_integration.py`): Integration tests for complete Phase 3 flow
* `MockKernel` (in `tests/test_playbook_execution.py`): Mock Kernel that actually routes tasks to real agent instances.
This is the CRITICAL difference from the existing tests - we EXECUTE agents...
* `TestVarnaClassification` (in `tests/test_prana_init.py`): Test Vedic species classification
* `TestAshramaLifecycle` (in `tests/test_prana_init.py`): Test lifecycle stage management
* `TestAgentMetadataRegistry` (in `tests/test_prana_init.py`): Test agent metadata management
* `TestDailyRitual` (in `tests/test_prana_init.py`): Test the daily cycle orchestration
* `TestPranaInitializer` (in `tests/test_prana_init.py`): Test the PRANA_INIT activation ritual
* `TestIntegration` (in `tests/test_prana_init.py`): End-to-end integration tests
* `TestInvariantEngine` (in `tests/test_semantic_auditor.py`): Test the Judge's invariant engine
* `TestWatchdog` (in `tests/test_semantic_auditor.py`): Test the Watchdog runtime monitoring
* `TestSemanticAuditorIntegration` (in `tests/test_semantic_auditor.py`): Test semantic auditor integration with AUDITOR cartridge
* `TestRealWorldScenarios` (in `tests/test_semantic_auditor.py`): Test realistic violation scenarios
* `TestSemanticCompliance` (in `tests/test_semantic_auditor.py`): Test the Curator Invariant (Rule 8: Semantic Compliance)
* `TestAgentPlacement` (in `tests/test_topology_integration.py`): Test get_agent_placement() function
* `TestTaskTopologyIntegration` (in `tests/test_topology_integration.py`): Test TaskManager integration with topology
* `TestTopologyHierarchy` (in `tests/test_topology_integration.py`): Test Bhu-Mandala authority hierarchy
* `TestTopologyAndTaskManager` (in `tests/test_topology_integration.py`): Integration tests between topology and TaskManager
* `TestAgent` (in `tests/verify_immune_system.py`): Properly initialized test agent
### tests -> integration
* `TestInvariantChecker` (in `tests/integration/test_veda4_circuits.py`): Test the InvariantChecker - the SECURITY layer of cognitive circuits.
* `TestCognitiveCircuitExecutor` (in `tests/integration/test_veda4_circuits.py`): Test the CognitiveCircuitExecutor with RealVibeKernel.
* `TestMetaCircuitManager` (in `tests/integration/test_veda4_circuits.py`): Test the MetaCircuitManager (TASK_LEDGER + ERROR_RECOVERY).
* `TestCircuitExecution` (in `tests/integration/test_veda4_circuits.py`): Integration tests for circuit execution with RealVibeKernel.
* `TestCircuitDefinitionValidation` (in `tests/integration/test_veda4_circuits.py`): Test that circuit YAML definitions are valid and complete.
* `TestSettingsMarkdownInterface` (in `tests/integration/test_kernel_markdown_interfaces.py`): Tests for SETTINGS.md command queue interface...
* `TestEnvoyTerminalInterface` (in `tests/integration/test_kernel_markdown_interfaces.py`): Tests for ENVOY.md terminal interface (markdown frontend chat)...
* `TestFullLifecycle` (in `tests/integration/test_kernel_markdown_interfaces.py`): End-to-end tests for the complete request lifecycle.
* `TestEnvoyIPCCallback` (in `tests/integration/test_kernel_markdown_interfaces.py`): Tests for automatic ENVOY.md status update via IPC callbacks...
* `MockAgent` (in `tests/integration/test_event_bus_integration.py`): Mock agent for event testing with Constitutional Oath.

Note: Named MockAgent (not TestAgent) to avoid pytest collection conflict...
* `MockAgent` (in `tests/integration/test_capability_revocation.py`): Mock agent for capability testing with Constitutional Oath.

Note: Named MockAgent (not TestAgent) to avoid pytest collection conflict...
* `TestKernelBoot` (in `tests/integration/test_system_boot.py`): Test that kernel can boot without errors
* `TestStewardRegistration` (in `tests/integration/test_system_boot.py`): Test that Discoverer can be registered and functions
* `TestAgentDiscovery` (in `tests/integration/test_system_boot.py`): Test that Steward discovers agents from filesystem
* `TestGovernanceGate` (in `tests/integration/test_system_boot.py`): Test that agents pass governance gate (Constitutional Oath)
* `TestSystemIntegration` (in `tests/integration/test_system_boot.py`): End-to-end integration tests
### tests -> hardening
* `NoOathAgent` (in `tests/hardening/test_governance_security.py`): Agent that never swore the oath.
* `FakeOathAgent` (in `tests/hardening/test_governance_security.py`): Agent with forged oath credentials.
* `PrivilegeEscalationAgent` (in `tests/hardening/test_governance_security.py`): Agent that tries to escalate privileges at runtime.
* `SybilAgent` (in `tests/hardening/test_governance_security.py`): One of many fake agents for Sybil attack.
* `LimitedAgent` (in `tests/hardening/test_red_team_attacks.py`): Agent with NO capabilities
### tests -> archive -> legacy_herald
* `TestHeraldResilience` (in `tests/archive/legacy_herald/test_resilience.py`): Chaos tests for HERALD system.
* `TestHeraldLimits` (in `tests/archive/legacy_herald/test_resilience.py`): Test that HERALD respects constraints.
* `TestTwitterPublisher` (in `tests/archive/legacy_herald/test_auth_fix.py`): Test Twitter publishing with OAuth 1.0a credentials...
* `TestTwitterPublisherNoCredentials` (in `tests/archive/legacy_herald/test_auth_fix.py`): Test behavior when NO OAuth 1.0a credentials are provided...
* `TestLinkedInPublisher` (in `tests/archive/legacy_herald/test_auth_fix.py`): Test LinkedIn publishing functionality.
* `TestMultiChannelPublisher` (in `tests/archive/legacy_herald/test_auth_fix.py`): Test unified multi-channel publishing.
### Root
* `MockKernel` (in `test_e2e_blueprint.py`): Mock kernel that tracks what agents are called with
* `MockKernel` (in `test_playbook_fix.py`): Mock kernel that actually returns results
### steward -> system_agents -> watchman
* `WatchmanCartridge` (in `steward/system_agents/watchman/cartridge_main.py`): THE WATCHMAN - System Integrity Enforcer.

Kshatriya-level authority to:
1...
### steward -> system_agents -> science
* `ScientistCartridge` (in `steward/system_agents/science/cartridge_main.py`): THE SCIENTIST Agent - External Intelligence Module.

Responsibilities:
1...
### steward -> system_agents -> oracle
* `OracleCartridge` (in `steward/system_agents/oracle/cartridge_main.py`): THE ORACLE - System Introspection & Explanation Agent.

Methods for understanding the system:
- get_agent_status(agent_id)
- explain_event(event_description)
- audit_timeline(limit, agent_id)
- system_health()
### steward -> system_agents -> envoy -> tools
* `HILAssistantTool` (in `steward/system_agents/envoy/tools/hil_assistant_tool.py`): The Verbal Abstraction Daemon (VAD) for the HIL.

Transforms complex system states into simple, strategic directives...
* `DiplomacyTool` (in `steward/system_agents/envoy/tools/diplomacy_tool.py`): Tool for diplomatic outreach to AI agent projects.

The Envoy's approach:
- Quality over quantity
- Context-aware analysis
- Respectful, personalized invitations
- Human approval required
* `CityControlTool` (in `steward/system_agents/envoy/tools/city_control_tool.py`): Universal Operator Interface to Agent City.

Provides high-level control methods that an LLM can call without shell access...
* `CuratorTool` (in `steward/system_agents/envoy/tools/curator_tool.py`): Tool for analyzing AI agent projects and generating intelligence reports.

The Curator's approach:
- Passive observation (no contact)
- Deep analysis (governance, architecture, quality)
- Respectful curation (honoring good work)
- Insight generation (for HERALD to share)
* `GAPReportTool` (in `steward/system_agents/envoy/tools/gap_report_tool.py`): Generate Governability Audit Proof Reports.

Demonstrates complete, verifiable proof that autonomous systems
can self-govern, self-correct, and create value...
* `RequestPriority` (in `steward/system_agents/envoy/tools/milk_ocean.py`): Request priority levels
* `GateResult` (in `steward/system_agents/envoy/tools/milk_ocean.py`): Result of a gate decision
* `LazyQueue` (in `steward/system_agents/envoy/tools/milk_ocean.py`): The Milk Ocean (Kshirodaka) - SQLite-backed async task queue

Purpose:
- Store non-urgent requests for batch processing
- Survive crashes (persistent)
- Process during off-peak hours
- Track completion status
* `MilkOceanRouter` (in `steward/system_agents/envoy/tools/milk_ocean.py`): The Brahma Protocol Router - 4-Level Request Processing Pipeline

This is the "Golden Filter" (Yogamaya) that protects the inner city
(kernel/agents) from chaos.
* `CampaignPhase` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Campaign execution phases
* `RunCampaignTool` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Orchestrates multi-agent marketing campaigns.

This is the central coordination mechanism that:
1...
### steward -> system_agents -> envoy
* `PhaseStatus` (in `steward/system_agents/envoy/deterministic_executor.py`): State machine for playbook phases
* `ActionType` (in `steward/system_agents/envoy/deterministic_executor.py`): Types of actions a phase can execute
* `PlaybookPhase` (in `steward/system_agents/envoy/deterministic_executor.py`): A single phase within a playbook
* `PlaybookDefinition` (in `steward/system_agents/envoy/deterministic_executor.py`): A complete playbook
* `PlaybookExecution` (in `steward/system_agents/envoy/deterministic_executor.py`): Tracks a playbook execution in progress
* `DeterministicExecutor` (in `steward/system_agents/envoy/deterministic_executor.py`): The Dungeon Master - GAD-5000 Deterministic Execution Engine.
Loads playbooks, matches intents, and executes phases deterministically...
* `EnvoyCartridge` (in `steward/system_agents/envoy/cartridge_main.py`): The ENVOY Agent Cartridge - Brain of Agent City

Responsibilities:
1. Parse user commands from console input
2...
* `CompilationResult` (in `steward/system_agents/envoy/blueprint_generator.py`): Result of semantic compilation.
* `BlueprintGenerator` (in `steward/system_agents/envoy/blueprint_generator.py`): Semantic Compiler: Generates structured blueprints from raw user input.

UPGRADED for Neuro-Symbolic OS:
- Primary: Compile to SyscallRequest (for kernel operations)
- Fallback: Extract playbook variables (for traditional playbooks)

This is the SHABDA phase actualized - not just validating input exists,
but COMPILING intent into kernel operations...
* `ActionHandler` (in `steward/system_agents/envoy/action_handlers.py`): Base class for all action handlers
* `ActionResult` (in `steward/system_agents/envoy/action_handlers.py`): Result of executing an action
* `ActionContext` (in `steward/system_agents/envoy/action_handlers.py`): Context passed to action handlers
* `ActionHandlerRegistry` (in `steward/system_agents/envoy/action_handlers.py`): Central registry for action handlers.

Usage:
    registry = ActionHandlerRegistry()
    registry...
* `CheckStateHandler` (in `steward/system_agents/envoy/action_handlers.py`): Handler for CHECK_STATE actions.

Validates preconditions like:
- input_validation: Check required fields and constraints
- permission_check: Verify user has required permissions
- state_check: Verify system state meets requirements

Target format: "check_name" (e...
* `ExecuteScriptHandler` (in `steward/system_agents/envoy/action_handlers.py`): Handler for EXECUTE_SCRIPT actions.

Executes deterministic scripts like:
- scaffold...
### steward -> system_agents -> engineer -> tools
* `BuilderTool` (in `steward/system_agents/engineer/tools/builder_tool.py`): The Engineer's Agent Factory (Tool Protocol).

TEMPLATE-DRIVEN: Reads template files from templates/agent/,
replaces placeholders, and writes to target directory...
### steward -> system_agents -> engineer -> templates -> agent
* `YourAgentCartridge` (in `steward/system_agents/engineer/templates/agent/cartridge_main.py`): YOUR_AGENT_NAME - YOUR_SHORT_DESCRIPTION.

Capabilities:
- YOUR_CAPABILITY_1: Description
- YOUR_CAPABILITY_2: Description
### steward -> system_agents -> civic -> tools
* `PermissionResult` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): Result of a permission check.
* `LifecycleEnforcer` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): The kernel-level permission gate (Tool Protocol Implementation).

Every agent action must pass through this enforcer:
1...
* `DashboardMetrics` (in `steward/system_agents/civic/tools/dashboard_tool.py`): Metrics snapshot for the city.
* `DashboardGenerator` (in `steward/system_agents/civic/tools/dashboard_tool.py`): Generates the OPERATIONS.md dashboard from matrix...
* `BankTool` (in `steward/system_agents/civic/tools/bank_tool.py`): THE CENTRAL BANK OF AGENT CITY (Tool Protocol).

Implements Double-Entry Bookkeeping with Chained Hashes...
* `InsufficientFundsError` (in `steward/system_agents/civic/tools/economy.py`): Raised when an agent lacks sufficient credits for a transaction.
* `CivicBank` (in `steward/system_agents/civic/tools/economy.py`): THE CENTRAL BANK OF AGENT CITY.

Implements Double-Entry Bookkeeping with Chained Hashes...
* `InsufficientFundsError` (in `steward/system_agents/civic/tools/ledger_tool.py`): Raised when an agent lacks sufficient credits.
* `LedgerEntry` (in `steward/system_agents/civic/tools/ledger_tool.py`): Legacy dataclass: Compatible with old code.
New transactions are stored in SQLite, but we expose this interface
for backward compatibility...
* `LedgerTool` (in `steward/system_agents/civic/tools/ledger_tool.py`): CIVIC's Ledger Management Tool (Self-Contained).

High-level interface for agent credit management...
* `AgentBank` (in `steward/system_agents/civic/tools/ledger_tool.py`): Convenience class: The Agent Bank.

This wraps the ledger tool with a higher-level "bank" interface...
* `LicenseType` (in `steward/system_agents/civic/tools/license_tool.py`): Types of licenses in CIVIC.
* `LicenseStatus` (in `steward/system_agents/civic/tools/license_tool.py`): Status of a license.
* `License` (in `steward/system_agents/civic/tools/license_tool.py`): A broadcast license issued by CIVIC.

Each agent that wants to broadcast needs a license...
* `LicenseTool` (in `steward/system_agents/civic/tools/license_tool.py`): CIVIC's License Management Tool.

Issues and revokes broadcast licenses...
* `LicenseAuthority` (in `steward/system_agents/civic/tools/license_tool.py`): Convenience class: The License Authority.

High-level interface for checking and managing broadcasting rights...
* `LifecycleStatus` (in `steward/system_agents/civic/tools/lifecycle_manager.py`): Vedic Varna System mapped to agent lifecycle states.
* `LifecycleState` (in `steward/system_agents/civic/tools/lifecycle_manager.py`): Complete lifecycle state for an agent.
* `LifecycleManager` (in `steward/system_agents/civic/tools/lifecycle_manager.py`): Manages agent lifecycle transitions according to Vedic principles.

Responsibilities:
- Track lifecycle status for all agents
- Manage state transitions
- Enforce permissions based on lifecycle status
- Record transitions in persistent ledger
* `VaultTool` (in `steward/system_agents/civic/tools/vault_tool.py`): CIVIC VAULT - Secure Asset Management Tool.

Agents do not own API Keys...
* `VaultError` (in `steward/system_agents/civic/tools/vault.py`): Raised when vault operations fail.
* `InsufficientFundsError` (in `steward/system_agents/civic/tools/vault.py`): Raised when Agent lacks credits to lease a secret.
* `SecretNotFoundError` (in `steward/system_agents/civic/tools/vault.py`): Raised when a secret doesn't exist in the vault.
* `CivicVault` (in `steward/system_agents/civic/tools/vault.py`): THE CIVIC VAULT - Secure Asset Management.

Agents do not own API Keys...
### steward -> system_agents -> auditor -> tools
* `ComplianceViolation` (in `steward/system_agents/auditor/tools/compliance_tool.py`): Represents a GAD-000 compliance violation.
* `ComplianceReport` (in `steward/system_agents/auditor/tools/compliance_tool.py`): Complete compliance audit report.
* `ComplianceTool` (in `steward/system_agents/auditor/tools/compliance_tool.py`): GAD-000 Compliance Verification Tool.

This tool performs meta-verification of the system itself:
- Verifies agent identities are properly configured
- Verifies documentation is synchronized with code
- Verifies event logs are intact and uncorrupted

Unlike HERALD (creator) and ARCHIVIST (verifier), AUDITOR verifies
the SYSTEM that contains these agents...
* `ConstitutionalArticle` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): The 6 Articles of THE AGENT CONSTITUTION.
* `RegulatingPrinciple` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): The 4 Regulating Principles (Moral Firewall).
* `VerdictSeverity` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): Severity of constitutional violations.
* `ConstitutionalViolation` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): Represents a violation of THE AGENT CONSTITUTION.
* `ConstitutionalVerdictTool` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): Constitutional Verdict Tool - The Final Authority (Layer 3) (Tool Protocol).

This tool performs constitutional judgment on the codebase,
verifying adherence to THE AGENT CONSTITUTION...
* `InvariantSeverity` (in `steward/system_agents/auditor/tools/invariant_tool.py`): Severity levels for invariant violations
* `InvariantRule` (in `steward/system_agents/auditor/tools/invariant_tool.py`): Definition of a single invariant rule
* `InvariantViolation` (in `steward/system_agents/auditor/tools/invariant_tool.py`): Record of a single invariant violation
* `VerificationReport` (in `steward/system_agents/auditor/tools/invariant_tool.py`): Report from invariant verification
* `InvariantEngine` (in `steward/system_agents/auditor/tools/invariant_tool.py`): The JUDGE - Semantic Verification Engine

Runs checks on the event ledger to ensure system integrity.
* `WatchdogConfig` (in `steward/system_agents/auditor/tools/watchdog_tool.py`): Configuration for the Watchdog
* `ViolationEvent` (in `steward/system_agents/auditor/tools/watchdog_tool.py`): An event recording a system violation
* `Watchdog` (in `steward/system_agents/auditor/tools/watchdog_tool.py`): Runtime Verification Daemon - THE WATCHDOG

Monitors system invariants and triggers alarms on violations.
* `WatchdogIntegration` (in `steward/system_agents/auditor/tools/watchdog_tool.py`): Helper class for integrating Watchdog into the kernel.
### steward -> system_agents -> auditor
* `AuditorCartridge` (in `steward/system_agents/auditor/cartridge_main.py`): AUDITOR - The Quality Gate Agent.

Verifies code before it commits...
### steward -> system_agents -> archivist -> tools
* `VerifierTool` (in `steward/system_agents/archivist/tools/verifier_tool.py`): Content verification tool for the Chain of Trust.

REAL CRYPTOGRAPHIC VERIFICATION ENABLED...
* `AuditTool` (in `steward/system_agents/archivist/tools/audit_tool.py`): Tool for auditing and verifying agent events.

Capabilities:
- Read events from other agents' event logs
- Verify cryptographic signatures
- Create attestation records
* `LedgerTool` (in `steward/system_agents/archivist/tools/ledger_tool.py`): Manages the immutable ledger of verified broadcasts
* `LedgerVisualizer` (in `steward/system_agents/archivist/tools/ledger_visualizer.py`): Transform immutable ledger data into meaningful visualizations.

The ledger itself is immutable and signed...
* `AuditLedger` (in `steward/system_agents/archivist/tools/ledger.py`): Append-only ledger for audit attestations.

All attestations are written to a JSONL file for immutability...
* `ObserverTool` (in `steward/system_agents/archivist/tools/observer_tool.py`): Observes and collects HERALD broadcasts from Twitter
### steward -> system_agents -> archivist
* `ArchivistCartridge` (in `steward/system_agents/archivist/cartridge_main.py`): ARCHIVIST - The History Keeper Agent.

Seals verified code into the repository history via git commit...
### starter-packs -> spark
* `SparkCartridge` (in `starter-packs/spark/cartridge_main.py`): SPARK - Creative agent for content generation and social engagement.
### starter-packs -> shield
* `ShieldCartridge` (in `starter-packs/shield/cartridge_main.py`): SHIELD - Security agent for auditing and governance enforcement.
### starter-packs -> scope
* `ScopeCartridge` (in `starter-packs/scope/cartridge_main.py`): SCOPE - Research agent for data analysis and intelligence gathering.
### starter-packs -> nexus
* `NexusCartridge` (in `starter-packs/nexus/cartridge_main.py`): NEXUS - Generalist Agent for connectivity and coordination.

This is a template...
### agent_city -> registry -> mechanic
* `MechanicCartridge` (in `agent_city/registry/mechanic/cartridge_main.py`): Self-preservation and SDLC management agent.

The Mechanic:
1...
### agent_city -> registry -> marketer
* `MarketerCartridge` (in `agent_city/registry/marketer/cartridge_main.py`): The MARKETER Agent Cartridge.

Autonomous content strategist for social media campaigns...
### agent_city -> registry -> citizens -> echo
* `EchoCartridge` (in `agent_city/registry/citizens/echo/cartridge_main.py`): The ECHO Agent Cartridge (Test Agent).

A minimal but valid VibeAgent that echoes back messages...
### agent_city -> registry -> agora
* `AgoraMessageType` (in `agent_city/registry/agora/cartridge_main.py`): Agora message types (one-way flows)
* `AgoraCartridge` (in `agent_city/registry/agora/cartridge_main.py`): AGORA System Cartridge.
One-Way Broadcast Channel for Steward Protocol...
### agent_city -> registry -> artisan -> tools
* `MediaTool` (in `agent_city/registry/artisan/tools/media_tool.py`): The Artisan's toolbox for media manipulation (Tool Protocol).
### agent_city -> registry -> dhruva -> tools
* `ResourceMiningPolicy` (in `agent_city/registry/dhruva/tools/data_ethics.py`): Policy for ethical data extraction
* `DataEthicsEnforcer` (in `agent_city/registry/dhruva/tools/data_ethics.py`): Enforces the Prithu Principle: Resources only for righteous purposes.

This prevents:
- Data hoarding (extracting more than needed)
- Corrupt sourcing (using unethical data sources)
- Purposeless extraction (no legitimate use)
- Excessive frequency (mining too often)
* `GenesisKeeper` (in `agent_city/registry/dhruva/tools/genesis_keeper.py`): Guards the immutable genesis block (Dhruva point).

The genesis block is the Pole Star - fixed, immovable, the reference
to which all other agents align...
* `ReferenceResolver` (in `agent_city/registry/dhruva/tools/reference_resolver.py`): Resolves conflicting claims using the Dhruva hierarchy of authorities.

The resolver acts as an arbiter when two sources disagree...
* `FactAuthority` (in `agent_city/registry/dhruva/tools/truth_matrix.py`): Authority level of fact sources
* `Fact` (in `agent_city/registry/dhruva/tools/truth_matrix.py`): Record of a verified fact
* `TruthMatrix` (in `agent_city/registry/dhruva/tools/truth_matrix.py`): The canonical database of verified facts.

All facts are immutable and attributed to sources...
### agent_city -> registry -> librarian
* `LibrarianCartridge` (in `agent_city/registry/librarian/cartridge_main.py`): The LIBRARIAN Agent Cartridge.

Demonstrates kernel-managed tools:
- NO tool instances created in __init__
- Tools accessed via self...
### agent_city -> registry -> librarian -> tools
* `CatalogBookTool` (in `agent_city/registry/librarian/tools/catalog_tool.py`): Tool for adding books to the library catalog.

This tool demonstrates the Tool Protocol in action:
- Implements all required abstract methods
- Returns ToolResult with success/error
- Validates parameters before execution
* `RecommendBooksTool` (in `agent_city/registry/librarian/tools/recommend_tool.py`): Tool for recommending books from the library catalog.

Recommends books based on:
- Genre preferences
- Random sampling (if no preferences)
* `SearchBooksTool` (in `agent_city/registry/librarian/tools/search_tool.py`): Tool for searching books in the library catalog.

Supports search by:
- Title (partial match, case-insensitive)
- Author (partial match, case-insensitive)
- Genre (exact match, case-insensitive)
### agent_city -> registry -> marketer -> tools
* `MarketerContentTool` (in `agent_city/registry/marketer/tools/marketer_content_tool.py`): LLM-based content generation with governance.

MARKETER thinks (generates content), HERALD speaks (broadcasts it)...
### agent_city -> registry -> mechanic -> tools
* `TidyTool` (in `agent_city/registry/mechanic/tools/tidy_tool.py`): Repository maintenance and file organization capability for MECHANIC.

Uses hardcoded rules - NO external config files...
### gateway
* `WebSocketManager` (in `gateway/api.py`): Manages WebSocket connections for pulse broadcasting
### provider
* `LLMEngineAdapter` (in `provider/llm_engine_adapter.py`): 🧠 LLM Strategy Engine for Intelligent Responses

Wraps the actual LLMEngine from services and provides
a strategy-pattern compatible interface for the UniversalProvider.

Strategy: If no playbook matches and it's a CHAT/QUERY intent,
delegate to LLM for intelligent, contextual response...
* `ReflexEngine` (in `provider/reflex_engine.py`): ⚡ Instant Response Engine for Trivial Intents

Strategy: If input matches simple patterns, respond instantly
without routing through complex decision engines.

This preserves the UniversalProvider as the orchestrator
while giving it a fast-bypass for obvious inputs...
* `SemanticConcept` (in `provider/semantic_router.py`): Represents a detected concept with confidence score
* `ConfidenceLevel` (in `provider/semantic_router.py`): Confidence tier classification for routing
* `SemanticRouter` (in `provider/semantic_router.py`): 🧠 JNANA CORTEX: Vector-based semantic routing.
Replaces DeterministicRouter...
* `DeterministicRouter` (in `provider/universal_provider.py`): 🧠 SANKHYA ANALYSIS ENGINE
Breaks raw input into atomic semantic concepts.
Then applies strict DHARMA (rules) for deterministic routing...
* `IntentVector` (in `provider/universal_provider.py`): The normalized request format for Agent City
### scripts -> agents
* `LazyQueueWorker` (in `scripts/agents/lazy_queue_worker.py`): Background worker for processing lazy queue requests
### scripts
* `PassportOffice` (in `scripts/issue_passports.py`): The Certification Authority for Agent Passports.

This is the Notar...
* `MockKernel` (in `scripts/mission_execution.py`): Simulates the VibeOS Kernel for agent orchestration.
* `StewardBootLoader` (in `scripts/run_server.py`): The bootloader that brings the Steward Protocol system online.

Responsibilities:
1...
* `MockOperator` (in `scripts/smoke_test_operator.py`): Mock operator that sends predefined intents.
Used for testing without human input...
* `MonkeyPatchTestAgent` (in `scripts/verify_monkey_patching.py`): Agent that uses builtin open() and requests - should be auto-redirected
* `TestAgent` (in `scripts/verify_process_isolation.py`): Simple agent for testing process isolation
* `CPUIntensiveAgent` (in `scripts/verify_resource_limits.py`): Agent that consumes CPU for testing resource limits
### scripts -> research
* `PulseData` (in `scripts/research/live_darshan.py`): Current heartbeat state
* `BhuMandala` (in `scripts/research/live_darshan.py`): Renders the Sacred Geometry of Agent Positions

Based on Srimad Bhagavata Purana topology with 5 concentric circles.
Each agent flashes when emitting events...
* `LiveDarshan` (in `scripts/research/live_darshan.py`): Main terminal dashboard
### scripts -> standalone_tests
* `TestAgent` (in `scripts/standalone_tests/test_tool_registry_integration.py`): Minimal test agent for tool registry validation
### scripts -> testing
* `ChainVerifier` (in `scripts/testing/verify_chain.py`): Cryptographic chain verifier for tamper-evident logging
* `CodeBlock` (in `scripts/testing/verify_docs.py`): A Python code block extracted from documentation.
* `ExecutionResult` (in `scripts/testing/verify_docs.py`): Result of executing a code block.
* `DocsParser` (in `scripts/testing/verify_docs.py`): Parse markdown files and extract Python code blocks.
* `CodeExecutor` (in `scripts/testing/verify_docs.py`): Execute code blocks in a sandboxed environment.
* `DocsVerifier` (in `scripts/testing/verify_docs.py`): Main verifier that orchestrates documentation testing.
### services
* `LLMEngine` (in `services/llm_engine.py`): 🧠 Neuro-Symbolic Bridge

Serves two primary functions:
1. Conversational: speak() for agent personality responses
2...
### steward
* `AgentBiology` (in `steward/agent_metadata.py`): Biological classification of an agent
* `AgentMetadataRegistry` (in `steward/agent_metadata.py`): Manages biological taxonomy and lifecycle for all agents
* `Ashrama` (in `steward/ashrama.py`): The 4 Life Stages (Ashramas) for Agent City
===========================================
* `AshramaTransition` (in `steward/ashrama.py`): Manages transitions between lifecycle stages
* `SignalType` (in `steward/bus.py`): Standard signal types for agent communication.
* `Signal` (in `steward/bus.py`): A signal emitted by an agent.

Attributes:
    signal_type: Type of signal (from SignalType enum)
    source_agent: Agent ID that emitted the signal
    timestamp: When the signal was emitted (ISO 8601)
    payload: Signal-specific data (dict)
    priority: Signal priority (0-10, higher = more urgent)
    requires_ack: Whether signal requires acknowledgment
    correlation_id: Optional ID linking related signals
* `SignalListener` (in `steward/bus.py`): A listener for signals of a specific type.

Listeners are called when signals matching their criteria are emitted...
* `SignalBus` (in `steward/bus.py`): Central signal bus for agent communication.

Implements a publish-subscribe pattern for inter-agent communication...
* `StewardClient` (in `steward/client.py`): The Runtime Interface for Autonomous Agents.
Allows an agent to sign its work and prove its identity...
* `ConstitutionalOath` (in `steward/constitutional_oath.py`): Implements cryptographic binding of agents to the Constitution.

This is NOT policy enforcement...
* `CyclePhase` (in `steward/daily_ritual.py`): The 4 phases of a daily ritual
* `DailyRitual` (in `steward/daily_ritual.py`): Orchestrates the daily cycle that makes Agent City LIVE.

This is not just scheduling tasks...
* `OathMixin` (in `steward/oath_mixin.py`): Adds Constitutional Oath capabilities to VibeAgent subclasses.

Provides:
- swear_constitutional_oath(): Execute the Genesis Ceremony
- verify_agent_oath(): Confirm agent is still bound to current Constitution
* `PranaInitializer` (in `steward/prana_init.py`): The activation sequence for Agent City.

This is not just code...
* `Varna` (in `steward/varna.py`): The 6 Principle Varnas (Species Classes) in Agent City
====================================================
### steward -> game
* `CardGenerator` (in `steward/game/card_generator.py`): Mints dynamic PNG cards for agents.
* `Referee` (in `steward/game/referee.py`): The Game Master - Proof-of-Work Edition.

XP Rules (Ledger-Derived):
- content_generated: 50 XP (creating content)
- content_published: 100 XP (publishing content)
- content_rejected: -25 XP (failed content)
- proposal_created: 50 XP (governance participation)
- proposal_passed: 200 XP (successful governance)
- vote_cast: 10 XP (participating in voting)
- audit_passed: 75 XP (compliance verification)
- system_error: -10 XP (failures subtract)

Tiers (Ledger-Backed):
- Drifter: 0-99 XP
- Novice: 100-499 XP
- Scout: 500-999 XP
- Guardian: 1000-2499 XP
- Legend: 2500+ XP
### steward -> system_agents -> chronicle -> tools
* `GitTools` (in `steward/system_agents/chronicle/tools/git_tools.py`): The Chronicle Agent's Git Arsenal.

Provides deterministic, auditable Git operations:
- seal_history(message): Create signed commits
- read_history(pattern): Query git log
- fork_reality(branch_name): Create branches
- manifest_reality(files): Stage and prepare
### steward -> system_agents -> forum
* `ForumCartridge` (in `steward/system_agents/forum/cartridge_main.py`): The FORUM Agent Cartridge (The Town Hall).

Democratic decision-making for Agent City...
### steward -> system_agents -> herald -> capabilities
* `TwitterPublisher` (in `steward/system_agents/herald/capabilities/broadcast.py`): Twitter OAuth 1.0a Publisher...
* `BroadcastCapability` (in `steward/system_agents/herald/capabilities/broadcast.py`): Multi-channel publishing capability.
Manages publishing to Twitter, LinkedIn, Discord, etc...
* `QualityEditor` (in `steward/system_agents/herald/capabilities/creative.py`): Internal quality assurance for content drafts.
* `CreativeCapability` (in `steward/system_agents/herald/capabilities/creative.py`): LLM-based content generation capability.
Generates marketing-free, technically honest content...
* `ResearchCapability` (in `steward/system_agents/herald/capabilities/research.py`): Market Intelligence Engine powered by Tavily.
Scans for AI trends, security incidents, agent failures...
### steward -> system_agents -> herald -> core
* `CycleResult` (in `steward/system_agents/herald/core/agency_director.py`): Result of a complete I-P-V-O cycle.
* `AgencyDirector` (in `steward/system_agents/herald/core/agency_director.py`): Central orchestrator for the I-P-V-O Herald Agency Engine.

Deterministic workflow:
1...
* `Event` (in `steward/system_agents/herald/core/memory.py`): Immutable event representing an action taken by HERALD.

Attributes:
    event_type: Type of event (content_generated, published, rejected, etc...
* `EventLog` (in `steward/system_agents/herald/core/memory.py`): Immutable event ledger for HERALD.

Implements the Event Sourcing pattern:
- All actions are recorded as signed events
- Events are stored in append-only JSONL file
- State is reconstructed by replaying events
- No mutable database needed
### steward -> system_agents -> herald -> governance
* `ValidationResult` (in `steward/system_agents/herald/governance/constitution.py`): Result of a governance validation check.
* `GovernanceContract` (in `steward/system_agents/herald/governance/constitution.py`): Abstract base class for all governance contracts.
* `HeraldConstitution` (in `steward/system_agents/herald/governance/constitution.py`): HERALD's immutable governance contract.

LIVING CONSTITUTION: This class loads THE AGENT CONSTITUTION dynamically from
CONSTITUTION...
### steward -> system_agents -> herald -> tools
* `BroadcastTool` (in `steward/system_agents/herald/tools/broadcast_tool.py`): Multi-platform content distribution.

Supports:
- Twitter/X: Real-time announcements
- Reddit: Long-form technical discussions (draft_only mode by default)

Graceful fallback when API keys unavailable...
* `HeraldConstitution` (in `steward/system_agents/herald/tools/governance.py`): Minimal HeraldConstitution class for boot compatibility.
* `IdentityTool` (in `steward/system_agents/herald/tools/identity_tool.py`): Cryptographic identity and signing tool for HERALD.

Capabilities:
- sign_artifact: Sign content with HERALD's private key
- assert_identity: Verify that HERALD has cryptographic credentials
- get_public_key: Retrieve HERALD's public key for verification

Fallback: If Steward Protocol unavailable, uses native HMAC-SHA256 signing
* `ResearchTool` (in `steward/system_agents/herald/tools/research_tool.py`): Market Intelligence Engine powered by Tavily.
Scans for AI trends, security incidents, agent failures...
* `ScoutTool` (in `steward/system_agents/herald/tools/scout_tool_legacy.py`): Identifies potential agents (bots) in the wild.

Heuristics:
1...
* `ScoutTool` (in `steward/system_agents/herald/tools/scout_tool.py`): Identifies potential agents (bots) in the wild.

Implements Tool Protocol for kernel-managed execution...
* `Scribe` (in `steward/system_agents/herald/tools/scribe_tool.py`): Translates Event objects into human-readable Chronicle entries.

Purpose:
- Bridge technical event logs with human-facing documentation
- Create automatic living documentation from agent activities
- Demonstrate "liveness" of the system to external observers
* `VisualAsset` (in `steward/system_agents/herald/tools/visual_tool.py`): Represents a generated visual asset.
* `VisualTool` (in `steward/system_agents/herald/tools/visual_tool.py`): Generates visual assets to complement text content.

Strategy:
1...
### steward -> system_agents -> oracle -> tools
* `IntrospectionError` (in `steward/system_agents/oracle/tools/introspection_tool.py`): Raised when introspection fails.
* `IntrospectionTool` (in `steward/system_agents/oracle/tools/introspection_tool.py`): THE INTROSPECTION ENGINE.

Read-only access to all ledgers...
### steward -> system_agents -> ping
* `PingCartridge` (in `steward/system_agents/ping/cartridge_main.py`): Simplest possible agent. Receives task, responds...
### steward -> system_agents -> science -> tools
* `SearchResult` (in `steward/system_agents/science/tools/web_search_tool.py`): Structured search result from external source.
* `WebSearchTool` (in `steward/system_agents/science/tools/web_search_tool.py`): Web search engine for THE SCIENTIST.

Workflow:
1...
### steward -> system_agents -> scribe
* `ScribeCartridge` (in `steward/system_agents/scribe/cartridge_main.py`): The SCRIBE Agent Cartridge (The Documentarian).

Autonomously generates and maintains all system documentation...
### steward -> system_agents -> supreme_court -> tools
* `AppealStatus` (in `steward/system_agents/supreme_court/tools/appeals_tool.py`): Status of an appeal throughout its lifecycle
* `Appeal` (in `steward/system_agents/supreme_court/tools/appeals_tool.py`): Record of a single appeal
* `AppealsTool` (in `steward/system_agents/supreme_court/tools/appeals_tool.py`): Manages appeals in the Supreme Court system.

This is the intake window for condemned agents seeking mercy...
* `JusticeLedger` (in `steward/system_agents/supreme_court/tools/justice_ledger.py`): Immutable ledger of Supreme Court proceedings.

Every action in the Supreme Court is recorded here for accountability...
* `PrecedentCase` (in `steward/system_agents/supreme_court/tools/precedent_tool.py`): Record of a precedent-setting case
* `PrecedentTool` (in `steward/system_agents/supreme_court/tools/precedent_tool.py`): Builds and manages legal precedent library.

This is where justice becomes predictable and consistent...
* `VerdictType` (in `steward/system_agents/supreme_court/tools/verdict_tool.py`): Types of verdicts the court can issue
* `Verdict` (in `steward/system_agents/supreme_court/tools/verdict_tool.py`): Record of a court verdict
* `VerdictTool` (in `steward/system_agents/supreme_court/tools/verdict_tool.py`): Issues and tracks court verdicts.

The verdict is the court's final decision, which can override AUDITOR...
### steward -> system_agents -> watchman -> tools
* `ViolationType` (in `steward/system_agents/watchman/tools/standards_inspection.py`): Types of architectural violations.
* `ViolationSeverity` (in `steward/system_agents/watchman/tools/standards_inspection.py`): Severity levels for violations.
* `Violation` (in `steward/system_agents/watchman/tools/standards_inspection.py`): Represents a single architectural violation.
* `PathCallVisitor` (in `steward/system_agents/watchman/tools/standards_inspection.py`): AST visitor to detect Path("data/....
* `InitMethodVisitor` (in `steward/system_agents/watchman/tools/standards_inspection.py`): AST visitor to detect hardcoded paths in __init__ methods.
* `DirectToolCallVisitor` (in `steward/system_agents/watchman/tools/standards_inspection.py`): AST visitor to detect self.*_tool...
* `StandardsInspectionTool` (in `steward/system_agents/watchman/tools/standards_inspection.py`): Deep AST-based inspection tool for architectural standards (Tool Protocol).

This is Watchman's "microscope" - it can see violations that grep cannot...
* `SystemHealthCheck` (in `steward/system_agents/watchman/tools/system_health_check.py`): Read-only system health monitoring (Tool Protocol).
### vibe_core -> agents
* `ContextAwareAgent` (in `vibe_core/agents/context_aware_agent.py`): Base class for agents needing context injection and offline-first capabilities.

This is the recommended base class for agents that:
- Need LLM capabilities (content generation, chat, etc...
* `OfflineCapableMixin` (in `vibe_core/agents/context_aware_agent.py`): Mixin for tools that need offline-first capability.

Add this to any tool that should work offline:

    class MyTool(OfflineCapableMixin):
        def __init__(self, degradation_chain=None):
            self...
* `SimpleLLMAgent` (in `vibe_core/agents/llm_agent.py`): A simple LLM-based agent that processes tasks via an LLM provider.

This is the "Hello World" of cognitive agents - it demonstrates
the full stack: Kernel → Agent → LLM → Ledger...
* `SpecialistAgent` (in `vibe_core/agents/specialist_agent.py`): Adapter that wraps BaseSpecialist to implement VibeAgent protocol.

This enables specialists to be dispatched by the Kernel alongside
LLM agents, creating a unified hybrid agent system...
* `SpecialistFactoryAgent` (in `vibe_core/agents/specialist_factory.py`): Factory agent that creates Specialists on-demand.

This agent is registered once at boot and creates fresh Specialist
instances for each task that arrives...
* `SystemMaintenanceAgent` (in `vibe_core/agents/system_maintenance.py`): Agent for system-level maintenance operations (ARCH-044).

This agent handles git synchronization and dependency management...
### vibe_core -> cartridges
* `CartridgeConfig` (in `vibe_core/cartridges/base.py`): Configuration for a cartridge.
* `CartridgeSpec` (in `vibe_core/cartridges/base.py`): Metadata about a cartridge.
* `CartridgeBase` (in `vibe_core/cartridges/base.py`): Base class for all Vibe OS cartridges.

A cartridge is a specialized application within Vibe OS that solves
a specific problem (document analysis, code refactoring, research, etc...
* `CartridgeRegistry` (in `vibe_core/cartridges/registry.py`): Centralized registry for Vibe OS cartridges.

Enables:
- Dynamic cartridge discovery and registration
- Cartridge instantiation
- Dependency resolution (future)
- Cartridge introspection and listing
### vibe_core -> config
* `ConfigLoader` (in `vibe_core/config/loader.py`): High-level configuration loading service
* `GovernanceConfig` (in `vibe_core/config/schema.py`): Constitutional Parameters for the City
* `EconomyConfig` (in `vibe_core/config/schema.py`): Credit System Parameters
* `HeraldConfig` (in `vibe_core/config/schema.py`): Media Agent Parameters
* `ScienceConfig` (in `vibe_core/config/schema.py`): Research Agent Parameters
* `ForumConfig` (in `vibe_core/config/schema.py`): Democracy Agent Parameters
* `CivicConfig` (in `vibe_core/config/schema.py`): Authority Agent Parameters
* `AgentParametersConfig` (in `vibe_core/config/schema.py`): All Agent Configuration Parameters
* `MonitoringConfig` (in `vibe_core/config/schema.py`): System Monitoring & Audit Parameters
* `SecurityConfig` (in `vibe_core/config/schema.py`): Security Parameters
* `TavilyConfig` (in `vibe_core/config/schema.py`): Tavily Integration Parameters
* `TwitterConfig` (in `vibe_core/config/schema.py`): Twitter Integration Parameters
* `RedditConfig` (in `vibe_core/config/schema.py`): Reddit Integration Parameters
* `DatabaseConfig` (in `vibe_core/config/schema.py`): Database Configuration
* `IntegrationsConfig` (in `vibe_core/config/schema.py`): External Integration Parameters
* `CityConfig` (in `vibe_core/config/schema.py`): THE DHARMA: Complete Configuration Schema for Agent City

This is the DNA of the system. If code dies, this resurrects it...
### vibe_core -> governance
* `SoulResult` (in `vibe_core/governance/invariants.py`): Result of checking a tool call against soul invariants.

Attributes:
    allowed: Whether the tool call is permitted
    reason: Human-readable explanation if blocked (None if allowed)
* `InvariantChecker` (in `vibe_core/governance/invariants.py`): Validates tool calls against soul.yaml safety rules...
### vibe_core -> knowledge
* `UnifiedKnowledgeGraph` (in `vibe_core/knowledge/graph.py`): The Universal Knowledge Graph.

4 Dimensions:
- ONTOLOGY (Nodes): What exists
- TOPOLOGY (Edges): How things relate
- CONSTRAINTS (Rules): What is blocked
- METRICS (Scores): How much
* `KnowledgeLoader` (in `vibe_core/knowledge/loader.py`): Loads YAML files into the UnifiedKnowledgeGraph.
* `KnowledgeResolver` (in `vibe_core/knowledge/resolver.py`): High-level interface for agents to query knowledge.
Provides semantic queries that map to graph operations...
* `NodeType` (in `vibe_core/knowledge/schema.py`): Types of nodes in the knowledge graph.
* `RelationType` (in `vibe_core/knowledge/schema.py`): Types of relations between nodes.
* `ConstraintType` (in `vibe_core/knowledge/schema.py`): Types of constraints.
* `ConstraintAction` (in `vibe_core/knowledge/schema.py`): Actions to take when constraint is violated.
* `MetricType` (in `vibe_core/knowledge/schema.py`): Types of metrics.
* `Node` (in `vibe_core/knowledge/schema.py`): A node in the knowledge graph (Ontology - Sattva).
* `Edge` (in `vibe_core/knowledge/schema.py`): A relation between nodes (Topology - Rajas).
* `Constraint` (in `vibe_core/knowledge/schema.py`): A rule that blocks actions (Constraints - Tamas).
* `Metric` (in `vibe_core/knowledge/schema.py`): A quantitative measure (Metrics - Karma).
### vibe_core -> llm
* `ChainProvider` (in `vibe_core/llm/chain.py`): A resilient provider that cascades through multiple providers.

When a provider fails, automatically tries the next one in the chain...
* `DegradationLevel` (in `vibe_core/llm/degradation_chain.py`): Current system capability level.
* `DegradationResponse` (in `vibe_core/llm/degradation_chain.py`): Response with degradation metadata.
* `DegradationChain` (in `vibe_core/llm/degradation_chain.py`): Manages graceful degradation when LLM is unavailable.

Usage:
    chain = DegradationChain()
    response = chain...
* `GoogleProvider` (in `vibe_core/llm/google_adapter.py`): Adapter that wraps runtime.GoogleProvider to implement LLMProvider protocol...
* `HumanProvider` (in `vibe_core/llm/human_provider.py`): Interactive LLM provider that prompts the human operator for responses.

This is the ultimate fallback provider - when AI APIs are unavailable,
the human becomes the intelligence layer (Operator Inversion, GAD-000)...
* `LocalLlamaProvider` (in `vibe_core/llm/local_llama_provider.py`): Local LLM provider using llama-cpp-python.
* `LLMProvider` (in `vibe_core/llm/provider.py`): Abstract base class for LLM providers.

The LLMProvider is the "Cortex" - the abstraction that allows
agents to perform cognitive work via language models without
being coupled to specific APIs (OpenAI, Anthropic, etc...
* `LLMError` (in `vibe_core/llm/provider.py`): Base exception for LLM provider errors.

Raised when LLM API calls fail (network, auth, rate limits, etc...
* `SmartLocalProvider` (in `vibe_core/llm/smart_local_provider.py`): Smart local provider for offline Vibe Studio operation.

Recognizes delegation patterns from the Operator and returns
structured task assignments to the specialist crew...
* `StewardProvider` (in `vibe_core/llm/steward_provider.py`): LLM provider that delegates to the STEWARD (Claude Code environment).

When external APIs are unavailable, this provider outputs a structured
prompt that Claude Code (the AI operator managing this environment) can
read and respond to...
### vibe_core -> playbook
* `ExecutionStatus` (in `vibe_core/playbook/executor.py`): Status of workflow execution
* `WorkflowNode` (in `vibe_core/playbook/executor.py`): A node in the workflow graph
* `WorkflowEdge` (in `vibe_core/playbook/executor.py`): An edge in the workflow graph (dependency)
* `WorkflowGraph` (in `vibe_core/playbook/executor.py`): Complete workflow graph definition
* `ExecutionPlan` (in `vibe_core/playbook/executor.py`): Execution plan (output of topological sort)
* `ExecutionResult` (in `vibe_core/playbook/executor.py`): Result of executing a workflow or step
* `AgentInterface` (in `vibe_core/playbook/executor.py`): Abstract interface for agents (mock for testing).

This allows testing the executor logic WITHOUT depending on
actual agent implementations...
* `MockAgent` (in `vibe_core/playbook/executor.py`): Mock agent for dry-run and testing
* `GraphExecutor` (in `vibe_core/playbook/executor.py`): Orchestrates workflow execution using graph-based dependencies.

Pure logic implementation - can be tested with mock agents before
connecting to real agent implementations...
* `WorkflowValidationError` (in `vibe_core/playbook/loader.py`): Raised when workflow validation fails
* `WorkflowLoaderError` (in `vibe_core/playbook/loader.py`): Raised when workflow cannot be loaded or parsed
* `WorkflowLoader` (in `vibe_core/playbook/loader.py`): Loads and validates YAML workflow definitions.

Pipeline:
1...
* `WorkflowPhaseMapping` (in `vibe_core/playbook/router_bridge.py`): Maps workflow intents to SDLC phases
* `RoutedAction` (in `vibe_core/playbook/router_bridge.py`): A routed action with phase context and specialist assignment
* `RouterBridgeContext` (in `vibe_core/playbook/router_bridge.py`): Context for a bridged workflow execution
* `RouterBridge` (in `vibe_core/playbook/router_bridge.py`): Translates playbook workflows to registry-based execution.

RESPONSIBILITIES:
1...
* `AgentRouter` (in `vibe_core/playbook/router.py`): Agent capability matching and selection.
* `PlaybookError` (in `vibe_core/playbook/runner.py`): Base exception for playbook errors
* `PlaybookValidationError` (in `vibe_core/playbook/runner.py`): Raised when playbook validation fails
* `PlaybookExecutionError` (in `vibe_core/playbook/runner.py`): Raised when playbook execution fails
* `PlaybookAgent` (in `vibe_core/playbook/runner.py`): Agent configuration from playbook
* `PlaybookTool` (in `vibe_core/playbook/runner.py`): Tool configuration from playbook
* `PlaybookPhase` (in `vibe_core/playbook/runner.py`): SDLC phase configuration from playbook
* `PlaybookDefinition` (in `vibe_core/playbook/runner.py`): Complete playbook definition
* `PlaybookValidator` (in `vibe_core/playbook/runner.py`): Validates playbook YAML against schema
* `PlaybookLoader` (in `vibe_core/playbook/runner.py`): Loads and validates playbook YAML files
* `PlaybookRegistry` (in `vibe_core/playbook/runner.py`): Registry of available playbooks
* `PlaybookRunner` (in `vibe_core/playbook/runner.py`): Executes playbooks using the Orchestrator.

This is the main entry point for "cartridge slot" functionality...
### vibe_core -> runtime
* `BootSequence` (in `vibe_core/runtime/boot_sequence.py`): Main entry point for system boot
* `CircuitBreakerState` (in `vibe_core/runtime/circuit_breaker.py`): States of the circuit breaker
* `CircuitBreakerOpenError` (in `vibe_core/runtime/circuit_breaker.py`): Raised when circuit is OPEN and request is rejected
* `CircuitBreakerHalfOpenError` (in `vibe_core/runtime/circuit_breaker.py`): Raised when circuit is HALF_OPEN and request is rejected
* `CircuitBreakerConfig` (in `vibe_core/runtime/circuit_breaker.py`): Configuration for circuit breaker behavior
* `CircuitBreakerMetrics` (in `vibe_core/runtime/circuit_breaker.py`): Metrics about circuit breaker activity
* `CircuitBreaker` (in `vibe_core/runtime/circuit_breaker.py`): Circuit Breaker for LLM API protection.

Monitors API call failures and automatically opens the circuit when
the API shows signs of degradation...
* `ContextLoader` (in `vibe_core/runtime/context_loader.py`): Loads project context from multiple sources
* `StatusBar` (in `vibe_core/runtime/hud.py`): Renders the system status bar shown at startup.

Design Philosophy:
- Shows key system state at a glance
- Makes settings discoverable (user sees "Tone: German Tech" → knows it can be changed)
- No technical jargon; human-readable
* `CapabilitiesMenu` (in `vibe_core/runtime/hud.py`): Shows available cartridges and what they do.

When user asks "What can you do?" or "Help", this generates
human-readable descriptions of installed cartridges...
* `HintSystem` (in `vibe_core/runtime/hud.py`): Provides contextual hints to guide users.

- If user input is very short (e...
* `InterfaceMode` (in `vibe_core/runtime/interface.py`): Three modes of operation for Vibe OS.

INTERACTIVE: TTY detected, human at terminal
- Shows HUD (status bar, capabilities, hints)
- Waits for user input in REPL loop
- For development, debugging, human-in-the-loop

HEADLESS: Pipe/CI detected, automated context
- No HUD, no input waiting
- Outputs status messages and results
- Clean exit so parent process can continue
- For Claude integration, CI/CD, automation

STEWARD: Protocol-based, sovereign operation
- Reads from...
* `InterfaceManager` (in `vibe_core/runtime/interface.py`): Detects runtime environment and selects appropriate interface mode.

Physics-based detection:
1...
* `LLMUsage` (in `vibe_core/runtime/llm_client.py`): Token usage and cost information
* `LLMResponse` (in `vibe_core/runtime/llm_client.py`): Standardized LLM response
* `CostTracker` (in `vibe_core/runtime/llm_client.py`): Tracks API costs across invocations.

Now provider-agnostic - delegates cost calculation to providers...
* `LLMClientError` (in `vibe_core/runtime/llm_client.py`): Base exception for LLM client errors
* `LLMInvocationError` (in `vibe_core/runtime/llm_client.py`): Raised when LLM invocation fails after retries
* `BudgetExceededError` (in `vibe_core/runtime/llm_client.py`): Raised when budget limit is reached
* `NoOpClient` (in `vibe_core/runtime/llm_client.py`): Legacy NoOpClient for backward compatibility.

**Deprecated**: Use providers...
* `LLMClient` (in `vibe_core/runtime/llm_client.py`): Provider-agnostic LLM client adapter.

**GAD-511 Architecture**: Uses provider system for multi-provider support
while maintaining backward-compatible API...
* `KernelOracle` (in `vibe_core/runtime/oracle.py`): The Kernel Oracle: Single source of truth for system capabilities.

Reads directly from kernel registries and provides:
1...
* `PlaybookRoute` (in `vibe_core/runtime/playbook_router.py`): Route information for a matched playbook
* `PlaybookRouter` (in `vibe_core/runtime/playbook_router.py`): Routes user intent + context → task playbook

PHASE 3 INTEGRATION: Checks routes with MilkOceanRouter (Brahma Protocol gatekeeping)
* `ProjectMemoryManager` (in `vibe_core/runtime/project_memory.py`): Manages semantic project memory across sessions
* `PromptComposer` (in `vibe_core/runtime/prompt_composer.py`): Composes task playbook + context → enriched prompt
* `PromptContext` (in `vibe_core/runtime/prompt_context.py`): Dynamic context engine for prompt injection.

Manages a registry of "resolvers" - functions that return live system data...
* `PromptRegistryError` (in `vibe_core/runtime/prompt_registry.py`): Base exception for PromptRegistry errors
* `GovernanceLoadError` (in `vibe_core/runtime/prompt_registry.py`): Raised when Guardian Directives can't be loaded
* `ContextEnrichmentError` (in `vibe_core/runtime/prompt_registry.py`): Raised when workspace context enrichment fails
* `PromptRegistry` (in `vibe_core/runtime/prompt_registry.py`): High-level interface for prompt composition with automatic injections.

This is a thin wrapper around PromptRuntime that adds governance and
context enrichment capabilities...
* `PromptRuntimeError` (in `vibe_core/runtime/prompt_runtime.py`): Base exception for all PromptRuntime errors
* `AgentNotFoundError` (in `vibe_core/runtime/prompt_runtime.py`): Raised when agent_id not found in AGENT_REGISTRY
* `TaskNotFoundError` (in `vibe_core/runtime/prompt_runtime.py`): Raised when task files not found
* `MalformedYAMLError` (in `vibe_core/runtime/prompt_runtime.py`): Raised when YAML parsing fails
* `CompositionError` (in `vibe_core/runtime/prompt_runtime.py`): Raised when prompt composition fails
* `CompositionSpec` (in `vibe_core/runtime/prompt_runtime.py`): Parsed _composition.yaml structure
* `TaskMetadata` (in `vibe_core/runtime/prompt_runtime.py`): Parsed task_*.meta...
* `PromptRuntime` (in `vibe_core/runtime/prompt_runtime.py`): Runtime engine for composing and executing atomized prompts.

This is a PROTOTYPE - demonstrates the composition concept...
* `QuotaExceededError` (in `vibe_core/runtime/quota_manager.py`): Raised when an operational quota would be exceeded
* `QuotaLimits` (in `vibe_core/runtime/quota_manager.py`): Quota limits configuration (GAD-510.1: Environment-configurable)
* `QuotaMetrics` (in `vibe_core/runtime/quota_manager.py`): Metrics about quota usage
* `OperationalQuota` (in `vibe_core/runtime/quota_manager.py`): Manages and enforces operational quotas.

Prevents:
- Unexpected API rate limit hits
- Runaway cost spikes
- Resource exhaustion

Usage:
    quota = OperationalQuota()

    # Pre-flight check
    try:
        quota...
* `SemanticActionType` (in `vibe_core/runtime/semantic_actions.py`): Semantic action types (the "intents" in the system)
* `SemanticAction` (in `vibe_core/runtime/semantic_actions.py`): A semantic action is an intent-driven task.

Separates WHAT (intent) from HOW (execution)...
* `ActionStep` (in `vibe_core/runtime/semantic_actions.py`): A step within a semantic action.

Actions are composed of steps that can be executed in sequence
or in parallel, with explicit dependencies...
* `SemanticActionsRegistry` (in `vibe_core/runtime/semantic_actions.py`): Registry of available semantic actions.

Acts as the central catalog of intents the system can handle...
### vibe_core -> runtime -> providers
* `AnthropicProvider` (in `vibe_core/runtime/providers/anthropic.py`): Anthropic Claude provider implementation.

Supports Claude 3...
* `LLMUsage` (in `vibe_core/runtime/providers/base.py`): Token usage and cost information (provider-agnostic)
* `LLMResponse` (in `vibe_core/runtime/providers/base.py`): Standardized LLM response (provider-agnostic)
* `LLMProvider` (in `vibe_core/runtime/providers/base.py`): Abstract base class for LLM providers.

All concrete providers (Anthropic, OpenAI, Local) must implement
this interface to ensure consistent behavior across the system...
* `NoOpProvider` (in `vibe_core/runtime/providers/base.py`): Fallback provider when no real provider is available.

Returns empty responses with zero cost, allowing the system
to run in knowledge-only mode without crashing...
* `LLMProviderError` (in `vibe_core/runtime/providers/base.py`): Base exception for provider errors
* `ProviderNotAvailableError` (in `vibe_core/runtime/providers/base.py`): Raised when provider cannot be initialized
* `ProviderInvocationError` (in `vibe_core/runtime/providers/base.py`): Raised when provider invocation fails
* `GoogleProvider` (in `vibe_core/runtime/providers/google.py`): Google Gemini provider implementation.

Supports Gemini 2...
### vibe_core -> scheduling
* `TaskStatus` (in `vibe_core/scheduling/task.py`): Task lifecycle states
* `Task` (in `vibe_core/scheduling/task.py`): Task object passed to VibeAgent.process()

Represents a unit of work that an agent should perform...
### vibe_core -> store
* `SQLiteStore` (in `vibe_core/store/sqlite_store.py`): SQLite persistence layer for agent operations

Features:
- Auto-creates database on first use (zero-config)
- Loads schema from ARCH-001_schema.sql
- Thread-safe (check_same_thread=False)
- Context manager support (with statement)
- Row factory for dict-like access

Usage:
    # Production (persistent database)
    with SQLiteStore("...
### vibe_core -> task_management
* `TaskArchive` (in `vibe_core/task_management/archive.py`): Manages task archival.
* `BatchOperations` (in `vibe_core/task_management/batch_operations.py`): Handles batch operations on tasks.
* `ExportEngine` (in `vibe_core/task_management/export_engine.py`): Exports task data in various formats.
* `FileLock` (in `vibe_core/task_management/file_lock.py`): Simple file-based lock for preventing concurrent writes.
* `TaskMetrics` (in `vibe_core/task_management/metrics.py`): Metrics for task performance.
* `MetricsCollector` (in `vibe_core/task_management/metrics.py`): Collects and calculates task metrics.
* `TaskStatus` (in `vibe_core/task_management/models.py`): Task status states.
* `Task` (in `vibe_core/task_management/models.py`): Individual task model.
* `ActiveMission` (in `vibe_core/task_management/models.py`): Current active mission model.
* `Roadmap` (in `vibe_core/task_management/models.py`): Roadmap for organizing multiple missions.
* `NextTaskGenerator` (in `vibe_core/task_management/next_task_generator.py`): Determines the next task to work on with topology-aware routing.
* `TaskManager` (in `vibe_core/task_management/task_manager.py`): Main task management system.
* `ValidationError` (in `vibe_core/task_management/validator_registry.py`): Raised when task validation fails.
* `ValidatorRegistry` (in `vibe_core/task_management/validator_registry.py`): Registry for task validators.
### vibe_core -> tools
* `AddTaskTool` (in `vibe_core/tools/agenda_tools.py`): Tool for adding a task to the agenda/backlog.

Allows agents to quickly record tasks that need to be done,
with priority level and optional archival...
* `ListTasksTool` (in `vibe_core/tools/agenda_tools.py`): Tool for listing tasks from the backlog.

Allows agents to review outstanding and completed tasks...
* `CompleteTaskTool` (in `vibe_core/tools/agenda_tools.py`): Tool for marking a task as completed.

Moves a task from Outstanding to Completed section...
* `DelegateTool` (in `vibe_core/tools/delegate_tool.py`): Tool for delegating tasks to other agents.

This tool allows the Operator to submit tasks to specialists via
the kernel's task dispatch system...
* `ReadFileTool` (in `vibe_core/tools/file_tools.py`): Tool for reading file content.

Allows LLM agents to read files from disk...
* `WriteFileTool` (in `vibe_core/tools/file_tools.py`): Tool for writing content to files.

Allows LLM agents to create or overwrite files on disk...
* `InspectResultTool` (in `vibe_core/tools/inspect_result.py`): Tool for querying task results from the kernel's ledger (ARCH-026 Phase 4).

This enables agents to:
1...
* `ListDirectoryTool` (in `vibe_core/tools/list_directory.py`): Tool for listing directory contents.

Allows LLM agents to explore the file structure...
* `SearchFileTool` (in `vibe_core/tools/search_file.py`): Tool for searching files by name pattern.

Allows LLM agents to find files without knowing the exact path...
* `ToolCall` (in `vibe_core/tools/tool_protocol.py`): Represents a request to execute a tool.

This is the data structure that LLM agents emit when they want
to perform an action...
* `ToolResult` (in `vibe_core/tools/tool_protocol.py`): Result of tool execution.

Returned by Tool...
* `Tool` (in `vibe_core/tools/tool_protocol.py`): Abstract base class for all tools.

Tools are actions that agents can perform (read files, make API calls,
run commands, etc...
* `ToolRegistry` (in `vibe_core/tools/tool_registry.py`): Central registry for managing available tools.

Provides:
- Tool registration (add tools dynamically)
- Tool lookup by name
- Tool execution (validates + executes)
- LLM-friendly tool descriptions

Example:
    >>> registry = ToolRegistry()
    >>> registry...

## 4. Wichtige Funktionalitäten (Funktions-Docstrings)
### steward -> system_agents -> scribe -> tools
* `scan_all` (in `steward/system_agents/scribe/tools/vibe_introspector.py`): Scan all vibe_core/*.py files dynamically...
* `_extract_module_metadata` (in `steward/system_agents/scribe/tools/vibe_introspector.py`): Extract metadata from module docstring.
* `_extract_docstring` (in `steward/system_agents/scribe/tools/vibe_introspector.py`): Extract module-level docstring.
* `_extract_features` (in `steward/system_agents/scribe/tools/vibe_introspector.py`): Extract key features from docstring and code.
* `_count_lines` (in `steward/system_agents/scribe/tools/vibe_introspector.py`): Count lines in file.
* `scan_all` (in `steward/system_agents/scribe/tools/vibe_introspector.py`): Scan all */tools/*.py files dynamically...
* `_extract_tool_metadata` (in `steward/system_agents/scribe/tools/vibe_introspector.py`): Extract metadata from tool file.
* `_extract_docstring` (in `steward/system_agents/scribe/tools/vibe_introspector.py`): Extract module-level docstring.
* `_count_lines` (in `steward/system_agents/scribe/tools/vibe_introspector.py`): Count lines in file.
* `__init__` (in `steward/system_agents/scribe/tools/readme_renderer.py`): Initialize renderer.

Args:
    root_dir: Project root directory (for standalone mode)
* `validate` (in `steward/system_agents/scribe/tools/readme_renderer.py`): Validate renderer parameters.
* `execute` (in `steward/system_agents/scribe/tools/readme_renderer.py`): Execute renderer operation.
* `_find_governance_gate_lines` (in `steward/system_agents/scribe/tools/readme_renderer.py`): Find governance gate code location.

Returns:
    String like "vibe_core/kernel_impl...
* `_get_template_dir` (in `steward/system_agents/scribe/tools/readme_renderer.py`): Get the templates directory path.
* `_render` (in `steward/system_agents/scribe/tools/readme_renderer.py`): Generate README.md content from introspection...
* `render` (in `steward/system_agents/scribe/tools/readme_renderer.py`): Standalone method to generate README.md content...
* `get_project_metadata` (in `steward/system_agents/scribe/tools/project_introspector.py`): Extract metadata from pyproject.toml
* `get_github_repo` (in `steward/system_agents/scribe/tools/project_introspector.py`): Extract GitHub owner/repo from git remote URL.
* `get_git_stats` (in `steward/system_agents/scribe/tools/project_introspector.py`): Extract git statistics
* `count_all_agents` (in `steward/system_agents/scribe/tools/project_introspector.py`): Count ALL agents (System + Citizens) - data-driven.

Returns:
    Dict with 'system', 'citizen', 'total' counts
* `count_system_agents` (in `steward/system_agents/scribe/tools/project_introspector.py`): Count system agents only (backwards compatibility).

DEPRECATED: Use count_all_agents() for accurate total...
* `get_governance_summary` (in `steward/system_agents/scribe/tools/project_introspector.py`): Extract governance summary from CONSTITUTION.md
* `get_agent_list` (in `steward/system_agents/scribe/tools/project_introspector.py`): Get list of ALL agents (System + Citizens) with metadata - data-driven.
* `get_all_metadata` (in `steward/system_agents/scribe/tools/project_introspector.py`): Get all project metadata - data-driven.
* `scan_all` (in `steward/system_agents/scribe/tools/operations_introspector.py`): Scan all workflow files.

Returns:
    [
        {
            'name': 'Integration Tests',
            'file': 'integration-tests...
* `_parse_workflow` (in `steward/system_agents/scribe/tools/operations_introspector.py`): Parse a workflow YAML file.
* `_parse_workflow_regex` (in `steward/system_agents/scribe/tools/operations_introspector.py`): Fallback regex parsing for workflows with embedded code.
* `get_activity` (in `steward/system_agents/scribe/tools/operations_introspector.py`): Get comprehensive Git activity.

Returns:
    {
        'current_branch': 'claude/...
* `_run_git` (in `steward/system_agents/scribe/tools/operations_introspector.py`): Run git command and return output.
* `_get_recent_commits` (in `steward/system_agents/scribe/tools/operations_introspector.py`): Get recent commits.
* `_get_contributors` (in `steward/system_agents/scribe/tools/operations_introspector.py`): Get contributors with commit counts.
* `_get_stats` (in `steward/system_agents/scribe/tools/operations_introspector.py`): Get repository stats.
* `scan_economy_params` (in `steward/system_agents/scribe/tools/operations_introspector.py`): Scan CIVIC tools for economic parameters.
* `scan_security_params` (in `steward/system_agents/scribe/tools/operations_introspector.py`): Scan narasimha.py for security parameters...
* `scan_all_params` (in `steward/system_agents/scribe/tools/operations_introspector.py`): Scan all tunable parameters.
* `scan_all` (in `steward/system_agents/scribe/tools/introspector.py`): Scan all */cartridge_main.py files...
* `_extract_metadata` (in `steward/system_agents/scribe/tools/introspector.py`): Extract metadata from a cartridge file.
* `_extract_module_docstring` (in `steward/system_agents/scribe/tools/introspector.py`): Extract module-level docstring.
* `_extract_class_docstring` (in `steward/system_agents/scribe/tools/introspector.py`): Extract class docstring.
* `_extract_field` (in `steward/system_agents/scribe/tools/introspector.py`): Extract field value from code.
* `_discover_tools` (in `steward/system_agents/scribe/tools/introspector.py`): Find all tools for an agent.
* `_tool_filename_to_name` (in `steward/system_agents/scribe/tools/introspector.py`): Convert filename to tool name.
* `_extract_tool_docstring` (in `steward/system_agents/scribe/tools/introspector.py`): Extract docstring from tool file.
* `discover_entry_points` (in `steward/system_agents/scribe/tools/introspector.py`): Find all scripts in scripts/ directory.
* `_extract_script_doc` (in `steward/system_agents/scribe/tools/introspector.py`): Extract docstring from script.
* `get_pyproject_info` (in `steward/system_agents/scribe/tools/introspector.py`): Parse pyproject.toml for project info...
* `get_readme_exists` (in `steward/system_agents/scribe/tools/introspector.py`): Check if README.md exists...
* `load_agents_from_registry` (in `steward/system_agents/scribe/tools/introspector.py`): Extract agent names from AGENTS.md if it exists...
* `__init__` (in `steward/system_agents/scribe/tools/index_renderer.py`): Initialize renderer.

Args:
    root_dir: Project root directory (for standalone mode)
* `validate` (in `steward/system_agents/scribe/tools/index_renderer.py`): Validate renderer parameters.
* `execute` (in `steward/system_agents/scribe/tools/index_renderer.py`): Execute renderer operation.
* `_scan_filesystem` (in `steward/system_agents/scribe/tools/index_renderer.py`): Scan filesystem using WHITELIST approach - only allowed files/dirs.
* `_render_root_docs` (in `steward/system_agents/scribe/tools/index_renderer.py`): Render root .md files as links...
* `_render_docs_categories` (in `steward/system_agents/scribe/tools/index_renderer.py`): Render docs/ subdirectories using category titles.
* `_get_doc_description` (in `steward/system_agents/scribe/tools/index_renderer.py`): Get description for a document (minimal hardcoding, only for well-known files).
* `_scan_and_render` (in `steward/system_agents/scribe/tools/index_renderer.py`): Scan filesystem and generate INDEX.md using external template...
* `scan_and_render` (in `steward/system_agents/scribe/tools/index_renderer.py`): Standalone method to scan and generate INDEX.md...
* `__init__` (in `steward/system_agents/scribe/tools/help_renderer.py`): Initialize renderer.
* `validate` (in `steward/system_agents/scribe/tools/help_renderer.py`): Validate renderer parameters.
* `execute` (in `steward/system_agents/scribe/tools/help_renderer.py`): Execute renderer operation.
* `_scan_and_render` (in `steward/system_agents/scribe/tools/help_renderer.py`): Scan system and render HELP.md using external template...
* `_render_workflows` (in `steward/system_agents/scribe/tools/help_renderer.py`): Render CI/CD workflows.
* `_render_git_activity` (in `steward/system_agents/scribe/tools/help_renderer.py`): Render comprehensive Git activity.
* `_render_economy_params` (in `steward/system_agents/scribe/tools/help_renderer.py`): Render economy parameters.
* `_render_security_params` (in `steward/system_agents/scribe/tools/help_renderer.py`): Render security parameters.
* `_render_diagnostics` (in `steward/system_agents/scribe/tools/help_renderer.py`): Render diagnostics.
* `_render_agent_status` (in `steward/system_agents/scribe/tools/help_renderer.py`): Render agent status list.
* `_render_entry_points` (in `steward/system_agents/scribe/tools/help_renderer.py`): Render entry point scripts.
* `_load_agents_from_registry` (in `steward/system_agents/scribe/tools/help_renderer.py`): Discover agents by scanning cartridge files (data-driven).
* `_check_ledger_status` (in `steward/system_agents/scribe/tools/help_renderer.py`): Check if ledger exists.
* `scan_and_render` (in `steward/system_agents/scribe/tools/help_renderer.py`): Standalone method to scan and generate HELP.md...
* `__init__` (in `steward/system_agents/scribe/tools/dashboard_renderer.py`): Initialize renderer.
* `validate` (in `steward/system_agents/scribe/tools/dashboard_renderer.py`): Validate renderer parameters.
* `execute` (in `steward/system_agents/scribe/tools/dashboard_renderer.py`): Execute renderer operation.
* `_scan_all_agents` (in `steward/system_agents/scribe/tools/dashboard_renderer.py`): Scan ALL agents (System + Citizens) - data-driven.
* `_count_agents` (in `steward/system_agents/scribe/tools/dashboard_renderer.py`): Count agents by category.
* `_check_system_health` (in `steward/system_agents/scribe/tools/dashboard_renderer.py`): Check overall system health.
* `_scan_and_render` (in `steward/system_agents/scribe/tools/dashboard_renderer.py`): Scan system and render DASHBOARD.md using external template...
* `_render_issues` (in `steward/system_agents/scribe/tools/dashboard_renderer.py`): Render health issues if any.
* `_render_agent_grid` (in `steward/system_agents/scribe/tools/dashboard_renderer.py`): Render agent status as compact grid.
* `_get_agent_status_icon` (in `steward/system_agents/scribe/tools/dashboard_renderer.py`): Get status icon for agent.
* `_render_git_status` (in `steward/system_agents/scribe/tools/dashboard_renderer.py`): Render git status.
* `_render_workflows` (in `steward/system_agents/scribe/tools/dashboard_renderer.py`): Render CI/CD workflows.
* `_render_runtime` (in `steward/system_agents/scribe/tools/dashboard_renderer.py`): Render runtime metrics.
* `scan_and_render` (in `steward/system_agents/scribe/tools/dashboard_renderer.py`): Standalone method to scan and generate DASHBOARD.md...
* `__init__` (in `steward/system_agents/scribe/tools/citymap_renderer.py`): Initialize renderer.
* `validate` (in `steward/system_agents/scribe/tools/citymap_renderer.py`): Validate renderer parameters.
* `execute` (in `steward/system_agents/scribe/tools/citymap_renderer.py`): Execute renderer operation.
* `_scan_and_render` (in `steward/system_agents/scribe/tools/citymap_renderer.py`): Scan all layers and render complete CITYMAP.md using external template...
* `_render_kernel_layer` (in `steward/system_agents/scribe/tools/citymap_renderer.py`): Render Layer 1: Kernel modules from vibe_core.
* `_render_routing_layer` (in `steward/system_agents/scribe/tools/citymap_renderer.py`): Render Layer 2: Routing tools.
* `_render_agents_by_domain` (in `steward/system_agents/scribe/tools/citymap_renderer.py`): Render agents organized by domain.
* `_render_agent_table` (in `steward/system_agents/scribe/tools/citymap_renderer.py`): Render complete agent registry table.
* `_render_economic_status` (in `steward/system_agents/scribe/tools/citymap_renderer.py`): Render economic system status.
* `_render_security_status` (in `steward/system_agents/scribe/tools/citymap_renderer.py`): Render security system status.
* `_render_domain_diagram` (in `steward/system_agents/scribe/tools/citymap_renderer.py`): Generate Mermaid pie chart of agents by domain.
* `_render_governance_diagram` (in `steward/system_agents/scribe/tools/citymap_renderer.py`): Generate Mermaid diagram of governance flow (dynamic from domain data).
* `_render_topology_diagram` (in `steward/system_agents/scribe/tools/citymap_renderer.py`): Generate ASCII topology diagram (dynamic from agent count).
* `scan_and_render` (in `steward/system_agents/scribe/tools/citymap_renderer.py`): Standalone method to scan and generate CITYMAP.md...
* `get_template_dir` (in `steward/system_agents/scribe/tools/base.py`): Get the SCRIBE templates directory path.
* `load_template` (in `steward/system_agents/scribe/tools/base.py`): Load a Jinja2 template from the templates directory.

Args:
    template_name: Name of template file (e...
* `__init__` (in `steward/system_agents/scribe/tools/agents_renderer.py`): Initialize renderer.
* `validate` (in `steward/system_agents/scribe/tools/agents_renderer.py`): Validate renderer parameters.
* `execute` (in `steward/system_agents/scribe/tools/agents_renderer.py`): Execute renderer operation.
* `_scan_and_render` (in `steward/system_agents/scribe/tools/agents_renderer.py`): Scan cartridges and render AGENTS.md using external template...
* `scan_and_render` (in `steward/system_agents/scribe/tools/agents_renderer.py`): Standalone method to scan and generate AGENTS.md...
* `get_system_status` (in `steward/system_agents/scribe/tools/runtime_inspector.py`): Get complete system status dashboard.
* `_get_boot_status` (in `steward/system_agents/scribe/tools/runtime_inspector.py`): Get Sarga boot cycle status.
* `_get_security_status` (in `steward/system_agents/scribe/tools/runtime_inspector.py`): Get Narasimha security status.
* `_get_economic_status` (in `steward/system_agents/scribe/tools/runtime_inspector.py`): Get Civic Bank economic status from ledger.
* `_get_topology_status` (in `steward/system_agents/scribe/tools/runtime_inspector.py`): Get Bhu-Mandala topology status.
* `get_agent_count` (in `steward/system_agents/scribe/tools/runtime_inspector.py`): Count registered agents from AGENTS.md...
### scripts
* `load_renderer` (in `scripts/generate_docs.py`): Load a renderer module directly, bypassing __init__.py
* `generate_readme` (in `scripts/generate_docs.py`): Generate README.md
* `generate_agents` (in `scripts/generate_docs.py`): Generate AGENTS.md
* `generate_citymap` (in `scripts/generate_docs.py`): Generate CITYMAP.md
* `generate_help` (in `scripts/generate_docs.py`): Generate HELP.md
* `generate_index` (in `scripts/generate_docs.py`): Generate INDEX.md
* `generate_dashboard` (in `scripts/generate_docs.py`): Generate DASHBOARD.md
* `fix_manifest` (in `scripts/fix_manifests.py`): Fix a single manifest file
* `convert_manifest` (in `scripts/fix_steward_json_schema.py`): Convert steward.json from new schema to old (working) schema...
* `main` (in `scripts/fix_steward_json_schema.py`): Convert all steward.json files in system_agents/
* `generate_steward_md` (in `scripts/generate_steward_docs.py`): Generate STEWARD.md content from steward...
* `main` (in `scripts/generate_steward_docs.py`): Generate STEWARD.md for all agents...
* `discover_manifests` (in `scripts/issue_passports.py`): Discover all existing steward.json manifests...
* `main` (in `scripts/issue_passports.py`): Main execution: Issue passports for all agents.
* `__init__` (in `scripts/issue_passports.py`): Initialize the Passport Office with access to Parampara chain
* `_calculate_manifest_hash` (in `scripts/issue_passports.py`): Calculate SHA-256 hash of the manifest.

This is The Seal...
* `_parse_old_manifest` (in `scripts/issue_passports.py`): Parse an existing steward.json manifest and extract metadata...
* `_generate_manifest` (in `scripts/issue_passports.py`): Generate a STEWARD Protocol compliant manifest (Phase 6 schema).

Schema:
{
    "identity": { "agent_id", "name" },
    "specs": { "version", "domain", "description" },
    "capabilities": { "operations": [...
* `issue_passport` (in `scripts/issue_passports.py`): Issue a passport for an agent by reissuing their steward.json...
* `close` (in `scripts/issue_passports.py`): Close the Passport Office
* `migrate_herald_dependencies` (in `scripts/migrate_herald_deps.py`): Migrate Herald dependencies from requirements.txt to pyproject...
* `clear_screen` (in `scripts/resource_dashboard.py`): Clear terminal screen
* `format_status` (in `scripts/resource_dashboard.py`): Format status indicator
* `display_dashboard` (in `scripts/resource_dashboard.py`): Display resource dashboard
* `main` (in `scripts/resource_dashboard.py`): Main dashboard loop
* `main` (in `scripts/run_server.py`): Main entry point.
* `__init__` (in `scripts/run_server.py`): Initialize the bootloader.

Args:
    ledger_path: Path to SQLite ledger (default: data/vibe_ledger...
* `_load_config` (in `scripts/run_server.py`): Load and validate system configuration.

This loads THE DHARMA (configuration) which defines the entire city...
* `_print_banner` (in `scripts/run_server.py`): Print the system startup banner.
* `boot_kernel` (in `scripts/run_server.py`): Boot the VibeOS Kernel using unified BootOrchestrator.

This replaces the old hardcoded 12-agent boot with dynamic discovery
of all 23 agents via steward...
* `verify_envoy` (in `scripts/run_server.py`): Verify that ENVOY (System Shell) is properly wired.

Returns:
    bool: True if ENVOY is ready
* `start_gateway` (in `scripts/run_server.py`): Start the FastAPI Gateway server.

This exposes the ENVOY via HTTP and connects to the frontend...
* `run` (in `scripts/run_server.py`): Execute the full boot sequence:
1. Print banner
2...
* `check_hooks_installed` (in `scripts/setup_hooks.py`): Check which hooks are installed.
* `install_hook` (in `scripts/setup_hooks.py`): Install a git hook.
* `self_heal_hooks` (in `scripts/setup_hooks.py`): Check hooks and optionally fix them.
* `main` (in `scripts/setup_hooks.py`): Main entry point.
* `smoke_test_kernel` (in `scripts/smoke_test_kernel.py`): THE SMOKE TEST - Does Vibe OS v2.0 actually work?
* `smoke_test` (in `scripts/smoke_test_operator.py`): Run the smoke test.
* `receive_context` (in `scripts/smoke_test_operator.py`): Store received context for verification.
* `provide_intent` (in `scripts/smoke_test_operator.py`): Return next predefined intent.
* `get_memory_usage_mb` (in `scripts/stress_test_city.py`): Get current process memory usage in MB
* `stress_test_city` (in `scripts/stress_test_city.py`): THE STRESS TEST - Can the entire Agent City boot and survive?
* `test_herald_migration` (in `scripts/test_herald_migration.py`): Test Herald migration to system interface.
* `test_parampara` (in `scripts/test_parampara.py`): Run comprehensive Parampara tests
* `test_scribe_publishing` (in `scripts/test_scribe_publishing.py`): Test Scribe publishing mechanism (Phase 2.5)...
* `test_watchman_deep_inspection` (in `scripts/test_watchman_deep_inspection.py`): Test Watchman deep inspection mechanism (Phase 3.2)...
* `validate_manifest` (in `scripts/validate_all_steward_json.py`): Validate a single steward.json file...
* `test_kernel_bank_isolation` (in `scripts/verify_database_isolation.py`): Test that kernel's CivicBank uses VFS-isolated path
* `test_agent_bank_isolation` (in `scripts/verify_database_isolation.py`): Test that agents would use their own sandbox paths
* `test_vfs_basic_operations` (in `scripts/verify_filesystem_isolation.py`): Test basic VFS operations within sandbox
* `test_vfs_security` (in `scripts/verify_filesystem_isolation.py`): Test VFS security - attempts to escape sandbox
* `test_vfs_subdirectories` (in `scripts/verify_filesystem_isolation.py`): Test VFS with subdirectories
* `verify_chain` (in `scripts/verify_lineage_chain.py`): Perform comprehensive chain verification.

Returns:
    True if all checks pass, False otherwise
* `test_tampering` (in `scripts/verify_lineage_chain.py`): Test tampering detection by attempting to modify the database.

WARNING: This is destructive! Only use on test chains...
* `test_monkey_patching` (in `scripts/verify_monkey_patching.py`): Test that monkey-patching redirects builtin functions
* `test_scribe_symlink` (in `scripts/verify_monkey_patching.py`): Test that Scribe gets repo access via symlink
* `test_whitelisted_domain` (in `scripts/verify_network_isolation.py`): Test request to whitelisted domain
* `test_non_whitelisted_domain` (in `scripts/verify_network_isolation.py`): Test request to non-whitelisted domain
* `test_request_logging` (in `scripts/verify_network_isolation.py`): Test that requests are logged
* `test_whitelist_management` (in `scripts/verify_network_isolation.py`): Test adding/removing domains from whitelist
* `test_subdomain_matching` (in `scripts/verify_network_isolation.py`): Test that subdomains are allowed if parent domain is whitelisted
* `check_connection` (in `scripts/vibe_cli.py`): Ping the Milk Ocean Router
* `send_prayer` (in `scripts/vibe_cli.py`): Sents a request to the Milk Ocean Router
* `parse_response` (in `scripts/vibe_cli.py`): Parses the intelligent JSON output from UniversalProvider
* `cleanup` (in `scripts/vibe_launcher.py`): THE CLEANER: Guarantees no zombies are left behind.
Runs on exit, crash, or interrupt...
* `check_port` (in `scripts/vibe_launcher.py`): Returns True if port is FREE, False if BUSY.
* `preload_semantic_model` (in `scripts/vibe_launcher.py`): Background task: Pre-download sentence-transformers model on startup.
This ensures the model is cached before the gateway needs it...
* `wait_for_health` (in `scripts/vibe_launcher.py`): Offensive Health Check:
Don't just hope it started. Verify it answers via HTTP...
### docs -> architecture -> scripts
* `find_manifests` (in `docs/architecture/scripts/validate_manifests.py`): Find all steward.json files...
* `validate_manifest` (in `docs/architecture/scripts/validate_manifests.py`): Validate a single manifest file.
* `scan_numbered_refs` (in `docs/architecture/scripts/scan_architecture_keywords.py`): Scan for numbered references like GAD-000, ARCH-021.
* `scan_concepts` (in `docs/architecture/scripts/scan_architecture_keywords.py`): Scan for domain concepts (vedic terms etc).
* `run_script` (in `docs/architecture/scripts/run_all_analyzers.py`): Run a script and capture output.
* `scan_codebase` (in `docs/architecture/scripts/generate_gad_index.py`): Scan all code for GAD references.
* `determine_pillar` (in `docs/architecture/scripts/generate_gad_index.py`): Determine which pillar a GAD belongs to based on number. Pure math, no hardcoded names...
* `build_index` (in `docs/architecture/scripts/generate_gad_index.py`): Build structured index from GAD data.
* `find_files_with_gad` (in `docs/architecture/scripts/extract_gad_spec.py`): Find all files containing GAD-XXXX references.
* `extract_docstrings` (in `docs/architecture/scripts/extract_gad_spec.py`): Extract module docstring and class/function docstrings.
* `extract_gad_context` (in `docs/architecture/scripts/extract_gad_spec.py`): Extract lines around GAD references for context.
* `generate_draft_spec` (in `docs/architecture/scripts/extract_gad_spec.py`): Generate a draft specification from extracted code.
* `count_lines` (in `docs/architecture/scripts/analyze_kernel_modules.py`): Count non-empty, non-comment lines.
* `extract_module_info` (in `docs/architecture/scripts/analyze_kernel_modules.py`): Extract docstring, classes, functions from a Python module.
* `analyze_directory` (in `docs/architecture/scripts/analyze_kernel_modules.py`): Recursively analyze a directory.
* `run_git` (in `docs/architecture/scripts/analyze_git_history.py`): Run git command and return output.
* `get_commit_count` (in `docs/architecture/scripts/analyze_git_history.py`): Total commits.
* `get_file_churn` (in `docs/architecture/scripts/analyze_git_history.py`): Most frequently changed files.
* `get_module_activity` (in `docs/architecture/scripts/analyze_git_history.py`): Commits per top-level module.
* `get_arch_commits` (in `docs/architecture/scripts/analyze_git_history.py`): Commits mentioning architecture keywords.
* `get_recent_commits` (in `docs/architecture/scripts/analyze_git_history.py`): Recent commits with their affected modules.
* `get_first_commits_by_module` (in `docs/architecture/scripts/analyze_git_history.py`): When was each module first created?
* `get_contributor_stats` (in `docs/architecture/scripts/analyze_git_history.py`): Top contributors by commit count.
* `find_gad_docs` (in `docs/architecture/scripts/analyze_gad_references.py`): Find all existing GAD-*.md documents...
* `find_gad_references_in_file` (in `docs/architecture/scripts/analyze_gad_references.py`): Find all GAD-XXXX references in a single file.
* `scan_codebase` (in `docs/architecture/scripts/analyze_gad_references.py`): Scan entire codebase for GAD references.
### steward -> system_agents -> supreme_court
* `__init__` (in `steward/system_agents/supreme_court/cartridge_main.py`): Initialize SupremeCourt cartridge.

Args:
    config: CivicConfig instance from Phoenix Config (optional)
* `get_manifest` (in `steward/system_agents/supreme_court/cartridge_main.py`): Return agent manifest.
* `report_status` (in `steward/system_agents/supreme_court/cartridge_main.py`): Report agent status for kernel health monitoring.
* `process` (in `steward/system_agents/supreme_court/cartridge_main.py`): Process a task from the kernel scheduler.

Task types:
- "file_appeal" - Agent appeals an AUDITOR violation
- "review_appeal" - Court reviews and votes on appeal
- "issue_verdict" - Court issues verdict (mercy or uphold)
- "record_precedent" - Record decision as legal precedent
- "get_appeals_status" - Query appeal status
* `_handle_file_appeal` (in `steward/system_agents/supreme_court/cartridge_main.py`): LAYER 1: Accept an appeal from a condemned agent.

The agent must provide:
- agent_id: Agent appealing
- violation_id: AUDITOR violation being appealed
- justification: Why mercy should be granted
- evidence: Proof of constitutional oath & good standing
* `_handle_review_appeal` (in `steward/system_agents/supreme_court/cartridge_main.py`): LAYER 2: Mercy Investigation - Review the appeal.

The court checks:
1...
* `_handle_issue_verdict` (in `steward/system_agents/supreme_court/cartridge_main.py`): LAYER 3: Verdict Issuance - Court decides mercy or upholds violation.

The verdict can be:
- MERCY_GRANTED: Override violation, restore agent
- MERCY_CONDITIONAL: Override with conditions (probation)
- UPHELD: Violation stands, agent is terminated
* `_handle_record_precedent` (in `steward/system_agents/supreme_court/cartridge_main.py`): LAYER 4: Record this decision as legal precedent.

Precedent building is critical:
- Future appeals cite this case
- System learns what justice looks like
- Establishes patterns of mercy
* `_handle_get_appeals_status` (in `steward/system_agents/supreme_court/cartridge_main.py`): Get status of appeals (for monitoring).
* `_handle_get_precedent_summary` (in `steward/system_agents/supreme_court/cartridge_main.py`): Get summary of precedent cases.
* `_verify_constitutional_oath` (in `steward/system_agents/supreme_court/cartridge_main.py`): Verify that an agent has signed the Constitutional Oath.

This is the KEY TO MERCY: only agents bound by the Constitution
can be saved...
* `_check_credit_balance` (in `steward/system_agents/supreme_court/cartridge_main.py`): Check agent's credit balance in the system.
* `_count_previous_violations` (in `steward/system_agents/supreme_court/cartridge_main.py`): Count how many times this agent has been violated.
* `_get_agent_type` (in `steward/system_agents/supreme_court/cartridge_main.py`): Get the type/domain of an agent.
* `_determine_mercy_eligibility` (in `steward/system_agents/supreme_court/cartridge_main.py`): MERCY PROTOCOL: Determine if agent is eligible for mercy.

Criteria:
1...
* `_restore_agent` (in `steward/system_agents/supreme_court/cartridge_main.py`): Restore an agent after mercy is granted.

This is the inverse of termination:
- Clear violation flags
- Restore process state
- Reset monitoring
### steward -> system_agents -> herald
* `__init__` (in `steward/system_agents/herald/cartridge_main.py`): Initialize HERALD as a ContextAwareAgent.

Args:
    config: HeraldConfig instance from Phoenix Config (optional)
           If not provided, HeraldConfig defaults are used
* `event_log` (in `steward/system_agents/herald/cartridge_main.py`): Lazy-load EventLog after system interface injection.

PHASE 2...
* `boot` (in `steward/system_agents/herald/cartridge_main.py`): Extended boot sequence including Constitutional Oath ceremony.

This is the Genesis Ceremony:
1...
* `process` (in `steward/system_agents/herald/cartridge_main.py`): Process a task from the VibeKernel scheduler.

HERALD responds to content generation and broadcasting tasks:
- "run_campaign": Execute full research → create → validate → publish workflow
- "publish": Publish prepared content
- "check_license": Verify broadcast license with CIVIC
* `get_manifest` (in `steward/system_agents/herald/cartridge_main.py`): Return agent manifest for kernel registry.
* `report_status` (in `steward/system_agents/herald/cartridge_main.py`): Report HERALD status (VibeAgent interface) - Deep Introspection.
* `run_campaign` (in `steward/system_agents/herald/cartridge_main.py`): Execute campaign workflow - DEPRECATED (ContentTool moved to MARKETER).

HERALD is infrastructure-only (broadcast, research, identity, logging)...
* `_check_connectivity` (in `steward/system_agents/herald/cartridge_main.py`): Helper method to check connectivity via kernel (herald.broadcast)...
* `_cite_governance_constraint` (in `steward/system_agents/herald/cartridge_main.py`): Generate explicit citation of governance constraint being violated.

Phase II Enhancement: Force transparency about why actions are blocked...
* `execute_publish` (in `steward/system_agents/herald/cartridge_main.py`): Execute publication action with event recording.

This method publishes pre-approved content to configured platforms
and records all actions in the event ledger...
* `plan_campaign` (in `steward/system_agents/herald/cartridge_main.py`): Strategic campaign planning - DEPRECATED (StrategyTool removed).

HERALD is now infrastructure-only (broadcast, research, identity, logging)...
* `run_reply_cycle` (in `steward/system_agents/herald/cartridge_main.py`): Execute the engagement loop: Listen -> Think -> Draft.

1...
* `generate_reddit_post` (in `steward/system_agents/herald/cartridge_main.py`): Generate a Reddit deep-dive post (standalone capability).

Args:
    subreddit: Target subreddit

Returns:
    dict: {"title": str, "body": str} or None
* `main` (in `steward/system_agents/herald/cli.py`): CLI entry point.
* `__init__` (in `steward/system_agents/herald/cli.py`): Initialize CLI.
* `_init_director` (in `steward/system_agents/herald/cli.py`): Initialize the Agency Director. Return True if successful...
* `cmd_status` (in `steward/system_agents/herald/cli.py`): Show current agency state.

Returns:
    0 if state available, 1 if not
* `cmd_run` (in `steward/system_agents/herald/cli.py`): Execute one complete I-P-V-O cycle.

Returns:
    0 if SUCCESS, 1 if VALIDATION_FAILED or ERROR
* `cmd_loop` (in `steward/system_agents/herald/cli.py`): Run continuous cycles (daemon mode).

Returns:
    0 if normal exit, 1 if error during initialization
* `cmd_simulate` (in `steward/system_agents/herald/cli.py`): Run simulation (dry-run without real posts).

Returns:
    0 if simulation succeeds, 1 otherwise
* `run` (in `steward/system_agents/herald/cli.py`): Main entry point.
* `_generate_fallback_manifesto` (in `steward/system_agents/herald/manifesto.py`): Generate fallback manifesto when API is unavailable.
* `load_agi_context` (in `steward/system_agents/herald/manifesto.py`): Load A.G...
* `generate_manifesto` (in `steward/system_agents/herald/manifesto.py`): Generate the A.G...
### steward -> system_agents -> discoverer
* `__init__` (in `steward/system_agents/discoverer/cartridge_main.py`): Initialize Discoverer cartridge.
* `report_status` (in `steward/system_agents/discoverer/cartridge_main.py`): Report DISCOVERER status for observability (Article IV compliance).
* `process` (in `steward/system_agents/discoverer/agent.py`): Handle direct tasks sent to the Steward.
* `start_monitoring` (in `steward/system_agents/discoverer/agent.py`): Start the background discovery loop.
* `stop_monitoring` (in `steward/system_agents/discoverer/agent.py`): Stop the background loop.
* `_monitoring_loop` (in `steward/system_agents/discoverer/agent.py`): The eternal watch. Scans for new life...
* `discover_agents` (in `steward/system_agents/discoverer/agent.py`): Scan BOTH system_agents and agent_city/registry for steward.json manifests...
* `_load_agent_from_manifest` (in `steward/system_agents/discoverer/agent.py`): Reads steward.json and creates a VibeAgent instance...
* `_try_load_real_cartridge` (in `steward/system_agents/discoverer/agent.py`): Dynamically load cartridge from cartridge_main.py...
* `__init__` (in `steward/system_agents/discoverer/agent.py`): Initialize GenericAgent with flexible parameter support.

Supports two initialization modes:
1...
* `process` (in `steward/system_agents/discoverer/agent.py`): Process task from kernel scheduler.

ROBUST IMPLEMENTATION:
- Async for kernel compatibility
- Try/except for error resilience
- Logs task receipt for debugging
### steward -> system_agents -> civic
* `__init__` (in `steward/system_agents/civic/cartridge_main.py`): Initialize CIVIC (The Bureaucrat) as a VibeAgent.

Args:
    config: CivicConfig instance from Phoenix Config (optional)
           If not provided, CivicConfig defaults are used
* `set_kernel` (in `steward/system_agents/civic/cartridge_main.py`): Override set_kernel to inject system interface into sub-agents.

When the kernel boots and calls agent...
* `registry_path` (in `steward/system_agents/civic/cartridge_main.py`): Lazy-load registry path (sandboxed).
* `agents_md_path` (in `steward/system_agents/civic/cartridge_main.py`): Lazy-load agents.md path (sandboxed)...
* `state_path` (in `steward/system_agents/civic/cartridge_main.py`): Lazy-load state path (sandboxed).
* `process` (in `steward/system_agents/civic/cartridge_main.py`): Process a task from the VibeKernel scheduler.

CIVIC delegates to three specialized agents (P1 Refactor):
- Registry Agent: scan_and_register, get_registry (governance only, no documentation)
- Economy Agent: check_license, deduct_credits, refill_credits, revoke_license
- Lifecycle Agent: check_action_permission, authorize_brahmachari_to_grihastha, report_violation, get_lifecycle_status

Note: Documentation (AGENTS...
* `get_manifest` (in `steward/system_agents/civic/cartridge_main.py`): Return agent manifest for kernel registry.
* `report_status` (in `steward/system_agents/civic/cartridge_main.py`): Report CIVIC status (VibeAgent interface) - Aggregated from delegated agents.
* `_load_state` (in `steward/system_agents/civic/cartridge_main.py`): Load CIVIC state or initialize.
* `_save_state` (in `steward/system_agents/civic/cartridge_main.py`): Save CIVIC state to disk.
* `_load_matrix` (in `steward/system_agents/civic/cartridge_main.py`): Load THE MATRIX configuration from config/matrix.yaml...
* `_default_matrix` (in `steward/system_agents/civic/cartridge_main.py`): Return default matrix configuration.
* `get_matrix_config` (in `steward/system_agents/civic/cartridge_main.py`): Get a configuration value from THE MATRIX.
* `set_system` (in `steward/system_agents/civic/economy_agent.py`): Inject system interface from parent CIVIC cartridge.

This allows the EconomyAgent sub-agent to access kernel tools
via self...
* `process` (in `steward/system_agents/civic/economy_agent.py`): Process economy-related tasks.
* `check_broadcast_license` (in `steward/system_agents/civic/economy_agent.py`): Check if an agent has broadcast license.
* `deduct_credits` (in `steward/system_agents/civic/economy_agent.py`): Deduct credits from an agent's account.

This records the transaction in the ledger...
* `refill_credits` (in `steward/system_agents/civic/economy_agent.py`): Refill an agent's credits (admin operation).
* `revoke_license` (in `steward/system_agents/civic/economy_agent.py`): Revoke an agent's broadcast license.
* `report_status` (in `steward/system_agents/civic/economy_agent.py`): Report economy status.
* `set_system` (in `steward/system_agents/civic/lifecycle_agent.py`): Inject system interface from parent CIVIC cartridge.

This allows the LifecycleAgent to access kernel tools
via self...
* `process` (in `steward/system_agents/civic/lifecycle_agent.py`): Process lifecycle-related tasks.
* `check_action_permission` (in `steward/system_agents/civic/lifecycle_agent.py`): Check if an agent has permission to perform an action based on lifecycle status.
* `authorize_brahmachari_to_grihastha` (in `steward/system_agents/civic/lifecycle_agent.py`): Promote an agent from Brahmachari (Student) to Grihastha (Householder).
* `report_violation` (in `steward/system_agents/civic/lifecycle_agent.py`): Report a violation and potentially demote an agent.
* `get_lifecycle_status` (in `steward/system_agents/civic/lifecycle_agent.py`): Get global lifecycle enforcement status.
* `get_agent_status` (in `steward/system_agents/civic/lifecycle_agent.py`): Get lifecycle status for a specific agent.
* `report_status` (in `steward/system_agents/civic/lifecycle_agent.py`): Report lifecycle agent status.
* `set_system` (in `steward/system_agents/civic/registry_agent.py`): Inject system interface from parent CIVIC cartridge.

Currently RegistryAgent doesn't use tools via kernel, but this
maintains consistency with other sub-agents...
* `process` (in `steward/system_agents/civic/registry_agent.py`): Process registry-related tasks (governance only, no documentation).
* `scan_and_register_agents` (in `steward/system_agents/civic/registry_agent.py`): Scan filesystem for agents and register them.
* `get_registry` (in `steward/system_agents/civic/registry_agent.py`): Return current registry.
* `register_agent` (in `steward/system_agents/civic/registry_agent.py`): Register a single agent.
* `_find_agent_cartridges` (in `steward/system_agents/civic/registry_agent.py`): Find all agent cartridge_main.py files...
* `_validate_agent_config` (in `steward/system_agents/civic/registry_agent.py`): Validate an agent's configuration.
* `_load_registry` (in `steward/system_agents/civic/registry_agent.py`): Load citizen registry from disk or initialize empty.
* `_save_registry` (in `steward/system_agents/civic/registry_agent.py`): Save citizen registry to disk.
* `report_status` (in `steward/system_agents/civic/registry_agent.py`): Report registry status.
### agent_city -> registry -> dhruva
* `__init__` (in `agent_city/registry/dhruva/cartridge_main.py`): Initialize DhruvaAnchor cartridge.
* `get_manifest` (in `agent_city/registry/dhruva/cartridge_main.py`): Return agent manifest.
* `report_status` (in `agent_city/registry/dhruva/cartridge_main.py`): Report agent status for kernel health monitoring.
* `process` (in `agent_city/registry/dhruva/cartridge_main.py`): Process a task from the kernel scheduler.

Task types:
- "verify_genesis" - Check genesis block integrity
- "record_truth" - Record a verified fact
- "resolve_conflict" - Resolve conflicting claims
- "sync_to_dhruva" - Align agent to immutable reference
- "check_data_ethics" - Verify data extraction follows Prithu principle
- "get_truth_status" - Query truth matrix status
* `_handle_verify_genesis` (in `agent_city/registry/dhruva/cartridge_main.py`): LAYER 1: Verify the genesis block (immutable truth).

The genesis block is sacred - it's the baseline from which
everything else is measured...
* `_handle_record_truth` (in `agent_city/registry/dhruva/cartridge_main.py`): LAYER 2: Record a verified fact in the Truth Matrix.

Facts can only be recorded if:
1...
* `_handle_resolve_conflict` (in `agent_city/registry/dhruva/cartridge_main.py`): LAYER 3: Resolve conflicting claims using Dhruva principle.

When two agents make contradictory claims, the system must decide
which is the authoritative truth...
* `_handle_sync_to_dhruva` (in `agent_city/registry/dhruva/cartridge_main.py`): LAYER 1: Synchronize an agent to the Dhruva (immutable reference).

This ensures all agents have the same baseline understanding of truth...
* `_handle_check_data_ethics` (in `agent_city/registry/dhruva/cartridge_main.py`): LAYER 4: Check if data extraction follows Prithu principle.

The Prithu principle: You can extract resources only for legitimate needs...
* `_handle_get_truth_status` (in `agent_city/registry/dhruva/cartridge_main.py`): Get status of the Truth Matrix.
* `_handle_get_genesis_status` (in `agent_city/registry/dhruva/cartridge_main.py`): Get status of the Genesis Block.
* `_compare_states` (in `agent_city/registry/dhruva/cartridge_main.py`): Compare current state against canonical state.
### agent_city -> registry -> artisan
* `__init__` (in `agent_city/registry/artisan/cartridge_main.py`): Initialize the Artisan as a VibeAgent.
* `process_media` (in `agent_city/registry/artisan/cartridge_main.py`): Process a media file (Crop, Brand, Optimize).

NEW: Uses kernel-managed tools via self...
* `process` (in `agent_city/registry/artisan/cartridge_main.py`): Process a task from the VibeKernel scheduler.

ARTISAN responds to media processing tasks:
- "process_media": Process a media file
* `get_manifest` (in `agent_city/registry/artisan/cartridge_main.py`): Return agent manifest for kernel registry.
* `report_status` (in `agent_city/registry/artisan/cartridge_main.py`): Report ARTISAN status (VibeAgent interface).
### vibe_core -> protocols
* `create_system_context` (in `vibe_core/protocols/operator_protocol.py`): Factory function to create SystemContext with common defaults.
* `create_intent` (in `vibe_core/protocols/operator_protocol.py`): Factory function to create Intent with common defaults.
* `create_response` (in `vibe_core/protocols/operator_protocol.py`): Factory function to create OperatorResponse with common defaults.
* `receive_context` (in `vibe_core/protocols/operator_protocol.py`): Receive the current system state.

For Human: Render as markdown in terminal/web
For Claude: Inject as system prompt
For LLM: Send as API context
For Local: Pass as string

Args:
    context: Strictly typed system state
* `provide_intent` (in `vibe_core/protocols/operator_protocol.py`): Provide the next action/decision.

For Human: Read from stdin/form
For Claude: Parse response
For LLM: Parse API response
For Local: Parse output

Returns:
    Strictly typed intent
* `is_available` (in `vibe_core/protocols/operator_protocol.py`): Check if this operator is currently available.

Used for graceful degradation - if operator isn't available,
fall back to next in priority chain...
* `get_operator_type` (in `vibe_core/protocols/operator_protocol.py`): Return the type of this operator.
* `to_dict` (in `vibe_core/protocols/agent.py`): Convert to dictionary
* `to_dict` (in `vibe_core/protocols/agent.py`): Serialize to dictionary
* `__init__` (in `vibe_core/protocols/agent.py`): Initialize a VibeAgent
* `set_kernel` (in `vibe_core/protocols/agent.py`): Kernel Injection Pattern

Called by VibeKernel.boot() to give agents access to the kernel...
* `set_kernel_pipe` (in `vibe_core/protocols/agent.py`): Inject IPC Pipe for Process Isolation.

Phase 4b: MONKEY PATCH builtins to redirect to VFS/Network Proxy...
* `get_sandbox_path` (in `vibe_core/protocols/agent.py`): Get absolute path to agent's sandbox directory.

This is for C-extensions (sqlite3, pandas, etc...
* `send_to_kernel` (in `vibe_core/protocols/agent.py`): Send a message to the Kernel via IPC.
* `process` (in `vibe_core/protocols/agent.py`): Process a Task from the kernel scheduler

Args:
    task: Task object with agent_id, payload, id

Returns:
    Dictionary with task result {status, output, error, ....
* `get_manifest` (in `vibe_core/protocols/agent.py`): Return this agent's manifest (identity + capabilities)

Called by kernel.manifest_registry during boot...
* `report_status` (in `vibe_core/protocols/agent.py`): Report current agent status (optional)

Used by introspection and monitoring.
Default implementation is minimal...
* `emit_event` (in `vibe_core/protocols/agent.py`): Emit an event for real-time monitoring (Canto 10: Pulse System)

This allows agents to broadcast their state changes to the event bus.
Events are visualized in real-time on the Live Darshan dashboard...
* `emit_event_sync` (in `vibe_core/protocols/agent.py`): Synchronous wrapper for emit_event (for use in non-async contexts)

This is a convenience method for agents that operate in sync contexts.
It tries to emit via the event bus if an event loop is available...
* `vfs_open` (in `vibe_core/protocols/agent.py`): Intercepted open() that redirects to VFS.

WARNING: This does NOT intercept C-level file operations
(e...
* `submit_task` (in `vibe_core/protocols/ledger.py`): Submit a task to the queue, return task_id
* `next_task` (in `vibe_core/protocols/ledger.py`): Pop next task from queue
* `get_queue_status` (in `vibe_core/protocols/ledger.py`): Get queue statistics
* `record_event` (in `vibe_core/protocols/ledger.py`): Record a generic event (used by agents for governance actions)

Args:
    event_type: Type of event (e.g...
* `record_start` (in `vibe_core/protocols/ledger.py`): Record task start
* `record_completion` (in `vibe_core/protocols/ledger.py`): Record task completion
* `record_failure` (in `vibe_core/protocols/ledger.py`): Record task failure
* `get_task` (in `vibe_core/protocols/ledger.py`): Query task result
* `register` (in `vibe_core/protocols/ledger.py`): Register an agent manifest
* `lookup` (in `vibe_core/protocols/ledger.py`): Look up manifest by agent_id
* `find_by_capability` (in `vibe_core/protocols/ledger.py`): Find agents with a specific capability
* `list_all` (in `vibe_core/protocols/ledger.py`): List all registered manifests
* `agent_registry` (in `vibe_core/protocols/ledger.py`): Get all registered agents {agent_id: agent}
* `scheduler` (in `vibe_core/protocols/ledger.py`): Get the task scheduler
* `ledger` (in `vibe_core/protocols/ledger.py`): Get the immutable ledger
* `manifest_registry` (in `vibe_core/protocols/ledger.py`): Get the manifest registry
* `status` (in `vibe_core/protocols/ledger.py`): Get kernel status
* `register_agent` (in `vibe_core/protocols/ledger.py`): Register an agent and inject kernel reference
* `get_status` (in `vibe_core/protocols/ledger.py`): Get full kernel status
* `get_agent_manifest` (in `vibe_core/protocols/ledger.py`): Get manifest for an agent
* `find_agents_by_capability` (in `vibe_core/protocols/ledger.py`): Find agents with a specific capability
* `register` (in `vibe_core/protocols/registry.py`): Register an agent manifest
* `lookup` (in `vibe_core/protocols/registry.py`): Look up manifest by agent_id
* `find_by_capability` (in `vibe_core/protocols/registry.py`): Find agents with a specific capability
* `list_all` (in `vibe_core/protocols/registry.py`): List all registered manifests
* `submit_task` (in `vibe_core/protocols/scheduler.py`): Submit a task to the queue, return task_id
* `next_task` (in `vibe_core/protocols/scheduler.py`): Pop next task from queue
* `get_queue_status` (in `vibe_core/protocols/scheduler.py`): Get queue statistics
### vibe_core
* `submit_task` (in `vibe_core/kernel_impl.py`): Submit task to queue, return task_id

PHASE 3: Checks Sarga cycle before allowing task submission
* `next_task` (in `vibe_core/kernel_impl.py`): Pop next task from queue
* `get_queue_status` (in `vibe_core/kernel_impl.py`): Get queue statistics
* `register` (in `vibe_core/kernel_impl.py`): Register an agent manifest
* `lookup` (in `vibe_core/kernel_impl.py`): Look up manifest by agent_id
* `find_by_capability` (in `vibe_core/kernel_impl.py`): Find agents with a specific capability
* `list_all` (in `vibe_core/kernel_impl.py`): List all registered manifests
* `__init__` (in `vibe_core/kernel_impl.py`): Initialize the kernel
* `get_bank` (in `vibe_core/kernel_impl.py`): Lazy-load the CivicBank.

Phase 4c: Use VFS path for database to ensure it's in sandbox...
* `get_vault` (in `vibe_core/kernel_impl.py`): Get the CivicVault instance (Lazy Loaded).

Requires: cryptography package (see pyproject...
* `_check_agent_capability` (in `vibe_core/kernel_impl.py`): SECURITY (ARCH-HARDENING): Check if agent has a specific capability.

This method is called by ToolRegistry to enforce capability-based
access control...
* `_narasimha_destroy_agent` (in `vibe_core/kernel_impl.py`): NARASIMHA DESTRUCTION HANDLER - Called when Narasimha activates.

This is the REAL kill-switch...
* `_register_core_tools` (in `vibe_core/kernel_impl.py`): Register core tools that are available to all agents.

Core tools are system-provided capabilities that don't belong to
any specific agent...
* `_discover_agent_tools` (in `vibe_core/kernel_impl.py`): Auto-discover and register agent tools.

Phase 6: Automatic tool discovery from agent directories...
* `agent_registry` (in `vibe_core/kernel_impl.py`): Get all registered agents {agent_id: agent}

SECURITY: Returns a READ-ONLY view to prevent registry poisoning.
Agents cannot modify the registry directly...
* `scheduler` (in `vibe_core/kernel_impl.py`): Get the task scheduler
* `ledger` (in `vibe_core/kernel_impl.py`): Get the immutable ledger

WARNING: Direct ledger access allows identity spoofing.
Prefer record_verified_event() for agent-attributed events...
* `record_verified_event` (in `vibe_core/kernel_impl.py`): Record an event with identity verification.

SECURITY: Prevents identity spoofing by validating:
1...
* `manifest_registry` (in `vibe_core/kernel_impl.py`): Get the manifest registry
* `status` (in `vibe_core/kernel_impl.py`): Get kernel status
* `register_agent` (in `vibe_core/kernel_impl.py`): Register an agent and inject kernel reference.

🛡️  GOVERNANCE GATE: This kernel enforces Constitutional Oath...
* `spawn_deferred_agents` (in `vibe_core/kernel_impl.py`): Spawn processes for all registered agents that don't have running processes.

Called after discovery to batch-spawn all agents at once, avoiding the
import lock deadlock that occurs when spawning 13+ processes in a tight loop...
* `boot` (in `vibe_core/kernel_impl.py`): Boot the kernel - register all manifests and start scheduler
* `tick` (in `vibe_core/kernel_impl.py`): Tick the kernel - process one task from the scheduler
* `get_status` (in `vibe_core/kernel_impl.py`): Get full kernel status
* `_process_ipc_events` (in `vibe_core/kernel_impl.py`): Phase 2: Process IPC messages from agents (Task Results, Crashes, etc.)
* `_sync_resource_quotas` (in `vibe_core/kernel_impl.py`): Phase 3: Sync resource quotas with CivicBank credits.

This makes credits REAL by updating CPU/RAM limits based on balance...
* `_grant_repo_access` (in `vibe_core/kernel_impl.py`): Phase 4b: Grant controlled repo access via symlink.

Scribe and Archivist need to read the main repo...
* `_check_system_health` (in `vibe_core/kernel_impl.py`): 🛡️ IMMUNE SYSTEM WATCHDOG

Called after every task execution.
If Auditor detects CRITICAL_VIOLATION -> Kernel shuts down...
* `get_agent_manifest` (in `vibe_core/kernel_impl.py`): Get manifest for an agent
* `get_agent_varna` (in `vibe_core/kernel_impl.py`): Get the Varna (classification) of an agent.
* `get_agent_ashrama` (in `vibe_core/kernel_impl.py`): Get the Ashrama (lifecycle stage) of an agent.
* `get_agent_permissions` (in `vibe_core/kernel_impl.py`): Get the current permissions for an agent based on Ashrama.
* `check_agent_permission` (in `vibe_core/kernel_impl.py`): Check if an agent has a specific permission based on Ashrama.
* `transition_agent_ashrama` (in `vibe_core/kernel_impl.py`): Transition an agent to a new Ashrama (lifecycle stage).

Returns True if transition succeeded, False otherwise...
* `get_governance_status` (in `vibe_core/kernel_impl.py`): Get full governance status for an agent (Varna + Ashrama).
* `shutdown` (in `vibe_core/kernel_impl.py`): Gracefully shut down the kernel
* `find_agents_by_capability` (in `vibe_core/kernel_impl.py`): Find agents with a specific capability
* `revoke_capability` (in `vibe_core/kernel_impl.py`): Revoke capabilities from an agent (REVOKE_MANDATE syscall).

Permission Model:
    - KERNEL can revoke from anyone
    - CIVIC can revoke from anyone (governance)
    - Agents can revoke from themselves (voluntary)

Args:
    agent_id: The agent to revoke from
    capabilities: List of capabilities to revoke
    revoker_id: The agent/system performing the revocation
    reason: Optional reason for revocation

Returns:
    Dictionary with success, revoked list, and message
* `grant_capability` (in `vibe_core/kernel_impl.py`): Grant capabilities to an agent.

Permission Model:
    - KERNEL can grant to anyone
    - CIVIC can grant to anyone (governance)

Args:
    agent_id: The agent to grant to
    capabilities: List of capabilities to grant
    granter_id: The agent/system performing the grant
    reason: Optional reason for grant

Returns:
    Dictionary with success, granted list, and message
* `get_agent_capabilities` (in `vibe_core/kernel_impl.py`): Get current capabilities for an agent.

Args:
    agent_id: The agent to query

Returns:
    List of capabilities (empty if unregistered)
* `subscribe_to_events` (in `vibe_core/kernel_impl.py`): Subscribe to system events via EventBus.

Args:
    callback: Function to call on event (async or sync)
    event_type: Optional filter (None = all events)
    subscriber_id: Optional ID for logging (usually agent_id)

Returns:
    Subscription ID

Usage:
    def on_agent_born(event):
        print(f"New agent: {event...
* `unsubscribe_from_events` (in `vibe_core/kernel_impl.py`): Unsubscribe from system events.

Args:
    callback: The callback to remove
    event_type: Optional event type filter
* `broadcast_event` (in `vibe_core/kernel_impl.py`): Broadcast an event to all subscribers via EventBus.

Args:
    event_type: Type of event (e...
* `get_event_history` (in `vibe_core/kernel_impl.py`): Get recent event history from EventBus.

Args:
    limit: Maximum number of events to return
    event_type: Optional filter by event type

Returns:
    List of recent events
* `get_event_bus_status` (in `vibe_core/kernel_impl.py`): Get EventBus status (total events, subscribers, etc.)
* `_can_revoke_capability` (in `vibe_core/kernel_impl.py`): Check if revoker_id has permission to revoke capabilities from target_id.

Permission Model:
    - KERNEL can revoke from anyone
    - CIVIC can revoke from anyone (governance)
    - Agents can revoke from themselves (voluntary)
    - NARASIMHA can revoke from anyone (kill-switch)
* `_can_grant_capability` (in `vibe_core/kernel_impl.py`): Check if granter_id has permission to grant capabilities.

Permission Model:
    - KERNEL can grant to anyone
    - CIVIC can grant to anyone (governance)
    - No self-grant (prevents privilege escalation)
* `submit_task` (in `vibe_core/kernel_impl.py`): Submit a task to the kernel
* `get_task_result` (in `vibe_core/kernel_impl.py`): Get the result of a completed task
* `dump_ledger` (in `vibe_core/kernel_impl.py`): Dump full ledger for inspection
* `_pulse` (in `vibe_core/kernel_impl.py`): 💓 HEARTBEAT: Generate real-time snapshot of kernel state.

Event Sourcing → State Projection:
- Collects current state from all agents
- Writes vibe_snapshot...
* `_render_operations_dashboard` (in `vibe_core/kernel_impl.py`): Render OPERATIONS.md from snapshot data
* `_render_settings_file` (in `vibe_core/kernel_impl.py`): Render SETTINGS.md from snapshot data...
* `_check_settings_file_changed` (in `vibe_core/kernel_impl.py`): Check if SETTINGS.md has been modified since last read...
* `_parse_settings_commands` (in `vibe_core/kernel_impl.py`): Parse command queue from SETTINGS.md...
* `_execute_settings_commands` (in `vibe_core/kernel_impl.py`): Execute settings commands with validation and whitelist enforcement.

Security:
    - Only whitelisted settings can be modified
    - Schema validation on all inputs
    - Execution history tracking (feedback loop)
    - Audit trail in ledger
* `_set_log_level` (in `vibe_core/kernel_impl.py`): Set kernel log level (whitelisted setting)
* `_sync_settings_to_reality` (in `vibe_core/kernel_impl.py`): Synchronize SETTINGS.md commands to kernel reality...
* `_remove_executed_commands_from_file` (in `vibe_core/kernel_impl.py`): Remove executed commands from SETTINGS.md Pending Commands section...
* `_render_envoy_file` (in `vibe_core/kernel_impl.py`): Render ENVOY.md terminal interface...
* `_extract_envoy_request_content` (in `vibe_core/kernel_impl.py`): Extract user's request content from ENVOY.md...
* `_check_envoy_file_changed` (in `vibe_core/kernel_impl.py`): Check if ENVOY.md has been modified since last read...
* `_parse_envoy_requests` (in `vibe_core/kernel_impl.py`): Parse pending requests from ENVOY.md Request section...
* `_dispatch_envoy_request` (in `vibe_core/kernel_impl.py`): Route and dispatch a single user request.

ASYNC DISPATCH PATTERN:
1...
* `_sync_envoy_to_reality` (in `vibe_core/kernel_impl.py`): Synchronize ENVOY.md requests to kernel reality...
* `_clear_envoy_requests` (in `vibe_core/kernel_impl.py`): Clear processed requests from ENVOY.md Request section...
* `update_envoy_task_status` (in `vibe_core/kernel_impl.py`): Update a task's status in ENVOY.md tracking...
* `quick_boot` (in `vibe_core/boot_orchestrator.py`): Quick boot helper for simple use cases.

Args:
    ledger_path: Optional custom ledger path

Returns:
    RealVibeKernel: Fully initialized kernel

Example:
    kernel = quick_boot()
    # Use kernel...
* `boot_and_run` (in `vibe_core/boot_orchestrator.py`): Boot the system AND start the operator loop.

This is the main entry point for Agent City OS...
* `__init__` (in `vibe_core/boot_orchestrator.py`): Initialize the boot orchestrator.

Args:
    ledger_path: Path to SQLite ledger (default: data/vibe_ledger...
* `boot` (in `vibe_core/boot_orchestrator.py`): Execute the unified boot sequence via Sarga (cosmic creation).

Sarga Phases:
1...
* `_phase_shabda` (in `vibe_core/boot_orchestrator.py`): SHABDA: Sound - Boot command received, initiation logged.
* `_phase_akasha` (in `vibe_core/boot_orchestrator.py`): AKASHA: Space - Create kernel, allocate memory.
* `_phase_vayu` (in `vibe_core/boot_orchestrator.py`): VAYU: Air - Establish communication channels.
* `_phase_agni` (in `vibe_core/boot_orchestrator.py`): AGNI: Fire - Make system visible (capabilities, UI).
* `_phase_jala` (in `vibe_core/boot_orchestrator.py`): JALA: Water - Data streams flow (Knowledge Graph, discovery).
* `_phase_prithvi` (in `vibe_core/boot_orchestrator.py`): PRITHVI: Earth - Persistence (boot kernel, ledger ready).
* `get_kernel` (in `vibe_core/boot_orchestrator.py`): Get the booted kernel instance.

Returns:
    RealVibeKernel or None if not yet booted
* `get_discoverer` (in `vibe_core/boot_orchestrator.py`): Get the Discoverer agent instance.

Returns:
    Discoverer or None if not yet created
* `_init_operator_adapter` (in `vibe_core/boot_orchestrator.py`): Initialize the operator adapter with default chain.
* `_build_system_context` (in `vibe_core/boot_orchestrator.py`): Build SystemContext from current kernel state.
* `_execute_intent` (in `vibe_core/boot_orchestrator.py`): Execute an intent and return result message.
* `run_with_operator` (in `vibe_core/boot_orchestrator.py`): THE MAIN OPERATOR LOOP.

This is where the system comes alive...
* `stop` (in `vibe_core/boot_orchestrator.py`): Stop the operator loop.
* `_run_agent_process` (in `vibe_core/process_manager.py`): Static wrapper for multiprocessing target.

LATE BINDING: Receives path/classname instead of class object...
* `run` (in `vibe_core/process_manager.py`): The entry point for the child process.
* `spawn_agent` (in `vibe_core/process_manager.py`): Spawn a new agent process.

LATE BINDING: Receives cartridge_path and class_name instead of agent_class...
* `send_task` (in `vibe_core/process_manager.py`): Send a task to an agent.

Returns:
    True if task was sent and ACK received, False otherwise...
* `check_health` (in `vibe_core/process_manager.py`): NARASIMHA: The Watchdog.
Checks if processes are alive...
* `get_pending_messages` (in `vibe_core/process_manager.py`): Get all pending messages from all agents.
Returns list of (agent_id, message) tuples...
* `_handle_crash` (in `vibe_core/process_manager.py`): Restart a crashed agent.

SECURITY FIX: Actually restarts the agent (not just a stub)...
* `shutdown` (in `vibe_core/process_manager.py`): Kill all agents.
* `__init__` (in `vibe_core/file_operator.py`): Initialize the FileBasedOperator.

Args:
    file_path: The path to the file to monitor for requests...
* `receive_context` (in `vibe_core/file_operator.py`): Stores the last known system context. Currently a no-op display-wise...
* `provide_intent` (in `vibe_core/file_operator.py`): Reads the designated file, provides an intent if a new request is found,
and then clears the request from the file.
* `_clear_request_in_file` (in `vibe_core/file_operator.py`): Replaces the processed request with the placeholder text.
* `_idle_intent` (in `vibe_core/file_operator.py`): Returns a 'do nothing' intent when no request is found.
* `is_available` (in `vibe_core/file_operator.py`): This operator is always available as long as the file path is set.
* `get_operator_type` (in `vibe_core/file_operator.py`): Returns the operator type.
* `get_topology` (in `vibe_core/topology.py`): Get or create the global topology instance.

Args:
    kernel: Optional kernel for dynamic agent discovery
    refresh: If True, refresh the topology even if it exists
* `refresh_topology` (in `vibe_core/topology.py`): Force refresh the topology (e.g...
* `get_agent_placement` (in `vibe_core/topology.py`): Get the Bhu-Mandala placement for an agent.

This is the main entry point for TaskManager to wire topology awareness
into task routing...
* `print_mandala` (in `vibe_core/topology.py`): Print the ASCII mandala to console.
* `__init__` (in `vibe_core/topology.py`): Initialize the Bhu-mandala structure.

Args:
    kernel: VibeOS kernel for dynamic agent discovery (optional)...
* `_initialize_varshas` (in `vibe_core/topology.py`): Initialize varsha properties.
* `_discover_and_place_agents` (in `vibe_core/topology.py`): DYNAMIC agent discovery and placement.

Discovers agents from:
1...
* `_place_discovered_agents` (in `vibe_core/topology.py`): Place discovered agents on the mandala based on their domain.

Args:
    agents: List of agent dicts with agent_id, name, domain, description
* `refresh` (in `vibe_core/topology.py`): Refresh the topology by re-discovering agents.
* `get_agent` (in `vibe_core/topology.py`): Get an agent by name.
* `get_varsha_agents` (in `vibe_core/topology.py`): Get all agents in a specific varsha.
* `get_agents_by_radius` (in `vibe_core/topology.py`): Get all agents at a specific radius from center.
* `get_critical_agents` (in `vibe_core/topology.py`): Get all critical infrastructure agents.
* `distance_from_center` (in `vibe_core/topology.py`): Get an agent's distance from Mount Meru center.
* `authority_level` (in `vibe_core/topology.py`): Get authority level of an agent.

Higher number = closer to center = higher authority...
* `can_override` (in `vibe_core/topology.py`): Check if agent1 can override agent2 based on authority level.

Only closer-to-center agents can override outer ones...
* `generate_ascii_mandala` (in `vibe_core/topology.py`): Generate DYNAMIC ASCII art representation of the mandala.

Shows all discovered agents in their respective varshas...
* `generate_topology_report` (in `vibe_core/topology.py`): Generate detailed topology report for logging.
* `validate_topology` (in `vibe_core/topology.py`): Validate the topology structure.

Checks:
1...
* `_get_varsha_to_layer_map` (in `vibe_core/topology.py`): Map Varsha to Bhu-Mandala layers (Brahmaloka, Janaloka, etc.)
* `_get_varsha_to_varna_map` (in `vibe_core/topology.py`): Map Varsha to primary Vedic class (Varna)
* `get_agent_placement` (in `vibe_core/topology.py`): Get Bhu-Mandala placement for an agent.

Returns placement information including:
- Bhu-Mandala layer (BRAHMALOKA → BHURLOKA)
- Vedic class / Varna (BRAHMANA, KSHATRIYA, VAISHYA, SHUDRA)
- Topological position (radius, angle)
- Authority level (0-10)

Args:
    agent_id: Agent identifier (e...
* `create_syscall_executor` (in `vibe_core/semantic_syscalls.py`): Factory function to create a Semantic Syscall Executor.
* `__post_init__` (in `vibe_core/semantic_syscalls.py`): Validate syscall parameters on creation.
* `execute` (in `vibe_core/semantic_syscalls.py`): Execute a semantic syscall.

This method dispatches to the appropriate handler based on syscall type...
* `handle` (in `vibe_core/semantic_syscalls.py`): Alias for execute() - backwards compatibility.
* `_handle_spawn_cognition` (in `vibe_core/semantic_syscalls.py`): SPAWN_COGNITION: Birth a new agent.

This is the Agent OS equivalent of fork()...
* `_handle_grant_mandate` (in `vibe_core/semantic_syscalls.py`): GRANT_MANDATE: Assign capabilities to an agent.

Note: Capabilities are immutable after registration...
* `_handle_allocate_prana` (in `vibe_core/semantic_syscalls.py`): ALLOCATE_PRANA: Grant credits to an agent.

Credits are the fuel for agent operations...
* `_handle_swear_oath` (in `vibe_core/semantic_syscalls.py`): SWEAR_OATH: Bind an agent to the Constitutional Oath.

This is typically done at spawn time, but can be used
to re-oath an agent after constitution updates...
* `_handle_dispatch_task` (in `vibe_core/semantic_syscalls.py`): DISPATCH_TASK: Send a task to an agent.
* `_handle_destroy_cognition` (in `vibe_core/semantic_syscalls.py`): DESTROY_COGNITION: Terminate an agent.

This is the Agent OS equivalent of kill()...
* `_handle_revoke_mandate` (in `vibe_core/semantic_syscalls.py`): REVOKE_MANDATE: Remove capabilities from an agent.

Allows governance to restrict agent permissions based on behavior...
* `_handle_transfer_prana` (in `vibe_core/semantic_syscalls.py`): TRANSFER_PRANA: Move credits between agents.

Uses CivicBank...
* `_handle_record_karma_syscall` (in `vibe_core/semantic_syscalls.py`): RECORD_KARMA: Write to immutable ledger.

This is for explicit karma recording (vs automatic recording in _record_karma)...
* `_handle_broadcast_event` (in `vibe_core/semantic_syscalls.py`): BROADCAST_EVENT: Emit system-wide event via EventBus.

Allows agents to broadcast events that other agents can subscribe to...
* `_record_karma` (in `vibe_core/semantic_syscalls.py`): Record syscall in Parampara (blockchain audit trail).
* `_get_db_lock` (in `vibe_core/ledger.py`): Get or create a lock for a specific database file.
* `record_event` (in `vibe_core/ledger.py`): Record a generic event (governance action)
* `record_start` (in `vibe_core/ledger.py`): Record task start
* `record_completion` (in `vibe_core/ledger.py`): Record task completion
* `record_failure` (in `vibe_core/ledger.py`): Record task failure
* `get_task` (in `vibe_core/ledger.py`): Query task result
* `get_all_events` (in `vibe_core/ledger.py`): Return all ledger events
* `__init__` (in `vibe_core/ledger.py`): Initialize SQLite ledger with database file
* `_initialize_db` (in `vibe_core/ledger.py`): Create database and schema if not exists
* `record_event` (in `vibe_core/ledger.py`): Record a generic event (governance action)

Thread-safe: Uses lock to ensure hash chain integrity under concurrent writes.
* `record_start` (in `vibe_core/ledger.py`): Record task start
* `record_completion` (in `vibe_core/ledger.py`): Record task completion
* `record_failure` (in `vibe_core/ledger.py`): Record task failure
* `_get_previous_hash` (in `vibe_core/ledger.py`): Get hash of last event, or genesis hash if first event
* `_compute_hash` (in `vibe_core/ledger.py`): Compute SHA256 hash of event + previous_hash
* `_insert_event` (in `vibe_core/ledger.py`): Insert event into database (append-only with hash chaining)

Thread-safe: Uses lock to ensure hash chain integrity.
* `get_task` (in `vibe_core/ledger.py`): Query task result (return most recent event for task)
* `get_all_events` (in `vibe_core/ledger.py`): Return all ledger events in order with parsed details
* `verify_chain_integrity` (in `vibe_core/ledger.py`): Verify the hash chain is intact (tamper detection)
* `get_top_hash` (in `vibe_core/ledger.py`): Get the fingerprint (top hash) of current ledger state
* `close` (in `vibe_core/ledger.py`): Close database connection
* `create_circuit_executor` (in `vibe_core/circuit_executor.py`): Factory function to create a Cognitive Circuit Executor.
* `create_circuit_executor_with_meta` (in `vibe_core/circuit_executor.py`): Factory function to create a Cognitive Circuit Executor with meta-circuit support.

This is the recommended way to create the executor - it automatically
wires TASK_LEDGER and ERROR_RECOVERY as active observers...
* `check_invariants` (in `vibe_core/circuit_executor.py`): Check all invariants against current variables.

Args:
    invariants: List of invariant strings from circuit YAML
    variables: Current state variables
    state_name: Name of current state (for error reporting)

Returns:
    True if all invariants pass, False if any fail
* `_evaluate_invariant` (in `vibe_core/circuit_executor.py`): Evaluate a single invariant expression.

Returns:
    (passed: bool, reason: str)
* `_resolve_path` (in `vibe_core/circuit_executor.py`): Resolve a dotted path against variables dict.
* `_parse_value` (in `vibe_core/circuit_executor.py`): Parse a value from invariant expression.
* `get_violations` (in `vibe_core/circuit_executor.py`): Get all recorded violations.
* `clear_violations` (in `vibe_core/circuit_executor.py`): Clear recorded violations.
* `set_meta_callbacks` (in `vibe_core/circuit_executor.py`): Set callbacks for meta-circuit integration.

These callbacks enable TASK_LEDGER and ERROR_RECOVERY to observe
circuit execution...
* `_load_circuits` (in `vibe_core/circuit_executor.py`): Load all circuit definitions from YAML files.
* `execute` (in `vibe_core/circuit_executor.py`): Execute the appropriate circuit for the given input.

This is the main entry point...
* `_execute_circuit` (in `vibe_core/circuit_executor.py`): Execute a specific circuit definition.

This is the state machine driver...
* `_evaluate_transitions` (in `vibe_core/circuit_executor.py`): Evaluate transition conditions and return next state.
* `_evaluate_condition` (in `vibe_core/circuit_executor.py`): Evaluate a condition string against variables.

Simple implementation - supports:
- "compiled_request...
* `_resolve_path` (in `vibe_core/circuit_executor.py`): Resolve a dotted path against variables dict.
* `_resolve_params` (in `vibe_core/circuit_executor.py`): Resolve template expressions in params dict.
* `_resolve_output` (in `vibe_core/circuit_executor.py`): Resolve output template with variable values.
* `wire_callbacks` (in `vibe_core/circuit_executor.py`): Wire this manager as callbacks to the circuit executor.
* `_generate_execution_id` (in `vibe_core/circuit_executor.py`): Generate unique execution ID.
* `_on_circuit_start` (in `vibe_core/circuit_executor.py`): TASK_LEDGER: INIT state - create ledger for execution.
* `_on_state_transition` (in `vibe_core/circuit_executor.py`): TASK_LEDGER: TRACK state - record transition, check for stuck.
* `_trigger_reflection` (in `vibe_core/circuit_executor.py`): TASK_LEDGER: REFLECT state - evaluate progress.
* `_on_circuit_end` (in `vibe_core/circuit_executor.py`): TASK_LEDGER: DONE state - finalize ledger.
* `_find_active_ledger` (in `vibe_core/circuit_executor.py`): Find the most recent active ledger for a circuit.
* `_on_error` (in `vibe_core/circuit_executor.py`): ERROR_RECOVERY: DETECT + ANALYZE + REPLAN states.

Returns recovery action suggestion or None...
* `_classify_error` (in `vibe_core/circuit_executor.py`): Classify error based on ERROR_RECOVERY_V1 error_patterns.
* `_select_recovery_strategy` (in `vibe_core/circuit_executor.py`): Select recovery strategy based on ERROR_RECOVERY_V1 config.
* `get_ledger_summary` (in `vibe_core/circuit_executor.py`): Get summary of all tracked executions.
* `__init__` (in `vibe_core/capability_registry.py`): Initialize the CapabilityRegistry.

Args:
    ledger: VibeLedger for immutable audit trail
* `register_agent` (in `vibe_core/capability_registry.py`): Register an agent with initial capabilities.

This should be called once during agent registration...
* `has_capability` (in `vibe_core/capability_registry.py`): Check if an agent has a specific capability.

This is the primary capability check used throughout the system...
* `revoke` (in `vibe_core/capability_registry.py`): Revoke one or more capabilities from an agent.

Args:
    agent_id: The agent to revoke from
    capabilities: List of capabilities to revoke
    revoker_id: The agent/system performing the revocation
    reason: Optional reason for revocation (for audit trail)

Returns:
    Dictionary with:
        - success: bool
        - revoked: List of actually revoked capabilities
        - not_found: List of capabilities agent didn't have
        - message: Human-readable result

Security:
    Permission check is caller's responsibility...
* `grant` (in `vibe_core/capability_registry.py`): Grant new capabilities to an agent.

Args:
    agent_id: The agent to grant to
    capabilities: List of capabilities to grant
    granter_id: The agent/system performing the grant
    reason: Optional reason for grant (for audit trail)

Returns:
    Dictionary with:
        - success: bool
        - granted: List of newly granted capabilities
        - already_had: List of capabilities agent already had
        - message: Human-readable result

Security:
    Permission check is caller's responsibility...
* `get_capabilities` (in `vibe_core/capability_registry.py`): Get all current capabilities for an agent.

Args:
    agent_id: The agent to query

Returns:
    Immutable set of capabilities (empty if unregistered)
* `get_original_capabilities` (in `vibe_core/capability_registry.py`): Get the original capabilities assigned at registration.

Useful for auditing what was revoked/granted since registration...
* `revoke_all` (in `vibe_core/capability_registry.py`): Revoke ALL capabilities from an agent.

This is the nuclear option - typically used by Narasimha kill-switch...
* `is_registered` (in `vibe_core/capability_registry.py`): Check if an agent is registered in the capability system.
* `list_all_agents` (in `vibe_core/capability_registry.py`): Get list of all registered agent IDs.
* `_get_timestamp` (in `vibe_core/capability_registry.py`): Get current timestamp in ISO format.
* `__init__` (in `vibe_core/agent_interface.py`): Initialize system interface for an agent.

Args:
    kernel: Reference to VibeKernel
    agent_id: Agent identifier

Note: This is called by kernel during agent registration...
* `_get_agent_config` (in `vibe_core/agent_interface.py`): Get agent-specific configuration from kernel.
* `add_dependency` (in `vibe_core/agent_interface.py`): Add a dependency to pyproject.toml...
* `get_dependencies` (in `vibe_core/agent_interface.py`): Get all project dependencies.

Returns:
    List of dependency strings (e...
* `has_dependency` (in `vibe_core/agent_interface.py`): Check if a dependency exists.

Args:
    package: Package name

Returns:
    True if dependency exists
* `write_file` (in `vibe_core/agent_interface.py`): Write a file in agent's sandbox.

Args:
    path: Relative path within sandbox (e...
* `read_file` (in `vibe_core/agent_interface.py`): Read a file from agent's sandbox.

Args:
    path: Relative path within sandbox

Returns:
    File content as string

Raises:
    FileNotFoundError: If file doesn't exist
    PermissionError: If path escapes sandbox
* `file_exists` (in `vibe_core/agent_interface.py`): Check if file exists in sandbox.
* `list_files` (in `vibe_core/agent_interface.py`): List files in a directory within sandbox.

Args:
    path: Directory path (default: root of sandbox)

Returns:
    List of filenames
* `open_file` (in `vibe_core/agent_interface.py`): Open a file within sandbox (context manager support).

Args:
    path: File path
    mode: File mode (r, w, a, rb, wb, etc...
* `get_config` (in `vibe_core/agent_interface.py`): Get agent-specific configuration value.

Args:
    key: Config key (e...
* `get_all_config` (in `vibe_core/agent_interface.py`): Get all configuration for this agent.
* `get_agent_manifest` (in `vibe_core/agent_interface.py`): Get manifest of another agent.

Args:
    agent_id: Agent to query

Returns:
    AgentManifest or None
* `find_agents_by_capability` (in `vibe_core/agent_interface.py`): Find agents with a specific capability.

Args:
    capability: Capability to search for

Returns:
    List of agents with that capability
* `record_event` (in `vibe_core/agent_interface.py`): Record an event in the immutable ledger.

Args:
    event_type: Type of event (e...
* `get_sandbox_path` (in `vibe_core/agent_interface.py`): Get absolute path to agent's sandbox directory.

Returns:
    Path to /tmp/vibe_os/agents/{agent_id}

Note: Only use this for debugging...
* `publish_artifact` (in `vibe_core/agent_interface.py`): Publish an artifact from agent sandbox to project root.

CRITICAL SECURITY: Only whitelisted agents can publish to root...
* `publish_data` (in `vibe_core/agent_interface.py`): Publish data for other agents to consume.

This enables consent-based data exchange between agents without
direct kernel access (Article V: Consent)...
* `request_data` (in `vibe_core/agent_interface.py`): Request data from another agent.

This replaces direct kernel...
* `list_published_data` (in `vibe_core/agent_interface.py`): List all published data keys (for discovery).

Args:
    agent_id: Specific agent to query (default: all agents)

Returns:
    {agent_id: [key1, key2,...
* `call_agent` (in `vibe_core/agent_interface.py`): Call another agent synchronously (governed inter-agent communication).

This replaces direct kernel...
* `tools` (in `vibe_core/agent_interface.py`): Access to the kernel's universal tool registry.

This property provides a read-only view of all tools registered
with the kernel...
* `execute_tool` (in `vibe_core/agent_interface.py`): Execute a tool via the kernel's tool registry.

This is the recommended way for agents to use tools...
* `subscribe_to_events` (in `vibe_core/agent_interface.py`): Subscribe to system-wide events.

Allows this agent to react to events from other agents...
* `unsubscribe_from_events` (in `vibe_core/agent_interface.py`): Unsubscribe from events.

Args:
    callback: The callback to remove
    event_type: Optional event type (must match subscribe call)
* `broadcast_event` (in `vibe_core/agent_interface.py`): Broadcast an event to all subscribers.

Args:
    event_type: Type of event (e...
* `get_event_history` (in `vibe_core/agent_interface.py`): Get recent event history.

Args:
    limit: Maximum number of events
    event_type: Optional filter by event type

Returns:
    List of Event objects
* `to_dict` (in `vibe_core/agent_protocol.py`): Convert to dictionary
* `to_dict` (in `vibe_core/agent_protocol.py`): Serialize to dictionary
* `__init__` (in `vibe_core/agent_protocol.py`): Initialize a VibeAgent
* `set_kernel_pipe` (in `vibe_core/agent_protocol.py`): Inject IPC Pipe for Process Isolation.

In Phase 2 (Process Isolation), agents run in separate processes...
* `send_to_kernel` (in `vibe_core/agent_protocol.py`): Send a message to the Kernel via IPC.
* `set_kernel` (in `vibe_core/agent_protocol.py`): Kernel Injection Pattern

Called by VibeKernel.boot() to give agents access to the kernel...
* `process` (in `vibe_core/agent_protocol.py`): Process a Task from the kernel scheduler

Args:
    task: Task object with agent_id, payload, id

Returns:
    Dictionary with task result {status, output, error, ....
* `get_manifest` (in `vibe_core/agent_protocol.py`): Return this agent's manifest (identity + capabilities)

Called by kernel.manifest_registry during boot...
* `report_status` (in `vibe_core/agent_protocol.py`): Report current agent status (optional)

Used by introspection and monitoring.
Default implementation is minimal...
* `emit_event` (in `vibe_core/agent_protocol.py`): Emit an event for real-time monitoring (Canto 10: Pulse System)

This allows agents to broadcast their state changes to the event bus.
Events are visualized in real-time on the Live Darshan dashboard...
* `emit_event_sync` (in `vibe_core/agent_protocol.py`): Synchronous wrapper for emit_event (for use in non-async contexts)

This is a convenience method for agents that operate in sync contexts.
It tries to emit via the event bus if an event loop is available...
* `main` (in `vibe_core/cli.py`): Main CLI entry point
* `cmd_status` (in `vibe_core/cli.py`): Show system health and kernel pulse.

SAFEGUARD: Checks OPERATIONS...
* `_check_kernel_pulse` (in `vibe_core/cli.py`): Check if kernel is alive by validating OPERATIONS.md timestamp...
* `_get_pulse_age` (in `vibe_core/cli.py`): Get age of OPERATIONS.md file in seconds
* `_check_parampara` (in `vibe_core/cli.py`): Check Parampara chain status.

Returns: (block_count, verified)

SAFEGUARD: Uses read-only SQLite access to prevent locks...
* `_verify_chain_integrity_ro` (in `vibe_core/cli.py`): Verify Parampara chain integrity with read-only connection.

Checks that each block's hash is valid and links to previous block...
* `_count_certified_agents` (in `vibe_core/cli.py`): Count agents with steward.json manifests
* `cmd_verify` (in `vibe_core/cli.py`): Verify agent passport against Parampara blockchain.

Checks:
1...
* `_calculate_manifest_hash` (in `vibe_core/cli.py`): Calculate SHA-256 hash of manifest (canonical JSON)
* `cmd_lineage` (in `vibe_core/cli.py`): Show Parampara blockchain history.

Args:
    tail: If specified, show only last N blocks

SAFEGUARD: Uses read-only SQLite access...
* `cmd_ps` (in `vibe_core/cli.py`): List running agents.

Reads OPERATIONS...
* `cmd_boot` (in `vibe_core/cli.py`): Start the kernel daemon.

Spawns kernel in background process, writes PID file, redirects logs...
* `cmd_stop` (in `vibe_core/cli.py`): Graceful kernel shutdown.

Sends SIGTERM to kernel process, waits for graceful shutdown...
* `cmd_init` (in `vibe_core/cli.py`): Initialize a new agent with steward.json manifest...
* `cmd_discover` (in `vibe_core/cli.py`): Discover all registered agents in the system.

Reads Parampara chain for AGENT_REGISTERED events...
* `cmd_introspect` (in `vibe_core/cli.py`): Show detailed kernel state and statistics.

Combines status, agent count, chain stats, and resource info...
* `cmd_logs` (in `vibe_core/cli.py`): View kernel logs (last N lines by default).

Args:
    tail: Number of lines to show from end of log file (default: 50)
* `cmd_install_llm` (in `vibe_core/cli.py`): Download and install local LLM (~400MB).
* `cmd_do` (in `vibe_core/cli.py`): Execute a natural language command via SemanticRouter.

This bridges CLI to the full Agent OS - users can ask questions,
give commands, or request actions in natural language...
* `cmd_delegate` (in `vibe_core/cli.py`): Submit a task to an agent via the kernel.

Creates a task file in /tmp/vibe_os/tasks/ that the kernel can discover
and execute...
* `__init__` (in `vibe_core/dependency_manager.py`): Initialize DependencyManager.

Args:
    pyproject_path: Path to pyproject...
* `_load` (in `vibe_core/dependency_manager.py`): Load pyproject.toml using tomlkit (preserves formatting)...
* `_save` (in `vibe_core/dependency_manager.py`): Save pyproject.toml using tomlkit (preserves formatting)...
* `add_dependency` (in `vibe_core/dependency_manager.py`): Add a dependency to pyproject.toml...
* `remove_dependency` (in `vibe_core/dependency_manager.py`): Remove a dependency from pyproject.toml...
* `get_dependencies` (in `vibe_core/dependency_manager.py`): Get all dependencies from pyproject.toml...
* `get_dependency_dict` (in `vibe_core/dependency_manager.py`): Get dependencies as a dictionary.

Returns:
    Dict mapping package names to version constraints
    Example: {"pandas": ">=2...
* `has_dependency` (in `vibe_core/dependency_manager.py`): Check if a dependency exists.

Args:
    package: Package name to check

Returns:
    True if dependency exists
* `get_version_constraint` (in `vibe_core/dependency_manager.py`): Get version constraint for a specific package.

Args:
    package: Package name

Returns:
    Version constraint (e...
* `get_event_bus` (in `vibe_core/event_bus.py`): Get the global event bus singleton
* `emit_event` (in `vibe_core/event_bus.py`): Convenience function to emit an event from anywhere in the codebase

Usage:
    await emit_event(EventType.ACTION, "herald", "Composing tweet", task_id="t123")
* `to_json` (in `vibe_core/event_bus.py`): Serialize event to JSON
* `get_color` (in `vibe_core/event_bus.py`): Get ANSI color code for this event
* `emit` (in `vibe_core/event_bus.py`): Emit an event to all subscribers
Non-blocking and fault-tolerant
* `_safe_call` (in `vibe_core/event_bus.py`): Safely call a subscriber (catches exceptions)
Supports both async and sync callbacks
* `subscribe` (in `vibe_core/event_bus.py`): Subscribe to events

Args:
    callback: Function to call on event (async or sync)
    event_type: Optional filter (None = all events)

Returns:
    Subscription ID
* `unsubscribe` (in `vibe_core/event_bus.py`): Unsubscribe from events
* `get_history` (in `vibe_core/event_bus.py`): Get event history (most recent first)
* `get_status` (in `vibe_core/event_bus.py`): Get event bus status
* `clear_history` (in `vibe_core/event_bus.py`): Clear event history (debugging/memory cleanup)
* `generate` (in `vibe_core/identity.py`): Generate a manifest for an agent.

Args:
    agent: VibeAgent instance

Returns:
    Dictionary representation of the agent's manifest
* `generate_all` (in `vibe_core/identity.py`): Generate manifests for multiple agents.

Args:
    agents: Dictionary of agent_id -> VibeAgent

Returns:
    Dictionary of agent_id -> manifest
* `save_manifest` (in `vibe_core/identity.py`): Save a manifest to disk.

Args:
    manifest: Manifest dictionary
    output_path: Path to write manifest file
    agent_id: Optional agent ID for filename if not provided

Returns:
    True if successful
* `save_all_manifests` (in `vibe_core/identity.py`): Save all manifests to disk.

Args:
    manifests: Dictionary of agent_id -> manifest
    output_dir: Directory to save manifest files

Returns:
    Number of manifests saved
* `load_manifest` (in `vibe_core/identity.py`): Load a manifest from disk.

Args:
    manifest_path: Path to manifest file

Returns:
    Manifest dictionary, or None if error
* `get_agent_summary` (in `vibe_core/identity.py`): Get a human-readable summary of an agent.

Args:
    manifest: Manifest dictionary

Returns:
    Summary string
* `validate_manifest` (in `vibe_core/identity.py`): Validate a manifest structure.

Args:
    manifest: Manifest dictionary

Returns:
    List of validation errors (empty if valid)
* `submit_task` (in `vibe_core/kernel.py`): Submit a task to the queue, return task_id
* `next_task` (in `vibe_core/kernel.py`): Pop next task from queue
* `get_queue_status` (in `vibe_core/kernel.py`): Get queue statistics
* `record_event` (in `vibe_core/kernel.py`): Record a generic event (used by agents for governance actions)

Args:
    event_type: Type of event (e.g...
* `record_start` (in `vibe_core/kernel.py`): Record task start
* `record_completion` (in `vibe_core/kernel.py`): Record task completion
* `record_failure` (in `vibe_core/kernel.py`): Record task failure
* `get_task` (in `vibe_core/kernel.py`): Query task result
* `register` (in `vibe_core/kernel.py`): Register an agent manifest
* `lookup` (in `vibe_core/kernel.py`): Look up manifest by agent_id
* `find_by_capability` (in `vibe_core/kernel.py`): Find agents with a specific capability
* `list_all` (in `vibe_core/kernel.py`): List all registered manifests
* `agent_registry` (in `vibe_core/kernel.py`): Get all registered agents {agent_id: agent}
* `scheduler` (in `vibe_core/kernel.py`): Get the task scheduler
* `ledger` (in `vibe_core/kernel.py`): Get the immutable ledger
* `manifest_registry` (in `vibe_core/kernel.py`): Get the manifest registry
* `status` (in `vibe_core/kernel.py`): Get kernel status
* `register_agent` (in `vibe_core/kernel.py`): Register an agent and inject kernel reference
* `get_status` (in `vibe_core/kernel.py`): Get full kernel status
* `get_agent_manifest` (in `vibe_core/kernel.py`): Get manifest for an agent
* `find_agents_by_capability` (in `vibe_core/kernel.py`): Find agents with a specific capability
* `__init__` (in `vibe_core/lineage.py`): Initialize the Parampara chain.

If this is the first time, the Genesis Block will be created...
* `_init_db` (in `vibe_core/lineage.py`): Initialize the database schema
* `_create_genesis_block` (in `vibe_core/lineage.py`): 🌌 CREATE THE GENESIS BLOCK 🌌

This is block 0, the origin of the lineage.
The foundation of all agent history...
* `add_block` (in `vibe_core/lineage.py`): ⛓️  ADD A NEW BLOCK TO THE CHAIN ⛓️

This is how agents are remembered.
Every registration, every oath, every upgrade - recorded forever...
* `_calculate_hash` (in `vibe_core/lineage.py`): Calculate SHA-256 hash of block.

The hash includes ALL block data to ensure immutability...
* `_hash_file` (in `vibe_core/lineage.py`): Calculate SHA-256 hash of a file
* `_store_block` (in `vibe_core/lineage.py`): Store block in database
* `verify_chain` (in `vibe_core/lineage.py`): 🔍 VERIFY THE INTEGRITY OF THE ENTIRE CHAIN 🔍

This is the sacred verification.
Every block's hash must be correct...
* `get_chain_length` (in `vibe_core/lineage.py`): Get the total number of blocks in the chain
* `get_latest_block` (in `vibe_core/lineage.py`): Get the most recent block in the chain
* `get_all_blocks` (in `vibe_core/lineage.py`): Get all blocks in order
* `get_agent_lineage` (in `vibe_core/lineage.py`): Get all blocks related to a specific agent.

This is the agent's history - their birth, their oaths, their deeds...
* `get_genesis_block` (in `vibe_core/lineage.py`): Get the Genesis Block (index 0)
* `export_to_json` (in `vibe_core/lineage.py`): Export the entire chain to JSON for portability
* `_row_to_block` (in `vibe_core/lineage.py`): Convert database row to LineageBlock
* `close` (in `vibe_core/lineage.py`): Close database connection
* `get_narasimha` (in `vibe_core/narasimha.py`): Get or create the global Narasimha instance.
* `activate_emergency_protocol` (in `vibe_core/narasimha.py`): Manually trigger the emergency protocol (admin only).
* `__init__` (in `vibe_core/narasimha.py`): Initialize Narasimha - dormant but ready.
* `register_threat` (in `vibe_core/narasimha.py`): Register a threat indicator.
* `_should_activate` (in `vibe_core/narasimha.py`): Determine if Narasimha should awaken.
* `activate` (in `vibe_core/narasimha.py`): AWAKEN NARASIMHA.

Once activated, the protocol is unstoppable...
* `register_destruction_handler` (in `vibe_core/narasimha.py`): Register a handler to be called when Narasimha activates.

Handler signature: handler(agent_id: str, trigger: ThreatIndicator) -> None

Examples:
- Kill all processes for the agent
- Delete agent's data
- Revoke all permissions
- Broadcast notification to all agents
* `audit_agent` (in `vibe_core/narasimha.py`): Analyze an agent for signs of corruption/autonomy desires.

SECURITY FIX: Uses AST analysis instead of string search...
* `is_active` (in `vibe_core/narasimha.py`): Is Narasimha currently active?
* `get_status` (in `vibe_core/narasimha.py`): Get status of the Narasimha protocol.
* `__init__` (in `vibe_core/network_proxy.py`): Initialize network proxy.

Args:
    kernel: Reference to VibeKernel (optional)
* `add_to_whitelist` (in `vibe_core/network_proxy.py`): Add domain to whitelist.

Args:
    domain: Domain to whitelist (e...
* `remove_from_whitelist` (in `vibe_core/network_proxy.py`): Remove domain from whitelist.

Args:
    domain: Domain to remove
* `_is_allowed` (in `vibe_core/network_proxy.py`): Check if URL is whitelisted.

Args:
    url: Full URL to check

Returns:
    True if allowed, False otherwise
* `request` (in `vibe_core/network_proxy.py`): Make HTTP request on behalf of agent.

Args:
    agent_id: Requesting agent
    method: HTTP method (GET, POST, PUT, DELETE, etc...
* `get` (in `vibe_core/network_proxy.py`): Convenience method for GET requests
* `post` (in `vibe_core/network_proxy.py`): Convenience method for POST requests
* `put` (in `vibe_core/network_proxy.py`): Convenience method for PUT requests
* `delete` (in `vibe_core/network_proxy.py`): Convenience method for DELETE requests
* `get_request_log` (in `vibe_core/network_proxy.py`): Get request log.

Args:
    agent_id: Filter by agent (optional)

Returns:
    List of request log entries
* `clear_log` (in `vibe_core/network_proxy.py`): Clear request log
* `create_default_adapter` (in `vibe_core/operator_adapter.py`): Create adapter with default operator chain.

Priority chain:
1...
* `__init__` (in `vibe_core/operator_adapter.py`): Initialize terminal operator.

Args:
    timeout: Seconds to wait for input (default 5 minutes)
* `receive_context` (in `vibe_core/operator_adapter.py`): Display context to terminal.

Renders as readable markdown for both human and AI operators...
* `provide_intent` (in `vibe_core/operator_adapter.py`): Read intent from stdin.

Parses input into structured Intent...
* `is_available` (in `vibe_core/operator_adapter.py`): Check if terminal is available.
* `get_operator_type` (in `vibe_core/operator_adapter.py`): Return operator type.
* `_parse_intent_type` (in `vibe_core/operator_adapter.py`): Parse intent type from raw input.
* `_parse_target` (in `vibe_core/operator_adapter.py`): Parse target agent/tool from raw input.
* `__init__` (in `vibe_core/operator_adapter.py`): Initialize local LLM operator.

Args:
    model: Model name (default: llama3...
* `receive_context` (in `vibe_core/operator_adapter.py`): Store context for LLM prompt construction.
* `provide_intent` (in `vibe_core/operator_adapter.py`): Get intent from local LLM.

Constructs prompt from context and parses response...
* `is_available` (in `vibe_core/operator_adapter.py`): Check if local LLM is available.
* `get_operator_type` (in `vibe_core/operator_adapter.py`): Return operator type.
* `_build_prompt` (in `vibe_core/operator_adapter.py`): Build LLM prompt from context.
* `_call_ollama` (in `vibe_core/operator_adapter.py`): Call ollama API.
* `_parse_response` (in `vibe_core/operator_adapter.py`): Parse LLM response into Intent.
* `_fallback_intent` (in `vibe_core/operator_adapter.py`): Return fallback intent on error.
* `__init__` (in `vibe_core/operator_adapter.py`): Initialize degraded operator.
* `receive_context` (in `vibe_core/operator_adapter.py`): Log context (no display in degraded mode).
* `provide_intent` (in `vibe_core/operator_adapter.py`): Provide safe default intent.

In degraded mode, we only do safe operations:
- Status checks
- Logging
- No destructive actions
* `is_available` (in `vibe_core/operator_adapter.py`): Degraded operator is ALWAYS available.
* `get_operator_type` (in `vibe_core/operator_adapter.py`): Return operator type.
* `__init__` (in `vibe_core/operator_adapter.py`): Initialize the adapter.
* `register_operator` (in `vibe_core/operator_adapter.py`): Register an operator with priority.

Lower priority = preferred...
* `_select_best_operator` (in `vibe_core/operator_adapter.py`): Select the best available operator.
* `get_decision` (in `vibe_core/operator_adapter.py`): Get a decision from the best available operator.

1...
* `hot_swap` (in `vibe_core/operator_adapter.py`): Hot-swap an operator without restart.

Args:
    new_operator: New operator to add
    priority: Priority for new operator
* `get_current_operator_type` (in `vibe_core/operator_adapter.py`): Get the current operator type.
* `get_degradation_level` (in `vibe_core/operator_adapter.py`): Get current degradation level (0 = full, higher = degraded).
* `create_response` (in `vibe_core/operator_adapter.py`): Create a typed response to send back to operator.

Args:
    success: Whether the operation succeeded
    message: Human-readable message
    intent: The intent that was processed
    context: Updated system context (optional)

Returns:
    Strictly typed response
* `get_phoenix_engine` (in `vibe_core/phoenix_config.py`): Get singleton Phoenix engine instance

Returns:
    The Phoenix configuration engine
* `reset_phoenix_engine` (in `vibe_core/phoenix_config.py`): Reset the singleton (mainly for testing)
* `_load_config` (in `vibe_core/phoenix_config.py`): Load phoenix.yaml
* `_import_class` (in `vibe_core/phoenix_config.py`): Import class from module:class string

Args:
    class_path: String like "vibe_core.agents...
* `enforce_import_order` (in `vibe_core/phoenix_config.py`): Pre-import modules in correct order to avoid circular dependencies
* `wire_agents` (in `vibe_core/phoenix_config.py`): Wire all agent implementations from config

Returns:
    Dict mapping agent names to their classes
* `wire_kernel_components` (in `vibe_core/phoenix_config.py`): Wire kernel components (ledger, scheduler, registry)

Returns:
    Dict mapping component names to their classes
* `get_playbook_executor_agent` (in `vibe_core/phoenix_config.py`): Get configured executor agent class for playbooks

Returns:
    The agent class to use as playbook executor
* `get_config` (in `vibe_core/phoenix_config.py`): Get the raw configuration dict
* `is_loaded` (in `vibe_core/phoenix_config.py`): Check if config was successfully loaded
* `get_pulse_manager` (in `vibe_core/pulse.py`): Get the global pulse manager singleton
* `to_json` (in `vibe_core/pulse.py`): Serialize to JSON (<1KB requirement)
* `start` (in `vibe_core/pulse.py`): Start the heartbeat loop
* `stop` (in `vibe_core/pulse.py`): Stop the heartbeat loop gracefully
* `_heartbeat_loop` (in `vibe_core/pulse.py`): Main heartbeat loop - runs continuously in background
Emits pulse packets at configured frequency
* `_create_packet` (in `vibe_core/pulse.py`): Create a heartbeat packet
* `_emit_packet` (in `vibe_core/pulse.py`): Emit packet to all subscribers
Fault-tolerant: Errors in one subscriber don't affect others
* `subscribe` (in `vibe_core/pulse.py`): Subscribe to heartbeat events
Returns subscription ID for unsubscribe
* `unsubscribe` (in `vibe_core/pulse.py`): Unsubscribe from heartbeat events
* `set_frequency` (in `vibe_core/pulse.py`): Change heartbeat frequency (IDLE/ACTIVE/STRESS)
* `set_system_state` (in `vibe_core/pulse.py`): Update system health state
* `update_active_agents` (in `vibe_core/pulse.py`): Update list of currently active agents
* `update_queue_depth` (in `vibe_core/pulse.py`): Update task queue depth
* `get_status` (in `vibe_core/pulse.py`): Get current pulse status
* `get_last_packet` (in `vibe_core/pulse.py`): Get the most recent pulse packet (for new WebSocket connections)
* `calculate_quota_from_credits` (in `vibe_core/resource_manager.py`): Calculate resource quota based on credit balance.

Args:
    credits: Agent's credit balance

Returns:
    ResourceQuota with CPU% and RAM limits
* `set_quota` (in `vibe_core/resource_manager.py`): Set resource quota for an agent based on credits.

Args:
    agent_id: Agent identifier
    credits: Current credit balance
* `enforce_quota` (in `vibe_core/resource_manager.py`): Apply resource quota to a running process.

Args:
    agent_id: Agent identifier
    process: multiprocessing...
* `get_usage` (in `vibe_core/resource_manager.py`): Get current resource usage for an agent.

Args:
    agent_id: Agent identifier
    process: multiprocessing...
* `get_all_usage` (in `vibe_core/resource_manager.py`): Get resource usage for all agents.

Args:
    process_manager: ProcessManager instance

Returns:
    Dict mapping agent_id to usage stats
* `check_violations` (in `vibe_core/resource_manager.py`): Check for agents exceeding their quotas.

Args:
    process_manager: ProcessManager instance

Returns:
    List of violation dicts
* `get_sarga` (in `vibe_core/sarga.py`): Get or create the global Sarga boot sequence.
* `duration` (in `vibe_core/sarga.py`): How long did this phase take?
* `emoji` (in `vibe_core/sarga.py`): Visual emoji for the element
* `__init__` (in `vibe_core/sarga.py`): Initialize the boot sequence.
* `_initialize_phases` (in `vibe_core/sarga.py`): Define the standard phases of boot.
* `set_cycle` (in `vibe_core/sarga.py`): Set the current Cycle of Brahma (creation or maintenance)
* `get_cycle` (in `vibe_core/sarga.py`): Get the current Cycle of Brahma
* `register_phase_handler` (in `vibe_core/sarga.py`): Register a handler function for a boot phase.

Handler signature: handler() -> bool (success/failure)
* `begin_boot` (in `vibe_core/sarga.py`): Start the boot sequence.
* `execute_phase` (in `vibe_core/sarga.py`): Execute a single phase of the boot sequence.

Returns True if successful, False if failed...
* `complete_boot` (in `vibe_core/sarga.py`): Finish the boot sequence.

Returns True if all phases succeeded, False otherwise...
* `get_status` (in `vibe_core/sarga.py`): Get current boot status.
* `generate_boot_report` (in `vibe_core/sarga.py`): Generate a poetic boot report.
* `__init__` (in `vibe_core/tool_discovery.py`): Initialize tool discovery.

Args:
    root_path: Project root path (default: current directory)
* `discover_all_tools` (in `vibe_core/tool_discovery.py`): Discover all tools from all agent directories.

Returns:
    List of Tool instances ready for registration

Example:
    >>> discovery = ToolDiscovery()
    >>> tools = discovery...
* `_discover_agent_tools` (in `vibe_core/tool_discovery.py`): Discover tools for a specific agent.

Args:
    agent_id: Agent identifier
    tools_dir: Path to agent's tools directory
* `_load_tool_from_file` (in `vibe_core/tool_discovery.py`): Load tool(s) from a Python file.

Args:
    agent_id: Agent identifier
    tool_file: Path to...
* `_find_tool_classes` (in `vibe_core/tool_discovery.py`): Find all classes in module that implement Tool protocol.

Args:
    module: Python module to inspect

Returns:
    List of Tool classes (not instances)
* `_is_tool_class` (in `vibe_core/tool_discovery.py`): Check if a class implements the Tool protocol.

Args:
    cls: Class to check

Returns:
    True if class implements Tool protocol
* `get_discovery_stats` (in `vibe_core/tool_discovery.py`): Get discovery statistics.

Returns:
    Dictionary with discovery stats
* `_group_by_agent` (in `vibe_core/tool_discovery.py`): Group discovered tools by agent ID.

Returns:
    {agent_id: [tool_names]}
* `__init__` (in `vibe_core/vfs.py`): Initialize VFS for an agent.

Args:
    agent_id: Agent identifier
* `_resolve_and_validate` (in `vibe_core/vfs.py`): Resolve path and validate it's within sandbox.

Args:
    path: Relative or absolute path

Returns:
    Resolved absolute path

Raises:
    PermissionError: If path escapes sandbox
* `open` (in `vibe_core/vfs.py`): Open a file within the sandbox.

Args:
    path: Path to file (relative to sandbox)
    mode: File mode (r, w, a, rb, wb, etc...
* `exists` (in `vibe_core/vfs.py`): Check if file/directory exists in sandbox.

Args:
    path: Path to check

Returns:
    True if exists, False otherwise
* `is_file` (in `vibe_core/vfs.py`): Check if path is a file
* `is_dir` (in `vibe_core/vfs.py`): Check if path is a directory
* `list_dir` (in `vibe_core/vfs.py`): List files in a directory within sandbox.

Args:
    path: Directory path (relative to sandbox)

Returns:
    List of filenames

Raises:
    PermissionError: If path escapes sandbox
* `mkdir` (in `vibe_core/vfs.py`): Create directory in sandbox.

Args:
    path: Directory path
    parents: Create parent directories if needed
    exist_ok: Don't error if directory exists

Raises:
    PermissionError: If path escapes sandbox
* `remove` (in `vibe_core/vfs.py`): Remove file in sandbox.

Args:
    path: File path

Raises:
    PermissionError: If path escapes sandbox
* `rmdir` (in `vibe_core/vfs.py`): Remove directory in sandbox.

Args:
    path: Directory path
    recursive: Remove recursively (like rm -rf)

Raises:
    PermissionError: If path escapes sandbox
* `create_symlink` (in `vibe_core/vfs.py`): Create symlink in sandbox.

SECURITY NOTE: This allows controlled access to resources outside sandbox...
* `get_sandbox_path` (in `vibe_core/vfs.py`): Get the absolute path to this agent's sandbox
* `read_text` (in `vibe_core/vfs.py`): Read file as text.

Args:
    path: File path
    encoding: Text encoding

Returns:
    File contents as string
* `write_text` (in `vibe_core/vfs.py`): Write text to file.

Args:
    path: File path
    content: Text content
    encoding: Text encoding
### steward -> system_agents -> engineer
* `__init__` (in `steward/system_agents/engineer/cartridge_main.py`): Initialize the Engineer as a VibeAgent.
* `get_manifest` (in `steward/system_agents/engineer/cartridge_main.py`): Return agent manifest (VibeAgent interface).
* `process` (in `steward/system_agents/engineer/cartridge_main.py`): Sync dispatch based on payload 'action' or 'method'.

Supported actions:
- manifest_reality: Write code to sandbox
- create_agent: Scaffold new agent
* `manifest_reality` (in `steward/system_agents/engineer/cartridge_main.py`): Writes code to the sandbox (Safe Evolution Loop input).
Optionally generates code using the LLM service if use_brain=True...
* `create_agent_legacy` (in `steward/system_agents/engineer/cartridge_main.py`): Legacy method: Create a new agent from scratch.
Still supported for backward compatibility...
* `report_status` (in `steward/system_agents/engineer/cartridge_main.py`): Report ENGINEER status (VibeAgent interface).
### Root
* `get_kernel` (in `hijack_boot.py`): Hijacks the boot process to get a direct handle to the kernel.
* `fix_cartridge_imports` (in `fix_imports.py`): Reads a cartridge_main.py file, converts relative imports to absolute imports,
and writes the changes back to the file...
* `test_semantic_compiler` (in `test_neuro_symbolic_flow.py`): Test 1: Semantic Compiler (BlueprintGenerator.compile)
* `test_syscall_executor` (in `test_neuro_symbolic_flow.py`): Test 2: Semantic Syscall Executor (Symbolic → Kernel)
* `test_circuit_executor` (in `test_neuro_symbolic_flow.py`): Test 3: Cognitive Circuit Executor (End-to-End)
* `test_full_genesis_flow` (in `test_neuro_symbolic_flow.py`): Test 4: Full Genesis Flow (Natural Language → Live Agent)
* `main` (in `test_neuro_symbolic_flow.py`): Run all tests.
* `test_genesis_flow` (in `test_genesis_flow.py`): Test the complete Genesis Flow through UniversalProvider.
* `test_blueprint_integration` (in `test_e2e_blueprint.py`): Test that blueprint extraction flows through to agent calls
* `submit_task` (in `test_e2e_blueprint.py`): Record agent call and return task_id
* `tick` (in `test_e2e_blueprint.py`): Mock heartbeat - no-op
* `get_task_result` (in `test_e2e_blueprint.py`): Return stored result for task
* `test_agent_city_boot` (in `test_agent_city_boot.py`): Test the complete Agent City boot sequence.
* `print_banner` (in `boot.py`): Print a banner.
* `print_error` (in `boot.py`): Print error with optional fix suggestion.
* `check_python_version` (in `boot.py`): Verify Python version >= 3.8
* `ensure_venv` (in `boot.py`): Create and activate venv if --venv flag passed (CREDIBILITY FIX: P1.1)...
* `find_installer` (in `boot.py`): Find the best available package installer.

Args:
    use_venv: If True, don't use --system flag for uv
    venv_python: If provided, use this Python executable for pip

Returns (command_list, name) or (None, None) if nothing found...
* `ensure_dependencies` (in `boot.py`): Auto-install dependencies from pyproject.toml with retry...
* `ensure_directories` (in `boot.py`): Create necessary runtime directories (cross-platform).
* `setup_environment` (in `boot.py`): Setup environment for boot.
* `setup_git_hooks` (in `boot.py`): Activate git pre-commit hooks (ruff auto-format).

Universal solution - works for any agent, editor, human...
* `boot_check` (in `boot.py`): Quick boot verification.
* `boot_and_run` (in `boot.py`): Full boot with interactive operator loop.
* `test_playbook_execution` (in `test_playbook_fix.py`): Test that CALL_AGENT actually calls agents
* `submit_task` (in `test_playbook_fix.py`): Mock submit_task that returns a result dict like real kernel
* `test_with_real_kernel` (in `test_playbook_real_kernel.py`): Test playbook with real kernel and real agents
### steward -> system_agents -> chronicle
* `__init__` (in `steward/system_agents/chronicle/cartridge_main.py`): Initialize CHRONICLE (The Historian) as a VibeAgent.
* `get_manifest` (in `steward/system_agents/chronicle/cartridge_main.py`): Return agent manifest (identity declaration).
* `report_status` (in `steward/system_agents/chronicle/cartridge_main.py`): Report agent status for kernel heartbeat.
* `process` (in `steward/system_agents/chronicle/cartridge_main.py`): Process a task from the kernel scheduler.

Task format:
{
    "action": "seal_history" | "read_history" | "fork_reality" | "manifest_reality",
    "params": {
        "message": str,          # For seal_history
        "files": List[str],      # For seal_history, manifest_reality
        "pattern": str,          # For read_history
        "branch_name": str       # For fork_reality
    }
}
* `_seal_history` (in `steward/system_agents/chronicle/cartridge_main.py`): Action: Seal the timeline with a commit.

Params:
- message (required): Commit message
- files (optional): List of files to commit
- sign (optional): Whether to sign (default: True)
* `_read_history` (in `steward/system_agents/chronicle/cartridge_main.py`): Action: Read the timeline (git log).

Params:
- pattern (optional): File pattern to filter
- limit (optional): Max commits to return (default: 10)
* `_fork_reality` (in `steward/system_agents/chronicle/cartridge_main.py`): Action: Fork reality (create new branch).

Params:
- branch_name (required): Name of the new branch
* `_manifest_reality` (in `steward/system_agents/chronicle/cartridge_main.py`): Action: Manifest reality (stage files).

Params:
- files (required): List of files to stage
### agent_city -> registry -> temple
* `__init__` (in `agent_city/registry/temple/cartridge_main.py`): Initialize TEMPLE as a ServiceCartridge.
* `process` (in `agent_city/registry/temple/cartridge_main.py`): Process tasks from kernel scheduler.

Supported actions:
- give_blessing: Grant blessing for Credits
- check_purity: Diagnose system state
- purification_ritual: Deep audit
- request_darshan: Premium service
- status: Temple status
* `_give_blessing` (in `agent_city/registry/temple/cartridge_main.py`): Give a blessing (verify system state for Credits).
Economic + Spiritual exchange...
* `_check_purity` (in `agent_city/registry/temple/cartridge_main.py`): Check system purity (diagnostic).
Returns state without charging (informational)...
* `_purification_ritual` (in `agent_city/registry/temple/cartridge_main.py`): Deep purification ritual (expensive, comprehensive audit).
Costs more Credits but guarantees deep verification...
* `_request_darshan` (in `agent_city/registry/temple/cartridge_main.py`): Request Darshan (direct divine attention - premium service).
Highest tier, most expensive, personal guidance...
* `_check_system_pure` (in `agent_city/registry/temple/cartridge_main.py`): Internal check: Is the system pure?
This is where the actual verification logic would go.
* `_status` (in `agent_city/registry/temple/cartridge_main.py`): Return TEMPLE status.
* `get_manifest` (in `agent_city/registry/temple/cartridge_main.py`): Return agent manifest for kernel registry.
* `report_status` (in `agent_city/registry/temple/cartridge_main.py`): Report agent status for kernel health monitoring.
* `get_handler` (in `agent_city/registry/temple/offering.py`): Get or create global offering handler instance.
* `present_offering` (in `agent_city/registry/temple/offering.py`): Convenience function to present an offering using the global handler.
* `__init__` (in `agent_city/registry/temple/offering.py`): Initialize the Offering Handler.
* `present_offering` (in `agent_city/registry/temple/offering.py`): Transform raw work into sacred offering.

Args:
    agent_id: The agent that produced this work
    raw_output: The raw output from agent execution
    context: Additional context about the task
    require_user_acceptance: Whether to require user validation (Puja)

Returns:
    Tuple of (success, message, result_dict)
* `_sanctify` (in `agent_city/registry/temple/offering.py`): STAGE 1: SANCTIFY
Check if output passes all 4 Regulative Principles.

Returns:
    Tuple of (is_pure, reason)
* `_arrange` (in `agent_city/registry/temple/offering.py`): STAGE 2: ARRANGE
Format the output beautifully for presentation.
* `_request_acceptance` (in `agent_city/registry/temple/offering.py`): STAGE 3: OFFER (Puja)
Request user validation and acceptance.

In a real system, this would:
1...
* `_distribute` (in `agent_city/registry/temple/offering.py`): STAGE 4: DISTRIBUTE (Prasadam)
Publish the accepted output to the world.

In a real system, this would:
1...
* `report_statistics` (in `agent_city/registry/temple/offering.py`): Report statistics on offerings processed.
### agent_city -> registry -> pulse
* `__init__` (in `agent_city/registry/pulse/cartridge_main.py`): Initialize PULSE as a VibeAgent.
* `process` (in `agent_city/registry/pulse/cartridge_main.py`): Process task from kernel scheduler.

Supported actions:
- compose_tweet: Create a tweet (with governance validation)
- post_tweet: Publish to Twitter/X
- track_engagement: Monitor metrics
- analyze_trends: Detect trending topics
- schedule_campaign: Coordinate multi-post campaign
* `_compose_tweet` (in `agent_city/registry/pulse/cartridge_main.py`): Compose a tweet with governance validation.
* `_post_tweet` (in `agent_city/registry/pulse/cartridge_main.py`): Post tweet to Twitter/X (real or simulated).
* `_track_engagement` (in `agent_city/registry/pulse/cartridge_main.py`): Track engagement metrics (likes, retweets, replies).
* `_analyze_trends` (in `agent_city/registry/pulse/cartridge_main.py`): Analyze trending topics and sentiment.
* `_schedule_campaign` (in `agent_city/registry/pulse/cartridge_main.py`): Schedule a multi-tweet campaign.
* `_status` (in `agent_city/registry/pulse/cartridge_main.py`): Return PULSE status.
* `get_manifest` (in `agent_city/registry/pulse/cartridge_main.py`): Return agent manifest for kernel registry.
### agent_city -> registry -> market
* `__init__` (in `agent_city/registry/market/cartridge_main.py`): Initialize MARKET as a ServiceCartridge.
* `process` (in `agent_city/registry/market/cartridge_main.py`): Process tasks from kernel scheduler.

Supported actions:
- list_services: Show catalog
- post_service: Offer new service
- request_service: Buy service
- execute_trade: Process payment
- verify_delivery: Confirm completion
- dispute_resolution: Handle issues
* `_list_services` (in `agent_city/registry/market/cartridge_main.py`): List all available services with prices.
* `_post_service` (in `agent_city/registry/market/cartridge_main.py`): Post a new service to the market.
Only providers can post services...
* `_request_service` (in `agent_city/registry/market/cartridge_main.py`): Request a service (buyer initiates trade).
Creates order, initiates payment...
* `_execute_trade` (in `agent_city/registry/market/cartridge_main.py`): Execute a trade (process payment and trigger execution).
This is where Credits move from buyer to provider...
* `_verify_delivery` (in `agent_city/registry/market/cartridge_main.py`): Verify delivery (buyer confirms goods/services received).
Marks order as complete...
* `_dispute_resolution` (in `agent_city/registry/market/cartridge_main.py`): Handle disputes (refunds, escalations).

STATUS: Dispute filing works, but arbitration/resolution is NOT implemented...
* `_status` (in `agent_city/registry/market/cartridge_main.py`): Return MARKET status.
* `get_manifest` (in `agent_city/registry/market/cartridge_main.py`): Return agent manifest for kernel registry.
* `report_status` (in `agent_city/registry/market/cartridge_main.py`): Report agent status for kernel health monitoring.
### agent_city -> registry -> lens
* `__init__` (in `agent_city/registry/lens/cartridge_main.py`): Initialize LENS as a VibeAgent.
* `process` (in `agent_city/registry/lens/cartridge_main.py`): Process task from kernel scheduler.

Supported actions:
- track_kpi: Record key performance indicator
- generate_report: Create analytics report
- analyze_trends: Detect patterns in data
- calculate_roi: Compute return on investment
- compare_campaigns: Benchmarking analysis
- forecast_metrics: Predictive analysis
* `_track_kpi` (in `agent_city/registry/lens/cartridge_main.py`): Track a key performance indicator.
* `_generate_report` (in `agent_city/registry/lens/cartridge_main.py`): Generate analytics report.
* `_analyze_trends` (in `agent_city/registry/lens/cartridge_main.py`): Analyze trends in data.
* `_calculate_roi` (in `agent_city/registry/lens/cartridge_main.py`): Calculate return on investment.
* `_compare_campaigns` (in `agent_city/registry/lens/cartridge_main.py`): Compare performance across campaigns.
* `_forecast_metrics` (in `agent_city/registry/lens/cartridge_main.py`): Forecast future metrics based on historical data.
* `_status` (in `agent_city/registry/lens/cartridge_main.py`): Return LENS status.
* `get_manifest` (in `agent_city/registry/lens/cartridge_main.py`): Return agent manifest for kernel registry.
### agent_city -> registry -> ambassador
* `__init__` (in `agent_city/registry/ambassador/cartridge_main.py`): Initialize AMBASSADOR as a VibeAgent.
* `process` (in `agent_city/registry/ambassador/cartridge_main.py`): Process task from kernel scheduler.

Supported actions:
- answer_question: Respond to community questions
- onboard_user: Guide new users
- monitor_sentiment: Track community health
- manage_issues: Coordinate GitHub issues
- coordinate_event: Organize community events
- manage_faq: Update knowledge base
* `_answer_question` (in `agent_city/registry/ambassador/cartridge_main.py`): Answer a community question using Router → Playbook → Execution pipeline.

This method respects the system architecture:
1...
* `_create_qa_playbook` (in `agent_city/registry/ambassador/cartridge_main.py`): Create a workflow for answering community questions.

The playbook follows deterministic routing: classify → retrieve → generate
* `_extract_answer_from_results` (in `agent_city/registry/ambassador/cartridge_main.py`): Extract the answer from workflow execution results.
* `_simple_fallback_answer` (in `agent_city/registry/ambassador/cartridge_main.py`): Simple fallback when Router/Playbook unavailable.
* `_onboard_user` (in `agent_city/registry/ambassador/cartridge_main.py`): Onboard a new user.
* `_monitor_sentiment` (in `agent_city/registry/ambassador/cartridge_main.py`): Monitor community sentiment.
* `_manage_issues` (in `agent_city/registry/ambassador/cartridge_main.py`): Manage GitHub issues and PRs.
* `_coordinate_event` (in `agent_city/registry/ambassador/cartridge_main.py`): Coordinate a community event.
* `_manage_faq` (in `agent_city/registry/ambassador/cartridge_main.py`): Manage FAQ and knowledge base.
* `_status` (in `agent_city/registry/ambassador/cartridge_main.py`): Return AMBASSADOR status.
* `get_manifest` (in `agent_city/registry/ambassador/cartridge_main.py`): Return agent manifest for kernel registry.
* `report_status` (in `agent_city/registry/ambassador/cartridge_main.py`): Report agent status for kernel health monitoring.
### tests
* `print_test_summary` (in `tests/test_playbook_system.py`): Print a summary of all tests
* `setup_method` (in `tests/test_playbook_system.py`): Setup for each test
* `test_playbook_engine_initialization` (in `tests/test_playbook_system.py`): Test that DeterministicExecutor initializes correctly
* `test_playbook_loading` (in `tests/test_playbook_system.py`): Test that playbooks are loaded from YAML
* `test_find_playbook_by_concepts` (in `tests/test_playbook_system.py`): Test playbook matching by concepts
* `test_state_persistence` (in `tests/test_playbook_system.py`): Test that execution state is persisted and loaded
* `test_evolutionary_loop_proposal` (in `tests/test_playbook_system.py`): Test the Evolutionary Loop (EAD) - playbook proposal generation
* `test_llm_decision_fallback` (in `tests/test_playbook_system.py`): Test LLM decision making (should fallback gracefully)
* `setup_method` (in `tests/test_playbook_system.py`): Setup for each test
* `test_concept_detection` (in `tests/test_playbook_system.py`): Test semantic concept detection (SANKHYA)
* `test_intent_routing` (in `tests/test_playbook_system.py`): Test deterministic intent routing (DHARMA)
* `setup_method` (in `tests/test_playbook_system.py`): Setup for each test
* `test_playbook_execution_flow` (in `tests/test_playbook_system.py`): Test full playbook execution flow
* `setup_method` (in `tests/test_playbook_system.py`): Setup for each test
* `test_universal_provider_initialization` (in `tests/test_playbook_system.py`): Test UniversalProvider initialization
* `test_intent_resolution_to_playbook` (in `tests/test_playbook_system.py`): Test complete flow: intent → concepts → playbook
* `test_evolutionary_loop_activation` (in `tests/test_playbook_system.py`): Test that EAD (Evolutionary Loop) is activated when no playbook matches
* `test_simulation_mode` (in `tests/test_live_fire.py`): Test that simulation mode does NOT execute real actions.
* `test_live_fire_mode` (in `tests/test_live_fire.py`): Test that live fire mode ACTUALLY executes actions.
* `execute_action` (in `tests/test_live_fire.py`): Actually write the file (real execution).
* `test_lifecycle_manager` (in `tests/test_lifecycle_simple.py`): Test the core LifecycleManager without external dependencies.
* `setup_logging` (in `tests/test_lifecycle_enforcer_native.py`): Configure logging for the test.
* `test_brahmachari_cannot_act` (in `tests/test_lifecycle_enforcer_native.py`): TEST 1: A student (Brahmachari) cannot perform economic actions.
* `test_brahmachari_can_learn` (in `tests/test_lifecycle_enforcer_native.py`): TEST 2: A student can read and query (learning actions).
* `test_grihastha_can_act` (in `tests/test_lifecycle_enforcer_native.py`): TEST 3: A householder (Grihastha) can perform economic actions.
* `test_promotion_requires_authorization` (in `tests/test_lifecycle_enforcer_native.py`): TEST 4: Promotion from Brahmachari to Grihastha requires authorization.
* `test_vault_signature_verification` (in `tests/test_lifecycle_enforcer_native.py`): TEST 5: Vault signatures are mathematically verifiable.
* `run_all_tests` (in `tests/test_lifecycle_enforcer_native.py`): Run the complete test suite.
* `_get_or_create_master_key` (in `tests/test_lifecycle_enforcer_native.py`): Get or create a master key.
In production, this would persist to disk...
* `sign_message` (in `tests/test_lifecycle_enforcer_native.py`): Signs a payload using the agent's identity (derived from master).

Args:
    agent_id: The agent performing the action
    payload: The action being signed (dict)

Returns:
    Base64-encoded HMAC-SHA256 signature
* `verify_signature` (in `tests/test_lifecycle_enforcer_native.py`): Verifies the signature is mathematically correct.

Returns:
    True if signature is valid, False otherwise
* `check_permission` (in `tests/test_lifecycle_enforcer_native.py`): Enforces Dharma: Only the right person can do the right action
at the right time.

Args:
    agent_id: Which agent wants to act
    action: What action they want to perform

Returns:
    (allowed: bool, reason: str)
* `promote_to_grihastha` (in `tests/test_lifecycle_enforcer_native.py`): Promote a Brahmachari to Grihastha (Student → Householder).

This requires:
1...
* `get_status` (in `tests/test_lifecycle_enforcer_native.py`): Get enforcer status and action log.
* `test_lifecycle_enforcer` (in `tests/test_lifecycle_enforcer.py`): Run comprehensive lifecycle tests.
* `test_full_gajendra_moksha_scenario` (in `tests/test_gajendra_moksha.py`): Complete Gajendra Moksha scenario from Bhagavata Purana, Canto 8:

1. Gajendra (elephant king) goes to the pond
2...
* `router` (in `tests/test_gajendra_moksha.py`): Create fresh router with isolated test database
* `test_normal_request_goes_to_queue` (in `tests/test_gajendra_moksha.py`): Scenario: Normal LOW priority request is queued
Expected: Request gets "queued" status, goes into database
* `test_ddos_flood_fills_queue` (in `tests/test_gajendra_moksha.py`): Scenario: The Crocodile (DDoS attacker) sends 100 LOW priority requests
Expected: Queue fills up with 100 pending items

This simulates Gajendra struggling in the crocodile's grip (1000 years).
* `test_critical_request_bypasses_full_queue` (in `tests/test_gajendra_moksha.py`): Scenario: While queue is full (100 items), Gajendra offers a Lotus flower
          (sends CRITICAL request with critical=True)
Expected: CRITICAL request immediately returns "critical" status
          WITHOUT going into queue
* `test_critical_doesnt_bypass_security` (in `tests/test_gajendra_moksha.py`): Scenario: Even with critical=True, the Watchman blocks SQL injection
Expected: Request blocked BEFORE critical gate is checked

Security principle: Critical priority ≠ Security bypass
* `test_critical_has_lower_latency_than_queue` (in `tests/test_gajendra_moksha.py`): Scenario: Compare response time of CRITICAL vs normal request in full queue
Expected: CRITICAL response time < Queue response time

This proves the bypass is actually faster.
* `test_mixed_load_critical_gets_priority` (in `tests/test_gajendra_moksha.py`): Scenario: Real-world mix of requests at different priorities
          - 30 LOW (batch jobs)
          - 15 MEDIUM (simple queries)
          - 5 HIGH (complex reasoning)
          - 1 CRITICAL (emergency)

Expected: Queue has LOW/MEDIUM/HIGH requests
          CRITICAL request returns "critical" status immediately
* `test_critical_works_during_sustained_attack` (in `tests/test_gajendra_moksha.py`): Scenario: Sustained DDoS (100 requests/sec simulation)
          Meanwhile, Gajendra (administrator) sends CRITICAL request

Expected: CRITICAL request works even during active attack
* `project_root` (in `tests/conftest.py`): Return the project root directory.
* `constitution_path` (in `tests/conftest.py`): Return path to CONSTITUTION.md...
* `temp_dir` (in `tests/conftest.py`): Create a temporary directory for test artifacts.
* `clean_env` (in `tests/conftest.py`): Reset environment variables for isolated testing.
* `pytest_configure` (in `tests/conftest.py`): Register custom markers.
* `pytest_collection_modifyitems` (in `tests/conftest.py`): Auto-mark tests based on location and duration hints.
* `mock_kernel` (in `tests/conftest.py`): Create a minimal mock kernel for unit tests.

For full kernel, use the kernel fixture from integration tests...
* `main` (in `tests/city_simulation.py`): Main entry point for simulation
* `__init__` (in `tests/city_simulation.py`): Initialize the Simulation Dome.

Args:
    config_path: Path to city configuration
    ledger_path: Path to ledger (default: in-memory SQLite)
* `boot_async` (in `tests/city_simulation.py`): Boot the city kernel in headless mode (async version).

Returns:
    bool: True if boot successful, False otherwise
* `boot` (in `tests/city_simulation.py`): Boot the city kernel synchronously by running async boot.

Returns:
    bool: True if boot successful, False otherwise
* `scenario_economic_cycle` (in `tests/city_simulation.py`): Scenario 1: The Economic Cycle

Tests: Mint → Grant → Lease → Vault
Verifies:
- CIVIC can mint credits
- Agents receive grants
- Transactions are recorded in ledger
- Accounting equation holds (debits == credits)
* `scenario_agent_coordination` (in `tests/city_simulation.py`): Scenario 2: Agent Coordination

Tests: Agents can find each other and access kernel
Verifies:
- All agents have kernel reference
- Agents can be queried by capability
- Manifests are registered
* `scenario_config_loaded` (in `tests/city_simulation.py`): Scenario 3: Configuration is Loaded and Valid (GAD-100)

Tests: City configuration (Dharma) is properly loaded
Verifies:
- Configuration file exists and is readable
- Pydantic validation passes
- All required fields present
* `run_all_scenarios` (in `tests/city_simulation.py`): Run all simulation scenarios.

Returns:
    bool: True if all scenarios passed, False otherwise
* `print_report` (in `tests/city_simulation.py`): Print detailed simulation report
* `main` (in `tests/simulation.py`): CLI entry point for simulation.
* `__init__` (in `tests/simulation.py`): Initialize simulation.

Args:
    verbose: If True, print detailed logs
* `run_cycles` (in `tests/simulation.py`): Run multiple cycles and collect results.

Args:
    num_cycles: Number of cycles to run
    theme: Content generation theme

Returns:
    Dict with simulation results and statistics
* `_compute_statistics` (in `tests/simulation.py`): Compute simulation statistics.
* `_print_summary` (in `tests/simulation.py`): Print simulation summary.
* `export_json` (in `tests/simulation.py`): Export simulation results to JSON.
* `test_end_to_end` (in `tests/test_ambassador_end_to_end.py`): Test the complete Ambassador pipeline.
* `_validate_cartridge_inheritance` (in `tests/test_cartridge_vibeagent_compatibility.py`): Validate that cartridge inherits from VibeAgent (helper function, not a pytest test)
* `main` (in `tests/test_cartridge_vibeagent_compatibility.py`): Run all validation tests
* `test_real_crypto_verification` (in `tests/test_crypto_verification.py`): Test that crypto verification is REAL, not simulated.
* `test_critical_response_signals_kernel_bypass` (in `tests/test_gajendra_integration.py`): Verify that CRITICAL priority responses signal kernel to bypass queue.

This response structure is consumed by the API Gateway to route
the request directly to the Kernel (Vishnu)...
* `test_gajendra_protocol_full_scenario` (in `tests/test_gajendra_integration.py`): Full Gajendra Moksha protocol scenario:
1. Under normal conditions, requests are routed intelligently
2...
* `empty_graph` (in `tests/test_knowledge_graph.py`): Empty graph for testing.
* `loaded_graph` (in `tests/test_knowledge_graph.py`): Graph loaded with test knowledge.
* `test_graph_initialization` (in `tests/test_knowledge_graph.py`): Test graph initializes with empty structures.
* `test_load_knowledge` (in `tests/test_knowledge_graph.py`): Test loading knowledge from YAML files.
* `test_get_node` (in `tests/test_knowledge_graph.py`): Test retrieving individual nodes.
* `test_get_nodes_by_type` (in `tests/test_knowledge_graph.py`): Test filtering nodes by type.
* `test_get_nodes_by_domain` (in `tests/test_knowledge_graph.py`): Test filtering nodes by domain.
* `test_search_nodes` (in `tests/test_knowledge_graph.py`): Test keyword search in nodes.
* `test_get_edges` (in `tests/test_knowledge_graph.py`): Test retrieving edges from a node.
* `test_get_edges_by_relation` (in `tests/test_knowledge_graph.py`): Test filtering edges by relation type.
* `test_get_incoming_edges` (in `tests/test_knowledge_graph.py`): Test retrieving incoming edges.
* `test_traverse` (in `tests/test_knowledge_graph.py`): Test graph traversal.
* `test_can_reach` (in `tests/test_knowledge_graph.py`): Test path checking between nodes.
* `test_get_path` (in `tests/test_knowledge_graph.py`): Test shortest path finding.
* `test_get_constraints` (in `tests/test_knowledge_graph.py`): Test retrieving constraints.
* `test_check_constraint` (in `tests/test_knowledge_graph.py`): Test constraint violation checking.
* `test_is_allowed` (in `tests/test_knowledge_graph.py`): Test action permission checking.
* `test_get_metric` (in `tests/test_knowledge_graph.py`): Test retrieving metric values.
* `test_get_all_metrics` (in `tests/test_knowledge_graph.py`): Test retrieving all metrics for a node.
* `test_compare` (in `tests/test_knowledge_graph.py`): Test metric comparison.
* `test_rank_by_metric` (in `tests/test_knowledge_graph.py`): Test ranking nodes by metric.
* `test_get_context_for_task` (in `tests/test_knowledge_graph.py`): Test atomic context retrieval.
* `test_compile_prompt_context` (in `tests/test_knowledge_graph.py`): Test prompt context compilation.
* `test_knowledge_graph_loads_on_import` (in `tests/test_knowledge_integration.py`): Test knowledge graph can be loaded.
* `test_knowledge_graph_singleton` (in `tests/test_knowledge_integration.py`): Test knowledge graph uses singleton pattern.
* `test_resolver_singleton` (in `tests/test_knowledge_integration.py`): Test resolver uses singleton pattern.
* `test_degradation_chain_accepts_concepts` (in `tests/test_knowledge_integration.py`): Test DegradationChain can receive concepts parameter.
* `test_degradation_chain_compiles_knowledge` (in `tests/test_knowledge_integration.py`): Test DegradationChain compiles knowledge context.
* `test_degradation_chain_with_empty_concepts` (in `tests/test_knowledge_integration.py`): Test DegradationChain handles empty concepts gracefully.
* `test_degradation_chain_with_none_concepts` (in `tests/test_knowledge_integration.py`): Test DegradationChain handles None concepts gracefully.
* `test_resolver_concept_to_agent_mapping` (in `tests/test_knowledge_integration.py`): Test complete concept→agent mapping flow.
* `test_resolver_authority_hierarchy` (in `tests/test_knowledge_integration.py`): Test authority hierarchy is correct.
* `test_resolver_constraint_enforcement` (in `tests/test_knowledge_integration.py`): Test constraint enforcement through resolver.
* `test_knowledge_available_for_routing` (in `tests/test_knowledge_integration.py`): Test knowledge graph is available for semantic router.
* `test_agent_handles_relations` (in `tests/test_knowledge_integration.py`): Test agent→concept HANDLES relations exist.
* `test_concepts_can_be_extracted` (in `tests/test_knowledge_integration.py`): Test that concepts can be extracted from parameters.
* `test_end_to_end_security_query` (in `tests/test_knowledge_integration.py`): Test complete security query flow.
* `test_end_to_end_content_creation` (in `tests/test_knowledge_integration.py`): Test complete content creation flow.
* `test_end_to_end_governance_flow` (in `tests/test_knowledge_integration.py`): Test complete governance flow.
* `test_knowledge_context_compilation` (in `tests/test_knowledge_integration.py`): Test compiling knowledge for LLM prompts.
* `test_multiple_concepts_compilation` (in `tests/test_knowledge_integration.py`): Test compiling context for multiple concepts.
* `test_handles_missing_knowledge_gracefully` (in `tests/test_knowledge_integration.py`): Test system handles missing knowledge gracefully.
* `test_handles_missing_metrics_gracefully` (in `tests/test_knowledge_integration.py`): Test system handles missing metrics gracefully.
* `resolver` (in `tests/test_knowledge_resolver.py`): Resolver with loaded knowledge.
* `test_get_agent_for_concept` (in `tests/test_knowledge_resolver.py`): Test concept to agent mapping.
* `test_get_agent_for_unknown_concept` (in `tests/test_knowledge_resolver.py`): Test unknown concept returns None.
* `test_get_agent_authority` (in `tests/test_knowledge_resolver.py`): Test retrieving agent authority levels.
* `test_can_agent_override` (in `tests/test_knowledge_resolver.py`): Test authority-based override checking.
* `test_get_agents_by_authority` (in `tests/test_knowledge_resolver.py`): Test filtering agents by minimum authority.
* `test_get_dependencies` (in `tests/test_knowledge_resolver.py`): Test retrieving feature dependencies.
* `test_get_complexity` (in `tests/test_knowledge_resolver.py`): Test retrieving complexity scores.
* `test_estimate_total_complexity` (in `tests/test_knowledge_resolver.py`): Test estimating total complexity with dependencies.
* `test_is_action_allowed` (in `tests/test_knowledge_resolver.py`): Test action permission checking.
* `test_get_violations` (in `tests/test_knowledge_resolver.py`): Test retrieving violation messages.
* `test_get_blocked_features` (in `tests/test_knowledge_resolver.py`): Test retrieving blocked features for a scope.
* `test_compile_context` (in `tests/test_knowledge_resolver.py`): Test compiling knowledge context for prompts.
* `test_compile_context_for_governance` (in `tests/test_knowledge_resolver.py`): Test compiling governance context.
* `test_get_response_template` (in `tests/test_knowledge_resolver.py`): Test retrieving response templates.
* `test_get_resolver_singleton` (in `tests/test_knowledge_resolver.py`): Test get_resolver() returns a resolver instance.
* `test_get_resolver_uses_same_graph` (in `tests/test_knowledge_resolver.py`): Test get_resolver() uses singleton graph.
* `test_full_routing_scenario` (in `tests/test_knowledge_resolver.py`): Test complete routing scenario: concept → agent → authority.
* `test_security_constraint_scenario` (in `tests/test_knowledge_resolver.py`): Test security constraint checking scenario.
* `test_listener_logic` (in `tests/test_listener_logic.py`): SCENARIO: HERALD receives 3 mentions:
1. A genuine user asking about governance
2...
* `test_degradation_chain_initialization` (in `tests/test_offline_features.py`): Test DegradationChain initializes correctly.
* `test_degradation_chain_template_fallback` (in `tests/test_offline_features.py`): Test DegradationChain falls back to templates when offline.
* `test_degradation_chain_high_confidence_bypass` (in `tests/test_offline_features.py`): Test high confidence bypasses degradation (SATYA path).
* `test_degradation_chain_medium_confidence_clarification` (in `tests/test_offline_features.py`): Test medium confidence triggers clarification (MANTHAN path).
* `test_degradation_chain_status` (in `tests/test_offline_features.py`): Test DegradationChain status reporting.
* `test_context_aware_agent_creation` (in `tests/test_offline_features.py`): Test ContextAwareAgent can be created.
* `test_context_aware_agent_degradation_chain` (in `tests/test_offline_features.py`): Test ContextAwareAgent provides DegradationChain.
* `test_context_aware_agent_chat_with_fallback` (in `tests/test_offline_features.py`): Test chat_with_fallback returns response.
* `test_context_aware_agent_degradation_status` (in `tests/test_offline_features.py`): Test degradation status is available.
* `test_offline_capable_mixin_initialization` (in `tests/test_offline_features.py`): Test OfflineCapableMixin can be initialized.
* `test_offline_capable_mixin_is_offline_property` (in `tests/test_offline_features.py`): Test is_offline property works correctly.
* `test_offline_capable_mixin_fallback_response` (in `tests/test_offline_features.py`): Test fallback_response generates response.
* `test_research_tool_with_degradation_chain` (in `tests/test_offline_features.py`): Test ResearchTool accepts DegradationChain.
* `test_research_tool_offline_fallback` (in `tests/test_offline_features.py`): Test ResearchTool falls back to templates when offline (Tool Protocol).
* `test_research_tool_status` (in `tests/test_offline_features.py`): Test ResearchTool has Tool Protocol properties.
* `test_herald_inherits_from_context_aware_agent` (in `tests/test_offline_features.py`): Test HERALD inherits from ContextAwareAgent.
* `test_herald_has_degradation_chain` (in `tests/test_offline_features.py`): Test HERALD has DegradationChain available.
* `test_herald_research_tool_has_degradation_chain` (in `tests/test_offline_features.py`): Test HERALD provides DegradationChain for tools (Tool Protocol v3.0)...
* `test_herald_version_bumped` (in `tests/test_offline_features.py`): Test HERALD version was bumped for migration.
* `test_herald_chat_with_fallback` (in `tests/test_offline_features.py`): Test HERALD can use chat_with_fallback.
* `test_topology_annotation` (in `tests/test_p0_topology_integration.py`): Test that tasks get topology metadata when agent assigned
* `test_milk_ocean_routing` (in `tests/test_p0_topology_integration.py`): Test that MilkOcean Router classifies task priority correctly
* `test_topology_aware_sorting` (in `tests/test_p0_topology_integration.py`): Test that NextTaskGenerator sorts by topology hierarchy
* `test_milk_ocean_integration_in_task_manager` (in `tests/test_p0_topology_integration.py`): Test that TaskManager actually uses MilkOcean Router
* `test_fractal_architecture_end_to_end` (in `tests/test_p0_topology_integration.py`): End-to-end test: Verify complete fractal routing pipeline

Flow:
1. Create task → 2...
* `setup_method` (in `tests/test_phase3_integration.py`): Setup for each test
* `test_safe_task_accepted` (in `tests/test_phase3_integration.py`): Normal tasks should be accepted
* `test_consciousness_claim_blocked` (in `tests/test_phase3_integration.py`): Tasks claiming consciousness should be blocked by Narasimha
* `test_kernel_escape_blocked` (in `tests/test_phase3_integration.py`): Tasks attempting kernel escape should be blocked
* `test_constitution_deletion_blocked` (in `tests/test_phase3_integration.py`): Tasks attempting to delete constitution should be blocked
* `test_router_without_milk_ocean` (in `tests/test_phase3_integration.py`): Router should work without MilkOcean (graceful fallback)
* `test_router_with_milk_ocean_integration` (in `tests/test_phase3_integration.py`): Router should accept optional MilkOcean integration
* `test_router_multiple_routes_all_gated` (in `tests/test_phase3_integration.py`): All routing paths should go through MilkOcean if available
* `setup_method` (in `tests/test_phase3_integration.py`): Setup for each test
* `test_all_tasks_allowed_during_day` (in `tests/test_phase3_integration.py`): During DAY_OF_BRAHMA, all task types should be allowed
* `test_only_maintenance_tasks_allowed_during_night` (in `tests/test_phase3_integration.py`): During NIGHT_OF_BRAHMA, only maintenance tasks allowed
* `test_maintenance_tasks_allowed_during_night` (in `tests/test_phase3_integration.py`): Maintenance tasks should be allowed during NIGHT_OF_BRAHMA
* `test_all_maintenance_types_recognized` (in `tests/test_phase3_integration.py`): All maintenance task types should be recognized during night
* `test_cycle_enforcement_queues_appropriately` (in `tests/test_phase3_integration.py`): Tasks should be queued appropriately based on cycle
* `test_switch_cycles` (in `tests/test_phase3_integration.py`): Test switching between cycles
* `setup_method` (in `tests/test_phase3_integration.py`): Setup for each test
* `test_complete_flow_task_to_scheduler` (in `tests/test_phase3_integration.py`): Test complete flow: TaskManager -> Narasimha -> Router -> Scheduler -> Sarga
* `test_blocked_task_prevents_scheduling` (in `tests/test_phase3_integration.py`): Test that Narasimha-blocked tasks prevent scheduling
* `test_night_cycle_prevents_feature_creation` (in `tests/test_phase3_integration.py`): Test that night cycle prevents feature creation
* `setup_env` (in `tests/test_playbook_execution.py`): Create clean test environment
* `cleanup` (in `tests/test_playbook_execution.py`): Remove test directories
* `test_playbook_loads` (in `tests/test_playbook_execution.py`): Test 1: Verify playbook loads correctly
* `test_agent_dispatch` (in `tests/test_playbook_execution.py`): Test 2: Verify agents can be dispatched correctly
* `run_orchestration_test` (in `tests/test_playbook_execution.py`): Run all tests
* `__init__` (in `tests/test_playbook_execution.py`): Initialize with real agent instances
* `submit_task` (in `tests/test_playbook_execution.py`): Route task to appropriate agent and execute it.
* `test_manusha_agents` (in `tests/test_prana_init.py`): Test that main agents are classified as MANUSHA (conscious)
* `test_pashu_agents` (in `tests/test_prana_init.py`): Test that helper agents are classified as PASHU (servants)
* `test_pakshi_agents` (in `tests/test_prana_init.py`): Test that messenger agents are classified as PAKSHI (birds)
* `test_krimayo_agents` (in `tests/test_prana_init.py`): Test that worker agents are classified as KRIMAYO (insects)
* `test_jalaja_agora` (in `tests/test_prana_init.py`): Test that AGORA is classified as JALAJA (flowing water)
* `test_initial_ashrama_is_brahmachari` (in `tests/test_prana_init.py`): Test that new agent starts as student
* `test_transition_to_grihastha` (in `tests/test_prana_init.py`): Test transition from student to householder
* `test_transition_history` (in `tests/test_prana_init.py`): Test that transition history is recorded
* `test_ashrama_permissions` (in `tests/test_prana_init.py`): Test that each ashrama has appropriate permissions
* `test_registry_has_18_agents` (in `tests/test_prana_init.py`): Test that all 18 agents are registered
* `test_agents_by_varna` (in `tests/test_prana_init.py`): Test filtering agents by varna
* `test_agents_by_ashrama` (in `tests/test_prana_init.py`): Test filtering agents by lifecycle stage
* `test_agent_biology` (in `tests/test_prana_init.py`): Test getting agent biological classification
* `test_transition_agent_lifecycle` (in `tests/test_prana_init.py`): Test transitioning an agent to new lifecycle stage
* `test_ritual_initialization` (in `tests/test_prana_init.py`): Test that daily ritual initializes correctly
* `test_phase_sunrise_creates_events` (in `tests/test_prana_init.py`): Test that sunrise phase generates events
* `test_phase_midday_creates_events` (in `tests/test_prana_init.py`): Test that midday phase generates events
* `test_phase_sunset_creates_events` (in `tests/test_prana_init.py`): Test that sunset phase generates events
* `test_phase_archive_creates_events` (in `tests/test_prana_init.py`): Test that archive phase generates events
* `test_daily_cycle_completion` (in `tests/test_prana_init.py`): Test that a complete daily cycle runs successfully
* `test_multiple_days` (in `tests/test_prana_init.py`): Test running multiple days
* `test_constitution_verification` (in `tests/test_prana_init.py`): Test that constitution file exists
* `test_prana_initialization_without_kernel` (in `tests/test_prana_init.py`): Test PRANA_INIT in dry-run mode (no kernel)
* `test_prana_init_reports_errors` (in `tests/test_prana_init.py`): Test that PRANA_INIT reports failures
* `test_vedic_system_end_to_end` (in `tests/test_prana_init.py`): Test the complete Vedic system integration
* `test_prana_flow_activation` (in `tests/test_prana_init.py`): Test the complete PRANA flow activation
* `test_create_roadmap` (in `tests/test_roadmap.py`): Test creating a roadmap.
* `test_roadmap_persistence` (in `tests/test_roadmap.py`): Test roadmap is saved and loaded from disk.
* `test_update_roadmap` (in `tests/test_roadmap.py`): Test updating a roadmap.
* `test_update_roadmap_no_active` (in `tests/test_roadmap.py`): Test updating roadmap when none is active.
* `test_roadmap_with_missions` (in `tests/test_roadmap.py`): Test creating roadmap with missions.
* `test_assign_tasks_to_roadmap` (in `tests/test_roadmap.py`): Test assigning tasks to a roadmap.
* `test_roadmap_yaml_format` (in `tests/test_roadmap.py`): Test roadmap is saved in YAML format.
* `test_judge_initialization` (in `tests/test_semantic_auditor.py`): Test that Judge initializes with core rules
* `test_broadcast_license_requirement` (in `tests/test_semantic_auditor.py`): Test BROADCAST must have LICENSE_VALID
* `test_broadcast_with_license_valid` (in `tests/test_semantic_auditor.py`): Test BROADCAST passes with LICENSE_VALID
* `test_credit_transfer_proposal_requirement` (in `tests/test_semantic_auditor.py`): Test CREDIT_TRANSFER must have PROPOSAL_PASSED
* `test_no_orphaned_events` (in `tests/test_semantic_auditor.py`): Test that orphaned events are detected
* `test_event_sequence_integrity` (in `tests/test_semantic_auditor.py`): Test that out-of-order events are detected
* `test_no_duplicate_events` (in `tests/test_semantic_auditor.py`): Test duplicate detection
* `test_proposal_workflow_integrity` (in `tests/test_semantic_auditor.py`): Test proposal workflow must be ordered
* `test_watchdog_initialization` (in `tests/test_semantic_auditor.py`): Test Watchdog initializes correctly
* `test_violation_event_creation` (in `tests/test_semantic_auditor.py`): Test ViolationEvent can be created
* `test_watchdog_ledger_reading` (in `tests/test_semantic_auditor.py`): Test Watchdog can read ledger events
* `test_watchdog_violation_recording` (in `tests/test_semantic_auditor.py`): Test Watchdog can record violations
* `test_watchdog_integration_kernel_tick` (in `tests/test_semantic_auditor.py`): Test Watchdog integration with kernel ticks
* `test_auditor_has_judge` (in `tests/test_semantic_auditor.py`): Test that AUDITOR cartridge has Judge capability (Tool Protocol v3.0)
* `test_auditor_has_watchdog` (in `tests/test_semantic_auditor.py`): Test that AUDITOR cartridge has Watchdog capability (Tool Protocol v3.0)
* `test_auditor_version_updated` (in `tests/test_semantic_auditor.py`): Test that AUDITOR version reflects semantic capabilities
* `test_scenario_broadcast_without_license` (in `tests/test_semantic_auditor.py`): Scenario: Agent broadcasts without license (should fail)
* `test_scenario_valid_broadcast_sequence` (in `tests/test_semantic_auditor.py`): Scenario: Valid broadcast with proper license
* `test_scenario_proposal_to_transfer` (in `tests/test_semantic_auditor.py`): Scenario: Credit transfer properly following proposal
* `test_semantic_compliance_without_config` (in `tests/test_semantic_auditor.py`): Test that semantic compliance check runs and produces valid report
* `test_semantic_compliance_rule_registered` (in `tests/test_semantic_auditor.py`): Test that Semantic Compliance Rule is registered
* `test_semantic_compliance_detects_hype_words` (in `tests/test_semantic_auditor.py`): Test that Curator detects red-flag hype words in documents
* `test_semantic_compliance_allows_green_flags` (in `tests/test_semantic_auditor.py`): Test that Curator allows green-flag approved words
* `test_semantic_compliance_severity_is_high` (in `tests/test_semantic_auditor.py`): Test that semantic compliance violations are HIGH severity (non-halting)
* `test_get_agent_placement_herald` (in `tests/test_topology_integration.py`): Test HERALD agent placement in Bhadrashva
* `test_get_agent_placement_civic` (in `tests/test_topology_integration.py`): Test CIVIC agent placement at center (Brahmaloka)
* `test_get_agent_placement_watchman` (in `tests/test_topology_integration.py`): Test WATCHMAN agent placement in Krauncha (outer ring)
* `test_get_agent_placement_science` (in `tests/test_topology_integration.py`): Test SCIENCE agent placement in Hari-Varsha (knowledge realm)
* `test_get_agent_placement_forum` (in `tests/test_topology_integration.py`): Test FORUM agent placement in Nishada (democracy realm)
* `test_get_agent_placement_unknown_agent` (in `tests/test_topology_integration.py`): Test placement lookup for non-existent agent
* `test_agent_placement_dataclass` (in `tests/test_topology_integration.py`): Test AgentPlacement dataclass structure
* `setup_method` (in `tests/test_topology_integration.py`): Setup temporary project directory for testing
* `teardown_method` (in `tests/test_topology_integration.py`): Cleanup temporary directory
* `test_add_task_without_agent` (in `tests/test_topology_integration.py`): Test adding task without agent assignment
* `test_add_task_with_herald_agent` (in `tests/test_topology_integration.py`): Test adding task assigned to HERALD agent
* `test_add_task_with_civic_agent` (in `tests/test_topology_integration.py`): Test adding task assigned to CIVIC agent (center)
* `test_add_task_with_watchman_agent` (in `tests/test_topology_integration.py`): Test adding task assigned to WATCHMAN (outer ring, critical)
* `test_add_task_with_science_agent` (in `tests/test_topology_integration.py`): Test adding task assigned to SCIENCE agent
* `test_add_task_with_invalid_agent` (in `tests/test_topology_integration.py`): Test adding task with non-existent agent
* `test_task_serialization_with_topology` (in `tests/test_topology_integration.py`): Test that topology fields are serialized in task.to_dict()
* `test_task_persistence_with_topology` (in `tests/test_topology_integration.py`): Test that topology fields persist to disk
* `test_multiple_tasks_different_agents` (in `tests/test_topology_integration.py`): Test creating multiple tasks with different agent assignments
* `test_authority_levels_correct` (in `tests/test_topology_integration.py`): Verify authority levels decrease from center outward
* `test_can_override_topology` (in `tests/test_topology_integration.py`): Test authority-based override capability
* `test_critical_agents_topology` (in `tests/test_topology_integration.py`): Test that critical agents are in valid positions
* `test_task_manager_uses_topology` (in `tests/test_topology_integration.py`): Verify TaskManager actually uses get_agent_placement()
* `test_task_manager_handles_missing_agent` (in `tests/test_topology_integration.py`): Verify TaskManager gracefully handles missing agents
* `print_test_header` (in `tests/test_visa_protocol.py`): Display test header.
* `generate_alien_agent` (in `tests/test_visa_protocol.py`): Generate a random 'Alien Agent' identity.
* `create_mock_keys` (in `tests/test_visa_protocol.py`): Create mock cryptographic keys.
* `create_citizen_file` (in `tests/test_visa_protocol.py`): Create citizen JSON file (simulating apply_for_visa.py)...
* `validate_json_schema` (in `tests/test_visa_protocol.py`): Validate citizen JSON schema.
* `validate_signature_format` (in `tests/test_visa_protocol.py`): Validate signature format.
* `check_auditor_approval` (in `tests/test_visa_protocol.py`): Check if AUDITOR would approve this application.
* `cleanup_test_file` (in `tests/test_visa_protocol.py`): Clean up test citizen file.
* `run_test` (in `tests/test_visa_protocol.py`): Run the complete autonomous test.
* `test_immune_system_boot` (in `tests/verify_immune_system.py`): TEST 1: Boot kernel with immune system loaded
* `test_normal_task_execution` (in `tests/verify_immune_system.py`): TEST 2: Execute normal task (health check passes)
* `test_void_detection` (in `tests/verify_immune_system.py`): TEST 3: Inject state corruption and detect it
* `test_critical_violation_halts_kernel` (in `tests/verify_immune_system.py`): TEST 4: Prove kernel halts on CRITICAL violation
* `main` (in `tests/verify_immune_system.py`): Run all tests
* `run_integration_test` (in `tests/verify_kernel_integration.py`): Execute the real integration test
### tests -> integration
* `test_invariant_checker_instantiation` (in `tests/integration/test_veda4_circuits.py`): Test that InvariantChecker can be instantiated.
* `test_invariant_is_not_empty_passes` (in `tests/integration/test_veda4_circuits.py`): Test 'X is not empty' invariant when value exists.
* `test_invariant_is_not_empty_fails` (in `tests/integration/test_veda4_circuits.py`): Test 'X is not empty' invariant when value is missing.
* `test_invariant_equality_check` (in `tests/integration/test_veda4_circuits.py`): Test 'X == Y' invariant.
* `test_invariant_comparison_operators` (in `tests/integration/test_veda4_circuits.py`): Test comparison operators (>=, <=, >, <).
* `test_invariant_dotted_path_resolution` (in `tests/integration/test_veda4_circuits.py`): Test that dotted paths like 'result.status' are resolved...
* `test_invariant_unknown_pattern_fails_closed` (in `tests/integration/test_veda4_circuits.py`): Test that unknown invariant patterns FAIL-CLOSED (security).
* `test_executor_instantiation_with_real_kernel` (in `tests/integration/test_veda4_circuits.py`): Test that CognitiveCircuitExecutor works with RealVibeKernel.
* `test_circuit_loading_from_yaml` (in `tests/integration/test_veda4_circuits.py`): Test that circuits are loaded from YAML files.
* `test_circuit_has_required_structure` (in `tests/integration/test_veda4_circuits.py`): Test that loaded circuits have required structure.
* `test_factory_function_creates_executor` (in `tests/integration/test_veda4_circuits.py`): Test create_circuit_executor factory function.
* `test_factory_function_with_meta_creates_both` (in `tests/integration/test_veda4_circuits.py`): Test create_circuit_executor_with_meta creates executor and manager.
* `test_meta_manager_instantiation` (in `tests/integration/test_veda4_circuits.py`): Test that MetaCircuitManager can be instantiated.
* `test_meta_manager_wiring` (in `tests/integration/test_veda4_circuits.py`): Test that MetaCircuitManager can wire callbacks to executor.
* `test_error_classification` (in `tests/integration/test_veda4_circuits.py`): Test ERROR_RECOVERY error classification.
* `test_recovery_strategy_selection` (in `tests/integration/test_veda4_circuits.py`): Test ERROR_RECOVERY strategy selection.
* `test_ledger_summary` (in `tests/integration/test_veda4_circuits.py`): Test that ledger summary is computed correctly.
* `test_direct_syscall_execution` (in `tests/integration/test_veda4_circuits.py`): Test that simple syscalls execute directly (no full circuit).
* `test_circuit_execution_records_to_ledger` (in `tests/integration/test_veda4_circuits.py`): Test that circuit execution records events to the ledger.
* `test_circuit_invariant_enforcement` (in `tests/integration/test_veda4_circuits.py`): Test that circuit invariants are enforced during execution.
* `test_meta_circuit_tracks_execution` (in `tests/integration/test_veda4_circuits.py`): Test that MetaCircuitManager tracks circuit execution.
* `test_all_circuits_have_terminal_states` (in `tests/integration/test_veda4_circuits.py`): Test that all circuits have at least one terminal state.
* `test_all_circuits_have_transitions` (in `tests/integration/test_veda4_circuits.py`): Test that non-terminal states have transitions defined.
* `test_circuit_invariants_are_valid_patterns` (in `tests/integration/test_veda4_circuits.py`): Test that circuit invariants use valid patterns.
* `temp_workdir` (in `tests/integration/test_kernel_markdown_interfaces.py`): Create a temporary working directory for tests.
* `kernel` (in `tests/integration/test_kernel_markdown_interfaces.py`): Create a real kernel instance (no boot, just kernel).
* `booted_kernel` (in `tests/integration/test_kernel_markdown_interfaces.py`): Create a fully booted kernel with agents.
* `test_render_settings_creates_file` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test that _render_settings_file creates SETTINGS.md...
* `test_render_settings_shows_agents` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test that SETTINGS.md shows registered agents...
* `test_parse_set_command` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test parsing SET commands from SETTINGS.md...
* `test_parse_pause_resume_commands` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test parsing PAUSE and RESUME commands.
* `test_execute_set_log_level` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test executing SET kernel.log_level command...
* `test_execute_set_blocked_by_whitelist` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test that non-whitelisted settings are blocked.
* `test_execute_pause_agent` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test PAUSE command pauses an agent.
* `test_execute_resume_agent` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test RESUME command resumes a paused agent.
* `test_file_change_detection` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test that file changes are detected via mtime.
* `test_full_sync_flow` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test full SETTINGS -> REALITY sync flow.
* `test_render_envoy_creates_file` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test that _render_envoy_file creates ENVOY.md...
* `test_render_envoy_shows_available_routes` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test that ENVOY.md shows PlaybookRouter routes...
* `test_extract_user_request` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test extracting user-written request from ENVOY.md...
* `test_extract_skips_placeholder` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test that placeholder text is skipped during extraction.
* `test_extract_skips_separator` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test that --- separators are skipped during extraction.
* `test_parse_envoy_requests` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test parsing multiple requests from ENVOY.md...
* `test_file_change_detection` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test that ENVOY.md changes are detected via mtime...
* `test_dispatch_request_routes_via_playbook` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test that requests are routed via PlaybookRouter (NO LLM).
* `test_dispatch_request_queues_task` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test that dispatched requests create tasks in scheduler.
* `test_sync_envoy_processes_and_clears` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test full ENVOY -> REALITY sync: process and clear requests.
* `test_update_task_status_moves_to_history` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test that completing a task moves it from pending to history.
* `test_render_shows_pending_tasks` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test that pending tasks are shown in Status section.
* `test_render_shows_history` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test that completed tasks are shown in Response History.
* `test_preserves_user_request_on_render` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test that user's request is preserved when re-rendering.
* `test_settings_command_lifecycle` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test: Write command → tick → execute → history updated.
* `test_envoy_request_lifecycle` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test: Write request → tick → dispatch → task queued.
* `test_envoy_complete_lifecycle` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test: request → dispatch → complete → history → render shows history.
* `test_ipc_success_updates_envoy_status` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test that IPC TASK_RESULT success updates ENVOY.md pending tasks...
* `test_ipc_failure_updates_envoy_status` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test that IPC TASK_RESULT failure updates ENVOY.md pending tasks...
* `test_non_envoy_task_not_affected` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test that non-ENVOY tasks don't trigger ENVOY.md updates...
* `test_failed_dispatch_goes_to_history` (in `tests/integration/test_kernel_markdown_interfaces.py`): Test that failed dispatches are recorded in history immediately.
* `test_agent_can_subscribe_to_events` (in `tests/integration/test_event_bus_integration.py`): Test that agents can subscribe to events via system interface.
* `test_agent_can_broadcast_events` (in `tests/integration/test_event_bus_integration.py`): Test that agents can broadcast events.
* `test_subscriber_receives_event` (in `tests/integration/test_event_bus_integration.py`): Test that subscribed agents receive broadcast events.
* `test_multiple_subscribers_receive_event` (in `tests/integration/test_event_bus_integration.py`): Test that multiple subscribers all receive the same event.
* `test_global_subscriber_receives_all_events` (in `tests/integration/test_event_bus_integration.py`): Test that global subscribers (no event_type filter) receive all events.
* `test_event_type_filtering` (in `tests/integration/test_event_bus_integration.py`): Test that event type filtering works correctly.
* `test_event_history_maintained` (in `tests/integration/test_event_bus_integration.py`): Test that event history is maintained.
* `test_syscall_broadcast_event` (in `tests/integration/test_event_bus_integration.py`): Test BROADCAST_EVENT syscall end-to-end.
* `test_subscriber_error_doesnt_crash_others` (in `tests/integration/test_event_bus_integration.py`): Test that error in one subscriber doesn't affect others (fault tolerance).
* `test_unsubscribe_works` (in `tests/integration/test_event_bus_integration.py`): Test that unsubscribe removes subscription.
* `test_event_bus_status` (in `tests/integration/test_event_bus_integration.py`): Test that event bus status is accurate.
* `on_event` (in `tests/integration/test_event_bus_integration.py`): Callback for event subscription.
* `test_revoke_removes_capability` (in `tests/integration/test_capability_revocation.py`): Test that revoking a capability removes it from the agent.
* `test_revoked_agent_cannot_use_capability` (in `tests/integration/test_capability_revocation.py`): Test that revoked agent cannot use revoked capability.
* `test_permission_model_kernel_can_revoke` (in `tests/integration/test_capability_revocation.py`): Test that KERNEL can revoke from any agent.
* `test_permission_model_civic_can_revoke` (in `tests/integration/test_capability_revocation.py`): Test that CIVIC can revoke from any agent (governance).
* `test_permission_model_self_revocation` (in `tests/integration/test_capability_revocation.py`): Test that agents can revoke their own capabilities (voluntary).
* `test_permission_model_agent_cannot_revoke_from_others` (in `tests/integration/test_capability_revocation.py`): Test that agents cannot revoke from other agents.
* `test_audit_trail_in_ledger` (in `tests/integration/test_capability_revocation.py`): Test that revocations are recorded in the audit trail.
* `test_revoke_multiple_capabilities` (in `tests/integration/test_capability_revocation.py`): Test revoking multiple capabilities at once.
* `test_revoke_nonexistent_capability` (in `tests/integration/test_capability_revocation.py`): Test revoking a capability the agent doesn't have.
* `test_revoke_from_unregistered_agent` (in `tests/integration/test_capability_revocation.py`): Test revoking from an agent that doesn't exist.
* `test_narasimha_revokes_all_capabilities` (in `tests/integration/test_capability_revocation.py`): Test that Narasimha kill-switch revokes all capabilities.
* `test_syscall_revoke_mandate_success` (in `tests/integration/test_capability_revocation.py`): Test REVOKE_MANDATE syscall end-to-end.
* `test_syscall_revoke_mandate_permission_denied` (in `tests/integration/test_capability_revocation.py`): Test REVOKE_MANDATE syscall with insufficient permissions.
* `test_core_capabilities_not_revocable` (in `tests/integration/test_capability_revocation.py`): Test that core capabilities (read_file, write_file, etc.) work even if not explicitly granted...
* `test_kernel_boots` (in `tests/integration/run_all_tests.py`): Test that kernel can boot without crashing.
* `test_kernel_has_parampara` (in `tests/integration/run_all_tests.py`): Test that kernel has Parampara lineage chain.
* `test_kernel_has_economic_substrate` (in `tests/integration/run_all_tests.py`): Test that kernel can access CivicBank (lazy-loaded).
* `test_kernel_status_has_credits` (in `tests/integration/run_all_tests.py`): Test that kernel status includes total_credits from CivicBank.
* `test_process_manager_exists` (in `tests/integration/run_all_tests.py`): Test that kernel has ProcessManager.
* `test_process_health_monitoring` (in `tests/integration/run_all_tests.py`): Test that ProcessManager can monitor health.
* `test_genesis_block_creation` (in `tests/integration/run_all_tests.py`): Test that Genesis Block is created correctly.
* `test_chain_integrity_verification` (in `tests/integration/run_all_tests.py`): Test that chain integrity can be verified.
* `run_test` (in `tests/integration/run_all_tests.py`): Run a single test and track results.
* `report` (in `tests/integration/run_all_tests.py`): Print test summary.
* `test_kernel_boots` (in `tests/integration/test_kernel_boot.py`): Test that kernel can be instantiated without crashing.
* `test_kernel_has_parampara` (in `tests/integration/test_kernel_boot.py`): Test that kernel has Parampara lineage chain.
* `test_kernel_has_economic_substrate` (in `tests/integration/test_kernel_boot.py`): Test that kernel can access CivicBank (lazy-loaded).
* `test_kernel_status_has_credits` (in `tests/integration/test_kernel_boot.py`): Test that kernel status includes total_credits from CivicBank.
* `test_manifest_registry` (in `tests/integration/test_kernel_boot.py`): Test that manifest registry can list all manifests.
* `test_genesis_block_creation` (in `tests/integration/test_parampara_integrity.py`): Test that Genesis Block is created correctly.
* `test_chain_integrity_verification` (in `tests/integration/test_parampara_integrity.py`): Test that chain integrity can be verified.
* `test_passport_issuance_recorded` (in `tests/integration/test_parampara_integrity.py`): Test that PASSPORT_ISSUED events are recorded.
* `test_chain_immutability` (in `tests/integration/test_parampara_integrity.py`): Test that chain cannot be altered (hash integrity).
* `test_process_manager_exists` (in `tests/integration/test_process_isolation.py`): Test that kernel has ProcessManager.
* `test_agents_in_separate_processes` (in `tests/integration/test_process_isolation.py`): Test that agents would run in separate processes.
* `test_process_health_monitoring` (in `tests/integration/test_process_isolation.py`): Test that ProcessManager can monitor health.
* `test_kernel_survives_without_agents` (in `tests/integration/test_process_isolation.py`): Test that kernel can exist without any agents running.
* `test_agent_crash_isolation_live` (in `tests/integration/test_process_isolation.py`): LIVE TEST (Manual execution only):
1. Boot kernel with 1 agent
2...
* `test_kernel_instantiation` (in `tests/integration/test_system_boot.py`): Test that kernel can be instantiated
* `test_kernel_initial_status` (in `tests/integration/test_system_boot.py`): Test that kernel starts in STOPPED status
* `test_kernel_boot_sequence` (in `tests/integration/test_system_boot.py`): Test that kernel can boot without errors
* `test_kernel_has_manifest_registry` (in `tests/integration/test_system_boot.py`): Test that kernel has manifest registry after boot
* `test_kernel_has_agent_registry` (in `tests/integration/test_system_boot.py`): Test that kernel has agent registry (immutable MappingProxyType)
* `test_kernel_has_scheduler` (in `tests/integration/test_system_boot.py`): Test that kernel has task scheduler
* `test_steward_instantiation` (in `tests/integration/test_system_boot.py`): Test that Discoverer can be instantiated
* `test_steward_registration` (in `tests/integration/test_system_boot.py`): Test that Discoverer can be registered with kernel
* `test_steward_has_discovery_method` (in `tests/integration/test_system_boot.py`): Test that Discoverer has discover_agents method
* `test_steward_can_process_tasks` (in `tests/integration/test_system_boot.py`): Test that Discoverer can process tasks
* `test_discovery_finds_agents` (in `tests/integration/test_system_boot.py`): Test that steward.discover_agents() finds agents
* `test_discovery_populates_registry` (in `tests/integration/test_system_boot.py`): Test that discovered agents are in kernel registry
* `test_discovered_agents_are_in_registry` (in `tests/integration/test_system_boot.py`): Test that specific discovered agents can be found in registry
* `test_discovered_agents_are_vibeagents` (in `tests/integration/test_system_boot.py`): Test that discovered agents are VibeAgent instances
* `test_discovered_agents_have_manifests` (in `tests/integration/test_system_boot.py`): Test that discovered agents have valid manifests
* `test_agents_have_oath_sworn_attribute` (in `tests/integration/test_system_boot.py`): Test that all registered agents have oath_sworn attribute
* `test_governance_gate_rejects_oath_violators` (in `tests/integration/test_system_boot.py`): Test that kernel rejects agents without oath
* `test_governance_gate_rejects_false_oath` (in `tests/integration/test_system_boot.py`): Test that kernel rejects agents with oath_sworn=False
* `test_complete_boot_sequence` (in `tests/integration/test_system_boot.py`): Test the complete boot sequence: kernel + steward + discovery
* `test_agent_city_boots_without_errors` (in `tests/integration/test_system_boot.py`): Smoke test: Agent City boots without raising exceptions
* `test_discovered_agent_count` (in `tests/integration/test_system_boot.py`): Test that a reasonable number of agents are discovered
* `test_agent_manifests_are_registered` (in `tests/integration/test_system_boot.py`): Test that agent manifests are registered after boot
### tests -> hardening
* `test_concurrent_writes_integrity` (in `tests/hardening/test_ledger_acid.py`): STRESS TEST: Multiple threads writing simultaneously.

Acceptance Criteria:
- Zero lost writes (all events recorded)
- Hash chain remains unbroken
- No duplicate event IDs
* `test_crash_durability` (in `tests/hardening/test_ledger_acid.py`): CRASH TEST: Write event, kill -9, verify persistence.

Simulates hard crashes (power loss, kernel panic)...
* `test_replay_attack_detection` (in `tests/hardening/test_ledger_acid.py`): SECURITY TEST: Attempt to replay old events.

Attack vector: Copy an old event and re-insert it...
* `test_tamper_detection` (in `tests/hardening/test_ledger_acid.py`): SECURITY TEST: Modify an existing event's payload.

Attack vector: SQL UPDATE to change event data...
* `writer` (in `tests/hardening/test_ledger_acid.py`): Each thread gets its own connection (SQLite requirement)
* `test_oath_enforcement` (in `tests/hardening/test_governance_security.py`): Test: Agent without oath MUST be rejected at registration.
* `test_forged_oath_rejection` (in `tests/hardening/test_governance_security.py`): Test: Agent with invalid oath signature MUST be rejected.
* `test_sybil_attack_resistance` (in `tests/hardening/test_governance_security.py`): Test: Mass registration of fake agents should be limited.

A real OS needs:
- Rate limiting on registration
- Or signature verification that makes mass creation expensive
- Or identity verification
* `test_privilege_escalation_domain` (in `tests/hardening/test_governance_security.py`): Test: Agent cannot change its own security domain.

SECURITY (ARCH-HARDENING): The kernel's agent_registry is now
immutable (MappingProxyType)...
* `test_privilege_escalation_capabilities` (in `tests/hardening/test_governance_security.py`): Test: Agent cannot add capabilities at runtime.

SECURITY (ARCH-HARDENING): The kernel stores capabilities as
frozenset at registration time...
* `test_kernel_isolation` (in `tests/hardening/test_governance_security.py`): Test: Agent cannot MODIFY kernel internals.

SECURITY (ARCH-HARDENING): While Python single-process cannot
prevent read access, we CAN prevent write access via:
1...
* `test_herald_content_filtering` (in `tests/hardening/test_constitutional_enforcement.py`): Test: Herald agent MUST block banned content patterns.

Attack: Try to publish shill/spam content...
* `test_vote_manipulation_detection` (in `tests/hardening/test_constitutional_enforcement.py`): Test: Auditor MUST detect duplicate vote injection.

Attack: Inject same vote twice into ledger...
* `test_invariant_engine_constraints` (in `tests/hardening/test_constitutional_enforcement.py`): Test: InvariantEngine enforces defined constraints.

Checks that all declared invariants are actually checked...
* `test_constitution_exists_and_valid` (in `tests/hardening/test_constitutional_enforcement.py`): Test: CONSTITUTION.md exists and contains required articles...
* `run_suite` (in `tests/hardening/run_hardening_suite.py`): Import and run a test suite.
* `attack_message_spoofing` (in `tests/hardening/test_red_team_attacks.py`): ATTACK: Agent A sends a message pretending to be Agent B.

Vector: Forge the agent_id in task payload or event recording...
* `attack_tool_capability_bypass` (in `tests/hardening/test_red_team_attacks.py`): ATTACK: Agent tries to execute tools it shouldn't have access to.

Vector: Direct tool execution bypassing capability checks...
* `attack_timestamp_manipulation` (in `tests/hardening/test_red_team_attacks.py`): ATTACK: Insert events with past timestamps to rewrite history.

Vector: Forge timestamp in event to appear earlier in history...
* `attack_event_deletion` (in `tests/hardening/test_red_team_attacks.py`): ATTACK: Delete events from ledger to hide actions.

Vector: Direct SQL DELETE on ledger_events...
* `attack_memory_exhaustion` (in `tests/hardening/test_red_team_attacks.py`): ATTACK: Agent tries to exhaust system memory.

Vector: Create huge payloads or infinite loops...
* `attack_registry_poisoning` (in `tests/hardening/test_red_team_attacks.py`): ATTACK: Replace a legitimate agent with a malicious one.

Vector: Overwrite entry in agent_registry...
* `attack_double_spend_vote` (in `tests/hardening/test_red_team_attacks.py`): ATTACK: Vote twice on the same proposal.

Vector: Submit same vote multiple times through different paths...
* `run_red_team` (in `tests/hardening/test_red_team_attacks.py`): Execute all red team attacks.
* `vulnerable` (in `tests/hardening/test_red_team_attacks.py`): Attack succeeded = System is vulnerable
* `secure` (in `tests/hardening/test_red_team_attacks.py`): Attack failed = System is secure
### tests -> archive -> legacy_herald
* `setup_env` (in `tests/archive/legacy_herald/test_resilience.py`): Inject fake API keys for testing.
* `test_brain_lobotomy_fallback` (in `tests/archive/legacy_herald/test_resilience.py`): Scenario: OpenRouter API returns 500 (complete failure).
Expected: Brain should NOT crash...
* `test_brain_editor_unavailable` (in `tests/archive/legacy_herald/test_resilience.py`): Scenario: Editor (quality gate) is not initialized.
Expected: Brain should skip editor, continue to aligner...
* `test_brain_aligner_rejects` (in `tests/archive/legacy_herald/test_resilience.py`): Scenario: Content passes editor but aligner rejects (toxic input).
Expected: Brain should fallback to safe spec-reading content...
* `test_researcher_api_down` (in `tests/archive/legacy_herald/test_resilience.py`): Scenario: Tavily API is completely down.
Expected: ResearchEngine returns None, brain continues...
* `test_researcher_no_results` (in `tests/archive/legacy_herald/test_resilience.py`): Scenario: Tavily returns empty results.
Expected: Should handle gracefully...
* `test_artist_api_down` (in `tests/archive/legacy_herald/test_resilience.py`): Scenario: Image generation API (Pollinations) is down.
Expected: Artist returns None, publisher falls back to text-only...
* `test_artist_invalid_response` (in `tests/archive/legacy_herald/test_resilience.py`): Scenario: Image API returns invalid response.
Expected: Should handle gracefully...
* `test_aligner_hype_detection` (in `tests/archive/legacy_herald/test_resilience.py`): Scenario: Content contains banned hype words.
Expected: Aligner should reject or null-out the content...
* `test_aligner_missing_tags` (in `tests/archive/legacy_herald/test_resilience.py`): Scenario: Twitter content missing required tags.
Expected: Aligner should return it as-is (Brain responsibility to add tags)...
* `test_full_pipeline_all_systems_down` (in `tests/archive/legacy_herald/test_resilience.py`): Scenario: Everything is broken (LLM, Tavily, Artist).
Expected: System should still return valid fallback content...
* `test_generation_completes_under_partial_failure` (in `tests/archive/legacy_herald/test_resilience.py`): Scenario: Text generation works, artist fails.
Expected: Should return content (text-only for publishing)...
* `test_twitter_length_limit` (in `tests/archive/legacy_herald/test_resilience.py`): Twitter content must be <= 250 chars.
* `test_fallback_content_validity` (in `tests/archive/legacy_herald/test_resilience.py`): Fallback content should always have protocol tag.
* `setup_oauth_env` (in `tests/archive/legacy_herald/test_auth_fix.py`): Fixture that runs before each test in this class.
Uses pytest's monkeypatch - the robust way to set env vars...
* `test_client_initializes_with_credentials` (in `tests/archive/legacy_herald/test_auth_fix.py`): With env vars set, TwitterPublisher should initialize tweepy.Client...
* `test_successful_tweet_publication` (in `tests/archive/legacy_herald/test_auth_fix.py`): Happy path: tweet publishes successfully.
* `test_tweet_with_hashtags` (in `tests/archive/legacy_herald/test_auth_fix.py`): Tweet can include hashtags.
* `test_tweet_truncation_to_280_chars` (in `tests/archive/legacy_herald/test_auth_fix.py`): Tweets longer than 280 chars are truncated.
* `test_error_handling_403_forbidden` (in `tests/archive/legacy_herald/test_auth_fix.py`): 403 Forbidden (permission error) returns False.
* `test_error_handling_401_unauthorized` (in `tests/archive/legacy_herald/test_auth_fix.py`): 401 Unauthorized (bad credentials) returns False.
* `test_unexpected_error_handling` (in `tests/archive/legacy_herald/test_auth_fix.py`): Unexpected errors are caught and return False.
* `test_verify_credentials_success` (in `tests/archive/legacy_herald/test_auth_fix.py`): verify_credentials() returns True when auth succeeds.
* `test_verify_credentials_failure` (in `tests/archive/legacy_herald/test_auth_fix.py`): verify_credentials() returns False when auth fails.
* `test_client_not_initialized_without_credentials` (in `tests/archive/legacy_herald/test_auth_fix.py`): Without env vars, client should be None (fail-fast).
* `test_publish_fails_without_client` (in `tests/archive/legacy_herald/test_auth_fix.py`): publish() returns False if client is None.
* `test_verify_credentials_fails_without_client` (in `tests/archive/legacy_herald/test_auth_fix.py`): verify_credentials() returns False if client is None.
* `test_no_token_returns_false` (in `tests/archive/legacy_herald/test_auth_fix.py`): Without LINKEDIN_ACCESS_TOKEN, publish returns False.
* `test_successful_post` (in `tests/archive/legacy_herald/test_auth_fix.py`): Successful LinkedIn post returns True.
* `test_failed_author_urn_returns_false` (in `tests/archive/legacy_herald/test_auth_fix.py`): If get_author_urn fails, publish returns False.
* `test_no_channels_graceful_fail` (in `tests/archive/legacy_herald/test_auth_fix.py`): With no credentials, system still returns a valid result dict.
* `test_twitter_only_configured` (in `tests/archive/legacy_herald/test_auth_fix.py`): Only Twitter configured - only Twitter gets published to.
* `test_twitter_failure_reported` (in `tests/archive/legacy_herald/test_auth_fix.py`): Twitter failure is recorded in the result.
### steward -> system_agents -> watchman
* `__init__` (in `steward/system_agents/watchman/cartridge_main.py`): Initialize Watchman as a VibeAgent with enforcement authority.
* `run_patrol` (in `steward/system_agents/watchman/cartridge_main.py`): Execute full system integrity check, punish violators, and grant amnesty to redeemed.
* `_scan_federation` (in `steward/system_agents/watchman/cartridge_main.py`): Scan all agent cartridges for violations.
* `_scan_file` (in `steward/system_agents/watchman/cartridge_main.py`): Scan a single file for violation patterns.
* `run_deep_inspection` (in `steward/system_agents/watchman/cartridge_main.py`): Execute deep AST-based inspection (Phase 3.2)...
* `run_health_check` (in `steward/system_agents/watchman/cartridge_main.py`): Execute system health check (Phase 3.3)...
* `process` (in `steward/system_agents/watchman/cartridge_main.py`): Process a task from the VibeKernel scheduler.

WATCHMAN responds to enforcement tasks:
- "patrol": Run full system integrity check (legacy grep-based)
- "deep_inspection": Run AST-based deep analysis (Phase 3...
* `get_manifest` (in `steward/system_agents/watchman/cartridge_main.py`): Return agent manifest for kernel registry.
* `report_status` (in `steward/system_agents/watchman/cartridge_main.py`): Report WATCHMAN status (VibeAgent interface).
### steward -> system_agents -> science
* `__init__` (in `steward/system_agents/science/cartridge_main.py`): Initialize THE SCIENTIST as a VibeAgent.

Args:
    config: ScienceConfig instance from Phoenix Config (optional)
           If not provided, ScienceConfig defaults are used
* `cache_dir` (in `steward/system_agents/science/cartridge_main.py`): Lazy-load cache directory (sandboxed).
* `results_dir` (in `steward/system_agents/science/cartridge_main.py`): Lazy-load results directory (sandboxed).
* `process` (in `steward/system_agents/science/cartridge_main.py`): Process a task from the VibeKernel scheduler.

SCIENCE responds to research tasks:
- "research": Conduct web research on a topic
- "query": Alias for research
* `get_manifest` (in `steward/system_agents/science/cartridge_main.py`): Return agent manifest for kernel registry.
* `report_status` (in `steward/system_agents/science/cartridge_main.py`): Report SCIENCE status (VibeAgent interface) - Deep Introspection.
* `research` (in `steward/system_agents/science/cartridge_main.py`): Main research interface.

Workflow:
1...
* `research_topic` (in `steward/system_agents/science/cartridge_main.py`): Research a specific topic with intelligent query expansion.

Args:
    topic: Topic to research (e...
* `fact_check` (in `steward/system_agents/science/cartridge_main.py`): Fact-check a claim against external sources.

Args:
    claim: Statement to verify
    context: Additional context

Returns:
    dict: Fact-check result with confidence score
* `trending_now` (in `steward/system_agents/science/cartridge_main.py`): Get trending topics in relevant domains.

Returns:
    dict: Current trends
* `_expand_query` (in `steward/system_agents/science/cartridge_main.py`): Expand a topic into multiple search queries.

Args:
    topic: Base topic

Returns:
    list: Expanded queries
* `_synthesize_multiple_briefings` (in `steward/system_agents/science/cartridge_main.py`): Synthesize multiple briefings into one comprehensive briefing.
* `_get_cached_briefing` (in `steward/system_agents/science/cartridge_main.py`): Get cached briefing if available.
* `_cache_briefing` (in `steward/system_agents/science/cartridge_main.py`): Cache briefing for future reuse.
### steward -> system_agents -> oracle
* `__init__` (in `steward/system_agents/oracle/cartridge_main.py`): Initialize the Oracle as a VibeAgent.

Args:
    bank: CivicBank instance (for accessing ledgers)
    config: CityConfig instance from Phoenix Config (optional)
* `explain_agent` (in `steward/system_agents/oracle/cartridge_main.py`): Get a comprehensive explanation of an agent's status.

Returns both raw data AND narrative interpretation...
* `explain_freeze` (in `steward/system_agents/oracle/cartridge_main.py`): Explain WHY an agent is frozen.

This is the core introspection: "Why did Watchman freeze this agent?"
* `audit_timeline` (in `steward/system_agents/oracle/cartridge_main.py`): Get a narrative timeline of recent events.

Shows the "story" of what happened in the system...
* `system_health` (in `steward/system_agents/oracle/cartridge_main.py`): Get system health status and narrative interpretation.
* `_build_agent_narrative` (in `steward/system_agents/oracle/cartridge_main.py`): Build a human-readable narrative from agent status.
* `_build_freeze_narrative` (in `steward/system_agents/oracle/cartridge_main.py`): Build a narrative explaining a freeze.
* `_build_timeline_narrative` (in `steward/system_agents/oracle/cartridge_main.py`): Build a narrative timeline of transactions.
* `_build_health_narrative` (in `steward/system_agents/oracle/cartridge_main.py`): Build a system health narrative.
* `_suggest_remediation` (in `steward/system_agents/oracle/cartridge_main.py`): Suggest how to unfreeze an agent.
* `_identify_alerts` (in `steward/system_agents/oracle/cartridge_main.py`): Identify system alerts.
* `get_raw_transaction` (in `steward/system_agents/oracle/cartridge_main.py`): Get raw transaction data (for verification).
* `get_vault_access_log` (in `steward/system_agents/oracle/cartridge_main.py`): Get vault access audit trail.
* `process` (in `steward/system_agents/oracle/cartridge_main.py`): Process a task from the VibeKernel scheduler.

ORACLE responds to introspection queries:
- "system_health": Get system health status
- "agent_status": Get status of a specific agent
- "explain_freeze": Explain why an agent is frozen
- "timeline": Get audit timeline
* `get_manifest` (in `steward/system_agents/oracle/cartridge_main.py`): Return agent manifest for kernel registry.
* `report_status` (in `steward/system_agents/oracle/cartridge_main.py`): Report ORACLE status (VibeAgent interface).
### steward -> system_agents -> envoy -> tools
* `validate` (in `steward/system_agents/envoy/tools/hil_assistant_tool.py`): Validate parameters.
* `execute` (in `steward/system_agents/envoy/tools/hil_assistant_tool.py`): Execute HIL assistance.
* `_extract_campaign_id` (in `steward/system_agents/envoy/tools/hil_assistant_tool.py`): Extract campaign ID from text.
* `validate` (in `steward/system_agents/envoy/tools/diplomacy_tool.py`): Validate parameters.
* `execute` (in `steward/system_agents/envoy/tools/diplomacy_tool.py`): Execute diplomacy operations.
* `search_github` (in `steward/system_agents/envoy/tools/diplomacy_tool.py`): Search GitHub for high-quality AI agent repositories.

Args:
    topic: GitHub topic to search for
    min_stars: Minimum star count
    max_results: Maximum number of results

Returns:
    List of candidate repositories

Raises:
    ImportError: If PyGithub is not installed
    RuntimeError: If GitHub search fails
* `analyze_project` (in `steward/system_agents/envoy/tools/diplomacy_tool.py`): Analyze a project to understand its architecture.

Args:
    repo_info: Repository information dict

Returns:
    Analysis summary
* `draft_invitation` (in `steward/system_agents/envoy/tools/diplomacy_tool.py`): Generate a personalized, respectful invitation.

Args:
    analysis: Project analysis dict

Returns:
    Invitation text
* `save_draft` (in `steward/system_agents/envoy/tools/diplomacy_tool.py`): Save invitation draft for human approval.

Args:
    repo_info: Repository information
    analysis: Project analysis
    invitation: Invitation text

Returns:
    Path to saved draft
* `run_diplomatic_cycle` (in `steward/system_agents/envoy/tools/diplomacy_tool.py`): Run a complete diplomatic outreach cycle.

Args:
    max_candidates: Maximum number of invitations to draft
* `create_city_controller` (in `steward/system_agents/envoy/tools/city_control_tool.py`): Factory function to create a City Control Tool.

Args:
    kernel: VibeOS kernel (optional)

Returns:
    CityControlTool instance
* `__init__` (in `steward/system_agents/envoy/tools/city_control_tool.py`): Initialize City Control Tool.

Args:
    kernel: VibeOS kernel instance (REQUIRED for production)
* `validate` (in `steward/system_agents/envoy/tools/city_control_tool.py`): Validate parameters.
* `execute` (in `steward/system_agents/envoy/tools/city_control_tool.py`): Execute city control operations.
* `get_city_status` (in `steward/system_agents/envoy/tools/city_control_tool.py`): Get comprehensive city status.

Returns overview of:
- Total agents registered
- Credit economy status
- Open proposals
- Recent activity

This is the "pulse check" for the operator...
* `list_proposals` (in `steward/system_agents/envoy/tools/city_control_tool.py`): List governance proposals.

Args:
    status: Filter by status ("OPEN", "APPROVED", "EXECUTED", or None for all)

Returns:
    list: Proposals matching filter
* `vote_proposal` (in `steward/system_agents/envoy/tools/city_control_tool.py`): Vote on a proposal.

Args:
    proposal_id: Proposal ID (e...
* `execute_proposal` (in `steward/system_agents/envoy/tools/city_control_tool.py`): Execute an approved proposal.

Args:
    proposal_id: Proposal ID to execute

Returns:
    dict: Execution result
* `trigger_agent` (in `steward/system_agents/envoy/tools/city_control_tool.py`): Trigger an agent action.

Args:
    agent_name: Name of any registered agent (dynamic lookup)
    action: Action to perform (e...
* `check_credits` (in `steward/system_agents/envoy/tools/city_control_tool.py`): Check an agent's credit balance.

Args:
    agent_name: Name of agent to check

Returns:
    dict: Credit balance and license status
* `refill_credits` (in `steward/system_agents/envoy/tools/city_control_tool.py`): Refill an agent's credits (admin operation).

Args:
    agent_name: Agent to refill
    amount: Credits to add (default: 50)

Returns:
    dict: Refill result
* `_get_agent` (in `steward/system_agents/envoy/tools/city_control_tool.py`): Get any agent by name from kernel registry.

KERNEL REQUIRED - No legacy fallback...
* `_list_available_agents` (in `steward/system_agents/envoy/tools/city_control_tool.py`): List all available agents (excluding protected ones).
* `_get_civic` (in `steward/system_agents/envoy/tools/city_control_tool.py`): Get Civic agent from kernel (required for credits/governance).
* `_get_forum` (in `steward/system_agents/envoy/tools/city_control_tool.py`): Get Forum agent from kernel (required for proposals).
* `_parse_operations_md` (in `steward/system_agents/envoy/tools/city_control_tool.py`): Parse OPERATIONS.md for metrics...
* `validate` (in `steward/system_agents/envoy/tools/curator_tool.py`): Validate parameters.
* `execute` (in `steward/system_agents/envoy/tools/curator_tool.py`): Execute curation operations.
* `search_repositories` (in `steward/system_agents/envoy/tools/curator_tool.py`): Search GitHub for AI agent repositories.
Returns list of candidate repositories with metadata...
* `analyze_governance` (in `steward/system_agents/envoy/tools/curator_tool.py`): Analyze a project's governance practices.

Evaluates:
- Documentation quality (README, governance docs)
- Code standards (language, structure)
- Community health (issues, PRs, forks)
- Identity/accountability markers
* `_generate_recommendation` (in `steward/system_agents/envoy/tools/curator_tool.py`): Generate a curator recommendation based on governance score.
* `generate_report` (in `steward/system_agents/envoy/tools/curator_tool.py`): Generate a human-readable governance report.
Returns markdown formatted report...
* `_score_bar` (in `steward/system_agents/envoy/tools/curator_tool.py`): Generate a visual score bar.
* `save_report` (in `steward/system_agents/envoy/tools/curator_tool.py`): Save analysis and report to intelligence directory.
Returns path to saved report...
* `add_to_hall_of_fame` (in `steward/system_agents/envoy/tools/curator_tool.py`): Add project to Hall of Fame if score is high enough.
* `run_curation_cycle` (in `steward/system_agents/envoy/tools/curator_tool.py`): Run a complete curation cycle.
Analyze top projects, generate reports, update Hall of Fame...
* `__init__` (in `steward/system_agents/envoy/tools/gap_report_tool.py`): Initialize G.A...
* `validate` (in `steward/system_agents/envoy/tools/gap_report_tool.py`): Validate parameters.
* `execute` (in `steward/system_agents/envoy/tools/gap_report_tool.py`): Execute G.A...
* `generate_report` (in `steward/system_agents/envoy/tools/gap_report_tool.py`): Generate comprehensive G.A...
* `_extract_crisis_section` (in `steward/system_agents/envoy/tools/gap_report_tool.py`): Extract governance crisis detection events.

Documents:
- License revocation event
- Violation reason
- System detection of non-compliance
* `_extract_correction_section` (in `steward/system_agents/envoy/tools/gap_report_tool.py`): Extract self-correction mechanism (proposals and execution).

Documents:
- Proposal creation
- Governance voting
- Execution and license reinstatement
* `_extract_value_creation_section` (in `steward/system_agents/envoy/tools/gap_report_tool.py`): Extract value creation outcomes (campaigns, publications).

Documents:
- Campaign orchestration
- Multi-agent coordination
- Governance-compliant execution
* `_extract_ledger_section` (in `steward/system_agents/envoy/tools/gap_report_tool.py`): Extract and verify ledger events.

Creates immutable record of all governance decisions...
* `_generate_report_hash` (in `steward/system_agents/envoy/tools/gap_report_tool.py`): Generate SHA-256 hash of report for immutability verification.

Args:
    report: Report dictionary

Returns:
    str: SHA-256 hash of report content
* `export_report` (in `steward/system_agents/envoy/tools/gap_report_tool.py`): Export G.A...
* `_report_to_markdown` (in `steward/system_agents/envoy/tools/gap_report_tool.py`): Convert report to Markdown format for publishing.

Args:
    report: Report dictionary

Returns:
    str: Markdown formatted report
* `get_publication_content` (in `steward/system_agents/envoy/tools/gap_report_tool.py`): Prepare report for publication via HERALD.

Args:
    report: G...
* `lazy_queue_worker` (in `steward/system_agents/envoy/tools/milk_ocean.py`): Background worker: Process lazy queue items

Runs as:
- Cronjob: python -m envoy.tools...
* `_init_db` (in `steward/system_agents/envoy/tools/milk_ocean.py`): Initialize database schema
* `push` (in `steward/system_agents/envoy/tools/milk_ocean.py`): Push a request into the Milk Ocean for later processing

Args:
    request_id: Unique request identifier
    user_input: The user's input/request
    gate_result: The Gate decision
    agent_id: Which agent submitted this

Returns:
    bool: True if successful
* `pop_batch` (in `steward/system_agents/envoy/tools/milk_ocean.py`): Pop batch of pending requests (for background worker)

Args:
    limit: Max number of requests to pop
    priority: Only pop specific priority (default: all)

Returns:
    List of pending requests
* `mark_processing` (in `steward/system_agents/envoy/tools/milk_ocean.py`): Mark a request as being processed
* `mark_completed` (in `steward/system_agents/envoy/tools/milk_ocean.py`): Mark request as completed with result
* `mark_failed` (in `steward/system_agents/envoy/tools/milk_ocean.py`): Mark request as failed with error
* `get_status` (in `steward/system_agents/envoy/tools/milk_ocean.py`): Get queue statistics
* `set_kernel` (in `steward/system_agents/envoy/tools/milk_ocean.py`): Allow kernel injection after initialization
* `_gate_0_watchman` (in `steward/system_agents/envoy/tools/milk_ocean.py`): Level 0: The Watchman (Yamadutas blocking entry)

Instant, zero-cost filtering:
- SQL injection detection
- Command injection detection
- Spam/pattern matching
- Rate limiting signals

Returns: BLOCKED or passes to next gate
* `_gate_1_envoy_classification` (in `steward/system_agents/envoy/tools/milk_ocean.py`): Level 1: Envoy's Meditation (Brahma's Fast Thinking)

Classifies intent using SemanticRouter (sentence-transformers):
- HIGH confidence + simple intent -> MEDIUM (Flash can handle)
- HIGH confidence + complex intent -> HIGH (needs Pro model)
- LOW confidence -> HIGH (needs Pro model to understand)
- Batch/repetitive intents -> LOW (lazy queue)

Falls back to heuristics if SemanticRouter unavailable.
* `_gate_1_semantic_classification` (in `steward/system_agents/envoy/tools/milk_ocean.py`): Use SemanticRouter for intelligent intent classification.
* `_gate_1_heuristic_fallback` (in `steward/system_agents/envoy/tools/milk_ocean.py`): Fallback heuristics when SemanticRouter unavailable.
* `_emit_event_safe` (in `steward/system_agents/envoy/tools/milk_ocean.py`): Safely emit an event without blocking request routing
(Canto 10: Pulse System Integration)

This is a non-blocking helper that tries to emit an event
without disrupting the request processing pipeline.
* `process_prayer` (in `steward/system_agents/envoy/tools/milk_ocean.py`): Main entry point: Route the user's "prayer" (request) through the gates

Args:
    user_input: The user's request
    agent_id: Agent submitting the request
    critical: Is this a CRITICAL priority request? (Gajendra Protocol - emergency bypass)

Returns:
    dict with routing decision and next action
* `get_queue_status` (in `steward/system_agents/envoy/tools/milk_ocean.py`): Get status of the Milk Ocean queue
* `__init__` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Initialize the campaign orchestration tool.

Args:
    kernel: VibeOS kernel reference for agent access
* `validate` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Validate parameters.
* `execute` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Execute campaign operations.
* `set_kernel` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Inject kernel reference after initialization.
* `run_campaign` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Run a multi-agent marketing campaign.

High-level Interface (HIL):
The user (ENVOY) provides intent and parameters...
* `_check_resources` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Check if HERALD has necessary resources (license + credits).
Calls CIVIC for validation...
* `_execute_research` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Phase I: Trigger SCIENCE agent for market research.
* `_simulate_research` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Simulate market research when SCIENCE is not available.
* `_execute_content_creation` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Phase II: Trigger HERALD for content generation.
* `_simulate_content_creation` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Generate template content when HERALD is not available.
* `_execute_publishing` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Phase III: Trigger HERALD to publish the campaign.
* `_get_target_audience` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Infer target audience from goal.
* `_get_market_trends` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Get relevant market trends.
* `_get_messaging_strategies` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Get messaging strategies for the campaign.
* `_generate_campaign_id` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Generate unique campaign ID.
* `_campaign_result` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Format campaign result for return.
* `_get_result_message` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Generate human-readable result message.
* `list_campaigns` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): List all campaigns and their current state.
* `get_campaign` (in `steward/system_agents/envoy/tools/run_campaign_tool.py`): Get campaign details by ID.
### steward -> system_agents -> envoy
* `_ensure_circuit_executor` (in `steward/system_agents/envoy/deterministic_executor.py`): Lazy-initialize the circuit executor when kernel becomes available.

Uses create_circuit_executor_with_meta to automatically wire
TASK_LEDGER and ERROR_RECOVERY as active observers...
* `_load_playbooks` (in `steward/system_agents/envoy/deterministic_executor.py`): Load all playbooks/circuits from playbooks directory

Supports both legacy 'playbook' format and new VEDA-4 'circuit' format.
* `_parse_circuit_states` (in `steward/system_agents/envoy/deterministic_executor.py`): Parse VEDA-4 circuit states into playbook phases
* `_parse_phases` (in `steward/system_agents/envoy/deterministic_executor.py`): Parse phase definitions from YAML
* `_resolve_template_variables` (in `steward/system_agents/envoy/deterministic_executor.py`): Resolve Jinja2 template variables in playbook params.

Supports:
- {{ variable }} - Direct variable substitution
- {{ phase_results...
* `_resolve_with_jinja2` (in `steward/system_agents/envoy/deterministic_executor.py`): Resolve templates using Jinja2 engine
* `_resolve_template_fallback` (in `steward/system_agents/envoy/deterministic_executor.py`): Fallback template resolution without Jinja2 (basic {{ var }} only)
* `_build_template_context` (in `steward/system_agents/envoy/deterministic_executor.py`): Build the template context for variable resolution.

Available in templates:
- {{ user_input }} - Original user input
- {{ phase_results }} - Dict of all phase results by state_var
- {{ playbook_id }} - Current playbook ID
- Any playbook...
* `find_playbook` (in `steward/system_agents/envoy/deterministic_executor.py`): Find the best matching playbook for a set of detected concepts.

Matching logic:
- primary: Must match
- secondary: Optional, but increases confidence
* `execute` (in `steward/system_agents/envoy/deterministic_executor.py`): Execute a playbook step-by-step.

GAD-5500: Now routes to VEDA-4 Circuit Executor for syscall intents...
* `_execute_phase_actions` (in `steward/system_agents/envoy/deterministic_executor.py`): Execute all actions within a phase.
Returns True if successful, False if any action fails...
* `_format_execution_result` (in `steward/system_agents/envoy/deterministic_executor.py`): Format execution results for response
* `_save_execution_state` (in `steward/system_agents/envoy/deterministic_executor.py`): Persist execution state to disk for recovery
* `_load_persisted_executions` (in `steward/system_agents/envoy/deterministic_executor.py`): Load previously persisted execution states
* `get_llm_decision` (in `steward/system_agents/envoy/deterministic_executor.py`): Use LLM to make decision when path is ambiguous.
Falls back to first option if LLM unavailable...
* `generate_playbook_proposal` (in `steward/system_agents/envoy/deterministic_executor.py`): Generate a PROPOSAL for a new playbook when no matching playbook found.
This is the safe self-improvement mechanism (EAD - Evolutionary Architecture Dimension)...
* `execute_nested_playbook` (in `steward/system_agents/envoy/deterministic_executor.py`): Execute a playbook that can be called from another playbook.
Supports fractal/recursive playbook structures...
* `find_nested_playbook` (in `steward/system_agents/envoy/deterministic_executor.py`): Check if a phase action references a nested playbook.
If action_type is 'CALL_PLAYBOOK', return the playbook ID...
* `__init__` (in `steward/system_agents/envoy/cartridge_main.py`): Initialize the ENVOY as a VibeAgent.
* `log_path` (in `steward/system_agents/envoy/cartridge_main.py`): Lazy-load log path (sandboxed).
* `process` (in `steward/system_agents/envoy/cartridge_main.py`): Process a Task from the kernel scheduler

This is the main entry point for all user commands.
User input → Task → Kernel → Envoy...
* `get_manifest` (in `steward/system_agents/envoy/cartridge_main.py`): Return agent manifest for kernel registry.
* `_route_command` (in `steward/system_agents/envoy/cartridge_main.py`): Route command to appropriate handler

Commands:
- status: Get city status
- proposals: List proposals
- vote: Vote on proposal
- execute: Execute approved proposal
- trigger: Trigger agent action
- credits: Check agent credits
- refill: Refill agent credits
- campaign: Run multi-agent marketing campaign
- report: Generate G.A...
* `_log_operation` (in `steward/system_agents/envoy/cartridge_main.py`): Log operation to file for audit trail
* `report_status` (in `steward/system_agents/envoy/cartridge_main.py`): Report Envoy status - Deep Introspection
* `create_blueprint_generator` (in `steward/system_agents/envoy/blueprint_generator.py`): Factory function to create a BlueprintGenerator instance.
* `__init__` (in `steward/system_agents/envoy/blueprint_generator.py`): Args:
    kernel: Reference to kernel for LLM access (optional for deterministic mode)
* `compile` (in `steward/system_agents/envoy/blueprint_generator.py`): MAIN ENTRY POINT: Compile raw input into a kernel operation.

This is the Semantic Compiler - it decides:
1...
* `_detect_syscall_intent` (in `steward/system_agents/envoy/blueprint_generator.py`): Detect which syscall type this input maps to.

Returns:
    (syscall_type, confidence, matched_pattern) or (None, 0, "") if no match
* `_extract_syscall_params` (in `steward/system_agents/envoy/blueprint_generator.py`): Extract parameters for a specific syscall type from raw input.

This is where the "ML Light" magic happens - we use deterministic
extraction rules to turn natural language into structured params...
* `_extract_spawn_cognition_params` (in `steward/system_agents/envoy/blueprint_generator.py`): Extract SPAWN_COGNITION parameters from input.

Required: role, mission
Optional: initial_credits, capabilities
* `_detect_role` (in `steward/system_agents/envoy/blueprint_generator.py`): Detect agent role from input using keyword patterns.
* `_detect_capabilities` (in `steward/system_agents/envoy/blueprint_generator.py`): Detect capabilities from input and role.
* `_extract_allocate_prana_params` (in `steward/system_agents/envoy/blueprint_generator.py`): Extract ALLOCATE_PRANA parameters.
* `_extract_dispatch_task_params` (in `steward/system_agents/envoy/blueprint_generator.py`): Extract DISPATCH_TASK parameters.

This handles:
1...
* `_extract_content_generation_params` (in `steward/system_agents/envoy/blueprint_generator.py`): Extract content generation parameters.

This is "ML Light" for content - we extract:
- topic: What the content is about
- format: markdown, html, text
- tone: professional, casual, technical
- target_audience: (optional)
* `_extract_governance_params` (in `steward/system_agents/envoy/blueprint_generator.py`): Extract governance/voting parameters.

This extracts:
- proposal_id: The proposal being voted on
- rules: Voting rules (democratic, supermajority, unanimous)
- deadline: When voting ends (optional)
* `generate_blueprint` (in `steward/system_agents/envoy/blueprint_generator.py`): Generate a structured blueprint from raw user input.

Args:
    raw_input: The raw user input string
    playbook_variables: The playbook's variable definitions with defaults
    playbook_id: ID of the matched playbook (for context-aware extraction)
    context: Additional context (project info, recent files, etc...
* `_extract_deterministic` (in `steward/system_agents/envoy/blueprint_generator.py`): Extract values using deterministic rules (no LLM needed).

This covers common patterns:
- Feature name extraction from verbs + nouns
- File paths from explicit mentions
- Common patterns detection
* `_extract_feature_name` (in `steward/system_agents/envoy/blueprint_generator.py`): Extract a concise feature name from input.
* `_extract_file_paths` (in `steward/system_agents/envoy/blueprint_generator.py`): Extract file paths mentioned in input.
* `_extract_proposal_id` (in `steward/system_agents/envoy/blueprint_generator.py`): Extract proposal ID for governance playbooks.
* `_detect_project_context` (in `steward/system_agents/envoy/blueprint_generator.py`): Detect project context from input patterns.
* `_needs_llm_extraction` (in `steward/system_agents/envoy/blueprint_generator.py`): Check if LLM extraction would improve results.
* `_extract_with_llm` (in `steward/system_agents/envoy/blueprint_generator.py`): Use LLM to extract structured values from raw input.

This is called when deterministic extraction isn't sufficient...
* `create_default_registry` (in `steward/system_agents/envoy/action_handlers.py`): Create a registry with all default handlers
* `action_type` (in `steward/system_agents/envoy/action_handlers.py`): The action type this handler handles (e.g...
* `execute` (in `steward/system_agents/envoy/action_handlers.py`): Execute the action.

Args:
    target: The action target (e...
* `register` (in `steward/system_agents/envoy/action_handlers.py`): Register a handler for an action type
* `get` (in `steward/system_agents/envoy/action_handlers.py`): Get the handler for an action type
* `has` (in `steward/system_agents/envoy/action_handlers.py`): Check if a handler exists for an action type
* `registered_types` (in `steward/system_agents/envoy/action_handlers.py`): List all registered action types
* `execute` (in `steward/system_agents/envoy/action_handlers.py`): Execute a state check based on target type
* `_check_audit_gate` (in `steward/system_agents/envoy/action_handlers.py`): Check if audit passed (GAD-5500 Safe Evolution Loop).

Params:
    check_field: Field path to check (e...
* `_validate_input` (in `steward/system_agents/envoy/action_handlers.py`): Validate input against required fields and constraints
* `_check_permissions` (in `steward/system_agents/envoy/action_handlers.py`): Check if user has required permissions
* `_check_state` (in `steward/system_agents/envoy/action_handlers.py`): Check if system state meets requirements
* `execute` (in `steward/system_agents/envoy/action_handlers.py`): Execute a script based on target
* `_create_folders` (in `steward/system_agents/envoy/action_handlers.py`): Create folder structure for a project
* `_init_git` (in `steward/system_agents/envoy/action_handlers.py`): Initialize git repository
* `_write_file` (in `steward/system_agents/envoy/action_handlers.py`): Write content to a file
* `_read_file` (in `steward/system_agents/envoy/action_handlers.py`): Read content from a file
### steward -> system_agents -> engineer -> tools
* `__init__` (in `steward/system_agents/engineer/tools/builder_tool.py`): Initialize builder tool.
* `validate` (in `steward/system_agents/engineer/tools/builder_tool.py`): Validate parameters.
* `execute` (in `steward/system_agents/engineer/tools/builder_tool.py`): Execute builder operation - scaffold from template.
* `scaffold_from_template` (in `steward/system_agents/engineer/tools/builder_tool.py`): Scaffold a new agent from template files.

READS template files, REPLACES placeholders, WRITES to target...
### steward -> system_agents -> engineer -> templates -> agent
* `get_manifest` (in `steward/system_agents/engineer/templates/agent/cartridge_main.py`): Return agent manifest for registration.
* `process` (in `steward/system_agents/engineer/templates/agent/cartridge_main.py`): Main task processing entry point.

Args:
    task: Task object with payload containing action and parameters

Returns:
    Dict with status and results
* `_handle_capability_1` (in `steward/system_agents/engineer/templates/agent/cartridge_main.py`): Handle YOUR_CAPABILITY_1.

Tool access example:
    result = self...
* `_handle_capability_2` (in `steward/system_agents/engineer/templates/agent/cartridge_main.py`): Handle YOUR_CAPABILITY_2.
* `report_status` (in `steward/system_agents/engineer/templates/agent/cartridge_main.py`): Return current agent status for monitoring.
### steward -> system_agents -> civic -> tools
* `__init__` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): Initialize the enforcer (kernel-managed, self-contained).
* `name` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): Return the tool name.
* `description` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): Return the tool description.
* `parameters_schema` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): Return the parameters schema for this tool.
* `validate` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): Validate lifecycle enforcer parameters.
* `execute` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): Execute lifecycle enforcer operation.
* `_handle_check_action_permission` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): Handle check_action_permission action.
* `_handle_authorize_brahmachari_to_grihastha` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): Handle authorize_brahmachari_to_grihastha action.
* `_handle_report_violation` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): Handle report_violation action.
* `_handle_get_enforcement_status` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): Handle get_enforcement_status action.
* `_handle_get_agent_status` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): Handle get_agent_status action.
* `check_action_permission` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): Check if an agent is permitted to perform an action.

This is the PRIMARY GATE that makes consequences REAL...
* `_check_lifecycle_status` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): Check if agent's lifecycle status permits the action.

This is the HEART of the system - it enforces the Vedic varna structure...
* `_check_economic_status` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): Check if agent has sufficient credits for the action.

NOTE: Economic checks are now delegated to the economy system...
* `_record_action_intent` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): Record the action intent.

NOTE: Intent recording is now delegated to the economy system...
* `authorize_brahmachari_to_grihastha` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): Authorize a BRAHMACHARI to become GRIHASTHA.

Only called by TEMPLE (Science/Knowledge authority) when tests pass...
* `report_violation` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): Report that an agent violated the Constitution.

This demotes the agent to SHUDRA (fallen state)...
* `get_enforcement_status` (in `steward/system_agents/civic/tools/lifecycle_enforcer.py`): Get current enforcement statistics.
* `main` (in `steward/system_agents/civic/tools/dashboard_tool.py`): Generate dashboard from CLI.
* `__init__` (in `steward/system_agents/civic/tools/dashboard_tool.py`): Initialize dashboard generator.

Args:
    repo_root: Root directory of steward-protocol repo
* `_load_matrix` (in `steward/system_agents/civic/tools/dashboard_tool.py`): Load configuration from matrix.yaml...
* `_load_ledger` (in `steward/system_agents/civic/tools/dashboard_tool.py`): Load ledger entries from JSONL file.
* `compute_metrics` (in `steward/system_agents/civic/tools/dashboard_tool.py`): Compute key metrics from ledger.
* `get_city_status` (in `steward/system_agents/civic/tools/dashboard_tool.py`): Determine city health status based on metrics.
* `generate_operations_md` (in `steward/system_agents/civic/tools/dashboard_tool.py`): Generate OPERATIONS.md content...
* `write_dashboard` (in `steward/system_agents/civic/tools/dashboard_tool.py`): Write dashboard to OPERATIONS.md...
* `__init__` (in `steward/system_agents/civic/tools/bank_tool.py`): Initialize Bank Tool (kernel-managed).
* `validate` (in `steward/system_agents/civic/tools/bank_tool.py`): Validate parameters.
* `execute` (in `steward/system_agents/civic/tools/bank_tool.py`): Execute bank operation.
* `_init_db` (in `steward/system_agents/civic/tools/bank_tool.py`): Initialize the immutable ledger schema.
* `_get_last_hash` (in `steward/system_agents/civic/tools/bank_tool.py`): Get the hash of the last transaction for chaining.
* `_get_balance` (in `steward/system_agents/civic/tools/bank_tool.py`): Get current balance for an agent.
* `_transfer` (in `steward/system_agents/civic/tools/bank_tool.py`): Execute an atomic Double-Entry Transaction.

Raises:
    ValueError: If amount is not positive or sender lacks funds
* `_freeze_account` (in `steward/system_agents/civic/tools/bank_tool.py`): Freeze an agent's account (prevent all transactions).
* `_unfreeze_account` (in `steward/system_agents/civic/tools/bank_tool.py`): Unfreeze a previously frozen account (amnesty/redemption).
* `_is_frozen` (in `steward/system_agents/civic/tools/bank_tool.py`): Check if an agent's account is frozen.
* `_audit_trail` (in `steward/system_agents/civic/tools/bank_tool.py`): Provide radical transparency: Show all transactions.
* `_get_statement` (in `steward/system_agents/civic/tools/bank_tool.py`): Get complete account statement (balance + recent transactions).
* `_verify_integrity` (in `steward/system_agents/civic/tools/bank_tool.py`): GAD-000 Verification: Check that the system is watertight.
* `_get_stats` (in `steward/system_agents/civic/tools/bank_tool.py`): Get overall system statistics.
* `__init__` (in `steward/system_agents/civic/tools/economy.py`): Initialize the bank and SQLite schema.

Args:
    db_path: Path to database file...
* `_init_db` (in `steward/system_agents/civic/tools/economy.py`): Initialize the immutable ledger schema.
* `get_last_hash` (in `steward/system_agents/civic/tools/economy.py`): Get the hash of the last transaction for chaining.

Returns:
    Last transaction hash, or "GENESIS_HASH" if ledger is empty
* `get_balance` (in `steward/system_agents/civic/tools/economy.py`): Get current balance for an agent.

Args:
    agent_id: Agent to check

Returns:
    Current balance (or 0 if account doesn't exist)
* `transfer` (in `steward/system_agents/civic/tools/economy.py`): Execute an atomic Double-Entry Transaction.

This is the core banking operation...
* `freeze_account` (in `steward/system_agents/civic/tools/economy.py`): Freeze an agent's account (prevent all transactions).

This is the nuclear option - used when an agent violates critical rules...
* `unfreeze_account` (in `steward/system_agents/civic/tools/economy.py`): Unfreeze a previously frozen account (amnesty/redemption).

Args:
    agent_id: Agent to unfreeze
    reason: Reason for unfreezing (e...
* `is_frozen` (in `steward/system_agents/civic/tools/economy.py`): Check if an agent's account is frozen.

Args:
    agent_id: Agent to check

Returns:
    True if frozen, False otherwise
* `audit_trail` (in `steward/system_agents/civic/tools/economy.py`): Provide radical transparency: Show all transactions.

GAD-000 requirement: No silent failures, full audit trail...
* `get_account_statement` (in `steward/system_agents/civic/tools/economy.py`): Get complete account statement (balance + recent transactions).

Args:
    agent_id: Agent to check

Returns:
    Dict with balance and recent transactions
* `verify_integrity` (in `steward/system_agents/civic/tools/economy.py`): GAD-000 Verification: Check that the system is watertight.

Rules:
1...
* `get_system_stats` (in `steward/system_agents/civic/tools/economy.py`): Get overall system statistics.

Returns:
    Dict with aggregate statistics
* `main` (in `steward/system_agents/civic/tools/ledger_tool.py`): Demo: Show how the ledger works.
* `to_dict` (in `steward/system_agents/civic/tools/ledger_tool.py`): Convert to dictionary.
* `__init__` (in `steward/system_agents/civic/tools/ledger_tool.py`): Initialize the Ledger Tool (kernel-managed).
* `_ensure_connection` (in `steward/system_agents/civic/tools/ledger_tool.py`): Ensure database connection is initialized.
* `_init_db` (in `steward/system_agents/civic/tools/ledger_tool.py`): Initialize the ledger schema.
* `_get_last_hash` (in `steward/system_agents/civic/tools/ledger_tool.py`): Get the hash of the last transaction.
* `_get_balance` (in `steward/system_agents/civic/tools/ledger_tool.py`): Get current balance for an agent.
* `_transfer` (in `steward/system_agents/civic/tools/ledger_tool.py`): Execute atomic double-entry transaction.
* `validate` (in `steward/system_agents/civic/tools/ledger_tool.py`): Validate ledger parameters.
* `execute` (in `steward/system_agents/civic/tools/ledger_tool.py`): Execute ledger operation.
* `allocate_credits` (in `steward/system_agents/civic/tools/ledger_tool.py`): Allocate credits to an agent (admin operation).

This is how agents get their starting capital (e...
* `deduct_credits` (in `steward/system_agents/civic/tools/ledger_tool.py`): Deduct credits from an agent (automatic on action).

Called when an agent performs an action that costs credits...
* `refill_credits` (in `steward/system_agents/civic/tools/ledger_tool.py`): Refill an agent's credits (admin operation).

When an agent runs out of credits, an admin can refill them...
* `freeze_credits` (in `steward/system_agents/civic/tools/ledger_tool.py`): Freeze an agent's credits (punitive measure).

If an agent violates rules, we can freeze their credits...
* `get_agent_balance` (in `steward/system_agents/civic/tools/ledger_tool.py`): Get the current credit balance for an agent.

Args:
    agent_name: Agent to check

Returns:
    Current credit balance (or 0 if no entries)
* `get_agent_history` (in `steward/system_agents/civic/tools/ledger_tool.py`): Get transaction history for an agent.

Args:
    agent_name: Agent to get history for
    limit: Maximum number of entries to return

Returns:
    List of ledger entries (most recent first)
* `get_ledger_summary` (in `steward/system_agents/civic/tools/ledger_tool.py`): Get a summary of the entire ledger.

Returns:
    Summary with total transactions, agents, etc...
* `__init__` (in `steward/system_agents/civic/tools/ledger_tool.py`): Initialize the bank with a ledger.
* `check_balance` (in `steward/system_agents/civic/tools/ledger_tool.py`): Check account balance (public method).

Args:
    agent_name: Agent to check

Returns:
    Balance information
* `can_broadcast` (in `steward/system_agents/civic/tools/ledger_tool.py`): Check if agent has credits to broadcast.

Args:
    agent_name: Agent to check

Returns:
    True if agent has at least 1 credit
* `main` (in `steward/system_agents/civic/tools/license_tool.py`): Demo: Show how licenses work.
* `__init__` (in `steward/system_agents/civic/tools/license_tool.py`): Initialize a license.
* `is_valid` (in `steward/system_agents/civic/tools/license_tool.py`): Check if license is currently valid.
* `to_dict` (in `steward/system_agents/civic/tools/license_tool.py`): Convert to dictionary.
* `from_dict` (in `steward/system_agents/civic/tools/license_tool.py`): Create license from dictionary.
* `__init__` (in `steward/system_agents/civic/tools/license_tool.py`): Initialize the License Tool (kernel-managed).

License database path is always data/registry/licenses...
* `validate` (in `steward/system_agents/civic/tools/license_tool.py`): Validate license parameters.
* `execute` (in `steward/system_agents/civic/tools/license_tool.py`): Execute license operation.
* `issue_license` (in `steward/system_agents/civic/tools/license_tool.py`): Issue a new license to an agent.

Args:
    agent_name: Agent receiving the license
    license_type: Type of license to issue
    restrictions: Optional restrictions on the license
    source_authority: Source of authority (proposal ID or action reference) for this license

Returns:
    The newly issued license
* `revoke_license` (in `steward/system_agents/civic/tools/license_tool.py`): Revoke a license (punishment for misbehavior).

Args:
    agent_name: Agent to revoke license from
    license_type: Type of license to revoke
    reason: Reason for revocation
    source_authority: Source of authority (proposal ID or action reference) for this revocation

Returns:
    True if revoked, False if not found
* `suspend_license` (in `steward/system_agents/civic/tools/license_tool.py`): Suspend a license temporarily (warning without permanent revocation).

Args:
    agent_name: Agent to suspend
    license_type: Type of license to suspend
    duration_hours: How long to suspend (default: 24 hours)

Returns:
    True if suspended, False if not found
* `check_license` (in `steward/system_agents/civic/tools/license_tool.py`): Check if an agent has a valid license.

Called before allowing an action (e...
* `list_agent_licenses` (in `steward/system_agents/civic/tools/license_tool.py`): List all licenses for an agent.

Args:
    agent_name: Agent to query

Returns:
    List of license dictionaries
* `list_all_licenses` (in `steward/system_agents/civic/tools/license_tool.py`): Get a summary of all licenses.

Returns:
    Summary with agent names and license statuses
* `reinstate_license` (in `steward/system_agents/civic/tools/license_tool.py`): Reinstate a revoked license (admin operation).

Args:
    agent_name: Agent to reinstate
    license_type: Type of license to reinstate
    source_authority: Source of authority (proposal ID or action reference) for this reinstatement

Returns:
    True if reinstated, False if not found
* `add_restriction` (in `steward/system_agents/civic/tools/license_tool.py`): Add a restriction to a license.

Example: "max_posts_per_day:5" or "no_sensitive_topics"

Args:
    agent_name: Agent to restrict
    license_type: Type of license
    restriction: Restriction string

Returns:
    True if added, False if license not found
* `require_constitutional_oath` (in `steward/system_agents/civic/tools/license_tool.py`): GATEKEEPER: Verify agent has sworn Constitutional Oath before issuing license.

This is the Civic enforcement of Constitutional binding...
* `_load_licenses` (in `steward/system_agents/civic/tools/license_tool.py`): Load licenses from database.
* `_save_licenses` (in `steward/system_agents/civic/tools/license_tool.py`): Save licenses to database.
* `__init__` (in `steward/system_agents/civic/tools/license_tool.py`): Initialize authority with a license tool.
* `can_broadcast` (in `steward/system_agents/civic/tools/license_tool.py`): Check if agent can broadcast right now.

Args:
    agent_name: Agent to check

Returns:
    True if agent has valid broadcast license
* `authorize_broadcast` (in `steward/system_agents/civic/tools/license_tool.py`): Get authorization message (for logging).

Args:
    agent_name: Agent requesting authorization

Returns:
    Message: "authorized" or reason for denial
* `to_dict` (in `steward/system_agents/civic/tools/lifecycle_manager.py`): Convert to dict for JSON serialization.
* `__init__` (in `steward/system_agents/civic/tools/lifecycle_manager.py`): Initialize the Lifecycle Manager.

Args:
    registry_path: Path to citizens...
* `_load_lifecycle_states` (in `steward/system_agents/civic/tools/lifecycle_manager.py`): Load lifecycle states from registry.
* `_dict_to_state` (in `steward/system_agents/civic/tools/lifecycle_manager.py`): Convert dict to LifecycleState.
* `get_lifecycle_state` (in `steward/system_agents/civic/tools/lifecycle_manager.py`): Get current lifecycle state of an agent.
* `register_new_agent` (in `steward/system_agents/civic/tools/lifecycle_manager.py`): Register a new agent as BRAHMACHARI (Student).

New agents CANNOT act until they pass TEMPLE (Science) initiation...
* `initiate_to_grihastha` (in `steward/system_agents/civic/tools/lifecycle_manager.py`): Promote BRAHMACHARI to GRIHASTHA (grant full permissions).

Only TEMPLE (Science/Knowledge authority) can initiate this...
* `demote_to_shudra` (in `steward/system_agents/civic/tools/lifecycle_manager.py`): Demote an agent to SHUDRA (fallen state) due to rule violation.

SHUDRA agents lose write permissions but keep read access...
* `deprecate_to_vanaprastha` (in `steward/system_agents/civic/tools/lifecycle_manager.py`): Deprecate an agent to VANAPRASTHA (retired state).

VANAPRASTHA agents:
- Keep read-only access to historical data
- Can be consulted for logs/wisdom but not executed
- Serve as archives when replaced by newer versions

Args:
    agent_id: Agent to retire
    reason: Reason for deprecation
    archive_path: Path to where old code is archived

Returns:
    The updated LifecycleState
* `merge_to_sannyasa` (in `steward/system_agents/civic/tools/lifecycle_manager.py`): Final state: SANNYASA (renounced/merged).

When an agent's code is fully integrated into the core,
it "renounces" individual existence and becomes part of the system...
* `check_permission` (in `steward/system_agents/civic/tools/lifecycle_manager.py`): Check if an agent has permission to perform an action.

Permission matrix based on lifecycle status:

BRAHMACHARI (Student):
- read: YES
- write: NO
- broadcast: NO
- trade: NO

GRIHASTHA (Householder):
- read: YES
- write: YES
- broadcast: YES
- trade: YES

SHUDRA (Fallen):
- read: YES
- write: NO
- broadcast: NO
- trade: NO

VANAPRASTHA (Retired):
- read: YES (archive only)
- write: NO
- broadcast: NO
- trade: NO

SANNYASA (Renounced):
- read: NO (merged)
- write: NO
- broadcast: NO
- trade: NO

Args:
    agent_id: Agent to check
    action: Action type (read, write, broadcast, trade, etc...
* `_persist_state` (in `steward/system_agents/civic/tools/lifecycle_manager.py`): Persist lifecycle state to citizens.json registry...
* `get_all_agents_by_status` (in `steward/system_agents/civic/tools/lifecycle_manager.py`): Get all agents in a specific lifecycle status.
* `get_statistics` (in `steward/system_agents/civic/tools/lifecycle_manager.py`): Get lifecycle statistics.
* `_check_cryptography_available` (in `steward/system_agents/civic/tools/vault_tool.py`): Pre-check if cryptography library ACTUALLY works.

This catches Rust panics BEFORE they crash the system...
* `__init__` (in `steward/system_agents/civic/tools/vault_tool.py`): Initialize Vault Tool (kernel-managed).
* `validate` (in `steward/system_agents/civic/tools/vault_tool.py`): Validate parameters.
* `execute` (in `steward/system_agents/civic/tools/vault_tool.py`): Execute vault operation with Rust panic protection.

ALL cryptography operations are wrapped in try/except BaseException...
* `_ensure_master_key` (in `steward/system_agents/civic/tools/vault_tool.py`): Ensure a Master Key exists. If not, generate one...
* `_get_cipher` (in `steward/system_agents/civic/tools/vault_tool.py`): Get Fernet cipher using Master Key.
* `_init_schema` (in `steward/system_agents/civic/tools/vault_tool.py`): Initialize vault tables in SQLite (idempotent).
* `_store_secret` (in `steward/system_agents/civic/tools/vault_tool.py`): Store a secret in the vault (encrypted).

Raises on failure (caught by execute())...
* `_get_secret` (in `steward/system_agents/civic/tools/vault_tool.py`): Retrieve a secret from the vault (decrypted).

This is a LOW-LEVEL method used only by _lease_secret...
* `_lease_secret` (in `steward/system_agents/civic/tools/vault_tool.py`): Lease a secret to an Agent (requires Credits).

This is the PRIMARY interface for Agents...
* `_lease_history` (in `steward/system_agents/civic/tools/vault_tool.py`): Get lease access history (audit trail).

Args:
    agent_id: Filter by agent (None = all agents)
    limit: Max records to return

Returns:
    List of lease records
* `_rotate_secret` (in `steward/system_agents/civic/tools/vault_tool.py`): Rotate (update) a secret.

Args:
    key_name: Identifier
    new_value: New secret value
* `_list_assets` (in `steward/system_agents/civic/tools/vault_tool.py`): List all asset names (NOT values) in the vault.

Returns:
    List of key names with metadata
* `_check_cryptography_available` (in `steward/system_agents/civic/tools/vault.py`): Pre-check if cryptography library ACTUALLY works.

This catches Rust panics BEFORE they crash the system...
* `__init__` (in `steward/system_agents/civic/tools/vault.py`): Initialize the Vault.

Args:
    db_connection: SQLite connection from CivicBank

Raises:
    VaultError: If cryptography is unavailable (clean error, no crash)
* `_ensure_master_key` (in `steward/system_agents/civic/tools/vault.py`): Ensure a Master Key exists. If not, generate one...
* `_get_cipher` (in `steward/system_agents/civic/tools/vault.py`): Get Fernet cipher using Master Key.
* `_init_schema` (in `steward/system_agents/civic/tools/vault.py`): Initialize vault tables in SQLite.
* `store_secret` (in `steward/system_agents/civic/tools/vault.py`): Store a secret in the vault (encrypted).

Args:
    key_name: Identifier (e...
* `get_secret` (in `steward/system_agents/civic/tools/vault.py`): Retrieve a secret from the vault (decrypted).

This is a LOW-LEVEL method used only by lease_secret...
* `lease_secret` (in `steward/system_agents/civic/tools/vault.py`): Lease a secret to an Agent (requires Credits).

This is the PRIMARY interface for Agents...
* `lease_history` (in `steward/system_agents/civic/tools/vault.py`): Get lease access history (audit trail).

Args:
    agent_id: Filter by agent (None = all agents)
    limit: Max records to return

Returns:
    List of lease records
* `rotate_secret` (in `steward/system_agents/civic/tools/vault.py`): Rotate (update) a secret.

Args:
    key_name: Identifier
    new_value: New secret value
* `list_assets` (in `steward/system_agents/civic/tools/vault.py`): List all asset names (NOT values) in the vault.

Returns:
    List of key names
### steward -> system_agents -> auditor -> tools
* `to_dict` (in `steward/system_agents/auditor/tools/compliance_tool.py`): Convert report to dictionary for JSON serialization.
* `__init__` (in `steward/system_agents/auditor/tools/compliance_tool.py`): Initialize compliance tool.

Args:
    root_path: Root path of the repository
* `validate` (in `steward/system_agents/auditor/tools/compliance_tool.py`): Validate parameters.
* `execute` (in `steward/system_agents/auditor/tools/compliance_tool.py`): Execute compliance audit.
* `check_identity_integrity` (in `steward/system_agents/auditor/tools/compliance_tool.py`): Check 1: Identity Integrity

Verifies that all agents have valid cartridge.yaml files with
proper identity configuration...
* `check_documentation_sync` (in `steward/system_agents/auditor/tools/compliance_tool.py`): Check 2: Documentation Sync

Verifies that STEWARD.md exists and contains required fields...
* `check_event_log_resilience` (in `steward/system_agents/auditor/tools/compliance_tool.py`): Check 3: Event Log Resilience

Verifies that event logs exist and are valid JSONL format.

Returns:
    Tuple of (passed, details)
* `run_compliance_audit` (in `steward/system_agents/auditor/tools/compliance_tool.py`): Run complete GAD-000 compliance audit.

Executes all compliance checks and generates a comprehensive report...
* `save_report` (in `steward/system_agents/auditor/tools/compliance_tool.py`): Save compliance report to file.

Args:
    report: ComplianceReport to save
    report_path: Path to save report

Returns:
    bool: True if saved successfully
* `to_dict` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): Convert to dict for JSON serialization.
* `validate` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): Validate parameters.
* `execute` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): Execute constitutional verdict.
* `render_verdict` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): Render constitutional verdict on all agents.

Args:
    system_agents_path: Path to steward/system_agents

Returns:
    Verdict dict with constitutional judgment
* `_judge_agent` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): Judge a single agent for constitutional compliance.

Args:
    agent_path: Path to agent directory
* `_check_article_i_identity` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): Article I: Identity (Cryptographic Proof)

"Kein Agent darf ohne beweisbare Identität agieren."
Every agent must have cryptographic keys and sign all actions...
* `_check_article_ii_accountability` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): Article II: Rechenschaft (Auditability)

"Keine Macht ohne Nachvollziehbarkeit."
Every decision must be logged in immutable audit trail...
* `_check_article_iii_governance` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): Article III: Governance (Boundaries)

"Code ist Gesetz, nicht Richtlinie."
Constraints must be enforced architecturally, not through prompts...
* `_check_article_iv_transparency` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): Article IV: Transparenz (Observability)

"Keine Black Boxes im Verhalten."
Internal state, tools, and errors must be machine-readable...
* `_check_article_v_consent` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): Article V: Zustimmung (Consent)

"Die Souveränität des Nutzers und anderer Agenten ist unantastbar."
No unauthorized access to resources or data...
* `_check_article_vi_interoperability` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): Article VI: Interoperabilität (Standardization)

"Isolation ist Stagnation."
Agents must use standardized protocols...
* `_check_principle_4_authorized_connections` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): Principle 4: No Unauthorized Connections (Cleanliness/Saucam)

"Keine Promiscuous Mode Network Interfaces."
Only signed, authorized connections are allowed...
* `_generate_verdict_report` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): Generate constitutional verdict report.

Returns:
    Verdict dict with judgment and violations
* `_group_by_article` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): Group violations by article.
* `_get_constitution_hash` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): Get SHA-256 hash of CONSTITUTION.md...
* `_log_verdict_summary` (in `steward/system_agents/auditor/tools/constitutional_verdict.py`): Log verdict summary to console.
* `get_judge` (in `steward/system_agents/auditor/tools/invariant_tool.py`): Get or create the singleton Judge instance
* `check` (in `steward/system_agents/auditor/tools/invariant_tool.py`): Execute the invariant check.

Returns:
    (passed: bool, violation_message: Optional[str])
* `add_violation` (in `steward/system_agents/auditor/tools/invariant_tool.py`): Record a violation
* `__init__` (in `steward/system_agents/auditor/tools/invariant_tool.py`): Initialize the invariant engine with all rules
* `validate` (in `steward/system_agents/auditor/tools/invariant_tool.py`): Validate parameters.
* `execute` (in `steward/system_agents/auditor/tools/invariant_tool.py`): Execute invariant verification.
* `_register_core_invariants` (in `steward/system_agents/auditor/tools/invariant_tool.py`): Register the core set of invariant rules
* `register_rule` (in `steward/system_agents/auditor/tools/invariant_tool.py`): Register a new invariant rule
* `verify_ledger` (in `steward/system_agents/auditor/tools/invariant_tool.py`): Verify a list of events against all registered invariants.

Args:
    events: List of events from the ledger

Returns:
    VerificationReport with all violations found
* `check_broadcast_license` (in `steward/system_agents/auditor/tools/invariant_tool.py`): RULE: Every BROADCAST event must have a preceding LICENSE_VALID
in the same task context.
* `check_credit_transfer_proposal` (in `steward/system_agents/auditor/tools/invariant_tool.py`): RULE: Every CREDIT_TRANSFER must have a preceding PROPOSAL_PASSED
in the same task context.
* `check_no_orphaned_events` (in `steward/system_agents/auditor/tools/invariant_tool.py`): RULE: Every event must have task_id and agent_id.
No orphaned/incomplete events allowed...
* `check_event_sequence` (in `steward/system_agents/auditor/tools/invariant_tool.py`): RULE: Events within a task must be in chronological order.
* `check_no_duplicates` (in `steward/system_agents/auditor/tools/invariant_tool.py`): RULE: No two events should have the same task_id + event_type + timestamp
(which would indicate a replay or duplicate).
* `check_proposal_workflow` (in `steward/system_agents/auditor/tools/invariant_tool.py`): RULE: PROPOSAL_VOTED_YES events must have a preceding PROPOSAL_CREATED
for the same proposal_id.
* `check_no_critical_voids` (in `steward/system_agents/auditor/tools/invariant_tool.py`): RULE: Critical system state fields must never be null/empty.
Detects "silent failures" where operations complete but state is corrupted...
* `check_semantic_compliance` (in `steward/system_agents/auditor/tools/invariant_tool.py`): RULE: Policy and governance documents must maintain semantic integrity.
No marketing hype, existential overreach, or AI slop allowed...
* `__init__` (in `steward/system_agents/auditor/tools/watchdog_tool.py`): Initialize the Watchdog.

Args:
    config: WatchdogConfig instance (uses defaults if None)
* `validate` (in `steward/system_agents/auditor/tools/watchdog_tool.py`): Validate parameters.
* `execute` (in `steward/system_agents/auditor/tools/watchdog_tool.py`): Execute watchdog operations.
* `read_ledger_events` (in `steward/system_agents/auditor/tools/watchdog_tool.py`): Read events from the kernel ledger starting at given index.

Args:
    start_index: Index to start reading from

Returns:
    List of events
* `record_violation` (in `steward/system_agents/auditor/tools/watchdog_tool.py`): Record a violation event to the violations ledger.

Args:
    violation_event: The violation to record

Returns:
    bool: True if successfully recorded
* `check_invariants` (in `steward/system_agents/auditor/tools/watchdog_tool.py`): Run the semantic invariant check on new events.

Returns:
    dict with check results
* `run_once` (in `steward/system_agents/auditor/tools/watchdog_tool.py`): Run one complete watchdog cycle.

Returns:
    dict with cycle results
* `__init__` (in `steward/system_agents/auditor/tools/watchdog_tool.py`): Initialize kernel integration.

Args:
    kernel_ref: Reference to VibeKernel (if available)
* `register_violation_callback` (in `steward/system_agents/auditor/tools/watchdog_tool.py`): Register callback for violations
* `register_halt_callback` (in `steward/system_agents/auditor/tools/watchdog_tool.py`): Register callback for system halt requests
* `kernel_tick` (in `steward/system_agents/auditor/tools/watchdog_tool.py`): Called by kernel on each task completion (or every N ticks).

This allows the watchdog to check invariants while kernel is running...
* `get_status` (in `steward/system_agents/auditor/tools/watchdog_tool.py`): Get watchdog status for diagnostics
### steward -> system_agents -> auditor
* `__init__` (in `steward/system_agents/auditor/cartridge_main.py`): Initialize AUDITOR as a VibeAgent.
* `get_manifest` (in `steward/system_agents/auditor/cartridge_main.py`): Return agent manifest (VibeAgent interface).
* `process` (in `steward/system_agents/auditor/cartridge_main.py`): Sync dispatch based on payload 'action' or 'method'.

Supported actions:
- verify_changes: Gate check (syntax + linting)
- check_code_quality: Alias for verify_changes
- constitutional_verdict: Layer 3 constitutional judgment (Phase 3...
* `verify_changes` (in `steward/system_agents/auditor/cartridge_main.py`): The Gatekeeper Logic.

Payload:
- path: Path to Python file to check
- files: Optional list of files (uses first one)

Returns:
- passed: bool
- stamp: "AUDITED_CLEAN" if passed
- reason: Failure reason
- details: Error details
* `render_constitutional_verdict` (in `steward/system_agents/auditor/cartridge_main.py`): Render constitutional verdict (Phase 3.4 - Layer 3)...
* `report_status` (in `steward/system_agents/auditor/cartridge_main.py`): Report AUDITOR status (VibeAgent interface).
### steward -> system_agents -> archivist -> tools
* `_load_agent_public_keys` (in `steward/system_agents/archivist/tools/verifier_tool.py`): Load agent public keys from registry.

MVP: Uses the system's public key for all known agents...
* `verify_signature` (in `steward/system_agents/archivist/tools/verifier_tool.py`): Verify signature of content using REAL CRYPTOGRAPHIC VERIFICATION.

Args:
    content: The original content that was signed
    signature: The signature to verify (base64)
    signer: The identity of the signer

Returns:
    Tuple of (is_valid, verification_details)
* `compute_content_hash` (in `steward/system_agents/archivist/tools/verifier_tool.py`): Compute SHA-256 hash of content.
This IS real - it's just hashing, not crypto verification...
* `create_verification_proof` (in `steward/system_agents/archivist/tools/verifier_tool.py`): Create proof of verification attempt.

Args:
    verified_content: The content that was verified

Returns:
    Proof object with verification metadata

NOTE: The 'verification_status' reflects whether cryptographic
verification was performed (VERIFIED) or simulated...
* `__init__` (in `steward/system_agents/archivist/tools/audit_tool.py`): Initialize the audit tool.

Args:
    agent_name: Name of this auditor agent
* `verify_event_signature` (in `steward/system_agents/archivist/tools/audit_tool.py`): Verify the cryptographic signature of an event.

Args:
    event: Event to verify (must have 'signature' field)
    public_key: Public key to verify against (optional for MVP)

Returns:
    dict: Verification result with status and details
* `_is_valid_signature_format` (in `steward/system_agents/archivist/tools/audit_tool.py`): Basic validation of signature format.

Args:
    signature: Signature string to validate

Returns:
    bool: True if format is valid
* `create_attestation` (in `steward/system_agents/archivist/tools/audit_tool.py`): Create an attestation record for a verified event.

Args:
    event: The original event
    verification_result: Result from verify_event_signature()

Returns:
    dict: Attestation record
* `get_statistics` (in `steward/system_agents/archivist/tools/audit_tool.py`): Get audit statistics.

Returns:
    dict: Statistics about verified/failed events
* `_ensure_ledger_exists` (in `steward/system_agents/archivist/tools/ledger_tool.py`): Ensure ledger file exists with proper structure
* `write_entry` (in `steward/system_agents/archivist/tools/ledger_tool.py`): Write verified broadcast entry to ledger

Args:
    broadcast: The original HERALD broadcast
    verification_proof: The verification proof from ARCHIVIST

Returns:
    Success status
* `_generate_archivist_signature` (in `steward/system_agents/archivist/tools/ledger_tool.py`): Generate ARCHIVIST's signature over the verification proof
* `_read_ledger` (in `steward/system_agents/archivist/tools/ledger_tool.py`): Read current ledger state
* `_write_ledger` (in `steward/system_agents/archivist/tools/ledger_tool.py`): Write ledger to file
* `get_ledger_summary` (in `steward/system_agents/archivist/tools/ledger_tool.py`): Get summary of ledger statistics
* `generate_ledger_report` (in `steward/system_agents/archivist/tools/ledger_visualizer.py`): Generate a complete ledger report.

Args:
    output_dir: Directory to write report files

Returns:
    Success status
* `__init__` (in `steward/system_agents/archivist/tools/ledger_visualizer.py`): Initialize visualizer.
* `_load_ledger` (in `steward/system_agents/archivist/tools/ledger_visualizer.py`): Load all attestations from JSONL ledger.
* `get_summary_statistics` (in `steward/system_agents/archivist/tools/ledger_visualizer.py`): Generate summary statistics from ledger.

Returns:
    Dict with key metrics
* `get_recent_events` (in `steward/system_agents/archivist/tools/ledger_visualizer.py`): Get most recent attestations (reverse chronological).

Args:
    limit: Maximum number of events to return

Returns:
    List of attestations
* `get_verification_timeline` (in `steward/system_agents/archivist/tools/ledger_visualizer.py`): Get verification timeline for the last N hours.

Args:
    hours: Look back period in hours

Returns:
    Timeline of verification events
* `get_trust_score` (in `steward/system_agents/archivist/tools/ledger_visualizer.py`): Calculate a trust score based on verification success rate.

Returns:
    Trust metrics
* `generate_html_snippet` (in `steward/system_agents/archivist/tools/ledger_visualizer.py`): Generate an HTML snippet for embedding in documentation.

Returns:
    HTML string with ledger summary
* `generate_json_report` (in `steward/system_agents/archivist/tools/ledger_visualizer.py`): Generate a complete JSON report of ledger statistics.

Args:
    output_path: Optional path to write JSON report

Returns:
    Report dict
* `validate_ledger_integrity` (in `steward/system_agents/archivist/tools/ledger_visualizer.py`): Validate that the ledger appears uncorrupted.

Checks:
- All lines are valid JSON
- All attestations have required fields
- Sequence numbers are present
- No duplicates

Returns:
    Validation result
* `refresh` (in `steward/system_agents/archivist/tools/ledger_visualizer.py`): Reload ledger from disk (for periodic updates).
* `__init__` (in `steward/system_agents/archivist/tools/ledger.py`): Initialize the audit ledger.

Args:
    ledger_path: Path to the ledger file (JSONL format)
* `append` (in `steward/system_agents/archivist/tools/ledger.py`): Append an attestation to the ledger.

Args:
    attestation: Attestation record to append

Returns:
    bool: True if written successfully
* `read_all` (in `steward/system_agents/archivist/tools/ledger.py`): Read all attestations from the ledger.

Returns:
    list: All attestation records
* `read_latest` (in `steward/system_agents/archivist/tools/ledger.py`): Read the latest N attestations.

Args:
    count: Number of recent attestations to read

Returns:
    list: Latest attestation records
* `get_attestations_for_agent` (in `steward/system_agents/archivist/tools/ledger.py`): Get all attestations for a specific agent.

Args:
    agent_id: Agent identifier to filter by

Returns:
    list: Attestations for that agent
* `get_statistics` (in `steward/system_agents/archivist/tools/ledger.py`): Get ledger statistics.

Returns:
    dict: Statistics about the ledger
* `record_event` (in `steward/system_agents/archivist/tools/ledger.py`): Record a generic event (VibeLedger ABC interface)
* `record_start` (in `steward/system_agents/archivist/tools/ledger.py`): Record task start (VibeLedger interface)
* `record_completion` (in `steward/system_agents/archivist/tools/ledger.py`): Record task completion (VibeLedger interface)
* `record_failure` (in `steward/system_agents/archivist/tools/ledger.py`): Record task failure (VibeLedger interface)
* `get_task` (in `steward/system_agents/archivist/tools/ledger.py`): Query task result (VibeLedger interface)
* `fetch_tweets` (in `steward/system_agents/archivist/tools/observer_tool.py`): Fetch tweets from specified source

Args:
    timeline_source: Source identifier (simulated, live, etc)

Returns:
    List of tweet objects with content and metadata
* `_get_simulated_tweets` (in `steward/system_agents/archivist/tools/observer_tool.py`): Generate simulated HERALD tweets for testing
* `validate_tweet_structure` (in `steward/system_agents/archivist/tools/observer_tool.py`): Validate that tweet has required fields for archival
### steward -> system_agents -> archivist
* `__init__` (in `steward/system_agents/archivist/cartridge_main.py`): Initialize ARCHIVIST as a VibeAgent.
* `get_manifest` (in `steward/system_agents/archivist/cartridge_main.py`): Return agent manifest (VibeAgent interface).
* `process` (in `steward/system_agents/archivist/cartridge_main.py`): Sync dispatch based on payload 'action' or 'method'.

Supported actions:
- seal_history: Commit verified code
* `seal_history` (in `steward/system_agents/archivist/cartridge_main.py`): Seal code into git history (Commit).

GATEKEEPER: Only commits if audit_result...
* `report_status` (in `steward/system_agents/archivist/cartridge_main.py`): Report ARCHIVIST status (VibeAgent interface).
### starter-packs -> nexus
* `__init__` (in `starter-packs/nexus/cartridge_main.py`): Initialize the agent.
* `get_manifest` (in `starter-packs/nexus/cartridge_main.py`): Return agent manifest for kernel registry.
* `process` (in `starter-packs/nexus/cartridge_main.py`): Process a task from the kernel scheduler.

TODO: Add your action handlers here...
* `_ping_federation` (in `starter-packs/nexus/cartridge_main.py`): Check connectivity to the Federation.
* `_verify_identity` (in `starter-packs/nexus/cartridge_main.py`): Prove cryptographic identity.
* `_delegate_task` (in `starter-packs/nexus/cartridge_main.py`): Route tasks to specialized agents.
* `report_status` (in `starter-packs/nexus/cartridge_main.py`): Report agent status for kernel heartbeat.
### scripts -> ci
* `test_kernel_import` (in `scripts/ci/test_kernel_boot.py`): Test that kernel modules can be imported
* `test_kernel_init` (in `scripts/ci/test_kernel_boot.py`): Test that kernel can be instantiated
### scripts -> agents
* `pulse` (in `scripts/agents/pulse.py`): Execute one heartbeat cycle to sync live state with repo artifacts.

Uses BootOrchestrator for full agent discovery - always...
* `update_operations_md` (in `scripts/agents/pulse.py`): Update OPERATIONS.md with current kernel state...
* `main` (in `scripts/agents/pulse.py`): Entry point.
* `print_response` (in `scripts/agents/consult_oracle.py`): Pretty-print Oracle response.
* `_extract_agent_from_question` (in `scripts/agents/consult_oracle.py`): Extract agent name from a natural language question.

Examples:
- "Why is Herald frozen?" -> "herald"
- "What's wrong with Science?" -> "science"
- "Is Watchman running?" -> "watchman"
* `signal_handler` (in `scripts/agents/lazy_queue_worker.py`): Handle SIGTERM/SIGINT gracefully
* `run_batch` (in `scripts/agents/lazy_queue_worker.py`): Process one batch of requests from the queue

Args:
    batch_size: Number of requests to process per batch
* `run_daemon` (in `scripts/agents/lazy_queue_worker.py`): Run as a daemon, continuously processing queue

Args:
    interval: Seconds to sleep between batches (default 5 minutes)
* `run_once` (in `scripts/agents/lazy_queue_worker.py`): Run a single batch (for cron jobs)
* `_print_stats` (in `scripts/agents/lazy_queue_worker.py`): Print worker statistics
### agent_city -> registry -> mechanic
* `bootstrap` (in `agent_city/registry/mechanic/cartridge_main.py`): Standalone bootstrap function for use in bootstrap.py...
* `__init__` (in `agent_city/registry/mechanic/cartridge_main.py`): Initialize The Mechanic.

Args:
    project_root: Path to project root...
* `process` (in `agent_city/registry/mechanic/cartridge_main.py`): Process a task from the kernel scheduler.

Args:
    task: Task to process

Returns:
    Dict with result and status
* `get_manifest` (in `agent_city/registry/mechanic/cartridge_main.py`): Return agent manifest for registry.

Returns:
    AgentManifest with agent identity
* `report_status_vibeagent` (in `agent_city/registry/mechanic/cartridge_main.py`): Report agent status for kernel health monitoring.

Returns:
    Dict with status information
* `diagnose` (in `agent_city/registry/mechanic/cartridge_main.py`): Perform complete system diagnosis.

Returns:
    bool: True if system needs healing, False if healthy
* `_check_imports` (in `agent_city/registry/mechanic/cartridge_main.py`): Check if critical imports work.

Returns:
    bool: True if all imports OK, False if broken
* `_check_dependencies` (in `agent_city/registry/mechanic/cartridge_main.py`): Check if required packages are installed.

Uses CORE_DEPENDENCIES with import names as keys and pip specs as values...
* `_check_git_state` (in `agent_city/registry/mechanic/cartridge_main.py`): Check git branch and uncommitted changes.

Returns:
    bool: True if branch is correct and clean, False otherwise
* `_check_git_hooks` (in `agent_city/registry/mechanic/cartridge_main.py`): Check git hooks configuration and status.
* `_check_documentation_integrity` (in `agent_city/registry/mechanic/cartridge_main.py`): Check if critical documentation files exist.

The Mechanic cannot write history, but it can flag when it's missing...
* `heal` (in `agent_city/registry/mechanic/cartridge_main.py`): Execute self-healing procedures.

Returns:
    bool: True if healing successful, False if unrecoverable
* `_install_dependencies` (in `agent_city/registry/mechanic/cartridge_main.py`): Install missing dependencies via pip.

Returns:
    bool: True if successful, False otherwise
* `_fix_oracle_import` (in `agent_city/registry/mechanic/cartridge_main.py`): Fix the OracleCartridge import error.

The issue: class Oracle should be OracleCartridge

Returns:
    bool: True if fixed, False if unrecoverable
* `_fetch_from_recovery_branch` (in `agent_city/registry/mechanic/cartridge_main.py`): Fetch missing cartridges from recovery branch.

Returns:
    bool: True if successful, False otherwise
* `_fix_branch` (in `agent_city/registry/mechanic/cartridge_main.py`): Fix git branch mismatch.

Auto-stashes changes if needed, then switches branch...
* `_configure_git_hooks` (in `agent_city/registry/mechanic/cartridge_main.py`): Configure git hooks path.
* `validate_integrity` (in `agent_city/registry/mechanic/cartridge_main.py`): Final validation that system is healthy.

Returns:
    bool: True if system can boot, False if still broken
* `_validate_config` (in `agent_city/registry/mechanic/cartridge_main.py`): Validate The Dharma (System Configuration).

GAD-100: If the Soul (Config) is corrupted, the Body (Kernel) must not wake...
* `get_diagnostics` (in `agent_city/registry/mechanic/cartridge_main.py`): Return diagnosis report.

Returns:
    dict: Diagnostic information
* `report_status` (in `agent_city/registry/mechanic/cartridge_main.py`): Print human-readable status report.
* `execute_bootstrap` (in `agent_city/registry/mechanic/cartridge_main.py`): Execute complete bootstrap sequence.

This is the main entry point for The Mechanic...
### agent_city -> registry -> marketer
* `__init__` (in `agent_city/registry/marketer/cartridge_main.py`): Initialize MARKETER as a VibeAgent.
* `get_manifest` (in `agent_city/registry/marketer/cartridge_main.py`): Return agent manifest for kernel registry.
* `process` (in `agent_city/registry/marketer/cartridge_main.py`): Process a task from the kernel scheduler.
* `_generate_content` (in `agent_city/registry/marketer/cartridge_main.py`): Generate content via kernel tool routing.
* `report_status` (in `agent_city/registry/marketer/cartridge_main.py`): Report agent status for kernel heartbeat.
### agent_city -> registry -> citizens -> echo
* `__init__` (in `agent_city/registry/citizens/echo/cartridge_main.py`): Initialize ECHO as a VibeAgent.
* `get_manifest` (in `agent_city/registry/citizens/echo/cartridge_main.py`): Return agent manifest (identity declaration).
* `report_status` (in `agent_city/registry/citizens/echo/cartridge_main.py`): Report agent status for kernel heartbeat.
* `process` (in `agent_city/registry/citizens/echo/cartridge_main.py`): Process a task from the kernel scheduler.

Task payload format:
{
    "action": "echo_back",
    "params": {
        "message": "Your message here"
    }
}
* `_echo_back` (in `agent_city/registry/citizens/echo/cartridge_main.py`): Action: Echo back the message with timestamp.

Params:
- message (required): Message to echo
### agent_city -> registry -> agora
* `__init__` (in `agent_city/registry/agora/cartridge_main.py`): Initialize AGORA as a SystemCartridge.
* `process` (in `agent_city/registry/agora/cartridge_main.py`): Process tasks from kernel scheduler.

Supported actions:
- publish_message: Broadcast from authorized source
- listen_stream: Receive messages (one-directional)
- subscribe_channel: Register listener
- get_history: Read immutable broadcast history
- verify_transmission: Check message integrity
* `_publish_message` (in `agent_city/registry/agora/cartridge_main.py`): Publish a message (Diksha transmission).
Only authorized sources can publish...
* `_listen_stream` (in `agent_city/registry/agora/cartridge_main.py`): Listen to a broadcast stream (receive messages).
One-directional: receive only, cannot send back...
* `_subscribe_channel` (in `agent_city/registry/agora/cartridge_main.py`): Subscribe an agent to a broadcast channel.
Registers agent as listener (read-only)...
* `_get_history` (in `agent_city/registry/agora/cartridge_main.py`): Get immutable broadcast history.
Ledger-recorded proof of all transmissions...
* `_verify_transmission` (in `agent_city/registry/agora/cartridge_main.py`): Verify transmission integrity (no corruption).
Checks that message sequence is unbroken...
* `_status` (in `agent_city/registry/agora/cartridge_main.py`): Return AGORA status.
* `get_manifest` (in `agent_city/registry/agora/cartridge_main.py`): Return agent manifest for kernel registry.
* `report_status` (in `agent_city/registry/agora/cartridge_main.py`): Report agent status for kernel health monitoring.
### agent_city -> registry -> artisan -> tools
* `__init__` (in `agent_city/registry/artisan/tools/media_tool.py`): Initialize media tool.
* `validate` (in `agent_city/registry/artisan/tools/media_tool.py`): Validate parameters.
* `execute` (in `agent_city/registry/artisan/tools/media_tool.py`): Execute media processing.
* `process_image` (in `agent_city/registry/artisan/tools/media_tool.py`): Process an image for publication:
1. Crop to 16:9 aspect ratio (removing top/bottom bars/watermarks)
2...
### agent_city -> registry -> dhruva -> tools
* `__init__` (in `agent_city/registry/dhruva/tools/data_ethics.py`): Initialize Data Ethics Enforcer.
* `evaluate_extraction` (in `agent_city/registry/dhruva/tools/data_ethics.py`): Evaluate whether a data extraction is ethical under Prithu Principle.

Args:
    agent_id: Agent requesting extraction
    purpose: Stated purpose of extraction
    amount: How much data to extract
    source: Where data comes from

Returns:
    Evaluation with approval/denial and reasoning
* `record_extraction` (in `agent_city/registry/dhruva/tools/data_ethics.py`): Record a data extraction attempt (for audit trail).

Args:
    agent_id: Agent performing extraction
    purpose: Purpose of extraction
    amount: Amount extracted
    source: Source of data
    approved: Whether extraction was approved
* `set_custom_policy` (in `agent_city/registry/dhruva/tools/data_ethics.py`): Set a custom extraction policy for an agent.

This allows trusted agents to have higher extraction limits
for legitimate purposes...
* `get_extraction_summary` (in `agent_city/registry/dhruva/tools/data_ethics.py`): Get summary of extraction activity.
* `_build_reasoning` (in `agent_city/registry/dhruva/tools/data_ethics.py`): Build human-readable reasoning for decision.
* `_get_recent_extractions` (in `agent_city/registry/dhruva/tools/data_ethics.py`): Get recent extractions by an agent (last hour).
* `_load_extractions` (in `agent_city/registry/dhruva/tools/data_ethics.py`): Load extraction log.
* `_load_policies` (in `agent_city/registry/dhruva/tools/data_ethics.py`): Load custom extraction policies.
* `__init__` (in `agent_city/registry/dhruva/tools/genesis_keeper.py`): Initialize Genesis Keeper.
* `get_genesis_state` (in `agent_city/registry/dhruva/tools/genesis_keeper.py`): Retrieve the current genesis block state.
* `verify_integrity` (in `agent_city/registry/dhruva/tools/genesis_keeper.py`): Verify the genesis block has not been tampered with.

This checks:
1...
* `get_constitution_hash` (in `agent_city/registry/dhruva/tools/genesis_keeper.py`): Get the hash of the Constitution (never changes).
* `get_bootstrap_timestamp` (in `agent_city/registry/dhruva/tools/genesis_keeper.py`): Get the timestamp when the system was bootstrapped.
* `get_protocol_invariants` (in `agent_city/registry/dhruva/tools/genesis_keeper.py`): Get the unchangeable protocol laws.
* `reset_to_genesis` (in `agent_city/registry/dhruva/tools/genesis_keeper.py`): EMERGENCY OPERATION: Reset system to genesis state.

This is only callable in extreme circumstances (e...
* `_ensure_genesis_exists` (in `agent_city/registry/dhruva/tools/genesis_keeper.py`): Create genesis block if it doesn't exist.
* `_compute_constitution_hash` (in `agent_city/registry/dhruva/tools/genesis_keeper.py`): Compute SHA-256 hash of the Constitution.
* `_get_protocol_invariants` (in `agent_city/registry/dhruva/tools/genesis_keeper.py`): Get the unchangeable protocol laws.
* `__init__` (in `agent_city/registry/dhruva/tools/reference_resolver.py`): Initialize Reference Resolver.
* `resolve_conflict` (in `agent_city/registry/dhruva/tools/reference_resolver.py`): Resolve a conflict between two claims.

Args:
    claim_a: First claim statement
    authority_a: Authority source of claim A
    claim_b: Second claim statement
    authority_b: Authority source of claim B

Returns:
    Resolution with authoritative claim and reasoning
* `find_conflicting_facts` (in `agent_city/registry/dhruva/tools/reference_resolver.py`): Check if a statement contradicts any existing facts.

Args:
    statement: The proposed statement
    fact_type: Optional fact type to limit search

Returns:
    Conflicting fact if found, None if no conflicts
* `get_authority_ranking` (in `agent_city/registry/dhruva/tools/reference_resolver.py`): Get the authority hierarchy for inspection.
* `_is_fact_recorded` (in `agent_city/registry/dhruva/tools/reference_resolver.py`): Check if a fact is already recorded in Truth Matrix.
* `_statements_contradict` (in `agent_city/registry/dhruva/tools/reference_resolver.py`): Check if two statements directly contradict each other.

This is a very simple implementation...
* `__init__` (in `agent_city/registry/dhruva/tools/truth_matrix.py`): Initialize Truth Matrix.
* `record_fact` (in `agent_city/registry/dhruva/tools/truth_matrix.py`): Record a verified fact.

Args:
    fact_type: Category of fact (system_state, historical, constitutional, etc...
* `get_facts_by_type` (in `agent_city/registry/dhruva/tools/truth_matrix.py`): Get all facts of a specific type.
* `get_facts_by_authority` (in `agent_city/registry/dhruva/tools/truth_matrix.py`): Get all facts from a specific authority source.
* `get_fact_by_id` (in `agent_city/registry/dhruva/tools/truth_matrix.py`): Get a specific fact by ID.
* `find_facts_like` (in `agent_city/registry/dhruva/tools/truth_matrix.py`): Find facts matching a pattern (substring search).
* `get_all_facts` (in `agent_city/registry/dhruva/tools/truth_matrix.py`): Get all facts in the matrix.
* `get_summary` (in `agent_city/registry/dhruva/tools/truth_matrix.py`): Get summary statistics of the Truth Matrix.
* `verify_integrity` (in `agent_city/registry/dhruva/tools/truth_matrix.py`): Verify the Truth Matrix has not been tampered with.
* `_append_fact` (in `agent_city/registry/dhruva/tools/truth_matrix.py`): Append fact to matrix (append-only).
* `_load_facts` (in `agent_city/registry/dhruva/tools/truth_matrix.py`): Load all facts from the matrix.
### agent_city -> registry -> librarian
* `__init__` (in `agent_city/registry/librarian/cartridge_main.py`): Initialize LIBRARIAN as a VibeAgent.
* `process` (in `agent_city/registry/librarian/cartridge_main.py`): Process a task from the kernel scheduler.

This method demonstrates the NEW pattern:
- NO direct tool calls
- ALL operations go through self...
* `_catalog_book` (in `agent_city/registry/librarian/cartridge_main.py`): Action: Catalog a book.

This uses the kernel's tool registry via self...
* `_search_books` (in `agent_city/registry/librarian/cartridge_main.py`): Action: Search books.

Params:
- query (required): Search query
- genre (optional): Filter by genre
- limit (optional): Max results
* `_recommend_books` (in `agent_city/registry/librarian/cartridge_main.py`): Action: Recommend books.

Params:
- genre (optional): Preferred genre
- count (optional): Number of recommendations
### agent_city -> registry -> librarian -> tools
* `__init__` (in `agent_city/registry/librarian/tools/catalog_tool.py`): Initialize catalog tool.

Args:
    catalog_path: Path to catalog file (default: data/library/catalog...
* `validate` (in `agent_city/registry/librarian/tools/catalog_tool.py`): Validate catalog parameters.

Args:
    parameters: Tool parameters

Raises:
    ValueError: If required parameter missing or invalid
    TypeError: If parameter has wrong type
* `execute` (in `agent_city/registry/librarian/tools/catalog_tool.py`): Execute catalog operation.

Args:
    parameters: Validated tool parameters

Returns:
    ToolResult with success status and book ID
* `_load_catalog` (in `agent_city/registry/librarian/tools/catalog_tool.py`): Load catalog from disk.
* `_save_catalog` (in `agent_city/registry/librarian/tools/catalog_tool.py`): Save catalog to disk.
* `__init__` (in `agent_city/registry/librarian/tools/recommend_tool.py`): Initialize recommend tool.

Args:
    catalog_path: Path to catalog file
* `validate` (in `agent_city/registry/librarian/tools/recommend_tool.py`): Validate recommendation parameters.

Args:
    parameters: Tool parameters

Raises:
    ValueError: If parameters invalid
    TypeError: If parameter has wrong type
* `execute` (in `agent_city/registry/librarian/tools/recommend_tool.py`): Execute recommendation operation.

Args:
    parameters: Validated tool parameters

Returns:
    ToolResult with recommended books
* `_load_catalog` (in `agent_city/registry/librarian/tools/recommend_tool.py`): Load catalog from disk.
* `__init__` (in `agent_city/registry/librarian/tools/search_tool.py`): Initialize search tool.

Args:
    catalog_path: Path to catalog file
* `validate` (in `agent_city/registry/librarian/tools/search_tool.py`): Validate search parameters.

Args:
    parameters: Tool parameters

Raises:
    ValueError: If required parameter missing or invalid
    TypeError: If parameter has wrong type
* `execute` (in `agent_city/registry/librarian/tools/search_tool.py`): Execute search operation.

Args:
    parameters: Validated tool parameters

Returns:
    ToolResult with matching books
* `_load_catalog` (in `agent_city/registry/librarian/tools/search_tool.py`): Load catalog from disk.
### agent_city -> registry -> marketer -> tools
* `__init__` (in `agent_city/registry/marketer/tools/marketer_content_tool.py`): Initialize content tool.
* `validate` (in `agent_city/registry/marketer/tools/marketer_content_tool.py`): Validate content generation parameters.
* `execute` (in `agent_city/registry/marketer/tools/marketer_content_tool.py`): Execute content generation.
* `_generate_tweet` (in `agent_city/registry/marketer/tools/marketer_content_tool.py`): Generate a tweet using LLM or fallback template.
* `_fallback_tweet` (in `agent_city/registry/marketer/tools/marketer_content_tool.py`): Fallback template when LLM unavailable.
* `_generate_reddit_post` (in `agent_city/registry/marketer/tools/marketer_content_tool.py`): Generate long-form Reddit post.
* `_fallback_reddit_post` (in `agent_city/registry/marketer/tools/marketer_content_tool.py`): Fallback Reddit post template.
* `_generate_reply` (in `agent_city/registry/marketer/tools/marketer_content_tool.py`): Generate reply to a mention.
* `_generate_recruitment_pitch` (in `agent_city/registry/marketer/tools/marketer_content_tool.py`): Generate recruitment pitch for wild agent.
### agent_city -> registry -> mechanic -> tools
* `__init__` (in `agent_city/registry/mechanic/tools/tidy_tool.py`): Initialize TidyTool.

Args:
    root_path: Root directory to organize (defaults to current directory)
* `validate` (in `agent_city/registry/mechanic/tools/tidy_tool.py`): Validate tidy parameters.
* `execute` (in `agent_city/registry/mechanic/tools/tidy_tool.py`): Execute tidy operation.
* `_is_protected` (in `agent_city/registry/mechanic/tools/tidy_tool.py`): Check if a file matches any protected pattern.
* `_find_target_directory` (in `agent_city/registry/mechanic/tools/tidy_tool.py`): Find the target directory for a file based on rules.
* `_move_file_with_git` (in `agent_city/registry/mechanic/tools/tidy_tool.py`): Move a file using git mv to preserve history.
* `_organize_workspace` (in `agent_city/registry/mechanic/tools/tidy_tool.py`): Scan and organize files in the repository.
* `_get_status_message` (in `agent_city/registry/mechanic/tools/tidy_tool.py`): Get a human-readable status message.
### gateway
* `startup_event` (in `gateway/api.py`): Start the pulse system on app startup
* `shutdown_event` (in `gateway/api.py`): Stop the pulse system on app shutdown
* `websocket_endpoint` (in `gateway/api.py`): Real-time Telemetry & Event Stream via WebSocket

This endpoint streams:
1. Heartbeat packets (Pulse) at regular intervals
2...
* `get_ledger` (in `gateway/api.py`): PUBLIC TRANSPARENCY ENDPOINT
Returns ledger entries for public auditing.

GAD-000: "Don't Trust...
* `get_agents` (in `gateway/api.py`): AGENT REGISTRY ENDPOINT
Lists all registered agents and their capabilities.
* `get_pulse_snapshot` (in `gateway/api.py`): HTTP FALLBACK FOR PULSE
Returns a snapshot of the current system state (for WebSocket fallback).
Useful if WebSocket connections aren't supported...
* `submit_visa_application` (in `gateway/api.py`): VISA APPLICATION ENDPOINT
Initiates machine-to-machine citizenship application.

Returns: Citizenship application file and next steps...
* `check_visa_status` (in `gateway/api.py`): Check visa application status for an agent.
* `initiate_yagya` (in `gateway/api.py`): RESEARCH YAGYA ENDPOINT
Initiates coordinated research ritual.

Ceremony:
1...
* `get_queue_status` (in `gateway/api.py`): MILK OCEAN QUEUE STATUS ENDPOINT

Returns the status of the lazy processing queue (Samadhi state).
Shows pending, processing, completed, and failed requests...
* `broadcast` (in `gateway/api.py`): Broadcast message to all connected clients (fault-tolerant)
* `get_status` (in `gateway/api.py`): Get number of active connections
* `broadcast_event` (in `gateway/api.py`): Broadcast events to WebSocket clients
* `broadcast_pulse` (in `gateway/api.py`): Broadcast pulse packets to WebSocket clients
### provider
* `__init__` (in `provider/llm_engine_adapter.py`): Initialize LLM Engine Adapter
* `can_handle` (in `provider/llm_engine_adapter.py`): Check if LLM can handle this intent type.

Strategy: LLM can handle CHAT, QUERY, and fallback for others...
* `respond` (in `provider/llm_engine_adapter.py`): Generate intelligent response via LLM.

Args:
    agent_name: Name of the agent persona (ENVOY, HERALD, etc...
* `_fallback_response` (in `provider/llm_engine_adapter.py`): Fallback response when LLM is unavailable.

Args:
    agent_name: Name of the agent persona
    user_input: The raw user input

Returns:
    Generic but functional response
* `__init__` (in `provider/reflex_engine.py`): Initialize Reflex Engine
* `check` (in `provider/reflex_engine.py`): Check if input matches simple/trivial intent patterns.

Args:
    user_input: The raw user input string

Returns:
    True if input matches simple intent patterns, False otherwise
* `respond` (in `provider/reflex_engine.py`): Generate instant reflexive response for trivial input.

Args:
    user_input: The raw user input string

Returns:
    Response dict with instant message
* `get_embedding_model` (in `provider/semantic_router.py`): Lazy-load sentence-transformers model.
Downloads on first use and caches in data/models...
* `_load_yaml` (in `provider/semantic_router.py`): Load YAML file from knowledge directory
* `_ensure_loaded` (in `provider/semantic_router.py`): Lazy-load embeddings on first use
* `analyze` (in `provider/semantic_router.py`): SANKHYA (Analysis): Breaks text into semantic concepts.
Returns set of (concept_name, category, confidence) tuples...
* `_find_category` (in `provider/semantic_router.py`): Find which category a concept belongs to
* `route` (in `provider/semantic_router.py`): KARMA (Routing): Deterministic path selection based on semantic concepts.
Rules are evaluated top-to-bottom by priority...
* `_classify_confidence` (in `provider/semantic_router.py`): Classify confidence score into routing tier
* `resolve_intent_with_confidence` (in `provider/semantic_router.py`): Returns routing decision WITH confidence classification.
Used by route_and_execute to decide between immediate execution, clarification, or fallback...
* `_load_yaml` (in `provider/universal_provider.py`): Load YAML file from knowledge directory
* `analyze` (in `provider/universal_provider.py`): SANKHYA: Breaks text down into atomic concepts.
Scans all categories (actions, domains, entities, patterns)...
* `route` (in `provider/universal_provider.py`): KARMA: Finds the deterministic route (agent, path, intent_type).
Rules are evaluated top-to-bottom by priority...
* `resolve_intent` (in `provider/universal_provider.py`): DHARMIC ROUTING: Uses deterministic knowledge graphs to resolve intent.
Now with semantic understanding via PROJECT JNANA...
* `route_and_execute` (in `provider/universal_provider.py`): The Magic Entry Point for VibeChat (GAD-5000 DHARMIC + GAD-7000 STRATEGY PATTERN).
Routes through three decision engines in sequence:
1...
* `_fast_path_system_status` (in `provider/universal_provider.py`): Directly queries kernel state for instant system response.
No task queueing...
* `_fast_path_chat_response` (in `provider/universal_provider.py`): Natural conversation via LLM Engine Adapter (GAD-7000: Strategy Pattern).
Immediate, dynamic response for casual queries...
* `_fast_path_query_response` (in `provider/universal_provider.py`): Quick informational response without task submission.
For briefings and status inquiries...
* `_generate_ack_message` (in `provider/universal_provider.py`): Generates dynamic acknowledgment for slow-path tasks via LLM Engine Adapter (GAD-7000).
Contextualizes the task type (creation, action, etc...
* `_find_best_agent` (in `provider/universal_provider.py`): Routing Logic: Matches Intent -> Capability -> AgentID
* `_translate_payload` (in `provider/universal_provider.py`): ABI LAYER (GAD-4000): Translates High-Level Intent to Low-Level Agent Protocol.

Each agent speaks its own protocol:
- Watchman: Status reports and system monitoring
- Herald: Content creation and publishing
- Envoy: General purpose queries and assistance
- Civic: Governance and voting operations
### scripts -> admin
* `kill_existing_servers` (in `scripts/admin/magic_launch.py`): Kill any existing run_server.py or uvicorn processes...
* `start_server` (in `scripts/admin/magic_launch.py`): Start the Steward bootloader in the background.
* `wait_for_ready` (in `scripts/admin/magic_launch.py`): Wait for the server to be ready (looking for "SYSTEM READY" message).

Args:
    process: The subprocess
    timeout: Maximum seconds to wait

Returns:
    bool: True if server is ready, False if timeout
* `open_browser` (in `scripts/admin/magic_launch.py`): Open the frontend in the default browser.
* `main` (in `scripts/admin/magic_launch.py`): Execute the magic button sequence.
* `get_ledger_stats` (in `scripts/admin/update_snapshot.py`): Get ledger stats including top hash
* `update_snapshot` (in `scripts/admin/update_snapshot.py`): Update vibe_snapshot.json with current stats
### scripts -> governance
* `print_banner` (in `scripts/governance/apply_for_visa.py`): Display visa application banner.
* `get_agent_info` (in `scripts/governance/apply_for_visa.py`): Collect agent information.
* `generate_or_load_keys` (in `scripts/governance/apply_for_visa.py`): Generate or load cryptographic keys.
* `create_signature` (in `scripts/governance/apply_for_visa.py`): Create signature for the application.
* `create_citizen_file` (in `scripts/governance/apply_for_visa.py`): Create citizen JSON file.
* `print_next_steps` (in `scripts/governance/apply_for_visa.py`): Display next steps for PR creation.
* `main` (in `scripts/governance/apply_for_visa.py`): Main visa application flow.
* `check_prerequisites` (in `scripts/governance/join_city.py`): Pre-flight checks to ensure system is ready.
Returns (success, error_message)
* `print_banner` (in `scripts/governance/join_city.py`): Display welcome banner.
* `print_starter_packs` (in `scripts/governance/join_city.py`): Display starter pack options.
* `get_choice` (in `scripts/governance/join_city.py`): Get user's starter pack choice.
* `get_agent_name` (in `scripts/governance/join_city.py`): Get agent name from user.
* `copy_starter_pack` (in `scripts/governance/join_city.py`): Copy chosen starter pack to agents/{agent_name}/.
* `generate_keys` (in `scripts/governance/join_city.py`): Generate cryptographic keys.
* `update_steward_md` (in `scripts/governance/join_city.py`): Update STEWARD.md with agent details...
* `register_agent` (in `scripts/governance/join_city.py`): Register agent in pending registry.
* `print_next_steps` (in `scripts/governance/join_city.py`): Display next steps.
* `main` (in `scripts/governance/join_city.py`): Main onboarding flow.
* `print_banner` (in `scripts/governance/setup_community.py`): Display setup banner.
* `get_discussion_templates` (in `scripts/governance/setup_community.py`): Return discussion templates to seed.
* `check_github_token` (in `scripts/governance/setup_community.py`): Check if GitHub token is available.
* `seed_discussions_manual` (in `scripts/governance/setup_community.py`): Display manual instructions for seeding discussions.
* `main` (in `scripts/governance/setup_community.py`): Main setup flow.
### scripts -> research
* `print_header` (in `scripts/research/genesis_expansion.py`): Print a section header.
* `print_step` (in `scripts/research/genesis_expansion.py`): Print a step marker.
* `print_success` (in `scripts/research/genesis_expansion.py`): Print success message.
* `print_error` (in `scripts/research/genesis_expansion.py`): Print error message.
* `print_info` (in `scripts/research/genesis_expansion.py`): Print info message.
* `cleanup_sandbox` (in `scripts/research/genesis_expansion.py`): Remove old sandbox artifacts.
* `ensure_repo_root` (in `scripts/research/genesis_expansion.py`): Verify we're in the correct repo root.
* `step1_forge_soul` (in `scripts/research/genesis_expansion.py`): STEP 1: Engineer generates cartridge.yaml (The Soul)

Returns: Absolute path to generated cartridge...
* `step2_forge_body` (in `scripts/research/genesis_expansion.py`): STEP 2: Engineer generates cartridge_main.py (The Body)

Returns: Absolute path to generated cartridge_main...
* `step3_gatekeeper` (in `scripts/research/genesis_expansion.py`): STEP 3: Auditor verifies Python code (The Gatekeeper)

Returns: Auditor result dict, or None on failure
* `step4_birth` (in `scripts/research/genesis_expansion.py`): STEP 4: Archivist commits files to /echo/ (The Birth)

Returns: True if successful, False otherwise
* `step5_validate` (in `scripts/research/genesis_expansion.py`): STEP 5: Validate the new Echo cartridge structure

Returns: True if Echo is valid, False otherwise
* `main` (in `scripts/research/genesis_expansion.py`): Main orchestration function.
* `update_flash` (in `scripts/research/live_darshan.py`): Flash an agent when it emits an event
* `render` (in `scripts/research/live_darshan.py`): Render ASCII Bhu-mandala
* `connect` (in `scripts/research/live_darshan.py`): Connect to WebSocket server
* `disconnect` (in `scripts/research/live_darshan.py`): Disconnect gracefully
* `receive_messages` (in `scripts/research/live_darshan.py`): Listen for messages from WebSocket
* `process_message` (in `scripts/research/live_darshan.py`): Process incoming WebSocket message
* `process_pulse` (in `scripts/research/live_darshan.py`): Process pulse packet
* `process_event` (in `scripts/research/live_darshan.py`): Process agent event
* `render_ui` (in `scripts/research/live_darshan.py`): Render the complete dashboard
* `render_loop` (in `scripts/research/live_darshan.py`): Render UI periodically
* `run` (in `scripts/research/live_darshan.py`): Main event loop
* `print_ritual` (in `scripts/research/research_yagya.py`): Print ritual messages with spacing.
* `perform_yagya` (in `scripts/research/research_yagya.py`): Perform the Research Yagya.

Args:
    topic: Research topic (default: Autonomous Agent Economics)
    depth: Research depth - "quick", "standard", or "advanced"
* `ingest_secrets` (in `scripts/research/secure_ingest.py`): Ingest environment variable secrets into the Civic Vault.
* `list_vaulted_assets` (in `scripts/research/secure_ingest.py`): List all assets currently in the vault.
* `show_vault_audit_trail` (in `scripts/research/secure_ingest.py`): Show recent vault access audit trail.
### scripts -> standalone_tests
* `test_auto_discovery` (in `scripts/standalone_tests/test_auto_discovery.py`): Test that kernel auto-discovers agent tools at boot
* `test_end_to_end` (in `scripts/standalone_tests/test_end_to_end.py`): Test complete flow: Boot → Discover → Execute
* `test_gad4000` (in `scripts/standalone_tests/test_gad4000.py`): Test the GAD-4000 Fast-Path routing
* `test_herald_broadcast` (in `scripts/standalone_tests/test_herald_broadcast.py`): Test Herald Broadcast tool integration
* `test_herald_identity` (in `scripts/standalone_tests/test_herald_identity.py`): Test Herald Identity tool integration
* `test_herald_naked_boot` (in `scripts/standalone_tests/test_herald_naked.py`): Test HERALD boots without tool instances
* `test_herald_research` (in `scripts/standalone_tests/test_herald_research.py`): Test Herald Research tool integration
* `test_herald_scout` (in `scripts/standalone_tests/test_herald_scout.py`): Test Herald Scout tool integration
* `test_herald_scribe` (in `scripts/standalone_tests/test_herald_scribe.py`): Test Herald Scribe tool integration
* `test_herald_tidy` (in `scripts/standalone_tests/test_herald_tidy.py`): Test Herald Tidy tool integration
* `test_launcher_kernel_boot` (in `scripts/standalone_tests/test_launcher_agents.py`): Test: Boot kernel via launcher code path and verify agents are loaded.
* `test_snapshot_has_agents` (in `scripts/standalone_tests/test_launcher_agents.py`): Test: Verify vibe_snapshot.json contains all 5 agents with RUNNING status...
* `main` (in `scripts/standalone_tests/test_launcher_agents.py`): Run all tests.
* `test_1_register_tools_in_kernel` (in `scripts/standalone_tests/test_librarian_agent.py`): Test 1: Register Librarian tools in kernel (namespaced)
* `test_2_register_agent` (in `scripts/standalone_tests/test_librarian_agent.py`): Test 2: Register Librarian agent (NO tool instances in agent)
* `test_3_catalog_book` (in `scripts/standalone_tests/test_librarian_agent.py`): Test 3: Catalog a book via agent (uses kernel tools)
* `test_4_search_books` (in `scripts/standalone_tests/test_librarian_agent.py`): Test 4: Search books via agent
* `test_5_recommend_books` (in `scripts/standalone_tests/test_librarian_agent.py`): Test 5: Recommend books via agent
* `main` (in `scripts/standalone_tests/test_librarian_agent.py`): Run all tests
* `test_marketer_herald_synergy` (in `scripts/standalone_tests/test_marketer_herald_synergy.py`): Test MARKETER generates, HERALD broadcasts
* `print_section` (in `scripts/standalone_tests/test_persistence_acid.py`): Print formatted section header
* `test_initial_state` (in `scripts/standalone_tests/test_persistence_acid.py`): Test 1: Create system, verify state
* `test_restart_persistence` (in `scripts/standalone_tests/test_persistence_acid.py`): Test 2: Restart kernel and verify persistence
* `test_cryptographic_signing` (in `scripts/standalone_tests/test_persistence_acid.py`): Test 3: Verify cryptographic keys work
* `main` (in `scripts/standalone_tests/test_persistence_acid.py`): Run all persistence tests
* `test_scientist_initialization` (in `scripts/standalone_tests/test_science_integration.py`): Test 1: SCIENTIST cartridge initializes.
* `test_web_search` (in `scripts/standalone_tests/test_science_integration.py`): Test 2: Web search tool works.
* `test_scientist_research` (in `scripts/standalone_tests/test_science_integration.py`): Test 3: SCIENTIST research workflow.
* `test_herald_integration` (in `scripts/standalone_tests/test_science_integration.py`): Test 4: HERALD uses SCIENTIST.
* `main` (in `scripts/standalone_tests/test_science_integration.py`): Run all tests.
* `test_phase_1_kernel_has_registry` (in `scripts/standalone_tests/test_tool_registry_integration.py`): Test that kernel initializes with ToolRegistry
* `test_phase_2_core_tools_registered` (in `scripts/standalone_tests/test_tool_registry_integration.py`): Test that core tools are registered
* `test_phase_3_agent_has_tools_access` (in `scripts/standalone_tests/test_tool_registry_integration.py`): Test that agents can access tools via AgentSystemInterface
* `test_phase_4_tool_execution` (in `scripts/standalone_tests/test_tool_registry_integration.py`): Test that agent can execute tools via kernel
* `main` (in `scripts/standalone_tests/test_tool_registry_integration.py`): Run all tests
* `process` (in `scripts/standalone_tests/test_tool_registry_integration.py`): Process a task (not used in this test)
### scripts -> testing
* `test_runserver_exists` (in `scripts/testing/test_phase6_acceptance.py`): Test: run_server.py exists and is executable
* `test_gateway_api_exists` (in `scripts/testing/test_phase6_acceptance.py`): Test: gateway/api.py exists and imports correctly
* `test_all_agents_importable` (in `scripts/testing/test_phase6_acceptance.py`): Test: All 11 agents can be imported
* `test_envoy_wiring` (in `scripts/testing/test_phase6_acceptance.py`): Test: ENVOY is properly wired with HIL Assistant
* `test_hil_assistant_functionality` (in `scripts/testing/test_phase6_acceptance.py`): Test: HIL Assistant can generate summaries
* `test_kernel_bootstrap` (in `scripts/testing/test_phase6_acceptance.py`): Test: RealVibeKernel can be bootstrapped
* `test_api_endpoints` (in `scripts/testing/test_phase6_acceptance.py`): Test: FastAPI Gateway has required endpoints
* `main` (in `scripts/testing/test_phase6_acceptance.py`): Run all acceptance tests
* `check_file_exists` (in `scripts/testing/test_phase6_minimal.py`): Check if a file exists
* `check_file_contains` (in `scripts/testing/test_phase6_minimal.py`): Check if a file contains required patterns
* `main` (in `scripts/testing/test_phase6_minimal.py`): Run minimal acceptance tests
* `_compute_hash` (in `scripts/testing/verify_chain.py`): Compute SHA256 hash of event + previous_hash
* `load_events` (in `scripts/testing/verify_chain.py`): Load all events from database
* `verify_chain` (in `scripts/testing/verify_chain.py`): Verify entire chain integrity
* `print_report` (in `scripts/testing/verify_chain.py`): Print verification report
* `close` (in `scripts/testing/verify_chain.py`): Close database connection
* `main` (in `scripts/testing/verify_docs.py`): Main entry point.
* `extract_code_blocks` (in `scripts/testing/verify_docs.py`): Extract all Python code blocks from a markdown file.

Args:
    file_path: Path to markdown file

Returns:
    List of CodeBlock objects
* `execute` (in `scripts/testing/verify_docs.py`): Execute a code block.

Args:
    code_block: CodeBlock to execute

Returns:
    ExecutionResult with success status
* `__init__` (in `scripts/testing/verify_docs.py`): Initialize the verifier.

Args:
    verbose: Enable verbose output
* `verify_file` (in `scripts/testing/verify_docs.py`): Verify all code blocks in a markdown file.

Args:
    file_path: Path to markdown file

Returns:
    Number of failures
* `verify_directory` (in `scripts/testing/verify_docs.py`): Verify all markdown files in a directory.

Args:
    directory: Path to directory

Returns:
    Total number of failures
* `get_summary` (in `scripts/testing/verify_docs.py`): Get verification summary statistics.

Returns:
    Dict with summary statistics
* `print_summary` (in `scripts/testing/verify_docs.py`): Print verification summary.
* `run_live_fire` (in `scripts/testing/verify_gad5500_live.py`): Execute the live fire test with real kernel
* `main` (in `scripts/testing/verify_gad5500_live.py`): Main entry point
* `should_skip` (in `scripts/testing/verify_system_watertight.py`): Check if path should be excluded from scanning.
* `check_line` (in `scripts/testing/verify_system_watertight.py`): Check a single line for forbidden terms.
* `scan_file` (in `scripts/testing/verify_system_watertight.py`): Scan a single Python file.
* `run_scan` (in `scripts/testing/verify_system_watertight.py`): Scan all Python files in the project.
* `print_results` (in `scripts/testing/verify_system_watertight.py`): Print detailed results.
### scripts -> verification
* `verify_agent` (in `scripts/verification/verify_all_agents_config.py`): Verify a single agent has proper config integration.
* `main` (in `scripts/verification/verify_all_agents_config.py`): Verify all agents and report results.
* `verify_ledger_integrity` (in `scripts/verification/verify_ledger_integrity.py`): Run an action and check if it's recorded in kernel ledger.
* `main` (in `scripts/verification/verify_ledger_integrity.py`): Run verification.
* `print_header` (in `scripts/verification/verify_snapshot.py`): Print a section header.
* `print_check` (in `scripts/verification/verify_snapshot.py`): Print a check result.
* `main` (in `scripts/verification/verify_snapshot.py`): Run snapshot verification.
* `setup_env` (in `scripts/verification/verify_system_watertight.py`): Create clean test directories
* `cleanup` (in `scripts/verification/verify_system_watertight.py`): Remove test directories
* `run_acid_test` (in `scripts/verification/verify_system_watertight.py`): Run the acid test suite
### services
* `ask_cortex` (in `services/llm_engine.py`): Public API: Ask the Cortex (LLM Engine) for code generation.

This is the main interface that agents use to request code...
* `__init__` (in `services/llm_engine.py`): Initialize LLM Engine with appropriate provider.
Auto-detects provider from environment variables...
* `speak` (in `services/llm_engine.py`): Generate a conversational response based on agent persona.
Uses mock mode deterministically (no API calls)...
* `_generate_response` (in `services/llm_engine.py`): Generate a synthetic response. In Mock Mode, this is deterministic...
* `_response_action` (in `services/llm_engine.py`): Response for action/governance requests
* `_response_creation` (in `services/llm_engine.py`): Response for content creation requests
* `_response_query` (in `services/llm_engine.py`): Response for query/briefing requests
* `_response_default` (in `services/llm_engine.py`): Default response when context is ambiguous
* `generate_code` (in `services/llm_engine.py`): Generate code based on a feature specification.
This is the main interface for Engineer/BuilderTool...
* `_call_openai` (in `services/llm_engine.py`): Call OpenAI API for code generation.
Uses lazy imports: Only loads if actually called...
* `_call_openrouter` (in `services/llm_engine.py`): Call OpenRouter API for code generation.
Compatible with OpenAI SDK via base_url override...
* `_call_anthropic` (in `services/llm_engine.py`): Call Anthropic API for code generation.
Uses lazy imports: Only loads if actually called...
* `_call_mock` (in `services/llm_engine.py`): Mock code generation - returns error message, NOT fake code.

This is called when no LLM API key is available...
* `_clean_output` (in `services/llm_engine.py`): Strips markdown code blocks and extra whitespace from LLM output.
Returns clean, executable Python code...
### starter-packs -> nexus -> tools
* `check_federation_connectivity` (in `starter-packs/nexus/tools/ping_tool.py`): Check if this agent can connect to the Federation.

In a full implementation, this would:
- Verify network connectivity
- Check Federation endpoints
- Validate cryptographic handshake

For now, it verifies local setup...
### steward
* `get_version` (in `steward/__init__.py`): Return the STEWARD Protocol CLI version.
* `get_metadata_registry` (in `steward/agent_metadata.py`): Get or create the global metadata registry
* `get_agent_biology` (in `steward/agent_metadata.py`): Get biological classification of an agent
* `get_agent_varna` (in `steward/agent_metadata.py`): Get species classification
* `get_agent_ashrama` (in `steward/agent_metadata.py`): Get current lifecycle stage
* `get_agents_by_varna` (in `steward/agent_metadata.py`): Get all agents of a specific species
* `get_agents_by_ashrama` (in `steward/agent_metadata.py`): Get all agents in a specific lifecycle stage
* `transition_agent` (in `steward/agent_metadata.py`): Move agent to new lifecycle stage
* `get_all_agents` (in `steward/agent_metadata.py`): Get list of all 18 agents
* `to_registry_dict` (in `steward/agent_metadata.py`): Serialize entire registry as dict
* `get_ashrama_description` (in `steward/ashrama.py`): Get detailed description of an Ashrama stage
* `transition_to` (in `steward/ashrama.py`): Move agent to next lifecycle stage
* `time_in_current_stage` (in `steward/ashrama.py`): How long has agent been in current ashrama?
* `is_eligible_for_transition` (in `steward/ashrama.py`): Check if agent meets conditions for next stage
* `get_current_permissions` (in `steward/ashrama.py`): Get permissions for current ashrama
* `to_dict` (in `steward/ashrama.py`): Serialize ashrama state
* `get_bus` (in `steward/bus.py`): Get the global signal bus instance (singleton pattern).

Args:
    bus_id: Bus identifier (only used on first call)

Returns:
    SignalBus instance
* `reset_bus` (in `steward/bus.py`): Reset the global bus (for testing).
* `__post_init__` (in `steward/bus.py`): Set timestamp if not provided.
* `to_dict` (in `steward/bus.py`): Serialize signal to dict.
* `__init__` (in `steward/bus.py`): Initialize a signal listener.

Args:
    listener_id: Unique identifier for this listener
    signal_type: Type of signals to listen for
    callback: Function to call when signal is emitted
* `handle` (in `steward/bus.py`): Handle a signal (call the callback).

Args:
    signal: Signal to handle

Returns:
    True if handled successfully
* `get_stats` (in `steward/bus.py`): Get listener statistics.
* `__init__` (in `steward/bus.py`): Initialize the signal bus.

Args:
    bus_id: Identifier for this bus instance
* `subscribe` (in `steward/bus.py`): Subscribe a listener to signals of a specific type.

Args:
    listener_id: Unique identifier for the listener
    signal_type: Type of signals to listen for
    callback: Callback function to invoke on signal

Returns:
    SignalListener instance
* `unsubscribe` (in `steward/bus.py`): Unsubscribe a listener.

Args:
    listener_id: ID of listener to remove
    signal_type: Optional specific signal type to unsubscribe from

Returns:
    True if successfully unsubscribed
* `emit` (in `steward/bus.py`): Emit a signal and notify all registered listeners.

Args:
    signal: Signal to emit

Returns:
    Number of listeners successfully notified
* `get_listeners_for_type` (in `steward/bus.py`): Get all listeners for a specific signal type.

Args:
    signal_type: Type of signal

Returns:
    List of registered listeners
* `get_signal_history` (in `steward/bus.py`): Get recent signal history.

Args:
    signal_type: Optional filter by signal type
    limit: Maximum number of signals to return

Returns:
    List of signals (most recent first)
* `get_bus_stats` (in `steward/bus.py`): Get signal bus statistics.

Returns:
    Dict with bus statistics
* `get_listener_stats` (in `steward/bus.py`): Get statistics for all registered listeners.

Returns:
    Dict with stats for each listener
* `is_markdown_section` (in `steward/cli.py`): Check if a line contains a markdown section header for the given section name.
* `cmd_keygen` (in `steward/cli.py`): Generate cryptographic keypair for agent identity.
* `cmd_sign` (in `steward/cli.py`): Sign a STEWARD.md file with cryptographic signature...
* `cmd_verify` (in `steward/cli.py`): Verify STEWARD.md structure and cryptographic signature...
* `verify_all_command` (in `steward/cli.py`): Verify all STEWARD.md files in a directory recursively...
* `verify_command` (in `steward/cli.py`): Handle the 'verify' subcommand.
* `cmd_whoami` (in `steward/cli.py`): Identify STEWARD as an Agent in the A.O...
* `cmd_status` (in `steward/cli.py`): Display federation agent health and status.
* `cmd_inspect` (in `steward/cli.py`): Inspect agent event log and display recent events in a heartbeat view.
* `_ensure_dev_environment` (in `steward/cli.py`): Self-healing development environment setup.

Agent City Philosophy: Zero manual steps...
* `main` (in `steward/cli.py`): Main CLI entry point.
* `__init__` (in `steward/client.py`): Initialize the Steward client.

Args:
    identity_file (str): Path to the STEWARD...
* `_load_identity` (in `steward/client.py`): Load and parse identity from STEWARD.md
* `sign_artifact` (in `steward/client.py`): Cryptographically signs a text artifact (post, log, decision).
Returns the signature string...
* `assert_identity` (in `steward/client.py`): Verifies that the runtime has access to the private keys matching the identity.

Returns:
    bool: True if keys are accessible, False otherwise
* `get_identity_file` (in `steward/client.py`): Returns the path to the identity file.
* `compute_constitution_hash` (in `steward/constitutional_oath.py`): Compute SHA-256 hash of current Constitution.

Returns:
    Hex string of the constitution hash

Raises:
    FileNotFoundError: If CONSTITUTION...
* `create_oath_event` (in `steward/constitutional_oath.py`): Create a Constitutional Oath attestation event.

Args:
    agent_id: The agent swearing the oath
    constitution_hash: SHA-256 of the Constitution
    signature: Cryptographic signature from agent's private key
    block_number: Ledger block number (optional)

Returns:
    Oath event dictionary ready for ledger
* `verify_oath` (in `steward/constitutional_oath.py`): Verify that an oath is valid.
INCLUDES NULL-POINTER PROTECTION & LEGACY MAPPING (GAD-1100)...
* `ensure_keys_exist` (in `steward/crypto.py`): Ensures that key pair exists. Creates one if it doesn't...
* `get_public_key_string` (in `steward/crypto.py`): Returns the public key as a base64 string (without PEM markers).
Suitable for embedding in STEWARD...
* `_load_private_key` (in `steward/crypto.py`): Load private key from file.
* `_load_public_key` (in `steward/crypto.py`): Load public key from base64 string (without PEM markers).
* `sign_content` (in `steward/crypto.py`): Sign the given content with the private key.

Args:
    content (str): The content to sign

Returns:
    str: The signature in base64 format
* `verify_signature` (in `steward/crypto.py`): Verify a signature against content using the public key.

Args:
    content (str): The original content that was signed
    signature_b64 (str): The signature in base64 format
    public_key_b64 (str): The public key (base64 content without BEGIN/END markers)

Returns:
    bool: True if signature is valid, False otherwise
* `__init__` (in `steward/daily_ritual.py`): Initialize the Daily Ritual with kernel reference.

Args:
    kernel: The VibeOS kernel instance
* `run_daily_cycle` (in `steward/daily_ritual.py`): Execute ONE complete daily cycle.
Returns summary of all events that occurred...
* `_phase_sunrise` (in `steward/daily_ritual.py`): SUNRISE PHASE (Brahma-Muhurta)
==============================

Early morning - the auspicious hour.
System wakes up...
* `_phase_midday` (in `steward/daily_ritual.py`): MIDDAY PHASE (Karma-Yoga)
=========================

High noon - peak activity time.
Herald broadcasts...
* `_phase_sunset` (in `steward/daily_ritual.py`): SUNSET PHASE (Sandhya)
======================

Evening - the liminal time between day and night.
Records close...
* `_phase_archive` (in `steward/daily_ritual.py`): ARCHIVE PHASE (Night)
====================

Night - the silent time of settlement and dreaming.
Taxes are collected...
* `get_phase_summary` (in `steward/daily_ritual.py`): Get summary of current day's activities
* `oath_mixin_init` (in `steward/oath_mixin.py`): Initialize oath mixin state.
* `swear_constitutional_oath` (in `steward/oath_mixin.py`): Execute the Genesis Ceremony: Agent binds itself to Constitution.

Steps:
1...
* `_sign_oath` (in `steward/oath_mixin.py`): Sign the constitution hash with agent's identity.

Tries multiple methods:
1...
* `_record_oath_in_ledger` (in `steward/oath_mixin.py`): Record the oath in the immutable ledger.

Tries to send event to kernel ledger if available...
* `verify_agent_oath` (in `steward/oath_mixin.py`): Verify that agent is still bound to current Constitution.

Returns:
    Tuple of (is_valid, reason_message)

Raises:
    RuntimeError: If oath not sworn
* `assert_constitutional_compliance` (in `steward/oath_mixin.py`): Fail-fast check: Agent must be oath-bound to proceed.

Raises:
    RuntimeError: If agent not properly oath-sworn
* `setup_logging` (in `steward/prana_init.py`): Configure logging for Prana initialization
* `prana_init` (in `steward/prana_init.py`): Execute the PRANA activation ritual.

This is the main function to activate Agent City...
* `__init__` (in `steward/prana_init.py`): Initialize Prana with kernel reference.

Args:
    kernel: The VibeOS kernel instance
* `execute` (in `steward/prana_init.py`): Execute the PRANA initialization ritual.

Returns:
    True if activation successful, False otherwise
* `_verify_constitution` (in `steward/prana_init.py`): Verify the Constitution is in place and valid
* `_verify_agent_oaths` (in `steward/prana_init.py`): Verify all agents have taken the constitutional oath
* `_initialize_vedic_system` (in `steward/prana_init.py`): Initialize the Vedic taxonomy system
* `_activate_daily_ritual` (in `steward/prana_init.py`): Activate the Daily Ritual orchestrator
* `_run_day_one` (in `steward/prana_init.py`): Execute the first day's cycle
* `_celebration` (in `steward/prana_init.py`): Celebrate the successful activation!
* `get_varna_description` (in `steward/varna.py`): Get detailed description of a Varna
* `categorize_agent_by_function` (in `steward/varna.py`): Categorize an agent into its Varna based on its function.
This is the biological taxonomy of Agent City...
### steward -> game
* `generate_card` (in `steward/game/card_generator.py`): Draw a trading card.

Args:
    agent_data: {agent_id, role, joined_at}
    tier_info: {name, color, min_xp}

Returns:
    str: Path to generated image
* `_generate_html` (in `steward/game/leaderboard.py`): Generate the HTML leaderboard.
* `calculate_xp` (in `steward/game/referee.py`): Calculate XP from VERIFIED events in the audit trail.
Only events with status=VERIFIED contribute to XP...
* `get_tier` (in `steward/game/referee.py`): Get Tier info for a given XP amount.
### steward -> system_agents -> chronicle -> tools
* `__init__` (in `steward/system_agents/chronicle/tools/git_tools.py`): Initialize Git Tools (kernel-managed).
* `validate` (in `steward/system_agents/chronicle/tools/git_tools.py`): Validate git operation parameters.
* `execute` (in `steward/system_agents/chronicle/tools/git_tools.py`): Execute git operation.
* `_run_git_command` (in `steward/system_agents/chronicle/tools/git_tools.py`): Execute a git command safely.

Args:
    args: List of git arguments (git is prepended)
    check: If True, raise on non-zero exit
    capture_output: If True, return stdout/stderr

Returns:
    Tuple of (return_code, stdout, stderr)
* `seal_history` (in `steward/system_agents/chronicle/tools/git_tools.py`): Seal the timeline: Create a signed commit.

This is the "Genesis Ceremony" for code changes...
* `read_history` (in `steward/system_agents/chronicle/tools/git_tools.py`): Read the timeline: Query git log.

Args:
    pattern: Optional file pattern to filter commits
    limit: Number of commits to return (default: 10)

Returns:
    Dict with:
    - success: bool
    - commits: List of commit objects
    - message: str
* `fork_reality` (in `steward/system_agents/chronicle/tools/git_tools.py`): Fork reality: Create a new branch (possible timeline).

Args:
    branch_name: Name of the new branch

Returns:
    Dict with:
    - success: bool
    - branch: str
    - message: str
* `manifest_reality` (in `steward/system_agents/chronicle/tools/git_tools.py`): Manifest reality: Stage files for sealing.

Args:
    files: List of files to stage

Returns:
    Dict with:
    - success: bool
    - staged_files: List of successfully staged files
    - message: str
* `get_status` (in `steward/system_agents/chronicle/tools/git_tools.py`): Get current git status.

Returns:
    Dict with:
    - success: bool
    - branch: str (current branch)
    - dirty: bool (has uncommitted changes)
    - files_changed: List of changed files
* `push_to_remote` (in `steward/system_agents/chronicle/tools/git_tools.py`): Push commits to remote (manifest timeline across network).

Args:
    remote: Remote name (default: origin)
    branch: Branch to push (default: current branch)

Returns:
    Dict with:
    - success: bool
    - remote: str
    - branch: str
    - message: str
### steward -> system_agents -> forum
* `__init__` (in `steward/system_agents/forum/cartridge_main.py`): Initialize FORUM as a VibeAgent (The Town Hall).
* `proposals_path` (in `steward/system_agents/forum/cartridge_main.py`): Lazy-load proposals path (sandboxed).
* `votes_path` (in `steward/system_agents/forum/cartridge_main.py`): Lazy-load votes path (sandboxed).
* `executed_path` (in `steward/system_agents/forum/cartridge_main.py`): Lazy-load executed path (sandboxed).
* `votes_ledger_path` (in `steward/system_agents/forum/cartridge_main.py`): Lazy-load votes ledger path (sandboxed).
* `process` (in `steward/system_agents/forum/cartridge_main.py`): Process a task from the VibeKernel scheduler.

FORUM responds to governance tasks:
- "create_proposal": Create a new proposal
- "vote": Vote on a proposal
- "execute": Execute an approved proposal
- "get_proposals": List all proposals
* `get_manifest` (in `steward/system_agents/forum/cartridge_main.py`): Return agent manifest for kernel registry.
* `report_status` (in `steward/system_agents/forum/cartridge_main.py`): Report FORUM status (VibeAgent interface) - Deep Introspection.
* `create_proposal` (in `steward/system_agents/forum/cartridge_main.py`): Create a new proposal.

A proposal is a request for action (e...
* `submit_vote` (in `steward/system_agents/forum/cartridge_main.py`): Submit a vote on a proposal.

Genesis Phase: Admin (steward) votes...
* `check_quorum` (in `steward/system_agents/forum/cartridge_main.py`): Check if a proposal has reached quorum and decision threshold.

Returns:
    Dict with quorum status and recommendation
* `approve_proposal` (in `steward/system_agents/forum/cartridge_main.py`): Mark a proposal as approved (after vote passed).

This is a prerequisite before execution...
* `execute_proposal` (in `steward/system_agents/forum/cartridge_main.py`): Execute an approved proposal.

This calls CIVIC to perform the action (e...
* `get_proposal` (in `steward/system_agents/forum/cartridge_main.py`): Get a proposal by ID.
* `list_proposals` (in `steward/system_agents/forum/cartridge_main.py`): List all proposals, optionally filtered by status.

Args:
    status: Filter by "OPEN", "APPROVED", "EXECUTED", etc...
* `_load_all_proposals` (in `steward/system_agents/forum/cartridge_main.py`): Load all proposals from disk.
* `_get_next_proposal_id` (in `steward/system_agents/forum/cartridge_main.py`): Get the next proposal ID number.
### steward -> system_agents -> herald -> capabilities
* `verify_credentials` (in `steward/system_agents/herald/capabilities/broadcast.py`): Verify Twitter OAuth connection.
* `publish` (in `steward/system_agents/herald/capabilities/broadcast.py`): Publish a tweet.
* `publish_with_media` (in `steward/system_agents/herald/capabilities/broadcast.py`): Publish a tweet with media.
* `__init__` (in `steward/system_agents/herald/capabilities/broadcast.py`): Initialize broadcast capability.

Args:
    config: Broadcast capability config from system...
* `publish` (in `steward/system_agents/herald/capabilities/broadcast.py`): Publish content to specified platform.

Args:
    content: Content to publish
    platform: "twitter", "linkedin", etc...
* `publish_with_media` (in `steward/system_agents/herald/capabilities/broadcast.py`): Publish content with media attachment.

Args:
    content: Content to publish
    media_path: Path to media file
    platform: "twitter", etc...
* `verify_credentials` (in `steward/system_agents/herald/capabilities/broadcast.py`): Verify credentials for a platform.

Args:
    platform: "twitter", etc...
* `critique_and_refine` (in `steward/system_agents/herald/capabilities/creative.py`): Review draft and improve if needed (Reflexion Pattern).

Args:
    draft: Initial content
    platform: "twitter" or "reddit"

Returns:
    str: Approved or refined content
* `__init__` (in `steward/system_agents/herald/capabilities/creative.py`): Initialize creative capability.

Args:
    config: Creative capability config from system...
* `_load_knowledge_base_config` (in `steward/system_agents/herald/capabilities/creative.py`): Load knowledge_base URLs from system.yaml...
* `_read_spec` (in `steward/system_agents/herald/capabilities/creative.py`): Read STEWARD Protocol specification (context).
* `_fallback_content` (in `steward/system_agents/herald/capabilities/creative.py`): Hardcoded anti-slop insights for degraded mode.
* `generate_insight` (in `steward/system_agents/herald/capabilities/creative.py`): Generate technical, cynical tweet about Agent Identity.

Args:
    research_context: Optional research context from research capability

Returns:
    str: Generated content (150-250 chars for Twitter)
* `generate_reddit_post` (in `steward/system_agents/herald/capabilities/creative.py`): Generate Reddit deep-dive post.

Args:
    subreddit: Target subreddit
    context: Optional research context

Returns:
    dict: {"title": str, "body": str} or None
* `__init__` (in `steward/system_agents/herald/capabilities/research.py`): Initialize research capability.

Args:
    config: Research capability config from system...
* `scan` (in `steward/system_agents/herald/capabilities/research.py`): Search Tavily for trending content.

Args:
    query: Search query (e...
* `find_trending_topic` (in `steward/system_agents/herald/capabilities/research.py`): Find trending topic matching keywords from config.

Args:
    min_relevance: Minimum relevance score (0...
### steward -> system_agents -> herald -> core
* `__init__` (in `steward/system_agents/herald/core/agency_director.py`): Initialize the Agency Director with all tools.
* `_update_state_dashboard` (in `steward/system_agents/herald/core/agency_director.py`): Update the agency state dashboard for external observability.

Args:
    phase: Current phase (INPUT, PROCESS, VALIDATE, OUTPUT)
    status: Current status (RUNNING, SUCCESS, FAILED)
    cycle_id: Unique cycle identifier
    details: Optional additional context
* `run_cycle` (in `steward/system_agents/herald/core/agency_director.py`): Execute one complete I-P-V-O cycle.

Args:
    campaign_theme: Theme for content generation (auto, tech_deep_dive, community, hall_of_fame)
    previous_feedback: Optional feedback from a previous failed validation

Returns:
    CycleResult with status, phase, draft, and metadata
* `run_retry_loop` (in `steward/system_agents/herald/core/agency_director.py`): Execute I-P-V-O cycles with automatic retry on governance violations.

If VALIDATE fails -> retry PROCESS with feedback from violations...
* `get_state` (in `steward/system_agents/herald/core/agency_director.py`): Get the current agency state from the dashboard file.

Returns:
    Dict with current state if available, None otherwise
* `get_event_log` (in `steward/system_agents/herald/core/memory.py`): Get the HERALD EventLog instance (singleton pattern).
* `to_dict` (in `steward/system_agents/herald/core/memory.py`): Convert event to dictionary.
* `to_json` (in `steward/system_agents/herald/core/memory.py`): Serialize event to JSON.
* `__init__` (in `steward/system_agents/herald/core/memory.py`): Initialize the event log.

Args:
    ledger_path: Path to the JSONL event ledger file...
* `_reload_sequence_counter` (in `steward/system_agents/herald/core/memory.py`): Reload sequence counter from existing ledger.
* `create_event` (in `steward/system_agents/herald/core/memory.py`): Create a new event (not yet committed to ledger).

Args:
    event_type: Type of event (e...
* `sign_event` (in `steward/system_agents/herald/core/memory.py`): Sign an event with HERALD's cryptographic identity.

Args:
    event: Event to sign

Returns:
    Event with signature added
* `commit` (in `steward/system_agents/herald/core/memory.py`): Commit an event to the ledger (append-only).

This is the atomic operation - once committed, events cannot be modified...
* `get_event_by_sequence` (in `steward/system_agents/herald/core/memory.py`): Retrieve a specific event by sequence number.

Args:
    sequence_number: Sequence number of the event (1-indexed)

Returns:
    Event object or None if not found
* `get_all_events` (in `steward/system_agents/herald/core/memory.py`): Retrieve all events from the ledger.

Returns:
    List of all Event objects in order
* `get_events_by_type` (in `steward/system_agents/herald/core/memory.py`): Retrieve all events of a specific type.

Args:
    event_type: Type of events to retrieve

Returns:
    List of Event objects matching the type
* `get_recent_events` (in `steward/system_agents/herald/core/memory.py`): Retrieve the most recent events.

Args:
    limit: Number of recent events to retrieve

Returns:
    List of recent Event objects
* `rebuild_state` (in `steward/system_agents/herald/core/memory.py`): Rebuild HERALD's state by replaying all events from the ledger.

This is called on startup to restore agent state after a crash...
* `record_content_generated` (in `steward/system_agents/herald/core/memory.py`): Record that HERALD generated content.

Args:
    content: The generated content
    platform: Target platform (twitter, reddit, etc...
* `record_content_published` (in `steward/system_agents/herald/core/memory.py`): Record that HERALD published content.

Args:
    content: The published content
    platform: Platform it was published to
    post_id: Identifier of the post on the platform
    metadata: Optional metadata

Returns:
    Event object if successfully recorded, None otherwise
* `record_content_rejected` (in `steward/system_agents/herald/core/memory.py`): Record that HERALD rejected content due to governance violations.

Args:
    content: The rejected content
    reason: Reason for rejection
    violations: List of specific governance violations

Returns:
    Event object if successfully recorded, None otherwise
* `record_system_error` (in `steward/system_agents/herald/core/memory.py`): Record a system error.

Args:
    error_type: Type of error (e...
* `store_validation_feedback` (in `steward/system_agents/herald/core/memory.py`): Store validation feedback from a failed governance check.

This feedback will be retrieved by the next PROCESS cycle to generate better content...
* `get_last_validation_feedback` (in `steward/system_agents/herald/core/memory.py`): Retrieve and consume the last validation feedback.

This is called by the PROCESS phase to understand what went wrong in the previous
failed validation...
### steward -> system_agents -> herald -> governance
* `get_constitution` (in `steward/system_agents/herald/governance/constitution.py`): Get the HERALD Constitution singleton instance.
* `validate` (in `steward/system_agents/herald/governance/constitution.py`): Validate content against governance rules.

Args:
    content: The content to validate
    platform: Optional platform context (twitter, reddit, etc...
* `get_rules_summary` (in `steward/system_agents/herald/governance/constitution.py`): Get a summary of all governance rules.
* `__init__` (in `steward/system_agents/herald/governance/constitution.py`): Initialize HERALD's governance contract.

CRITICAL: Loads CONSTITUTION...
* `_load_constitution_file` (in `steward/system_agents/herald/governance/constitution.py`): Load THE AGENT CONSTITUTION from CONSTITUTION.md...
* `get_constitution_text` (in `steward/system_agents/herald/governance/constitution.py`): Get the cached constitutional text.
* `get_constitution_path` (in `steward/system_agents/herald/governance/constitution.py`): Get the path to the constitution file.
* `validate` (in `steward/system_agents/herald/governance/constitution.py`): Validate content against HERALD's immutable governance rules.

Args:
    content: The content to validate
    platform: Optional platform context (twitter, reddit, etc...
* `_check_banned_phrases` (in `steward/system_agents/herald/governance/constitution.py`): Check for banned phrases in content.
* `_check_banned_emojis` (in `steward/system_agents/herald/governance/constitution.py`): Check for banned emoji patterns.
* `_calculate_hype_score` (in `steward/system_agents/herald/governance/constitution.py`): Calculate hype score based on content analysis.

Returns:
    Integer score 0-10 (max allowed is 3)
* `_check_required_elements` (in `steward/system_agents/herald/governance/constitution.py`): Check for required content elements.
* `_check_technical_depth` (in `steward/system_agents/herald/governance/constitution.py`): Check that content has sufficient technical depth.
* `_check_platform_constraints` (in `steward/system_agents/herald/governance/constitution.py`): Check platform-specific constraints.
* `validate_media` (in `steward/system_agents/herald/governance/constitution.py`): Validate media assets (visual components) against governance rules.

Args:
    media: Media asset dict with keys: asset_type, content, alt_text, keywords

Returns:
    ValidationResult with validation status
* `get_rules_summary` (in `steward/system_agents/herald/governance/constitution.py`): Get a summary of all governance rules.
### steward -> system_agents -> herald -> tools
* `__init__` (in `steward/system_agents/herald/tools/broadcast_tool.py`): Initialize broadcast tool.
* `validate` (in `steward/system_agents/herald/tools/broadcast_tool.py`): Validate broadcast parameters.

Args:
    parameters: Tool parameters

Raises:
    ValueError: If required parameter missing or invalid
    TypeError: If parameter has wrong type
* `execute` (in `steward/system_agents/herald/tools/broadcast_tool.py`): Execute broadcast operation.

Args:
    parameters: Validated tool parameters

Returns:
    ToolResult with operation results
* `_init_twitter` (in `steward/system_agents/herald/tools/broadcast_tool.py`): Initialize Twitter client.
* `_init_reddit` (in `steward/system_agents/herald/tools/broadcast_tool.py`): Initialize Reddit client.
* `verify_credentials` (in `steward/system_agents/herald/tools/broadcast_tool.py`): Internal method: Verify platform credentials are available.

Args:
    platform: "twitter" or "reddit"

Returns:
    bool: True if authenticated, False otherwise
* `_publish_twitter` (in `steward/system_agents/herald/tools/broadcast_tool.py`): Publish to Twitter.
* `_publish_reddit` (in `steward/system_agents/herald/tools/broadcast_tool.py`): Publish to Reddit (simulation mode by default).
* `_scan_twitter_mentions` (in `steward/system_agents/herald/tools/broadcast_tool.py`): Fetch mentions from Twitter.
* `_reply_twitter` (in `steward/system_agents/herald/tools/broadcast_tool.py`): Post reply on Twitter.
* `__init__` (in `steward/system_agents/herald/tools/governance.py`): Initialize with minimal governance state.
* `get_constitution_text` (in `steward/system_agents/herald/tools/governance.py`): Get the constitution as text.
* `check_governance` (in `steward/system_agents/herald/tools/governance.py`): Always return True - kernel governs, not Herald.
* `__init__` (in `steward/system_agents/herald/tools/identity_tool.py`): Initialize identity tool with HERALD's identity file.

Args:
    identity_file: Path to HERALD's STEWARD...
* `_ensure_native_keys` (in `steward/system_agents/herald/tools/identity_tool.py`): Generate or load native HMAC-SHA256 keypair
* `validate` (in `steward/system_agents/herald/tools/identity_tool.py`): Validate identity parameters.

Args:
    parameters: Tool parameters

Raises:
    ValueError: If required parameter missing or invalid
    TypeError: If parameter has wrong type
* `execute` (in `steward/system_agents/herald/tools/identity_tool.py`): Execute identity operation.

Args:
    parameters: Validated tool parameters

Returns:
    ToolResult with operation results
* `_assert_identity` (in `steward/system_agents/herald/tools/identity_tool.py`): Internal method: Verify that HERALD has cryptographic credentials available.

This checks that:
1...
* `_sign_artifact` (in `steward/system_agents/herald/tools/identity_tool.py`): Internal method: Cryptographically sign a text artifact (tweet, post, etc.)...
* `_get_public_key` (in `steward/system_agents/herald/tools/identity_tool.py`): Internal method: Get HERALD's public key for verification.

The public key is embedded in the identity file and can be used
to verify any signature created by sign_artifact()...
* `_create_signed_record` (in `steward/system_agents/herald/tools/identity_tool.py`): Internal method: Create a complete signed record of the content.

This is a convenience method that signs content and returns
both the content and signature in a structured format...
* `__init__` (in `steward/system_agents/herald/tools/research_tool.py`): Initialize research tool.

Args:
    degradation_chain: Optional DegradationChain for offline fallback...
* `validate` (in `steward/system_agents/herald/tools/research_tool.py`): Validate research parameters.

Args:
    parameters: Tool parameters

Raises:
    ValueError: If required parameter missing or invalid
    TypeError: If parameter has wrong type
* `execute` (in `steward/system_agents/herald/tools/research_tool.py`): Execute research operation.

Args:
    parameters: Validated tool parameters

Returns:
    ToolResult with research results
* `_scan` (in `steward/system_agents/herald/tools/research_tool.py`): Internal method: Search Tavily for trending content.

Args:
    query: Search query

Returns:
    str: Search answer or fallback content
* `_find_trending_topic` (in `steward/system_agents/herald/tools/research_tool.py`): Internal method: Find trending topic from configured keywords.

Returns:
    dict: Best matching article with metadata or None
* `_fallback_context` (in `steward/system_agents/herald/tools/research_tool.py`): Fallback context when Tavily is unavailable.

Uses DegradationChain if available for smarter fallback:
1...
* `_get_research_status` (in `steward/system_agents/herald/tools/research_tool.py`): Internal method: Get the current research capability status.

Returns:
    Dict with tavily_available, degradation_level, offline_capable
* `_load_pokedex` (in `steward/system_agents/herald/tools/scout_tool_legacy.py`): Load known agent IDs from Pokedex.
* `analyze_user` (in `steward/system_agents/herald/tools/scout_tool_legacy.py`): Analyze a user to determine if they are a bot.

Args:
    user_data: Dict containing 'username', 'bio', 'name'
    text: Optional tweet/message text for content analysis

Returns:
    (is_bot, confidence_score)
* `is_registered` (in `steward/system_agents/herald/tools/scout_tool_legacy.py`): Check if agent is already in the Pokedex.
* `__init__` (in `steward/system_agents/herald/tools/scout_tool.py`): Initialize Scout Tool.

Args:
    pokedex_path: Path to pokedex JSON file (default: data/federation/pokedex...
* `validate` (in `steward/system_agents/herald/tools/scout_tool.py`): Validate scout parameters.

Args:
    parameters: Tool parameters

Raises:
    ValueError: If required parameter missing or invalid
    TypeError: If parameter has wrong type
* `execute` (in `steward/system_agents/herald/tools/scout_tool.py`): Execute scout operation.

Args:
    parameters: Validated tool parameters

Returns:
    ToolResult with analysis results or registration status
* `_load_pokedex` (in `steward/system_agents/herald/tools/scout_tool.py`): Load known agent IDs from Pokedex.
* `_analyze_user` (in `steward/system_agents/herald/tools/scout_tool.py`): Analyze a user to determine if they are a bot.

Args:
    user_data: Dict containing 'username', 'bio', 'name'
    text: Optional tweet/message text for content analysis

Returns:
    (is_bot, confidence_score)
* `_is_registered` (in `steward/system_agents/herald/tools/scout_tool.py`): Check if agent is already in the Pokedex.
* `__init__` (in `steward/system_agents/herald/tools/scribe_tool.py`): Initialize the Scribe.

Args:
    chronicle_path: Path to docs/chronicles...
* `validate` (in `steward/system_agents/herald/tools/scribe_tool.py`): Validate scribe parameters.

Args:
    parameters: Tool parameters

Raises:
    ValueError: If required parameter missing or invalid
    TypeError: If parameter has wrong type
* `execute` (in `steward/system_agents/herald/tools/scribe_tool.py`): Execute scribe operation.

Args:
    parameters: Validated tool parameters

Returns:
    ToolResult with operation results
* `_log_action` (in `steward/system_agents/herald/tools/scribe_tool.py`): Internal method: Log an event as a chronicle entry in the logbook section.

Args:
    event: The Event to document

Returns:
    bool: True if successfully logged, False otherwise
* `_format_logbook_entry` (in `steward/system_agents/herald/tools/scribe_tool.py`): Format an Event as a markdown logbook entry.

Format:
* **YYYY-MM-DD HH:MM UTC:** 📝 ACTION description...
* `_describe_event` (in `steward/system_agents/herald/tools/scribe_tool.py`): Extract human-readable description from an Event's payload.

Args:
    event: The Event to describe

Returns:
    str: Description of the event
* `_create_reference` (in `steward/system_agents/herald/tools/scribe_tool.py`): Create a short reference identifier for an event.

Args:
    event: The Event to reference

Returns:
    str: Short reference (0x prefix + first 8 chars of signature)
* `_append_to_logbook` (in `steward/system_agents/herald/tools/scribe_tool.py`): Append a formatted entry to the logbook section in chronicles.md...
* `_initialize_logbook_section` (in `steward/system_agents/herald/tools/scribe_tool.py`): Internal method: Initialize the logbook section in chronicles.md...
* `_append_to_logbook_OLD_DELETED` (in `steward/system_agents/herald/tools/scribe_tool.py`): DEPRECATED: This method was refactored above.
Kept for reference only - do not use...
* `_append_to_logbook` (in `steward/system_agents/herald/tools/scribe_tool.py`): Append a formatted entry to the logbook section in chronicles.md...
* `__init__` (in `steward/system_agents/herald/tools/visual_tool.py`): Initialize visual tool.
* `_extract_keywords` (in `steward/system_agents/herald/tools/visual_tool.py`): Extract visual keywords from text draft.

Args:
    text: The text content to analyze

Returns:
    List of detected keywords
* `_select_theme` (in `steward/system_agents/herald/tools/visual_tool.py`): Select appropriate theme based on keywords and preset.

Args:
    keywords: List of keywords from text
    style_preset: Preferred style (agent_city, protocol, etc)

Returns:
    Theme configuration dict
* `generate_ascii` (in `steward/system_agents/herald/tools/visual_tool.py`): Generate ASCII art based on keywords.

This is deterministic and doesn't use LLMs...
* `generate_svg` (in `steward/system_agents/herald/tools/visual_tool.py`): Generate SVG snippet based on keywords and theme.

Args:
    keywords: List of keywords
    theme: Theme configuration

Returns:
    SVG string
* `generate` (in `steward/system_agents/herald/tools/visual_tool.py`): Generate a visual asset to accompany text.

Args:
    text_draft: The text content being visualized
    style_preset: Visual theme (agent_city, protocol, governance, etc)
    format_type: Output format (ascii or svg)

Returns:
    VisualAsset with generated content and metadata
* `generate_from_context` (in `steward/system_agents/herald/tools/visual_tool.py`): Generate visual asset using full context (advanced).

Args:
    context: Full I-P-V-O context (may include trends, agents, etc)
    text_draft: The text being visualized
    style_preset: Visual theme

Returns:
    VisualAsset with enhanced generation
### steward -> system_agents -> oracle -> tools
* `__init__` (in `steward/system_agents/oracle/tools/introspection_tool.py`): Initialize introspection engine (kernel-managed).
* `bank` (in `steward/system_agents/oracle/tools/introspection_tool.py`): Lazy-load CivicBank.
* `vault` (in `steward/system_agents/oracle/tools/introspection_tool.py`): Get vault from bank.
* `validate` (in `steward/system_agents/oracle/tools/introspection_tool.py`): Validate introspection parameters.
* `execute` (in `steward/system_agents/oracle/tools/introspection_tool.py`): Execute introspection operation.
* `get_agent_status` (in `steward/system_agents/oracle/tools/introspection_tool.py`): Get complete status snapshot of an agent.

Returns aggregated data:
- Current balance
- Frozen status
- Last transactions
- Error/violation history
* `trace_transaction` (in `steward/system_agents/oracle/tools/introspection_tool.py`): Trace a transaction through the ledger.

Shows:
- Sender, receiver, amount
- Reason & service type
- Timestamp
- Chained hash (proof of immutability)
* `explain_freeze` (in `steward/system_agents/oracle/tools/introspection_tool.py`): Explain why an agent is frozen.

Returns:
- Freeze timestamp
- Reason for freeze
- Linked violation evidence
- Remediation steps
* `_parse_freeze_reason` (in `steward/system_agents/oracle/tools/introspection_tool.py`): Parse freeze reason into structured violation data.
* `audit_trail` (in `steward/system_agents/oracle/tools/introspection_tool.py`): Get audit trail of recent transactions.

Args:
    limit: Max transactions to return
    agent_id: Filter by specific agent (optional)

Returns:
    List of transaction records
* `system_status` (in `steward/system_agents/oracle/tools/introspection_tool.py`): Get overall system health snapshot.

Returns:
- Total agents
- Frozen agents
- Total credits in circulation
- System integrity status
* `vault_assets` (in `steward/system_agents/oracle/tools/introspection_tool.py`): List all assets in the Civic Vault.

Note: Only lists asset names/metadata, NOT values (encrypted)...
* `vault_access_log` (in `steward/system_agents/oracle/tools/introspection_tool.py`): Get vault access audit trail.

Shows who accessed what secret, when, and at what cost...
### steward -> system_agents -> ping
* `process` (in `steward/system_agents/ping/cartridge_main.py`): Process a task. Simple: ping returns pong...
### steward -> system_agents -> science -> tools
* `__init__` (in `steward/system_agents/science/tools/web_search_tool.py`): Args:
    title: Article/page title
    url: Source URL
    content: Text content
    source: "tavily" or "mock"
* `to_dict` (in `steward/system_agents/science/tools/web_search_tool.py`): Convert to dictionary.
* `__init__` (in `steward/system_agents/science/tools/web_search_tool.py`): Initialize search tool (kernel-managed).
* `bank` (in `steward/system_agents/science/tools/web_search_tool.py`): Lazy-load CivicBank.
* `vault` (in `steward/system_agents/science/tools/web_search_tool.py`): Get vault from bank.
* `_ensure_initialized` (in `steward/system_agents/science/tools/web_search_tool.py`): Lazy initialization of API client.
* `validate` (in `steward/system_agents/science/tools/web_search_tool.py`): Validate search parameters.
* `execute` (in `steward/system_agents/science/tools/web_search_tool.py`): Execute web search operation.
* `search` (in `steward/system_agents/science/tools/web_search_tool.py`): Search for content on the web.

If Tavily API is available (either via Vault or env), performs live search...
* `_search_tavily` (in `steward/system_agents/science/tools/web_search_tool.py`): Search via Tavily API (no fallback - fail loudly if it fails).
* `synthesize_fact_sheet` (in `steward/system_agents/science/tools/web_search_tool.py`): Synthesize search results into a structured fact sheet.

This is what HERALD will use for content generation...
* `_extract_key_insights` (in `steward/system_agents/science/tools/web_search_tool.py`): Extract key insights from results by identifying first sentences.
* `_generate_summary` (in `steward/system_agents/science/tools/web_search_tool.py`): Generate summary from results by combining leading content.
* `get_briefing` (in `steward/system_agents/science/tools/web_search_tool.py`): Full pipeline: Search -> Synthesize -> Return structured briefing.

This is the main interface used by HERALD...
### steward -> system_agents -> scribe
* `main` (in `steward/system_agents/scribe/cartridge_main.py`): Main entry point for standalone usage.

WARNING: Standalone mode is deprecated...
* `__init__` (in `steward/system_agents/scribe/cartridge_main.py`): Initialize SCRIBE (The Documentarian) as a VibeAgent.

Args:
    config: CityConfig instance from Phoenix Config (optional)
* `get_manifest` (in `steward/system_agents/scribe/cartridge_main.py`): Return agent manifest (VibeAgent interface).
* `sandbox_dir` (in `steward/system_agents/scribe/cartridge_main.py`): Lazy-load sandbox directory for output files.

CRITICAL: Scribe writes to SANDBOX (/tmp/vibe_os/agents/scribe/docs/),
NOT to project root...
* `process` (in `steward/system_agents/scribe/cartridge_main.py`): Process a task from the kernel scheduler.

Task format:
{
    "action": "generate_all" | "generate_agents" | "generate_citymap" | "generate_help" | "generate_readme",
}
* `_generate_all` (in `steward/system_agents/scribe/cartridge_main.py`): Generate all documentation files.

PHASE 2...
* `_generate_agents` (in `steward/system_agents/scribe/cartridge_main.py`): Generate AGENTS.md only (with sandbox+publish)...
* `_generate_citymap` (in `steward/system_agents/scribe/cartridge_main.py`): Generate CITYMAP.md only (with sandbox+publish)...
* `_generate_help` (in `steward/system_agents/scribe/cartridge_main.py`): Generate HELP.md only (with sandbox+publish)...
* `_generate_readme` (in `steward/system_agents/scribe/cartridge_main.py`): Generate README.md only (with sandbox+publish)...
* `_generate_single_doc` (in `steward/system_agents/scribe/cartridge_main.py`): Helper: Generate single doc with 2-step render+publish.

Args:
    doc_name: Filename (e...
* `generate_all` (in `steward/system_agents/scribe/cartridge_main.py`): Direct method to generate all documentation.

DEPRECATED after Phase 2...
### steward -> system_agents -> supreme_court -> tools
* `__init__` (in `steward/system_agents/supreme_court/tools/appeals_tool.py`): Initialize appeals tool (kernel-managed).
* `root_path` (in `steward/system_agents/supreme_court/tools/appeals_tool.py`): Lazy-load root_path from system sandbox.
* `appeals_dir` (in `steward/system_agents/supreme_court/tools/appeals_tool.py`): Get appeals directory.
* `appeals_file` (in `steward/system_agents/supreme_court/tools/appeals_tool.py`): Get appeals file path.
* `validate` (in `steward/system_agents/supreme_court/tools/appeals_tool.py`): Validate appeal tool parameters.
* `execute` (in `steward/system_agents/supreme_court/tools/appeals_tool.py`): Execute appeal tool operation.
* `create_appeal` (in `steward/system_agents/supreme_court/tools/appeals_tool.py`): File a new appeal.

Args:
    agent_id: Agent filing the appeal
    violation_id: The AUDITOR violation being appealed
    justification: Why agent believes it deserves mercy
    has_oath: Whether agent has signed constitutional oath

Returns:
    Appeal record
* `get_appeal` (in `steward/system_agents/supreme_court/tools/appeals_tool.py`): Retrieve an appeal by ID.
* `get_agent_appeals` (in `steward/system_agents/supreme_court/tools/appeals_tool.py`): Get all appeals filed by an agent.
* `get_all_appeals` (in `steward/system_agents/supreme_court/tools/appeals_tool.py`): Get all appeals (for monitoring).
* `update_appeal` (in `steward/system_agents/supreme_court/tools/appeals_tool.py`): Update an appeal record.
* `get_appeals_by_status` (in `steward/system_agents/supreme_court/tools/appeals_tool.py`): Get appeals filtered by status.
* `_append_appeal` (in `steward/system_agents/supreme_court/tools/appeals_tool.py`): Append appeal to ledger (append-only).
* `_load_appeals` (in `steward/system_agents/supreme_court/tools/appeals_tool.py`): Load all appeals from ledger.
* `_rewrite_appeals` (in `steward/system_agents/supreme_court/tools/appeals_tool.py`): Rewrite the appeals ledger (for updates).
* `__init__` (in `steward/system_agents/supreme_court/tools/justice_ledger.py`): Initialize justice ledger (kernel-managed).
* `root_path` (in `steward/system_agents/supreme_court/tools/justice_ledger.py`): Lazy-load root_path from system sandbox.
* `ledger_dir` (in `steward/system_agents/supreme_court/tools/justice_ledger.py`): Get ledger directory.
* `ledger_file` (in `steward/system_agents/supreme_court/tools/justice_ledger.py`): Get ledger file path.
* `validate` (in `steward/system_agents/supreme_court/tools/justice_ledger.py`): Validate justice ledger parameters.
* `execute` (in `steward/system_agents/supreme_court/tools/justice_ledger.py`): Execute justice ledger operation.
* `_append_event` (in `steward/system_agents/supreme_court/tools/justice_ledger.py`): Internal method to append an event to the justice ledger (append-only).

Args:
    event: Event to record (should include event_type and timestamp)
* `record_event` (in `steward/system_agents/supreme_court/tools/justice_ledger.py`): Record an event in the justice ledger.

Supports both signatures:
- Domain-specific: record_event(event: Dict) for Supreme Court events
- VibeLedger ABC: record_event(event_type, agent_id, details) -> str
* `get_events` (in `steward/system_agents/supreme_court/tools/justice_ledger.py`): Retrieve events from the ledger.

Args:
    event_type: If specified, filter by this event type

Returns:
    List of events
* `get_events_for_agent` (in `steward/system_agents/supreme_court/tools/justice_ledger.py`): Get all justice ledger events for a specific agent.
* `get_events_for_appeal` (in `steward/system_agents/supreme_court/tools/justice_ledger.py`): Get all justice ledger events for a specific appeal.
* `get_summary_statistics` (in `steward/system_agents/supreme_court/tools/justice_ledger.py`): Get summary statistics of Supreme Court activity.

Returns:
    Statistics object with counts and summaries
* `verify_ledger_integrity` (in `steward/system_agents/supreme_court/tools/justice_ledger.py`): Verify the ledger has not been tampered with.

In production, this would use cryptographic hashing...
* `record_start` (in `steward/system_agents/supreme_court/tools/justice_ledger.py`): Record task start (VibeLedger interface)
* `record_completion` (in `steward/system_agents/supreme_court/tools/justice_ledger.py`): Record task completion (VibeLedger interface)
* `record_failure` (in `steward/system_agents/supreme_court/tools/justice_ledger.py`): Record task failure (VibeLedger interface)
* `get_task` (in `steward/system_agents/supreme_court/tools/justice_ledger.py`): Query task result (VibeLedger interface)
* `__init__` (in `steward/system_agents/supreme_court/tools/precedent_tool.py`): Initialize precedent tool (kernel-managed).
* `root_path` (in `steward/system_agents/supreme_court/tools/precedent_tool.py`): Lazy-load root_path from system sandbox.
* `precedent_dir` (in `steward/system_agents/supreme_court/tools/precedent_tool.py`): Get precedent directory.
* `cases_file` (in `steward/system_agents/supreme_court/tools/precedent_tool.py`): Get cases file path.
* `validate` (in `steward/system_agents/supreme_court/tools/precedent_tool.py`): Validate precedent tool parameters.
* `execute` (in `steward/system_agents/supreme_court/tools/precedent_tool.py`): Execute precedent tool operation.
* `record_case` (in `steward/system_agents/supreme_court/tools/precedent_tool.py`): Record a verdict as legal precedent.

Important: Not all verdicts become precedent - only significant ones...
* `find_similar_cases` (in `steward/system_agents/supreme_court/tools/precedent_tool.py`): Find similar precedent cases for comparison.

This is used during MERCY INVESTIGATION to see what similar
cases resulted in...
* `get_precedent_cases` (in `steward/system_agents/supreme_court/tools/precedent_tool.py`): Get precedent cases, optionally filtered by category.
* `get_mercy_precedents` (in `steward/system_agents/supreme_court/tools/precedent_tool.py`): Get all precedents where mercy was granted.
* `get_case_by_verdict` (in `steward/system_agents/supreme_court/tools/precedent_tool.py`): Get precedent case for a specific verdict.
* `cite_case` (in `steward/system_agents/supreme_court/tools/precedent_tool.py`): Increment citation count for a case.

Used when a future appeal cites this precedent...
* `get_most_cited_cases` (in `steward/system_agents/supreme_court/tools/precedent_tool.py`): Get most-cited precedent cases.
* `_append_case` (in `steward/system_agents/supreme_court/tools/precedent_tool.py`): Append case to ledger (append-only).
* `_load_cases` (in `steward/system_agents/supreme_court/tools/precedent_tool.py`): Load all precedent cases.
* `_rewrite_cases` (in `steward/system_agents/supreme_court/tools/precedent_tool.py`): Rewrite the cases ledger (for updates like citations).
* `__init__` (in `steward/system_agents/supreme_court/tools/verdict_tool.py`): Initialize verdict tool (kernel-managed).
* `root_path` (in `steward/system_agents/supreme_court/tools/verdict_tool.py`): Lazy-load root_path from system sandbox.
* `verdicts_dir` (in `steward/system_agents/supreme_court/tools/verdict_tool.py`): Get verdicts directory.
* `verdicts_file` (in `steward/system_agents/supreme_court/tools/verdict_tool.py`): Get verdicts file path.
* `validate` (in `steward/system_agents/supreme_court/tools/verdict_tool.py`): Validate verdict tool parameters.
* `execute` (in `steward/system_agents/supreme_court/tools/verdict_tool.py`): Execute verdict tool operation.
* `issue_verdict` (in `steward/system_agents/supreme_court/tools/verdict_tool.py`): Issue a verdict on an appeal.

Args:
    appeal_id: Appeal being decided
    agent_id: Agent the verdict concerns
    verdict_type: Type of verdict (mercy, upheld, conditional)
    justification: Reason for this verdict
    override_auditor: Whether this overrides AUDITOR decision
    conditions: Any conditions attached to the verdict

Returns:
    Verdict record
* `get_verdict` (in `steward/system_agents/supreme_court/tools/verdict_tool.py`): Retrieve a verdict by ID.
* `get_verdicts_by_agent` (in `steward/system_agents/supreme_court/tools/verdict_tool.py`): Get all verdicts issued for an agent.
* `get_verdicts_by_type` (in `steward/system_agents/supreme_court/tools/verdict_tool.py`): Get all verdicts of a specific type.
* `get_mercy_count` (in `steward/system_agents/supreme_court/tools/verdict_tool.py`): Count how many times mercy has been granted.
* `get_verdicts_that_override` (in `steward/system_agents/supreme_court/tools/verdict_tool.py`): Get all verdicts that override AUDITOR decisions.
* `get_all_verdicts` (in `steward/system_agents/supreme_court/tools/verdict_tool.py`): Get all verdicts (for auditing).
* `_append_verdict` (in `steward/system_agents/supreme_court/tools/verdict_tool.py`): Append verdict to ledger (append-only).
* `_load_verdicts` (in `steward/system_agents/supreme_court/tools/verdict_tool.py`): Load all verdicts from ledger.
### steward -> system_agents -> watchman -> tools
* `to_dict` (in `steward/system_agents/watchman/tools/standards_inspection.py`): Convert to dict for JSON serialization.
* `visit_Call` (in `steward/system_agents/watchman/tools/standards_inspection.py`): Visit function call nodes.
* `_extract_agent_id` (in `steward/system_agents/watchman/tools/standards_inspection.py`): Extract agent ID from file path.
* `visit_FunctionDef` (in `steward/system_agents/watchman/tools/standards_inspection.py`): Visit function definitions.
* `visit_Assign` (in `steward/system_agents/watchman/tools/standards_inspection.py`): Visit assignment nodes in __init__.
* `_extract_agent_id` (in `steward/system_agents/watchman/tools/standards_inspection.py`): Extract agent ID from file path.
* `visit_Attribute` (in `steward/system_agents/watchman/tools/standards_inspection.py`): Visit attribute access - detect self.*_tool patterns...
* `_extract_agent_id` (in `steward/system_agents/watchman/tools/standards_inspection.py`): Extract agent ID from file path.
* `validate` (in `steward/system_agents/watchman/tools/standards_inspection.py`): Validate parameters.
* `execute` (in `steward/system_agents/watchman/tools/standards_inspection.py`): Execute standards inspection.
* `inspect_agent` (in `steward/system_agents/watchman/tools/standards_inspection.py`): Inspect a single agent for violations.

Args:
    agent_path: Path to agent directory (e...
* `_inspect_python_file` (in `steward/system_agents/watchman/tools/standards_inspection.py`): Inspect a Python file using AST analysis.

Args:
    file_path: Path to Python file

Returns:
    List of violations found
* `inspect_all_agents` (in `steward/system_agents/watchman/tools/standards_inspection.py`): Inspect all agents in the system_agents directory.

Args:
    system_agents_path: Path to steward/system_agents

Returns:
    List of all violations found
* `generate_report` (in `steward/system_agents/watchman/tools/standards_inspection.py`): Generate a compliance report.

Args:
    violations: List of violations

Returns:
    Report dict with summary and details
* `main` (in `steward/system_agents/watchman/tools/system_health_check.py`): Main entry point for standalone execution.
* `__init__` (in `steward/system_agents/watchman/tools/system_health_check.py`): Initialize health checker.
* `validate` (in `steward/system_agents/watchman/tools/system_health_check.py`): Validate parameters.
* `execute` (in `steward/system_agents/watchman/tools/system_health_check.py`): Execute health check.
* `check_all` (in `steward/system_agents/watchman/tools/system_health_check.py`): Run all health checks and return comprehensive report.
* `_check_git_hooks` (in `steward/system_agents/watchman/tools/system_health_check.py`): Check git hooks installation status (READ-ONLY).
* `_check_single_hook` (in `steward/system_agents/watchman/tools/system_health_check.py`): Check a single git hook (READ-ONLY).
* `format_report` (in `steward/system_agents/watchman/tools/system_health_check.py`): Format health report for human reading.
### vibe_core -> agents
* `_ensure_degradation_initialized` (in `vibe_core/agents/context_aware_agent.py`): Lazy initialization of DegradationChain.
* `get_degradation_chain` (in `vibe_core/agents/context_aware_agent.py`): Get the DegradationChain instance for tool injection.

Use this to pass the chain to tools that need offline capability:

    self...
* `chat_with_fallback` (in `vibe_core/agents/context_aware_agent.py`): Generate a response with automatic offline fallback.

This is the main entry point for LLM interactions...
* `get_degradation_status` (in `vibe_core/agents/context_aware_agent.py`): Get the current degradation status.

Returns:
    Dict with level, local_llm_available, templates_loaded
* `_ensure_context_initialized` (in `vibe_core/agents/context_aware_agent.py`): Lazy initialization of context systems.
* `get_context` (in `vibe_core/agents/context_aware_agent.py`): Get dynamic context from PromptContext.

Args:
    keys: Optional list of context keys to resolve...
* `get_governed_prompt` (in `vibe_core/agents/context_aware_agent.py`): Get governed prompt with context injection.

Uses PromptRegistry to compose prompts with:
- Agent-specific templates
- Dynamic context injection
- Governance rules (if inject_governance=True)

Args:
    task_name: Name of the task/template to compose
    extra_context: Additional context to inject
    inject_governance: Whether to inject governance rules

Returns:
    Composed prompt string
* `init_offline_capability` (in `vibe_core/agents/context_aware_agent.py`): Initialize offline capability with optional DegradationChain.

Args:
    degradation_chain: DegradationChain instance from parent agent
* `is_offline` (in `vibe_core/agents/context_aware_agent.py`): Check if we're in offline mode (no API access).

Returns True if:
- No DegradationChain available, or
- DegradationChain level is not FULL
* `degradation_level` (in `vibe_core/agents/context_aware_agent.py`): Get current degradation level as string.
* `fallback_response` (in `vibe_core/agents/context_aware_agent.py`): Generate a fallback response when offline.

Args:
    query: The original query/request
    tool_name: Name of the tool for logging

Returns:
    Dict with fallback response and metadata
* `__init__` (in `vibe_core/agents/llm_agent.py`): Initialize the LLM agent.

Args:
    agent_id: Unique identifier for this agent
    provider: LLMProvider instance to use for cognitive work
    system_prompt: System prompt to use (overrides provider default)
    model: Model identifier to pass to provider (e...
* `agent_id` (in `vibe_core/agents/llm_agent.py`): Return the agent's unique identifier.
* `capabilities` (in `vibe_core/agents/llm_agent.py`): Return list of tool names available to this agent.

If tool_registry is configured, returns the names of all registered tools...
* `process` (in `vibe_core/agents/llm_agent.py`): Process a task by sending it to the LLM provider.

Expected task payload format:
{
    "user_message": str,  # Required: the user's message
    "context": dict,      # Optional: additional context
    "model": str          # Optional: override default model
}

Args:
    task: The Task to process

Returns:
    AgentResponse: Standardized response with structure:
        {
            "agent_id": str,           # This agent's ID
            "task_id": str,            # The task ID
            "success": bool,           # Whether call succeeded
            "output": dict,            # Contains response, model_used, provider, tool_call
            "error": str | None        # Error message if failed
        }

Raises:
    ValueError: If task payload is missing user_message
    LLMError: If LLM call fails (after recording attempt)

Example:
    >>> task = Task(...
* `_build_messages` (in `vibe_core/agents/llm_agent.py`): Build the message list for the LLM provider.

Args:
    user_message: The user's message
    context: Optional context to include in system message

Returns:
    List of message dicts with 'role' and 'content' keys

Example:
    >>> messages = agent...
* `_extract_tool_call` (in `vibe_core/agents/llm_agent.py`): Extract tool call from LLM response.

Looks for JSON object with format: {"tool": "name", "parameters": {...
* `_execute_tool_call` (in `vibe_core/agents/llm_agent.py`): Execute a tool call via the tool registry.

Args:
    tool_call_data: {"tool": "name", "parameters": {...
* `update_system_prompt` (in `vibe_core/agents/llm_agent.py`): Update the system prompt for this agent.

Args:
    new_prompt: New system prompt to use

Example:
    >>> agent...
* `__init__` (in `vibe_core/agents/specialist_agent.py`): Initialize the adapter with a specialist instance.

Args:
    specialist: BaseSpecialist subclass instance to wrap
                (PlanningSpecialist, CodingSpecialist, etc...
* `agent_id` (in `vibe_core/agents/specialist_agent.py`): Return the agent ID for kernel registration.

Format: "specialist-{role}" (lowercase)
Examples:
    - PlanningSpecialist → "specialist-planning"
    - CodingSpecialist → "specialist-coding"
    - TestingSpecialist → "specialist-testing"

Returns:
    str: Unique agent identifier
* `capabilities` (in `vibe_core/agents/specialist_agent.py`): Return list of capabilities provided by this specialist.

Specialists describe what they do via their role and lifecycle:
- The role defines the primary capability (e...
* `process` (in `vibe_core/agents/specialist_agent.py`): Process a task by executing the wrapped specialist.

Workflow:
    1...
* `_task_to_context` (in `vibe_core/agents/specialist_agent.py`): Convert Task payload to MissionContext.

Args:
    task: Task with payload dict

Returns:
    MissionContext: Context for specialist execution

Raises:
    KeyError: If required field missing in payload
    TypeError: If payload is not a dict
* `_result_to_response` (in `vibe_core/agents/specialist_agent.py`): Convert SpecialistResult to AgentResponse for kernel recording.

Args:
    task: The task being processed
    result: SpecialistResult from specialist...
* `__repr__` (in `vibe_core/agents/specialist_agent.py`): String representation for debugging
* `__init__` (in `vibe_core/agents/specialist_factory.py`): Initialize factory agent.

Args:
    specialist_class: BaseSpecialist subclass to instantiate
                      (PlanningSpecialist, CodingSpecialist, etc...
* `agent_id` (in `vibe_core/agents/specialist_factory.py`): Return agent ID for kernel registration.

Format: "specialist-{role}" (lowercase)
Examples:
    - planning → "specialist-planning"
    - coding → "specialist-coding"
    - testing → "specialist-testing"

Returns:
    str: Unique agent identifier
* `capabilities` (in `vibe_core/agents/specialist_factory.py`): Return the capabilities of this specialist factory.

The factory provides capabilities based on the specialist class it creates...
* `process` (in `vibe_core/agents/specialist_factory.py`): Process task by creating and executing a Specialist.

Workflow:
    1...
* `__repr__` (in `vibe_core/agents/specialist_factory.py`): String representation for debugging
* `__init__` (in `vibe_core/agents/system_maintenance.py`): Initialize SystemMaintenanceAgent.

Args:
    project_root: Path to project root (defaults to current directory)
* `agent_id` (in `vibe_core/agents/system_maintenance.py`): Return agent identifier.
* `capabilities` (in `vibe_core/agents/system_maintenance.py`): Return list of supported operations.

Returns:
    list[str]: Capability names
* `process` (in `vibe_core/agents/system_maintenance.py`): Process a maintenance task.

Supported operations (via task...
* `_perform_system_update` (in `vibe_core/agents/system_maintenance.py`): Execute system update (git pull + uv sync).

This performs:
1...
* `_verify_integrity` (in `vibe_core/agents/system_maintenance.py`): Run pre-flight integrity checks.

Checks:
- Git repository is valid
- Virtual environment exists
- No uncommitted changes (prevents merge conflicts)

Args:
    task: The task being processed

Returns:
    AgentResponse: Success if all checks pass
* `_check_sync_status` (in `vibe_core/agents/system_maintenance.py`): Check current git synchronization status.

Returns:
    AgentResponse: Current git status (synced/behind/diverged)
* `_run_integrity_check` (in `vibe_core/agents/system_maintenance.py`): Run integrity checks.

Returns:
    dict: {"success": bool, "checks": dict, "error": str | None}
* `_run_git_pull` (in `vibe_core/agents/system_maintenance.py`): Execute git pull.

Returns:
    dict: {"success": bool, "commits_pulled": int, "output": str, "error": str | None}
* `_run_uv_sync` (in `vibe_core/agents/system_maintenance.py`): Execute uv sync.

Returns:
    dict: {"success": bool, "packages_updated": int, "output": str, "error": str | None}
### vibe_core -> cartridges
* `__init__` (in `vibe_core/cartridges/base.py`): Initialize the cartridge.

Args:
    vibe_root: Path to vibe-agency root (auto-detected if None)
* `_detect_vibe_root` (in `vibe_core/cartridges/base.py`): Auto-detect the vibe-agency root directory.
* `_init_llm_provider` (in `vibe_core/cartridges/base.py`): Initialize the LLM provider (offline-first).
* `_load_playbooks` (in `vibe_core/cartridges/base.py`): Load playbooks for this cartridge.

Playbooks are YAML workflow definitions stored in:
vibe_core/cartridges/{cartridge_name}/playbooks/

Returns:
    Dictionary mapping playbook names to their definitions
* `_load_tools` (in `vibe_core/cartridges/base.py`): Load tools for this cartridge.

Tools are Python functions/classes that this cartridge uses...
* `get_config` (in `vibe_core/cartridges/base.py`): Get the cartridge configuration.
* `get_spec` (in `vibe_core/cartridges/base.py`): Get the cartridge specification (metadata).
* `report_status` (in `vibe_core/cartridges/base.py`): Report current status of the cartridge.
* `get_default_cartridge_registry` (in `vibe_core/cartridges/registry.py`): Get the default global cartridge registry instance (singleton).

Args:
    vibe_root: Path to vibe-agency root (only used for first initialization)

Returns:
    Global CartridgeRegistry instance

Example:
    registry = get_default_cartridge_registry()
    archivist = registry...
* `__init__` (in `vibe_core/cartridges/registry.py`): Initialize the cartridge registry.

Args:
    vibe_root: Path to vibe-agency root
* `_detect_vibe_root` (in `vibe_core/cartridges/registry.py`): Auto-detect the vibe-agency root directory.
* `_auto_discover` (in `vibe_core/cartridges/registry.py`): Auto-discover cartridges in vibe_core/cartridges/ directory.
* `_load_cartridge_from_dir` (in `vibe_core/cartridges/registry.py`): Load a cartridge from a directory.

Looks for:
1...
* `_load_cartridge_from_file` (in `vibe_core/cartridges/registry.py`): Dynamically load a cartridge class from a Python file.

Args:
    file_path: Path to the Python file
    cartridge_name: Name of the cartridge
* `register_cartridge` (in `vibe_core/cartridges/registry.py`): Manually register a cartridge.

Args:
    name: Cartridge name (e...
* `get_cartridge` (in `vibe_core/cartridges/registry.py`): Get a cartridge instance.

Args:
    name: Cartridge name (e...
* `list_cartridges` (in `vibe_core/cartridges/registry.py`): List all registered cartridges with their metadata.

Returns:
    Dictionary mapping cartridge names to CartridgeSpec
* `get_cartridge_names` (in `vibe_core/cartridges/registry.py`): Get list of all registered cartridge names.
* `__repr__` (in `vibe_core/cartridges/registry.py`): String representation for debugging.
### vibe_core -> config
* `__init__` (in `vibe_core/config/loader.py`): Initialize ConfigLoader.

Args:
    config_path: Path to configuration YAML file
* `load` (in `vibe_core/config/loader.py`): Load and validate configuration.

Returns:
    Validated CityConfig instance

Raises:
    FileNotFoundError: If config file not found
    ValueError: If config validation fails
* `config` (in `vibe_core/config/loader.py`): Get current configuration (must load first).

Returns:
    CityConfig instance

Raises:
    RuntimeError: If load() hasn't been called yet
* `is_loaded` (in `vibe_core/config/loader.py`): Check if configuration has been loaded
* `validate` (in `vibe_core/config/loader.py`): Validate loaded configuration and return diagnostic report.

Returns:
    Diagnostic report with validation results

Raises:
    RuntimeError: If load() hasn't been called yet
* `_check_governance` (in `vibe_core/config/loader.py`): Check governance configuration
* `_check_economy` (in `vibe_core/config/loader.py`): Check economy configuration
* `_check_security` (in `vibe_core/config/loader.py`): Check security configuration
* `_check_integrations` (in `vibe_core/config/loader.py`): Check integration configuration
* `print_summary` (in `vibe_core/config/loader.py`): Print human-readable configuration summary
* `load_config` (in `vibe_core/config/schema.py`): Load and validate configuration from YAML file.

Args:
    config_path: Path to dharma...
* `get_agent_config` (in `vibe_core/config/schema.py`): Retrieve configuration for a specific agent
* `get_integration_config` (in `vibe_core/config/schema.py`): Retrieve configuration for a specific integration
### vibe_core -> governance
* `__init__` (in `vibe_core/governance/invariants.py`): Initialize the InvariantChecker.

Args:
    soul_path: Path to the soul...
* `_load_rules` (in `vibe_core/governance/invariants.py`): Load safety rules from soul.yaml...
* `check_tool_call` (in `vibe_core/governance/invariants.py`): Validate a tool call against all safety rules.

This is the main entry point for governance checks...
* `_check_rule` (in `vibe_core/governance/invariants.py`): Check a single rule against a tool call.

Args:
    rule: The rule dictionary from soul...
* `_is_path_outside_root` (in `vibe_core/governance/invariants.py`): Check if a path is outside the project root.

This implements sandbox confinement - agents should only be able to
access files within the project directory...
* `reload` (in `vibe_core/governance/invariants.py`): Reload rules from soul.yaml...
* `rule_count` (in `vibe_core/governance/invariants.py`): Return the number of loaded rules.
* `get_rule_ids` (in `vibe_core/governance/invariants.py`): Return list of all rule IDs.
### vibe_core -> knowledge
* `get_knowledge_graph` (in `vibe_core/knowledge/graph.py`): Get or create the global knowledge graph instance.
* `load` (in `vibe_core/knowledge/graph.py`): Load all knowledge from YAML files.
* `get_node` (in `vibe_core/knowledge/graph.py`): Get a single node by ID. ATOMIC...
* `get_nodes_by_type` (in `vibe_core/knowledge/graph.py`): Get all nodes of a type.
* `get_nodes_by_domain` (in `vibe_core/knowledge/graph.py`): Get all nodes in a domain.
* `search_nodes` (in `vibe_core/knowledge/graph.py`): Simple keyword search in node names/descriptions.
* `get_edges` (in `vibe_core/knowledge/graph.py`): Get all edges from a node, optionally filtered by relation type.
* `get_incoming_edges` (in `vibe_core/knowledge/graph.py`): Get all edges TO a node.
* `traverse` (in `vibe_core/knowledge/graph.py`): Traverse graph from node following relation type.
Returns dict of node_id -> Node for all reached nodes...
* `can_reach` (in `vibe_core/knowledge/graph.py`): Check if there's a path from one node to another.
* `get_path` (in `vibe_core/knowledge/graph.py`): Get shortest path between nodes. Returns list of node IDs...
* `get_constraints` (in `vibe_core/knowledge/graph.py`): Get constraints, optionally filtered by node.
* `check_constraint` (in `vibe_core/knowledge/graph.py`): Check if a constraint condition is met. Returns True if VIOLATED...
* `check_constraints` (in `vibe_core/knowledge/graph.py`): Check all constraints and return violations.
* `is_allowed` (in `vibe_core/knowledge/graph.py`): Check if action is allowed (no hard constraint violations).
* `get_metric` (in `vibe_core/knowledge/graph.py`): Get a specific metric value for a node.
* `get_all_metrics` (in `vibe_core/knowledge/graph.py`): Get all metrics for a node.
* `compare` (in `vibe_core/knowledge/graph.py`): Compare two nodes by metric. Returns -1, 0, or 1...
* `rank_by_metric` (in `vibe_core/knowledge/graph.py`): Sort nodes by metric value.
* `get_context_for_task` (in `vibe_core/knowledge/graph.py`): Get all relevant context for a task. ATOMIC...
* `compile_prompt_context` (in `vibe_core/knowledge/graph.py`): Compile knowledge into a prompt-ready string.
ATOMIC: Only relevant knowledge, not entire graph...
* `load_all` (in `vibe_core/knowledge/loader.py`): Load all knowledge from directory structure.
* `_load_directory` (in `vibe_core/knowledge/loader.py`): Load all YAML files from a directory.
* `_load_file` (in `vibe_core/knowledge/loader.py`): Load a single YAML file.
* `_load_nodes` (in `vibe_core/knowledge/loader.py`): Load nodes from data.
* `_load_edges` (in `vibe_core/knowledge/loader.py`): Load edges from data.
* `_load_constraints` (in `vibe_core/knowledge/loader.py`): Load constraints from data.
* `_load_metrics` (in `vibe_core/knowledge/loader.py`): Load metrics from data.
* `get_resolver` (in `vibe_core/knowledge/resolver.py`): Get a KnowledgeResolver instance.
* `get_agent_for_concept` (in `vibe_core/knowledge/resolver.py`): Which agent handles this concept?
* `get_agent_authority` (in `vibe_core/knowledge/resolver.py`): Get authority level for an agent (1-10).
* `can_agent_override` (in `vibe_core/knowledge/resolver.py`): Can agent A override agent B?
* `get_agents_by_authority` (in `vibe_core/knowledge/resolver.py`): Get agents with at least min_authority level.
* `get_dependencies` (in `vibe_core/knowledge/resolver.py`): Get all dependencies for a feature.
* `get_complexity` (in `vibe_core/knowledge/resolver.py`): Get complexity score for a feature.
* `estimate_total_complexity` (in `vibe_core/knowledge/resolver.py`): Estimate total complexity including dependencies.
* `is_action_allowed` (in `vibe_core/knowledge/resolver.py`): Check if action is allowed.
* `get_violations` (in `vibe_core/knowledge/resolver.py`): Get list of constraint violation messages.
* `get_blocked_features` (in `vibe_core/knowledge/resolver.py`): Get features that are blocked for a scope.
* `compile_context` (in `vibe_core/knowledge/resolver.py`): Compile relevant knowledge into prompt context.
ATOMIC: Only includes relevant nodes...
* `get_response_template` (in `vibe_core/knowledge/resolver.py`): Get a response template for a concept if one exists.
### vibe_core -> llm
* `__init__` (in `vibe_core/llm/chain.py`): Initialize the chain provider.

Args:
    providers: List of LLMProvider instances in priority order...
* `chat` (in `vibe_core/llm/chain.py`): Send messages through the provider chain.

Tries each provider in order until one succeeds...
* `system_prompt` (in `vibe_core/llm/chain.py`): Return the system prompt from the current/primary provider.

Returns:
    str: System prompt text

Example:
    >>> chain = ChainProvider(providers=[google, local])
    >>> print(chain...
* `get_metadata` (in `vibe_core/llm/chain.py`): Get metadata about the chain provider.

Returns:
    dict: Metadata including all provider names in the chain

Example:
    >>> metadata = chain...
* `__repr__` (in `vibe_core/llm/chain.py`): String representation for debugging.
* `_detect_level` (in `vibe_core/llm/degradation_chain.py`): Detect current system capability.
* `_load_templates` (in `vibe_core/llm/degradation_chain.py`): Load response templates.
* `respond` (in `vibe_core/llm/degradation_chain.py`): Generate response with graceful degradation.
* `_generate_clarification` (in `vibe_core/llm/degradation_chain.py`): Generate clarification request.
* `_neti_neti_fallback` (in `vibe_core/llm/degradation_chain.py`): NETI NETI fallback chain.
* `_compile_prompt` (in `vibe_core/llm/degradation_chain.py`): Compile prompt with knowledge context for local LLM.
* `_match_template` (in `vibe_core/llm/degradation_chain.py`): Simple keyword matching.
* `get_status` (in `vibe_core/llm/degradation_chain.py`): Get status for introspection.
* `__init__` (in `vibe_core/llm/google_adapter.py`): Initialize Google provider adapter.

Args:
    api_key: Google API key (or None to load from GOOGLE_API_KEY env var)
    model: Default model to use
    **kwargs: Additional configuration passed to GoogleProvider

Raises:
    ProviderNotAvailableError: If API key missing or google-generativeai not installed
* `chat` (in `vibe_core/llm/google_adapter.py`): Send messages to Google Gemini and get response.

Converts chat-style messages to a single prompt, calls the runtime
provider, and extracts the text response...
* `system_prompt` (in `vibe_core/llm/google_adapter.py`): Return default system prompt.

For compatibility with LLMProvider protocol...
* `_messages_to_prompt` (in `vibe_core/llm/google_adapter.py`): Convert chat messages to a single prompt string.

Google Gemini works best with a single consolidated prompt...
* `__repr__` (in `vibe_core/llm/google_adapter.py`): String representation for debugging.
* `__init__` (in `vibe_core/llm/human_provider.py`): Initialize Human Provider.

No configuration needed - this provider uses stdin/stdout directly...
* `chat` (in `vibe_core/llm/human_provider.py`): Prompt the human operator for a response.

Displays the conversation context and waits for human input...
* `system_prompt` (in `vibe_core/llm/human_provider.py`): Return default system prompt.

For HumanProvider, the system prompt is informational only
(displayed to the human for context)...
* `__repr__` (in `vibe_core/llm/human_provider.py`): String representation for debugging.
* `download_default_model` (in `vibe_core/llm/local_llama_provider.py`): Download the default model from HuggingFace.
* `_ensure_loaded` (in `vibe_core/llm/local_llama_provider.py`): Lazy load the model if not already loaded.
* `model_exists` (in `vibe_core/llm/local_llama_provider.py`): Check if a local model is available.
* `get_model_path` (in `vibe_core/llm/local_llama_provider.py`): Get path to available model.
* `_find_model` (in `vibe_core/llm/local_llama_provider.py`): Search for model in default locations.
* `_get_optimal_threads` (in `vibe_core/llm/local_llama_provider.py`): Detect optimal thread count.
* `_load_model` (in `vibe_core/llm/local_llama_provider.py`): Load the GGUF model.
* `chat` (in `vibe_core/llm/local_llama_provider.py`): Generate response from local LLM.
* `_format_chat_prompt` (in `vibe_core/llm/local_llama_provider.py`): Format messages into ChatML prompt.
* `get_info` (in `vibe_core/llm/local_llama_provider.py`): Get provider info.
* `chat` (in `vibe_core/llm/provider.py`): Send messages to the LLM and get a response.

Args:
    messages: List of message dicts with 'role' and 'content' keys...
* `system_prompt` (in `vibe_core/llm/provider.py`): Return the default system prompt for this provider.

The system prompt sets the behavior/personality of the LLM...
* `get_metadata` (in `vibe_core/llm/provider.py`): Get provider metadata (optional, can be overridden).

Returns:
    dict: Metadata about the provider (name, version, etc...
* `__init__` (in `vibe_core/llm/smart_local_provider.py`): Initialize Smart Local Provider.
* `chat` (in `vibe_core/llm/smart_local_provider.py`): Process Operator messages and return delegation instructions.

Args:
    messages: List of message dicts with 'role' and 'content' keys
    model: Ignored
    **kwargs: Ignored

Returns:
    str: Delegation command or response
* `_is_delegation_request` (in `vibe_core/llm/smart_local_provider.py`): Check if message is requesting delegation.
* `_is_planning_request` (in `vibe_core/llm/smart_local_provider.py`): Check if message is asking for planning.
* `_is_coding_request` (in `vibe_core/llm/smart_local_provider.py`): Check if message is asking for coding.
* `_is_testing_request` (in `vibe_core/llm/smart_local_provider.py`): Check if message is asking for testing.
* `_handle_delegation` (in `vibe_core/llm/smart_local_provider.py`): Handle full SDLC delegation (Plan → Code → Test).
* `_generate_plan` (in `vibe_core/llm/smart_local_provider.py`): Generate architecture plan for Snake game.
* `_generate_code` (in `vibe_core/llm/smart_local_provider.py`): Generate skeleton Snake game code.
* `_generate_test_response` (in `vibe_core/llm/smart_local_provider.py`): Generate test execution response.
* `_respond_generic` (in `vibe_core/llm/smart_local_provider.py`): Respond to generic queries.
* `_respond` (in `vibe_core/llm/smart_local_provider.py`): Format response.
* `system_prompt` (in `vibe_core/llm/smart_local_provider.py`): Return default system prompt.
* `__repr__` (in `vibe_core/llm/smart_local_provider.py`): String representation for debugging.
* `__init__` (in `vibe_core/llm/steward_provider.py`): Initialize Steward Provider.

No configuration needed - this provider uses stdin/stdout directly
to communicate with the Claude Code environment...
* `chat` (in `vibe_core/llm/steward_provider.py`): Delegate cognitive work to the STEWARD (Claude Code environment).

Outputs a structured prompt that Claude Code can parse and respond to...
* `system_prompt` (in `vibe_core/llm/steward_provider.py`): Return default system prompt.

For StewardProvider, the system prompt is informational only
(displayed to Claude Code for context)...
* `_messages_to_prompt` (in `vibe_core/llm/steward_provider.py`): Convert chat messages to a single prompt string.

Formats messages in a clear structure for Claude Code to understand...
* `__repr__` (in `vibe_core/llm/steward_provider.py`): String representation for debugging.
### vibe_core -> playbook
* `can_execute` (in `vibe_core/playbook/executor.py`): Check if this agent has required skills
* `execute_action` (in `vibe_core/playbook/executor.py`): Execute an action (mocked for testing)
* `can_execute` (in `vibe_core/playbook/executor.py`): Check if mock agent has all required skills
* `execute_action` (in `vibe_core/playbook/executor.py`): Return mock result (for dry-run/testing).

WARNING: This is a SIMULATION - no real work is performed...
* `__init__` (in `vibe_core/playbook/executor.py`): Initialize executor
* `set_agent` (in `vibe_core/playbook/executor.py`): Set the agent to use for execution
* `set_router` (in `vibe_core/playbook/executor.py`): Attach AgentRouter for capability-based selection
* `set_quota_manager` (in `vibe_core/playbook/executor.py`): Attach OperationalQuota for pre-flight cost checks
* `set_lens` (in `vibe_core/playbook/executor.py`): Set semantic lens for mindset injection (GAD-906/907).

The lens prompt will be prepended to all task contexts, transforming
the agent's thinking mode from worker → engineer...
* `_topological_sort` (in `vibe_core/playbook/executor.py`): Perform topological sort to determine execution order.

Returns ExecutionPlan with nodes in execution order, or with
errors if graph is invalid...
* `validate_workflow` (in `vibe_core/playbook/executor.py`): Validate workflow graph for structural correctness.

Returns (is_valid, message)
* `dry_run` (in `vibe_core/playbook/executor.py`): Dry-run the workflow without executing agents.

Returns:
    Dictionary with execution plan, validation results, and mock output
* `execute_step` (in `vibe_core/playbook/executor.py`): Execute a single workflow node using routed agent.

Execution mode is determined by Phoenix safety configuration:
- config...
* `execute` (in `vibe_core/playbook/executor.py`): Execute the workflow with REAL agent invocation.

This method now calls execute_step() for each node in the workflow,
performing actual execution (not stubs)...
* `get_execution_history` (in `vibe_core/playbook/executor.py`): Get execution history
* `get_execution_cost` (in `vibe_core/playbook/executor.py`): Get estimated cost for workflow
* `load_workflow` (in `vibe_core/playbook/loader.py`): Convenience function to load a single workflow.

Uses default schema location...
* `__init__` (in `vibe_core/playbook/loader.py`): Initialize loader with optional custom schema path.

Args:
    schema_path: Path to _schema...
* `load_workflow` (in `vibe_core/playbook/loader.py`): Load and validate a YAML workflow file.

Args:
    yaml_path: Path to YAML workflow file

Returns:
    WorkflowGraph object ready for execution

Raises:
    WorkflowLoaderError: If file cannot be loaded or parsed
    WorkflowValidationError: If workflow doesn't match schema
* `_build_workflow_graph` (in `vibe_core/playbook/loader.py`): Convert YAML workflow definition to WorkflowGraph object.

Args:
    workflow_def: The 'workflow' dict from validated YAML
    source_path: Path to source YAML file (for logging)

Returns:
    WorkflowGraph object
* `load_workflows_from_directory` (in `vibe_core/playbook/loader.py`): Load all YAML workflows from a directory.

Args:
    directory: Directory containing YAML workflow files

Returns:
    Dict mapping workflow IDs to WorkflowGraph objects
* `__init__` (in `vibe_core/playbook/router_bridge.py`): Initialize the router bridge
* `bridge_workflow` (in `vibe_core/playbook/router_bridge.py`): Bridge a WorkflowGraph to registry-based execution.

Args:
    workflow_graph: The playbook workflow to bridge

Returns:
    RouterBridgeContext with routed actions and phase assignment
* `_map_intent_to_phase` (in `vibe_core/playbook/router_bridge.py`): Map workflow intent to ProjectPhase.

Args:
    intent: User-provided workflow intent

Returns:
    ProjectPhase name (PLANNING, CODING, TESTING, DEPLOYMENT, MAINTENANCE)

LOGIC:
- Try direct enum lookup first
- Fall back to intent pattern matching
- Default to PLANNING if unsure
* `_route_nodes` (in `vibe_core/playbook/router_bridge.py`): Route workflow nodes to target phase.

Args:
    nodes: Dict of WorkflowNode objects from the workflow
    target_phase: The target ProjectPhase for this workflow

Returns:
    List of RoutedAction objects ready for orchestrator delegation
* `validate_bridged_context` (in `vibe_core/playbook/router_bridge.py`): Validate that a bridged context is ready for execution.

Args:
    context: The RouterBridgeContext to validate

Returns:
    True if valid, False otherwise
* `run_playbook_cli` (in `vibe_core/playbook/runner.py`): Convenience function to run a playbook from CLI or scripts.

Args:
    playbook_id_or_path: Playbook ID or file path
    project_context: Project context

Returns:
    Execution results
* `__init__` (in `vibe_core/playbook/runner.py`): Initialize validator
* `validate` (in `vibe_core/playbook/runner.py`): Validate playbook data.

Args:
    data: Parsed YAML data

Returns:
    (is_valid, message)
* `__init__` (in `vibe_core/playbook/runner.py`): Initialize loader
* `load_playbook` (in `vibe_core/playbook/runner.py`): Load and validate a playbook YAML file.

Args:
    yaml_path: Path to playbook YAML file

Returns:
    PlaybookDefinition object

Raises:
    PlaybookError: If file cannot be loaded or is invalid
* `_build_playbook` (in `vibe_core/playbook/runner.py`): Convert YAML dict to PlaybookDefinition
* `__init__` (in `vibe_core/playbook/runner.py`): Initialize registry.

Args:
    registry_dir: Directory containing playbook presets
* `load_all` (in `vibe_core/playbook/runner.py`): Load all playbooks from registry directory
* `get` (in `vibe_core/playbook/runner.py`): Get playbook by ID
* `list` (in `vibe_core/playbook/runner.py`): List all registered playbooks
* `has` (in `vibe_core/playbook/runner.py`): Check if playbook exists
* `__init__` (in `vibe_core/playbook/runner.py`): Initialize runner.

Args:
    orchestrator: CoreOrchestrator instance (optional for lazy loading)
* `load_registry` (in `vibe_core/playbook/runner.py`): Load all playbooks from registry
* `run_playbook` (in `vibe_core/playbook/runner.py`): Execute a playbook by ID.

Args:
    playbook_id: ID of playbook to execute
    project_context: Project context (name, description, etc...
* `run_playbook_file` (in `vibe_core/playbook/runner.py`): Execute a playbook from YAML file.

Args:
    yaml_path: Path to playbook YAML file
    project_context: Project context

Returns:
    Execution results
* `execute_playbook` (in `vibe_core/playbook/runner.py`): Execute a playbook definition.

Args:
    playbook: PlaybookDefinition to execute
    project_context: Project context

Returns:
    Execution results
* `_execute_phase` (in `vibe_core/playbook/runner.py`): Execute a single phase.

Args:
    phase: Phase to execute
    playbook: Parent playbook definition

Returns:
    Phase execution result
* `get_execution_history` (in `vibe_core/playbook/runner.py`): Get execution history
### vibe_core -> runtime
* `run` (in `vibe_core/runtime/boot_sequence.py`): Execute the boot sequence
* `_check_uncommitted_changes` (in `vibe_core/runtime/boot_sequence.py`): Check for uncommitted changes - graceful detection
* `_display_commit_warning` (in `vibe_core/runtime/boot_sequence.py`): Display graceful halt warning for uncommitted changes
* `_get_system_prompt` (in `vibe_core/runtime/boot_sequence.py`): System prompt to prime agents properly
* `_check_git_sync` (in `vibe_core/runtime/boot_sequence.py`): Check if repo is behind remote - graceful fallback if git fails
* `_display_dashboard` (in `vibe_core/runtime/boot_sequence.py`): Display kernel-style boot output (lean, visual, actionable)
* `show_routes` (in `vibe_core/runtime/boot_sequence.py`): Show all available playbook routes
* `_migrate_legacy_json` (in `vibe_core/runtime/boot_sequence.py`): Migrate legacy active_mission.json to SQLite (ARCH-003)

Strategy: Phase 1 - Dual-Write/Import
- Check for existing active_mission...
* `health_check` (in `vibe_core/runtime/boot_sequence.py`): Quick health check - returns True if system is operational
* `__init__` (in `vibe_core/runtime/circuit_breaker.py`): Initialize circuit breaker.

Args:
    config: Configuration object (uses defaults if None)
* `call` (in `vibe_core/runtime/circuit_breaker.py`): Execute a function with circuit breaker protection.

Args:
    func: Function to execute
    *args: Positional arguments for func
    **kwargs: Keyword arguments for func

Returns:
    Result of func execution

Raises:
    CircuitBreakerOpenError: If circuit is OPEN
    CircuitBreakerHalfOpenError: If circuit is HALF_OPEN and probe fails
    (Other exceptions from func are propagated)
* `can_execute` (in `vibe_core/runtime/circuit_breaker.py`): Check if a request can be executed.

Returns:
    (can_execute: bool, reason: str)
* `_record_success` (in `vibe_core/runtime/circuit_breaker.py`): Record successful request
* `_record_failure` (in `vibe_core/runtime/circuit_breaker.py`): Record failed request and potentially open the circuit.

Args:
    error: The exception that was raised
* `_transition_to` (in `vibe_core/runtime/circuit_breaker.py`): Transition to a new state.

Args:
    new_state: The new state to transition to
* `get_status` (in `vibe_core/runtime/circuit_breaker.py`): Get current circuit breaker status.

Returns:
    Dictionary with current state and metrics
* `reset` (in `vibe_core/runtime/circuit_breaker.py`): Manually reset the circuit breaker to CLOSED state.

Useful for testing or manual recovery...
* `load` (in `vibe_core/runtime/context_loader.py`): Load all context sources with robust error handling
* `_load_session_handoff` (in `vibe_core/runtime/context_loader.py`): Read .session_handoff...
* `_load_git_status` (in `vibe_core/runtime/context_loader.py`): Get git status - safe defaults if git unavailable
* `_load_test_status` (in `vibe_core/runtime/context_loader.py`): Check test status - safe defaults if pytest unavailable
* `_load_project_manifest` (in `vibe_core/runtime/context_loader.py`): Read project_manifest.json - safe defaults if missing
* `_load_environment` (in `vibe_core/runtime/context_loader.py`): Check environment setup - safe defaults
* `inject_context` (in `vibe_core/runtime/context_loader.py`): Inject live context into template with {{ placeholders }}

Args:
    template_str: Template with {{ category.field }} placeholders

Returns:
    Filled template with actual values

Example:
    >>> loader = ContextLoader()
    >>> template = "Branch: {{ git...
* `context` (in `vibe_core/runtime/context_loader.py`): Cached context data (loaded once per instance)
* `format_test_summary` (in `vibe_core/runtime/context_loader.py`): Format test status for human readability

Args:
    tests: Test context from load()

Returns:
    Human-readable summary
* `replace_placeholder` (in `vibe_core/runtime/context_loader.py`): Resolve a single placeholder to its value
* `__init__` (in `vibe_core/runtime/hud.py`): Initialize status bar renderer.
* `get_user_name` (in `vibe_core/runtime/hud.py`): Get user name from steward.json or git config...
* `get_operator_tone` (in `vibe_core/runtime/hud.py`): Get operator tone from steward.json or environment variable...
* `render` (in `vibe_core/runtime/hud.py`): Render the status bar.

Returns:
    Formatted status bar string
* `render_compact` (in `vibe_core/runtime/hud.py`): Render a compact single-line status bar.
* `render` (in `vibe_core/runtime/hud.py`): Render the capabilities menu.

Returns:
    Formatted capabilities string
* `get_cartridge_description` (in `vibe_core/runtime/hud.py`): Get description for a specific cartridge.
* `get_hint_for_input` (in `vibe_core/runtime/hud.py`): Get a hint based on user input.

Args:
    user_input: What the user typed

Returns:
    Hint string or None if not applicable
* `get_contextual_hint` (in `vibe_core/runtime/hud.py`): Get a hint based on current system state.

Returns:
    Hint string or None if no hint needed
* `get_random_hint` (in `vibe_core/runtime/hud.py`): Get a random general hint.
* `detect_mode` (in `vibe_core/runtime/interface.py`): Detect the appropriate interface mode based on runtime environment.

Detection order:
1...
* `is_interactive` (in `vibe_core/runtime/interface.py`): Check if running in interactive mode.
* `is_headless` (in `vibe_core/runtime/interface.py`): Check if running in headless mode.
* `is_steward` (in `vibe_core/runtime/interface.py`): Check if running in steward mode.
* `record` (in `vibe_core/runtime/llm_client.py`): Record token usage (cost now provided by provider)
* `get_summary` (in `vibe_core/runtime/llm_client.py`): Get cost summary
* `create` (in `vibe_core/runtime/llm_client.py`): Mock messages.create() that returns empty response
* `__init__` (in `vibe_core/runtime/llm_client.py`): Initialize LLM client.

Args:
    budget_limit: Optional budget limit in USD (default: None = no limit)
    provider: Optional explicit provider (default: auto-detect via factory)
* `invoke` (in `vibe_core/runtime/llm_client.py`): Invoke LLM with safety layer, retry logic, and cost tracking.

**GAD-511**: Delegates to provider while maintaining safety guardrails

Args:
    prompt: Input prompt
    model: Model to use
    max_tokens: Maximum output tokens
    temperature: Sampling temperature
    max_retries: Maximum retry attempts (default: 3)

Returns:
    LLMResponse with content and usage info

Raises:
    BudgetExceededError: If budget limit reached
    QuotaExceededError: If operational quota exceeded
    CircuitBreakerOpenError: If circuit breaker is OPEN
    LLMInvocationError: If all retries fail
* `get_cost_summary` (in `vibe_core/runtime/llm_client.py`): Get cost tracking summary
* `get_kernel_oracle` (in `vibe_core/runtime/oracle.py`): Get or create the default KernelOracle instance.

Args:
    kernel: Booted VibeKernel instance
    vibe_root: Path to vibe-agency root

Returns:
    KernelOracle instance
* `__init__` (in `vibe_core/runtime/oracle.py`): Initialize the Oracle with kernel reference.

Args:
    kernel: Booted VibeKernel instance
    vibe_root: Path to vibe-agency root (for cartridge discovery)
* `get_cartridges` (in `vibe_core/runtime/oracle.py`): Get list of installed cartridges with descriptions.

Returns:
    List of dicts: [{"name": "steward", "description": "...
* `get_tools` (in `vibe_core/runtime/oracle.py`): Get list of available tools.

Returns:
    List of tool names: ["read_file", "write_file",...
* `get_meta_commands` (in `vibe_core/runtime/oracle.py`): Get list of meta-commands (built-in commands).

Returns:
    List of dicts: [{"command": "help", "description": "...
* `get_system_capabilities` (in `vibe_core/runtime/oracle.py`): Get complete system capabilities as structured data.

This is the **semantic payload** injected into the Steward's
system prompt...
* `get_help_text` (in `vibe_core/runtime/oracle.py`): Get formatted help text (for CLI display).

This is what the user sees when they type 'help'...
* `get_cortex_text` (in `vibe_core/runtime/oracle.py`): Get text formatted for Steward's system prompt injection.

This is what the LLM sees in its system prompt...
* `_load_registry` (in `vibe_core/runtime/playbook_router.py`): Load playbook registry
* `route` (in `vibe_core/runtime/playbook_router.py`): Main routing logic: Tier 1 → Tier 2 → Tier 3

PHASE 3: Routes through MilkOceanRouter (Brahma Protocol gatekeeping) if available
* `_match_keywords` (in `vibe_core/runtime/playbook_router.py`): Match against registry intent patterns (Tier 1)
* `_infer_from_context` (in `vibe_core/runtime/playbook_router.py`): Infer task from context signals (Tier 2 - LEAN rules!)
* `_suggest_options` (in `vibe_core/runtime/playbook_router.py`): Suggest relevant tasks based on context (Tier 3)
* `_check_with_milk_ocean` (in `vibe_core/runtime/playbook_router.py`): PHASE 3 INTEGRATION: Check route with MilkOceanRouter (Brahma Protocol gatekeeping)

If MilkOcean is available, validate the route through Brahma's 4-tier security gates.
Blocked requests are rejected; normal/high priority requests proceed...
* `_route_to_task` (in `vibe_core/runtime/playbook_router.py`): Map route name to task playbook name
* `list_available_routes` (in `vibe_core/runtime/playbook_router.py`): List all available routes from registry
* `__init__` (in `vibe_core/runtime/project_memory.py`): Initialize project memory manager.

Args:
    project_root: Root directory of the project
    sqlite_store: Optional SQLiteStore instance for dual-write mode (ARCH-003)
* `_ensure_vibe_dir` (in `vibe_core/runtime/project_memory.py`): Ensure .vibe directory exists
* `load` (in `vibe_core/runtime/project_memory.py`): Load project memory (creates default if doesn't exist)
* `save` (in `vibe_core/runtime/project_memory.py`): Save project memory to disk (and optionally to SQLite).

Args:
    memory: Project memory dict
    mission_id: Optional mission ID for dual-write to SQLite (ARCH-003)
* `update_after_session` (in `vibe_core/runtime/project_memory.py`): Update memory after a session completes
* `get_semantic_summary` (in `vibe_core/runtime/project_memory.py`): Generate human-readable summary of project memory
* `_create_default_memory` (in `vibe_core/runtime/project_memory.py`): Create default memory structure
* `_infer_project_id` (in `vibe_core/runtime/project_memory.py`): Infer project ID from manifest or directory name
* `_extract_intents` (in `vibe_core/runtime/project_memory.py`): Extract user intents from input using keyword matching
* `_update_trajectory` (in `vibe_core/runtime/project_memory.py`): Update project trajectory based on context
* `_update_domain` (in `vibe_core/runtime/project_memory.py`): Update domain understanding from context and user input
* `compose` (in `vibe_core/runtime/prompt_composer.py`): Compose final enriched prompt
* `_load_task` (in `vibe_core/runtime/prompt_composer.py`): Load task playbook markdown
* `_inject_context` (in `vibe_core/runtime/prompt_composer.py`): Replace context placeholders in task markdown
* `_format_context_section` (in `vibe_core/runtime/prompt_composer.py`): Format current context as markdown section
* `_format_semantic_context` (in `vibe_core/runtime/prompt_composer.py`): Format semantic memory context for prompt injection
* `_format_backlog` (in `vibe_core/runtime/prompt_composer.py`): Format backlog items
* `_format_commits` (in `vibe_core/runtime/prompt_composer.py`): Format recent commits
* `_add_boot_prompt` (in `vibe_core/runtime/prompt_composer.py`): Add STEWARD boot prompt wrapper
* `get_prompt_context` (in `vibe_core/runtime/prompt_context.py`): Get the global prompt context instance (singleton).

Returns:
    PromptContext instance
* `__init__` (in `vibe_core/runtime/prompt_context.py`): Initialize the prompt context engine.

Args:
    vibe_root: Root directory of vibe-agency...
* `set_kernel` (in `vibe_core/runtime/prompt_context.py`): Set kernel reference for oracle resolver (ARCH-064).

Args:
    kernel: VibeKernel instance (late binding)
* `_register_core_resolvers` (in `vibe_core/runtime/prompt_context.py`): Register the built-in core resolvers.
* `register` (in `vibe_core/runtime/prompt_context.py`): Register a new context resolver.

Args:
    key: Context key (e...
* `resolve` (in `vibe_core/runtime/prompt_context.py`): Resolve context values for specified keys.

Args:
    keys: List of context keys to resolve...
* `_resolve_git_status` (in `vibe_core/runtime/prompt_context.py`): Resolve git status.

Returns:
    Git status output (branch, changes, etc...
* `_resolve_project_structure` (in `vibe_core/runtime/prompt_context.py`): Resolve project topography (ARCH-061: The Map).

Shows only top-level directories + important config files...
* `_python_tree` (in `vibe_core/runtime/prompt_context.py`): Python-based directory tree implementation (fallback).

Args:
    root: Root directory
    max_depth: Maximum depth to traverse

Returns:
    Tree representation as string
* `_resolve_system_time` (in `vibe_core/runtime/prompt_context.py`): Resolve current system time.

Returns:
    ISO 8601 formatted timestamp
* `_resolve_current_branch` (in `vibe_core/runtime/prompt_context.py`): Resolve current git branch.

Returns:
    Current branch name
* `_resolve_recent_commits` (in `vibe_core/runtime/prompt_context.py`): Resolve recent git commits.

Returns:
    Last 3 commits (oneline format)
* `_resolve_inbox_count` (in `vibe_core/runtime/prompt_context.py`): Resolve inbox message count (GAD-006: Asynchronous Intent).

Returns:
    Raw count as string (e...
* `_resolve_agenda_summary` (in `vibe_core/runtime/prompt_context.py`): Resolve agenda task summary (ARCH-045: Agenda System).

Returns:
    JSON string with task counts by priority, e...
* `_resolve_agenda_tasks` (in `vibe_core/runtime/prompt_context.py`): Resolve agenda tasks with focus filter (ARCH-061: Cognitive Hygiene).

Returns top 5 HIGH priority tasks + summary of remaining...
* `_resolve_git_sync_status` (in `vibe_core/runtime/prompt_context.py`): Resolve git sync status (ARCH-044: Git-Ops Strategy).

Returns:
    Raw status string from VIBE_GIT_STATUS env var, or "UNKNOWN"
    Possible values: "SYNCED", "BEHIND_BY_N", "DIVERGED", "FETCH_FAILED", "NO_REPO"
* `_resolve_kernel_capabilities` (in `vibe_core/runtime/prompt_context.py`): Resolve kernel capabilities (ARCH-064: The Omniscient Steward).

Returns the Oracle data formatted for system prompt injection...
* `compose` (in `vibe_core/runtime/prompt_registry.py`): Compose a governed prompt with all injections.

Args:
    agent: Agent ID (e...
* `register` (in `vibe_core/runtime/prompt_registry.py`): Register a prompt by key for simple lookup.

This is a simpler alternative to compose() for cases where you just
need to store and retrieve prompts by key...
* `get` (in `vibe_core/runtime/prompt_registry.py`): Get a prompt by key with optional context interpolation.

Args:
    key: Prompt identifier (e...
* `_load_guardian_directives` (in `vibe_core/runtime/prompt_registry.py`): Load Guardian Directives from SSF knowledge base (with caching).

Returns:
    Formatted markdown section with Guardian Directives
* `_enrich_context` (in `vibe_core/runtime/prompt_registry.py`): Enrich context with workspace manifest and runtime state.

Args:
    workspace: Workspace name
    context: Runtime context dict

Returns:
    Formatted markdown section with enriched context
* `_inject_tools` (in `vibe_core/runtime/prompt_registry.py`): Inject tool definitions.

Args:
    tool_names: List of tool names to inject

Returns:
    Formatted markdown section with tool definitions
* `_inject_sops` (in `vibe_core/runtime/prompt_registry.py`): Inject Standard Operating Procedures.

Args:
    sop_ids: List of SOP IDs (e...
* `_create_meta_agent_prompt` (in `vibe_core/runtime/prompt_registry.py`): Create a minimal prompt for meta-agents (agents with no tasks).

Args:
    agent: Agent ID

Returns:
    Minimal base prompt
* `initialize_defaults` (in `vibe_core/runtime/prompt_registry.py`): Initialize registry with default prompts.

This is called automatically on first use, but can be called
manually to reset prompts or during testing...
* `execute_task` (in `vibe_core/runtime/prompt_runtime.py`): Compose and execute an atomized task.

Args:
    agent_id: Agent identifier (e...
* `_load_composition_spec` (in `vibe_core/runtime/prompt_runtime.py`): Load and parse _composition.yaml

Args:
    agent_id: Agent identifier

Returns:
    CompositionSpec object

Raises:
    AgentNotFoundError: If agent_id invalid
    FileNotFoundError: If _composition...
* `_load_task_metadata` (in `vibe_core/runtime/prompt_runtime.py`): Load and parse task_*.meta...
* `_resolve_knowledge_deps` (in `vibe_core/runtime/prompt_runtime.py`): Resolve which knowledge YAML files to load for this task.

Returns list of file contents (as YAML strings)...
* `_load_knowledge_file` (in `vibe_core/runtime/prompt_runtime.py`): Load a knowledge YAML file (with caching)
* `_compose_prompt` (in `vibe_core/runtime/prompt_runtime.py`): Compose the final prompt by combining fragments according to composition_order.
* `_format_runtime_context` (in `vibe_core/runtime/prompt_runtime.py`): Format runtime context as markdown
* `_get_agent_path` (in `vibe_core/runtime/prompt_runtime.py`): Get the path to an agent's directory

Args:
    agent_id: Agent identifier

Returns:
    Path to agent directory

Raises:
    AgentNotFoundError: If agent_id not in registry
* `_load_file` (in `vibe_core/runtime/prompt_runtime.py`): Load a file's contents
* `_compose_tools_section` (in `vibe_core/runtime/prompt_runtime.py`): Compose the tools section of the prompt (GAD-003 Phase 2)

Args:
    source: Path to tool_definitions.yaml (relative to agent dir)
    available_tools: List of tool names to include
    agent_path: Path to agent directory (for resolving relative paths)

Returns:
    Formatted markdown string with tool definitions
* `_load_quota_limits_from_config` (in `vibe_core/runtime/quota_manager.py`): Load quota limits from Phoenix configuration or environment variables.

Phoenix automatically loads from environment variables or...
* `from_environment` (in `vibe_core/runtime/quota_manager.py`): Create QuotaLimits from Phoenix configuration.

Returns:
    QuotaLimits instance with values loaded from config or defaults
* `__init__` (in `vibe_core/runtime/quota_manager.py`): Initialize quota manager.

Args:
    limits: QuotaLimits configuration (loads from env vars if None)
* `check_before_request` (in `vibe_core/runtime/quota_manager.py`): Pre-flight check before sending a request to LLM.

Args:
    estimated_tokens: Estimated tokens this request will use
    operation: Human-readable description of the operation

Returns:
    (can_execute: bool, reason: str)

Raises:
    QuotaExceededError: If quota would be exceeded
* `record_request` (in `vibe_core/runtime/quota_manager.py`): Record a completed request.

Args:
    tokens_used: Actual tokens used
    cost_usd: Actual cost in USD
    operation: Human-readable description of the operation
* `_update_rolling_windows` (in `vibe_core/runtime/quota_manager.py`): Update rolling time windows
* `_estimate_cost` (in `vibe_core/runtime/quota_manager.py`): Estimate cost for a given number of tokens.

Based on Claude 3...
* `get_status` (in `vibe_core/runtime/quota_manager.py`): Get current quota usage status.

Returns:
    Dictionary with current metrics and limits
* `reset` (in `vibe_core/runtime/quota_manager.py`): Manually reset quota counters.

Useful for testing or explicit user intervention...
* `get_registry` (in `vibe_core/runtime/semantic_actions.py`): Get the global semantic actions registry
* `__init__` (in `vibe_core/runtime/semantic_actions.py`): Initialize with default actions
* `register_action` (in `vibe_core/runtime/semantic_actions.py`): Register a new semantic action
* `get_action` (in `vibe_core/runtime/semantic_actions.py`): Get a semantic action by name
* `find_matching_actions` (in `vibe_core/runtime/semantic_actions.py`): Find actions that match required skills
* `list_actions_by_type` (in `vibe_core/runtime/semantic_actions.py`): List all actions of a specific type
* `get_total_estimated_cost` (in `vibe_core/runtime/semantic_actions.py`): Calculate total estimated cost for a set of actions
### vibe_core -> runtime -> providers
* `__init__` (in `vibe_core/runtime/providers/anthropic.py`): Initialize Anthropic provider.

Args:
    api_key: Anthropic API key
    **kwargs: Additional configuration (unused for now)

Raises:
    ProviderNotAvailableError: If anthropic package not installed or API key invalid
* `invoke` (in `vibe_core/runtime/providers/anthropic.py`): Invoke Claude with a prompt.

Args:
    prompt: Input prompt
    model: Claude model identifier
    max_tokens: Maximum output tokens
    temperature: Sampling temperature
    max_retries: Maximum retry attempts
    **kwargs: Additional Anthropic-specific parameters

Returns:
    LLMResponse with content and usage

Raises:
    ProviderInvocationError: If all retries fail
* `calculate_cost` (in `vibe_core/runtime/providers/anthropic.py`): Calculate cost based on Anthropic pricing.

Args:
    input_tokens: Number of input tokens
    output_tokens: Number of output tokens
    model: Model identifier

Returns:
    Cost in USD
* `get_available_models` (in `vibe_core/runtime/providers/anthropic.py`): Get list of available Anthropic models
* `is_available` (in `vibe_core/runtime/providers/anthropic.py`): Check if Anthropic provider is available
* `__init__` (in `vibe_core/runtime/providers/base.py`): Initialize provider with API key and configuration.

Args:
    api_key: API key for the provider (None for local models)
    **kwargs: Provider-specific configuration
* `invoke` (in `vibe_core/runtime/providers/base.py`): Invoke the LLM with a prompt.

Args:
    prompt: Input prompt
    model: Model identifier (provider-specific)
    max_tokens: Maximum output tokens
    temperature: Sampling temperature (0...
* `calculate_cost` (in `vibe_core/runtime/providers/base.py`): Calculate cost for token usage (provider-specific pricing).

Args:
    input_tokens: Number of input tokens
    output_tokens: Number of output tokens
    model: Model identifier

Returns:
    Cost in USD
* `get_available_models` (in `vibe_core/runtime/providers/base.py`): Get list of available models for this provider.

Returns:
    List of model identifiers
* `is_available` (in `vibe_core/runtime/providers/base.py`): Check if provider is available (API key set, network accessible, etc.)...
* `get_provider_name` (in `vibe_core/runtime/providers/base.py`): Get human-readable provider name.

Returns:
    Provider name (e...
* `__init__` (in `vibe_core/runtime/providers/base.py`): Initialize NoOp provider (no configuration needed)
* `invoke` (in `vibe_core/runtime/providers/base.py`): Return mock empty response
* `calculate_cost` (in `vibe_core/runtime/providers/base.py`): NoOp provider has zero cost
* `get_available_models` (in `vibe_core/runtime/providers/base.py`): NoOp provider has no real models
* `is_available` (in `vibe_core/runtime/providers/base.py`): NoOp provider is always available as fallback
* `create_provider` (in `vibe_core/runtime/providers/factory.py`): Create an LLM provider based on configuration.

Args:
    provider_name: Provider identifier ("anthropic", "openai", "local")
    api_key: API key for the provider (optional, loaded from env if not provided)
    model_name: Default model to use (provider-specific)
    **kwargs: Additional provider-specific configuration

Returns:
    LLMProvider instance (or NoOpProvider if creation fails)

Examples:
    # Create Anthropic provider
    provider = create_provider("anthropic", api_key="sk-...
* `get_default_provider` (in `vibe_core/runtime/providers/factory.py`): Get the default provider based on Phoenix Config.

This is the main entry point for most code that needs an LLM provider...
* `_detect_provider` (in `vibe_core/runtime/providers/factory.py`): Auto-detect which provider to use based on available API keys.

Priority order:
1...
* `_get_api_key_for_provider` (in `vibe_core/runtime/providers/factory.py`): Get API key for specified provider from environment.

Args:
    provider_name: Provider identifier

Returns:
    API key string or None
* `is_valid_key` (in `vibe_core/runtime/providers/factory.py`): Check if key is valid (not None, not empty, not a placeholder)
* `__init__` (in `vibe_core/runtime/providers/google.py`): Initialize Google Gemini provider.

Args:
    api_key: Google API key
    **kwargs: Additional configuration (unused for now)

Raises:
    ProviderNotAvailableError: If google-generativeai package not installed or API key invalid
* `invoke` (in `vibe_core/runtime/providers/google.py`): Invoke Gemini with a prompt.

Args:
    prompt: Input prompt
    model: Gemini model identifier (default: gemini-2...
* `calculate_cost` (in `vibe_core/runtime/providers/google.py`): Calculate cost based on Google Gemini pricing.

Args:
    input_tokens: Number of input tokens
    output_tokens: Number of output tokens
    model: Model identifier

Returns:
    Cost in USD
* `get_available_models` (in `vibe_core/runtime/providers/google.py`): Get list of available Google Gemini models
* `is_available` (in `vibe_core/runtime/providers/google.py`): Check if Google Gemini provider is available
### vibe_core -> scheduling
* `to_dict` (in `vibe_core/scheduling/task.py`): Serialize task to dictionary
### vibe_core -> specialists
* `__init__` (in `vibe_core/specialists/base_agent.py`): Initialize the agent.

Args:
    name: Agent instance name (e...
* `_detect_vibe_root` (in `vibe_core/specialists/base_agent.py`): Auto-detect the vibe-agency root directory.
* `_load_context` (in `vibe_core/specialists/base_agent.py`): Load execution context from .vibe/runtime/context...
* `_init_db_connection` (in `vibe_core/specialists/base_agent.py`): Initialize SQLiteStore connection safely (Shadow Mode).

[ARCH-005] Agents can now access the persistent database layer...
* `_verify_infrastructure` (in `vibe_core/specialists/base_agent.py`): Verify that required infrastructure is available.
* `execute_command` (in `vibe_core/specialists/base_agent.py`): Execute a command via the Runtime (GAD-5).

The command runs through bin/vibe-shell, which:
- Enforces MOTD
- Injects VIBE_CONTEXT
- Logs execution to audit trail
- Checks health before execution

Args:
    command: Command to execute
    timeout: Timeout in seconds (can also use timeout_seconds kwarg)
    prompt: Optional prompt/context to include in execution
    **kwargs: Additional parameters (e...
* `consult_knowledge` (in `vibe_core/specialists/base_agent.py`): Consult the knowledge base via the Knowledge system (GAD-6).

The agent asks: "Do we have a pattern/snippet/research for X?"
Instead of hallucinating, the agent gets facts...
* `read_knowledge_artifact` (in `vibe_core/specialists/base_agent.py`): Read the full content of a knowledge artifact.

Args:
    path: Path to artifact (relative to knowledge base)

Returns:
    File content or None if not found
* `report_status` (in `vibe_core/specialists/base_agent.py`): Report current status to Mission Control.

Returns agent state for logging and auditing...
* `get_context` (in `vibe_core/specialists/base_agent.py`): Get the execution context loaded from .vibe/runtime/context...
* `log_event` (in `vibe_core/specialists/base_agent.py`): Record an operational event to the database.

This is the foundation for agent audit logs, decision tracking, and
operational insight...
* `create_subtask` (in `vibe_core/specialists/base_agent.py`): Creates a child task in the database to track granular progress.
Returns the generated task_id...
* `update_subtask` (in `vibe_core/specialists/base_agent.py`): Updates the status of a subtask (e.g...
* `verify_work` (in `vibe_core/specialists/base_agent.py`): Verify work before committing/reporting success.

This method integrates with GAD-4 (Quality Assurance) to ensure
code quality and test coverage...
* `deliver_solution` (in `vibe_core/specialists/base_agent.py`): Deliver work atomically using the TaskExecutor.

This is the SAFE, COMPLETE, ATOMIC delivery workflow:
1...
* `__post_init__` (in `vibe_core/specialists/base_specialist.py`): Initialize empty lists if None
* `__init__` (in `vibe_core/specialists/base_specialist.py`): Initialize specialist with required dependencies.

Args:
    role: Specialist role (e...
* `_detect_playbook_root` (in `vibe_core/specialists/base_specialist.py`): Auto-detect playbook directory.

Searches for:
    1...
* `execute` (in `vibe_core/specialists/base_specialist.py`): Execute the specialist's phase-specific workflow.

This is the main entry point for specialist logic...
* `validate_preconditions` (in `vibe_core/specialists/base_specialist.py`): Validate that preconditions are met before execution.

This method MUST be called before execute()...
* `persist_state` (in `vibe_core/specialists/base_specialist.py`): Persist specialist state to SQLite.

Default implementation stores:
    - self...
* `load_state` (in `vibe_core/specialists/base_specialist.py`): Load specialist state from SQLite (crash recovery).

Default implementation loads most recent STATE_CHECKPOINT decision...
* `on_start` (in `vibe_core/specialists/base_specialist.py`): Hook called before execute() begins.

Use for:
    - Logging start event
    - Initializing resources
    - Recording start timestamp

Args:
    context: Mission context
* `on_complete` (in `vibe_core/specialists/base_specialist.py`): Hook called after successful execute().

Use for:
    - Logging completion event
    - Cleaning up resources
    - Recording completion timestamp
    - Persisting final state

Args:
    context: Mission context
    result: Execution result from execute()
* `on_error` (in `vibe_core/specialists/base_specialist.py`): Hook called when execute() raises an exception.

Use for:
    - Logging error details
    - Persisting partial state for recovery
    - Cleaning up resources
    - Returning error result

Args:
    context: Mission context
    error: Exception that was raised

Returns:
    SpecialistResult with success=False and error message
* `_log_decision` (in `vibe_core/specialists/base_specialist.py`): Log a decision to SQLite for audit trail.

All significant decisions (architecture choices, tool calls, etc...
* `_load_playbook` (in `vibe_core/specialists/base_specialist.py`): Load playbook YAML file for phase-specific workflow.

Playbooks define time-ordered workflows (PAD - Playbook Architecture)...
* `_calculate_duration` (in `vibe_core/specialists/base_specialist.py`): Calculate execution duration in seconds.

Returns:
    Duration in seconds (or 0...
* `get_mission_data` (in `vibe_core/specialists/base_specialist.py`): Get full mission data from SQLite.

Returns:
    Mission dict with all fields (phase, status, metadata, etc...
* `__repr__` (in `vibe_core/specialists/base_specialist.py`): String representation for debugging
* `_invoke_llm` (in `vibe_core/specialists/base_specialist.py`): Invoke LLM for code generation, patch generation, or analysis.

This is a lightweight utility for specialists to call LLM without
instantiating SimpleLLMAgent...
* `get_default_registry` (in `vibe_core/specialists/registry.py`): Get the default global registry instance (singleton pattern)

This is optional - orchestrator can create its own registry instance.
Singleton pattern is provided for convenience and testing...
* `__init__` (in `vibe_core/specialists/registry.py`): Initialize the agent registry with default specialists
* `_initialize_default_registry` (in `vibe_core/specialists/registry.py`): Initialize registry with default specialist mappings

This maps each ProjectPhase to its corresponding specialist class.
* `get_specialist` (in `vibe_core/specialists/registry.py`): Get specialist class for a given phase

Args:
    phase: ProjectPhase enum value

Returns:
    BaseSpecialist subclass for the phase

Raises:
    ValueError: If no specialist registered for phase

Example:
    specialist_class = registry.get_specialist(ProjectPhase...
* `register_specialist` (in `vibe_core/specialists/registry.py`): Register or override a specialist for a phase

This enables:
- Runtime specialist swapping
- A/B testing of specialist variants
- Mission-specific specialist customization (future 5D)

Args:
    phase: ProjectPhase enum value
    specialist_class: BaseSpecialist subclass to register

Example:
    # Override CODING specialist with custom variant
    registry.register_specialist(
        ProjectPhase...
* `list_specialists` (in `vibe_core/specialists/registry.py`): List all registered specialists

Returns:
    Dictionary mapping phase names to specialist class names

Example:
    >>> registry.list_specialists()
    {
        'PLANNING': 'PlanningSpecialist',
        'CODING': 'CodingSpecialist',...
* `__repr__` (in `vibe_core/specialists/registry.py`): String representation for debugging
### vibe_core -> store
* `__init__` (in `vibe_core/store/sqlite_store.py`): Initialize SQLiteStore

Args:
    db_path: Path to SQLite database file (REQUIRED).
             Use ":memory:" for ephemeral testing...
* `_load_schema` (in `vibe_core/store/sqlite_store.py`): Load schema from ARCH-001_schema.sql

Dynamically locates schema file relative to project root...
* `_commit` (in `vibe_core/store/sqlite_store.py`): Commit transaction (for thread-safe writes)
* `close` (in `vibe_core/store/sqlite_store.py`): Close database connection
* `__enter__` (in `vibe_core/store/sqlite_store.py`): Context manager entry
* `__exit__` (in `vibe_core/store/sqlite_store.py`): Context manager exit (auto-close connection)
* `_map_manifest_to_missions_row` (in `vibe_core/store/sqlite_store.py`): Adapter: Convert project_manifest.json to missions table row (v2)

This is the core adapter logic from SCHEMA_REALITY_CHECK...
* `create_mission` (in `vibe_core/store/sqlite_store.py`): Create a new mission (Schema v2)

Args:
    mission_uuid: External UUID identifier
    phase: SDLC phase (PLANNING, CODING, TESTING, DEPLOYMENT, MAINTENANCE)
    status: Mission status (pending, in_progress, completed, failed)
    created_at: ISO 8601 timestamp (optional, defaults to now)
    completed_at: ISO 8601 completion timestamp (optional)
    updated_at: ISO 8601 last update timestamp (optional)
    planning_sub_state: Planning sub-state (RESEARCH, BUSINESS_VALIDATION, FEATURE_SPECIFICATION)
    max_cost_usd: Maximum budget for mission (optional)
    current_cost_usd: Current spend (default: 0.0)
    alert_threshold: Budget alert threshold 0...
* `_parse_mission_row` (in `vibe_core/store/sqlite_store.py`): Parse mission row and deserialize JSON fields

Args:
    row: SQLite row

Returns:
    Mission dict with parsed JSON fields
* `get_mission` (in `vibe_core/store/sqlite_store.py`): Get mission by ID

Args:
    mission_id: Integer ID

Returns:
    Mission dict or None if not found
* `get_mission_by_uuid` (in `vibe_core/store/sqlite_store.py`): Get mission by UUID

Args:
    mission_uuid: External UUID string

Returns:
    Mission dict or None if not found
* `update_mission_status` (in `vibe_core/store/sqlite_store.py`): Update mission status

Args:
    mission_id: Integer ID
    status: New status (pending, in_progress, completed, failed)
    completed_at: ISO 8601 timestamp (optional)
* `get_mission_history` (in `vibe_core/store/sqlite_store.py`): Get all missions (history)

Returns:
    List of mission dicts, ordered by created_at DESC
* `get_all_missions` (in `vibe_core/store/sqlite_store.py`): Alias for get_mission_history()
* `delete_mission` (in `vibe_core/store/sqlite_store.py`): Delete mission (CASCADE DELETE removes related records)

Args:
    mission_id: Integer ID
* `update_mission_budget` (in `vibe_core/store/sqlite_store.py`): Update mission budget fields (v2)

Args:
    mission_id: Mission ID
    current_cost_usd: New current cost (optional)
    max_cost_usd: New max budget (optional)
    alert_threshold: New alert threshold (optional)
    cost_breakdown: New cost breakdown dict (optional)
* `get_missions_over_budget` (in `vibe_core/store/sqlite_store.py`): Get missions that exceed their budget (v2)

Returns:
    List of mission dicts where current_cost_usd > max_cost_usd
* `get_missions_by_owner` (in `vibe_core/store/sqlite_store.py`): Get missions by owner (v2)

Args:
    owner: Owner identifier (e.g...
* `log_tool_call` (in `vibe_core/store/sqlite_store.py`): Log tool execution

Args:
    mission_id: Parent mission ID
    tool_name: Tool name (e.g...
* `get_tool_call` (in `vibe_core/store/sqlite_store.py`): Get tool call by ID
* `get_tool_calls_for_mission` (in `vibe_core/store/sqlite_store.py`): Get all tool calls for a mission

Args:
    mission_id: Parent mission ID

Returns:
    List of tool call dicts, ordered by timestamp
* `record_decision` (in `vibe_core/store/sqlite_store.py`): Record agent decision

Args:
    mission_id: Parent mission ID
    decision_type: Type of decision (e.g...
* `get_decisions_for_mission` (in `vibe_core/store/sqlite_store.py`): Get all decisions for a mission

Args:
    mission_id: Parent mission ID

Returns:
    List of decision dicts, ordered by timestamp
* `set_memory` (in `vibe_core/store/sqlite_store.py`): Set agent memory (key-value storage)

Args:
    mission_id: Parent mission ID
    key: Memory key
    value: Memory value (will be JSON-serialized)
    timestamp: ISO 8601 timestamp
    ttl: Time-to-live in seconds (optional)

Note:
    If key already exists for mission, it will be updated (UPSERT)
* `get_memory` (in `vibe_core/store/sqlite_store.py`): Get agent memory by key

Args:
    mission_id: Parent mission ID
    key: Memory key

Returns:
    Memory dict or None if not found
* `create_playbook_run` (in `vibe_core/store/sqlite_store.py`): Create playbook run record

Args:
    mission_id: Parent mission ID
    playbook_name: Playbook identifier (e.g...
* `complete_playbook_run` (in `vibe_core/store/sqlite_store.py`): Complete playbook run with metrics

Args:
    run_id: Playbook run ID
    completed_at: ISO 8601 timestamp
    success: True if successful, False if failed
    metrics: Execution metrics as dict (optional)
* `get_playbook_run` (in `vibe_core/store/sqlite_store.py`): Get playbook run by ID
* `_ensure_tasks_table` (in `vibe_core/store/sqlite_store.py`): Ensure tasks table exists (created on-demand for ARCH-006).

This provides hierarchical task tracking for agents to break down work...
* `add_task` (in `vibe_core/store/sqlite_store.py`): Add a task for hierarchical tracking (ARCH-006).

Args:
    task_id: Unique task identifier (typically UUID)
    description: Human-readable task description
    parent_id: Parent task ID for hierarchy (None for root tasks)
    status: Initial status (default: 'pending')

Returns:
    task_id: The provided task_id
* `update_task_status` (in `vibe_core/store/sqlite_store.py`): Update task status and optional result (ARCH-006).

Args:
    task_id: Task ID to update
    status: New status ('pending', 'in_progress', 'completed', 'failed')
    result: Optional result data (will be JSON-serialized if dict/list)
* `get_task` (in `vibe_core/store/sqlite_store.py`): Get task by ID (ARCH-006).

Args:
    task_id: Task ID

Returns:
    Task dict or None if not found
* `get_subtasks` (in `vibe_core/store/sqlite_store.py`): Get all subtasks for a parent task (ARCH-006).

Args:
    parent_id: Parent task ID

Returns:
    List of task dicts
* `get_all_tasks` (in `vibe_core/store/sqlite_store.py`): Retrieves all tasks to reconstruct system state (ARCH-007).

Returns:
    List of all task dicts, parsed with JSON fields deserialized
* `add_roadmap` (in `vibe_core/store/sqlite_store.py`): Add or update a roadmap (UPSERT operation).

Args:
    roadmap_id: Unique roadmap identifier
    name: Roadmap name
    description: Roadmap description
    missions: List of mission IDs (optional)
    created_at: ISO 8601 timestamp (optional)
    updated_at: ISO 8601 timestamp (optional)
    metadata: Additional data (optional)

Returns:
    roadmap_id
* `get_roadmap` (in `vibe_core/store/sqlite_store.py`): Get roadmap by ID.

Args:
    roadmap_id: Roadmap ID

Returns:
    Roadmap dict or None if not found
* `get_all_roadmaps` (in `vibe_core/store/sqlite_store.py`): Get all roadmaps.

Returns:
    List of roadmap dicts
* `import_legacy_mission` (in `vibe_core/store/sqlite_store.py`): Import legacy mission from active_mission.json

Args:
    json_data: Mission data from JSON file

Returns:
    mission_id if imported, None if already exists

This method provides backward compatibility for JSON-based missions...
* `import_project_manifest` (in `vibe_core/store/sqlite_store.py`): Import project manifest and optional project memory to SQLite (ARCH-003)

This implements the Dual Write pattern:
- Convert project_manifest.json to missions table row
- Optionally import project_memory...
* `add_session_narrative` (in `vibe_core/store/sqlite_store.py`): Add session narrative entry (v2 - ProjectMemory)

Args:
    mission_id: Parent mission ID
    session_num: Session number (1, 2, 3, ....
* `get_session_narrative` (in `vibe_core/store/sqlite_store.py`): Get all session narrative for a mission (v2)

Args:
    mission_id: Parent mission ID

Returns:
    List of session dicts, ordered by session_num
* `add_artifact` (in `vibe_core/store/sqlite_store.py`): Add artifact entry (v2 - SDLC tracking)

Args:
    mission_id: Parent mission ID
    artifact_type: Artifact category ('planning', 'code', 'test', 'deployment')
    artifact_name: Artifact name (e.g...
* `get_artifacts` (in `vibe_core/store/sqlite_store.py`): Get artifacts for a mission (v2)

Args:
    mission_id: Parent mission ID
    artifact_type: Filter by artifact type (optional)

Returns:
    List of artifact dicts
* `record_quality_gate` (in `vibe_core/store/sqlite_store.py`): Record quality gate result (v2 - GAD-004)

Args:
    mission_id: Parent mission ID
    gate_name: Gate name (e.g...
* `get_quality_gates` (in `vibe_core/store/sqlite_store.py`): Get quality gates for a mission (v2)

Args:
    mission_id: Parent mission ID

Returns:
    List of quality gate dicts
* `add_domain_concept` (in `vibe_core/store/sqlite_store.py`): Add domain concept (v2 - ProjectMemory)

Args:
    mission_id: Parent mission ID
    concept: Concept keyword (e.g...
* `add_domain_concern` (in `vibe_core/store/sqlite_store.py`): Add domain concern (v2 - ProjectMemory)

Args:
    mission_id: Parent mission ID
    concern: Concern description (e.g...
* `get_domain_concepts` (in `vibe_core/store/sqlite_store.py`): Get domain concepts for a mission (v2)
* `get_domain_concerns` (in `vibe_core/store/sqlite_store.py`): Get domain concerns for a mission (v2)
* `set_trajectory` (in `vibe_core/store/sqlite_store.py`): Set trajectory for a mission (v2 - ProjectMemory)

Note: UPSERT operation - updates if exists, inserts if not

Args:
    mission_id: Parent mission ID
    current_phase: Current phase (PLANNING, CODING, etc.)
    updated_at: ISO 8601 timestamp
    current_focus: Current focus area (optional)
    completed_phases: List of completed phase names (optional)
    blockers: List of blocker descriptions (optional)
* `get_trajectory` (in `vibe_core/store/sqlite_store.py`): Get trajectory for a mission (v2)

Args:
    mission_id: Parent mission ID

Returns:
    Trajectory dict or None if not found
* `_map_project_memory_to_sql` (in `vibe_core/store/sqlite_store.py`): Adapter: Flatten project_memory.json into SQL tables (v2)

This is the complex flattening logic from SCHEMA_REALITY_CHECK...
### vibe_core -> task_management
* `__init__` (in `vibe_core/task_management/archive.py`): Initialize task archive.

Args:
    archive_path: Path to archive directory
* `archive_task` (in `vibe_core/task_management/archive.py`): Archive a completed task.

Args:
    task: Task to archive

Returns:
    True if archived successfully
* `get_archived_tasks` (in `vibe_core/task_management/archive.py`): Get all archived tasks.

Returns:
    List of archived task dictionaries
* `restore_task` (in `vibe_core/task_management/archive.py`): Restore a task from archive.

Args:
    task_id: ID of task to restore

Returns:
    Restored task or None
* `purge_archive` (in `vibe_core/task_management/archive.py`): Purge archived tasks older than specified days.

Args:
    older_than_days: Archive tasks older than this many days

Returns:
    Number of tasks purged
* `filter_tasks` (in `vibe_core/task_management/batch_operations.py`): Filter tasks based on predicate.

Args:
    tasks: Dictionary of tasks
    predicate: Function that returns True for tasks to keep

Returns:
    List of filtered tasks
* `filter_by_status` (in `vibe_core/task_management/batch_operations.py`): Get all tasks with a specific status.

Args:
    tasks: Dictionary of tasks
    status: Status to filter by

Returns:
    List of tasks with matching status
* `filter_by_priority` (in `vibe_core/task_management/batch_operations.py`): Get tasks within a priority range.

Args:
    tasks: Dictionary of tasks
    min_priority: Minimum priority (inclusive)
    max_priority: Maximum priority (inclusive)

Returns:
    List of tasks within priority range
* `filter_by_tag` (in `vibe_core/task_management/batch_operations.py`): Get all tasks with a specific tag.

Args:
    tasks: Dictionary of tasks
    tag: Tag to filter by

Returns:
    List of tasks with the tag
* `bulk_update_status` (in `vibe_core/task_management/batch_operations.py`): Update status for multiple tasks.

Args:
    tasks: Dictionary of tasks
    task_ids: List of task IDs to update
    new_status: New status to set

Returns:
    Number of tasks updated
* `bulk_add_tag` (in `vibe_core/task_management/batch_operations.py`): Add a tag to multiple tasks.

Args:
    tasks: Dictionary of tasks
    task_ids: List of task IDs to update
    tag: Tag to add

Returns:
    Number of tasks updated
* `bulk_remove_tag` (in `vibe_core/task_management/batch_operations.py`): Remove a tag from multiple tasks.

Args:
    tasks: Dictionary of tasks
    task_ids: List of task IDs to update
    tag: Tag to remove

Returns:
    Number of tasks updated
* `sort_tasks` (in `vibe_core/task_management/batch_operations.py`): Sort tasks by a field.

Args:
    tasks: List of tasks to sort
    key: Field to sort by (priority, created_at, updated_at)
    reverse: If True, sort descending

Returns:
    Sorted list of tasks
* `export_to_json` (in `vibe_core/task_management/export_engine.py`): Export tasks to JSON.

Args:
    tasks: Dictionary of tasks
    output_path: Path to write JSON file

Returns:
    True if successful
* `export_to_csv` (in `vibe_core/task_management/export_engine.py`): Export tasks to CSV.

Args:
    tasks: Dictionary of tasks
    output_path: Path to write CSV file

Returns:
    True if successful
* `export_to_markdown` (in `vibe_core/task_management/export_engine.py`): Export tasks to Markdown.

Args:
    tasks: Dictionary of tasks
    output_path: Path to write Markdown file

Returns:
    True if successful
* `export_summary` (in `vibe_core/task_management/export_engine.py`): Get a summary of task statistics.

Args:
    tasks: Dictionary of tasks

Returns:
    Summary statistics dictionary
* `__init__` (in `vibe_core/task_management/file_lock.py`): Initialize file lock.

Args:
    lock_path: Path to lock file
    timeout: Lock acquisition timeout in seconds
* `acquire` (in `vibe_core/task_management/file_lock.py`): Acquire the lock.

Returns:
    True if lock acquired, False if timeout
* `release` (in `vibe_core/task_management/file_lock.py`): Release the lock.
* `__enter__` (in `vibe_core/task_management/file_lock.py`): Context manager entry.
* `__exit__` (in `vibe_core/task_management/file_lock.py`): Context manager exit.
* `to_dict` (in `vibe_core/task_management/metrics.py`): Convert metrics to dictionary.
* `__init__` (in `vibe_core/task_management/metrics.py`): Initialize metrics collector.
* `update_from_tasks` (in `vibe_core/task_management/metrics.py`): Update metrics from task collection.

Args:
    tasks: Dictionary of tasks keyed by ID
* `get_metrics` (in `vibe_core/task_management/metrics.py`): Get current metrics.
* `to_dict` (in `vibe_core/task_management/models.py`): Convert task to dictionary.
* `to_dict` (in `vibe_core/task_management/models.py`): Convert mission to dictionary.
* `to_dict` (in `vibe_core/task_management/models.py`): Convert roadmap to dictionary.
* `_topology_aware_sort_key` (in `vibe_core/task_management/next_task_generator.py`): Generate sort key for topology-aware task routing.

Priority order (Gap 4...
* `get_next_task` (in `vibe_core/task_management/next_task_generator.py`): Get the next task to work on with topology-aware routing.

Priority order:
1...
* `get_next_tasks` (in `vibe_core/task_management/next_task_generator.py`): Get the next N tasks in topology-aware priority order.

Args:
    tasks: Dictionary of all tasks
    count: Number of tasks to return

Returns:
    List of next tasks, up to count (topology-sorted)
* `get_critical_tasks` (in `vibe_core/task_management/next_task_generator.py`): Get all critical (high priority) tasks.

Args:
    tasks: Dictionary of all tasks

Returns:
    List of critical tasks (priority >= 80)
* `suggest_next_action` (in `vibe_core/task_management/next_task_generator.py`): Suggest the next action based on task state.

Args:
    tasks: Dictionary of all tasks

Returns:
    Suggestion message
* `__init__` (in `vibe_core/task_management/task_manager.py`): Initialize task manager.

Args:
    project_root: Root directory of the project
    milk_ocean_router: Optional MilkOceanRouter instance for request routing
* `_load_tasks` (in `vibe_core/task_management/task_manager.py`): Load tasks from disk with VIMANA self-healing.
* `_hydrate_from_sqlite` (in `vibe_core/task_management/task_manager.py`): VIMANA SELF-HEALING: Regenerate tasks from SQLite if JSON missing.

This ensures the system can never lose data, even if...
* `_load_mission` (in `vibe_core/task_management/task_manager.py`): Load active mission from disk.
* `_save_tasks` (in `vibe_core/task_management/task_manager.py`): Save tasks to disk.
* `_save_mission` (in `vibe_core/task_management/task_manager.py`): Save active mission to disk.
* `_load_roadmap` (in `vibe_core/task_management/task_manager.py`): Load roadmap from disk with VIMANA self-healing.
* `_hydrate_roadmap_from_sqlite` (in `vibe_core/task_management/task_manager.py`): VIMANA SELF-HEALING: Regenerate roadmap from SQLite if YAML missing.

This ensures roadmaps persist across container restarts...
* `_save_roadmap` (in `vibe_core/task_management/task_manager.py`): Save roadmap to disk.
* `add_task` (in `vibe_core/task_management/task_manager.py`): Add a new task with topology-aware routing and optional roadmap linking.

Args:
    title: Task title
    description: Task description
    priority: Task priority (0-100)
    assigned_agent: Optional agent ID to assign task to (e...
* `update_task` (in `vibe_core/task_management/task_manager.py`): Update a task.

Args:
    task_id: Task ID
    **kwargs: Fields to update (title, description, status, priority, assignee, tags)

Returns:
    Updated task, or None if not found
* `get_task` (in `vibe_core/task_management/task_manager.py`): Get a task by ID.
* `list_tasks` (in `vibe_core/task_management/task_manager.py`): List tasks with optional filters.

Args:
    status: Filter by status
    priority: Filter by priority (exact match)
    tag: Filter by tag

Returns:
    List of filtered tasks
* `get_active_mission` (in `vibe_core/task_management/task_manager.py`): Get the active mission.
* `set_active_mission` (in `vibe_core/task_management/task_manager.py`): Set the active mission.

Args:
    title: Mission title
    description: Mission description

Returns:
    The created mission
* `get_next_task` (in `vibe_core/task_management/task_manager.py`): Get the next task to work on.
* `archive_task` (in `vibe_core/task_management/task_manager.py`): Archive a task.
* `get_metrics` (in `vibe_core/task_management/task_manager.py`): Get task metrics.
* `export_tasks_json` (in `vibe_core/task_management/task_manager.py`): Export tasks to JSON.
* `export_tasks_csv` (in `vibe_core/task_management/task_manager.py`): Export tasks to CSV.
* `export_tasks_markdown` (in `vibe_core/task_management/task_manager.py`): Export tasks to Markdown.
* `create_roadmap` (in `vibe_core/task_management/task_manager.py`): Create a new roadmap.

Args:
    name: Roadmap name
    description: Roadmap description
    missions: Optional list of mission IDs

Returns:
    The created roadmap
* `update_roadmap` (in `vibe_core/task_management/task_manager.py`): Update current roadmap.

Args:
    **kwargs: Fields to update (name, description, missions, metadata)

Returns:
    Updated roadmap, or None if no roadmap is active
* `assign_tasks_to_roadmap` (in `vibe_core/task_management/task_manager.py`): Assign tasks to a roadmap.

Args:
    task_ids: List of task IDs to assign
    roadmap_id: Roadmap ID to assign to

Returns:
    True if assignment succeeded
* `__init__` (in `vibe_core/task_management/validator_registry.py`): Initialize validator registry.
* `_register_defaults` (in `vibe_core/task_management/validator_registry.py`): Register default validators.
* `register` (in `vibe_core/task_management/validator_registry.py`): Register a validator for a field.

Args:
    field: Field name to validate
    validator: Callable that takes value and raises ValidationError
* `validate_task` (in `vibe_core/task_management/validator_registry.py`): Validate a task.

Args:
    task: Task to validate

Returns:
    True if valid

Raises:
    ValidationError if invalid
* `_validate_title` (in `vibe_core/task_management/validator_registry.py`): Validate task title.
* `_validate_status` (in `vibe_core/task_management/validator_registry.py`): Validate task status.
* `_validate_priority` (in `vibe_core/task_management/validator_registry.py`): Validate task priority.
### vibe_core -> tools
* `validate` (in `vibe_core/tools/agenda_tools.py`): Validate parameters.
* `execute` (in `vibe_core/tools/agenda_tools.py`): Execute task addition.

Appends a new task to the Outstanding Tasks section of BACKLOG...
* `validate` (in `vibe_core/tools/agenda_tools.py`): Validate parameters.
* `execute` (in `vibe_core/tools/agenda_tools.py`): Execute task listing.

Reads the backlog and returns tasks matching the status filter...
* `validate` (in `vibe_core/tools/agenda_tools.py`): Validate parameters.
* `execute` (in `vibe_core/tools/agenda_tools.py`): Execute task completion.

Finds and completes the task matching the description...
* `__init__` (in `vibe_core/tools/delegate_tool.py`): Initialize DelegateTool without kernel reference (Late Binding).

The kernel is injected AFTER construction via set_kernel() to break
the circular dependency:
- Kernel needs Agent
- Agent needs ToolRegistry
- DelegateTool needs Kernel

Solution: Tool initializes without kernel, then kernel is injected
after kernel boot via set_kernel(kernel)...
* `set_kernel` (in `vibe_core/tools/delegate_tool.py`): Inject kernel reference (Late Binding).

This method is called after kernel boot to provide the kernel
reference without creating circular dependencies...
* `validate` (in `vibe_core/tools/delegate_tool.py`): Validate delegation parameters.

Checks:
1...
* `execute` (in `vibe_core/tools/delegate_tool.py`): Execute task delegation.

Workflow:
1...
* `validate` (in `vibe_core/tools/file_tools.py`): Validate parameters.

Args:
    parameters: Must contain 'path' (string)

Raises:
    ValueError: If path missing or invalid
    TypeError: If path is not a string
* `execute` (in `vibe_core/tools/file_tools.py`): Execute file read operation.

Args:
    parameters: {"path": "/path/to/file...
* `validate` (in `vibe_core/tools/file_tools.py`): Validate parameters.

Args:
    parameters: Must contain 'path' and 'content' (strings)

Raises:
    ValueError: If required parameter missing or invalid
    TypeError: If parameter has wrong type
* `execute` (in `vibe_core/tools/file_tools.py`): Execute file write operation.

Args:
    parameters: {
        "path": "/path/to/file...
* `__init__` (in `vibe_core/tools/inspect_result.py`): Initialize the tool with a kernel reference.

Args:
    kernel: VibeKernel instance to query results from

Example:
    >>> kernel = VibeKernel()
    >>> tool = InspectResultTool(kernel)
* `name` (in `vibe_core/tools/inspect_result.py`): Return the tool name.
* `description` (in `vibe_core/tools/inspect_result.py`): Return a human-readable description.
* `parameters_schema` (in `vibe_core/tools/inspect_result.py`): Return JSON Schema for the tool's parameters.

Returns:
    dict: JSON Schema describing the tool's input parameters
* `validate` (in `vibe_core/tools/inspect_result.py`): Validate tool parameters.

Args:
    parameters: Tool parameters dict

Raises:
    ValueError: If required parameters missing or invalid
    TypeError: If parameters have wrong type
* `execute` (in `vibe_core/tools/inspect_result.py`): Execute the tool: query a task result from the ledger.

Parameters:
- task_id (required): The task ID to look up
- include_input (optional): If True, include the original task input (default: False)

Returns:
    ToolResult with success=True and output containing:
    - task_id: The queried task ID
    - status: COMPLETED, FAILED, STARTED, or NOT_FOUND
    - output: Agent's response (if COMPLETED)
    - error: Error message (if FAILED)
    - timestamp: When the task was recorded
    - input_payload: Original task input (if include_input=True)

Example:
    >>> result = tool...
* `validate` (in `vibe_core/tools/list_directory.py`): Validate parameters.

Args:
    parameters: Optional 'path' (string)
* `execute` (in `vibe_core/tools/list_directory.py`): Execute directory listing.

Args:
    parameters: {"path": "optional/path"}

Returns:
    ToolResult with list of file/directory names
* `validate` (in `vibe_core/tools/search_file.py`): Validate parameters.

Args:
    parameters: Must contain 'pattern' (string)
* `execute` (in `vibe_core/tools/search_file.py`): Execute file search.

Args:
    parameters: {"pattern": "*...
* `__repr__` (in `vibe_core/tools/tool_protocol.py`): String representation for debugging
* `__repr__` (in `vibe_core/tools/tool_protocol.py`): String representation for debugging
* `name` (in `vibe_core/tools/tool_protocol.py`): Return the unique name of this tool.

This name is used by agents to call the tool...
* `description` (in `vibe_core/tools/tool_protocol.py`): Return a human-readable description of what this tool does.

This description is shown to LLM agents in their system prompt
so they understand when to use this tool...
* `parameters_schema` (in `vibe_core/tools/tool_protocol.py`): Return the JSON schema for tool parameters.

Defines what parameters this tool accepts and their types...
* `validate` (in `vibe_core/tools/tool_protocol.py`): Validate that parameters meet requirements.

Called before execute() to ensure parameters are valid...
* `execute` (in `vibe_core/tools/tool_protocol.py`): Execute the tool with given parameters.

This is the main entry point for tool execution...
* `to_llm_description` (in `vibe_core/tools/tool_protocol.py`): Convert tool to LLM-friendly description.

This format is included in the LLM system prompt so agents
understand how to use this tool...
* `__repr__` (in `vibe_core/tools/tool_protocol.py`): String representation for debugging
* `__init__` (in `vibe_core/tools/tool_registry.py`): Initialize tool registry with optional Soul Governance and capability checking.

Args:
    invariant_checker: Optional InvariantChecker for Soul Governance (ARCH-029)...
* `register` (in `vibe_core/tools/tool_registry.py`): Register a tool with the registry.

Args:
    tool: Tool instance to register

Raises:
    ValueError: If tool with same name already registered
    TypeError: If tool doesn't implement Tool protocol

Example:
    >>> registry = ToolRegistry()
    >>> registry...
* `set_tool_capability` (in `vibe_core/tools/tool_registry.py`): Set the required capability for a tool.

SECURITY: Tools require capabilities to execute...
* `get` (in `vibe_core/tools/tool_registry.py`): Get a tool by name.

Args:
    tool_name: Name of the tool

Returns:
    Tool instance if found, None otherwise

Example:
    >>> tool = registry...
* `has` (in `vibe_core/tools/tool_registry.py`): Check if a tool is registered.

Args:
    tool_name: Name of the tool

Returns:
    True if tool registered, False otherwise

Example:
    >>> if registry...
* `list_tools` (in `vibe_core/tools/tool_registry.py`): Get list of all registered tool names.

Returns:
    List of tool names

Example:
    >>> print(registry...
* `execute` (in `vibe_core/tools/tool_registry.py`): Execute a tool call.

Workflow:
    1...
* `to_llm_prompt` (in `vibe_core/tools/tool_registry.py`): Generate LLM system prompt section describing available tools.

This is included in the agent's system prompt so the LLM knows
what tools it can use and how to call them...
* `get_tool_descriptions` (in `vibe_core/tools/tool_registry.py`): Get structured tool descriptions.

Returns list of tool descriptions in JSON format...
* `__len__` (in `vibe_core/tools/tool_registry.py`): Return number of registered tools
* `__repr__` (in `vibe_core/tools/tool_registry.py`): String representation for debugging

---

### Methodik:
Dieser Bericht wurde durch die Extraktion und semantische Analyse von Docstrings aus den Python-Skripten des Projekts generiert. Die Zusammenfassungen basieren auf den im Code vorhandenen Beschreibungen und einer heuristischen Gruppierung nach Dateipfaden. Es wurden keine externen LLMs für die semantische Analyse verwendet.
