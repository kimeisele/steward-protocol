from unittest.mock import MagicMock

import pytest

from vibe_core.phoenix.sections.steward.section_main import BehaviorConfig, StewardConfig, UserContext, UserPreferences
from vibe_core.protocols.identity import IdentityProtocol
from vibe_core.steward.manager import DigitalSteward


class TestActiveSteward:
    @pytest.fixture
    def mock_identity(self):
        return MagicMock(spec=IdentityProtocol)

    @pytest.fixture
    def strict_config(self):
        """A strict persona config."""
        config = StewardConfig()
        config.behavior = BehaviorConfig(anti_slop_rules=True, require_tests=True)
        config.user_context = UserContext(default_user=UserPreferences(role="strict_architect"))
        return config

    @pytest.fixture
    def relaxed_config(self):
        """A relaxed persona config."""
        config = StewardConfig()
        config.behavior = BehaviorConfig(anti_slop_rules=False, require_tests=False)
        return config

    def test_anti_slop_blocks_empty_context(self, mock_identity, strict_config):
        steward = DigitalSteward(mock_identity, strict_config)

        # Anti-slop enabled: Empty details should block
        assert steward.sign_off("any_op", {}) is False

        # Populated details should pass (if no other rule blocks)
        assert steward.sign_off("any_op", {"reason": "valid"}) is True

    def test_require_tests_blocks_deploy(self, mock_identity, strict_config):
        steward = DigitalSteward(mock_identity, strict_config)

        # Deploy without tests_passed
        context = {"reason": "yolo"}
        assert steward.sign_off("deploy", context) is False

        # Deploy with tests_passed
        context_valid = {"tests_passed": True, "reason": "verified"}
        assert steward.sign_off("deploy", context_valid) is True

    def test_relaxed_steward_allows_slop(self, mock_identity, relaxed_config):
        steward = DigitalSteward(mock_identity, relaxed_config)

        # Anti-slop disabled: Empty details OK
        assert steward.sign_off("any_op", {}) is True

        # Require tests disabled: Deploy without tests OK
        assert steward.sign_off("deploy", {"reason": "yolo"}) is True
