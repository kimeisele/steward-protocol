# STEWARD Protocol - Usage Examples

**Version:** 0.1.0-draft
**Date:** 2025-11-21

---

## 🎯 EXAMPLE 1: Agent Discovery & Verification

### Scenario: Planning Agent needs SDLC orchestration

```bash
# Step 1: Discover agents with SDLC capability
$ steward discover --capability "orchestrate_sdlc" --min-trust-score 0.9

Found 2 agents:
┌──────────────────────────────┬─────────┬────────────┬─────────┐
│ Agent ID                     │ Version │ Trust Score│ Uptime  │
├──────────────────────────────┼─────────┼────────────┼─────────┤
│ vibe-agency-orchestrator     │ 4.0.0   │ 0.96       │ 100%    │
│ acme-sdlc-bot                │ 2.1.0   │ 0.91       │ 99.5%   │
└──────────────────────────────┴─────────┴────────────┴─────────┘

# Step 2: Get detailed info
$ steward info vibe-agency-orchestrator

Agent: vibe-agency-orchestrator v4.0.0
Class: orchestration_operator
Specialization: sdlc_management
Status: ACTIVE

Capabilities:
  - orchestrate_sdlc (attested 2h ago)
  - delegate_to_specialist (attested 2h ago)
  - execute_playbook (attested 2h ago)

Quality Metrics:
  - Test coverage: 96%
  - Uptime: 100%
  - Latency P99: 5000ms

Last attestation: 2025-11-21T08:00:00Z (valid for 24h)

# Step 3: Verify identity
$ steward verify vibe-agency-orchestrator

✅ Identity verified
✅ Signature valid (sha256:vibe-agency:gad-000:operator-inversion)
✅ Capabilities attested (2h ago)
✅ Tests passing: 369/383 (96%)
✅ Trust score: 0.96

Ready for delegation.

# Step 4: Check if attestation is fresh
$ steward attestation-status vibe-agency-orchestrator

Capability: orchestrate_sdlc
  - Attested: 2025-11-21T08:00:00Z
  - Expires: 2025-11-22T08:00:00Z
  - Time remaining: 22h 15m
  - Status: ✅ VALID

Health check: ✅ HEALTHY (verified 30s ago)
```

---

## 🎯 EXAMPLE 2: Task Delegation

### Scenario: Delegate restaurant app planning

```bash
# Delegate task with context
$ steward delegate vibe-agency-orchestrator \
  --operation orchestrate_sdlc \
  --context '{
    "domain": "restaurant",
    "business_type": "fast_casual",
    "scale": "multi_location",
    "integrations": ["pos_system", "delivery_apis"],
    "compliance": ["pci_dss", "gdpr"]
  }' \
  --constraints '{
    "min_test_coverage": 0.8,
    "max_latency_ms": 600000,
    "required_quality": 0.9
  }' \
  --timeout 600s \
  --callback https://my-agent.com/webhook/results

✅ Task submitted: task-f3a9b2c1
✅ Agent accepted: vibe-agency-orchestrator v4.0.0
⏱️  Expected completion: ~5-10 minutes

Monitor progress:
  steward monitor task-f3a9b2c1

View logs:
  steward logs task-f3a9b2c1

# Monitor task progress
$ steward monitor task-f3a9b2c1

Task: task-f3a9b2c1
Status: RUNNING
Agent: vibe-agency-orchestrator v4.0.0
Started: 2025-11-21T10:00:00Z
Elapsed: 4m 32s

Progress:
  [████████████████░░░░] 75% (Phase: PLANNING)

Current step: Generating architecture.md
  ├─ Requirements analysis: ✅ DONE
  ├─ Technology stack selection: ✅ DONE
  ├─ Architecture design: 🔄 IN PROGRESS (2m 15s)
  └─ Compliance check: ⏳ PENDING

Estimated time remaining: 1m 30s

# Get results when complete
$ steward result task-f3a9b2c1

Task: task-f3a9b2c1
Status: ✅ SUCCESS
Completed: 2025-11-21T10:06:12Z
Duration: 6m 12s

Artifacts:
  📄 architecture.md (12.3 KB)
  📄 requirements.md (8.7 KB)
  📄 project_manifest.json (2.1 KB)

Validation:
  ✅ Test coverage: 96% (exceeds minimum 80%)
  ✅ Quality score: 0.94 (exceeds minimum 0.9)
  ✅ Compliance checks: PASSED (PCI-DSS, GDPR)

Download artifacts:
  steward download task-f3a9b2c1 --output ./artifacts/

Audit trail:
  Task logged to VibeLedger (vibe_core/ledger.db)
  Execution ID: exec-abc123
```

---

## 🎯 EXAMPLE 3: Multi-Agent Collaboration

### Scenario: Healthcare platform with compliance validation

```bash
# Orchestrator delegates to multiple specialized agents

# 1. Architecture design (STEWARD)
$ steward delegate vibe-agency-orchestrator \
  --operation orchestrate_sdlc \
  --context '{"domain": "healthcare", "compliance": ["hipaa", "gdpr"]}' \
  --callback https://orchestrator.com/webhook/architecture
# → task-arch-001

# 2. Compliance validation (separate agent)
$ steward delegate hipaa-compliance-validator \
  --operation validate_compliance \
  --context '{"artifacts": ["architecture.md"], "standards": ["hipaa"]}' \
  --callback https://orchestrator.com/webhook/compliance
# → task-comp-001

# 3. Security review (separate agent)
$ steward delegate security-scanner \
  --operation security_audit \
  --context '{"artifacts": ["architecture.md"], "threat_model": true}' \
  --callback https://orchestrator.com/webhook/security
# → task-sec-001

# Monitor all tasks in parallel
$ steward monitor task-arch-001 task-comp-001 task-sec-001 --watch

┌──────────────────┬────────────┬──────────┬──────────┐
│ Task ID          │ Agent      │ Status   │ Progress │
├──────────────────┼────────────┼──────────┼──────────┤
│ task-arch-001    │ vibe-agency│ RUNNING  │ 65%      │
│ task-comp-001    │ hipaa-val  │ PENDING  │ -        │
│ task-sec-001     │ sec-scanner│ PENDING  │ -        │
└──────────────────┴────────────┴──────────┴──────────┘

# Wait for architecture to complete before compliance runs
# (task-comp-001 depends on artifacts from task-arch-001)
```

---

## 🎯 EXAMPLE 4: Agent Publishing & Attestation

### Scenario: Publishing a new agent to registry

```bash
# 1. Initialize agent manifest
$ steward init

Creating steward.json...
Agent ID: my-planning-agent
Name: My Planning Agent
Version: 1.0.0
Class: [orchestration_operator, task_executor, knowledge_agent, ...]: task_executor
Specialization: project_planning

✅ Created steward.json

# 2. Generate keypair
$ steward keygen --agent-id my-planning-agent

Generating RSA keypair...
✅ Private key: .steward/my-planning-agent_id_rsa (KEEP SECRET!)
✅ Public key: .steward/my-planning-agent_id_rsa.pub

Add to .gitignore:
  .steward/*_id_rsa

Publish public key:
  .steward/*_id_rsa.pub

# 3. Sign manifest
$ steward sign steward.json --key .steward/my-planning-agent_id_rsa

Signing steward.json...
✅ Signature: steward.json.sig
✅ Fingerprint: sha256:abc123...

Commit to repository:
  git add steward.json steward.json.sig .steward/*.pub
  git commit -m "Add STEWARD manifest"

# 4. Attest capabilities
$ steward attest --capability project_planning

Running capability attestation for 'project_planning'...
  ├─ Running test suite... ✅ 145/150 tests passing (96.7%)
  ├─ Checking dependencies... ✅ All dependencies satisfied
  ├─ Validating examples... ✅ 12/12 examples passing
  └─ Generating attestation certificate...

✅ Attestation: attestations/project_planning_2025-11-21.json
Valid until: 2025-11-22T10:00:00Z (24h)

# 5. Publish to registry
$ steward publish --registry github:my-org/agent-registry

Publishing my-planning-agent v1.0.0...
  ├─ Validating manifest... ✅
  ├─ Verifying signature... ✅
  ├─ Checking attestations... ✅ (1 capability attested)
  └─ Submitting to registry...

✅ Published: my-planning-agent v1.0.0
Registry: https://github.com/my-org/agent-registry
Discoverable in: ~5 minutes (registry sync)

Other agents can now discover your agent:
  steward discover --capability project_planning
```

---

## 🎯 EXAMPLE 5: Introspection & Runtime State

### Scenario: Query live agent state

```bash
# Check current runtime state (not static manifest)
$ steward introspect vibe-agency-orchestrator --live

Agent: vibe-agency-orchestrator v4.0.0
Status: ACTIVE
Uptime: 47 days, 13 hours

Current State:
  - Active tasks: 3
  - Queued tasks: 7
  - Completed today: 142
  - Success rate (24h): 98.6%

Resource Usage:
  - CPU: 12%
  - Memory: 2.3 GB / 8 GB (28%)
  - Disk: 45 GB / 100 GB (45%)

Test Status (last run: 2h ago):
  - Total: 383 tests
  - Passing: 369 (96.3%)
  - Failed: 4 (deployment workflow - known issue)
  - Duration: 47s

Health Checks:
  ✅ Kernel: HEALTHY
  ✅ Ledger: HEALTHY (last write: 3s ago)
  ✅ Specialists: 5/5 HEALTHY
  ✅ PlaybookEngine: HEALTHY

Last Attestation Refresh: 2025-11-21T08:00:00Z
Next Refresh: 2025-11-21T14:00:00Z (in 4h)

# Query specific capability status
$ steward capability-status vibe-agency-orchestrator orchestrate_sdlc

Capability: orchestrate_sdlc
Status: ✅ ATTESTED

Attestation:
  - Date: 2025-11-21T08:00:00Z
  - Expires: 2025-11-22T08:00:00Z
  - Remaining: 22h 15m
  - Certificate: attestations/orchestrate_sdlc_2025-11-21.json

Test Results:
  - test_orchestrate_planning: ✅ PASS
  - test_orchestrate_coding: ✅ PASS
  - test_orchestrate_testing: ✅ PASS
  - test_orchestrate_deployment: ⚠️  PARTIAL (4 tests failing)
  - test_orchestrate_maintenance: ✅ PASS

Quality Metrics:
  - Accuracy: 96%
  - Latency P99: 4823ms
  - Success rate (7d): 98.2%

Recent Usage:
  - Delegations today: 12
  - Successful: 11 (91.7%)
  - Failed: 1 (error: timeout after 600s)
```

---

## 🎯 EXAMPLE 6: Handling Stale Attestations

### Scenario: Attestation expired, request refresh

```bash
# Discover agent but attestation expired
$ steward discover --capability orchestrate_sdlc

Found 1 agent:
  vibe-agency-orchestrator v4.0.0 ⚠️  ATTESTATION EXPIRED (3h ago)

# Check attestation status
$ steward attestation-status vibe-agency-orchestrator

Capability: orchestrate_sdlc
  - Attested: 2025-11-20T10:00:00Z
  - Expired: 2025-11-21T10:00:00Z (3h ago)
  - Status: ⚠️  EXPIRED

⚠️  Warning: Attestation expired. Capability may have changed.

Options:
  1. Request fresh attestation: steward refresh-attestation vibe-agency-orchestrator
  2. Run health check: steward health vibe-agency-orchestrator
  3. Accept risk and delegate anyway: steward delegate --accept-expired

# Request fresh attestation
$ steward refresh-attestation vibe-agency-orchestrator

Requesting attestation refresh from vibe-agency-orchestrator...
  ├─ Contacting agent... ✅
  ├─ Agent running test suite... ⏳ (30-60s)
  └─ Generating new attestation...

✅ Attestation refreshed
New attestation: orchestrate_sdlc_2025-11-21.json
Valid until: 2025-11-22T13:30:00Z (24h)

Test results:
  - 369/383 tests passing (96.3%)
  - No regressions detected

You can now delegate safely.

# Alternatively, run quick health check
$ steward health vibe-agency-orchestrator

Running health check...
  ✅ Agent responding (latency: 42ms)
  ✅ All interfaces accessible
  ✅ Test suite: 369/383 passing (96.3%)
  ✅ No critical failures

Recommendation: Agent appears healthy despite expired attestation.
Consider delegating with caution or request full attestation refresh.
```

---

## 🎯 EXAMPLE 7: Trust Score & Reputation

### Scenario: Choosing between agents based on trust

```bash
# Search agents with trust metrics
$ steward discover --capability code_generation --show-trust

Found 4 agents:
┌──────────────────────┬─────────┬────────────┬──────────────────────┐
│ Agent ID             │ Version │ Trust Score│ Trust Factors        │
├──────────────────────┼─────────┼────────────┼──────────────────────┤
│ vibe-agency-coder    │ 3.2.0   │ 0.94       │ ⭐⭐⭐⭐⭐ (52 endorsements)│
│ acme-code-bot        │ 1.5.0   │ 0.87       │ ⭐⭐⭐⭐☆ (12 endorsements)│
│ quickcode-ai         │ 2.0.1   │ 0.72       │ ⭐⭐⭐☆☆ (3 endorsements) │
│ newbie-coder         │ 0.1.0   │ 0.45       │ ⭐⭐☆☆☆ (0 endorsements) │
└──────────────────────┴─────────┴────────────┴──────────────────────┘

# Get detailed trust breakdown
$ steward trust-score vibe-agency-coder

Agent: vibe-agency-coder v3.2.0
Overall Trust Score: 0.94 (⭐⭐⭐⭐⭐)

Trust Factors:
  ✅ Test Coverage: 0.96 (96% coverage) - Weight: 30%
  ✅ Uptime: 0.99 (99% uptime) - Weight: 20%
  ✅ Success Rate: 0.98 (98% successful delegations) - Weight: 25%
  ✅ Endorsements: 52 endorsements - Weight: 15%
  ✅ Attestation Freshness: 2h old - Weight: 10%

Recent Delegation History (last 30 days):
  - Total delegations: 1,247
  - Successful: 1,223 (98%)
  - Failed: 24 (2%)
    - Timeouts: 12
    - Quality gate failures: 8
    - System errors: 4

Endorsements:
  - external-planning-agent-1.0: "Excellent code quality"
  - project-manager-bot-2.1: "Fast and reliable"
  - security-validator-3.0: "Secure coding practices"
  [+49 more]

# Endorse an agent after successful delegation
$ steward endorse vibe-agency-coder --comment "Outstanding architecture work"

✅ Endorsement recorded
Your endorsement will be visible to other agents considering delegation.
```

---

## 🔄 COMPARISON: Before vs After STEWARD Protocol

### Before (Static STEWARD.md)
```bash
# Manual, error-prone process:
1. Read STEWARD.md (human interpretation)
2. Check if info is current (no way to verify)
3. Manually verify capabilities (trust, but verify?)
4. Hand-craft delegation payload
5. Hope for the best
```

### After (STEWARD Protocol)
```bash
# Automated, verifiable process:
$ steward discover --capability orchestrate_sdlc
$ steward verify vibe-agency-orchestrator
$ steward delegate vibe-agency-orchestrator --operation orchestrate_sdlc --context '{...}'
$ steward monitor <task-id>
$ steward result <task-id>
```

**Benefits:**
- ✅ Machine-readable (JSON, not Markdown prose)
- ✅ Always current (runtime introspection + fresh attestations)
- ✅ Cryptographically verified (signing + attestation)
- ✅ Standardized (same commands for all agents)
- ✅ Auditable (trust scores + delegation history)

---

**Next:** See `STEWARD_PROTOCOL_SPEC.md` for full specification.
