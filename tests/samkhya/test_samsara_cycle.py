"""
TEST SAMSARA CYCLE - The Proof of Life

"Prove that we need new python code."

OBJECTIVE:
Demonstrate that a static list of entities (Mayavad) fails to maintain Sovereignty.
Demonstrate that a "Samsara Stream" (Generator + Context Injection) maintains "The Eternal Now".

SCENARIO:
We have a civilization of 100 Entities.
We need to verify their Identity (SovereignContext).

METHOD:
1. Mayavad Approach: List[Entity]. Iterate. Context is lost or stale.
2. Samsara Approach: proper Generator yielding (Entity, Context). Context is fresh (NOW).
"""

import time
from dataclasses import dataclass
from typing import Iterator, List, Tuple

import pytest

from vibe_core.protocols.universal.types import SovereignContext

# --- MOCK ENTITIES ---


@dataclass
class Entity:
    id: int
    name: str


# --- 1. THE MAYAVAD APPROACH (Static) ---


def get_static_civilization(size: int) -> List[Entity]:
    return [Entity(i, f"Ancestor_{i}") for i in range(size)]


def process_mayavad(civilization: List[Entity], context: SovereignContext):
    """
    The Mayavad Flaw:
    The context passed here is static. It represents the 'Start Time'.
    By the time we reach ancestor 99, the context is stale.
    The 'Now' is checking a 'Past' signature.
    """
    valid_count = 0
    start_time = context.timestamp

    for entity in civilization:
        # Simulate processing time
        time.sleep(0.001)

        # Check: Is the context timestamp close to NOW?
        # In a strict system (Satya Yuga), signatures expire in milliseconds.
        current_time = time.time()
        if current_time - context.timestamp > 0.05:  # Strict TTL
            # FAIL: Context expired. This entity is processing in the Past.
            continue

        valid_count += 1

    return valid_count


# --- 2. THE SAMSARA APPROACH (Dynamic Stream) ---


class SamsaraStream:
    """
    The Living Stream.
    Injects FRESH Context into every iteration.
    """

    def __init__(self, size: int):
        self.size = size

    def stream(self) -> Iterator[Tuple[Entity, SovereignContext]]:
        for i in range(self.size):
            entity = Entity(i, f"Ancestor_{i}")

            # THE ETERNAL NOW: Create fresh context for this moment
            now_context = SovereignContext(
                identity_id="SELF",
                signature=f"sig_{time.time()}",  # Fresh signature
                timestamp=time.time(),  # FRESH TIMESTAMP
                intent_id=f"will_{i}",
            )

            yield entity, now_context

            # Simulate processing time
            time.sleep(0.001)


def process_samsara(stream: SamsaraStream):
    valid_count = 0

    for entity, context in stream.stream():
        # Check: Is the context timestamp close to NOW?
        current_time = time.time()

        # Since context is fresh, delta should be near 0
        if current_time - context.timestamp <= 0.05:
            valid_count += 1

    return valid_count


# --- TESTS ---


def test_mayavad_failure():
    """Prove that static context leads to expiration (Death)."""
    # Create valid context AT START
    ctx = SovereignContext(identity_id="ROOT", signature="sig_start", timestamp=time.time())

    # Process 100 entities. sleeping 1ms each = 100ms total.
    # TTL is 50ms.
    # Expectation: Only the first ~50 will be valid. The rest fail.
    civ = get_static_civilization(100)
    survivors = process_mayavad(civ, ctx)

    print(f"Mayavad Survivors: {survivors}/100")

    # PROOF: We lost souls because the Context (Time) didn't move with them.
    assert survivors < 100


def test_samsara_success():
    """Prove that Samsara (Stream) keeps everyone alive."""
    stream = SamsaraStream(100)
    survivors = process_samsara(stream)

    print(f"Samsara Survivors: {survivors}/100")

    # PROOF: Everyone survives because Context is regenerated in the NOW.
    assert survivors == 100
