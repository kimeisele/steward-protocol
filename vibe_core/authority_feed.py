from __future__ import annotations

import argparse
import json
import subprocess
from hashlib import sha256
from pathlib import Path
from typing import Any

from vibe_core.authority_exports import export_authority_bundle

AUTHORITY_FEED_CONTRACT_VERSION = 1


def _source_sha(workspace: Path) -> str:
    try:
        return (
            subprocess.check_output(["git", "-C", str(workspace), "rev-parse", "HEAD"], text=True).strip() or "unknown"
        )
    except Exception:
        return "unknown"


def _write_json(path: Path, payload: dict[str, Any]) -> str:
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered)
    return sha256(rendered.encode("utf-8")).hexdigest()


def write_authority_feed(
    *, workspace: Path | str | None = None, output_dir: Path | str | None = None, source_sha: str | None = None
) -> tuple[Path, dict[str, Any]]:
    root = Path(workspace or ".").resolve()
    target_root = Path(output_dir).resolve() if output_dir is not None else root / ".authority-feed"
    effective_source_sha = str(source_sha or _source_sha(root)).strip() or "working-tree"
    bundle = export_authority_bundle(workspace=root, source_sha=effective_source_sha)
    persisted_bundle = {key: value for key, value in bundle.items() if key != "artifacts"}
    bundle_root = target_root / "bundles" / effective_source_sha
    artifacts_manifest: dict[str, dict[str, str]] = {}
    for relative_path, payload in dict(bundle.get("artifacts", {})).items():
        file_sha = _write_json(bundle_root / relative_path, payload)
        export_kind = next(
            str(kind)
            for kind, artifact_path in dict(persisted_bundle.get("artifact_paths", {})).items()
            if str(artifact_path) == str(relative_path)
        )
        artifacts_manifest[str(relative_path)] = {
            "path": str(Path("bundles") / effective_source_sha / str(relative_path)),
            "sha256": file_sha,
            "export_kind": export_kind,
        }
    bundle_path = bundle_root / "source-authority-bundle.json"
    bundle_sha = _write_json(bundle_path, persisted_bundle)
    manifest = {
        "kind": "source_authority_feed_manifest",
        "contract_version": AUTHORITY_FEED_CONTRACT_VERSION,
        "generated_at": persisted_bundle.get("generated_at"),
        "source_repo_id": persisted_bundle["repo_role"]["repo_id"],
        "source_sha": effective_source_sha,
        "bundle": {
            "path": str(Path("bundles") / effective_source_sha / "source-authority-bundle.json"),
            "sha256": bundle_sha,
            "kind": "source_authority_bundle",
        },
        "artifacts": artifacts_manifest,
    }
    manifest_path = target_root / "latest-authority-manifest.json"
    _write_json(manifest_path, manifest)
    return manifest_path, manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="steward-authority-feed")
    parser.add_argument("--workspace", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--source-sha", default="")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path, manifest = write_authority_feed(
        workspace=args.workspace,
        output_dir=args.output_dir,
        source_sha=(args.source_sha or None),
    )
    print(
        json.dumps(
            {"output": str(path), "repo_id": manifest["source_repo_id"], "source_sha": manifest["source_sha"]}, indent=2
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
