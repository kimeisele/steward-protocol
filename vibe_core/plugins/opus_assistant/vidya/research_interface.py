"""
VIDYA Research Interface - Science Cartridge Orchestration.

OPUS-033: Orchestration over Implementation

"Opus doesn't Google. Opus commands the ScienceAgent to Google."
    - Senior Partner Directive

This module is a thin orchestration layer that wraps calls to the
existing Science Cartridge. We don't reimplement web search - we
delegate to the specialist.

Usage:
    from vibe_core.plugins.opus_assistant.vidya import ResearchInterface

    research = ResearchInterface()
    result = await research.query("Best practices for Python plugin architecture")
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol

logger = logging.getLogger("VIDYA.Research")


@dataclass
class ResearchResult:
    """Result from a research query."""

    query: str
    success: bool
    sources: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    key_insights: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    mode: str = "offline"  # "tavily", "offline", "cached"
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "success": self.success,
            "sources": self.sources,
            "summary": self.summary,
            "key_insights": self.key_insights,
            "timestamp": self.timestamp,
            "mode": self.mode,
            "error": self.error,
        }


class ResearchInterface:
    """
    Orchestration layer for research operations.

    This class wraps the Science Cartridge to provide:
    - Web search via Tavily API
    - Research query synthesis
    - Best practices lookup

    Philosophy: We don't implement search. We delegate to ScienceAgent.
    """

    def __init__(self, kernel: Optional["KernelProtocol"] = None):
        """
        Initialize research interface.

        Args:
            kernel: Optional kernel for agent calls
        """
        self._kernel = kernel
        self._web_search_tool = None
        self._cache: Dict[str, ResearchResult] = {}

    def _get_web_search_tool(self):
        """Lazy-load the web search tool from Science Cartridge."""
        if self._web_search_tool is None:
            try:
                from vibe_core.cartridges.system.science.tools.web_search_tool import WebSearchTool

                self._web_search_tool = WebSearchTool()
                logger.debug("✅ WebSearchTool loaded from Science Cartridge")
            except ImportError as e:
                logger.warning(f"⚠️ Could not load WebSearchTool: {e}")
        return self._web_search_tool

    async def query(
        self,
        query: str,
        max_results: int = 5,
        use_cache: bool = True,
    ) -> ResearchResult:
        """
        Execute a research query.

        This is the main interface for VIDYA's research capability.
        It delegates to the Science Cartridge's WebSearchTool.

        Args:
            query: Research query (e.g., "How to safely load Python plugins")
            max_results: Maximum number of results
            use_cache: Whether to use cached results

        Returns:
            ResearchResult with sources and synthesis
        """
        # Check cache first
        cache_key = f"{query}:{max_results}"
        if use_cache and cache_key in self._cache:
            logger.debug(f"📚 Cache hit for: {query[:50]}...")
            cached = self._cache[cache_key]
            cached.mode = "cached"
            return cached

        # Try kernel CALL_AGENT first (preferred method)
        if self._kernel:
            try:
                result = await self._query_via_kernel(query, max_results)
                if result.success:
                    self._cache[cache_key] = result
                    return result
            except Exception as e:
                logger.warning(f"Kernel agent call failed: {e}")

        # Fallback to direct WebSearchTool access
        try:
            result = self._query_direct(query, max_results)
            self._cache[cache_key] = result
            return result
        except Exception as e:
            logger.error(f"Research query failed: {e}")
            return ResearchResult(
                query=query,
                success=False,
                error=str(e),
            )

    async def _query_via_kernel(
        self,
        query: str,
        max_results: int,
    ) -> ResearchResult:
        """
        Query via kernel's CALL_AGENT mechanism.

        This is the preferred method as it goes through proper
        agent orchestration.
        """
        from vibe_core.runtime.syscalls import execute_syscall

        # Call Science agent via syscall
        try:
            result = execute_syscall(
                self._kernel,
                "CALL_AGENT",
                {
                    "agent_id": "science",
                    "task": {
                        "action": "briefing",
                        "query": query,
                        "max_results": max_results,
                    },
                },
            )

            if result.get("success"):
                output = result.get("output", {})
                return ResearchResult(
                    query=query,
                    success=True,
                    sources=output.get("sources", []),
                    summary=output.get("summary", ""),
                    key_insights=output.get("key_insights", []),
                    mode=output.get("mode", "tavily"),
                )
            else:
                return ResearchResult(
                    query=query,
                    success=False,
                    error=result.get("error", "Unknown error"),
                )

        except Exception as e:
            raise RuntimeError(f"CALL_AGENT failed: {e}")

    def _query_direct(self, query: str, max_results: int) -> ResearchResult:
        """
        Direct query via WebSearchTool (fallback method).

        Used when kernel is not available.
        """
        tool = self._get_web_search_tool()
        if tool is None:
            return ResearchResult(
                query=query,
                success=False,
                mode="offline",
                error="WebSearchTool not available",
            )

        try:
            # Get briefing from tool
            briefing = tool.get_briefing(query, max_results)

            return ResearchResult(
                query=query,
                success=True,
                sources=briefing.get("sources", []),
                summary=briefing.get("summary", ""),
                key_insights=briefing.get("key_insights", []),
                mode=briefing.get("mode", "tavily"),
            )

        except Exception as e:
            return ResearchResult(
                query=query,
                success=False,
                error=str(e),
            )

    async def get_best_practices(self, topic: str) -> ResearchResult:
        """
        Get best practices for a specific topic.

        This is a convenience method that formulates the query
        for best practices lookup.

        Args:
            topic: Topic to research (e.g., "Python dynamic module loading")

        Returns:
            ResearchResult with best practices
        """
        query = f"Best practices for {topic} in Python security safety"
        return await self.query(query, max_results=5)

    async def get_implementation_guide(self, task: str) -> ResearchResult:
        """
        Get implementation guidance for a specific task.

        Args:
            task: Task to implement (e.g., "Docker container scanner")

        Returns:
            ResearchResult with implementation guidance
        """
        query = f"How to implement {task} safely in Python with examples"
        return await self.query(query, max_results=5)

    def clear_cache(self) -> None:
        """Clear the research cache."""
        self._cache.clear()
        logger.debug("🗑️ Research cache cleared")


# Synchronous wrapper for non-async contexts
def research_sync(query: str, max_results: int = 5) -> ResearchResult:
    """
    Synchronous research query (uses direct method).

    For async contexts, use ResearchInterface().query() instead.
    """
    interface = ResearchInterface()
    return interface._query_direct(query, max_results)
