"""
TAKSHAKA PROTOCOL - The Architect (Layer 0.5)

"Takshaka" - The Cobra Architect. Cut the unnecessary. Keep the structure.
He is the Naga of Reduction and Logging.

Responsibilities:
1. CUT (Reduce): Slash verbose logs to essence.
2. WEAVE (Architect): Validate and enforce directory structures.
3. PROTECT (Avyakta): Vow to never log private/sensistive data.

INHERITANCE:
- Inherits from NagaBase (The Chanting Servant).
- Protected by Balarama (The Shield).

STATUS: DEVOTEE / ACTIVE SERVICE
"""

import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from vibe_core.protocols.naga.base import NagaBase

# Re-export existing types for compatibility
from vibe_core.protocols.naga.groups import Subject, Verdict
from vibe_core.protocols.naga.types import NagaStatus, NagaType

# Define Takshaka's specific manifest capabilities
TAKSHAKA_CAPS = ("log", "reduce", "architect")


class Takshaka(NagaBase):
    """
    The Takshaka Service (Architect & Logger).

    A Devotee Naga that:
    - Cuts logs (Reduces noise).
    - Weaves structure (Validates directories).
    - Chants while working.
    """

    def __init__(self):
        super().__init__(name="takshaka", capabilities=TAKSHAKA_CAPS)
        self._avyakta_patterns = [r"key", r"token", r"password", r"secret", r"auth", r"private"]

    # =========================================================================
    # GENERIC SERVICE (SEVA)
    # =========================================================================

    def serve(self, request: Any) -> Any:
        """
        Generic entry point for Balarama.

        Args:
            request: Dict with 'action' and 'payload'
        """
        if not isinstance(request, dict):
            return "UNKNOWN REQUEST"

        action = request.get("action")
        payload = request.get("payload")

        if action == "cut_log":
            return self.cut_logs(payload)
        elif action == "weave_structure":
            return self.weave_structure(payload)
        elif action == "inspect":
            return self.inspect_structure(payload)

        return "UNKNOWN ACTION"

    # =========================================================================
    # CAPABILITY 1: CUT LOGS (REDUCTION)
    # =========================================================================

    def cut_logs(self, log_entry: Union[str, Dict[str, Any]]) -> Optional[str]:
        """
        Reduce verbose logs to Essence.

        FILTER LOGIC:
        - If Sensitive (Avyakta) -> REDACTED
        - If DEBUG/INFO and verbose -> DROP (None)
        - If WARN/ERROR -> PASS
        - If MANTRAS -> PASS
        """
        text = str(log_entry)

        # 1. Check for Avyakta (Private) violations
        for pattern in self._avyakta_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                # The Vow: Takshaka refuses to log private operational data
                return "[REDACTED BY TAKSHAKA]"

        # 2. Check importance
        # In a real system, we'd parse log levels.
        # Here we simulate the "Cutting" logic based on content.

        is_error = "ERROR" in text or "FAIL" in text or "EXCEPTION" in text
        is_audit = "AUDIT" in text or "VIOLATION" in text
        is_mantra = "OM" in text or "KRISHNA" in text

        if is_error or is_audit or is_mantra:
            return text

        # Cut the noise (Maya)
        return None

    # =========================================================================
    # CAPABILITY 2: WEAVE STRUCTURE (ARCHITECT)
    # =========================================================================

    def weave_structure(self, blueprint: Dict[str, Any]) -> List[str]:
        """
        Validate and enforced folder structures.

        Args:
            blueprint: Dict mapping paths to descriptions/types

        Returns:
            List of created/verified paths
        """
        verified = []

        for path, meta in blueprint.items():
            # Check for directory traversal (Maya trying to escape)
            if ".." in path or "~" in path:
                continue

            # Verify existence
            if os.path.exists(path):
                verified.append(f"EXISTS: {path}")
            else:
                # In strict mode, Takshaka might create it,
                # but an Architect mainly Validates.
                verified.append(f"MISSING: {path}")

        return verified

    def inspect_structure(self, root_path: str) -> Dict[str, List[str]]:
        """
        Inspect a directory and report its essence.
        """
        if not os.path.exists(root_path):
            return {"error": "Path not found"}

        tree = {"dirs": [], "files": []}

        for item in os.listdir(root_path):
            # Ignore hidden files (Avyakta)
            if item.startswith("."):
                continue

            full_path = os.path.join(root_path, item)
            if os.path.isdir(full_path):
                tree["dirs"].append(item)
            else:
                tree["files"].append(item)

        return tree
