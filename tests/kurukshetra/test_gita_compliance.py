"""
TEST GITA COMPLIANCE - The Red Suite

"Prove that the system is not yet Divine."

OBJECTIVE:
Verify if the Core Components implement the `GitaProtocol`.
Since they do not, this test MUST FAIL (Red).

TARGETS:
1. NagaBase (The Services)
2. RealVibeKernel (The Controller)
"""

import pytest

from vibe_core.protocols.naga.base import NagaBase
from vibe_core.protocols.universal.gita import GitaProtocol

# Assuming RealVibeKernel is importable or mockable for interface check
# from vibe_core.kernel_impl import RealVibeKernel


class MockService(NagaBase):
    """A standard Naga (Snake) Service."""

    def serve(self, req):
        pass


def test_naga_is_divine():
    """
    Test if a Standard Naga observes the Gita Protocol.
    EXPECTED: FAIL (It currently only observes NagaBase).
    """
    snake = MockService("Takshaka", ("bite",))

    # IS IT DIVINE?
    assert isinstance(snake, GitaProtocol), "Naga does not follow the Gita!"


def test_kernel_is_divine():
    """
    Test if the Kernel observes the Gita Protocol.
    EXPECTED: FAIL (It currently observes KernelProtocol).
    """
    # We can't easily instantiate Kernel here due to deps, but we can check the class
    # or a mock that represents current reality.

    class CurrentKernel:
        """Represents current Kernel implementation."""

        pass

    kernel = CurrentKernel()
    assert isinstance(kernel, GitaProtocol), "Kernel does not follow the Gita!"
