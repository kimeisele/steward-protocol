"""
ENGINEER Builder Tool - Agent Factory (Tool Protocol).

OPUS-160: Now delegates to vibe_core.genesis.GenesisService.

The Engineer is the first official customer of the Stadtamt.
All agent scaffolding goes through the central Genesis service.

Tool Protocol compliant for kernel-managed execution.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger("ENGINEER_BUILDER")


class BuilderTool(Tool):
    """
    The Engineer's Agent Factory (Tool Protocol).

    OPUS-160: Delegates to vibe_core.genesis.GenesisService.
    The Stadtamt handles all infrastructure generation.

    Capabilities:
    - scaffold: Create agent from GenesisService templates
    - (Future: generate via LLM service)
    """

    def __init__(self):
        """Initialize builder tool."""
        self._genesis_service: Optional[Any] = None
        logger.info("🔨 Builder Tool initialized (OPUS-160: Stadtamt integration)")

    def _get_genesis_service(self):
        """Lazy-load GenesisService."""
        if self._genesis_service is None:
            try:
                from vibe_core.genesis import GenesisService

                self._genesis_service = GenesisService.get_instance()
                logger.debug("🏛️ Connected to Stadtamt (GenesisService)")
            except ImportError:
                logger.warning("⚠️ GenesisService not available, using legacy mode")
        return self._genesis_service

    @property
    def name(self) -> str:
        return "engineer.builder"  # Namespaced: agent_id.tool_name

    @property
    def description(self) -> str:
        return "Agent scaffolding via Stadtamt (GenesisService) - GAD-000 compliant"

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
                "description": "Target directory (default: vibe_core/cartridges/agent_city/{name})",
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
        """Execute builder operation - scaffold via Stadtamt."""
        try:
            name = parameters["name"].lower()
            domain = parameters["domain"].upper()
            description = parameters.get("description", f"{name.capitalize()} agent for {domain} domain")
            target_dir = parameters.get("target_dir", f"vibe_core/cartridges/agent_city/{name}")

            result = self.scaffold_agent(
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
                        "genesis": "OPUS-160",
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

    def scaffold_agent(
        self,
        agent_id: str,
        agent_name: str,
        domain: str,
        description: str,
        target_dir: Path,
    ) -> Dict[str, Any]:
        """
        Scaffold a new agent via GenesisService (Stadtamt).

        OPUS-160: Delegates to vibe_core.genesis for GAD-000 compliance.

        Args:
            agent_id: Lowercase agent identifier (e.g., 'lazara')
            agent_name: Display name (e.g., 'LAZARA')
            domain: Agent domain (e.g., 'SECURITY')
            description: Agent description
            target_dir: Where to create the agent

        Returns:
            Dict with success status and details
        """
        logger.info(f"🏗️ Scaffolding agent '{agent_id}' via Stadtamt...")

        # Check if target already exists
        if target_dir.exists():
            return {"success": False, "error": f"Target directory already exists: {target_dir}"}

        # Get GenesisService
        genesis = self._get_genesis_service()

        if genesis is not None:
            # Use the Stadtamt (OPUS-160)
            return self._scaffold_via_stadtamt(genesis, agent_id, agent_name, domain, description, target_dir)
        else:
            # Fallback to legacy mode
            return self._scaffold_legacy(agent_id, agent_name, domain, description, target_dir)

    def _scaffold_via_stadtamt(
        self,
        genesis,
        agent_id: str,
        agent_name: str,
        domain: str,
        description: str,
        target_dir: Path,
    ) -> Dict[str, Any]:
        """Scaffold via GenesisService (the proper way)."""
        try:
            from vibe_core.genesis import ModuleType

            # Call the Stadtamt
            result = genesis.scaffold_new(
                path=target_dir,
                module_type=ModuleType.CARTRIDGE,
                context={
                    "id": agent_id,
                    "id_upper": agent_id.upper(),
                    "name": agent_name,
                    "class_name": agent_id.capitalize(),
                    "domain": domain,
                    "description": description,
                },
            )

            if result.success:
                logger.info(f"✅ Agent '{agent_id}' scaffolded via Stadtamt at {target_dir}")
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "domain": domain,
                    "target_dir": str(target_dir),
                    "files_created": result.files_created,
                    "compliance_score": result.compliance_after.score if result.compliance_after else None,
                    "genesis": "OPUS-160 (Stadtamt)",
                }
            else:
                errors = result.build_result.errors if result.build_result else ["Unknown error"]
                return {"success": False, "error": "; ".join(errors)}

        except Exception as e:
            logger.error(f"❌ Stadtamt scaffold failed: {e}")
            return {"success": False, "error": str(e)}

    def _scaffold_legacy(
        self,
        agent_id: str,
        agent_name: str,
        domain: str,
        description: str,
        target_dir: Path,
    ) -> Dict[str, Any]:
        """Legacy scaffold (fallback when GenesisService unavailable)."""
        logger.warning("⚠️ Using legacy scaffold mode (GenesisService unavailable)")

        try:
            # Create basic structure
            target_dir.mkdir(parents=True)
            (target_dir / "tools").mkdir()

            files_created = []

            # Create __init__.py
            init_content = f'"""{agent_name} Agent Cartridge."""\n\nfrom .cartridge_main import {agent_id.capitalize()}Cartridge\n\n__all__ = ["{agent_id.capitalize()}Cartridge"]\n'
            (target_dir / "__init__.py").write_text(init_content)
            files_created.append("__init__.py")

            # Create cartridge_main.py (minimal)
            main_content = f'''"""
{agent_name} Cartridge (Legacy Mode)

Generated by Engineer BuilderTool (legacy fallback).
"""

import logging
from typing import Any, Dict

logger = logging.getLogger("AGENT.{agent_id.upper()}")


class {agent_id.capitalize()}Cartridge:
    """
    {agent_name} Agent.

    Domain: {domain}
    Description: {description}
    """

    def __init__(self, config=None):
        self.config = config or {{}}
        self.agent_id = "{agent_id}"
        logger.info(f"{{self.__class__.__name__}} initialized")

    async def process(self, task) -> Dict[str, Any]:
        return {{"status": "not_implemented"}}

    def report_status(self) -> Dict[str, Any]:
        return {{"agent_id": self.agent_id, "status": "operational"}}
'''
            (target_dir / "cartridge_main.py").write_text(main_content)
            files_created.append("cartridge_main.py")

            # Create tools/__init__.py
            (target_dir / "tools" / "__init__.py").write_text('"""Tools for agent."""\n')
            files_created.append("tools/__init__.py")

            logger.info(f"✅ Agent '{agent_id}' scaffolded (legacy) at {target_dir}")
            return {
                "success": True,
                "agent_id": agent_id,
                "domain": domain,
                "target_dir": str(target_dir),
                "files_created": files_created,
                "genesis": "legacy",
            }

        except Exception as e:
            logger.error(f"❌ Legacy scaffold failed: {e}")
            if target_dir.exists():
                import shutil

                shutil.rmtree(target_dir)
            return {"success": False, "error": str(e)}


__all__ = ["BuilderTool"]
