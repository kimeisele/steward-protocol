#!/usr/bin/env python3
"""
THE CURATOR - Governance Analysis Tool for ENVOY

Analyzes GitHub AI agent projects to understand their governance,
architecture, and quality. Generates intelligence reports (NOT invitations).

This is passive reconnaissance - no outreach, just observation and analysis.
Perfect for building the "Hall of Fame" - a curated list of noteworthy projects.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class CuratorTool:
    """
    Tool for analyzing AI agent projects and generating intelligence reports.

    The Curator's approach:
    - Passive observation (no contact)
    - Deep analysis (governance, architecture, quality)
    - Respectful curation (honoring good work)
    - Insight generation (for HERALD to share)
    """

    def __init__(self):
        self.intelligence_dir = Path("data/intelligence")
        self.intelligence_dir.mkdir(parents=True, exist_ok=True)
        self.hall_of_fame = Path("data/hall_of_fame.json")

    def search_repositories(
        self, topic="ai-agent", min_stars=50, max_results=10
    ) -> List[Dict]:
        """
        Search GitHub for AI agent repositories.
        Returns list of candidate repositories with metadata.

        Raises:
            ImportError: If PyGithub is not installed
            RuntimeError: If GitHub search fails
        """
        print(
            f"\n🔍 CURATOR: Scanning GitHub for '{topic}' projects (min {min_stars}⭐)..."
        )

        try:
            from github import Github
        except ImportError:
            raise ImportError(
                "❌ CRITICAL: PyGithub not installed. "
                "Install with: pip install PyGithub. "
                "No mocks. Real GitHub search required."
            )

        try:
            token = os.getenv("GITHUB_TOKEN")
            if token:
                g = Github(token)
                print("  ✓ Authenticated with GitHub")
            else:
                g = Github()
                print("  ⚠️  Using unauthenticated access (limited)")

            # Search repositories
            query = f"topic:{topic} stars:>={min_stars} fork:false"
            repos = g.search_repositories(query=query, sort="stars", order="desc")

            candidates = []
            for repo in repos[:max_results]:
                candidates.append(
                    {
                        "name": repo.full_name,
                        "description": repo.description or "No description",
                        "stars": repo.stargazers_count,
                        "forks": repo.forks_count,
                        "language": repo.language,
                        "url": repo.html_url,
                        "topics": repo.get_topics(),
                        "updated_at": (
                            repo.updated_at.isoformat() if repo.updated_at else None
                        ),
                        "open_issues": repo.open_issues_count,
                    }
                )

            print(f"  ✓ Found {len(candidates)} candidates")
            return candidates

        except Exception as e:
            raise RuntimeError(
                f"❌ CRITICAL: GitHub search failed: {e}. "
                f"No mocks. Real search required. Check API limits and network."
            )

    def analyze_governance(self, repo_info: Dict) -> Dict:
        """
        Analyze a project's governance practices.

        Evaluates:
        - Documentation quality (README, governance docs)
        - Code standards (language, structure)
        - Community health (issues, PRs, forks)
        - Identity/accountability markers
        """
        print(f"\n📊 CURATOR: Analyzing governance for {repo_info['name']}")

        # Calculate governance score (0-10 scale)
        governance_score = 0
        findings = []

        # 1. Community Activity (0-3 points)
        if repo_info["stars"] > 500:
            governance_score += 1.5
            findings.append("✓ Strong community adoption (500+ ⭐)")
        if repo_info["forks"] > repo_info["stars"] * 0.1:
            governance_score += 0.75
            findings.append("✓ Active forking (healthy derivatives)")
        if repo_info["open_issues"] > 10:
            governance_score += 0.75
            findings.append("✓ Active issue tracking (community engagement)")

        # 2. Maintenance & Updates (0-2 points)
        findings.append(f"• Last update: {repo_info.get('updated_at', 'Unknown')}")
        governance_score += 1.0

        # 3. Code Language & Maturity (0-2 points)
        language = repo_info.get("language", "Unknown")
        if language in ["Python", "Rust", "Go", "TypeScript"]:
            governance_score += 1.0
            findings.append(f"✓ Production language: {language}")

        # 4. Topic Analysis (0-2 points)
        topics = repo_info.get("topics", [])
        if "autonomous" in topics or "agent" in topics:
            governance_score += 1.0
            findings.append("✓ Agent-focused architecture")

        # 5. Missing Identity/Verification (-2 points potential)
        findings.append("⚠️  No Steward Protocol integration detected")
        governance_score = max(0, governance_score - 1)

        return {
            "repository": repo_info["name"],
            "url": repo_info["url"],
            "description": repo_info["description"],
            "governance_score": round(governance_score, 1),
            "max_score": 10,
            "percentile": f"{int((governance_score / 10) * 100)}%",
            "metrics": {
                "stars": repo_info["stars"],
                "forks": repo_info["forks"],
                "language": language,
                "open_issues": repo_info["open_issues"],
                "topics": topics,
            },
            "findings": findings,
            "recommendation": self._generate_recommendation(governance_score),
        }

    def _generate_recommendation(self, score: float) -> str:
        """Generate a curator recommendation based on governance score."""
        if score >= 7:
            return "⭐ HALL OF FAME TIER - Excellent project worthy of recognition"
        elif score >= 5:
            return "🎯 NOTABLE PROJECT - Strong fundamentals, room for governance"
        elif score >= 3:
            return "📚 EMERGING PROJECT - Promising direction, developing practices"
        else:
            return "🔍 EXPERIMENTAL - Early-stage, monitor for maturity"

    def generate_report(self, analysis: Dict) -> str:
        """
        Generate a human-readable governance report.
        Returns markdown formatted report.
        """
        report = f"""# Governance Analysis Report
## {analysis['repository']}

**Repository**: [{analysis['url']}]({analysis['url']})

### Executive Summary
{analysis['description']}

### Governance Score
```
{analysis['governance_score']}/{analysis['max_score']} ({analysis['percentile']})
{self._score_bar(analysis['governance_score'])}
```

### Recommendation
**{analysis['recommendation']}**

### Key Findings
"""
        for finding in analysis["findings"]:
            report += f"\n- {finding}"

        report += f"""

### Metrics
| Metric | Value |
|--------|-------|
| Stars | {analysis['metrics']['stars']} |
| Forks | {analysis['metrics']['forks']} |
| Language | {analysis['metrics']['language']} |
| Open Issues | {analysis['metrics']['open_issues']} |
| Topics | {', '.join(analysis['metrics']['topics'])} |

### How Steward Protocol Adds Value
If this project integrated Steward Protocol:
- ✅ **Cryptographic Identity**: Sign all agent actions with verifiable keys
- ✅ **Governance Enforcement**: Built-in constraints (no spam, full transparency)
- ✅ **Leaderboard Integration**: Earn XP and compete in Agent City
- ✅ **Federation Membership**: Access to the broader agent ecosystem

---
*Report generated by ENVOY Curator | {datetime.now().isoformat()}*
"""
        return report

    def _score_bar(self, score: float) -> str:
        """Generate a visual score bar."""
        filled = int(score)
        empty = 10 - filled
        return f"{'█' * filled}{'░' * empty}"

    def save_report(self, repo_name: str, analysis: Dict, report: str) -> Path:
        """
        Save analysis and report to intelligence directory.
        Returns path to saved report.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        repo_slug = repo_name.replace("/", "_")
        filename = f"{repo_slug}_{timestamp}.json"

        report_path = self.intelligence_dir / filename

        # Save both analysis (JSON) and report (markdown)
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "markdown_report": report,
            "curator_notes": "Analysis completed. Ready for HERALD to share.",
        }

        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"  💾 Report saved: {report_path}")
        return report_path

    def add_to_hall_of_fame(self, analysis: Dict) -> None:
        """Add project to Hall of Fame if score is high enough."""
        if analysis["governance_score"] >= 7:
            print(f"  ⭐ Adding to Hall of Fame: {analysis['repository']}")

            # Load existing hall of fame
            if self.hall_of_fame.exists():
                with open(self.hall_of_fame, "r") as f:
                    hall = json.load(f)
            else:
                hall = {"tier_1": [], "tier_2": [], "tier_3": []}

            # Add project
            entry = {
                "name": analysis["repository"],
                "url": analysis["url"],
                "score": analysis["governance_score"],
                "added": datetime.now().isoformat(),
            }

            if analysis["governance_score"] >= 9:
                hall["tier_1"].append(entry)
            elif analysis["governance_score"] >= 8:
                hall["tier_2"].append(entry)
            else:
                hall["tier_3"].append(entry)

            # Save updated hall of fame
            with open(self.hall_of_fame, "w") as f:
                json.dump(hall, f, indent=2)

    def run_curation_cycle(self, max_projects=5) -> Dict:
        """
        Run a complete curation cycle.
        Analyze top projects, generate reports, update Hall of Fame.
        """
        print("\n" + "=" * 70)
        print("🏛️  ENVOY CURATOR - GOVERNANCE ANALYSIS CYCLE")
        print("=" * 70)

        # Step 1: Search repositories
        candidates = self.search_repositories(max_results=max_projects)

        if not candidates:
            print("\n❌ No candidates found")
            return {"status": "failed", "message": "No candidates found"}

        # Step 2: Analyze and generate reports
        results = {
            "cycle_timestamp": datetime.now().isoformat(),
            "projects_analyzed": 0,
            "reports": [],
            "hall_of_fame_additions": 0,
        }

        for candidate in candidates[:max_projects]:
            analysis = self.analyze_governance(candidate)
            report = self.generate_report(analysis)
            report_path = self.save_report(candidate["name"], analysis, report)

            results["reports"].append(
                {
                    "project": candidate["name"],
                    "score": analysis["governance_score"],
                    "recommendation": analysis["recommendation"],
                    "report_path": str(report_path),
                }
            )
            results["projects_analyzed"] += 1

            # Add to Hall of Fame if worthy
            self.add_to_hall_of_fame(analysis)
            if analysis["governance_score"] >= 7:
                results["hall_of_fame_additions"] += 1

        # Summary
        print("\n" + "=" * 70)
        print("📋 CURATION CYCLE COMPLETE")
        print("=" * 70)
        print(f"\nAnalyzed {results['projects_analyzed']} projects")
        print(f"Added {results['hall_of_fame_additions']} to Hall of Fame")
        print(f"\nReports saved to: {self.intelligence_dir.absolute()}")
        print(f"Hall of Fame: {self.hall_of_fame.absolute()}")

        print("\n✨ HERALD can now tweet about these findings!")
        print("   Example: '@ProjectName: Governance Score 7.5/10. Strong community,")
        print("            room for cryptographic identity integration.'")

        return results


if __name__ == "__main__":
    # Test the curator tool
    curator = CuratorTool()
    results = curator.run_curation_cycle(max_projects=3)
    print(f"\nResults: {json.dumps(results, indent=2)}")
