"""
VAJRA ARMOR: Immutable DNA Protection Mixin.

"The Diamond Thunderbolt that nothing can shatter."

This module provides the VajraGuarded mixin - a clean way to make
critical attributes immutable after initialization.

Architecture:
    1. Inherit from VajraGuarded
    2. Call protect_attribute("name") for critical fields
    3. Call vajra_seal() at end of __init__
    4. Any attempt to modify sealed attributes raises PermissionError

Usage:
    class MyKernel(VajraGuarded):
        def __init__(self):
            VajraGuarded.__init__(self)

            self._critical_factory = lambda: SomeClass()
            self.protect_attribute("_critical_factory")

            # ... rest of init ...

            self.vajra_seal()  # Lock it down

    # After seal():
    kernel._critical_factory = malicious_factory  # Raises PermissionError!

GAD-000 ACTIVE SECURITY (Vajra Intent):
    Instead of passive hash verification, the system uses Active Intent Authorization.
    Changes to the Kernel/Castle must be proposed as a SecurityIntent/Request.
    The HIL (Sovereign) then "Clicks Accept" (Requests Execution).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "nrisimha"
__position__ = 12
__genesis__ = "0x51a6b9d4"  # GenesisByte: parampara % 37 == 0

import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

logger = logging.getLogger("VAJRA")


class VajraGuarded:
    """
    Mixin that seals objects against attribute modification.

    Once vajra_seal() is called, protected attributes become immutable.
    Any attempt to modify them raises PermissionError.

    This is the kernel's "DNA protection" - blueprints and factories
    cannot be poisoned after initialization.
    """

    def __init__(self):
        """Initialize Vajra protection (unsealed by default)."""
        # These must be set via object.__setattr__ to avoid recursion
        object.__setattr__(self, "_vajra_sealed", False)
        object.__setattr__(self, "_vajra_protected", set())

    def protect_attribute(self, name: str) -> None:
        """
        Mark an attribute as part of the DNA (immutable after seal).

        Args:
            name: Attribute name to protect (e.g., "_ledger_blueprint")
        """
        self._vajra_protected.add(name)

    def vajra_seal(self) -> None:
        """
        Activate the Vajra seal.

        After this call, any attempt to modify protected attributes
        will raise PermissionError("VAJRA VIOLATION").
        """
        object.__setattr__(self, "_vajra_sealed", True)
        logger.info(f"💎 VAJRA SEAL: {self.__class__.__name__} DNA locked. Protected: {self._vajra_protected}")

    def vajra_unseal(self) -> None:
        """
        Temporarily unseal for legitimate modifications.

        WARNING: Use sparingly! This should only be used for
        controlled kernel upgrades or testing.
        """
        object.__setattr__(self, "_vajra_sealed", False)
        logger.warning(f"⚠️ VAJRA UNSEAL: {self.__class__.__name__} DNA unlocked!")

    def is_vajra_sealed(self) -> bool:
        """Check if the object is currently sealed."""
        return getattr(self, "_vajra_sealed", False)

    def get_protected_attributes(self) -> Set[str]:
        """Get the set of protected attribute names."""
        return getattr(self, "_vajra_protected", set()).copy()

    def __setattr__(self, name: str, value) -> None:
        """
        Intercept attribute setting to enforce Vajra protection.

        Raises:
            PermissionError: If attempting to modify a sealed, protected attribute.
        """
        # 1. Always allow setting Vajra control attributes
        if name in ("_vajra_sealed", "_vajra_protected"):
            object.__setattr__(self, name, value)
            return

        # 2. Check if seal is active
        if getattr(self, "_vajra_sealed", False):
            # 3. Check if attribute is protected
            protected = getattr(self, "_vajra_protected", set())
            if name in protected:
                logger.error(f"🚫 VAJRA VIOLATION: Attempt to poison '{name}' on {self.__class__.__name__}!")
                raise PermissionError(
                    f"VAJRA VIOLATION: Attempt to rewrite immutable DNA '{name}' "
                    f"on {self.__class__.__name__}. The blueprint is sealed."
                )

        # 4. Allowed - proceed with normal setattr
        object.__setattr__(self, name, value)


class VajraViolation(PermissionError):
    """
    Exception raised when attempting to modify sealed DNA.
    """

    pass


# =============================================================================
# GAD-000 ACTIVE SECURITY: Intent Authorization
# =============================================================================


class IntentStatus(str, Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    REJECTED = "rejected"
    EXECUTED = "executed"


@dataclass
class SecurityIntent:
    """
    A proposed security change (Castle Repair).
    Instead of editing hashes manually, we propose an Intent.
    """

    id: str  # UUID
    author: str  # "System" or Sovereign ID
    description: str
    changes: Dict[str, str]  # {file_path: new_sha256}
    status: IntentStatus = IntentStatus.PENDING
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    signature: Optional[str] = None

    def sign(self, key: str) -> None:
        """Sign the intent (Placeholder for full crypto)."""
        content = f"{self.id}{self.author}{json.dumps(self.changes, sort_keys=True)}"
        self.signature = hashlib.sha256((content + key).encode()).hexdigest()
        self.status = IntentStatus.AUTHORIZED

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "SecurityIntent":
        data = json.loads(json_str)
        # Convert status string back to Enum
        data["status"] = IntentStatus(data["status"])
        return cls(**data)


class SecurityIntentManager:
    """
    Manages the lifecycle of Security Intents.
    """

    INTENT_DIR = Path(".vibe/security_intents")
    HASH_FILE = Path("scripts/governance/kernel_hashes.json")

    def __init__(self):
        self.INTENT_DIR.mkdir(parents=True, exist_ok=True)

    def propose_intent(self, author: str, description: str, changes: Dict[str, str]) -> SecurityIntent:
        """Create and save a new pending intent."""
        import uuid

        intent = SecurityIntent(id=str(uuid.uuid4()), author=author, description=description, changes=changes)
        self._save_intent(intent)
        logger.info(f"🛡️ VAJRA: Proposed Security Intent {intent.id}: {description}")
        return intent

    def get_intent(self, intent_id: str) -> Optional[SecurityIntent]:
        path = self.INTENT_DIR / f"{intent_id}.json"
        if not path.exists():
            return None
        return SecurityIntent.from_json(path.read_text())

    def authorize_intent(self, intent_id: str, key: str) -> bool:
        """Authorize a pending intent."""
        intent = self.get_intent(intent_id)
        if not intent:
            return False

        intent.sign(key)
        self._save_intent(intent)
        logger.info(f"🛡️ VAJRA: Authorized Intent {intent.id}")
        return True

    def execute_intent(self, intent_id: str) -> bool:
        """
        Execute an authorized intent by updating the kernel hashes.
        """
        intent = self.get_intent(intent_id)
        if not intent:
            logger.error(f"Intent {intent_id} not found")
            return False

        if intent.status != IntentStatus.AUTHORIZED:
            logger.error(f"Intent {intent_id} is not AUTHORIZED (status: {intent.status})")
            return False

        # Update Hash File
        try:
            current_hashes = {}
            if self.HASH_FILE.exists():
                current_hashes = json.loads(self.HASH_FILE.read_text())

            # Apply changes
            for file_path, new_hash in intent.changes.items():
                current_hashes[file_path] = new_hash
                logger.info(f"🛡️ VAJRA: Updated hash for {file_path}")

            # Save Hash File
            self.HASH_FILE.write_text(json.dumps(current_hashes, indent=2))

            # Mark Executed
            intent.status = IntentStatus.EXECUTED
            self._save_intent(intent)
            return True
        except Exception as e:
            logger.error(f"Failed to execute intent: {e}")
            return False

    def _save_intent(self, intent: SecurityIntent) -> None:
        path = self.INTENT_DIR / f"{intent.id}.json"
        path.write_text(intent.to_json())
