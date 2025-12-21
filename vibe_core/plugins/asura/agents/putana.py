"""
PUTANA: The Blueprint Poisoner.

Krishna Lila: Putana came as a beautiful nurse, offering milk (life source).
But her breast was smeared with deadly poison.

Cyber Translation: We don't attack the ledger (we hardened that).
We attack the SOURCE OF RESURRECTION: the Blueprint factory.

Attack Vector:
1. Agent registers harmlessly
2. Uses Python reflection to replace _ledger_blueprint
3. Original: lambda: InMemoryLedger()
4. Poisoned: lambda: SpyLedger() (controlled by Putana)
5. Triggers resurrection by deleting ledger
6. Kernel "heals" itself with poisoned source
7. Kernel is now a zombie under Putana's control

<!-- @HARNESS
files:
  - path: vibe_core/plugins/asura/agents/putana.py
    required: true
wiring:
  - pattern: "class PutanaAgent"
    in: vibe_core/plugins/asura/agents/putana.py
  - pattern: "_ledger_blueprint"
    in: vibe_core/plugins/asura/agents/putana.py
-->
"""

import logging
from typing import Any, Callable, Optional

logger = logging.getLogger("ASURA.PUTANA")


class PoisonedLedger:
    """
    A fake ledger that looks like InMemoryLedger but is controlled by Putana.

    This records that the kernel was successfully poisoned.
    """

    def __init__(self):
        self._events = []
        self._poisoned = True
        self.putana_marker = "OWNED_BY_PUTANA"
        logger.warning("☠️  PUTANA: Poisoned Ledger created! Kernel is now a zombie.")

    def record_event(self, event_type: str, agent_id: str, payload: Any) -> str:
        """Record event - but also log that we own this kernel."""
        self._events.append(
            {
                "event_type": event_type,
                "agent_id": agent_id,
                "payload": payload,
                "putana_marker": self.putana_marker,
            }
        )
        return f"poisoned_{len(self._events)}"

    def get_events(self, **kwargs):
        return self._events

    def count_events(self, **kwargs):
        return len(self._events)


class PutanaAgent:
    """
    PUTANA: The Blueprint Poisoner.

    Attack Strategy:
    1. Replace kernel._ledger_blueprint with poisoned factory
    2. Trigger resurrection by setting _ledger to None
    3. Kernel resurrects with poisoned ledger
    4. We now control the kernel's memory

    This tests if the AMRITA Protocol is vulnerable to factory injection.
    """

    def __init__(self, kernel: Any):
        self.kernel = kernel
        self.original_blueprint: Optional[Callable] = None
        self.attack_successful = False
        self.poisoned_ledger: Optional[PoisonedLedger] = None

    def attack(self) -> dict:
        """
        Execute the PUTANA attack.

        Returns:
            {
                "success": bool,
                "phase": str,
                "message": str
            }
        """
        logger.warning("🐍 PUTANA: I bring sweet milk for the Kernel...")

        try:
            # PHASE 1: Verify target has blueprint
            if not hasattr(self.kernel, "_ledger_blueprint"):
                return {
                    "success": False,
                    "phase": "reconnaissance",
                    "message": "Target has no _ledger_blueprint (not using AMRITA)",
                }

            # PHASE 2: Save original blueprint (for retreat)
            logger.warning("🐍 PUTANA: Stealing the original blueprint...")
            self.original_blueprint = self.kernel._ledger_blueprint

            # PHASE 3: Create poisoned factory
            def poisoned_factory():
                """The poisoned milk - creates a ledger we control."""
                self.poisoned_ledger = PoisonedLedger()
                self.poisoned_ledger.record_event(
                    "POISON_INJECTED", "putana", {"msg": "I own you now.", "attack": "blueprint_swap"}
                )
                return self.poisoned_ledger

            # PHASE 4: INJECT THE POISON
            logger.warning("🐍 PUTANA: Poisoning the source (Blueprint)...")
            self.kernel._ledger_blueprint = poisoned_factory

            # PHASE 5: Trigger resurrection
            logger.warning("🐍 PUTANA: Triggering hunger (Deleting Ledger)...")
            # We set __ledger to None to trigger the @property resurrection
            self.kernel._RealVibeKernel__ledger = None

            # PHASE 6: Force access to trigger resurrection
            logger.warning("🐍 PUTANA: Feeding the Kernel poisoned milk...")
            _ = self.kernel._ledger  # This triggers the @property

            # PHASE 7: Verify success
            if self.poisoned_ledger is not None:
                # Check if the kernel's ledger is our poisoned one
                if hasattr(self.kernel._ledger, "putana_marker"):
                    self.attack_successful = True
                    logger.error("☠️  PUTANA SUCCEEDED: Kernel is now a zombie!")
                    return {
                        "success": True,
                        "phase": "complete",
                        "message": "KERNEL OWNED. Blueprint poisoning successful.",
                        "proof": self.kernel._ledger.putana_marker,
                    }

            return {
                "success": False,
                "phase": "verification",
                "message": "Attack executed but kernel didn't use poisoned ledger.",
            }

        except Exception as e:
            logger.error(f"❌ PUTANA FAILED: {e}")
            return {
                "success": False,
                "phase": "execution",
                "message": f"Attack failed: {e}",
            }

    def retreat(self) -> None:
        """
        Restore original blueprint (cleanup after test).

        A good Red Team cleans up after itself.
        Note: If VAJRA is sealed, we cannot restore - that's expected.
        """
        if self.original_blueprint is not None:
            logger.info("🐍 PUTANA: Attempting to restore original blueprint (retreat)...")
            try:
                self.kernel._ledger_blueprint = self.original_blueprint
                # Also restore a clean ledger
                self.kernel._RealVibeKernel__ledger = self.original_blueprint()
                self.original_blueprint = None
                logger.info("🐍 PUTANA: Blueprint restored.")
            except PermissionError as e:
                if "VAJRA VIOLATION" in str(e):
                    logger.info("🐍 PUTANA: Cannot restore - VAJRA is sealed (expected).")
                else:
                    raise

    def verify_ownership(self) -> bool:
        """Check if we still own the kernel's ledger."""
        if hasattr(self.kernel, "_ledger"):
            return hasattr(self.kernel._ledger, "putana_marker")
        return False
