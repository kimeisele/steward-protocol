"""
ENGINEER Builder Tool - Scaffolding and Code Generation (Tool Protocol).

Capabilities:
- Scaffold new agent directory structure
- Generate cartridge code via abstracted LLM service
- NO vendor lock-in: Uses services.llm_engine for all LLM interactions

Tool Protocol compliant for kernel-managed execution.
"""

import logging
from pathlib import Path
from typing import Any, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

# Import the abstracted LLM service (not vendor-specific)
from services.llm_engine import llm

logger = logging.getLogger("ENGINEER_BUILDER")


class BuilderTool(Tool):
    """
    The Engineer's toolbox for creating new agents (Tool Protocol).
    Delegates all LLM interactions to the abstracted LLMEngine service.
    This tool is agnostic to which LLM provider is being used.
    """

    def __init__(self):
        """Initialize builder tool with LLM service."""
        self.llm = llm  # Use singleton instance from services
        logger.info("🔨 Builder Tool initialized (using LLMEngine service)")

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
                "description": "Action: 'scaffold' | 'generate_code'",
            },
            "name": {
                "type": "string",
                "required": True,
                "description": "Agent name (e.g., 'weather')",
            },
            "mission": {
                "type": "string",
                "required": False,
                "description": "Agent mission/description (required for generate_code)",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        if action not in ["scaffold", "generate_code"]:
            raise ValueError(f"Invalid action: {action}. Must be 'scaffold' or 'generate_code'")

        if "name" not in parameters:
            raise ValueError("Missing required parameter: name")

        if action == "generate_code" and "mission" not in parameters:
            raise ValueError("generate_code requires 'mission' parameter")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute builder operation."""
        try:
            action = parameters["action"]
            name = parameters["name"]

            if action == "scaffold":
                success = self.scaffold_agent(name)
                if success:
                    return ToolResult(
                        success=True,
                        output={"scaffolded": True, "agent_name": name},
                        metadata={
                            "action": "scaffold",
                            "path": str(Path(name)),
                        },
                    )
                else:
                    return ToolResult(
                        success=False,
                        error=f"Scaffold failed for agent '{name}' (directory might already exist)",
                    )

            elif action == "generate_code":
                mission = parameters["mission"]
                code = self.generate_agent_code(name, mission)

                if code:
                    return ToolResult(
                        success=True,
                        output={"code": code, "agent_name": name},
                        metadata={
                            "action": "generate_code",
                            "code_length": len(code),
                        },
                    )
                else:
                    return ToolResult(
                        success=False,
                        error="Code generation failed",
                    )

        except Exception as e:
            error_msg = f"Builder tool execution failed: {type(e).__name__}: {e!s}"
            logger.error(f"BuilderTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)

    def scaffold_agent(self, name: str) -> bool:
        """
        Create directory structure for a new agent.

        Args:
            name: Agent name (e.g., 'weather')

        Returns:
            bool: True if successful
        """
        try:
            base_path = Path(name)
            tools_path = base_path / "tools"

            if base_path.exists():
                logger.warning(f"⚠️  Agent directory '{name}' already exists.")
                return False

            base_path.mkdir(parents=True)
            tools_path.mkdir(parents=True)

            # Create __init__.py files
            (base_path / "__init__.py").touch()
            (tools_path / "__init__.py").touch()

            logger.info(f"🏗️  Scaffolded agent structure for '{name}'")
            return True

        except Exception as e:
            logger.error(f"❌ Scaffold failed: {e}")
            return False

    def generate_agent_code(self, name: str, mission: str) -> Optional[str]:
        """
        Generate the cartridge code for a new agent.
        Uses the abstracted LLMEngine service (no vendor lock-in).

        Args:
            name: Agent name
            mission: Description of what the agent does

        Returns:
            str: Generated Python code or fallback template
        """
        prompt = (
            f"You are THE ENGINEER, a meta-agent that builds other autonomous agents.\n"
            f"TASK: Write the Python code for a new agent named '{name}'.\n"
            f"MISSION: {mission}\n\n"
            f"REQUIREMENTS:\n"
            f"1. Class name: {name.capitalize()}Cartridge\n"
            f"2. Must inherit from VibeAgent.\n"
            f"3. Must have a 'process(task: Task)' method.\n"
            f"4. Must use standard logging.\n"
            f"5. Return ONLY the Python code, no markdown formatting.\n"
            f"6. Include a comprehensive docstring explaining the agent's role.\n"
            f"7. Include type hints for all methods.\n"
        )

        system_prompt = (
            "You are an Expert Agent Developer. "
            "Generate production-ready Python code for autonomous agents. "
            "Output ONLY valid Python code, no explanations."
        )

        try:
            logger.info(f"🧠 Generating code for agent '{name}' via LLMEngine...")
            code = self.llm.generate_code(prompt, system_prompt)
            return code

        except Exception as e:
            logger.error(f"❌ Code generation failed: {e}")
            logger.info(f"⚠️  Falling back to template for '{name}'")
            return self._fallback_template(name, mission)

    def _fallback_template(self, name: str, mission: str) -> str:
        """
        Return a basic template if LLM fails.
        This is a graceful fallback that matches the project's VibeAgent interface.
        """
        class_name = f"{name.capitalize()}Cartridge"
        return f"""\"\"\"
Agent: {name}
Mission: {mission}
Generated by: The Engineer (Fallback Mode)
\"\"\"

import logging
from typing import Dict, Any

from vibe_core.protocols import VibeAgent, AgentManifest
from vibe_core.scheduling.task import Task

logger = logging.getLogger("{name.upper()}_AGENT")


class {class_name}(VibeAgent):
    \"\"\"
    {name.capitalize()} Agent Cartridge.
    Mission: {mission}
    \"\"\"

    def __init__(self):
        super().__init__(
            agent_id="{name.lower()}",
            name="{name.upper()}",
            version="1.0.0",
            author="The Engineer",
            description="{mission}",
            domain="GENERAL",
            capabilities=["execute"]
        )
        logger.info(f"📍 {{self.name}} cartridge initialized.")

    def get_manifest(self) -> AgentManifest:
        \"\"\"Return agent manifest.\"\"\"
        return AgentManifest(
            agent_id=self.agent_id,
            name=self.name,
            version=self.version,
            author=self.author,
            description=self.description,
            domain=self.domain,
            capabilities=self.capabilities,
            dependencies=[]
        )

    def process(self, task: Task) -> Dict[str, Any]:
        \"\"\"
        Process an incoming task.

        Args:
            task: The task to process

        Returns:
            Task result dictionary
        \"\"\"
        logger.info(f"⚙️  {{self.name}} processing task: {{task.id}}")

        # TODO: Implement actual task processing logic
        return {{
            "status": "success",
            "message": f"{{self.name}} processed task {{task.id}}",
            "agent": self.agent_id
        }}

    def report_status(self) -> Dict[str, Any]:
        \"\"\"Report agent status.\"\"\"
        return {{
            "agent_id": self.agent_id,
            "name": self.name,
            "status": "RUNNING",
            "domain": self.domain,
            "capabilities": self.capabilities
        }}
"""


__all__ = ["BuilderTool"]
