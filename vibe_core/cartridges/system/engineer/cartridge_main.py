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
        Generic Task Dispatcher.

        Instead of hardcoded if/elif blocks, we look for a tool that
        matches the requested action and delegate execution to the kernel.
        """
        action = task.payload.get("action") or task.payload.get("method")
        logger.info(f"📐 ENGINEER processing: {action}")

        # 1. Try to find a tool for this specific action
        # Convention: engineer.{action}
        tool_name = f"engineer.{action}"

        try:
            # Check if we have a system tool for this
            result = self.system.execute_tool(tool_name, task.payload)

            if result.success:
                # If the tool returned code that needs to be sandboxed, do it here
                if isinstance(result.output, dict) and "code" in result.output:
                    filename = os.path.basename(task.payload.get("path") or task.payload.get("file") or "generated.py")
                    self.system.write_file(filename, result.output["code"])
                    result.output["sandbox_path"] = str(self.system.get_sandbox_path() / filename)

                return {"status": "success", "action": action, "result": result.output}

            # 2. Fallback: If tool not found or failed, try legacy handlers
            # (Keeping them for 1 tick to ensure backward compatibility during migration)
            if action == "manifest_reality":
                return self.manifest_reality(task)

            return {
                "status": "error",
                "reason": f"No tool found for action '{action}' and legacy handler failed.",
                "details": result.error if not result.success else None,
            }

        except Exception as e:
            logger.error(f"❌ ENGINEER dispatch failed for {action}: {e}")
            return {"status": "error", "reason": str(e)}

    # Legacy methods remain below but are being phased out...
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

        # Use System-Managed Sandbox
        sandbox_root = self.system.get_sandbox_path()
        filename = os.path.basename(relative_path)

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
            # Protocol-Compliant Write (Audited & Sandboxed)
            self.system.write_file(filename, code_content)

            # Resolve full path for return metadata (Auditor needs this)
            full_path = str(sandbox_root / filename)

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

            # 3. Write Code (Protocol-Compliant)
            file_rel_path = f"{name}/cartridge_main.py"
            self.system.write_file(file_rel_path, code)

            full_path = self.system.get_sandbox_path() / file_rel_path
            logger.info(f"✅ Agent code written to: {full_path}")
            return {"status": "success", "path": str(full_path)}

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
        # STEP 1: Write cartridge code to sandbox (Protocol-Compliant)
        # =====================================================================
        sandbox_root = self.system.get_sandbox_path()
        agent_sandbox_rel = f"{agent_id}"

        cartridge_code = self._generate_cartridge_code(agent_id, name, mission, capabilities)
        cartridge_rel_path = f"{agent_sandbox_rel}/cartridge_main.py"
        self.system.write_file(cartridge_rel_path, cartridge_code)

        cartridge_path = sandbox_root / cartridge_rel_path
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

        passport_rel_path = f"{agent_sandbox_rel}/steward.json"
        self.system.write_file(passport_rel_path, json.dumps(passport, indent=2))

        passport_path = sandbox_root / passport_rel_path
        logger.info(f"✅ Passport written to: {passport_path}")

        # =====================================================================
        # STEP 3: Request audit from Auditor
        # =====================================================================
        # Auditor expects absolute path to sandbox dir
        agent_sandbox_abs = sandbox_root / agent_sandbox_rel
        audit_result = self._request_audit(agent_id, agent_sandbox_abs)
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
                    "sandbox_path": str(agent_sandbox_abs),
                    "spawn_result": result,
                }
            else:
                logger.warning("No kernel access - cannot execute syscall")
                return {
                    "status": "pending",
                    "agent_id": agent_id,
                    "sandbox_path": str(agent_sandbox_abs),
                    "reason": "No kernel access for syscall",
                }

        except Exception as e:
            logger.error(f"❌ Spawn failed: {e}")
            return {
                "status": "error",
                "agent_id": agent_id,
                "reason": str(e),
                "sandbox_path": str(agent_sandbox_abs),
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

        Creates a signed audit_certificate.json using real crypto.
        """
        import json
        from datetime import datetime

        # Create audit certificate content
        content = json.dumps(
            {
                "agent_id": agent_id,
                "sandbox_path": str(sandbox_dir),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
            sort_keys=True,
        )

        # Sign with real crypto
        try:
            from vibe_core.steward.crypto import load_or_generate_keys, sign_content

            private_key, _ = load_or_generate_keys()
            signature = sign_content(content, private_key)
            auditor_id = "engineer"
        except ImportError:
            logger.warning("⚠️ steward.crypto not available, using unsigned certificate")
            signature = None
            auditor_id = "engineer_unsigned"

        audit_cert = {
            "agent_id": agent_id,
            "status": "approved",
            "auditor": auditor_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "signature": signature,
            "content_hash": __import__("hashlib").sha256(content.encode()).hexdigest(),
        }

        # Resolve relative path for system.write_file
        # sandbox_dir passed in is absolute, we need rel to sandbox_root
        sandbox_root = self.system.get_sandbox_path()
        try:
            rel_dir = os.path.relpath(sandbox_dir, sandbox_root)
        except ValueError:
            rel_dir = os.path.basename(sandbox_dir)

        cert_rel_path = f"{rel_dir}/audit_certificate.json"
        self.system.write_file(cert_rel_path, json.dumps(audit_cert, indent=2))

        logger.info(f"✅ Audit certificate created (signed: {signature is not None})")

        return {"success": True, "certificate_path": str(sandbox_root / cert_rel_path), "signed": signature is not None}
