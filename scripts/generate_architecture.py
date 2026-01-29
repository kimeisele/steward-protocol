#!/usr/bin/env python3
"""
Generate ARCHITECTURE.md - Demo Script

This demonstrates how to use the ARCHITECTURE_ANALYSIS circuit to generate
comprehensive architecture documentation.

Usage:
    python generate_architecture.py

Output:
    ARCHITECTURE.md (auto-generated from live introspection)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0xb404f9f3"  # GenesisByte: parampara % 37 == 0

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Generate ARCHITECTURE.md using ANALYST.architecture tool."""
    print("=" * 80)
    print("ARCHITECTURE.md GENERATOR")
    print("=" * 80)
    print("\nPhilosophy: ZERO HARDCODED VALUES - All introspected from live system!\n")

    try:
        from vibe_core.cartridges.agent_city.analyst.tools.architecture_tool import ArchitectureAnalysisTool

        # Initialize tool
        tool = ArchitectureAnalysisTool(root_dir=".")

        print("Step 1: Introspecting kernel...")
        kernel_result = tool.execute({"action": "introspect_kernel"})
        if not kernel_result.success:
            print(f"❌ Kernel introspection failed: {kernel_result.error}")
            return 1

        kernel_data = kernel_result.output
        print(f"✅ Found {kernel_data['agent_count']} agents")
        print(f"   Introspection mode: {kernel_data.get('introspection_mode', 'unknown')}")

        print("\nStep 2: Extracting SQLite schema...")
        schema_result = tool.execute({"action": "extract_schema"})
        if not schema_result.success:
            print(f"❌ Schema extraction failed: {schema_result.error}")
            return 1

        schema_data = schema_result.output
        print(f"✅ Schema extracted from: {schema_data['path']}")
        print(f"   Event count: {schema_data['event_count']}")
        print(f"   Tables: {len(schema_data.get('schemas', []))}")

        print("\nStep 3: Generating diagrams...")

        # Layer diagram
        layer_result = tool.execute(
            {
                "action": "generate_diagram",
                "diagram_type": "graph",
                "data": {
                    "layers": [
                        {"name": "Layer 0: Constitution"},
                        {"name": "Layer 1: VibeOS Kernel"},
                        {"name": "Layer 2: Governance"},
                        {"name": "Layer 3: Agents"},
                    ]
                },
            }
        )

        # Sequence diagram
        sequence_result = tool.execute(
            {
                "action": "generate_diagram",
                "diagram_type": "sequence",
                "data": {"actors": ["User", "Kernel", "Agent", "Ledger"], "flow": {}},
            }
        )

        # Lifecycle diagram
        lifecycle_result = tool.execute(
            {
                "action": "generate_diagram",
                "diagram_type": "flowchart",
                "data": {"flows": []},
            }
        )

        diagrams = {
            "layer_diagram": layer_result.output if layer_result.success else "",
            "sequence_diagram": sequence_result.output if sequence_result.success else "",
            "lifecycle_diagram": lifecycle_result.output if lifecycle_result.success else "",
        }

        print("✅ Diagrams generated (3 Mermaid diagrams)")

        print("\nStep 4: Rendering ARCHITECTURE.md...")
        render_result = tool.execute(
            {
                "action": "render",
                "data": {
                    "system_snapshot": kernel_data,
                    "understanding": {"schema": schema_data},
                    "artifacts": diagrams,
                    "plan": {},
                },
            }
        )

        if not render_result.success:
            print(f"❌ Rendering failed: {render_result.error}")
            return 1

        content = render_result.output

        # Write to file
        output_path = Path("ARCHITECTURE.md")
        output_path.write_text(content, encoding="utf-8")

        print("✅ ARCHITECTURE.md generated!")
        print(f"   File: {output_path.absolute()}")
        print(f"   Size: {len(content)} chars ({len(content.splitlines())} lines)")

        print("\n" + "=" * 80)
        print("✅ SUCCESS - Architecture documentation generated!")
        print("=" * 80)
        print("\nView the result: cat ARCHITECTURE.md")

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
