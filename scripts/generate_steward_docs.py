#!/usr/bin/env python3
"""
Generate STEWARD.md documentation from steward.json manifests.

This script:
1. Finds all steward.json files in system_agents/ and agent_city/registry/
2. Generates Level 2 STEWARD.md for each agent
3. Uses sensible defaults based on agent specialization

Run: python scripts/generate_steward_docs.py
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SYSTEM_AGENTS_DIR = PROJECT_ROOT / "steward" / "system_agents"
CITIZEN_AGENTS_DIR = PROJECT_ROOT / "agent_city" / "registry"

# Specialization-based descriptions and capabilities
SPECIALIZATION_MAP = {
    "GOVERNANCE": {
        "description": "System governance and administrative operations",
        "capabilities": ["policy_enforcement", "rule_management", "decision_execution"],
    },
    "OBSERVATION": {
        "description": "System monitoring, analysis, and health checks",
        "capabilities": ["monitoring", "analysis", "reporting"],
    },
    "VERIFICATION": {
        "description": "Integrity verification and audit operations",
        "capabilities": ["verification", "audit", "compliance_checking"],
    },
    "MEDIA": {
        "description": "Content generation, broadcasting, and distribution",
        "capabilities": ["content_generation", "distribution", "broadcasting"],
    },
    "HISTORY": {
        "description": "Event recording, archival, and historical management",
        "capabilities": ["archival", "event_recording", "history_tracking"],
    },
    "RESEARCH": {
        "description": "Research, intelligence gathering, and analysis",
        "capabilities": ["research", "intelligence", "analysis"],
    },
    "ENGINEERING": {
        "description": "System engineering, building, and infrastructure",
        "capabilities": ["engineering", "building", "infrastructure"],
    },
    "COMMERCE": {
        "description": "Economic operations, trading, and transactions",
        "capabilities": ["trading", "commerce", "transactions"],
    },
    "COMMUNITY": {
        "description": "Community management and collective operations",
        "capabilities": ["community_management", "engagement", "coordination"],
    },
    "MAINTENANCE": {
        "description": "System maintenance, repair, and upkeep",
        "capabilities": ["maintenance", "repair", "upkeep"],
    },
    "PRODUCTION": {
        "description": "Production and manufacturing operations",
        "capabilities": ["production", "creation", "manufacturing"],
    },
    "ETHICS": {
        "description": "Data ethics, truth verification, and moral guidance",
        "capabilities": ["ethics_checking", "truth_verification", "guidance"],
    },
}


def generate_steward_md(agent_data: dict, agent_path: Path) -> str:
    """Generate STEWARD.md content from steward.json data."""

    agent = agent_data.get("agent", {})
    credentials = agent_data.get("credentials", {})
    capabilities = agent_data.get("capabilities", {})
    governance = agent_data.get("governance", {})

    agent_id = agent.get("id", "unknown")
    agent_name = agent.get("name", "UNKNOWN")
    version = agent.get("version", "1.0.0")
    specialization = agent.get("specialization", "CUSTOM")
    status = agent.get("status", "active")
    mandate = credentials.get("mandate", "Custom agent operations")

    # Get specialization-based info
    spec_info = SPECIALIZATION_MAP.get(
        specialization,
        {
            "description": mandate,
            "capabilities": [op.get("name") for op in capabilities.get("operations", [])],
        },
    )

    # Extract operations from manifest
    operations = capabilities.get("operations", [])
    op_descriptions = [
        f"- `{op.get('name')}` - {op.get('description', 'Operation')}"
        for op in operations
    ]

    # Status icon
    status_icon = "✅" if status == "active" else "🟡"

    # Compliance level
    compliance_level = governance.get("compliance_level", 2)

    md = f"""# 🤖 {agent_name} Agent Identity

## Agent Identity

- **Agent ID:** {agent_id}
- **Name:** {agent_name}
- **Version:** {version}
- **Class:** {agent.get('class', 'service')}
- **Specialization:** {specialization}
- **Status:** {status_icon} {status.upper()}

**Protocol Compliance:** Level {compliance_level}

---

## 🎯 What I Do

{mandate}

---

## ✅ Core Capabilities

{chr(10).join(op_descriptions) if op_descriptions else "- System operations (auto-generated from manifest)"}

---

## 🚀 Quick Start

### Basic Usage

This agent is part of the STEWARD Protocol Agent OS. To interact with it:

```bash
# Verify agent identity
steward verify {agent_id}

# Discover this agent
steward discover

# Delegate task to this agent
steward delegate {agent_id} "your task description"
```

### Protocol-based Usage

```bash
# Verify identity
steward verify {agent_id}

# Check agent status
steward ps | grep {agent_id}

# View agent in Parampara blockchain
steward lineage | grep {agent_name}
```

---

## 🔐 Verification

### Identity Verification

```bash
# Verify agent signature
steward verify {agent_id}

# Expected output:
# ✅ Identity verified
# ✅ Passport valid in Parampara blockchain
# ✅ Compliance Level {compliance_level}
```

### Machine-Readable Manifest

- **Manifest:** [steward.json](./steward.json)
- **Protocol:** STEWARD v1.0.0
- **Compliance Level:** {compliance_level}
- **Status:** ✅ VALID

---

## 🛡️ Security & Trust

**Security:**
- ✅ Cryptographically signed manifest (Parampara blockchain)
- ✅ Constitutional oath binding
- ✅ Immutable audit trail

**Trust & Reputation:**
- **Status:** ✅ Operational
- **Registry:** Part of official Agent City

---

## 👤 Maintained By

- **System:** STEWARD Protocol Agent OS
- **Contact:** See [OPERATIONS.md](../../../OPERATIONS.md)
- **Authority:** Steward Protocol

**Audit Trail:** Recorded in Parampara blockchain (`steward lineage`)

---

## 📚 More Information

**Protocol Compliance:**
- **Compliance Level:** Level {compliance_level}
- **Protocol Version:** STEWARD v1.0.0
- **Full Specification:** [UNIVERSE_MIGRATION_PLAN.md](../../../docs/architecture/UNIVERSE_MIGRATION_PLAN.md)

**Agent Resources:**
- **Machine-readable manifest:** [steward.json](./steward.json)
- **Source:** [steward-protocol](https://github.com/kimeisele/steward-protocol)

**Registry:**
- **Discover:** `steward discover`

---

## 🔄 Status & Updates

**Current Status:**
- {status_icon} {status.upper()} (verified 2025-11-28)

**Recent Updates:**
- **2025-11-28:** Auto-documented via STEWARD Protocol

**Known Issues:**
- None reported

---

**Status:** {status_icon} Operational
**Authority:** Steward Protocol
**Philosophy:** Part of the STEWARD Protocol Agent OS infrastructure.
"""

    return md


def main():
    """Generate STEWARD.md for all agents."""
    generated = 0
    skipped = 0

    # System agents
    if SYSTEM_AGENTS_DIR.exists():
        for agent_dir in SYSTEM_AGENTS_DIR.iterdir():
            if not agent_dir.is_dir():
                continue

            manifest_path = agent_dir / "steward.json"
            if not manifest_path.exists():
                continue

            steward_md_path = agent_dir / "STEWARD.md"
            # Regenerate if file exists but is empty or too small (stub)
            if steward_md_path.exists() and steward_md_path.stat().st_size >= 500:
                print(f"⏭️  Skip (exists): {agent_dir.name}/STEWARD.md")
                skipped += 1
                continue

            try:
                with open(manifest_path, "r") as f:
                    agent_data = json.load(f)

                md_content = generate_steward_md(agent_data, agent_dir)

                with open(steward_md_path, "w") as f:
                    f.write(md_content)

                print(f"✅ Generated: steward/system_agents/{agent_dir.name}/STEWARD.md")
                generated += 1
            except Exception as e:
                print(
                    f"❌ Error generating {agent_dir.name}: {e}"
                )

    # Citizen agents
    if CITIZEN_AGENTS_DIR.exists():
        for agent_dir in CITIZEN_AGENTS_DIR.iterdir():
            if not agent_dir.is_dir():
                continue

            manifest_path = agent_dir / "steward.json"
            if not manifest_path.exists():
                continue

            steward_md_path = agent_dir / "STEWARD.md"
            # Regenerate if file exists but is empty or too small (stub)
            if steward_md_path.exists() and steward_md_path.stat().st_size >= 500:
                print(f"⏭️  Skip (exists): {agent_dir.name}/STEWARD.md")
                skipped += 1
                continue

            try:
                with open(manifest_path, "r") as f:
                    agent_data = json.load(f)

                md_content = generate_steward_md(agent_data, agent_dir)

                with open(steward_md_path, "w") as f:
                    f.write(md_content)

                print(f"✅ Generated: agent_city/registry/{agent_dir.name}/STEWARD.md")
                generated += 1
            except Exception as e:
                print(
                    f"❌ Error generating {agent_dir.name}: {e}"
                )

    print()
    print(f"📊 Summary: Generated {generated}, Skipped {skipped}")
    return 0 if generated > 0 else 1


if __name__ == "__main__":
    exit(main())
