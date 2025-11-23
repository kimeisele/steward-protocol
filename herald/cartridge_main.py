#!/usr/bin/env python3
"""
HERALD Cartridge - ARCH-050 Vibe-OS Compatible Reference Agent

This cartridge demonstrates the Steward Protocol in action:
1. Autonomous content generation for marketing
2. Multi-platform distribution (Twitter, Reddit)
3. Cryptographic identity via Steward Protocol (prepared)
4. Governance-first architecture (no marketing slop)

Can be run standalone (via shim.py) OR as a native Vibe-OS cartridge.

Usage:
    Standalone: python herald/shim.py --action run
    VibeOS:     kernel.load_cartridge("herald").run_campaign()
"""

import logging
import json
from typing import Dict, Any, Optional
from pathlib import Path

from herald.tools.research_tool import ResearchTool
from herald.tools.content_tool import ContentTool
from herald.tools.broadcast_tool import BroadcastTool
from herald.tools.identity_tool import IdentityTool
from herald.tools.scribe_tool import Scribe
from herald.core.memory import EventLog
from herald.governance import HeraldConstitution

logger = logging.getLogger("HERALD_CARTRIDGE")


class HeraldCartridge:
    """
    HERALD - The Autonomous Intelligence Agent for STEWARD Protocol.

    This cartridge encapsulates the complete workflow:
    1. Research: Market trend analysis via Tavily
    2. Create: LLM-based content generation with governance
    3. Publish: Multi-platform distribution
    4. Observe: Full audit trail (GAD-000 compliance)

    Architecture:
    - Vibe-OS compatible (ARCH-050 CartridgeBase)
    - Offline-capable (graceful fallback)
    - Identity-ready (Steward Protocol integration prepared)
    - Governance-first (no marketing clichés)
    """

    # Cartridge Metadata (ARCH-050 required fields)
    name = "herald"
    version = "3.0.0"
    description = "Autonomous intelligence and content distribution agent"
    author = "Steward Protocol"

    def __init__(self):
        """Initialize HERALD cartridge."""
        logger.info("🦅 HERALD v3.0: Cartridge initialization")

        # Initialize tools
        self.research = ResearchTool()
        self.content = ContentTool()
        self.broadcast = BroadcastTool()
        self.identity = IdentityTool()

        # Initialize governance (immutable rules as code)
        self.governance = HeraldConstitution()
        logger.info("⚖️  Governance loaded: HeraldConstitution (immutable code-based rules)")

        # Initialize event sourcing (state as event ledger)
        self.event_log = EventLog(ledger_path=Path("data/events/herald.jsonl"))
        logger.info("📖 EventLog initialized: All actions will be recorded and signed")

        # Initialize living documentation (Auto-Scribe)
        self.scribe = Scribe(chronicle_path=Path("docs/chronicles.md"))
        self.scribe.initialize_logbook_section()
        logger.info("✍️  Auto-Scribe initialized: Activity will be logged to chronicles.md")

        # Rebuild state from event ledger (self-correction on startup)
        self.agent_state = self.event_log.rebuild_state()
        self.safe_mode = self.agent_state.get("safe_mode", False)

        if self.safe_mode:
            logger.warning("⚠️  SAFE MODE ENABLED: Last execution had errors")
            logger.warning(f"   Last failure: {self.agent_state.get('last_failure')}")
            logger.info("   Reduce operation scope and increase validation checks")

        # Execution metadata
        self.execution_id = None
        self.last_result = None

        logger.info("✅ HERALD: Ready for operation")

    def get_config(self) -> Dict[str, Any]:
        """Get cartridge configuration (ARCH-050 interface)."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
        }

    def report_status(self) -> Dict[str, Any]:
        """Report cartridge status (ARCH-050 interface)."""
        return {
            "name": self.name,
            "version": self.version,
            "last_execution": self.execution_id,
            "last_result": self.last_result,
            "connectivity": {
                "twitter": self.broadcast.verify_credentials("twitter"),
                "reddit": self.broadcast.verify_credentials("reddit"),
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

            # Step 1: Research
            trending = self.research.find_trending_topic()
            research_context = None
            if trending:
                research_context = trending.get("article", {}).get("content")
                logger.info(f"✅ Trending topic found: {trending.get('search_query')}")
            else:
                logger.warning("⚠️  No trending topic, using generic context")

            # Step 2: Generate Content
            logger.info("\n🦅 PHASE 2: CREATION")
            logger.info("=" * 70)

            tweet = self.content.generate_tweet(research_context=research_context)
            if not tweet:
                logger.error("❌ Content generation failed")
                event = self.event_log.record_system_error(
                    error_type="content_generation_error",
                    error_message="LLM returned empty content"
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
                context={"research_query": research_context[:100] if research_context else None}
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

                # Record rejection with governance violations and log to chronicle
                event = self.event_log.record_content_rejected(
                    content=tweet,
                    reason="governance_violation",
                    violations=validation_result.violations
                )
                if event:
                    self.scribe.log_action(event)
                return {
                    "status": "rejected",
                    "reason": "governance_violations",
                    "content": tweet,
                    "violations": validation_result.violations,
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
                }
            }

            self.last_result = result
            logger.info("\n" + "=" * 70)
            logger.info("✅ CAMPAIGN COMPLETE")
            logger.info(f"   Content: {len(tweet)} chars")
            logger.info(f"   Status: {'DRY RUN' if dry_run else 'READY FOR PUBLISH'}")
            logger.info("=" * 70)

            return result

        except Exception as e:
            logger.error(f"❌ Campaign execution error: {e}")
            import traceback
            tb = traceback.format_exc()
            logger.error(f"   Traceback: {tb}")

            # Record system error to event ledger and log to chronicle
            event = self.event_log.record_system_error(
                error_type="campaign_error",
                error_message=str(e),
                traceback=tb
            )
            if event:
                self.scribe.log_action(event)

            return {
                "status": "error",
                "reason": "campaign_execution_error",
                "error": str(e),
                "content": None,
            }

    def execute_publish(self, content: str) -> Dict[str, Any]:
        """
        Execute publication action with event recording.

        This method publishes pre-approved content to configured platforms
        and records all actions in the event ledger.

        Args:
            content: Text to publish

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
                    violations=["Content too short or empty"]
                )
                if event:
                    self.scribe.log_action(event)
                return {"status": "failed", "reason": "invalid_content"}

            # Publish to Twitter
            logger.info("[STEP 1] Verifying Twitter credentials...")
            if not self.broadcast.verify_credentials("twitter"):
                logger.warning("⚠️  Twitter offline, skipping")
                return {"status": "skipped", "reason": "twitter_offline"}
            else:
                logger.info("[STEP 2] Publishing to Twitter...")
                success = self.broadcast.publish(content, platform="twitter")
                if not success:
                    logger.error("❌ Twitter publish failed")
                    event = self.event_log.record_system_error(
                        error_type="publish_error",
                        error_message="Twitter publish failed"
                    )
                    if event:
                        self.scribe.log_action(event)
                    return {"status": "failed", "platform": "twitter"}

                # Record successful publication and log to chronicle
                from datetime import datetime, timezone
                event = self.event_log.record_content_published(
                    content=content,
                    platform="twitter",
                    post_id=None,  # Would be populated from API response in production
                    metadata={"published_at": datetime.now(timezone.utc).isoformat()}
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
                traceback=traceback.format_exc()
            )
            if event:
                self.scribe.log_action(event)
            return {"status": "error", "reason": "publication_error", "error": str(e)}

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
