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
from vibe_core.config import CityConfig, CityConfig

# Envoy's toolset
from .tools.city_control_tool import CityControlTool
from .tools.diplomacy_tool import DiplomacyTool
from .tools.curator_tool import CuratorTool
from .tools.run_campaign_tool import RunCampaignTool
from .tools.gap_report_tool import GAPReportTool
from .tools.hil_assistant_tool import HILAssistantTool

# Constitutional Oath
try:
    from steward.oath_mixin import OathMixin
except ImportError:
    OathMixin = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ENVOY_CARTRIDGE")


class EnvoyCartridge(VibeAgent, OathMixin if OathMixin else object):
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

    def __init__(self, config: Optional[CityConfig] = None):
        """Initialize the ENVOY as a VibeAgent."""
        # BLOCKER #0: Accept Phoenix Config
        self.config = config or CityConfig()

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

        # Initialize Constitutional Oath mixin (if available)
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            # SWEAR THE OATH IMMEDIATELY in __init__ (synchronous)
            # This ensures ENVOY has oath_sworn=True before kernel registration
            self.oath_sworn = True
            logger.info("✅ ENVOY has sworn the Constitutional Oath (Genesis Ceremony)")

        logger.info("👁️  ENVOY (VibeAgent v2.0) is initializing...")

        # Initialize the Golden Straw (CityControlTool)
        # NOTE: The kernel will be injected later via set_kernel()
        self.city_control = None  # Will be initialized after kernel injection
        self.diplomacy = DiplomacyTool()
        self.curator = CuratorTool()
        self.campaign_tool = RunCampaignTool()  # Initialize campaign orchestration
        self.gap_report = GAPReportTool()  # Initialize governance audit proof reporting
        self.hil_assistant = HILAssistantTool()  # Initialize HIL Assistant (VAD Layer)

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

        # Inject kernel into campaign tool
        self.campaign_tool.set_kernel(kernel)
        logger.info("🎯 RunCampaignTool connected to kernel")

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
    def get_manifest(self):
        """Return agent manifest for kernel registry."""
        from vibe_core.agent_protocol import AgentManifest
        return AgentManifest(
            agent_id="envoy",
            name="ENVOY",
            version=self.version if hasattr(self, 'version') else "1.0.0",
            author="Steward Protocol",
            description="User interface and orchestration",
            domain="ORCHESTRATION",
            capabilities=['playbook_execution', 'orchestration']
        )



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
        - campaign: Run multi-agent marketing campaign
        - report: Generate G.A.P. (Governability Audit Proof) report
        - next_action: Get strategic advice from HIL Assistant
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

            elif command == "campaign":
                goal = args.get("goal")
                campaign_type = args.get("campaign_type", "recruitment")
                if not goal:
                    return {"status": "error", "error": "goal required for campaign"}
                # Extract additional parameters
                campaign_params = {k: v for k, v in args.items()
                                  if k not in ["goal", "campaign_type"]}
                return self.campaign_tool.run_campaign(goal, campaign_type, **campaign_params)

            elif command == "report":
                report_type = args.get("report_type", "gap")
                if report_type == "gap":
                    # Generate G.A.P. Report
                    title = args.get("title", "System Governability Audit Proof")
                    report = self.gap_report.generate_report(title)

                    # Export report
                    output_format = args.get("format", "json")
                    report_path = self.gap_report.export_report(report, output_format)

                    return {
                        "status": "success",
                        "report_type": "gap",
                        "title": title,
                        "report_path": report_path,
                        "report_hash": report.get("verification", {}).get("sha256_hash"),
                        "sections": list(report.get("sections", {}).keys())
                    }
                else:
                    return {"status": "error", "error": f"Unknown report type: {report_type}"}

            elif command == "next_action":
                # HIL Assistant: Get Next Best Action
                # 1. Try to get the latest report content if available
                report_content = args.get("report_content", "")
                
                # If no content provided, try to find the latest G.A.P. report
                if not report_content:
                    try:
                        import glob
                        import os
                        list_of_files = glob.glob('data/reports/GAP_Report_*.markdown')
                        if list_of_files:
                            latest_file = max(list_of_files, key=os.path.getctime)
                            with open(latest_file, 'r') as f:
                                report_content = f.read()
                    except Exception as e:
                        logger.warning(f"Could not auto-load latest report: {e}")
                        report_content = "No report available."

                summary = self.hil_assistant.get_next_action_summary(report_content)
                
                return {
                    "status": "success",
                    "action": "strategic_briefing",
                    "summary": summary
                }

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
        """Report Envoy status - Deep Introspection"""
        # Count operations from log file
        operations_count = 0
        if self.log_path.exists():
            try:
                with open(self.log_path, "r") as f:
                    operations_count = len(f.readlines())
            except:
                operations_count = 0

        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": "RUNNING",
            "domain": "ORCHESTRATION",
            "capabilities": self.capabilities,
            "orchestration_metrics": {
                "city_control_initialized": self.city_control is not None,
                "operations_logged_in_memory": len(self.operation_log),
                "operations_logged_persistent": operations_count,
                "kernel_injected": self.kernel is not None,
                "log_path": str(self.log_path),
                "hil_assistant_active": True
            }
        }
