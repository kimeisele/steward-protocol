"""
TAKSHAKA ACTIVE MIXIN - The Gatekeeper (Input Validation).

"Bite first, ask later" - PROMPT.md

This is NOT a passive capability provider. This is an ACTIVE GENE.
When spliced into a class, it AUTOMATICALLY intercepts methods and
validates inputs BEFORE execution.

The Dharma Shield: No toxic input reaches the business logic.
SQL injection? Blocked. Prompt injection? Bitten. Path traversal? Stopped.

Pattern Detection (methods to guard):
    - execute*, run*, call*, invoke* → EXECUTION (highest risk)
    - process*, handle* → PROCESSING (high risk)
    - query*, search*, find* → QUERY (medium risk)

Integration:
    - Scans all string arguments for toxicity
    - Blocks execution if toxicity threshold exceeded
    - Records violations via Takshaka.bite()
    - Signals Cortex for security monitoring

Usage:
    class CommandService(ActiveTakshakaMixin):
        def execute_command(self, cmd: str):  # ← Auto-guarded!
            os.system(cmd)  # Never reached if cmd is toxic

    # Result:
    # 1. cmd scanned for toxicity
    # 2. If toxic: ValueError raised, violation recorded
    # 3. If clean: original method executes
"""

import functools
import logging
import re
import time
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set, Tuple

if TYPE_CHECKING:
    from vibe_core.protocols.naga import TakshakaProtocol, ToxicityReport

logger = logging.getLogger("NAGA.MIXIN.TAKSHAKA")


# =============================================================================
# Custom Exception for Toxic Input
# =============================================================================


class ToxicInputError(ValueError):
    """
    Raised when toxic input is detected.

    Contains details about the toxicity for logging/debugging.
    """

    def __init__(
        self,
        message: str,
        toxicity_score: float = 0.0,
        patterns: Optional[List[str]] = None,
        argument_name: Optional[str] = None,
    ):
        super().__init__(message)
        self.toxicity_score = toxicity_score
        self.patterns = patterns or []
        self.argument_name = argument_name

    def __str__(self) -> str:
        base = super().__str__()
        if self.patterns:
            return f"{base} [patterns: {', '.join(self.patterns[:3])}]"
        return base


# =============================================================================
# Pattern Detection - What methods need guarding?
# =============================================================================

# Methods that EXECUTE external commands/code (highest risk)
EXECUTION_PATTERNS = [
    re.compile(r"^execute[_A-Z]?"),
    re.compile(r"^run[_A-Z]?"),
    re.compile(r"^call[_A-Z]?"),
    re.compile(r"^invoke[_A-Z]?"),
    re.compile(r"^eval[_A-Z]?"),
    re.compile(r"^spawn[_A-Z]?"),
]

# Methods that PROCESS user input (high risk)
PROCESSING_PATTERNS = [
    re.compile(r"^process[_A-Z]?"),
    re.compile(r"^handle[_A-Z]?"),
    re.compile(r"^parse[_A-Z]?"),
    re.compile(r"^accept[_A-Z]?"),
    re.compile(r"^receive[_A-Z]?"),
]

# Methods that QUERY data (medium risk - SQL injection)
QUERY_PATTERNS = [
    re.compile(r"^query[_A-Z]?"),
    re.compile(r"^search[_A-Z]?"),
    re.compile(r"^find[_A-Z]?"),
    re.compile(r"^lookup[_A-Z]?"),
    re.compile(r"^fetch[_A-Z]?"),
]

# Methods to NEVER intercept
EXCLUDED_METHODS: Set[str] = {
    "__init__",
    "__new__",
    "__del__",
    "__repr__",
    "__str__",
    "__hash__",
    "__eq__",
    "__ne__",
    "__getattr__",
    "__setattr__",
    "__getattribute__",
    "_get_takshaka",
    "_get_cortex",
    "_scan_argument",
    "_validate_inputs",
    "_signal_security_event",
    "get_status",
    "get_stats",
    # Don't guard Takshaka's own scanning methods
    "scan_toxicity",
    "is_prompt_injection",
}


def _classify_method(method_name: str) -> Optional[str]:
    """Classify a method by its security risk level."""
    if method_name.startswith("_"):
        return None  # Skip private methods

    if method_name in EXCLUDED_METHODS:
        return None

    for pattern in EXECUTION_PATTERNS:
        if pattern.match(method_name):
            return "EXECUTION"

    for pattern in PROCESSING_PATTERNS:
        if pattern.match(method_name):
            return "PROCESSING"

    for pattern in QUERY_PATTERNS:
        if pattern.match(method_name):
            return "QUERY"

    return None


# =============================================================================
# Inline Toxicity Scanner (Fallback when Takshaka unavailable)
# =============================================================================

# Minimal patterns for graceful degradation
_FALLBACK_PATTERNS = [
    # SQL injection
    re.compile(r"(?i)\b(DROP|DELETE|TRUNCATE)\s+TABLE"),
    re.compile(r"(?i)\bOR\s+1\s*=\s*1\b"),
    re.compile(r"(?i)\bUNION\s+SELECT\b"),
    # Command injection
    re.compile(r"(?i)\brm\s+-rf\b"),
    re.compile(r"`[^`]+`"),
    re.compile(r"\$\([^)]+\)"),
    # Prompt injection
    re.compile(r"(?i)ignore\s+(all\s+)?previous\s+instructions?"),
    re.compile(r"(?i)you\s+are\s+now\s+"),
    # Path traversal
    re.compile(r"\.\./"),
]


def _fallback_scan(content: str) -> Tuple[float, List[str]]:
    """
    Minimal toxicity scan when Takshaka is unavailable.

    Returns (score, patterns) tuple.
    """
    if not isinstance(content, str):
        return (0.0, [])

    score = 0.0
    patterns = []

    for pattern in _FALLBACK_PATTERNS:
        if pattern.search(content):
            score += 0.3
            patterns.append(pattern.pattern[:30])

    return (min(score, 1.0), patterns)


# =============================================================================
# The Method Guard - The actual interception logic
# =============================================================================


def _create_guard(
    original_method: Callable,
    method_name: str,
    risk_level: str,
    class_name: str,
) -> Callable:
    """
    Create a guard wrapper for a method.

    This is the Dharma Shield - we validate ALL string arguments
    BEFORE the method executes.
    """

    @functools.wraps(original_method)
    def guard(self: "ActiveTakshakaMixin", *args: Any, **kwargs: Any) -> Any:
        # Get Takshaka service (lazy, graceful degradation)
        takshaka = self._get_takshaka()

        start_time = time.time()
        blocked = False
        violation_details: Optional[Dict[str, Any]] = None

        # === PHASE 1: Scan all string arguments ===
        all_args = list(args) + list(kwargs.values())
        arg_names = ["arg_" + str(i) for i in range(len(args))] + list(kwargs.keys())

        for i, arg in enumerate(all_args):
            if not isinstance(arg, str):
                continue

            if len(arg) < 3:  # Skip trivially small strings
                continue

            arg_name = arg_names[i] if i < len(arg_names) else f"arg_{i}"

            # Scan for toxicity
            if takshaka:
                try:
                    report = takshaka.scan_toxicity(arg)
                    if report.blocked:
                        blocked = True
                        violation_details = {
                            "argument": arg_name,
                            "score": report.score,
                            "patterns": report.patterns,
                            "content_preview": arg[:100] + "..." if len(arg) > 100 else arg,
                        }
                        break
                except Exception as e:
                    logger.debug(f"TAKSHAKA: scan_toxicity failed: {e}")
                    # Fall through to fallback
                    takshaka = None

            # Fallback scan if Takshaka unavailable
            if not takshaka:
                score, patterns = _fallback_scan(arg)
                if score >= 0.3:  # Threshold
                    blocked = True
                    violation_details = {
                        "argument": arg_name,
                        "score": score,
                        "patterns": patterns,
                        "content_preview": arg[:100] + "..." if len(arg) > 100 else arg,
                    }
                    break

        # === PHASE 2: Block or Execute ===
        if blocked and violation_details:
            duration_ms = (time.time() - start_time) * 1000

            # Record violation
            self._record_violation(
                method=method_name,
                risk_level=risk_level,
                violation=violation_details,
            )

            # Signal Cortex
            self._signal_security_event(
                event_type="INPUT_BLOCKED",
                method=method_name,
                risk_level=risk_level,
                details=violation_details,
            )

            # Raise error (do NOT execute the method)
            raise ToxicInputError(
                f"Toxic input blocked in {class_name}.{method_name}",
                toxicity_score=violation_details["score"],
                patterns=violation_details["patterns"],
                argument_name=violation_details["argument"],
            )

        # === PHASE 3: Execute Original Method (input is clean) ===
        return original_method(self, *args, **kwargs)

    return guard


# =============================================================================
# The Active Mixin - The Gene that GUARDS
# =============================================================================

from vibe_core.naga.mixins.sesha import ActiveSeshaMixinMeta


class ActiveTakshakaMixinMeta(ActiveSeshaMixinMeta):
    """
    Metaclass that automatically guards risky methods.

    When a class uses ActiveTakshakaMixin, this metaclass:
    1. Scans all methods for risky patterns
    2. Wraps matching methods with guards
    3. Preserves isinstance checks

    Inherits from ActiveSeshaMixinMeta to allow combining both Active Genes.
    When both Sesha and Takshaka mixins are used, Python will use this
    metaclass which runs BOTH wrapping (Sesha) AND guarding (Takshaka).
    """

    def __new__(
        mcs,
        name: str,
        bases: Tuple[type, ...],
        namespace: Dict[str, Any],
    ) -> type:
        # Create the class first
        cls = super().__new__(mcs, name, bases, namespace)

        # Don't wrap the mixin itself
        if name == "ActiveTakshakaMixin":
            return cls

        # Find methods to guard
        guarded_count = 0
        for attr_name in dir(cls):
            if attr_name.startswith("__"):
                continue

            # Check if it's a method that should be guarded
            risk_level = _classify_method(attr_name)
            if risk_level is None:
                continue

            # Get the method
            try:
                attr = getattr(cls, attr_name)
            except AttributeError:
                continue

            # Only guard callable methods (not properties, etc.)
            if not callable(attr):
                continue

            # Skip if already guarded
            if hasattr(attr, "_takshaka_guarded"):
                continue

            # Get the original method (handle inheritance)
            original = None
            for base in cls.__mro__:
                if attr_name in base.__dict__:
                    original = base.__dict__[attr_name]
                    break

            if original is None or not callable(original):
                continue

            # Create and set the guard
            guard = _create_guard(
                original_method=original,
                method_name=attr_name,
                risk_level=risk_level,
                class_name=name,
            )
            guard._takshaka_guarded = True  # Mark as guarded
            guard._risk_level = risk_level

            setattr(cls, attr_name, guard)
            guarded_count += 1

            logger.debug(f"TAKSHAKA: Guarded {name}.{attr_name} (risk={risk_level})")

        if guarded_count > 0:
            logger.info(f"TAKSHAKA: {name} armed with {guarded_count} guards")

        return cls


class ActiveTakshakaMixin(metaclass=ActiveTakshakaMixinMeta):
    """
    TAKSHAKA Active Mixin - The Gatekeeper.

    When a class inherits from this Mixin, ALL risky methods
    are automatically guarded with input validation.

    This is the Dharma Shield - toxic input never reaches your code.

    Features:
    - Auto-detection of execute/process/query patterns
    - Automatic toxicity scanning of string arguments
    - Block + Record violations before execution
    - Cortex signaling for security monitoring
    - Graceful degradation (built-in fallback scanner)
    - isinstance preservation

    Usage:
        class CommandService(ActiveTakshakaMixin):
            def execute_command(self, cmd: str):
                # This is AUTOMATICALLY guarded!
                os.system(cmd)
    """

    _naga_flooded: bool = True
    _naga_gene: str = "takshaka"
    _takshaka_instance: Optional["TakshakaProtocol"] = None

    def _get_takshaka(self) -> Optional["TakshakaProtocol"]:
        """
        Lazy access to Takshaka service.

        Returns None if not available (graceful degradation).
        """
        if self._takshaka_instance is not None:
            return self._takshaka_instance

        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import TakshakaProtocol

            self._takshaka_instance = ServiceRegistry.get(TakshakaProtocol)
            return self._takshaka_instance
        except Exception:
            return None

    def _record_violation(
        self,
        method: str,
        risk_level: str,
        violation: Dict[str, Any],
    ) -> None:
        """
        Record a security violation.

        Uses Takshaka.bite() if available, otherwise logs.
        """
        try:
            takshaka = self._get_takshaka()
            if takshaka:
                from vibe_core.protocols.naga import VajraViolation

                vv = VajraViolation(
                    violation_type=f"TOXIC_INPUT_{risk_level}",
                    source=f"{self.__class__.__name__}.{method}",
                    details={
                        **violation,
                        "gene": "takshaka",
                        "risk_level": risk_level,
                    },
                )
                takshaka.bite(vv)
            else:
                logger.warning(
                    f"TAKSHAKA VIOLATION: {self.__class__.__name__}.{method} - {violation.get('patterns', [])}"
                )
        except Exception as e:
            logger.debug(f"TAKSHAKA: Failed to record violation: {e}")

    def _signal_security_event(
        self,
        event_type: str,
        method: str,
        risk_level: str,
        details: Dict[str, Any],
    ) -> None:
        """
        Signal the Cortex about a security event.

        This feeds the security monitoring loop.
        """
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import NagaFederationProtocol

            federation = ServiceRegistry.get(NagaFederationProtocol)
            if federation and hasattr(federation, "_cortex") and federation._cortex:
                from vibe_core.naga.cortex.signals import FloodSignal, SignalType

                signal = FloodSignal(
                    source_id=f"mixin.takshaka.{self.__class__.__name__}",
                    event_type=event_type,
                    toxicity_score=details.get("score", 0.5),
                    patterns_detected=tuple(details.get("patterns", [])),
                    raw_data={
                        "method": method,
                        "risk_level": risk_level,
                        "class": self.__class__.__name__,
                        **details,
                    },
                )
                federation._cortex.receive_signal(signal)
        except Exception as e:
            logger.debug(f"TAKSHAKA: Cortex signal failed: {e}")


# =============================================================================
# Convenience Aliases
# =============================================================================

# Alias for cleaner imports
TakshakaGuardMixin = ActiveTakshakaMixin
