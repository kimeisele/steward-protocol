<div align="center">

# STEWARD PROTOCOL

### The Operating System for AI Agents

**Cryptographic Identity + Governance for AI Agents. A.G.I. Infrastructure.**

[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/kimeisele/steward-protocol/releases)
[![Python](https://img.shields.io/badge/python-3.9+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/agents-30-purple.svg)](#the-federation)
[![Tests](https://img.shields.io/badge/tests-685%20passed-brightgreen.svg)](#testing)

*An actual kernel with process isolation, immutable ledger, and constitutional governance.*

[What Is This?](#-what-is-this) • [Quick Start](#-quick-start) • [Architecture](#-the-kernel) • [Security](#-security-architecture)

</div>

---

## What Is This?

**STEWARD is to AI agents what Linux is to processes.**

Most "agent frameworks" are orchestration layers. STEWARD is a real operating system:

| OS Concept | STEWARD Implementation |
|------------|------------------------|
| **Kernel** | Process table, task scheduler, syscall interface |
| **Process Isolation** | Virtual filesystem sandboxing per agent |
| **Audit Log** | Immutable append-only ledger (SQLite-backed chain) |
| **Kill Switch** | Hypervisor-level agent termination protocol |
| **Memory Protection** | Immutable kernel blueprints, self-healing on corruption |
| **Constitution** | Governance enforced at architecture level, not prompts |
| **Identity** | ECDSA P-256 signatures on every action |

**The key insight:** An agent that "promises" to follow rules is insecure. An agent that *physically cannot* violate them is secure.

---

## Quick Start

```bash
# Clone
git clone https://github.com/kimeisele/steward-protocol
cd steward-protocol

# Install
pip install -e ".[dev]"   # or: uv sync

# Boot the kernel
steward boot

# Check system status
steward status            # Kernel health, ledger blocks, certified agents
steward introspect        # Deep kernel inspection
```

**What happens on first boot:**
1. Initializes the immutable ledger (append-only event chain)
2. Loads 30 plugins via oath verification
3. Registers 30 agents with cryptographic identity
4. Starts the heartbeat system for liveness monitoring

---

## The Kernel

This is a real kernel implementation (`vibe_core/kernel_impl.py`):

```
┌──────────────────────────────────────────────────────────────┐
│                      HUMAN OPERATOR                          │
│                    (Intent & Oversight)                      │
└──────────────────────────────────────────────────────────────┘
                              ↓ intent
┌──────────────────────────────────────────────────────────────┐
│                      VIBE KERNEL (L0)                        │
│                                                              │
│  • Process Table        • Task Scheduler (async)             │
│  • Immutable Ledger     • Hypervisor Kill-Switch             │
│  • Blueprint Protection • Constitutional Gate                │
│  • VFS Sandboxing       • Event Bus                          │
└──────────────────────────────────────────────────────────────┘
                              ↓ syscalls
┌──────────────────────────────────────────────────────────────┐
│                      THE FEDERATION                          │
│                                                              │
│      30 Certified Agents • 75 Capabilities              │
└──────────────────────────────────────────────────────────────┘
```

### Core Components

| Component | Purpose |
|-----------|---------|
| **Kernel** (`kernel_impl.py`) | Process table, scheduler, ledger integration |
| **Ledger** (`ledger.py`) | Append-only cryptographic event chain |
| **Kill-Switch** (`narasimha.py`) | Hypervisor-level agent termination |
| **DNA Protection** (`security.py`) | Immutable blueprints, self-healing |
| **State Engine** (`state/prakriti.py`) | Unified state across persistence layers |
| **Purifier** (`shuddhi/`) | AST-level self-healing for code violations |

### Three-Layer State Model

The system maintains state across three distinct layers:

1. **Physical Layer** — Git + Ledger (immutable history, cryptographically linked)
2. **Runtime Layer** — Kernel state, ephemeral data (survives restart via snapshots)
3. **Identity Layer** — Agent personas, reputation, relationships (constant across restarts)

---

## Constitutional Governance

Governance is enforced at the **architecture level**, not through prompts:

### The Constitution ([CONSTITUTION.md](CONSTITUTION.md))

| Article | Principle | Enforcement |
|---------|-----------|-------------|
| **I: Identity** | No action without cryptographic proof | Unsigned messages dropped |
| **II: Auditability** | Every decision logged immutably | Missing audit = transaction rollback |
| **III: Governance** | Code is law, not policy | Sandbox blocks violations |
| **IV: Transparency** | No black boxes | Machine-readable state exposure |
| **V: Consent** | No access without mandate | Capability tokens required |

### Operating Inversion (GAD-000)

Traditional model: *Human operates machine.*
STEWARD model: *AI operates system. Human provides intent.*

```bash
# Human provides intent
steward pending              # See what the system wants to do
steward approve <id>         # Approve an intent
steward reject <id>          # Reject with reason

# System operates autonomously within bounds
steward karma                # See trust score evolution
```

---

## Security Architecture

### Hypervisor Kill-Switch

When an agent attempts to modify the constitution, escape its sandbox, or manipulate the ledger:

```
Threat Level:  GREEN → YELLOW → ORANGE → RED → CRITICAL
                                                   ↓
                                        Kill-switch activates
                                                   ↓
                                        Instant termination
                                        (Irreversible)
```

### Self-Healing Architecture

- **Blueprint Protocol**: Critical kernel components stored as factories, not instances
- **Immutable Sealing**: Protected attributes locked after initialization
- **Auto-Recovery**: Corruption detected → rebuild from blueprint

### Kernel File Protection

21 kernel files are cryptographically guarded. Pre-commit hooks prevent modification without explicit authorization.

### Security Test Suite

The `tests/hardening/` suite includes attack simulations:

| Test | Attack Type |
|------|-------------|
| `test_red_team_attacks.py` | Identity spoofing, capability bypass |
| `test_halahala_poison.py` | SQL injection, memory bombs |
| `test_kurukshetra_metal.py` | Multi-threaded kernel destruction |
| `test_vritrasura_vacuum.py` | Message hoarding, fake heartbeats |
| `test_hiranyakashipu_paradox.py` | TOCTOU logic vulnerabilities |

---

## The Federation

30 specialized agents form a self-governing federation:

### Governance

| Agent | Role | Capabilities |
|-------|------|--------------|
| **AUDITOR** | GAD-000 compliance enforcement agent | 3 |
| **CIVIC** | Governance agent: enforces rules, manages lic… | 4 |
| **SUPREME_COURT** | Appellate justice system with mercy protocol | 2 |

### Intelligence

| Agent | Role | Capabilities |
|-------|------|--------------|
| **ENVOY** | Universal operator interface agent | 5 |
| **MANAS** | The Cognitive Mind - Proactive Intent Generat… | 6 |
| **ORACLE** | System introspection and explanation agent | 3 |
| **SCIENCE** | External intelligence module via web research | 3 |

### Communications

| Agent | Role | Capabilities |
|-------|------|--------------|
| **HERALD** | Protocol communications and identity verifica… | 5 |
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
| **MARKETER** | Autonomous content strategist and generator f… | 4 |
| **PULSE** | Social media amplification | 2 |

<details>
<summary><b>View all 30 agents</b></summary>

See [AGENTS.md](AGENTS.md) for the complete registry.

</details>

---

## CLI Reference

```bash
# System
steward boot                 # Initialize kernel
steward status               # Health check
steward introspect           # Deep kernel state
steward stop                 # Graceful shutdown

# Unified Execution
steward run <capability>     # Execute any tool/circuit/agent
steward run list             # Discover all capabilities

# Human-in-the-Loop
steward pending              # Pending intents
steward approve <id>         # Approve execution
steward reject <id>          # Reject with reason

# Diagnostics
steward system:doctor        # Health diagnosis
steward agents:list          # Process table
```

---

## Documentation

| Document | Purpose |
|----------|---------|
| [CONSTITUTION.md](CONSTITUTION.md) | The supreme law |
| [OPUS.md](OPUS.md) | Live system dashboard |
| [AGENTS.md](AGENTS.md) | Agent registry |
| [PROMPT.md](PROMPT.md) | Architecture guide for developers |
| [docs/architecture/](docs/architecture/) | Technical deep-dives |

---

## Testing

```bash
steward test:run             # Full test suite
pytest tests/hardening/ -v   # Security/architecture tests
pytest tests/manas/ -v       # Cognitive tests
```

**685 tests** including red-team attack simulations.

---

## Philosophy

> *"An agent that promises to follow rules is insecure. An agent that cannot violate them is trustworthy."*

STEWARD redefines AGI as **Artificial Governed Intelligence** — autonomous systems with cryptographic accountability and constitutional constraints enforced at the kernel level.

---

<div align="center">

**Built by humans and agents**

*"The filesystem is not storage. It is the operating reality."*

[GitHub](https://github.com/kimeisele/steward-protocol) · [Issues](https://github.com/kimeisele/steward-protocol/issues) · [Constitution](CONSTITUTION.md)

</div>