"""
Debug script for OPUS verification.

Uses opus_assistant plugin (OPUS-029 migration).
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def run():
    """Run OPUS verification debug."""
    from vibe_core.plugins.opus_assistant.core.verification_logic import VerificationEngine

    print("DEBUG: Initializing VerificationEngine")
    engine = VerificationEngine(workspace_root=PROJECT_ROOT)

    print("DEBUG: Running verification...")
    try:
        report = engine.run_verification(quick=True)
        print(f"DEBUG: Total score: {report.get('total_score', 0)}%")
        print(f"DEBUG: Docs with harness: {report.get('docs_with_harness', 0)}")
        print(f"DEBUG: Docs without harness: {report.get('docs_without_harness', 0)}")
        print()
        print("--- TOP 5 DOCS ---")
        for doc in report.get("docs", [])[:5]:
            if doc.get("has_harness"):
                print(f"  {doc['name']}: {doc.get('score', 0)}%")
            else:
                print(f"  {doc['name']}: (no harness)")
    except Exception as e:
        print(f"DEBUG: Verification failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    run()
