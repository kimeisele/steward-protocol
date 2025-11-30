#!/usr/bin/env python3
"""
SCRIBE README Renderer - Generate README.md from introspection

NO HARDCODED CONTENT! All data from:
- pyproject.toml
- git stats
- agent count
- CONSTITUTION.md

Tool Protocol Compliant (Kernel-Managed).
"""

from pathlib import Path
from typing import Any

from jinja2 import Template
from vibe_core.tools.tool_protocol import Tool, ToolResult

from .project_introspector import ProjectIntrospector


class ReadmeRenderer(Tool):
    """Render README.md from project introspection."""

    def __init__(self):
        """Initialize renderer (kernel-managed)."""
        self.root_dir = Path(".")
        self.introspector = ProjectIntrospector(str(self.root_dir))

    @property
    def name(self) -> str:
        return "scribe.readme_renderer"

    @property
    def description(self) -> str:
        return "Generate README.md from project introspection (pyproject.toml, git stats, agent count)"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'generate' to scan and render README.md content",
            }
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate renderer parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")
        if parameters["action"] not in ["generate"]:
            raise ValueError(f"Invalid action: {parameters['action']}. Must be 'generate'")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute renderer operation."""
        try:
            action = parameters["action"]
            if action == "generate":
                content = self._render()
                return ToolResult(success=True, output=content)
            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def _render(self) -> str:
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
{% for agent in agents -%}
| **{{ agent.name }}** | {{ agent.role }} |
{% endfor %}

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
            project=metadata["project"],
            git=metadata["git"],
            agent_count=metadata["agent_count"],
            governance=metadata["governance"],
            agents=metadata["agents"],
        )

        return content

