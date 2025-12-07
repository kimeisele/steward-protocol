# DER TOTALE KRIEG - Execution Plan for All 7 Battles

> **Purpose:** Complete execution prompts for every battle in MASTER_PLAN_V4.1_FINAL.md
> **Prerequisite:** OPUS_REFACTOR_PHASE2.md (immediate tech debt) MUST be complete first
> **Assignee:** Sonnet (execution), Opus (review)
> **Last Validated:** 2025-12-07 (against actual codebase)

---

## CRITICAL STATUS UPDATE (2025-12-07)

**The Codebase has evolved beyond MASTER_PLAN_V4.1_FINAL.md!**

Most battles are ALREADY COMPLETE:

| Schlacht | Status | Evidence |
|----------|--------|----------|
| 1: CORTEX | ✅ DONE | `vibe_core/cortex/engines/` exists |
| 2: KNOWLEDGE | ✅ DONE | `knowledge/{concepts,intents,circuits,playbooks}/` structured |
| 3: CARTRIDGES | ✅ DONE | All agents in `vibe_core/cartridges/{system,agent_city}/` |
| 4: PROVIDER | ✅ DONE | `provider/` directory deleted |
| 5: SERVICES | ✅ DONE | `services/` directory deleted |
| 6: LEGACY | ✅ DONE | sandbox, diplomatic_bag, intelligence deleted (2025-12-07) |
| 7: INTEGRATION | 🟡 PARTIAL | Needs final verification pass |

**Remaining Work:**
- Phase 0 (OPUS_REFACTOR_PHASE2.md) - Still pending
- Schlacht 7 verification pass
- Delete stale auto-generated cartridges (DONE 2025-12-07: 9 test cartridges removed)

---

## EXECUTION ORDER

```
PHASE 0: OPUS_REFACTOR_PHASE2.md (Immediate Debt)    ← YOU ARE HERE
    │
    ├─ Task 1: Kill Legacy Routers
    ├─ Task 2: Fix EphemeralStorage Lifecycle
    ├─ Task 3: Async Panel Rendering
    ├─ Task 4: Externalize Templates
    └─ Task 5: Unit Test Coverage
    │
    ▼
PHASE 1: SCHLACHT 1-2 (Foundation) ─────────────────── ✅ ALREADY DONE
    │
    ├─ Schlacht 1: CORTEX FOUNDATION ✅
    └─ Schlacht 2: KNOWLEDGE FRAKTALISIERUNG ✅
    │
    ▼
PHASE 2: SCHLACHT 3 (The Big Move) ─────────────────── ✅ ALREADY DONE
    │
    └─ Schlacht 3: CARTRIDGE CONSOLIDATION ✅
    │
    ▼
PHASE 3: SCHLACHT 4-5 (Cleanup) ────────────────────── ✅ ALREADY DONE
    │
    ├─ Schlacht 4: PROVIDER ELIMINATION ✅
    └─ Schlacht 5: SERVICES CLEANUP ✅
    │
    ▼
PHASE 4: SCHLACHT 6-7 (Polish) ─────────────────────── 🟡 PARTIAL
    │
    ├─ Schlacht 6: LEGACY CLEANUP ✅ (completed 2025-12-07)
    └─ Schlacht 7: FINAL INTEGRATION 🟡 (needs verification)
```

---

## SCHLACHT 1: CORTEX FOUNDATION

**Priority:** HIGH
**Risk:** LOW
**Effort:** 4-6 hours
**Assignee:** Sonnet

### Objective

Create `vibe_core/cortex/` as the cognitive engine center - all routing, execution, and semantic logic lives here.

### Current State

```
SCATTERED:
├── provider/semantic_router.py        # Semantic matching
├── provider/reflex_engine.py          # Fast deterministic
├── vibe_core/circuit_executor.py      # State machine
├── vibe_core/playbook/executor.py     # DAG executor
└── vibe_core/playbook/unified_router.py # Routing
```

### Target State

```
vibe_core/cortex/
├── __init__.py
├── loader.py                          # CortexLoader (VEDA-4)
├── engines/
│   ├── __init__.py
│   ├── semantic_engine.py             # ← from provider/
│   ├── reflex_engine.py               # ← from provider/
│   ├── circuit_engine.py              # ← from circuit_executor.py
│   └── playbook_engine.py             # ← from playbook/executor.py
├── router/
│   ├── __init__.py
│   └── unified_router.py              # ← from playbook/unified_router.py
└── protocols/
    ├── __init__.py
    └── cognitive.py                   # CognitiveProtocol ABC
```

### Step-by-Step Instructions

#### Step 1.1: Create Directory Structure
```bash
mkdir -p vibe_core/cortex/{engines,router,protocols}
touch vibe_core/cortex/__init__.py
touch vibe_core/cortex/engines/__init__.py
touch vibe_core/cortex/router/__init__.py
touch vibe_core/cortex/protocols/__init__.py
```

#### Step 1.2: Create CognitiveProtocol ABC
```python
# vibe_core/cortex/protocols/cognitive.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class CognitiveEngine(ABC):
    """Base protocol for all cognitive engines."""

    @property
    @abstractmethod
    def engine_id(self) -> str:
        """Unique identifier for this engine."""
        pass

    @abstractmethod
    async def process(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return result."""
        pass

    @abstractmethod
    def can_handle(self, input: Dict[str, Any]) -> bool:
        """Check if this engine can handle the input."""
        pass
```

#### Step 1.3: Copy Engines (DO NOT DELETE ORIGINALS YET)
```bash
# COPY, not move! Keep originals until tests pass
cp provider/semantic_router.py vibe_core/cortex/engines/semantic_engine.py
cp provider/reflex_engine.py vibe_core/cortex/engines/reflex_engine.py
cp vibe_core/circuit_executor.py vibe_core/cortex/engines/circuit_engine.py
cp vibe_core/playbook/executor.py vibe_core/cortex/engines/playbook_engine.py
```

#### Step 1.4: Update Imports in Copied Files
Each engine file needs import path updates:
```python
# OLD
from provider.semantic_router import ...

# NEW
from vibe_core.cortex.engines.semantic_engine import ...
```

#### Step 1.5: Create Cortex Loader
```python
# vibe_core/cortex/loader.py
from vibe_core.loaders.unified_loader import UnifiedLoader
from pathlib import Path
from typing import Dict, Any

class CortexLoader(UnifiedLoader):
    """Load cognitive engines using VEDA-4 pattern."""

    @property
    def loader_id(self) -> str:
        return "cortex"

    @property
    def base_path(self) -> Path:
        return Path("vibe_core/cortex/engines")

    def discover(self) -> Dict[str, Any]:
        """Discover all available engines."""
        engines = {}
        for engine_file in self.base_path.glob("*_engine.py"):
            if engine_file.name.startswith("_"):
                continue
            engine_id = engine_file.stem.replace("_engine", "")
            engines[engine_id] = {
                "file": str(engine_file),
                "engine_id": engine_id,
            }
        return engines
```

#### Step 1.6: Add Aliases for Backwards Compatibility
```python
# provider/__init__.py (update, don't delete)
import warnings

def _deprecated_import(old_path, new_import):
    warnings.warn(
        f"{old_path} is deprecated, use {new_import}",
        DeprecationWarning,
        stacklevel=3
    )

# Alias for backwards compatibility
try:
    from vibe_core.cortex.engines.semantic_engine import SemanticRouter
    _deprecated_import("provider.semantic_router", "vibe_core.cortex.engines.semantic_engine")
except ImportError:
    from .semantic_router import SemanticRouter
```

### Validation Commands

```bash
# 1. Structure exists
ls -la vibe_core/cortex/engines/

# 2. Imports work
python -c "from vibe_core.cortex.engines import semantic_engine"
python -c "from vibe_core.cortex.engines import circuit_engine"
python -c "from vibe_core.cortex.loader import CortexLoader"

# 3. Tests still pass
python -m pytest tests/integration/test_veda4_circuits.py -v
python -m pytest tests/ -k "semantic or router" -v

# 4. No new failures
python -m pytest tests/ --timeout=60 -q
```

### Acceptance Criteria

- [ ] `vibe_core/cortex/engines/` contains 4 engine files
- [ ] `CortexLoader` discovers all engines
- [ ] `CognitiveEngine` protocol defined
- [ ] All existing tests pass (no regressions)
- [ ] Deprecation warnings for old import paths

### Rollback

If anything breaks:
```bash
rm -rf vibe_core/cortex/
git checkout -- provider/
```

---

## SCHLACHT 2: KNOWLEDGE FRAKTALISIERUNG

**Priority:** HIGH
**Risk:** MEDIUM
**Effort:** 4-6 hours
**Assignee:** Sonnet

### Objective

Structure `knowledge/` as the CONFIG layer with proper manifests and folder organization.

### Current State

```
knowledge/
├── concept_map.yaml           # Loose
├── intent_rules.yaml          # Loose
├── circuits/                  # Already good!
│   ├── manifest.json
│   └── *.yaml
└── playbooks/                 # Already good!
    ├── manifest.json
    └── *.yaml
```

### Target State

```
knowledge/
├── manifest.json              # Master index
├── concepts/
│   ├── manifest.json
│   ├── general.yaml           # ← from concept_map.yaml
│   └── domains/
│       ├── coding.yaml
│       └── philosophy.yaml
├── intents/
│   ├── manifest.json
│   └── routing_rules.yaml     # ← from intent_rules.yaml
├── circuits/                  # Keep as-is
│   ├── manifest.json
│   └── *.yaml
├── playbooks/                 # Keep as-is
│   ├── manifest.json
│   └── *.yaml
└── templates/                 # NEW - from Task 4 in Phase 0
    ├── manifest.json
    └── *.j2
```

### Step-by-Step Instructions

#### Step 2.1: Create Directory Structure
```bash
mkdir -p knowledge/{concepts/domains,intents,templates}
```

#### Step 2.2: Create Master Manifest
```json
// knowledge/manifest.json
{
  "name": "Knowledge Base",
  "version": "1.0.0",
  "description": "Configuration layer for cognitive systems",
  "categories": {
    "concepts": {
      "path": "concepts/",
      "description": "Semantic concept maps"
    },
    "intents": {
      "path": "intents/",
      "description": "Routing and intent classification rules"
    },
    "circuits": {
      "path": "circuits/",
      "description": "State machine definitions"
    },
    "playbooks": {
      "path": "playbooks/",
      "description": "DAG execution definitions"
    },
    "templates": {
      "path": "templates/",
      "description": "Jinja2 output templates"
    }
  }
}
```

#### Step 2.3: Move Concept Files
```bash
mv knowledge/concept_map.yaml knowledge/concepts/general.yaml
```

Create concepts manifest:
```json
// knowledge/concepts/manifest.json
{
  "name": "Concept Maps",
  "version": "1.0.0",
  "files": [
    {"file": "general.yaml", "description": "General concept mappings"},
    {"file": "domains/coding.yaml", "description": "Code-related concepts"},
    {"file": "domains/philosophy.yaml", "description": "Philosophical concepts"}
  ]
}
```

#### Step 2.4: Move Intent Files
```bash
mv knowledge/intent_rules.yaml knowledge/intents/routing_rules.yaml
```

Create intents manifest:
```json
// knowledge/intents/manifest.json
{
  "name": "Intent Rules",
  "version": "1.0.0",
  "files": [
    {"file": "routing_rules.yaml", "description": "Main routing rules"}
  ]
}
```

#### Step 2.5: Update All Loaders

Find and update all references:
```bash
grep -r "concept_map.yaml\|intent_rules.yaml" vibe_core/
```

Update paths in:
- `vibe_core/cortex/engines/semantic_engine.py`
- `vibe_core/playbook/unified_router.py`
- Any other files that load these configs

#### Step 2.6: Create KnowledgeLoader
```python
# vibe_core/loaders/knowledge_loader.py
from vibe_core.loaders.unified_loader import UnifiedLoader
from pathlib import Path
from typing import Dict, Any
import json

class KnowledgeLoader(UnifiedLoader):
    """Load knowledge base using VEDA-4 pattern."""

    @property
    def loader_id(self) -> str:
        return "knowledge"

    @property
    def base_path(self) -> Path:
        return Path("knowledge")

    def discover(self) -> Dict[str, Any]:
        """Discover all knowledge categories."""
        manifest_path = self.base_path / "manifest.json"
        if manifest_path.exists():
            return json.loads(manifest_path.read_text())
        return {}

    def load_category(self, category: str) -> Dict[str, Any]:
        """Load a specific category (concepts, intents, etc.)."""
        category_path = self.base_path / category / "manifest.json"
        if category_path.exists():
            return json.loads(category_path.read_text())
        return {}
```

### Validation Commands

```bash
# 1. Structure exists
ls -la knowledge/
ls -la knowledge/concepts/
ls -la knowledge/intents/

# 2. Manifests valid
python -c "import json; json.load(open('knowledge/manifest.json'))"
python -c "import json; json.load(open('knowledge/concepts/manifest.json'))"
python -c "import json; json.load(open('knowledge/intents/manifest.json'))"

# 3. Loaders work
python -c "from vibe_core.loaders.knowledge_loader import KnowledgeLoader; print(KnowledgeLoader().discover())"

# 4. No broken imports
grep -r "concept_map.yaml" vibe_core/ && echo "FAIL: Old path still referenced" || echo "OK"
grep -r "intent_rules.yaml" vibe_core/ && echo "FAIL: Old path still referenced" || echo "OK"

# 5. All tests pass
python -m pytest tests/ --timeout=60 -q
```

### Acceptance Criteria

- [ ] `knowledge/manifest.json` exists with all categories
- [ ] `knowledge/concepts/` contains general.yaml + manifest.json
- [ ] `knowledge/intents/` contains routing_rules.yaml + manifest.json
- [ ] No code references old paths (concept_map.yaml, intent_rules.yaml)
- [ ] KnowledgeLoader discovers all categories
- [ ] All tests pass

---

## SCHLACHT 3: CARTRIDGE CONSOLIDATION

**Priority:** CRITICAL
**Risk:** HIGH (Many import changes!)
**Effort:** 8-12 hours
**Assignee:** Sonnet + Gemini (bulk work)

### Objective

Move ALL agents under `vibe_core/cartridges/` - one location for all agent code.

### Current State

```
SCATTERED:
├── steward/system_agents/     # 15 system agents
│   ├── envoy/
│   ├── herald/
│   ├── watchman/
│   └── ... (12 more)
├── agent_city/registry/       # 14 city agents
│   ├── ambassador/
│   ├── analyst/
│   └── ... (12 more)
└── vibe_core/cartridges/      # Already exists (partial)
    ├── system/
    └── agent_city/
```

### Target State

```
vibe_core/cartridges/
├── __init__.py
├── loader.py                  # CartridgeLoader (VEDA-4)
├── base.py                    # BaseCartridge class
├── system/                    # ← FROM steward/system_agents/
│   ├── __init__.py
│   ├── envoy/
│   │   ├── __init__.py
│   │   ├── manifest.json
│   │   ├── cartridge_main.py
│   │   └── prompts/
│   ├── herald/
│   ├── watchman/
│   ├── auditor/
│   ├── scribe/
│   └── ... (10 more)
└── agent_city/                # ← FROM agent_city/registry/
    ├── __init__.py
    ├── ambassador/
    ├── analyst/
    └── ... (12 more)
```

### Step-by-Step Instructions

#### Step 3.1: Audit Current State
```bash
# Count agents to move
ls -d steward/system_agents/*/ 2>/dev/null | wc -l
ls -d agent_city/registry/*/ 2>/dev/null | wc -l

# Find all import references
grep -r "from steward.system_agents" vibe_core/ tests/ --include="*.py" > /tmp/imports_steward.txt
grep -r "from agent_city.registry" vibe_core/ tests/ --include="*.py" > /tmp/imports_city.txt

# Count them
wc -l /tmp/imports_steward.txt /tmp/imports_city.txt
```

#### Step 3.2: Create Import Refactor Script
```python
# scripts/refactor_cartridge_imports.py
"""
Automated import refactor for cartridge consolidation.
RUN WITH --dry-run first!
"""
import re
import sys
from pathlib import Path

DRY_RUN = "--dry-run" in sys.argv

REPLACEMENTS = [
    # System agents
    (r"from steward\.system_agents\.(\w+)", r"from vibe_core.cartridges.system.\1"),
    (r"from steward\.system_agents import", r"from vibe_core.cartridges.system import"),
    (r"import steward\.system_agents\.(\w+)", r"import vibe_core.cartridges.system.\1"),

    # City agents
    (r"from agent_city\.registry\.(\w+)", r"from vibe_core.cartridges.agent_city.\1"),
    (r"from agent_city\.registry import", r"from vibe_core.cartridges.agent_city import"),
    (r"import agent_city\.registry\.(\w+)", r"import vibe_core.cartridges.agent_city.\1"),
]

def refactor_file(path: Path) -> int:
    content = path.read_text()
    original = content

    for old, new in REPLACEMENTS:
        content = re.sub(old, new, content)

    if content != original:
        if DRY_RUN:
            print(f"WOULD MODIFY: {path}")
        else:
            path.write_text(content)
            print(f"MODIFIED: {path}")
        return 1
    return 0

def main():
    total = 0
    for pattern in ["vibe_core/**/*.py", "tests/**/*.py", "scripts/**/*.py"]:
        for path in Path(".").glob(pattern):
            total += refactor_file(path)

    print(f"\n{'Would modify' if DRY_RUN else 'Modified'} {total} files")
    if DRY_RUN:
        print("Run without --dry-run to apply changes")

if __name__ == "__main__":
    main()
```

#### Step 3.3: Copy Agents (NOT move yet!)
```bash
# Create target directories
mkdir -p vibe_core/cartridges/system
mkdir -p vibe_core/cartridges/agent_city

# Copy system agents
cp -r steward/system_agents/* vibe_core/cartridges/system/

# Copy city agents
cp -r agent_city/registry/* vibe_core/cartridges/agent_city/

# Remove __pycache__ from copied dirs
find vibe_core/cartridges -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
```

#### Step 3.4: Update AgentLoader Scan Paths
```python
# vibe_core/steward/loader.py - UPDATE scan paths

# OLD
AGENT_PATHS = [
    Path("steward/system_agents"),
    Path("agent_city/registry"),
]

# NEW
AGENT_PATHS = [
    Path("vibe_core/cartridges/system"),
    Path("vibe_core/cartridges/agent_city"),
    # Keep old paths temporarily for migration
    Path("steward/system_agents"),
    Path("agent_city/registry"),
]
```

#### Step 3.5: Run Import Refactor
```bash
# Dry run first!
python scripts/refactor_cartridge_imports.py --dry-run

# If looks good, apply
python scripts/refactor_cartridge_imports.py

# Verify
grep -r "from steward.system_agents" vibe_core/ tests/ --include="*.py"
# Should return nothing (or only deprecation aliases)
```

#### Step 3.6: Run Full Test Suite
```bash
python -m pytest tests/ --timeout=60 -v

# If failures, fix one by one
# DO NOT proceed until all tests pass!
```

#### Step 3.7: Update steward.json Discovery
```python
# vibe_core/plugins/steward_protocol/plugin_main.py

# Find the steward.json discovery code and update paths
# OLD: steward/system_agents/{agent}/steward.json
# NEW: vibe_core/cartridges/system/{agent}/steward.json
```

#### Step 3.8: Remove Old Directories (ONLY after tests pass!)
```bash
# ONLY DO THIS AFTER ALL TESTS PASS!
rm -rf steward/system_agents/
rm -rf agent_city/registry/

# Keep steward/ for docs only
# Keep agent_city/ empty or delete
```

### Validation Commands

```bash
# 1. New structure exists
ls vibe_core/cartridges/system/ | wc -l  # Should be 15+
ls vibe_core/cartridges/agent_city/ | wc -l  # Should be 14+

# 2. No old import references
grep -r "from steward.system_agents" vibe_core/ tests/ --include="*.py" | grep -v "deprecated" && echo "FAIL" || echo "OK"
grep -r "from agent_city.registry" vibe_core/ tests/ --include="*.py" | grep -v "deprecated" && echo "FAIL" || echo "OK"

# 3. AgentLoader finds all agents
python -c "
from vibe_core.steward.loader import AgentLoader
agents = AgentLoader().discover()
print(f'Found {len(agents)} agents')
for a in agents:
    print(f'  - {a}')
"

# 4. All tests pass
python -m pytest tests/ --timeout=60 -q
```

### Acceptance Criteria

- [ ] All 29 agents exist in `vibe_core/cartridges/`
- [ ] AgentLoader discovers all agents from new paths
- [ ] No imports reference old paths (steward/system_agents, agent_city/registry)
- [ ] All tests pass
- [ ] Old directories deleted (steward/system_agents, agent_city/registry)

---

## SCHLACHT 4: PROVIDER ELIMINATION

**Priority:** MEDIUM
**Risk:** MEDIUM
**Effort:** 4-6 hours
**Assignee:** Sonnet

### Objective

Eliminate `provider/` directory - its concepts live on in Cortex and EnvoyCartridge.

### Current State

After Schlacht 1 (Cortex Foundation), provider/ still exists with:
- Original files (deprecated aliases)
- Universal provider logic

### Target State

```
provider/                      # DELETED!

Logic moved to:
├── vibe_core/cortex/          # Engines (done in Schlacht 1)
└── vibe_core/cartridges/system/envoy/provider.py  # Universal provider
```

### Step-by-Step Instructions

#### Step 4.1: Move Universal Provider Logic
```bash
# Check what's left in provider/
ls -la provider/

# Copy universal provider to envoy
cp provider/universal_provider.py vibe_core/cartridges/system/envoy/provider.py
```

#### Step 4.2: Update Gateway API
```python
# gateway/api.py

# OLD
from provider.universal_provider import UniversalProvider

# NEW
# Option A: Direct kernel routing
result = kernel.route_to_agent("envoy", request)

# Option B: Use envoy provider
from vibe_core.cartridges.system.envoy.provider import EnvoyProvider
```

#### Step 4.3: Remove Deprecated Aliases
```python
# provider/__init__.py - After all imports migrated, this becomes:
raise ImportError(
    "The 'provider' package is deprecated. "
    "Use 'vibe_core.cortex.engines' for routing logic, "
    "or 'vibe_core.cartridges.system.envoy' for provider logic."
)
```

#### Step 4.4: Delete Provider Directory
```bash
# ONLY after all tests pass!
rm -rf provider/
```

### Validation Commands

```bash
# 1. No imports from provider/
grep -r "from provider\b" vibe_core/ gateway/ tests/ --include="*.py" && echo "FAIL" || echo "OK"
grep -r "import provider\b" vibe_core/ gateway/ tests/ --include="*.py" && echo "FAIL" || echo "OK"

# 2. Gateway still works
python gateway/api.py &
sleep 2
curl localhost:8000/health
kill %1

# 3. All tests pass
python -m pytest tests/ --timeout=60 -q
```

### Acceptance Criteria

- [ ] `provider/` directory deleted
- [ ] No code imports from `provider`
- [ ] Gateway API works with new imports
- [ ] All tests pass

---

## SCHLACHT 5: SERVICES CLEANUP

**Priority:** LOW
**Risk:** LOW
**Effort:** 2-3 hours
**Assignee:** Sonnet

### Objective

Eliminate `services/` directory - move LLM engine to runtime.

### Current State

```
services/
└── llm_engine.py
```

### Target State

```
vibe_core/runtime/
├── __init__.py
├── io_service.py              # Already exists
├── oracle.py                  # Already exists
└── llm_engine.py              # ← FROM services/
```

### Step-by-Step Instructions

#### Step 5.1: Move LLM Engine
```bash
mkdir -p vibe_core/runtime
cp services/llm_engine.py vibe_core/runtime/llm_engine.py
```

#### Step 5.2: Update Imports
```bash
# Find all references
grep -r "from services\." vibe_core/ tests/ --include="*.py"

# Update them
sed -i '' 's/from services\.llm_engine/from vibe_core.runtime.llm_engine/g' **/*.py
```

#### Step 5.3: Delete Services Directory
```bash
rm -rf services/
```

### Validation Commands

```bash
# 1. No imports from services/
grep -r "from services\b" vibe_core/ tests/ --include="*.py" && echo "FAIL" || echo "OK"

# 2. New import works
python -c "from vibe_core.runtime.llm_engine import LLMEngine"

# 3. All tests pass
python -m pytest tests/ --timeout=60 -q
```

### Acceptance Criteria

- [ ] `services/` directory deleted
- [ ] `vibe_core/runtime/llm_engine.py` exists
- [ ] No code imports from `services`
- [ ] All tests pass

---

## SCHLACHT 6: LEGACY CLEANUP

**Priority:** LOW
**Risk:** LOW
**Effort:** 2-3 hours
**Assignee:** Sonnet

### Objective

Delete all legacy directories that are no longer needed.

### Directories to Delete

```bash
# Delete after confirmation
rm -rf prompts/           # Prompts in cartridges now
rm -rf content/           # Unused
rm -rf archive/           # Old backups
rm -rf MagicMock/         # Test artifact
rm -rf sandbox/           # Development sandbox
rm -rf migration/         # Completed migrations
rm -rf starter-packs/     # Move to knowledge/ or delete

# Move, don't delete
mv workspace/ data/workspace/
mv workspaces/ data/workspaces/
mv diplomatic_bag/ data/diplomatic_bag/   # If exists
mv intelligence/ data/intelligence/       # If exists
```

### Directories to Keep

```
steward/                  # Keep docs only (move .py files elsewhere)
├── STEWARD_*.md
└── templates/
```

### Step-by-Step Instructions

#### Step 6.1: Audit What Exists
```bash
ls -la | grep -E "^d" | awk '{print $NF}'
```

#### Step 6.2: Check for Dependencies
```bash
# For each directory, check if anything imports from it
for dir in prompts content archive MagicMock sandbox migration; do
    echo "=== $dir ==="
    grep -r "from $dir\b\|import $dir\b" vibe_core/ tests/ --include="*.py" || echo "No imports found"
done
```

#### Step 6.3: Delete Safely
```bash
# Only delete directories with no imports
# Add to .gitignore first as safety
echo "# Legacy directories scheduled for deletion" >> .gitignore
echo "prompts/" >> .gitignore
echo "content/" >> .gitignore
# ... etc

# Then delete
rm -rf prompts/ content/ archive/ MagicMock/ sandbox/ migration/
```

#### Step 6.4: Move Workspace Data
```bash
mkdir -p data/workspace data/workspaces
mv workspace/* data/workspace/ 2>/dev/null
mv workspaces/* data/workspaces/ 2>/dev/null
rmdir workspace workspaces 2>/dev/null
```

### Validation Commands

```bash
# 1. Legacy directories gone
for dir in prompts content archive MagicMock sandbox migration; do
    [ -d "$dir" ] && echo "FAIL: $dir still exists" || echo "OK: $dir deleted"
done

# 2. Workspace moved
[ -d "data/workspace" ] && echo "OK" || echo "FAIL"

# 3. All tests pass
python -m pytest tests/ --timeout=60 -q
```

### Acceptance Criteria

- [ ] Legacy directories deleted (prompts, content, archive, MagicMock, sandbox, migration)
- [ ] Workspace directories moved to data/
- [ ] No broken imports
- [ ] All tests pass

---

## SCHLACHT 7: FINAL INTEGRATION

**Priority:** HIGH
**Risk:** LOW
**Effort:** 4-6 hours
**Assignee:** Opus (review), Sonnet (execution)

### Objective

Verify the complete system works and document the new structure.

### Verification Checklist

#### 7.1: Directory Structure
```bash
# Only these top-level directories should exist:
ls -d */ | sort

# Expected:
# data/
# docs/
# gateway/
# knowledge/
# scripts/
# steward/        (docs only)
# tests/
# vibe_core/
```

#### 7.2: Import Verification
```bash
# No legacy imports
for old in "from provider" "from services" "from steward.system_agents" "from agent_city.registry"; do
    echo "=== Checking: $old ==="
    grep -r "$old" vibe_core/ tests/ gateway/ --include="*.py" | grep -v "deprecated" || echo "OK: No legacy imports"
done
```

#### 7.3: Boot Test
```bash
python -c "
from vibe_core.kernel_impl import RealVibeKernel

kernel = RealVibeKernel(ledger_path=':memory:')
kernel.boot()

print(f'Kernel: {kernel.status}')
print(f'Plugins: {len(kernel._plugins)}')
print(f'Agents: {len(kernel._agent_registry)}')

# List agents
for agent_id in kernel._agent_registry.list_agents():
    print(f'  - {agent_id}')
"
```

#### 7.4: Full Test Suite
```bash
python -m pytest tests/ -v --timeout=120

# Target: 0 FAILED, 0 BLOCKED
# Acceptable: Some WARNED (tech debt)
```

#### 7.5: Gateway Test
```bash
python gateway/api.py &
sleep 3
curl localhost:8000/health
curl -X POST localhost:8000/api/chat -d '{"message": "hello"}'
kill %1
```

### Documentation Update

#### 7.6: Update README.md
The new structure should be documented:

```markdown
## Project Structure

```
steward-protocol/
├── vibe_core/              # ══════ CODE ══════
│   ├── kernel_impl.py      # The Kernel (eternal)
│   ├── loaders/            # VEDA-4 Loader Framework
│   ├── plugins/            # Kernel Plugins
│   ├── cortex/             # Cognitive Engines
│   ├── cartridges/         # Agent Plugins
│   │   ├── system/         # Core agents
│   │   └── agent_city/     # Community agents
│   └── runtime/            # Runtime Services
│
├── knowledge/              # ══════ CONFIG ══════
│   ├── concepts/           # Semantic maps
│   ├── intents/            # Routing rules
│   ├── circuits/           # State machines
│   ├── playbooks/          # DAG definitions
│   └── templates/          # Jinja2 templates
│
├── data/                   # ══════ RUNTIME ══════ (gitignored)
│   ├── ledger/             # Immutable records
│   ├── cache/              # Temporary data
│   └── models/             # ML models
│
├── gateway/                # HTTP API
├── tests/                  # Test suite
├── docs/                   # Documentation
└── scripts/                # Utilities
```
```

#### 7.7: Update ARCHITECTURE.md
Reference the new structure and fraktal pattern.

### Final Metrics

```bash
# Root directories (target: ≤6)
ls -d */ | wc -l

# vibe_core structure
find vibe_core -type d | wc -l

# Total agents
ls vibe_core/cartridges/system vibe_core/cartridges/agent_city 2>/dev/null | wc -l

# Test results
python -m pytest tests/ --timeout=60 -q 2>&1 | tail -5
```

### Acceptance Criteria

- [ ] Only 6-8 top-level directories exist
- [ ] Kernel boots in < 2 seconds
- [ ] All agents discovered from new paths
- [ ] Full test suite passes (0 FAILED)
- [ ] Gateway API functional
- [ ] README.md and ARCHITECTURE.md updated
- [ ] `.gitignore` updated for data/

---

## SUCCESS CRITERIA - Der Totale Sieg

After all 7 Schlachten are complete:

```
✅ CODE lives in vibe_core/
✅ CONFIG lives in knowledge/
✅ RUNTIME lives in data/ (gitignored)
✅ Legacy directories eliminated
✅ All 29 agents in vibe_core/cartridges/
✅ Cortex engines in vibe_core/cortex/
✅ No legacy import paths
✅ All tests pass
✅ Kernel boots < 2 seconds
✅ Documentation updated
```

**The Fraktal Vision is achieved.**

---

## APPENDIX: Emergency Rollback

If any Schlacht goes catastrophically wrong:

```bash
# 1. Stop everything
pkill -f python

# 2. Reset to last known good state
git stash
git checkout main
git pull

# 3. Restore from backup branch
git checkout -b recovery
git cherry-pick <last-good-commit>

# 4. Run tests to verify
python -m pytest tests/ --timeout=60 -q
```

---

*Generated by Opus (Architect)*
*For execution by Sonnet*
*Review by The Watcher*
