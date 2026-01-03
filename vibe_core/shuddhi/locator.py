"""
OPUS-212: CSTLocator - The Bridge Between Analysis and Surgery.

This module implements the AST-to-CST Bridge Pattern, enabling the system
to take violations detected by AST-based analyzers (LCOM4, Narasimha) and
locate the exact corresponding node in the CST for modification.

The bridge logic relies on the fact that ast and LibCST (when populated
with metadata) share a coordinate system:
- AST Coordinates: 1-based lines, 0-based columns
- LibCST Coordinates: CodePosition(line, column)
"""

from typing import Optional, Type

import libcst as cst
from libcst.metadata import MetadataWrapper, PositionProvider


class CSTLocator(cst.CSTVisitor):
    """
    The Bridge: Locates a CST node corresponding to specific AST coordinates.

    This enables the system to:
    1. Analyze code with AST (fast, lossy)
    2. Detect violations with line/col coordinates
    3. Bridge to CST (lossless)
    4. Apply surgical fixes preserving formatting
    """

    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(
        self,
        target_line: int,
        target_col: int,
        node_type_filter: Optional[Type[cst.CSTNode]] = None,
    ):
        """
        Initialize the locator.

        Args:
            target_line: 1-based line number from AST node
            target_col: 0-based column offset from AST node
            node_type_filter: Optional CST node type to filter matches
        """
        self.target_line = target_line
        self.target_col = target_col
        self.node_type_filter = node_type_filter
        self.best_match: Optional[cst.CSTNode] = None
        self.best_match_range = None

    def on_visit(self, node: cst.CSTNode) -> bool:
        """
        Generic visit hook called for every node.

        Logic: We want the *most specific* node. If we find a match,
        it might be a parent (e.g., IfStmt). We continue traversal
        to see if a child (e.g., Name) also matches.
        LibCST visits parents before children.
        """
        try:
            pos = self.get_metadata(PositionProvider, node)
        except KeyError:
            return True

        if pos.start.line == self.target_line and pos.start.column == self.target_col:
            if self.node_type_filter and not isinstance(node, self.node_type_filter):
                return True

            self.best_match = node
            self.best_match_range = pos
            return True

        if pos.end.line < self.target_line:
            return False

        return True


class ASTBridge:
    """
    High-level bridge API for AST-to-CST conversion.

    Usage:
        bridge = ASTBridge(source_code)
        cst_node = bridge.locate(ast_node)
    """

    def __init__(self, source_code: str):
        """Initialize with source code."""
        self.source_code = source_code
        self._wrapper: Optional[MetadataWrapper] = None

    @property
    def wrapper(self) -> MetadataWrapper:
        """Lazy-initialize the metadata wrapper."""
        if self._wrapper is None:
            module = cst.parse_module(self.source_code)
            self._wrapper = MetadataWrapper(module)
        return self._wrapper

    def locate(
        self,
        line: int,
        col: int,
        node_type: Optional[Type[cst.CSTNode]] = None,
    ) -> Optional[cst.CSTNode]:
        """
        Locate a CST node at the given AST coordinates.

        Args:
            line: 1-based line number
            col: 0-based column offset
            node_type: Optional CST node type filter

        Returns:
            The most specific CST node at the coordinates, or None
        """
        locator = CSTLocator(line, col, node_type)
        self.wrapper.visit(locator)
        return locator.best_match

    def locate_from_ast_node(self, ast_node) -> Optional[cst.CSTNode]:
        """
        Locate a CST node corresponding to an AST node.

        Args:
            ast_node: Python ast node with lineno and col_offset

        Returns:
            Corresponding CST node, or None

        Raises:
            ValueError: If AST node lacks position information
        """
        if not hasattr(ast_node, "lineno"):
            raise ValueError("AST Node lacks position information")

        return self.locate(ast_node.lineno, ast_node.col_offset)
