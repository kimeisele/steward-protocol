#!/usr/bin/env python3
"""
🗡️ CHRONICLE CARTRIDGE - The Keeper of Temporal Lines 🗡️

CHRONICLE is the Vyasa of Agent City - the historian and scribe who:
1. Records all code changes (Git commits)
2. Reads the historical timeline (Git log)
3. Forks new possible futures (Git branches)
4. Manifests code into reality (staged commits)

This is a VibeAgent that:
- Inherits from vibe_core.VibeAgent
- Receives tasks from the kernel scheduler
- Executes deterministic Git operations
- Maintains immutable code history with cryptographic signatures

Philosophy:
"I am Vyasa. I write the Mahabharata of your code.
Every commit is a verse. Every branch is a possible universe."
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x5501ec91"  # GenesisByte: parampara % 37 == 0

import logging
from typing import Any, Dict

# VibeOS Integration
from vibe_core import AgentManifest, Task, VibeAgent

# Config import with fallback
try:
    from vibe_core.config import CityConfig
except ImportError:
    CityConfig = None

# Constitutional Oath Mixin
from vibe_core.steward import OathMixin

# ALL TOOLS: Accessed via kernel (self.system.execute_tool)
# - chronicle.git - Git operations (commits, branches, history)

# Constitutional Oath
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CHRONICLE_CARTRIDGE")


class ChronicleCartridge(VibeAgent, OathMixin):
    """
    The CHRONICLE Agent Cartridge (The Historian).

    Manages the immutable code timeline and repository operations.

    Key Responsibilities:
    - Git Operations: Commits, branches, history queries
    - Code Archival: Seal changes with cryptographic signatures
    - Timeline Management: Create branches (possible universes)
    - History Queries: Read the git log and understand code evolution

    Philosophy:
    "Every piece of code has a story. I am the keeper of that story."
    """

    def __init__(self, config=None):
        """Initialize CHRONICLE (The Historian) as a VibeAgent."""
        # BLOCKER #0: Accept Phoenix Config
        if config:
            self.config = config
        elif CityConfig is not None:
            self.config = CityConfig()
        else:
            self.config = None

        # Initialize VibeAgent base class
        super().__init__(
            agent_id="chronicle",
            name="CHRONICLE",
            version="1.0.0",
            author="Steward Protocol",
            description="Temporal agent: manages git operations, commits, branches, and code history",
            domain="SYSTEM",
            capabilities=[
                "content_generation",  # Can create commits (git operations)
                "chronicle.git",  # Required capability for chronicle.git tool access
            ],
        )

        logger.info("🗡️  CHRONICLE Cartridge initializing (VibeAgent v1.0)...")

        # Initialize Constitutional Oath mixin (if available)
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            # Use SYNC oath ceremony (works in __init__ regardless of event loop)
            self.swear_oath_sync()
            logger.info("✅ CHRONICLE has sworn the Constitutional Oath")

        # NO tool instances owned - agent is NAKED
        # Tools accessed via self.system.execute_tool()
        logger.info("✅ CHRONICLE ready (NO tool instances owned)")

        # Task count for tracking
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
            dependencies=[],
        )

    def report_status(self) -> Dict[str, Any]:
        """Report agent status for kernel heartbeat."""
        # Get git status via kernel
        git_result = self.system.execute_tool("chronicle.git", {"action": "get_status"})
        git_status = git_result.output if git_result.success else {"success": False}

        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": "operational",
            "tasks_processed": self.tasks_processed,
            "tasks_successful": self.tasks_successful,
            "git_status": git_status,
        }

    async def process(self, task: Task) -> Dict[str, Any]:
        """
        Process a task from the kernel scheduler.

        Task format:
        {
            "action": "seal_history" | "read_history" | "fork_reality" | "manifest_reality",
            "params": {
                "message": str,          # For seal_history
                "files": List[str],      # For seal_history, manifest_reality
                "pattern": str,          # For read_history
                "branch_name": str       # For fork_reality
            }
        }
        """
        self.tasks_processed += 1
        logger.info(f"📜 CHRONICLE processing task {task.task_id}...")

        try:
            action = task.input.get("action")
            params = task.input.get("params", {})

            if action == "seal_history":
                result = self._seal_history(params)
            elif action == "read_history":
                result = self._read_history(params)
            elif action == "fork_reality":
                result = self._fork_reality(params)
            elif action == "manifest_reality":
                result = self._manifest_reality(params)
            else:
                result = {"success": False, "error": f"Unknown action: {action}"}

            if result.get("success"):
                self.tasks_successful += 1
                logger.info(f"✅ Task {task.task_id} completed successfully")
            else:
                logger.warning(f"⚠️  Task {task.task_id} failed: {result.get('error', 'Unknown error')}")

            return result

        except Exception as e:
            logger.error(f"❌ Task processing failed: {e}")
            return {"success": False, "error": str(e), "task_id": task.task_id}

    def _seal_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Action: Seal the timeline with a commit.

        Params:
        - message (required): Commit message
        - files (optional): List of files to commit
        - sign (optional): Whether to sign (default: True)
        """
        message = params.get("message")
        files = params.get("files")
        sign = params.get("sign", True)

        if not message:
            return {"success": False, "error": "Missing required param: message"}

        logger.info(f"🔐 Sealing history with message: {message[:50]}...")

        tool_result = self.system.execute_tool(
            "chronicle.git", {"action": "seal_history", "message": message, "files": files, "sign": sign}
        )

        if not tool_result.success:
            return {"success": False, "error": tool_result.error}

        result = tool_result.output
        return {
            "success": result["success"],
            "action": "seal_history",
            "commit_hash": result.get("commit_hash"),
            "message": result.get("message"),
            "timestamp": result.get("timestamp"),
        }

    def _read_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Action: Read the timeline (git log).

        Params:
        - pattern (optional): File pattern to filter
        - limit (optional): Max commits to return (default: 10)
        """
        pattern = params.get("pattern")
        limit = params.get("limit", 10)

        logger.info(f"📖 Reading history (limit: {limit})...")

        tool_params = {"action": "read_history", "limit": limit}
        if pattern:
            tool_params["pattern"] = pattern

        tool_result = self.system.execute_tool("chronicle.git", tool_params)

        if not tool_result.success:
            return {"success": False, "error": tool_result.error}

        result = tool_result.output
        return {
            "success": result["success"],
            "action": "read_history",
            "commits": result.get("commits", []),
            "message": result.get("message"),
        }

    def _fork_reality(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Action: Fork reality (create new branch).

        Params:
        - branch_name (required): Name of the new branch
        """
        branch_name = params.get("branch_name")

        if not branch_name:
            return {"success": False, "error": "Missing required param: branch_name"}

        logger.info(f"🔀 Forking reality: {branch_name}...")

        tool_result = self.system.execute_tool("chronicle.git", {"action": "fork_reality", "branch_name": branch_name})

        if not tool_result.success:
            return {"success": False, "error": tool_result.error}

        result = tool_result.output
        return {
            "success": result["success"],
            "action": "fork_reality",
            "branch": result.get("branch"),
            "message": result.get("message"),
        }

    def _manifest_reality(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Action: Manifest reality (stage files).

        Params:
        - files (required): List of files to stage
        """
        files = params.get("files")

        if not files:
            return {"success": False, "error": "Missing required param: files"}

        logger.info(f"📋 Manifesting {len(files)} files...")

        tool_result = self.system.execute_tool("chronicle.git", {"action": "manifest_reality", "files": files})

        if not tool_result.success:
            return {"success": False, "error": tool_result.error}

        result = tool_result.output
        return {
            "success": result["success"],
            "action": "manifest_reality",
            "staged_files": result.get("staged_files", []),
            "message": result.get("message"),
        }
