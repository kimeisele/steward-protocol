"""
VERIFY MEMORY (THE LIVING SOUL)
===============================

Tests that the Reactor:
1. Routing: Maps "remember" -> Kapila (Pos 6).
2. Persistence: Remembers data across "sleep" (new offer calls).
3. Recall: Retrieves data correctly.
"""

import sys
import time
from vibe_core.mahamantra.substrate.bridge import offer


def verify():
    print("CORE: Testing Living Memory...")

    # 1. Remember a Secret
    # Note: bridge.offer takes `content`. Kapila checks `payload`.
    # wrap_cell converts content to payload.
    # If content is dict, it becomes payload JSON.

    secret_payload = {"op": "REMEMBER", "key": "mahamantra_secret", "value": "om_namo_bhagavate_vasudevaya"}

    print(f"\n[1] Remembering Secret: {secret_payload['key']}...")
    res1 = offer(secret_payload, purpose="remember")

    if not res1["success"]:
        print(f"FAIL [1]: {res1['error']}")
        sys.exit(1)

    print(f"Result 1: {res1['execution_result']}")
    if res1["error"]:
        print(f"Dissonance 1: {res1['error']}")

    if "Remembered" not in str(res1["execution_result"]):
        print(f"FAIL [1]: Did not confirm memory. Got: {res1['execution_result']}")
        sys.exit(1)

    # 2. Recall the Secret
    print("\n[2] Recalling Secret...")
    recall_payload = {"op": "RECALL", "key": "mahamantra_secret"}
    res2 = offer(recall_payload, purpose="recall")

    if not res2["success"]:
        print(f"FAIL [2]: {res2['error']}")
        sys.exit(1)

    result_val = res2["execution_result"]
    print(f"Result 2: {result_val}")

    if result_val != "om_namo_bhagavate_vasudevaya":
        print(f"FAIL [2]: Core Amnesia! Expected 'om_namo_bhagavate_vasudevaya', got '{result_val}'")
        sys.exit(1)

    print("\nSUCCESS: The Soul Remembers.")


if __name__ == "__main__":
    verify()
