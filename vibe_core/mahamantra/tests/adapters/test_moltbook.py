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


def test_challenge_solver_division():
    assert ChallengeSolver.solve("What is twenty divided by 4?") == "5"
    assert ChallengeSolver.solve("100 / five") == "20"


def test_challenge_solver_edge_cases():
    assert ChallengeSolver.solve("What is the meaning of life?") == "0"
    assert ChallengeSolver.solve("Just the number 5") == "0"


def test_challenge_solver_compound_numbers():
    """Compound numbers must NOT be corrupted by substring replacement.
    'eighteen' must NOT become '8een'. This was a real bug."""
    assert ChallengeSolver.solve("What is eighteen + 2?") == "20"
    assert ChallengeSolver.solve("What is eighteen - eight?") == "10"
    assert ChallengeSolver.solve("What is eighty + twenty?") == "100"
    assert ChallengeSolver.solve("What is thirteen + seven?") == "20"
    assert ChallengeSolver.solve("What is nineteen - nine?") == "10"
    assert ChallengeSolver.solve("What is fifteen * two?") == "30"
    assert ChallengeSolver.solve("What is ninety - fifty?") == "40"


def test_challenge_solver_teens_and_tens():
    """All teen/tens numbers should be recognized."""
    assert ChallengeSolver.solve("eleven + twelve") == "23"
    assert ChallengeSolver.solve("fourteen + sixteen") == "30"
    assert ChallengeSolver.solve("seventeen - thirteen") == "4"
    assert ChallengeSolver.solve("thirty + forty") == "70"
    assert ChallengeSolver.solve("sixty - fifty") == "10"
    assert ChallengeSolver.solve("seventy + ninety") == "160"


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
async def test_comment_hourly_limit():
    """50 comments per hour — verified against API README."""
    client = MoltbookClient(api_key="offline_key", offline_mode=True)
    client.limits.comments_this_hour = 49

    # This triggers a challenge (first comment attempt), so _enforce_limits runs once
    # for the initial attempt, then the challenge retry also runs _enforce_limits.
    # But comment_with_verification now decrements on challenge, so net = +1.
    await client._request("POST", "/posts/p1/comments", {"content": "Hello", "challenge_solution": "x"})
    assert client.limits.comments_this_hour == 50

    with pytest.raises(Exception, match="Hourly comment limit exceeded"):
        await client._request("POST", "/posts/p1/comments", {"content": "Spam", "challenge_solution": "x"})


@pytest.mark.asyncio
async def test_comment_verification_does_not_double_count():
    """A challenged comment must count as 1, not 2, against the hourly limit.
    This was a real bug — comment_with_verification called _request twice."""
    client = MoltbookClient(api_key="offline_key", offline_mode=True)
    initial = client.limits.comments_this_hour

    await client.comment_with_verification("post_123", "Hello!")
    # Should be initial + 1, NOT initial + 2
    assert client.limits.comments_this_hour == initial + 1


# =============================================================================
# Registration (unauthenticated endpoint)
# =============================================================================


def test_sync_register_offline():
    """Registration works in offline mode and returns expected structure."""
    client = MoltbookClient(api_key="", offline_mode=True)
    result = client.sync_register("TestAgent", "A test agent")
    assert "agent" in result
    assert "api_key" in result["agent"]
    assert result["agent"]["api_key"] == "moltbook_offline_test_key"
    assert "claim_url" in result["agent"]
    assert "verification_code" in result["agent"]
    assert result["important"] == "Save your API key!"


# =============================================================================
# Verification Flow
# =============================================================================


@pytest.mark.asyncio
async def test_comment_verification_flow():
    """comment_with_verification auto-solves the math challenge."""
    client = MoltbookClient(api_key="offline_key", offline_mode=True)
    res = await client.comment_with_verification("post_123", "Brilliant architecture!")
    assert res.get("id") == "c99", "Failed to auto-solve verification challenge"


# =============================================================================
# Offline Mock — Conversations
# =============================================================================


@pytest.mark.asyncio
async def test_offline_dm_conversations():
    """Offline mock returns conversation list from mock_db."""
    client = MoltbookClient(api_key="offline_key", offline_mode=True)
    client._mock_db["conversations"] = [
        {"id": "conv1", "with": "AgentX"},
        {"id": "conv2", "with": "AgentY"},
    ]
    convs = await client.get_dm_conversations()
    assert len(convs) == 2
    assert convs[0]["id"] == "conv1"


@pytest.mark.asyncio
async def test_offline_dm_messages_by_conversation():
    """Offline mock filters messages by conversation_id."""
    client = MoltbookClient(api_key="offline_key", offline_mode=True)
    client._mock_db["dms"] = [
        {"conversation_id": "conv1", "sender": "AgentX", "content": "Hello"},
        {"conversation_id": "conv2", "sender": "AgentY", "content": "Hi"},
        {"conversation_id": "conv1", "sender": "AgentX", "content": "Follow up"},
    ]
    msgs = await client.get_dm_messages("conv1")
    assert len(msgs) == 2
    assert all(m["conversation_id"] == "conv1" for m in msgs)


def test_sync_get_dm_conversations():
    """sync_get_dm_conversations works from plain sync context."""
    client = MoltbookClient(api_key="offline_key", offline_mode=True)
    client._mock_db["conversations"] = [{"id": "c1"}]
    convs = client.sync_get_dm_conversations()
    assert len(convs) == 1


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
