# STEWARD PROTOCOL - Architecture Analysis Report

> **Generated:** 2025-12-03 20:04:14 UTC
> **Method:** Automated analysis scripts (reproducible)
> **Scripts:** docs/architecture/scripts/

---

## GAD Reference Analysis

```
======================================================================
GAD REFERENCE ANALYZER - Reverse Engineering Specs from Code
======================================================================

📚 Found 2 existing GAD documents:
   GAD-5000: docs/architecture/GAD-5000.md
   GAD-5500: docs/architecture/GAD-5500.md

🔍 Scanning codebase for GAD references...
   Found references to 36 unique GAD specifications

✅ DOCUMENTED GAD SPECS (have .md files):
----------------------------------------------------------------------
   GAD-5000: 15 references in 4 files
            Doc: docs/architecture/GAD-5000.md
   GAD-5500: 26 references in 15 files
            Doc: docs/architecture/GAD-5500.md

❌ UNDOCUMENTED GAD SPECS (code exists, no spec doc!):
----------------------------------------------------------------------

   GAD-000: 81 references in 38 files
   Files:
      - agent_city/registry/mechanic/__init__.py
      - agent_city/registry/mechanic/cartridge_main.py
      - scripts/final_launch.py
      - scripts/fix_manifests.py
      - scripts/run_server.py
      ... and 33 more
   Sample contexts:
      vibe_core/cli.py:9: GAD-000 (the human) commands. The system obeys....
      vibe_core/cli.py:380: print(f"          GAD-000:  {anchors.get('philosophy_hash', ...
      vibe_core/lineage.py:118: - GAD-000 (The Spirit): Operator Inversion Principle...

   GAD-002: 2 references in 2 files
   Files:
      - vibe_core/runtime/__init__.py
      - vibe_core/runtime/llm_client.py
   Sample contexts:
      vibe_core/runtime/__init__.py:5: GAD-002 Phase 3 Implementation...
      vibe_core/runtime/llm_client.py:6: Implements GAD-002 Decision 6 + GAD-511 Neural Adapter Strat...

   GAD-2: 1 references in 1 files
   Files:
      - vibe_core/specialists/base_agent.py
   Sample contexts:
      vibe_core/specialists/base_agent.py:562: # ATOMIC DELIVERY (GAD-2: The Atomic Gearbox)...

   GAD-003: 4 references in 1 files
   Files:
      - vibe_core/runtime/prompt_runtime.py
   Sample contexts:
      vibe_core/runtime/prompt_runtime.py:103: tools: list[str] = None  # GAD-003: List of available tool n...
      vibe_core/runtime/prompt_runtime.py:284: # GAD-003: Load tool definitions if agent uses tools...
      vibe_core/runtime/prompt_runtime.py:434: # === TOOLS (GAD-003 Phase 2) ===...

   GAD-4: 2 references in 1 files
   Files:
      - vibe_core/specialists/base_agent.py
   Sample contexts:
      vibe_core/specialists/base_agent.py:473: # CONNECTION TO FEET (GAD-4: Quality Assurance)...
      vibe_core/specialists/base_agent.py:485: This method integrates with GAD-4 (Quality Assurance) to ens...

   GAD-004: 2 references in 1 files
   Files:
      - vibe_core/store/sqlite_store.py
   Sample contexts:
      vibe_core/store/sqlite_store.py:1359: # v2: QUALITY GATES (GAD-004 Compliance)...
      vibe_core/store/sqlite_store.py:1371: Record quality gate result (v2 - GAD-004)...

   GAD-5: 5 references in 1 files
   Files:
      - vibe_core/specialists/base_agent.py
   Sample contexts:
      vibe_core/specialists/base_agent.py:6: - Body (GAD-5): Runtime execution via bin/vibe-shell...
      vibe_core/specialists/base_agent.py:57: 2. Execute commands safely via Runtime (GAD-5)...
      vibe_core/specialists/base_agent.py:164: f"Infrastructure incomplete. Missing: {missing}. Ensure GAD-...

   GAD-006: 1 references in 1 files
   Files:
      - vibe_core/runtime/prompt_context.py
   Sample contexts:
      vibe_core/runtime/prompt_context.py:322: Resolve inbox message count (GAD-006: Asynchronous Intent)....

   GAD-6: 5 references in 1 files
   Files:
      - vibe_core/specialists/base_agent.py
   Sample contexts:
      vibe_core/specialists/base_agent.py:8: - Arms (GAD-6): Knowledge retrieval via bin/vibe-knowledge...
      vibe_core/specialists/base_agent.py:58: 3. Consult knowledge base via Knowledge (GAD-6)...
      vibe_core/specialists/base_agent.py:164: f"Infrastructure incomplete. Missing: {missing}. Ensure GAD-...

   GAD-7: 4 references in 1 files
   Files:
      - vibe_core/specialists/base_agent.py
   Sample contexts:
      vibe_core/specialists/base_agent.py:7: - Brain (GAD-7): Mission control & orchestration...
      vibe_core/specialists/base_agent.py:59: 4. Report status to Mission Control (GAD-7)...
      vibe_core/specialists/base_agent.py:164: f"Infrastructure incomplete. Missing: {missing}. Ensure GAD-...

   GAD-100: 8 references in 3 files
   Files:
      - agent_city/registry/mechanic/cartridge_main.py
      - scripts/run_server.py
      - tests/city_simulation.py
   Sample contexts:
      agent_city/registry/mechanic/cartridge_main.py:611: # Validate configuration (GAD-100: Phoenix Configuration)...
      agent_city/registry/mechanic/cartridge_main.py:622: GAD-100: If the Soul (Config) is corrupted, the Body (Kernel...
      scripts/run_server.py:55: # Import Configuration (GAD-100: Phoenix Configuration)...

   GAD-201: 1 references in 1 files
   Files:
      - vibe_core/specialists/base_agent.py
   Sample contexts:
      vibe_core/specialists/base_agent.py:578: task_id: Task identifier (e.g., GAD-201_TASK_EXECUTOR)...

   GAD-301: 1 references in 1 files
   Files:
      - vibe_core/specialists/base_agent.py
   Sample contexts:
      vibe_core/specialists/base_agent.py:3: BaseAgent: The Integration Hub (GAD-301)...

   GAD-502: 1 references in 1 files
   Files:
      - vibe_core/runtime/context_loader.py
   Sample contexts:
      vibe_core/runtime/context_loader.py:200: # GAD-502: Context Projection - Vibe Injection...

   GAD-509: 8 references in 3 files
   Files:
      - vibe_core/runtime/circuit_breaker.py
      - vibe_core/runtime/llm_client.py
      - vibe_core/runtime/tool_safety_guard.py
   Sample contexts:
      vibe_core/runtime/tool_safety_guard.py:3: GAD-509 Extension: Tool Safety Guard ("Iron Dome")...
      vibe_core/runtime/tool_safety_guard.py:16: Version: 1.0 (GAD-509 Extension - Operation Iron Dome)...
      vibe_core/runtime/circuit_breaker.py:3: GAD-509: Circuit Breaker Protocol...

   GAD-510: 10 references in 2 files
   Files:
      - vibe_core/runtime/llm_client.py
      - vibe_core/runtime/quota_manager.py
   Sample contexts:
      vibe_core/runtime/llm_client.py:14: - Operational quotas (GAD-510)...
      vibe_core/runtime/llm_client.py:193: - Operational quotas (GAD-510)...
      vibe_core/runtime/llm_client.py:218: # Initialize safety layer (GAD-509 & GAD-510)...

   GAD-511: 20 references in 6 files
   Files:
      - vibe_core/runtime/llm_client.py
      - vibe_core/runtime/providers/__init__.py
      - vibe_core/runtime/providers/anthropic.py
      - vibe_core/runtime/providers/base.py
      - vibe_core/runtime/providers/factory.py
      ... and 1 more
   Sample contexts:
      vibe_core/runtime/llm_client.py:3: LLM Client - Provider-Agnostic Adapter (GAD-511 Refactor)...
      vibe_core/runtime/llm_client.py:6: Implements GAD-002 Decision 6 + GAD-511 Neural Adapter Strat...
      vibe_core/runtime/llm_client.py:9: - **Multi-provider support** (Anthropic, OpenAI, Local) via ...

   GAD-800: 1 references in 1 files
   Files:
      - steward/system_agents/envoy/tools/hil_assistant_tool.py
   Sample contexts:
      steward/system_agents/envoy/tools/hil_assistant_tool.py:11: - GAD-800 (Graceful Degradation): Reduces cognitive load....

   GAD-900: 3 references in 1 files
   Files:
      - scripts/final_launch.py
   Sample contexts:
      scripts/final_launch.py:3: Final Launch Script - GAD-900: The HIL-Operator Contract...
      scripts/final_launch.py:32: print("🚀 GAD-900: FINAL STRATEGIC LAUNCH")...
      scripts/final_launch.py:91: print("🎉 MISSION ACCOMPLISHED: GAD-900 CONTRACT FULFILLED")...

   GAD-902: 1 references in 1 files
   Files:
      - vibe_core/playbook/executor.py
   Sample contexts:
      vibe_core/playbook/executor.py:3: GAD-902: Graph Executor (Isolated Implementation)...

   GAD-903: 1 references in 1 files
   Files:
      - vibe_core/playbook/loader.py
   Sample contexts:
      vibe_core/playbook/loader.py:3: GAD-903: Workflow Loader (OPERATION SEMANTIC MOTOR - Phase 2...

   GAD-904: 3 references in 2 files
   Files:
      - vibe_core/playbook/executor.py
      - vibe_core/playbook/router.py
   Sample contexts:
      vibe_core/playbook/router.py:3: GAD-904: Agent Routing System (Neural Link)...
      vibe_core/playbook/executor.py:169: self.router = None  # AgentRouter (GAD-904) when connected...
      vibe_core/playbook/executor.py:178: # GAD-904: Neural link setup...

   GAD-905: 1 references in 1 files
   Files:
      - vibe_core/playbook/router_bridge.py
   Sample contexts:
      vibe_core/playbook/router_bridge.py:3: GAD-905: Router Bridge (Playbook → Registry Translation)...

   GAD-906: 3 references in 1 files
   Files:
      - vibe_core/playbook/executor.py
   Sample contexts:
      vibe_core/playbook/executor.py:171: self.lens_prompt = None  # GAD-906/907: Semantic lens inject...
      vibe_core/playbook/executor.py:189: Set semantic lens for mindset injection (GAD-906/907)....
      vibe_core/playbook/executor.py:485: # GAD-906/907: Semantic lens injection for mindset transform...

   GAD-908: 1 references in 1 files
   Files:
      - vibe_core/playbook/executor.py
   Sample contexts:
      vibe_core/playbook/executor.py:417: # GAD-908: Knowledge Context Injection (OPERATION INSIGHT)...

   GAD-909: 5 references in 4 files
   Files:
      - vibe_core/playbook/executor.py
      - vibe_core/runtime/__init__.py
      - vibe_core/runtime/prompt_context.py
      - vibe_core/runtime/prompt_registry.py
   Sample contexts:
      vibe_core/playbook/executor.py:393: # GAD-909: Resolve dynamic context (The Flesh / OPERATION CO...
      vibe_core/runtime/prompt_registry.py:505: ## SYSTEM CONTEXT (GAD-909: Dynamic Injection)...
      vibe_core/runtime/prompt_context.py:3: Prompt Context Engine - The Flesh (GAD-909)...

   GAD-913: 1 references in 1 files
   Files:
      - vibe_core/playbook/runner.py
   Sample contexts:
      vibe_core/playbook/runner.py:3: GAD-913: Playbook Runner (Cartridge Slot Implementation)...

   GAD-1000: 8 references in 3 files
   Files:
      - scripts/vibe_cli.py
      - steward/system_agents/auditor/tools/constitutional_verdict.py
      - steward/system_agents/watchman/cartridge_main.py
   Sample contexts:
      steward/system_agents/watchman/cartridge_main.py:73: r"requests\.get\s*\(",  # HTTP without GAD-1000 verification...
      steward/system_agents/watchman/cartridge_main.py:280: # Check for raw socket operations without GAD-1000 verificat...
      steward/system_agents/watchman/cartridge_main.py:297: "reason": "Unauthorized network operation detected - violate...

   GAD-1100: 1 references in 1 files
   Files:
      - steward/constitutional_oath.py
   Sample contexts:
      steward/constitutional_oath.py:98: INCLUDES NULL-POINTER PROTECTION & LEGACY MAPPING (GAD-1100)...

   GAD-3000: 2 references in 2 files
   Files:
      - vibe_core/store/sqlite_store.py
      - vibe_core/task_management/task_manager.py
   Sample contexts:
      vibe_core/task_management/task_manager.py:54: # VIMANA DUAL-CORE PERSISTENCE (GAD-3000)...
      vibe_core/store/sqlite_store.py:992: # ROADMAP PERSISTENCE (GAD-3000 VIMANA)...

   GAD-4000: 5 references in 2 files
   Files:
      - provider/universal_provider.py
      - scripts/standalone_tests/test_gad4000.py
   Sample contexts:
      provider/universal_provider.py:792: ABI LAYER (GAD-4000): Translates High-Level Intent to Low-Le...
      scripts/standalone_tests/test_gad4000.py:3: 🌌 GAD-4000 Fast-Path Execution Test...
      scripts/standalone_tests/test_gad4000.py:41: """Test the GAD-4000 Fast-Path routing"""...

   GAD-5001: 7 references in 2 files
   Files:
      - steward/system_agents/envoy/blueprint_generator.py
      - steward/system_agents/envoy/deterministic_executor.py
   Sample contexts:
      steward/system_agents/envoy/blueprint_generator.py:2: BLUEPRINT GENERATOR (GAD-5001: The Missing Bridge)...
      steward/system_agents/envoy/deterministic_executor.py:55: # Blueprint Generator (GAD-5001 Raw Input → Structured Param...
      steward/system_agents/envoy/deterministic_executor.py:141: # GAD-5001: Extracted blueprint values (replaces defaults)...

   GAD-6000: 4 references in 2 files
   Files:
      - provider/universal_provider.py
      - steward/system_agents/envoy/deterministic_executor.py
   Sample contexts:
      steward/system_agents/envoy/deterministic_executor.py:175: # Import LLM Engine (GAD-6000)...
      provider/universal_provider.py:57: # Import Legacy LLM Engine (GAD-6000) - for backward compati...
      provider/universal_provider.py:650: # Fallback: Use legacy llm engine if available (GAD-6000)...

   GAD-7000: 10 references in 3 files
   Files:
      - provider/llm_engine_adapter.py
      - provider/reflex_engine.py
      - provider/universal_provider.py
   Sample contexts:
      provider/universal_provider.py:40: # Import Strategy Pattern Engines (GAD-7000: NEURAL INJECTIO...
      provider/universal_provider.py:219: # === STRATEGY PATTERN ENGINES (GAD-7000: NEURAL INJECTION) ...
      provider/universal_provider.py:258: logger.info("🌌 Universal Provider GAD-5000 (DHARMIC) initial...

======================================================================
SUMMARY
======================================================================
   Documented:   2 GAD specs
   Undocumented: 34 GAD specs  ← NEED SPECS WRITTEN!

🔥 PRIORITY: Write specs for these undocumented GADs:
   GAD-000 (81 code references)
   GAD-511 (20 code references)
   GAD-510 (10 code references)
   GAD-7000 (10 code references)
   GAD-100 (8 code references)
   GAD-509 (8 code references)
   GAD-1000 (8 code references)
   GAD-5001 (7 code references)
   GAD-5 (5 code references)
   GAD-6 (5 code references)
   GAD-909 (5 code references)
   GAD-4000 (5 code references)
   GAD-003 (4 code references)
   GAD-7 (4 code references)
   GAD-6000 (4 code references)
   GAD-900 (3 code references)
   GAD-904 (3 code references)
   GAD-906 (3 code references)
   GAD-002 (2 code references)
   GAD-4 (2 code references)
   GAD-004 (2 code references)
   GAD-3000 (2 code references)
   GAD-2 (1 code references)
   GAD-006 (1 code references)
   GAD-201 (1 code references)
   GAD-301 (1 code references)
   GAD-502 (1 code references)
   GAD-800 (1 code references)
   GAD-902 (1 code references)
   GAD-903 (1 code references)
   GAD-905 (1 code references)
   GAD-908 (1 code references)
   GAD-913 (1 code references)
   GAD-1100 (1 code references)

```

---

## Kernel Module Analysis

```
======================================================================
KERNEL MODULE ANALYZER - vibe_core/ Deep Scan
======================================================================

📊 SUMMARY
   Total modules: 105
   Total lines:   26,537
   Total classes: 290
   Total functions: 40

📦 TOP 15 MODULES BY SIZE:
----------------------------------------------------------------------
    1316 lines | vibe_core/store/sqlite_store.py [GAD: 004,3000]
    1205 lines | vibe_core/kernel_impl.py
     923 lines | vibe_core/circuit_executor.py [GAD: 5500]
     784 lines | vibe_core/cli.py [GAD: 000]
     617 lines | vibe_core/semantic_syscalls.py [GAD: 5500]
     550 lines | vibe_core/agent_interface.py
     545 lines | vibe_core/playbook/executor.py [GAD: 904,906,909]
     478 lines | vibe_core/specialists/base_agent.py [GAD: 201,2,7]
     477 lines | vibe_core/runtime/prompt_runtime.py [GAD: 003]
     474 lines | vibe_core/topology.py
     466 lines | vibe_core/runtime/prompt_registry.py [GAD: 909]
     461 lines | vibe_core/task_management/task_manager.py [GAD: 3000]
     446 lines | vibe_core/operator_adapter.py
     410 lines | vibe_core/runtime/prompt_context.py [GAD: 909,006]
     409 lines | vibe_core/doc_renderer.py

📝 MODULES WITH SUBSTANTIAL DOCSTRINGS (potential specs):
----------------------------------------------------------------------

   📄 vibe_core/store/sqlite_store.py (1316 lines)
   GAD refs: 004, 3000
   " SQLite persistence layer for vibe-agency (Schema v2)  Implements ARCH-002: SQLiteStore class with CRUD operations for: - Missions (lifecycle tracking + budget + metadata) - Tool calls (audit trail) -..."

   📄 vibe_core/kernel_impl.py (1205 lines)
   GAD refs: None
   " ⚙️ REAL VIBE KERNEL IMPLEMENTATION ⚙️ =====================================  This is an actual working implementation of the VibeKernel that: 1. Manages a process table of agents 2. Runs a real task ..."

   📄 vibe_core/circuit_executor.py (923 lines)
   GAD refs: 5500
   " COGNITIVE CIRCUIT EXECUTOR ========================== GAD-5500: Neuro-Symbolic OS Implementation  This module executes Cognitive Circuits - semantic state machines that orchestrate kernel syscalls.  ..."

   📄 vibe_core/cli.py (784 lines)
   GAD refs: 000
   " 🎛️  THE STEWARD CLI - PHASE 7: THE STEERING WHEEL 🎛️ ======================================================  The command-line interface for controlling the STEWARD Protocol Agent OS.  This is the con..."

   📄 vibe_core/semantic_syscalls.py (617 lines)
   GAD refs: 5500
   " SEMANTIC SYSCALLS - Neuro-Symbolic Kernel Interface  This module defines the semantic syscall layer for the VibeOS kernel. Unlike procedural calls, semantic syscalls operate on MEANING, not just data..."

   📄 vibe_core/agent_interface.py (550 lines)
   GAD refs: None
   " AGENT SYSTEM INTERFACE - The Bridge Between Kernel and Agents ============================================================== ..."

   📄 vibe_core/playbook/executor.py (545 lines)
   GAD refs: 904, 906, 909, 908, 902
   " GAD-902: Graph Executor (Isolated Implementation) ===================================================  Orchestrates workflow execution using graph-based dependencies.  KEY PRINCIPLE: Pure logic first..."

   📄 vibe_core/specialists/base_agent.py (478 lines)
   GAD refs: 201, 2, 7, 301, 5, 6, 4
   " BaseAgent: The Integration Hub (GAD-301)  This is the abstract class that connects:   - Body (GAD-5): Runtime execution via bin/vibe-shell   - Brain (GAD-7): Mission control & orchestration   - Arms ..."

   📄 vibe_core/runtime/prompt_runtime.py (477 lines)
   GAD refs: 003
   " Prompt Runtime - AOS v0.2 Composition Engine  Composes atomized prompt fragments (core + task + knowledge + gates + context) into a final executable prompt for LLM execution.  Usage:     runtime = Pr..."

   📄 vibe_core/topology.py (474 lines)
   GAD refs: None
   " 🕉️ TOPOLOGY.PY - STEWARD PROTOCOL BHU-MANDALA ⛛ ================================================  Based on Srimad Bhagavata Purana, Canto 5 (Kosmologie).  Agent City is not a flat hierarchy. It is a ..."

   📄 vibe_core/runtime/prompt_registry.py (466 lines)
   GAD refs: 909
   " Prompt Registry - High-level interface for governed prompt composition  This is the "heart" of the system - provides automatic governance injection, context enrichment, and tool/SOP composition.  Usa..."

   📄 vibe_core/operator_adapter.py (446 lines)
   GAD refs: None
   " UNIVERSAL OPERATOR ADAPTER - TCP/IP for Agent Intelligence  PHOENIX VIMANA UNIFIED BOOT - Phase C  This module implements the operator-agnostic interface for Agent City OS. The system doesn't care WH..."

   📄 vibe_core/runtime/prompt_context.py (410 lines)
   GAD refs: 909, 006
   " Prompt Context Engine - The Flesh (GAD-909) ============================================  Provides dynamic context injection for prompts - the "flesh" that makes the skeleton (workflows) and voice (p..."

   📄 vibe_core/doc_renderer.py (409 lines)
   GAD refs: None
   " DocRenderer - Markdown document rendering for Kernel output.  EXTRACTED FROM kernel_impl.py to reduce kernel churn.  Kernel should ONLY: 1. Collect state (snapshot) 2. Call DocRenderer.render_all(sna..."

   📄 vibe_core/specialists/base_specialist.py (409 lines)
   GAD refs: None
   " BaseSpecialist - Abstract Base Class for HAP (Hierarchical Agent Pattern) ARCH-005: Design BaseSpecialist Interface  This module defines the contract that all specialist agents must implement. Specia..."

   📄 vibe_core/agents/system_maintenance.py (396 lines)
   GAD refs: None
   " System Maintenance Agent - ARCH-044  Agent for system-level maintenance operations (git sync, dependency updates, etc.). This is distinct from the MaintenanceSpecialist which handles production monit..."

   📄 vibe_core/playbook/runner.py (384 lines)
   GAD refs: 913
   " GAD-913: Playbook Runner (Cartridge Slot Implementation) =========================================================  Connects Playbook definitions to CoreOrchestrator execution.  A "Playbook" is a YAM..."

   📄 vibe_core/settings_sync.py (382 lines)
   GAD refs: None
   " SettingsSync - Bidirectional SETTINGS.md Interface  EXTRACTED FROM kernel_impl.py to reduce kernel complexity.  Implements the Command Queue pattern: 1. User writes commands in SETTINGS.md "Pending C..."

   📄 vibe_core/ledger.py (365 lines)
   GAD refs: None
   " ⚙️ VIBE CORE: LEDGER MODULE ⚙️ =====================================  The Immutable Memory of Agent City. Provides append-only event recording with cryptographic hash chaining for tamper detection.  ..."

   📄 vibe_core/boot_orchestrator.py (354 lines)
   GAD refs: None
   " ⚡ BOOT ORCHESTRATOR ⚡ ======================  The unified boot sequence for Agent City OS.  PHOENIX VIMANA UNIFIED BOOT - Sarga Integration ----------------------------------------------- This orches..."

   📄 vibe_core/llm/smart_local_provider.py (351 lines)
   GAD refs: None
   " Smart Local Provider - Offline Delegation Orchestrator (ARCH-041).  This provider enables the Operator to orchestrate the Specialist crew entirely offline, without external APIs.  Design: - Parses th..."

   📄 vibe_core/narasimha.py (324 lines)
   GAD refs: None
   " ⚡ NARASIMHA.PY - THE HYPERVISOR KILL-SWITCH ⚡ =======================================================================================  Based on Srimad Bhagavata Purana, Canto 7 (Prahlad and Narasimha..."

   📄 vibe_core/protocols/agent.py (311 lines)
   GAD refs: None
   " VibeAgent Protocol - Interface Definition  All agents running in VibeOS must implement this protocol. This is the contract between the kernel and cartridges. ..."

   📄 vibe_core/runtime/quota_manager.py (308 lines)
   GAD refs: 510
   " GAD-510: Operational Quota Manager ====================================  Tracks and enforces operational quotas to prevent surprise cost spikes and API rate limit hits.  Quotas tracked:   - Requests ..."

   📄 vibe_core/runtime/boot_sequence.py (304 lines)
   GAD refs: None
   "Boot Sequence - Main entry point for system-boot.sh → vibe-cli boot  Orchestrates the conveyor belt: 1. Context Loader → Collect signals 2. Playbook Engine → Route to task 3. Prompt Composer → Compose..."

   📄 vibe_core/lineage.py (300 lines)
   GAD refs: 000
   " ⛓️  PARAMPARA - THE LINEAGE CHAIN ⛓️ =====================================  "In the Vedic tradition, Parampara is the unbroken chain of disciplic succession. Each teacher receives knowledge from thei..."

   📄 vibe_core/process_manager.py (299 lines)
   GAD refs: None
   " PROCESS MANAGER - The "Airbag" System =====================================  Goal: Isolate agents in separate processes so one crash doesn't kill the kernel.  Architecture: - AgentProcess: A wrapper ..."

   📄 vibe_core/sarga.py (295 lines)
   GAD refs: None
   " 🌌 SARGA.PY - THE BOOT PROCESS AS COSMIC CREATION 🌌 ======================================================  Based on Srimad Bhagavata Purana, Canto 2 (Kosmologie).  SARGA = Creation. Evolution from ab..."

   📄 vibe_core/tools/agenda_tools.py (295 lines)
   GAD refs: None
   " Agenda Management Tools for vibe-agency OS (ARCH-045)  Provides tools for managing the backlog/agenda system. These tools allow agents to add, list, and complete tasks in the persistent backlog.  The..."

   📄 vibe_core/envoy_sync.py (292 lines)
   GAD refs: None
   " EnvoySync - Bidirectional ENVOY.md Terminal Interface  EXTRACTED FROM kernel_impl.py to reduce kernel complexity.  Implements the Async Dispatch pattern: 1. User writes request in ENVOY.md "Request" ..."

   📄 vibe_core/runtime/llm_client.py (289 lines)
   GAD refs: 510, 509, 002, 511
   " LLM Client - Provider-Agnostic Adapter (GAD-511 Refactor) ===========================================================  Implements GAD-002 Decision 6 + GAD-511 Neural Adapter Strategy  Features: - **M..."

   📄 vibe_core/agents/llm_agent.py (287 lines)
   GAD refs: None
   " Simple LLM-based agent for vibe-agency OS.  This module implements a generic agent that performs cognitive work via an LLM provider (ARCH-025).  Updated in ARCH-027 to support tool-use capability. ..."

   📄 vibe_core/tools/tool_registry.py (276 lines)
   GAD refs: None
   " Tool Registry for vibe-agency OS (ARCH-027 + ARCH-029)  Manages available tools and provides lookup/execution functionality. Integrates Soul Governance (ARCH-029) for security by design.  SECURITY (A..."

   📄 vibe_core/agents/context_aware_agent.py (270 lines)
   GAD refs: None
   " Context-Aware Agent Base Class with Offline-First Capabilities.  Provides: 1. Automatic context injection (PromptContext + PromptRegistry) 2. Graceful degradation via DegradationChain 3. chat_with_fa..."

   📄 vibe_core/agents/specialist_agent.py (264 lines)
   GAD refs: None
   " SpecialistAgent Adapter - Bridge between Kernel and Specialists (ARCH-026)  This module implements the adapter pattern that allows BaseSpecialist subclasses to work with the VibeKernel dispatch mecha..."

   📄 vibe_core/capability_registry.py (258 lines)
   GAD refs: None
   " ⚙️ VIBE CORE: CAPABILITY REGISTRY MODULE ⚙️ ==========================================  Capability Management System for Agent Governance.  This module implements the REVOKE_MANDATE feature, allowing..."

   📄 vibe_core/knowledge/graph.py (238 lines)
   GAD refs: None
   " Unified Knowledge Graph Implementation  The Universal Knowledge Graph with 4 Dimensions: - ONTOLOGY (Nodes): What exists - TOPOLOGY (Edges): How things relate - CONSTRAINTS (Rules): What is blocked -..."

   📄 vibe_core/runtime/oracle.py (234 lines)
   GAD refs: None
   " ARCH-064: KernelOracle - Single Source of Truth for System Capabilities  The Oracle is the **semantic backbone** of the system. It provides deterministic, factual information about what the kernel ca..."

   📄 vibe_core/runtime/context_loader.py (232 lines)
   GAD refs: 502
   "Context Loader - Conveyor Belt #1: Collect ALL signals  Loads project context from multiple sources: - Session handoff state - Git status - Test results - Project manifest - Environment checks ..."

   📄 vibe_core/protocols/operator_protocol.py (231 lines)
   GAD refs: None
   " OPERATOR PROTOCOL - Strictly Typed Universal Operator Interface  PHOENIX VIMANA UNIFIED BOOT PLAN - Section 4: Strict Typing Protocol  This module defines the HARD PROTOCOL for operator communication..."

   📄 vibe_core/tools/delegate_tool.py (229 lines)
   GAD refs: None
   " DelegateTool - ARCH-037: Inter-Agent Communication  Allows the Operator to delegate tasks to specialist agents.  This is the "intercom" that enables the Commander (Operator) to assign work to the Cre..."

   📄 vibe_core/runtime/project_memory.py (228 lines)
   GAD refs: None
   "Project Memory - Semantic layer for STEWARD intelligence  Tracks project narrative, domain understanding, evolution, and intent history across sessions. This is the "brain" that makes STEWARD understa..."

   📄 vibe_core/agent_protocol.py (221 lines)
   GAD refs: None
   " VibeAgent Protocol - Interface Definition  All agents running in VibeOS must implement this protocol. This is the contract between the kernel and cartridges. ..."

   📄 vibe_core/runtime/circuit_breaker.py (221 lines)
   GAD refs: 509
   " GAD-509: Circuit Breaker Protocol ==================================  Protects VIBE Agency OS from cascading failures when LLM API is degraded.  State Machine:   CLOSED (healthy) ──(5 failures/60s)──..."

   📄 vibe_core/vfs.py (219 lines)
   GAD refs: None
   " VIRTUAL FILESYSTEM (VFS) - Agent Sandboxing ===========================================  Goal: Prevent agents from accessing arbitrary files on the system.  Philosophy: "An agent's world is its sandb..."

   📄 vibe_core/runtime/hud.py (207 lines)
   GAD refs: None
   " ARCH-062: Heads-Up Display (HUD) & Discovery =============================================  Provides rich visual feedback for system state, making the invisible visible. The HUD transforms the "blank..."

   📄 vibe_core/runtime/tool_safety_guard.py (204 lines)
   GAD refs: 509
   " GAD-509 Extension: Tool Safety Guard ("Iron Dome") ===================================================  Protects VIBE Agency OS from dangerous tool operations that cause regressions.  This is a HARD ..."

   📄 vibe_core/tools/file_tools.py (201 lines)
   GAD refs: None
   " File operation tools for vibe-agency OS (ARCH-027)  Provides safe, auditable file read/write operations for LLM agents. ..."

   📄 vibe_core/tools/tool_protocol.py (200 lines)
   GAD refs: None
   " Tool Protocol for vibe-agency OS (ARCH-027)  Defines the clean interface that all tools must implement. This enables LLM agents to perform actions safely and extensibly.  Design Principles: - NO exec..."

   📄 vibe_core/tool_discovery.py (197 lines)
   GAD refs: None
   " Tool Discovery - Automatic tool registration from agent directories.  Scans agent tool directories and registers tools automatically. ..."

   📄 vibe_core/event_bus.py (194 lines)
   GAD refs: None
   " CANTO 10: THE FLUTE (Event Bus - The Song of Agents)  The Event Bus is the mechanism through which agents communicate their state changes. Instead of static logs, agents now "emit" events that are br..."

   📄 vibe_core/config/schema.py (190 lines)
   GAD refs: None
   " THE DHARMA SCHEMA: Pydantic Models for Configuration Validation  These models define the structure and constraints for the entire system. If the Soul (Config) is corrupted, the Body (Kernel) must not..."

   📄 vibe_core/runtime/semantic_actions.py (190 lines)
   GAD refs: None
   " Semantic Actions Framework (OPERATION SEMANTIC MOTOR - Phase 1) ================================================================  The "Nodes" in VIBE's graph-based orchestration system.  Semantic Act..."

   📄 vibe_core/playbook/router_bridge.py (186 lines)
   GAD refs: 905
   " GAD-905: Router Bridge (Playbook → Registry Translation) ========================================================  Connects the Playbook system to the Agent Registry (ProjectPhase orchestration).  MI..."

   📄 vibe_core/runtime/providers/google.py (185 lines)
   GAD refs: 511
   " GAD-511: Google Gemini Provider Implementation ===============================================  Concrete implementation of LLMProvider for Google's Gemini models.  Features: - Gemini 2.5 Flash (exper..."

   📄 vibe_core/agents/specialist_factory.py (184 lines)
   GAD refs: None
   " SpecialistFactoryAgent - ARCH-036 (Crew Assembly) ===================================================  Factory agent that creates Specialists on-demand for each task.  Problem: - Specialists require ..."

   📄 vibe_core/playbook/loader.py (182 lines)
   GAD refs: 903
   " GAD-903: Workflow Loader (OPERATION SEMANTIC MOTOR - Phase 2) ==============================================================  Connects the data layer (YAML workflows) to the logic layer (GraphExecuto..."

   📄 vibe_core/pulse.py (181 lines)
   GAD refs: None
   " CANTO 10: THE PULSE (Spandana - Primordial Vibration)  This module implements the heartbeat of the VibeOS system. Every agent's dance is choreographed by this rhythmic vibration.  The Pulse emits a J..."

   📄 vibe_core/cartridges/base.py (175 lines)
   GAD refs: None
   " CartridgeBase - ARCH-050  Base class for all Vibe OS cartridges (apps).  A Cartridge represents a specialized domain agent with:   1. Configuration (metadata, dependencies)   2. Initialization (load ..."

   📄 vibe_core/cartridges/registry.py (174 lines)
   GAD refs: None
   " CartridgeRegistry - ARCH-050  Centralized registry for Vibe OS cartridges.  This registry: 1. Maintains a mapping of cartridge names to their classes 2. Enables dynamic cartridge discovery and loadin..."

   📄 vibe_core/resource_manager.py (173 lines)
   GAD refs: None
   " RESOURCE MANAGER - Real OS-Level Enforcement ============================================  Goal: Make CivicBank credits REAL by enforcing CPU/RAM limits.  Philosophy: "Credits are not numbers in a da..."

   📄 vibe_core/llm/local_llama_provider.py (167 lines)
   GAD refs: None
   " Local LLM Provider - Offline Intelligence via llama.cpp.  Provides local LLM inference without API calls. Target: Smallest viable models (~400MB).  Models (preference order): 1. Qwen2.5-0.5B-Instruct..."

   📄 vibe_core/runtime/providers/base.py (167 lines)
   GAD refs: 511
   " GAD-511: Neural Adapter Strategy - Base Provider Interface ===========================================================  Abstract interface for LLM providers, enabling provider-agnostic integration (A..."

   📄 vibe_core/tools/inspect_result.py (167 lines)
   GAD refs: None
   " InspectResultTool - Agent tool for querying task results from ledger (ARCH-026 Phase 4).  This module provides a Tool that agents can use to query the results of previously submitted tasks. This is t..."

   📄 vibe_core/governance/invariants.py (166 lines)
   GAD refs: None
   " Invariant Checker for Vibe Agency Governance.  The InvariantChecker enforces the "Soul" of the system - hard constraints that must be satisfied before any tool execution. This is the "Über-Ich" (Supe..."

   📄 vibe_core/llm/degradation_chain.py (165 lines)
   GAD refs: None
   " Graceful Degradation Chain for Offline Operation.  Fallback order: 1. SemanticRouter (>0.85 confidence) -> Direct execution 2. SemanticRouter (0.60-0.85) -> Execute with clarification 3. LocalLLM (if..."

   📄 vibe_core/dependency_manager.py (164 lines)
   GAD refs: None
   " DEPENDENCY MANAGER - Central pyproject.toml Management ======================================================  Goal: Stop agents from creating requirements.txt Strategy: Provide kernel-level API for ..."

   📄 vibe_core/runtime/providers/anthropic.py (162 lines)
   GAD refs: 511
   " GAD-511: Anthropic Provider Implementation ===========================================  Concrete implementation of LLMProvider for Anthropic's Claude models.  Features: - Claude 3.5 Sonnet support - ..."

   📄 vibe_core/runtime/playbook_router.py (158 lines)
   GAD refs: None
   "Playbook Router - Conveyor Belt #2: Route to task  Routes user intent + context → task playbook Uses LEAN logic (simple if/else, no ML for MVP)  PHASE 3 WIRING: Integrated with MilkOceanRouter for Bra..."

   📄 vibe_core/runtime/prompt_composer.py (158 lines)
   GAD refs: None
   "Prompt Composer - Conveyor Belt #3: Compose final prompt  Composes task playbook + context → enriched prompt for STEWARD ..."

   📄 vibe_core/llm/steward_provider.py (157 lines)
   GAD refs: 000
   " Steward Provider - Claude Code Environment Integration (ARCH-033C).  This provider delegates cognitive work to the STEWARD (Claude Code environment) when primary LLM APIs are unavailable.  The STEWAR..."

   📄 vibe_core/llm/chain.py (154 lines)
   GAD refs: None
   " ChainProvider - ARCH-067 (Runtime Provider Cascade) ====================================================  A resilient provider that maintains a chain of fallback providers.  If the primary provider f..."

   📄 vibe_core/network_proxy.py (146 lines)
   GAD refs: None
   " KERNEL NETWORK PROXY - Controlled External Access =================================================  Goal: Prevent agents from making arbitrary network requests.  Philosophy: "The kernel is the gatew..."

   📄 vibe_core/phoenix_config.py (144 lines)
   GAD refs: None
   " Layer 3: Phoenix Configuration Engine Dynamic wiring of implementations to protocols.  This module provides the runtime system for connecting implementations (Layer 2) to protocols (Layer 1) based on..."

   📄 vibe_core/llm/google_adapter.py (144 lines)
   GAD refs: None
   " Google Provider Adapter for SimpleLLMAgent compatibility.  This adapter wraps vibe_core.runtime.providers.google.GoogleProvider to implement the chat-based interface expected by SimpleLLMAgent.  Arch..."

   📄 vibe_core/runtime/providers/factory.py (143 lines)
   GAD refs: 511
   " GAD-511: Provider Factory ==========================  Factory for creating and configuring LLM providers based on Phoenix Config.  Supports: - Provider selection via configuration - Automatic API key..."

   📄 vibe_core/specialists/registry.py (142 lines)
   GAD refs: None
   " AgentRegistry - ARCH-009 Centralized registry for specialist agents  This registry maps ProjectPhase to BaseSpecialist classes, providing a clean injection point for: - HAP (Hierarchical Agent Patter..."

   📄 vibe_core/config/loader.py (138 lines)
   GAD refs: None
   " CONFIG LOADER: Service for loading and managing configuration  Provides high-level interface for configuration management. ..."

   📄 vibe_core/kernel.py (132 lines)
   GAD refs: None
   " VibeKernel Interface Stub  This is a stub definition of the VibeKernel interface that steward-protocol cartridges depend on. When cartridges run in vibe-agency, they will use the actual implementatio..."

   📄 vibe_core/protocols/ledger.py (131 lines)
   GAD refs: None
   " VibeKernel Interface Stub  This is a stub definition of the VibeKernel interface that steward-protocol cartridges depend on. When cartridges run in vibe-agency, they will use the actual implementatio..."

   📄 vibe_core/knowledge/loader.py (120 lines)
   GAD refs: None
   " Knowledge Loader  Loads YAML files into the UnifiedKnowledgeGraph. Parses nodes, edges, constraints, and metrics from YAML format. ..."

   📄 vibe_core/llm/human_provider.py (106 lines)
   GAD refs: 000
   " Human Provider - Interactive LLM Provider with Operator-in-the-Loop.  This provider implements Human-in-the-Loop AI by prompting the human operator for responses instead of calling an external LLM AP..."

   📄 vibe_core/llm/provider.py (101 lines)
   GAD refs: None
   " LLM Provider abstraction for vibe-agency OS.  This module defines the standard interface for LLM providers (ARCH-025), enabling the kernel to orchestrate cognitive work via language models. ..."

   📄 vibe_core/settings_executor.py (95 lines)
   GAD refs: None
   " SettingsExecutor - Executes settings commands from SETTINGS.md  SEPARATED FROM kernel_impl.py to keep kernel clean.  This module handles the ACTUAL execution of settings commands: - RESTART agent.<id..."

   📄 vibe_core/knowledge/resolver.py (95 lines)
   GAD refs: None
   " Knowledge Resolver  High-level interface for agents to query knowledge. Provides semantic queries that map to graph operations. ..."

   📄 vibe_core/runtime/interface.py (88 lines)
   GAD refs: 000
   " ARCH-065: Polymorphic Interface Manager  The brain that detects and switches between interface modes.  Vibe OS is a shapeshifter: - Am I at a terminal? -> INTERACTIVE MODE (fancy UI, colors, wait for..."

   📄 vibe_core/tools/list_directory.py (84 lines)
   GAD refs: None
   " List Directory Tool for vibe-agency OS (ARCH-042).  Empowers the agent to explore the filesystem "Senses". ..."

   📄 vibe_core/knowledge/schema.py (76 lines)
   GAD refs: None
   " Knowledge Graph Schema Definitions  Defines the 4 dimensions of the Unified Knowledge Graph: - ONTOLOGY (Nodes): What exists - TOPOLOGY (Edges): How things relate - CONSTRAINTS (Rules): What is block..."

   📄 vibe_core/playbook/router.py (56 lines)
   GAD refs: 904
   " GAD-904: Agent Routing System (Neural Link) ===========================================  Connects Semantic Actions / Workflow Nodes to the best available Agent based on declared capabilities.  Phase:..."

   📄 vibe_core/scheduling/task.py (37 lines)
   GAD refs: None
   " Task Definition for VibeOS Scheduler  Tasks are the unit of work in VibeOS. Agents receive tasks from the kernel scheduler, process them, and return results. ..."

   📄 vibe_core/protocols/registry.py (25 lines)
   GAD refs: None
   " Manifest Registry Protocol - Interface Definition  BLOCKER #2: Layer 1 Protocol (no implementations) ..."

   📄 vibe_core/bridge.py (21 lines)
   GAD refs: None
   " 🌉 THE NEURAL BRIDGE 🌉 ======================  Kapselt die historische Weisheit (Steward) für den modernen Körper (Vibe).  This is the SOLE location where steward imports are allowed. All vibe_core mo..."

🔗 GAD REFERENCES PER MODULE:
----------------------------------------------------------------------
   GAD-000: 5 modules
      - vibe_core/cli.py
      - vibe_core/lineage.py
      - vibe_core/llm/steward_provider.py
      ... and 2 more
   GAD-511: 5 modules
      - vibe_core/runtime/llm_client.py
      - vibe_core/runtime/providers/google.py
      - vibe_core/runtime/providers/base.py
      ... and 2 more
   GAD-909: 3 modules
      - vibe_core/playbook/executor.py
      - vibe_core/runtime/prompt_registry.py
      - vibe_core/runtime/prompt_context.py
   GAD-509: 3 modules
      - vibe_core/runtime/llm_client.py
      - vibe_core/runtime/circuit_breaker.py
      - vibe_core/runtime/tool_safety_guard.py
   GAD-3000: 2 modules
      - vibe_core/store/sqlite_store.py
      - vibe_core/task_management/task_manager.py
   GAD-5500: 2 modules
      - vibe_core/circuit_executor.py
      - vibe_core/semantic_syscalls.py
   GAD-904: 2 modules
      - vibe_core/playbook/executor.py
      - vibe_core/playbook/router.py
   GAD-510: 2 modules
      - vibe_core/runtime/quota_manager.py
      - vibe_core/runtime/llm_client.py
   GAD-004: 1 modules
      - vibe_core/store/sqlite_store.py
   GAD-906: 1 modules
      - vibe_core/playbook/executor.py
   GAD-908: 1 modules
      - vibe_core/playbook/executor.py
   GAD-902: 1 modules
      - vibe_core/playbook/executor.py
   GAD-201: 1 modules
      - vibe_core/specialists/base_agent.py
   GAD-2: 1 modules
      - vibe_core/specialists/base_agent.py
   GAD-7: 1 modules
      - vibe_core/specialists/base_agent.py
   GAD-301: 1 modules
      - vibe_core/specialists/base_agent.py
   GAD-5: 1 modules
      - vibe_core/specialists/base_agent.py
   GAD-6: 1 modules
      - vibe_core/specialists/base_agent.py
   GAD-4: 1 modules
      - vibe_core/specialists/base_agent.py
   GAD-003: 1 modules
      - vibe_core/runtime/prompt_runtime.py
   GAD-006: 1 modules
      - vibe_core/runtime/prompt_context.py
   GAD-913: 1 modules
      - vibe_core/playbook/runner.py
   GAD-002: 1 modules
      - vibe_core/runtime/llm_client.py
   GAD-502: 1 modules
      - vibe_core/runtime/context_loader.py
   GAD-905: 1 modules
      - vibe_core/playbook/router_bridge.py
   GAD-903: 1 modules
      - vibe_core/playbook/loader.py

🏛️ CLASS INVENTORY (main classes):
----------------------------------------------------------------------

   vibe_core/store/sqlite_store.py:
      class SQLiteStore: [__init__, _load_schema, _commit, close, __enter__, ... (+47)]

   vibe_core/kernel_impl.py:
      class InMemoryScheduler: [__init__, submit_task, next_task, get_queue_status]
      class InMemoryManifestRegistry: [__init__, register, lookup, find_by_capability, list_all]
      class RealVibeKernel: [__init__, get_bank, get_vault, _check_agent_capability, _narasimha_destroy_agent, ... (+41)]

   vibe_core/circuit_executor.py:
      class InvariantViolation: []
      class InvariantChecker: [__init__, check_invariants, _evaluate_invariant, _resolve_path, _parse_value, ... (+2)]
      class CircuitState: []
      class CircuitExecutionResult: []
      class CognitiveCircuitExecutor: [__init__, set_meta_callbacks, _load_circuits, execute, _execute_circuit, ... (+5)]

   vibe_core/cli.py:
      class StewardCLI: [__init__, cmd_status, _check_kernel_pulse, _get_pulse_age, _check_parampara, ... (+15)]

   vibe_core/semantic_syscalls.py:
      class SyscallType: []
      class SyscallRequest: [__post_init__]
      class SyscallResult: []
      class SemanticSyscallExecutor: [__init__, execute, handle, _handle_spawn_cognition, _handle_grant_mandate, ... (+9)]
      class DynamicAgent: [__init__, get_manifest, process, report_status]

   vibe_core/agent_interface.py:
      class AgentSystemInterface: [__init__, _get_agent_config, add_dependency, get_dependencies, has_dependency, ... (+21)]

   vibe_core/playbook/executor.py:
      class ExecutionStatus: []
      class WorkflowNode: []
      class WorkflowEdge: []
      class WorkflowGraph: []
      class ExecutionPlan: []

   vibe_core/specialists/base_agent.py:
      class ExecutionResult: []
      class KnowledgeResult: []
      class BaseAgent: [__init__, _detect_vibe_root, _load_context, _init_db_connection, _verify_infrastructure, ... (+13)]

   vibe_core/runtime/prompt_runtime.py:
      class PromptRuntimeError: []
      class AgentNotFoundError: []
      class TaskNotFoundError: []
      class MalformedYAMLError: []
      class CompositionError: []

   vibe_core/topology.py:
      class Varsha: []
      class Agent: []
      class AgentPlacement: []
      class BhuMandalaTopology: [__init__, _initialize_varshas, _discover_and_place_agents, _place_discovered_agents, refresh, ... (+14)]

   vibe_core/runtime/prompt_registry.py:
      class PromptRegistryError: []
      class GovernanceLoadError: []
      class ContextEnrichmentError: []
      class PromptRegistry: [compose, register, get, _load_guardian_directives, _enrich_context, ... (+4)]

   vibe_core/task_management/task_manager.py:
      class TaskManager: [__init__, _load_tasks, _hydrate_from_sqlite, _load_mission, _save_tasks, ... (+19)]

   vibe_core/operator_adapter.py:
      class TerminalOperator: [__init__, is_available, get_operator_type, _parse_intent_type, _parse_target]
      class LocalLLMOperator: [__init__, is_available, get_operator_type, _build_prompt, _parse_response, ... (+1)]
      class DegradedOperator: [__init__, is_available, get_operator_type]
      class UniversalOperatorAdapter: [__init__, register_operator, _select_best_operator, hot_swap, get_current_operator_type, ... (+2)]

   vibe_core/runtime/prompt_context.py:
      class PromptContext: [__init__, set_kernel, _register_core_resolvers, register, resolve, ... (+11)]

   vibe_core/doc_renderer.py:
      class SettingsRenderState: []
      class EnvoyRenderState: []
      class DocRenderer: [render_unified_header, render_operations, render_settings, render_envoy, render_all]

   vibe_core/specialists/base_specialist.py:
      class MissionContext: []
      class SpecialistResult: [__post_init__]
      class BaseSpecialist: [__init__, _detect_playbook_root, execute, validate_preconditions, persist_state, ... (+10)]

   vibe_core/agents/system_maintenance.py:
      class SystemMaintenanceAgent: [__init__, agent_id, capabilities, process, _perform_system_update, ... (+5)]

   vibe_core/playbook/runner.py:
      class PlaybookError: []
      class PlaybookValidationError: []
      class PlaybookExecutionError: []
      class PlaybookAgent: []
      class PlaybookTool: []

   vibe_core/settings_sync.py:
      class SettingsSyncState: []
      class SettingsExecutionResult: []
      class SettingsSync: [__init__, check_file_changed, parse_commands, execute_commands, _execute_set, ... (+7)]

   vibe_core/ledger.py:
      class InMemoryLedger: [__init__, record_event, record_start, record_completion, record_failure, ... (+2)]
      class SQLiteLedger: [__init__, _initialize_db, record_event, record_start, record_completion, ... (+9)]

```

---

## Manifest Validation

```
======================================================================
MANIFEST VALIDATOR - steward.json Compliance Check
======================================================================

📦 Found 33 steward.json files

✅ VALID MANIFESTS (31):
----------------------------------------------------------------------
   ping                 | SYSTEM          | steward/system_agents/ping/steward.json
   civic                | GOVERNANCE      | steward/system_agents/civic/steward.json
   archivist            | SYSTEM          | steward/system_agents/archivist/steward.json
   discoverer           | GOVERNANCE      | steward/system_agents/discoverer/steward.json
   supreme_court        | JUSTICE         | steward/system_agents/supreme_court/steward.json
   oracle               | SYSTEM          | steward/system_agents/oracle/steward.json
   science              | INTELLIGENCE    | steward/system_agents/science/steward.json ⚠️ 1 warnings
   envoy                | INTERFACE       | steward/system_agents/envoy/steward.json
   forum                | COMMUNITY       | steward/system_agents/forum/steward.json
   watchman             | SYSTEM          | steward/system_agents/watchman/steward.json
   scribe               | INFRASTRUCTURE  | steward/system_agents/scribe/steward.json
   herald               | COMMUNICATIONS  | steward/system_agents/herald/steward.json ⚠️ 1 warnings
   chronicle            | SYSTEM          | steward/system_agents/chronicle/steward.json
   auditor              | SECURITY        | steward/system_agents/auditor/steward.json
   engineer             | INFRASTRUCTURE  | steward/system_agents/engineer/steward.json
   YOUR_AGENT_ID        | YOUR_DOMAIN     | steward/system_agents/engineer/templates/agent/steward.json ⚠️ 1 warnings
   analyst              | RESEARCH        | agent_city/registry/analyst/steward.json
   mechanic             | MAINTENANCE     | agent_city/registry/mechanic/steward.json
   agora                | COMMUNITY       | agent_city/registry/agora/steward.json
   ambassador           | DIPLOMACY       | agent_city/registry/ambassador/steward.json ⚠️ 1 warnings
   pulse                | MEDIA           | agent_city/registry/pulse/steward.json
   artisan              | MEDIA           | agent_city/registry/artisan/steward.json
   lens                 | OBSERVATION     | agent_city/registry/lens/steward.json
   market               | ECONOMY         | agent_city/registry/market/steward.json ⚠️ 1 warnings
   dhruva               | DATA_ETHICS     | agent_city/registry/dhruva/steward.json
   echo                 | TESTING         | agent_city/registry/citizens/echo/steward.json
   temple               | SPIRITUAL       | agent_city/registry/temple/steward.json ⚠️ 1 warnings
   shield               | SECURITY        | starter-packs/shield/steward.json
   scope                | RESEARCH        | starter-packs/scope/steward.json
   nexus                | COORDINATION    | starter-packs/nexus/steward.json ⚠️ 1 warnings
   spark                | MEDIA           | starter-packs/spark/steward.json

❌ INVALID MANIFESTS (2):
----------------------------------------------------------------------

   agent_city/registry/librarian/steward.json
      ❌ Missing specs.version
      ❌ Missing section: capabilities
      ❌ Missing governance.compliance_level
      ❌ Missing governance.constitution_hash
      ❌ Missing governance.issued_at
      ❌ Missing governance.issuer

   agent_city/registry/marketer/steward.json
      ❌ Missing specs.version
      ❌ Missing section: capabilities
      ❌ Missing governance.compliance_level
      ❌ Missing governance.constitution_hash
      ❌ Missing governance.issued_at
      ❌ Missing governance.issuer

⚠️ WARNINGS (11):
----------------------------------------------------------------------

   steward/system_agents/science/steward.json
      ⚠️ Unknown domain: INTELLIGENCE

   steward/system_agents/herald/steward.json
      ⚠️ Unknown domain: COMMUNICATIONS

   steward/system_agents/engineer/templates/agent/steward.json
      ⚠️ Unknown domain: YOUR_DOMAIN

   agent_city/registry/librarian/steward.json
      ⚠️ Unknown domain: KNOWLEDGE
      ⚠️ Constitution hash not set

   agent_city/registry/marketer/steward.json
      ⚠️ Unknown domain: CONTENT
      ⚠️ Constitution hash not set

   agent_city/registry/ambassador/steward.json
      ⚠️ Unknown domain: DIPLOMACY

   agent_city/registry/market/steward.json
      ⚠️ Unknown domain: ECONOMY

   agent_city/registry/temple/steward.json
      ⚠️ Unknown domain: SPIRITUAL

   starter-packs/nexus/steward.json
      ⚠️ Unknown domain: COORDINATION

📊 DOMAIN DISTRIBUTION:
----------------------------------------------------------------------
   COMMUNICATIONS: herald
   COMMUNITY: forum, agora
   CONTENT: marketer
   COORDINATION: nexus
   DATA_ETHICS: dhruva
   DIPLOMACY: ambassador
   ECONOMY: market
   GOVERNANCE: civic, discoverer
   INFRASTRUCTURE: scribe, engineer
   INTELLIGENCE: science
   INTERFACE: envoy
   JUSTICE: supreme_court
   KNOWLEDGE: librarian
   MAINTENANCE: mechanic
   MEDIA: pulse, artisan, spark
   OBSERVATION: lens
   RESEARCH: analyst, scope
   SECURITY: auditor, shield
   SPIRITUAL: temple
   SYSTEM: ping, archivist, oracle, watchman, chronicle
   TESTING: echo
   YOUR_DOMAIN: YOUR_AGENT_ID

======================================================================
SUMMARY
======================================================================
   Valid:    31
   Invalid:  2
   Warnings: 11
   Domains:  22

```

---

## Next Steps (Based on Analysis)

### Priority 1: Undocumented GAD Specs
Create formal specification documents for GADs with most code references.
See GAD Reference Analysis above for priority list.

### Priority 2: Invalid Manifests
Fix steward.json files that fail validation.
See Manifest Validation above for details.

### Priority 3: Module Documentation
Extract docstrings from large modules into formal specs.
See Kernel Module Analysis for candidates.

---

*This report is auto-generated. Re-run `run_all_analyzers.py` to refresh.*
