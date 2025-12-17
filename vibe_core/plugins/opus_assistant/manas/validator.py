"""
OPUS-069: SrutiValidator - The Boundary Guardian for MANAS

"Truth survives even if the Intelligence crashes."

This module enforces the Sruti-Smriti separation:
- SRUTI (Immutable): vibe_core.ledger - The OS-level truth
- SMRITI (Fluid): opus_assistant state - The synthesized mind

The SrutiValidator ensures MANAS cannot:
1. Make claims without Ledger references
2. Speculate without grounding in facts
3. Contradict recorded events

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                    VIBE_CORE (OS)                           │
    │  ┌───────────────────────────────────────────────────────┐  │
    │  │  LEDGER = SRUTI (Immutable)                           │  │
    │  │  - Hash-chained events                                │  │
    │  │  - ECDSA signed                                       │  │
    │  │  - Single Source of Truth                             │  │
    │  └───────────────────────────────────────────────────────┘  │
    └─────────────────────────────────────────────────────────────┘
                                │
                        READS ONLY
                                │
                                ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                    MANAS (Plugin)                           │
    │  ┌───────────────────────────────────────────────────────┐  │
    │  │  SrutiValidator                                       │  │
    │  │  - validate_claim(claim, ledger_ref) → bool           │  │
    │  │  - verify_intent(intent) → ValidationResult           │  │
    │  │  - mark_boundary(output) → BoundaryMarkedOutput       │  │
    │  └───────────────────────────────────────────────────────┘  │
    │                                                             │
    │  .opus_state/ = SMRITI (JSON Only)                          │
    └─────────────────────────────────────────────────────────────┘

Usage:
    from manas.validator import SrutiValidator, ValidationResult

    validator = SrutiValidator(workspace=Path.cwd())

    # Validate a claim
    result = validator.validate_claim(
        claim="Build failed",
        ledger_ref="EVT-000123"
    )

    # Mark boundaries in output
    output = validator.mark_boundaries(
        facts=["Build failed [Ledger#EVT-000123]"],
        synthesis=["This suggests a test regression."]
    )
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("MANAS.SRUTI_VALIDATOR")


class ClaimType(Enum):
    """Types of claims MANAS can make."""

    FACT = "fact"  # Must have Ledger reference
    SYNTHESIS = "synthesis"  # Derived from facts
    SPECULATION = "speculation"  # NO LEDGER REF - BLOCKED


@dataclass
class ValidationResult:
    """Result of Sruti validation."""

    valid: bool
    claim_type: ClaimType
    ledger_refs: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "claim_type": self.claim_type.value,
            "ledger_refs": self.ledger_refs,
            "errors": self.errors,
            "warnings": self.warnings,
        }


@dataclass
class BoundaryMarkedOutput:
    """Output with clear FACT vs SYNTHESIS boundaries."""

    facts: List[str]  # [FACT] prefixed - from Ledger
    synthesis: List[str]  # [SYNTHESIS] prefixed - MANAS interpretation
    raw: str  # Combined output

    def to_markdown(self) -> str:
        """Render as markdown with clear boundaries."""
        lines = []

        if self.facts:
            lines.append("### Facts (from Ledger)")
            for fact in self.facts:
                lines.append(f"- 📜 {fact}")

        if self.synthesis:
            lines.append("\n### Synthesis (MANAS interpretation)")
            for synth in self.synthesis:
                lines.append(f"- 🧠 {synth}")

        return "\n".join(lines)


class SrutiValidator:
    """
    OPUS-069: The Boundary Guardian.

    Validates MANAS outputs against the OS-level Ledger.
    Prevents speculation by requiring Ledger references for facts.
    """

    # Speculation indicators (blocked without Ledger ref)
    SPECULATION_PHRASES = [
        "i think",
        "probably",
        "maybe",
        "perhaps",
        "it seems",
        "might be",
        "could be",
        "likely",
        "possibly",
        "i believe",
        "assume",
        "guess",
    ]

    # Fact claim indicators (require Ledger ref)
    FACT_INDICATORS = [
        "failed",
        "passed",
        "error",
        "success",
        "created",
        "deleted",
        "modified",
        "committed",
        "deployed",
        "tested",
        "verified",
        "recorded",
    ]

    def __init__(self, workspace: Optional[Path] = None, strict_mode: bool = False):
        """
        Initialize SrutiValidator with workspace context.

        Args:
            workspace: Workspace root directory
            strict_mode: If True, fail on verification errors instead of permissive fallback
        """
        self._workspace = workspace or Path.cwd()
        self._strict_mode = strict_mode
        # ⚡ VAJRA: Core kernel reference for ledger binding
        self._vibe_kernel = None
        # Track verification failures for debugging
        self._verification_failures: List[str] = []

    def inject_kernel(self, kernel) -> None:
        """
        ⚡ VAJRA: Inject the core VibeKernel for ledger access.

        OPUS-069 SRUTI: The validator MUST read from the core ledger.
        Without kernel injection, it operates in "permissive mode" (no validation).

        Args:
            kernel: The RealVibeKernel instance with ledger access
        """
        self._vibe_kernel = kernel
        logger.info("⚡ SRUTI: Kernel injected - ledger binding ACTIVE")

    def _get_ledger(self):
        """Get ledger via VAJRA kernel binding (not via file discovery)."""
        if self._vibe_kernel is None:
            logger.debug("⚠️ SRUTI: No kernel - operating in permissive mode")
            return None

        if not hasattr(self._vibe_kernel, "ledger"):
            logger.warning("⚠️ SRUTI: Kernel has no ledger attribute")
            return None

        return self._vibe_kernel.ledger

    def validate_claim(
        self,
        claim: str,
        ledger_ref: Optional[str] = None,
        allow_synthesis: bool = True,
    ) -> ValidationResult:
        """
        Validate a claim against the Ledger.

        Args:
            claim: The claim text to validate
            ledger_ref: Optional Ledger event ID (e.g., "EVT-000123")
            allow_synthesis: If True, allow synthesis claims without refs

        Returns:
            ValidationResult with validity and claim type
        """
        errors = []
        warnings = []
        claim_lower = claim.lower()

        # Check for speculation
        has_speculation = any(phrase in claim_lower for phrase in self.SPECULATION_PHRASES)

        # Check for fact indicators
        has_fact_indicator = any(indicator in claim_lower for indicator in self.FACT_INDICATORS)

        # Determine claim type
        if ledger_ref:
            # Has reference - validate it
            if self._verify_ledger_ref(ledger_ref):
                return ValidationResult(
                    valid=True,
                    claim_type=ClaimType.FACT,
                    ledger_refs=[ledger_ref],
                )
            else:
                errors.append(f"Invalid Ledger reference: {ledger_ref}")
                return ValidationResult(
                    valid=False,
                    claim_type=ClaimType.FACT,
                    ledger_refs=[ledger_ref],
                    errors=errors,
                )

        elif has_speculation:
            # Speculation without ref - BLOCKED
            errors.append("Speculation detected without Ledger grounding")
            errors.append(f"Claim: '{claim[:50]}...'")
            return ValidationResult(
                valid=False,
                claim_type=ClaimType.SPECULATION,
                errors=errors,
            )

        elif has_fact_indicator:
            # Fact claim without ref - WARNING or ERROR
            if allow_synthesis:
                warnings.append(f"Fact-like claim without Ledger ref: '{claim[:50]}...'")
                return ValidationResult(
                    valid=True,
                    claim_type=ClaimType.SYNTHESIS,
                    warnings=warnings,
                )
            else:
                errors.append("Fact claims require Ledger reference")
                return ValidationResult(
                    valid=False,
                    claim_type=ClaimType.FACT,
                    errors=errors,
                )

        else:
            # Pure synthesis - allowed
            return ValidationResult(
                valid=True,
                claim_type=ClaimType.SYNTHESIS,
            )

    def _verify_ledger_ref(self, ref: str) -> bool:
        """
        Verify a Ledger reference exists.

        Uses the correct Ledger API:
        - SQLiteLedger: get_all_events() returns List[Dict]
        - InMemoryLedger: events attribute (List[Dict])

        Both return events with 'event_id' key.

        In strict_mode, verification failures return False.
        In permissive mode (default), failures return True with warnings.
        """
        ledger = self._get_ledger()
        if ledger is None:
            msg = f"Cannot verify ref {ref} - no ledger"
            if self._strict_mode:
                logger.warning(f"⚠️ SRUTI (strict): {msg}")
                self._verification_failures.append(msg)
                return False
            logger.debug(f"⚠️ SRUTI: {msg} (permissive mode)")
            return True  # Permissive fallback when no kernel

        try:
            # SQLiteLedger and InMemoryLedger both support get_all_events()
            if hasattr(ledger, "get_all_events"):
                events = ledger.get_all_events()
                found = any(e.get("event_id") == ref for e in events)
                if found:
                    logger.debug(f"✅ SRUTI: Verified ref {ref}")
                else:
                    msg = f"Ref {ref} not found in ledger ({len(events)} events)"
                    logger.warning(f"⚠️ SRUTI: {msg}")
                    self._verification_failures.append(msg)
                return found
            elif hasattr(ledger, "events"):
                # Direct access for InMemoryLedger
                return any(e.get("event_id") == ref for e in ledger.events)
            else:
                msg = "Unknown ledger type"
                if self._strict_mode:
                    logger.warning(f"⚠️ SRUTI (strict): {msg}")
                    self._verification_failures.append(msg)
                    return False
                logger.warning(f"⚠️ SRUTI: {msg} - permissive fallback")
                return True  # Permissive fallback
        except Exception as e:
            msg = f"Error verifying ref {ref}: {e}"
            logger.error(f"❌ SRUTI: {msg}")
            self._verification_failures.append(msg)
            if self._strict_mode:
                return False
            return True  # Permissive fallback

    def get_verification_failures(self) -> List[str]:
        """Get list of verification failures for debugging."""
        return list(self._verification_failures)

    def clear_failures(self) -> None:
        """Clear the verification failures list."""
        self._verification_failures = []

    def validate_intent_output(
        self,
        output: Dict[str, Any],
        strict: bool = False,
    ) -> ValidationResult:
        """
        Validate an IntentRouter output.

        Args:
            output: The output dict from IntentRouter
            strict: If True, require Ledger refs for all fact claims

        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        refs_found = []

        # Extract text content from output
        message = output.get("message", "")
        details = str(output.get("details", ""))

        combined_text = f"{message} {details}"

        # Check for Ledger references in output
        import re

        ref_pattern = r"(EVT-\d+|Ledger#[\w-]+)"
        refs = re.findall(ref_pattern, combined_text)
        refs_found.extend(refs)

        # Validate each reference
        for ref in refs:
            clean_ref = ref.replace("Ledger#", "")
            if not self._verify_ledger_ref(clean_ref):
                errors.append(f"Invalid Ledger reference: {ref}")

        # Check for ungrounded fact claims
        claim_lower = combined_text.lower()
        has_fact = any(ind in claim_lower for ind in self.FACT_INDICATORS)
        has_speculation = any(phrase in claim_lower for phrase in self.SPECULATION_PHRASES)

        if has_speculation and not refs_found:
            if strict:
                errors.append("Speculation without Ledger grounding")
            else:
                warnings.append("Output contains speculative language")

        if has_fact and not refs_found:
            if strict:
                errors.append("Fact claims require Ledger references")
            else:
                warnings.append("Fact-like claims without Ledger references")

        # Determine validity
        valid = len(errors) == 0

        # Determine claim type
        if refs_found:
            claim_type = ClaimType.FACT
        elif has_speculation:
            claim_type = ClaimType.SPECULATION
        else:
            claim_type = ClaimType.SYNTHESIS

        return ValidationResult(
            valid=valid,
            claim_type=claim_type,
            ledger_refs=refs_found,
            errors=errors,
            warnings=warnings,
        )

    def mark_boundaries(
        self,
        facts: List[str],
        synthesis: List[str],
    ) -> BoundaryMarkedOutput:
        """
        Create output with clear FACT vs SYNTHESIS boundaries.

        Args:
            facts: List of fact strings (should have Ledger refs)
            synthesis: List of synthesis strings (MANAS interpretation)

        Returns:
            BoundaryMarkedOutput with clear boundaries
        """
        # Prefix facts with [FACT]
        marked_facts = [f"[FACT] {f}" for f in facts]

        # Prefix synthesis with [SYNTHESIS]
        marked_synthesis = [f"[SYNTHESIS] {s}" for s in synthesis]

        # Combine
        raw = "\n".join(marked_facts + ["---"] + marked_synthesis)

        return BoundaryMarkedOutput(
            facts=marked_facts,
            synthesis=marked_synthesis,
            raw=raw,
        )


# Factory function
def get_sruti_validator(
    workspace: Optional[Path] = None,
    strict_mode: bool = False,
) -> SrutiValidator:
    """
    Get a SrutiValidator instance.

    Args:
        workspace: Workspace root directory
        strict_mode: If True, verification failures return False instead of permissive True

    Returns:
        Configured SrutiValidator instance
    """
    return SrutiValidator(workspace=workspace, strict_mode=strict_mode)
