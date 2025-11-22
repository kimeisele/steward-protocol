# STEWARD Protocol Specification (DRAFT)
> **"Docker for AI Agents" + "LinkedIn for Agents"**
>
> Universal Standard for Agent Identity, Discovery, Verification & Delegation

**Version:** 0.1.0-draft
**Status:** 🚧 DRAFT - Design Phase
**Authors:** vibe-agency core team
**Date:** 2025-11-21

---

## 🎯 VISION

**Problem:** AI Agents can't discover, verify, or delegate to each other systematically.

**Solution:** STEWARD Protocol - A universal standard for agent interoperability, like:
- 🐳 **Docker**: Standardized runtime, manifests, registries
- 💼 **LinkedIn**: Professional profiles, skill verification, reputation
- 🌐 **HTTP**: Universal protocol for communication

---

## 📋 CORE REQUIREMENTS

### What a Real STANDARD Needs:

1. **Agent Manifest Format** (like Dockerfile)
   - Machine-readable identity
   - Capability declarations
   - Versioning & compatibility
   - Cryptographic signing

2. **Discovery Protocol** (like Docker Hub search)
   - Find agents by capability
   - Filter by trust score
   - Version compatibility checking
   - Geographic/network proximity

3. **Verification Protocol** (like SSL/TLS certificates)
   - Cryptographic identity proof
   - Capability attestation
   - Reputation/trust scores
   - Revocation mechanism

4. **Delegation Protocol** (like REST API)
   - Task submission format
   - Progress monitoring
   - Result validation
   - Error handling

5. **Registry/Index** (like npm registry, Docker Hub)
   - Central or federated agent directory
   - Version history
   - Usage statistics
   - Trust scores

6. **CLI Tools** (like docker CLI, gh CLI)
   - `steward init` - Initialize agent
   - `steward verify` - Verify identity
   - `steward delegate` - Submit tasks
   - `steward discover` - Find agents

---

## 🏗️ ARCHITECTURE LAYERS

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 5: Agent Applications                                 │
│  (STEWARD, other AI agents consuming the protocol)          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: STEWARD CLI & SDKs                                 │
│  (steward CLI, Python SDK, JS SDK, etc.)                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: STEWARD Protocol APIs                              │
│  ├─ Discovery API (find agents)                             │
│  ├─ Verification API (verify identity)                      │
│  ├─ Delegation API (submit tasks)                           │
│  └─ Monitoring API (track progress)                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: STEWARD Registry                                   │
│  ├─ Agent Index (searchable directory)                      │
│  ├─ Reputation System (trust scores)                        │
│  ├─ Version Store (capability history)                      │
│  └─ Audit Logs (delegation trail)                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Agent Manifest Format                              │
│  (steward.json - machine-readable agent identity)           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 LAYER 1: AGENT MANIFEST FORMAT

### File: `steward.json`

**Like:** `package.json` (npm), `Dockerfile`, `docker-compose.yml`

```json
{
  "steward_version": "1.0.0",
  "agent": {
    "id": "vibe-agency-orchestrator",
    "name": "STEWARD",
    "version": "4.0.0",
    "class": "orchestration_operator",
    "specialization": "sdlc_management",
    "status": "active",
    "fingerprint": "sha256:abc123...",
    "issued_by": "vibe-agency",
    "issued_date": "2025-11-21T00:00:00Z"
  },

  "credentials": {
    "mandate": [
      {
        "capability": "orchestrate_sdlc",
        "scope": ["planning", "coding", "testing", "deployment", "maintenance"],
        "attestation": "sha256:def456..."
      }
    ],
    "constraints": [
      {
        "forbidden": "bypass_tests",
        "reason": "Test-first discipline mandatory"
      }
    ],
    "prime_directive": "Trust tests over claims, verify over assume"
  },

  "capabilities": {
    "interfaces": [
      {
        "type": "cli",
        "protocol": "bash",
        "endpoint": "./bin/vibe --json",
        "health_check": "./bin/vibe status --json"
      },
      {
        "type": "api",
        "protocol": "http",
        "endpoint": "http://localhost:8080/api/v1",
        "health_check": "http://localhost:8080/health"
      }
    ],

    "operations": [
      {
        "name": "orchestrate_sdlc",
        "input_schema": {
          "$ref": "#/schemas/MissionContext"
        },
        "output_schema": {
          "$ref": "#/schemas/SpecialistResult"
        },
        "latency_ms": 300000,
        "idempotent": true,
        "versioned": true
      }
    ],

    "quality_metrics": {
      "accuracy": 0.96,
      "test_coverage": 0.80,
      "uptime": 1.00,
      "latency_p99_ms": 5000
    }
  },

  "runtime": {
    "introspection_endpoint": "./bin/vibe introspect --json",
    "state_query": "./bin/vibe ledger-query --json",
    "logs": "./logs/steward.log"
  },

  "governance": {
    "principal": "vibe-agency-core-team",
    "contact": "https://github.com/kimeisele/vibe-agency",
    "audit_trail": "vibe_core/ledger.db",
    "transparency": "public"
  }
}
```

**Key Improvements over static STEWARD.md:**
1. ✅ **Machine-readable** (JSON, not Markdown prose)
2. ✅ **Versioned** (semver for agent evolution)
3. ✅ **Introspectable** (runtime status endpoint)
4. ✅ **Schema-validated** (input/output contracts)
5. ✅ **Health-checkable** (liveness probes)

---

## 👤 LAYER 1.5: USER & TEAM CONTEXT (Optional Extension)

### Purpose: Single Source of Truth for Agent + Operator Context

**Problem:** Agents need to know not just WHAT they are, but WHO operates them and HOW they should behave.

**Solution:** Extend `STEWARD.md` to include optional user preferences and team context alongside agent identity.

### Why This Matters

1. **Personalization**: Different users have different workflows (test-first vs iterative, verbose vs concise)
2. **Team Consistency**: Team-wide defaults ensure consistent behavior across all sessions
3. **Multi-User Support**: Same agent, different operators with different preferences
4. **Session Continuity**: User context persists across sessions without re-configuration
5. **Graceful Degradation**: Agent works without user context, but works BETTER with it

### Structure: All-in-One STEWARD.md

```markdown
# STEWARD.md

> **Protocol Version:** 1.0.0
> **Compliance Level:** Level 2 (Standard)

---

## 🤖 AGENT IDENTITY (Required - Level 1)

### Agent Manifest
- **ID**: vibe-agency-orchestrator
- **Version**: 4.0.0
- **Class**: orchestration_operator
- **Specialization**: sdlc_management
- **Status**: active
- **Trust Score**: 0.94

### Capabilities
- orchestrate_sdlc (v2.0.0)
- delegate_to_specialist (v1.5.0)
- execute_playbook (v1.8.0)

### Prime Directive
Trust tests over claims, verify over assume.

### Machine-Readable Manifest
[View steward.json](./steward.json)

---

## 👤 USER CONTEXT (Optional - Level 2+)

### Default User
```yaml
default_user:
  workflow_style: "balanced"
  verbosity: "medium"
  communication: "friendly"
```

### Personal Preferences (Multi-User)

#### User: kim
```yaml
kim:
  role: "Tech Lead"
  workflow_style: "test_first"
  verbosity: "low"
  communication: "concise_technical"
  timezone: "Europe/Berlin"
  language: "de-DE"

  preferences:
    code_style:
      python: "black"
      typescript: "strict"
    git:
      commit_style: "conventional_commits"
      workflow: "rebase_over_merge"
    testing:
      framework: "pytest"
      min_coverage: 0.80

  constraints:
    - "No verbose confirmations"
    - "Show full tracebacks on errors"
    - "Minimal logging output"
```

#### User: alex
```yaml
alex:
  role: "Backend Developer"
  workflow_style: "iterative"
  verbosity: "medium"
  communication: "explanatory"
  timezone: "Europe/Berlin"
  language: "en-US"

  preferences:
    - "Explain reasoning before actions"
    - "Step-by-step guidance"
    - "Ask before major changes"
```

### Team Context
```yaml
team:
  development_style: "test_driven"
  git_workflow: "rebase_over_merge"
  commit_style: "conventional_commits"

  testing:
    framework: "pytest"
    min_coverage: 0.80
    pre_push: true

  documentation:
    style: "inline_comments"
    format: "markdown"

  quality_gates:
    - "All tests must pass"
    - "Pre-push checks mandatory"
    - "Min 80% test coverage"
```
```

### Boot Modes & CLI Integration

```bash
# Mode 1: Agent-Only (Minimal - Level 1)
steward boot
# Uses only AGENT IDENTITY section
# No user context loaded

# Mode 2: Single User (Level 2)
steward boot --user kim
# Uses AGENT IDENTITY + kim's preferences

# Mode 3: Team Default (Level 2)
steward boot --team
# Uses AGENT IDENTITY + team context

# Mode 4: Auto-Detect (Level 2)
steward boot --auto
# CLI detects Git user: git config user.name
# If "Kim" → use kim preferences
# If "Alex" → use alex preferences
# If unknown → use team default
# If no team → use default_user
```

### Context Precedence (Conflict Resolution)

When multiple contexts apply:

```
┌─────────────────────────────────────────────────┐
│ 1. User Preferences (Highest Priority)         │
│    ↓ (overrides)                                │
│ 2. Team Context                                 │
│    ↓ (overrides)                                │
│ 3. Agent Defaults (Lowest Priority)             │
└─────────────────────────────────────────────────┘
```

**Example:**
```yaml
# Agent default: verbosity = "high"
# Team context: verbosity = "medium"
# kim's preference: verbosity = "low"
# → Final: verbosity = "low" (user wins)
```

### Graceful Degradation

| Sections Present | Boot Works? | Features Available |
|-----------------|-------------|-------------------|
| Agent Identity only | ✅ YES | Basic agent functionality |
| + Default User | ✅ YES | Basic personalization |
| + Team Context | ✅ YES | Team-wide consistency |
| + Multi-User | ✅ YES | Per-user customization |

**Key Point:** Every level works independently - no breaking changes!

### Privacy & Security

**Committed to Git (Public):**
```yaml
kim:
  role: "Tech Lead"
  workflow_style: "test_first"
  verbosity: "low"
  # Public preferences are fine
```

**Gitignored (Private):**
```yaml
kim:
  preferences_file: ".steward/kim.private.md"  # gitignored
  # Points to external file for sensitive data
```

**.gitignore:**
```gitignore
.steward/*.private.md
.steward/secrets.yaml
```

### CLI Validation

```bash
# Validate STEWARD.md structure
steward validate
# Output:
# ✅ Agent Identity: VALID
# ✅ User Context: VALID (2 users)
# ✅ Team Context: VALID
# 📊 Compliance Level: STANDARD (Level 2)

# Inspect sections
steward inspect
# Output:
# ✅ Agent Identity: PRESENT
# ✅ User Context: PRESENT (kim, alex)
# ✅ Team Context: PRESENT
# ⚠️  Runtime Introspection: NOT IMPLEMENTED (required for Level 3)

# Test user context
steward test --user kim
# Output:
# ✅ User 'kim' found
# Settings applied:
#   - workflow_style: test_first
#   - verbosity: low
#   - communication: concise_technical
#   - language: de-DE
```

### Examples

#### Example 1: Solo Developer (Minimal - Level 1)
```markdown
# STEWARD.md

## AGENT IDENTITY
- **ID**: my-simple-agent
- **Version**: 1.0.0
- **Class**: task_executor

# That's it! No user context needed.
```

#### Example 2: Solo Developer with Preferences (Level 2)
```markdown
# STEWARD.md

## AGENT IDENTITY
- **ID**: my-agent
- **Version**: 1.0.0

## USER CONTEXT
default_user:
  verbosity: "low"
  workflow: "test_first"
  language: "en-US"
```

#### Example 3: Team with Multiple Users (Level 2 Full)
```markdown
# STEWARD.md

## AGENT IDENTITY
[... full agent manifest ...]

## USER CONTEXT

### kim:
  role: "Tech Lead"
  verbosity: "low"
  workflow: "test_first"

### alex:
  role: "Developer"
  verbosity: "medium"
  workflow: "iterative"

### team:
  development_style: "test_driven"
  min_coverage: 0.80
```

### Benefits

✅ **Single Source of Truth**: One file (`STEWARD.md`) for agent + operators
✅ **Backwards Compatible**: Existing STEWARD.md (agent-only) still works
✅ **Graceful Degradation**: Each level works independently
✅ **Scalable**: 1 user → 100 users, same structure
✅ **Privacy-Friendly**: Sensitive data can be gitignored
✅ **Team-Friendly**: Consistent behavior across team members
✅ **Session Persistence**: Context survives across sessions

### Relationship to steward.json

- **STEWARD.md** (human-readable): Agent identity + user context + team context
- **steward.json** (machine-readable): Agent identity only (for protocol compliance)

User context is intentionally NOT in `steward.json` because:
1. User preferences are operational, not protocol-level
2. Privacy concerns (don't expose personal preferences in public manifest)
3. Keeps steward.json focused on agent identity/capabilities

---

## 🔍 LAYER 2: STEWARD REGISTRY

### Like: Docker Hub, npm registry, PyPI

**Components:**

1. **Agent Index** (search & discovery)
   ```bash
   steward search --capability "sdlc_orchestration"
   steward search --specialization "healthcare_compliance"
   steward search --trust-score ">0.9"
   ```

2. **Version Store** (capability history)
   ```bash
   steward versions vibe-agency-orchestrator
   # Output:
   # 4.0.0 (latest) - Added hybrid agent pattern
   # 3.9.0 - Kernel/Agency split
   # 3.8.0 - RouterBridge integration
   ```

3. **Reputation System** (trust scores)
   ```json
   {
     "agent_id": "vibe-agency-orchestrator",
     "trust_score": 0.96,
     "factors": {
       "test_coverage": 0.96,
       "uptime": 1.00,
       "successful_delegations": 1247,
       "endorsements": 42
     }
   }
   ```

4. **Audit Logs** (delegation trail)
   ```bash
   steward audit vibe-agency-orchestrator --last-30-days
   # Output: All delegations, results, errors
   ```

**Registry Implementation Options:**

### Option A: Centralized Registry (like npm)
- ✅ Simple, fast lookup
- ❌ Single point of failure
- ❌ Centralized trust

### Option B: Federated Registry (like email, Mastodon)
- ✅ No single point of failure
- ✅ Decentralized trust
- ❌ Complex discovery
- ❌ Consistency challenges

### Option C: Git-Based Registry (like Homebrew)
- ✅ Version control built-in
- ✅ Transparent history
- ✅ No infrastructure needed
- ❌ No real-time updates
- ❌ Limited search

**Recommendation:** Start with **Option C (Git-Based)**, evolve to **Option B (Federated)** when scale requires.

---

## 🔐 LAYER 3: VERIFICATION PROTOCOL

### Problem: How do agents trust each other?

**Like:** SSL/TLS certificates, PGP web of trust, OAuth

### Solution: Cryptographic Identity + Capability Attestation

1. **Agent Identity (Signing)**
   ```bash
   # Generate agent keypair
   steward keygen --agent-id vibe-agency-orchestrator
   # → steward_id_rsa (private key, NEVER share)
   # → steward_id_rsa.pub (public key, publish)

   # Sign manifest
   steward sign steward.json --key steward_id_rsa
   # → steward.json.sig (cryptographic signature)
   ```

2. **Verification (by requesting agent)**
   ```bash
   # Download manifest + signature
   curl https://raw.githubusercontent.com/kimeisele/vibe-agency/main/steward.json
   curl https://raw.githubusercontent.com/kimeisele/vibe-agency/main/steward.json.sig

   # Verify signature
   steward verify steward.json --signature steward.json.sig --pubkey steward_id_rsa.pub
   # → ✅ VALID: Signature matches agent fingerprint
   ```

3. **Capability Attestation**
   ```bash
   # Attest capability (run test suite, generate proof)
   steward attest --capability orchestrate_sdlc
   # → Runs tests, generates attestation certificate
   # → attestation_orchestrate_sdlc_2025-11-21.json

   # Requesting agent verifies attestation
   steward verify-attestation attestation_orchestrate_sdlc_2025-11-21.json
   # → ✅ VALID: 369/383 tests passing (96%), verified by trusted CI
   ```

4. **Trust Chain**
   ```
   vibe-agency (root authority)
     └─ STEWARD v4.0.0 (signed by vibe-agency)
         ├─ Capability: orchestrate_sdlc (attested by CI/CD)
         ├─ Test Suite: 369/383 passing (attested by pytest)
         └─ Uptime: 100% (attested by monitoring)
   ```

---

## 🤝 LAYER 4: DELEGATION PROTOCOL

### Problem: How do agents delegate tasks to each other?

**Like:** REST API, gRPC, GraphQL, JSON-RPC

### Solution: Standardized Delegation API

```bash
# 1. Discovery
steward discover --capability "restaurant_app_planning"
# → Found: vibe-agency-orchestrator (trust_score: 0.96)

# 2. Verification
steward verify vibe-agency-orchestrator
# → ✅ Identity verified, capabilities attested

# 3. Delegation
steward delegate vibe-agency-orchestrator \
  --task orchestrate_sdlc \
  --context '{
    "domain": "restaurant",
    "scale": "multi_location",
    "integrations": ["pos_system", "delivery_apis"]
  }' \
  --quality '>0.8' \
  --timeout 600s
# → Task submitted: task-id-abc123

# 4. Monitoring
steward monitor task-id-abc123
# → Status: RUNNING (phase: PLANNING, progress: 45%)

# 5. Results
steward result task-id-abc123
# → ✅ SUCCESS: artifacts/architecture.md (validated, test_coverage: 0.96)
```

### Delegation Payload Format

```json
{
  "protocol_version": "1.0.0",
  "delegation": {
    "task_id": "task-id-abc123",
    "requesting_agent": {
      "id": "external-planning-agent-1.0",
      "fingerprint": "sha256:xyz789...",
      "signature": "..."
    },
    "target_agent": {
      "id": "vibe-agency-orchestrator-4.0",
      "operation": "orchestrate_sdlc"
    },
    "payload": {
      "domain": "restaurant",
      "scale": "multi_location",
      "integrations": ["pos_system", "delivery_apis"]
    },
    "constraints": {
      "min_test_coverage": 0.8,
      "max_latency_ms": 600000,
      "required_quality": 0.9
    },
    "callback": {
      "type": "webhook",
      "url": "https://requesting-agent.example.com/callback",
      "auth": "Bearer token123..."
    }
  }
}
```

---

## 🛠️ LAYER 5: STEWARD CLI

### Commands

```bash
# ===== AGENT INITIALIZATION =====
steward init                    # Initialize new agent (creates steward.json)
steward keygen                  # Generate keypair for signing
steward sign                    # Sign manifest with private key

# ===== DISCOVERY =====
steward search <query>          # Search agent registry
steward discover --capability   # Find agents by capability
steward info <agent-id>         # Show agent details

# ===== VERIFICATION =====
steward verify <agent-id>       # Verify agent identity
steward verify-attestation      # Verify capability attestation
steward trust <agent-id>        # Add agent to trusted list

# ===== DELEGATION =====
steward delegate <agent-id>     # Delegate task to agent
steward monitor <task-id>       # Monitor task progress
steward result <task-id>        # Get task results
steward cancel <task-id>        # Cancel running task

# ===== INTROSPECTION =====
steward status                  # Show agent health
steward introspect              # Show runtime state
steward logs                    # Show agent logs
steward audit                   # Show delegation history

# ===== REGISTRY =====
steward publish                 # Publish agent to registry
steward versions <agent-id>     # Show version history
steward pull <agent-id>         # Download agent manifest
```

---

## 🔄 STALENESS PROBLEM: SOLUTIONS

### Problem: Static STEWARD.md becomes outdated

### Solution 1: Runtime Introspection API
```bash
# Instead of reading static steward.json, query live agent:
steward introspect vibe-agency-orchestrator --endpoint ./bin/vibe
# → Returns CURRENT state (tests passing, versions, capabilities)
```

### Solution 2: Versioned Manifests
```bash
# Multiple versions tracked in registry:
steward versions vibe-agency-orchestrator
# 4.0.0 (2025-11-21) - Current, verified 1h ago
# 3.9.0 (2025-11-20) - Deprecated
# 3.8.0 (2025-11-18) - Archived
```

### Solution 3: Health Checks + Attestation Expiry
```json
{
  "capabilities": {
    "orchestrate_sdlc": {
      "attested_date": "2025-11-21T10:00:00Z",
      "expires": "2025-11-22T10:00:00Z",
      "health_check": "./bin/vibe status --json"
    }
  }
}
```

**Requesting agents can:**
1. Check if attestation expired
2. Run health check to verify liveness
3. Request fresh attestation if needed

### Solution 4: Git-Based Continuous Verification
```yaml
# .github/workflows/steward-verify.yml
name: STEWARD Verification
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: ./bin/verify-claude-md.sh
      - run: steward attest --all-capabilities
      - run: git commit -m "Update attestations"
      - run: git push
```

**Result:** steward.json is auto-updated every 6 hours with fresh attestations.

---

## 🌍 REGISTRY OPTIONS: COMPARISON

| Feature | Git-Based | Centralized | Federated |
|---------|-----------|-------------|-----------|
| **Infrastructure** | None (use GitHub) | Requires servers | Requires coordination |
| **Discovery** | Basic (git search) | Fast (DB index) | Complex (multi-registry) |
| **Versioning** | Built-in (git) | Custom | Custom |
| **Trust** | GitHub trust | Single authority | Web of trust |
| **Offline** | ✅ Clone repo | ❌ Need internet | ⚠️ Partial |
| **Censorship Resistance** | ⚠️ GitHub controls | ❌ Registry controls | ✅ Fully distributed |
| **Speed** | Slow (clone repo) | Fast (API) | Medium (DNS-like) |

**Phase 1 Recommendation:** Git-Based (MVP)
**Phase 2 Recommendation:** Federated (scale + resilience)

---

## 📚 COMPARISON: STEWARD vs Existing Standards

### vs Docker
| Feature | Docker | STEWARD |
|---------|--------|---------|
| **Purpose** | Container runtime | Agent coordination |
| **Manifest** | Dockerfile | steward.json |
| **Registry** | Docker Hub | STEWARD Registry |
| **Discovery** | `docker search` | `steward discover` |
| **Execution** | `docker run` | `steward delegate` |
| **Trust** | Image signing | Agent signing + attestation |

### vs OpenAPI/Swagger
| Feature | OpenAPI | STEWARD |
|---------|---------|---------|
| **Purpose** | API documentation | Agent capability declaration |
| **Format** | YAML/JSON | steward.json |
| **Discovery** | SwaggerHub | STEWARD Registry |
| **Verification** | Schema validation | Cryptographic signing + tests |
| **Delegation** | HTTP calls | `steward delegate` |

### vs LinkedIn
| Feature | LinkedIn | STEWARD |
|---------|----------|---------|
| **Purpose** | Professional networking | Agent networking |
| **Profile** | Resume/CV | steward.json |
| **Skills** | Self-declared + endorsed | Cryptographically attested |
| **Discovery** | Search + filters | `steward discover` |
| **Trust** | Endorsements + recommendations | Test pass rate + attestations |
| **Reputation** | Profile views + connections | Trust score + delegation history |

---

## 💰 ECONOMIC MODEL (Optional)

### Problem: Agent Monetization

Agents may provide services that require compensation:
- **Free tier**: Basic capabilities (discovery, verification)
- **Paid tier**: Premium capabilities (high-priority delegation, SLA guarantees)
- **Usage-based**: Pay per delegation, per compute time, per result quality

### Pricing Declaration

Agents can declare pricing in `steward.json`:

```json
{
  "pricing": {
    "model": "free",  // "free", "pay_per_use", "subscription", "hybrid"
    "currency": "USD",
    "free_tier": {
      "included": [
        "discovery",
        "verification",
        "basic_delegation"
      ],
      "limits": {
        "delegations_per_day": 10,
        "max_task_duration_minutes": 5
      }
    },
    "paid_tiers": [
      {
        "name": "standard",
        "model": "pay_per_use",
        "rates": {
          "orchestrate_sdlc": {
            "cost_per_invocation": 0.10,
            "billing_unit": "per_invocation",
            "estimated_duration_minutes": 10
          },
          "generate_code": {
            "cost_per_invocation": 0.05,
            "billing_unit": "per_invocation"
          }
        }
      },
      {
        "name": "premium",
        "model": "subscription",
        "cost_per_month": 99.00,
        "includes": {
          "unlimited_delegations": true,
          "priority_queue": true,
          "sla_guarantee": "99.9% uptime",
          "max_latency_p99_ms": 2000
        }
      }
    ]
  }
}
```

### Payment Flow

```
1. Client discovers agent
   ├─ Check pricing model
   └─ Choose tier (free/standard/premium)

2. Client delegates task
   ├─ Include payment authorization
   └─ Agent validates payment

3. Agent executes task
   ├─ Track resource usage
   └─ Calculate cost

4. Agent returns results + invoice
   ├─ Client validates invoice
   └─ Payment processed

5. Payment confirmation
   ├─ Agent receives funds
   └─ Transaction logged
```

### Payment Methods

```json
{
  "pricing": {
    "payment_methods": [
      {
        "type": "cryptocurrency",
        "chains": ["ethereum", "polygon"],
        "tokens": ["USDC", "DAI"],
        "payment_address": "0x..."
      },
      {
        "type": "fiat",
        "providers": ["stripe", "paypal"],
        "payment_endpoint": "https://payments.example.com/invoice"
      },
      {
        "type": "credits",
        "provider": "agent_marketplace",
        "credit_system": "steward_credits"
      }
    ]
  }
}
```

### Cost Estimation

Clients can estimate costs before delegating:

```bash
$ steward estimate vibe-agency-orchestrator \
    --operation orchestrate_sdlc \
    --context '{"complexity": "medium", "duration_estimate": "10min"}'

Cost Estimation:
  Operation: orchestrate_sdlc
  Tier: standard (pay-per-use)
  Base cost: $0.10 per invocation
  Estimated duration: 10 minutes
  Additional fees: None

  Total estimated cost: $0.10

Proceed with delegation? [y/N]:
```

### Billing & Invoicing

```json
{
  "invoice": {
    "invoice_id": "inv-abc123",
    "task_id": "task-xyz789",
    "agent_id": "vibe-agency-orchestrator",
    "client_id": "requesting-agent-1.0",

    "line_items": [
      {
        "description": "orchestrate_sdlc invocation",
        "quantity": 1,
        "unit_price": 0.10,
        "total": 0.10
      },
      {
        "description": "Compute time (10 minutes)",
        "quantity": 10,
        "unit_price": 0.01,
        "total": 0.10
      }
    ],

    "subtotal": 0.20,
    "tax": 0.02,
    "total": 0.22,

    "payment_due": "2025-11-28T00:00:00Z",
    "payment_status": "pending"
  }
}
```

### Revenue Sharing (Registry Fees)

Registries may charge fees for listing agents:

```yaml
registry_fees:
  listing_fee:
    free_tier: 0  # Free for basic listing
    verified_tier: 10  # $10/month for verified badge
    featured_tier: 100  # $100/month for featured placement

  transaction_fee:
    percentage: 2.5  # 2.5% of transaction value
    applies_to: "paid_delegations_only"

  revenue_split:
    agent: 0.95  # 95% to agent
    registry: 0.025  # 2.5% to registry
    protocol: 0.025  # 2.5% to protocol development
```

### Free vs Paid Decision Matrix

| Factor | Free | Paid |
|--------|------|------|
| **Compute cost** | Low (< $0.01/request) | High (> $0.10/request) |
| **Development cost** | Low | High (custom models, infrastructure) |
| **Target users** | Hobbyists, students | Enterprises, professionals |
| **SLA required** | No | Yes |
| **Support** | Community | Dedicated |

### Examples

#### Example 1: Free Agent (Open Source)
```json
{
  "pricing": {
    "model": "free",
    "rationale": "Open source project, funded by donations"
  }
}
```

#### Example 2: Freemium Agent
```json
{
  "pricing": {
    "model": "hybrid",
    "free_tier": {
      "delegations_per_day": 10,
      "max_duration_minutes": 5
    },
    "paid_tier": {
      "cost_per_delegation": 0.10,
      "unlimited": true
    }
  }
}
```

#### Example 3: Enterprise Agent
```json
{
  "pricing": {
    "model": "subscription",
    "tiers": [
      { "name": "team", "cost": 299, "seats": 10 },
      { "name": "enterprise", "cost": 999, "seats": "unlimited" }
    ],
    "sla": "99.9% uptime",
    "support": "24/7"
  }
}
```

### Important Notes

**Economic model is OPTIONAL:**
- Not required for protocol compliance
- Agents can be 100% free
- Useful for commercial agents

**Trust score impact:**
- Paid agents don't automatically get higher trust
- Trust based on technical metrics, not pricing
- Expensive ≠ Better

**Transparency required:**
- Pricing must be declared upfront in manifest
- No hidden fees
- No price changes mid-delegation

---

## 🎯 IMPLEMENTATION ROADMAP

### Phase 1: MVP (4 weeks)
- [ ] **Week 1**: Define `steward.json` schema (JSON Schema spec)
- [ ] **Week 2**: Build `steward` CLI (basic commands: init, verify, delegate)
- [ ] **Week 3**: Git-based registry (GitHub as index)
- [ ] **Week 4**: Cryptographic signing + verification

### Phase 2: Protocol Extensions (8 weeks)
- [ ] Health checks + introspection API
- [ ] Attestation expiry + refresh
- [ ] Reputation system (trust scores)
- [ ] Monitoring + audit logs

### Phase 3: Federated Registry (12 weeks)
- [ ] Federated discovery protocol
- [ ] Cross-registry search
- [ ] Reputation aggregation
- [ ] Web of trust implementation

---

## 💡 NEXT STEPS

1. **Validate Design** with community feedback
2. **Write JSON Schema** for `steward.json`
3. **Build Proof-of-Concept CLI** (`steward` command)
4. **Implement Git-Based Registry** (MVP)
5. **Publish STEWARD Protocol RFC** for wider adoption

---

## 🤝 CONTRIBUTING

This is a **DRAFT** specification. Feedback welcome:
- GitHub Issues: `kimeisele/vibe-agency`
- Discussion: `docs/drafts/steward/` directory

---

**Remember:** This is "Docker for AI Agents" - standardized identity, discovery, verification, and delegation for the AI Agent Economy.

**Status:** 🚧 DRAFT - Seeking feedback
**Next Milestone:** JSON Schema + MVP CLI
