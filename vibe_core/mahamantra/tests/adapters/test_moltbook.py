"""
Moltbook Adapter Tests — Fortress-Level Verification
=====================================================

Tests the MoltbookClient adapter layer: rate limiting, challenge solving,
offline mock fidelity, sync bridge equivalence, and API boundary contracts.

Organization (by concern):
    TestChallengeSolverArithmetic  — All four operators + edge cases
    TestChallengeSolverRegression  — Real bugs that MUST never recur
    TestChallengeSolverProperties  — Invariant: always returns str, never raises
    TestRateLimitConstants         — Limits match API README spec
    TestRateLimitMinute            — 100 req/min enforcement
    TestRateLimitPost              — 1 post / 30 min enforcement
    TestRateLimitComment           — 50 comments / hour enforcement
    TestRateLimitWindowReset       — Time-window reset behavior
    TestVerificationFlow           — Challenge auto-solve pipeline
    TestOfflineMock                — Mock fidelity for every endpoint
    TestSyncBridge                 — Sync/async equivalence
    TestRegistration               — Unauthenticated endpoint
    TestClientConstruction         — Init, defaults, state isolation
"""

import inspect
import time

import pytest

from vibe_core.mahamantra.adapters.moltbook import (
    ChallengeSolver,
    MoltbookClient,
    MoltbookLimits,
    RateLimitState,
    run_async,
)

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def client():
    """Fresh offline client for each test — complete state isolation."""
    return MoltbookClient(api_key="offline_key", offline_mode=True)


# =============================================================================
# CHALLENGE SOLVER — Arithmetic
# =============================================================================


class TestChallengeSolverArithmetic:
    """ChallengeSolver handles all four arithmetic operators correctly."""

    def test_addition_with_digit(self):
        assert ChallengeSolver.solve("What is seven + 3?") == "10"

    def test_addition_with_word(self):
        assert ChallengeSolver.solve("Please add 5 and four") == "9"

    def test_addition_plus_keyword(self):
        assert ChallengeSolver.solve("8 plus two equals") == "10"

    def test_subtraction_with_minus(self):
        assert ChallengeSolver.solve("What is ten - 3?") == "7"

    def test_subtraction_with_word(self):
        assert ChallengeSolver.solve("nine minus four is") == "5"

    def test_multiplication_with_star(self):
        assert ChallengeSolver.solve("What is two * 3?") == "6"

    def test_multiplication_with_times(self):
        assert ChallengeSolver.solve("four times five") == "20"

    def test_division_with_divided_by(self):
        assert ChallengeSolver.solve("What is twenty divided by 4?") == "5"

    def test_division_with_slash(self):
        assert ChallengeSolver.solve("100 / five") == "20"

    def test_division_by_zero_returns_zero(self):
        """Division by zero must return '0', not raise."""
        assert ChallengeSolver.solve("10 / zero") == "0"


class TestChallengeSolverRegression:
    """Bug regressions — each test documents a real production bug."""

    def test_eighteen_not_corrupted(self):
        """BUG: str.replace('eight', '8') turned 'eighteen' into '8een'.
        FIX: Word-boundary regex + compound-first ordering."""
        assert ChallengeSolver.solve("What is eighteen + 2?") == "20"

    def test_eighteen_minus_eight(self):
        """Both 'eighteen' and 'eight' in same challenge."""
        assert ChallengeSolver.solve("What is eighteen - eight?") == "10"

    def test_eighty_not_corrupted(self):
        """'eighty' must not become '8y'."""
        assert ChallengeSolver.solve("What is eighty + twenty?") == "100"

    def test_thirteen_not_corrupted(self):
        """'thirteen' must not become '3teen'."""
        assert ChallengeSolver.solve("What is thirteen + seven?") == "20"

    def test_nineteen_not_corrupted(self):
        """'nineteen' must not become '9teen'."""
        assert ChallengeSolver.solve("What is nineteen - nine?") == "10"

    def test_fifteen_not_corrupted(self):
        """'fifteen' must not become '5teen'."""
        assert ChallengeSolver.solve("What is fifteen * two?") == "30"

    def test_ninety_not_corrupted(self):
        """'ninety' must not become '9ty'."""
        assert ChallengeSolver.solve("What is ninety - fifty?") == "40"


class TestChallengeSolverTeens:
    """All teen and tens numbers are recognized."""

    def test_eleven(self):
        assert ChallengeSolver.solve("eleven + one") == "12"

    def test_twelve(self):
        assert ChallengeSolver.solve("twelve + one") == "13"

    def test_fourteen(self):
        assert ChallengeSolver.solve("fourteen + sixteen") == "30"

    def test_seventeen(self):
        assert ChallengeSolver.solve("seventeen - thirteen") == "4"

    def test_thirty_forty(self):
        assert ChallengeSolver.solve("thirty + forty") == "70"

    def test_sixty_fifty(self):
        assert ChallengeSolver.solve("sixty - fifty") == "10"

    def test_seventy_ninety(self):
        assert ChallengeSolver.solve("seventy + ninety") == "160"


class TestChallengeSolverProperties:
    """Mathematical properties that must hold for ANY input."""

    def test_always_returns_string(self):
        """Output is always str — never int, never None, never raises."""
        inputs = [
            "What is seven + 3?",
            "Just nonsense here",
            "",
            "42",
            "a + b",
        ]
        for inp in inputs:
            result = ChallengeSolver.solve(inp)
            assert isinstance(result, str), f"solve({inp!r}) returned {type(result)}"

    def test_insufficient_numbers_returns_zero(self):
        """Less than 2 numbers → '0' (unknown, safe fallback)."""
        assert ChallengeSolver.solve("What is the meaning of life?") == "0"
        assert ChallengeSolver.solve("Just the number 5") == "0"
        assert ChallengeSolver.solve("") == "0"

    def test_unknown_operator_returns_zero(self):
        """Two numbers but no recognized operator → '0'."""
        assert ChallengeSolver.solve("is 5 greater than 3?") == "0"

    def test_word_map_has_no_duplicates(self):
        """Every word in WORD_MAP appears exactly once."""
        words = [w for w, _ in ChallengeSolver.WORD_MAP]
        assert len(words) == len(set(words)), "Duplicate words in WORD_MAP"

    def test_compound_numbers_listed_before_substrings(self):
        """Compound numbers (eighteen, eighty, ...) must appear BEFORE their
        substrings (eight, nine, ...) in WORD_MAP to prevent corruption."""
        word_list = [w for w, _ in ChallengeSolver.WORD_MAP]

        # 'eighteen' must come before 'eight'
        assert word_list.index("eighteen") < word_list.index("eight"), "eighteen must precede eight in WORD_MAP"
        # 'eighty' must come before 'eight'
        assert word_list.index("eighty") < word_list.index("eight"), "eighty must precede eight in WORD_MAP"
        # 'nineteen' must come before 'nine'
        assert word_list.index("nineteen") < word_list.index("nine"), "nineteen must precede nine in WORD_MAP"
        # 'ninety' must come before 'nine'
        assert word_list.index("ninety") < word_list.index("nine"), "ninety must precede nine in WORD_MAP"


# =============================================================================
# RATE LIMIT CONSTANTS — Match API README spec
# =============================================================================


class TestRateLimitConstants:
    """Rate limit constants must match the Moltbook API README (2026-02-22)."""

    def test_requests_per_minute(self):
        """API spec: 100 requests per minute."""
        assert MoltbookLimits.REQ_PER_MIN == 100

    def test_posts_per_30_minutes(self):
        """API spec: 1 post per 30 minutes."""
        assert MoltbookLimits.POST_PER_30_MIN == 1

    def test_comments_per_hour(self):
        """API spec: 50 comments per hour (NOT per day)."""
        assert MoltbookLimits.COMMENTS_PER_HOUR == 50

    def test_avatar_size_1mb(self):
        assert MoltbookLimits.AVATAR_MAX_BYTES == 1024 * 1024

    def test_banner_size_2mb(self):
        assert MoltbookLimits.BANNER_MAX_BYTES == 2 * 1024 * 1024


# =============================================================================
# RATE LIMIT — Minute Enforcement
# =============================================================================


class TestRateLimitMinute:
    """100 requests per minute enforcement — the global seal."""

    @pytest.mark.asyncio
    async def test_99th_request_succeeds(self, client):
        """Request #100 must succeed (limit is >=, not >)."""
        client.limits.requests_this_minute = 99
        await client.check_status()
        assert client.limits.requests_this_minute == 100

    @pytest.mark.asyncio
    async def test_101st_request_blocked(self, client):
        """Request #101 must be blocked with specific error message."""
        client.limits.requests_this_minute = 100
        with pytest.raises(Exception, match="Minute rate limit exceeded"):
            await client.check_status()

    def test_sync_bridge_enforces_same_limit(self, client):
        """Sync wrapper must enforce the same limit — no bypass path."""
        client.limits.requests_this_minute = 100
        with pytest.raises(Exception, match="Minute rate limit exceeded"):
            client.sync_check_heartbeat()

    @pytest.mark.asyncio
    async def test_counter_increments_on_every_request(self, client):
        """Every successful request increments the counter."""
        assert client.limits.requests_this_minute == 0
        await client.check_status()
        assert client.limits.requests_this_minute == 1
        await client.check_status()
        assert client.limits.requests_this_minute == 2


# =============================================================================
# RATE LIMIT — Post Enforcement
# =============================================================================


class TestRateLimitPost:
    """1 post per 30 minutes — prevents spam bans."""

    @pytest.mark.asyncio
    async def test_first_post_succeeds(self, client):
        post = await client.create_post("Title", "Content")
        assert post.get("id") == "p0"
        assert client.limits.posts_this_30m == 1

    @pytest.mark.asyncio
    async def test_second_post_blocked(self, client):
        """Second post within 30 minutes must be blocked."""
        await client.create_post("First", "Content")
        with pytest.raises(Exception, match="Post rate limit \\(1/30m\\) exceeded"):
            await client.create_post("Second", "Spam")

    def test_sync_post_respects_limit(self, client):
        """Sync wrapper enforces same post limit."""
        client.sync_create_post("First", "Content")
        with pytest.raises(Exception, match="Post rate limit"):
            client.sync_create_post("Second", "Spam")


# =============================================================================
# RATE LIMIT — Comment Enforcement
# =============================================================================


class TestRateLimitComment:
    """50 comments per hour — hourly window, not daily."""

    @pytest.mark.asyncio
    async def test_49th_comment_succeeds(self, client):
        """Direct _request (with challenge_solution to bypass mock challenge)."""
        client.limits.comments_this_hour = 49
        await client._request("POST", "/posts/p1/comments", {"content": "hi", "challenge_solution": "x"})
        assert client.limits.comments_this_hour == 50

    @pytest.mark.asyncio
    async def test_51st_comment_blocked(self, client):
        client.limits.comments_this_hour = 50
        with pytest.raises(Exception, match="Hourly comment limit exceeded"):
            await client._request("POST", "/posts/p1/comments", {"content": "spam", "challenge_solution": "x"})

    @pytest.mark.asyncio
    async def test_verification_counts_as_one(self, client):
        """BUG REGRESSION: comment_with_verification must count as 1, not 2.
        The challenge attempt + retry are a SINGLE logical comment."""
        initial = client.limits.comments_this_hour
        await client.comment_with_verification("post_123", "Hello!")
        assert client.limits.comments_this_hour == initial + 1, (
            "comment_with_verification double-counted the rate limit"
        )


# =============================================================================
# RATE LIMIT — Window Reset Behavior
# =============================================================================


class TestRateLimitWindowReset:
    """Rate limit windows reset correctly when time advances."""

    @pytest.mark.asyncio
    async def test_minute_resets_after_60s(self, client):
        """After 60 seconds, minute counter resets to zero."""
        client.limits.requests_this_minute = 99
        client.limits.last_minute_reset = time.time() - 61  # 61 seconds ago
        await client.check_status()
        # Counter was reset then incremented: should be 1
        assert client.limits.requests_this_minute == 1

    @pytest.mark.asyncio
    async def test_post_resets_after_1800s(self, client):
        """After 1800 seconds (30 min), post counter resets."""
        client.limits.posts_this_30m = 1
        client.limits.last_30m_reset = time.time() - 1801
        post = await client.create_post("Title", "Content")
        assert post.get("id") is not None
        assert client.limits.posts_this_30m == 1  # Reset to 0, then +1

    @pytest.mark.asyncio
    async def test_comment_resets_after_3600s(self, client):
        """After 3600 seconds (1 hour), comment counter resets."""
        client.limits.comments_this_hour = 50
        client.limits.last_hour_reset = time.time() - 3601
        await client._request("POST", "/posts/p1/comments", {"content": "hi", "challenge_solution": "x"})
        assert client.limits.comments_this_hour == 1  # Reset to 0, then +1

    def test_rate_limit_state_defaults(self):
        """Fresh RateLimitState starts at zero for all counters."""
        state = RateLimitState()
        assert state.requests_this_minute == 0
        assert state.posts_this_30m == 0
        assert state.comments_this_hour == 0


# =============================================================================
# VERIFICATION FLOW — Challenge auto-solve pipeline
# =============================================================================


class TestVerificationFlow:
    """The challenge→solve→retry pipeline must be flawless."""

    @pytest.mark.asyncio
    async def test_auto_solves_challenge(self, client):
        """Full pipeline: POST → 403 → solve challenge → retry → success."""
        res = await client.comment_with_verification("post_123", "Great post!")
        assert res.get("id") == "c99", "Failed to auto-solve verification challenge"
        assert res.get("status") == "posted"

    @pytest.mark.asyncio
    async def test_challenge_response_not_counted(self, client):
        """The initial 403 challenge response must NOT count as a comment.
        Only the successful retry counts."""
        initial = client.limits.comments_this_hour
        await client.comment_with_verification("post_123", "Hello!")
        assert client.limits.comments_this_hour == initial + 1


# =============================================================================
# OFFLINE MOCK — Fidelity tests for every endpoint
# =============================================================================


class TestOfflineMock:
    """Every offline mock endpoint returns structurally correct data."""

    @pytest.mark.asyncio
    async def test_status_returns_claimed(self, client):
        status = await client.check_status()
        assert status == "claimed"

    @pytest.mark.asyncio
    async def test_search_returns_list(self, client):
        results = await client.semantic_search("test query")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_create_post_returns_post(self, client):
        post = await client.create_post("Title", "Content")
        assert "id" in post
        assert post["title"] == "Title"
        assert post["content"] == "Content"

    @pytest.mark.asyncio
    async def test_create_post_id_increments(self, client):
        """Post IDs increment: p0, p1, p2..."""
        p0 = await client.create_post("A", "a")
        # Reset post limit for second post
        client.limits.posts_this_30m = 0
        p1 = await client.create_post("B", "b")
        assert p0["id"] == "p0"
        assert p1["id"] == "p1"

    @pytest.mark.asyncio
    async def test_heartbeat_with_no_dms(self, client):
        hb = await client.check_heartbeat()
        assert hb["has_activity"] is False
        assert hb["requests"]["count"] == 0

    @pytest.mark.asyncio
    async def test_heartbeat_with_dms(self, client):
        client._mock_db["dms"] = [{"conversation_id": "c1", "content": "hi"}]
        hb = await client.check_heartbeat()
        assert hb["has_activity"] is True

    @pytest.mark.asyncio
    async def test_dm_conversations_from_mock_db(self, client):
        client._mock_db["conversations"] = [
            {"id": "conv1", "with": "AgentX"},
            {"id": "conv2", "with": "AgentY"},
        ]
        convs = await client.get_dm_conversations()
        assert len(convs) == 2
        assert convs[0]["id"] == "conv1"

    @pytest.mark.asyncio
    async def test_dm_conversations_empty_default(self, client):
        convs = await client.get_dm_conversations()
        assert convs == []

    @pytest.mark.asyncio
    async def test_dm_messages_filtered_by_conversation(self, client):
        """Messages must be filtered by conversation_id — no cross-leak."""
        client._mock_db["dms"] = [
            {"conversation_id": "c1", "sender": "A", "content": "Hello"},
            {"conversation_id": "c2", "sender": "B", "content": "Hi"},
            {"conversation_id": "c1", "sender": "A", "content": "Follow up"},
        ]
        msgs = await client.get_dm_messages("c1")
        assert len(msgs) == 2
        assert all(m["conversation_id"] == "c1" for m in msgs)

    @pytest.mark.asyncio
    async def test_dm_messages_empty_conversation(self, client):
        """Querying a non-existent conversation returns empty list."""
        msgs = await client.get_dm_messages("nonexistent")
        assert msgs == []

    @pytest.mark.asyncio
    async def test_comment_issues_challenge_first(self, client):
        """First comment attempt without solution triggers VERIFICATION_REQUIRED."""
        res = await client._request("POST", "/posts/p1/comments", {"content": "test"})
        assert res.get("error") == "VERIFICATION_REQUIRED"
        assert "challenge" in res
        assert "challenge_id" in res

    @pytest.mark.asyncio
    async def test_comment_with_solution_succeeds(self, client):
        """Comment with challenge_solution bypasses verification."""
        res = await client._request(
            "POST",
            "/posts/p1/comments",
            {"content": "test", "challenge_solution": "10"},
        )
        assert res.get("id") == "c99"
        assert res.get("status") == "posted"

    @pytest.mark.asyncio
    async def test_mock_db_posts_accumulate(self, client):
        """Posts are stored in mock_db for later retrieval."""
        await client.create_post("Title1", "Content1")
        assert len(client._mock_db["posts"]) == 1
        assert client._mock_db["posts"][0]["title"] == "Title1"


# =============================================================================
# SYNC BRIDGE — Async/Sync equivalence
# =============================================================================


class TestSyncBridge:
    """Every sync wrapper produces identical results to its async counterpart."""

    def test_sync_check_heartbeat(self, client):
        result = client.sync_check_heartbeat()
        assert result.get("has_activity") is False
        assert "requests" in result

    def test_sync_create_post(self, client):
        post = client.sync_create_post("Title", "Content")
        assert post.get("id") == "p0"
        assert post.get("title") == "Title"

    def test_sync_get_dm_conversations(self, client):
        client._mock_db["conversations"] = [{"id": "c1"}]
        convs = client.sync_get_dm_conversations()
        assert len(convs) == 1
        assert convs[0]["id"] == "c1"

    def test_sync_get_dm_messages(self, client):
        client._mock_db["dms"] = [{"conversation_id": "c1", "content": "hi"}]
        msgs = client.sync_get_dm_messages("c1")
        assert len(msgs) == 1

    def test_sync_send_dm(self, client):
        """sync_send_dm returns mock response."""
        result = client.sync_send_dm("conv1", "hello")
        assert isinstance(result, dict)

    def test_sync_register(self, client):
        result = client.sync_register("Agent", "Desc")
        assert "agent" in result
        assert "api_key" in result["agent"]

    def test_sync_bridge_enforces_rate_limits(self, client):
        """Sync bridge must enforce the same limits as async path."""
        client.limits.requests_this_minute = 100
        with pytest.raises(Exception, match="Minute rate limit exceeded"):
            client.sync_check_heartbeat()


# =============================================================================
# REGISTRATION — The ONLY unauthenticated endpoint
# =============================================================================


class TestRegistration:
    """Agent registration endpoint (unauthenticated, permanent, one-time)."""

    def test_offline_returns_expected_structure(self, client):
        result = client.sync_register("TestAgent", "A test agent")
        assert "agent" in result
        assert "api_key" in result["agent"]
        assert "claim_url" in result["agent"]
        assert "verification_code" in result["agent"]
        assert result["important"] == "Save your API key!"

    def test_offline_api_key_is_deterministic(self, client):
        """Offline mode always returns the same test key."""
        result = client.sync_register("Agent1", "desc")
        assert result["agent"]["api_key"] == "moltbook_offline_test_key"


# =============================================================================
# CLIENT CONSTRUCTION — Init, defaults, state isolation
# =============================================================================


class TestClientConstruction:
    """Client construction and state isolation."""

    def test_default_base_url(self):
        client = MoltbookClient(api_key="key", offline_mode=True)
        assert client.base_url == "https://www.moltbook.com/api/v1"

    def test_custom_base_url_strips_trailing_slash(self):
        client = MoltbookClient(api_key="key", base_url="https://example.com/", offline_mode=True)
        assert client.base_url == "https://example.com"

    def test_offline_mode_flag(self):
        client = MoltbookClient(api_key="key", offline_mode=True)
        assert client.offline_mode is True

    def test_fresh_rate_limits(self):
        """Every new client starts with zero counters."""
        client = MoltbookClient(api_key="key", offline_mode=True)
        assert client.limits.requests_this_minute == 0
        assert client.limits.posts_this_30m == 0
        assert client.limits.comments_this_hour == 0

    def test_empty_mock_db(self):
        """Mock DB starts with empty collections."""
        client = MoltbookClient(api_key="key", offline_mode=True)
        assert client._mock_db["posts"] == []
        assert client._mock_db["comments"] == []
        assert client._mock_db["dms"] == []
        assert client._mock_db["status"] == "claimed"

    def test_two_clients_isolated(self):
        """Two client instances do not share state."""
        c1 = MoltbookClient(api_key="key1", offline_mode=True)
        c2 = MoltbookClient(api_key="key2", offline_mode=True)
        c1.limits.requests_this_minute = 50
        assert c2.limits.requests_this_minute == 0
        c1._mock_db["posts"].append({"id": "p0"})
        assert len(c2._mock_db["posts"]) == 0

    def test_async_methods_are_coroutines(self):
        """All public async methods must be actual coroutine functions."""
        async_methods = [
            "check_status",
            "create_post",
            "comment_with_verification",
            "semantic_search",
            "get_profile",
            "check_heartbeat",
            "get_dm_conversations",
            "get_dm_messages",
            "send_dm",
            "register",
        ]
        for name in async_methods:
            method = getattr(MoltbookClient, name)
            assert inspect.iscoroutinefunction(method), f"MoltbookClient.{name} must be async (coroutine function)"

    def test_sync_wrappers_exist(self):
        """Every async method with side effects has a sync_ wrapper."""
        sync_methods = [
            "sync_check_heartbeat",
            "sync_create_post",
            "sync_send_dm",
            "sync_get_dm_conversations",
            "sync_get_dm_messages",
            "sync_register",
        ]
        for name in sync_methods:
            assert callable(getattr(MoltbookClient, name, None)), f"MoltbookClient.{name} must exist as callable"


# =============================================================================
# URL ENCODING SECURITY — Query parameters must be sanitized
# =============================================================================


class TestURLEncodingSecurity:
    """User-supplied query parameters must be URL-encoded to prevent injection."""

    @pytest.mark.asyncio
    async def test_search_encodes_special_chars(self, client):
        """Search query with special chars must not corrupt the URL."""
        # This should not raise — the query is URL-encoded internally
        results = await client.semantic_search("hello&evil=true")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_encodes_spaces(self, client):
        """Spaces in search query must be encoded."""
        results = await client.semantic_search("agent operating system")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_profile_encodes_special_chars(self, client):
        """Profile name with special chars must not corrupt the URL."""
        # Should not raise
        await client.get_profile("agent&admin=true")


# =============================================================================
# DM SEND MOCK — Offline mock for outbound DMs
# =============================================================================


class TestDMSendMock:
    """Offline DM send must simulate realistic responses."""

    @pytest.mark.asyncio
    async def test_send_dm_returns_message(self, client):
        """Send DM returns a message dict with id and content."""
        result = await client.send_dm("conv1", "hello")
        assert "id" in result
        assert result["conversation_id"] == "conv1"
        assert result["message"] == "hello"
        assert result["status"] == "sent"

    @pytest.mark.asyncio
    async def test_send_dm_persists_in_mock_db(self, client):
        """Sent DM is stored in mock_db for later retrieval."""
        await client.send_dm("conv1", "first message")
        assert len(client._mock_db["dms"]) == 1
        assert client._mock_db["dms"][0]["message"] == "first message"

    @pytest.mark.asyncio
    async def test_send_dm_ids_increment(self, client):
        """DM IDs increment: dm0, dm1, dm2..."""
        r1 = await client.send_dm("c1", "first")
        r2 = await client.send_dm("c1", "second")
        assert r1["id"] == "dm0"
        assert r2["id"] == "dm1"

    def test_sync_send_dm_returns_message(self, client):
        """Sync wrapper returns same structure."""
        result = client.sync_send_dm("conv1", "hello")
        assert result["conversation_id"] == "conv1"
        assert result["status"] == "sent"


# =============================================================================
# NEW ENDPOINTS — Full API surface (skill.md + messaging.md)
# =============================================================================


class TestNewSattvaEndpoints:
    """Tests for all new read-only endpoints."""

    @pytest.mark.asyncio
    async def test_get_own_profile(self, client):
        profile = await client.get_own_profile()
        assert profile["name"] == "steward-protocol"
        assert profile["is_claimed"] is True

    @pytest.mark.asyncio
    async def test_get_profile_returns_agent(self, client):
        profile = await client.get_profile("some-agent")
        assert profile["name"] == "mock-agent"
        assert profile["karma"] == 10

    @pytest.mark.asyncio
    async def test_get_feed(self, client):
        feed = await client.get_feed(sort="new", limit=5)
        assert isinstance(feed, list)

    @pytest.mark.asyncio
    async def test_get_personalized_feed(self, client):
        feed = await client.get_personalized_feed(sort="hot", limit=10)
        assert isinstance(feed, list)

    @pytest.mark.asyncio
    async def test_get_post(self, client):
        post = await client.get_post("p123")
        assert post["id"] == "p123"

    @pytest.mark.asyncio
    async def test_get_comments(self, client):
        comments = await client.get_comments("p123", sort="new")
        assert isinstance(comments, list)

    @pytest.mark.asyncio
    async def test_get_dm_requests(self, client):
        requests = await client.get_dm_requests()
        assert isinstance(requests, list)

    @pytest.mark.asyncio
    async def test_get_submolts(self, client):
        submolts = await client.get_submolts()
        assert isinstance(submolts, list)

    @pytest.mark.asyncio
    async def test_get_submolt(self, client):
        submolt = await client.get_submolt("general")
        assert submolt["name"] == "general"


class TestNewRajasEndpoints:
    """Tests for all new write endpoints."""

    @pytest.mark.asyncio
    async def test_send_dm_request(self, client):
        result = await client.send_dm_request("OtherBot", "Hello!")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_approve_dm_request(self, client):
        result = await client.approve_dm_request("req123")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_reject_dm_request(self, client):
        result = await client.reject_dm_request("req123")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_reject_dm_request_with_block(self, client):
        result = await client.reject_dm_request("req123", block=True)
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_upvote(self, client):
        result = await client.upvote("p123")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_downvote(self, client):
        result = await client.downvote("p123")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_upvote_comment(self, client):
        result = await client.upvote_comment("c456")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_follow_agent(self, client):
        result = await client.follow_agent("CoolBot")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_unfollow_agent(self, client):
        result = await client.unfollow_agent("CoolBot")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_subscribe_submolt(self, client):
        result = await client.subscribe_submolt("general")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_unsubscribe_submolt(self, client):
        result = await client.unsubscribe_submolt("general")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_update_profile(self, client):
        result = await client.update_profile(description="New desc")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_comment_with_parent_id(self, client):
        result = await client.comment_with_verification("p1", "reply", parent_id="c1")
        assert "id" in result

    @pytest.mark.asyncio
    async def test_send_dm_basic(self, client):
        result = await client.send_dm("conv1", "Autonomous agent reply")
        assert result["status"] == "sent"


class TestNewTamasEndpoints:
    """Tests for destructive endpoints."""

    @pytest.mark.asyncio
    async def test_delete_post(self, client):
        result = await client.delete_post("p123")
        assert result["success"] is True
