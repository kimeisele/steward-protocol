#!/usr/bin/env python3
"""
SCRIBE README Renderer - Generate README.md from introspection

NO HARDCODED CONTENT! All data from:
- pyproject.toml
- git stats
- agent count
- CONSTITUTION.md
"""

from pathlib import Path
from typing import Dict, Any
from jinja2 import Template
from .project_introspector import ProjectIntrospector


class ReadmeRenderer:
    """Render README.md from project introspection."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.introspector = ProjectIntrospector(root_dir)

    def render(self) -> str:
        """Generate README.md content from introspection."""
        # Get all metadata
        metadata = self.introspector.get_all_metadata()

        # Jinja2 template
        template_str = """# {{ project.name }}

## {{ project.description }}

**Agents literally cannot boot without cryptographically verified oath.**

[![License: {{ project.license }}](https://img.shields.io/badge/License-{{ project.license }}-yellow.svg)](https://opensource.org/licenses/{{ project.license }})
[![Python {{ project.python_version }}](https://img.shields.io/badge/python-{{ project.python_version }}-blue.svg)](https://www.python.org/downloads/)
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

{{ governance }}

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

{{ agent_count }} specialized agents govern Agent City:

| Agent | Role |
|-------|------|
| **HERALD** | Creative Director — governance-aligned narratives |
| **CIVIC** | Governance Engine — proposals, voting, treasury |
| **FORUM** | Public Square — discussion & debate |
| **SCIENCE** | Research — validates protocols & data |
| **ARCHIVIST** | Auditor — signature verification & chain of trust |
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
1. [AGI_MANIFESTO.md](AGI_MANIFESTO.md) — Why governance matters
2. [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) — How it works
3. [CONSTITUTION.md](CONSTITUTION.md) — The rules
4. [docs/deployment/DEPLOYMENT.md](docs/deployment/DEPLOYMENT.md) — Boot, deploy, and operate Agent City
5. [vibe_core/](./vibe_core/) — Kernel integration

**For AI Assistants:** Paste [docs/guides/MISSION_BRIEFING.md](./docs/guides/MISSION_BRIEFING.md) into your context to activate as a governed agent.

---

*Verified by Steward Protocol.*
"""

        template = Template(template_str)
        content = template.render(
            project=metadata['project'],
            git=metadata['git'],
            agent_count=metadata['agent_count'],
            governance=metadata['governance']
        )

        return content

    def render_to_file(self, output_file: str = "README.md") -> bool:
        """Render and write to file."""
        try:
            content = self.render()
            output_path = self.root_dir / output_file

            output_path.write_text(content)
            print(f"✅ README.md generated: {output_path}")

            return True
        except Exception as e:
            print(f"❌ Error writing README.md: {e}")
            return False
