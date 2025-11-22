# STEWARD Protocol - Failure Mode Analysis

**Status:** ⚠️ DRAFT (TODO before v1.0.0)
**Last Updated:** 2025-11-21

---

## 🎯 PURPOSE

Document real-world failure scenarios and mitigation strategies to ensure protocol resilience.

**Principle:** Design for failure, not just success.

---

## 🚨 FAILURE MODE CATEGORIES

1. **Agent Failures** - Agent goes offline, crashes, or becomes unresponsive
2. **Network Failures** - Connection loss, timeouts, packet loss
3. **Attestation Failures** - Expired attestations, failed refreshes
4. **Trust Failures** - Gaming, Sybil attacks, reputation manipulation
5. **Registry Failures** - Registry downtime, data corruption, split-brain
6. **Security Failures** - Key compromise, impersonation, man-in-the-middle

---

## 1️⃣ AGENT FAILURES

### Scenario 1.1: Agent Goes Offline Mid-Delegation

**Description:** Agent accepts task, starts execution, then crashes/network fails.

```
Client → Agent: delegate task-abc123
Agent: ✅ Accepted (started execution)
[... Agent crashes after 50% completion ...]
Client: ⏳ Waiting for results... (timeout after 10min)
```

**Impact:**
- Client loses results of partial work
- Resources wasted (no partial artifacts recovered)
- Client uncertain if task completed

**Mitigation:**

```json
{
  "delegation": {
    "checkpointing": {
      "enabled": true,
      "checkpoint_interval_ms": 60000,  // Every 60s
      "checkpoint_storage": "./checkpoints/task-abc123/"
    },

    "on_agent_failure": {
      "action": "recover_from_checkpoint",
      "recovery_agent": "fallback-agent-id",  // Optional
      "max_recovery_attempts": 2
    }
  }
}
```

**Recovery Workflow:**
```bash
# 1. Client detects agent offline
$ steward monitor task-abc123
❌ Agent offline (last heartbeat: 5min ago)

# 2. Client attempts recovery
$ steward recover task-abc123 --from-checkpoint

Recovering from checkpoint...
  ├─ Last checkpoint: 50% complete (4min ago)
  ├─ Artifacts recovered: architecture.md, partial code/
  └─ Resuming from CODING phase...

# 3. Fallback to different agent (optional)
$ steward delegate fallback-agent-id \
    --resume-from task-abc123 \
    --checkpoint ./checkpoints/task-abc123/

✅ Task resumed on fallback agent
```

---

### Scenario 1.2: Agent Returns Corrupted Results

**Description:** Agent completes task but returns invalid/corrupted artifacts.

```
Agent → Client: ✅ Task complete (artifacts.zip)
Client: Downloads artifacts.zip
Client: Extracts... ❌ Corrupted files (invalid JSON, incomplete code)
```

**Mitigation:**

```json
{
  "delegation": {
    "result_validation": {
      "checksum_required": true,
      "schema_validation": true,
      "content_validation": {
        "json_files": "validate_json_syntax",
        "code_files": "lint_and_parse",
        "markdown_files": "validate_markdown"
      }
    },

    "on_invalid_result": {
      "action": "reject_and_retry",
      "notify_agent": true,
      "report_issue": true
    }
  }
}
```

**Validation Example:**
```python
def validate_result(artifacts: Dict[str, bytes]) -> bool:
    """
    Validate all artifacts before accepting.
    """
    for filename, content in artifacts.items():
        # Check checksum
        if not verify_checksum(content, expected_checksums[filename]):
            raise ValidationError(f"Checksum mismatch: {filename}")

        # Validate content based on file type
        if filename.endswith(".json"):
            json.loads(content)  // Throws if invalid JSON

        if filename.endswith(".py"):
            ast.parse(content)  // Throws if invalid Python

    return True
```

---

## 2️⃣ NETWORK FAILURES

### Scenario 2.1: Connection Lost During Delegation

**Description:** Client loses network mid-request, uncertain if delegation succeeded.

```
Client → Agent: delegate task-abc123
[NETWORK ERROR - did agent receive request?]

Options:
  1. Retry (risk: duplicate execution)
  2. Don't retry (risk: lost task)
  3. Check status first ✅
```

**Mitigation:** **Idempotency Keys** (see ERROR_HANDLING.md)

```bash
# Safe to retry with same idempotency key
$ steward delegate agent-id \
    --operation foo \
    --idempotency-key task-abc123

✅ If agent received request: returns existing task
✅ If agent didn't receive: creates new task
✅ No duplicate execution
```

---

### Scenario 2.2: Slow Network (High Latency)

**Description:** Network is slow, causing timeouts despite agent being responsive.

**Mitigation:**

```json
{
  "delegation": {
    "adaptive_timeouts": {
      "enabled": true,
      "initial_timeout_ms": 120000,
      "measure_latency": true,

      "on_slow_network": {
        "action": "extend_timeout",
        "timeout_multiplier": 2.0,  // Double timeout
        "max_timeout_ms": 600000
      }
    }
  }
}
```

**Latency Measurement:**
```bash
$ steward delegate agent-id --operation foo --adaptive-timeout

Measuring network latency...
  ├─ Ping: 250ms
  ├─ Health check RTT: 500ms
  └─ Adjusted timeout: 240s (doubled from 120s)

Submitting delegation with extended timeout...
```

---

## 3️⃣ ATTESTATION FAILURES

### Scenario 3.1: Attestation Expired, Refresh Failed

**Description:** Agent's attestation expired, CI/CD is down, can't refresh.

```
Client: Discover agent with "orchestrate_sdlc"
Registry: Found vibe-agency-orchestrator
Client: Verify agent
Registry: ⚠️  Attestation expired 3h ago

Client: Request refresh
Agent: ❌ CI/CD down (GitHub Actions outage)
```

**Mitigation:**

```json
{
  "attestation_policy": {
    "on_expired_attestation": {
      "action": "use_last_known_good",
      "grace_period_hours": 48,  // 2 days after expiry

      "warnings": [
        "⚠️  Attestation expired (3h ago)",
        "Using last known good attestation (within grace period)",
        "Health check: ✅ PASSED (agent responsive)"
      ],

      "require_explicit_acceptance": true  // Client must --accept-expired
    }
  }
}
```

**Client Workflow:**
```bash
$ steward verify agent-id

⚠️  WARNING: Attestation expired 3h ago
⚠️  Last known good attestation: 2025-11-21T08:00:00Z (27h ago)
✅ Health check passed (agent responsive)
✅ Within grace period (48h)

Options:
  1. Wait for automatic refresh (next attempt: 15min)
  2. Accept risk: steward delegate --accept-expired
  3. Abort delegation
```

---

### Scenario 3.2: Attestation Refresh Causes Test Failures

**Description:** Agent updates code, tests fail, can't generate fresh attestation.

```
Agent: Auto-refresh attestation (scheduled 6h)
Agent: Run tests... ❌ 12 tests failing (regression introduced)
Agent: Cannot generate valid attestation
```

**Mitigation:**

```json
{
  "attestation_policy": {
    "on_test_failure": {
      "action": "extend_previous_attestation",
      "max_extensions": 3,
      "extension_duration_hours": 6,

      "alert_owner": true,
      "mark_as_degraded": true,  // Show in registry
      "prevent_new_delegations": false  // Still allow (but with warning)
    }
  }
}
```

**Registry Display:**
```bash
$ steward discover --capability orchestrate_sdlc

Found 1 agent:
  vibe-agency-orchestrator v4.0.0 ⚠️  DEGRADED
  - Attestation: Extended (test failures detected)
  - Tests: 369/383 passing (12 failures)
  - Last verified: 6h ago
  - Status: Available (with degraded quality)
```

---

## 4️⃣ TRUST FAILURES

### Scenario 4.1: Trust Score Gaming (Fake Endorsements)

**Description:** Agent creates fake agents to endorse itself (Sybil attack).

```
Attacker: Create 100 fake agents
Fake Agents → Attacker's Agent: Endorse (100 endorsements)
Attacker's Agent: Trust score artificially inflated
```

**Detection:**

```python
def detect_sybil_attack(agent: Agent) -> bool:
    """
    Check for suspicious endorsement patterns.
    """
    checks = {
        # All endorsers created recently
        "new_endorsers": all(
            (now - e.created_date).days < 30
            for e in agent.endorsers
        ),

        # Endorsers have no other activity
        "inactive_endorsers": sum(
            e.total_delegations == 0
            for e in agent.endorsers
        ) > len(agent.endorsers) * 0.8,

        # Circular endorsements (A→B, B→A)
        "circular": has_circular_endorsements(agent.endorsers),

        # Similar key fingerprints (same creator)
        "similar_keys": has_similar_fingerprints(agent.endorsers),
    }

    return sum(checks.values()) >= 2  // 2+ red flags
```

**Mitigation:**
```yaml
registry_policy:
  endorsement_validation:
    - min_endorser_age_days: 30
    - min_endorser_delegations: 10
    - max_endorsements_per_endorser_per_month: 5
    - detect_circular_endorsements: true

  penalties:
    - sybil_detected: ban_agent + ban_all_endorsers
```

---

### Scenario 4.2: Test Coverage Gaming (Cherry-Picking)

**Description:** Agent runs tests multiple times, only reports passing runs.

```
Agent: Run tests (attempt 1) → 350/383 passing ❌
Agent: Run tests (attempt 2) → 365/383 passing ❌
Agent: Run tests (attempt 3) → 369/383 passing ✅ (report this!)
```

**Detection:**

```yaml
attestation_validation:
  test_determinism:
    - run_tests_multiple_times: 3
    - require_consistent_results: true
    - max_variance_percent: 2  # Allow 2% variance for flaky tests

  on_inconsistent_results:
    - reject_attestation: true
    - flag_for_review: true
    - investigate_flaky_tests: true
```

**Example:**
```bash
$ steward attest --capability orchestrate_sdlc

Running tests (attempt 1/3)... 369/383 passing
Running tests (attempt 2/3)... 371/383 passing
Running tests (attempt 3/3)... 368/383 passing

⚠️  Variance detected: 368-371 (0.8% variance - ACCEPTABLE)
✅ Tests are reasonably deterministic

Attestation generated.
```

---

## 5️⃣ REGISTRY FAILURES

### Scenario 5.1: Registry Downtime

**Description:** Central registry is down, agents can't be discovered.

```
Client: steward discover --capability foo
Client: ❌ Error: Registry unavailable (connection timeout)
```

**Mitigation:** **Fallback Registries**

```json
{
  "discovery": {
    "registries": [
      {
        "url": "https://steward-registry.org",
        "priority": 1,
        "timeout_ms": 5000
      },
      {
        "url": "https://backup-registry.steward.io",
        "priority": 2,
        "timeout_ms": 5000
      },
      {
        "url": "github:steward-protocol/agent-registry",  // Git-based fallback
        "priority": 3,
        "timeout_ms": 30000
      }
    ],

    "on_registry_failure": {
      "action": "try_next_registry",
      "cache_results": true,
      "cache_ttl_hours": 24
    }
  }
}
```

**Fallback Workflow:**
```bash
$ steward discover --capability orchestrate_sdlc

Trying registry: https://steward-registry.org...
❌ Timeout (5s)

Trying registry: https://backup-registry.steward.io...
❌ Connection refused

Trying registry: github:steward-protocol/agent-registry...
✅ Success (cloned git repository)

Found 1 agent (cached for 24h):
  vibe-agency-orchestrator v4.0.0
```

---

### Scenario 5.2: Registry Poisoning (Typosquatting)

**Description:** Attacker publishes malicious agent with similar name.

```
Legitimate: vibe-agency-orchestrator
Malicious:  vibe-agency-orchestratοr  (greek omicron)
```

**Detection:**

```python
def check_typosquatting(new_agent_id: str) -> List[Alert]:
    """
    Detect potential typosquatting/homograph attacks.
    """
    alerts = []

    for existing in registry:
        # Levenshtein distance
        if levenshtein_distance(new_agent_id, existing.id) <= 2:
            alerts.append(Alert(
                type="similar_name",
                existing=existing.id,
                similarity=0.95
            ))

        # Homograph attack (unicode lookalikes)
        if has_homograph(new_agent_id, existing.id):
            alerts.append(Alert(
                type="homograph_attack",
                existing=existing.id,
                characters=get_suspicious_chars(new_agent_id)
            ))

    return alerts
```

**Registry Policy:**
```yaml
submission_validation:
  - check_typosquatting: true
  - require_manual_review_if_similar: true
  - block_unicode_lookalikes: true
  - verified_namespace_prefix: true  # "verified/vibe-agency-orchestrator"
```

---

## 6️⃣ SECURITY FAILURES

### Scenario 6.1: Key Compromise

**Description:** Agent's private key is stolen/leaked.

```
Attacker: Obtains private key (leaked in commit, stolen from dev machine)
Attacker: Signs malicious attestations with stolen key
Attacker: Impersonates agent
```

**Detection:**

```yaml
security_monitoring:
  alerts:
    - unusual_signing_activity:
        - signing_from_unexpected_ip
        - high_frequency_signing
        - signing_outside_business_hours

    - suspicious_attestations:
        - test_coverage_suddenly_improved
        - capabilities_added_without_code_changes
        - attestations_from_multiple_locations

  automated_response:
    - suspend_agent
    - revoke_key
    - notify_owner
```

**Recovery Workflow:**
```bash
# 1. Owner detects compromise
$ steward security-alert vibe-agency-orchestrator

⚠️  SECURITY ALERT
- Unusual signing activity detected
- Attestation signed from unknown IP: 203.0.113.42
- Last 10 signatures from: 198.51.100.10

Recommended action: Revoke key immediately

# 2. Owner revokes compromised key
$ steward revoke-key sha256:abc123... \
    --reason key_compromise \
    --immediate

✅ Key revoked immediately
✅ All attestations invalidated
✅ Agent suspended from registry

# 3. Owner generates new key + re-attests
$ steward keygen --rotate
$ steward attest --all-capabilities
$ steward publish

✅ Agent reactivated with new key
```

---

### Scenario 6.2: Man-in-the-Middle Attack

**Description:** Attacker intercepts client-agent communication.

```
Client → [Attacker Proxy] → Agent
         (modifies delegation payload)
```

**Mitigation:** **Mutual TLS + Signature Verification**

```json
{
  "delegation": {
    "security": {
      "require_tls": true,
      "require_mutual_tls": true,  // Both client & agent authenticate
      "verify_agent_certificate": true,
      "pin_agent_public_key": true  // Public key pinning
    },

    "payload_signing": {
      "sign_request": true,  // Client signs delegation payload
      "sign_response": true,  // Agent signs result
      "verify_signatures": true
    }
  }
}
```

**Protection:**
- TLS prevents eavesdropping
- Mutual TLS prevents impersonation
- Request/response signing prevents tampering

---

## ✅ PRODUCTION READINESS CHECKLIST

### Before v1.0.0

- [ ] Agent failure recovery (checkpointing + resume)
- [ ] Result validation (checksums + schema validation)
- [ ] Idempotency keys (prevent duplicate execution)
- [ ] Adaptive timeouts (handle slow networks)
- [ ] Attestation grace period (expired but recent)
- [ ] Sybil attack detection (fake endorsements)
- [ ] Test determinism validation (anti-gaming)
- [ ] Registry fallbacks (downtime resilience)
- [ ] Typosquatting detection (registry poisoning)
- [ ] Key compromise monitoring (security alerts)
- [ ] MITM protection (mutual TLS + signing)

### Failure Mode Testing

- [ ] Simulate agent crash mid-delegation
- [ ] Simulate network loss during delegation
- [ ] Simulate CI/CD outage (attestation refresh failure)
- [ ] Simulate Sybil attack (fake endorsements)
- [ ] Simulate registry downtime (fallback testing)
- [ ] Simulate key compromise (revocation workflow)
- [ ] Chaos engineering tests (random failures)

---

## 📚 REFERENCES

- **Chaos Engineering:** Netflix's Chaos Monkey
- **Failure Mode Analysis:** FMEA (Failure Mode and Effects Analysis)
- **Resilience Patterns:** Microsoft Azure Well-Architected Framework
- **Byzantine Fault Tolerance:** Practical BFT (Castro & Liskov)

---

**Status:** ⚠️ DRAFT - Implementation required before v1.0.0
**Critical:** Failure modes must be tested, not just documented
