#!/usr/bin/env python3
"""
Documentation Generator - Standalone
=====================================

Generates ALL documentation files WITHOUT kernel dependency.

This is the reliable way:
- No kernel boot required
- No sandbox complexity
- Direct introspection → rendering → writing
- Fast, deterministic, debuggable

Usage:
    python scripts/generate_docs.py              # Generate all docs
    python scripts/generate_docs.py --readme     # Only README.md
    python scripts/generate_docs.py --agents     # Only AGENTS.md
    python scripts/generate_docs.py --citymap    # Only CITYMAP.md
    python scripts/generate_docs.py --help-doc   # Only HELP.md
    python scripts/generate_docs.py --index      # Only INDEX.md
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Direct imports of renderers WITHOUT going through __init__.py
# (avoids pydantic dependency from cartridge_main.py)
import importlib.util

def load_renderer(full_module_name, module_path):
    """Load a renderer module directly, bypassing __init__.py"""
    spec = importlib.util.spec_from_file_location(full_module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_module_name] = module
    spec.loader.exec_module(module)
    return module

# Load all renderer modules with full package names
# This allows relative imports to work correctly
tools_dir = project_root / "steward/system_agents/scribe/tools"

# Load introspector first (dependency for others)
introspector_module = load_renderer(
    "steward.system_agents.scribe.tools.introspector",
    tools_dir / "introspector.py"
)

project_introspector_module = load_renderer(
    "steward.system_agents.scribe.tools.project_introspector",
    tools_dir / "project_introspector.py"
)

readme_renderer_module = load_renderer(
    "steward.system_agents.scribe.tools.readme_renderer",
    tools_dir / "readme_renderer.py"
)

agents_renderer_module = load_renderer(
    "steward.system_agents.scribe.tools.agents_renderer",
    tools_dir / "agents_renderer.py"
)

citymap_renderer_module = load_renderer(
    "steward.system_agents.scribe.tools.citymap_renderer",
    tools_dir / "citymap_renderer.py"
)

help_renderer_module = load_renderer(
    "steward.system_agents.scribe.tools.help_renderer",
    tools_dir / "help_renderer.py"
)

index_renderer_module = load_renderer(
    "steward.system_agents.scribe.tools.index_renderer",
    tools_dir / "index_renderer.py"
)

# Extract classes
ReadmeRenderer = readme_renderer_module.ReadmeRenderer
AgentsRenderer = agents_renderer_module.AgentsRenderer
CitymapRenderer = citymap_renderer_module.CitymapRenderer
HelpRenderer = help_renderer_module.HelpRenderer
IndexRenderer = index_renderer_module.IndexRenderer


def generate_readme() -> bool:
    """Generate README.md"""
    print("\n📖 Generating README.md...")
    try:
        renderer = ReadmeRenderer(root_dir=".")
        content = renderer.render()

        readme_path = Path("README.md")
        readme_path.write_text(content)

        print(f"   ✅ README.md generated ({len(content)} bytes)")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_agents() -> bool:
    """Generate AGENTS.md"""
    print("\n🤖 Generating AGENTS.md...")
    try:
        renderer = AgentsRenderer(root_dir=".")
        content = renderer.scan_and_render()

        agents_path = Path("AGENTS.md")
        agents_path.write_text(content)

        print(f"   ✅ AGENTS.md generated ({len(content)} bytes)")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_citymap() -> bool:
    """Generate CITYMAP.md"""
    print("\n🗺️  Generating CITYMAP.md...")
    try:
        renderer = CitymapRenderer(root_dir=".")
        content = renderer.scan_and_render()

        citymap_path = Path("CITYMAP.md")
        citymap_path.write_text(content)

        print(f"   ✅ CITYMAP.md generated ({len(content)} bytes)")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_help() -> bool:
    """Generate HELP.md"""
    print("\n❓ Generating HELP.md...")
    try:
        renderer = HelpRenderer(root_dir=".")
        content = renderer.scan_and_render()

        help_path = Path("HELP.md")
        help_path.write_text(content)

        print(f"   ✅ HELP.md generated ({len(content)} bytes)")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_index() -> bool:
    """Generate INDEX.md"""
    print("\n📑 Generating INDEX.md...")
    try:
        renderer = IndexRenderer(root_dir=".")
        content = renderer.scan_and_render()

        index_path = Path("INDEX.md")
        index_path.write_text(content)

        print(f"   ✅ INDEX.md generated ({len(content)} bytes)")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate documentation files")
    parser.add_argument("--readme", action="store_true", help="Generate only README.md")
    parser.add_argument("--agents", action="store_true", help="Generate only AGENTS.md")
    parser.add_argument("--citymap", action="store_true", help="Generate only CITYMAP.md")
    parser.add_argument("--help-doc", action="store_true", help="Generate only HELP.md")
    parser.add_argument("--index", action="store_true", help="Generate only INDEX.md")

    args = parser.parse_args()

    print("=" * 70)
    print("📚 DOCUMENTATION GENERATOR (Standalone)")
    print("=" * 70)

    # If no specific flag, generate all
    generate_all = not any([args.readme, args.agents, args.citymap, args.help_doc, args.index])

    results = {}

    if generate_all or args.readme:
        results['README.md'] = generate_readme()

    if generate_all or args.agents:
        results['AGENTS.md'] = generate_agents()

    if generate_all or args.citymap:
        results['CITYMAP.md'] = generate_citymap()

    if generate_all or args.help_doc:
        results['HELP.md'] = generate_help()

    if generate_all or args.index:
        results['INDEX.md'] = generate_index()

    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)

    for doc_name, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {doc_name}")

    all_success = all(results.values())

    if all_success:
        print("\n✅ ALL DOCUMENTATION GENERATED SUCCESSFULLY")
        print("=" * 70)
        return 0
    else:
        print("\n❌ SOME DOCUMENTATION FAILED TO GENERATE")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
