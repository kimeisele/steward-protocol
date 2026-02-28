"""Moltbook Guna Enforcer — I/O Policy + Knowledge Graph validation."""

import logging
import time
from typing import List, Protocol

from vibe_core.protocols.moltbook import MOLTBOOK_GUNA_MAP, MoltbookGuna

logger = logging.getLogger("MOLTBOOK.GUNA")


class GunaEnforcerCallbacks(Protocol):
    """Callbacks that MoltbookPlugin provides to GunaEnforcer."""

    _operation_log: List[dict]  # List of {operation, guna, timestamp}


class GunaEnforcer:
    """Enforce Guna I/O Policy and Knowledge Graph constraints.

    Responsibilities:
    - Map operation to Guna (SATTVA=read, RAJAS=write, TAMAS=delete)
    - Block TAMAS operations (destructive without explicit auth)
    - Check Knowledge Graph platform constraints
    - Log RAJAS (write) operations with timestamp
    - Trim operation log when exceeding 5000 entries (keep last 2500)

    Guna Meanings:
    - SATTVA: Pass through (read-only, safe)
    - RAJAS: Log and allow (write, rate-limited by client)
    - TAMAS: Block (destructive, not implemented)

    YANTRA Discipline:
    - Explicit constraint checking from Knowledge Graph
    - Clear error on TAMAS (fail loudly, don't fallback)
    - Operation logging for audit trail
    - No exceptions on constraint violations (warnings only)
    """

    _MAX_LOG_SIZE = 5000
    _TRIM_TO_SIZE = 2500

    def __init__(self, actions: GunaEnforcerCallbacks) -> None:
        self._actions = actions

    def enforce(self, operation: str) -> None:
        """Enforce Guna I/O Policy and Knowledge Graph constraints.

        Args:
            operation: Operation name to validate

        Raises:
            PermissionError: If operation is TAMAS (destructive)
        """
        # Map operation to Guna
        guna = MOLTBOOK_GUNA_MAP.get(operation, MoltbookGuna.SATTVA)

        # Block TAMAS operations (destructive without explicit authorization)
        if guna == MoltbookGuna.TAMAS:
            raise PermissionError(
                f"MOLTBOOK-TAMAS: Operation '{operation}' is destructive and requires "
                f"explicit authorization. Not implemented."
            )

        # Check Knowledge Graph constraints (knowledge/moltbook/platform.yaml)
        self._check_kg_constraints(operation, guna)

        # Log RAJAS (write) operations
        if guna == MoltbookGuna.RAJAS:
            self._log_write_operation(operation, guna)

    def _check_kg_constraints(self, operation: str, guna: MoltbookGuna) -> None:
        """Check Knowledge Graph platform constraints for operation.

        Args:
            operation: Operation name
            guna: Guna classification
        """
        try:
            from vibe_core.knowledge.resolver import get_resolver

            resolver = get_resolver()
            violations = resolver.get_violations(
                operation,
                {"guna": guna.value, "operation": operation},
            )
            for v in violations:
                logger.warning(f"MOLTBOOK-KG-CONSTRAINT: {v}")
        except Exception as e:
            logger.debug(f"KG constraint check unavailable: {e}")

    def _log_write_operation(self, operation: str, guna: MoltbookGuna) -> None:
        """Log write operation with timestamp and trim log if needed.

        Args:
            operation: Operation name
            guna: Guna classification (RAJAS)
        """
        entry = {
            "operation": operation,
            "guna": guna.value,
            "timestamp": time.time(),
        }
        self._actions._operation_log.append(entry)

        # Prevent unbounded growth: trim when log exceeds max size
        if len(self._actions._operation_log) > self._MAX_LOG_SIZE:
            self._actions._operation_log = self._actions._operation_log[-self._TRIM_TO_SIZE :]

        logger.info(f"MOLTBOOK-RAJAS: {operation} (write operation logged)")
