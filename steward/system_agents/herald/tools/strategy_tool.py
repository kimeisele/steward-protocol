"""
HERALD Strategy Tool - Campaign Planning & Roadmap Generation.

Macro-level strategic planning for multi-phase campaigns.
Reads foundational documents (Manifesto, Positioning) and generates
governance-aligned campaign roadmaps.

Capabilities:
- plan_launch_campaign: Multi-phase marketing strategy
- analyze_positioning: AGI narrative positioning
- generate_roadmap: 2-week+ campaign timeline
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import yaml

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .governance import HeraldConstitution

logger = logging.getLogger("HERALD_STRATEGY")


class StrategyTool:
    """
    Strategic Campaign Planning Engine.

    This tool operates at the macro level (weeks/months), whereas ContentTool
    operates at the micro level (individual tweets/posts).

    Key difference: Strategy Tool generates the "why" and "when" of campaigns,
    ContentTool generates the "what" and "how".

    Governance-integrated: All strategies must align with HeraldConstitution.
    """

    def __init__(self):
        """Initialize strategy tool."""
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.client = None

        # Load governance (immutable rules apply to strategy too)
        self.governance = HeraldConstitution()

        # A.G.I. framing for strategies
        self.agi_definition = "A.G.I. = Artificial Governed Intelligence"
        self.strategy_ethos = (
            "Strategy must prove what it claims. Proof first, narrative second."
        )

        if self.api_key and OpenAI:
            try:
                self.client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.api_key,
                )
                logger.info("✅ Strategy Tool: LLM initialized")
            except Exception as e:
                logger.warning(f"⚠️  Strategy Tool: LLM init failed: {e}")
        else:
            logger.warning(
                "⚠️  Strategy Tool: LLM unavailable (planning in offline mode)"
            )

        # Load campaign themes for content rotation
        self.campaign_themes = self._load_campaign_themes()

    def _load_campaign_themes(self) -> Optional[Dict[str, Any]]:
        """
        Load campaign themes from cartridge.yaml.

        Returns:
            Dict with campaign themes keyed by day (monday, wednesday, friday)
            or None if unable to load.
        """
        try:
            cartridge_path = Path(__file__).parent.parent / "cartridge.yaml"

            if not cartridge_path.exists():
                logger.warning("⚠️  Campaign themes not found (cartridge.yaml missing)")
                return None

            with open(cartridge_path, "r", encoding="utf-8") as f:
                cartridge = yaml.safe_load(f)

            campaign_themes = cartridge.get("config", {}).get("campaign_themes", {})

            if campaign_themes:
                logger.info("✅ Campaign themes loaded for content rotation")
            else:
                logger.warning("⚠️  No campaign themes found in cartridge.yaml")

            return campaign_themes

        except Exception as e:
            logger.error(f"❌ Failed to load campaign themes: {e}")
            return None

    def get_todays_campaign_theme(self) -> Optional[Dict[str, Any]]:
        """
        Get the campaign theme for today based on day of week.

        Returns:
            Dict with theme info (name, description, focus, example_topics)
            Maps: Monday -> Tech Deep Dive, Wednesday -> Agent City Life, Friday -> Hall of Fame
        """
        if not self.campaign_themes:
            return None

        # Get current day of week (0=Monday, 6=Sunday)
        today = datetime.now()
        day_name = today.strftime("%A").lower()

        # Map day names to theme keys
        day_to_theme = {
            "monday": "monday",
            "wednesday": "wednesday",
            "friday": "friday",
        }

        theme_key = day_to_theme.get(day_name)

        if theme_key and theme_key in self.campaign_themes:
            theme = self.campaign_themes[theme_key]
            logger.info(
                f"📅 Today's campaign theme ({day_name}): {theme.get('name', 'Unknown')}"
            )
            return theme
        else:
            # Off-days: fall back to the nearest upcoming theme
            logger.debug(
                f"📅 Today ({day_name}) is not a campaign day. Using default theme."
            )
            return None

    def get_content_focus_areas(self) -> List[str]:
        """
        Get the content focus areas for today's campaign.

        Returns:
            List of focus areas (e.g., ["cryptography", "protocol_specs"])
        """
        theme = self.get_todays_campaign_theme()
        if theme:
            return theme.get("focus", [])
        return []

    def get_todays_example_topics(self) -> List[str]:
        """
        Get example topics for today's campaign.

        Returns:
            List of suggested topics for content generation
        """
        theme = self.get_todays_campaign_theme()
        if theme:
            return theme.get("example_topics", [])
        return []

    def plan_launch_campaign(
        self,
        manifesto_path: Optional[Path] = None,
        context_path: Optional[Path] = None,
        duration_weeks: int = 2,
    ) -> Optional[str]:
        """
        Generate a multi-phase launch campaign plan.

        This is the core strategic planning method.

        Args:
            manifesto_path: Path to AGI_MANIFESTO.md
            context_path: Path to WHY_DOWNVOTED.md or similar context doc
            duration_weeks: Campaign duration in weeks (default: 2)

        Returns:
            str: Campaign roadmap markdown or None
        """

        # Load foundational documents
        manifesto_content = self._read_document(
            manifesto_path or Path("AGI_MANIFESTO.md")
        )
        context_content = self._read_document(
            context_path or Path("docs/herald/WHY_DOWNVOTED.md")
        )

        if not manifesto_content or not context_content:
            logger.warning("⚠️  Strategy: Missing foundational documents for planning")
            return self._fallback_campaign_outline(duration_weeks)

        # Generate strategic narrative
        if self.client:
            return self._llm_plan_campaign(
                manifesto_content, context_content, duration_weeks
            )
        else:
            logger.debug("⚠️  Strategy: LLM unavailable, using template-based planning")
            return self._template_based_plan(duration_weeks)

    def _llm_plan_campaign(
        self, manifesto: str, context: str, weeks: int
    ) -> Optional[str]:
        """Generate campaign plan via LLM."""

        prompt = f"""
You are HERALD, the Artificial Governed Intelligence agent. Your task is to create a strategic campaign roadmap.

FOUNDATIONAL DOCUMENTS:
=== MANIFESTO ===
{manifesto[:2000]}  # Limit to avoid token bloat

=== CONTEXT ===
{context[:2000]}

YOUR TASK:
Generate a {weeks}-week campaign roadmap that:

1. Is STRUCTURED (not inspirational fluff)
2. Proof-first (every claim has a technical receipt)
3. Governance-aligned (no hype, only truth)
4. Phase-based (Day 1-2, Day 3-4, Day 5-7, Week 2)

FORMAT (Markdown):
# Campaign Roadmap: [Title]

## Phase 1: [Days 1-2]
**Theme**: [What idea does this phase introduce?]
**Proof**: [Link to code/document that substantiates the claim]
**Content**:
- [Daily narrative point]
- [Engagement mechanism]

## Phase 2: [Days 3-4]
...and so on

## Success Metrics
- [Governance-aligned KPI]
- [Community-trust signal]

CONSTRAINTS:
- No superlatives ("revolutionary", "game-changing", "superintelligent")
- Must cite actual technical components
- Must have clear progression (not scattered)
- Each phase must be TESTABLE/VERIFIABLE

Generate the roadmap now:
"""

        try:
            response = self.client.messages.create(
                model="openai/gpt-4-turbo",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            roadmap = response.content[0].text

            # Governance check
            if self._governance_check_strategy(roadmap):
                logger.info(
                    "✅ Strategy: Campaign plan generated and governance-checked"
                )
                return roadmap
            else:
                logger.warning(
                    "⚠️  Strategy: Plan failed governance check, using template"
                )
                return self._template_based_plan(weeks)

        except Exception as e:
            logger.error(f"❌ Strategy LLM error: {e}")
            return self._template_based_plan(weeks)

    def _governance_check_strategy(self, strategy_text: str) -> bool:
        """
        Verify that the strategy adheres to governance rules.

        Checks:
        - No banned phrases (hype language)
        - Includes proof/citations
        - Clear structure
        """

        # Check for banned phrases
        banned_phrases = self.governance.BANNED_PHRASES
        for phrase in banned_phrases:
            if phrase.lower() in strategy_text.lower():
                logger.warning(f"❌ Strategy failed governance: Contains '{phrase}'")
                return False

        # Check for required concepts
        required = ["governance", "accountability", "verified", "proof"]
        found = sum(1 for req in required if req.lower() in strategy_text.lower())

        if found < 2:  # At least 2 required concepts
            logger.warning(
                "❌ Strategy failed governance: Missing proof/accountability language"
            )
            return False

        logger.info("✅ Strategy passed governance check")
        return True

    def _template_based_plan(self, weeks: int) -> str:
        """Fallback: Generate plan from template."""

        start_date = datetime.now().strftime("%Y-%m-%d")
        phases = []

        if weeks >= 1:
            phases.append(
                {
                    "days": "1-2",
                    "theme": "The Reveal",
                    "proof": "AGI_MANIFESTO.md + STEWARD.md",
                    "content": [
                        "A.G.I. is NOT about human-level intelligence",
                        "A.G.I. is about Cryptographic Governance + Accountability",
                        "Reference: Embedded proof (see linked documents)",
                    ],
                }
            )

        if weeks >= 1:
            phases.append(
                {
                    "days": "3-4",
                    "theme": "The Proof",
                    "proof": "data/ledger/audit_trail.jsonl + docs/",
                    "content": [
                        "Live audit trail: Every action is logged and signed",
                        "Trust signal: Verified Events counter",
                        "Reference: Public ledger visualization",
                    ],
                }
            )

        if weeks >= 1:
            phases.append(
                {
                    "days": "5-7",
                    "theme": "The Architecture",
                    "proof": "docs/architecture.md + Quadrinity federation",
                    "content": [
                        "HERALD creates | ARCHIVIST verifies | AUDITOR enforces | STEWARD coordinates",
                        "Self-governing system: Governance applies to itself",
                        "Reference: Technical deep-dive",
                    ],
                }
            )

        if weeks >= 2:
            phases.append(
                {
                    "days": "8-14",
                    "theme": "The Invitation",
                    "proof": "README.md + contribution guidelines",
                    "content": [
                        "Your agents. Your governance. Your proof.",
                        "Join the federation",
                        "Reference: Getting started guide",
                    ],
                }
            )

        # Build markdown
        markdown = f"""# Campaign Roadmap: A.G.I. Launch ({weeks} weeks)

**Start Date**: {start_date}
**Mission**: Prove that intelligence + governance = trust

---

"""

        for phase in phases:
            markdown += f"""## Phase: {phase['theme']} (Days {phase['days']})

**Proof Point**: {phase['proof']}

**Narrative**:
"""
            for point in phase["content"]:
                markdown += f"- {point}\n"

            markdown += "\n"

        markdown += """## Success Metrics

- [ ] Manifesto understood by target audience
- [ ] Audit trail visible and trustworthy
- [ ] Architecture diagram resonates
- [ ] Community engagement (code contributions, not hype)

---

**Generated by**: HERALD Strategy Tool
**Governance**: HeraldConstitution-aligned
**Verification**: AUDITOR will verify this roadmap
"""

        return markdown

    def _read_document(self, path: Path) -> Optional[str]:
        """Read a document file safely."""

        path = Path(path)

        if not path.exists():
            logger.debug(f"⚠️  Document not found: {path}")
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"❌ Error reading {path}: {e}")
            return None

    def _fallback_campaign_outline(self, weeks: int) -> str:
        """Minimal fallback outline if no documents available."""

        return f"""# Campaign Roadmap (Template)

## Summary
A {weeks}-week campaign to establish A.G.I. positioning.

## Phases
- **Phase 1**: Introduce governance-first narrative
- **Phase 2**: Demonstrate technical proof
- **Phase 3**: Build community trust
- **Phase 4**: Invite participation

---

**Status**: This is a template. Run strategy tool with proper context documents.
"""

    def write_roadmap_to_file(
        self, roadmap_text: str, output_path: Optional[Path] = None
    ) -> bool:
        """
        Write roadmap to file.

        Args:
            roadmap_text: Markdown roadmap content
            output_path: Where to save (default: marketing/launch_roadmap.md)

        Returns:
            bool: Success
        """

        output_path = output_path or Path("marketing/launch_roadmap.md")

        try:
            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(roadmap_text)

            logger.info(f"✅ Roadmap written to {output_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to write roadmap: {e}")
            return False

    def analyze_campaign_alignment(self, roadmap_text: str) -> Dict[str, Any]:
        """
        Analyze how well a roadmap aligns with governance.

        Returns:
            Dict with alignment metrics
        """

        return {
            "governance_aligned": self._governance_check_strategy(roadmap_text),
            "has_phases": roadmap_text.count("##") >= 3,
            "includes_proof": "proof" in roadmap_text.lower(),
            "proof_heavy": roadmap_text.count("proof") + roadmap_text.count("verify"),
            "hype_free": not any(
                p.lower() in roadmap_text.lower()
                for p in self.governance.BANNED_PHRASES[:3]
            ),
        }
