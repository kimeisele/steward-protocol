from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

from vibe_core.wiki_publisher import build_wiki, ensure_wiki_checkout, publish_wiki


def test_build_wiki_materializes_sutra_pages(tmp_path, monkeypatch):
    class FakeOrchestrator:
        def __init__(self, workspace):
            self.workspace = workspace

        def generate(self):
            return [SimpleNamespace(filename="Home.md", content="# Home\n"), SimpleNamespace(filename="_Sidebar.md", content="* nav\n")]

    monkeypatch.setattr("vibe_core.wiki_publisher.SutraOrchestrator", FakeOrchestrator)
    built = build_wiki(root=tmp_path, output_dir=tmp_path / "out")
    assert [path.name for path in built] == ["Home.md", "_Sidebar.md"]
    assert (tmp_path / "out" / "Home.md").exists()


def test_ensure_wiki_checkout_clones_when_missing(tmp_path, monkeypatch):
    calls = []

    def fake_run(cmd, cwd, check, capture_output, text):
        calls.append((cmd, cwd))
        if cmd[:2] == ["git", "clone"]:
            Path(cmd[3]).mkdir(parents=True, exist_ok=True)
        return SimpleNamespace(stdout="", stderr="")

    monkeypatch.setattr("vibe_core.wiki_publisher.subprocess.run", fake_run)
    checkout = ensure_wiki_checkout(workspace=tmp_path, wiki_repo_url="git@example:wiki.git")
    assert checkout.exists()
    assert calls[0][0][:2] == ["git", "clone"]


def test_publish_wiki_commits_without_push(tmp_path, monkeypatch):
    checkout = tmp_path / "wiki"
    checkout.mkdir()
    calls = []

    monkeypatch.setattr("vibe_core.wiki_publisher.ensure_wiki_checkout", lambda **kwargs: checkout)
    monkeypatch.setattr("vibe_core.wiki_publisher.build_wiki", lambda root, output_dir: _write_pages(output_dir, ["Home.md"]))
    monkeypatch.setattr("vibe_core.wiki_publisher._detect_wiki_repo_url", lambda root: "git@example:wiki.git")

    def fake_run(cmd, cwd, check, capture_output, text):
        calls.append(cmd)
        if cmd[:3] == ["git", "status", "--porcelain"]:
            return SimpleNamespace(stdout=" M Home.md\n", stderr="")
        if cmd[:3] == ["git", "rev-parse", "HEAD"]:
            return SimpleNamespace(stdout="abc123\n", stderr="")
        return SimpleNamespace(stdout="", stderr="")

    monkeypatch.setattr("vibe_core.wiki_publisher.subprocess.run", fake_run)
    result = publish_wiki(root=Path.cwd(), wiki_path=checkout, push=False)
    assert result["changed"] is True
    assert result["pushed"] is False
    assert result["pruned"] == 0
    assert result["source_sha"] == "abc123"
    assert (checkout / ".wiki-generated-inventory.json").exists()
    assert ["git", "commit", "-m", "wiki: publish SUTRA from abc123"] in calls


def test_publish_wiki_prunes_stale_generated_pages_and_keeps_manual_pages(tmp_path, monkeypatch):
    wiki_remote = _init_bare_remote(tmp_path / "wiki-remote.git")
    checkout = tmp_path / "wiki-checkout"
    monkeypatch.setattr("vibe_core.wiki_publisher.build_wiki", lambda root, output_dir: _write_pages(output_dir, ["Home.md"]))
    publish_wiki(root=Path.cwd(), wiki_path=checkout, wiki_repo_url=str(wiki_remote), push=False, prune_generated=True)

    stale_generated = checkout / "Legacy-Generated.md"
    stale_generated.write_text("# Legacy\n")
    manual_page = checkout / "Manual-Page.md"
    manual_page.write_text("# Manual\n")
    inventory = checkout / ".wiki-generated-inventory.json"
    payload = json.loads(inventory.read_text())
    payload["files"].append("Legacy-Generated.md")
    inventory.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    _git(checkout, "add", ".")
    _git(checkout, "commit", "-m", "add stale generated and manual pages")

    result = publish_wiki(root=Path.cwd(), wiki_path=checkout, wiki_repo_url=str(wiki_remote), push=False, prune_generated=True)
    assert result["pruned"] == 1
    assert result["pruned_paths"] == ["Legacy-Generated.md"]
    assert not stale_generated.exists()
    assert manual_page.exists()


def _write_pages(output_dir: Path, names: list[str]) -> list[Path]:
    built: list[Path] = []
    for name in names:
        path = output_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {Path(name).stem}\n")
        built.append(path)
    return built


def _init_bare_remote(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "--bare", str(path)], check=True, capture_output=True, text=True)
    return path


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True, text=True)