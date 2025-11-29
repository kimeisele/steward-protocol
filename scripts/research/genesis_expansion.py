#!/usr/bin/env python3
"""
🚀 GENESIS EXPANSION: PROJECT ECHO
═══════════════════════════════════════════════════════════════

This orchestrates the creation of a new Echo Cartridge using the Safe Evolution Loop.

FLOW:
1. STEP 1 (The Soul)    → Engineer generates cartridge.yaml
2. STEP 2 (The Body)    → Engineer generates cartridge_main.py
3. STEP 3 (The Gate)    → Auditor verifies Python syntax & linting
4. STEP 4 (The Birth)   → Archivist commits to /echo/ and seals with git
5. STEP 5 (The Proof)   → Validate the new cartridge exists and is valid

This demonstrates Option A+C: Engineer builds valid cartridge structure.
"""

import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from steward.system_agents.archivist.cartridge_main import ArchivistCartridge
from steward.system_agents.auditor.cartridge_main import AuditorCartridge
from steward.system_agents.engineer.cartridge_main import EngineerCartridge

# Steward Protocol imports
from vibe_core.scheduling.task import Task

# ═════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═════════════════════════════════════════════════════════════════════════

REPO_ROOT = os.path.abspath(".")
SANDBOX_ROOT = os.path.join(REPO_ROOT, "workspaces", "sandbox", "echo")
ECHO_TARGET = os.path.join(REPO_ROOT, "agent_city", "registry", "citizens", "echo")
WORKSPACES_ROOT = os.path.join(REPO_ROOT, "workspaces", "sandbox")

# ═════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════


def print_header(title: str):
    """Print a section header."""
    print(f"\n{'═' * 70}")
    print(f"{title}")
    print(f"{'═' * 70}\n")


def print_step(step: int, msg: str):
    """Print a step marker."""
    print(f"\n🔹 STEP {step}: {msg}")
    print(f"{'─' * 70}")


def print_success(msg: str):
    """Print success message."""
    print(f"   ✅ {msg}")


def print_error(msg: str):
    """Print error message."""
    print(f"   ❌ {msg}")


def print_info(msg: str):
    """Print info message."""
    print(f"   ℹ️  {msg}")


def cleanup_sandbox():
    """Remove old sandbox artifacts."""
    if os.path.exists(SANDBOX_ROOT):
        print_info(f"Cleaning sandbox: {SANDBOX_ROOT}")
        shutil.rmtree(SANDBOX_ROOT)
    os.makedirs(SANDBOX_ROOT, exist_ok=True)
    print_success("Sandbox prepared")


def ensure_repo_root():
    """Verify we're in the correct repo root."""
    if not os.path.exists(os.path.join(REPO_ROOT, ".git")):
        print_error("Not in a git repository root")
        return False
    if not os.path.exists(os.path.join(REPO_ROOT, "vibe_core")):
        print_error("Not in steward-protocol repository root")
        return False
    return True


# ═════════════════════════════════════════════════════════════════════════
# ECHO CARTRIDGE TEMPLATES
# ═════════════════════════════════════════════════════════════════════════

ECHO_YAML_TEMPLATE = """# 🔔 ECHO CARTRIDGE MANIFEST 🔔
# Test Agent - Minimal but valid VibeAgent implementation

cartridge:
  id: echo
  name: ECHO
  version: "1.0.0"
  author: "Genesis Protocol"
  description: "Test agent: echoes messages with timestamp"

  type: AGENT
  domain: TESTING

  capabilities:
    - echo_back

  dependencies:
    - vibe_core

  config:
    enabled: true

  responsibilities:
    - "Echo back messages from tasks"
    - "Respond with timestamp"

  actions:
    - action: echo_back
      description: "Echo a message back with timestamp"
      params:
        - name: message
          type: string
          required: true
          description: "Message to echo"

steward:
  constitutional_oath: optional
  governance_domain: TESTING
  risk_level: LOW
"""

ECHO_PYTHON_TEMPLATE = '''#!/usr/bin/env python3
"""
🔔 ECHO CARTRIDGE - Test Agent 🔔

ECHO is a minimal VibeAgent for testing the cartridge protocol.
It echoes back messages with a timestamp.

This demonstrates:
1. Valid VibeAgent implementation
2. Proper inheritance from VibeAgent
3. Task processing and response format
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any

from vibe_core.agent_protocol import VibeAgent, AgentManifest
from vibe_core.scheduling.task import Task

# Constitutional Oath
logger = logging.getLogger("ECHO_CARTRIDGE")


class EchoCartridge(VibeAgent):
    """
    The ECHO Agent Cartridge (Test Agent).

    A minimal but valid VibeAgent that echoes back messages.
    Used to verify the cartridge protocol works correctly.
    """

    def __init__(self):
        """Initialize ECHO as a VibeAgent."""
        super().__init__(
            agent_id="echo",
            name="ECHO",
            version="1.0.0",
            author="Genesis Protocol",
            description="Test agent: echoes messages with timestamp",
            domain="TESTING",
            capabilities=["echo_back"]
        )

        logger.info("🔔 ECHO Cartridge initializing...")

        # Initialize Constitutional Oath mixin (if available)
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            self.oath_sworn = True
            logger.info("✅ ECHO has sworn the Constitutional Oath")

        logger.info("🔔 ECHO Cartridge ready")
        self.tasks_processed = 0
        self.tasks_successful = 0

    def get_manifest(self) -> AgentManifest:
        """Return agent manifest (identity declaration)."""
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

    def report_status(self) -> Dict[str, Any]:
        """Report agent status for kernel heartbeat."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": "operational",
            "tasks_processed": self.tasks_processed,
            "tasks_successful": self.tasks_successful
        }

    def process(self, task: Task) -> Dict[str, Any]:
        """
        Process a task from the kernel scheduler.

        Task payload format:
        {
            "action": "echo_back",
            "params": {
                "message": "Your message here"
            }
        }
        """
        self.tasks_processed += 1
        logger.info(f"📬 ECHO processing task {task.task_id}...")

        try:
            action = task.payload.get("action")
            params = task.payload.get("params", {})

            if action == "echo_back":
                result = self._echo_back(params)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }

            if result.get("success"):
                self.tasks_successful += 1
                logger.info(f"✅ Task {task.task_id} completed")
            else:
                err_msg = result.get('error')
                logger.warning(f"⚠️  Task {task.task_id} failed: {err_msg}")

            return result

        except Exception as e:
            logger.error(f"❌ Task processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task.task_id
            }

    def _echo_back(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Action: Echo back the message with timestamp.

        Params:
        - message (required): Message to echo
        """
        message = params.get("message")

        if not message:
            return {
                "success": False,
                "error": "Missing required param: message"
            }

        timestamp = datetime.now(timezone.utc).isoformat()

        return {
            "success": True,
            "action": "echo_back",
            "message": message,
            "timestamp": timestamp,
            "echo_id": f"{self.agent_id}_{timestamp}"
        }
'''

# ═════════════════════════════════════════════════════════════════════════
# GENESIS EXPANSION ORCHESTRATION
# ═════════════════════════════════════════════════════════════════════════


def step1_forge_soul(engineer: EngineerCartridge) -> Optional[str]:
    """
    STEP 1: Engineer generates cartridge.yaml (The Soul)

    Returns: Absolute path to generated cartridge.yaml, or None on failure
    """
    print_step(1, "Forging the Soul (cartridge.yaml)")

    task = Task(
        agent_id="engineer",
        payload={
            "action": "manifest_reality",
            "feature_spec": "cartridge.yaml for Echo test agent",
            "path": "echo/cartridge.yaml",
            "content": ECHO_YAML_TEMPLATE,
            "use_brain": False,
        },
        task_id="genesis_yaml",
    )

    try:
        result = engineer.process(task)

        if result.get("status") != "manifested":
            print_error(f"Engineer failed: {result.get('reason', 'unknown')}")
            return None

        yaml_path = result.get("path")
        print_success(f"Generated: {yaml_path}")

        # Verify file exists
        if not os.path.exists(yaml_path):
            print_error("Generated file not found in sandbox")
            return None

        print_success("YAML file validated")
        return yaml_path

    except Exception as e:
        print_error(f"Exception during YAML generation: {e}")
        return None


def step2_forge_body(engineer: EngineerCartridge) -> Optional[str]:
    """
    STEP 2: Engineer generates cartridge_main.py (The Body)

    Returns: Absolute path to generated cartridge_main.py, or None on failure
    """
    print_step(2, "Forging the Body (cartridge_main.py)")

    task = Task(
        agent_id="engineer",
        payload={
            "action": "manifest_reality",
            "feature_spec": "cartridge_main.py for Echo test agent",
            "path": "echo/cartridge_main.py",
            "content": ECHO_PYTHON_TEMPLATE,
            "use_brain": False,
        },
        task_id="genesis_python",
    )

    try:
        result = engineer.process(task)

        if result.get("status") != "manifested":
            print_error(f"Engineer failed: {result.get('reason', 'unknown')}")
            return None

        python_path = result.get("path")
        print_success(f"Generated: {python_path}")

        # Verify file exists
        if not os.path.exists(python_path):
            print_error("Generated file not found in sandbox")
            return None

        # Quick syntax check
        try:
            with open(python_path, "r") as f:
                compile(f.read(), python_path, "exec")
            print_success("Python syntax validated")
        except SyntaxError as e:
            print_error(f"Python syntax error: {e}")
            return None

        return python_path

    except Exception as e:
        print_error(f"Exception during Python generation: {e}")
        return None


def step3_gatekeeper(auditor: AuditorCartridge, python_path: str) -> Optional[Dict[str, Any]]:
    """
    STEP 3: Auditor verifies Python code (The Gatekeeper)

    Returns: Auditor result dict, or None on failure
    """
    print_step(3, "The Gatekeeper (Auditor verification)")

    task = Task(
        agent_id="auditor",
        payload={"action": "verify_changes", "path": python_path},
        task_id="genesis_audit",
    )

    try:
        result = auditor.process(task)

        if not result.get("passed"):
            print_error(f"Audit failed: {result.get('reason', 'unknown')}")
            print_error(f"Details: {result.get('details', 'none')}")
            return None

        print_success(f"Auditor Stamp: {result.get('stamp', 'APPROVED')}")
        return result

    except Exception as e:
        print_error(f"Exception during audit: {e}")
        return None


def step4_birth(
    archivist: ArchivistCartridge,
    yaml_path: str,
    python_path: str,
    audit_result: Dict[str, Any],
) -> bool:
    """
    STEP 4: Archivist commits files to /echo/ (The Birth)

    Returns: True if successful, False otherwise
    """
    print_step(4, "The Birth (Archiving to /echo/)")

    # First, commit the Python file
    task_py = Task(
        agent_id="archivist",
        payload={
            "action": "seal_history",
            "source_path": python_path,
            "dest_path": "echo/cartridge_main.py",
            "audit_result": audit_result,
            "message": "Genesis of Echo Agent (Implementation)",
        },
        task_id="seal_python",
    )

    try:
        print_info("Committing cartridge_main.py...")
        result_py = archivist.process(task_py)

        if result_py.get("status") != "sealed":
            print_error(f"Failed to seal Python: {result_py.get('reason', 'unknown')}")
            return False

        print_success(f"Sealed: {result_py.get('commit_short')} - cartridge_main.py")

    except Exception as e:
        print_error(f"Exception sealing Python: {e}")
        return False

    # Then, commit the YAML file (using same audit result, since both safe)
    task_yaml = Task(
        agent_id="archivist",
        payload={
            "action": "seal_history",
            "source_path": yaml_path,
            "dest_path": "echo/cartridge.yaml",
            "audit_result": audit_result,
            "message": "Genesis of Echo Agent (Manifest)",
        },
        task_id="seal_yaml",
    )

    try:
        print_info("Committing cartridge.yaml...")
        result_yaml = archivist.process(task_yaml)

        if result_yaml.get("status") != "sealed":
            print_error(f"Failed to seal YAML: {result_yaml.get('reason', 'unknown')}")
            return False

        print_success(f"Sealed: {result_yaml.get('commit_short')} - cartridge.yaml")
        return True

    except Exception as e:
        print_error(f"Exception sealing YAML: {e}")
        return False


def step5_validate() -> bool:
    """
    STEP 5: Validate the new Echo cartridge structure

    Returns: True if Echo is valid, False otherwise
    """
    print_step(5, "The Proof (Validating Echo structure)")

    # Check directory exists
    if not os.path.exists(ECHO_TARGET):
        print_error(f"Echo directory not found: {ECHO_TARGET}")
        return False

    print_success(f"Echo directory exists: {ECHO_TARGET}")

    # Check cartridge.yaml
    yaml_path = os.path.join(ECHO_TARGET, "cartridge.yaml")
    if not os.path.exists(yaml_path):
        print_error("Missing cartridge.yaml")
        return False

    print_success("✓ cartridge.yaml exists")

    # Check cartridge_main.py
    python_path = os.path.join(ECHO_TARGET, "cartridge_main.py")
    if not os.path.exists(python_path):
        print_error("Missing cartridge_main.py")
        return False

    print_success("✓ cartridge_main.py exists")

    # Validate Python syntax
    try:
        with open(python_path, "r") as f:
            compile(f.read(), python_path, "exec")
        print_success("✓ Python syntax valid")
    except SyntaxError as e:
        print_error(f"Python syntax error: {e}")
        return False

    # Try to import the cartridge
    try:
        # Add echo to path if needed
        sys.path.insert(0, REPO_ROOT)
        from agent_city.registry.citizens.echo.cartridge_main import EchoCartridge

        print_success("✓ EchoCartridge class can be imported")

        # Try to instantiate
        echo = EchoCartridge()
        print_success(f"✓ EchoCartridge instantiated: {echo.name} v{echo.version}")

        # Check required methods
        if not hasattr(echo, "process"):
            print_error("Missing process() method")
            return False

        if not hasattr(echo, "get_manifest"):
            print_error("Missing get_manifest() method")
            return False

        print_success("✓ Required methods exist")

        # Get manifest
        manifest = echo.get_manifest()
        print_success(f"✓ Manifest valid: {manifest.agent_id}")

        return True

    except Exception as e:
        print_error(f"Failed to import/validate: {e}")
        import traceback

        traceback.print_exc()
        return False


# ═════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═════════════════════════════════════════════════════════════════════════


def main():
    """Main orchestration function."""
    print_header("🚀 GENESIS EXPANSION: PROJECT ECHO")

    # Verify we're in the right place
    if not ensure_repo_root():
        print_error("Aborting: Not in steward-protocol repository root")
        return False

    print_success(f"Repository root confirmed: {REPO_ROOT}")

    # Cleanup old sandbox
    cleanup_sandbox()

    # Initialize agents
    print_info("Initializing cartridges...")
    try:
        engineer = EngineerCartridge()
        auditor = AuditorCartridge()
        archivist = ArchivistCartridge()
        print_success("Cartridges initialized")
    except Exception as e:
        print_error(f"Failed to initialize cartridges: {e}")
        return False

    # STEP 1: Forge the Soul
    yaml_path = step1_forge_soul(engineer)
    if not yaml_path:
        print_error("GENESIS FAILED at Step 1")
        return False

    # STEP 2: Forge the Body
    python_path = step2_forge_body(engineer)
    if not python_path:
        print_error("GENESIS FAILED at Step 2")
        return False

    # STEP 3: The Gatekeeper
    audit_result = step3_gatekeeper(auditor, python_path)
    if not audit_result:
        print_error("GENESIS FAILED at Step 3")
        return False

    # STEP 4: The Birth
    if not step4_birth(archivist, yaml_path, python_path, audit_result):
        print_error("GENESIS FAILED at Step 4")
        return False

    # STEP 5: The Proof
    if not step5_validate():
        print_error("GENESIS FAILED at Step 5")
        return False

    # SUCCESS!
    print_header("🎉 GENESIS COMPLETE - PROJECT ECHO BORN")
    print(f"\n✨ Echo Cartridge is now alive in: {ECHO_TARGET}")
    print("\nNext steps:")
    print("1. Boot the VibeKernel to load and register Echo")
    print("2. Submit tasks to Echo via the kernel scheduler")
    print("3. Verify Echo processes echo_back actions correctly\n")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
