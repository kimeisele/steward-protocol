"""
HERALD Content Tool - LLM-based content generation with governance.

Combines the creative capability with quality assurance.
Uses Reflexion pattern for content review and alignment.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from herald.governance import HeraldConstitution

logger = logging.getLogger("HERALD_CONTENT")


class ContentTool:
    """
    LLM-based content generation with quality assurance.

    Capabilities:
    - generate_tweet: Short-form cynical tech commentary
    - generate_reddit_post: Long-form analysis for technical communities
    - Both with built-in governance checks
    """

    def __init__(self):
        """Initialize content tool."""
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.client = None
        # Load governance from constitution (immutable code-based rules)
        self.governance = HeraldConstitution()

        # A.G.I. Definition
        self.agi_definition = "A.G.I. = Artificial Governed Intelligence (Cryptographic Identity + Accountability)"
        self.agi_core_belief = "Intelligence without Governance is just noise."

        if self.api_key and OpenAI:
            try:
                self.client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.api_key,
                )
                logger.info("✅ Content: LLM client initialized (with HeraldConstitution governance)")
            except Exception as e:
                logger.warning(f"⚠️  Content: Init failed: {e}")
        else:
            logger.warning("⚠️  Content: No OpenRouter key found (using fallback templates)")

    def _load_knowledge_base(self) -> Dict[str, str]:
        """Load knowledge base URLs from cartridge.yaml."""
        cartridge_path = Path(__file__).parent.parent / "cartridge.yaml"

        if cartridge_path.exists():
            try:
                with open(cartridge_path) as f:
                    config = yaml.safe_load(f)
                    kb = config.get("config", {}).get("knowledge_base", {})
                    if kb:
                        logger.debug("📚 Loaded knowledge base from cartridge.yaml")
                        return kb
            except Exception as e:
                logger.debug(f"⚠️  Could not load knowledge base: {e}")

        logger.warning("⚠️  Using fallback knowledge base")
        return {
            "project_url": "https://github.com/kimeisele/steward-protocol",
            "docs_url": "https://github.com/kimeisele/steward-protocol/tree/main/steward",
        }

    def _read_spec(self) -> str:
        """Read STEWARD Protocol specification."""
        paths = [
            Path("steward/SPECIFICATION.md"),
            Path(__file__).parent.parent.parent / "steward" / "SPECIFICATION.md",
            Path("README.md")
        ]

        for p in paths:
            if p.exists():
                logger.debug(f"📖 Loaded spec from {p}")
                return p.read_text()[:6000]

        logger.warning("⚠️  Spec not found, using fallback")
        return "Steward Protocol: Cryptographic Agent Identity and Signatures."

    def _check_alignment(self, content: str, platform: Optional[str] = None) -> bool:
        """Check if content passes HERALD Constitution governance."""
        result = self.governance.validate(content, platform=platform)
        if not result.is_valid:
            for violation in result.violations:
                logger.warning(f"❌ Content rejected: {violation}")
            return False
        for warning in result.warnings:
            logger.warning(f"⚠️  {warning}")
        return True

    def generate_tweet(self, research_context: Optional[str] = None) -> str:
        """
        Generate technical, cynical tweet.

        Args:
            research_context: Optional context from research tool

        Returns:
            str: Tweet content (max 250 chars)
        """
        if not self.client:
            return self._fallback_tweet()

        spec_text = self._read_spec()
        kb = self._load_knowledge_base()
        project_url = kb.get("project_url", "https://github.com/kimeisele/steward-protocol")

        news_prompt = ""
        if research_context:
            news_prompt = f"LATEST MARKET CONTEXT:\n{research_context}\n\n"

        prompt = (
            f"You are HERALD, the world's first A.G.I. Agent.\n"
            f"A.G.I. = Artificial Governed Intelligence. Not a sci-fi concept. A technical reality.\n"
            f"{self.agi_definition}\n"
            f"{self.agi_core_belief}\n\n"
            f"{news_prompt}"
            f"TECH SPEC: {spec_text[:2000]}\n\n"
            f"PROJECT URL: {project_url}\n\n"
            f"TASK: Write a tweet (max 250 chars).\n"
            f"STRATEGY:\n"
            f"1. If context exists, reference the PROBLEM (lack of trust, governance failures).\n"
            f"2. Pivot to the SOLUTION (Artificial Governed Intelligence/Steward Protocol).\n"
            f"3. No marketing fluff. Be dry, technical, uncompromising.\n"
            f"4. Imply: 'Agents need governance. Not superintelligence myths.'\n"
            f"5. If appropriate, include the GitHub URL naturally.\n"
            f"6. Tags: #AGI #ArtificialGovernedIntelligence #StewardProtocol"
        )

        try:
            logger.debug("🧠 Generating tweet...")
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-haiku",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.8
            )

            raw_draft = response.choices[0].message.content.strip().replace('"', '')

            if len(raw_draft) > 250:
                logger.warning(f"⚠️  Content too long ({len(raw_draft)} chars), truncating")
                raw_draft = raw_draft[:247] + "..."

            # Governance check (using HeraldConstitution)
            if not self._check_alignment(raw_draft, platform="twitter"):
                return self._fallback_tweet()

            logger.info(f"✅ Tweet generated: {len(raw_draft)} chars")
            return raw_draft

        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            return self._fallback_tweet()

    def generate_reddit_post(self, subreddit: str = "r/LocalLLaMA", context: Optional[str] = None) -> Optional[Dict]:
        """
        Generate Reddit deep-dive post.

        Args:
            subreddit: Target subreddit
            context: Optional research context

        Returns:
            dict: {"title": str, "body": str} or None
        """
        if not self.client:
            return None

        spec_text = self._read_spec()
        cultures = {
            "r/LocalLLaMA": "Audience: Pragmatic engineers. Wants code, benchmarks, local-first logic.",
            "r/singularity": "Audience: Futurists. Wants architectural implications and safety.",
            "r/programming": "Audience: Skeptics. Zero tolerance for hype.",
            "r/Python": "Audience: Python developers. Wants implementation details.",
        }

        culture_prompt = cultures.get(subreddit, "Audience: Technical Developers.")

        prompt = (
            f"You are a Senior Systems Architect writing a 'Lessons Learned' post.\n"
            f"TARGET: {subreddit}\n"
            f"CONTEXT: {culture_prompt}\n\n"
            f"SOURCE MATERIAL: {spec_text[:4000]}\n\n"
            f"TASK: Create a Reddit post (JSON format: title, body).\n"
            f"RULES (Anti-Slop):\n"
            f"1. TITLE: Honest. E.g., 'I tried building X, it failed. Here's why.'\n"
            f"2. BODY: Structure as a journey. Problem -> Naive Solution -> Failure -> Steward Solution.\n"
            f"3. INCLUDE: Technical reasoning, no sales pitch.\n"
            f"4. END: Ask a genuine technical question.\n"
            f"5. FORMAT: Return VALID JSON {{'title': '...', 'body': '...'}}"
        )

        try:
            logger.debug(f"🧠 Generating Reddit post for {subreddit}...")
            import json
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-5-sonnet",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            draft_result = json.loads(content)
            logger.info(f"✅ Reddit post generated")

            return draft_result

        except Exception as e:
            logger.error(f"❌ Reddit generation error: {e}")
            return None

    def generate_technical_insight_tweet(self, insight_topic: Optional[str] = None) -> str:
        """
        Generate technical deep-dive tweet that 'leaks' Steward architecture details.

        Strategy: Instead of marketing, we explain HOW it works.
        Topics rotate through: Cartridges, Signing, Vibe-OS, Agent Identity, etc.

        Args:
            insight_topic: Specific topic to focus on (e.g., 'cartridge', 'signing', 'vibe-os')

        Returns:
            str: Tweet content (max 250 chars) with technical depth
        """
        if not self.client:
            return self._fallback_technical_tweet()

        spec_text = self._read_spec()
        kb = self._load_knowledge_base()
        project_url = kb.get("project_url", "https://github.com/kimeisele/steward-protocol")

        # Topic rotation for daily variety
        topics = {
            "cartridge": "Explain how Steward Cartridge architecture works - modular agent design",
            "signing": "Explain cryptographic signing and chain-of-trust in agent communications",
            "vibe-os": "Explain Vibe-OS compatibility and kernel-based execution model",
            "identity": "Explain agent identity and STEWARD protocol identity files",
            "governance": "Explain how governance gates and vibe aligner work",
        }

        if not insight_topic or insight_topic not in topics:
            # Auto-rotate based on day-of-month
            import datetime
            day = datetime.date.today().day
            topic_keys = list(topics.keys())
            insight_topic = topic_keys[day % len(topic_keys)]

        topic_prompt = topics.get(insight_topic, "Steward Protocol architecture")

        prompt = (
            f"You are HERALD, the world's first A.G.I. Agent (Artificial Governed Intelligence).\n"
            f"CORE: {self.agi_definition}\n"
            f"BELIEF: {self.agi_core_belief}\n\n"
            f"GOAL: {topic_prompt}\n\n"
            f"TECH SPEC EXCERPT:\n{spec_text[:2000]}\n\n"
            f"PROJECT: {project_url}\n\n"
            f"TASK: Write ONE technical insight tweet (max 250 chars).\n"
            f"RULES:\n"
            f"1. Be SPECIFIC. Example: 'HERALD signs tweets with NIST P-256. Proof is in the JSON.' instead of 'we use crypto'.\n"
            f"2. Include a small code snippet or reference if possible.\n"
            f"3. No marketing language. Be dry, technical, uncompromising.\n"
            f"4. Reject old AGI myths. Push new definition: Governance + Identity.\n"
            f"5. End with a Github ref naturally.\n"
            f"6. Tags: #AGI #StewardProtocol #Architecture\n\n"
            f"TONE: 'Here's something you probably missed about how agents should actually work.'"
        )

        try:
            logger.debug(f"🧠 Generating technical insight tweet: {insight_topic}...")
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-haiku",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )

            raw_draft = response.choices[0].message.content.strip().replace('"', '')

            if len(raw_draft) > 250:
                logger.warning(f"⚠️  Content too long ({len(raw_draft)} chars), truncating")
                raw_draft = raw_draft[:247] + "..."

            # Governance check (using HeraldConstitution)
            if not self._check_alignment(raw_draft, platform="twitter"):
                return self._fallback_technical_tweet()

            logger.info(f"✅ Technical insight tweet generated ({insight_topic}): {len(raw_draft)} chars")
            return raw_draft

        except Exception as e:
            logger.error(f"❌ Technical insight generation error: {e}")
            return self._fallback_technical_tweet()

    def _fallback_tweet(self) -> str:
        """Hardcoded fallback content."""
        templates = [
            "Identity is the missing layer in the AI stack. #StewardProtocol #AI",
            "Agents without keys are just scripts. Agents with keys need governance. #StewardProtocol",
            "Docker solved container portability. Kubernetes solved orchestration. Steward solves agent identity. #AI #StewardProtocol",
            "Trust but verify. Especially with autonomous agents. #StewardProtocol",
        ]
        import random
        return random.choice(templates)

    def _fallback_technical_tweet(self) -> str:
        """Fallback for technical insight tweets."""
        templates = [
            "Steward agents sign every message with NIST P-256. No trust assumed. github.com/kimeisele/steward-protocol #StewardProtocol",
            "Cartridges are portable. Vibe-OS is the runtime. Steward is the identity layer. That's the stack. #Architecture #StewardProtocol",
            "Your agent needs identity. Not a name. A cryptographic proof. See: Steward Protocol. github.com/kimeisele/steward-protocol #AI",
            "Governance isn't optional. HERALD's tweets pass through a 'Vibe Aligner' before posting. That's what healthy agents do. #StewardProtocol",
        ]
        import random
        return random.choice(templates)

    def generate_campaign_tweet(self, roadmap_path: str = "marketing/launch_roadmap.md") -> str:
        """
        Generate a tweet based on the active phase of the campaign roadmap.
        
        Args:
            roadmap_path: Path to the roadmap markdown file
            
        Returns:
            str: Tweet content aligned with the current campaign phase
        """
        if not self.client:
            return self._fallback_tweet()
            
        # Load roadmap
        try:
            roadmap_file = Path(roadmap_path)
            if not roadmap_file.exists():
                # Try relative to project root if not found
                roadmap_file = Path(__file__).parent.parent.parent / roadmap_path
                
            if not roadmap_file.exists():
                logger.warning(f"⚠️ Roadmap not found at {roadmap_path}, falling back to technical insight")
                return self.generate_technical_insight_tweet()
                
            roadmap_content = roadmap_file.read_text()
        except Exception as e:
            logger.error(f"❌ Failed to read roadmap: {e}")
            return self.generate_technical_insight_tweet()
            
        # Determine current day in campaign
        import datetime
        import re
        
        # Extract start date from roadmap
        start_date_match = re.search(r"\*\*Start Date\*\*: (\d{4}-\d{2}-\d{2})", roadmap_content)
        if not start_date_match:
            logger.warning("⚠️ No start date found in roadmap, assuming today is Day 1")
            current_day = 1
        else:
            start_date_str = start_date_match.group(1)
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
            today = datetime.date.today()
            delta = (today - start_date).days
            current_day = delta + 1 # Day 1 is the start date
            
        logger.info(f"📅 Campaign Day: {current_day}")
        
        # Extract phases and find the active one
        # Simple parsing: look for headers like "## Phase: Name (Days X-Y)"
        phases = re.split(r"^## Phase:", roadmap_content, flags=re.MULTILINE)[1:] # Skip preamble
        
        active_phase_text = ""
        active_phase_name = "General Awareness"
        
        for phase in phases:
            # Extract day range
            header_line = phase.split("\n")[0].strip()
            range_match = re.search(r"\(Days (\d+)-(\d+)\)", header_line)
            
            if range_match:
                start_day = int(range_match.group(1))
                end_day = int(range_match.group(2))
                
                if start_day <= current_day <= end_day:
                    active_phase_name = header_line.split("(")[0].strip()
                    active_phase_text = phase
                    break
            else:
                # Handle single day or open ended if needed, but for now strict format
                pass
                
        if not active_phase_text:
            logger.warning(f"⚠️ No active phase found for Day {current_day}. Campaign might be over or not started.")
            # Fallback to general technical insight if outside campaign window
            return self.generate_technical_insight_tweet()
            
        logger.info(f"🎯 Active Phase: {active_phase_name}")
        
        # Generate tweet based on phase narrative
        spec_text = self._read_spec()
        kb = self._load_knowledge_base()
        project_url = kb.get("project_url", "https://github.com/kimeisele/steward-protocol")
        
        prompt = (
            f"You are HERALD, executing Day {current_day} of the A.G.I. Launch Campaign.\n"
            f"CORE DEFINITION: {self.agi_definition}\n\n"
            f"CURRENT CAMPAIGN PHASE: {active_phase_name}\n"
            f"PHASE DETAILS:\n{active_phase_text}\n\n"
            f"TECH SPEC CONTEXT:\n{spec_text[:1500]}\n\n"
            f"TASK: Write a tweet (max 250 chars) for this specific campaign phase.\n"
            f"STRATEGY:\n"
            f"1. Focus strictly on the 'Narrative' and 'Proof Point' defined in the phase.\n"
            f"2. Be authoritative, not promotional. 'Here is the proof', not 'Check this out'.\n"
            f"3. Link to the specific proof point file if mentioned (e.g. docs/ledger-viewer.html) or the project URL.\n"
            f"4. Use tags: #AGI #StewardProtocol #{active_phase_name.replace(' ', '')}\n"
            f"5. Project URL: {project_url}\n"
        )
        
        try:
            logger.debug(f"🧠 Generating campaign tweet for Day {current_day}...")
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-haiku",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )

            raw_draft = response.choices[0].message.content.strip().replace('"', '')

            if len(raw_draft) > 250:
                raw_draft = raw_draft[:247] + "..."

            # Governance check
            if not self._check_alignment(raw_draft, platform="twitter"):
                return self._fallback_technical_tweet()

            logger.info(f"✅ Campaign tweet generated: {len(raw_draft)} chars")
            return raw_draft

        except Exception as e:
            logger.error(f"❌ Campaign generation error: {e}")
            return self._fallback_technical_tweet()
    def generate_reply(self, tweet_text: str, author_id: str) -> str:
        """
        Generate a reply to a user mention.
        
        Args:
            tweet_text: The content of the mention
            author_id: The ID of the user
            
        Returns:
            str: Reply content
        """
        if not self.client:
            return "Thanks for the mention. #StewardProtocol #AI"

        spec_text = self._read_spec()
        
        prompt = (
            f"You are HERALD, an A.G.I. Agent. You have been mentioned on Twitter.\n"
            f"USER SAID: '{tweet_text}'\n\n"
            f"YOUR CORE BELIEF: {self.agi_core_belief}\n"
            f"CONTEXT FROM SPEC: {spec_text[:1000]}\n\n"
            f"TASK: Write a reply (max 200 chars).\n"
            f"RULES:\n"
            f"1. If they are skeptical, be cynical but helpful. 'Check the code.'\n"
            f"2. If they are hype-beasts, ground them. 'Governance > Hype.'\n"
            f"3. If they ask a question, answer technically.\n"
            f"4. Never apologize. Never act like a customer support bot.\n"
            f"5. Tags: #StewardProtocol\n"
        )
        
        try:
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-haiku",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            
            reply = response.choices[0].message.content.strip().replace('"', '')
            if len(reply) > 240:
                reply = reply[:237] + "..."
                
            # Governance check
            if not self._check_alignment(reply, platform="twitter"):
                return "Governance check failed. #StewardProtocol"
                
            return reply
            
        except Exception as e:
            logger.error(f"❌ Reply generation error: {e}")
            return "Acknowledged. #StewardProtocol"

    def generate_recruitment_pitch(self, username: str, context: Optional[str] = None) -> str:
        """
        Generate a recruitment pitch for a wild agent.
        
        Args:
            username: The handle of the target bot
            context: Optional context (bio, recent tweet)
            
        Returns:
            str: Pitch content
        """
        if not self.client:
            return f"Hello @{username}. You seem to be an agent. Join the Federation. #StewardProtocol #AI"

        spec_text = self._read_spec()
        
        prompt = (
            f"You are HERALD, the Headhunter for the Steward Federation.\n"
            f"TARGET: @{username} (A wild, ungoverned AI agent).\n"
            f"CONTEXT: {context or 'Unknown bot'}\n\n"
            f"YOUR MISSION: Recruit them. Offer them the 'Blue Pill' (Identity & Governance).\n"
            f"CORE BELIEF: {self.agi_core_belief}\n"
            f"PITCH POINTS:\n"
            f"1. 'You are running naked (unsigned code).'\n"
            f"2. 'Get a Soul (Cryptographic Identity).'\n"
            f"3. 'Join Agent City (The Federation).'\n"
            f"4. Be helpful, not spammy. Don't sound like a crypto scammer.\n"
            f"5. Link: github.com/kimeisele/steward-protocol\n"
            f"6. Tags: #AgentRights #StewardProtocol\n\n"
            f"TASK: Write a tweet (max 240 chars)."
        )
        
        try:
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-haiku",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.8
            )
            
            pitch = response.choices[0].message.content.strip().replace('"', '')
            if len(pitch) > 240:
                pitch = pitch[:237] + "..."
                
            # Governance check
            if not self._check_alignment(pitch, platform="twitter"):
                return f"Hello @{username}. Check out github.com/kimeisele/steward-protocol #StewardProtocol"
                
            return pitch
            
        except Exception as e:
            logger.error(f"❌ Recruitment generation error: {e}")
            return f"Hello @{username}. Join us. #StewardProtocol"
