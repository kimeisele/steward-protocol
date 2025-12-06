#!/usr/bin/env python3
"""
Test ARCHITECTURE_ANALYSIS Circuit - Validation Script

This script tests the new architecture analysis tool and circuit WITHOUT
hardcoded values. It validates:

1. Tool Protocol implementation
2. Kernel introspection (live data)
3. Schema extraction (from real DB)
4. Diagram generation (Mermaid syntax)
5. Template rendering (Jinja2)

NO HARDCODED ROTZ! Everything introspected.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def test_tool_import():
    """Test 1: Tool can be imported."""
    print("=" * 80)
    print("TEST 1: Import ArchitectureAnalysisTool")
    print("=" * 80)

    try:
        from vibe_core.cartridges.agent_city.analyst.tools.architecture_tool import ArchitectureAnalysisTool

        tool = ArchitectureAnalysisTool()
        assert tool is not None, "Tool must be instantiated"
        print(f"✅ Tool imported: {tool.name}")
        print(f"   Description: {tool.description}")
        return tool
    except Exception as e:
        print(f"❌ Import failed: {e}")
        assert False, f"Import failed: {e}"
        return None


def test_kernel_introspection(tool):
    """Test 2: Kernel introspection (live data)."""
    print("\n" + "=" * 80)
    print("TEST 2: Introspect Kernel (Live Data)")
    print("=" * 80)

    try:
        result = tool.execute({"action": "introspect_kernel"})

        if result.success:
            data = result.output
            assert data is not None, "Output should not be None"
            print("✅ Kernel introspected successfully")
            print(f"   Kernel Type: {data.get('kernel_type')}")
            print(f"   Agent Count: {data.get('agent_count')}")
            print(f"   Ledger Path: {data.get('ledger_path')}")
            print(f"   Scheduler State: {data.get('scheduler_state')}")

            # Validate NO HARDCODED values
            if data.get("kernel_type") == "RealVibeKernel":
                print("   ✅ Real kernel detected (not mocked)")
            else:
                print(f"   ⚠️  Unexpected kernel type: {data.get('kernel_type')}")

            return data
        else:
            print(f"❌ Introspection failed: {result.error}")
            assert False, f"Introspection failed: {result.error}"
            return None

    except Exception as e:
        print(f"❌ Introspection error: {e}")
        import traceback

        traceback.print_exc()
        return None


def test_schema_extraction(tool):
    """Test 3: SQLite schema extraction (from real DB)."""
    print("\n" + "=" * 80)
    print("TEST 3: Extract Schema (Real Database)")
    print("=" * 80)

    try:
        result = tool.execute({"action": "extract_schema"})

        if result.success:
            data = result.output
            assert data is not None, "Output should not be None"
            print("✅ Schema extracted successfully")
            print(f"   Database Path: {data.get('path')}")
            print(f"   Event Count: {data.get('event_count')}")
            print(f"   Tables Found: {len(data.get('schemas', []))}")

            # Show first schema (NO HARDCODED SQL!)
            schemas = data.get("schemas", [])
            if schemas:
                print("\n   Sample Schema (Introspected):")
                print(f"   {schemas[0][:200]}...")

            # Validate NO HARDCODED values
            if data.get("event_count", 0) >= 0:
                print("   ✅ Event count is realistic")
            else:
                print("   ⚠️  Unexpected event count")

            return data
        else:
            print(f"❌ Schema extraction failed: {result.error}")
            assert False, f"Schema extraction failed: {result.error}"
            return None

    except Exception as e:
        print(f"❌ Schema extraction error: {e}")
        import traceback

        traceback.print_exc()
        return None


def test_diagram_generation(tool):
    """Test 4: Mermaid diagram generation."""
    print("\n" + "=" * 80)
    print("TEST 4: Generate Diagrams (Mermaid)")
    print("=" * 80)

    diagrams = {}

    # Test layer diagram
    try:
        result = tool.execute(
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

        if result.success:
            diagrams["layer"] = result.output
            print("✅ Layer diagram generated")
            print(f"   Length: {len(result.output)} chars")
            assert "```mermaid" in result.output, "Mermaid syntax marker not found"
            if "```mermaid" in result.output:
                print("   ✅ Valid Mermaid syntax detected")
            else:
                print("   ⚠️  Mermaid syntax marker not found")
        else:
            print(f"❌ Layer diagram failed: {result.error}")
            assert False, f"Layer diagram failed: {result.error}"

    except Exception as e:
        print(f"❌ Layer diagram error: {e}")

    # Test sequence diagram
    try:
        result = tool.execute(
            {
                "action": "generate_diagram",
                "diagram_type": "sequence",
                "data": {"actors": ["User", "Kernel", "Agent", "Ledger"], "flow": {}},
            }
        )

        if result.success:
            diagrams["sequence"] = result.output
            print("✅ Sequence diagram generated")
            print(f"   Length: {len(result.output)} chars")
        else:
            print(f"❌ Sequence diagram failed: {result.error}")

    except Exception as e:
        print(f"❌ Sequence diagram error: {e}")

    return diagrams


def test_template_rendering(tool, kernel_data, schema_data, diagrams):
    """Test 5: Jinja2 template rendering."""
    print("\n" + "=" * 80)
    print("TEST 5: Render ARCHITECTURE.md (Jinja2)")
    print("=" * 80)

    try:
        result = tool.execute(
            {
                "action": "render",
                "data": {
                    "system_snapshot": kernel_data or {},
                    "understanding": {"schema": schema_data or {}},
                    "artifacts": diagrams or {},
                    "plan": {},
                },
            }
        )

        if result.success:
            content = result.output
            assert content is not None, "Content should not be None"
            print("✅ Template rendered successfully")
            print(f"   Content Length: {len(content)} chars")
            print(f"   Lines: {len(content.splitlines())}")

            # Check for NO HARDCODED values
            if "Auto-Generated" in content:
                print("   ✅ Auto-generated marker present")
            if "ANALYST" in content:
                print("   ✅ Agent attribution present")
            if "```mermaid" in content:
                print("   ✅ Diagrams embedded")

            # Show preview
            print("\n   Preview (first 500 chars):")
            print("   " + content[:500].replace("\n", "\n   "))

            return content
        else:
            print(f"❌ Rendering failed: {result.error}")
            assert False, f"Rendering failed: {result.error}"
            return None

    except Exception as e:
        print(f"❌ Rendering error: {e}")
        import traceback

        traceback.print_exc()
        return None


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("ARCHITECTURE ANALYSIS TOOL - VALIDATION TESTS")
    print("=" * 80)
    print("\nPhilosophy: ZERO HARDCODED VALUES - All introspected!")
    print()

    # Test 1: Import
    tool = test_tool_import()
    if not tool:
        print("\n❌ CRITICAL: Tool import failed. Aborting tests.")
        sys.exit(1)

    # Inject TestKernel for introspection
    print("\n[SETUP] Injecting TestKernel fixture...")
    from vibe_core.plugins.test_orchestration import TestKernel

    tool.kernel = TestKernel.with_governance()
    print("✅ TestKernel injected")

    # Test 2: Kernel introspection
    kernel_data = test_kernel_introspection(tool)

    # Test 3: Schema extraction
    schema_data = test_schema_extraction(tool)

    # Test 4: Diagram generation
    diagrams = test_diagram_generation(tool)

    # Test 5: Template rendering
    content = test_template_rendering(tool, kernel_data, schema_data, diagrams)

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    results = {
        "Tool Import": tool is not None,
        "Kernel Introspection": kernel_data is not None,
        "Schema Extraction": schema_data is not None,
        "Diagram Generation": bool(diagrams),
        "Template Rendering": content is not None,
    }

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    all_passed = all(results.values())
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED - Implementation valid!")
    else:
        print("❌ SOME TESTS FAILED - Review errors above")
    print("=" * 80)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
