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
from herald.tools.scout_tool import ScoutTool
from herald.tools.tidy_tool import TidyTool
from herald.tools.strategy_tool import StrategyTool
from herald.core.memory import EventLog
from herald.governance import HeraldConstitution
from artisan.cartridge_main import ArtisanCartridge

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HERALD_MAIN")


class HeraldCartridge:
    """
    The HERALD Agent Cartridge.
    Autonomous Technical Evangelist for Steward Protocol.

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
        """Initialize HERALD with all tools."""
        self.content = ContentTool()
        self.broadcast = BroadcastTool()
        self.research = ResearchTool()
        self.strategy = StrategyTool()
        self.scout = ScoutTool()
        self.artisan = ArtisanCartridge()
        self.identity = IdentityTool()
        logger.info("🦅 HERALD is online.")

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

        # Initialize repository maintenance (Tidy)
        self.tidy = TidyTool(root_path=Path("."), steward_path=Path("STEWARD.md"))
        logger.info("🧹 Tidy Tool initialized: Repository hygiene enabled")

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
                duration_weeks=duration_weeks
            )

            if not roadmap:
                logger.error("❌ Failed to generate campaign roadmap")
                return {
                    "status": "failed",
                    "reason": "strategy_generation_failed"
                }

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
                    "roadmap": roadmap
                }

            logger.info("✅ Roadmap passed governance validation")

            # Step 3: Write to file (unless dry_run)
            logger.info("\n[STEP 3] Writing roadmap to file...")
            if not dry_run:
                success = self.strategy.write_roadmap_to_file(
                    roadmap,
                    output_path=Path("marketing/launch_roadmap.md")
                )
                if not success:
                    logger.error("❌ Failed to write roadmap to file")
                    return {
                        "status": "failed",
                        "reason": "file_write_failed",
                        "roadmap": roadmap
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
                }
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
                "message": "Campaign roadmap generated. AUDITOR will now verify."
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
                error_type="strategy_planning_error",
                error_message=str(e),
                traceback=tb
            )
            if event:
                self.scribe.log_action(event)

            return {
                "status": "error",
                "reason": "strategy_planning_error",
                "error": str(e)
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
        
        # Load state
        state_path = Path("data/state/twitter_state.json")
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
            user_data = {"username": author, "bio": "", "name": ""} # In real implementation, fetch full user profile
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
                "type": "recruitment" if is_bot else "reply"
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
            "drafts_file": str(output_path)
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
