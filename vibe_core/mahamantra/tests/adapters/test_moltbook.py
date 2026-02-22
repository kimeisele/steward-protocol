"""
MOLTBOOK ADAPTER TESTS - Watertight Offline Verification
========================================================

"yogasthah kuru karmani sangam tyaktva dhananjaya"
"Be steadfast in yoga, O Arjuna. Perform your duty and abandon all attachment to success or failure."

Testing the deterministic constraints of the Moltbook adapter.
We test RATE LIMITS and MATH CHALLENGES entirely offline.
"""

import asyncio
import pytest
import time
from vibe_core.mahamantra.adapters.moltbook import MoltbookClient, ChallengeSolver, MoltbookLimits

# =============================================================================
# 1. CHALLENGE SOLVER TESTS
# =============================================================================

def test_challenge_solver_addition():
    """Verify basic addition parsing"""
    assert ChallengeSolver.solve("What is seven + 3?") == "10"
    assert ChallengeSolver.solve("Please add 5 and four") == "9"
    assert ChallengeSolver.solve("8 plus two equals") == "10"

def test_challenge_solver_subtraction():
    """Verify basic subtraction parsing"""
    assert ChallengeSolver.solve("What is ten - 3?") == "7"
    assert ChallengeSolver.solve("nine minus four is") == "5"

def test_challenge_solver_multiplication():
    """Verify basic multiplication parsing"""
    assert ChallengeSolver.solve("What is two * 3?") == "6"
    assert ChallengeSolver.solve("four times five") == "20"

def test_challenge_solver_edge_cases():
    """Verify failure modes don't crash"""
    assert ChallengeSolver.solve("What is the meaning of life?") == "0" # No numbers
    assert ChallengeSolver.solve("Just the number 5") == "0" # Only one number, no operator
    
# =============================================================================
# 2. RATE LIMITER TESTS (The Watertight Seal)
# =============================================================================

@pytest.mark.asyncio
async def test_minute_rate_limit():
    """Verify we hit the wall at 100 requests per minute"""
    client = MoltbookClient(api_key="offline_key", offline_mode=True)
    
    # Fast forward: 99 requests
    client.limits.requests_this_minute = 99
    
    # 100th request should pass
    await client.check_status()
    assert client.limits.requests_this_minute == 100
    
    # 101st request should THROW
    with pytest.raises(Exception, match="Minute rate limit exceeded"):
        await client.check_status()

@pytest.mark.asyncio
async def test_post_rate_limit():
    """Verify we cannot post more than once per 30 minutes"""
    client = MoltbookClient(api_key="offline_key", offline_mode=True)
    
    # First post works
    post = await client.create_post("Title", "Content")
    assert post.get("id") == "p0"
    assert client.limits.posts_this_30m == 1
    
    # Second post within 30m MUST THROW
    with pytest.raises(Exception, match="Post rate limit \\(1/30m\\) exceeded"):
        await client.create_post("Spam", "Spam")

@pytest.mark.asyncio
async def test_comment_daily_limit():
    """Verify we stop commenting after 50 per day"""
    client = MoltbookClient(api_key="offline_key", offline_mode=True)
    
    # Fast forward to 49 comments today
    client.limits.comments_today = 49
    
    # 50th comment works
    # Note: Using underlying _request directly to test limit, avoiding verification flow
    await client._request("POST", "/posts/p1/comments", {"content": "Hello"})
    assert client.limits.comments_today == 50
    
    # 51st comment MUST THROW
    with pytest.raises(Exception, match="Daily comment limit exceeded"):
        await client._request("POST", "/posts/p1/comments", {"content": "Spam"})

# =============================================================================
# 3. VERIFICATION FLOW TEST
# =============================================================================

@pytest.mark.asyncio
async def test_comment_verification_flow():
    """
    Verify the adapter catches VERIFICATION_REQUIRED, solves it, 
    and resubmits automatically.
    """
    client = MoltbookClient(api_key="offline_key", offline_mode=True)
    
    # The offline mock is wired to throw a "seven + 3" challenge
    # Our adapter should catch it, solve it (10), and succeed.
    res = await client.comment_with_verification("post_123", "Brilliant architecture!")
    
    # Mock hub returns "c99" on successful verification
    assert res.get("id") == "c99", "Failed to auto-solve verification challenge"
    
