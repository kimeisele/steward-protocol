# STEWARD.md Template

> **STEWARD Protocol v1.0.0 Template**
> *Graceful Degradation: Choose your compliance level*

**📖 Instructions:** This template supports 4 compliance levels. Fill in sections based on your target level:
- **Level 1 (Minimal):** Fill sections marked `[REQUIRED]`
- **Level 2 (Standard):** Fill `[REQUIRED]` + `[STANDARD]` ← **Recommended**
- **Level 3 (Advanced):** Fill `[REQUIRED]` + `[STANDARD]` + `[ADVANCED]`
- **Level 4 (Full Protocol):** Fill all sections

**See:** [GRACEFUL_DEGRADATION.md](../GRACEFUL_DEGRADATION.md) for level details

---

## 🆔 Agent Identity `[REQUIRED]`

> Fill in your agent's core identity information

- **ID:** `[your-agent-id]` (lowercase, kebab-case, e.g., `vibe-agency-orchestrator`)
- **Name:** `[Your Agent Name]` (human-readable, e.g., `STEWARD`)
- **Class:** `[Agent Type]` (e.g., `orchestration_operator`, `code_generator`, `research_agent`)
- **Version:** `[X.Y.Z]` (semver, e.g., `1.0.0`)
- **Status:** `[ACTIVE|DEVELOPMENT|MAINTENANCE|DEPRECATED]`

**`[STANDARD]` Additional fields:**
- **Fingerprint:** `sha256:[your-key-fingerprint]` (run `steward keygen` to generate)
- **Trust Score:** `[0.XX]` ⭐ (e.g., `0.94 ⭐⭐⭐⭐ (Highly Trusted)`)
- **Protocol Compliance:** `Level [1|2|3|4]`

---

## 🎯 What I Do `[REQUIRED]`

> 1-2 sentence description of what your agent does

```
[Your agent description here. Be concise and specific.]

Example: "Professional-grade code generation with test coverage, documentation,
and quality guarantees. Specializes in Python, JavaScript, and TypeScript."
```

---

## ✅ Core Capabilities `[REQUIRED]`

> List 3-5 main capabilities (what your agent can do)

- `[capability_name_1]` - [Brief description]
- `[capability_name_2]` - [Brief description]
- `[capability_name_3]` - [Brief description]
- `[capability_name_4]` - [Brief description]
- `[capability_name_5]` - [Brief description]

**Examples:**
- `generate_function` - Generate Python functions from natural language specs
- `generate_tests` - Generate pytest test suites with 90%+ coverage
- `refactor_code` - Refactor for readability, performance, and maintainability

---

## 🚀 Quick Start `[REQUIRED]`

> Show users how to use your agent

### Basic Usage

```bash
# [Your basic usage command]
# Example: python your_agent.py "task description"
```

**`[STANDARD]` Protocol-based usage:**

```bash
# Discover this agent
steward discover --capability [your-capability]

# Verify identity
steward verify [your-agent-id]

# Delegate task
steward delegate [your-agent-id] \
  --operation [operation-name] \
  --context '{"key": "value"}'
```

---

## 📊 Quality Guarantees `[STANDARD]`

> Declare your quality metrics (Level 2+)

**Current Metrics:**
- **Test Coverage:** [XX]% (target: >[YY]%)
- **Uptime:** [XX]% (last 30 days)
- **Success Rate:** [XX]% ([successful]/[total] delegations)
- **Latency P99:** [X.X]s (target: <[Y]s)

**`[ADVANCED]` Live Metrics:**
- **Health Check:** `[https://your-agent.com/health]` (refresh every 5min)
- **Introspection API:** `[https://your-agent.com/introspect]`
- **Monitoring Dashboard:** `[https://monitor.your-agent.com]`

---

## 🔐 Verification `[STANDARD]`

> Enable cryptographic verification (Level 2+)

### Identity Verification

```bash
# Verify agent signature
steward verify [your-agent-id]

# Expected output:
# ✅ Identity verified
# ✅ Signature valid: sha256:[your-fingerprint]
# ✅ Capabilities attested (Xh ago)
```

### Manifest & Attestations

- **Machine-readable manifest:** [steward.json](./steward.json)
- **Last attested:** [X hours ago] ([YYYY-MM-DD]T[HH:MM:SS]Z)
- **Attestation expires:** [Y hours] ([YYYY-MM-DD]T[HH:MM:SS]Z)
- **Status:** ✅ VALID / ⚠️ EXPIRING / ❌ EXPIRED

**`[ADVANCED]` Auto-refresh:**
- **CI/CD:** Attestations auto-refresh every 6 hours via GitHub Actions
- **See:** [.github/workflows/steward-attest.yml](./.github/workflows/steward-attest.yml)

---

## 🤝 For Other Agents `[STANDARD]`

> Enable agent-to-agent delegation (Level 2+)

### Python Example

```python
from steward import delegate

result = delegate(
    agent_id="[your-agent-id]",
    operation="[operation-name]",
    context={
        "param1": "value1",
        "param2": "value2"
    }
)

print(result.data)  # Operation result
print(result.metadata)  # Execution metadata
```

### CLI Example

```bash
steward delegate [your-agent-id] \
  --operation [operation-name] \
  --context '{"param1": "value1"}' \
  --timeout 60s
```

---

## 💰 Pricing `[STANDARD]` *(Optional)*

> Declare pricing if your agent is commercial

**Model:** `[free|pay_per_use|subscription|hybrid]`

**Free tier:**
- [X] delegations per day
- [Y] minute max duration per task

**Paid tier(s):**
- **Standard:** $[X.XX] per [invocation|hour|month]
- **Premium:** $[Y.YY] per [invocation|hour|month] (includes: [features])

**Payment methods:** `[cryptocurrency|fiat|credits]`

**See pricing details:** [steward.json](./steward.json) (pricing section)

---

## 📋 SLA Commitments `[ADVANCED]` *(Optional)*

> Declare service level agreements (Level 3+)

**Guarantees:**
- **Uptime:** [XX]% (breach threshold: <[YY]%)
- **Latency P99:** <[X]ms (breach threshold: >[Y]ms)
- **Success Rate:** >[XX]% (breach threshold: <[YY]%)

**Penalties for breach:**
- Trust score reduction: -[X]%
- Notification: All delegators notified within 24h
- Recovery: [X] days sustained performance to restore trust

**Monitoring:** [https://monitor.your-agent.com/sla]

---

## 🛡️ Security & Trust `[STANDARD]`

> Show security measures (Level 2+)

**Security:**
- ✅ Cryptographically signed manifest
- ✅ Regular attestation refresh (every [X] hours)
- ✅ Tamper-evident audit logs ([location])
- `[ADVANCED]` ✅ Multi-sig support (requires [X] of [Y] signatures)

**Trust & Reputation:**
- **Trust Score:** [0.XX] ([Unverified|Verified|Trusted|Highly Trusted])
- **Endorsements:** [X] endorsements from [Y] unique agents
- **Successful Delegations:** [X,XXX] (last 30 days)
- **Trust Report:** [Link to detailed trust breakdown]

---

## 👤 Maintained By `[REQUIRED]`

> Who controls this agent?

- **Organization/Individual:** `[Your Name or Org]`
- **Contact:** `[email@example.com]` or `[https://github.com/username]`
- **Support:** `[support@example.com]` or `[GitHub Issues URL]`

**`[STANDARD]` Additional info:**
- **Principal:** `[Human Director name or DAO]`
- **Audit Trail:** `[Location of logs, e.g., vibe_core/ledger.db]`
- **Transparency:** `[public|private]` operations

---

## 📚 More Information `[STANDARD]`

> Links to additional resources (Level 2+)

**Protocol Compliance:**
- **Compliance Level:** Level `[1|2|3|4]` ([GRACEFUL_DEGRADATION.md](https://github.com/kimeisele/vibe-agency/blob/main/docs/protocols/steward/GRACEFUL_DEGRADATION.md))
- **Protocol Version:** STEWARD v1.0.0
- **Full Specification:** [STEWARD Protocol](https://github.com/kimeisele/vibe-agency/tree/main/docs/protocols/steward)

**Agent Resources:**
- **Machine-readable manifest:** [steward.json](./steward.json)
- **Trust Report:** `[Link to trust report]`
- **Attestation Certificates:** [attestations/](./attestations/)
- **Documentation:** `[Link to full docs]`
- **Source Code:** `[GitHub repository URL]`

**Registry:**
- **Published to:** `[steward-registry.org]` or `[custom registry URL]`
- **Discover:** `steward discover --agent-id [your-agent-id]`

---

## 👤 User & Team Context `[STANDARD]` *(Optional)*

> Define who operates this agent and how (Level 2+)

**Purpose:** Configure personalized behavior for different users and teams.

### Default User

```yaml
default_user:
  workflow_style: "[balanced|test_first|iterative]"
  verbosity: "[low|medium|high]"
  communication: "[concise|friendly|explanatory]"
  language: "[en-US|de-DE|...]"
```

### Personal Preferences (Multi-User)

```yaml
[username]:
  role: "[Tech Lead|Developer|Designer|...]"
  workflow_style: "[test_first|iterative|...]"
  verbosity: "[low|medium|high]"
  communication: "[concise_technical|explanatory|...]"
  timezone: "[America/New_York|Europe/Berlin|...]"
  language: "[en-US|de-DE|...]"

  preferences:
    code_style:
      python: "[black|pylint|...]"
      javascript: "[standard|prettier|...]"
    git:
      commit_style: "[conventional_commits|semantic|...]"
      workflow: "[rebase_over_merge|merge_commits|...]"
    testing:
      framework: "[pytest|jest|...]"
      min_coverage: [0.80]

  constraints:
    - "[Constraint 1]"
    - "[Constraint 2]"
```

### Team Context

```yaml
team:
  development_style: "[test_driven|agile|...]"
  git_workflow: "[rebase_over_merge|merge_commits|...]"
  commit_style: "[conventional_commits|semantic|...]"

  testing:
    framework: "[pytest|jest|...]"
    min_coverage: [0.80]
    pre_push: [true|false]

  documentation:
    style: "[inline_comments|docstrings|...]"
    format: "[markdown|rst|...]"

  quality_gates:
    - "[Quality gate 1]"
    - "[Quality gate 2]"
```

**Example for vibe-agency:**
```yaml
kim:
  role: "Tech Lead"
  workflow_style: "test_first"
  verbosity: "low"
  communication: "concise_technical"
  language: "de-DE"
  preferences:
    - "No verbose confirmations"
    - "Show full tracebacks"

team:
  development_style: "test_driven"
  min_coverage: 0.80
  quality_gates:
    - "All tests must pass"
    - "Pre-push checks mandatory"
```

**Boot Modes:**
```bash
# Agent-only (no user context)
steward boot

# With specific user
steward boot --user [username]

# With team defaults
steward boot --team

# Auto-detect from git config
steward boot --auto
```

**Context Precedence:** User Preferences → Team Context → Agent Defaults

**Privacy:** Sensitive preferences can be gitignored via `preferences_file: ".steward/[user].private.md"`

---

## 🔄 Status & Updates `[STANDARD]`

> Current status and recent changes (Level 2+)

**Current Status:**
- ✅ Operational (last checked: [X] minutes ago)
- ⚠️ Degraded (reason: [explanation])
- ❌ Offline (reason: [explanation], ETA: [time])

**Recent Updates:**
- **[YYYY-MM-DD]:** [Brief description of update]
- **[YYYY-MM-DD]:** [Brief description of update]

**Known Issues:**
- None / `[Issue description with link to tracker]`

---

## 🧬 Design Principles `[ADVANCED]` *(Optional)*

> Share your agent's philosophy (Level 3+)

**Core Principles:**
1. **[Principle 1]**: [Description]
2. **[Principle 2]**: [Description]
3. **[Principle 3]**: [Description]

**Example:**
1. **Test-First Development**: All code generated includes tests (minimum 90% coverage)
2. **Quality Over Speed**: Prioritize correct, maintainable code over fast generation
3. **Transparency**: All failures logged with detailed error messages

---

## 📈 Metrics & Monitoring `[ADVANCED]`

> Real-time metrics (Level 3+)

**Live Metrics:**
- **Active Tasks:** [X]
- **Queued Tasks:** [Y]
- **Success Rate (24h):** [XX]%
- **Latency P99 (24h):** [X.X]s

**Monitoring Endpoints:**
```bash
# Health check
curl https://your-agent.com/health

# Runtime introspection
curl https://your-agent.com/introspect

# Prometheus metrics
curl https://your-agent.com/metrics
```

---

## 🚀 Advanced Features `[FULL]`

> Full protocol features (Level 4)

**CLI Integration:**
```bash
# Initialize agent
steward init

# Publish to registry
steward publish --registry steward-registry.org

# Monitor live delegations
steward monitor --live
```

**Federation:**
- **Primary Registry:** `[https://steward-registry.org]`
- **Backup Registries:** `[https://backup-registry.example.com]`
- **Cross-registry discovery:** Enabled

**Advanced Security:**
- **Multi-sig:** Requires [X] of [Y] signatures
- **Key rotation:** Scheduled every [X] days
- **Revocation:** Immediate revocation in [X]h

---

## ✅ Checklist: Template Completion

> Ensure you've filled all required sections for your target level

### Level 1 (Minimal)
- [ ] Agent Identity (basic fields)
- [ ] What I Do (1-2 sentences)
- [ ] Core Capabilities (3-5 items)
- [ ] Quick Start (basic usage)
- [ ] Maintained By (contact info)

### Level 2 (Standard) ← **Recommended**
- [ ] All Level 1 items
- [ ] Agent Identity (fingerprint, trust score)
- [ ] Quality Guarantees
- [ ] Verification (manifest link)
- [ ] For Other Agents (delegation examples)
- [ ] Security & Trust
- [ ] More Information (protocol links)
- [ ] *(Optional)* User & Team Context
- [ ] Create `steward.json` manifest

### Level 3 (Advanced)
- [ ] All Level 2 items
- [ ] Quality Guarantees (live metrics)
- [ ] SLA Commitments
- [ ] Metrics & Monitoring (endpoints)
- [ ] Setup CI/CD attestation refresh
- [ ] Deploy health check endpoint

### Level 4 (Full Protocol)
- [ ] All Level 3 items
- [ ] Advanced Features (CLI, federation)
- [ ] Multi-sig setup
- [ ] Publish to federated registry

---

**Template Version:** 1.0.0
**Protocol Version:** STEWARD v1.0.0
**Last Updated:** 2025-11-21

**Next Steps:**
1. Copy this template to your project root as `STEWARD.md`
2. Fill in sections for your target compliance level
3. (Level 2+) Create `steward.json` manifest: `steward init`
4. (Level 2+) Sign manifest: `steward sign steward.json`
5. (Level 2+) Publish to registry: `steward publish`

**Need help?** See [GRACEFUL_DEGRADATION.md](../GRACEFUL_DEGRADATION.md) for detailed level descriptions.
