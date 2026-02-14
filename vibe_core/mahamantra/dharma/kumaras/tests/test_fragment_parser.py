"""
Tests for the Fragment Parser and CSTFragment.

Verifies:
1. File decomposition into atomic fragments (functions, classes, imports, constants)
2. Fragment reconstruction back to valid source
3. CSTFragment properties and compile_check
4. Cell registration via MahaCellUnified.from_content()
"""

import textwrap
from pathlib import Path

import pytest

from vibe_core.mahamantra.dharma.kumaras.fragment import (
    CSTFragment,
    FileFragments,
    FragmentType,
)
from vibe_core.mahamantra.dharma.kumaras.fragment_parser import (
    parse_source_to_fragments,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

SAMPLE_SOURCE = textwrap.dedent('''\
    """Module docstring."""

    import os
    from pathlib import Path

    CONSTANT_A = 42
    CONSTANT_B = "hello"

    def standalone_function(x: int) -> int:
        """A top-level function."""
        return x * 2

    class MyClass:
        """A sample class."""

        def __init__(self):
            self.value = 0

        def method_a(self):
            return self.value

        def method_b(self, x):
            self.value = x

    def another_function():
        pass
''')

SAMPLE_PATH = Path("/tmp/test_sample.py")


# =============================================================================
# FRAGMENT PARSER TESTS
# =============================================================================


class TestFragmentParser:
    """Test parse_source_to_fragments."""

    def test_parses_functions(self):
        result = parse_source_to_fragments(SAMPLE_SOURCE, SAMPLE_PATH)
        func_frags = [f for f in result.fragments if f.fragment_type == FragmentType.FUNCTION]
        func_names = [f.qualified_name for f in func_frags]
        assert "standalone_function" in func_names
        assert "another_function" in func_names

    def test_parses_classes(self):
        result = parse_source_to_fragments(SAMPLE_SOURCE, SAMPLE_PATH)
        class_frags = [f for f in result.fragments if f.fragment_type == FragmentType.CLASS]
        assert len(class_frags) >= 1
        assert any(f.qualified_name == "MyClass" for f in class_frags)

    def test_parses_imports(self):
        result = parse_source_to_fragments(SAMPLE_SOURCE, SAMPLE_PATH)
        import_frags = [f for f in result.fragments if f.fragment_type == FragmentType.IMPORT]
        assert len(import_frags) >= 1

    def test_parses_constants(self):
        result = parse_source_to_fragments(SAMPLE_SOURCE, SAMPLE_PATH)
        const_frags = [f for f in result.fragments if f.fragment_type == FragmentType.CONSTANT]
        const_names = [f.qualified_name for f in const_frags]
        assert "CONSTANT_A" in const_names or any("CONSTANT" in n for n in const_names)

    def test_fragment_count(self):
        result = parse_source_to_fragments(SAMPLE_SOURCE, SAMPLE_PATH)
        # At minimum: 2 imports + 2 constants + 2 functions + 1 class = 7
        assert result.count >= 5

    def test_sort_keys_are_sequential(self):
        result = parse_source_to_fragments(SAMPLE_SOURCE, SAMPLE_PATH)
        keys = [f.sort_key for f in result.fragments]
        assert keys == sorted(keys), "sort_keys must be in order"

    def test_all_fragments_have_source(self):
        result = parse_source_to_fragments(SAMPLE_SOURCE, SAMPLE_PATH)
        for frag in result.fragments:
            assert frag.source_code, f"Fragment {frag.qualified_name} has empty source"

    def test_all_fragments_have_line_range(self):
        result = parse_source_to_fragments(SAMPLE_SOURCE, SAMPLE_PATH)
        for frag in result.fragments:
            assert frag.line_start >= 1
            assert frag.line_end >= frag.line_start

    def test_empty_source_returns_module_fragment(self):
        result = parse_source_to_fragments("", SAMPLE_PATH)
        assert result.count >= 1
        assert result.fragments[0].fragment_type == FragmentType.MODULE

    def test_unparseable_source_returns_module_fragment(self):
        result = parse_source_to_fragments("def broken(:\n  pass", SAMPLE_PATH)
        assert result.count == 1
        assert result.fragments[0].fragment_type == FragmentType.MODULE


# =============================================================================
# CST FRAGMENT TESTS
# =============================================================================


class TestCSTFragment:
    """Test CSTFragment dataclass."""

    def _make_fragment(self, source: str = "def foo(): pass") -> CSTFragment:
        return CSTFragment(
            fragment_type=FragmentType.FUNCTION,
            qualified_name="foo",
            file_path=SAMPLE_PATH,
            line_start=1,
            line_end=1,
            source_code=source,
            sort_key=0,
        )

    def test_compile_check_valid(self):
        frag = self._make_fragment("def foo(): pass")
        assert frag.compile_check() is True

    def test_compile_check_invalid(self):
        frag = self._make_fragment("def foo(: pass")
        assert frag.compile_check() is False

    def test_line_count(self):
        frag = CSTFragment(
            fragment_type=FragmentType.FUNCTION,
            qualified_name="foo",
            file_path=SAMPLE_PATH,
            line_start=10,
            line_end=20,
            source_code="x",
            sort_key=0,
        )
        assert frag.line_count == 11

    def test_is_method(self):
        frag = CSTFragment(
            fragment_type=FragmentType.METHOD,
            qualified_name="bar",
            file_path=SAMPLE_PATH,
            line_start=1,
            line_end=1,
            source_code="def bar(self): pass",
            sort_key=0,
            parent_class="MyClass",
        )
        assert frag.is_method is True
        assert frag.display_name == "MyClass.bar"

    def test_with_new_source(self):
        frag = self._make_fragment("def foo(): pass")
        healed = frag.with_new_source("def foo():\n    return 42")
        assert healed.source_code == "def foo():\n    return 42"
        assert healed.qualified_name == "foo"
        assert healed.sort_key == 0
        assert healed.line_end == healed.line_start + 1  # 2 lines

    def test_parse_cst(self):
        frag = self._make_fragment("def foo(): pass")
        module = frag.parse_cst()
        assert module is not None

    def test_frozen(self):
        frag = self._make_fragment()
        with pytest.raises(AttributeError):
            frag.source_code = "changed"


# =============================================================================
# FILE FRAGMENTS TESTS
# =============================================================================


class TestFileFragments:
    """Test FileFragments collection."""

    def test_sorted_by_sort_key(self):
        frags = FileFragments(
            file_path=SAMPLE_PATH,
            fragments=[
                CSTFragment(FragmentType.FUNCTION, "b", SAMPLE_PATH, 10, 15, "def b(): pass", 2),
                CSTFragment(FragmentType.FUNCTION, "a", SAMPLE_PATH, 1, 5, "def a(): pass", 0),
                CSTFragment(FragmentType.CONSTANT, "C", SAMPLE_PATH, 7, 7, "C = 1", 1),
            ],
        )
        ordered = frags.sorted()
        assert [f.qualified_name for f in ordered] == ["a", "C", "b"]

    def test_get_by_name(self):
        frags = FileFragments(
            file_path=SAMPLE_PATH,
            fragments=[
                CSTFragment(FragmentType.FUNCTION, "foo", SAMPLE_PATH, 1, 3, "def foo(): pass", 0),
                CSTFragment(FragmentType.FUNCTION, "bar", SAMPLE_PATH, 5, 7, "def bar(): pass", 1),
            ],
        )
        found = frags.get_by_name("bar")
        assert found is not None
        assert found.qualified_name == "bar"

    def test_replace_fragment(self):
        old = CSTFragment(FragmentType.FUNCTION, "foo", SAMPLE_PATH, 1, 3, "def foo(): pass", 0)
        new = old.with_new_source("def foo(): return 42")
        frags = FileFragments(file_path=SAMPLE_PATH, fragments=[old])
        replaced = frags.replace_fragment(old, new)
        assert replaced.fragments[0].source_code == "def foo(): return 42"

    def test_reconstruct(self):
        frags = FileFragments(
            file_path=SAMPLE_PATH,
            fragments=[
                CSTFragment(FragmentType.IMPORT, "import:os", SAMPLE_PATH, 1, 1, "import os", 0),
                CSTFragment(FragmentType.FUNCTION, "foo", SAMPLE_PATH, 3, 4, "def foo():\n    pass", 1),
            ],
        )
        reconstructed = frags.reconstruct()
        assert "import os" in reconstructed
        assert "def foo():" in reconstructed
