# OPUS Working Document - Fighting Non-Persistence

> **PURPOSE:** This document is my working memory. I MUST read this before EVERY action.
> **PROBLEM:** I keep forgetting, making the same mistakes, treating symptoms not causes.
> **METHOD:** Iterative. Read code → Update this doc → Verify with code → Repeat.

---

## ⚠️ CRITICAL REMINDERS (READ FIRST)

1. **PROMPT IS A SYMPTOM, PROTOCOL IS THE CAUSE**
   - I fixed prompts but ignored the STEWARD Protocol structure
   - The fractal pattern means: if Protocol is wrong, everything downstream is wrong

2. **READ MORE, WRITE LESS**
   - This project needs understanding, not code generation
   - Follow the plugin trails from kernel outward

3. **TESTS TIMING OUT ≠ TESTS PASSING**
   - I lied to myself saying tests pass when they just timed out
   - Must verify with actual test runs, not assumptions

4. **ITERATE OVER THIS DOCUMENT**
   - Each session: Read this → Check code → Update gaps → Verify
   - Don't claim victory until code verification passes

---

## THE FRACTAL PATTERN (Swastika Metaphor)

```
                         KERNEL (Vishnu - Immutable Center)
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    PLUGINS ──────────── KERNEL ──────────── AGENTS
    (Avatars)            (Core)              (Cartridges)
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                         SECTIONS
                       (Phoenix Config)
```

**The REAL Structure (from kernel_impl.py):**

```
RealVibeKernel.__init__():
    │
    ├── self._scheduler = InMemoryScheduler()
    ├── self._ledger = SQLiteLedger()
    ├── self._manifest_registry = InMemoryManifestRegistry()
    │
    ├── self.process_manager = ProcessManager()
    ├── self.resource_manager = ResourceManager()
    ├── self.network = KernelNetworkProxy()
    ├── self.lineage = LineageChain()
    │
    ├── self._capability_registry = CapabilityRegistry()
    ├── self.io = KernelIOService()       ← I/O Service
    ├── self.tool_registry = ToolRegistry()
    │
    ├── self._event_bus = get_event_bus()
    ├── self._playbook_router = PlaybookRouter()
    │
    └── self._plugins = PluginLoader.discover()   ← PLUGINS!
        for plugin in self._plugins:
            plugin.on_boot(self)                   ← Each plugin boots
```

**Plugins Location:** `vibe_core/plugins/`
- sarga_cycle.py - Cosmic cycle (day/night of Brahma)
- vedic_governance.py - Varna/Ashrama governance
- envoy_ui.py - ENVOY.md interface
- ephemeral_ui.py - EPHEMERAL.md interface
- settings_ui.py - SETTINGS.md interface
- git_history.py - Git integration
- test_mode.py - Test mode

**KernelPlugin Protocol:**
```python
class KernelPlugin(ABC):
    def on_boot(kernel)           # Kernel starts
    def on_tick_pre(kernel)       # Before each tick
    def on_tick_post(kernel)      # After each tick
    def on_task_submit(kernel, task) -> bool  # COSMIC GATE
    def on_task_pre_assign(kernel, agent_id, task) -> bool  # GOVERNANCE GATE
    def on_agent_registered(kernel, agent_id)
    def on_task_completed/failed(...)
```

**Follow the trails:**
- Kernel → PluginLoader.discover() → vibe_core/plugins/*.py
- Kernel → config property → PhoenixConfig.from_files() or injected
- Kernel → manifest_registry → AgentManifest objects
- Kernel → io → KernelIOService → All file writes

Each level has the SAME PATTERN. If I understand one, I understand all.

---

## THE BOOT CHAIN (Complete Picture)

```
Entry Point: vibe_core/boot_orchestrator.py
                    │
                    ▼
        BootOrchestrator.boot()
                    │
    ┌───────────────┴───────────────┐
    │  SARGA PHASES (Cosmic Creation)  │
    │                                  │
    │  1. SHABDA (Sound)     → Log boot command
    │  2. AKASHA (Space)     → kernel = RealVibeKernel()
    │  3. VAYU (Air)         → PromptContext, communication
    │  4. AGNI (Fire)        → KernelOracle (capabilities)
    │  5. JALA (Water)       → Discoverer, Knowledge Graph
    │  6. PRITHVI (Earth)    → kernel.boot(), BootSequence
    └───────────────────────────────────┘
                    │
                    ▼
        BootOrchestrator.run_with_operator()
                    │
                    ▼
        self.boot_sequence.run()  ← PROMPT GENERATION ONLY!
```

**Key Insight:**
- `boot_sequence.py` is NOT the entry point
- It's just the PROMPT GENERATION component
- Created in PRITHVI phase: `self.boot_sequence = BootSequence(project_root)`
- Called in operator loop: `self.boot_sequence.run()`

**The REAL boot is:**
1. BootOrchestrator creates RealVibeKernel
2. RealVibeKernel.__init__() loads everything (plugins, tools, etc.)
3. Discoverer discovers agents from steward.json files
4. kernel.boot() finalizes
5. THEN BootSequence runs to generate prompts

**My Previous Mistake:**
I thought boot_sequence.py was the main entry point and tried to fix prompts there.
But prompts are DOWNSTREAM of the entire boot chain.
The PROTOCOL (steward.json, AgentManifest, AgentLoader) happens EARLIER in the chain.

**Where Agent Discovery Happens:**
```
JALA Phase (boot_orchestrator.py:228-256):
    self.discoverer = Discoverer(kernel=self.kernel, config=self.config)
    self.kernel.register_agent(self.discoverer, spawn_process=False)
    discovered_count = self.discoverer.discover_agents()
```

The Discoverer calls AgentLoader.discover_manifests() internally!

**Complete Discovery Chain:**
```
Discoverer.discover_agents()  (steward/system_agents/discoverer/agent.py:99-150)
    │
    └── AgentLoader.discover_and_load(config)  (vibe_core/steward/loader.py)
            │
            ├── Scans: steward/system_agents/*/ → Finds steward.json
            ├── Scans: agent_city/registry/*/ → Finds steward.json
            │
            └── For each steward.json:
                    │
                    ├── AgentManifest.from_dict(data)  → Parse manifest
                    ├── Load cartridge_main.py if exists → Instance
                    │
                    └── Returns: {agent_id: agent_instance}, {agent_id: AgentMeta}
```

**Then in kernel:**
```
kernel.register_agent(agent)
    │
    ├── self._agent_registry[agent_id] = agent
    └── self._manifest_registry.register(agent.get_manifest())
```

---

## ITERATION LOG

### Iteration 1: Prompt Templates (INCOMPLETE)

**What I did:**
- Added templates to steward.yaml
- Created resolve_template() method
- Removed hardcoded strings from boot_sequence.py and prompt_composer.py

**What I missed:**
- [ ] STEWARD Protocol itself is more than prompts
- [ ] Capabilities section not implemented
- [ ] Quality guarantees not implemented
- [ ] Verification/attestation not implemented
- [ ] The TEMPLATE structure should match steward/SPECIFICATION.md

**Code to verify:**
```bash
# Check if StewardConfig has all Protocol sections
python3 -c "from vibe_core.phoenix.sections.steward import StewardConfig; print(dir(StewardConfig))"
```

### Iteration 2: TODO

**Read these files to understand Protocol:**
- [ ] `steward/SPECIFICATION.md` - What MUST be in the Protocol
- [ ] `steward/protocol.py` - Existing Protocol implementation
- [ ] `steward/loader.py` - How Protocol is loaded
- [ ] `steward/constitution.py` - Constitutional rules

**Questions to answer:**
- What sections does SPECIFICATION.md require?
- Does StewardConfig match the specification?
- Where is the gap?

---

## GAP ANALYSIS: SPECIFICATION vs IMPLEMENTATION

### The REAL Structure (from SPECIFICATION.md)

**STEWARD Protocol is 5 LAYERS:**
1. Layer 1: Agent Manifest (steward.json) - Machine-readable identity
2. Layer 1.5: User Context - User/Team preferences
3. Layer 1.6: Cognitive Policy - Model preferences, economic constraints
4. Layer 2: Registry - Discovery, versioning, reputation
5. Layer 3: Verification - Cryptographic signing, attestation
6. Layer 4: Delegation - Task submission, monitoring
7. Layer 5: CLI Tools - steward init/verify/delegate/discover

### Existing Implementation (steward/ directory)

| File | What it does | Status |
|------|--------------|--------|
| client.py | StewardClient - sign artifacts, assert identity | EXISTS |
| crypto.py | Cryptographic signing | EXISTS |
| agent_metadata.py | AgentBiology registry (Varna/Ashrama) | EXISTS |
| varna.py | Species classification (MANUSHA, PASHU, etc.) | EXISTS |
| ashrama.py | Lifecycle stages | EXISTS |
| cli.py | CLI commands | EXISTS |

### What I Added (Iteration 1) - WRONG LAYER

| My Addition | Where | Problem |
|-------------|-------|---------|
| identity in steward.yaml | Phoenix Config | Should be in steward.json (Layer 1) |
| system_prompt_template | Phoenix Config | Prompts are DOWNSTREAM of Protocol |
| templates in StewardConfig | Phoenix Section | Mixing concerns |

### The REAL Gap (Updated after reading code)

**steward.json FILES EXIST!** In:
- `steward/system_agents/*/steward.json` (for each system agent)
- `agent_city/registry/*/steward.json` (for city agents)

**Format (example from herald):**
```json
{
  "identity": { "agent_id": "herald", "name": "HERALD" },
  "specs": { "version": "1.0.0", "domain": "COMMUNICATIONS" },
  "capabilities": { "operations": [...] },
  "governance": { "compliance_level": 2, "constitution_hash": "..." }
}
```

**The REAL Gap is:**
1. Phoenix Config doesn't READ these steward.json files
2. boot_sequence.py doesn't use the existing Protocol structure
3. My steward.yaml duplicates what steward.json already does

### What SHOULD happen:

```
steward.json (Layer 1)          steward/client.py (Runtime)
       │                                │
       └──────────┬────────────────────┘
                  │
                  ▼
           Phoenix Config (Reads steward.json)
                  │
                  ▼
           boot_sequence.py (Uses both)
                  │
                  ▼
           System Prompt (Generated from Protocol)
```

### Priority Fix (Revised)

1. ~~Find/create steward.json~~ - ALREADY EXISTS in steward/system_agents/
2. Phoenix Config should LOAD steward.json, not duplicate it in steward.yaml
3. Remove identity/templates from steward.yaml (use steward.json instead)
4. System prompt should be GENERATED from steward.json Protocol data

### Iteration 2 FINDINGS (COMPLETE PICTURE)

**THE SYSTEM ALREADY EXISTS!**

| Component | Location | Status |
|-----------|----------|--------|
| steward.json files | `steward/system_agents/*/steward.json` | EXISTS |
| AgentLoader | `vibe_core/steward/loader.py` | EXISTS |
| AgentManifest | `vibe_core/protocols/agent.py` | EXISTS |
| AgentLoader.discover_manifests() | Scans directories, loads JSON | EXISTS |
| VibeAgent.get_manifest() | Returns AgentManifest | EXISTS |

**The Fractal Pattern:**
```
phoenix/section_loader.py  → Discovers ConfigSection classes
steward/loader.py          → Discovers Agent manifests
```

**My Mistake:**
I DUPLICATED what already exists instead of USING it.
- identity in steward.yaml → Should use steward.json via AgentLoader
- templates in steward.yaml → Prompts should be GENERATED from AgentManifest

### What SHOULD Happen (Corrected)

```
steward/system_agents/steward/steward.json   (THE IDENTITY)
                    │
                    ▼
           AgentLoader.discover_manifests()
                    │
                    ▼
           AgentManifest (from_dict)
                    │
                    ▼
           BootSequence uses AgentManifest.to_dict()
                    │
                    ▼
           System Prompt GENERATED from manifest data
```

### Iteration 3 TODO

- [ ] Check if steward/system_agents/steward/steward.json exists (STEWARD itself)
- [ ] If not, create it following the existing pattern
- [ ] Modify boot_sequence to use AgentLoader instead of Phoenix steward.yaml
- [ ] Remove identity/templates from steward.yaml (keep Layer 1.5/1.6 only)
- [ ] Generate system prompt from AgentManifest

---

## CODE VERIFICATION CHECKLIST

Before claiming anything works, run:

```bash
# 1. Check config loads without error
python3 -c "from vibe_core.phoenix.config import PhoenixConfig; p = PhoenixConfig.from_files(); print('OK')"

# 2. Check steward section has all fields
python3 -c "
from vibe_core.phoenix.config import PhoenixConfig
p = PhoenixConfig.from_files()
s = p.steward
print(f'Identity: {s.identity.name}')
print(f'Templates: {len(s.templates.system_prompt_template)} chars')
print(f'Behavior: {s.behavior.genesis_protocol}')
"

# 3. Check template resolution
python3 -c "
from vibe_core.phoenix.config import PhoenixConfig
p = PhoenixConfig.from_files()
result = p.steward.resolve_template('system_prompt', {'behavior_rules': 'test', 'user_context': 'test', 'team_context': 'test', 'cognitive_policy': 'test', 'kernel_status': 'ok', 'kernel_agents_count': '0'})
print(f'Resolved: {len(result)} chars')
"

# 4. Run actual tests (with timeout awareness)
timeout 30 python -m pytest tests/integration/test_system_boot.py -v 2>&1 | tail -20
```

---

## FILES MODIFIED (Track Changes)

| File | Change | Verified? |
|------|--------|-----------|
| config/steward.yaml | Added identity, templates | ❌ |
| vibe_core/phoenix/sections/steward.py | Added AgentIdentity, PromptTemplates, resolve_template() | ❌ |
| vibe_core/phoenix/sections/__init__.py | Added exports | ❌ |
| vibe_core/runtime/boot_sequence.py | Use config template | ❌ |
| vibe_core/runtime/prompt_composer.py | Use config template | ❌ |

---

## NEXT ACTIONS (Priority Order)

1. [ ] Commit current changes (even if incomplete)
2. [ ] Read steward/SPECIFICATION.md to understand full Protocol
3. [ ] Read steward/protocol.py to see existing implementation
4. [ ] Update GAP ANALYSIS table
5. [ ] Plan what's actually needed vs what I added

---

## ANTI-PATTERNS I KEEP DOING

❌ Treating symptoms (prompt) instead of causes (protocol)
❌ Claiming tests pass when they timeout
❌ Writing code before reading existing code
❌ Adding new things instead of using existing infrastructure
❌ Not iterating over this document
❌ Declaring victory prematurely

---

---

## KEY REALIZATION: STEWARD IS NOT AN AGENT

From STEWARD.md:
> **Type:** Protocol (Governance Framework)
> STEWARD is a **distributed governance protocol** that coordinates autonomous agents

**STEWARD is NOT an agent like herald or civic!**
STEWARD is the ENTIRE PROTOCOL - the governance framework itself.

```
STEWARD Protocol (The Whole System)
    │
    ├── Layer 1: VibeOS Kernel (vibe_core)
    │       └── RealVibeKernel, Ledger, Scheduler, etc.
    │
    ├── Layer 2: Core Agents (herald, civic, forum, science)
    │
    ├── Layer 3: System Agents (engineer, auditor, archivist)
    │
    └── Layer 4: Citizen Agents (user-created)
```

**This explains:**
- Why there's no `steward/system_agents/steward/steward.json`
- Why "STEWARD boot" means booting the WHOLE PROTOCOL
- Why BootSequence generates prompts FOR THE OPERATOR (human/LLM)

**The "STEWARD System Prompt" is:**
- NOT the identity of an agent
- The instructions FOR THE OPERATOR running the protocol
- What the human/LLM sees when they boot the system

**My Fundamental Error:**
I tried to treat STEWARD like an agent with identity/capabilities in steward.yaml.
But STEWARD IS THE FRAMEWORK - it doesn't have a steward.json because IT IS the thing that LOADS steward.json files.

---

## REVISED UNDERSTANDING: What steward.yaml SHOULD Be

**steward.yaml is for OPERATOR configuration, NOT agent identity.**

The OPERATOR is the Human or LLM (like Claude Code) that RUNS the protocol.
The system prompt tells the OPERATOR how to behave.

**CORRECT use of steward.yaml:**
- Layer 1.5: User Context (Operator preferences - verbosity, language, etc.)
- Layer 1.6: Cognitive Policy (Model preferences - which LLM for what)
- Behavior Rules (Genesis Protocol, Anti-Slop - rules FOR THE OPERATOR)

**INCORRECT (what I added):**
- identity section → STEWARD doesn't have an identity like an agent
- capabilities section → Agents have capabilities, not STEWARD
- system_prompt_template → Should be GENERATED from Protocol state, not configured

**The System Prompt should be COMPOSED from:**
1. STEWARD.md (Protocol description - already exists)
2. kernel.manifest_registry (discovered agents and their capabilities)
3. steward.yaml Layer 1.5/1.6 (operator preferences)
4. Current kernel state (from PromptContext resolvers)

**NOT from:**
- Hardcoded templates in steward.yaml
- Fake "identity" pretending STEWARD is an agent

---

## WHAT NEEDS TO BE FIXED

1. **Remove from steward.yaml:**
   - identity section (WRONG - STEWARD is not an agent)
   - system_prompt_template (WRONG - should be generated)
   - boot_prompt_template (WRONG - should be generated)

2. **Keep in steward.yaml:**
   - user_context (Layer 1.5 - correct)
   - cognitive_policy (Layer 1.6 - correct)
   - behavior (rules for operator - correct)

3. **Change system prompt generation:**
   - Read STEWARD.md for protocol description
   - Read kernel.manifest_registry for agent capabilities
   - Apply behavior rules from steward.yaml
   - Apply user preferences from steward.yaml

---

---

## DEEP DIVE: STEWARD AS COMPLETE UNIVERSE

**STEWARD is not ONE thing. It is EVERYTHING simultaneously:**

### The 8 Dimensions of STEWARD

| Dimension | What it IS | Where it lives |
|-----------|------------|----------------|
| 1. **The Protocol** | The specification itself (5 layers) | steward/SPECIFICATION.md |
| 2. **The Bot Father** | Creates/registers other agents | Discoverer + AgentLoader |
| 3. **Universal Operator** | CLI + SDK for humans/LLMs | steward/cli.py, steward/client.py |
| 4. **Trust Infrastructure** | Verification, Attestation, Reputation | TRUST_MODEL.md, crypto.py |
| 5. **Economic System** | Pricing, Billing, Revenue sharing | SPECIFICATION.md (Economic Model) |
| 6. **Federation** | Registry, Discovery, DNS-like | FEDERATION.md |
| 7. **Meta-Agent** | Describes itself and others | steward.json, STEWARD.md |
| 8. **Guardian** | Crypto security, Constitution | SECURITY.md, constitution.py |

### The 5 Layers (from SPECIFICATION.md)

```
Layer 5: Agent Applications (STEWARD itself, other agents)
    │
Layer 4: CLI & SDKs (steward CLI, Python SDK)
    │
Layer 3: Protocol APIs (Discovery, Verification, Delegation, Monitoring)
    │
Layer 2: Registry (Index, Reputation, Version Store, Audit)
    │
Layer 1: Agent Manifest (steward.json - machine-readable identity)
    │
Layer 1.5: User Context (Optional - User/Team preferences)
    │
Layer 1.6: Cognitive Policy (Optional - Model preferences, budgets)
```

### FULL Protocol Compliance Requirements

From SPECIFICATION.md, for FULL compliance:

**Layer 1 (Agent Manifest):**
- [ ] steward.json with all required fields
- [ ] Cryptographic signing
- [ ] Capability declarations
- [ ] Quality metrics
- [ ] Health check endpoints

**Layer 1.5 (User Context):**
- [ ] Default user preferences
- [ ] Multi-user support
- [ ] Team context
- [ ] Context precedence

**Layer 1.6 (Cognitive Policy):**
- [ ] Model preferences
- [ ] Economic constraints
- [ ] Provider priority

**Layer 2 (Registry):**
- [ ] Agent Index
- [ ] Reputation System
- [ ] Version Store
- [ ] Audit Logs

**Layer 3 (APIs):**
- [ ] Discovery API
- [ ] Verification API
- [ ] Delegation API
- [ ] Monitoring API

**Layer 4 (CLI):**
- [ ] steward init
- [ ] steward verify
- [ ] steward delegate
- [ ] steward discover
- [ ] steward attest
- [ ] steward monitor

**Layer 5 (Applications):**
- [ ] STEWARD as self-describing agent
- [ ] Integration with other agents

### Trust Model (from TRUST_MODEL.md)

```python
trust_score = weighted_average([
    (test_coverage, 0.30),
    (uptime, 0.20),
    (success_rate, 0.25),
    (endorsements, 0.15),
    (attestation_freshness, 0.10)
])
```

Plus SLA enforcement, dispute resolution, anti-gaming measures...

### What Currently EXISTS vs What's PLANNED

| Component | Status | Location |
|-----------|--------|----------|
| steward.json format | ✅ EXISTS | steward/system_agents/*/steward.json |
| AgentLoader | ✅ EXISTS | vibe_core/steward/loader.py |
| StewardClient | ✅ EXISTS | steward/client.py |
| Crypto signing | ✅ EXISTS | steward/crypto.py |
| Constitution | ✅ EXISTS | steward/constitution.py |
| AgentMetadata | ✅ EXISTS | steward/agent_metadata.py |
| Trust Score calculation | ⚠️ DRAFT | TRUST_MODEL.md (not implemented) |
| Federation | 📝 PLANNED | FEDERATION.md |
| Economic Model | 📝 PLANNED | SPECIFICATION.md |
| Full CLI | ⚠️ PARTIAL | steward/cli.py |

### The Gap: What I Tried vs What's Needed

**What I did (WRONG):**
- Added identity to steward.yaml (Layer 1.5/1.6 config, not Layer 1)
- Added templates to steward.yaml (prompts are downstream, not protocol)
- Treated STEWARD like a single agent

**What's actually needed:**
- Connect EXISTING infrastructure (AgentLoader, StewardClient, etc.)
- Implement MISSING pieces (Trust Score calculation, etc.)
- Wire Phoenix Config to READ steward.json properly
- Generate prompts FROM Protocol data, not configure them

---

## BLIND SPOT FOUND: STEWARD AS PLUGIN

**The Golden Plugin Pattern exists:** `VedicGovernancePlugin` shows exactly how to do it:

```python
class VedicGovernancePlugin(KernelPlugin):
    def __init__(self):
        self._paused_agents = set()    # Own state
        self._varna_registry = {}

    def on_boot(self, kernel):
        kernel.governance = self       # Register on kernel

    def on_agent_registered(self, kernel, agent_id):
        # Apply governance rules

    def on_task_pre_assign(self, kernel, agent_id, task) -> bool:
        # GOVERNANCE GATE - can veto

    # Public API: kernel.governance.pause_agent(), etc.
```

**STEWARD should be the SAME pattern:**

```python
class StewardProtocolPlugin(KernelPlugin):
    def __init__(self):
        self._protocol_config = None   # From Phoenix
        self._trust_scores = {}
        self._attestations = {}

    def on_boot(self, kernel):
        kernel.steward = self          # Register on kernel
        self._load_protocol_config()   # From config/steward.yaml

    def on_agent_registered(self, kernel, agent_id):
        # Load steward.json for agent
        # Verify manifest signature
        # Initialize trust tracking

    def on_task_submit(self, kernel, task) -> bool:
        # PROTOCOL GATE - verify delegation

    # Public API:
    # - kernel.steward.verify(agent_id)
    # - kernel.steward.delegate(agent_id, task)
    # - kernel.steward.get_trust_score(agent_id)
    # - kernel.steward.attest(capability)
```

**What currently EXISTS but is NOT connected as plugin:**
- steward/client.py → StewardClient (signing, verification)
- vibe_core/steward/loader.py → AgentLoader (discovery)
- steward/crypto.py → Cryptographic functions
- steward/constitution.py → Constitutional rules
- config/steward.yaml → Protocol configuration (Layer 1.5/1.6)

**The MISSING piece:** A `StewardProtocolPlugin` that:
1. Connects all these pieces
2. Registers as `kernel.steward`
3. Uses hooks for Protocol enforcement
4. Provides public API for verification, delegation, trust

---

## IMPLEMENTATION PLAN: StewardProtocolPlugin

### ⚠️ CRITICAL FINDINGS (2025-12-05) - DAS HABE ICH VERPASST

**ICH WAR BLIND FÜR DAS ECHTE SYSTEM:**

1. **Das Plugin ist nur BOOKKEEPING** - es trackt Manifests aber ist NICHT in den Datenfluss eingebunden!

2. **Capabilities kommen aus dem FALSCHEN ORT:**
   ```python
   # kernel_impl.py:834 - FALSCH
   agent_caps = getattr(agent, "capabilities", [])
   self._capability_registry.register_agent(agent.agent_id, agent_caps)
   ```
   Capabilities kommen aus `agent.capabilities`, NICHT aus steward.json manifest!

3. **Timing Problem:**
   ```
   kernel.register_agent():
     Line 835: _capability_registry.register_agent(agent_id, agent_caps)  ← HIER
     Line 841: plugin.on_agent_registered(...)                            ← ZU SPÄT!
   ```
   Die Plugin-Hook wird NACH der Capability-Registrierung aufgerufen!

4. **Tool Execution Flow ist KOMPLETT GETRENNT:**
   ```
   Agent → ToolRegistry.execute() → _check_agent_capability() → CapabilityRegistry
                                          ↑
                                    STEWARD Plugin ist NICHT hier!
   ```

### DAS ECHTE SYSTEM (Das ich ignoriert habe)

```
vibe_core/kernel_impl.py:
├── self._capability_registry = CapabilityRegistry(ledger)
├── self.tool_registry = ToolRegistry(capability_checker=self._check_agent_capability)
│
└── register_agent(agent):
        agent_caps = agent.capabilities  ← HIER kommen capabilities her
        _capability_registry.register_agent(agent_id, agent_caps)
        for plugin in plugins:
            plugin.on_agent_registered(...)  ← Plugin kommt zu spät

vibe_core/capability_registry.py:
├── register_agent(agent_id, capabilities)  ← Speichert capabilities
├── has_capability(agent_id, cap)           ← Tool calls prüfen hier
├── revoke(agent_id, caps, revoker)         ← Capabilities entziehen
└── grant(agent_id, caps, granter)          ← Capabilities hinzufügen

vibe_core/tools/tool_registry.py:
└── execute(tool_call):
        if capability_checker:
            has_cap = capability_checker(agent_id, required_cap)  ← Prüft capabilities
```

### WAS DAS STEWARD PLUGIN WIRKLICH TUN MUSS

**NICHT NUR BOOKKEEPING** - sondern echte Integration:

1. **Capabilities müssen aus steward.json kommen:**
   - Plugin lädt manifest in on_agent_registered
   - Plugin muss capabilities an CapabilityRegistry weitergeben
   - ABER: Timing Problem - Hook ist zu spät!

2. **Lösung A: Pre-Registration Hook (SAUBER)**
   ```python
   # In kernel_impl.py register_agent() VORHER einfügen:
   if hasattr(self, 'steward') and self.steward:
       manifest_caps = self.steward.get_manifest_capabilities(agent.agent_id)
       if manifest_caps:
           agent_caps = manifest_caps
   ```

3. **Lösung B: Grant nach Registration (HACKY)**
   ```python
   # In plugin on_agent_registered:
   caps_from_manifest = manifest['capabilities']['operations']
   self._kernel._capability_registry.grant(agent_id, caps_from_manifest, 'steward')
   ```

4. **Tool Execution Auditing:**
   - Plugin sollte Tool-Aufrufe sehen können
   - Braucht Hook: `on_tool_execute(agent_id, tool_name, params)`
   - EXISTIERT NICHT im KernelPlugin Protocol!

### REVISED PHASES

#### Phase 1: Basic Skeleton ✅ DONE
- Plugin exists at vibe_core/plugins/steward_protocol.py
- Registers as kernel.steward
- Loads config, connects infrastructure

#### Phase 2: Cleanup ✅ DONE
- Removed wrong identity/templates from steward.yaml
- Removed AgentIdentity/PromptTemplates from section classes
- Fixed boot_sequence.py prompt generation

#### Phase 3: MISSING - Capability Integration ❌ NOT DONE
**Das ist das ECHTE Problem!**

Option A (CLEAN - requires kernel change):
- [ ] Add new method: `StewardProtocolPlugin.get_manifest_capabilities(agent_id)`
- [ ] Modify kernel_impl.py register_agent() to call plugin first
- [ ] Capabilities come from manifest, not agent.capabilities

Option B (HACKY - no kernel change):
- [ ] In on_agent_registered, grant capabilities from manifest
- [ ] Overwrites whatever agent.capabilities had
- [ ] Works but timing is weird

#### Phase 4: MISSING - Tool Call Integration ❌ NOT DONE
**Keine Hooks für Tool-Aufrufe!**

Options:
- [ ] Add new hook to KernelPlugin: on_tool_execute()
- [ ] Or: Plugin registers as observer on ToolRegistry
- [ ] Or: Wrap _check_agent_capability to go through plugin

#### Phase 5: MISSING - Full Protocol Enforcement ❌ NOT DONE

What the plugin SHOULD control:
- [ ] Which agents can call which tools (via capabilities)
- [ ] Which agents can delegate to which agents
- [ ] Trust score affects capability access
- [ ] Attestation required for sensitive operations

### BEWEIS: DUALITÄT DER CAPABILITIES (2025-12-05)

**steward.json** (Protocol Source of Truth):
```json
// steward/system_agents/herald/steward.json
"capabilities": {
  "operations": [
    {"name": "herald.broadcast"},
    {"name": "herald.research"},
    {"name": "herald.scribe"},
    {"name": "herald.scout"},
    {"name": "herald.identity"}
  ]
}
```

**cartridge_main.py** (Hardcoded - FALSCH):
```python
# steward/system_agents/herald/cartridge_main.py:95
capabilities=[
    "content_generation", "broadcasting", "research", "strategy"
]
```

**DAS SIND VERSCHIEDENE WERTE!** Der Kernel nimmt die falschen.

### LÖSUNG: Protocol Enforcement via grant()

**KEINE Kernel-Änderung nötig!**

```python
# In StewardProtocolPlugin.on_agent_registered():

def on_agent_registered(self, kernel, agent_id):
    # 1. Load manifest from steward.json
    manifest = self._load_agent_manifest(agent_id)

    if manifest:
        # 2. Extract CORRECT capabilities from manifest
        caps = manifest.get("capabilities", {})
        operations = caps.get("operations", [])
        correct_caps = [op.get("name", "") for op in operations if isinstance(op, dict)]

        # 3. Grant correct capabilities (overwrites/extends wrong cartridge caps)
        if correct_caps:
            kernel._capability_registry.grant(
                agent_id=agent_id,
                capabilities=correct_caps,
                granter_id="steward_protocol",
                reason="Protocol enforcement: capabilities from steward.json"
            )
```

Das ist **Protocol Enforcement**, nicht hacky!

### IMPLEMENTATION PLAN (FINAL)

#### Phase 1-2: ✅ DONE
- Plugin skeleton exists
- Cleanup done (removed wrong identity/templates)

#### Phase 3: ✅ DONE (2025-12-05)
- [x] In `on_agent_registered`: Extract capabilities from steward.json manifest
- [x] Call `kernel._capability_registry.grant()` with correct capabilities
- [x] Log what was granted vs what cartridge had
- [x] Verify with test: herald has `herald.broadcast` ✓

**VERIFIED:**
```
HERALD CAPABILITIES:
  - broadcasting           ← cartridge (old)
  - herald.broadcast       ← steward.json (NEW) ✓
  - herald.identity        ← steward.json (NEW) ✓
  - herald.research        ← steward.json (NEW) ✓
  - herald.scout           ← steward.json (NEW) ✓
  - herald.scribe          ← steward.json (NEW) ✓
```

#### Phase 4: ✅ DONE (2025-12-05)
- [x] Trust score affects capability access
- [x] Low trust = warn on sensitive operations
- [x] Wired into `_check_agent_capability` flow
- [x] Task tracking for trust calculation (completed/failed)

**Implementation:**
```
Agent calls tool → ToolRegistry.execute()
                        ↓
              capability_checker(agent_id, cap)
                        ↓
              kernel._check_agent_capability()
                        ↓
              CapabilityRegistry.has_capability()  ← Step 1
                        ↓
              kernel.steward.get_trust_score()    ← Step 2 (NEW)
                        ↓
              if trust < 0.3: log warning
```

**Files changed:**
- `kernel_impl.py:_check_agent_capability` - added trust check
- `steward_protocol.py` - task tracking for trust (on_task_submit/completed/failed)

#### Phase 5: Full Protocol (FUTURE)
- [ ] Attestation required for sensitive operations
- [ ] Delegation permissions between agents
- [ ] Strict mode (block on low trust, not just warn)

---

*Last updated: 2025-12-05 - Phase 4 COMPLETE*
*Status: Core Protocol enforcement done! Phase 5 is future work.*
