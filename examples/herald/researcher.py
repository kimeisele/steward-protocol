#!/usr/bin/env python3
"""
HERALD Researcher Module
Gives HERALD "eyes" for trend detection and intelligent content generation

Powered by Tavily API for AI/Tech-focused web search
Enables research-driven, current-events-aware content generation

Architecture:
- Tavily Search API: Fetch trending topics
- Relevance Scoring: Filter for STEWARD-relevant content
- Source Attribution: Track and cite sources
- Fallback Strategy: Graceful degradation if API unavailable
"""

import os
import requests
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict


class TavilyResearcher:
    """
    HERALD's Research Module
    Searches web for AI/Protocol/Web3 trends and provides research summaries

    Requires:
    - TAVILY_API_KEY (from https://tavily.com)

    Search Strategy:
    - Focus: AI Agents, Autonomous Systems, Blockchain Protocols
    - Frequency: Daily
    - Max Results: 5 per query
    - Relevance: Only STEWARD-relevant topics
    """

    def __init__(self):
        """Initialize Tavily API researcher."""
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.api_url = "https://api.tavily.com/search"

        # Research keywords for STEWARD-relevant content
        self.keywords = [
            "AI agents autonomous",
            "agent protocols standards",
            "cryptographic verification agents",
            "agent budget governance",
            "sovereign AI",
            "verifiable AI",
        ]

        # Sources we trust for research
        self.trusted_domains = [
            "github.com",
            "arxiv.org",
            "dev.to",
            "medium.com",
            "huggingface.co",
            "openai.com",
            "anthropic.com",
            "news.ycombinator.com",
        ]

    def search(self, query: str, max_results: int = 5) -> Optional[Dict]:
        """
        Search Tavily for trending content.

        Args:
            query (str): Search query (e.g., "AI agents autonomous")
            max_results (int): Max results to return (default 5)

        Returns:
            dict: Search results with articles, or None if API unavailable
        """
        if not self.api_key:
            print("⚠️  No TAVILY_API_KEY found. Research mode disabled.")
            return None

        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "include_answer": True,
        }

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=15
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️  Tavily API error: {response.status_code}")
                return None

        except requests.RequestException as e:
            print(f"⚠️  Network error searching Tavily: {e}")
            return None

    def score_relevance(self, article: Dict) -> float:
        """
        Score article relevance to STEWARD Protocol themes.

        Scores higher for:
        - Agent/autonomous system topics
        - Verification/trust/security themes
        - Budget/cost management discussions
        - Protocol standards

        Args:
            article (dict): Article from search results

        Returns:
            float: Relevance score 0.0-1.0
        """
        title = article.get("title", "").lower()
        content = article.get("content", "").lower()
        url = article.get("url", "").lower()

        score = 0.0

        # Keywords boost
        agent_keywords = ["agent", "autonomous", "ai", "bot"]
        trust_keywords = ["verify", "trust", "secure", "sign", "attest"]
        protocol_keywords = ["protocol", "standard", "spec", "governance"]
        budget_keywords = ["budget", "cost", "spend", "constraint"]

        for keyword in agent_keywords:
            if keyword in title:
                score += 0.3
            if keyword in content[:500]:  # Check first 500 chars
                score += 0.1

        for keyword in trust_keywords:
            if keyword in title:
                score += 0.2
            if keyword in content[:500]:
                score += 0.1

        for keyword in protocol_keywords:
            if keyword in title:
                score += 0.2

        for keyword in budget_keywords:
            if keyword in title:
                score += 0.15

        # Domain boost for trusted sources
        for domain in self.trusted_domains:
            if domain in url:
                score += 0.1
                break

        # Normalize to 0-1 range
        return min(score, 1.0)

    def find_trending_topic(self, min_relevance: float = 0.5) -> Optional[Dict]:
        """
        Find trending AI/Protocol topic with research context.

        Searches through STEWARD-relevant keywords and returns
        the most relevant article with highest score.

        Args:
            min_relevance (float): Minimum relevance score to consider (default 0.5)

        Returns:
            dict: Best article + research context, or None if nothing found
        """
        best_article = None
        best_score = 0.0
        search_query_used = None

        # Try each keyword until we find relevant content
        for keyword in self.keywords:
            print(f"🔍 Searching: {keyword}...")
            results = self.search(keyword)

            if not results or "results" not in results:
                continue

            # Score each result
            for article in results.get("results", []):
                score = self.score_relevance(article)

                if score > best_score and score >= min_relevance:
                    best_score = score
                    best_article = article
                    search_query_used = keyword

            # If we found something good enough, stop searching
            if best_score >= min_relevance:
                break

        if best_article:
            return {
                "article": best_article,
                "score": best_score,
                "search_query": search_query_used,
                "found_at": datetime.now().isoformat(),
            }

        return None

    def extract_summary(self, topic: Dict) -> Dict:
        """
        Extract research summary from trending topic.

        Args:
            topic (dict): Result from find_trending_topic()

        Returns:
            dict: Structured research data for content generation
        """
        article = topic.get("article", {})

        return {
            "title": article.get("title", ""),
            "url": article.get("url", ""),
            "content_preview": article.get("content", "")[:300],
            "relevance_score": topic.get("score", 0.0),
            "search_query": topic.get("search_query", ""),
            "timestamp": datetime.now().isoformat(),
        }


class ResearchReport:
    """
    Compiled research findings ready for content generation.

    Can be passed to ContentGenerator for intelligent response creation.
    """

    def __init__(self, topic: Dict):
        """Initialize from trending topic research."""
        self.topic = topic
        self.research = TavilyResearcher().extract_summary(topic)
        self.created_at = datetime.now()

    def to_prompt(self) -> str:
        """
        Convert research to a prompt for LLM-based content generation.

        Returns:
            str: Structured prompt for content generation
        """
        return f"""
Research Finding:
Title: {self.research['title']}
URL: {self.research['url']}
Relevance: {self.research['relevance_score']:.1%}

Content Preview:
{self.research['content_preview']}

Task:
Create a compelling Twitter hot take and a longer LinkedIn post about this topic,
explaining how STEWARD Protocol provides solutions to the problems/opportunities
mentioned in this article.

Focus on:
1. Agent identity verification
2. Budget governance
3. Cryptographic trust
4. Verifiable operations

Include the source URL and relevant hashtags.
"""

    def save_to_file(self, output_dir: str = "content/research") -> Path:
        """
        Save research findings to file for archival.

        Args:
            output_dir (str): Directory to save research

        Returns:
            Path: Path to saved file
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        filename = Path(output_dir) / f"{self.created_at.strftime('%Y-%m-%d_%H%M%S')}_research.json"

        with open(filename, "w") as f:
            json.dump(
                {
                    "research": self.research,
                    "created_at": self.created_at.isoformat(),
                },
                f,
                indent=2
            )

        print(f"💾 Research saved: {filename}")
        return filename


# Demo/Test Mode
if __name__ == "__main__":
    print("🔍 HERALD RESEARCHER - Test Mode")
    print("=" * 60)

    researcher = TavilyResearcher()

    if researcher.api_key:
        print("✅ TAVILY_API_KEY found - Research mode available")
        print("\n🔎 Searching for trending STEWARD-relevant topics...")

        # Try to find a trending topic
        topic = researcher.find_trending_topic(min_relevance=0.5)

        if topic:
            print(f"\n✅ Found: {topic['article']['title']}")
            print(f"   Score: {topic['score']:.1%}")
            print(f"   URL: {topic['article']['url']}")

            # Create research report
            report = ResearchReport(topic)
            print(f"\n📋 Research Report Generated")
            print(f"   Prompt Preview: {report.to_prompt()[:100]}...")
        else:
            print("⚠️  No highly relevant articles found in current searches")
    else:
        print("⚠️  TAVILY_API_KEY not configured")
        print("   To enable research mode:")
        print("   1. Go to https://tavily.com")
        print("   2. Sign up and get API key")
        print("   3. Add TAVILY_API_KEY to GitHub Secrets")
        print("   4. HERALD will gain research capabilities!")

    print("=" * 60)
