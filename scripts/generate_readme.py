#!/usr/bin/env python3
"""
Quick README.md generator - NO DEPENDENCIES
Inline implementation to avoid import hell
"""

import re
import subprocess
from pathlib import Path

from jinja2 import Template


def get_project_metadata():
    """Extract metadata from pyproject.toml"""
    pyproject = Path("pyproject.toml")
    metadata = {
        "name": "Steward Protocol",
        "version": "1.0.0",
        "description": "Constitutional AI Agent Operating System",
        "python_version": "3.11+",
        "license": "MIT",
    }

    if not pyproject.exists():
        return metadata

    try:
        content = pyproject.read_text()

        # Extract name
        name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
        if name_match:
            metadata["name"] = name_match.group(1)

        # Extract version
        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if version_match:
            metadata["version"] = version_match.group(1)

        # Extract description
        desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
        if desc_match:
            metadata["description"] = desc_match.group(1)

        # Extract python version
        python_match = re.search(r'python\s*=\s*["\']([^"\']+)["\']', content)
        if python_match:
            metadata["python_version"] = python_match.group(1)

    except Exception as e:
        print(f"Warning: Could not parse pyproject.toml: {e}")

    return metadata


def get_git_stats():
    """Extract git statistics"""
    stats = {"commit_count": 0, "contributors": [], "recent_commits": []}

    try:
        # Get commit count
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            stats["commit_count"] = int(result.stdout.strip())

        # Get contributors
        result = subprocess.run(
            ["git", "log", "--format=%an", "--all"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            contributors = set(result.stdout.strip().split("\n"))
            stats["contributors"] = sorted(list(contributors))[:5]

        # Get recent commits
        result = subprocess.run(
            ["git", "log", "--oneline", "-3"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            commits = result.stdout.strip().split("\n")
            stats["recent_commits"] = [c.strip() for c in commits if c.strip()]

    except Exception as e:
        print(f"Warning: Could not extract git stats: {e}")

    return stats


def count_system_agents():
    """Count system agents"""
    agents_dir = Path("steward/system_agents")
    if not agents_dir.exists():
        return 0

    cartridges = list(agents_dir.glob("*/cartridge_main.py"))
    return len(cartridges)


def get_agent_list():
    """Get list of actual agents with their metadata"""
    import re

    agents_dir = Path("steward/system_agents")
    if not agents_dir.exists():
        return []

    agents_list = []
    for cartridge_file in sorted(agents_dir.glob("*/cartridge_main.py")):
        agent_name = cartridge_file.parent.name

        try:
            content = cartridge_file.read_text()

            # Extract description from class docstring
            class_match = re.search(
                r'class\s+\w+Cartridge.*?"""(.*?)"""', content, re.DOTALL
            )
            description = "Specialized Agent"
            if class_match:
                doc = class_match.group(1).strip()
                first_line = doc.split("\n")[0].strip()
                description = first_line if first_line else "Specialized Agent"

            agents_list.append({"name": agent_name.upper(), "role": description})
        except Exception as e:
            print(f"Warning: Could not parse {agent_name}: {e}")
            agents_list.append(
                {"name": agent_name.upper(), "role": "Specialized Agent"}
            )

    return agents_list


def get_governance_summary():
    """Extract governance summary from CONSTITUTION.md"""
    constitution = Path("CONSTITUTION.md")
    if not constitution.exists():
        return "Constitutional governance enforced at kernel level—not policy, architecture. Violations are impossible, not prohibited."

    try:
        content = constitution.read_text()
        # Extract first paragraph after title
        lines = content.split("\n")
        summary_lines = []
        in_summary = False
        for line in lines:
            if line.strip().startswith("#"):
                in_summary = True
                continue
            if in_summary and line.strip():
                summary_lines.append(line.strip())
                if len(summary_lines) >= 2:
                    break

        if summary_lines:
            return " ".join(summary_lines)
    except:
        pass

    return "Constitutional governance enforced at kernel level—not policy, architecture. Violations are impossible, not prohibited."


def main():
    print("=" * 70)
    print("REGENERATING README.md FROM TEMPLATE")
    print("=" * 70)

    # Get all metadata
    project = get_project_metadata()
    git = get_git_stats()
    agent_count = count_system_agents()
    governance = get_governance_summary()
    agents = get_agent_list()

    print(f"\n📊 Introspection results:")
    print(f"   Project: {project['name']} v{project['version']}")
    print(f"   Agent count: {agent_count}")
    print(f"   Agents discovered: {len(agents)}")
    print(f"   Git commits: {git['commit_count']}")

    # Jinja2 template (from readme_renderer.py)
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
        project=project,
        git=git,
        agent_count=agent_count,
        governance=governance,
        agents=agents,
    )

    # Write to README.md
    readme_path = Path("README.md")
    readme_path.write_text(content)

    print(f"\n✅ README.md regenerated ({len(content)} bytes)")
    print(f"✅ Location: {readme_path.absolute()}")
    print("\n" + "=" * 70)
    print("DONE - README.md is now template-based, not hardcoded!")
    print("=" * 70)


if __name__ == "__main__":
    main()
