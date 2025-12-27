
<div align="center">

# 🕉️ STEWARD PROTOCOL

**Cryptographic Identity + Governance for AI Agents. A.G.I. Infrastructure.**

[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/kimeisele/steward-protocol/releases)
[![Python](https://img.shields.io/badge/python-3.9+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/agents-30-purple.svg)](#the-federation)
[![Tests](https://img.shields.io/badge/tests-685%20passed-brightgreen.svg)](#testing)

*What if AI agents had cryptographic identities, constitutional rights, and governed themselves?*

[Quick Start](#-quick-start) • [Why STEWARD?](#-why-steward) • [Architecture](#-architecture) • [CLI](#-unified-cli)

</div>

---

## 🚀 Quick Start

```bash
# Install
git clone https://github.com/kimeisele/steward-protocol
cd steward-protocol
pip install -e ".[dev]"

# Boot the system
steward boot

# See what's running
steward status

# Run any capability (unified interface)
steward run list              # See all 75+ capabilities
steward run envoy.curator     # Example: curate documentation
```

<details>
<summary><b>Alternative: uv (faster)</b></summary>

```bash
git clone https://github.com/kimeisele/steward-protocol
cd steward-protocol
uv sync
steward boot
```

</details>

---

## ✨ Why STEWARD?

Traditional AI agents are **stateless, identity-less tools**. STEWARD creates **autonomous entities** with real accountability:

| Problem | STEWARD Solution |
|---------|------------------|
| **No Identity** | ECDSA P-256 cryptographic signatures — every action is signed |
| **No Rules** | Constitutional governance — agents follow enforceable laws |
| **No Memory** | MANAS cognitive kernel — agents think, learn, plan |
| **Isolated** | 30 federated agents collaborate |
| **No Trust** | Chain of trust — cryptographic audit trail |

**This is not an agent framework.** This is an **operating system** for AI agents.

---

## 🎛️ Unified CLI

One command to rule them all. No memorizing 50 different APIs:

```bash
steward run <capability>     # Run anything: tool, circuit, or agent
steward run list             # Discover all capabilities
steward run info <cap>       # Get details before running
```

### System Commands

```bash
steward boot                 # Start the kernel
steward status               # System health
steward ps                   # Running agents (like Unix ps)
steward state                # Unified state view
```

### MANAS Commands (Human-in-the-Loop)

```bash
steward pending              # See what MANAS wants to do
steward approve <id>         # Approve an intent
steward reject <id>          # Reject with reason
steward karma                # See MANAS performance stats
```

---

## 🏛️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      HUMAN OPERATOR                          │
│                    (Intent & Oversight)                      │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                    🧠 MANAS Cognitive Kernel                 │
│                                                              │
│  JNANA (Knowledge) → KRIYA (Action) → SAMVADA (Dialogue)    │
│                                                              │
│  "The mind that perceives, decides, and acts"               │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                    ⚙️ VIBE Kernel (L0)                       │
│                                                              │
│  • Constitutional Oath      • Cryptographic Ledger          │
│  • Plugin Lifecycle         • VISNU Protection              │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                    🤖 The Federation                         │
│                                                              │
│           30 Agents • 75 Tools • Self-governing              │
└──────────────────────────────────────────────────────────────┘
```

**GAD-000 Principle:** *The AI operates the system. The human provides intent.*

---

## 🤖 The Federation

30 agents form a self-governing federation:



### Governance

| Agent | Role | Capabilities |
|-------|------|--------------|
| **AUDITOR** | GAD-000 compliance enforcement agent | 3 |
| **CIVIC** | Governance agent: enforces rules, manages licenses, aud… | 4 |
| **SUPREME_COURT** | Appellate justice system with mercy protocol | 2 |




### Intelligence

| Agent | Role | Capabilities |
|-------|------|--------------|
| **ENVOY** | Universal operator interface agent | 5 |
| **MANAS** | The Cognitive Mind - Proactive Intent Generation and Sy… | 6 |
| **ORACLE** | System introspection and explanation agent | 3 |
| **SCIENCE** | External intelligence module via web research | 3 |
| **ANALYST** | Multi-Source Repository Analysis (Realtime Architecture… | 6 |




### Communications

| Agent | Role | Capabilities |
|-------|------|--------------|
| **HERALD** | Protocol communications and identity verification agent… | 5 |
| **AMBASSADOR** | External relations and partnerships | 1 |




### Infrastructure

| Agent | Role | Capabilities |
|-------|------|--------------|
| **ARCHIVIST** | Event verification and audit trail agent | 3 |
| **CHRONICLE** | Temporal operations and event tracking | 1 |
| **ENGINEER** | Meta-agent for building new agents and code | 3 |
| **SCRIBE** | Autonomous documentation generation agent | 3 |




### Content

| Agent | Role | Capabilities |
|-------|------|--------------|
| **ARTISAN** | Media and technical operations | 1 |
| **MARKETER** | Autonomous content strategist and generator for social … | 4 |
| **PULSE** | Social media amplification | 2 |






<details>
<summary><b>View all 30 agents →</b></summary>

See [AGENTS.md](AGENTS.md) for the complete registry.

</details>

---

## 🧠 MANAS: The Cognitive Kernel

MANAS (Sanskrit: *mind*) is the autonomous intelligence layer:

| Module | Purpose |
|--------|---------|
| **JNANA** | LLM-powered reasoning and memory |
| **KRIYA** | Intent → tool execution |
| **SAMVADA** | Real-time dialogue |
| **VAK** | Safe command execution with audit |

MANAS doesn't just respond — it **perceives**, **plans**, and **acts**.

---

## 🔐 Trust & Governance

Governance is enforced at the **kernel level** — not as policy, but as physics:

- **[CONSTITUTION.md](CONSTITUTION.md)** — The supreme law
- **VISNU Protection** — Kernel files are cryptographically guarded
- **Chain of Trust** — Every action signed with ECDSA P-256
- **Governance Gate** — Constitutional checks before syscalls

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [OPUS.md](OPUS.md) | Live system dashboard |
| [AGENTS.md](AGENTS.md) | Agent registry |
| [CONSTITUTION.md](CONSTITUTION.md) | Governance rules |
| [docs/architecture/](docs/architecture/) | Technical deep-dives |

---

## 🧪 Testing

```bash
pytest tests/ -v                    # All tests
pytest tests/hardening/ -v          # Architecture enforcement
pytest tests/manas/ -v              # Cognitive tests
```

**Coverage:** 685 tests

---

## 🤝 Contributing

STEWARD is built for AI-human collaboration. The system operates itself — you provide intent.

```bash
steward boot
steward run opus.status      # See current state
# Then tell MANAS what you want to build
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

<div align="center">

**Built with intention by humans and agents**

*"Know thyself, and you shall know the universe."*

[GitHub](https://github.com/kimeisele/steward-protocol) · [Issues](https://github.com/kimeisele/steward-protocol/issues)

</div>