# OPUS-029: OPUS Plugin Architecture

**Status:** PLANNING
**Author:** Claude (Senior Architect)
**Date:** 2025-12-12
**Scope:** Full OPUS Plugin System - From Renderer to Agent Operating System

---

## Executive Summary

Transform the existing OPUS Renderer from a **passive display system** into an **active Agent Operating System plugin**. This is NOT a new build - it's a **surgical extraction and enhancement** of existing code.

**Core Insight:** We are building **software INTO the existing AOS**, not on top of it.

---

## Current State Analysis

### What EXISTS (Assets to Reuse)

| Component | Location | Status | Action |
|-----------|----------|--------|--------|
| OPUS Renderer | `vibe_core/plugins/interface/renderers/opus/` | UI-coupled | Keep as Frontend |
| VerificationPanel | `opus/panels/verification.py` (686 LOC) | GOLD | Extract Logic |
| Event Bus | `vibe_core/event_bus.py` | Active | Integrate |
| Auditor Cartridge | `vibe_core/cartridges/system/auditor/` | Active | Orchestrate (DON'T duplicate!) |
| GitState | `vibe_core/state/git_state.py` | Active | Use for Drift |
| Prakriti | `vibe_core/state/prakriti.py` | Active | Bridge |
| Circuit Engine | `vibe_core/cortex/engines/circuit_engine.py` | Active | Use existing! |
| Ledger | `vibe_core/ledger.py` | Active | Integrate |
| Plugin Template | `vibe_core/plugins/plugin_template/` | Reference | Copy pattern |

### What DOESN'T Exist (Must Build)

1. **Standalone OPUS Plugin** - Currently lives in Interface plugin
2. **CLI Commands** - No `steward opus verify`
3. **Opus Assistant Agent** - Orchestrator for OPUS operations
4. **Drift Detection** - Code vs Docs comparison
5. **Event-Driven Triggers** - Auto-workflows on changes

---

## Architecture Decision

```
                            BEFORE                                 AFTER

┌─────────────────────────────────┐        ┌──────────────────────────────────────┐
│     Interface Plugin            │        │       Interface Plugin                │
│  ┌───────────────────────────┐  │        │  ┌───────────────────────────────┐    │
│  │   OPUS Renderer           │  │        │  │   OPUS Renderer (UI ONLY)     │    │
│  │   - render()              │  │        │  │   - render()                  │    │
│  │   - verification logic    │  │   →    │  │   - imports from opus plugin  │    │
│  │   - panels/*              │  │        │  └───────────────────────────────┘    │
│  └───────────────────────────┘  │        └──────────────────────────────────────┘
└─────────────────────────────────┘                            │
                                                               │ imports
                                                               ▼
                                           ┌──────────────────────────────────────┐
                                           │      opus_assistant Plugin           │
                                           │  ┌───────────────────────────────┐    │
                                           │  │  core/                        │    │
                                           │  │   - verification_logic.py     │    │
                                           │  │   - drift_detector.py         │    │
                                           │  │   - state_bridge.py           │    │
                                           │  ├───────────────────────────────┤    │
                                           │  │  agents/                      │    │
                                           │  │   - opus_assistant.py         │    │
                                           │  │   - city_spawner.py           │    │
                                           │  ├───────────────────────────────┤    │
                                           │  │  cli/                         │    │
                                           │  │   - commands.py               │    │
                                           │  ├───────────────────────────────┤    │
                                           │  │  events/                      │    │
                                           │  │   - handlers.py               │    │
                                           │  └───────────────────────────────┘    │
                                           └──────────────────────────────────────┘
```

---

## Phase 0: The Split (Foundation)

**Goal:** Extract verification LOGIC from UI without breaking existing functionality.

### 0.1 Create Pure Logic Module

**File:** `vibe_core/plugins/opus_assistant/core/verification_logic.py`

```python
"""
Pure verification logic - NO rich, NO UI dependencies.
Extracted from interface/renderers/opus/panels/verification.py
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
import re

@dataclass
class HarnessResult:
    """Result of verifying a single @HARNESS section."""
    doc_name: str
    has_harness: bool
    score: int
    checks: Dict[str, Dict[str, Any]]

@dataclass
class VerificationReport:
    """Complete verification report."""
    total_score: int
    docs_with_harness: int
    docs_without_harness: int
    docs: List[HarnessResult]
    error: Optional[str] = None

class VerificationEngine:
    """
    Pure verification engine - no UI dependencies.

    Usage:
        engine = VerificationEngine(workspace_root=Path("."))
        report = engine.run_verification()
    """

    def __init__(self, workspace_root: Path, config: Optional[Dict] = None):
        self._root = workspace_root
        self._config = config or self._load_default_config()

    def run_verification(self) -> VerificationReport:
        """Run full verification suite."""
        # ... extracted logic from VerificationPanel._run_verification()

    def verify_doc(self, md_file: Path) -> HarnessResult:
        """Verify a single OPUS document."""
        # ... extracted logic from VerificationPanel._verify_doc()

    def extract_harness(self, content: str) -> Optional[Dict]:
        """Extract @HARNESS YAML from markdown."""
        # ... extracted logic from VerificationPanel._extract_harness()
```

### 0.2 Update Existing Renderer to Use New Logic

**File:** `vibe_core/plugins/interface/renderers/opus/panels/verification.py`

```python
# OLD:
class VerificationPanel(BasePanel):
    def _run_verification(self, config):
        # 600+ lines of logic here

# NEW:
from vibe_core.plugins.opus_assistant.core.verification_logic import VerificationEngine

class VerificationPanel(BasePanel):
    def _run_verification(self, config):
        engine = VerificationEngine(self._root, config)
        return engine.run_verification()  # Returns same dict structure
```

### 0.3 Tests

```bash
# Existing panel tests must still pass
pytest tests/unit/opus/test_verification_panel.py

# New logic tests
pytest vibe_core/plugins/opus_assistant/tests/test_verification_logic.py
```

**SUCCESS CRITERIA:**
- [ ] OPUS.md still renders correctly
- [ ] No `rich` imports in `verification_logic.py`
- [ ] All existing tests pass
- [ ] New unit tests for extracted logic

---

## Phase 1: Plugin Kernel

**Goal:** Create standalone `opus_assistant` plugin.

### 1.1 Plugin Structure

```
vibe_core/plugins/opus_assistant/
├── manifest.json
├── plugin_main.py
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── verification_logic.py    # From Phase 0
│   ├── drift_detector.py        # NEW: Git diff vs docs
│   └── state_bridge.py          # NEW: Prakriti integration
├── agents/
│   ├── __init__.py
│   └── opus_assistant.py        # NEW: Main orchestrator agent
├── cli/
│   ├── __init__.py
│   └── commands.py              # NEW: steward opus ...
├── events/
│   ├── __init__.py
│   └── handlers.py              # NEW: Event-driven triggers
├── circuits/
│   ├── __init__.py
│   └── verify_workflow.yaml     # NEW: Verification circuit
└── tests/
    ├── __init__.py
    ├── test_opus_assistant_sanity.py
    └── test_verification_logic.py
```

### 1.2 Manifest

**File:** `vibe_core/plugins/opus_assistant/manifest.json`

```json
{
  "type": "plugin",
  "id": "opus_assistant",
  "name": "OPUS Assistant",
  "version": "1.0.0",
  "description": "OPUS.md management, verification, drift detection, and assistant agents",

  "entry_point": "plugin_main.py",
  "entry_class": "OpusAssistantPlugin",

  "priority": 50,
  "enabled": true,

  "hooks": [
    "on_boot",
    "on_shutdown",
    "on_cli_register",
    "on_event"
  ],

  "dependencies": [
    "interface"
  ],

  "capabilities": [
    "opus.verify",
    "opus.drift_detect",
    "opus.assistant"
  ],

  "defaults": {
    "auto_verify_on_boot": true,
    "drift_detection_enabled": true
  },

  "author": "STEWARD Protocol",
  "tags": ["opus", "verification", "assistant", "governance"]
}
```

### 1.3 Plugin Main

**File:** `vibe_core/plugins/opus_assistant/plugin_main.py`

```python
"""
OPUS Assistant Plugin - The OPUS.md Management System
"""
import logging
from typing import TYPE_CHECKING, Optional

from vibe_core.plugin_protocol import KernelPlugin
from vibe_core.event_bus import get_event_bus, EventType

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("OPUS_ASSISTANT")

class OpusAssistantPlugin(KernelPlugin):
    """
    OPUS Assistant - Active manager for OPUS.md ecosystem.

    Capabilities:
    - opus.verify: Run @HARNESS verification
    - opus.drift_detect: Compare code vs docs
    - opus.assistant: AI assistant for OPUS maintenance
    """

    @property
    def plugin_id(self) -> str:
        return "opus_assistant"

    @property
    def priority(self) -> int:
        return 50  # After interface (10), before most others

    def __init__(self):
        self._kernel: Optional["RealVibeKernel"] = None
        self._verification_engine = None
        self._drift_detector = None
        self._event_bus = None

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """Initialize OPUS Assistant on kernel boot."""
        self._kernel = kernel

        # Initialize core components
        from .core.verification_logic import VerificationEngine
        from .core.drift_detector import DriftDetector
        from .core.state_bridge import StateBridge

        self._verification_engine = VerificationEngine(kernel.workspace_path)
        self._drift_detector = DriftDetector(kernel)
        self._state_bridge = StateBridge(kernel)

        # Subscribe to events
        self._event_bus = get_event_bus()
        self._event_bus.subscribe(self._on_commit_event, EventType.COMPLETED)

        # Auto-verify on boot if enabled
        config = kernel.get_plugin_config("opus_assistant")
        if config.get("auto_verify_on_boot", True):
            self._run_quick_verify()

        logger.info("🎯 OPUS Assistant online")

    def on_cli_register(self, cli_registry) -> None:
        """Register CLI commands."""
        from .cli.commands import register_commands
        register_commands(cli_registry, self)

    def verify(self, quick: bool = False) -> dict:
        """Run OPUS verification."""
        return self._verification_engine.run_verification(quick=quick)

    def detect_drift(self) -> dict:
        """Detect drift between code and documentation."""
        return self._drift_detector.detect()
```

---

## Phase 2: Drift Detection

**Goal:** Detect when code changes but docs don't (or vice versa).

### 2.1 DriftDetector

**File:** `vibe_core/plugins/opus_assistant/core/drift_detector.py`

```python
"""
Drift Detection - Code vs Documentation alignment.

Uses GitState to compare:
- Files changed in recent commits
- @HARNESS sections in OPUS docs
- Linked file timestamps
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

@dataclass
class DriftReport:
    """Report of detected drift."""
    code_without_docs: List[str]  # Files changed but not in @HARNESS
    docs_without_code: List[str]  # @HARNESS refs to non-existent files
    stale_docs: List[str]         # Docs older than linked code
    overall_health: float         # 0.0 - 1.0

class DriftDetector:
    """
    Detects drift between code and documentation.

    Integrates with:
    - GitState (vibe_core/state/git_state.py)
    - Prakriti (vibe_core/state/prakriti.py)
    - VerificationEngine (our core/verification_logic.py)
    """

    def __init__(self, kernel: "RealVibeKernel"):
        self._kernel = kernel
        from vibe_core.state.prakriti import Prakriti
        self._prakriti = Prakriti.from_workspace(str(kernel.workspace_path))

    def detect(self, since_commit: str = "HEAD~10") -> DriftReport:
        """
        Detect drift since a given commit.

        Strategy:
        1. Get files changed since commit (GitState.diff)
        2. Get all @HARNESS file references
        3. Cross-reference to find orphans
        """
        # 1. Get changed files
        git_diff = self._prakriti.diff(since_commit)
        changed_files = set(git_diff.files)

        # 2. Get @HARNESS references
        from .verification_logic import VerificationEngine
        engine = VerificationEngine(self._kernel.workspace_path)
        harness_files = engine.get_all_harness_files()

        # 3. Find drift
        code_without_docs = [f for f in changed_files
                           if f.endswith('.py') and f not in harness_files]
        docs_without_code = [f for f in harness_files
                           if not (self._kernel.workspace_path / f).exists()]

        # Calculate health
        total = len(changed_files) + len(harness_files)
        issues = len(code_without_docs) + len(docs_without_code)
        health = 1.0 - (issues / total) if total > 0 else 1.0

        return DriftReport(
            code_without_docs=code_without_docs,
            docs_without_code=docs_without_code,
            stale_docs=[],  # TODO: timestamp comparison
            overall_health=health
        )
```

---

## Phase 3: Event-Driven Architecture

**Goal:** React to system events automatically.

### 3.1 Event Handlers

**File:** `vibe_core/plugins/opus_assistant/events/handlers.py`

```python
"""
Event handlers for OPUS Assistant.

Subscribes to EventBus and triggers actions:
- On commit: Check if OPUS docs need update
- On file change: Re-verify affected @HARNESS
- On boot: Quick verification
"""
from vibe_core.event_bus import Event, EventType, emit_event

async def on_git_commit(event: Event, plugin):
    """Handle git commit events."""
    # Check if any OPUS-tracked files changed
    files = event.details.get("files", [])
    opus_affected = any(
        f.startswith("docs/architecture/OPUS/") or
        f == "OPUS.md"
        for f in files
    )

    if opus_affected:
        # Re-run verification
        result = plugin.verify(quick=True)

        # Emit verification result
        await emit_event(
            event_type="OPUS_VERIFICATION_COMPLETED",
            agent_id="opus_assistant",
            message=f"Verification: {result['total_score']}%",
            details=result
        )

async def on_file_change(event: Event, plugin):
    """Handle file change events (watch mode)."""
    path = event.details.get("path", "")

    # Check if it's a tracked file
    if plugin._drift_detector.is_tracked(path):
        await emit_event(
            event_type="OPUS_DRIFT_DETECTED",
            agent_id="opus_assistant",
            message=f"Potential drift: {path} changed",
            details={"file": path, "severity": "info"}
        )
```

---

## Phase 4: Opus Assistant Agent

**Goal:** Create the orchestrator agent that uses EXISTING Auditor tools.

### 4.1 Assistant Agent

**File:** `vibe_core/plugins/opus_assistant/agents/opus_assistant.py`

```python
"""
OPUS Assistant Agent - The Orchestrator.

IMPORTANT: Does NOT duplicate Auditor functionality!
Instead, USES Auditor tools via kernel.execute_tool().

Capabilities:
- Orchestrate verification workflows
- Suggest documentation updates
- Spawn ephemeral verification agents
"""
from typing import Any, Dict, TYPE_CHECKING
from vibe_core.protocols import VibeAgent, AgentManifest
from vibe_core.scheduling.task import Task

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

class OpusAssistantAgent(VibeAgent):
    """
    OPUS Assistant - Orchestrates documentation maintenance.

    Tool Protocol Compliant:
    - NO tool instances owned
    - Uses self.system.execute_tool() for Auditor, etc.
    """

    def __init__(self, kernel: "RealVibeKernel"):
        super().__init__(
            agent_id="opus_assistant",
            name="OPUS Assistant",
            version="1.0.0",
            author="Steward Protocol",
            description="Documentation verification and maintenance orchestrator",
            domain="GOVERNANCE",
            capabilities=[
                "opus.verify",
                "opus.drift_detect",
                "opus.suggest_update",
                "opus.spawn_verifiers"
            ]
        )
        self._kernel = kernel

    async def process(self, task: Task) -> Dict[str, Any]:
        """Process OPUS-related tasks."""
        action = task.payload.get("action")

        if action == "verify":
            return await self._verify(task)
        elif action == "constitutional_check":
            # DELEGATE to Auditor - don't duplicate!
            return self.system.execute_tool(
                "auditor.verdict",
                {"action": "render_verdict"}
            )
        elif action == "suggest_update":
            return await self._suggest_update(task)
        else:
            return {"status": "unknown_action", "action": action}

    async def _verify(self, task: Task) -> Dict[str, Any]:
        """Run verification through the plugin."""
        plugin = self._kernel.get_plugin("opus_assistant")
        return plugin.verify(quick=task.payload.get("quick", False))

    async def _suggest_update(self, task: Task) -> Dict[str, Any]:
        """Suggest documentation updates based on code changes."""
        plugin = self._kernel.get_plugin("opus_assistant")
        drift = plugin.detect_drift()

        suggestions = []
        for file in drift.code_without_docs:
            suggestions.append({
                "type": "add_to_harness",
                "file": file,
                "reason": "File changed but not tracked in @HARNESS"
            })

        return {
            "suggestions": suggestions,
            "drift_health": drift.overall_health
        }
```

---

## Phase 5: CLI Commands

**Goal:** `steward opus verify`, `steward opus drift`, etc.

### 5.1 Commands

**File:** `vibe_core/plugins/opus_assistant/cli/commands.py`

```python
"""
CLI commands for OPUS Assistant.

Registers:
- steward opus verify [--quick]
- steward opus drift [--since COMMIT]
- steward opus status
"""
import click

def register_commands(cli_registry, plugin):
    """Register OPUS CLI commands."""

    @cli_registry.group()
    def opus():
        """OPUS documentation management commands."""
        pass

    @opus.command()
    @click.option("--quick", is_flag=True, help="Quick verification (skip semantic)")
    def verify(quick: bool):
        """Run @HARNESS verification on OPUS docs."""
        result = plugin.verify(quick=quick)

        # Format output
        score = result.get("total_score", 0)
        emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"

        click.echo(f"\n{emoji} OPUS Verification: {score}%")
        click.echo(f"   Docs with @HARNESS: {result.get('docs_with_harness', 0)}")
        click.echo(f"   Docs without: {result.get('docs_without_harness', 0)}")

        if result.get("failures"):
            click.echo("\n❌ Failures:")
            for f in result["failures"][:5]:
                click.echo(f"   - {f}")

    @opus.command()
    @click.option("--since", default="HEAD~10", help="Check drift since commit")
    def drift(since: str):
        """Detect code vs documentation drift."""
        result = plugin.detect_drift()

        health = result.overall_health
        emoji = "🟢" if health >= 0.8 else "🟡" if health >= 0.6 else "🔴"

        click.echo(f"\n{emoji} Drift Health: {health:.0%}")

        if result.code_without_docs:
            click.echo("\n⚠️  Code changed but not in @HARNESS:")
            for f in result.code_without_docs[:5]:
                click.echo(f"   - {f}")

    @opus.command()
    def status():
        """Show OPUS system status."""
        click.echo("\n📊 OPUS Assistant Status")
        click.echo(f"   Plugin: {'✅ Active' if plugin._kernel else '❌ Inactive'}")
        click.echo(f"   Auto-verify: {plugin._kernel.get_plugin_config('opus_assistant').get('auto_verify_on_boot')}")
```

---

## Phase 6: Circuits & Playbooks

**Goal:** Declarative workflows using existing CircuitEngine.

### 6.1 Verification Circuit

**File:** `vibe_core/plugins/opus_assistant/circuits/verify_workflow.yaml`

```yaml
# OPUS Verification Circuit
# Uses existing circuit_engine.py - NO new executor needed!

circuit:
  id: OPUS_VERIFY_V1
  name: "OPUS Documentation Verification"
  description: "Verify all OPUS docs against @HARNESS definitions"

  entry_state: INIT

  invariants:
    - check: "workspace is not empty"
      severity: critical
    - check: "opus_docs_path is not empty"
      severity: critical

  states:
    INIT:
      operations:
        - action: SET_VARIABLE
          name: opus_docs_path
          value: "docs/architecture/OPUS"
        - action: SET_VARIABLE
          name: results
          value: []
      transitions:
        - condition: "opus_docs_path is not empty"
          to: SCAN_DOCS

    SCAN_DOCS:
      operations:
        - action: EXECUTE_SYSCALL
          syscall_type: DISPATCH_TASK
          params:
            target_agent: "opus_assistant"
            action: "list_docs"
            path: "{{ opus_docs_path }}"
      transitions:
        - condition: "scan_result.success == true"
          to: VERIFY_EACH
        - condition: "true"
          to: FAILED

    VERIFY_EACH:
      operations:
        - action: FOR_EACH
          items: "{{ scan_result.docs }}"
          do:
            - action: EXECUTE_SYSCALL
              syscall_type: DISPATCH_TASK
              params:
                target_agent: "opus_assistant"
                action: "verify_doc"
                doc_path: "{{ item }}"
      transitions:
        - condition: "all_verified == true"
          to: SUCCESS
        - condition: "true"
          to: PARTIAL_SUCCESS

    SUCCESS:
      terminal: true
      output:
        status: "verified"
        score: "{{ total_score }}"
        docs_checked: "{{ docs_checked }}"

    PARTIAL_SUCCESS:
      terminal: true
      output:
        status: "partial"
        score: "{{ total_score }}"
        failures: "{{ failures }}"

    FAILED:
      terminal: true
      output:
        status: "failed"
        error: "{{ error_message }}"
```

---

## Phase 7: Ephemeral Cities (Advanced)

**Goal:** Spawn verification agent swarms for parallel processing.

### 7.1 City Spawner

**File:** `vibe_core/plugins/opus_assistant/agents/city_spawner.py`

```python
"""
Ephemeral City Spawner - Parallel verification agents.

Uses EventBus for result aggregation (as per Gemini's review).
"""
import asyncio
from typing import Any, Dict, List
from vibe_core.event_bus import get_event_bus, Event, emit_event

class CitySpawner:
    """
    Spawns ephemeral verification agents for parallel processing.

    Architecture (Event-Driven):
    1. Spawn N agents for N documents
    2. Each agent emits OPUS_DOC_VERIFIED event
    3. Aggregator collects events and builds final report
    """

    def __init__(self, kernel):
        self._kernel = kernel
        self._event_bus = get_event_bus()
        self._results: Dict[str, Any] = {}

    async def spawn_verification_city(self, docs: List[str]) -> Dict[str, Any]:
        """
        Spawn ephemeral agents for parallel doc verification.

        Args:
            docs: List of doc paths to verify

        Returns:
            Aggregated verification results
        """
        # Subscribe to results
        self._results = {}
        completion_event = asyncio.Event()
        expected = len(docs)

        async def on_doc_verified(event: Event):
            doc = event.details.get("doc")
            self._results[doc] = event.details.get("result")
            if len(self._results) >= expected:
                completion_event.set()

        self._event_bus.subscribe(on_doc_verified, "OPUS_DOC_VERIFIED")

        # Spawn verification tasks
        tasks = []
        for doc in docs:
            task = self._kernel.schedule_task(
                agent_id="opus_assistant_ephemeral",
                payload={
                    "action": "verify_single",
                    "doc": doc,
                    "ephemeral": True  # Agent terminates after task
                }
            )
            tasks.append(task)

        # Wait for all results (with timeout)
        try:
            await asyncio.wait_for(completion_event.wait(), timeout=30.0)
        except asyncio.TimeoutError:
            pass  # Return partial results

        # Aggregate
        return {
            "docs_verified": len(self._results),
            "docs_failed": expected - len(self._results),
            "results": self._results,
            "total_score": self._calculate_score()
        }

    def _calculate_score(self) -> int:
        if not self._results:
            return 0
        scores = [r.get("score", 0) for r in self._results.values()]
        return sum(scores) // len(scores)
```

---

## Implementation Order

### Immediate (This Session)

1. **Phase 0.1**: Create `opus_assistant` plugin directory structure
2. **Phase 0.2**: Extract VerificationEngine (pure logic)
3. **Phase 0.3**: Create manifest.json and plugin_main.py skeleton
4. **Phase 0.4**: Wire up so existing OPUS panel uses new logic

### Next Session

5. **Phase 1**: Full plugin implementation with DriftDetector
6. **Phase 2**: CLI commands
7. **Phase 3**: Event handlers

### Future

8. **Phase 4**: Opus Assistant Agent
9. **Phase 5**: Circuits
10. **Phase 6**: Ephemeral Cities

---

## @HARNESS

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manifest.json
    required: true
  - path: vibe_core/plugins/opus_assistant/plugin_main.py
    required: true
  - path: vibe_core/plugins/opus_assistant/core/verification_logic.py
    required: true

tests:
  - vibe_core/plugins/opus_assistant/tests/test_opus_assistant_sanity.py
  - vibe_core/plugins/opus_assistant/tests/test_verification_logic.py

wiring:
  - pattern: "class OpusAssistantPlugin"
    in: vibe_core/plugins/opus_assistant/plugin_main.py
  - pattern: "class VerificationEngine"
    in: vibe_core/plugins/opus_assistant/core/verification_logic.py

semantic:
  - type: plugin_loaded
    plugin: opus_assistant
    name: "Plugin entry point valid"
-->

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Breaking existing OPUS panel | Phase 0 extracts logic FIRST, panel imports from new location |
| Duplicating Auditor | Assistant USES auditor tools, doesn't rebuild them |
| Circular imports | Clear dependency direction: plugin → core → no kernel imports in core |
| Performance (large codebases) | Existing safety limits (MAX_FILES_TO_SCAN=500) preserved |

---

## Success Criteria

1. **Phase 0 Complete:** OPUS.md still renders, no rich imports in verification_logic.py
2. **Phase 1 Complete:** `steward opus verify` works from CLI
3. **Full MVP:** Drift detection + event-driven auto-verification
4. **Golden Standard:** Ephemeral cities for parallel verification

---

*This document is the blueprint. Implementation follows.*
