# STEWARD Protocol - Error Handling

**Status:** ⚠️ DRAFT (TODO before v1.0.0)
**Last Updated:** 2025-11-21

---

## 🎯 ERROR HANDLING PRINCIPLES

1. **Fail Fast, Recover Gracefully** - Detect errors immediately, provide clear recovery paths
2. **Explicit Retry Policies** - Never silently retry, always configurable
3. **Partial Success Support** - Not all-or-nothing, support incremental progress
4. **Compensation Strategies** - Rollback or compensate when failures occur
5. **Observable Failures** - All errors logged, traceable, debuggable

---

## 🔄 RETRY POLICIES

### Configuration

```json
{
  "delegation": {
    "retry_policy": {
      "enabled": true,
      "max_retries": 3,
      "backoff_strategy": "exponential",  // "fixed", "exponential", "linear"
      "initial_delay_ms": 1000,
      "max_delay_ms": 60000,
      "retry_on": [
        "timeout",
        "transient_error",
        "rate_limit_exceeded",
        "agent_temporarily_unavailable"
      ],
      "do_not_retry_on": [
        "invalid_input",
        "capability_not_found",
        "attestation_expired",
        "authentication_failure"
      ]
    }
  }
}
```

### Backoff Strategies

#### 1. Exponential Backoff (Recommended)

```python
def calculate_delay(attempt: int, initial_delay: int, max_delay: int) -> int:
    """
    Exponential backoff: 1s, 2s, 4s, 8s, 16s, ...
    """
    delay = initial_delay * (2 ** attempt)
    return min(delay, max_delay)

# Example:
# Attempt 1: 1000ms
# Attempt 2: 2000ms
# Attempt 3: 4000ms
# Attempt 4: 8000ms (capped at max_delay)
```

#### 2. Jittered Exponential Backoff (Best for distributed systems)

```python
import random

def calculate_delay_jitter(attempt: int, initial_delay: int, max_delay: int) -> int:
    """
    Add randomness to avoid thundering herd problem.
    """
    base_delay = initial_delay * (2 ** attempt)
    jitter = random.uniform(0, base_delay * 0.3)  // 30% jitter
    return min(base_delay + jitter, max_delay)

# Example:
# Attempt 1: 1000ms + [0-300ms] = 1000-1300ms
# Attempt 2: 2000ms + [0-600ms] = 2000-2600ms
```

### Retry Logic Example

```bash
$ steward delegate vibe-agency-orchestrator \
    --operation orchestrate_sdlc \
    --retry-policy exponential \
    --max-retries 3

Submitting delegation...
❌ Attempt 1 failed: Agent temporarily unavailable (503)
⏳ Retrying in 1.2s... (1/3)

❌ Attempt 2 failed: Timeout after 30s
⏳ Retrying in 2.5s... (2/3)

✅ Attempt 3 succeeded
Task ID: task-abc123
Duration: 45s (including 2 retries)
```

---

## ✅ PARTIAL SUCCESS HANDLING

### Scenario: Multi-Step Operation

```json
{
  "operation": "orchestrate_sdlc",
  "steps": [
    {"phase": "PLANNING", "status": "completed", "artifacts": ["architecture.md"]},
    {"phase": "CODING", "status": "completed", "artifacts": ["src/"]},
    {"phase": "TESTING", "status": "failed", "error": "Unit tests failed (12/150)"},
    {"phase": "DEPLOYMENT", "status": "not_started"},
    {"phase": "MAINTENANCE", "status": "not_started"}
  ],

  "partial_success": {
    "enabled": true,
    "min_success_rate": 0.6,  // 60% of steps must succeed
    "actual_success_rate": 0.4,  // 2/5 = 40%
    "result": "partial_failure"
  }
}
```

### Configuration

```json
{
  "delegation": {
    "partial_success": {
      "allowed": true,
      "min_success_rate": 0.8,  // 80% of sub-tasks must succeed

      "on_partial_success": {
        "action": "return_partial_results",  // or "fail_entire_operation"
        "include_failed_steps": true,
        "include_error_details": true
      },

      "on_threshold_not_met": {
        "action": "fail",  // or "retry_failed_steps"
        "retry_failed_steps": true,
        "max_step_retries": 2
      }
    }
  }
}
```

### Usage Example

```bash
$ steward delegate vibe-agency-orchestrator \
    --operation orchestrate_sdlc \
    --allow-partial-success \
    --min-success-rate 0.8

Executing operation...
  [████████████████████] PLANNING: ✅ SUCCESS (2m 15s)
  [████████████████████] CODING: ✅ SUCCESS (4m 32s)
  [████████░░░░░░░░░░░░] TESTING: ❌ FAILED (12 unit tests failing)
  [░░░░░░░░░░░░░░░░░░░░] DEPLOYMENT: ⏸️  SKIPPED (dependency failed)
  [░░░░░░░░░░░░░░░░░░░░] MAINTENANCE: ⏸️  SKIPPED (dependency failed)

⚠️  Partial Success: 2/5 steps completed (40%)
❌ Below minimum threshold (80% required)

Options:
  1. Accept partial results: steward accept-partial task-abc123
  2. Retry failed steps: steward retry-failed task-abc123
  3. Rollback: steward rollback task-abc123
  4. Abandon: steward abandon task-abc123
```

---

## 🔄 COMPENSATION STRATEGIES

### 1. Rollback (Undo Changes)

```json
{
  "delegation": {
    "compensation": {
      "strategy": "rollback",
      "on_failure": "undo_all_changes",

      "rollback_steps": [
        {
          "phase": "CODING",
          "action": "delete_generated_files",
          "files": ["src/**/*.py"]
        },
        {
          "phase": "PLANNING",
          "action": "delete_artifacts",
          "artifacts": ["architecture.md", "requirements.md"]
        }
      ]
    }
  }
}
```

**Usage:**
```bash
$ steward delegate vibe-agency-orchestrator \
    --operation orchestrate_sdlc \
    --on-failure rollback

❌ Operation failed at TESTING phase
🔄 Rolling back changes...
  ├─ Deleted src/**/*.py (CODING phase)
  ├─ Deleted architecture.md (PLANNING phase)
  └─ Deleted requirements.md (PLANNING phase)

✅ Rollback complete
✅ System restored to pre-delegation state
```

### 2. Compensate (Opposite Operation)

```json
{
  "delegation": {
    "compensation": {
      "strategy": "compensate",
      "compensation_operations": [
        {
          "phase": "DEPLOYMENT",
          "compensation": "undeploy",
          "script": "./scripts/undeploy.sh"
        },
        {
          "phase": "DATABASE_MIGRATION",
          "compensation": "migrate_down",
          "script": "./scripts/migrate_down.sh"
        }
      ]
    }
  }
}
```

**Usage:**
```bash
$ steward delegate deployment-agent \
    --operation deploy_to_production \
    --on-failure compensate

✅ Step 1: Deploy app (SUCCESS)
✅ Step 2: Migrate database (SUCCESS)
❌ Step 3: Update load balancer (FAILED: Connection timeout)

🔄 Compensating...
  ├─ Running migrate_down.sh (undo database migration)
  └─ Running undeploy.sh (remove deployed app)

✅ Compensation complete
✅ System in consistent state
```

### 3. Keep Partial Results (Manual Cleanup)

```json
{
  "delegation": {
    "compensation": {
      "strategy": "keep_partial",
      "rationale": "Partial results may be valuable for debugging",

      "cleanup_instructions": {
        "manual_steps": [
          "Review generated code in src/",
          "Delete if not needed",
          "Run tests manually to verify state"
        ],
        "automated_cleanup": "./scripts/cleanup_partial.sh"
      }
    }
  }
}
```

---

## 🚨 ERROR CATEGORIES

### 1. Transient Errors (Retry Recommended)

```json
{
  "error_categories": {
    "transient": {
      "codes": [
        "timeout",
        "rate_limit_exceeded",
        "agent_temporarily_unavailable",
        "network_error",
        "internal_server_error"
      ],
      "retry": true,
      "backoff": "exponential"
    }
  }
}
```

### 2. Permanent Errors (Do Not Retry)

```json
{
  "error_categories": {
    "permanent": {
      "codes": [
        "invalid_input",
        "capability_not_found",
        "attestation_expired",
        "authentication_failure",
        "insufficient_permissions"
      ],
      "retry": false,
      "action": "return_error_immediately"
    }
  }
}
```

### 3. Ambiguous Errors (Retry with Idempotency Check)

```json
{
  "error_categories": {
    "ambiguous": {
      "codes": [
        "connection_lost_mid_operation",
        "partial_response_received"
      ],
      "retry": true,
      "idempotency_check": true,  // Check if operation actually succeeded
      "check_method": "query_task_status"
    }
  }
}
```

---

## 🔍 ERROR RESPONSE FORMAT

### Standard Error Response

```json
{
  "error": {
    "code": "attestation_expired",
    "message": "Capability 'orchestrate_sdlc' attestation expired 3h ago",
    "category": "permanent",
    "retry_recommended": false,

    "details": {
      "capability": "orchestrate_sdlc",
      "attested_date": "2025-11-20T10:00:00Z",
      "expired_date": "2025-11-21T10:00:00Z",
      "current_time": "2025-11-21T13:00:00Z"
    },

    "recovery_suggestions": [
      "Request fresh attestation: steward refresh-attestation vibe-agency-orchestrator",
      "Accept risk and delegate with --accept-expired flag",
      "Wait for automatic attestation refresh (next: 2025-11-21T14:00:00Z)"
    ],

    "documentation": "https://steward-protocol.org/errors/attestation_expired"
  }
}
```

### Nested Errors (Multi-Step Operations)

```json
{
  "error": {
    "code": "partial_failure",
    "message": "Operation completed with failures",
    "category": "partial_success",

    "steps": [
      {
        "phase": "PLANNING",
        "status": "success",
        "duration_ms": 135000
      },
      {
        "phase": "CODING",
        "status": "success",
        "duration_ms": 272000
      },
      {
        "phase": "TESTING",
        "status": "failed",
        "error": {
          "code": "unit_tests_failed",
          "message": "12 unit tests failed",
          "details": {
            "total_tests": 150,
            "passed": 138,
            "failed": 12,
            "test_failures": [
              "test_authentication.py::test_login_with_invalid_credentials",
              "test_api.py::test_rate_limiting",
              // ...
            ]
          }
        }
      }
    ],

    "success_rate": 0.4,  // 2/5 steps
    "min_required": 0.8,  // 80% threshold

    "recovery_suggestions": [
      "Retry failed steps: steward retry-failed task-abc123",
      "Accept partial results: steward accept-partial task-abc123",
      "Rollback all changes: steward rollback task-abc123"
    ]
  }
}
```

---

## ⏱️ TIMEOUT HANDLING

### Configuration

```json
{
  "delegation": {
    "timeouts": {
      "operation_timeout_ms": 600000,  // 10 minutes for entire operation
      "step_timeout_ms": 120000,  // 2 minutes per step
      "health_check_timeout_ms": 5000,  // 5 seconds for health check

      "on_timeout": {
        "action": "retry",  // or "fail" or "extend_timeout"
        "retry_with_longer_timeout": true,
        "timeout_multiplier": 1.5
      }
    }
  }
}
```

### Progressive Timeout Extension

```python
def handle_timeout(attempt: int, base_timeout: int) -> int:
    """
    Extend timeout on retry (agent might be under load).
    """
    return base_timeout * (1.5 ** attempt)

# Example:
# Attempt 1: 600000ms (10min)
# Attempt 2: 900000ms (15min)
# Attempt 3: 1350000ms (22.5min)
```

---

## 🔄 IDEMPOTENCY

### Problem: Ambiguous Failures

```
Client → Agent: delegate task
Client → Agent: ...waiting...
[NETWORK ERROR - did task complete?]

Options:
  1. Retry (risk: duplicate execution)
  2. Don't retry (risk: lost task)
  3. Check status first (idempotent retry) ✅
```

### Solution: Idempotency Keys

```json
{
  "delegation": {
    "idempotency_key": "task-abc123-attempt-1",
    "operation": "orchestrate_sdlc",
    "context": {...}
  }
}
```

**Agent behavior:**
```python
def handle_delegation(request):
    idempotency_key = request["idempotency_key"]

    # Check if already processed
    if exists_in_cache(idempotency_key):
        return get_cached_result(idempotency_key)

    # Process request
    result = execute_operation(request)

    # Cache result (TTL: 24h)
    cache_result(idempotency_key, result, ttl=86400)

    return result
```

**Client behavior:**
```bash
$ steward delegate vibe-agency-orchestrator \
    --operation orchestrate_sdlc \
    --idempotency-key task-abc123

Connection lost mid-operation...

# Safe to retry with same idempotency key
$ steward delegate vibe-agency-orchestrator \
    --operation orchestrate_sdlc \
    --idempotency-key task-abc123  # Same key!

✅ Operation already completed (returned cached result)
✅ No duplicate execution
```

---

## 📊 ERROR MONITORING

### Required Metrics

```yaml
metrics:
  error_rates:
    - total_errors_per_minute
    - errors_by_category (transient, permanent, ambiguous)
    - errors_by_code (timeout, auth_failure, etc.)

  retry_metrics:
    - retry_success_rate
    - average_retries_until_success
    - operations_exhausting_retries

  latency:
    - p50_latency (median)
    - p95_latency
    - p99_latency
    - max_latency

alerts:
  - error_rate_spike: >10% increase in 5min
  - retry_exhaustion: >20% operations failing after max retries
  - high_latency: p99 latency >60s
```

---

## ✅ PRODUCTION READINESS CHECKLIST

### Before v1.0.0

- [ ] Retry policies implemented (exponential backoff with jitter)
- [ ] Partial success handling (configurable thresholds)
- [ ] Compensation strategies (rollback, compensate, keep partial)
- [ ] Error categorization (transient, permanent, ambiguous)
- [ ] Idempotency support (idempotency keys + caching)
- [ ] Timeout handling (progressive extension)
- [ ] Standard error response format
- [ ] Error monitoring & alerting
- [ ] Documentation for all error codes
- [ ] End-to-end error handling tests

---

## 📚 REFERENCES

- **Retry Logic:** Google Cloud Retry Strategy Best Practices
- **Idempotency:** Stripe API Design (Idempotent Requests)
- **Compensation:** Saga Pattern (Chris Richardson)
- **Error Handling:** Microsoft REST API Guidelines

---

**Status:** ⚠️ DRAFT - Implementation required before v1.0.0
**Critical:** Error handling is non-negotiable for production reliability
