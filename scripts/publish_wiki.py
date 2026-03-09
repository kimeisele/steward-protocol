#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vibe_core.wiki_publisher import publish_wiki, write_publication_result


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish the STEWARD Protocol wiki")
    parser.add_argument("--wiki-path", help="Optional local checkout path for the wiki repo")
    parser.add_argument("--wiki-url", help="Optional override for the wiki remote URL")
    parser.add_argument("--push", action="store_true", help="Push committed changes to the wiki remote")
    parser.add_argument("--prune-generated", action="store_true", help="Prune stale pages that were previously generated")
    parser.add_argument("--result-path", help="Optional path to write the publication result as JSON")
    args = parser.parse_args()
    result = publish_wiki(
        root=ROOT,
        wiki_path=Path(args.wiki_path).resolve() if args.wiki_path else None,
        wiki_repo_url=args.wiki_url,
        push=args.push,
        prune_generated=args.prune_generated,
    )
    if args.result_path:
        write_publication_result((ROOT / args.result_path).resolve(), result)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())