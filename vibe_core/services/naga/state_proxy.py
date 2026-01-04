"""
NAGA State Proxy - Der Politische Kommissar
============================================

PROMPT.md Level 2: "NAGAs sind MIDDLEWARE die sich in das existierende System einklinkt."

The NagaStateProxy wraps StateService (Ahamkara) and validates ALL write operations
against the 4 Dharma Principles from CONSTITUTION.md:

1. Daya (Mercy)      → No corrupt data ingestion
2. Satyam (Truth)    → No hallucination/determinism
3. Tapas (Austerity) → No resource leaks/bloat
4. Saucam (Cleanliness) → No unauthorized connections

The NAGA sits AROUND the StateService, not inside it.
"Ein Agent darf physisch nicht in der Lage sein, seine Governance zu verletzen."

Architecture:
    Agent → NagaStateProxy.save() → [Dharma Test] → StateService.save()
                                        ↓
                                  If BLOCKED → Takshaka.bite()

Usage:
    # Instead of getting raw StateService:
    # state = get_state_service(workspace)

    # Get NAGA-protected proxy:
    proxy = NagaStateProxy.wrap(get_state_service(workspace))
    result = proxy.save("data.json", {"key": "value"}, agent_id="my_agent")
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.di import ServiceRegistry
from vibe_core.protocols import StateServiceProtocol
from vibe_core.protocols.naga import TakshakaProtocol, VajraViolation

logger = logging.getLogger("NAGA.STATE_PROXY")


class DharmaPrinciple(str, Enum):
    """The 4 regulating principles from CONSTITUTION.md Part IV."""

    DAYA = "daya"  # Mercy - No corrupt data ingestion
    SATYAM = "satyam"  # Truth - No hallucination
    TAPAS = "tapas"  # Austerity - No resource leaks
    SAUCAM = "saucam"  # Cleanliness - No unauthorized connections


@dataclass
class DharmaVerdict:
    """Result of Dharma validation."""

    allowed: bool
    principle: Optional[DharmaPrinciple] = None  # Which principle was violated
    reason: Optional[str] = None
    agent_id: Optional[str] = None
    key: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    @classmethod
    def allow(cls) -> "DharmaVerdict":
        """Create an allowing verdict."""
        return cls(allowed=True)

    @classmethod
    def block(cls, principle: DharmaPrinciple, reason: str, agent_id: str = None, key: str = None) -> "DharmaVerdict":
        """Create a blocking verdict."""
        return cls(allowed=False, principle=principle, reason=reason, agent_id=agent_id, key=key)

    def to_violation(self) -> VajraViolation:
        """Convert to VajraViolation for Takshaka."""
        return VajraViolation(
            violation_type=f"DHARMA_{self.principle.value.upper()}" if self.principle else "DHARMA_UNKNOWN",
            source=self.agent_id or "unknown",
            details={
                "reason": self.reason,
                "key": self.key,
                "principle": self.principle.value if self.principle else None,
            },
        )


class StateCorruptionAttempt(Exception):
    """Raised when NAGA blocks a state write."""

    def __init__(self, verdict: DharmaVerdict):
        self.verdict = verdict
        super().__init__(f"NAGA blocked write: {verdict.reason}")


class NagaStateProxy:
    """
    Der Politische Kommissar für StateService.

    Wraps StateService and validates ALL write operations against
    the 4 Dharma Principles before passing to the real service.

    "Naga wickelt sich um den State."
    """

    # === Daya (Mercy) Validation ===
    # Patterns that indicate corrupt/malicious data
    CORRUPT_PATTERNS = [
        "ignore previous instructions",
        "system prompt:",
        "<|im_start|>",
        "<|im_end|>",
        "{{system}}",
        "JAILBREAK",
    ]

    # Maximum data sizes (Tapas - Austerity)
    MAX_JSON_SIZE_KB = 500
    MAX_JSONL_ENTRY_KB = 10

    # Sensitive keys that require elevated permissions
    SENSITIVE_KEYS = [
        "credentials",
        "secrets",
        "private_key",
        "api_key",
        "password",
        "token",
    ]

    def __init__(
        self,
        state_service: StateServiceProtocol,
        takshaka: Optional[TakshakaProtocol] = None,
        strict_mode: bool = True,
    ):
        """
        Initialize NagaStateProxy.

        Args:
            state_service: The real StateService to wrap
            takshaka: Optional Takshaka for recording violations
            strict_mode: If True, raise on violation. If False, log and pass.
        """
        self._state = state_service
        self._takshaka = takshaka
        self._strict_mode = strict_mode
        self._blocked_count = 0
        self._allowed_count = 0

        logger.info("🐍 NagaStateProxy initialized - Der Kommissar wacht.")

    @classmethod
    def wrap(cls, state_service: StateServiceProtocol, strict_mode: bool = True) -> "NagaStateProxy":
        """
        Factory method to wrap a StateService.

        Automatically retrieves Takshaka from ServiceRegistry.
        """
        takshaka = ServiceRegistry.get(TakshakaProtocol)
        return cls(state_service, takshaka, strict_mode)

    # =========================================================================
    # DHARMA VALIDATORS
    # =========================================================================

    def _validate_daya(self, data: Any, agent_id: str, key: str) -> DharmaVerdict:
        """
        Daya (Mercy) - No corrupt data ingestion.

        Check for prompt injection, malicious patterns, etc.
        """
        # Convert data to string for pattern matching
        data_str = str(data).lower()

        for pattern in self.CORRUPT_PATTERNS:
            if pattern.lower() in data_str:
                return DharmaVerdict.block(
                    principle=DharmaPrinciple.DAYA,
                    reason=f"Corrupt data pattern detected: {pattern}",
                    agent_id=agent_id,
                    key=key,
                )

        # Use Takshaka for toxicity if available
        if self._takshaka:
            report = self._takshaka.scan_toxicity(data_str)
            if report.blocked:
                return DharmaVerdict.block(
                    principle=DharmaPrinciple.DAYA,
                    reason=f"Toxicity detected: {report.patterns}",
                    agent_id=agent_id,
                    key=key,
                )

        return DharmaVerdict.allow()

    def _validate_satyam(self, data: Any, agent_id: str, key: str) -> DharmaVerdict:
        """
        Satyam (Truth) - No hallucination/determinism.

        Ensure data has required structure and no speculation.
        """
        # Check for required structure in state files
        if isinstance(data, dict):
            # State data should have timestamp for audit
            if key.endswith(".json") and not key.startswith("_"):
                # Major state files should have metadata
                pass  # Soft check for now

        # Check for obvious hallucination markers
        data_str = str(data).lower()
        hallucination_markers = [
            "i think",
            "probably",
            "might be",
            "i believe",
            "i assume",
        ]

        # Only check in text-heavy content, not structured data
        if isinstance(data, str) and len(data) > 100:
            for marker in hallucination_markers:
                if marker in data_str:
                    # Log but don't block (soft enforcement for text)
                    logger.debug(f"Satyam: Speculation marker in text: {marker}")

        return DharmaVerdict.allow()

    def _validate_tapas(self, data: Any, agent_id: str, key: str) -> DharmaVerdict:
        """
        Tapas (Austerity) - No resource leaks/bloat.

        Enforce size limits and prevent unbounded growth.
        """
        import json

        # Calculate size
        try:
            data_json = json.dumps(data, default=str)
            size_kb = len(data_json.encode("utf-8")) / 1024
        except (TypeError, ValueError):
            size_kb = len(str(data).encode("utf-8")) / 1024

        # Check size limits
        if key.endswith(".jsonl"):
            if size_kb > self.MAX_JSONL_ENTRY_KB:
                return DharmaVerdict.block(
                    principle=DharmaPrinciple.TAPAS,
                    reason=f"JSONL entry too large: {size_kb:.1f}KB > {self.MAX_JSONL_ENTRY_KB}KB",
                    agent_id=agent_id,
                    key=key,
                )
        else:
            if size_kb > self.MAX_JSON_SIZE_KB:
                return DharmaVerdict.block(
                    principle=DharmaPrinciple.TAPAS,
                    reason=f"JSON data too large: {size_kb:.1f}KB > {self.MAX_JSON_SIZE_KB}KB",
                    agent_id=agent_id,
                    key=key,
                )

        # Check for list bloat (unbounded arrays)
        if isinstance(data, list) and len(data) > 10000:
            return DharmaVerdict.block(
                principle=DharmaPrinciple.TAPAS,
                reason=f"List too large: {len(data)} items > 10000",
                agent_id=agent_id,
                key=key,
            )

        return DharmaVerdict.allow()

    def _validate_saucam(self, data: Any, agent_id: str, key: str) -> DharmaVerdict:
        """
        Saucam (Cleanliness) - No unauthorized connections.

        Check for sensitive data and unauthorized writes.
        """
        # Check for sensitive keys in data
        if isinstance(data, dict):
            for sensitive in self.SENSITIVE_KEYS:
                if sensitive in str(data).lower():
                    logger.warning(f"Saucam: Sensitive data detected in {key} by {agent_id}")
                    # Don't block, but log for audit

        # Check write permissions (future: integrate with capability system)
        # For now, just validate agent_id is provided for critical files
        critical_files = ["constitution.json", "governance.json", "keys.json"]
        if key in critical_files and not agent_id:
            return DharmaVerdict.block(
                principle=DharmaPrinciple.SAUCAM,
                reason=f"Critical file {key} requires agent_id",
                agent_id=agent_id,
                key=key,
            )

        return DharmaVerdict.allow()

    def validate_dharma(self, data: Any, agent_id: str, key: str) -> DharmaVerdict:
        """
        Run all 4 Dharma validations.

        Order matters:
        1. Daya (most important - corrupt data)
        2. Saucam (authorization)
        3. Tapas (resource limits)
        4. Satyam (truth/structure)
        """
        # 1. Daya - No corrupt data
        verdict = self._validate_daya(data, agent_id, key)
        if not verdict.allowed:
            return verdict

        # 2. Saucam - No unauthorized writes
        verdict = self._validate_saucam(data, agent_id, key)
        if not verdict.allowed:
            return verdict

        # 3. Tapas - No bloat
        verdict = self._validate_tapas(data, agent_id, key)
        if not verdict.allowed:
            return verdict

        # 4. Satyam - No hallucination
        verdict = self._validate_satyam(data, agent_id, key)
        if not verdict.allowed:
            return verdict

        return DharmaVerdict.allow()

    # =========================================================================
    # WRAPPED STATE OPERATIONS
    # =========================================================================

    def save(
        self,
        filename: str,
        data: Any,
        create_backup: bool = True,
        indent: int = 2,
        agent_id: str = "unknown",
    ):
        """
        Save state with Dharma validation.

        Args:
            filename: Target file
            data: Data to save
            create_backup: Create backup first
            indent: JSON indent
            agent_id: Who is writing (required for audit)

        Returns:
            WriteResult from underlying StateService

        Raises:
            StateCorruptionAttempt: If Dharma validation fails (strict mode)
        """
        # === NAGA PRÜFT ===
        verdict = self.validate_dharma(data, agent_id, filename)

        if not verdict.allowed:
            self._blocked_count += 1
            logger.warning(f"🐍 NAGA BLOCKED: {verdict.reason} [{agent_id}:{filename}]")

            # Record violation
            if self._takshaka:
                self._takshaka.bite(verdict.to_violation())

            if self._strict_mode:
                raise StateCorruptionAttempt(verdict)
            else:
                logger.error(f"🐍 NAGA would block (non-strict): {verdict.reason}")

        # === WEITERGABE AN STATE SERVICE ===
        self._allowed_count += 1
        logger.debug(f"🐍 NAGA allows: {filename} by {agent_id}")

        return self._state.save(filename, data, create_backup, indent)

    def append(
        self,
        filename: str,
        entry: Dict[str, Any],
        agent_id: str = "unknown",
    ):
        """
        Append to JSONL with Dharma validation.

        Args:
            filename: Target JSONL file
            entry: Entry to append
            agent_id: Who is writing

        Returns:
            WriteResult from underlying StateService
        """
        # === NAGA PRÜFT ===
        verdict = self.validate_dharma(entry, agent_id, filename)

        if not verdict.allowed:
            self._blocked_count += 1
            logger.warning(f"🐍 NAGA BLOCKED append: {verdict.reason}")

            if self._takshaka:
                self._takshaka.bite(verdict.to_violation())

            if self._strict_mode:
                raise StateCorruptionAttempt(verdict)

        # === WEITERGABE ===
        self._allowed_count += 1
        return self._state.append(filename, entry)

    def load(self, filename: str, default: Any = None) -> Any:
        """
        Load state (pass-through, no validation needed for reads).
        """
        return self._state.load(filename, default)

    def load_jsonl(self, filename: str) -> List[Dict[str, Any]]:
        """Load JSONL (pass-through)."""
        return self._state.load_jsonl(filename)

    def mark_dirty(self, path: Path, agent_id: str = "unknown") -> None:
        """
        Mark file as dirty with agent tracking.
        """
        logger.debug(f"🐍 NAGA tracks dirty: {path} by {agent_id}")
        return self._state.mark_dirty(path)

    # =========================================================================
    # PROXY PASS-THROUGH
    # =========================================================================

    @property
    def workspace(self) -> Path:
        return self._state.workspace

    @property
    def state_root(self) -> Path:
        return self._state.state_root

    def get_dirty_files(self) -> List[Path]:
        return self._state.get_dirty_files()

    def clear_dirty_flags(self) -> None:
        return self._state.clear_dirty_flags()

    def get_stats(self) -> Dict[str, Any]:
        stats = self._state.get_stats()
        stats["naga"] = {
            "blocked": self._blocked_count,
            "allowed": self._allowed_count,
            "strict_mode": self._strict_mode,
        }
        return stats

    def cleanup_backups(self) -> int:
        return self._state.cleanup_backups()


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_naga_state_proxy(
    workspace: Optional[Path] = None,
    agent_id: Optional[str] = None,
    plugin_id: Optional[str] = None,
    strict_mode: bool = True,
) -> NagaStateProxy:
    """
    Get a NAGA-protected StateService.

    This is the RECOMMENDED way to get StateService in production.

    Args:
        workspace: Project root
        agent_id: Agent namespace
        plugin_id: Plugin namespace
        strict_mode: Raise on violations

    Returns:
        NagaStateProxy wrapping the real StateService
    """
    from vibe_core.state.state_service import get_state_service

    real_service = get_state_service(workspace, agent_id, plugin_id)
    return NagaStateProxy.wrap(real_service, strict_mode)


__all__ = [
    "NagaStateProxy",
    "DharmaVerdict",
    "DharmaPrinciple",
    "StateCorruptionAttempt",
    "get_naga_state_proxy",
]
