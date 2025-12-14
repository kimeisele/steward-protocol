"""
OPUS-047: MUKHA (Das Gesicht) - System Identity & Self-Documentation.

Sanskrit: Mukha = Face / Mouth / Gateway.

This module provides MANAS with the ability to:
1. Introspect the entire system topology
2. Understand its own capabilities and structure
3. Generate dynamic documentation (README.md)
4. Maintain a living "face" for the repository

Architecture:
    IdentityScanner → Scans manifests, agents, plugins
         ↓
    SystemIdentity → Aggregated view of the system
         ↓
    MukhaGenerator → Creates README.md from identity
         ↓
    Physical File → docs/philosophy/SYSTEM_FACE.md or README.md

"Know thyself, and you shall know the universe."
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("MANAS.Cortex.Mukha")


# =============================================================================
# DATA MODELS
# =============================================================================


@dataclass
class AgentIdentity:
    """Identity of a single agent."""

    agent_id: str
    name: str
    domain: str
    description: str
    version: str
    capabilities: List[str]
    operations: List[Dict[str, Any]]
    risk_level: str
    manifest_path: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "domain": self.domain,
            "description": self.description,
            "version": self.version,
            "capabilities": self.capabilities,
            "operations": [op.get("name", "unknown") for op in self.operations],
            "risk_level": self.risk_level,
        }


@dataclass
class PluginIdentity:
    """Identity of a plugin module."""

    name: str
    path: str
    has_manas: bool
    submodules: List[str]


@dataclass
class SystemIdentity:
    """Complete system identity - the mirror reflection."""

    # Core info
    project_name: str
    version: str
    generated_at: str

    # Agents
    system_agents: List[AgentIdentity] = field(default_factory=list)
    city_agents: List[AgentIdentity] = field(default_factory=list)

    # Plugins
    plugins: List[PluginIdentity] = field(default_factory=list)

    # Statistics
    total_agents: int = 0
    total_capabilities: int = 0
    total_operations: int = 0

    # MANAS state
    manas_tests: int = 0
    opus_iterations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "version": self.version,
            "generated_at": self.generated_at,
            "system_agents": [a.to_dict() for a in self.system_agents],
            "city_agents": [a.to_dict() for a in self.city_agents],
            "plugins": [{"name": p.name, "path": p.path, "has_manas": p.has_manas} for p in self.plugins],
            "statistics": {
                "total_agents": self.total_agents,
                "total_capabilities": self.total_capabilities,
                "total_operations": self.total_operations,
                "manas_tests": self.manas_tests,
            },
        }


# =============================================================================
# IDENTITY SCANNER - The Mirror
# =============================================================================


class IdentityScanner:
    """
    Scans the system to build a complete identity map.

    This is MANAS looking into the mirror - understanding what exists,
    what can be done, and how it all fits together.
    """

    def __init__(self, workspace: Optional[Path] = None):
        self._workspace = workspace or Path.cwd()

    def scan(self) -> SystemIdentity:
        """
        Perform complete system scan.

        Returns:
            SystemIdentity with all discovered components
        """
        logger.info("🪞 MUKHA: Beginning system introspection...")

        identity = SystemIdentity(
            project_name="steward-protocol",
            version=self._get_version(),
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

        # Scan agents
        identity.system_agents = self._scan_system_agents()
        identity.city_agents = self._scan_city_agents()

        # Scan plugins
        identity.plugins = self._scan_plugins()

        # Calculate statistics
        all_agents = identity.system_agents + identity.city_agents
        identity.total_agents = len(all_agents)
        identity.total_capabilities = sum(len(a.capabilities) for a in all_agents)
        identity.total_operations = sum(len(a.operations) for a in all_agents)

        # Scan MANAS state
        identity.manas_tests = self._count_manas_tests()
        identity.opus_iterations = self._scan_opus_iterations()

        logger.info(
            f"🪞 MUKHA: Scan complete - {identity.total_agents} agents, {identity.total_capabilities} capabilities"
        )

        return identity

    def _get_version(self) -> str:
        """Get project version from pyproject.toml."""
        try:
            pyproject = self._workspace / "pyproject.toml"
            if pyproject.exists():
                content = pyproject.read_text()
                for line in content.split("\n"):
                    if line.strip().startswith("version"):
                        # Extract version from 'version = "x.y.z"'
                        parts = line.split("=")
                        if len(parts) == 2:
                            return parts[1].strip().strip('"').strip("'")
        except Exception:
            pass
        return "0.3.0"  # Default

    def _scan_system_agents(self) -> List[AgentIdentity]:
        """Scan system cartridges."""
        agents = []
        system_dir = self._workspace / "vibe_core" / "cartridges" / "system"

        if not system_dir.exists():
            return agents

        for agent_dir in system_dir.iterdir():
            if not agent_dir.is_dir() or agent_dir.name.startswith("_"):
                continue

            manifest = agent_dir / "steward.json"
            if manifest.exists():
                agent = self._parse_manifest(manifest, "SYSTEM")
                if agent:
                    agents.append(agent)

        return sorted(agents, key=lambda a: a.agent_id)

    def _scan_city_agents(self) -> List[AgentIdentity]:
        """Scan agent_city cartridges."""
        agents = []
        city_dir = self._workspace / "vibe_core" / "cartridges" / "agent_city"

        if not city_dir.exists():
            return agents

        for agent_dir in city_dir.iterdir():
            if not agent_dir.is_dir() or agent_dir.name.startswith("_"):
                continue

            manifest = agent_dir / "steward.json"
            if manifest.exists():
                agent = self._parse_manifest(manifest, "CITIZEN")
                if agent:
                    agents.append(agent)

        return sorted(agents, key=lambda a: a.agent_id)

    def _parse_manifest(self, manifest_path: Path, category: str) -> Optional[AgentIdentity]:
        """Parse a steward.json manifest."""
        try:
            data = json.loads(manifest_path.read_text())

            # Extract identity
            identity = data.get("identity", data.get("agent", {}))
            agent_id = identity.get("agent_id", identity.get("id", manifest_path.parent.name))
            name = identity.get("name", agent_id.upper())
            version = identity.get("version", "1.0.0")

            # Extract specs
            specs = data.get("specs", {})
            domain = specs.get("domain", category)
            description = specs.get("description", "No description")

            # Extract capabilities
            capabilities = specs.get("capabilities", [])
            if not capabilities and "capabilities" in data:
                cap_data = data.get("capabilities", {})
                if isinstance(cap_data, dict) and "operations" in cap_data:
                    capabilities = [op.get("name", "") for op in cap_data.get("operations", [])]

            # Extract operations
            operations = data.get("operations", [])
            if not operations and "capabilities" in data:
                cap_data = data.get("capabilities", {})
                if isinstance(cap_data, dict):
                    operations = cap_data.get("operations", [])

            # Extract governance
            governance = data.get("governance", {})
            risk_level = governance.get("risk_level", "MEDIUM")

            return AgentIdentity(
                agent_id=agent_id,
                name=name,
                domain=domain,
                description=description,
                version=version,
                capabilities=capabilities,
                operations=operations if isinstance(operations, list) else [],
                risk_level=risk_level,
                manifest_path=str(manifest_path.relative_to(self._workspace)),
            )

        except Exception as e:
            logger.warning(f"Failed to parse manifest {manifest_path}: {e}")
            return None

    def _scan_plugins(self) -> List[PluginIdentity]:
        """Scan vibe_core/plugins for plugin modules."""
        plugins = []
        plugins_dir = self._workspace / "vibe_core" / "plugins"

        if not plugins_dir.exists():
            return plugins

        for plugin_dir in plugins_dir.iterdir():
            if not plugin_dir.is_dir() or plugin_dir.name.startswith("_"):
                continue

            # Check for MANAS
            has_manas = (plugin_dir / "manas").exists()

            # Get submodules
            submodules = []
            for sub in plugin_dir.iterdir():
                if sub.is_dir() and not sub.name.startswith("_"):
                    submodules.append(sub.name)

            plugins.append(
                PluginIdentity(
                    name=plugin_dir.name,
                    path=str(plugin_dir.relative_to(self._workspace)),
                    has_manas=has_manas,
                    submodules=sorted(submodules),
                )
            )

        return sorted(plugins, key=lambda p: p.name)

    def _count_manas_tests(self) -> int:
        """Count MANAS tests."""
        test_dir = self._workspace / "tests" / "manas"
        if not test_dir.exists():
            return 0

        count = 0
        for test_file in test_dir.glob("test_*.py"):
            try:
                content = test_file.read_text()
                # Count test functions
                count += content.count("def test_")
                count += content.count("async def test_")
            except Exception:
                pass

        return count

    def _scan_opus_iterations(self) -> List[str]:
        """Scan for OPUS iterations in commit history or files."""
        iterations = []

        # Check git log for OPUS commits
        try:
            import subprocess

            result = subprocess.run(
                ["git", "log", "--oneline", "--grep=opus-", "-20"],
                capture_output=True,
                text=True,
                cwd=str(self._workspace),
                timeout=10,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line and "opus-" in line.lower():
                        # Extract OPUS number
                        import re

                        match = re.search(r"opus-(\d+)", line.lower())
                        if match:
                            opus_num = f"OPUS-{match.group(1).zfill(3)}"
                            if opus_num not in iterations:
                                iterations.append(opus_num)
        except Exception:
            pass

        return sorted(iterations, reverse=True)[:10]  # Last 10


# =============================================================================
# MUKHA GENERATOR - The Face
# =============================================================================


class MukhaGenerator:
    """
    Generates the system's "face" - its README and identity documents.

    This is the mouth of MANAS - how it presents itself to the world.
    """

    def __init__(self, workspace: Optional[Path] = None):
        self._workspace = workspace or Path.cwd()
        self._scanner = IdentityScanner(workspace=workspace)

    def generate_readme(self, identity: Optional[SystemIdentity] = None) -> str:
        """
        Generate a complete README.md from system identity.

        Args:
            identity: Pre-scanned identity (or will scan now)

        Returns:
            Complete README.md content
        """
        if identity is None:
            identity = self._scanner.scan()

        return self._render_readme(identity)

    def _render_readme(self, identity: SystemIdentity) -> str:
        """Render the README template with identity data."""
        # Organize agents by domain
        domains: Dict[str, List[AgentIdentity]] = {}
        for agent in identity.system_agents + identity.city_agents:
            domain = agent.domain
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(agent)

        # Build agent sections
        agent_sections = []
        for domain, agents in sorted(domains.items()):
            agent_list = "\n".join(
                [
                    f"| `{a.agent_id}` | {a.description[:50]}{'...' if len(a.description) > 50 else ''} | {len(a.capabilities)} |"
                    for a in agents
                ]
            )
            agent_sections.append(f"""### {domain}

| Agent | Description | Capabilities |
|-------|-------------|--------------|
{agent_list}""")

        agent_content = "\n\n".join(agent_sections)

        # Build plugin section
        plugin_rows = "\n".join(
            [
                f"| `{p.name}` | {'🧠 MANAS' if p.has_manas else '📦 Standard'} | {', '.join(p.submodules[:3])}{'...' if len(p.submodules) > 3 else ''} |"
                for p in identity.plugins
            ]
        )

        # Build OPUS section
        opus_list = (
            "\n".join([f"- {op}" for op in identity.opus_iterations[:5]])
            if identity.opus_iterations
            else "_No OPUS iterations found_"
        )

        # MANAS status
        manas_status = "🟢 OPERATIONAL" if identity.manas_tests > 0 else "⚪ DORMANT"

        readme = f"""<!--
AUTO-GENERATED by MUKHA (OPUS-047)
Generated: {identity.generated_at}
This file reflects the ACTUAL system state.
Manual edits to dynamic sections will be overwritten.
-->

# 🕉️ STEWARD Protocol

*Cryptographic Identity + Governance for AI Agents. A.G.I. Infrastructure.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/MANAS_tests-{identity.manas_tests}-green.svg)](#manas-cognitive-kernel)

---

## 🎯 Quick Start

```bash
git clone https://github.com/kimeisele/steward-protocol
cd steward-protocol
uv sync  # or pip install -e .
steward boot
```

---

## 📊 System Status

| Metric | Value |
|--------|-------|
| **Version** | `{identity.version}` |
| **Total Agents** | {identity.total_agents} |
| **Capabilities** | {identity.total_capabilities} |
| **Operations** | {identity.total_operations} |
| **MANAS Status** | {manas_status} |
| **MANAS Tests** | {identity.manas_tests} |

---

## 🏛️ Architecture

STEWARD Protocol is built on the **Vedic Computing** paradigm:

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLAUDE CODE (Avatar)                        │
│                   "The God Outside the System"                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    MANAS (Cognitive Kernel)                     │
│            "The Mind - Thinks, Wills, Acts"                     │
│                                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │ JNANA   │  │ KRIYA   │  │ SAMVADA │  │  VAK    │            │
│  │Knowledge│→ │ Action  │→ │Dialogue │→ │ Voice   │            │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     VIBE KERNEL (Nervous System)                │
│              Syscalls, Ledger, Constitutional Oath              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       AGENT CITY (Citizens)                     │
│              {len(identity.city_agents)} Citizen Agents                                │
└─────────────────────────────────────────────────────────────────┘
```

### The Three Layers

| Layer | Name | Purpose |
|-------|------|---------|
| **L0** | Foundation | Kernel + Ledger + Constitution |
| **L1** | Federation | {len(identity.system_agents)} System Agents (Governance) |
| **L2** | Citizens | {len(identity.city_agents)} Agent City Residents |

---

## 🤖 Agent Registry

{agent_content}

---

## 🔌 Plugins

| Plugin | Type | Submodules |
|--------|------|------------|
{plugin_rows}

---

## 🧠 MANAS Cognitive Kernel

MANAS (Sanskrit: Mind/Will) is the cognitive layer that gives the system intelligence.

### Capabilities

- **JNANA** (Knowledge): LLM-powered intelligent responses
- **KRIYA** (Action): Chat-to-intent bridging
- **SAMVADA** (Dialogue): Real-time Unix socket communication
- **VAK** (Voice): Safe CLI command execution

### Recent OPUS Iterations

{opus_list}

### Test Coverage

```
Total MANAS Tests: {identity.manas_tests}
```

---

## 🔐 Trust Anchor

This system enforces governance at the kernel level:

- **[CONSTITUTION.md](CONSTITUTION.md)** - The supreme law
- **[Governance Gate](vibe_core/kernel_impl.py)** - Cryptographic enforcement
- **VISNU Kernel Protection** - 21 protected files

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [OPUS.md](OPUS.md) | Live system dashboard |
| [INDEX.md](INDEX.md) | Documentation index |
| [AGENTS.md](AGENTS.md) | Agent registry |
| [CITYMAP.md](CITYMAP.md) | Visual architecture |
| [CONSTITUTION.md](CONSTITUTION.md) | Governance rules |

---

## 🔗 Links

- [Documentation](https://github.com/kimeisele/steward-protocol#readme)
- [Source](https://github.com/kimeisele/steward-protocol)
- [Issues](https://github.com/kimeisele/steward-protocol/issues)

---

*Auto-generated by MUKHA (OPUS-047) · {identity.generated_at[:19]} UTC*
*"Know thyself, and you shall know the universe."*
"""
        return readme

    def update_readme(self) -> Path:
        """
        Update the repository README.md with current system state.

        Returns:
            Path to updated README.md
        """
        # Scan system
        identity = self._scanner.scan()

        # Generate content
        content = self.generate_readme(identity)

        # Archive old README if exists
        readme_path = self._workspace / "README.md"
        if readme_path.exists():
            archive_dir = self._workspace / "docs" / "archive"
            archive_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = archive_dir / f"README_{timestamp}.md"
            archive_path.write_text(readme_path.read_text())
            logger.info(f"📦 Archived old README to {archive_path}")

        # Write new README
        readme_path.write_text(content)
        logger.info(f"✨ Updated README.md ({len(content)} bytes)")

        return readme_path
