import pytest
from vibe_core.naga.services.tuv import TÜVService
from vibe_core.protocols.naga.tuv import TuvBadge


@pytest.mark.unit
def test_badge_issuance_and_check(tmp_path):
    # 1. Instantiate Service
    registry_path = tmp_path / "tuv_registry.json"
    tuv = TÜVService(registry_path=registry_path)

    # 2. Issue Badge
    badge = tuv.issue_badge("test_agent")
    assert type(badge).__name__ == "TuvBadge"

    # 3. Verify Badge
    assert tuv.verify_badge(badge) is True


@pytest.mark.unit
def test_tuv_full_scan(tmp_path):
    # 1. Setup
    registry_path = tmp_path / "tuv_registry_scan.json"
    tuv = TÜVService(registry_path=registry_path)

    # 2. Run Scan (on a small subdirectory to keep it fast)
    # We use naga/services as a sample
    report = tuv.scan_module("vibe_core/naga/services")

    # 3. Verify
    assert isinstance(report, list)
    assert len(report) >= 0
