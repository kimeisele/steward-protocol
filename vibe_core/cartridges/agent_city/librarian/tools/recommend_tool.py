"""
Recommend Books Tool - Recommend books based on preferences.

Implements Tool Protocol (vibe_core.tools.tool_protocol.Tool).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xa94d3340"  # GenesisByte: parampara % 37 == 0

import json
import logging
import random
from pathlib import Path
from typing import Any

from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger("LIBRARIAN_RECOMMEND")


class RecommendBooksTool(Tool):
    """
    Tool for recommending books from the library catalog.

    Recommends books based on:
    - Genre preferences
    - Random sampling (if no preferences)
    """

    def __init__(self, catalog_path: str = "data/library/catalog.json"):
        """
        Initialize recommend tool.

        Args:
            catalog_path: Path to catalog file
        """
        self.catalog_path = Path(catalog_path)

    @property
    def name(self) -> str:
        return "librarian.recommend_books"  # Namespaced: agent_id.tool_name

    @property
    def description(self) -> str:
        return "Recommend books from the library catalog based on genre or random selection"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "genre": {
                "type": "string",
                "required": False,
                "description": "Preferred genre (if not specified, recommends random books)",
            },
            "count": {
                "type": "integer",
                "required": False,
                "description": "Number of recommendations (default: 3, max: 10)",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """
        Validate recommendation parameters.

        Args:
            parameters: Tool parameters

        Raises:
            ValueError: If parameters invalid
            TypeError: If parameter has wrong type
        """
        # Count validation (optional)
        if "count" in parameters:
            count = parameters["count"]
            if not isinstance(count, int):
                raise TypeError("count must be an integer")
            if count < 1 or count > 10:
                raise ValueError("count must be between 1 and 10")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute recommendation operation.

        Args:
            parameters: Validated tool parameters

        Returns:
            ToolResult with recommended books
        """
        try:
            genre_pref = parameters.get("genre", "").strip().lower()
            count = parameters.get("count", 3)

            # Load catalog
            catalog = self._load_catalog()

            if not catalog:
                return ToolResult(
                    success=True,
                    output="No books available for recommendations yet",
                    metadata={"recommendations": [], "total": 0},
                )

            # Filter by genre if specified
            if genre_pref:
                candidates = [book for book in catalog if book["genre"].lower() == genre_pref]

                if not candidates:
                    return ToolResult(
                        success=True,
                        output=f"No books found in genre '{genre_pref}'",
                        metadata={"recommendations": [], "total": 0, "genre": genre_pref},
                    )
            else:
                candidates = catalog

            # Random sample (up to count)
            recommendations = random.sample(candidates, min(count, len(candidates)))

            logger.info(
                f"💡 Recommended {len(recommendations)} books"
                + (f" (genre: {genre_pref})" if genre_pref else " (random)")
            )

            return ToolResult(
                success=True,
                output=recommendations,
                metadata={
                    "total": len(recommendations),
                    "genre": genre_pref if genre_pref else "random",
                },
            )

        except Exception as e:
            error_msg = f"Failed to recommend books: {type(e).__name__}: {e!s}"
            logger.error(f"RecommendBooksTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)

    def _load_catalog(self) -> list[dict]:
        """Load catalog from disk."""
        try:
            with open(self.catalog_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
