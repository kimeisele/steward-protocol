"""
CST FRAGMENT - The Atomic Unit of Code for Cellular Healing
============================================================

"yad yad vibhūtimat sattvaṁ śrīmad ūrjitam eva vā
tat tad evāvagaccha tvaṁ mama tejo-'ṁśa-sambhavam"

"Know that all opulent, beautiful and glorious creations
spring from but a spark of My splendor."
— Bhagavad Gita 10.41

A CSTFragment is the bridge between Maya (filesystem) and the Inner World (runtime).
It wraps an atomic code unit (function, method, class, import block) as a
MahaCellUnified payload, enabling granular Lotus-addressed healing.

FRAGMENT TYPES (Natural code boundaries):
    FUNCTION   - Top-level function definition
    METHOD     - Method within a class
    CLASS      - Entire class definition
    IMPORT     - Import block (contiguous imports)
    CONSTANT   - Module-level assignment
    MODULE     - Entire module (fallback)

LIFECYCLE:
    File (Maya) → parse → [CSTFragment, ...] → MahaCellUnified.from_content()
    → CellRouter (Lotus Address) → Chamber (Resonance) → Healing → Maya-Sync
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kumaras"
__position__ = 5
__genesis__ = "0xfe9a70b8"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional

import libcst as cst

# =============================================================================
# FRAGMENT TYPE (Natural code boundaries)
# =============================================================================


class FragmentType(str, Enum):
    """The type of atomic code unit. Derived from CST node type."""

    FUNCTION = "function"  # FunctionDef at module level
    METHOD = "method"  # FunctionDef inside ClassDef
    CLASS = "class"  # ClassDef (entire class)
    IMPORT = "import"  # Import / ImportFrom block
    CONSTANT = "constant"  # Module-level SimpleStatementLine (assignment)
    MODULE = "module"  # Entire module (fallback / reconstruction)


# =============================================================================
# CST FRAGMENT - The Atomic Payload
# =============================================================================


@dataclass(frozen=True)
class CSTFragment:
    """
    An atomic code fragment extracted from a Python file.

    This is the PAYLOAD of a MahaCellUnified when the cell represents code.
    The fragment carries enough context to:
    - Identify WHERE it came from (file_path, line range)
    - Know WHAT it is (fragment_type, qualified_name)
    - Reconstruct the CODE (source_code, parsed CST node)
    - Track its POSITION in the original file (sort_key for reconstruction)

    IMMUTABLE: Once extracted, a fragment is frozen.
    Healing creates a NEW fragment (new Cell, new Lotus address).

    WATERTIGHT: No Any types. All fields explicit.
    """

    # Identity
    fragment_type: FragmentType
    qualified_name: str  # e.g. "MyClass.my_method" or "process_data"

    # Origin (Maya reference)
    file_path: Path
    line_start: int  # 1-indexed, inclusive
    line_end: int  # 1-indexed, inclusive

    # Content
    source_code: str  # The exact source text of this fragment

    # Ordering (for file reconstruction)
    sort_key: int  # Position index in original file (0-based)

    # Parent context (for methods)
    parent_class: Optional[str] = None  # Class name if this is a METHOD

    @property
    def line_count(self) -> int:
        """Number of source lines."""
        return self.line_end - self.line_start + 1

    @property
    def is_method(self) -> bool:
        """True if this fragment is a method inside a class."""
        return self.fragment_type == FragmentType.METHOD

    @property
    def display_name(self) -> str:
        """Human-readable name for logging."""
        if self.parent_class:
            return f"{self.parent_class}.{self.qualified_name}"
        return self.qualified_name

    def compile_check(self) -> bool:
        """
        Verify this fragment compiles as valid Python.

        Returns:
            True if the source_code compiles without SyntaxError.
        """
        try:
            compile(self.source_code, f"<fragment:{self.display_name}>", "exec")
            return True
        except SyntaxError:
            return False

    def parse_cst(self) -> cst.Module:
        """
        Parse the source_code into a LibCST Module.

        Returns:
            Parsed CST module wrapping this fragment.

        Raises:
            cst.ParserSyntaxError: If source is unparseable.
        """
        return cst.parse_module(self.source_code)

    def with_new_source(self, new_source: str) -> "CSTFragment":
        """
        Create a healed copy with new source code.

        All identity fields preserved, only source changes.
        Line range updated based on new source.

        Args:
            new_source: The healed source code.

        Returns:
            New CSTFragment with updated source.
        """
        new_lines = new_source.count("\n") + 1
        return CSTFragment(
            fragment_type=self.fragment_type,
            qualified_name=self.qualified_name,
            file_path=self.file_path,
            line_start=self.line_start,
            line_end=self.line_start + new_lines - 1,
            source_code=new_source,
            sort_key=self.sort_key,
            parent_class=self.parent_class,
        )


# =============================================================================
# FRAGMENT COLLECTION (All fragments from one file)
# =============================================================================


@dataclass
class FileFragments:
    """
    All fragments extracted from a single Python file.

    Maintains ordering for reconstruction: sorted by sort_key,
    the fragments can be concatenated to reproduce the original file.
    """

    file_path: Path
    fragments: List[CSTFragment] = field(default_factory=list)
    original_source: str = ""  # The full original source (for diff verification)

    @property
    def count(self) -> int:
        """Number of fragments."""
        return len(self.fragments)

    def sorted(self) -> List[CSTFragment]:
        """Fragments in original file order."""
        return sorted(self.fragments, key=lambda f: f.sort_key)

    def reconstruct(self) -> str:
        """
        Reconstruct the full file source from fragments.

        Joins fragments in sort_key order with appropriate spacing.

        Returns:
            Reconstructed source code string.
        """
        if not self.fragments:
            return ""

        ordered = self.sorted()
        parts: List[str] = []

        for frag in ordered:
            parts.append(frag.source_code)

        return "\n\n".join(parts) + "\n"

    def get_by_name(self, qualified_name: str) -> Optional[CSTFragment]:
        """Find fragment by qualified name."""
        for frag in self.fragments:
            if frag.qualified_name == qualified_name:
                return frag
            if frag.display_name == qualified_name:
                return frag
        return None

    def replace_fragment(
        self,
        old_fragment: CSTFragment,
        new_fragment: CSTFragment,
    ) -> "FileFragments":
        """
        Replace one fragment with a healed version.

        Returns a new FileFragments with the replacement applied.
        """
        new_frags = []
        for frag in self.fragments:
            if frag.sort_key == old_fragment.sort_key:
                new_frags.append(new_fragment)
            else:
                new_frags.append(frag)

        return FileFragments(
            file_path=self.file_path,
            fragments=new_frags,
            original_source=self.original_source,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "FragmentType",
    "CSTFragment",
    "FileFragments",
]
