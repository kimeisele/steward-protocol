#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vibe_core.wiki_publisher import build_wiki


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the local STEWARD Protocol wiki manifestation")
    parser.add_argument("--output-dir", default=".vibe/wiki-build", help="Where to materialize wiki markdown files")
    args = parser.parse_args()
    built = build_wiki(root=ROOT, output_dir=ROOT / args.output_dir)
    page_count = len([path for path in built if path.suffix.lower() == ".md"])
    metadata_count = len(built) - page_count
    print(f"built {page_count} wiki pages and {metadata_count} metadata artifacts into {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())