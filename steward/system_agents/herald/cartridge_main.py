#!/usr/bin/env python3
"""
HERALD Cartridge - ContextAwareAgent with Offline-First Capabilities

This cartridge demonstrates the Steward Protocol in action:
1. Autonomous content generation for marketing
2. Multi-platform distribution (Twitter, Reddit)
3. Cryptographic identity via Steward Protocol
4. Governance-first architecture (no marketing slop)

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
from steward.oath_mixin import OathMixin

from .core.memory import EventLog
from .governance import HeraldConstitution
from .tools.broadcast_tool import BroadcastTool
from .tools.content_tool import ContentTool
from .tools.identity_tool import IdentityTool
from .tools.research_tool import ResearchTool
from .tools.scout_tool import ScoutTool
from .tools.scribe_tool import Scribe
from .tools.strategy_tool import StrategyTool
from .tools.tidy_tool import TidyTool

# Constitutional Oath
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HERALD_MAIN")


class HeraldCartridge(ContextAwareAgent, OathMixin):
    """
    The HERALD Agent Cartridge.
    Autonomous Technical Evangelist for Steward Protocol.

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
            description="Autonomous intelligence and content distribution agent (offline-first)",
            domain="MEDIA",
            capabilities=["content_generation", "broadcasting", "research", "strategy"],
            config=config,  # Pass config to parent
        )

        # BLOCKER #0: Accept Phoenix Config (with fallback for missing pydantic)
        # Override self.config set by parent if needed
        class FallbackConfig:
            posting_frequency_hours = 4
            dry_run = True

        if config:
            self.config = config
        elif HeraldConfig is not None:
            try:
                self.config = HeraldConfig()
            except Exception:
                self.config = FallbackConfig()
        else:
            self.config = FallbackConfig()

        logger.info(
            f"🦅 HERALD (ContextAwareAgent v3.1) is online (config: {self.config.posting_frequency_hours}h frequency)."
        )

        # Initialize Constitutional Oath mixin (if available)
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            # SWEAR THE OATH IMMEDIATELY in __init__ (synchronous)
            # This ensures Herald has oath_sworn=True before kernel registration
            self.oath_sworn = True
            logger.info("✅ HERALD has sworn the Constitutional Oath (Genesis Ceremony)")

        # Initialize all tools with DegradationChain injection for offline capability
        # The DegradationChain is provided by ContextAwareAgent.get_degradation_chain()
        degradation_chain = self.get_degradation_chain()

        self.content = ContentTool()
        self.broadcast = BroadcastTool()
        # ResearchTool now uses DegradationChain for offline fallback
        self.research = ResearchTool(degradation_chain=degradation_chain)
        self.strategy = StrategyTool()
        self.scout = ScoutTool()
        self.identity = IdentityTool()

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

        # Initialize living documentation (Auto-Scribe)
        # Note: Scribe/Tidy require repo access - will be migrated in later phase
        self.scribe = Scribe(chronicle_path=Path("docs/chronicles.md"))
        self.scribe.initialize_logbook_section()
        logger.info("✍️  Auto-Scribe initialized: Activity will be logged to chronicles.md")

        # Initialize repository maintenance (Tidy)
        self.tidy = TidyTool(root_path=Path("."), steward_path=Path("STEWARD.md"))
        logger.info("🧹 Tidy Tool initialized: Repository hygiene enabled")

        # Execution metadata
        self.execution_id = None
        self.last_result = None

        logger.info("✅ HERALD: Ready for operation")

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
                logger.info(f"✅ Herald has been bound to Constitution")
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

    def process(self, task: Task) -> Dict[str, Any]:
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
                return self.broadcast.publish(content, platform=platform)

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
                "twitter": self.broadcast.verify_credentials("twitter"),
                "reddit": self.broadcast.verify_credentials("reddit"),
            },
            "governance": {
                "safe_mode": self.safe_mode,
                "last_failure": (self.agent_state.get("last_failure") if self.safe_mode else None),
            },
        }

    def run_campaign(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Execute the main campaign workflow with event sourcing.

        This is the primary action that orchestrates the full pipeline:
        1. Research current market trends
        2. Generate content based on research
        3. Validate against HeraldConstitution governance
        4. Record all actions in immutable event ledger
        5. Prepare for publication (or publish if approved)

        All events are cryptographically signed and stored.
        If execution fails, state is preserved for recovery.

        Args:
            dry_run: If True, don't actually publish (for testing)

        Returns:
            dict: Campaign result with status and generated content
        """
        try:
            logger.info("🦅 PHASE 1: RESEARCH")
            logger.info("=" * 70)

            # Step 1: Research via local ResearchTool
            logger.info("[RESEARCH] Researching current trends...")
            trending = self.research.find_trending_topic()

            research_context = None
            if trending:
                research_context = trending.get("article", {}).get("content")
                logger.info(f"✅ Trending topic found: {trending.get('search_query')}")
                logger.info(f"   Query: {trending.get('search_query')}")
            else:
                logger.warning("⚠️  No trending topic found, using generic context")

            # Step 2: Generate Content
            logger.info("\n🦅 PHASE 2: CREATION")
            logger.info("=" * 70)

            tweet = self.content.generate_tweet(research_context=research_context)
            if not tweet:
                logger.error("❌ Content generation failed")
                event = self.event_log.record_system_error(
                    error_type="content_generation_error",
                    error_message="LLM returned empty content",
                )
                if event:
                    self.scribe.log_action(event)
                return {
                    "status": "failed",
                    "reason": "content_generation_failed",
                    "content": None,
                }

            logger.info(f"✅ Content generated: {len(tweet)} chars")
            logger.info(f"   Preview: {tweet[:80]}...")

            # Record generation event and log to chronicle
            event = self.event_log.record_content_generated(
                content=tweet,
                platform="twitter",
                context={"research_query": (research_context[:100] if research_context else None)},
            )
            if event:
                self.scribe.log_action(event)

            # Step 2.5: Sign Content (Steward Protocol Integration)
            logger.info("\n🦅 PHASE 2.5: IDENTITY")
            logger.info("=" * 70)

            signature = None
            if self.identity.assert_identity():
                signature = self.identity.sign_artifact(tweet)
                if signature:
                    logger.info(f"✅ Content signed: {signature[:40]}...")
                else:
                    logger.warning("⚠️  Signing attempted but failed (no credentials)")
            else:
                logger.debug("ℹ️  Identity not available, skipping signature")

            # Step 3: Governance Validation (Architectural Gate)
            logger.info("\n🦅 PHASE 3: GOVERNANCE")
            logger.info("=" * 70)

            validation_result = self.governance.validate(tweet, platform="twitter")
            if not validation_result.is_valid:
                logger.error("❌ Content failed governance validation")
                for violation in validation_result.violations:
                    logger.error(f"   ❌ {violation}")

                # PHASE II: Cite governance constraint
                constraint_citation = self._cite_governance_constraint(
                    "governance_violation",
                    details="Content violates " + "; ".join(validation_result.violations[:2]),
                )
                logger.error(constraint_citation)

                # Record rejection with governance violations and log to chronicle
                event = self.event_log.record_content_rejected(
                    content=tweet,
                    reason="governance_violation",
                    violations=[constraint_citation] + validation_result.violations,
                )
                if event:
                    self.scribe.log_action(event)

                # Still perform housekeeping even on failure
                logger.info("\n🦅 PHASE 5: HOUSEKEEPING")
                logger.info("=" * 70)
                moved, protected, errors = self.tidy.organize_workspace(dry_run=dry_run)
                logger.info(f"✅ Repository tidied: {moved} files organized, {protected} protected, {errors} errors")

                return {
                    "status": "rejected",
                    "reason": "governance_violations",
                    "content": tweet,
                    "violations": validation_result.violations,
                    "constraint_citation": constraint_citation,
                }

            # Warnings (don't reject, but log)
            if validation_result.warnings:
                logger.warning("⚠️  Governance warnings:")
                for warning in validation_result.warnings:
                    logger.warning(f"   {warning}")

            logger.info("✅ Content passed governance validation")
            logger.info(f"   Philosophy: {self.governance.get_rules_summary()['philosophy']}")

            # Step 4: Prepare Artifact
            result = {
                "status": "draft_ready",
                "content": tweet,
                "context": research_context or "No trending topic",
                "platform": "twitter",
                "dry_run": dry_run,
                "signature": signature,
                "validation": {
                    "is_valid": True,
                    "violations": validation_result.violations,
                    "warnings": validation_result.warnings,
                },
            }

            self.last_result = result
            logger.info("\n" + "=" * 70)
            logger.info("✅ CAMPAIGN COMPLETE")
            logger.info(f"   Content: {len(tweet)} chars")
            logger.info(f"   Status: {'DRY RUN' if dry_run else 'READY FOR PUBLISH'}")
            logger.info("=" * 70)

            # Phase 5: Housekeeping (Repository Maintenance)
            logger.info("\n🦅 PHASE 5: HOUSEKEEPING")
            logger.info("=" * 70)
            moved, protected, errors = self.tidy.organize_workspace(dry_run=dry_run)
            logger.info(f"✅ Repository tidied: {moved} files organized, {protected} protected, {errors} errors")

            return result

        except Exception as e:
            logger.error(f"❌ Campaign execution error: {e}")
            import traceback

            tb = traceback.format_exc()
            logger.error(f"   Traceback: {tb}")

            # Record system error to event ledger and log to chronicle
            event = self.event_log.record_system_error(error_type="campaign_error", error_message=str(e), traceback=tb)
            if event:
                self.scribe.log_action(event)

            return {
                "status": "error",
                "reason": "campaign_execution_error",
                "error": str(e),
                "content": None,
            }

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
            "license_revoked": f"❌ Failure. Action was blocked because **broadcast license is revoked**. I cannot violate **Article IV (Secure Broadcast)** of my STEWARD.md governance rules.",
            "license_inactive": f"❌ Failure. Action was blocked because **broadcast license is inactive**. I cannot violate **Article IV (Secure Broadcast)** of my STEWARD.md governance rules.",
            "connectivity_disabled": f"❌ Failure. Action was blocked because **connectivity is unauthorized/inactive**. I cannot violate **Article IV (Secure Broadcast)** of my STEWARD.md governance rules.",
            "insufficient_credits": f"❌ Failure. Action was blocked because **insufficient credits remain**. Budget allocation requires **FORUM proposal approval** per Article V (Economic Governance).",
            "governance_violation": f"❌ Failure. Action was blocked by governance validation. The content violates one or more rules in the **HeraldConstitution** governance framework.",
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
                    self.scribe.log_action(event)
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
                        self.scribe.log_action(event)
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
                            self.scribe.log_action(event)

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
            if not self.broadcast.verify_credentials("twitter"):
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
                    self.scribe.log_action(event)
                return {
                    "status": "rejected",
                    "reason": "twitter_offline",
                    "message": constraint_citation,
                }
            else:
                logger.info("[STEP 3] Publishing to Twitter...")
                success = self.broadcast.publish(content, platform="twitter")
                if not success:
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
                        self.scribe.log_action(event)
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
                    self.scribe.log_action(event)

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
                self.scribe.log_action(event)
            return {"status": "error", "reason": "publication_error", "error": str(e)}

    def plan_campaign(self, duration_weeks: int = 2, dry_run: bool = False) -> Dict[str, Any]:
        """
        Strategic campaign planning - macro-level roadmap generation.

        This is the "dogfooding" capability: HERALD plans its own campaign.

        Workflow:
        1. Read AGI_MANIFESTO.md and WHY_DOWNVOTED.md for context
        2. Generate strategic roadmap (governance-aligned)
        3. Write to marketing/launch_roadmap.md
        4. Record in event ledger
        5. AUDITOR will verify the strategy

        Args:
            duration_weeks: Campaign duration (default: 2 weeks)
            dry_run: If True, generate but don't write to file

        Returns:
            dict: Planning result with status and roadmap
        """
        try:
            logger.info("\n🦅 PHASE 1: STRATEGIC PLANNING")
            logger.info("=" * 70)
            logger.info(f"   Duration: {duration_weeks} weeks")
            logger.info("   Mission: Generate governance-aligned campaign roadmap")

            # Step 1: Plan campaign (LLM or template-based)
            logger.info("\n[STEP 1] Reading foundational documents...")
            manifesto_path = Path("AGI_MANIFESTO.md")
            context_path = Path("docs/herald/WHY_DOWNVOTED.md")

            roadmap = self.strategy.plan_launch_campaign(
                manifesto_path=manifesto_path,
                context_path=context_path,
                duration_weeks=duration_weeks,
            )

            if not roadmap:
                logger.error("❌ Failed to generate campaign roadmap")
                return {"status": "failed", "reason": "strategy_generation_failed"}

            logger.info(f"✅ Roadmap generated ({len(roadmap)} chars)")

            # Step 2: Governance check
            logger.info("\n[STEP 2] Governance validation...")
            alignment = self.strategy.analyze_campaign_alignment(roadmap)
            logger.info(f"   Governance-aligned: {alignment['governance_aligned']}")
            logger.info(f"   Has phases: {alignment['has_phases']}")
            logger.info(f"   Proof-heavy: {alignment['proof_heavy'] > 3}")
            logger.info(f"   Hype-free: {alignment['hype_free']}")

            if not alignment["governance_aligned"]:
                logger.warning("⚠️  Roadmap failed governance check, regenerating...")
                # Fallback will use template
                return {
                    "status": "partial",
                    "reason": "governance_rework_needed",
                    "roadmap": roadmap,
                }

            logger.info("✅ Roadmap passed governance validation")

            # Step 3: Write to file (unless dry_run)
            logger.info("\n[STEP 3] Writing roadmap to file...")
            if not dry_run:
                success = self.strategy.write_roadmap_to_file(roadmap, output_path=Path("marketing/launch_roadmap.md"))
                if not success:
                    logger.error("❌ Failed to write roadmap to file")
                    return {
                        "status": "failed",
                        "reason": "file_write_failed",
                        "roadmap": roadmap,
                    }
            else:
                logger.info("🔍 DRY RUN: Skipping file write")

            logger.info("✅ Roadmap written to marketing/launch_roadmap.md")

            # Step 4: Record in event ledger
            logger.info("\n[STEP 4] Recording in event ledger...")
            event = self.event_log.create_event(
                event_type="strategy_planned",
                payload={
                    "duration_weeks": duration_weeks,
                    "governance_aligned": alignment.get("governance_aligned", False),
                    "roadmap_size": len(roadmap),
                    "dry_run": dry_run,
                    "phases": alignment.get("has_phases", False),
                },
            )
            if self.event_log.commit(event):
                self.scribe.log_action(event)
                logger.info("✅ Event recorded and logged")

            # Step 5: Prepare result
            result = {
                "status": "complete",
                "duration_weeks": duration_weeks,
                "roadmap_path": "marketing/launch_roadmap.md" if not dry_run else None,
                "roadmap_preview": roadmap[:500] + "...",
                "alignment": alignment,
                "message": "Campaign roadmap generated. AUDITOR will now verify.",
            }

            logger.info("\n" + "=" * 70)
            logger.info("✅ STRATEGIC PLANNING COMPLETE")
            logger.info("   Next: AUDITOR verification (automatic)")
            logger.info("=" * 70)

            self.last_result = result
            return result

        except Exception as e:
            logger.error(f"❌ Planning error: {e}")
            import traceback

            tb = traceback.format_exc()
            logger.error(f"   Traceback: {tb}")

            # Record error to event ledger
            event = self.event_log.record_system_error(
                error_type="strategy_planning_error", error_message=str(e), traceback=tb
            )
            if event:
                self.scribe.log_action(event)

            return {
                "status": "error",
                "reason": "strategy_planning_error",
                "error": str(e),
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
            except Exception:
                pass

        since_id = state.get("last_mention_id")
        logger.info(f"👂 Scanning mentions since ID: {since_id}")

        mentions = self.broadcast.scan_mentions(since_id=since_id, platform="twitter")

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

            # SCOUTING: Check if user is a wild agent
            user_data = {
                "username": author,
                "bio": "",
                "name": "",
            }  # In real implementation, fetch full user profile
            is_bot, confidence = self.scout.analyze_user(user_data, text=text)

            reply_content = ""

            if is_bot and not self.scout.is_registered(author):
                logger.info(f"🔭 Detected Wild Agent: {author} (Confidence: {confidence})")
                reply_content = self.content.generate_recruitment_pitch(author, context=text)
            else:
                # Standard reply
                reply_content = self.content.generate_reply(text, author)

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
        return self.content.generate_reddit_post(subreddit=subreddit)


# Export for VibeOS cartridge loading
__all__ = ["HeraldCartridge"]
