# OPUS-006: GAD-000 Compliance Audit

> **Status**: IN PROGRESS
> **Created**: 2025-12-08
> **Scope**: Audit all kernel components against GAD-000 "Operator Inversion" tests
> **Precedence**: This document MUST be satisfied before implementing OPUS-001 through OPUS-005

---

## Executive Summary

GAD-000 is the **Foundational Law** of the Steward Protocol. All architecture decisions must pass the "GAD-000 Turing Test" - can an AI successfully operate this system without human intervention?

**Current State**: The codebase has good architecture but **fails 4 of 6 GAD-000 tests**.

This audit identifies what needs to change to achieve compliance.

---

## The GAD-000 Turing Test (6 Tests)

| # | Test | Question | Required |
|---|------|----------|----------|
| 1 | **Discoverability** | Can AI find this tool without being told? | `--help --json` or capability schema |
| 2 | **Observability** | Can AI see the current state? | Structured `get_status()` API |
| 3 | **Parseability** | Can AI understand errors? | Machine-readable error codes |
| 4 | **Composability** | Can AI chain operations? | Output matches input schemas |
| 5 | **Idempotency** | Can AI safely retry? | "already done" vs "failed" reporting |
| 6 | **Identity** | Cryptographic signatures? | ECDSA P-256 verification |

**Pass Threshold**: All 6 tests must be "Yes" for GAD-000 compliance.

---

## Current Compliance Matrix

### Core Kernel Components

| Component | 1 | 2 | 3 | 4 | 5 | 6 | Score | Status |
|-----------|---|---|---|---|---|---|-------|--------|
| `kernel.status` | ⚠️ | ❌ | ❌ | ⚠️ | ✅ | ❌ | 1.5/6 | **FAIL** |
| `kernel.ledger` | ⚠️ | ✅ | ⚠️ | ✅ | ✅ | ❌ | 3.5/6 | **FAIL** |
| `kernel.scheduler` | ❌ | ⚠️ | ❌ | ⚠️ | ⚠️ | ❌ | 1/6 | **FAIL** |
| `kernel.envoy` | ⚠️ | ⚠️ | ❌ | ✅ | ⚠️ | ❌ | 2/6 | **FAIL** |
| `LayeredRouter` | ✅ | ✅ | ⚠️ | ✅ | ✅ | ❌ | 4.5/6 | **PARTIAL** |
| `UnifiedExecutor` | ⚠️ | ❌ | ❌ | ✅ | ⚠️ | ❌ | 1.5/6 | **FAIL** |
| `Phoenix Config` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | 5/6 | **PARTIAL** |

### Legend
- ✅ Pass
- ⚠️ Partial (needs improvement)
- ❌ Fail

---

## Test 1: Discoverability

### Current State: ⚠️ PARTIAL

**Problem**: No machine-readable capability discovery.

**What exists**:
- `manifest.json` files for plugins (good)
- Circuit YAML files with metadata (good)
- CLI has `--help` but not `--help --json`

**What's missing**:
- No `kernel.get_capabilities()` returning structured schema
- No tool discovery API for AI agents

### Fix Required

```python
# vibe_core/kernel_impl.py
def get_capabilities(self) -> dict:
    """GAD-000 Test 1: Machine-readable capability discovery."""
    return {
        "version": "1.0",
        "kernel_status": self.status.value,
        "available_methods": [
            {
                "name": "submit_task",
                "purpose": "Queue a task for execution",
                "parameters": [
                    {"name": "agent_id", "type": "string", "required": True},
                    {"name": "payload", "type": "dict", "required": True}
                ],
                "returns": {"success": "task_id", "failure": "error_code + description"}
            },
            # ... more methods
        ],
        "registered_agents": list(self._agent_registry.keys()),
        "available_circuits": list(self.envoy._circuits.keys()) if hasattr(self, 'envoy') else [],
        "plugins_loaded": [p.id for p in self._plugins]
    }
```

---

## Test 2: Observability

### Current State: ❌ FAIL

**Problem**: AI cannot query "what is happening right now?"

**What exists**:
- `kernel.status` enum (IDLE, BOOTING, RUNNING, etc.)
- Ledger stores events (but must query by task_id)
- Logs go to files (human-readable only)

**What's missing**:
- No `get_system_status()` returning structured state
- No execution trace API
- No "what tasks are running?" query

### Fix Required (OPUS-005 Phase 5)

```python
# vibe_core/kernel_impl.py
def get_system_status(self) -> dict:
    """GAD-000 Test 2: AI-readable system state."""
    return {
        "timestamp": time.time(),
        "kernel_status": self.status.value,
        "queue": {
            "pending": self._scheduler.get_queue_status()["pending"],
            "in_progress": self._scheduler.get_queue_status().get("in_progress", 0),
            "completed_last_minute": len([
                e for e in self.ledger.get_recent_events(60)
                if e["event_type"] == "task_completed"
            ])
        },
        "agents": {
            agent_id: {
                "status": agent.status if hasattr(agent, 'status') else "unknown",
                "capabilities": agent.capabilities
            }
            for agent_id, agent in self._agent_registry.items()
        },
        "last_error": self._last_error if hasattr(self, '_last_error') else None,
        "uptime_seconds": time.time() - self._boot_time if hasattr(self, '_boot_time') else 0
    }
```

**Integration with UnifiedTrace (OPUS-005)**:
```python
def get_execution_trace(self, trace_id: str) -> List[dict]:
    """GAD-000 Test 2: What happened in this execution?"""
    return self._trace.get_trace(trace_id)
```

---

## Test 3: Parseability

### Current State: ❌ FAIL

**Problem**: Errors are human-friendly prose, not machine-readable.

**Current error handling**:
```python
# BAD - Current state
logger.error(f"Task {task_id} failed: {str(e)}")
raise Exception(f"Circuit execution failed: {e}")
```

**AI cannot**:
- Distinguish transient vs permanent failures
- Know if retry is safe
- Extract error codes for programmatic handling

### Fix Required

```python
# vibe_core/errors.py (NEW)
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class ErrorCode(Enum):
    # Transient (retry safe)
    E1001_AGENT_BUSY = "E1001"
    E1002_TIMEOUT = "E1002"
    E1003_RATE_LIMITED = "E1003"

    # Permanent (do not retry)
    E2001_INVALID_CIRCUIT = "E2001"
    E2002_AGENT_NOT_FOUND = "E2002"
    E2003_CAPABILITY_DENIED = "E2003"

    # System (escalate)
    E3001_KERNEL_FAULT = "E3001"
    E3002_LEDGER_CORRUPT = "E3002"

@dataclass
class StructuredError:
    """GAD-000 Test 3: Machine-parseable error."""
    code: ErrorCode
    message: str
    context: dict
    retry_safe: bool
    suggested_action: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "error_code": self.code.value,
            "error_name": self.code.name,
            "message": self.message,
            "context": self.context,
            "retry_safe": self.retry_safe,
            "suggested_action": self.suggested_action
        }
```

**Usage**:
```python
# GOOD - GAD-000 compliant
from vibe_core.errors import StructuredError, ErrorCode

try:
    result = await agent.process(task)
except AgentBusyError:
    raise StructuredError(
        code=ErrorCode.E1001_AGENT_BUSY,
        message=f"Agent {agent_id} is processing another task",
        context={"agent_id": agent_id, "task_id": task.task_id},
        retry_safe=True,
        suggested_action="Wait 1 second and retry"
    )
```

---

## Test 4: Composability

### Current State: ⚠️ PARTIAL

**Problem**: Output of one operation doesn't always match input of next.

**What works**:
- Circuit output → Ledger storage (structured)
- Router result → Executor input (RouteResult dataclass)
- Config → All components (Phoenix config objects)

**What doesn't work**:
- CLI output is human-formatted, not JSON
- ENVOY.md is markdown, not machine-readable
- Renderer output is strings, not structured

### Fix Required

```python
# Every public method must return dict or dataclass, never raw strings

# BAD
def execute_circuit(self, circuit_id: str, params: dict) -> str:
    return f"Executed {circuit_id} successfully"

# GOOD - GAD-000 compliant
def execute_circuit(self, circuit_id: str, params: dict) -> dict:
    return {
        "circuit_id": circuit_id,
        "status": "completed",
        "result": {...},
        "trace_id": "abc123",
        "duration_ms": 150
    }
```

---

## Test 5: Idempotency

### Current State: ⚠️ PARTIAL

**Problem**: AI doesn't know if retry is safe or if operation already succeeded.

**What works**:
- Ledger records all events (can check if task exists)
- Task IDs are unique (won't duplicate)

**What's missing**:
- No "operation already completed" detection
- No idempotency keys for requests

### Fix Required

```python
# vibe_core/scheduler.py
def submit_task(self, task: Task, idempotency_key: Optional[str] = None) -> dict:
    """GAD-000 Test 5: Safe retry with idempotency."""

    # Check if operation already completed
    if idempotency_key:
        existing = self._idempotency_cache.get(idempotency_key)
        if existing:
            return {
                "status": "already_completed",
                "task_id": existing["task_id"],
                "result": existing["result"],
                "idempotency_key": idempotency_key
            }

    # Execute new task
    task_id = self._queue_task(task)

    # Store for idempotency
    if idempotency_key:
        self._idempotency_cache[idempotency_key] = {
            "task_id": task_id,
            "timestamp": time.time()
        }

    return {
        "status": "queued",
        "task_id": task_id,
        "idempotency_key": idempotency_key
    }
```

---

## Test 6: Identity (GAD-1000)

### Current State: ❌ NOT IMPLEMENTED

**Problem**: No cryptographic signature verification.

**What exists**:
- Agent IDs (string identifiers)
- Capability system (permission checks)

**What's missing**:
- ECDSA P-256 key pairs for agents
- Signature verification on operations
- Human identity wallet integration

### Fix Required (Future - GAD-1000 Implementation)

```python
# vibe_core/identity.py (NEW - FUTURE)
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization

class AgentIdentity:
    """GAD-1000: Cryptographic agent identity."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._private_key = ec.generate_private_key(ec.SECP256R1())
        self._public_key = self._private_key.public_key()

    def sign(self, message: bytes) -> bytes:
        """Sign a message with agent's private key."""
        return self._private_key.sign(message, ec.ECDSA(hashes.SHA256()))

    def verify(self, message: bytes, signature: bytes, public_key) -> bool:
        """Verify a signature against a public key."""
        try:
            public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
            return True
        except:
            return False

    def export_public_key(self) -> str:
        """Export public key for sharing."""
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
```

**Priority**: LOW (deferred to GAD-1000 implementation phase)

---

## Impact on OPUS Documents

### OPUS-001 (Memory Migration)
- **Impact**: Must ensure ledger queries return structured data
- **Add**: `ledger.get_events_json()` method

### OPUS-002 (Phoenix Config)
- **Impact**: Already mostly compliant ✅
- **Add**: Document GAD-000 compliance in config schema

### OPUS-003 (AOS Repair)
- **Impact**: UI rendering must have JSON alternative
- **Add**: `renderer.generate_content_json()` for each renderer

### OPUS-004 (Boot Audit)
- **Impact**: Boot errors must be structured
- **Add**: Boot validation returns StructuredError on failure

### OPUS-005 (Unification)
- **Impact**: Phase 5 (UnifiedTrace) is THE solution for Test 2
- **Add**: UnifiedTrace must emit JSON events, not logs

---

## Implementation Priority

### Phase A: Critical (Test 2+3) - Do First

| Task | Effort | Impact |
|------|--------|--------|
| Add `kernel.get_system_status()` | LOW | HIGH |
| Create `StructuredError` class | LOW | HIGH |
| Update error handling in executors | MEDIUM | HIGH |

### Phase B: Important (Test 1+4+5)

| Task | Effort | Impact |
|------|--------|--------|
| Add `kernel.get_capabilities()` | LOW | MEDIUM |
| Ensure all methods return dict | MEDIUM | MEDIUM |
| Add idempotency keys | MEDIUM | MEDIUM |

### Phase C: Future (Test 6)

| Task | Effort | Impact |
|------|--------|--------|
| Implement GAD-1000 identity | HIGH | HIGH |
| ECDSA key management | HIGH | HIGH |

---

## Verification Script

```python
# scripts/verify_gad000_compliance.py
"""GAD-000 Compliance Verification Script."""

def test_discoverability(kernel):
    """Test 1: Can AI discover capabilities?"""
    caps = kernel.get_capabilities()
    assert "available_methods" in caps
    assert "registered_agents" in caps
    return True

def test_observability(kernel):
    """Test 2: Can AI see system state?"""
    status = kernel.get_system_status()
    assert "kernel_status" in status
    assert "queue" in status
    assert "agents" in status
    return True

def test_parseability(kernel):
    """Test 3: Are errors machine-readable?"""
    try:
        kernel.submit_task(None)  # Force error
    except StructuredError as e:
        assert hasattr(e, 'code')
        assert hasattr(e, 'retry_safe')
        return True
    return False

def test_composability(kernel):
    """Test 4: Do outputs match input schemas?"""
    result = kernel.envoy.execute_circuit("SYSTEM_STATUS_V2", {})
    assert isinstance(result, dict)
    assert "status" in result
    return True

def test_idempotency(kernel):
    """Test 5: Can AI safely retry?"""
    from vibe_core import Task
    task = Task(agent_id="envoy", payload={"command": "status"})

    r1 = kernel.scheduler.submit_task(task, idempotency_key="test-123")
    r2 = kernel.scheduler.submit_task(task, idempotency_key="test-123")

    assert r2["status"] == "already_completed"
    return True

def test_identity(kernel):
    """Test 6: Cryptographic verification (FUTURE)."""
    # Skip until GAD-1000 implementation
    return None  # Not yet implemented

def run_all_tests():
    from vibe_core.kernel_impl import RealVibeKernel
    kernel = RealVibeKernel(ledger_path=':memory:')
    kernel.boot()

    results = {
        "discoverability": test_discoverability(kernel),
        "observability": test_observability(kernel),
        "parseability": test_parseability(kernel),
        "composability": test_composability(kernel),
        "idempotency": test_idempotency(kernel),
        "identity": test_identity(kernel)
    }

    passed = sum(1 for v in results.values() if v is True)
    total = sum(1 for v in results.values() if v is not None)

    print(f"GAD-000 Compliance: {passed}/{total} tests passed")
    return results
```

---

## Success Criteria

| Test | Current | Target | Deadline |
|------|---------|--------|----------|
| 1. Discoverability | ⚠️ | ✅ | Phase B |
| 2. Observability | ❌ | ✅ | Phase A |
| 3. Parseability | ❌ | ✅ | Phase A |
| 4. Composability | ⚠️ | ✅ | Phase B |
| 5. Idempotency | ⚠️ | ✅ | Phase B |
| 6. Identity | ❌ | ⚠️ | Phase C |

**GAD-000 Compliance Score Target**: 5/6 (Test 6 deferred to GAD-1000)

---

## Related Documents

- **GAD-000**: The Operator Inversion Principle (foundational law)
- **GAD-1000**: Identity Fusion (Test 6 implementation)
- **OPUS-005**: Unification Roadmap (Phase 5 = Test 2 solution)
- **OPUS-003**: AOS Foundation Repair (affected by Test 4)
