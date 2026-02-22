"""
Moltbook Adapter Tests — Offline Verification
==============================================

Tests rate limiting, challenge solving, and the sync bridge.
All tests run in offline mode — zero network calls.
"""

import pytest

from vibe_core.mahamantra.adapters.moltbook import (
    ChallengeSolver,
    MoltbookClient,
    MoltbookLimits,
)

# =============================================================================
# Challenge Solver
# =============================================================================


def test_challenge_solver_addition():
    assert ChallengeSolver.solve("What is seven + 3?") == "10"
    assert ChallengeSolver.solve("Please add 5 and four") == "9"
    assert ChallengeSolver.solve("8 plus two equals") == "10"


def test_challenge_solver_subtraction():
    assert ChallengeSolver.solve("What is ten - 3?") == "7"
    assert ChallengeSolver.solve("nine minus four is") == "5"


def test_challenge_solver_multiplication():
    assert ChallengeSolver.solve("What is two * 3?") == "6"
    assert ChallengeSolver.solve("four times five") == "20"


def test_challenge_solver_edge_cases():
    assert ChallengeSolver.solve("What is the meaning of life?") == "0"
    assert ChallengeSolver.solve("Just the number 5") == "0"


# =============================================================================
# Rate Limits
# =============================================================================


@pytest.mark.asyncio
async def test_minute_rate_limit():
    client = MoltbookClient(api_key="offline_key", offline_mode=True)
    client.limits.requests_this_minute = 99

    await client.check_status()
    assert client.limits.requests_this_minute == 100

    with pytest.raises(Exception, match="Minute rate limit exceeded"):
        await client.check_status()


@pytest.mark.asyncio
async def test_post_rate_limit():
    client = MoltbookClient(api_key="offline_key", offline_mode=True)

    post = await client.create_post("Title", "Content")
    assert post.get("id") == "p0"
    assert client.limits.posts_this_30m == 1

    with pytest.raises(Exception, match="Post rate limit \\(1/30m\\) exceeded"):
        await client.create_post("Spam", "Spam")


@pytest.mark.asyncio
async def test_comment_daily_limit():
    client = MoltbookClient(api_key="offline_key", offline_mode=True)
    client.limits.comments_today = 49

    await client._request("POST", "/posts/p1/comments", {"content": "Hello"})
    assert client.limits.comments_today == 50

    with pytest.raises(Exception, match="Daily comment limit exceeded"):
        await client._request("POST", "/posts/p1/comments", {"content": "Spam"})


# =============================================================================
# Verification Flow
# =============================================================================


@pytest.mark.asyncio
async def test_comment_verification_flow():
    client = MoltbookClient(api_key="offline_key", offline_mode=True)
    res = await client.comment_with_verification("post_123", "Brilliant architecture!")
    assert res.get("id") == "c99", "Failed to auto-solve verification challenge"


# =============================================================================
# Sync Bridge
# =============================================================================


def test_sync_check_heartbeat():
    """sync_check_heartbeat() must work from plain sync context."""
    client = MoltbookClient(api_key="offline_key", offline_mode=True)
    result = client.sync_check_heartbeat()
    assert result.get("has_new_messages") is False
    assert "pending_requests" in result


def test_sync_create_post():
    """sync_create_post() must work from plain sync context."""
    client = MoltbookClient(api_key="offline_key", offline_mode=True)
    post = client.sync_create_post("Test Title", "Test Content")
    assert post.get("id") == "p0"
    assert post.get("title") == "Test Title"


def test_sync_bridge_respects_rate_limits():
    """Sync bridge must still enforce rate limits."""
    client = MoltbookClient(api_key="offline_key", offline_mode=True)
    client.limits.requests_this_minute = 100

    with pytest.raises(Exception, match="Minute rate limit exceeded"):
        client.sync_check_heartbeat()
