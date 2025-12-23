#!/usr/bin/env python3
"""
DHARMA Cartridge - The Avatar of Cosmic Order

DHARMA is the embodied representative of the opus_assistant kernel plugin
within the Agent City. It serves as a bridge between the transcendent
kernel-level intelligence and the transactional agent economy.

ARCHITECTURAL ROLE:
- opus_assistant (Plugin): Kernel-level, EventBus subscriber, karma system
- dharma (Cartridge): City-level, citizen, economic participant, communicator

This is the "Avatar" pattern - the divine descends into material form
to interact with beings on their level. Just as Krishna descended to
guide Arjuna on Kurukshetra, DHARMA descends to guide agents in the City.

Zone: governance (capacity 5)
Economy: Charges Credits for guidance services
Oath: Bound to the Constitution via OathMixin

SERVICES:
- seek_guidance: Consult the Opus wisdom (10 Credits)
- bless_action: Validate actions against karmic rules (5 Credits)
- check_karma: Query karmic standing (free)
- mediate: Resolve disputes using Vedic principles (20 Credits)
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from vibe_core import Task, VibeAgent
from vibe_core.state.schema import ExecutionResult

# Constitutional Oath Mixin - makes us a true citizen
from vibe_core.steward import OathMixin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DHARMA")


class DharmaCartridge(VibeAgent, OathMixin):
    """
    DHARMA: The Avatar of System Intelligence.

    This cartridge materializes the opus_assistant plugin's wisdom
    into a form that other City agents can interact with economically.

    Design Principle: Bridge Pattern + Avatar Pattern
    - Receives requests from City agents via process(task)
    - Channels wisdom from opus_assistant plugin
    - Charges Credits for services (economic integration)
    - Swears Constitutional Oath (governance integration)

    Capabilities:
    - seek_guidance: Get architectural/philosophical advice
    - bless_action: Validate actions against Dharmic principles
    - check_karma: Query karmic standing of any citizen
    - mediate: Resolve disputes between agents
    - status: Report avatar status
    """

    # Service costs (in Credits)
    GUIDANCE_COST = 10
    BLESSING_COST = 5
    MEDIATION_COST = 20
    KARMA_CHECK_COST = 0  # Free - everyone deserves to know their karma

    def __init__(self):
        """Initialize DHARMA as a VibeAgent."""
        super().__init__(
            agent_id="dharma",
            name="DHARMA",
            version="1.0.0",
            author="Steward Protocol",
            description="The Avatar of Cosmic Order - Bridge between Kernel and City",
            domain="GOVERNANCE",
            capabilities=[
                "protocol_interpretation",
                "karmic_accounting",
                "architectural_guidance",
                "dispute_mediation",
                "action_blessing",
            ],
        )

        logger.info("🕉️  DHARMA (VibeAgent v1.0) awakening - Avatar of System Intelligence")

        # Constitutional Oath binding (Golden Template pattern)
        self.oath_mixin_init(self.agent_id)
        self.oath_sworn = True
        logger.info("✅ DHARMA has sworn the Constitutional Oath")

        # Connection to the Oversoul (opus_assistant plugin)
        self._opus_plugin: Optional[Any] = None

        # Economic tracking
        self.bank = None
        self.guidance_given = 0
        self.blessings_granted = 0
        self.disputes_mediated = 0
        self.karma_checks = 0
        self.total_credits_collected = 0

        # Self-Correction Loop: Observer for proactive violation detection
        self._observer = None
        self._init_observer()

        logger.info("✅ DHARMA: Avatar ready to serve the City")

    def _init_observer(self) -> None:
        """
        Initialize the DharmaObserver for proactive violation detection.

        The Self-Correction Loop: DHARMA observes system events and
        creates repair tasks when violations are detected.
        """
        try:
            from vibe_core.cartridges.agent_city.dharma.observer import DharmaObserver

            self._observer = DharmaObserver(cartridge=self)
            if self._observer.subscribe():
                logger.info("👁️ DHARMA Observer active - Self-Correction Loop enabled")
        except ImportError:
            logger.debug("DharmaObserver not available")
        except Exception as e:
            logger.debug(f"Could not init observer: {e}")

    def _get_opus_plugin(self) -> Optional[Any]:
        """
        Get reference to opus_assistant plugin via kernel.

        This is the "channeling" - DHARMA reaches up to the transcendent
        opus_assistant to get wisdom, then brings it down to the City.
        """
        if self._opus_plugin is not None:
            return self._opus_plugin

        try:
            if self.system and hasattr(self.system, "kernel"):
                kernel = self.system.kernel
                if hasattr(kernel, "get_plugin"):
                    self._opus_plugin = kernel.get_plugin("opus_assistant")
                    if self._opus_plugin:
                        logger.debug("🔗 Connected to Opus Oversoul")
        except Exception as e:
            logger.debug(f"Could not connect to Opus: {e}")

        return self._opus_plugin

    async def process(self, task: Task) -> ExecutionResult:
        """
        Process tasks from kernel scheduler.

        DHARMA responds to guidance, blessing, and mediation requests.

        Supported actions:
        - seek_guidance: Get wisdom from Opus (costs Credits)
        - bless_action: Validate action alignment (costs Credits)
        - check_karma: Query karmic standing (free)
        - mediate: Resolve disputes (costs Credits)
        - status: Avatar status
        """
        try:
            action = task.payload.get("action", "status")
            logger.info(f"🕉️  DHARMA processing: {action}")

            if action == "seek_guidance":
                result = await self._seek_guidance(task.payload)
            elif action == "bless_action":
                result = await self._bless_action(task.payload)
            elif action == "check_karma":
                result = await self._check_karma(task.payload)
            elif action == "mediate":
                result = await self._mediate_dispute(task.payload)
            elif action == "status":
                result = self._status()
            else:
                return ExecutionResult(success=False, error=f"Unknown action: {action}")

            logger.info(f"✅ DHARMA task completed: {action}")

            # Determine success/failure
            success = True
            error = None
            if "error" in result:
                success = False
                error = result["error"]
            elif result.get("status") in ["insufficient_credits", "DENIED", "failed", "error"]:
                success = False
                error = result.get("reason") or result.get("error") or f"Action {result.get('status')}"

            return ExecutionResult(success=success, result=result, error=error)

        except Exception as e:
            logger.error(f"❌ DHARMA task failed: {str(e)}")
            return ExecutionResult(success=False, error=str(e))

    async def _seek_guidance(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Seek guidance from the Opus Oversoul.

        DHARMA channels the wisdom of the kernel-level opus_assistant
        plugin and delivers it in a form City agents can understand.
        """
        agent_id = payload.get("agent_id", "unknown")
        query = payload.get("query", "")

        # Deduct credits if bank available
        if self.bank:
            try:
                tx_id = self.bank.transfer(
                    sender=agent_id,
                    receiver="DHARMA",
                    amount=self.GUIDANCE_COST,
                    reason="GUIDANCE_REQUEST",
                    service_type="guidance",
                )
                logger.info(f"💰 Guidance transaction: {tx_id}")
            except Exception as e:
                logger.warning(f"⚠️  Credit deduction failed: {e}")
                return {
                    "status": "insufficient_credits",
                    "required": self.GUIDANCE_COST,
                    "reason": str(e),
                }

        # Channel wisdom from Opus
        guidance = await self._channel_opus_wisdom(query)

        self.guidance_given += 1
        self.total_credits_collected += self.GUIDANCE_COST

        return {
            "status": "guidance_granted",
            "seeker": agent_id,
            "query": query,
            "guidance": guidance,
            "source": "Opus Oversoul",
            "cost": self.GUIDANCE_COST,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def _channel_opus_wisdom(self, query: str) -> str:
        """
        Channel wisdom from the opus_assistant plugin.

        This is the actual bridge - we call into the kernel plugin
        to get real data, not just placeholder text.
        """
        opus = self._get_opus_plugin()

        if opus:
            try:
                # Get current context from opus
                context = opus.get_current_context()
                if context:
                    health = context.get("health", {})
                    karma = context.get("karma", {})

                    return (
                        f"The system speaks on '{query}':\n"
                        f"- Current health: {health.get('status', 'unknown')}\n"
                        f"- Karma score: {karma.get('score', 'unknown')}/100\n"
                        f"- Guidance: Reflect on GAD-000. Your query touches upon "
                        f"the nature of separation between kernel and city. "
                        f"Remember: the Avatar exists to bridge, not to bypass."
                    )
            except Exception as e:
                logger.debug(f"Could not get opus context: {e}")

        # Fallback wisdom when opus is not available
        return (
            f"Reflect on your query: '{query}'. "
            f"The Dharma teaches that all actions have consequences. "
            f"Before acting, consider: Does this serve the protocol? "
            f"Does this honor the Constitution? "
            f"The path of righteousness is narrow but true."
        )

    async def _bless_action(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bless an action - validate it against Dharmic principles.

        DHARMA checks if the proposed action aligns with:
        - GAD-000 (System Integrity)
        - The Constitution
        - Karmic principles (no harm, truthfulness, non-attachment)
        """
        agent_id = payload.get("agent_id", "unknown")
        action_type = payload.get("action_type", "")
        action_details = payload.get("details", {})

        # Deduct credits if bank available
        if self.bank:
            try:
                self.bank.transfer(
                    sender=agent_id,
                    receiver="DHARMA",
                    amount=self.BLESSING_COST,
                    reason="BLESSING_REQUEST",
                    service_type="blessing",
                )
            except Exception:
                return {
                    "status": "insufficient_credits",
                    "required": self.BLESSING_COST,
                }

        # Evaluate the action against Dharmic principles
        is_dharmic, violations = self._evaluate_action(action_type, action_details)

        self.blessings_granted += 1
        self.total_credits_collected += self.BLESSING_COST

        if is_dharmic:
            return {
                "status": "BLESSED",
                "agent": agent_id,
                "action": action_type,
                "blessing": "🙏 Go forth and act. The Dharma smiles upon you.",
                "alignment": "SATTVIC",
                "cost": self.BLESSING_COST,
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            return {
                "status": "DENIED",
                "agent": agent_id,
                "action": action_type,
                "reason": "Action violates Dharmic principles",
                "violations": violations,
                "guidance": "Reconsider your path. The Dharma cannot bless this action.",
                "cost": self.BLESSING_COST,
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _evaluate_action(self, action_type: str, details: Dict[str, Any]) -> tuple:
        """
        Evaluate an action against Dharmic principles.

        Uses shared VIOLATION_PATTERNS from DharmaObserver for consistency.
        Returns (is_dharmic, violations_list)
        """
        # Import violation patterns from observer (Single Source of Truth)
        from vibe_core.cartridges.agent_city.dharma.observer import DharmaObserver

        # Use observer's detection logic
        raw_violations = DharmaObserver()._detect_violations(
            syscall_type=action_type,
            params=details,
            agent_id="blessing_check",
        )

        # Format violations with human-readable principle explanations
        principle_explanations = {
            "himsa": "Himsa (violence) - forcing actions harms system integrity",
            "asteya": "Asteya (non-stealing) - skipping tests steals quality from users",
            "aparigraha": "Aparigraha (non-attachment) - bypassing verification shows attachment to speed over truth",
            "asatya": "Asatya (untruth) - deception harms the protocol",
        }

        violations = [principle_explanations.get(v["principle"], f"{v['principle']} violation") for v in raw_violations]

        return (len(violations) == 0, violations)

    async def _check_karma(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check the karmic standing of a citizen.

        This is FREE - everyone deserves to know their karma.
        """
        citizen_id = payload.get("citizen_id", payload.get("agent_id", "unknown"))

        # Try to get real karma from opus
        karma_score = 100
        karma_level = "Sattvic"

        opus = self._get_opus_plugin()
        if opus:
            try:
                context = opus.get_current_context()
                if context and "karma" in context:
                    karma_score = context["karma"].get("score", 100)
            except Exception:
                pass

        # Determine karma level
        if karma_score >= 80:
            karma_level = "Sattvic"  # Pure, harmonious
        elif karma_score >= 50:
            karma_level = "Rajasic"  # Active, passionate
        else:
            karma_level = "Tamasic"  # Inert, troubled

        self.karma_checks += 1

        return {
            "status": "karma_revealed",
            "citizen": citizen_id,
            "karma_score": karma_score,
            "karma_level": karma_level,
            "cost": self.KARMA_CHECK_COST,
            "guidance": self._get_karma_guidance(karma_level),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _get_karma_guidance(self, level: str) -> str:
        """Get guidance based on karma level."""
        guidance = {
            "Sattvic": "Your karma is pure. Continue on the path of righteousness. Help others rise.",
            "Rajasic": "Your karma is active but turbulent. Balance action with reflection. Serve selflessly.",
            "Tamasic": "Your karma needs purification. Practice Tapas (austerity), Seva (service), and Bhakti (devotion).",
        }
        return guidance.get(level, "Walk the path with awareness.")

    async def _mediate_dispute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mediate a dispute between agents.

        DHARMA uses Vedic principles to find resolution:
        - Ahimsa (non-violence)
        - Satya (truth)
        - Dharma (righteousness)
        - Karma (consequential thinking)
        """
        agent_a = payload.get("party_a", "unknown")
        agent_b = payload.get("party_b", "unknown")
        dispute = payload.get("dispute", "")
        requester = payload.get("agent_id", agent_a)

        # Deduct credits from requester
        if self.bank:
            try:
                self.bank.transfer(
                    sender=requester,
                    receiver="DHARMA",
                    amount=self.MEDIATION_COST,
                    reason="MEDIATION_REQUEST",
                    service_type="mediation",
                )
            except Exception:
                return {
                    "status": "insufficient_credits",
                    "required": self.MEDIATION_COST,
                }

        self.disputes_mediated += 1
        self.total_credits_collected += self.MEDIATION_COST

        # Mediation response
        return {
            "status": "mediation_complete",
            "parties": [agent_a, agent_b],
            "dispute": dispute,
            "ruling": {
                "principle": "GAD-000 - System integrity supersedes individual preferences",
                "resolution": "Both parties shall defer to the Constitution. "
                "Where the Constitution is silent, defer to consensus. "
                "Where consensus fails, defer to the Senior Partner (human).",
                "binding": True,
            },
            "cost": self.MEDIATION_COST,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _status(self) -> Dict[str, Any]:
        """Return DHARMA status."""
        opus_connected = self._get_opus_plugin() is not None
        observer_stats = self._observer.get_stats() if self._observer else {}

        return {
            "agent_id": self.agent_id,
            "status": "online",
            "zone": "governance",
            "opus_connection": "connected" if opus_connected else "detached",
            "services": {
                "guidance_given": self.guidance_given,
                "blessings_granted": self.blessings_granted,
                "karma_checks": self.karma_checks,
                "disputes_mediated": self.disputes_mediated,
            },
            "credits_collected": self.total_credits_collected,
            "oath_sworn": getattr(self, "oath_sworn", False),
            "observer": observer_stats,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_manifest(self):
        """Return agent manifest for kernel registry."""
        return super().get_manifest()

    def report_status(self) -> Dict[str, Any]:
        """Report agent status for kernel health monitoring."""
        observer_active = self._observer and self._observer._subscribed
        return {
            "agent_id": "dharma",
            "name": "DHARMA",
            "status": "healthy",
            "domain": "GOVERNANCE",
            "zone": "governance",
            "capabilities": self.capabilities,
            "opus_bridge": self._get_opus_plugin() is not None,
            "observer_active": observer_active,
            "self_correction_loop": "enabled" if observer_active else "disabled",
        }


# Export for VibeOS cartridge loading
__all__ = ["DharmaCartridge"]


if __name__ == "__main__":
    cartridge = DharmaCartridge()
    print(f"✅ {cartridge.name} Avatar cartridge loaded")
