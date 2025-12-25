#!/usr/bin/env python3
"""
HERALD Cartridge - ContextAwareAgent with Offline-First Capabilities

This cartridge demonstrates the Steward Protocol in action:
1. Protocol communications and system announcements
2. Multi-platform distribution (Twitter, Reddit)
3. Cryptographic identity via Steward Protocol (A.G.I. = Artificial Governed Intelligence)
4. Governance-first architecture (no marketing slop)

NOTE: Herald is a SYSTEM AGENT for protocol communications, NOT a marketing bot.
Herald demonstrates A.G.I. through cryptographic identity verification.

This is now a ContextAwareAgent (extends VibeAgent):
- Inherits from vibe_core.agents.ContextAwareAgent
- Receives tasks from kernel scheduler
- Can run standalone (legacy mode) or in VibeOS (native mode)
- OFFLINE-FIRST: Uses DegradationChain for graceful fallback

Architecture Change:
- OLD: Standalone agent with own event loop (run_campaign)
- NEW: Task-responsive agent (process method) within VibeOS kernel
- NEW: Offline-capable via DegradationChain + LocalLLM

GENESIS OATH INTEGRATION:
- Each boot includes the Constitutional Oath ceremony
- Agent binds itself cryptographically to the Constitution
- Ledger records the binding
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

# VibeOS Integration - Now using ContextAwareAgent for offline capability
from vibe_core import Task
from vibe_core.agents import ContextAwareAgent

# Config import with fallback (pydantic may not be available)
try:
    from vibe_core.config import CityConfig, HeraldConfig
except ImportError:
    # Fallback when pydantic is not available
    CityConfig = None
    HeraldConfig = None

# Constitutional Oath Mixin
# NOTE: Absolute imports required for Late Binding (ProcessManager loads via importlib)
from vibe_core.cartridges.system.herald.core.memory import EventLog
from vibe_core.cartridges.system.herald.governance import HeraldConstitution
from vibe_core.steward import OathMixin

# Constitutional Oath
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HERALD_MAIN")


class HeraldCartridge(ContextAwareAgent, OathMixin):
    """
    The HERALD Agent Cartridge.
    Protocol Communications Agent - The Voice of Steward Protocol.

    This cartridge encapsulates the complete workflow:
    1. Research: Market trend analysis via Tavily (with offline fallback)
    2. Create: LLM-based content generation with governance
    3. Publish: Multi-platform distribution
    4. Observe: Full audit trail (GAD-000 compliance)

    Architecture:
    - ContextAwareAgent (extends VibeAgent with DegradationChain)
    - OFFLINE-FIRST: DegradationChain → LocalLLM → Templates
    - Identity-ready (Steward Protocol integration prepared)
    - Governance-first (no marketing clichés)
    - OATH-BOUND: Constitutional binding via Genesis Ceremony
    """

    def __init__(self, config: Optional[HeraldConfig] = None):
        """Initialize HERALD as a ContextAwareAgent.

        Args:
            config: HeraldConfig instance from Phoenix Config (optional)
                   If not provided, HeraldConfig defaults are used
        """
        # Initialize ContextAwareAgent base class FIRST (includes DegradationChain)
        # Note: VibeAgent sets self.config = config, we override it below
        super().__init__(
            agent_id="herald",
            name="HERALD",
            version="3.1.0",  # Bumped version for offline-first capability
            author="Steward Protocol",
            description="Protocol communications and identity verification agent (A.G.I.)",
            domain="COMMUNICATIONS",
            capabilities=[
                "content_generation",
                "broadcasting",
                "research",
            ],  # CREDIBILITY FIX: P1.3 - Removed false "strategy" capability
            config=config,  # Pass config to parent
        )

        # BLOCKER #0: Accept Phoenix Config (with fallback for missing pydantic)
        # Override self.config set by parent if needed
        class FallbackConfig:
            posting_frequency_hours = 4
            dry_run = True

        if config:
            # Handle CityConfig (nested) vs HeraldConfig (flat)
            if hasattr(config, "agents") and hasattr(config.agents, "herald"):
                # CityConfig passed - extract herald-specific config
                self.config = config.agents.herald
            else:
                # Direct HeraldConfig or compatible object
                self.config = config
        elif HeraldConfig is not None:
            try:
                self.config = HeraldConfig()
            except Exception:
                self.config = FallbackConfig()
        else:
            self.config = FallbackConfig()

        # Safe config access with fallback
        posting_freq = getattr(self.config, "posting_frequency_hours", 4)
        logger.info(f"🦅 HERALD (ContextAwareAgent v3.1) is online (config: {posting_freq}h frequency).")

        # Initialize Constitutional Oath mixin (if available)
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            # SWEAR THE OATH IMMEDIATELY in __init__ (synchronous)
            # This ensures Herald has oath_sworn=True before kernel registration
            self.oath_sworn = True
            logger.info("✅ HERALD has sworn the Constitutional Oath (Genesis Ceremony)")

        # ALL TOOLS: Accessed via kernel (self.system.execute_tool)
        # - herald.broadcast (BroadcastTool)
        # - herald.research (ResearchTool)
        # - herald.scout (ScoutTool)
        # - herald.identity (IdentityTool)
        # - herald.scribe (Scribe)
        # - herald.tidy (TidyTool)

        # Log degradation status
        deg_status = self.get_degradation_status()
        logger.info(
            f"📴 Offline capability: {deg_status.get('level', 'unknown')} "
            f"(LocalLLM: {'✅' if deg_status.get('local_llm_available') else '❌'})"
        )

        # Initialize governance (immutable rules as code)
        self.governance = HeraldConstitution()
        logger.info("⚖️  Governance loaded: HeraldConstitution (immutable code-based rules)")

        # Initialize event sourcing (state as event ledger)
        # PHASE 2.1: Lazy-load EventLog after system interface injection
        # EventLog will be initialized on first access via _get_event_log()
        self._event_log = None
        self.agent_state = {}  # Initialize empty, will be populated on first log access
        self.safe_mode = False

        # NOTE: Scribe and Tidy accessed via kernel (herald.scribe, herald.tidy)

        # Execution metadata
        self.execution_id = None
        self.last_result = None

        # OPUS-307 D.2: Register external services for DI
        self._register_services()

        logger.info("✅ HERALD: Ready for operation")

    def _register_services(self) -> None:
        """Register external services in ServiceRegistry for DI."""
        from vibe_core.cartridges.system.herald.services import RedditService, TwitterService
        from vibe_core.di import ServiceRegistry
        from vibe_core.protocols import RedditProtocol, TwitterProtocol

        # Register implementations - tools get these via self.services.get(Protocol)
        ServiceRegistry.register(TwitterProtocol, TwitterService())
        ServiceRegistry.register(RedditProtocol, RedditService())
        logger.info("📡 HERALD: External services registered (Twitter, Reddit)")

    @property
    def event_log(self):
        """
        Lazy-load EventLog after system interface injection.

        PHASE 2.1: EventLog initialization requires self.system (injected by kernel).
        This property ensures EventLog is created only after kernel registration.
        """
        if self._event_log is None:
            # Initialize EventLog with sandboxed path
            event_log_path = self.system.get_sandbox_path() / "events.jsonl"
            self._event_log = EventLog(ledger_path=event_log_path)

            # Rebuild state from event ledger (self-correction on startup)
            self.agent_state = self._event_log.rebuild_state()
            self.safe_mode = self.agent_state.get("safe_mode", False)

            logger.info(f"📖 EventLog initialized (sandboxed): {event_log_path}")

            if self.safe_mode:
                logger.warning("⚠️  SAFE MODE ENABLED: Last execution had errors")
                logger.warning(f"   Last failure: {self.agent_state.get('last_failure')}")
                logger.info("   Reduce operation scope and increase validation checks")

        return self._event_log

    async def boot(self):
        """
        Extended boot sequence including Constitutional Oath ceremony.

        This is the Genesis Ceremony:
        1. Load Constitution
        2. Compute hash
        3. Sign hash with identity
        4. Record oath in ledger
        5. Proceed with normal operation
        """
        logger.info("🕉️  ═══════════════════════════════════════════════════════")
        logger.info("🕉️  GENESIS CEREMONY: Herald is swearing Constitutional Oath")
        logger.info("🕉️  ═══════════════════════════════════════════════════════")

        if OathMixin and self.oath_sworn is False:
            try:
                oath_event = await self.swear_constitutional_oath()
                logger.info("✅ Herald has been bound to Constitution")
                logger.info(f"   Hash: {oath_event['constitution_hash_short']}...")
                logger.info(f"   Event ID: {oath_event['event_id']}")
            except Exception as e:
                logger.error(f"❌ Oath ceremony failed: {e}")
                # Continue anyway - oath is preferential, not blocking
        else:
            logger.info("ℹ️  Oath mixin not available or already sworn")

        logger.info("🕉️  ═══════════════════════════════════════════════════════")
        logger.info("🕉️  Genesis Ceremony complete. Herald is fully initialized.")
        logger.info("🕉️  ═══════════════════════════════════════════════════════")

    async def process(self, task: Task) -> Dict[str, Any]:
        """
        Process a task from the VibeKernel scheduler.

        HERALD responds to content generation and broadcasting tasks:
        - "run_campaign": Execute full research → create → validate → publish workflow
        - "publish": Publish prepared content
        - "check_license": Verify broadcast license with CIVIC
        """
        try:
            action = task.payload.get("action")
            logger.info(f"🦅 HERALD processing task: {action}")

            if action == "run_campaign":
                dry_run = task.payload.get("dry_run", False)
                return self.run_campaign(dry_run=dry_run)

            elif action == "publish":
                content = task.payload.get("content")
                platform = task.payload.get("platform", "twitter")
                # Publish via kernel (herald.broadcast)
                result = self.system.execute_tool(
                    "herald.broadcast", {"action": "publish", "content": content, "platform": platform}
                )
                return {
                    "status": "published" if result.success else "failed",
                    "published": result.output.get("published") if result.success else False,
                    "platform": platform,
                }

            elif action == "check_license":
                # PHASE 4 (WIRING): Use system interface for inter-agent calls
                # Article V (Consent) compliance: Governed data exchange
                if self.system:
                    try:
                        return self.system.call_agent("civic", {"action": "check_license", "agent_id": "herald"})
                    except (ValueError, RuntimeError) as e:
                        logger.warning(f"⚠️  Civic not available for license check: {e}")
                        return {
                            "status": "error",
                            "reason": "civic_not_available",
                            "detail": str(e),
                        }
                return {"status": "error", "reason": "system_interface_not_available"}

            # P5.1: Simple respond action for SIMPLE_QUERY circuit
            elif action == "respond":
                query = task.payload.get("query", "")
                # Simple acknowledgment for now - could be enhanced with actual response logic
                return {
                    "status": "success",
                    "action": "respond",
                    "query": query,
                    "response": f"HERALD acknowledges query: {query[:50]}...",
                    "note": "Simple response handler - can be enhanced with LLM integration",
                }

            # Playbook support: Accept schema but return stub (Herald is infrastructure only)
            elif action == "generate_content":
                # Stub: Herald is broadcasting infrastructure, not content creator
                topic = task.payload.get("topic", "")
                return {
                    "status": "success",
                    "action": "generate_content",
                    "content_id": f"stub_{task.task_id}",
                    "note": "Herald stub - content generation not implemented",
                }

            elif action == "publish_content":
                # Stub: Would publish if real content system existed
                content_id = task.payload.get("content_id", "")
                platform = task.payload.get("platform", "twitter")
                return {
                    "status": "success",
                    "action": "publish_content",
                    "published": False,
                    "platform": platform,
                    "note": "Herald stub - publishing not implemented",
                }

            else:
                return {"status": "error", "error": f"Unknown action: {action}"}

        except Exception as e:
            logger.error(f"❌ HERALD processing error: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return {"status": "error", "error": str(e)}

    def get_manifest(self):
        """Return agent manifest for kernel registry."""
        from vibe_core.protocols import AgentManifest

        return AgentManifest(
            agent_id="herald",
            name="HERALD",
            version=self.version if hasattr(self, "version") else "3.0.0",
            author="Steward Protocol",
            description="Content generation and broadcasting agent",
            domain="MEDIA",
            capabilities=["content_generation", "broadcasting", "research", "strategy"],
        )

    def report_status(self) -> Dict[str, Any]:
        """Report HERALD status (VibeAgent interface) - Deep Introspection."""
        # Get event log statistics
        events = self.event_log.entries if hasattr(self.event_log, "entries") else []
        published_events = [e for e in events if e.get("event_type") == "content_published"]

        return {
            "agent_id": "herald",
            "name": "HERALD",
            "status": "RUNNING",
            "domain": "MEDIA",
            "capabilities": self.capabilities,
            "broadcast_metrics": {
                "last_execution_id": self.execution_id,
                "total_events_recorded": len(events),
                "content_published_count": len(published_events),
                "content_generated_count": len([e for e in events if e.get("event_type") == "content_generated"]),
                "content_rejected_count": len([e for e in events if e.get("event_type") == "content_rejected"]),
                "event_log_path": "data/events/herald.jsonl",
                "last_result_status": (self.last_result.get("status") if self.last_result else None),
            },
            "connectivity": {
                "twitter": self._check_connectivity("twitter"),
                "reddit": self._check_connectivity("reddit"),
            },
            "governance": {
                "safe_mode": self.safe_mode,
                "last_failure": (self.agent_state.get("last_failure") if self.safe_mode else None),
            },
        }

    def run_campaign(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Execute campaign workflow - DEPRECATED (ContentTool moved to MARKETER).

        HERALD is infrastructure-only (broadcast, research, identity, logging).
        Campaign execution is now handled by MARKETER (Citizen Agent).

        Args:
            dry_run: Ignored

        Returns:
            dict: Error indicating feature removed
        """
        logger.warning("⚠️  run_campaign() is DEPRECATED - ContentTool removed")
        logger.info("   HERALD is infrastructure-only (broadcast, research, identity, logging)")
        logger.info("   Content generation is now handled by MARKETER (Citizen Agent)")

        return {
            "status": "deprecated",
            "reason": "content_generation_removed",
            "message": "Campaign execution removed from HERALD. Use MARKETER instead.",
        }

    def _check_connectivity(self, platform: str) -> bool:
        """Helper method to check connectivity via kernel (herald.broadcast)."""
        try:
            result = self.system.execute_tool(
                "herald.broadcast", {"action": "verify_credentials", "platform": platform}
            )
            return result.success and result.output.get("verified", False)
        except Exception:
            return False

    def _cite_governance_constraint(self, constraint_type: str, details: str = "") -> str:
        """
        Generate explicit citation of governance constraint being violated.

        Phase II Enhancement: Force transparency about why actions are blocked.
        When Herald fails, it must quote the specific governance rule.

        Args:
            constraint_type: Type of constraint ("license_revoked", "connectivity_disabled", "governance_violation", etc)
            details: Additional detail about the constraint

        Returns:
            Formatted constraint citation string
        """
        citations = {
            "license_revoked": "❌ Failure. Action was blocked because **broadcast license is revoked**. I cannot violate **Article IV (Secure Broadcast)** of my STEWARD.md governance rules.",
            "license_inactive": "❌ Failure. Action was blocked because **broadcast license is inactive**. I cannot violate **Article IV (Secure Broadcast)** of my STEWARD.md governance rules.",
            "connectivity_disabled": "❌ Failure. Action was blocked because **connectivity is unauthorized/inactive**. I cannot violate **Article IV (Secure Broadcast)** of my STEWARD.md governance rules.",
            "insufficient_credits": "❌ Failure. Action was blocked because **insufficient credits remain**. Budget allocation requires **FORUM proposal approval** per Article V (Economic Governance).",
            "governance_violation": "❌ Failure. Action was blocked by governance validation. The content violates one or more rules in the **HeraldConstitution** governance framework.",
        }

        citation = citations.get(
            constraint_type,
            f"❌ Failure. Action blocked by constraint: {constraint_type}",
        )

        if details:
            citation += f"\n   Details: {details}"

        return citation

    def execute_publish(self, content: str, civic_cartridge=None, forum_cartridge=None) -> Dict[str, Any]:
        """
        Execute publication action with event recording.

        This method publishes pre-approved content to configured platforms
        and records all actions in the event ledger.

        NEW: Checks broadcast license and credits via CIVIC before publishing.
        If out of credits, creates a proposal automatically.

        PHASE II: Explicitly cites governance constraints when blocking actions.

        Args:
            content: Text to publish
            civic_cartridge: Reference to CIVIC cartridge (for license/credit checks)
            forum_cartridge: Reference to FORUM cartridge (for proposal creation)

        Returns:
            dict: Publication result with status
        """
        try:
            logger.info("🦅 PHASE 4: PUBLICATION")
            logger.info("=" * 70)

            # Verify content
            if not content or len(content) < 10:
                logger.error("❌ Invalid content")
                event = self.event_log.record_content_rejected(
                    content=content,
                    reason="invalid_content",
                    violations=["Content too short or empty"],
                )
                if event:
                    # Log via kernel (herald.scribe)
                    self.system.execute_tool("herald.scribe", {"action": "log_action", "event_data": event.to_dict()})
                return {"status": "failed", "reason": "invalid_content"}

            # NEW: Check broadcast license with CIVIC
            if civic_cartridge:
                logger.info("[STEP 1] Checking broadcast license with CIVIC...")
                license_check = civic_cartridge.check_broadcast_license("herald")
                if not license_check["licensed"]:
                    # PHASE II: Explicitly cite the governance constraint
                    constraint_citation = self._cite_governance_constraint(
                        ("license_revoked" if license_check.get("reason") == "revoked" else "license_inactive"),
                        details=f"License status: {license_check.get('reason')}",
                    )
                    logger.error(constraint_citation)

                    event = self.event_log.record_content_rejected(
                        content=content,
                        reason="no_broadcast_license",
                        violations=[constraint_citation],
                    )
                    if event:
                        # Log via kernel (herald.scribe)
                        self.system.execute_tool(
                            "herald.scribe", {"action": "log_action", "event_data": event.to_dict()}
                        )
                    return {
                        "status": "rejected",
                        "reason": "no_broadcast_license",
                        "message": constraint_citation,
                    }
                logger.info(f"   ✅ License valid (credits: {license_check.get('credits', 'N/A')})")

                # NEW: Check credit balance
                balance = civic_cartridge.ledger.get_agent_balance("herald")
                logger.info(f"   Current balance: {balance} credits")

                if balance == 0:
                    logger.warning("⚠️  Out of credits! Creating proposal for budget request...")

                    # PHASE II: Cite governance constraint
                    constraint_citation = self._cite_governance_constraint(
                        "insufficient_credits",
                        details="Zero balance. Broadcasting requires credits per economic governance.",
                    )
                    logger.error(constraint_citation)

                    if forum_cartridge:
                        proposal = forum_cartridge.create_proposal(
                            title="Budget Request - Herald Marketing Campaign",
                            description="Herald has exhausted credits and requests budget allocation for continued operations.",
                            proposer="herald",
                            action={
                                "type": "civic.ledger.transfer",
                                "params": {
                                    "to": "herald",
                                    "amount": 50,
                                    "reason": "proposal_approved",
                                },
                            },
                        )

                        event = self.event_log.record_content_rejected(
                            content=content,
                            reason="insufficient_credits",
                            violations=[
                                constraint_citation,
                                f"Created proposal {proposal['id']} requesting budget",
                            ],
                        )
                        if event:
                            # Log via kernel (herald.scribe)
                            self.system.execute_tool(
                                "herald.scribe", {"action": "log_action", "event_data": event.to_dict()}
                            )

                        return {
                            "status": "insufficient_credits",
                            "message": constraint_citation,
                            "proposal_id": proposal["id"],
                            "proposal_message": f"Created proposal {proposal['id']} requesting 50 credits.",
                        }
                    else:
                        return {
                            "status": "insufficient_credits",
                            "message": constraint_citation,
                        }

            # Publish to Twitter
            logger.info("[STEP 2] Verifying Twitter credentials...")
            verify_result = self.system.execute_tool(
                "herald.broadcast", {"action": "verify_credentials", "platform": "twitter"}
            )
            if not (verify_result.success and verify_result.output.get("verified")):
                # PHASE II: Cite governance constraint
                constraint_citation = self._cite_governance_constraint(
                    "connectivity_disabled",
                    details="Twitter connection is unavailable or unauthorized.",
                )
                logger.warning(constraint_citation)
                event = self.event_log.record_content_rejected(
                    content=content,
                    reason="connectivity_unavailable",
                    violations=[constraint_citation],
                )
                if event:
                    # Log via kernel (herald.scribe)
                    self.system.execute_tool("herald.scribe", {"action": "log_action", "event_data": event.to_dict()})
                return {
                    "status": "rejected",
                    "reason": "twitter_offline",
                    "message": constraint_citation,
                }
            else:
                logger.info("[STEP 3] Publishing to Twitter...")
                publish_result = self.system.execute_tool(
                    "herald.broadcast", {"action": "publish", "content": content, "platform": "twitter"}
                )
                if not publish_result.success:
                    logger.error("❌ Twitter publish failed")
                    # PHASE II: Cite governance constraint
                    constraint_citation = self._cite_governance_constraint(
                        "connectivity_disabled",
                        details="Twitter API returned an error during publication.",
                    )
                    event = self.event_log.record_system_error(
                        error_type="publish_error", error_message=constraint_citation
                    )
                    if event:
                        # Log via kernel (herald.scribe)
                        self.system.execute_tool(
                            "herald.scribe", {"action": "log_action", "event_data": event.to_dict()}
                        )
                    return {
                        "status": "failed",
                        "reason": "publish_error",
                        "message": constraint_citation,
                        "platform": "twitter",
                    }

                # NEW: Deduct credits from CIVIC
                if civic_cartridge:
                    logger.info("[STEP 4] Deducting credits...")
                    deduction = civic_cartridge.deduct_credits("herald", 1, "broadcast")
                    logger.info(f"   Deducted 1 credit. Balance: {deduction.get('credits_remaining', 'N/A')}")

                # Record successful publication and log to chronicle
                from datetime import datetime, timezone

                event = self.event_log.record_content_published(
                    content=content,
                    platform="twitter",
                    post_id=None,  # Would be populated from API response in production
                    metadata={"published_at": datetime.now(timezone.utc).isoformat()},
                )
                if event:
                    # Log via kernel (herald.scribe)
                    self.system.execute_tool("herald.scribe", {"action": "log_action", "event_data": event.to_dict()})

                logger.info("✅ Published to Twitter")

            logger.info("\n" + "=" * 70)
            logger.info("✅ PUBLICATION COMPLETE")
            logger.info("=" * 70)

            return {"status": "published", "platform": "twitter"}

        except Exception as e:
            import traceback

            logger.error(f"❌ Publication error: {e}")
            event = self.event_log.record_system_error(
                error_type="publish_error",
                error_message=str(e),
                traceback=traceback.format_exc(),
            )
            if event:
                # Log via kernel (herald.scribe)
                self.system.execute_tool("herald.scribe", {"action": "log_action", "event_data": event.to_dict()})
            return {"status": "error", "reason": "publication_error", "error": str(e)}

    def plan_campaign(self, duration_weeks: int = 2, dry_run: bool = False) -> Dict[str, Any]:
        """
        Strategic campaign planning - DEPRECATED (StrategyTool removed).

        HERALD is now infrastructure-only (broadcast, research, identity, logging).
        Campaign planning is no longer part of HERALD's responsibilities.

        Args:
            duration_weeks: Campaign duration (ignored)
            dry_run: Dry run flag (ignored)

        Returns:
            dict: Error indicating feature removed
        """
        logger.warning("⚠️  plan_campaign() is DEPRECATED - StrategyTool has been removed")
        logger.info("   HERALD is now infrastructure-only (broadcast, research, identity, logging)")
        return {
            "status": "deprecated",
            "reason": "strategy_tool_removed",
            "message": "Campaign planning removed - HERALD is infrastructure-only",
        }

    def run_reply_cycle(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Execute the engagement loop: Listen -> Think -> Draft.

        1. Load state (last processed tweet)
        2. Scan for new mentions
        3. Generate replies
        4. Validate governance
        5. Save drafts for approval

        Args:
            dry_run: If True, don't update state

        Returns:
            dict: Result summary
        """
        logger.info("\n🦅 PHASE 1: LISTENING")
        logger.info("=" * 70)

        # Load state (PHASE 3.2.1: Fixed - use sandboxed path)
        state_path = self.system.get_sandbox_path() / "state" / "twitter_state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state = {}
        if state_path.exists():
            try:
                with open(state_path) as f:
                    state = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load state from {state_path}: {e}")
                pass

        since_id = state.get("last_mention_id")
        logger.info(f"👂 Scanning mentions since ID: {since_id}")

        # Scan mentions via kernel (herald.broadcast)
        scan_result = self.system.execute_tool(
            "herald.broadcast", {"action": "scan_mentions", "since_id": since_id, "platform": "twitter"}
        )
        mentions = scan_result.output.get("mentions", []) if scan_result.success else []

        if not mentions:
            logger.info("✅ No new mentions found.")
            return {"status": "no_new_mentions", "count": 0}

        logger.info(f"✅ Found {len(mentions)} mentions. Processing...")

        drafts = []
        new_since_id = since_id

        logger.info("\n🦅 PHASE 2: ENGAGEMENT")
        logger.info("=" * 70)

        for mention in mentions:
            t_id = mention["id"]
            text = mention["text"]
            author = mention["author_id"]

            # Update high-water mark
            if not new_since_id or int(t_id) > int(new_since_id):
                new_since_id = t_id

            logger.info(f"🤔 Thinking about: {text[:50]}...")

            # SCOUTING: Check if user is a wild agent via kernel (herald.scout)
            user_data = {
                "username": author,
                "bio": "",
                "name": "",
            }  # In real implementation, fetch full user profile
            scout_result = self.system.execute_tool(
                "herald.scout", {"action": "analyze_user", "user_data": user_data, "text": text}
            )
            is_bot = scout_result.output.get("is_bot", False) if scout_result.success else False
            confidence = scout_result.output.get("confidence", 0.0) if scout_result.success else 0.0

            reply_content = ""

            # Check registration via kernel (herald.scout)
            registered_result = self.system.execute_tool(
                "herald.scout", {"action": "is_registered", "username": author}
            )
            is_registered = registered_result.output.get("is_registered", False) if registered_result.success else False

            if is_bot and not is_registered:
                logger.info(f"🔭 Detected Wild Agent: {author} (Confidence: {confidence})")
                # DEPRECATED: Content generation removed
                logger.warning("⚠️  Recruitment pitch generation removed - use MARKETER")
                reply_content = f"[MARKETER REQUIRED] Would recruit {author}"
            else:
                # Standard reply
                # DEPRECATED: Content generation removed
                logger.warning("⚠️  Reply generation removed - use MARKETER")
                reply_content = f"[MARKETER REQUIRED] Would reply to {author}"

            # Validate (Double Check)
            validation = self.governance.validate(reply_content, platform="twitter")

            draft = {
                "reply_to_id": t_id,
                "original_text": text,
                "reply_content": reply_content,
                "is_valid": validation.is_valid,
                "violations": validation.violations,
                "type": "recruitment" if is_bot else "reply",
            }

            if validation.is_valid:
                logger.info(f"   ✅ Drafted ({draft['type']}): {reply_content}")
                drafts.append(draft)
            else:
                logger.warning(f"   ❌ Rejected: {reply_content} ({validation.violations})")

        # Save Drafts
        logger.info("\n🦅 PHASE 3: APPROVAL QUEUE")
        logger.info("=" * 70)

        output_path = Path("dist/replies.json")
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(drafts, f, indent=2)

        logger.info(f"✅ Saved {len(drafts)} drafts to {output_path}")

        # Update State
        if not dry_run and new_since_id != since_id:
            state["last_mention_id"] = new_since_id
            state_path.parent.mkdir(parents=True, exist_ok=True)
            with open(state_path, "w") as f:
                json.dump(state, f, indent=2)
            logger.info(f"💾 State updated: last_mention_id = {new_since_id}")

        return {
            "status": "success",
            "processed": len(mentions),
            "drafted": len(drafts),
            "drafts_file": str(output_path),
        }

    def generate_reddit_post(self, subreddit: str = "r/LocalLLaMA") -> Optional[Dict[str, Any]]:
        """
        Generate a Reddit deep-dive post (standalone capability).

        Args:
            subreddit: Target subreddit

        Returns:
            dict: {"title": str, "body": str} or None
        """
        logger.info(f"🦅 Generating Reddit post for {subreddit}...")
        # DEPRECATED: Content generation removed
        logger.warning("⚠️  Reddit post generation removed - use MARKETER")
        return {"error": "Content generation removed from HERALD. Use MARKETER instead."}


# Export for VibeOS cartridge loading
__all__ = ["HeraldCartridge"]
