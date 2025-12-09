#!/usr/bin/env python3
"""
📦 STANDARD LIBRARY RELEASE SCRIPT

Creates a distributable ZIP of all holons in library/.
This is the "Vibe OS Standard Library" - ready for distribution.

Usage:
    python scripts/release_library.py

Output:
    dist/vibe_standard_library_v1.0.zip
"""

import zipfile
from datetime import datetime
from pathlib import Path


def create_release():
    """Create the Standard Library release artifact."""
    library_path = Path("library")
    dist_path = Path("dist")
    dist_path.mkdir(exist_ok=True)

    # Version from date
    version = "1.0"
    timestamp = datetime.now().strftime("%Y%m%d")

    output_file = dist_path / f"vibe_standard_library_v{version}.zip"

    print("📦 Creating Vibe OS Standard Library Release")
    print("=" * 50)

    # Collect all holons
    holons = list(library_path.glob("*.vibe"))

    if not holons:
        print("❌ No holons found in library/")
        return 1

    print(f"📚 Found {len(holons)} holons:")
    total_size = 0

    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for holon in sorted(holons):
            size = holon.stat().st_size
            total_size += size
            print(f"  + {holon.name} ({size:,} bytes)")
            zf.write(holon, holon.name)

        # Add manifest
        manifest = f"""# Vibe OS Standard Library v{version}
# Generated: {datetime.now().isoformat()}
# Contents: {len(holons)} holons

holons:
"""
        for holon in sorted(holons):
            manifest += f"  - {holon.stem}\n"

        zf.writestr("MANIFEST.yaml", manifest)

    print()
    print(f"✅ Release created: {output_file}")
    print(f"   Total holons: {len(holons)}")
    print(f"   Uncompressed: {total_size:,} bytes")
    print(f"   Compressed:   {output_file.stat().st_size:,} bytes")

    return 0


if __name__ == "__main__":
    exit(create_release())
