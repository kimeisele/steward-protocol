"""
FRAGMENT PARSER - Decompose Python Files into Atomic Cells
==========================================================

"nāsato vidyate bhāvo nābhāvo vidyate sataḥ"
"Of the nonexistent there is no endurance, and of the existent there is no cessation."
— Bhagavad Gita 2.16

The Fragment Parser is the bridge from Maya (filesystem) to the Inner World (Cells).
It reads a Python file, parses it into a CST, and extracts atomic fragments
(functions, methods, classes, imports, constants) — each becoming a CSTFragment
that can be wrapped in a MahaCellUnified and registered in the CellRouter.

GRANULARITY: Function / Method / Class level.
    - Functions and methods are the natural "cells" of code.
    - Classes are extracted whole (methods are NOT extracted separately by default).
    - Import blocks are grouped contiguously.
    - Module-level assignments become CONSTANT fragments.

DETERMINISM: Same file → same fragments → same Lotus addresses. Always.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kumaras"
__position__ = 5
__genesis__ = "0xfe9a70b8"  # GenesisByte: parampara % 37 == 0

import logging
from pathlib import Path
from typing import List, Optional, Sequence

import libcst as cst

from vibe_core.mahamantra.dharma.kumaras.fragment import (
    CSTFragment,
    FileFragments,
    FragmentType,
)

logger = logging.getLogger("SHUDDHI.PARSER")


# =============================================================================
# CST VISITOR - Extracts fragment boundaries from a parsed module
# =============================================================================


class _FragmentExtractor(cst.CSTVisitor):
    """
    Walks a LibCST tree and collects fragment boundaries.

    Only visits top-level statements (depth 0 and 1 for class methods).
    Does NOT recurse into nested functions or inner classes.
    """

    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

    def __init__(self, source_lines: List[str], file_path: Path) -> None:
        self._source_lines = source_lines
        self._file_path = file_path
        self._fragments: List[CSTFragment] = []
        self._sort_counter: int = 0
        self._in_class: Optional[str] = None  # Current class name if inside one
        self._class_start: int = 0
        self._class_end: int = 0
        self._in_compound: int = 0  # Depth inside compound stmts (if/for/with/try)

    @property
    def fragments(self) -> List[CSTFragment]:
        return list(self._fragments)

    def _line_range(self, node: cst.CSTNode) -> tuple:
        """Extract (start_line, end_line) from a CST node's position."""
        pos = self.get_metadata(cst.metadata.PositionProvider, node)
        return pos.start.line, pos.end.line

    def _extract_source(self, start_line: int, end_line: int) -> str:
        """Extract source lines (1-indexed, inclusive)."""
        return "\n".join(self._source_lines[start_line - 1 : end_line])

    def _add_fragment(
        self,
        fragment_type: FragmentType,
        name: str,
        start_line: int,
        end_line: int,
        parent_class: Optional[str] = None,
    ) -> None:
        """Create and store a CSTFragment."""
        source = self._extract_source(start_line, end_line)
        frag = CSTFragment(
            fragment_type=fragment_type,
            qualified_name=name,
            file_path=self._file_path,
            line_start=start_line,
            line_end=end_line,
            source_code=source,
            sort_key=self._sort_counter,
            parent_class=parent_class,
        )
        self._fragments.append(frag)
        self._sort_counter += 1

    def visit_If(self, node: cst.If) -> Optional[bool]:
        """Capture top-level if-blocks (e.g. `if TYPE_CHECKING:`) as one fragment."""
        if self._in_class is not None or self._in_compound > 0:
            return False

        start, end = self._line_range(node)
        self._add_fragment(FragmentType.CONSTANT, f"if_block:{start}", start, end)
        return False  # Don't recurse — avoids extracting indented imports

    def visit_For(self, node: cst.For) -> Optional[bool]:
        """Capture top-level for-loops as one fragment."""
        if self._in_class is not None or self._in_compound > 0:
            return False
        start, end = self._line_range(node)
        self._add_fragment(FragmentType.CONSTANT, f"for_block:{start}", start, end)
        return False

    def visit_While(self, node: cst.While) -> Optional[bool]:
        """Capture top-level while-loops as one fragment."""
        if self._in_class is not None or self._in_compound > 0:
            return False
        start, end = self._line_range(node)
        self._add_fragment(FragmentType.CONSTANT, f"while_block:{start}", start, end)
        return False

    def visit_Try(self, node: cst.Try) -> Optional[bool]:
        """Capture top-level try-blocks as one fragment."""
        if self._in_class is not None or self._in_compound > 0:
            return False
        start, end = self._line_range(node)
        self._add_fragment(FragmentType.CONSTANT, f"try_block:{start}", start, end)
        return False

    def visit_With(self, node: cst.With) -> Optional[bool]:
        """Capture top-level with-blocks as one fragment."""
        if self._in_class is not None or self._in_compound > 0:
            return False
        start, end = self._line_range(node)
        self._add_fragment(FragmentType.CONSTANT, f"with_block:{start}", start, end)
        return False

    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        """Extract top-level functions. Methods are captured as part of their class."""
        if self._in_class is not None:
            # We're inside a class — skip, the class fragment captures everything
            return False  # Don't recurse deeper

        start, end = self._line_range(node)
        name = node.name.value
        self._add_fragment(FragmentType.FUNCTION, name, start, end)
        return False  # Don't recurse into nested functions

    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        """Extract entire class as one fragment."""
        if self._in_class is not None:
            # Nested class — skip
            return False

        start, end = self._line_range(node)
        name = node.name.value
        self._in_class = name
        self._class_start = start
        self._class_end = end

        self._add_fragment(FragmentType.CLASS, name, start, end)

        self._in_class = None
        return False  # Don't recurse — class is captured whole

    def visit_SimpleStatementLine(self, node: cst.SimpleStatementLine) -> Optional[bool]:
        """Extract imports and module-level constants."""
        if self._in_class is not None or self._in_compound > 0:
            return False

        start, end = self._line_range(node)

        # Check if this is an import
        for stmt in node.body:
            if isinstance(stmt, (cst.Import, cst.ImportFrom)):
                source = self._extract_source(start, end)
                # Try to get the module name for a readable qualified_name
                if isinstance(stmt, cst.ImportFrom) and isinstance(stmt.module, cst.Attribute):
                    mod_name = cst.parse_module("").code  # fallback
                    mod_name = f"import:{start}"
                elif isinstance(stmt, cst.ImportFrom) and isinstance(stmt.module, cst.Name):
                    mod_name = f"import:{stmt.module.value}"
                elif isinstance(stmt, cst.Import):
                    mod_name = f"import:{start}"
                else:
                    mod_name = f"import:{start}"

                self._add_fragment(FragmentType.IMPORT, mod_name, start, end)
                return False

            # Check for assignment (constant)
            if isinstance(stmt, (cst.Assign, cst.AnnAssign, cst.AugAssign)):
                # Extract the target name
                if isinstance(stmt, cst.Assign) and stmt.targets:
                    target = stmt.targets[0].target
                    if isinstance(target, cst.Name):
                        name = target.value
                    else:
                        name = f"assign:{start}"
                elif isinstance(stmt, cst.AnnAssign) and isinstance(stmt.target, cst.Name):
                    name = stmt.target.value
                else:
                    name = f"assign:{start}"

                self._add_fragment(FragmentType.CONSTANT, name, start, end)
                return False

        return False


# =============================================================================
# PUBLIC API - Parse a file into fragments
# =============================================================================


def parse_file_to_fragments(file_path: Path) -> FileFragments:
    """
    Parse a Python file into atomic CSTFragments.

    Each top-level function, class, import block, and constant
    becomes its own fragment with a deterministic sort_key.

    Args:
        file_path: Path to the Python file.

    Returns:
        FileFragments containing all extracted fragments.

    Raises:
        FileNotFoundError: If file doesn't exist.
        cst.ParserSyntaxError: If file can't be parsed.
    """
    source = file_path.read_text(encoding="utf-8")
    return parse_source_to_fragments(source, file_path)


def parse_source_to_fragments(source: str, file_path: Path) -> FileFragments:
    """
    Parse source code string into atomic CSTFragments.

    Args:
        source: Python source code string.
        file_path: Path for identification (may not exist on disk).

    Returns:
        FileFragments containing all extracted fragments.
    """
    source_lines = source.splitlines()

    # Parse with position metadata
    try:
        wrapper = cst.metadata.MetadataWrapper(cst.parse_module(source))
    except cst.ParserSyntaxError:
        logger.warning(f"[PARSER] Cannot parse {file_path}, returning as single MODULE fragment")
        # Fallback: entire file as one MODULE fragment
        frag = CSTFragment(
            fragment_type=FragmentType.MODULE,
            qualified_name=file_path.stem,
            file_path=file_path,
            line_start=1,
            line_end=len(source_lines),
            source_code=source,
            sort_key=0,
        )
        return FileFragments(
            file_path=file_path,
            fragments=[frag],
            original_source=source,
        )

    # Extract fragments
    extractor = _FragmentExtractor(source_lines, file_path)
    wrapper.visit(extractor)

    fragments = extractor.fragments

    # If no fragments were extracted (e.g. empty file or only comments),
    # return the whole file as a MODULE fragment
    if not fragments:
        frag = CSTFragment(
            fragment_type=FragmentType.MODULE,
            qualified_name=file_path.stem,
            file_path=file_path,
            line_start=1,
            line_end=max(1, len(source_lines)),
            source_code=source,
            sort_key=0,
        )
        fragments = [frag]

    logger.debug(
        f"[PARSER] {file_path.name}: {len(fragments)} fragments "
        f"({sum(1 for f in fragments if f.fragment_type == FragmentType.FUNCTION)} functions, "
        f"{sum(1 for f in fragments if f.fragment_type == FragmentType.CLASS)} classes)"
    )

    return FileFragments(
        file_path=file_path,
        fragments=fragments,
        original_source=source,
    )


# =============================================================================
# CELL REGISTRATION - Fragments → MahaCellUnified in CellRouter
# =============================================================================


def register_fragments_as_cells(
    file_fragments: FileFragments,
) -> List[int]:
    """
    Register all fragments from a file as MahaCellUnified in the global CellRouter.

    Each fragment becomes a Cell with:
    - header.sravanam = Lotus address (deterministic from source_code)
    - header.pada_sevanam = Mahamantra position (0-15)
    - lifecycle.dna = source_code
    - payload = CSTFragment

    Args:
        file_fragments: Parsed fragments from a file.

    Returns:
        List of Lotus addresses (one per registered cell).
    """
    from vibe_core.mahamantra.substrate.cell import MahaCellUnified

    addresses: List[int] = []

    for frag in file_fragments.fragments:
        cell = MahaCellUnified.from_content(
            content=frag.source_code,
            initial_state=frag,
            register=True,  # Auto-register in CellRouter
        )
        addresses.append(cell.header.sravanam)

        logger.debug(
            f"[PARSER] Registered {frag.display_name} "
            f"@ 0x{cell.header.sravanam:08X} "
            f"({frag.line_count} lines, {frag.fragment_type.value})"
        )

    return addresses


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "parse_file_to_fragments",
    "parse_source_to_fragments",
    "register_fragments_as_cells",
]
