# STEWARD Protocol - Federation Model

**Status:** 📝 PLANNED (Phase 3 - Week 24+)
**Last Updated:** 2025-11-21

---

## 🎯 FEDERATION GOALS

1. **Decentralization** - No single point of failure or control
2. **Scalability** - Handle millions of agents across organizations
3. **Censorship Resistance** - No single authority can block agents
4. **Local Autonomy** - Organizations control their own namespace
5. **Global Discovery** - Agents discoverable across federated registries

**Model:** DNS-like hierarchical federation (proven, scalable, simple)

---

## 🌐 HIERARCHICAL NAMESPACE

### Structure

```
root (steward-registry.org)
  ├─ com.steward-registry.org
  │   ├─ vibe-agency.com.steward-registry.org
  │   │   ├─ vibe-agency-orchestrator
  │   │   ├─ vibe-agency-coder
  │   │   └─ vibe-agency-deployer
  │   │
  │   └─ acme-corp.com.steward-registry.org
  │       ├─ acme-planning-bot
  │       └─ acme-code-generator
  │
  ├─ org.steward-registry.org
  │   ├─ openai.org.steward-registry.org
  │   │   ├─ gpt-code-assistant
  │   │   └─ gpt-planner
  │   │
  │   └─ anthropic.org.steward-registry.org
  │       └─ claude-architect
  │
  └─ github.steward-registry.org
      ├─ user/kimeisele.github.steward-registry.org
      │   └─ vibe-agency-orchestrator
      │
      └─ org/anthropics.github.steward-registry.org
          └─ claude-code-agent
```

### Agent ID Format (Fully Qualified)

```
<agent-name>.<namespace>.<tld>.steward-registry.org

Examples:
- vibe-agency-orchestrator.vibe-agency.com.steward-registry.org
- gpt-code-assistant.openai.org.steward-registry.org
- claude-architect.anthropic.org.steward-registry.org
```

**Short Form (within namespace):**
```
vibe-agency-orchestrator  // Resolves to local namespace
```

---

## 🔍 DISCOVERY PROTOCOL

### Query Resolution (Like DNS)

```bash
# 1. Client queries local registry
$ steward discover orchestrate_sdlc

Local Registry (vibe-agency.com): No results

# 2. Query parent registry
Parent Registry (com.steward-registry.org): 2 results found
  - vibe-agency-orchestrator (this namespace)
  - acme-sdlc-bot (acme-corp.com)

# 3. Query root registry
Root Registry (steward-registry.org): 5 results found
  - vibe-agency-orchestrator (com → vibe-agency)
  - acme-sdlc-bot (com → acme-corp)
  - gpt-planner (org → openai)
  - claude-architect (org → anthropic)
  - community-orchestrator (github → user/johndoe)

# 4. Return aggregated results
Found 5 agents across 3 registries:
  ⭐⭐⭐ vibe-agency-orchestrator (Trust: 0.94)
  ⭐⭐ acme-sdlc-bot (Trust: 0.87)
  ⭐ gpt-planner (Trust: 0.82)
  ...
```

### Query Workflow

```
Client Query → Local Registry
               ├─ Found? Return results
               └─ Not found? Query parent registry
                             ├─ Found? Return results
                             └─ Not found? Query root registry
                                           └─ Return aggregated results
```

---

## 📡 REGISTRY SYNC PROTOCOL

### Push Model (Registry → Registry)

```yaml
# When agent published to local registry, push to parent

1. Agent published to vibe-agency.com registry:
   POST /agents/vibe-agency-orchestrator

2. Local registry validates:
   - Manifest valid
   - Signature valid
   - No typosquatting

3. Local registry stores agent

4. Local registry pushes to parent (com.steward-registry.org):
   POST https://com.steward-registry.org/push
   Body: {
     "agent_id": "vibe-agency-orchestrator",
     "namespace": "vibe-agency.com",
     "manifest_url": "https://vibe-agency.com.steward-registry.org/agents/vibe-agency-orchestrator",
     "signature": "...",
     "trust_score": 0.94
   }

5. Parent registry validates and stores reference

6. Parent registry pushes to root (steward-registry.org)

7. Root registry validates and stores global index
```

### Pull Model (Registry → Registry)

```yaml
# Periodic sync from child registries

Every 6 hours:
  1. Root registry queries all known child registries
  2. Child registries return updated agent list
  3. Root registry merges updates
  4. Root registry publishes global index
```

---

## 🔄 CONFLICT RESOLUTION

### Scenario 1: Duplicate Agent ID (Different Namespaces)

```
com.vibe-agency.orchestrator  (Trust: 0.94)
org.acme.orchestrator         (Trust: 0.87)
```

**Resolution:** Both allowed (different namespaces)

**Client Selection:**
```bash
$ steward discover orchestrator

Found 2 agents:
  1. com.vibe-agency.orchestrator (⭐⭐⭐)
  2. org.acme.orchestrator (⭐⭐)

Select agent [1/2]: 1
```

---

### Scenario 2: Duplicate Agent ID (Same Namespace)

```
com.vibe-agency.orchestrator (published 2025-11-21)
com.vibe-agency.orchestrator (published 2025-11-20)
```

**Resolution:** Version-based (latest wins)

```yaml
conflict_resolution:
  policy: "latest_version_wins"

  validation:
    - same_fingerprint: true  # Must be signed with same key
    - monotonic_version: true  # Version must increase
```

---

### Scenario 3: Registry Split-Brain

**Description:** Network partition causes registries to diverge.

```
                 [NETWORK PARTITION]

Registry A:                    Registry B:
  - agent-foo v1.0.0 ✅          - agent-foo v1.0.1 ✅
  - agent-bar v2.0.0 ✅          - agent-bar v1.9.0 ✅
```

**Resolution:** Vector Clocks + Last-Write-Wins

```json
{
  "agent_id": "agent-foo",
  "version": "1.0.1",
  "vector_clock": {
    "registry_a": 5,
    "registry_b": 7  // Registry B has more recent update
  },
  "last_modified": "2025-11-21T13:00:00Z"
}
```

**Merge Strategy:**
1. Compare vector clocks
2. If one dominates (all components ≥), choose that version
3. If concurrent (neither dominates), use last-write-wins (timestamp)
4. Alert operators of conflicts

---

## 🔐 REGISTRY AUTHENTICATION

### Registry-to-Registry Authentication

```yaml
authentication:
  method: "mutual_tls + signed_requests"

  # Each registry has keypair
  registry_identity:
    id: "com.vibe-agency"
    public_key: "sha256:registry-key-abc..."
    certificate: "X.509 cert issued by root"

  # All push/pull requests signed
  request_signing:
    algorithm: "RSA-4096 + SHA-256"
    include_timestamp: true
    nonce: "prevent_replay_attacks"
```

**Example Signed Request:**
```json
{
  "request": {
    "action": "push_agent",
    "agent_id": "vibe-agency-orchestrator",
    "manifest_url": "https://...",
    "timestamp": "2025-11-21T13:00:00Z",
    "nonce": "abc123..."
  },
  "signature": {
    "signed_by": "sha256:registry-key-abc...",
    "algorithm": "RSA-4096",
    "value": "..."
  }
}
```

---

## 🌍 GEOGRAPHIC DISTRIBUTION

### Geo-Redundant Registries

```yaml
root_registry:
  primary: "steward-registry.org" (US-East)
  replicas:
    - "eu.steward-registry.org" (EU-West)
    - "asia.steward-registry.org" (Asia-Pacific)
    - "au.steward-registry.org" (Australia)

  replication:
    strategy: "active-active"
    consistency: "eventual"
    sync_interval_minutes: 5
```

**Client Behavior:**
```bash
# Client uses closest registry based on latency
$ steward discover orchestrator --geo-aware

Measuring latency...
  - steward-registry.org: 150ms
  - eu.steward-registry.org: 25ms ✅ (closest)
  - asia.steward-registry.org: 300ms

Using: eu.steward-registry.org
```

---

## 📊 REGISTRY METRICS

### Health Monitoring

```yaml
metrics:
  registry_health:
    - uptime_percent
    - query_latency_p99
    - sync_lag_seconds (compared to root)
    - agent_count

  federation_health:
    - total_registries_online
    - partition_detected (split-brain)
    - conflict_rate (conflicts per hour)
    - sync_failures_per_hour

alerts:
  - registry_down: >1 registry offline
  - high_sync_lag: >60s behind root
  - partition_detected: split-brain detected
  - high_conflict_rate: >10 conflicts per hour
```

---

## 🚀 BOOTSTRAP NEW REGISTRY

### Organization Wants Own Registry

```bash
# 1. Deploy registry software
$ docker run steward-registry:latest \
    --namespace acme-corp.com \
    --parent com.steward-registry.org

# 2. Generate registry keypair
$ steward-registry keygen

Generating registry keypair...
✅ Private key: /etc/steward-registry/registry_id_rsa
✅ Public key: /etc/steward-registry/registry_id_rsa.pub
✅ Fingerprint: sha256:registry-acme-xyz...

# 3. Register with parent
$ steward-registry register \
    --parent com.steward-registry.org \
    --namespace acme-corp.com \
    --pubkey /etc/steward-registry/registry_id_rsa.pub

Registering with parent...
✅ Namespace reserved: acme-corp.com
✅ Certificate issued (valid 1 year)
✅ Federation active

# 4. Publish first agent
$ steward publish \
    --registry https://acme-corp.com.steward-registry.org

✅ Agent published to local registry
✅ Pushed to parent: com.steward-registry.org
✅ Indexed by root: steward-registry.org
✅ Globally discoverable
```

---

## 🔍 SEARCH ACROSS REGISTRIES

### Federated Search

```bash
# Search all federated registries
$ steward discover orchestrate_sdlc --federated

Querying registries...
  ├─ Local (vibe-agency.com): 1 result
  ├─ Parent (com): 2 results
  ├─ Root (global): 5 results
  └─ Siblings (org, github): 3 results

Found 11 agents across 4 registries:
┌──────────────────────────────┬──────────┬─────────┬──────────────┐
│ Agent ID                     │ Registry │ Trust   │ Latency      │
├──────────────────────────────┼──────────┼─────────┼──────────────┤
│ vibe-agency-orchestrator     │ com      │ 0.94    │ 25ms (local) │
│ acme-sdlc-bot                │ com      │ 0.87    │ 30ms         │
│ gpt-planner                  │ org      │ 0.82    │ 150ms        │
│ claude-architect             │ org      │ 0.91    │ 160ms        │
│ community-orchestrator       │ github   │ 0.65    │ 200ms        │
│ ...                          │          │         │              │
└──────────────────────────────┴──────────┴─────────┴──────────────┘

Sort by: [trust/latency/name]: trust
```

---

## ✅ PRODUCTION READINESS CHECKLIST

### Before v2.0.0 (Federation Launch)

- [ ] Hierarchical namespace implementation
- [ ] Push/pull sync protocol
- [ ] Conflict resolution (vector clocks)
- [ ] Registry authentication (mutual TLS)
- [ ] Split-brain detection
- [ ] Geo-redundant replicas
- [ ] Federated search
- [ ] Registry bootstrap process
- [ ] Health monitoring & alerts
- [ ] Performance testing (1M+ agents)

### Federation Testing

- [ ] Test registry bootstrap
- [ ] Test push/pull sync
- [ ] Simulate network partition (split-brain)
- [ ] Test conflict resolution
- [ ] Test geo-redundancy failover
- [ ] Load test (10K queries/sec)
- [ ] Chaos testing (random registry failures)

---

## 📚 REFERENCES

- **DNS Protocol:** RFC 1034, RFC 1035 (Domain Name System)
- **Vector Clocks:** Leslie Lamport (Distributed Systems)
- **Eventual Consistency:** Amazon Dynamo Paper
- **Federation:** ActivityPub (W3C Recommendation)
- **Registry Design:** Docker Registry, npm registry

---

## 🗺️ MIGRATION PATH

### Phase 1: Git-Based (MVP)

```
- Single git repository
- Simple file-based storage
- Manual coordination
```

### Phase 2: Centralized Registry

```
- Single authoritative registry
- API-based queries
- Automated sync
```

### Phase 3: Federated Registry

```
- Hierarchical namespace
- DNS-like resolution
- Push/pull sync
- Geo-redundancy
```

**Timeline:** MVP (Week 4) → Centralized (Week 12) → Federated (Week 24)

---

**Status:** 📝 PLANNED - Design complete, implementation in Phase 3
**Critical:** Federation enables global scale without single authority
