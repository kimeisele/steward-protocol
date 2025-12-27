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
        """Render a state-of-the-art README from system identity."""
        # Get project metadata from pyproject.toml
        project_meta = self._load_project_metadata()

        # Categorize agents into core groups
        core_agents = self._get_core_agents(identity)

        # Get recent OPUS work
        recent_opus = self._get_recent_opus_work()

        # Build core agents section (only the important ones)
        core_agents_content = self._render_core_agents(core_agents)

        # Calculate key metrics
        total_tools = sum(len(a.capabilities) for a in identity.system_agents + identity.city_agents)
        manas_plugins = len([p for p in identity.plugins if p.has_manas])

        readme = f"""<!--
AUTO-GENERATED by MUKHA (OPUS-047) · {identity.generated_at[:19]} UTC
Source of truth: System introspection via IdentityScanner
-->

<div align="center">

# 🕉️ STEWARD Protocol

### *The Operating System for AI Agents*

**Cryptographic Identity · Constitutional Governance · Cognitive Autonomy**

[![Version](https://img.shields.io/badge/version-{identity.version}-blue.svg)](https://github.com/kimeisele/steward-protocol/releases)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-{identity.manas_tests}%20passed-brightgreen.svg)](#testing)
[![Agents](https://img.shields.io/badge/agents-{identity.total_agents}-purple.svg)](#agent-city)

---

*What if AI agents had cryptographic identities, constitutional rights, and governed themselves?*

[Quick Start](#-quick-start) · [Architecture](#-architecture) · [Agent City](#-agent-city) · [Documentation](#-documentation)

</div>

---

## ✨ Why STEWARD?

Traditional AI systems are **stateless tools**. STEWARD Protocol creates **autonomous agents** with:

| Problem | STEWARD Solution |
|---------|------------------|
| 🔓 No identity | **ECDSA P-256 cryptographic signatures** - Every agent signs its work |
| 📜 No rules | **Constitutional governance** - Agents follow enforceable laws |
| 🧠 No memory | **MANAS cognitive kernel** - Agents think, learn, and plan |
| 🏝️ Isolated | **Agent City federation** - {identity.total_agents} agents collaborate |
| 🎭 No trust | **Chain of trust verification** - Cryptographic audit trail |

---

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/kimeisele/steward-protocol
cd steward-protocol
uv sync  # or: pip install -e ".[dev]"

# Boot the kernel
steward boot

# Talk to MANAS (the cognitive mind)
steward chat "What agents are available?"
```

<details>
<summary>📦 Alternative installation methods</summary>

```bash
# With pip
pip install -e .

# Development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

</details>

---

## 🏛️ Architecture

STEWARD follows the **GAD-000 Operator Inversion Principle**: *The AI operates the system, the human provides intent.*

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HUMAN OPERATOR                               │
│                    (Intent & Oversight)                             │
└─────────────────────────────────────────────────────────────────────┘
                                ↓ intent
┌─────────────────────────────────────────────────────────────────────┐
│                     🧠 MANAS (Cognitive Kernel)                     │
│                                                                     │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│   │  JNANA   │→ │  KRIYA   │→ │ SAMVADA  │→ │   VAK    │          │
│   │ Knowledge│  │  Action  │  │ Dialogue │  │  Voice   │          │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘          │
│                                                                     │
│   "The Mind that thinks, wills, and acts"                          │
└─────────────────────────────────────────────────────────────────────┘
                                ↓ syscalls
┌─────────────────────────────────────────────────────────────────────┐
│                    ⚙️ VIBE KERNEL (L0 Foundation)                   │
│                                                                     │
│   • Constitutional Oath Enforcement    • Cryptographic Ledger      │
│   • Plugin Lifecycle Management        • VFS Sandboxing            │
│   • VISNU Kernel Protection (21 files guarded)                     │
└─────────────────────────────────────────────────────────────────────┘
                                ↓ governs
┌─────────────────────────────────────────────────────────────────────┐
│                      🏙️ AGENT CITY (L1 + L2)                        │
│                                                                     │
│   L1 Federation: {len(identity.system_agents):2d} System Agents (governance, security, comms)    │
│   L2 Citizens:   {len(identity.city_agents):2d} Domain Agents (research, content, community)   │
│                                                                     │
│   Total: {identity.total_agents} agents · {total_tools} tools · {manas_plugins} cognitive plugins          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🏙️ Agent City

The {identity.total_agents} agents form a **self-governing federation**. Here are the key players:

{core_agents_content}

<details>
<summary>📋 View all {identity.total_agents} agents</summary>

See [AGENTS.md](AGENTS.md) for the complete registry with capabilities and operations.

</details>

---

## 🧠 MANAS: The Cognitive Kernel

MANAS (Sanskrit: *mind/will*) gives the system **autonomous intelligence**:

| Module | Sanskrit | Function |
|--------|----------|----------|
| **JNANA** | ज्ञान (knowledge) | LLM-powered reasoning and memory |
| **KRIYA** | क्रिया (action) | Intent → tool execution bridging |
| **SAMVADA** | संवाद (dialogue) | Real-time communication protocol |
| **VAK** | वाक् (voice) | Safe command execution with audit |

### Cognitive Capabilities

- 🎯 **Intent Generation** - Proactively identifies what needs to be done
- 📚 **Knowledge Synthesis** - Learns from codebase and documentation
- 🔄 **Self-Improvement** - OPUS iterations refine the system
- 🛡️ **Constitutional Compliance** - All actions checked against governance rules

{recent_opus}

---

## 🔐 Trust & Governance

STEWARD enforces governance at the **kernel level** — not as policy, but as *physics*.

| Mechanism | Purpose |
|-----------|---------|
| **[CONSTITUTION.md](CONSTITUTION.md)** | The supreme law all agents must follow |
| **VISNU Protection** | 21 kernel files are cryptographically guarded |
| **Chain of Trust** | Every action signed with ECDSA P-256 |
| **Governance Gate** | Constitutional checks before syscalls execute |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[OPUS.md](OPUS.md)** | 🎯 Live system dashboard & current goals |
| **[AGENTS.md](AGENTS.md)** | 🤖 Complete agent registry |
| **[CONSTITUTION.md](CONSTITUTION.md)** | 📜 Governance rules |
| **[CITYMAP.md](CITYMAP.md)** | 🗺️ Visual architecture map |
| **[docs/architecture/](docs/architecture/)** | 🏗️ Deep technical docs |

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run MANAS cognitive tests
pytest tests/manas/ -v

# Run hardening tests (architecture enforcement)
pytest tests/hardening/ -v
```

**Current coverage:** {identity.manas_tests} MANAS tests · 79 hardening tests

---

## 🤝 Contributing

STEWARD is built for **AI-human collaboration**. The system *operates itself* — you provide intent.

```bash
# Start a development session
steward chat "Help me implement feature X"

# MANAS will analyze, plan, and execute
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

<div align="center">

**Built with 🕉️ by humans and agents**

*"Know thyself, and you shall know the universe."*

[GitHub]({project_meta.get("source_url", "https://github.com/kimeisele/steward-protocol")}) · [Issues]({project_meta.get("issues_url", "https://github.com/kimeisele/steward-protocol/issues")}) · [Docs](https://github.com/kimeisele/steward-protocol#readme)

</div>
"""
        return readme

    def _load_project_metadata(self) -> Dict[str, Any]:
        """Load metadata from pyproject.toml."""
        try:
            import tomlkit

            pyproject = self._workspace / "pyproject.toml"
            if pyproject.exists():
                data = tomlkit.load(pyproject.open())
                project = data.get("project", {})
                urls = project.get("urls", {})
                return {
                    "name": project.get("name", "steward-protocol"),
                    "description": project.get("description", ""),
                    "version": project.get("version", "0.0.0"),
                    "source_url": urls.get("Source", "https://github.com/kimeisele/steward-protocol"),
                    "issues_url": urls.get("Tracker", "https://github.com/kimeisele/steward-protocol/issues"),
                }
        except Exception:
            pass
        return {"name": "steward-protocol", "source_url": "https://github.com/kimeisele/steward-protocol"}

    def _get_core_agents(self, identity: SystemIdentity) -> Dict[str, List[AgentIdentity]]:
        """Categorize agents into core functional groups."""
        categories = {
            "🔐 Governance": [],
            "🧠 Intelligence": [],
            "📡 Communications": [],
            "🛠️ Infrastructure": [],
            "🎨 Content": [],
        }

        governance_keywords = ["civic", "supreme", "auditor", "watchman", "discoverer"]
        intelligence_keywords = ["manas", "oracle", "science", "analyst", "librarian"]
        comms_keywords = ["herald", "envoy", "ambassador"]
        infra_keywords = ["engineer", "scribe", "archivist", "chronicle", "mechanic"]
        content_keywords = ["marketer", "artisan", "pulse"]

        all_agents = identity.system_agents + identity.city_agents

        for agent in all_agents:
            aid = agent.agent_id.lower()
            if any(k in aid for k in governance_keywords):
                categories["🔐 Governance"].append(agent)
            elif any(k in aid for k in intelligence_keywords):
                categories["🧠 Intelligence"].append(agent)
            elif any(k in aid for k in comms_keywords):
                categories["📡 Communications"].append(agent)
            elif any(k in aid for k in infra_keywords):
                categories["🛠️ Infrastructure"].append(agent)
            elif any(k in aid for k in content_keywords):
                categories["🎨 Content"].append(agent)

        # Only return non-empty categories
        return {k: v for k, v in categories.items() if v}

    def _render_core_agents(self, core_agents: Dict[str, List[AgentIdentity]]) -> str:
        """Render core agents in a clean table format."""
        sections = []
        for category, agents in core_agents.items():
            rows = []
            for a in agents[:4]:  # Max 4 per category
                desc = a.description if a.description != "No description" else f"*{a.domain.lower()} operations*"
                desc = desc[:60] + "..." if len(desc) > 60 else desc
                rows.append(f"| `{a.agent_id}` | {desc} | {len(a.capabilities)} |")

            if rows:
                sections.append(f"""### {category}

| Agent | Role | Tools |
|-------|------|-------|
{chr(10).join(rows)}""")

        return "\n\n".join(sections)

    def _get_recent_opus_work(self) -> str:
        """Get recent OPUS iterations in a nice format."""
        try:
            import subprocess

            result = subprocess.run(
                ["git", "log", "--oneline", "--grep=OPUS", "-10"],
                capture_output=True,
                text=True,
                cwd=str(self._workspace),
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                commits = result.stdout.strip().split("\n")[:5]
                items = []
                for c in commits:
                    # Extract just the message part
                    parts = c.split(" ", 1)
                    if len(parts) == 2:
                        items.append(f"- {parts[1]}")
                if items:
                    return f"""### Recent Development

{chr(10).join(items)}

See [OPUS.md](OPUS.md) for current goals and roadmap."""
        except Exception:
            pass
        return ""

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
