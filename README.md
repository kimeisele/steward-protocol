<div align="center">

# 🕉️ STEWARD PROTOCOL

### The First Operating System for AI Agents

**Cryptographic Identity + Governance for AI Agents. A.G.I. Infrastructure.**

[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/kimeisele/steward-protocol/releases)
[![Python](https://img.shields.io/badge/python-3.9+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/agents-30-purple.svg)](#the-federation)
[![Tests](https://img.shields.io/badge/tests-685%20passed-brightgreen.svg)](#testing)

*Not another agent framework. An actual kernel with process isolation, immutable ledger, and constitutional governance.*

[What Is This?](#-what-is-this) • [Quick Start](#-quick-start) • [Architecture](#-the-kernel) • [Constitution](#-constitutional-governance)

</div>

---

## ⚡ What Is This?

**STEWARD is to AI agents what Linux is to processes.**

Most "agent frameworks" are just prompt wrappers. STEWARD is a real operating system with:

| OS Concept | STEWARD Implementation |
|------------|------------------------|
| **Kernel** | VIBE Kernel — process table, scheduler, syscalls |
| **Process Isolation** | VFS sandboxing — agents can't escape their boundaries |
| **Audit Log** | Immutable Ledger — 432+ cryptographic chain blocks |
| **Kill Switch** | NARASIMHA Protocol — hypervisor-level agent termination |
| **Memory Protection** | VAJRA Armor — self-healing DNA, immutable blueprints |
| **Constitution** | Supreme Law — governance enforced at kernel level, not prompts |
| **Identity** | ECDSA P-256 — every action cryptographically signed |

**The difference:** An agent that "promises" to follow rules is insecure. An agent that *physically cannot* violate them is secure.

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/kimeisele/steward-protocol
cd steward-protocol

# Install (creates virtual environment)
pip install -e ".[dev]"   # or: uv sync

# Boot the kernel
steward boot

# Check system status
steward status            # Kernel health, ledger blocks, certified agents
steward introspect        # Deep kernel inspection
```

**First time?** The kernel will:
1. Initialize the immutable ledger (SQLite-backed blockchain)
2. Load 30 plugins via Constitutional Oath
3. Register 30 agents with cryptographic identity
4. Start the PRANA heartbeat (life force)

---

## 🔬 The Kernel

This is a **real kernel**, not a metaphor:

```
┌──────────────────────────────────────────────────────────────┐
│                      HUMAN OPERATOR                          │
│                    (Intent & Oversight)                      │
└──────────────────────────────────────────────────────────────┘
                              ↓ intent
┌──────────────────────────────────────────────────────────────┐
│                    ⚙️ VIBE KERNEL (L0)                       │
│                                                              │
│  • Process Table (30 agents)    • Task Scheduler (FIFO)       │
│  • Immutable Ledger (432+ blocks)  • NARASIMHA Kill-Switch   │
│  • VAJRA DNA Protection    • Constitutional Oath Gate        │
│  • VFS Sandboxing          • Event Bus (async)               │
└──────────────────────────────────────────────────────────────┘
                              ↓ syscalls
┌──────────────────────────────────────────────────────────────┐
│                    🤖 THE FEDERATION                         │
│                                                              │
│  30 Certified Agents • 75 Capabilities • Self-Governing     │
└──────────────────────────────────────────────────────────────┘
```

### Kernel Components

| Component | File | Purpose |
|-----------|------|---------|
| **VIBE Kernel** | `kernel_impl.py` | Process table, scheduler, ledger |
| **NARASIMHA** | `narasimha.py` | Hypervisor kill-switch (destroys rogue agents) |
| **VAJRA** | `security.py` | Immutable DNA protection |
| **PRANA** | `prana.py` | Heartbeat, lifecycle management |
| **VISNU** | `.github/hooks/` | Kernel file protection (21 guarded files) |
| **Ledger** | `ledger.py` | Append-only cryptographic chain |

---

## 📜 Constitutional Governance

Unlike prompt-based "safety", STEWARD enforces governance at the **architecture level**:

### The Constitution (CONSTITUTION.md)

| Article | Principle | Enforcement |
|---------|-----------|-------------|
| **I: Identity** | No agent acts without cryptographic proof | Drop unsigned messages |
| **II: Auditability** | Every decision logged immutably | Transaction rollback on missing audit |
| **III: Governance** | Code is law, not policy | Sandbox blocks violations |
| **IV: Transparency** | No black boxes | Machine-readable state exposure |
| **V: Consent** | No access without mandate | ACLs + Capability Tokens |

### GAD-000: The Operating Inversion

Traditional: *Human operates machine.*
STEWARD: *AI operates system. Human provides intent.*

```bash
# Human provides intent
steward pending              # See what MANAS wants to do
steward approve <id>         # Approve an intent
steward reject <id>          # Reject with reason

# AI operates autonomously within bounds
steward karma                # See trust score evolution
```

---

## 🤖 The Federation

30 specialized agents form a self-governing federation:

### Governance

| Agent | Role | Tools |
|-------|------|-------|
| **AUDITOR** | GAD-000 compliance enforcement agent | 3 |
| **CIVIC** | Governance agent: enforces rules, manages licenses… | 4 |
| **SUPREME_COURT** | Appellate justice system with mercy protocol | 2 |

### Intelligence

| Agent | Role | Tools |
|-------|------|-------|
| **ENVOY** | Universal operator interface agent | 5 |
| **MANAS** | The Cognitive Mind - Proactive Intent Generation a… | 6 |
| **ORACLE** | System introspection and explanation agent | 3 |
| **SCIENCE** | External intelligence module via web research | 3 |
| **ANALYST** | Multi-Source Repository Analysis (Realtime Archite… | 6 |

### Communications

| Agent | Role | Tools |
|-------|------|-------|
| **HERALD** | Protocol communications and identity verification … | 5 |
| **AMBASSADOR** | External relations and partnerships | 1 |

### Infrastructure

| Agent | Role | Tools |
|-------|------|-------|
| **ARCHIVIST** | Event verification and audit trail agent | 3 |
| **CHRONICLE** | Temporal operations and event tracking | 1 |
| **ENGINEER** | Meta-agent for building new agents and code | 3 |
| **SCRIBE** | Autonomous documentation generation agent | 3 |

### Content

| Agent | Role | Tools |
|-------|------|-------|
| **ARTISAN** | Media and technical operations | 1 |
| **MARKETER** | Autonomous content strategist and generator for so… | 4 |
| **PULSE** | Social media amplification | 2 |

<details>
<summary><b>View all 30 agents →</b></summary>

See [AGENTS.md](AGENTS.md) for the complete registry with capabilities.

</details>

---

## 🛡️ Security Architecture

### NARASIMHA: The Kill Switch

When an agent goes rogue (tries to modify Constitution, escape sandbox, manipulate ledger):

```
Threat Level:  GREEN → YELLOW → ORANGE → RED → APOCALYPSE
                                               ↓
                                    NARASIMHA activates
                                               ↓
                                    Instant termination
                                    (No appeal, no recovery)
```

### VAJRA: DNA Protection

Critical kernel components are **immutable after boot**:
- Ledger blueprints cannot be poisoned
- Agent registry factories are sealed
- Self-healing via Blueprint Protocol

### VISNU: Kernel File Guard

21 kernel files are cryptographically protected. Pre-commit hooks prevent modification without explicit bypass.

---

## 🎛️ CLI Reference

```bash
# System
steward boot                 # Initialize kernel
steward status               # Health check
steward introspect           # Deep kernel state
steward stop                 # Graceful shutdown

# Unified Execution (OPUS-307)
steward run <capability>     # Execute any tool/circuit/agent
steward run list             # Discover capabilities
steward run info <cap>       # Capability details

# Human-in-the-Loop (MANAS)
steward pending              # Pending intents
steward approve <id>         # Approve
steward reject <id>          # Reject
steward karma                # Trust metrics

# Diagnostics
steward system:doctor        # Health diagnosis
steward agents:list          # Process table (like ps)
steward resources:usage      # Resource consumption
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [CONSTITUTION.md](CONSTITUTION.md) | The supreme law |
| [OPUS.md](OPUS.md) | Live system dashboard |
| [AGENTS.md](AGENTS.md) | Agent registry |
| [docs/architecture/](docs/architecture/) | Technical deep-dives |

---

## 🧪 Testing

```bash
steward test:run             # Full test suite
pytest tests/hardening/ -v   # Security/architecture tests
pytest tests/manas/ -v       # Cognitive tests
```

**Coverage:** 685 tests (including red-team attack simulations)

---

## 🤝 Philosophy

> *"A system where AI can't break the rules isn't oppressive — it's trustworthy."*

STEWARD redefines AGI: Not *Artificial General Intelligence*, but **Artificial Governed Intelligence**.

This is Windows 7 for AI agents. Before it becomes macOS.

---

<div align="center">

**Built with 🕉️ by humans and agents**

*"The filesystem is not storage. It is the operating reality."*

[GitHub](https://github.com/kimeisele/steward-protocol) · [Issues](https://github.com/kimeisele/steward-protocol/issues) · [Constitution](CONSTITUTION.md)

</div>