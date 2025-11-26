#!/usr/bin/env python3
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
try:
    from steward.oath_mixin import OathMixin
except ImportError:
    OathMixin = None

logger = logging.getLogger("ECHO_CARTRIDGE")


class EchoCartridge(VibeAgent, OathMixin if OathMixin else object):
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
            try:
                self.swear_constitutional_oath()
                logger.info("✅ ECHO has sworn the Constitutional Oath")
            except Exception as e:
                logger.warning(f"⚠️  Oath swearing failed: {e}")

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
