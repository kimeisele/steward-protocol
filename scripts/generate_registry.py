#!/usr/bin/env python3
"""
Steward Protocol Registry Generator

Automatically discovers and catalogs all agents in the system.
Generates AGENTS.md based on actual cartridge configurations.

Usage:
    python scripts/generate_registry.py

This creates a self-documenting agent registry that reflects
the actual state of the system (Layer 3: Discovery).
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class RegistryGenerator:
    """Scans the codebase and generates agent registry"""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.agents: List[Dict[str, Any]] = []

    def discover_agents(self) -> None:
        """Find all cartridge_main.py files and extract metadata"""
        cartridge_files = sorted(self.root_dir.glob("*/cartridge_main.py"))

        for cartridge_file in cartridge_files:
            agent_dir = cartridge_file.parent.name
            metadata = self._extract_metadata(cartridge_file, agent_dir)
            if metadata:
                self.agents.append(metadata)

    def _extract_metadata(self, cartridge_file: Path, agent_name: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from a cartridge file"""
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
        """Extract the module-level docstring"""
        match = re.match(r'^\s*"""(.*?)"""', content, re.DOTALL)
        if match:
            text = match.group(1).strip()
            # Get only the first paragraph/line
            first_line = text.split('\n')[0].strip()
            return first_line
        return ""

    def _extract_class_docstring(self, content: str, class_name: str) -> str:
        """Extract docstring from a class"""
        pattern = rf'class\s+{class_name}\s*:.*?"""(.*?)"""'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            text = match.group(1).strip()
            # Get first few lines
            lines = text.split('\n')
            return lines[0].strip() if lines else ""
        return ""

    def _extract_field(self, content: str, field_name: str) -> str:
        """Extract a specific field value (name = "value")"""
        pattern = rf'{field_name}\s*=\s*["\']([^"\']*)["\']'
        match = re.search(pattern, content)
        if match:
            return match.group(1)
        return "1.0.0" if field_name == "version" else ""

    def _discover_tools(self, agent_name: str) -> List[Dict[str, str]]:
        """Find all tools for an agent"""
        tools_dir = self.root_dir / agent_name / "tools"
        tools = []

        if tools_dir.exists():
            for tool_file in sorted(tools_dir.glob("*.py")):
                if tool_file.name == "__init__.py":
                    continue

                # Try to extract docstring from tool
                tool_name = self._tool_filename_to_name(tool_file.stem)
                tool_doc = self._extract_tool_docstring(tool_file)

                tools.append({
                    'name': tool_name,
                    'file': tool_file.stem + ".py",
                    'description': tool_doc
                })

        return tools

    def _tool_filename_to_name(self, filename: str) -> str:
        """Convert filename to tool name (scout_tool -> Scout)"""
        name = filename.replace("_tool", "").replace("_", " ").title().replace(" ", "")
        return name

    def _extract_tool_docstring(self, tool_file: Path) -> str:
        """Extract docstring from a tool file"""
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

    def generate_registry(self) -> str:
        """Generate the AGENTS.md content"""
        self.discover_agents()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")

        content = f"""# 🏙️ AGENT CITY REGISTRY

**Autogenerated by Steward Protocol Registry Generator**
**Last Updated:** {timestamp}

---

## 🏛️ GOVERNANCE

| Field | Value |
|-------|-------|
| **Constitution** | [CONSTITUTION.md](./CONSTITUTION.md) |
| **Protocol Level** | 3 (Federated Discovery) |
| **Status** | ✅ Active & Enforced |
| **Registry Version** | 1.0 |

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

---

## 📝 NOTES

This registry is **auto-generated** from the actual cartridge configurations.
When you add or modify an agent's tools, re-run `python scripts/generate_registry.py` to update this document.

### How It Works

1. **Discovery**: Scans all `*/cartridge_main.py` files
2. **Extraction**: Parses class definitions and docstrings
3. **Tools**: Discovers `*/tools/*.py` modules
4. **Generation**: Writes to `AGENTS.md`

This is **Layer 3 (Discovery)** of the Steward Protocol—the system explaining itself.
"""

        return content

    def _format_agent_section(self, agent: Dict[str, Any]) -> str:
        """Format a single agent section"""
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

    def write_registry(self, output_file: str = "AGENTS.md") -> None:
        """Write the registry to a file"""
        content = self.generate_registry()

        output_path = self.root_dir / output_file
        with open(output_path, 'w') as f:
            f.write(content)

        print(f"✅ Registry generated: {output_path}")
        print(f"📊 Discovered {len(self.agents)} agents")
        print(f"🔧 Total tools: {sum(len(a['tools']) for a in self.agents)}")


def main():
    """Main entry point"""
    import sys

    # If called with an argument, use it as the root dir
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    gen = RegistryGenerator(root_dir)
    gen.write_registry()


if __name__ == "__main__":
    main()
