from pathlib import Path

import pytest

from vibe_core.naga.mixins.tuv import TuvBadge, TuvMixin
from vibe_core.naga.services.tuv import TÜVService


class TestTuvIntegration:
    """
    Integration Test: TÜV Service -> Badge -> Mixin.
    The Ouroboros Cycle.
    """

    def test_badge_issuance_and_check(self, tmp_path):
        # 1. Instantiate Service
        registry_path = tmp_path / "tuv_registry.json"
        tuv = TÜVService(registry_path=registry_path)

        # 2. Issue Badge
        badge = tuv.issue_badge("test_agent")
        assert isinstance(badge, TuvBadge)
        assert badge.entity_id == "test_agent"
        assert badge.score == 1.0

        # 3. Inject into Mixin
        agent = TuvMixin()
        agent.inject_tuv_badge(badge)

        # 4. Check Validity
        assert agent.check_tuv_badge() is True
        assert agent.tuv_score == 1.0

    def test_verify_badge(self, tmp_path):
        registry_path = tmp_path / "tuv_registry_verify.json"
        tuv = TÜVService(registry_path=registry_path)
        badge = tuv.issue_badge("valid_agent")

        # Service verification
        assert tuv.verify_badge(badge) is True
