# STEWARD Protocol - Graceful Degradation

**Status:** ✅ STABLE
**Last Updated:** 2025-11-21

---

## 🎯 VISION: Universal Compatibility

**Problem:** Not all agents need (or can implement) the full STEWARD Protocol.

**Solution:** **Graceful Degradation** - multiple compliance levels that work together.

---

## 📊 FOUR COMPLIANCE LEVELS

```
┌─────────────────────────────────────────────────────────────┐
│ Level 1: MINIMAL (Human-Readable Only)                      │
│  - Root STEWARD.md (lean, for humans & AI operators)       │
│  - No machine-readable format                               │
│  - Better than nothing!                                     │
│                                                             │
│  Use Case: Small projects, hobbyist agents, MVP            │
│  Effort: 30 minutes                                         │
└─────────────────────────────────────────────────────────────┘
                          ↓ UPGRADE
┌─────────────────────────────────────────────────────────────┐
│ Level 2: STANDARD (Hybrid) ← RECOMMENDED                   │
│  - Root STEWARD.md (human-readable summary)                │
│  - steward.json (machine-readable manifest)                │
│  - Best of both worlds!                                     │
│                                                             │
│  Use Case: Production agents, serious projects             │
│  Effort: 2-4 hours                                          │
└─────────────────────────────────────────────────────────────┘
                          ↓ UPGRADE
┌─────────────────────────────────────────────────────────────┐
│ Level 3: ADVANCED (Runtime Introspection)                   │
│  - STEWARD.md + steward.json                                │
│  - Live attestations (auto-refresh)                         │
│  - Health check endpoints                                   │
│  - Dynamic trust scores                                     │
│                                                             │
│  Use Case: High-trust operations, SLA requirements          │
│  Effort: 1-2 days                                           │
└─────────────────────────────────────────────────────────────┘
                          ↓ UPGRADE
┌─────────────────────────────────────────────────────────────┐
│ Level 4: FULL PROTOCOL (CLI + Federation)                   │
│  - All of above                                             │
│  - steward CLI tools                                        │
│  - Federated registry                                       │
│  - Complete ecosystem                                       │
│                                                             │
│  Use Case: Agent ecosystems, marketplaces                   │
│  Effort: 1-2 weeks                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎚️ LEVEL 1: MINIMAL

### What You Need

**Single file:** `STEWARD.md` in repository root

**Minimum content:**
- Agent name & version
- What it does (1-2 sentences)
- Core capabilities (3-5 bullet points)
- How to use it (basic commands)
- Who maintains it

**Size:** ~50-100 lines

### Example: STEWARD_MINIMAL.md

```markdown
# STEWARD.md

## Agent Identity
- **Name:** simple-code-generator
- **Version:** 1.0.0
- **Status:** ACTIVE

## What I Do
Generate Python code from natural language descriptions.

## Core Capabilities
- Generate functions from docstrings
- Generate test cases from functions
- Refactor code for readability

## How to Use
```bash
python simple_code_gen.py "create a function that sorts a list"
```

## Maintained By
GitHub: @username
```

### Pros
- ✅ Zero setup (just markdown)
- ✅ Human & AI readable
- ✅ Works with any operator (Claude, GPT, etc.)

### Cons
- ❌ Not machine-parseable
- ❌ No agent-to-agent delegation
- ❌ No automatic discovery

### When to Use
- Hobby projects
- Internal tools (not public agents)
- MVP/prototype phase
- Learning STEWARD Protocol

---

## 🎚️ LEVEL 2: STANDARD (Recommended)

### What You Need

**Two files:**
1. `STEWARD.md` (human-readable summary)
2. `steward.json` (machine-readable manifest)

**STEWARD.md content:**
- Agent identity card
- Link to steward.json
- Quick start guide
- Trust score summary
- Attestation status

**steward.json content:**
- Full agent manifest (per JSON Schema)
- Capabilities declaration
- Quality metrics
- Interfaces & operations

**Size:** ~200 lines (md) + JSON manifest

### Example: STEWARD_STANDARD.md

```markdown
# STEWARD.md

> **STEWARD Protocol v1.0.0 Compliant (Level 2: Standard)**
> Machine-readable manifest: [steward.json](./steward.json)

## 🆔 Agent Identity
- **ID:** code-generator-pro-1.0
- **Name:** CodeGenPro
- **Class:** Code Generator
- **Version:** 1.0.0
- **Status:** 🟢 ACTIVE
- **Trust Score:** 0.89 ⭐⭐⭐⭐ (Trusted)

## 🎯 What I Do
Professional-grade code generation with test coverage, documentation, and quality guarantees.

## ✅ Core Capabilities
- `generate_function` - Generate Python functions from specs
- `generate_tests` - Generate pytest test suites
- `refactor_code` - Refactor for readability & performance
- `generate_docs` - Generate docstrings & README

## 📊 Quality Guarantees
- **Test Coverage:** 92% (target: >90%)
- **Uptime:** 98.5% (last 30 days)
- **Success Rate:** 96% (1847/1923 delegations)
- **Latency P99:** 3.2s (target: <5s)

## 🔐 Verification
```bash
# Verify identity
steward verify code-generator-pro

# Check attestations
steward attestation-status code-generator-pro
```

## 🚀 Quick Start

### Discover & Delegate
```bash
# Discover this agent
steward discover --capability generate_function

# Delegate task
steward delegate code-generator-pro \
  --operation generate_function \
  --context '{"spec": "sort list of integers", "include_tests": true}'
```

### Direct Usage (Non-Protocol)
```bash
python codegen_pro.py "create a function that sorts a list"
```

## 📋 Attestations
- **Last Attested:** 2 hours ago (2025-11-21T11:00:00Z)
- **Expires:** 22 hours (2025-11-22T11:00:00Z)
- **Status:** ✅ VALID

## 🤝 For Other Agents
```python
# Agent-to-agent delegation (Python example)
from steward import delegate

result = delegate(
    agent_id="code-generator-pro",
    operation="generate_function",
    context={"spec": "...", "include_tests": True}
)
```

## 👤 Maintained By
- **Organization:** CodeGen Labs
- **Contact:** https://github.com/codegenl abs/codegen-pro
- **Support:** support@codegenlabs.com

## 📚 More Info
- **Full Manifest:** [steward.json](./steward.json)
- **Trust Report:** [View Trust Score Breakdown](https://steward-registry.org/agents/code-generator-pro/trust-report)
- **Protocol Docs:** [STEWARD Protocol](https://github.com/kimeisele/vibe-agency/tree/main/docs/protocols/steward)

---

**STEWARD Protocol Compliance:** Level 2 (Standard) ✅
**Protocol Version:** 1.0.0
**Last Updated:** 2025-11-21
```

### Pros
- ✅ Human & machine-readable
- ✅ Agent-to-agent delegation works
- ✅ Discoverable in registry
- ✅ Cryptographically verifiable

### Cons
- ⚠️ Attestations may become stale (manual refresh)
- ⚠️ No real-time introspection

### When to Use
- **Production agents** (recommended)
- Public agents in marketplace
- Agents with SLA requirements
- Commercial services

---

## 🎚️ LEVEL 3: ADVANCED

### What You Need

**All of Level 2, plus:**
- Attestation auto-refresh (CI/CD)
- Health check endpoints
- Runtime introspection API
- Trust score monitoring

**Infrastructure:**
- GitHub Actions (or similar CI/CD)
- Monitoring service (optional)
- Health check endpoint (HTTP)

**Effort:** ~1-2 days setup

### Additional Features

#### 1. Auto-Refresh Attestations (CI/CD)
```yaml
# .github/workflows/steward-attest.yml
name: STEWARD Attestation Refresh
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  attest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: uv run pytest tests/ -v
      - run: steward attest --all-capabilities
      - run: git commit -m "Update attestations"
      - run: git push
```

#### 2. Health Check Endpoint
```python
# health_check.py
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "uptime_seconds": get_uptime(),
        "last_test_run": "2025-11-21T11:00:00Z",
        "test_pass_rate": 0.92
    })

@app.route('/introspect')
def introspect():
    return jsonify({
        "agent_id": "code-generator-pro",
        "active_tasks": 3,
        "queued_tasks": 7,
        "success_rate_24h": 0.96,
        "latency_p99_ms": 3200
    })
```

#### 3. Trust Score Monitoring
```bash
# Monitor trust score
steward trust-score code-generator-pro --watch

# Alert if trust drops below threshold
steward alert trust-score code-generator-pro \
  --threshold 0.85 \
  --notify slack://webhook-url
```

### Pros
- ✅ Always up-to-date attestations
- ✅ Real-time health status
- ✅ Proactive trust monitoring

### Cons
- ⚠️ Requires CI/CD setup
- ⚠️ More infrastructure overhead

### When to Use
- High-trust operations (financial, healthcare)
- SLA-bound services (99.9% uptime guarantee)
- Enterprise agents
- Critical infrastructure agents

---

## 🎚️ LEVEL 4: FULL PROTOCOL

### What You Need

**All of Level 3, plus:**
- `steward` CLI installed
- Published to federated registry
- Full cryptographic signing
- Multi-sig support (optional)

**Infrastructure:**
- Registry participation (push attestations)
- Monitoring dashboard
- Key management (KMS)
- Backup & disaster recovery

**Effort:** ~1-2 weeks setup

### Additional Features

#### 1. CLI Operations
```bash
# Initialize agent
steward init

# Generate keys
steward keygen

# Sign manifest
steward sign steward.json

# Publish to registry
steward publish

# Monitor delegations
steward monitor --live
```

#### 2. Federated Registry
```bash
# Publish to multiple registries
steward publish \
  --registry https://steward-registry.org \
  --registry https://backup-registry.example.com

# Cross-registry discovery
steward discover --capability generate_code --federated
```

#### 3. Advanced Security
```bash
# Multi-sig signing (requires 2 of 3 keys)
steward sign steward.json \
  --multi-sig \
  --signers "team-member-1,team-member-2,team-member-3" \
  --threshold 2

# Key rotation
steward rotate-key --grace-period 30d
```

### Pros
- ✅ Complete protocol compliance
- ✅ Maximum trust & discoverability
- ✅ Enterprise-grade security
- ✅ Full ecosystem participation

### Cons
- ⚠️ Significant infrastructure investment
- ⚠️ Ongoing maintenance overhead

### When to Use
- Agent marketplaces
- Multi-tenant platforms
- Ecosystem builders
- Protocol contributors

---

## 🔄 MIGRATION PATH

### From Nothing → Level 1 (30 min)
```bash
# Create basic STEWARD.md
cp docs/protocols/steward/templates/STEWARD_TEMPLATE.md STEWARD.md
# Fill in agent details
vim STEWARD.md
# Commit
git add STEWARD.md && git commit -m "Add STEWARD.md (Level 1)"
```

### From Level 1 → Level 2 (2-4 hours)
```bash
# Create steward.json
steward init  # Interactive manifest builder

# Add to STEWARD.md
echo "Machine-readable manifest: [steward.json](./steward.json)" >> STEWARD.md

# Sign manifest
steward keygen
steward sign steward.json

# Commit
git add steward.json steward.json.sig STEWARD.md
git commit -m "Upgrade to Level 2 (Standard)"
```

### From Level 2 → Level 3 (1-2 days)
```bash
# Setup CI/CD attestation refresh
cp docs/protocols/steward/examples/github-actions-attest.yml .github/workflows/

# Add health check endpoint
cp docs/protocols/steward/examples/health_check.py ./

# Deploy health check
python health_check.py &

# Update steward.json with endpoints
vim steward.json  # Add health_check, introspection endpoints

# Commit
git add .github/workflows/ health_check.py steward.json
git commit -m "Upgrade to Level 3 (Advanced)"
```

### From Level 3 → Level 4 (1-2 weeks)
```bash
# Install steward CLI
pip install steward-cli

# Publish to registry
steward publish --registry https://steward-registry.org

# Setup monitoring
steward monitor --dashboard https://monitor.example.com

# Enable federation
steward federate \
  --primary-registry steward-registry.org \
  --backup-registry backup-registry.example.com

# Commit
git add steward_config.yml
git commit -m "Upgrade to Level 4 (Full Protocol)"
```

---

## 📊 COMPARISON MATRIX

| Feature | Level 1 | Level 2 | Level 3 | Level 4 |
|---------|---------|---------|---------|---------|
| **Human-readable** | ✅ | ✅ | ✅ | ✅ |
| **Machine-readable** | ❌ | ✅ | ✅ | ✅ |
| **Agent-to-Agent delegation** | ❌ | ✅ | ✅ | ✅ |
| **Registry discovery** | ❌ | ✅ | ✅ | ✅ |
| **Cryptographic signing** | ❌ | ✅ | ✅ | ✅ |
| **Attestation auto-refresh** | ❌ | ❌ | ✅ | ✅ |
| **Health checks** | ❌ | ❌ | ✅ | ✅ |
| **Runtime introspection** | ❌ | ❌ | ✅ | ✅ |
| **CLI tools** | ❌ | ❌ | ❌ | ✅ |
| **Federated registry** | ❌ | ❌ | ❌ | ✅ |
| **Multi-sig support** | ❌ | ❌ | ❌ | ✅ |
| **Setup time** | 30min | 2-4h | 1-2d | 1-2w |
| **Maintenance** | None | Low | Medium | High |

---

## 🎯 RECOMMENDATION

### Choose Level Based On:

**Level 1 (Minimal):**
- ✅ Hobby project
- ✅ Internal tool
- ✅ Learning protocol
- ✅ MVP phase

**Level 2 (Standard) ← RECOMMENDED:**
- ✅ Production agent
- ✅ Public marketplace
- ✅ Serious project
- ✅ SLA commitments

**Level 3 (Advanced):**
- ✅ High-trust operations
- ✅ Enterprise services
- ✅ 99.9% uptime SLA
- ✅ Real-time monitoring

**Level 4 (Full Protocol):**
- ✅ Agent marketplace
- ✅ Ecosystem platform
- ✅ Protocol contributor
- ✅ Maximum trust required

---

## ✅ VALIDATION

### How to Check Your Level

```bash
$ steward level STEWARD.md

Analyzing STEWARD compliance...

Level 1 (Minimal): ✅ PASS
  ✅ STEWARD.md exists
  ✅ Has agent identity
  ✅ Has capabilities list

Level 2 (Standard): ✅ PASS
  ✅ steward.json exists
  ✅ Manifest valid
  ✅ Cryptographically signed

Level 3 (Advanced): ❌ FAIL
  ❌ No health check endpoint
  ❌ Attestations not auto-refreshing

Level 4 (Full Protocol): ❌ NOT CHECKED

Overall: Level 2 (Standard) ✅
Recommendation: Upgrade to Level 3 for better trust
```

---

## 📚 EXAMPLES

See `docs/protocols/steward/examples/` for:
- `minimal/` - Level 1 examples
- `standard/` - Level 2 examples (vibe-agency)
- `advanced/` - Level 3 examples
- `full/` - Level 4 examples

---

**Status:** ✅ STABLE - Graceful degradation model complete
**Next:** Create templates for each level + vibe-agency reference implementation
