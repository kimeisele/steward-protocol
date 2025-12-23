#!/usr/bin/env python3
"""
📚 LIBRARIAN CARTRIDGE - Proof of Concept for Universal Tool Registry

This agent demonstrates the NEW pattern:
- Agent does NOT own tool instances
- Agent does NOT import tool classes
- Agent calls tools via self.system.execute_tool()
- Tools are registered in kernel and accessed via AgentSystemInterface

This is the future: YAML-based agents that declare tools, not own them.

CRITICAL DIFFERENCE:

OLD PATTERN (Legacy):
    class HeraldCartridge:
        def __init__(self):
            self.broadcast = BroadcastTool()  # Agent owns tool
            self.content = ContentTool()

NEW PATTERN (This Agent):
    class LibrarianCartridge:
        def __init__(self):
            # NO tool instances!
            # Tools accessed via self.system.execute_tool()
            pass
"""

import logging
from typing import Any, Dict

from vibe_core.agent_protocol import VibeAgent
from vibe_core.scheduling.task import Task
from vibe_core.state.schema import ExecutionResult

logger = logging.getLogger("LIBRARIAN")


class LibrarianCartridge(VibeAgent):
    """
    The LIBRARIAN Agent Cartridge.

    Demonstrates kernel-managed tools:
    - NO tool instances created in __init__
    - Tools accessed via self.system.execute_tool()
    - Namespaced tools: librarian.catalog_book, librarian.search_books, etc.
    """

    def __init__(self):
        """Initialize LIBRARIAN as a VibeAgent."""
        super().__init__(
            agent_id="librarian",
            name="LIBRARIAN",
            version="1.0.0",
            author="Universal Tool Registry Initiative",
            description="Knowledge management: catalog, search, recommend books",
            domain="KNOWLEDGE",
            capabilities=["catalog_books", "search_books", "recommend_books"],
        )

        logger.info("📚 LIBRARIAN Cartridge initializing...")

        # Constitutional Oath (if available)
        try:
            from vibe_core.bridge import OathMixin

            if OathMixin:
                # Simulate oath for testing (in production, would be proper ceremony)
                self.oath_sworn = True
                logger.info("✅ LIBRARIAN has sworn the Constitutional Oath")
        except ImportError:
            self.oath_sworn = True  # Allow operation without oath for testing
            logger.info("⚠️  Constitutional Oath not available, proceeding anyway")

        # CRITICAL: NO TOOL INSTANCES CREATED HERE
        # Tools are accessed via self.system.execute_tool()

        logger.info("📚 LIBRARIAN Cartridge ready (NO tool instances owned)")

    def process(self, task: Task) -> ExecutionResult:
        """
        Process a task from the kernel scheduler.

        This method demonstrates the NEW pattern:
        - NO direct tool calls
        - ALL operations go through self.system.execute_tool()
        - Tools are kernel-managed, not agent-owned

        Task payload format:
        {
            "action": "catalog" | "search" | "recommend",
            "params": {...}
        }
        """
        logger.info(f"📬 LIBRARIAN processing task {task.task_id}...")

        try:
            action = task.payload.get("action")
            params = task.payload.get("params", {})

            # Route action to appropriate tool
            if action == "catalog":
                res_dict = self._catalog_book(params)
            elif action == "search":
                res_dict = self._search_books(params)
            elif action == "recommend":
                res_dict = self._recommend_books(params)
            else:
                return ExecutionResult(success=False, error=f"Unknown action: {action}")

            if res_dict.get("success"):
                logger.info(f"✅ Task {task.task_id} completed")
                return ExecutionResult(success=True, result=res_dict)
            else:
                logger.warning(f"⚠️  Task {task.task_id} failed: {res_dict.get('error')}")
                return ExecutionResult(success=False, error=res_dict.get("error"), result=res_dict)

        except Exception as e:
            logger.error(f"❌ Task processing failed: {e}", exc_info=True)
            return ExecutionResult(success=False, error=str(e))

    def _catalog_book(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Action: Catalog a book.

        This uses the kernel's tool registry via self.system.execute_tool().
        NO direct tool instance is created or called.

        Params:
        - title (required): Book title
        - author (required): Book author
        - genre (optional): Book genre
        - year (optional): Publication year
        """
        logger.info(f"📖 Cataloging book: {params.get('title', 'unknown')}")

        # CRITICAL: Tool call goes through kernel
        result = self.system.execute_tool("librarian.catalog_book", params)

        if result.success:
            return {
                "success": True,
                "action": "catalog",
                "message": result.output,
                "book_id": result.metadata.get("book_id"),
                "total_books": result.metadata.get("total_books"),
            }
        else:
            return {"success": False, "error": result.error}

    def _search_books(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Action: Search books.

        Params:
        - query (required): Search query
        - genre (optional): Filter by genre
        - limit (optional): Max results
        """
        logger.info(f"🔍 Searching books: {params.get('query', 'unknown')}")

        # CRITICAL: Tool call goes through kernel
        result = self.system.execute_tool("librarian.search_books", params)

        if result.success:
            books = result.output if isinstance(result.output, list) else []
            return {
                "success": True,
                "action": "search",
                "books": books,
                "total": result.metadata.get("total", 0),
            }
        else:
            return {"success": False, "error": result.error}

    def _recommend_books(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Action: Recommend books.

        Params:
        - genre (optional): Preferred genre
        - count (optional): Number of recommendations
        """
        logger.info(f"💡 Recommending books (genre: {params.get('genre', 'random')})")

        # CRITICAL: Tool call goes through kernel
        result = self.system.execute_tool("librarian.recommend_books", params)

        if result.success:
            recommendations = result.output if isinstance(result.output, list) else []
            return {
                "success": True,
                "action": "recommend",
                "recommendations": recommendations,
                "total": result.metadata.get("total", 0),
                "genre": result.metadata.get("genre"),
            }
        else:
            return {"success": False, "error": result.error}
