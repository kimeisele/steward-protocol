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

import json
import logging
from typing import Any, Dict, Optional

# VibeOS Integration
from vibe_core import Task
from vibe_core.agents.context_aware_agent import ContextAwareAgent

# OPUS-307 Phase I.2: ExecutorSingularity replaces DeterministicExecutor
from vibe_core.cartridges.system.envoy.executor_singularity import (
    ExecutorSingularity,
    create_executor_singularity,
)

# GAD-5500: The Missing Link (Wiring)
from vibe_core.config import CityConfig

# Constitutional Oath Mixin
from vibe_core.steward import OathMixin

# ALL TOOLS: Accessed via kernel (self.system.execute_tool)
# - envoy.city_control (CityControlTool) - The Golden Straw
# - envoy.curator (CuratorTool) - Governance analysis
# - envoy.diplomacy (DiplomacyTool) - GitHub outreach
# - envoy.gap_report (GAPReportTool) - G.A.P. Report generation
# - envoy.hil (HILAssistantTool) - HIL Assistant (VAD Layer)
# - envoy.campaign (RunCampaignTool) - Campaign orchestration
#
# ✅ MIGRATION COMPLETE: All tool calls converted to kernel routing

# Constitutional Oath
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ENVOY_CARTRIDGE")


class EnvoyCartridge(ContextAwareAgent, OathMixin):
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
            version="3.1.0",  # Bumped for GAD-5500 Wiring
            author="Steward Protocol",
            description="Universal Operator Interface - diplomatic and operational bridge",
            domain="INTERFACE",
            capabilities=[
                "orchestration",
                "governance",
                "broadcasting",
                "registry",
                "auditing",
                "circuit_execution",  # GAD-5500
                # Tool capabilities (required to execute tools via self.system)
                "envoy.city_control",
                "envoy.curator",
                "envoy.diplomacy",
                "envoy.gap_report",
                "envoy.hil",
                "envoy.campaign",
            ],
        )

        # Initialize Constitutional Oath mixin (if available)
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            # SWEAR THE OATH IMMEDIATELY in __init__ (synchronous)
            # This ensures ENVOY has oath_sworn=True before kernel registration
            self.oath_sworn = True
            logger.info("✅ ENVOY has sworn the Constitutional Oath (Genesis Ceremony)")

        logger.info("👁️  ENVOY (VibeAgent v3.1) is initializing...")

        # OPUS-307 Phase I.2: ExecutorSingularity (lazy init - needs kernel)
        # Router will be accessed from EnvoyPlugin via kernel
        self._router = None  # Lazy - set when kernel available
        self._executor_singularity = None  # Lazy - needs kernel
        logger.info("✋ ExecutorSingularity will be initialized with kernel (OPUS-307)")

        # ALL TOOLS: Accessed via kernel (self.system.execute_tool)
        # NO tool instances owned - agent is NAKED
        # Available tools (kernel-managed):
        # - envoy.city_control - The Golden Straw
        # - envoy.curator - Governance analysis
        # - envoy.diplomacy - GitHub outreach
        # - envoy.gap_report - G.A.P. Report generation
        # - envoy.hil - HIL Assistant (VAD Layer)
        # - envoy.campaign - Campaign orchestration

        # PHASE 2.3: Lazy-load operation log path after system interface injection
        self.operation_log = []
        self._log_path = None

        logger.info("✅ ENVOY ready (NO tool instances owned)")

    @property
    def log_path(self):
        """Lazy-load log path (sandboxed)."""
        if self._log_path is None:
            self._log_path = self.system.get_sandbox_path() / "logs" / "envoy_operations.jsonl"
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
        return self._log_path

    @property
    def router(self):
        """Get UnifiedRouter from EnvoyPlugin."""
        if self._router is None and self.kernel:
            if hasattr(self.kernel, "envoy") and self.kernel.envoy:
                self._router = self.kernel.envoy._unified_router
        return self._router

    @property
    def executor(self) -> ExecutorSingularity:
        """
        OPUS-307 Phase I.2: Lazy-init ExecutorSingularity.

        Returns the unified executor (no fallback, no DeterministicExecutor).
        """
        if self._executor_singularity is None and self.kernel:
            self._executor_singularity = create_executor_singularity(self.kernel)
            logger.info("✋ ExecutorSingularity initialized (OPUS-307)")
        return self._executor_singularity

    # NO set_kernel() override - tools accessed via self.system.execute_tool()

    async def process(self, task: Task) -> Dict[str, Any]:
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
            # Router comes from EnvoyPlugin - no manual injection needed
            logger.info(f"⚡ ENVOY processing task: {task.task_id}")

            # Extract the command from task payload
            # Support multiple payload formats:
            # 1. Direct command: {"command": "status", "args": {...}}
            # 2. ENVOY.md request: {"type": "envoy_request", "request": "...", "route": "..."}
            # 3. Input-based: {"input": "user query"}
            payload = task.payload or {}
            command = payload.get("command")
            args = payload.get("args", {})

            # Handle ENVOY.md requests (from EnvoySync)
            if payload.get("type") == "envoy_request":
                user_input = payload.get("request", "")
                # Use the pre-routed task if available
                if payload.get("route"):
                    command = payload.get("route")
            else:
                user_input = payload.get("input", "") or command  # Fallback to command if input missing

            if not command and not user_input:
                return {
                    "status": "error",
                    "task_id": task.task_id,
                    "error": "No command or input specified in payload",
                }

            # 1. Check for Internal Envoy Commands first (Fast Path)
            # These are direct commands like "status", "vote", "credits"
            if command and command in [
                "status",
                "proposals",
                "vote",
                "execute",
                "trigger",
                "credits",
                "refill",
                "campaign",
                "report",
                "next_action",
            ]:
                # Route the command to appropriate handler
                result = self._route_command(command, args, task.task_id)
                self._log_operation(task.task_id, command, args, result)
                logger.info(f"✅ ENVOY internal command {task.task_id} completed: {result.get('status')}")
                return result

            # 2. Route via UnifiedRouter (Classification)
            logger.info(f"🧠 Routing via UnifiedRouter: {user_input}")
            if not self.router:
                logger.error("❌ UnifiedRouter not available - EnvoyPlugin not loaded?")
                return {"status": "error", "error": "Router not initialized"}

            request = self.router.route(user_input, source="cartridge")
            routing_decision = {
                "status": "routing" if request.gate_decision.value == "allow" else request.gate_decision.value,
                "path": request.execution_path.value,
                "details": {"confidence": request.confidence, "target": request.target_id},
            }

            # 3. Handle Routing Decision
            status = routing_decision.get("status")
            path = routing_decision.get("path")

            if status == "blocked":
                return {"status": "blocked", "reason": routing_decision.get("reason")}

            elif status == "queued":
                # Lazy queue - return acknowledgment
                return {"status": "queued", "request_id": routing_decision.get("request_id")}

            elif status == "critical":
                # P4.1: GAJENDRA PROTOCOL - Emergency kernel bypass
                logger.warning("🐘 CRITICAL PRIORITY - Direct kernel execution")
                # Execute immediately with highest priority
                from vibe_core.scheduling.task import Task

                critical_task = Task(agent_id="envoy", payload={"input": user_input, "critical": True})
                task_id = self.kernel.submit_task(critical_task)
                return {"status": "critical_handled", "task_id": task_id}

            elif status == "routing":
                # Execute based on path
                if path == "flash":
                    # Simple queries - use ExecutorSingularity (OPUS-307)
                    result = await self.executor.execute(
                        playbook_or_circuit_id="SIMPLE_QUERY",
                        user_input=user_input,
                        intent_vector=routing_decision.get("details"),
                    )
                    return result

                elif path == "science":
                    # Complex queries - submit to SCIENCE agent via kernel
                    from vibe_core.scheduling.task import Task

                    task = Task(agent_id="science", payload={"query": user_input})
                    task_id = self.kernel.submit_task(task)
                    return {"status": "delegated", "agent": "science", "task_id": task_id}

                elif path == "lazy":
                    # Lazy processing - queue for background execution
                    logger.info("⏳ Lazy path - queuing for background processing")
                    # Note: Actual queuing happens in UnifiedRouter
                    return {
                        "status": "queued",
                        "path": "lazy",
                        "request_id": routing_decision.get("request_id"),
                        "message": "Request queued for lazy processing",
                    }

                else:
                    # P4.1: Unknown path - log warning and use flash as fallback
                    logger.warning(f"Unknown routing path '{path}', using flash fallback")
                    result = await self.executor.execute(
                        playbook_or_circuit_id="SIMPLE_QUERY",
                        user_input=user_input,
                        intent_vector=routing_decision.get("details"),
                    )
                    return result

            # Fallback
            return {"status": "error", "error": "Unknown routing status"}

        except Exception as e:
            error_result = {"status": "error", "task_id": task.task_id, "error": str(e)}
            logger.exception(f"❌ ENVOY task {task.task_id} failed: {e}")
            self._log_operation(task.task_id, "unknown", {}, error_result)
            return error_result

    def get_manifest(self):
        """Return agent manifest for kernel registry."""
        from vibe_core.protocols import AgentManifest

        return AgentManifest(
            agent_id="envoy",
            name="ENVOY",
            version=self.version if hasattr(self, "version") else "1.0.0",
            author="Steward Protocol",
            description="User interface and orchestration",
            domain="INTERFACE",
            capabilities=["playbook_execution", "orchestration", "circuit_execution"],
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
        - research: Gather research/intelligence on a topic (via herald.research)
        """
        logger.info(f"🔄 ENVOY routing command: {command} with args: {args}")

        try:
            # Status commands - GAD-6000: Route to SYSTEM_STATUS_V2 circuit
            if command == "status":
                # Try circuit execution first (neuro-symbolic, no LLM)
                if self.kernel and hasattr(self.kernel, "envoy"):
                    try:
                        circuit_result = self.kernel.envoy.execute_circuit(
                            "SYSTEM_STATUS_V2",
                            params={"user_input": "status"},
                        )
                        if circuit_result.get("status") == "COMPLETED":
                            # FIX 4: Extract rendered output from correct path
                            # Circuit returns: {phases_executed: [{phase_id: "render_output", result: {rendered: "..."}}]}
                            rendered = ""
                            phases = circuit_result.get("phases_executed", [])
                            for phase in phases:
                                if phase.get("phase_id") == "render_output":
                                    result = phase.get("result", {})
                                    rendered = result.get("rendered", "") if isinstance(result, dict) else ""
                                    break
                            # Fallback: check details.rendered for backwards compatibility
                            if not rendered:
                                details = circuit_result.get("details", {})
                                if isinstance(details.get("rendered"), dict):
                                    rendered = details.get("rendered", {}).get("rendered", "")
                                elif isinstance(details.get("rendered"), str):
                                    rendered = details.get("rendered", "")
                            if rendered:
                                return {
                                    "status": "success",
                                    "response": rendered,
                                    "source": "circuit:SYSTEM_STATUS_V2",
                                }
                    except Exception as e:
                        logger.warning(f"Circuit execution failed, falling back to tool: {e}")

                # Fallback: direct tool call
                result = self.system.execute_tool("envoy.city_control", {"action": "get_city_status"})
                return result.output if result.success else {"status": "error", "error": result.error}

            # Governance commands
            elif command == "proposals":
                status = args.get("status", "OPEN")
                return {
                    "status": "success",
                    "proposals": self.system.execute_tool(
                        "envoy.city_control", {"action": "list_proposals", "status": status}
                    ).output.get("proposals", []),
                }

            elif command == "vote":
                proposal_id = args.get("proposal_id")
                choice = args.get("choice")
                voter = args.get("voter", "operator")
                if not proposal_id or not choice:
                    return {
                        "status": "error",
                        "error": "proposal_id and choice required",
                    }
                result = self.system.execute_tool(
                    "envoy.city_control",
                    {"action": "vote_proposal", "proposal_id": proposal_id, "choice": choice, "voter": voter},
                )
                return result.output if result.success else {"status": "error", "error": result.error}

            elif command == "execute":
                proposal_id = args.get("proposal_id")
                if not proposal_id:
                    return {"status": "error", "error": "proposal_id required"}
                result = self.system.execute_tool(
                    "envoy.city_control", {"action": "execute_proposal", "proposal_id": proposal_id}
                )
                return result.output if result.success else {"status": "error", "error": result.error}

            # Agent commands
            elif command == "trigger":
                agent_name = args.get("agent_name")
                action = args.get("action")
                if not agent_name or not action:
                    return {
                        "status": "error",
                        "error": "agent_name and action required",
                    }
                kwargs = args.get("kwargs", {})
                result = self.system.execute_tool(
                    "envoy.city_control",
                    {"action": "trigger_agent", "agent_name": agent_name, "agent_action": action, **kwargs},
                )
                return result.output if result.success else {"status": "error", "error": result.error}

            # Credit commands
            elif command == "credits":
                agent_name = args.get("agent_name")
                if not agent_name:
                    return {"status": "error", "error": "agent_name required"}
                result = self.system.execute_tool(
                    "envoy.city_control", {"action": "check_credits", "agent_name": agent_name}
                )
                return result.output if result.success else {"status": "error", "error": result.error}

            elif command == "refill":
                agent_name = args.get("agent_name")
                amount = args.get("amount", 50)
                if not agent_name:
                    return {"status": "error", "error": "agent_name required"}
                result = self.system.execute_tool(
                    "envoy.city_control", {"action": "refill_credits", "agent_name": agent_name, "amount": amount}
                )
                return result.output if result.success else {"status": "error", "error": result.error}

            elif command == "campaign":
                goal = args.get("goal")
                campaign_type = args.get("campaign_type", "recruitment")
                if not goal:
                    return {"status": "error", "error": "goal required for campaign"}
                # Extract additional parameters
                campaign_params = {k: v for k, v in args.items() if k not in ["goal", "campaign_type"]}
                result = self.system.execute_tool(
                    "envoy.campaign",
                    {"action": "run_campaign", "goal": goal, "campaign_type": campaign_type, **campaign_params},
                )
                return result.output if result.success else {"status": "error", "error": result.error}

            elif command == "report":
                report_type = args.get("report_type", "gap")
                if report_type == "gap":
                    # Generate G.A.P. Report
                    title = args.get("title", "System Governability Audit Proof")
                    result = self.system.execute_tool("envoy.gap_report", {"action": "generate_report", "title": title})
                    report = result.output if result.success else {}

                    # Export report
                    output_format = args.get("format", "json")
                    result = self.system.execute_tool(
                        "envoy.gap_report",
                        {"action": "export_report", "report": report, "output_format": output_format},
                    )
                    report_path = result.output.get("export_path") if result.success else None

                    return {
                        "status": "success",
                        "report_type": "gap",
                        "title": title,
                        "report_path": report_path,
                        "report_hash": report.get("verification", {}).get("sha256_hash"),
                        "sections": list(report.get("sections", {}).keys()),
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"Unknown report type: {report_type}",
                    }

            elif command == "next_action":
                # HIL Assistant: Get Next Best Action
                # 1. Try to get the latest report content if available
                report_content = args.get("report_content", "")

                # If no content provided, try to find the latest G.A.P. report
                if not report_content:
                    try:
                        import glob
                        import os

                        list_of_files = glob.glob("data/reports/GAP_Report_*.markdown")
                        if list_of_files:
                            latest_file = max(list_of_files, key=os.path.getctime)
                            with open(latest_file, "r") as f:
                                report_content = f.read()
                    except Exception as e:
                        logger.warning(f"Could not auto-load latest report: {e}")
                        report_content = "No report available."

                result = self.system.execute_tool(
                    "envoy.hil", {"action": "get_next_action", "full_report": report_content}
                )
                summary = result.output.get("summary") if result.success else "Error: Could not generate summary"

                return {
                    "status": "success",
                    "action": "strategic_briefing",
                    "summary": summary,
                }

            # Research command - Not Implemented (Architecture Decision)
            elif command == "research" or command == "gather_research":
                # Research is handled by SCIENCE agent, not ENVOY
                # ENVOY is for coordination/routing, not data gathering
                topic = args.get("topic", "")
                sources = args.get("sources", "web")

                return {
                    "status": "not_implemented",
                    "command": "research",
                    "topic": topic,
                    "sources": sources,
                    "message": (
                        "Research capability is not available through ENVOY. "
                        "Use the SCIENCE agent for research tasks, or route via: "
                        "'steward do \"research [topic]\"' for automatic agent selection."
                    ),
                    "suggestion": "Try: steward delegate science research --topic '{}'".format(topic)
                    if topic
                    else None,
                }

            else:
                return {"status": "error", "error": f"Unknown command: {command}"}

        except Exception as e:
            logger.error(f"❌ Command routing failed: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc(),
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
                "result_status": result.get("status", "unknown"),
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
            except Exception:
                operations_count = 0

        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": "RUNNING",
            "domain": "ORCHESTRATION",
            "capabilities": self.capabilities,
            "orchestration_metrics": {
                "city_control_initialized": True,  # Tools accessed via kernel,
                "operations_logged_in_memory": len(self.operation_log),
                "operations_logged_persistent": operations_count,
                "kernel_injected": self.kernel is not None,
                "log_path": str(self.log_path),
                "hil_assistant_active": True,
            },
        }
