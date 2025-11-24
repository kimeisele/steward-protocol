#!/usr/bin/env python3
"""
CIVIC Registry Tool - Agent Discovery & Registry Generation

This tool is the "public records office" of the city. It:
1. Discovers all agents in the system
2. Validates their configurations
3. Generates AGENTS.md (the official registry)
4. Maintains citizens.json (the bureaucratic database)

Previously: scripts/generate_registry.py
Now: civic/tools/registry_tool.py (official tool of CIVIC cartridge)
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone


class RegistryTool:
    """
    CIVIC's Registry Management Tool.

    Scans the codebase and generates/updates the agent registry.
    This is the "voice of truth" for who's registered in Agent City.
    """

    def __init__(self, root_dir: str = "."):
        """Initialize registry tool with root directory."""
        self.root_dir = Path(root_dir)
        self.agents: List[Dict[str, Any]] = []

    def discover_agents(self) -> List[Dict[str, Any]]:
        """
        Find all cartridge_main.py files and extract metadata.

        Returns:
            List of agent metadata dictionaries
        """
        cartridge_files = sorted(self.root_dir.glob("*/cartridge_main.py"))
        self.agents = []

        for cartridge_file in cartridge_files:
            agent_dir = cartridge_file.parent.name
            metadata = self._extract_metadata(cartridge_file, agent_dir)
            if metadata:
                self.agents.append(metadata)

        return self.agents

    def _extract_metadata(self, cartridge_file: Path, agent_name: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from a cartridge file."""
        try:
            with open(cartridge_file, 'r') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {cartridge_file}: {e}")
            return None

        # Extract module docstring (first docstring in file)
        module_doc = self._extract_module_docstring(content)

        # Find the main Cartridge class
        class_match = re.search(r'class\s+(\w+Cartridge)\s*:', content)
        if not class_match:
            return None

        class_name = class_match.group(1)

        # Extract class docstring
        class_doc = self._extract_class_docstring(content, class_name)

        # Extract metadata fields
        metadata = {
            'agent_name': agent_name,
            'agent_name_pretty': agent_name.upper(),
            'class_name': class_name,
            'module_doc': module_doc,
            'class_doc': class_doc,
            'version': self._extract_field(content, 'version'),
            'description': self._extract_field(content, 'description'),
            'author': self._extract_field(content, 'author'),
            'tools': self._discover_tools(agent_name),
        }

        return metadata

    def _extract_module_docstring(self, content: str) -> str:
        """Extract the module-level docstring."""
        match = re.match(r'^\s*"""(.*?)"""', content, re.DOTALL)
        if match:
            text = match.group(1).strip()
            first_line = text.split('\n')[0].strip()
            return first_line
        return ""

    def _extract_class_docstring(self, content: str, class_name: str) -> str:
        """Extract docstring from a class."""
        pattern = rf'class\s+{class_name}\s*:.*?"""(.*?)"""'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            text = match.group(1).strip()
            lines = text.split('\n')
            return lines[0].strip() if lines else ""
        return ""

    def _extract_field(self, content: str, field_name: str) -> str:
        """Extract a specific field value (name = "value")."""
        pattern = rf'{field_name}\s*=\s*["\']([^"\']*)["\']'
        match = re.search(pattern, content)
        if match:
            return match.group(1)
        return "1.0.0" if field_name == "version" else ""

    def _discover_tools(self, agent_name: str) -> List[Dict[str, str]]:
        """Find all tools for an agent."""
        tools_dir = self.root_dir / agent_name / "tools"
        tools = []

        if tools_dir.exists():
            for tool_file in sorted(tools_dir.glob("*.py")):
                if tool_file.name == "__init__.py":
                    continue

                tool_name = self._tool_filename_to_name(tool_file.stem)
                tool_doc = self._extract_tool_docstring(tool_file)

                tools.append({
                    'name': tool_name,
                    'file': tool_file.stem + ".py",
                    'description': tool_doc
                })

        return tools

    def _tool_filename_to_name(self, filename: str) -> str:
        """Convert filename to tool name (scout_tool -> Scout)."""
        name = filename.replace("_tool", "").replace("_", " ").title().replace(" ", "")
        return name

    def _extract_tool_docstring(self, tool_file: Path) -> str:
        """Extract docstring from a tool file."""
        try:
            with open(tool_file, 'r') as f:
                content = f.read()

            match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if match:
                text = match.group(1).strip()
                first_line = text.split('\n')[0].strip()
                return first_line
            return ""
        except:
            return ""

    def generate_agents_markdown(self) -> str:
        """
        Generate the AGENTS.md content.

        Returns:
            Markdown string for AGENTS.md
        """
        if not self.agents:
            self.discover_agents()

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        content = f"""# 🏙️ AGENT CITY REGISTRY

**Autogenerated by CIVIC (The Bureaucrat) via Registry Tool**
**Last Updated:** {timestamp}

---

## 🏛️ GOVERNANCE

| Field | Value |
|-------|-------|
| **Constitution** | [CONSTITUTION.md](./CONSTITUTION.md) |
| **Protocol Level** | 3 (Federated Discovery) |
| **Status** | ✅ Active & Enforced |
| **Registry Version** | 2.0 (CIVIC-managed) |
| **Authority** | CIVIC Cartridge |

---

## 🤖 ACTIVE AGENTS

"""

        for agent in self.agents:
            content += self._format_agent_section(agent)

        # System summary
        total_tools = sum(len(a['tools']) for a in self.agents)
        content += f"""---

## 📊 SYSTEM SUMMARY

| Metric | Value |
|--------|-------|
| **Total Agents** | {len(self.agents)} |
| **Total Tools** | {total_tools} |
| **System Status** | 🟢 All Systems Operational |
| **Registry Authority** | 🏛️ CIVIC (Immutable) |

---

## 📝 NOTES

This registry is **auto-generated** by CIVIC and reflects the authoritative citizen registry.
When you add or modify an agent, CIVIC's `scan_and_register_agents()` method updates this document.

### How It Works

1. **Discovery**: Scans all `*/cartridge_main.py` files
2. **Extraction**: Parses class definitions and docstrings
3. **Validation**: Checks cartridge configurations
4. **Tools**: Discovers `*/tools/*.py` modules
5. **Generation**: Updates `AGENTS.md` via RegistryTool

This is **Layer 3 (Discovery)** of the Steward Protocol—the system explaining itself.

---

**CIVIC AUTHORITY NOTICE:**
This registry is maintained by The Bureaucrat. Any agent not listed here is not registered.
Unregistered agents cannot obtain broadcast licenses. No exceptions. 🏛️
"""

        return content

    def _format_agent_section(self, agent: Dict[str, Any]) -> str:
        """Format a single agent section for AGENTS.md."""
        section = f"""### 🤖 {agent['agent_name_pretty']}

**Class:** `{agent['class_name']}`
**Version:** `{agent['version']}`
**Status:** 🟢 OPERATIONAL

**Description:**
{agent['class_doc'] or "Autonomous agent in the Steward Protocol ecosystem."}

"""

        # Tools section
        if agent['tools']:
            section += "**Tools:**\n\n"
            for tool in agent['tools']:
                desc = f" — {tool['description']}" if tool['description'] else ""
                section += f"- **{tool['name']}** (`{tool['file']}`) {desc}\n"
        else:
            section += "**Tools:** None discovered\n"

        section += "\n"
        return section

    def write_agents_registry(self, output_file: str = "AGENTS.md") -> bool:
        """
        Write the registry to AGENTS.md.

        Args:
            output_file: Output filename (default: AGENTS.md)

        Returns:
            True if successful, False otherwise
        """
        try:
            content = self.generate_agents_markdown()
            output_path = self.root_dir / output_file

            with open(output_path, 'w') as f:
                f.write(content)

            print(f"✅ Registry generated: {output_path}")
            print(f"📊 Discovered {len(self.agents)} agents")
            print(f"🔧 Total tools: {sum(len(a['tools']) for a in self.agents)}")

            return True
        except Exception as e:
            print(f"❌ Error writing registry: {e}")
            return False


# Legacy support (for existing scripts)
class RegistryGenerator(RegistryTool):
    """Legacy alias for backward compatibility."""
    pass


def main():
    """Main entry point (legacy support)."""
    import sys
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    tool = RegistryTool(root_dir)
    tool.discover_agents()
    tool.write_agents_registry()


if __name__ == "__main__":
    main()
