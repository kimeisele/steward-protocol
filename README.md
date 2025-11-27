# Steward Protocol

## Constitutional AI Agent Operating System

**Agents literally cannot boot without cryptographically verified oath.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Status: LIVE](https://img.shields.io/badge/Status-LIVE-green.svg)](./AUDIT_REPORT_OPUS.md)

---

## Quick Start

```bash
python scripts/research_yagya.py
```

Then activate Agent City:
```bash
vibe activate cartridges:steward-protocol
```

---

## The Innovation

Constitutional governance enforced at **kernel level**—not policy, architecture. Violations are impossible, not prohibited.

- **[Governance Gate Code](vibe_core/kernel_impl.py#L544-L621)** — The cryptographic oath enforcement
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — Full system design
- **[A.G.I. Manifesto](AGI_MANIFESTO.md)** — Why this matters

---

## How It Works

### Constitutional Enforcement at Boot

Before any agent can run, Steward Protocol verifies:
- ✅ Cryptographic identity (ECDSA keys)
- ✅ Constitutional oath signing
- ✅ Governance compliance markers

No workarounds. No exceptions. This is kernel-level, not policy.

### The Federation

Seven specialized agents govern Agent City:

| Agent | Role |
|-------|------|
| **HERALD** | Creative Director — governance-aligned narratives |
| **CIVIC** | Governance Engine — proposals, voting, treasury |
| **FORUM** | Public Square — discussion & debate |
| **SCIENCE** | Research — validates protocols & data |
| **ARCHIVIST** | Auditor — signature verification & chain of trust |
| **ARTISAN** | Media Ops — branding & asset formatting |
| **ENVOY** | Interface — natural language to protocol execution |

### Immutable Ledger

Every action is cryptographically signed and recorded:
- **Database:** SQLite (`data/vibe_ledger.db`)
- **Format:** Append-only event log
- **Recovery:** Full history restored on restart
- **Proof:** Unforgeable signatures on every entry

---

## For Developers

**Install to VibeOS:**
```bash
git clone https://github.com/kimeisele/steward-protocol.git
cd steward-protocol
./install_to_vibe.sh /path/to/vibe-agency
```

**Run tests:**
```bash
pytest tests/
```

### Testing & Validation

**Integration Test Suite** — Proves Agent City boots and discovers agents:

```bash
# Run integration tests
pytest tests/integration/test_system_boot.py -v

# What it validates:
# ✅ Kernel boots without errors
# ✅ Discoverer registers successfully
# ✅ Steward discovers 10+ agents from steward.json manifests
# ✅ All agents pass Governance Gate (oath_sworn=True)
# ✅ Constitutional enforcement is active
```

**CI/CD Pipeline** — Automatic validation on every push:
- Runs on all `claude/*` branches and `main`
- Executes full integration test suite
- Verifies governance gate rejection of unsworn agents
- See: `.github/workflows/integration-tests.yml`

**Smoke Test** — Quick verification Agent City boots:

```bash
python -c "
from vibe_core.kernel_impl import RealVibeKernel
from steward.system_agents.discoverer.agent import Discoverer

kernel = RealVibeKernel(ledger_path=':memory:')
steward = Discoverer(kernel)
kernel.register_agent(steward)
kernel.boot()
count = steward.discover_agents()
print(f'✅ Boot OK: {len(kernel.agent_registry)} agents registered ({count} discovered)')
"
```

**Learn the system:**
1. [A.G.I. Manifesto](AGI_MANIFESTO.md) — Why governance matters
2. [ARCHITECTURE.md](ARCHITECTURE.md) — How it works
3. [CONSTITUTION.md](CONSTITUTION.md) — The rules
4. [DEPLOYMENT.md](DEPLOYMENT.md) — Boot, deploy, and operate Agent City
5. [vibe_core/](./vibe_core/) — Kernel integration

**For AI Assistants:** Paste [MISSION_BRIEFING.md](./MISSION_BRIEFING.md) into your context to activate as a governed agent.

---

*Verified by Steward Protocol.*
