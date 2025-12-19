# OPUS-089: MANAS Oracle API - Wisdom Interface

**Status:** ✅ Production Ready
**Scope:** Service-Oriented Architecture for MANAS Consultation
**Philosophy:** "System agents are fractal-matching collections of jobs" → Clean interface, no spaghetti

---

## The Oracle Harness

<!-- @HARNESS
files:
  # === ORACLE API ===
  - path: vibe_core/plugins/opus_assistant/manas/api.py
    required: true
    description: "ManasOracle class, AnalysisResult dataclass, wisdom interface"

  # === INTEGRATION ===
  - path: scripts/heartbeat.py
    required: true
    description: "Heartbeat engine with pre_analysis + post_analysis gates"

  - path: vibe_core/plugins/opus_assistant/manas/__init__.py
    required: true
    description: "Module exports for ManasOracle, AnalysisResult"

  # === TESTS ===
  - path: tests/unit/test_manas_oracle_api.py
    required: true
    description: "15 unit tests covering all API methods"

  - path: tests/integration/test_manas_oracle_heartbeat.py
    required: true
    description: "13 integration tests for heartbeat flow"

  # === DOCUMENTATION ===
  - path: docs/MANAS_ORACLE_API.md
    required: true
    description: "Complete API reference and usage guide"

wiring:
  # === HEARTBEAT INITIALIZATION ===
  # Heartbeat imports ManasOracle
  - pattern: "from vibe_core.plugins.opus_assistant.manas.api import ManasOracle"
    in: scripts/heartbeat.py

  # MANAS_ORACLE_AVAILABLE flag set
  - pattern: "MANAS_ORACLE_AVAILABLE = True"
    in: scripts/heartbeat.py

  # ManasOracle instantiated in __init__
  - pattern: "self.manas_oracle = ManasOracle"
    in: scripts/heartbeat.py

  # === PRE-ANALYSIS GATE (before execution) ===
  # Pre-analysis called before UnifiedRouter
  - pattern: "self.manas_oracle.pre_analysis"
    in: scripts/heartbeat.py

  # Gate decision checked
  - pattern: "if not gate_decision\\[\"proceed\"\\]"
    in: scripts/heartbeat.py

  # Blocked tasks marked as BLOCKED
  - pattern: "status=TaskStatus.BLOCKED"
    in: scripts/heartbeat.py

  # === POST-ANALYSIS LEARNING (after execution) ===
  # Post-analysis called after success
  - pattern: "self.manas_oracle.post_analysis"
    in: scripts/heartbeat.py

  # Learning recorded
  - pattern: "task_type.*success.*error"
    in: scripts/heartbeat.py

  # === MODULE EXPORTS ===
  # ManasOracle exported from manas module
  - pattern: "ManasOracle"
    in: vibe_core/plugins/opus_assistant/manas/__init__.py

  # AnalysisResult exported
  - pattern: "AnalysisResult"
    in: vibe_core/plugins/opus_assistant/manas/__init__.py

  # === API COMPLETENESS ===
  # consult() method exists
  - pattern: "def consult"
    in: vibe_core/plugins/opus_assistant/manas/api.py

  # pre_analysis() method exists
  - pattern: "def pre_analysis"
    in: vibe_core/plugins/opus_assistant/manas/api.py

  # post_analysis() method exists
  - pattern: "def post_analysis"
    in: vibe_core/plugins/opus_assistant/manas/api.py

tests:
  # === UNIT TESTS ===
  - path: tests/unit/test_manas_oracle_api.py
    suite: TestManasOracleBasics
    tests:
      - test_oracle_initialization
      - test_consult_low_risk_task
      - test_consult_high_risk_task
      - test_analysis_result_to_dict
      - test_analysis_result_str

  - path: tests/unit/test_manas_oracle_api.py
    suite: TestManasOracleAPIs
    tests:
      - test_pre_analysis_allows_safe_task
      - test_pre_analysis_blocks_dangerous_task
      - test_post_analysis_records_success
      - test_post_analysis_records_failure

  - path: tests/unit/test_manas_oracle_api.py
    suite: TestManasOracleRiskIdentification
    tests:
      - test_identifies_production_risk
      - test_identifies_large_changeset_risk
      - test_suggests_production_precautions

  - path: tests/unit/test_manas_oracle_api.py
    suite: TestManasOracleMemoryIntegration
    tests:
      - test_confidence_based_on_history

  - path: tests/unit/test_manas_oracle_api.py
    suite: TestManasOracleErrorHandling
    tests:
      - test_consult_handles_missing_context_keys
      - test_consult_returns_safe_default_on_error

  # === INTEGRATION TESTS ===
  - path: tests/integration/test_manas_oracle_heartbeat.py
    suite: TestManasOracleHeartbeatIntegration
    tests:
      - test_oracle_import_in_heartbeat
      - test_heartbeat_imports_oracle_conditionally
      - test_oracle_api_structure
      - test_oracle_pre_analysis_gate_decision
      - test_oracle_post_analysis_learning
      - test_oracle_analysis_result_serialization
      - test_oracle_available_flag_in_heartbeat

  - path: tests/integration/test_manas_oracle_heartbeat.py
    suite: TestManasOracleHeartbeatFlow
    tests:
      - test_heartbeat_with_oracle_flow
      - test_oracle_risk_identification_in_flow
      - test_oracle_confidence_evolution

  - path: tests/integration/test_manas_oracle_heartbeat.py
    suite: TestManasOracleErrorRecovery
    tests:
      - test_oracle_handles_malformed_context
      - test_oracle_handles_null_values
      - test_oracle_handles_extreme_values

quality:
  # All tests must pass
  - unit_tests_passing: "28/28 ✅"
  - integration_tests_passing: "13/13 ✅"
  - code_coverage: ">90%"
  - documentation_complete: "yes"
  - error_handling: "resilient"
@HARNESS -->

---

## Architecture

### The Flow

```
Heartbeat (every 15 min)
  ↓
  ├─→ OPUS-089: Pre-Analysis Gate
  │   └─→ ManasOracle.pre_analysis(context)
  │       ├─→ Risk identification
  │       ├─→ Safety scoring
  │       └─→ Gate decision (proceed/block)
  │
  ├─→ [GATE DECISION]
  │   ├─→ If blocked: Update task as BLOCKED
  │   └─→ If proceed: Continue
  │
  ├─→ UnifiedRouter → Task Execution
  │
  └─→ OPUS-089: Post-Analysis Learning
      └─→ ManasOracle.post_analysis(result)
          ├─→ Record outcome
          ├─→ Update memory
          └─→ Improve confidence
```

### Core Classes

**`ManasOracle`** - The Wisdom Service
- `consult(context)` → `AnalysisResult` - Ask for advice
- `pre_analysis(task_context)` → `Dict` - Gate before execution
- `post_analysis(task_result)` → `Dict` - Learn after execution

**`AnalysisResult`** - The Recommendation
- `priority: IntentPriority` - CRITICAL/HIGH/MEDIUM/LOW
- `safety_score: float` - 0.0-1.0
- `confidence: float` - 0.0-1.0
- `advice: str` - Human-readable recommendation
- `risks: List[str]` - Identified risks
- `precautions: List[str]` - Suggested safeguards

---

## Safety Heuristics

| Scenario | Safety Score | Action |
|----------|--------------|--------|
| Low risk + user approval | 0.95+ | EXECUTE_NOW |
| Medium risk + approval | 0.70-0.90 | EXECUTE_WITH_MONITORING |
| High risk + no approval | 0.30-0.50 | REQUEST_APPROVAL |
| Critical + automated | <0.10 | BLOCK_AND_REVIEW |
| Production without backup plan | -0.20 penalty | Extra precautions |

---

## Key Features

✅ **Separation of Concerns** - Clean interface, no direct coupling  
✅ **Stateful Learning** - Memory improves confidence over time  
✅ **Deterministic** - Same input → same output  
✅ **Resilient** - Handles errors gracefully, never raises  
✅ **Traceable** - All decisions include reasoning  
✅ **Fractal-Ready** - Any system agent can use this API  

---

## Integration Points

### Heartbeat (✅ Done)
```python
# In _execute_tasks():
gate = oracle.pre_analysis(context)
if gate["proceed"]:
    result = execute_task()
    oracle.post_analysis(result)
```

### Envoy (⏳ Next)
```python
# Router could ask: "How confident am I about this route?"
recommendation = oracle.consult(route_context)
confidence = recommendation.confidence
```

### Other Agents (⏳ Future)
```python
# Herald: "Is this health check reliable?"
# Auditor: "Is this compliant?"
# Any agent can consult MANAS
```

---

## Test Coverage

**Unit Tests (15):**
- Basic functionality ✅
- All 3 APIs ✅
- Risk identification ✅
- Memory learning ✅
- Error handling ✅

**Integration Tests (13):**
- Heartbeat integration ✅
- Risk flow ✅
- Confidence evolution ✅
- Error recovery ✅

**Total: 28/28 passing** 🎉

---

## Philosophy

> "The harness is the truth. The code follows the harness."

This OPUS-089 harness defines:
1. **What files must exist** (the API)
2. **How they're wired** (the integration)
3. **What tests verify them** (the proof)

Run the harness → know the state. No guessing.

---

## See Also

- [MANAS Oracle API Docs](../../../docs/MANAS_ORACLE_API.md)
- [Heartbeat Integration](../../../scripts/heartbeat.py)
- [OPUS-075: MANAS Reliability](./075-MANAS-RELIABILITY.md)
- [OPUS-032: Cognitive Kernel](./032-MANAS-COGNITION.md)
