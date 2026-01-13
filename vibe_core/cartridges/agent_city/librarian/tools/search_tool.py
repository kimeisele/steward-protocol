"""
Search Books Tool - Search the library catalog.

Implements Tool Protocol (vibe_core.tools.tool_protocol.Tool).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x6bc36ba0"  # GenesisByte: parampara % 37 == 0

import json
import logging
from pathlib import Path
from typing import Any

from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger("LIBRARIAN_SEARCH")


class SearchBooksTool(Tool):
    """
    Tool for searching books in the library catalog.

    Supports search by:
    - Title (partial match, case-insensitive)
    - Author (partial match, case-insensitive)
    - Genre (exact match, case-insensitive)
    """

    def __init__(self, catalog_path: str = "data/library/catalog.json"):
        """
        Initialize search tool.

        Args:
            catalog_path: Path to catalog file
        """
        self.catalog_path = Path(catalog_path)

    @property
    def name(self) -> str:
        return "librarian.search_books"  # Namespaced: agent_id.tool_name

    @property
    def description(self) -> str:
        return "Search books in the library catalog by title, author, or genre"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "query": {
                "type": "string",
                "required": True,
                "description": "Search query (searches title and author)",
            },
            "genre": {
                "type": "string",
                "required": False,
                "description": "Filter by genre (exact match)",
            },
            "limit": {
                "type": "integer",
                "required": False,
                "description": "Maximum number of results (default: 10)",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """
        Validate search parameters.

        Args:
            parameters: Tool parameters

        Raises:
            ValueError: If required parameter missing or invalid
            TypeError: If parameter has wrong type
        """
        if "query" not in parameters:
            raise ValueError("Missing required parameter: query")

        query = parameters["query"]
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")

        # Optional limit validation
        if "limit" in parameters:
            limit = parameters["limit"]
            if not isinstance(limit, int):
                raise TypeError("limit must be an integer")
            if limit < 1 or limit > 100:
                raise ValueError("limit must be between 1 and 100")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute search operation.

        Args:
            parameters: Validated tool parameters

        Returns:
            ToolResult with matching books
        """
        try:
            query = parameters["query"].strip().lower()
            genre_filter = parameters.get("genre", "").strip().lower()
            limit = parameters.get("limit", 10)

            # Load catalog
            catalog = self._load_catalog()

            if not catalog:
                return ToolResult(
                    success=True,
                    output="No books in catalog yet",
                    metadata={"results": [], "total": 0},
                )

            # Search
            results = []
            for book in catalog:
                # Search in title and author
                title_match = query in book["title"].lower()
                author_match = query in book["author"].lower()

                # Genre filter (if specified)
                genre_match = True
                if genre_filter:
                    genre_match = book["genre"].lower() == genre_filter

                if (title_match or author_match) and genre_match:
                    results.append(book)

                # Limit results
                if len(results) >= limit:
                    break

            logger.info(f"🔍 Search '{query}': Found {len(results)} books")

            return ToolResult(
                success=True,
                output=results,
                metadata={
                    "query": query,
                    "total": len(results),
                    "limit": limit,
                },
            )

        except Exception as e:
            error_msg = f"Failed to search books: {type(e).__name__}: {e!s}"
            logger.error(f"SearchBooksTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)

    def _load_catalog(self) -> list[dict]:
        """Load catalog from disk."""
        try:
            with open(self.catalog_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
