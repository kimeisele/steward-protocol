#!/usr/bin/env python3
"""
THE ENGINEER - Meta-Agent & Builder.
Part of the Steward Protocol Federation.

Role: The Generalist / Builder
Mission: Manifest reality into code. Build new agents on demand.

Updated for Safe Evolution Loop (GAD-5500):
- manifest_reality: Write code to sandbox (input for Auditor)
- Legacy create_agent: Still supported for agent scaffolding
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# VibeOS Integration
from vibe_core.protocols import VibeAgent, AgentManifest
from vibe_core.config import CityConfig
from vibe_core.scheduling.task import Task


# Constitutional Oath Mixin
from steward.oath_mixin import OathMixin
from steward.system_agents.engineer.tools.builder_tool import BuilderTool

# Constitutional Oath
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ENGINEER_AGENT")


class EngineerCartridge(VibeAgent, OathMixin):
    """
    The Engineer Agent Cartridge.

    Capabilities:
    - manifest_reality: Write code to sandbox (Safe Evolution Loop)
    - create_agent: Scaffold new agents (Legacy)
    """

    def __init__(self, config: Optional[CityConfig] = None):
        """Initialize the Engineer as a VibeAgent."""
        # BLOCKER #0: Accept Phoenix Config
        self.config = config or CityConfig()

        super().__init__(
            agent_id="engineer",
            name="ENGINEER",
            version="2.0.0",
            author="Steward Protocol",
            description="Builder agent: manifests code and scaffolds new agents",
            domain="ENGINEERING",
            capabilities=["manifest_reality", "agent_scaffolding", "code_generation"],
        )

        logger.info("📐 THE ENGINEER is online.")

        # Initialize Constitutional Oath
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            self.oath_sworn = True
            logger.info("✅ ENGINEER has sworn the Constitutional Oath")

        self.builder = BuilderTool()

    def get_manifest(self) -> AgentManifest:
        """Return agent manifest (VibeAgent interface)."""
        return AgentManifest(
            agent_id=self.agent_id,
            name=self.name,
            version=self.version,
            author=self.author,
            description=self.description,
            domain=self.domain,
            capabilities=self.capabilities,
            dependencies=[],
        )

    def process(self, task: Task) -> Dict[str, Any]:
        """
        Sync dispatch based on payload 'action' or 'method'.

        Supported actions:
        - manifest_reality: Write code to sandbox
        - create_agent: Scaffold new agent
        """
        action = task.payload.get("action") or task.payload.get("method")
        logger.info(f"📐 ENGINEER processing: {action}")

        if action == "manifest_reality" or action == "write_code":
            return self.manifest_reality(task)
        elif action == "create_agent":
            return self.create_agent_legacy(task)
        else:
            return {"status": "ignored", "reason": f"Unknown action: {action}"}

    def manifest_reality(self, task: Task) -> Dict[str, Any]:
        """
        Writes code to the sandbox (Safe Evolution Loop input).
        Optionally generates code using the LLM service if use_brain=True.

        Payload:
        - feature_spec: Description of feature to implement
        - path: Relative path (e.g., "src/auth.py")
        - content: Code content (or generated from feature_spec if use_brain=True)
        - use_brain: Boolean. If True, generate code from feature_spec via LLM.

        Architecture: The engineer asks the builder for code via abstracted service.
        The builder has NO idea which LLM provider is being used.
        """
        feature_spec = task.payload.get("feature_spec", "Unknown feature")
        relative_path = task.payload.get("path")
        use_brain = task.payload.get("use_brain", False)

        if not relative_path:
            return {"status": "error", "reason": "No path provided"}

        # Force Sandbox (Safety First)
        sandbox_dir = os.path.abspath("./workspaces/sandbox")
        os.makedirs(sandbox_dir, exist_ok=True)

        full_path = os.path.join(sandbox_dir, os.path.basename(relative_path))

        # STEP 1: Get code content
        code_content = task.payload.get("content")

        # STEP 2: If no content and use_brain=True, ask the builder to generate it
        if not code_content and use_brain and feature_spec:
            try:
                logger.info(f"🧠 Asking builder to generate code for: {feature_spec}")
                code_content = self.builder.generate_agent_code(
                    name=os.path.splitext(os.path.basename(relative_path))[0],
                    mission=feature_spec,
                )
                logger.info(f"✅ Builder generated code ({len(code_content)} chars)")
            except Exception as e:
                logger.error(f"❌ Code generation failed: {e}")
                logger.info(f"⚠️  Falling back to stub")
                code_content = None

        # STEP 3: Fallback to stub if still no content
        if not code_content:
            code_content = f"""# Implementation of {feature_spec}
# Generated by Engineer via Safe Evolution Loop
# This is a placeholder stub.

def run():
    \"\"\"Placeholder implementation.\"\"\"
    pass
"""

        # STEP 4: Write to sandbox
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(code_content)

            logger.info(f"✅ Code manifested to: {full_path}")

            return {
                "status": "manifested",
                "path": full_path,  # Absolute path for Auditor
                "sandbox": True,
                "feature": feature_spec,
                "generator": "Brain" if use_brain else "Payload",
            }
        except Exception as e:
            logger.error(f"❌ manifest_reality failed: {e}")
            return {"status": "error", "reason": str(e)}

    def create_agent_legacy(self, task: Task) -> Dict[str, Any]:
        """
        Legacy method: Create a new agent from scratch.
        Still supported for backward compatibility.
        """
        name = task.payload.get("name")
        mission = task.payload.get("mission")

        if not name or not mission:
            return {"status": "error", "reason": "name and mission required"}

        logger.info(f"📐 Engineer received job: Build agent '{name}'")
        logger.info(f"   Mission: {mission}")

        try:
            # 1. Scaffold
            if not self.builder.scaffold_agent(name):
                return {"status": "error", "reason": f"Could not scaffold {name}"}

            # 2. Generate Code
            code = self.builder.generate_agent_code(name, mission)
            if not code:
                return {
                    "status": "error",
                    "reason": f"Code generation failed for {name}",
                }

            # 3. Write Code
            file_path = Path(name) / "cartridge_main.py"
            with open(file_path, "w") as f:
                f.write(code)

            logger.info(f"✅ Agent code written to: {file_path}")
            return {"status": "success", "path": str(file_path)}

        except Exception as e:
            logger.error(f"❌ create_agent_legacy failed: {e}")
            return {"status": "error", "reason": str(e)}

    def report_status(self) -> Dict[str, Any]:
        """Report ENGINEER status (VibeAgent interface)."""
        return {
            "agent_id": "engineer",
            "name": self.name,
            "status": "RUNNING",
            "domain": self.domain,
            "capabilities": self.capabilities,
            "description": self.description,
        }
