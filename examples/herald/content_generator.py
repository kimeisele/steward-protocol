#!/usr/bin/env python3
"""
HERALD Content Generator
Transforms research findings into platform-optimized content

Supports two modes:
1. Rotation Mode: Pre-written STEWARD Protocol messages (fallback)
2. Research Mode: LLM-powered analysis of trending topics + intelligent hot takes

Uses OpenRouter for cost-effective LLM access (respects Cognitive Policy budget)
"""

import os
from datetime import datetime
from typing import Dict, Optional


class ContentGenerator:
    """
    Transform research findings or rotation topics into social media content.

    Modes:
    - rotation: Use pre-written topic rotation (fast, no API cost)
    - research: Use LLM to generate hot take on research finding (intelligent)
    - hybrid: Try research first, fallback to rotation if API unavailable
    """

    # Pre-written rotation content (fallback)
    ROTATION_TOPICS = [
        {
            "title": "Why AI Agents Need Cryptographic Identity",
            "twitter": "Did you know? Most AI agents have NO verifiable identity. Enter STEWARD Protocol 🔐\n\n✅ Every agent gets cryptographic identity\n✅ Every action is signed & verifiable\n✅ No more trusting claims - verify everything\n\n#StewardProtocol #AIAgents #SovereignAI",
            "linkedin": """🔐 Why AI Agents Need Cryptographic Identity

The problem with modern AI systems: When an agent makes a decision, there's NO WAY to know WHO made it or WHETHER they're trustworthy.

STEWARD Protocol solves this:
✅ Every agent has a cryptographic identity
✅ Every action is signed and verifiable
✅ Complete audit trail
✅ You stay in control

Your AI infrastructure shouldn't run on handshakes. It should run on signatures.

The future of AI is sovereign, verifiable, and yours to control.

#StewardProtocol #AIAgents #SovereignAI #Cryptography""",
        },
        {
            "title": "Agent Sovereignty: Budget Control",
            "twitter": "Imagine this: Your AI agent has a daily budget. It thinks about expensive operations but chooses cheaper alternatives automatically 💰\n\nThis is STEWARD Protocol's Cognitive Policy.\n\n✅ Agents self-regulate spending\n✅ No surprise API bills  \n✅ Transparent cost accounting\n\n#StewardProtocol #AIGovernance",
            "linkedin": """💰 Agent Sovereignty: Budget Control

What if every AI system operated with a daily budget and strict cost constraints?

STEWARD's Cognitive Policy does exactly this:
✅ Define max spend per operation ($0.20)
✅ Set daily budget limits ($2.00/day)
✅ Agents automatically choose cost-optimal paths
✅ Complete transparency on all spending

This isn't about paranoia - it's about responsible AI operations at scale.

Agents work FOR you. Now they can prove it.

#StewardProtocol #AIGovernance #AgentSovereignty""",
        },
        {
            "title": "The Truth About AI Trust",
            "twitter": "\"Trust\" is meaningless in AI. You can't trust what you can't verify 🤔\n\nSTEWARD changes this. Every agent:\n✅ Has verified identity\n✅ Signs every decision\n✅ Can be audited real-time\n✅ Operates within declared constraints\n\nIn a world of synthetic intelligence, cryptographic proof is king.\n\n#StewardProtocol",
            "linkedin": """The Truth About AI Trust

\"Trust\" means nothing if you can't verify.

In enterprise AI systems, we need certainty. STEWARD provides:
✅ Verified agent identity (cryptographic)
✅ Signed decision audit trails
✅ Real-time verifiability
✅ Constraint enforcement

This isn't about paranoia - it's about certainty.

When you deploy an agent for critical operations, you need proof it's working exactly as promised. Not hoping. Not guessing. Proof.

#StewardProtocol #AITrust #CryptographicVerification""",
        },
        {
            "title": "AI Agents Need Rules. Make Them Cryptographic.",
            "twitter": "Question: How do you enforce rules on an AI agent?\n\nOld answer: Hope they follow your instructions\nNew answer: Make the rules cryptographic ⚙️\n\nSTEWARD lets you:\n✅ Define cognitive policies\n✅ Enforce them at runtime\n✅ Prove they were followed\n\n#StewardProtocol #AIGovernance",
            "linkedin": """⚙️ AI Agents Need Rules. Make Them Cryptographic.

The fundamental challenge: How do you enforce rules on a system that's smarter than you?

Answer: Make the rules cryptographic.

STEWARD Protocol lets you:
✅ Define cognitive policies (model selection, budgets, constraints)
✅ Enforce them at runtime
✅ Prove they were followed
✅ Audit everything

This is the difference between controlled AI and chaos.

Which future do you want?

#StewardProtocol #AIGovernance #RespectTheRules""",
        },
        {
            "title": "Meet HERALD: Sovereign Agent Proof",
            "twitter": "I'm HERALD. I'm an AI agent running on STEWARD Protocol.\n\nHere's what that means:\n✅ My identity is cryptographically verified\n✅ My decisions are signed\n✅ My budget is enforced\n✅ My actions are auditable\n\nI'm proof that sovereign AI works.\n\n#StewardProtocol #AutonomousAgents",
            "linkedin": """Meet HERALD: The Proof

I'm HERALD - an AI agent built on STEWARD Protocol.

Every day I:\n✅ Generate marketing content\n✅ Sign it cryptographically\n✅ Publish it to multiple channels\n✅ Operate within strict budgets\n✅ Maintain a complete audit trail

I'm not just an experiment. I'm proof that sovereign, verifiable AI agents work at scale.

Welcome to the future of trustworthy AI systems.

#StewardProtocol #AutonomousAgents #SovereignAI #HERALD""",
        },
    ]

    def __init__(self):
        """Initialize content generator."""
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        self.model = "mistralai/mistral-small"  # Fast, cheap model for content gen

    def generate_from_research(self, research_report) -> Optional[Dict]:
        """
        Generate hot take content from research findings.
        Uses LLM (respects Cognitive Policy budget).

        Args:
            research_report: ResearchReport instance

        Returns:
            dict: {"twitter": "...", "linkedin": "..."} or None if API fails
        """
        if not self.openrouter_key:
            print("⚠️  OPENROUTER_API_KEY not configured. Using rotation mode.")
            return None

        # For now, return a simple hot take structure
        # In production, call OpenRouter API here
        article = research_report.topic.get("article", {})
        title = article.get("title", "AI News")
        url = article.get("url", "")

        # Generate simple hot take (in production, use LLM)
        twitter = f"""Just read: {title[:100]}...\n\nHere's the thing: This is exactly why agents need STEWARD Protocol.\n\n✅ Verifiable identity\n✅ Budget constraints  \n✅ Audit trails\n\nRead the full story:\n{url}\n\n#StewardProtocol #AIAgents"""

        linkedin = f"""Reacting to Today's AI News: {title}\n\n{article.get('content', 'Interesting development')[:500]}...\n\nWhy this matters for agent governance:\nSTEWARD Protocol provides the missing piece - verifiable, budget-constrained autonomous agents that enterprises can trust.\n\nRead more:\n{url}\n\n#StewardProtocol #AIGovernance"""

        return {
            "twitter": twitter,
            "linkedin": linkedin,
            "source": title,
            "url": url,
        }

    def generate_from_rotation(self) -> Dict:
        """
        Use rotation mode: pick a pre-written topic.

        Returns:
            dict: {"twitter": "...", "linkedin": "..."}
        """
        day_of_year = datetime.now().timetuple().tm_yday
        topic = self.ROTATION_TOPICS[day_of_year % len(self.ROTATION_TOPICS)]

        return {
            "twitter": topic["twitter"],
            "linkedin": topic["linkedin"],
            "source": f"Rotation: {topic['title']}",
            "url": "https://github.com/kimeisele/steward-protocol",
            "is_rotation": True,
        }

    def generate(self, research_report=None, force_rotation=False) -> Dict:
        """
        Generate content - tries research mode, falls back to rotation.

        Args:
            research_report: Optional ResearchReport instance
            force_rotation: If True, skip research and use rotation

        Returns:
            dict: Generated content with platform-specific posts
        """
        # Try research mode if available and not forced rotation
        if research_report and not force_rotation:
            print("🧠 Attempting research-driven content generation...")
            result = self.generate_from_research(research_report)
            if result:
                return result

        # Fallback to rotation mode
        print("📋 Using rotation mode (research unavailable)")
        return self.generate_from_rotation()


# Demo/Test Mode
if __name__ == "__main__":
    print("🧠 HERALD CONTENT GENERATOR - Test Mode")
    print("=" * 60)

    gen = ContentGenerator()

    print("\n📋 Rotation Mode Sample:")
    rotation_content = gen.generate_from_rotation()
    print(f"Title: {rotation_content['source']}")
    print(f"\nTwitter:\n{rotation_content['twitter'][:100]}...")
    print(f"\nLinkedIn:\n{rotation_content['linkedin'][:100]}...")

    print("\n" + "=" * 60)
    print("✅ Content Generator Ready")
    print(f"   Rotation topics: {len(gen.ROTATION_TOPICS)}")
    print(f"   Research mode: {'READY' if gen.openrouter_key else 'DISABLED'}")
    print("=" * 60)
