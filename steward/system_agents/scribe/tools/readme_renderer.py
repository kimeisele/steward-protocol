#!/usr/bin/env python3
"""
SCRIBE README Renderer - Generate README.md from introspection

ZERO HARDCODED LINE NUMBERS! All data from:
- pyproject.toml
- git stats
- agent count (link to AGENTS.md, NO full table)
- CONSTITUTION.md
- AST parsing for code references

Tool Protocol Compliant (Kernel-Managed).
"""

import ast
from pathlib import Path
from typing import Any, Optional

from jinja2 import Template

# Tool Protocol import - optional for standalone mode
try:
    from vibe_core.tools.tool_protocol import Tool, ToolResult

    TOOL_PROTOCOL_AVAILABLE = True
except ImportError:
    TOOL_PROTOCOL_AVAILABLE = False

    # Dummy base class for standalone mode
    class Tool:
        pass

    class ToolResult:
        def __init__(self, success, output=None, error=None):
            self.success = success
            self.output = output
            self.error = error


from steward.system_agents.scribe.tools.project_introspector import ProjectIntrospector


class ReadmeRenderer(Tool):
    """Render README.md from project introspection.

    Supports both:
    - Kernel-managed mode (via Tool Protocol)
    - Standalone mode (via render() method)
    """

    def __init__(self, root_dir: str = "."):
        """Initialize renderer.

        Args:
            root_dir: Project root directory (for standalone mode)
        """
        self.root_dir = Path(root_dir)
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

    def _find_governance_gate_lines(self) -> Optional[str]:
        """Find actual line numbers of GovernanceGate via AST parsing.

        Returns:
            String like "vibe_core/kernel_impl.py:544-621" or None
        """
        kernel_file = self.root_dir / "vibe_core" / "kernel_impl.py"
        if not kernel_file.exists():
            return None

        try:
            source = kernel_file.read_text()
            tree = ast.parse(source)

            # Find the governance gate enforcement function/class
            for node in ast.walk(tree):
                # Look for function or method with "governance" in name
                if isinstance(node, ast.FunctionDef):
                    if "governance" in node.name.lower() or "oath" in node.name.lower():
                        start_line = node.lineno
                        end_line = node.end_lineno
                        return f"vibe_core/kernel_impl.py#L{start_line}-L{end_line}"

                # Look for class definitions related to governance
                if isinstance(node, ast.ClassDef):
                    if "governance" in node.name.lower():
                        start_line = node.lineno
                        end_line = node.end_lineno
                        return f"vibe_core/kernel_impl.py#L{start_line}-L{end_line}"

            # Fallback: search for specific patterns in source
            lines = source.split("\n")
            for i, line in enumerate(lines, 1):
                if "def _enforce_governance_gate" in line or "class GovernanceGate" in line:
                    # Find end of function/class
                    end = i
                    indent = len(line) - len(line.lstrip())
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip() and not lines[j].startswith(" " * (indent + 1)):
                            end = j - 1
                            break
                    return f"vibe_core/kernel_impl.py#L{i}-L{end}"

        except Exception as e:
            print(f"Warning: Could not parse kernel_impl.py for governance gate: {e}")

        return None

    def _render(self) -> str:
        """Generate README.md content from introspection."""
        # Get all metadata
        metadata = self.introspector.get_all_metadata()

        # Find governance gate line numbers dynamically
        governance_gate_ref = self._find_governance_gate_lines()
        if governance_gate_ref:
            governance_link = f"[Governance Gate Code]({governance_gate_ref})"
        else:
            governance_link = "[Governance Gate Code](vibe_core/kernel_impl.py)"

        # Jinja2 template - MINIMAL agent content
        template_str = """# {{ project.name }}

## {{ project.description }}

**Agents literally cannot boot without cryptographically verified oath.**

[![License: {{ project.license }}](https://img.shields.io/badge/License-{{ project.license }}-yellow.svg)](https://opensource.org/licenses/{{ project.license }})
[![Python {{ project.python_version }}](https://img.shields.io/badge/python-{{ project.python_version }}-blue.svg)](https://www.python.org/downloads/)
[![Status: LIVE](https://img.shields.io/badge/Status-LIVE-green.svg)](./docs/reports/VERIFICATION_REPORT.md)

---

## Quick Start

```bash
git clone https://github.com/kimeisele/steward-protocol.git
cd steward-protocol
python boot.py
```

That's it. One command boots everything. Dependencies auto-install.

**Verify boot:**
```bash
python boot.py --check
```

---

## The Innovation

**Version:** 1.0 (Genesis) **Layer:** 0 (The Immutable Foundation)

- **{{ governance_link }}** — The cryptographic oath enforcement
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

{{ agent_count }} specialized agents govern Agent City.

**[See complete agent registry →](AGENTS.md)**

Key agents:
- **CIVIC** — Constitutional governance, registry, and economic system
- **WATCHMAN** — System integrity enforcement and governance monitoring
- **ENVOY** — Universal operator interface and orchestration
- **HERALD** — Autonomous content generation and distribution
- **ARCHIVIST** — Cryptographic audit trail and event verification
- **AUDITOR** — Quality gate and compliance enforcement

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
            governance_link=governance_link,
        )

        return content

    # Standalone mode method (for generate_docs.py)
    def render(self) -> str:
        """Standalone method to generate README.md content.

        Returns:
            Generated README.md content
        """
        return self._render()
