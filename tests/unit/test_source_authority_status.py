from pathlib import Path

from vibe_core.source_authority_status import get_source_authority_for_chat, handle_source_authority_query


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_handle_source_authority_query_describes_available_exports():
    result = handle_source_authority_query("show authority bundle", workspace=_repo_root())

    assert "Source Authority Export" in result
    assert "canonical_surface" in result
    assert "source_surface_registry" in result


def test_handle_source_authority_query_redirects_local_wiki_publish_requests():
    result = handle_source_authority_query("sync wiki", workspace=_repo_root())

    assert "agent-internet" in result
    assert "no longer publishes local wiki pages" in result


def test_get_source_authority_for_chat_reports_neutral_boundary():
    result = get_source_authority_for_chat(workspace=_repo_root())

    assert "Source Authority Export" in result
    assert "agent-internet" in result
    assert "no longer runs through `sutra.py`" in result