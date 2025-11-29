#!/usr/bin/env python3
"""
Fix all steward.json manifests with correct values from code.
"""
import json
import re
from pathlib import Path

# Map agent_id -> correct values from code
AGENT_INFO = {
    "oracle": {
        "name": "ORACLE",
        "description": "System introspection and explanation agent",
        "domain": "SYSTEM",
        "version": "1.0.0",
    },
    "watchman": {
        "name": "WATCHMAN",
        "description": "System integrity and monitoring agent",
        "domain": "SYSTEM",
        "version": "1.0.0",
    },
    "forum": {
        "name": "FORUM",
        "description": "Democratic decision layer for governance",
        "domain": "GOVERNANCE",
        "version": "1.0.0",
    },
    "supreme_court": {
        "name": "SUPREME_COURT",
        "description": "Appellate justice system with mercy protocol",
        "domain": "JUSTICE",
        "version": "1.0.0",
    },
    "herald": {
        "name": "HERALD",
        "description": "Content generation and broadcasting agent",
        "domain": "MEDIA",
        "version": "1.0.0",
    },
    "archivist": {
        "name": "ARCHIVIST",
        "description": "Event verification and audit trail agent",
        "domain": "SYSTEM",
        "version": "1.0.0",
    },
    "science": {
        "name": "SCIENCE",
        "description": "External intelligence module via web research",
        "domain": "INTELLIGENCE",
        "version": "1.0.0",
    },
    "engineer": {
        "name": "ENGINEER",
        "description": "Meta-agent for building new agents and code",
        "domain": "INFRASTRUCTURE",
        "version": "1.0.0",
    },
    "auditor": {
        "name": "AUDITOR",
        "description": "GAD-000 compliance enforcement agent",
        "domain": "GOVERNANCE",
        "version": "1.0.0",
    },
    "envoy": {
        "name": "ENVOY",
        "description": "Universal operator interface agent",
        "domain": "INTERFACE",
        "version": "1.0.0",
    },
    "chronicle": {
        "name": "CHRONICLE",
        "description": "Temporal operations and event tracking",
        "domain": "SYSTEM",
        "version": "1.0.0",
    },
    "scribe": {
        "name": "SCRIBE",
        "description": "Autonomous documentation generation agent",
        "domain": "INFRASTRUCTURE",
        "version": "1.0.0",
    },
    "discoverer": {
        "name": "DISCOVERER",
        "description": "Agent discovery, verification, and registration",
        "domain": "GOVERNANCE",
        "version": "1.0.0",
    },
}


def fix_manifest(agent_id: str, manifest_path: Path):
    """Fix a single manifest file"""
    if agent_id not in AGENT_INFO:
        print(f"⚠️  Skipping {agent_id} - no info available")
        return False

    with open(manifest_path) as f:
        manifest = json.load(f)

    info = AGENT_INFO[agent_id]

    # Update identity
    manifest["identity"]["agent_id"] = agent_id
    manifest["identity"]["name"] = info["name"]

    # Update specs
    manifest["specs"]["description"] = info["description"]
    manifest["specs"]["domain"] = info["domain"]
    manifest["specs"]["version"] = info["version"]

    # Write back
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"✅ Fixed {agent_id}")
    return True


def main():
    agents_dir = Path("steward/system_agents")
    fixed = 0

    for agent_dir in agents_dir.iterdir():
        if not agent_dir.is_dir():
            continue

        agent_id = agent_dir.name
        manifest_path = agent_dir / "steward.json"

        if not manifest_path.exists():
            print(f"⚠️  No manifest: {agent_id}")
            continue

        if fix_manifest(agent_id, manifest_path):
            fixed += 1

    print(f"\n✅ Fixed {fixed} manifests")


if __name__ == "__main__":
    main()
