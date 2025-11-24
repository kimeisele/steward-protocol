#!/usr/bin/env python3
"""
ENVOY CARTRIDGE - The Brain Connected to the Heart

The Envoy is the diplomatic and operational interface between:
- User Intent (console input)
- VibeOS Kernel (real execution engine)
- Agent City (Herald, Civic, Forum, etc.)

This cartridge is now a native VibeAgent:
- Receives tasks from the kernel scheduler
- Owns the CityControlTool (Golden Straw)
- Routes user commands through proper kernel channels
- Maintains operational logs

The Envoy was the missing link. Now it's truly wired in.
"""

import logging
import json
from typing import Dict, Any, Optional
from pathlib import Path

# VibeOS Integration
from vibe_core import VibeAgent, Task

# Envoy's toolset
from envoy.tools.city_control_tool import CityControlTool
from envoy.tools.diplomacy_tool import DiplomacyTool
from envoy.tools.curator_tool import CuratorTool

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ENVOY_CARTRIDGE")


class EnvoyCartridge(VibeAgent):
    """
    The ENVOY Agent Cartridge - Brain of Agent City

    Responsibilities:
    1. Parse user commands from console input
    2. Route commands through proper channels
    3. Maintain operational transparency (logging)
    4. Coordinate between kernel and user

    The Envoy is NOT just an interface - it's an active agent in the kernel.
    When a user types a command, it becomes a Task for the Envoy.
    The Envoy.process() method decides what to do.
    """

    def __init__(self):
        """Initialize the ENVOY as a VibeAgent."""
        # Initialize VibeAgent base class
        super().__init__(
            agent_id="envoy",
            name="ENVOY",
            version="2.0.0",
            author="Steward Protocol",
            description="Universal Operator Interface - diplomatic and operational bridge",
            domain="ORCHESTRATION",
            capabilities=[
                "orchestration",
                "governance",
                "broadcasting",
                "registry",
                "auditing"
            ]
        )

        logger.info("👁️  ENVOY (VibeAgent v2.0) is initializing...")

        # Initialize the Golden Straw (CityControlTool)
        # NOTE: The kernel will be injected later via set_kernel()
        self.city_control = None  # Will be initialized after kernel injection
        self.diplomacy = DiplomacyTool()
        self.curator = CuratorTool()

        # Operation logs (state)
        self.operation_log = []
        self.log_path = Path("data/logs/envoy_operations.jsonl")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("✅ ENVOY ready (awaiting kernel injection)")

    def set_kernel(self, kernel):
        """
        Kernel Injection Override

        When the kernel boots, it injects itself into this agent.
        Now we can initialize CityControlTool with the kernel reference.
        """
        super().set_kernel(kernel)

        # Initialize CityControlTool with kernel reference
        # This is the critical connection: the Envoy now has direct access to the kernel
        self.city_control = CityControlTool(kernel=kernel)
        logger.info("🧠❤️ ENVOY brain wired to kernel heart via CityControlTool")

    def process(self, task: Task) -> Dict[str, Any]:
        """
        Process a Task from the kernel scheduler

        This is the main entry point for all user commands.
        User input → Task → Kernel → Envoy.process() → CityControlTool → Kernel

        Args:
            task: Task with payload containing the command

        Returns:
            dict: Result of the operation
        """
        try:
            logger.info(f"⚡ ENVOY processing task: {task.task_id}")

            # Extract the command from task payload
            payload = task.payload or {}
            command = payload.get("command")
            args = payload.get("args", {})

            if not command:
                return {
                    "status": "error",
                    "task_id": task.task_id,
                    "error": "No command specified in payload"
                }

            # Ensure CityControlTool is initialized
            if not self.city_control:
                return {
                    "status": "error",
                    "task_id": task.task_id,
                    "error": "CityControlTool not initialized (kernel not injected)"
                }

            # Route the command to appropriate handler
            result = self._route_command(command, args, task.task_id)

            # Log operation
            self._log_operation(task.task_id, command, args, result)

            logger.info(f"✅ ENVOY task {task.task_id} completed: {result.get('status')}")
            return result

        except Exception as e:
            error_result = {
                "status": "error",
                "task_id": task.task_id,
                "error": str(e)
            }
            logger.exception(f"❌ ENVOY task {task.task_id} failed: {e}")
            self._log_operation(task.task_id, "unknown", {}, error_result)
            return error_result

    def _route_command(self, command: str, args: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        """
        Route command to appropriate handler

        Commands:
        - status: Get city status
        - proposals: List proposals
        - vote: Vote on proposal
        - execute: Execute approved proposal
        - trigger: Trigger agent action
        - credits: Check agent credits
        - refill: Refill agent credits
        """
        logger.info(f"🔄 ENVOY routing command: {command} with args: {args}")

        try:
            # Status commands
            if command == "status":
                return self.city_control.get_city_status()

            # Governance commands
            elif command == "proposals":
                status = args.get("status", "OPEN")
                return {
                    "status": "success",
                    "proposals": self.city_control.list_proposals(status=status)
                }

            elif command == "vote":
                proposal_id = args.get("proposal_id")
                choice = args.get("choice")
                voter = args.get("voter", "operator")
                if not proposal_id or not choice:
                    return {"status": "error", "error": "proposal_id and choice required"}
                return self.city_control.vote_proposal(proposal_id, choice, voter)

            elif command == "execute":
                proposal_id = args.get("proposal_id")
                if not proposal_id:
                    return {"status": "error", "error": "proposal_id required"}
                return self.city_control.execute_proposal(proposal_id)

            # Agent commands
            elif command == "trigger":
                agent_name = args.get("agent_name")
                action = args.get("action")
                if not agent_name or not action:
                    return {"status": "error", "error": "agent_name and action required"}
                kwargs = args.get("kwargs", {})
                return self.city_control.trigger_agent(agent_name, action, **kwargs)

            # Credit commands
            elif command == "credits":
                agent_name = args.get("agent_name")
                if not agent_name:
                    return {"status": "error", "error": "agent_name required"}
                return self.city_control.check_credits(agent_name)

            elif command == "refill":
                agent_name = args.get("agent_name")
                amount = args.get("amount", 50)
                if not agent_name:
                    return {"status": "error", "error": "agent_name required"}
                return self.city_control.refill_credits(agent_name, amount)

            else:
                return {
                    "status": "error",
                    "error": f"Unknown command: {command}"
                }

        except Exception as e:
            logger.error(f"❌ Command routing failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def _log_operation(self, task_id: str, command: str, args: Dict, result: Dict) -> None:
        """Log operation to file for audit trail"""
        try:
            from datetime import datetime, timezone

            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "task_id": task_id,
                "command": command,
                "args": args,
                "result_status": result.get("status", "unknown")
            }

            self.operation_log.append(log_entry)

            # Append to file
            with open(self.log_path, "a") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            logger.warning(f"Failed to log operation: {e}")

    def report_status(self) -> Dict[str, Any]:
        """Report Envoy status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": "RUNNING",
            "capabilities": self.capabilities,
            "city_control_initialized": self.city_control is not None,
            "operations_logged": len(self.operation_log),
            "kernel_injected": self.kernel is not None
        }
