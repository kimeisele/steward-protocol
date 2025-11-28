# steward-protocol

## Cryptographic Identity + Governance for AI Agents. A.G.I. Infrastructure.

**Agents literally cannot boot without cryptographically verified oath.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python >=3.8](https://img.shields.io/badge/python->=3.8-blue.svg)](https://www.python.org/downloads/)
[![Status: LIVE](https://img.shields.io/badge/Status-LIVE-green.svg)](./docs/reports/VERIFICATION_REPORT.md)

---

## Quick Start

```bash
python scripts/summon.py
```

Then activate Agent City:
```bash
vibe activate cartridges:steward-protocol
```

---

## The Innovation

**Version:** 1.0 (Genesis) **Layer:** 0 (The Immutable Foundation)

- **[Governance Gate Code](vibe_core/kernel_impl.py#L544-L621)** — The cryptographic oath enforcement
- **[docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md)** — Full system design
- **[AGI_MANIFESTO.md](AGI_MANIFESTO.md)** — Why this matters

---

## How It Works

### Constitutional Enforcement at Boot

Before any agent can run, Steward Protocol verifies:
- ✅ Cryptographic identity (ECDSA keys)
- ✅ Constitutional oath signing
- ✅ Governance compliance markers

No workarounds. No exceptions. This is kernel-level, not policy.

### The Federation

13 specialized agents govern Agent City:

| Agent | Role |
|-------|------|
| **ARCHIVIST** | ARCHIVIST - The History Keeper Agent. |
| **AUDITOR** | AUDITOR - The Quality Gate Agent. |
| **CHRONICLE** | The CHRONICLE Agent Cartridge (The Historian). |
| **CIVIC** | The CIVIC Agent Cartridge (The Bureaucrat). |
| **ENGINEER** | The Engineer Agent Cartridge. |
| **ENVOY** | The ENVOY Agent Cartridge - Brain of Agent City |
| **FORUM** | The FORUM Agent Cartridge (The Town Hall). |
| **HERALD** | The HERALD Agent Cartridge. |
| **ORACLE** | THE ORACLE - System Introspection & Explanation Agent. |
| **SCIENCE** | THE SCIENTIST Agent - External Intelligence Module. |
| **SCRIBE** | The SCRIBE Agent Cartridge (The Documentarian). |
| **SUPREME_COURT** | SUPREME COURT - The Appellate Justice & Mercy System for STEWARD Protocol. |
| **WATCHMAN** | THE WATCHMAN - System Integrity Enforcer. |


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
1. [AGI_MANIFESTO.md](AGI_MANIFESTO.md) — Why governance matters
2. [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) — How it works
3. [CONSTITUTION.md](CONSTITUTION.md) — The rules
4. [docs/deployment/DEPLOYMENT.md](docs/deployment/DEPLOYMENT.md) — Boot, deploy, and operate Agent City
5. [vibe_core/](./vibe_core/) — Kernel integration

**For AI Assistants:** Paste [docs/guides/MISSION_BRIEFING.md](./docs/guides/MISSION_BRIEFING.md) into your context to activate as a governed agent.

---

*Verified by Steward Protocol.*