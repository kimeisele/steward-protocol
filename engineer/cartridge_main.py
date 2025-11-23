"""
THE ENGINEER - Meta-Agent & Builder.
Part of the Steward Protocol Federation.

Role: The Generalist / Builder
Mission: Self-Replication. Build new agents on demand.
"""

import logging
from pathlib import Path
from engineer.tools.builder_tool import BuilderTool

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ENGINEER_AGENT")


class EngineerCartridge:
    """
    The Engineer Agent Cartridge.
    Capable of scaffolding and generating code for new agents.
    """

    def __init__(self):
        """Initialize the Engineer."""
        self.builder = BuilderTool()
        logger.info("📐 THE ENGINEER is online.")

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
