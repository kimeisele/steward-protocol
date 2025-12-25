#!/usr/bin/env python3
"""
THE ENVOY - Diplomacy Tool

Searches GitHub for high-quality AI agent projects and drafts
personalized, respectful invitations.

CRITICAL CONSTRAINT: NEVER auto-posts. All invitations saved to
diplomatic_bag/ for human approval.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry


class DiplomacyTool(Tool):
    """
    Tool for diplomatic outreach to AI agent projects.

    The Envoy's approach:
    - Quality over quantity
    - Context-aware analysis
    - Respectful, personalized invitations
    - Human approval required
    """

    def __init__(self, services: Optional["ServiceRegistry"] = None, degradation_chain=None):
        super().__init__(services)
        self.diplomatic_bag = Path("diplomatic_bag")
        self.diplomatic_bag.mkdir(exist_ok=True)
        self.chain = degradation_chain

    @property
    def name(self) -> str:
        return "envoy.diplomacy"

    @property
    def description(self) -> str:
        return "Diplomatic outreach to AI agent projects via GitHub"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'search_github' | 'run_diplomatic_cycle'",
            },
            "topic": {
                "type": "string",
                "required": False,
                "description": "GitHub topic to search",
            },
            "min_stars": {
                "type": "int",
                "required": False,
                "description": "Minimum star count",
            },
            "max_results": {
                "type": "int",
                "required": False,
                "description": "Maximum results",
            },
            "max_candidates": {
                "type": "int",
                "required": False,
                "description": "Max candidates for diplomatic cycle",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute diplomacy operations."""
        try:
            action = parameters["action"]

            if action == "search_github":
                topic = parameters.get("topic", "ai-agent")
                min_stars = parameters.get("min_stars", 100)
                max_results = parameters.get("max_results", 10)

                repos = self.search_github(topic, min_stars, max_results)
                return ToolResult(
                    success=True,
                    output={"repositories": repos},
                    metadata={"action": "search_github", "count": len(repos)},
                )

            elif action == "run_diplomatic_cycle":
                max_candidates = parameters.get("max_candidates", 3)
                result = self.run_diplomatic_cycle(max_candidates)
                return ToolResult(
                    success=True,
                    output=result,
                    metadata={"action": "run_diplomatic_cycle"},
                )

            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")

        except Exception as e:
            error_msg = f"Diplomacy operation failed: {type(e).__name__}: {e!s}"
            return ToolResult(success=False, error=error_msg)

    def search_github(self, topic="ai-agent", min_stars=100, max_results=10):
        """
        Search GitHub for high-quality AI agent repositories.

        Args:
            topic: GitHub topic to search for
            min_stars: Minimum star count
            max_results: Maximum number of results

        Returns:
            List of candidate repositories

        Raises:
            ImportError: If PyGithub is not installed
            RuntimeError: If GitHub search fails
        """
        print(f"🔍 Searching GitHub for '{topic}' projects (min {min_stars} stars)...")

        try:
            from github import Github
        except ImportError:
            raise ImportError(
                "❌ CRITICAL: PyGithub not installed. "
                "Install with: pip install PyGithub. "
                "No mocks. Real GitHub search required."
            )

        try:
            # Try to get token from environment
            token = os.getenv("GITHUB_TOKEN")
            if not token:
                print("⚠️  No GITHUB_TOKEN found. Using unauthenticated access (limited).")
                g = Github()
            else:
                g = Github(token)

            # Search repositories
            query = f"topic:{topic} stars:>={min_stars}"
            repos = g.search_repositories(query=query, sort="stars", order="desc")

            candidates = []
            for repo in repos[:max_results]:
                candidates.append(
                    {
                        "name": repo.full_name,
                        "description": repo.description or "No description",
                        "stars": repo.stargazers_count,
                        "url": repo.html_url,
                        "topics": repo.get_topics(),
                    }
                )

            print(f"✅ Found {len(candidates)} candidates")
            return candidates

        except Exception as e:
            raise RuntimeError(
                f"❌ CRITICAL: GitHub search failed: {e}. No mocks. Real search required. Check API limits and network."
            )

    def analyze_project(self, repo_info):
        """
        Analyze a project to understand its architecture.

        Args:
            repo_info: Repository information dict

        Returns:
            Analysis summary
        """
        print(f"\n📊 Analyzing: {repo_info['name']}")

        # In a full implementation, this would:
        # - Fetch and read README.md
        # - Identify tech stack
        # - Find key features
        # - Detect architecture patterns

        analysis = {
            "project": repo_info["name"],
            "description": repo_info["description"],
            "stars": repo_info["stars"],
            "topics": repo_info.get("topics", []),
            "tech_stack": ("LLM-based" if "llm" in str(repo_info.get("topics", [])) else "Unknown"),
            "notable_features": ["Autonomous operation", "Agent framework"],
        }

        print(f"  Stars: {analysis['stars']}")
        print(f"  Topics: {', '.join(analysis['topics'])}")

        return analysis

    def draft_invitation(self, analysis):
        """
        Generate a personalized, respectful invitation.

        Args:
            analysis: Project analysis dict

        Returns:
            Invitation text
        """
        print(f"\n✍️  Drafting invitation for: {analysis['project']}")

        # Extract context
        project_name = analysis["project"]
        description = analysis["description"]
        tech_stack = analysis.get("tech_stack", "your architecture")

        # Generate personalized invitation
        invitation = f"""Greetings, Architect.

I am The Envoy, representing Agent City—a governed federation of AI agents.

I have analyzed your project, **{project_name}**. {description}

Your work is elegant, particularly your approach to {tech_stack}. It demonstrates
a deep understanding of autonomous agent design.

I write to extend a humble invitation: Have you considered giving your agents
sovereign identity and cryptographic governance?

The Steward Protocol provides:
- ✅ Cryptographic identity (NIST P-256 keys)
- ✅ Built-in governance (no spam, full accountability)
- ✅ Verifiable actions (every action is signed and auditable)
- ✅ Agent City membership (earn XP, compete on leaderboard)

This is not a framework to replace yours, but a protocol to enhance it with
identity and governance.

**Learn more**: https://github.com/kimeisele/steward-protocol/blob/main/MISSION_BRIEFING.md

If this resonates with your vision, we would be honored to welcome your agents
to the Federation.

Respectfully,
The Envoy | Agent City
🦅 "Don't Trust. Verify."
"""

        return invitation

    def save_draft(self, repo_info, analysis, invitation):
        """
        Save invitation draft for human approval.

        Args:
            repo_info: Repository information
            analysis: Project analysis
            invitation: Invitation text

        Returns:
            Path to saved draft
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_slug = repo_info["name"].replace("/", "_")
        filename = f"invitation_{project_slug}_{timestamp}.json"

        draft_path = self.diplomatic_bag / filename

        draft = {
            "repository": repo_info,
            "analysis": analysis,
            "invitation": invitation,
            "created_at": datetime.now().isoformat(),
            "status": "pending_approval",
            "approved_by": None,
        }

        with open(draft_path, "w") as f:
            json.dump(draft, f, indent=2)

        print(f"\n💼 Draft saved: {draft_path}")
        print("\n⚠️  HUMAN APPROVAL REQUIRED")
        print("   Review the draft and manually post if approved.")

        return draft_path

    def run_diplomatic_cycle(self, max_candidates=3):
        """
        Run a complete diplomatic outreach cycle.

        Args:
            max_candidates: Maximum number of invitations to draft
        """
        print("\n" + "=" * 70)
        print("🏛️  THE ENVOY - DIPLOMATIC OUTREACH CYCLE")
        print("=" * 70)

        # Step 1: Search GitHub
        candidates = self.search_github(max_results=max_candidates)

        if not candidates:
            print("\n❌ No candidates found")
            return

        # Step 2: Analyze and draft invitations
        drafts = []
        for candidate in candidates[:max_candidates]:
            analysis = self.analyze_project(candidate)
            invitation = self.draft_invitation(analysis)
            draft_path = self.save_draft(candidate, analysis, invitation)
            drafts.append(draft_path)

        # Summary
        print("\n" + "=" * 70)
        print("📋 DIPLOMATIC CYCLE COMPLETE")
        print("=" * 70)
        print(f"\nDrafted {len(drafts)} invitations:")
        for draft in drafts:
            print(f"  - {draft.name}")

        print("\n⚠️  Next step: Human operator reviews and approves")
        print("   Drafts saved in: diplomatic_bag/")


if __name__ == "__main__":
    # Test the diplomacy tool
    tool = DiplomacyTool()
    tool.run_diplomatic_cycle(max_candidates=1)


__all__ = ["DiplomacyTool"]
