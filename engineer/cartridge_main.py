"""
THE ENGINEER - Meta-Agent & Builder.
Part of the Steward Protocol Federation.

Role: The Generalist / Builder
Mission: Self-Replication. Build new agents on demand.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any

# VibeOS Integration
from vibe_core import VibeAgent, Task

from engineer.tools.builder_tool import BuilderTool

# Constitutional Oath
try:
    from steward.oath_mixin import OathMixin
except ImportError:
    OathMixin = None

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ENGINEER_AGENT")


class EngineerCartridge(VibeAgent, OathMixin if OathMixin else object):
    """
    The Engineer Agent Cartridge.
    Capable of scaffolding and generating code for new agents.
    """

    def __init__(self):
        """Initialize the Engineer as a VibeAgent."""
        # Initialize VibeAgent base class
        super().__init__(
            agent_id="engineer",
            name="ENGINEER",
            version="1.0.0",
            author="Steward Protocol",
            description="Meta-agent and builder for new agents",
            domain="ENGINEERING",
            capabilities=["agent_scaffolding", "code_generation", "agent_creation"]
        )

        logger.info("📐 THE ENGINEER is online.")

        # Initialize Constitutional Oath mixin (if available)
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            # SWEAR THE OATH IMMEDIATELY in __init__
            self.oath_sworn = True
            logger.info("✅ ENGINEER has sworn the Constitutional Oath")

        self.builder = BuilderTool()

    def create_agent(self, name: str, mission: str) -> str:
        """
        Create a new agent from scratch.
        
        Args:
            name: Name of the new agent (snake_case)
            mission: Description of the agent's purpose
            
        Returns:
            str: Path to the new agent's main file
        """
        logger.info(f"📐 Engineer received job: Build agent '{name}'")
        logger.info(f"   Mission: {mission}")
        
        # 1. Scaffold
        if not self.builder.scaffold_agent(name):
            logger.error("❌ Scaffolding failed (directory might exist)")
            return f"Error: Could not scaffold {name}"
            
        # 2. Generate Code
        code = self.builder.generate_agent_code(name, mission)
        
        if not code:
            logger.error("❌ Code generation failed")
            return f"Error: Could not generate code for {name}"
            
        # 3. Write Code
        file_path = Path(name) / "cartridge_main.py"
        try:
            with open(file_path, "w") as f:
                f.write(code)
            logger.info(f"✅ Agent code written to: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"❌ File write failed: {e}")
            return f"Error: Could not write file {file_path}"

    # ==================== VIBEOS AGENT INTERFACE ====================

    def process(self, task: Task) -> Dict[str, Any]:
        """
        Process a task from the VibeKernel scheduler.

        ENGINEER responds to agent creation tasks:
        - "create_agent": Create a new agent
        """
        try:
            action = task.payload.get("action") or task.payload.get("command")
            logger.info(f"📐 ENGINEER processing task: {action}")

            if action == "create_agent":
                name = task.payload.get("name")
                mission = task.payload.get("mission")
                if not name or not mission:
                    return {"status": "error", "error": "name and mission required"}
                result = self.create_agent(name, mission)
                return {"status": "success", "result": result}
            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}"
                }
        except Exception as e:
            logger.error(f"❌ ENGINEER processing error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e)
            }

    def report_status(self) -> Dict[str, Any]:
        """Report ENGINEER status (VibeAgent interface)."""
        return {
            "agent_id": "engineer",
            "name": "ENGINEER",
            "status": "RUNNING",
            "domain": "ENGINEERING",
            "capabilities": self.capabilities,
            "description": "Meta-agent and builder for new agents"
        }
