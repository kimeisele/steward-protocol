"""
ENGINEER Builder Tool - Agent Factory (Tool Protocol).

TEMPLATE-BASED SCAFFOLDING:
Uses templates from engineer/templates/agent/ directory.
NO hardcoded strings - reads and transforms template files.

Capabilities:
- Scaffold complete agent from template
- Generate cartridge code via LLM service
- Proper steward.json, cartridge.yaml, cartridge_main.py creation

Tool Protocol compliant for kernel-managed execution.
"""

import logging
from pathlib import Path
from typing import Any, Dict

from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger("ENGINEER_BUILDER")

# Template directory (relative to this file)
TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "agent"


class BuilderTool(Tool):
    """
    The Engineer's Agent Factory (Tool Protocol).

    TEMPLATE-DRIVEN: Reads template files from templates/agent/,
    replaces placeholders, and writes to target directory.

    NO HARDCODED STRINGS in the output - everything comes from template files.
    Updates to the template automatically apply to new agents.
    """

    # Placeholder mapping - what to replace in templates
    PLACEHOLDERS = [
        "YOUR_AGENT_ID",
        "YOUR_AGENT_NAME",
        "YOUR_DOMAIN",
        "YOUR_AGENT_DESCRIPTION",
        "YOUR_NAME",
        "YOUR_AGENT_CLASS",
        "YOUR_AGENT_ROLE",
        "YOUR_CAPABILITY_1",
        "YOUR_CAPABILITY_2",
        "YOUR_SHORT_DESCRIPTION",
        "YOUR_TOOL_DESCRIPTION_HERE",
        "YOUR_TOOL_NAME",
        "YourAgentCartridge",
    ]

    def __init__(self):
        """Initialize builder tool."""
        self.template_dir = TEMPLATE_DIR
        if not self.template_dir.exists():
            logger.warning(f"⚠️ Template directory not found: {self.template_dir}")
        else:
            logger.info(f"🔨 Builder Tool initialized (templates: {self.template_dir})")

    @property
    def name(self) -> str:
        return "engineer.builder"  # Namespaced: agent_id.tool_name

    @property
    def description(self) -> str:
        return "Agent scaffolding and code generation - scaffold structure, generate cartridge code"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'scaffold' (create agent from template)",
            },
            "name": {
                "type": "string",
                "required": True,
                "description": "Agent name (e.g., 'lazara')",
            },
            "domain": {
                "type": "string",
                "required": True,
                "description": "Agent domain (e.g., 'SECURITY', 'RESEARCH', 'MEDIA')",
            },
            "description": {
                "type": "string",
                "required": False,
                "description": "Agent description/mission",
            },
            "target_dir": {
                "type": "string",
                "required": False,
                "description": "Target directory (default: agent_city/registry/{name})",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        if action != "scaffold":
            raise ValueError(f"Invalid action: {action}. Only 'scaffold' is supported.")

        if "name" not in parameters:
            raise ValueError("Missing required parameter: name")

        if "domain" not in parameters:
            raise ValueError("Missing required parameter: domain")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute builder operation - scaffold from template."""
        try:
            name = parameters["name"].lower()
            domain = parameters["domain"].upper()
            description = parameters.get("description", f"{name.capitalize()} agent for {domain} domain")
            target_dir = parameters.get("target_dir", f"agent_city/registry/{name}")

            result = self.scaffold_from_template(
                agent_id=name,
                agent_name=name.upper(),
                domain=domain,
                description=description,
                target_dir=Path(target_dir),
            )

            if result["success"]:
                return ToolResult(
                    success=True,
                    output=result,
                    metadata={
                        "action": "scaffold",
                        "path": target_dir,
                        "files_created": result.get("files_created", []),
                    },
                )
            else:
                return ToolResult(
                    success=False,
                    error=result.get("error", "Scaffold failed"),
                )

        except Exception as e:
            error_msg = f"Builder tool execution failed: {type(e).__name__}: {e!s}"
            logger.error(f"BuilderTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)

    def scaffold_from_template(
        self,
        agent_id: str,
        agent_name: str,
        domain: str,
        description: str,
        target_dir: Path,
    ) -> Dict[str, Any]:
        """
        Scaffold a new agent from template files.

        READS template files, REPLACES placeholders, WRITES to target.
        NO hardcoded strings - everything from template.

        Args:
            agent_id: Lowercase agent identifier (e.g., 'lazara')
            agent_name: Display name (e.g., 'LAZARA')
            domain: Agent domain (e.g., 'SECURITY')
            description: Agent description
            target_dir: Where to create the agent

        Returns:
            Dict with success status and details
        """
        logger.info(f"🏗️ Scaffolding agent '{agent_id}' from template...")

        if not self.template_dir.exists():
            return {"success": False, "error": f"Template directory not found: {self.template_dir}"}

        if target_dir.exists():
            return {"success": False, "error": f"Target directory already exists: {target_dir}"}

        # Replacement map for placeholders
        replacements = {
            "YOUR_AGENT_ID": agent_id,
            "YOUR_AGENT_NAME": agent_name,
            "YOUR_DOMAIN": domain,
            "YOUR_AGENT_DESCRIPTION": description,
            "YOUR_NAME": "Engineer",
            "YOUR_AGENT_CLASS": "Agent",
            "YOUR_AGENT_ROLE": f"{domain} Agent",
            "YOUR_CAPABILITY_1": "process_task",
            "YOUR_CAPABILITY_2": "report_status",
            "YOUR_SHORT_DESCRIPTION": description[:50] if len(description) > 50 else description,
            "YOUR_TOOL_DESCRIPTION_HERE": f"Tool for {agent_id}",
            "YOUR_TOOL_NAME": "main_tool",
            "YourAgentCartridge": f"{agent_id.capitalize()}Cartridge",
        }

        files_created = []

        try:
            # Create target directory
            target_dir.mkdir(parents=True)
            (target_dir / "tools").mkdir()

            # Process each template file
            template_files = [
                ("steward.json", "steward.json"),
                ("cartridge.yaml", "cartridge.yaml"),
                ("cartridge_main.py", "cartridge_main.py"),
                ("tools/__init__.py", "tools/__init__.py"),
            ]

            for template_name, target_name in template_files:
                template_path = self.template_dir / template_name
                target_path = target_dir / target_name

                if template_path.exists():
                    content = template_path.read_text()

                    # Replace all placeholders
                    for placeholder, value in replacements.items():
                        content = content.replace(placeholder, value)

                    target_path.write_text(content)
                    files_created.append(str(target_path))
                    logger.debug(f"  ✓ Created {target_path}")
                else:
                    logger.warning(f"  ⚠️ Template not found: {template_path}")

            # Create __init__.py
            init_path = target_dir / "__init__.py"
            init_path.write_text(f'"""{agent_name} Agent Cartridge."""\n')
            files_created.append(str(init_path))

            logger.info(f"✅ Agent '{agent_id}' scaffolded at {target_dir}")
            logger.info(f"   Files created: {len(files_created)}")

            return {
                "success": True,
                "agent_id": agent_id,
                "domain": domain,
                "target_dir": str(target_dir),
                "files_created": files_created,
            }

        except Exception as e:
            logger.error(f"❌ Scaffold failed: {e}")
            # Cleanup on failure
            if target_dir.exists():
                import shutil

                shutil.rmtree(target_dir)
            return {"success": False, "error": str(e)}


__all__ = ["BuilderTool"]
