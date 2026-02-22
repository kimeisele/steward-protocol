import sys
import os
import argparse
from pathlib import Path
import logging

# Add project root to path
sys.path.append(os.getcwd())

from vibe_core.mahamantra.dharma.kumaras.engine import ShuddhiEngine
from vibe_core.mahamantra.substrate.sankirtan import SCAN_DIRECTORIES
from vibe_core.mahamantra.substrate.shuddhi import ShuddhiStatus

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("GENESIS_HEALER")


def main():
    parser = argparse.ArgumentParser(description="Invoke ShuddhiEngine to heal Genesis markers.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without modifying files.")
    parser.add_argument("--apply", action="store_true", help="Apply the changes.")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Please specify --dry-run or --apply")
        sys.exit(1)

    if args.dry_run:
        print("🔍 RUNNING IN DRY-RUN MODE (No files will be modified)")

    # Initialize Engine
    engine = ShuddhiEngine()

    # Target Rule ID
    RULE_ID = "broken_genesis"

    # Check if remedy exists
    if not engine.can_heal(RULE_ID):
        print(f"❌ Error: Remedy '{RULE_ID}' not found in ShuddhiEngine!")
        print("Available remedies:", engine.list_remedies())
        sys.exit(1)

    print(f"✅ Engine initialized. Targeting remedy: {RULE_ID}")
    print(f"📂 Scanning directories: {SCAN_DIRECTORIES}")
    print("-" * 60)

    total_files = 0
    healed_files = 0
    failed_files = 0

    # Iterate valid directories
    for start_dir in SCAN_DIRECTORIES:
        if start_dir == ".":
            # Handle root files
            path = Path(".")
            files = [f for f in path.iterdir() if f.is_file() and f.suffix == ".py"]
        else:
            path = Path(start_dir)
            if not path.exists():
                continue
            files = path.rglob("*.py")

        for file_path in files:
            # Skip hidden/test/sankirtan specific skips
            if any(part.startswith(".") or part == "__pycache__" for part in file_path.parts):
                continue

            total_files += 1

            # SCAN
            # In dry-run, engine.scan_file returns results but doesn't write types usually?
            # actually engine.scan_file does NOT write to disk, it returns results.
            # engine.purify DOES write if we ask it to? No, purify returns result.
            # We must use scan_file which returns results, then we decide what to do.
            # Wait, engine.scan_file returns Purified results but does it write?
            # implementation says: "scan_file... Returns List[ShuddhiResult]". It compiles but doesn't write.

            results = engine.scan_file(file_path, rule_ids=[RULE_ID])

            for result in results:
                if result.status == ShuddhiStatus.PURIFIED:
                    if args.dry_run:
                        print(f"📝 [WOULD HEAL] {file_path}")
                        # print(result.diff) # Optional: print diff
                    else:
                        # APPLY
                        try:
                            file_path.write_text(result.purified_code)
                            print(f"✨ [HEALED] {file_path}")
                            healed_files += 1
                        except Exception as e:
                            print(f"❌ [FAILED] {file_path}: {e}")
                            failed_files += 1
                elif result.status == ShuddhiStatus.FAILED:
                    print(f"⚠️ [FAILED] {file_path}: {result.message}")
                    failed_files += 1

    print("-" * 60)
    print(f"Scanned: {total_files} files")
    if args.dry_run:
        print(f"Found {healed_files} files that need healing (Dry Run)")
    else:
        print(f"Healed {healed_files} files")
    print(f"Failed: {failed_files}")


if __name__ == "__main__":
    main()
