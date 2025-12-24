# OPUS-212: SHUDDHI ENGINE - Core Self-Healing Architecture

**Status:** PLANNING
**Priority:** P0 - Architectural Foundation
**Author:** Claude Opus 4.5
**Date:** 2024-12-24
**Dependencies:** OPUS-053 (SILPA), standards.yaml, HEAL_CODEBASE_V1 Circuit

---

## 1. PROBLEM STATEMENT

### 1.1 The Gap

The system has:
- **Detection** (Watchman/StandardsInspectionTool) - AST-based violation detection via `config/standards.yaml`
- **Orchestration** (HEAL_CODEBASE_V1 Circuit) - State machine for healing workflow
- **Execution** (Engineer Agent) - Task dispatch and tool invocation

But it lacks:
- **Transformation** - The ability to actually modify code from Tamas (violating) to Sattva (compliant)

### 1.2 The Hidden Asset

SILPA (`vibe_core/plugins/opus_assistant/manas/cortex/silpa.py`) already implements:
- `SilpaTransformer` - AST-based code transformation
- `SilpaAuditor` - Platinum Protocol (tests before/after)
- `SilpaArchitect` - Orchestration with rollback

But SILPA is a **Plugin** (opus_assistant). The State cannot depend on Plugins for core functionality.

### 1.3 The Architectural Sin

Previous agent created `refactor_tool.py` with:
- Hardcoded string patterns (not scalable)
- Raw I/O (`file.read_text()`, `file.write_text()`) - Dharma violation
- No test verification (no Platinum Protocol)

This was "imperative thinking in a declarative system."

---

## 2. SOLUTION: SHUDDHI ENGINE

**Sanskrit:** Shuddhi = Purification, Cleansing

### 2.1 Core Principle

> "The purifier reads the law (standards.yaml) and applies it to the code.
> It does not invent the law. It enforces it."

### 2.2 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CORE (vibe_core)                             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            ShuddhiEngine (cortex/engines/shuddhi.py)    │   │
│  │                                                         │   │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │   │
│  │   │ShuddhiAuditor│  │ShuddhiTrans-│  │ShuddhiArchi-│    │   │
│  │   │ (Platinum   │  │  former     │  │   tect      │    │   │
│  │   │  Protocol)  │  │ (AST-based) │  │(Orchestrator│    │   │
│  │   └─────────────┘  └─────────────┘  └─────────────┘    │   │
│  │          │                │                │            │   │
│  │          └────────────────┼────────────────┘            │   │
│  │                           │                             │   │
│  │                    ┌──────┴──────┐                      │   │
│  │                    │ standards.  │                      │   │
│  │                    │    yaml     │                      │   │
│  │                    │ (transform  │                      │   │
│  │                    │   rules)    │                      │   │
│  │                    └─────────────┘                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ▲                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────┐
│                    PLUGIN (opus_assistant)                      │
│                              │                                  │
│  ┌───────────────────────────┴──────────────────────────────┐  │
│  │                    SILPA (The Self-Architect)             │  │
│  │                                                           │  │
│  │   Imports: from vibe_core.cortex.engines.shuddhi import   │  │
│  │            ShuddhiEngine                                  │  │
│  │                                                           │  │
│  │   SILPA becomes a CONSUMER of ShuddhiEngine, not OWNER    │  │
│  │   - Adds cognitive layer (LLM-assisted refactoring)       │  │
│  │   - Adds JNANA integration (chat interface)               │  │
│  │   - Adds complex refactorings (extract method, etc.)      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 2.3 Dependency Inversion

**Before (Wrong):**
```
State → depends on → Plugin (SILPA)
```

**After (Correct):**
```
State (ShuddhiEngine) ← used by ← Plugin (SILPA)
```

---

## 3. DESIGN SPECIFICATION

### 3.1 standards.yaml Extension

Current structure (Detection only):
```yaml
rules:
  - id: "unsafe_io_write"
    target: "Call"
    match:
      func: "open"
      args_contain: ["w", "a"]
    severity: "CRITICAL"
    message: "Raw write-access detected"
    fix_suggestion: "Use self.system.write_file()"  # Text only
```

Extended structure (Detection + Transformation):
```yaml
rules:
  - id: "unsafe_io_write"
    target: "Call"
    match:
      func: "open"
      args_contain: ["w", "a"]
    severity: "CRITICAL"
    message: "Raw write-access detected"

    # NEW: Structured transformation rule
    transform:
      type: "call_replacement"

      # AST pattern to match (symbolic)
      from_pattern:
        call: "open"
        context: "with_statement"  # with open(...) as f: f.write(...)

      # AST pattern to generate
      to_pattern:
        call: "self.system.write_file"
        args: ["$path", "$content"]

      # Fallback: If AST transform fails, use semantic description
      fallback_instruction: |
        Replace:
          with open(path, 'w') as f:
              f.write(content)
        With:
          self.system.write_file(str(path), content)
```

### 3.2 ShuddhiTransformer

```python
# vibe_core/cortex/engines/shuddhi.py

class ShuddhiTransformer:
    """
    AST-based code transformer for Todsünden (Cardinal Sins).

    Reads transformation rules from standards.yaml and applies them.
    Does NOT invent transformations - only enforces declared rules.
    """

    def __init__(self):
        self._rules = self._load_rules()

    def _load_rules(self) -> Dict[str, TransformRule]:
        """Load transform rules from standards.yaml."""
        # Returns only rules that have 'transform' field

    def can_transform(self, rule_id: str) -> bool:
        """Check if we have a transform rule for this violation."""
        return rule_id in self._rules

    def transform(
        self,
        code: str,
        rule_id: str,
        violation_context: Dict[str, Any],
    ) -> Tuple[str, List[str]]:
        """
        Transform code according to the rule.

        Args:
            code: Original source code
            rule_id: Rule ID from standards.yaml (e.g., "unsafe_io_write")
            violation_context: Context from StandardsInspectionTool
                - line_number
                - code_snippet
                - etc.

        Returns:
            Tuple of (transformed_code, list_of_changes)
        """
```

### 3.3 ShuddhiAuditor

```python
class ShuddhiAuditor:
    """
    Platinum Protocol enforcement.

    Copied from SILPA but simplified for Core usage.
    No cognitive features - just test verification.
    """

    def run_pre_gate(self, target_file: Path) -> TestResult:
        """Tests must pass BEFORE transformation."""

    def run_post_gate(self, target_file: Path) -> TestResult:
        """Tests must pass AFTER transformation."""
```

### 3.4 ShuddhiArchitect

```python
class ShuddhiArchitect:
    """
    Main orchestrator for code purification.

    Coordinates:
    1. PRE-GATE (tests must pass)
    2. TRANSFORM (apply AST changes)
    3. POST-GATE (tests must still pass)
    4. ROLLBACK (if POST-GATE fails)
    """

    def __init__(self, system: AgentSystemInterface):
        self._system = system  # VFS access, no Raw I/O
        self._transformer = ShuddhiTransformer()
        self._auditor = ShuddhiAuditor()

    def purify(
        self,
        violation: Violation,
        dry_run: bool = False,
    ) -> ShuddhiResult:
        """
        Purify a single violation.

        Args:
            violation: Violation from StandardsInspectionTool
            dry_run: If True, don't modify files

        Returns:
            ShuddhiResult with success/failure and audit trail
        """
```

---

## 4. INTEGRATION

### 4.1 Engineer Tool

```python
# vibe_core/cartridges/system/engineer/tools/heal_violation_tool.py

class HealViolationTool(Tool):
    """
    Heals code violations using ShuddhiEngine.

    This tool is a THIN WRAPPER around ShuddhiArchitect.
    It does NOT implement transformation logic - that's in the Engine.
    """

    @property
    def name(self) -> str:
        return "engineer.heal_violation"

    def execute(self, params: Dict) -> ToolResult:
        from vibe_core.cortex.engines.shuddhi import ShuddhiArchitect

        architect = ShuddhiArchitect(self._system)
        result = architect.purify(
            violation=params["violation"],
            dry_run=params.get("dry_run", False),
        )

        return ToolResult(
            success=result.success,
            output=result.to_dict(),
        )
```

### 4.2 HEAL_CODEBASE_V1 Circuit

The circuit remains as designed in the earlier fix:
1. SHABDA: Validate input (violation info)
2. ARTHA: Pass-through (context already captured)
3. PRATYAYA: Route based on violation_type
4. KARMA: DISPATCH_TASK to engineer.heal_violation
5. VERIFY: Check result
6. SUCCESS/FAILURE: Terminal states

### 4.3 SILPA Migration

```python
# vibe_core/plugins/opus_assistant/manas/cortex/silpa.py (UPDATED)

# Import Core engine
from vibe_core.cortex.engines.shuddhi import (
    ShuddhiArchitect,
    ShuddhiTransformer,
    ShuddhiAuditor,
)

class SilpaArchitect:
    """
    SILPA now EXTENDS ShuddhiEngine with cognitive capabilities.

    Core transformation: Delegated to ShuddhiArchitect
    Cognitive features: LLM-assisted analysis, complex refactorings
    """

    def __init__(self, workspace: Path = None):
        # Core engine for basic transformations
        self._shuddhi = ShuddhiArchitect(workspace)

        # SILPA-specific: LLM integration, JNANA interface, etc.
        self._cognitive_enabled = True

    def execute(self, plan: SilpaPlan, ...) -> SilpaResult:
        # For basic violations: delegate to ShuddhiEngine
        if self._shuddhi.can_transform(plan.refactoring.rule_id):
            return self._shuddhi.purify(...)

        # For complex refactorings: use SILPA's cognitive layer
        return self._execute_cognitive(plan, ...)
```

---

## 5. IMPLEMENTATION PLAN

### Phase 1: Foundation (This Session)

1. [ ] Create `vibe_core/cortex/engines/shuddhi.py`
   - [ ] ShuddhiTransformer (AST-based, reads from standards.yaml)
   - [ ] ShuddhiAuditor (Platinum Protocol)
   - [ ] ShuddhiArchitect (Orchestrator)

2. [ ] Extend `config/standards.yaml`
   - [ ] Add `transform` field to existing rules
   - [ ] Define patterns for: unsafe_io_write, silent_failure, direct_path_data

3. [ ] Update `refactor_tool.py` → `heal_violation_tool.py`
   - [ ] Thin wrapper around ShuddhiArchitect
   - [ ] No hardcoded patterns

### Phase 2: Integration

4. [ ] Wire into HEAL_CODEBASE_V1 Circuit
   - [ ] Verify DISPATCH_TASK reaches engineer
   - [ ] Verify engineer invokes heal_violation tool

5. [ ] Test with pilot case: `dashboard_tool.py`
   - [ ] Run circuit
   - [ ] Verify transformation applied
   - [ ] Verify tests pass

### Phase 3: Migration

6. [ ] Update SILPA to use ShuddhiEngine
   - [ ] Import from Core
   - [ ] Delegate basic transformations
   - [ ] Keep cognitive features

7. [ ] Verify no regression in MANAS functionality

### Phase 4: Scale

8. [ ] Run against all 200+ violations
   - [ ] Batch execution
   - [ ] Report generation

---

## 6. RISK ASSESSMENT

| Risk | Mitigation |
|------|------------|
| AST unparse destroys formatting | Run `ruff format` after transformation |
| Complex patterns not matchable | Fallback to semantic instruction (future: LLM) |
| Tests fail after transformation | Platinum Protocol with automatic rollback |
| SILPA regression | Keep SILPA, just change import source |

---

## 7. SUCCESS CRITERIA

1. **ShuddhiEngine exists in Core** - `vibe_core/cortex/engines/shuddhi.py`
2. **No Plugin dependency** - Core can self-heal without opus_assistant
3. **Declarative transforms** - Rules in standards.yaml, not hardcoded
4. **Platinum Protocol** - Tests before/after, rollback on failure
5. **Pilot success** - `dashboard_tool.py` healed via circuit

---

## 8. PHILOSOPHICAL NOTE

> "Shuddhi is not destruction. It is purification.
> The impure code becomes pure not by deletion, but by transformation.
> The law (standards.yaml) declares what is impure.
> The engine (ShuddhiEngine) enforces the purification.
> The architect (ShuddhiArchitect) ensures no harm is done."

---

**Sign-off Required:** Senior Architect approval before implementation.

---

*Generated by Claude Opus 4.5 - OPUS-212 Planning Phase*
