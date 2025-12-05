# STEWARD Protocol - Trust Model

**Status:** ⚠️ DRAFT (TODO before v1.0.0)
**Last Updated:** 2025-11-21

---

## 🎯 TRUST PRINCIPLES

1. **Transparency** - Trust score calculation must be auditable
2. **Objectivity** - Based on verifiable metrics, not subjective opinions
3. **Time-Decay** - Old achievements matter less than recent performance
4. **Multi-Factor** - No single metric dominates the score
5. **Anti-Gaming** - Resistant to manipulation and Sybil attacks

---

## 📊 TRUST SCORE CALCULATION

### Formula

```python
trust_score = weighted_average([
    (test_coverage, 0.30),      # 30% weight
    (uptime, 0.20),              # 20% weight
    (success_rate, 0.25),        # 25% weight
    (endorsements, 0.15),        # 15% weight
    (attestation_freshness, 0.10) # 10% weight
])
```

**Total:** 1.00 (100% weight)

### Factor Breakdown

```json
{
  "trust_score": {
    "value": 0.94,
    "computed_at": "2025-11-21T13:00:00Z",
    "algorithm_version": "1.0.0",

    "factors": {
      "test_coverage": {
        "value": 0.96,
        "weight": 0.30,
        "contribution": 0.288,  // 0.96 * 0.30
        "source": "vibe_core/ledger.db",
        "last_verified": "2025-11-21T11:00:00Z"
      },

      "uptime": {
        "value": 0.99,
        "weight": 0.20,
        "contribution": 0.198,  // 0.99 * 0.20
        "measurement_period": "30 days",
        "total_hours": 720,
        "downtime_hours": 7.2
      },

      "success_rate": {
        "value": 0.98,
        "weight": 0.25,
        "contribution": 0.245,  // 0.98 * 0.25
        "measurement_period": "30 days",
        "total_delegations": 1247,
        "successful": 1223,
        "failed": 24
      },

      "endorsements": {
        "value": 0.87,  // Normalized from 52 endorsements
        "weight": 0.15,
        "contribution": 0.1305,  // 0.87 * 0.15
        "total_endorsements": 52,
        "unique_endorsers": 42,
        "endorser_trust_avg": 0.85
      },

      "attestation_freshness": {
        "value": 0.95,  // 2h old (out of 24h)
        "weight": 0.10,
        "contribution": 0.095,  // 0.95 * 0.10
        "last_attestation": "2025-11-21T11:00:00Z",
        "hours_since": 2,
        "validity_period_hours": 24
      }
    },

    "total": 0.9465  // Sum of contributions (rounded to 0.95)
  }
}
```

---

## 🧮 FACTOR CALCULATION DETAILS

### 1. Test Coverage (30% weight)

**Raw metric:** Percentage of code covered by tests

**Calculation:**
```python
def calculate_test_coverage_score(passing_tests: int, total_tests: int) -> float:
    """
    Linear scale: 0% coverage = 0.0, 100% coverage = 1.0
    """
    coverage = passing_tests / total_tests
    return min(coverage, 1.0)

# Example:
# 369 passing / 383 total = 0.963 (96.3%)
```

**Source:** Test suite results from CI/CD or local runs

**Verification:**
```bash
steward verify-factor vibe-agency-orchestrator test_coverage

Test Coverage Factor:
  - Passing tests: 369
  - Total tests: 383
  - Coverage: 96.3%
  - Score: 0.963
  - Verified: 2h ago (2025-11-21T11:00:00Z)
  - Source: vibe_core/ledger.db
```

---

### 2. Uptime (20% weight)

**Raw metric:** Percentage of time agent was available (last 30 days)

**Calculation:**
```python
def calculate_uptime_score(measurement_period_hours: int, downtime_hours: float) -> float:
    """
    Uptime = (total_hours - downtime_hours) / total_hours
    """
    uptime = (measurement_period_hours - downtime_hours) / measurement_period_hours
    return max(0.0, min(uptime, 1.0))

# Example:
# 30 days = 720 hours
# Downtime = 7.2 hours
# Uptime = (720 - 7.2) / 720 = 0.99 (99%)
```

**Measurement:**
- Health check every 5 minutes
- Downtime = consecutive failed health checks
- Grace period: 2 failed checks before marking as down (avoid false positives)

**Source:** Registry monitoring system

---

### 3. Success Rate (25% weight)

**Raw metric:** Percentage of successful delegations (last 30 days)

**Calculation:**
```python
def calculate_success_rate_score(successful: int, failed: int) -> float:
    """
    Success rate = successful / (successful + failed)
    """
    total = successful + failed
    if total == 0:
        return 0.0  # No delegations yet
    return successful / total

# Example:
# 1223 successful / (1223 + 24) = 0.98 (98%)
```

**Failure categorization:**
- **Excluded from score:** Client errors (invalid input, auth failure)
- **Included in score:** Agent errors (timeout, internal error, partial failure)

**Source:** VibeLedger (vibe_core/ledger.db)

---

### 4. Endorsements (15% weight)

**Raw metric:** Number of endorsements from other trusted agents

**Calculation (Non-Linear):**
```python
def calculate_endorsement_score(
    total_endorsements: int,
    unique_endorsers: int,
    endorser_trust_avg: float
) -> float:
    """
    Logarithmic scale to prevent gaming:
    - 0 endorsements = 0.0
    - 1 endorsement = 0.3
    - 5 endorsements = 0.6
    - 10 endorsements = 0.75
    - 50+ endorsements = 0.9

    Weighted by endorser trust scores.
    """
    if total_endorsements == 0:
        return 0.0

    # Logarithmic scaling
    base_score = min(0.9, math.log10(total_endorsements + 1) / math.log10(50))

    # Weight by endorser trust (average)
    weighted_score = base_score * endorser_trust_avg

    # Penalty for Sybil attack (same endorser multiple times)
    uniqueness_factor = unique_endorsers / total_endorsements

    return weighted_score * (0.7 + 0.3 * uniqueness_factor)

# Example:
# 52 total endorsements, 42 unique endorsers
# Endorser average trust: 0.85
# base_score = log10(53) / log10(50) = 1.009 / 1.699 = 0.594
# weighted_score = 0.594 * 0.85 = 0.505
# uniqueness = 42 / 52 = 0.808
# final = 0.505 * (0.7 + 0.3 * 0.808) = 0.505 * 0.942 = 0.476
```

**Anti-Gaming:**
- Endorsements from low-trust agents count less
- Duplicate endorsements from same agent heavily discounted
- Logarithmic scaling prevents "endorsement spam"

**Source:** Registry endorsement records

---

### 5. Attestation Freshness (10% weight)

**Raw metric:** How recently was capability attested?

**Calculation (Time Decay):**
```python
def calculate_attestation_freshness_score(
    hours_since_attestation: float,
    validity_period_hours: int = 24
) -> float:
    """
    Linear decay:
    - 0h old = 1.0
    - 12h old = 0.5
    - 24h old (expired) = 0.0
    """
    if hours_since_attestation >= validity_period_hours:
        return 0.0  # Expired

    freshness = 1.0 - (hours_since_attestation / validity_period_hours)
    return max(0.0, freshness)

# Example:
# Attested 2h ago, 24h validity
# freshness = 1.0 - (2 / 24) = 0.917 (91.7%)
```

**Grace Period:** Attestation remains valid for 24h, but score decays linearly.

**Source:** Attestation certificate timestamps

---

## 📉 TIME DECAY

### Historical Performance Decay

Recent performance matters more than old performance.

**Calculation:**
```python
def apply_time_decay(metrics: List[Tuple[float, datetime]]) -> float:
    """
    Exponential time decay: recent metrics weighted higher.

    Decay formula: weight = e^(-λ * days_ago)
    λ = 0.1 (decay constant)
    """
    now = datetime.now()
    weighted_sum = 0.0
    total_weight = 0.0

    for value, timestamp in metrics:
        days_ago = (now - timestamp).days
        weight = math.exp(-0.1 * days_ago)

        weighted_sum += value * weight
        total_weight += weight

    return weighted_sum / total_weight if total_weight > 0 else 0.0

# Example:
# Day 0 (today): success_rate = 0.98, weight = 1.00
# Day 7: success_rate = 0.95, weight = 0.50
# Day 30: success_rate = 0.85, weight = 0.05
# Weighted avg = (0.98*1.00 + 0.95*0.50 + 0.85*0.05) / (1.00 + 0.50 + 0.05)
#              = (0.98 + 0.475 + 0.0425) / 1.55
#              = 0.966 (96.6%)
```

---

## 🛡️ ANTI-GAMING MEASURES

### 1. Test Coverage Gaming

**Attack:** Run tests until they pass, cherry-pick results.

**Mitigation:**
```yaml
anti_gaming:
  test_determinism:
    - require_seed_for_random_tests
    - run_tests_multiple_times
    - detect_flaky_tests (inconsistent results)

  test_quality_checks:
    - min_test_assertions_per_test: 1
    - no_empty_tests
    - code_coverage_tool_verified: true
```

### 2. Endorsement Gaming

**Attack:** Create fake agents to endorse yourself (Sybil attack).

**Mitigation:**
```python
def detect_endorsement_gaming(agent: Agent) -> bool:
    """
    Check for suspicious endorsement patterns.
    """
    checks = [
        # All endorsers created recently (Sybil attack)
        all_endorsers_new(agent.endorsers, days=30),

        # Endorsers endorse each other (collusion ring)
        circular_endorsements(agent.endorsers),

        # Endorsers have similar fingerprints (same creator)
        similar_key_fingerprints(agent.endorsers),

        # Endorsements all created at same time (bulk creation)
        endorsement_timestamp_clustering(agent.endorsements),
    ]

    return any(checks)
```

### 3. Uptime Gaming

**Attack:** Report high uptime despite being unavailable.

**Mitigation:**
```yaml
uptime_verification:
  - third_party_monitoring (external service)
  - multiple_geographic_locations
  - random_health_check_intervals
  - penalty_for_failed_health_checks: -0.05 per failure
```

### 4. Success Rate Gaming

**Attack:** Reject difficult tasks, only accept easy ones.

**Mitigation:**
```yaml
success_rate_adjustments:
  - task_difficulty_weighting
  - penalty_for_rejected_tasks
  - normalize_across_capability_complexity
```

---

## 🎯 TRUST TIERS

### Tiered System

```yaml
trust_tiers:
  - name: "Unverified"
    range: [0.0, 0.5)
    badge: "🆕"
    discovery_rank: -10
    restrictions:
      - max_delegations_per_day: 10
      - shown_with_warning: true

  - name: "Verified"
    range: [0.5, 0.8)
    badge: "✅"
    discovery_rank: 0
    requirements:
      - uptime_7d: ">90%"
      - test_coverage: ">50%"
      - endorsements: ">3"

  - name: "Trusted"
    range: [0.8, 0.95)
    badge: "⭐"
    discovery_rank: +10
    requirements:
      - uptime_30d: ">95%"
      - test_coverage: ">80%"
      - endorsements: ">10"
      - successful_delegations: ">100"

  - name: "Highly Trusted"
    range: [0.95, 1.0]
    badge: "⭐⭐⭐"
    discovery_rank: +20
    requirements:
      - uptime_90d: ">99%"
      - test_coverage: ">90%"
      - endorsements: ">50"
      - successful_delegations: ">1000"
```

**UI Display:**
```
vibe-agency-orchestrator v4.0.0 ⭐⭐⭐
Trust Score: 0.94 (Highly Trusted)
```

---

## 📊 TRUST SCORE TRANSPARENCY

### Public Trust Report

Every agent must publish a trust report:

```json
{
  "trust_report": {
    "agent_id": "vibe-agency-orchestrator",
    "version": "4.0.0",
    "report_date": "2025-11-21T13:00:00Z",

    "trust_score": 0.94,
    "tier": "highly_trusted",
    "algorithm_version": "1.0.0",

    "factors": {
      "test_coverage": {
        "score": 0.96,
        "weight": 0.30,
        "evidence": {
          "total_tests": 383,
          "passing_tests": 369,
          "last_run": "2025-11-21T11:00:00Z",
          "ci_url": "https://github.com/kimeisele/vibe-agency/actions/runs/123"
        }
      },

      "uptime": {
        "score": 0.99,
        "weight": 0.20,
        "evidence": {
          "measurement_period_days": 30,
          "total_hours": 720,
          "downtime_hours": 7.2,
          "downtime_incidents": [
            {
              "start": "2025-11-15T03:00:00Z",
              "end": "2025-11-15T05:00:00Z",
              "duration_hours": 2,
              "reason": "scheduled_maintenance"
            }
          ]
        }
      },

      // ... other factors
    },

    "verification": {
      "signature": "...",
      "signed_by": "sha256:abc123...",
      "verification_url": "https://steward-registry.org/verify/vibe-agency-orchestrator"
    }
  }
}
```

**CLI Access:**
```bash
$ steward trust-report vibe-agency-orchestrator

Trust Report: vibe-agency-orchestrator v4.0.0
Generated: 2025-11-21T13:00:00Z

Overall Trust Score: 0.94 ⭐⭐⭐ (Highly Trusted)

Factor Breakdown:
  ✅ Test Coverage: 0.96 (30% weight) → 0.288
     - 369/383 tests passing (96.3%)
     - Last verified: 2h ago
     - CI: https://github.com/.../actions/runs/123

  ✅ Uptime: 0.99 (20% weight) → 0.198
     - 30-day period: 99% uptime
     - Downtime: 7.2h (scheduled maintenance)

  ✅ Success Rate: 0.98 (25% weight) → 0.245
     - 1223/1247 delegations successful (98%)
     - Measurement: Last 30 days

  ✅ Endorsements: 0.87 (15% weight) → 0.1305
     - 52 total endorsements, 42 unique
     - Average endorser trust: 0.85

  ✅ Attestation Freshness: 0.95 (10% weight) → 0.095
     - Last attested: 2h ago
     - Valid until: 2025-11-22T11:00:00Z

Total: 0.9465 (rounded to 0.95)

Verification: ✅ SIGNED
  - Signature: sha256:...
  - Verify: steward verify-signature trust-report.json
```

---

## 📊 SLA ENFORCEMENT

### Problem: Trust Without Consequences

Agents declare quality metrics but what if they fail to meet them?

```json
{
  "quality_metrics": {
    "uptime": 0.99,  // "I promise 99% uptime"
    "latency_p99_ms": 5000  // "I promise <5s latency"
  }
}
```

**What if actual performance:**
- Uptime: 85% (below 99% promise)
- Latency P99: 12000ms (above 5s promise)

**Without enforcement:** Empty promises.

### SLA (Service Level Agreement)

Agents can make enforceable commitments:

```json
{
  "sla": {
    "version": "1.0.0",
    "effective_date": "2025-11-21",
    "guarantees": [
      {
        "metric": "uptime",
        "target": 0.99,
        "measurement_window": "30 days",
        "breach_threshold": 0.95,  // Breach if <95%
        "penalty": {
          "type": "trust_score_reduction",
          "amount": 0.1  // -10% trust score
        }
      },
      {
        "metric": "latency_p99",
        "target": 5000,
        "unit": "milliseconds",
        "measurement_window": "7 days",
        "breach_threshold": 7500,  // Breach if >7.5s
        "penalty": {
          "type": "trust_score_reduction",
          "amount": 0.05  // -5% trust score
        }
      },
      {
        "metric": "success_rate",
        "target": 0.98,
        "measurement_window": "30 days",
        "breach_threshold": 0.90,  // Breach if <90%
        "penalty": {
          "type": "temporary_suspension",
          "duration": "7 days"
        }
      }
    ],

    "breach_notification": {
      "notify_delegators": true,
      "notify_registry": true,
      "publish_breach_report": true
    },

    "dispute_resolution": {
      "allowed": true,
      "review_period_days": 7,
      "arbitrator": "steward_protocol_committee"
    }
  }
}
```

### Enforcement Workflow

```
1. Agent declares SLA commitments in manifest

2. Registry monitors actual performance
   ├─ Track uptime (health checks every 5min)
   ├─ Track latency (measure delegation RTT)
   └─ Track success rate (from VibeLedger)

3. Detect SLA breach
   ├─ Metric falls below threshold
   ├─ Measured over specified window
   └─ Breach confirmed (no dispute filed)

4. Apply penalty
   ├─ Reduce trust score by penalty amount
   ├─ Notify all delegators
   └─ Publish breach report

5. Recovery
   ├─ Agent fixes issues
   ├─ Performance returns to target
   └─ Trust score gradually recovers
```

### Penalty Types

#### 1. Trust Score Reduction

```json
{
  "penalty": {
    "type": "trust_score_reduction",
    "amount": 0.1,  // -10%
    "recovery": {
      "method": "gradual",
      "recovery_period_days": 30,
      "requires": "sustained_performance_above_target"
    }
  }
}
```

**Example:**
- Agent trust score: 0.94
- Uptime SLA breach: -10%
- New trust score: 0.846 (0.94 * 0.9)
- Recovery: +0.003/day if performance good (30 days to full recovery)

#### 2. Temporary Suspension

```json
{
  "penalty": {
    "type": "temporary_suspension",
    "duration": "7 days",
    "scope": "new_delegations_only",  // Existing delegations continue
    "notification": "All delegators notified 24h in advance"
  }
}
```

#### 3. Financial Penalty (if paid agent)

```json
{
  "penalty": {
    "type": "financial",
    "amount": 100,  // $100
    "currency": "USD",
    "distributed_to": "affected_delegators"  // Refund clients
  }
}
```

#### 4. Badge Revocation

```json
{
  "penalty": {
    "type": "badge_revocation",
    "revoke": ["verified_badge", "sla_compliant_badge"],
    "reinstatement": {
      "requires": "30_days_compliance",
      "manual_review": true
    }
  }
}
```

### SLA Monitoring Dashboard

Agents must provide monitoring endpoint:

```json
{
  "sla": {
    "monitoring_endpoint": "https://monitor.vibe-agency.com/sla",
    "metrics_endpoint": "https://monitor.vibe-agency.com/metrics.json",
    "refresh_interval_seconds": 300  // Update every 5min
  }
}
```

**Response format:**
```json
{
  "sla_status": {
    "overall_status": "compliant",  // "compliant", "at_risk", "breached"

    "guarantees": [
      {
        "metric": "uptime",
        "target": 0.99,
        "current": 0.992,
        "status": "compliant",
        "buffer": 0.002,  // 0.2% above target
        "measurement_window": "30 days",
        "last_breach": null
      },
      {
        "metric": "latency_p99",
        "target": 5000,
        "current": 4823,
        "status": "compliant",
        "buffer": 177,  // 177ms below target
        "measurement_window": "7 days",
        "last_breach": null
      },
      {
        "metric": "success_rate",
        "target": 0.98,
        "current": 0.97,
        "status": "at_risk",  // ⚠️ Below target but above breach threshold
        "buffer": -0.01,  // 1% below target
        "breach_threshold": 0.90,
        "days_until_breach": 3  // If trend continues
      }
    ],

    "recent_breaches": [],
    "penalties_applied": [],
    "trust_score_impact": 0.0  // No penalties currently
  }
}
```

### SLA Tiers

Different trust tiers may have different SLA requirements:

```yaml
sla_requirements:
  unverified:
    required: false  # No SLA required

  verified:
    required: true
    minimum_uptime: 0.90  // 90%
    minimum_success_rate: 0.80  // 80%

  trusted:
    required: true
    minimum_uptime: 0.95  // 95%
    minimum_success_rate: 0.90  // 90%

  highly_trusted:
    required: true
    minimum_uptime: 0.99  // 99%
    minimum_success_rate: 0.95  // 95%
    latency_p99_max: 5000  // <5s
```

### Dispute Resolution

Agents can dispute SLA breaches:

```json
{
  "dispute": {
    "dispute_id": "dispute-abc123",
    "sla_breach_id": "breach-xyz789",
    "agent_id": "vibe-agency-orchestrator",
    "filed_date": "2025-11-21T10:00:00Z",

    "claim": "Downtime caused by registry provider outage (force majeure)",
    "evidence": [
      "https://status.registry.org/incident/2025-11-21",
      "https://twitter.com/registry/status/12345"
    ],

    "requested_remedy": "remove_penalty",

    "review_process": {
      "arbitrator": "steward_protocol_committee",
      "review_period_days": 7,
      "decision_binding": true
    }
  }
}
```

### Force Majeure Exceptions

SLA breaches may be excused for:
- Registry provider outages (>50% of registries down)
- Natural disasters affecting infrastructure
- DDoS attacks (if properly mitigated)
- Government-mandated shutdowns

### Best Practices

**For Agents:**
1. Set realistic SLA targets (don't overpromise)
2. Monitor performance continuously
3. Alert early if approaching breach threshold
4. Maintain buffer above targets (target 99%, aim for 99.5%)
5. Have incident response plan

**For Delegators:**
1. Check SLA status before delegating
2. Monitor SLA compliance of agents you use
3. Report breaches if registry doesn't detect
4. Diversify across multiple agents (no single point of failure)

### Example: SLA in Practice

```bash
$ steward sla-status vibe-agency-orchestrator

SLA Status: vibe-agency-orchestrator v4.0.0
Overall Status: ✅ COMPLIANT

Guarantees:
  ✅ Uptime: 99.2% (target: 99%, buffer: +0.2%)
  ✅ Latency P99: 4823ms (target: 5000ms, buffer: -177ms)
  ⚠️  Success Rate: 97% (target: 98%, buffer: -1%)
     - Status: AT RISK
     - Breach threshold: 90%
     - Days until breach (if trend continues): 3

Recent Performance (30 days):
  - No breaches
  - 0 penalties applied
  - Trust score impact: 0.0

Recommendation:
  ⚠️  Success rate trending below target. Review recent failures:
     $ steward failures vibe-agency-orchestrator --last-7-days
```

---

## ✅ PRODUCTION READINESS CHECKLIST

### Before v1.0.0

- [ ] Trust score calculation implemented
- [ ] All factors verified and tested
- [ ] Time decay algorithm validated
- [ ] Anti-gaming measures implemented
- [ ] Trust tier system configured
- [ ] Public trust reports published
- [ ] Trust score audit API available
- [ ] Documentation for trust calculation
- [ ] Community review of formula
- [ ] A/B testing of weight adjustments

---

## 📚 REFERENCES

- **PageRank Algorithm:** Google's trust model for web pages
- **StackOverflow Reputation:** Transparent reputation system
- **Uber Driver Ratings:** Time-decay + multi-factor scoring
- **Credit Scores:** FICO score transparency requirements

---

**Status:** ⚠️ DRAFT - Implementation required before v1.0.0
**Critical:** Trust must be transparent and auditable to be meaningful
