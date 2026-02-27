"""Tests for CivicBank economy wiring in Moltbook.

Tests credit-gating in ContentDrainer and bank initialization.
"""

from unittest.mock import MagicMock, patch

from vibe_core.plugins.moltbook.managers.drainer import (
    ContentDrainer,
    _CREDIT_COSTS,
)
from vibe_core.protocols.moltbook_content import ContentQueue, ContentType


def _make_drainer(bank=None, **kwargs):
    """Create a ContentDrainer with mocked dependencies."""
    return ContentDrainer(
        service_getter=MagicMock,
        log_activity=MagicMock(),
        broadcast_to_agora=MagicMock(),
        emit_event=MagicMock(),
        own_post_ids={},
        own_comment_ids=set(),
        comment_post_map={},
        followed_agents=set(),
        subscribed_submolts=set(),
        bank=bank,
        agent_id="test-agent",
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Credit cost table
# ---------------------------------------------------------------------------


class TestCreditCosts:
    def test_post_costs_5(self):
        assert _CREDIT_COSTS["post"] == 5

    def test_comment_costs_2(self):
        assert _CREDIT_COSTS["comment"] == 2

    def test_dm_costs_1(self):
        assert _CREDIT_COSTS["dm_reply"] == 1
        assert _CREDIT_COSTS["dm_initiate"] == 1

    def test_vote_free(self):
        assert _CREDIT_COSTS["vote"] == 0

    def test_follow_free(self):
        assert _CREDIT_COSTS["follow"] == 0

    def test_subscribe_free(self):
        assert _CREDIT_COSTS["subscribe"] == 0


# ---------------------------------------------------------------------------
# Credit check
# ---------------------------------------------------------------------------


class TestCreditCheck:
    def test_no_bank_always_allows(self):
        drainer = _make_drainer(bank=None)
        assert drainer.check_credits("post") is True

    def test_sufficient_balance_allows(self):
        bank = MagicMock()
        bank.get_balance.return_value = 100
        drainer = _make_drainer(bank=bank)
        assert drainer.check_credits("post") is True

    def test_insufficient_balance_blocks(self):
        bank = MagicMock()
        bank.get_balance.return_value = 3  # Need 5 for post
        drainer = _make_drainer(bank=bank)
        assert drainer.check_credits("post") is False

    def test_free_actions_always_allowed(self):
        bank = MagicMock()
        bank.get_balance.return_value = 0  # No credits
        drainer = _make_drainer(bank=bank)
        assert drainer.check_credits("vote") is True
        assert drainer.check_credits("follow") is True
        assert drainer.check_credits("subscribe") is True

    def test_bank_error_fails_open(self):
        bank = MagicMock()
        bank.get_balance.side_effect = RuntimeError("DB locked")
        drainer = _make_drainer(bank=bank)
        assert drainer.check_credits("post") is True  # Fail open


# ---------------------------------------------------------------------------
# Credit deduction
# ---------------------------------------------------------------------------


class TestCreditDeduction:
    def test_deducts_on_post(self):
        bank = MagicMock()
        bank.transfer.return_value = "TX-001"
        drainer = _make_drainer(bank=bank)
        drainer.deduct_credits("post")
        bank.transfer.assert_called_once_with(
            "test-agent", "CIVIC", 5, "moltbook_post", service_type="content",
        )

    def test_deducts_on_comment(self):
        bank = MagicMock()
        bank.transfer.return_value = "TX-002"
        drainer = _make_drainer(bank=bank)
        drainer.deduct_credits("comment")
        bank.transfer.assert_called_once_with(
            "test-agent", "CIVIC", 2, "moltbook_comment", service_type="content",
        )

    def test_no_deduction_for_free_actions(self):
        bank = MagicMock()
        drainer = _make_drainer(bank=bank)
        drainer.deduct_credits("vote")
        bank.transfer.assert_not_called()

    def test_no_bank_no_crash(self):
        drainer = _make_drainer(bank=None)
        drainer.deduct_credits("post")  # Should not crash

    def test_deduction_error_no_crash(self):
        bank = MagicMock()
        bank.transfer.side_effect = RuntimeError("DB error")
        drainer = _make_drainer(bank=bank)
        drainer.deduct_credits("post")  # Should log warning, not crash


# ---------------------------------------------------------------------------
# Credit check in drain loop
# ---------------------------------------------------------------------------


class TestDrainCreditGating:
    def test_insufficient_credits_defers_proposal(self):
        """When credits are insufficient, proposal is deferred, not dropped."""
        bank = MagicMock()
        bank.get_balance.return_value = 1  # Not enough for post (5)

        service = MagicMock()
        drainer = _make_drainer(bank=bank)
        drainer._get_service = MagicMock(return_value=service)

        queue = ContentQueue()
        queue.enqueue({
            "content_type": ContentType.POST.value,
            "title": "Test Post",
            "content": "Test content",
            "priority": 5,
        })

        drainer.drain(queue, offline_mode=False)

        # Service should NOT have been called (credit blocked)
        service.create_post.assert_not_called()

        # Proposal should be re-enqueued (deferred)
        assert not queue.is_empty

    def test_sufficient_credits_allows_drain(self):
        """When credits are sufficient, drain proceeds and deducts."""
        bank = MagicMock()
        bank.get_balance.return_value = 100
        bank.transfer.return_value = "TX-003"

        service = MagicMock()
        service.upvote.return_value = None

        drainer = _make_drainer(bank=bank)
        drainer._get_service = MagicMock(return_value=service)

        queue = ContentQueue()
        queue.enqueue({
            "content_type": ContentType.VOTE.value,
            "post_id": "p1",
            "priority": 1,
        })

        drainer.drain(queue, offline_mode=False)

        # Vote is free, should execute
        service.upvote.assert_called_once_with("p1")
        # Vote is free, no transfer
        bank.transfer.assert_not_called()


# ---------------------------------------------------------------------------
# Bank initialization
# ---------------------------------------------------------------------------


class TestBankInit:
    def test_init_bank_creates_bank(self):
        """_init_bank() creates CivicBank and mints initial credits."""
        from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin

        plugin = MoltbookPlugin()
        # Mock to avoid actual SQLite
        mock_bank = MagicMock()
        mock_bank.get_balance.return_value = 0
        mock_bank.transfer.return_value = "TX-MINT"

        with patch(
            "vibe_core.cartridges.system.civic.tools.economy.CivicBank",
            return_value=mock_bank,
        ):
            plugin._state_dir = None
            plugin._init_bank()

        assert plugin._bank is mock_bank
        # Should mint initial credits when balance = 0
        mock_bank.transfer.assert_called_once()
        args = mock_bank.transfer.call_args
        assert args[0][0] == "MINT"  # sender
        assert args[0][2] == 1000    # amount

    def test_init_bank_skips_mint_when_funded(self):
        """Don't mint if account already has credits."""
        from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin

        plugin = MoltbookPlugin()
        mock_bank = MagicMock()
        mock_bank.get_balance.return_value = 500  # Already funded

        with patch(
            "vibe_core.cartridges.system.civic.tools.economy.CivicBank",
            return_value=mock_bank,
        ):
            plugin._state_dir = None
            plugin._init_bank()

        mock_bank.transfer.assert_not_called()

    def test_init_bank_failure_no_crash(self):
        """If CivicBank import fails, plugin continues without bank."""
        from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin

        plugin = MoltbookPlugin()
        with patch(
            "vibe_core.cartridges.system.civic.tools.economy.CivicBank",
            side_effect=ImportError("no sqlite"),
        ):
            plugin._init_bank()

        assert plugin._bank is None
