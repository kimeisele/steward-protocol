from __future__ import annotations

import json
import subprocess
from pathlib import Path

from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraOrchestrator

WIKI_GENERATED_INVENTORY = ".wiki-generated-inventory.json"
WIKI_SURFACE_REGISTRY = ".wiki-surface-registry.json"


def build_wiki(*, root: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    orchestrator = SutraOrchestrator(workspace=root)
    pages = orchestrator.generate()
    built: list[Path] = []
    for page in pages:
        path = output_dir / page.filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(page.content)
        built.append(path)
    registry_export = getattr(orchestrator, "export_surface_metadata", None)
    if callable(registry_export):
        registry_path = output_dir / WIKI_SURFACE_REGISTRY
        registry_path.write_text(json.dumps(registry_export(), indent=2, sort_keys=True) + "\n")
        built.append(registry_path)
    return built


def publish_wiki(
    *,
    root: Path,
    wiki_path: Path | None = None,
    wiki_repo_url: str | None = None,
    push: bool = False,
    prune_generated: bool = False,
) -> dict:
    effective_wiki_repo_url = wiki_repo_url or _detect_wiki_repo_url(root)
    checkout = ensure_wiki_checkout(workspace=root, wiki_repo_url=effective_wiki_repo_url, wiki_path=wiki_path)
    _ensure_local_git_identity(checkout)
    built = build_wiki(root=root, output_dir=checkout)
    generated_paths = sorted(_normalize_relative_paths(checkout, built))
    pruned = _prune_generated_paths(checkout, keep_paths=generated_paths) if prune_generated else []
    _write_generated_inventory(checkout, generated_paths)
    _git_run(["add", "."], cwd=checkout)
    status = _git_output(["status", "--porcelain"], cwd=checkout)
    source_sha = _git_output(["rev-parse", "HEAD"], cwd=root).strip() or "unknown"
    commit_message = f"wiki: publish SUTRA from {source_sha}"
    if not status.strip():
        return {
            "changed": False,
            "built": len(built),
            "generated_inventory": str(checkout / WIKI_GENERATED_INVENTORY),
            "prune_generated": prune_generated,
            "pruned": len(pruned),
            "pruned_paths": pruned,
            "wiki_path": str(checkout),
            "wiki_repo_url": effective_wiki_repo_url,
            "pushed": False,
            "source_sha": source_sha,
            "commit_message": commit_message,
        }
    _git_run(["commit", "-m", commit_message], cwd=checkout)
    if push:
        branch = _git_output(["branch", "--show-current"], cwd=checkout).strip() or "master"
        _git_run(["push", "-u", "origin", branch], cwd=checkout)
    return {
        "changed": True,
        "built": len(built),
        "generated_inventory": str(checkout / WIKI_GENERATED_INVENTORY),
        "prune_generated": prune_generated,
        "pruned": len(pruned),
        "pruned_paths": pruned,
        "wiki_path": str(checkout),
        "wiki_repo_url": effective_wiki_repo_url,
        "pushed": push,
        "source_sha": source_sha,
        "commit_message": commit_message,
    }


def write_publication_result(path: Path, result: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return path


def ensure_wiki_checkout(*, workspace: Path, wiki_repo_url: str, wiki_path: Path | None = None) -> Path:
    checkout = wiki_path or workspace / ".vibe" / "wiki"
    if not checkout.exists():
        checkout.parent.mkdir(parents=True, exist_ok=True)
        try:
            _git_run(["clone", wiki_repo_url, str(checkout)], cwd=workspace)
        except subprocess.CalledProcessError as exc:
            detail = f"{exc.stdout}\n{exc.stderr}".lower()
            if "repository not found" in detail or "not found" in detail:
                raise RuntimeError(
                    f"wiki repo is not materialized yet: {wiki_repo_url}. Create the first GitHub wiki page, then rerun publish."
                ) from exc
            raise
        return checkout
    _git_run(["fetch", "origin", "--prune"], cwd=checkout)
    current_branch = _git_output(["branch", "--show-current"], cwd=checkout).strip()
    remote_branches = _git_output(["for-each-ref", "--format=%(refname:short)", "refs/remotes/origin"], cwd=checkout).splitlines()
    if current_branch and f"origin/{current_branch}" in remote_branches:
        _git_run(["pull", "--rebase", "origin", current_branch], cwd=checkout)
    return checkout


def _detect_wiki_repo_url(root: Path) -> str:
    origin = _git_output(["remote", "get-url", "origin"], cwd=root).strip()
    if origin.endswith(".git"):
        return origin[:-4] + ".wiki.git"
    return origin + ".wiki.git"


def _git_run(args: list[str], *, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True, text=True)


def _git_output(args: list[str], *, cwd: Path) -> str:
    completed = subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True, text=True)
    return completed.stdout


def _ensure_local_git_identity(checkout: Path) -> None:
    for key, value in (("user.name", "sutra-bot"), ("user.email", "bot@steward-protocol")):
        current = subprocess.run(["git", "config", key], cwd=str(checkout), check=False, capture_output=True, text=True)
        if getattr(current, "returncode", 0) != 0 or not getattr(current, "stdout", "").strip():
            _git_run(["config", key, value], cwd=checkout)


def _normalize_relative_paths(root: Path, built: list[Path]) -> list[str]:
    return [_normalize_relative_path(Path(path).resolve().relative_to(root.resolve()).as_posix()) for path in built]


def _normalize_relative_path(path: str) -> str:
    relative = Path(path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"unsafe wiki relative path: {path}")
    return relative.as_posix()


def _read_generated_inventory(root: Path) -> list[str]:
    path = root / WIKI_GENERATED_INVENTORY
    if not path.exists():
        return []
    payload = json.loads(path.read_text())
    return [_normalize_relative_path(str(item)) for item in payload.get("files", [])]


def _write_generated_inventory(root: Path, files: list[str]) -> Path:
    path = root / WIKI_GENERATED_INVENTORY
    payload = {"kind": "generated_wiki_inventory", "version": 1, "files": sorted({_normalize_relative_path(path) for path in files})}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return path


def _prune_generated_paths(root: Path, *, keep_paths: list[str]) -> list[str]:
    keep = {_normalize_relative_path(path) for path in keep_paths}
    stale = [path for path in _read_generated_inventory(root) if path not in keep]
    removed: list[str] = []
    for relative_path in stale:
        target = root / relative_path
        if target.exists():
            target.unlink()
            removed.append(relative_path)
    return removed