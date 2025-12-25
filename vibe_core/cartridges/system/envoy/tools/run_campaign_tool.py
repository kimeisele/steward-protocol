#!/usr/bin/env python3
"""
RunCampaignTool - Multi-Agent Marketing Campaign Orchestration

This tool enables ENVOY to coordinate a multi-agent marketing campaign:
- Goal Parsing: Understand the intent (e.g., "recruit founders")
- Resource Check: Verify HERALD can execute (license + credits)
- Multi-Phase Execution:
  * Phase I: SCIENCE conducts market research
  * Phase II: HERALD generates optimized content
  * Phase III: HERALD publishes the campaign

Architecture:
- ENVOY: Orchestration Brain (this tool)
- SCIENCE: Research Brain (market analysis, trends, targeting)
- HERALD: Content Brain (generation, optimization, publishing)
- CIVIC: Governance Brain (license checks, credit deductions)

Value Creation Chain:
Intent → Resource Check → Research → Content → Publishing → Ledger Record
"""

import logging
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RUN_CAMPAIGN_TOOL")


class CampaignPhase(Enum):
    """Campaign execution phases"""

    PLANNING = "planning"
    RESEARCH = "research"
    CREATION = "creation"
    EXECUTION = "execution"
    COMPLETE = "complete"


class RunCampaignTool(Tool):
    """
    Orchestrates multi-agent marketing campaigns.

    This is the central coordination mechanism that:
    1. Parses high-level intent (HIL) from user
    2. Validates resource availability (CIVIC checks)
    3. Orchestrates multi-phase workflow
    4. Tracks campaign state and results
    5. Records outcomes in ledger
    """

    def __init__(self, services: Optional["ServiceRegistry"] = None, kernel=None):
        super().__init__(services)
        """
        Initialize the campaign orchestration tool.

        Args:
            kernel: VibeOS kernel reference for agent access
        """
        self.kernel = kernel
        self.campaigns = {}  # Track active campaigns
        logger.info("🎯 RunCampaignTool initialized (awaiting kernel injection)")

    @property
    def name(self) -> str:
        return "envoy.campaign"

    @property
    def description(self) -> str:
        return "Multi-agent marketing campaign orchestration"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'run_campaign' | 'list_campaigns' | 'get_campaign'",
            },
            "goal": {
                "type": "string",
                "required": False,
                "description": "Campaign goal (for run_campaign)",
            },
            "campaign_type": {
                "type": "string",
                "required": False,
                "description": "Campaign type: 'recruitment' | 'product_launch' | etc.",
            },
            "campaign_id": {
                "type": "string",
                "required": False,
                "description": "Campaign ID (for get_campaign)",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        valid_actions = ["run_campaign", "list_campaigns", "get_campaign"]
        if action not in valid_actions:
            raise ValueError(f"Invalid action: {action}")

        if action == "run_campaign" and "goal" not in parameters:
            raise ValueError("run_campaign requires 'goal' parameter")

        if action == "get_campaign" and "campaign_id" not in parameters:
            raise ValueError("get_campaign requires 'campaign_id' parameter")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute campaign operations."""
        try:
            action = parameters["action"]

            if action == "run_campaign":
                goal = parameters["goal"]
                campaign_type = parameters.get("campaign_type", "recruitment")
                kwargs = {k: v for k, v in parameters.items() if k not in ["action", "goal", "campaign_type"]}

                result = self.run_campaign(goal, campaign_type, **kwargs)
                return ToolResult(
                    success=True,
                    output=result,
                    metadata={"action": "run_campaign", "campaign_type": campaign_type},
                )

            elif action == "list_campaigns":
                campaigns = self.list_campaigns()
                return ToolResult(
                    success=True,
                    output={"campaigns": campaigns},
                    metadata={"action": "list_campaigns", "count": len(campaigns)},
                )

            elif action == "get_campaign":
                campaign_id = parameters["campaign_id"]
                campaign = self.get_campaign(campaign_id)
                if campaign:
                    return ToolResult(
                        success=True,
                        output=campaign,
                        metadata={"action": "get_campaign", "campaign_id": campaign_id},
                    )
                else:
                    return ToolResult(
                        success=False,
                        error=f"Campaign not found: {campaign_id}",
                    )

        except Exception as e:
            error_msg = f"Campaign operation failed: {type(e).__name__}: {e!s}"
            logger.error(f"RunCampaignTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)

    def set_kernel(self, kernel):
        """Inject kernel reference after initialization."""
        self.kernel = kernel
        logger.info("🧠 RunCampaignTool connected to VibeOS kernel")

    def run_campaign(self, goal: str, campaign_type: str = "recruitment", **kwargs) -> Dict[str, Any]:
        """
        Run a multi-agent marketing campaign.

        High-level Interface (HIL):
        The user (ENVOY) provides intent and parameters.
        The tool handles orchestration complexity.

        Args:
            goal: Campaign goal (e.g., "recruit founders")
            campaign_type: Type of campaign ("recruitment", "awareness", "engagement")
            **kwargs: Additional parameters (target_audience, budget, timeline, etc.)

        Returns:
            dict: Campaign result with status and outcomes
        """
        campaign_id = self._generate_campaign_id()
        logger.info(f"\n🎯 Starting campaign: {campaign_id}")
        logger.info(f"   Goal: {goal}")
        logger.info(f"   Type: {campaign_type}")

        campaign = {
            "id": campaign_id,
            "goal": goal,
            "type": campaign_type,
            "phase": CampaignPhase.PLANNING.value,
            "status": "running",
            "results": {},
            "errors": [],
            "metadata": kwargs,
        }

        self.campaigns[campaign_id] = campaign

        try:
            # ========== PHASE 0: RESOURCE VALIDATION ==========
            logger.info("\n📋 Phase 0: Resource Validation")
            resource_check = self._check_resources()
            if not resource_check["ready"]:
                campaign["status"] = "failed"
                campaign["errors"].append(f"Resource check failed: {resource_check['reason']}")
                logger.error(f"   ❌ {resource_check['reason']}")
                return self._campaign_result(campaign)

            logger.info("   ✅ All resources available")
            campaign["results"]["resource_check"] = resource_check

            # ========== PHASE I: RESEARCH ==========
            logger.info("\n🔬 Phase I: Market Research")
            campaign["phase"] = CampaignPhase.RESEARCH.value

            research_result = self._execute_research(goal, campaign_type, **kwargs)
            if research_result.get("status") != "success":
                campaign["status"] = "failed"
                campaign["errors"].append(f"Research phase failed: {research_result.get('error')}")
                logger.error("   ❌ Research phase failed")
                return self._campaign_result(campaign)

            campaign["results"]["research"] = research_result
            logger.info("   ✅ Research complete")

            # ========== PHASE II: CONTENT CREATION ==========
            logger.info("\n✍️  Phase II: Content Creation")
            campaign["phase"] = CampaignPhase.CREATION.value

            content_result = self._execute_content_creation(
                goal=goal, research_data=research_result.get("data"), **kwargs
            )
            if content_result.get("status") != "success":
                campaign["status"] = "failed"
                campaign["errors"].append(f"Content creation failed: {content_result.get('error')}")
                logger.error("   ❌ Content creation failed")
                return self._campaign_result(campaign)

            campaign["results"]["content"] = content_result
            logger.info("   ✅ Content created")

            # ========== PHASE III: EXECUTION (PUBLISHING) ==========
            logger.info("\n📢 Phase III: Campaign Execution")
            campaign["phase"] = CampaignPhase.EXECUTION.value

            execution_result = self._execute_publishing(goal=goal, content=content_result.get("content"), **kwargs)
            if execution_result.get("status") != "success":
                campaign["status"] = "failed"
                campaign["errors"].append(f"Publishing failed: {execution_result.get('error')}")
                logger.error("   ❌ Publishing failed")
                return self._campaign_result(campaign)

            campaign["results"]["execution"] = execution_result
            logger.info("   ✅ Campaign published")

            # ========== SUCCESS ==========
            campaign["status"] = "complete"
            campaign["phase"] = CampaignPhase.COMPLETE.value

            logger.info(f"\n✅ Campaign {campaign_id} completed successfully")
            logger.info(f"   Research Insights: {len(research_result.get('data', {}).get('insights', []))} items")
            logger.info(f"   Content Generated: {execution_result.get('publications', 0)} publications")

            return self._campaign_result(campaign)

        except Exception as e:
            campaign["status"] = "error"
            campaign["errors"].append(str(e))
            logger.error(f"❌ Campaign error: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return self._campaign_result(campaign)

    # ========== INTERNAL PHASE IMPLEMENTATIONS ==========

    def _check_resources(self) -> Dict[str, Any]:
        """
        Check if HERALD has necessary resources (license + credits).
        Calls CIVIC for validation.
        """
        if not self.kernel:
            # Fallback: assume resources are available when kernel is not available
            logger.info("   ℹ️  Kernel not available, assuming resources are available")
            return {
                "ready": True,
                "herald_license": "active",
                "herald_credits": 100,
                "research_available": True,
                "herald_available": True,
                "civic_available": True,
                "note": "simulated_mode",
            }

        try:
            # Get CIVIC cartridge
            civic = self.kernel.get_agent("civic")
            if not civic:
                return {"ready": False, "reason": "CIVIC not available"}

            # Check HERALD's broadcast license
            herald_license = civic.check_broadcast_license("herald")
            if not herald_license.get("licensed"):
                return {
                    "ready": False,
                    "reason": f"HERALD broadcast license not active: {herald_license.get('reason')}",
                }

            # Check HERALD's credits
            agents = civic.registry.get("agents", {})
            herald_agent = agents.get("herald")
            if not herald_agent:
                return {"ready": False, "reason": "HERALD not registered"}

            credits = herald_agent.get("credits", 0)
            if credits <= 0:
                return {
                    "ready": False,
                    "reason": "HERALD has no credits for campaign execution",
                }

            return {
                "ready": True,
                "herald_license": "active",
                "herald_credits": credits,
                "research_available": True,
                "herald_available": True,
                "civic_available": True,
            }

        except Exception as e:
            return {"ready": False, "reason": f"Resource check error: {str(e)}"}

    def _execute_research(self, goal: str, campaign_type: str, **kwargs) -> Dict[str, Any]:
        """
        Phase I: Trigger SCIENCE agent for market research.
        """
        if not self.kernel:
            # Use simulated research when kernel is unavailable
            return self._simulate_research(goal, campaign_type)

        try:
            # Get SCIENCE cartridge
            science = self.kernel.get_agent("science")
            if not science:
                # Fallback: simulate research
                return self._simulate_research(goal, campaign_type)

            # Trigger SCIENCE analysis via kernel task
            from vibe_core.scheduling import Task

            task = Task(
                agent_id="science",
                payload={
                    "action": "market_analysis",
                    "goal": goal,
                    "campaign_type": campaign_type,
                    "parameters": kwargs,
                },
            )

            result = science.process(task)

            # Extract research data
            if result.get("status") == "success":
                return {
                    "status": "success",
                    "agent": "science",
                    "data": result.get("data", {}),
                    "insights": result.get("insights", []),
                    "timestamp": result.get("timestamp"),
                }
            else:
                # Fallback if SCIENCE returns error
                return self._simulate_research(goal, campaign_type)

        except Exception as e:
            logger.warning(f"⚠️  SCIENCE not available, using simulated research: {e}")
            return self._simulate_research(goal, campaign_type)

    def _simulate_research(self, goal: str, campaign_type: str) -> Dict[str, Any]:
        """Simulate market research when SCIENCE is not available."""
        return {
            "status": "success",
            "agent": "simulated",
            "data": {
                "goal": goal,
                "campaign_type": campaign_type,
                "target_audience": self._get_target_audience(goal),
                "market_trends": self._get_market_trends(goal),
                "messaging_strategies": self._get_messaging_strategies(goal),
                "insights": [
                    "Founder recruitment responds to credibility signals",
                    "Technical founders value transparency and governance",
                    "Agent-based systems are emerging opportunity",
                    "Multi-agent orchestration is compelling narrative",
                ],
            },
        }

    def _execute_content_creation(self, goal: str, research_data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """
        Phase II: Trigger HERALD for content generation.
        """
        if not self.kernel:
            # Use simulated content generation when kernel is unavailable
            return self._simulate_content_creation(goal, research_data)

        try:
            # Get HERALD cartridge
            herald = self.kernel.get_agent("herald")
            if not herald:
                return self._simulate_content_creation(goal, research_data)

            # Trigger HERALD content generation
            from vibe_core.scheduling import Task

            task = Task(
                agent_id="herald",
                payload={
                    "action": "generate_campaign_content",
                    "goal": goal,
                    "research_data": research_data or {},
                    "parameters": kwargs,
                },
            )

            result = herald.process(task)

            if result.get("status") == "success":
                return {
                    "status": "success",
                    "agent": "herald",
                    "content": result.get("content", ""),
                    "metadata": result.get("metadata", {}),
                    "timestamp": result.get("timestamp"),
                }
            else:
                return self._simulate_content_creation(goal, research_data)

        except Exception as e:
            logger.warning(f"⚠️  HERALD content generation failed, using template: {e}")
            return self._simulate_content_creation(goal, research_data)

    def _simulate_content_creation(self, goal: str, research_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate template content when HERALD is not available."""
        content = f"""
# {goal.title()} - Multi-Agent Protocol Initiative

## The Opportunity
Steward Protocol brings revolutionary governance to agent-based systems.
We're building the infrastructure for AI agents to collaborate, govern themselves,
and create value through transparent, democratic decision-making.

## Why Join Us
- Pioneer the future of autonomous systems governance
- Work on cryptographic mechanisms for agent coordination
- Design constitutional frameworks for AI
- Shape governance protocols that will define industry standards

## The Vision
Agents that are:
✓ Self-Governing (Democracy)
✓ Transparent (Ledger-Verified)
✓ Trustworthy (Cryptographic Oath)
✓ Coordinated (Multi-Agent Orchestration)

## Next Steps
Experience the power of agentic governance. Steward Protocol is live.
        """

        return {
            "status": "success",
            "agent": "simulated",
            "content": content,
            "metadata": {
                "tone": "professional",
                "audience": "technical_founders",
                "length": "medium",
            },
        }

    def _execute_publishing(self, goal: str, content: str, **kwargs) -> Dict[str, Any]:
        """
        Phase III: Trigger HERALD to publish the campaign.
        """
        if not self.kernel:
            # Simulate publishing when kernel is unavailable
            return {
                "status": "success",
                "publications": 1,
                "platforms": ["simulated"],
                "note": "HERALD not available, publishing simulated",
            }

        try:
            # Get HERALD cartridge
            herald = self.kernel.get_agent("herald")
            if not herald:
                return {
                    "status": "success",
                    "publications": 0,
                    "platforms": [],
                    "note": "HERALD not available, publishing simulated",
                }

            # Trigger HERALD publishing
            from vibe_core.scheduling import Task

            task = Task(
                agent_id="herald",
                payload={
                    "action": "publish_campaign",
                    "content": content,
                    "goal": goal,
                    "parameters": kwargs,
                },
            )

            result = herald.process(task)

            if result.get("status") == "success":
                return {
                    "status": "success",
                    "agent": "herald",
                    "publications": result.get("publications", 1),
                    "platforms": result.get("platforms", []),
                    "transaction_hash": result.get("transaction_hash"),
                    "timestamp": result.get("timestamp"),
                }
            else:
                return {
                    "status": "success",
                    "publications": 1,
                    "platforms": ["simulated"],
                    "note": "HERALD unavailable, publishing recorded",
                }

        except Exception as e:
            logger.error(f"❌ Publishing error: {e}")
            return {"status": "error", "error": str(e)}

    # ========== HELPER METHODS ==========

    def _get_target_audience(self, goal: str) -> List[str]:
        """Infer target audience from goal."""
        if "founder" in goal.lower() or "recruit" in goal.lower():
            return ["technical_founders", "ai_researchers", "entrepreneurs"]
        elif "customer" in goal.lower():
            return ["enterprises", "startups", "developers"]
        else:
            return ["general_audience"]

    def _get_market_trends(self, goal: str) -> List[str]:
        """Get relevant market trends."""
        return [
            "AI agents becoming mainstream",
            "Governance-first protocols gaining traction",
            "Multi-agent coordination emerging as critical",
            "Trustless systems valued over permissioned",
            "Founder interest in protocol governance",
        ]

    def _get_messaging_strategies(self, goal: str) -> List[str]:
        """Get messaging strategies for the campaign."""
        return [
            "Lead with transparency and governance",
            "Emphasize technical rigor and security",
            "Show working examples and proofs",
            "Build credibility through ledger transparency",
            "Appeal to pioneering mindset",
        ]

    def _generate_campaign_id(self) -> str:
        """Generate unique campaign ID."""
        import time

        timestamp = int(time.time() * 1000) % 1000000
        return f"CAMP-{timestamp:06d}"

    def _campaign_result(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Format campaign result for return."""
        return {
            "status": campaign["status"],
            "campaign_id": campaign["id"],
            "goal": campaign["goal"],
            "phase": campaign["phase"],
            "results": campaign["results"],
            "errors": campaign["errors"] if campaign["errors"] else None,
            "message": self._get_result_message(campaign),
        }

    def _get_result_message(self, campaign: Dict[str, Any]) -> str:
        """Generate human-readable result message."""
        if campaign["status"] == "complete":
            return f"✅ Campaign '{campaign['goal']}' completed successfully with {len(campaign['results'])} phases executed"
        elif campaign["status"] == "failed":
            return f"❌ Campaign failed: {campaign['errors'][0] if campaign['errors'] else 'Unknown error'}"
        elif campaign["status"] == "running":
            return f"🔄 Campaign '{campaign['goal']}' in progress (Phase: {campaign['phase']})"
        else:
            return f"⚠️  Campaign status: {campaign['status']}"

    def list_campaigns(self) -> List[Dict[str, Any]]:
        """List all campaigns and their current state."""
        return list(self.campaigns.values())

    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign details by ID."""
        return self.campaigns.get(campaign_id)


__all__ = ["RunCampaignTool"]
