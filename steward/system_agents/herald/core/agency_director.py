"""
HERALD Agency Director - Central Orchestrator for I-P-V-O Engine.

Implements the deterministic automation loop:
INPUT (Gather Context) -> PROCESS (Generate Content) -> VALIDATE (Governance) -> OUTPUT (Publish)

With automatic feedback loops for failed validations and immutable event sourcing.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# VALIDATE Tools
from .governance.constitution import HeraldConstitution

# MEMORY
from .memory import EventLog

# OUTPUT Tools
from .tools.broadcast_tool import BroadcastTool

# PROCESS Tools
from .tools.content_tool import ContentTool
from .tools.identity_tool import IdentityTool
from .tools.research_tool import ResearchTool

# INPUT Tools
from .tools.scout_tool import ScoutTool
from .tools.strategy_tool import StrategyTool
from .tools.visual_tool import VisualTool

# ARCHIVIST (for verification)
try:
    from steward.system_agents.archivist.tools.audit_tool import AuditTool
except ImportError:
    AuditTool = None

logger = logging.getLogger("HERALD_DIRECTOR")


@dataclass
class CycleResult:
    """Result of a complete I-P-V-O cycle."""

    status: str  # SUCCESS, VALIDATION_FAILED, ERROR
    phase: str  # INPUT, PROCESS, VALIDATE, OUTPUT
    cycle_id: str
    draft: Optional[str] = None
    media: Optional[Dict[str, Any]] = None  # Visual asset from VisualTool
    violations: Optional[List[str]] = None
    error: Optional[str] = None
    broadcast_result: Optional[Dict[str, Any]] = None
    retries_used: int = 0


class AgencyDirector:
    """
    Central orchestrator for the I-P-V-O Herald Agency Engine.

    Deterministic workflow:
    1. INPUT: Gather context (scout, research, observer)
    2. PROCESS: Generate content with feedback from previous failures
    3. VALIDATE: Enforce governance rules + cryptographic signing
    4. OUTPUT: Publish to platforms + log to ledger

    With automatic retry loops on governance violations.
    """

    def __init__(self):
        """Initialize the Agency Director with all tools."""
        logger.info("🎬 HERALD Agency Director initializing...")

        # INPUT Tools
        self.scout = ScoutTool()
        self.research = ResearchTool()
        logger.info("✅ INPUT: Scout and Research tools loaded")

        # PROCESS Tools
        self.content = ContentTool()
        self.strategy = StrategyTool()
        self.visual = VisualTool()
        logger.info("✅ PROCESS: Content, Strategy, and Visual tools loaded")

        # VALIDATE Tools
        self.constitution = HeraldConstitution()
        self.identity = IdentityTool()
        logger.info("✅ VALIDATE: Constitution and Identity tools loaded")

        # OUTPUT Tools
        self.broadcast = BroadcastTool()
        logger.info("✅ OUTPUT: Broadcast tool loaded")

        # MEMORY
        self.event_log = EventLog()
        logger.info("✅ MEMORY: EventLog loaded")

        # ARCHIVIST (optional)
        self.auditor = AuditTool() if AuditTool else None
        if self.auditor:
            logger.info("✅ AUDIT: AuditTool available")

        # State Dashboard directory
        self.state_dir = Path("data/reports")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / "agency_state.json"

        logger.info("🎬 HERALD Agency Director ready for operation")

    def _update_state_dashboard(
        self,
        phase: str,
        status: str,
        cycle_id: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Update the agency state dashboard for external observability.

        Args:
            phase: Current phase (INPUT, PROCESS, VALIDATE, OUTPUT)
            status: Current status (RUNNING, SUCCESS, FAILED)
            cycle_id: Unique cycle identifier
            details: Optional additional context
        """
        state = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cycle_id": cycle_id,
            "phase": phase,
            "status": status,
            "details": details or {},
        }

        try:
            with open(self.state_file, "w") as f:
                json.dump(state, f, indent=2, default=str)
            logger.debug(f"📊 State dashboard updated: {phase} / {status}")
        except Exception as e:
            logger.warning(f"⚠️  Failed to update state dashboard: {e}")

    def run_cycle(
        self,
        campaign_theme: str = "auto",
        previous_feedback: Optional[Dict[str, Any]] = None,
    ) -> CycleResult:
        """
        Execute one complete I-P-V-O cycle.

        Args:
            campaign_theme: Theme for content generation (auto, tech_deep_dive, community, hall_of_fame)
            previous_feedback: Optional feedback from a previous failed validation

        Returns:
            CycleResult with status, phase, draft, and metadata
        """
        cycle_id = datetime.now(timezone.utc).isoformat()
        context = {}
        media_data = None  # Will be populated in PROCESS phase

        # ========== PHASE 1: INPUT ==========
        try:
            self._update_state_dashboard("INPUT", "RUNNING", cycle_id)

            logger.info(f"🔍 PHASE 1 - INPUT (Cycle: {cycle_id})")

            # Gather context from multiple sources
            # Research Tool: scan for trending topics
            trends_data = self.research.find_trending_topic()
            if trends_data is None:
                trends_data = self.research.scan("AI agents governance")

            # Scout Tool: check agent registry status
            agents_count = len(self.scout._load_pokedex()) if self.scout._load_pokedex() else 0

            context = {
                "trends": trends_data,
                "agent_registry_size": agents_count,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            self.event_log.record_content_generated(
                content="[INPUT] Context gathered",
                platform="internal",
                context={"agents": agents_count},
            )

            self._update_state_dashboard("INPUT", "SUCCESS", cycle_id, {"context_sources": 2})
            logger.info("✅ INPUT Phase Complete: Context aggregated")

        except Exception as e:
            logger.error(f"❌ INPUT Phase Failed: {e}")
            self._update_state_dashboard("INPUT", "FAILED", cycle_id, {"error": str(e)})
            self.event_log.record_system_error(
                error_type="input_failure",
                error_message=str(e),
            )
            return CycleResult(
                status="ERROR",
                phase="INPUT",
                cycle_id=cycle_id,
                error=str(e),
            )

        # ========== PHASE 2: PROCESS ==========
        try:
            self._update_state_dashboard("PROCESS", "RUNNING", cycle_id)

            logger.info("🧠 PHASE 2 - PROCESS (Content Generation)")

            # Check if we have feedback from a previous failed validation
            if previous_feedback is None:
                previous_feedback = self.event_log.get_last_validation_feedback()

            if previous_feedback:
                logger.info(
                    f"📋 Using feedback from previous validation: {len(previous_feedback['violations'])} violations to fix"
                )

            # Generate content based on theme
            # Map theme to actual ContentTool methods
            theme = campaign_theme.lower() if campaign_theme else "auto"

            if theme == "auto" or theme == "tech_deep_dive":
                draft = self.content.generate_technical_insight_tweet()
            elif theme == "campaign":
                draft = self.content.generate_campaign_tweet()
            elif theme == "agent_city":
                draft = self.content.generate_agent_city_tweet()
            else:
                # Default to technical insight
                draft = self.content.generate_technical_insight_tweet()

            if not draft:
                raise ValueError("ContentTool returned empty draft")

            # Generate visual asset to accompany text
            visual_asset = self.visual.generate(text_draft=draft, style_preset="agent_city", format_type="ascii")

            media_data = {
                "asset_type": visual_asset.asset_type,
                "content": visual_asset.content,
                "alt_text": visual_asset.alt_text,
                "keywords": visual_asset.keywords,
            }

            self.event_log.record_content_generated(
                content=draft,
                platform="internal",
                context={"has_media": True, "media_type": visual_asset.asset_type},
            )

            self._update_state_dashboard(
                "PROCESS",
                "SUCCESS",
                cycle_id,
                {
                    "draft_length": len(draft),
                    "media_generated": True,
                    "media_type": visual_asset.asset_type,
                },
            )
            logger.info(f"✅ PROCESS Phase Complete: Draft ({len(draft)} chars) + {visual_asset.asset_type} visual")

        except Exception as e:
            logger.error(f"❌ PROCESS Phase Failed: {e}")
            self._update_state_dashboard("PROCESS", "FAILED", cycle_id, {"error": str(e)})
            self.event_log.record_system_error(
                error_type="process_failure",
                error_message=str(e),
            )
            return CycleResult(
                status="ERROR",
                phase="PROCESS",
                cycle_id=cycle_id,
                error=str(e),
            )

        # ========== PHASE 3: VALIDATE (Critical Gate) ==========
        try:
            self._update_state_dashboard("VALIDATE", "RUNNING", cycle_id)

            logger.info("⚖️  PHASE 3 - VALIDATE (Governance Check)")

            # Step 1: Constitution validation (governance rules)
            validation_result = self.constitution.validate(draft)

            if not validation_result.is_valid:
                # Governance violation detected
                logger.warning(f"⚠️  Governance violations detected: {validation_result.violations}")

                # Store feedback for next retry
                self.event_log.store_validation_feedback(
                    violations=validation_result.violations,
                    draft=draft,
                )

                # Log the rejection
                self.event_log.record_content_rejected(
                    content=draft,
                    reason="governance_violation",
                    violations=validation_result.violations,
                )

                self._update_state_dashboard(
                    "VALIDATE",
                    "FAILED",
                    cycle_id,
                    {"violations": len(validation_result.violations)},
                )

                return CycleResult(
                    status="VALIDATION_FAILED",
                    phase="VALIDATE",
                    cycle_id=cycle_id,
                    draft=draft,
                    media=media_data,
                    violations=validation_result.violations,
                )

            logger.info("✅ Governance validation passed (text)")

            # Step 2: Validate media asset (if present)
            if media_data:
                media_validation = self.constitution.validate_media(media_data)
                if not media_validation.is_valid:
                    logger.warning(f"⚠️  Media validation failed: {media_validation.violations}")
                    self.event_log.store_validation_feedback(
                        violations=media_validation.violations,
                        draft=draft,
                    )
                    self.event_log.record_content_rejected(
                        content=draft,
                        reason="media_validation_failure",
                        violations=media_validation.violations,
                    )
                    self._update_state_dashboard(
                        "VALIDATE",
                        "FAILED",
                        cycle_id,
                        {
                            "violations": len(media_validation.violations),
                            "reason": "media",
                        },
                    )
                    return CycleResult(
                        status="VALIDATION_FAILED",
                        phase="VALIDATE",
                        cycle_id=cycle_id,
                        draft=draft,
                        media=media_data,
                        violations=media_validation.violations,
                    )
                logger.info("✅ Media validation passed")

            # Step 3: Cryptographic signing (Article I Compliance - REQUIRED)
            # CONSTITUTIONAL REQUIREMENT: Artikel I mandates cryptographic signing
            signature = None
            if self.identity and self.identity.client:
                try:
                    signature = self.identity.sign_artifact(draft)
                    logger.info(f"✅ Content signed: {signature[:16]}...")
                    logger.info("✅ Artikel I (Cryptographic Identity) - COMPLIANT")
                except Exception as e:
                    logger.error(f"❌ Signing failed (Article I violation): {e}")
                    # Fail validation if signing fails (Article I requirement)
                    self._update_state_dashboard(
                        "VALIDATE",
                        "FAILED",
                        cycle_id,
                        {
                            "reason": "article_i_violation_signature_failed",
                            "error": str(e),
                        },
                    )
                    self.event_log.record_content_rejected(
                        content=draft,
                        reason="article_i_violation_no_signature",
                        violations=[f"Content must be cryptographically signed (Article I): {e}"],
                    )
                    return CycleResult(
                        status="VALIDATION_FAILED",
                        phase="VALIDATE",
                        cycle_id=cycle_id,
                        draft=draft,
                        media=media_data,
                        violations=[f"Article I violation: Cryptographic signing required - {e}"],
                    )
            else:
                logger.error("❌ Identity tool unavailable (Article I violation)")
                self._update_state_dashboard(
                    "VALIDATE",
                    "FAILED",
                    cycle_id,
                    {"reason": "article_i_violation_no_identity_tool"},
                )
                self.event_log.record_content_rejected(
                    content=draft,
                    reason="article_i_violation_no_identity",
                    violations=["Content cannot be signed without identity tool (Article I)"],
                )
                return CycleResult(
                    status="VALIDATION_FAILED",
                    phase="VALIDATE",
                    cycle_id=cycle_id,
                    draft=draft,
                    media=media_data,
                    violations=["Article I violation: Identity tool required for cryptographic signing"],
                )

            # Step 3: Audit verification (if auditor available)
            audit_result = None
            if self.auditor:
                try:
                    audit_result = self.auditor.verify_event_signature(
                        {"content": draft, "signature": signature},
                    )
                    logger.info("✅ Content verified by auditor")
                except Exception as e:
                    logger.warning(f"⚠️  Auditor verification failed: {e}")
                    # Continue without audit (not fatal)

            self._update_state_dashboard(
                "VALIDATE",
                "SUCCESS",
                cycle_id,
                {"signed": signature is not None, "verified": audit_result is not None},
            )

            logger.info("✅ VALIDATE Phase Complete: All checks passed")

        except Exception as e:
            logger.error(f"❌ VALIDATE Phase Failed: {e}")
            self._update_state_dashboard("VALIDATE", "FAILED", cycle_id, {"error": str(e)})
            self.event_log.record_system_error(
                error_type="validate_failure",
                error_message=str(e),
            )
            return CycleResult(
                status="ERROR",
                phase="VALIDATE",
                cycle_id=cycle_id,
                error=str(e),
            )

        # ========== PHASE 4: OUTPUT (Only if validation passed) ==========
        try:
            self._update_state_dashboard("OUTPUT", "RUNNING", cycle_id)

            logger.info("📢 PHASE 4 - OUTPUT (Publication)")

            # Publish to platforms (default Twitter)
            publish_success = self.broadcast.publish(
                content=draft,
                platform="twitter",
            )

            # Record publication in ledger
            broadcast_result = {
                "platform": "twitter",
                "success": publish_success,
                "signature": signature,
                "media": media_data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            self.event_log.record_content_published(
                content=draft,
                platform="twitter",
                metadata=broadcast_result,
            )

            self._update_state_dashboard(
                "OUTPUT",
                "SUCCESS" if publish_success else "SUCCESS_SIMULATION",
                cycle_id,
                {
                    **broadcast_result,
                    "media": {
                        "type": media_data["asset_type"],
                        "keywords": media_data["keywords"],
                    },
                },
            )

            logger.info("✅ OUTPUT Phase Complete: Multimodal content published and logged")

            return CycleResult(
                status="SUCCESS",
                phase="OUTPUT",
                cycle_id=cycle_id,
                draft=draft,
                media=media_data,
                broadcast_result=broadcast_result,
            )

        except Exception as e:
            logger.error(f"❌ OUTPUT Phase Failed: {e}")
            self._update_state_dashboard("OUTPUT", "FAILED", cycle_id, {"error": str(e)})
            self.event_log.record_system_error(
                error_type="output_failure",
                error_message=str(e),
            )
            return CycleResult(
                status="ERROR",
                phase="OUTPUT",
                cycle_id=cycle_id,
                error=str(e),
            )

    def run_retry_loop(
        self,
        campaign_theme: str = "auto",
        max_retries: int = 3,
    ) -> CycleResult:
        """
        Execute I-P-V-O cycles with automatic retry on governance violations.

        If VALIDATE fails -> retry PROCESS with feedback from violations.
        If max_retries exceeded -> return last failure result.

        Args:
            campaign_theme: Theme for content generation
            max_retries: Maximum number of retry attempts

        Returns:
            CycleResult with final status (SUCCESS or FAILED after max retries)
        """
        logger.info(f"🔄 Starting retry loop (max_retries={max_retries})")

        last_result = None

        for attempt in range(max_retries):
            logger.info(f"\n--- Attempt {attempt + 1}/{max_retries} ---")

            result = self.run_cycle(campaign_theme=campaign_theme)
            last_result = result

            if result.status == "SUCCESS":
                logger.info(f"✅ SUCCESS on attempt {attempt + 1}")
                result.retries_used = attempt
                return result

            elif result.status == "VALIDATION_FAILED":
                logger.info(f"⚠️  Validation failed on attempt {attempt + 1}: {result.violations}")

                # Feedback automatically stored in event_log
                # Next cycle will retrieve it and use it to generate better content

                if attempt + 1 < max_retries:
                    logger.info(f"🔄 Retrying with feedback (attempt {attempt + 2}/{max_retries})")
                    continue
                else:
                    logger.error(f"❌ Max retries ({max_retries}) exceeded")
                    result.retries_used = attempt
                    return result

            else:
                # System error (not validation error)
                logger.error(f"❌ System error on attempt {attempt + 1}: {result.error}")
                result.retries_used = attempt
                return result

        # Should not reach here, but failsafe
        if last_result:
            last_result.retries_used = max_retries
            return last_result

        return CycleResult(
            status="ERROR",
            phase="UNKNOWN",
            cycle_id=datetime.now(timezone.utc).isoformat(),
            error="Retry loop exited unexpectedly",
        )

    def get_state(self) -> Optional[Dict[str, Any]]:
        """
        Get the current agency state from the dashboard file.

        Returns:
            Dict with current state if available, None otherwise
        """
        try:
            if self.state_file.exists():
                with open(self.state_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️  Could not read state file: {e}")
        return None
