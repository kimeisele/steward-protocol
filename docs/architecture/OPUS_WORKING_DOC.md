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

*Last updated: Iteration 1 - Prompt templates added but Protocol not verified*
*Status: INCOMPLETE - Must iterate*
