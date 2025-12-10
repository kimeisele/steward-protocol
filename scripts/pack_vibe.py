#!/usr/bin/env python3
"""
Holon Builder - Pack Vibe Containers (.vibe)
"""

import argparse
import hashlib
import logging
import sys
import zipfile
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("PACKER")


def build_container(source_dir: Path, output_path: Optional[Path] = None) -> Path:
    """
    Build a .vibe container from a folder.

    Enforces:
    1. manifest.json exists
    2. tests/ directory exists
    3. manifest.json is FIRST file in zip (GAD-000)
    4. SIGNATURE.sig is generated and added
    """
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    # 1. Manifest Discovery (steward.json or manifest.json)
    manifest_path = source_dir / "manifest.json"
    manifest_name = "manifest.json"

    if not manifest_path.exists():
        manifest_path = source_dir / "steward.json"
        manifest_name = "steward.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest missing (checked manifest.json and steward.json) in {source_dir}")

    tests_dir = source_dir / "tests"
    if not tests_dir.exists():  # or not any(tests_dir.iterdir()):
        # Warning for now, but OPUS says HARD FAIL. Let's start with warning for dev ease?
        # No, user said "HARD FAIL".
        raise FileNotFoundError(f"Tests directory missing: {tests_dir}. Holon rejected.")

    if output_path is None:
        output_path = source_dir.with_suffix(".vibe")

    logger.info(f"📦 Packing Holon: {source_dir.name} -> {output_path.name}")

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_STORED) as z:
        # 1. GAD-000: Manifest FIRST (Stored, no compression for streaming)
        # NORMALIZE: Always calls it manifest.json inside the container
        logger.info(f"  📄 Adding {manifest_name} as manifest.json (Layer 0)")
        z.write(manifest_path, "manifest.json")

        # Calculate hash for signature
        hasher = hashlib.sha256()
        hasher.update(manifest_path.read_bytes())

        def add_recursive(path: Path):
            # SECURITY: Alphabetical sorting is MANDATORY for deterministic hashing
            # Without this, hash differs between Linux/Mac/Windows = verification impossible
            for item in sorted(path.iterdir()):
                if item.name.startswith((".", "__pycache__")):
                    continue
                if item.name == manifest_name:
                    continue  # Already added as manifest.json
                if item.name == "manifest.json" and manifest_name != "manifest.json":
                    # Edge case: If both exist?
                    continue
                if item.name == "SIGNATURE.sig":
                    continue  # Generated file

                # Determine destination path in archive
                rel_path = item.relative_to(source_dir)

                # Special Top-Level folders
                if str(rel_path).startswith("tests"):
                    arcname = str(rel_path)
                elif str(rel_path).startswith("hollows"):
                    arcname = str(rel_path)
                else:
                    # Everything else goes to content/
                    arcname = f"content/{rel_path}"

                if item.is_dir():
                    # Just recurse (zipfile doesn't need dir entries specifically if we write files)
                    # But if empty dir? Let's verify.
                    pass
                else:
                    logger.info(f"  📎 Adding {arcname}")
                    z.write(item, arcname, compress_type=zipfile.ZIP_DEFLATED)
                    hasher.update(item.read_bytes())

                if item.is_dir():
                    add_recursive(item)

        # Add all files
        add_recursive(source_dir)

        # 2. SIGNATURE
        signature = hasher.hexdigest()
        logger.info(f"  ✍️  Signing Holon: {signature[:8]}...")
        z.writestr("SIGNATURE.sig", signature)

    logger.info("✅ Holon successfully packed.")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Pack a Vibe Container (.vibe)")
    parser.add_argument("source", type=Path, help="Source directory of the plugin/agent")
    parser.add_argument("-o", "--output", type=Path, help="Output .vibe file path")

    args = parser.parse_args()

    try:
        build_container(args.source, args.output)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
