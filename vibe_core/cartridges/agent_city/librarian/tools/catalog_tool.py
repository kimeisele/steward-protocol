"""
Catalog Book Tool - Add books to the library catalog.

Implements Tool Protocol (vibe_core.tools.tool_protocol.Tool).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x5219bb91"  # GenesisByte: parampara % 37 == 0

import json
import logging
from pathlib import Path
from typing import Any

from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger("LIBRARIAN_CATALOG")


class CatalogBookTool(Tool):
    """
    Tool for adding books to the library catalog.

    This tool demonstrates the Tool Protocol in action:
    - Implements all required abstract methods
    - Returns ToolResult with success/error
    - Validates parameters before execution
    """

    def __init__(self, catalog_path: str = "data/library/catalog.json"):
        """
        Initialize catalog tool.

        Args:
            catalog_path: Path to catalog file (default: data/library/catalog.json)
        """
        self.catalog_path = Path(catalog_path)
        self.catalog_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize empty catalog if doesn't exist
        if not self.catalog_path.exists():
            self._save_catalog([])

    @property
    def name(self) -> str:
        return "librarian.catalog_book"  # Namespaced: agent_id.tool_name

    @property
    def description(self) -> str:
        return "Add a book to the library catalog with metadata (title, author, genre, year)"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "title": {
                "type": "string",
                "required": True,
                "description": "Book title",
            },
            "author": {
                "type": "string",
                "required": True,
                "description": "Book author",
            },
            "genre": {
                "type": "string",
                "required": False,
                "description": "Book genre (e.g., fiction, non-fiction, science)",
            },
            "year": {
                "type": "integer",
                "required": False,
                "description": "Publication year",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """
        Validate catalog parameters.

        Args:
            parameters: Tool parameters

        Raises:
            ValueError: If required parameter missing or invalid
            TypeError: If parameter has wrong type
        """
        # Check required fields
        if "title" not in parameters:
            raise ValueError("Missing required parameter: title")
        if "author" not in parameters:
            raise ValueError("Missing required parameter: author")

        # Type checks
        title = parameters["title"]
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title must be a non-empty string")

        author = parameters["author"]
        if not isinstance(author, str) or not author.strip():
            raise ValueError("author must be a non-empty string")

        # Optional field validation
        if "year" in parameters:
            year = parameters["year"]
            if not isinstance(year, int):
                raise TypeError("year must be an integer")
            if year < 0 or year > 2100:
                raise ValueError("year must be between 0 and 2100")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute catalog operation.

        Args:
            parameters: Validated tool parameters

        Returns:
            ToolResult with success status and book ID
        """
        try:
            title = parameters["title"].strip()
            author = parameters["author"].strip()
            genre = parameters.get("genre", "unknown").strip()
            year = parameters.get("year")

            # Load existing catalog
            catalog = self._load_catalog()

            # Check for duplicates
            for book in catalog:
                if book["title"].lower() == title.lower() and book["author"].lower() == author.lower():
                    return ToolResult(
                        success=False,
                        error=f"Book already exists in catalog: '{title}' by {author}",
                    )

            # Add book
            book_id = len(catalog) + 1
            book = {
                "id": book_id,
                "title": title,
                "author": author,
                "genre": genre,
                "year": year,
            }

            catalog.append(book)
            self._save_catalog(catalog)

            logger.info(f"📚 Cataloged book #{book_id}: '{title}' by {author}")

            return ToolResult(
                success=True,
                output=f"Book cataloged successfully: '{title}' by {author}",
                metadata={"book_id": book_id, "total_books": len(catalog)},
            )

        except Exception as e:
            error_msg = f"Failed to catalog book: {type(e).__name__}: {e!s}"
            logger.error(f"CatalogBookTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)

    def _load_catalog(self) -> list[dict]:
        """Load catalog from disk."""
        try:
            with open(self.catalog_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_catalog(self, catalog: list[dict]) -> None:
        """Save catalog to disk."""
        with open(self.catalog_path, "w") as f:
            json.dump(catalog, f, indent=2)
