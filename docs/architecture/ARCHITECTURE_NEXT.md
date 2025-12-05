# ARCHITECTURE NEXT - Fraktal Plugin System

> **Purpose:** This document describes the NEXT phase of system architecture.
> **Previous:** OPUS_WORKING_DOC.md (STEWARD Protocol - COMPLETE)
> **Consultant Report:** [GEMINI_PRO.md](./GEMINI_PRO.md) (READ THIS FIRST!)
> **Status:** PLANNING

---

## 🎯 BATTLE PLAN: PHASE 2 (The Fraktal Transition)

**Status:** 🚀 READY FOR EXECUTION
**Consultant:** Gemini Pro (Architecture & Debugging)
**Executor:** Opus (Migration & Refactoring)

### 1. THE DEADLOCK BREAKER (Immediate Action)

**Objective:** Fix the test suite crash (`pytest --collect-only` hang) BEFORE migration.

| Task | Command / Action | Owner |
|------|------------------|-------|
| **Fix Package** | `touch tests/__init__.py` | Opus |
| **Fix Dependency** | `pip install ecdsa` | Opus |
| **Fix Crypto** | Refactor `steward/crypto.py` to use **Lazy Imports** for `ecdsa` | Opus |
| **Verify** | Run `pytest --collect-only` (Must be clean) | Opus |

### 2. MIGRATION ROADMAP (The 3 Phases)

#### Phase 2a: The Foundation (Short Term)
*Goal: Stabilize Kernel & Decouple Core Logic*

| Priority | Plugin | Source | Target | Why? |
|----------|--------|--------|--------|------|
| 🚨 **CRITICAL** | **Crypto** | `steward/crypto.py` | `vibe_core/plugins/crypto/` | Decouple hard dependency. |
| 🚨 **CRITICAL** | **Steward** | `plugins/steward_protocol.py` | `vibe_core/plugins/steward_protocol/` | Break the Monolith. |
| 🔴 **HIGH** | **Test Mode** | `plugins/test_mode.py` | `vibe_core/plugins/test_mode/` | Fix global state issues. |

#### Phase 2b: The Governance Layer (Medium Term)
*Goal: Modularize "Vedic Laws"*

| Priority | Plugin | Source | Target | Why? |
|----------|--------|--------|--------|------|
| 🟡 **MEDIUM** | **Governance** | `plugins/vedic_governance.py` | `vibe_core/plugins/vedic_governance/` | Foundational logic. |
| 🟡 **MEDIUM** | **Sarga** | `plugins/sarga_cycle.py` | `vibe_core/plugins/sarga_cycle/` | Scheduler gating. |

#### Phase 3: The Interface Layer (Long Term)
*Goal: Cleanup User-Space Plugins*

| Priority | Plugin | Source | Target | Why? |
|----------|--------|--------|--------|------|
| 🟢 **LOW** | **Git History** | `plugins/git_history.py` | `vibe_core/plugins/git_history/` | Analytics tool. |
| 🟢 **LOW** | **UI Plugins** | `plugins/*_ui.py` | `vibe_core/plugins/*_ui/` | Interface sync. |

### 3. ROLES & RESPONSIBILITIES (Parallel Flight)

**OPUS (Senior Steward - Fraktal Architecture):**
- ✅ Deadlock Breaker - DONE
- ✅ steward_protocol migrated - DONE
- ✅ plugin_template created - DONE
- ⏳ **CURRENT:** Fraktal deep work - UnifiedLoader für ALLE item types
- ⏳ Phoenix Config fraktal machen
- ⏳ Agent Loader alignment (steward.json → manifest.json)

**GEMINI (Builder - Plugin Migration):**
- [ ] **BUILD:** `test_mode/` - Migrate from test_mode.py
- [ ] **BUILD:** `sarga_cycle/` - Migrate from sarga_cycle.py
- [ ] **BUILD:** `vedic_governance/` - Migrate from vedic_governance.py
- [ ] **BUILD:** `crypto/` - Extract from steward/crypto.py
- [ ] **BUILD:** UI plugins (envoy_ui, settings_ui, ephemeral_ui, git_history)

**Parallel Flight Pattern:**
```
OPUS (Deep Architecture)          GEMINI (Bulk Migration)
─────────────────────────         ─────────────────────────
UnifiedLoader → ALL types         test_mode/ ✓
Phoenix fraktal                   sarga_cycle/ ✓
Agent alignment                   vedic_governance/ ✓
Schema validation                 crypto/ ✓
Pre-commit integration            UI plugins/ ✓
```

**CRITICAL for Gemini:** Each plugin MUST have:
1. `manifest.json` (use schema from `vibe_core/loaders/manifest_schema.json`)
2. `plugin_main.py` (NO global side effects!)
3. `__init__.py` (export the Plugin class)
4. Copy from `plugin_template/` as starting point

---

## 0. VEDA-4 COGNITIVE PATTERN (Das Fundament)

> "The infinite fractal rotating swastika zoom - it is so clear.
> Everywhere hang these 'bushes' - the fractal pattern."

### The Sacred Loop - Überall Gleich

```
SHABDA (शब्द)    → Capture Intent     "Was wurde gesagt/angefragt?"
ARTHA (अर्थ)     → Validate Meaning   "Was bedeutet das wirklich?"
PRATYAYA (प्रत्यय) → Verify Conditions  "Sind die Bedingungen erfüllt?"
KARMA (कर्म)     → Execute Action     "Führe aus"
```

Dieses Pattern ist **NICHT** nur für Circuits. Es ist für **ALLES**:

### VEDA-4 Applied to Plugin System

```
Plugin Boot:
    SHABDA    → Read config YAML (Was will der User?)
    ARTHA     → Parse/validate config (Was bedeutet das?)
    PRATYAYA  → Check dependencies met (Kann ich booten?)
    KARMA     → Execute on_boot() (Tu es)

Plugin Hook Call:
    SHABDA    → Receive hook event (Was ist passiert?)
    ARTHA     → Extract meaning (Welcher Agent? Welche Action?)
    PRATYAYA  → Check permissions (Darf das passieren?)
    KARMA     → Return decision (Allow/Veto/None)

Guard Check:
    SHABDA    → Read file content (Was steht da?)
    ARTHA     → Pattern match (Ist das ein Violation?)
    PRATYAYA  → Check severity (Ist das kritisch?)
    KARMA     → Report violation (Melde es)
```

### Fraktal Self-Similarity

```
Universe:    Brahman → Vishnu → Avatars
Kernel:      KernelProtocol → RealVibeKernel → Hooks
Plugin:      KernelPlugin → BasePlugin → ConfigurablePlugin → ConcretePlugin
Agent:       VibeAgent → OathMixin → GenericAgent → HeraldAgent
Circuit:     CircuitProtocol → SHABDA → ARTHA → PRATYAYA → KARMA
Guard:       GuardProtocol → BaseGuard → PatternGuard → ConcreteGuard
Config:      PhoenixConfig → Section → Field → Value
```

Jede Ebene folgt dem gleichen Pattern. Wenn es anders ist, ist es **falsch**.

---

## 1. CURRENT STATE (What we have)

### Kernel Hooks (COMPLETE - Never change again)

| Category | Hook | Status |
|----------|------|--------|
| Lifecycle | on_boot, on_tick_pre/post, on_shutdown | ✅ |
| Agent | on_agent_registered, on_agent_unregistered | ✅ |
| Task | on_task_submit, on_task_pre_assign, on_task_completed/failed | ✅ |
| Capability | on_capability_check | ✅ |
| Tool | on_tool_execute, on_tool_executed | ✅ |

### Current Plugins (10)

```
vibe_core/plugins/
├── __init__.py
├── sarga_cycle.py        # Cosmic Day/Night
├── vedic_governance.py   # Varna/Ashrama
├── steward_protocol.py   # Protocol Enforcement
├── envoy_ui.py           # ENVOY.md Interface
├── ephemeral_ui.py       # EPHEMERAL.md Interface
├── settings_ui.py        # SETTINGS.md Interface
├── git_history.py        # Git Analytics
├── test_mode.py          # Test Mode
└── test_orchestration.py # Test Discovery
```

---

## 2. THE FRAKTAL GAP (What's Different)

### 2.1 Agent Structure (4 Files - Golden Cartridge)

```
steward/system_agents/herald/
├── steward.json        ← Protocol Identity (MANIFEST)
├── cartridge.yaml      ← Config
├── cartridge_main.py   ← Entry Point (class *Cartridge)
├── STEWARD.md          ← Documentation
└── tools/              ← Optional
```

**Discovery:** `AgentLoader.discover_and_load()`
- Scans: `steward/system_agents/`, `agent_city/registry/`
- Looks for: `steward.json` or `manifest.json`
- Loads: `cartridge_main.py` → `*Cartridge` class
- Runtime: `Discoverer` agent does continuous monitoring

### 2.2 Plugin Structure (1 File - No Template)

```
vibe_core/plugins/
├── steward_protocol.py   ← Everything in ONE file
├── vedic_governance.py
├── envoy_ui.py
└── ...
```

**Discovery:** `PluginLoader.discover()`
- Scans: `vibe_core/plugins/`
- Looks for: ANY .py file with `KernelPlugin` subclass
- NO manifest file
- NO config file
- NO documentation template

### 2.3 The Gap

| Aspect | Agents | Plugins |
|--------|--------|---------|
| Manifest | steward.json | ❌ NONE |
| Config | cartridge.yaml | ❌ hardcoded |
| Discovery | AgentLoader + Discoverer | PluginLoader only |
| Hot-reload | ❌ No | ❌ No |
| Documentation | STEWARD.md | ❌ NONE |
| Structure | 4 files | 1 file |

### 2.4 Why This Matters

Agents can be:
- Discovered at runtime
- Configured via YAML
- Documented consistently
- Extended without changing core

Plugins are:
- Hardcoded Python
- No external config
- No discovery agent
- Changes require code edits

---

## 3. THE FRAKTAL SOLUTION

### 3.1 Plugin Cartridge Structure (Like Agents)

```
vibe_core/plugins/
├── steward_protocol/
│   ├── plugin.json       ← Manifest (like steward.json)
│   ├── plugin_main.py    ← Entry (like cartridge_main.py)
│   ├── config.yaml       ← Config (like cartridge.yaml)
│   └── PLUGIN.md         ← Docs (like STEWARD.md)
│
├── vedic_governance/
│   ├── plugin.json
│   ├── plugin_main.py
│   ├── config.yaml
│   └── PLUGIN.md
│
└── ... (other plugins)
```

### 3.2 PluginLoader Enhancement

```python
# vibe_core/plugin_loader.py - FRAKTAL VERSION
class PluginLoader:
    """
    Mirrors AgentLoader pattern:
    - Scans for plugin.json manifests
    - Loads plugin_main.py → *Plugin class
    - Reads config.yaml
    """

    SCAN_PATHS = [Path("vibe_core/plugins")]
    MANIFEST_FILENAMES = ["plugin.json", "manifest.json"]

    @classmethod
    def discover_and_load(cls) -> List[KernelPlugin]:
        # Same pattern as AgentLoader.discover_and_load()
        pass
```

### 3.3 PluginDiscoverer Agent (Optional)

Like Discoverer for agents, a PluginDiscoverer could:
- Monitor `vibe_core/plugins/` for new plugin.json files
- Hot-reload plugins at runtime
- Register/unregister plugins dynamically

**BUT:** This may be overkill. Plugins are more stable than agents.

### 3.4 Migration Strategy

**Option A: Keep 1-file plugins, add manifest**
- Add plugin.json next to each .py file
- PluginLoader reads both

**Option B: Full cartridge structure**
- Convert each plugin to folder with 4 files
- Maximum fraktal consistency

**Decision needed:** Which option?

---

## 4. THE REAL PROBLEM - LOADER EXPLOSION

### 4.1 All Loaders in the System

| Loader | Location | Discovers | Pattern |
|--------|----------|-----------|---------|
| **PluginLoader** | `vibe_core/plugin_loader.py` | KernelPlugin classes | scan .py → find subclass |
| **SectionLoader** | `vibe_core/phoenix/section_loader.py` | ConfigSection classes | scan .py → find section_id |
| **SettingsSectionLoader** | `vibe_core/settings/loader.py` | SettingsSection classes | scan .py → find subclass |
| **AgentLoader** | `vibe_core/steward/loader.py` | Agent manifests + cartridges | scan dirs → find manifest.json |
| **KnowledgeLoader** | `vibe_core/knowledge/loader.py` | Knowledge files | scan dirs → load files |
| **WorkflowLoader** | `vibe_core/playbook/loader.py` | Workflow YAML | scan .yaml files |
| **PlaybookLoader** | `vibe_core/playbook/runner.py` | Playbook definitions | scan playbooks |
| **ContextLoader** | `vibe_core/runtime/context_loader.py` | Context files | load context |
| **ToolDiscovery** | `vibe_core/tool_discovery.py` | Tool classes | scan for Tools |

### 4.2 The Pattern They ALL Follow

```
1. SHABDA  → Scan directory for files
2. ARTHA   → Find valid items (by class, manifest, or pattern)
3. PRATYAYA → Validate/filter
4. KARMA   → Return instances
```

### 4.3 What's DIFFERENT About Each

| Loader | Manifest? | Config? | Sub-items? |
|--------|-----------|---------|------------|
| PluginLoader | ❌ No | ❌ No | ❌ No |
| SectionLoader | ❌ No | ✅ YAML | ❌ No |
| SettingsSectionLoader | ❌ No | ❌ No | ❌ No |
| AgentLoader | ✅ steward.json | ✅ cartridge.yaml | ✅ tools/ |
| KnowledgeLoader | ❌ No | ❌ No | ❌ No |
| WorkflowLoader | ✅ YAML itself | ✅ YAML itself | ❌ No |

### 4.4 The UnifiedLoader Alignment Plan

**STATUS: Phase 1 COMPLETE** - `vibe_core/loaders/base_loader.py` exists!

```
vibe_core/loaders/
    __init__.py           ← ✅ DONE
    base_loader.py        ← ✅ DONE (UnifiedLoader ABC)
    manifest_schema.json  ← ✅ DONE (JSON Schema)
    schema.py             ← ✅ DONE (Validation)
```

**Phase 2: Loader Alignment** (Opus deep work)

| Loader | Current Location | Action | Complexity |
|--------|------------------|--------|------------|
| `AgentLoader` | `vibe_core/steward/loader.py` | Inherit UnifiedLoader | 🟢 LOW - already has manifest |
| `PluginLoader` | `vibe_core/plugin_loader.py` | Keep as-is, new items use folder | 🟢 LOW |
| `SectionLoader` | `vibe_core/phoenix/section_loader.py` | Add manifest.json support | 🟡 MEDIUM |
| `SettingsSectionLoader` | `vibe_core/settings/loader.py` | Merge with SectionLoader | 🟡 MEDIUM |
| `WorkflowLoader` | `vibe_core/playbook/loader.py` | Keep YAML-based (already has schema) | 🟢 LOW |
| `KnowledgeLoader` | `vibe_core/knowledge/loader.py` | Keep YAML-based | 🟢 LOW |
| `ContextLoader` | `vibe_core/runtime/context_loader.py` | Keep as-is (different purpose) | ⚪ SKIP |

**Alignment Strategy (NO BREAKING CHANGES):**

1. **AgentLoader** → KEEP AS-IS (it's the gold standard, UnifiedLoader was modeled after it)
2. **PluginLoader** → Works with both old .py AND new folders (backward compat)
3. **New folders** → Use UnifiedLoader pattern (manifest.json + {type}_main.py)
4. **YAML Loaders** → Keep YAML-native (WorkflowLoader, KnowledgeLoader)
5. **ContextLoader** → Skip (different purpose, not a discovery loader)

**Key Insight:** AgentLoader IS the fraktal pattern. UnifiedLoader was extracted FROM it.
The goal is NOT to change working code, but to ensure NEW code follows the pattern.

```
EXISTING (don't touch):          NEW (use UnifiedLoader pattern):
─────────────────────────        ─────────────────────────────────
AgentLoader (steward.json)       manifest.json
PluginLoader (backward compat)   plugin_template/ as reference
SectionLoader                    (future) section folders
```

---

## 5. THE UNIFIED CARTRIDGE PATTERN

### 5.1 The Universal Structure (ALLE Items)

```
{item_type}/{item_name}/
    manifest.json         ← SHABDA: Identity + Schema (required)
    {item_type}_main.py   ← KARMA: Entry Point (required)
    config.yaml           ← PRATYAYA: Local Config (optional)
    {sub_items}/          ← Scalable children (optional)
```

**Examples:**
```
vibe_core/plugins/steward_protocol/
    manifest.json         ← Plugin identity
    plugin_main.py        ← StewardProtocolPlugin class
    config.yaml           ← Plugin-specific settings (optional)
    validators/           ← Sub-items that scale

steward/system_agents/herald/
    manifest.json         ← Agent identity (currently steward.json)
    cartridge_main.py     ← HeraldCartridge class
    config.yaml           ← Agent-specific settings (currently cartridge.yaml)
    tools/                ← Sub-items that scale

vibe_core/phoenix/sections/kernel/
    manifest.json         ← Section identity
    section_main.py       ← KernelSection class
    config.yaml           ← Section defaults
```

### 5.2 The manifest.json Schema (SHABDA)

```json
{
  "$schema": "https://steward-protocol.org/schemas/manifest.v1.json",
  "type": "plugin|agent|section|workflow",
  "id": "steward_protocol",
  "name": "STEWARD Protocol Plugin",
  "version": "1.0.0",
  "description": "Protocol enforcement for Agent City",

  "entry_point": "plugin_main.py",
  "entry_class": "StewardProtocolPlugin",

  "config_schema": "config.schema.json",

  "sub_items": {
    "type": "validators",
    "path": "validators/"
  },

  "dependencies": ["vedic_governance"],
  "priority": 20
}
```

**Schema Validation:** If manifest.json doesn't validate → item NOT loaded. No exceptions.

### 5.3 The Config Hierarchy (PRATYAYA)

```
Priority (highest wins):
1. Environment Variables     → STEWARD_PLUGIN_STRICT_MODE=true
2. Phoenix Global Config     → config/plugins.yaml
3. Local config.yaml         → plugins/steward_protocol/config.yaml
4. Manifest Defaults         → manifest.json defaults
5. Code Defaults             → Python class defaults
```

**Phoenix Integration:**
```yaml
# config/plugins.yaml (global)
plugins:
  steward_protocol:
    enabled: true
    strict_mode: false

  vedic_governance:
    enabled: true
```

**Local Override:**
```yaml
# plugins/steward_protocol/config.yaml (local)
strict_mode: true  # Overrides global
custom_validators:
  - capability_check
  - trust_threshold
```

### 5.4 The Unified Loader (ONE Loader Pattern)

```python
# vibe_core/loaders/base_loader.py

class UnifiedLoader(ABC):
    """
    VEDA-4 Loader Pattern - Same for ALL item types.

    SHABDA   → scan_directory() + load_manifest()
    ARTHA    → validate_manifest()
    PRATYAYA → load_config() + check_dependencies()
    KARMA    → instantiate()
    """

    # Override in subclass
    item_type: str           # "plugin", "agent", "section"
    scan_paths: List[Path]   # Where to look
    entry_suffix: str        # "_main.py", "_cartridge.py"

    @classmethod
    def discover_and_load(cls, config: PhoenixConfig) -> Dict[str, Any]:
        """The universal discovery loop."""
        items = {}

        for path in cls.scan_paths:
            for item_dir in path.iterdir():
                if not item_dir.is_dir():
                    continue

                # SHABDA - Read manifest
                manifest = cls.load_manifest(item_dir)
                if not manifest:
                    continue

                # ARTHA - Validate
                if not cls.validate_manifest(manifest):
                    logger.error(f"Invalid manifest: {item_dir}")
                    continue

                # PRATYAYA - Load config
                item_config = cls.load_config(item_dir, config)
                if not item_config.get("enabled", True):
                    logger.info(f"Disabled: {manifest['id']}")
                    continue

                # KARMA - Instantiate
                instance = cls.instantiate(item_dir, manifest, item_config)
                if instance:
                    items[manifest["id"]] = instance

        return items
```

### 5.5 Migration Path

**Phase 1: Create Schema + Loader**
- [ ] Define manifest.json JSON Schema
- [ ] Create UnifiedLoader base class
- [ ] Create schema validator (pre-flight check)

**Phase 2: Migrate Plugins First**
- [ ] Convert steward_protocol.py → steward_protocol/
- [ ] Convert vedic_governance.py → vedic_governance/
- [ ] Convert UI plugins (envoy_ui, settings_ui, ephemeral_ui)
- [ ] Update PluginLoader to use UnifiedLoader

**Phase 3: Align Agents**
- [ ] Rename steward.json → manifest.json (or alias)
- [ ] Rename cartridge.yaml → config.yaml (or alias)
- [ ] Update AgentLoader to use UnifiedLoader

**Phase 4: Align Phoenix Sections**
- [ ] Convert sections to folder structure
- [ ] Update SectionLoader to use UnifiedLoader

**Phase 5: Pre-flight Validation**
- [ ] Add manifest validation to pre-commit hook
- [ ] Add schema check to CI/CD
- [ ] No "good will" - invalid = rejected

### 5.6 Pre-flight Schema Validation

```bash
# .githooks/pre-commit addition
python -m vibe_core.loaders.validate_manifests "$STAGED_FILES"
```

```python
# vibe_core/loaders/validate_manifests.py
def validate_all_manifests(files: List[Path]) -> bool:
    """
    Pre-commit check: All manifest.json files must be valid.

    Returns False (blocks commit) if ANY manifest is invalid.
    """
    for file in files:
        if file.name == "manifest.json":
            if not validate_manifest_schema(file):
                print(f"❌ Invalid manifest: {file}")
                return False
    return True
```

---

## 6. OPEN QUESTIONS

1. **Naming:** Keep `steward.json` + `cartridge.yaml` for agents (backward compat) or rename to `manifest.json` + `config.yaml`?

2. **Entry Point Naming:** `plugin_main.py` vs `cartridge_main.py` vs just `main.py`?

3. **Sub-items:** Should sub-items (tools/, validators/) ALSO have manifest.json? (Recursive fractal?)

4. **Phoenix Integration:** Does Phoenix need a `plugins` section, or do plugins self-register?

5. **Hot Reload:** Should UnifiedLoader support hot-reload on file change?

---

## 7. SUCCESS CRITERIA

1. **ONE manifest.json schema** - All items use same structure
2. **ONE UnifiedLoader** - All loaders inherit from it
3. **Schema validation in pre-commit** - Invalid = rejected
4. **Config hierarchy works** - Env → Phoenix → Local → Defaults
5. **Backward compatible** - Agents still work during migration
6. **Tests pass** - 374+ tests still green

---

## 8. ANSWERS TO OPEN QUESTIONS

Based on the fraktal principle and VEDA-4 pattern:

### 8.1 Naming Convention

**Decision:** Use **universal names** for new items, **alias** for backward compat.

```
NEW (preferred):           ALIAS (backward compat):
manifest.json       ←→     steward.json (agents only)
config.yaml         ←→     cartridge.yaml (agents only)
{type}_main.py      ←→     cartridge_main.py (agents only)
```

**Why:** One name everywhere = less cognitive load. Aliases only for existing agents.

### 8.2 Entry Point Naming

**Decision:** `{type}_main.py` pattern.

```
plugins/     → plugin_main.py
agents/      → agent_main.py (or cartridge_main.py alias)
sections/    → section_main.py
workflows/   → workflow_main.py
```

**Why:** Self-documenting. When you see `plugin_main.py` you know what it is.

### 8.3 Sub-items Manifest (Recursive Fractal)

**Decision:** **Optional** manifest.json for sub-items.

```
steward_protocol/
    manifest.json              ← Required (parent)
    plugin_main.py
    validators/                ← Sub-items
        __init__.py            ← Simple: Just export classes
        capability_check.py    ← No manifest needed
        trust_threshold.py
```

OR for complex sub-items:

```
steward_protocol/
    manifest.json
    plugin_main.py
    validators/
        capability_check/      ← Complex: Has own manifest
            manifest.json
            validator_main.py
            config.yaml
```

**Why:** Don't force complexity. Simple sub-items = files. Complex sub-items = folders with manifest.

### 8.4 Phoenix Integration

**Decision:** Plugins **self-register** via manifest, Phoenix provides **global config**.

```yaml
# Phoenix config/plugins.yaml (global overrides)
plugins:
  steward_protocol:
    enabled: true
    strict_mode: false

# Plugin's own config.yaml (local defaults)
# Merged with Phoenix at load time
```

**Why:** Plugins are self-contained. Phoenix is the knob to tune them.

### 8.5 Hot Reload

**Decision:** **Phase 2** feature. Not in initial implementation.

**Why:** Get the basic loader working first. Hot reload adds complexity (state management, cleanup).

---

## 9. IMPLEMENTATION ORDER

```
Phase 1: Foundation (FIRST)
├── vibe_core/loaders/base_loader.py      ← UnifiedLoader ABC
├── vibe_core/loaders/schema.py           ← JSON Schema validation
├── vibe_core/loaders/manifest_schema.json ← The schema itself
└── tests/test_unified_loader.py          ← Tests FIRST

Phase 2: Plugin Migration
├── Convert steward_protocol.py → steward_protocol/
├── Convert vedic_governance.py → vedic_governance/
├── Update PluginLoader to use UnifiedLoader
└── All 374+ tests still green

Phase 3: Agent Alignment
├── AgentLoader inherits UnifiedLoader
├── Add alias support (steward.json → manifest.json)
└── No breaking changes to existing agents

Phase 4: Section Alignment
├── Convert Phoenix sections to folder structure
├── SectionLoader inherits UnifiedLoader
└── Phoenix config still works

Phase 5: Pre-commit Integration
├── python -m vibe_core.loaders.validate_manifests
├── Add to .githooks/pre-commit
└── CI/CD validation
```

---

## 10. SUCCESS CRITERIA (FINAL)

| Criterion | Metric |
|-----------|--------|
| ONE schema | All manifest.json files validate against same schema |
| ONE loader | All loaders inherit UnifiedLoader |
| Backward compat | Existing agents work without changes |
| Tests green | 374+ tests pass |
| Pre-commit works | Invalid manifest = blocked commit |
| Config hierarchy | Env → Phoenix → Local → Defaults |

---

*Created: 2025-12-05*
*Status: PLAN COMPLETE - Ready for Implementation*
