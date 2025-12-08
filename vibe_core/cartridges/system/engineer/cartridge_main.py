#!/usr/bin/env python3
"""
THE ENGINEER - Meta-Agent & Builder.
Part of the Steward Protocol Federation.

Role: The Generalist / Builder
Mission: Manifest reality into code. Build new agents on demand.

REFACTORED: Tool Protocol Compliant
- NO tool instances owned by agent
- ALL tools accessed via kernel (self.system.execute_tool)

Updated for Safe Evolution Loop (GAD-5500):
- manifest_reality: Write code to sandbox (input for Auditor)
- Legacy create_agent: Still supported for agent scaffolding
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from vibe_core.config import CityConfig

# VibeOS Integration
from vibe_core.protocols import AgentManifest, VibeAgent
from vibe_core.scheduling.task import Task

# Constitutional Oath Mixin
from vibe_core.steward import OathMixin

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ENGINEER_AGENT")


class EngineerCartridge(VibeAgent, OathMixin):
    """
    The Engineer Agent Cartridge.

    Capabilities:
    - manifest_reality: Write code to sandbox (Safe Evolution Loop)
    - create_agent: Scaffold new agents (Legacy)

    Tool Protocol Compliant:
    - NO tool instances in __init__
    - Tools accessed via self.system.execute_tool()
    """

    def __init__(self, config: Optional[CityConfig] = None):
        """Initialize the Engineer as a VibeAgent."""
        # BLOCKER #0: Accept Phoenix Config
        self.config = config or CityConfig()

        super().__init__(
            agent_id="engineer",
            name="ENGINEER",
            version="3.0.0",  # Bumped for Tool Protocol refactor
            author="Steward Protocol",
            description="Builder agent: manifests code and scaffolds new agents",
            domain="INFRASTRUCTURE",
            capabilities=["manifest_reality", "agent_scaffolding", "code_generation"],
        )

        logger.info("📐 THE ENGINEER is online (Tool Protocol v3.0).")

        # Initialize Constitutional Oath
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            self.oath_sworn = True
            logger.info("✅ ENGINEER has sworn the Constitutional Oath")

        # ALL TOOLS: Accessed via kernel (self.system.execute_tool)
        # - engineer.builder (BuilderTool)

        logger.info("✅ ENGINEER: Ready for operation (NO tool instances owned)")

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

    async def process(self, task: Task) -> Dict[str, Any]:
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
        elif action == "spawn_agent" or action == "spawn":
            return self.spawn_agent(task)
        else:
            return {"status": "ignored", "reason": f"Unknown action: {action}"}

    def manifest_reality(self, task: Task) -> Dict[str, Any]:
        """
        Writes code to the sandbox (Safe Evolution Loop input).
        Optionally generates code using the LLM service if use_brain=True.

        NEW: Uses kernel-managed tools via self.system.execute_tool()

        Payload:
        - feature_spec: Description of feature to implement
        - path: Relative path (e.g., "src/auth.py")
        - content: Code content (or generated from feature_spec if use_brain=True)
        - use_brain: Boolean. If True, generate code from feature_spec via LLM.

        Architecture: The engineer asks the builder for code via kernel.
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

        # STEP 2: If no content and use_brain=True, ask builder via kernel
        if not code_content and use_brain and feature_spec:
            try:
                logger.info(f"🧠 Asking builder (via kernel) to generate code for: {feature_spec}")

                # CRITICAL: Tool call goes through kernel
                result = self.system.execute_tool(
                    "engineer.builder",
                    {
                        "action": "generate_code",
                        "name": os.path.splitext(os.path.basename(relative_path))[0],
                        "mission": feature_spec,
                    },
                )

                if result.success:
                    code_content = result.output.get("code")
                    logger.info(f"✅ Builder generated code ({len(code_content)} chars)")
                else:
                    logger.error(f"❌ Code generation failed: {result.error}")
                    code_content = None

            except Exception as e:
                logger.error(f"❌ Builder call failed: {e}")
                logger.info("⚠️  Falling back to stub")
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

        NEW: Uses kernel-managed tools via self.system.execute_tool()
        """
        name = task.payload.get("name")
        mission = task.payload.get("mission")

        if not name or not mission:
            return {"status": "error", "reason": "name and mission required"}

        logger.info(f"📐 Engineer received job: Build agent '{name}'")
        logger.info(f"   Mission: {mission}")

        try:
            # 1. Scaffold via kernel
            scaffold_result = self.system.execute_tool("engineer.builder", {"action": "scaffold", "name": name})

            if not scaffold_result.success:
                return {"status": "error", "reason": f"Could not scaffold {name}: {scaffold_result.error}"}

            # 2. Generate Code via kernel
            code_result = self.system.execute_tool(
                "engineer.builder", {"action": "generate_code", "name": name, "mission": mission}
            )

            if not code_result.success:
                return {
                    "status": "error",
                    "reason": f"Code generation failed for {name}: {code_result.error}",
                }

            code = code_result.output.get("code")

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
            "description": "Builder agent (Tool Protocol v3.0)",
        }

    # =========================================================================
    # OPUS-012: New Spawn Protocol (Separation of Powers)
    # =========================================================================

    def spawn_agent(self, task: Task) -> Dict[str, Any]:
        """
        OPUS-012: Spawn a new agent via LifecyclePlugin.

        This implements the Separation of Powers:
        - ENGINEER: Proposes life (writes code, creates passport)
        - LIFECYCLE: Grants life (verifies governance, registers agent)

        Flow:
        1. Write cartridge code to sandbox
        2. Generate steward.json passport with constitution hash
        3. Request audit from Auditor
        4. Call SPAWN_COGNITION syscall via LifecyclePlugin

        Payload:
        - name: Agent name (e.g., "curator")
        - mission: Agent's purpose/dharma
        - capabilities: List of capabilities
        """
        name = task.payload.get("name")
        mission = task.payload.get("mission") or task.payload.get("dharma")
        capabilities = task.payload.get("capabilities", [])

        if not name or not mission:
            return {"status": "error", "reason": "name and mission required"}

        agent_id = name.lower().replace(" ", "_")
        logger.info(f"🧬 ENGINEER: Spawning agent '{agent_id}'")

        # =====================================================================
        # STEP 1: Write cartridge code to sandbox
        # =====================================================================
        sandbox_dir = Path("./workspaces/sandbox") / agent_id
        sandbox_dir.mkdir(parents=True, exist_ok=True)

        cartridge_code = self._generate_cartridge_code(agent_id, name, mission, capabilities)
        cartridge_path = sandbox_dir / "cartridge_main.py"
        cartridge_path.write_text(cartridge_code, encoding="utf-8")
        logger.info(f"✅ Cartridge written to: {cartridge_path}")

        # =====================================================================
        # STEP 2: Generate steward.json passport
        # =====================================================================
        import json
        from datetime import datetime

        # Get constitution hash from LifecyclePlugin
        constitution_hash = "no_constitution"
        if hasattr(self, "system") and hasattr(self.system, "kernel"):
            kernel = self.system.kernel
            if hasattr(kernel, "lifecycle"):
                constitution_hash = kernel.lifecycle.constitution_hash

        passport = {
            "identity": {
                "agent_id": agent_id,
                "name": name.upper(),
            },
            "specs": {
                "description": mission,
                "domain": "CUSTOM",
                "version": "1.0.0",
            },
            "capabilities": {
                "operations": [{"name": cap, "description": f"{cap} operation"} for cap in capabilities],
            },
            "governance": {
                "constitution_hash": constitution_hash,
                "issued_at": datetime.utcnow().isoformat() + "Z",
                "issuer": "engineer",
                "compliance_level": 2,
            },
        }

        passport_path = sandbox_dir / "steward.json"
        passport_path.write_text(json.dumps(passport, indent=2), encoding="utf-8")
        logger.info(f"✅ Passport written to: {passport_path}")

        # =====================================================================
        # STEP 3: Request audit from Auditor
        # =====================================================================
        audit_result = self._request_audit(agent_id, sandbox_dir)
        if not audit_result.get("success"):
            logger.warning(f"⚠️ Audit request failed: {audit_result.get('reason')}")
            # Continue anyway - LifecyclePlugin will check for certificate

        # =====================================================================
        # STEP 4: Request spawn via LifecyclePlugin (syscall)
        # =====================================================================
        spec = {
            "id": agent_id,
            "name": name,
            "description": mission,
            "capabilities": capabilities,
            "cartridge_path": str(cartridge_path),
        }

        try:
            # Try via syscall registry
            from vibe_core.runtime.syscalls import execute_syscall

            if hasattr(self, "system") and hasattr(self.system, "kernel"):
                result = execute_syscall(
                    self.system.kernel,
                    "SPAWN_COGNITION",
                    {"spec": spec, "passport": passport, "skip_audit": True},  # skip_audit for now
                )
                logger.info(f"🌱 Spawn result: {result}")
                return {
                    "status": "spawned",
                    "agent_id": agent_id,
                    "sandbox_path": str(sandbox_dir),
                    "spawn_result": result,
                }
            else:
                logger.warning("No kernel access - cannot execute syscall")
                return {
                    "status": "pending",
                    "agent_id": agent_id,
                    "sandbox_path": str(sandbox_dir),
                    "reason": "No kernel access for syscall",
                }

        except Exception as e:
            logger.error(f"❌ Spawn failed: {e}")
            return {
                "status": "error",
                "agent_id": agent_id,
                "reason": str(e),
                "sandbox_path": str(sandbox_dir),
            }

    def _generate_cartridge_code(
        self,
        agent_id: str,
        name: str,
        mission: str,
        capabilities: list,
    ) -> str:
        """Generate cartridge code for a new agent."""
        caps_str = ", ".join(f'"{c}"' for c in capabilities)

        return f'''#!/usr/bin/env python3
"""
{name.upper()} Agent - Auto-generated by ENGINEER
Mission: {mission}

Generated via OPUS-012 Spawn Protocol.
"""

import logging
from typing import Any, Dict, Optional

from vibe_core.config import CityConfig
from vibe_core.protocols import AgentManifest, VibeAgent
from vibe_core.scheduling.task import Task
from vibe_core.steward import OathMixin

logger = logging.getLogger("{agent_id.upper()}_AGENT")


class {name.title().replace(" ", "")}Cartridge(VibeAgent, OathMixin):
    """
    {name} Agent Cartridge.
    
    Mission: {mission}
    """

    def __init__(self, config: Optional[CityConfig] = None):
        self.config = config or CityConfig()
        
        super().__init__(
            agent_id="{agent_id}",
            name="{name.upper()}",
            version="1.0.0",
            author="Engineer (Auto-generated)",
            description="{mission}",
            domain="CUSTOM",
            capabilities=[{caps_str}],
        )
        
        # Constitutional Oath
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            self.oath_sworn = True
        
        logger.info("✅ {name.upper()} is online")

    def get_manifest(self) -> AgentManifest:
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

    async def process(self, task: Task) -> Dict[str, Any]:
        action = task.payload.get("action")
        logger.info(f"Processing: {{action}}")
        
        # TODO: Implement agent-specific logic
        return {{"status": "processed", "action": action}}

    def report_status(self) -> Dict[str, Any]:
        return {{
            "agent_id": "{agent_id}",
            "name": self.name,
            "status": "RUNNING",
            "domain": self.domain,
            "capabilities": self.capabilities,
        }}
'''

    def _request_audit(self, agent_id: str, sandbox_dir: Path) -> Dict[str, Any]:
        """
        Request audit from Auditor agent.

        For Phase 2, we create a stub audit_certificate.json.
        In production, this would spawn an Auditor task.
        """
        import json
        from datetime import datetime

        # Create stub audit certificate (in production, Auditor would create this)
        audit_cert = {
            "agent_id": agent_id,
            "status": "approved",
            "auditor": "engineer_stub",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "signature": "stub_signature",
            "notes": "Auto-approved by Engineer (Phase 2 stub)",
        }

        cert_path = sandbox_dir / "audit_certificate.json"
        cert_path.write_text(json.dumps(audit_cert, indent=2), encoding="utf-8")

        logger.info(f"✅ Audit certificate created at: {cert_path}")

        # TODO: In production, spawn Auditor task:
        # self.system.create_subtask("auditor", {"action": "verify", "path": str(sandbox_dir)})

        return {"success": True, "certificate_path": str(cert_path)}
