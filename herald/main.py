#!/usr/bin/env python3
"""
HERALD System Entrypoint
Single, unified execution point for all HERALD operations.

Usage:
    python herald/main.py --action generate      # Generate content only
    python herald/main.py --action publish       # Publish pre-generated content
    python herald/main.py --action full          # Generate + Publish (if approved)

Architecture: VibeOS Standard
- Kernel-based boot sequence
- Dependency injection
- Single config source (system.yaml)
- Unified error handling (GAD-000)
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from herald.core.kernel import VibeKernel
from herald.core.aligner import VibeAligner
from herald.capabilities.research import ResearchCapability
from herald.capabilities.creative import CreativeCapability
from herald.capabilities.broadcast import BroadcastCapability


def main():
    """Main HERALD execution handler."""

    # === PARSING ===
    parser = argparse.ArgumentParser(
        description="HERALD - Industrial-Grade Content Generation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python herald/main.py --action generate        Generate content only
  python herald/main.py --action publish         Publish pre-generated content
  python herald/main.py --action full            Generate + Publish
        """
    )
    parser.add_argument(
        "--action",
        choices=["generate", "publish", "full"],
        required=True,
        help="Action to execute"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without publishing (for testing)"
    )

    args = parser.parse_args()

    # === BOOT KERNEL ===
    print("🔌 HERALD: System boot sequence initiated")
    print("=" * 70)

    try:
        kernel = VibeKernel(config_path="herald/config/system.yaml").boot()
    except Exception as e:
        print(f"❌ KERNEL BOOT FAILED: {e}")
        sys.exit(1)

    # === REGISTER CAPABILITIES ===
    print("\n🧩 HERALD: Loading capabilities")
    try:
        kernel.register_capability(
            "research",
            ResearchCapability(kernel.get_config("capabilities.research"))
        )
        kernel.register_capability(
            "creative",
            CreativeCapability(kernel.get_config("capabilities.creative"))
        )
        kernel.register_capability(
            "broadcast",
            BroadcastCapability(kernel.get_config("capabilities.broadcast"))
        )

        # Aligner is always available (governance)
        aligner = VibeAligner(kernel.get_config("alignment"))

    except Exception as e:
        print(f"❌ CAPABILITY LOADING FAILED: {e}")
        sys.exit(1)

    print("✅ All capabilities loaded")

    # === PREPARE ARTIFACTS ===
    dist_dir = Path(kernel.get_config("artifacts.output_dir"))
    dist_dir.mkdir(exist_ok=True)

    # === ACTION HANDLERS ===
    if args.action == "generate":
        generate_action(kernel, aligner, dist_dir, args.dry_run)

    elif args.action == "publish":
        publish_action(kernel, dist_dir, args.dry_run)

    elif args.action == "full":
        generate_action(kernel, aligner, dist_dir, args.dry_run)
        if (dist_dir / "content.json").exists():
            publish_action(kernel, dist_dir, args.dry_run)
        else:
            print("⚠️  Generation failed, skipping publish")
            sys.exit(1)


def generate_action(kernel, aligner, dist_dir, dry_run=False):
    """Generate content phase."""
    print("\n🧠 PHASE: GENERATION")
    print("=" * 70)

    try:
        # Step 1: Research
        print("\n[STEP 1] Research: Scanning market trends...")
        research_cap = kernel.get_capability("research")
        topic = research_cap.find_trending_topic() if research_cap else None

        research_context = None
        if topic:
            research_context = topic.get("article", {}).get("content", "")
            print(f"✅ Found trending topic: {topic.get('search_query')}")
        else:
            print("⚠️  No trending topic found, using fallback context")

        # Step 2: Generate
        print("\n[STEP 2] Creative: Generating content...")
        creative_cap = kernel.get_capability("creative")
        content = creative_cap.generate_insight(research_context=research_context)

        if not content:
            print("❌ Content generation failed")
            sys.exit(1)

        print(f"✅ Content generated: {len(content)} chars")
        print(f"   Preview: {content[:80]}...")

        # Step 3: Align (Governance)
        print("\n[STEP 3] Governance: Checking alignment...")
        final_content = aligner.align(content, platform="twitter")

        if not final_content:
            print("❌ Content rejected by governance")
            rejections = aligner.get_rejection_log()
            if rejections:
                print(f"   Reason: {rejections[-1].get('reason')}")
            sys.exit(1)

        print("✅ Content approved by governance")

        # Step 4: Bundle Artifact
        print("\n[STEP 4] Bundling: Saving artifact...")
        payload = {
            "text": final_content,
            "image_filename": None,
            "image_path": None,
            "generated_at": __import__("datetime").datetime.now().isoformat(),
        }

        content_file = dist_dir / "content.json"
        with open(content_file, "w") as f:
            json.dump(payload, f, indent=2)

        print(f"✅ Bundle saved: {content_file}")

        # Step 5: GitHub Output
        if "GITHUB_OUTPUT" in os.environ:
            output_file = os.environ["GITHUB_OUTPUT"]
            clean_text = final_content.replace('\n', ' ').replace('"', '\\"')
            with open(output_file, "a") as gh_out:
                gh_out.write(f"preview_text={clean_text}\n")
                gh_out.write(f"has_image=false\n")
            print("✅ GitHub Output written")

        # Summary
        print("\n" + "=" * 70)
        print("✅ GENERATION COMPLETE")
        print(f"   Content: {len(final_content)} chars")
        print(f"   Artifact: {content_file}")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ GENERATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def publish_action(kernel, dist_dir, dry_run=False):
    """Publish content phase."""
    print("\n🚀 PHASE: PUBLICATION")
    print("=" * 70)

    try:
        # Step 1: Load Artifact
        print("\n[STEP 1] Loading artifact...")
        content_file = dist_dir / "content.json"

        if not content_file.exists():
            print(f"❌ No bundle found: {content_file}")
            sys.exit(1)

        with open(content_file, "r") as f:
            data = json.load(f)

        text = data.get("text")
        if not text:
            print("❌ Bundle missing 'text' field")
            sys.exit(1)

        print(f"✅ Bundle loaded: {len(text)} chars")

        # Step 2: Verify Credentials
        print("\n[STEP 2] Verifying credentials...")
        broadcast_cap = kernel.get_capability("broadcast")

        if not broadcast_cap.verify_credentials("twitter"):
            print("❌ Twitter credentials invalid")
            sys.exit(1)

        print("✅ Twitter credentials verified")

        # Step 3: Publish
        print("\n[STEP 3] Publishing...")

        if dry_run:
            print(f"[DRY RUN] Would publish: {text[:80]}...")
            success = True
        else:
            success = broadcast_cap.publish(text, platform="twitter")

        if not success:
            print("❌ Publication failed")
            sys.exit(1)

        print("✅ Publication successful")

        # Summary
        print("\n" + "=" * 70)
        print("✅ PUBLICATION COMPLETE")
        print(f"   Platform: Twitter")
        print(f"   Length: {len(text)} chars")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ PUBLICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
