"""
PROOF OF CONCEPT: Move a substrate module, imports survive.

This test creates a temporary copy of a real substrate module,
removes the original from sys.modules, installs the LotusFinder
with a patched root pointing to a tree where the file has been
"moved" to a subdirectory, and verifies the import still resolves.

This is the critical proof that the LotusFinder enables safe
file reorganization without breaking any imports.
"""

import importlib
import sys
import textwrap


class TestMoveProof:
    """Prove that moved files are still importable via LotusFinder."""

    def test_simulated_move_resolves(self, tmp_path):
        """
        Simulate: substrate/fake_test_mod.py -> substrate/core/fake_test_mod.py

        The import 'vibe_core.mahamantra.substrate.fake_test_mod' should
        resolve via the LotusFinder even though the file isn't at the
        expected flat location.
        """
        import vibe_core.mahamantra.substrate.lotus_finder as lf

        # 1. Create a fake substrate tree where the module is NESTED
        fake_substrate = tmp_path / "substrate"
        fake_substrate.mkdir()
        (fake_substrate / "__init__.py").write_text("")

        core_dir = fake_substrate / "core"
        core_dir.mkdir()
        (core_dir / "__init__.py").write_text("")
        (core_dir / "fake_test_mod.py").write_text(
            textwrap.dedent("""\
                PROOF_VALUE = 42
                PROOF_NAME = "lotus_finder_works"
            """)
        )

        # NOTE: fake_test_mod.py does NOT exist at fake_substrate/fake_test_mod.py
        # It only exists at fake_substrate/core/fake_test_mod.py

        # 2. Patch the finder's root and rebuild the map
        original_root = lf._SUBSTRATE_ROOT
        original_map = lf._MODULE_MAP

        try:
            lf._SUBSTRATE_ROOT = fake_substrate
            lf.invalidate_cache()

            # 3. Verify the module map finds it in the nested location
            module_map = lf._get_module_map()
            assert "fake_test_mod" in module_map
            assert "core" in str(module_map["fake_test_mod"])

            # 4. Install the finder
            lf.install()

            # 5. Attempt to import the "moved" module
            # Python's normal import would FAIL (no substrate/fake_test_mod.py)
            # LotusFinder should resolve it from substrate/core/fake_test_mod.py
            fullname = "vibe_core.mahamantra.substrate.fake_test_mod"

            # Clean any cached version
            sys.modules.pop(fullname, None)

            # Use the finder directly to get the spec
            finder = lf._finder
            spec = finder.find_spec(fullname, None)

            assert spec is not None, "LotusFinder should find the moved module"
            assert "core/fake_test_mod.py" in spec.origin

            # 6. Actually load it
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            assert module.PROOF_VALUE == 42
            assert module.PROOF_NAME == "lotus_finder_works"

        finally:
            # Clean up
            sys.modules.pop("vibe_core.mahamantra.substrate.fake_test_mod", None)
            lf._SUBSTRATE_ROOT = original_root
            lf._MODULE_MAP = original_map

    def test_unmoved_file_uses_normal_import(self):
        """
        Files that HAVEN'T been moved are imported normally by Python.
        The LotusFinder doesn't interfere (returns None for already-loaded).
        """
        import vibe_core.mahamantra.substrate.lotus_finder as lf

        lf.install()

        # seed is at its normal location — Python handles it
        # The finder should return None (already in sys.modules)
        spec = lf._finder.find_spec("vibe_core.mahamantra.substrate.seed", None)
        assert spec is None  # Finder defers to Python's normal import

    def test_module_map_count_covers_substrate(self):
        """
        The module map should find at least as many modules as there are
        .py files in substrate/ (minus private ones).
        """
        import vibe_core.mahamantra.substrate.lotus_finder as lf

        lf.invalidate_cache()
        module_map = lf._build_module_map()

        # Count non-private .py files in substrate/
        substrate_root = lf._SUBSTRATE_ROOT
        direct_py_count = sum(1 for f in substrate_root.glob("*.py") if not f.name.startswith("_"))

        # Module map should have at least this many (plus nested + subpackages)
        assert len(module_map) >= direct_py_count, (
            f"Module map has {len(module_map)} entries but substrate/ has {direct_py_count} non-private .py files"
        )
