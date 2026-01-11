"""
VALIDATION - Input Validation Protocol
======================================

OWNER: KUMARAS (The Four Pure Ones)
POSITION: 5 (DHARMA Quarter)
OPCODE: RESOLVE_REQ

The Kumaras are eternally pure - nothing impure can enter their presence.
This is input validation: only pure data passes through.

SHASTRA BASIS:
    The Four Kumaras - Sanaka, Sanandana, Sanatana, Sanat-kumara.
    Eternally five years old. Eternally pure.
    When Jaya and Vijaya blocked them at Vaikuntha,
    they cursed them for allowing impurity at the gate.

    In code:
    - Validator = Gatekeeper (like Jaya/Vijaya should have been)
    - Invalid data = Impurity (cannot enter)
    - Validation rules = Purity standards

VALIDATION TYPES:
    - TYPE: Check data type
    - RANGE: Check value range
    - PATTERN: Check against regex
    - SCHEMA: Check against schema
    - CUSTOM: Custom validation function

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, Final, List, Optional, Pattern, Protocol, Union, runtime_checkable

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode

from vibe_core.protocols.mahajanas.kumaras import (
    PurifiableData,
    PurityLevel,
    PurificationResult,
    PurityState,
)


# =============================================================================
# OWNERSHIP DECLARATION
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.KUMARAS
LOTUS_POSITION: Final[int] = 5
LOTUS_QUARTER: Final[str] = "dharma"

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.RESOLVE_REQ,
]


# =============================================================================
# VALIDATION TYPES
# =============================================================================

class ValidationType(str, Enum):
    """Types of validation."""
    TYPE = "type"           # Type checking
    RANGE = "range"         # Value range
    PATTERN = "pattern"     # Regex pattern
    LENGTH = "length"       # String/list length
    REQUIRED = "required"   # Non-null check
    CUSTOM = "custom"       # Custom function


# =============================================================================
# VALIDATION RULE
# =============================================================================

ValidatorFunc = Callable[[PurifiableData], bool]


@dataclass
class ValidationRule:
    """A single validation rule."""
    name: str
    validation_type: ValidationType
    error_message: str
    # Type validation
    expected_type: Optional[str] = None
    # Range validation
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    # Pattern validation
    pattern: Optional[str] = None
    # Length validation
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    # Custom validation
    validator: Optional[ValidatorFunc] = None

    def validate(self, data: PurifiableData) -> bool:
        """Validate data against this rule."""
        if self.validation_type == ValidationType.REQUIRED:
            return data is not None

        if data is None:
            return True  # Non-required fields can be None

        if self.validation_type == ValidationType.TYPE:
            return type(data).__name__ == self.expected_type

        if self.validation_type == ValidationType.RANGE:
            if not isinstance(data, (int, float)):
                return False
            if self.min_value is not None and data < self.min_value:
                return False
            if self.max_value is not None and data > self.max_value:
                return False
            return True

        if self.validation_type == ValidationType.PATTERN:
            if not isinstance(data, str) or self.pattern is None:
                return False
            return bool(re.match(self.pattern, data))

        if self.validation_type == ValidationType.LENGTH:
            if not isinstance(data, (str, list, dict, bytes)):
                return False
            length = len(data)
            if self.min_length is not None and length < self.min_length:
                return False
            if self.max_length is not None and length > self.max_length:
                return False
            return True

        if self.validation_type == ValidationType.CUSTOM:
            if self.validator is None:
                return True
            return self.validator(data)

        return True


@dataclass(frozen=True)
class ValidationResult:
    """Result of validation."""
    valid: bool
    field: str
    value_type: str
    errors: List[str]
    purity_level: PurityLevel


# =============================================================================
# VALIDATION PROTOCOL
# =============================================================================

@runtime_checkable
class ValidationProtocol(Protocol):
    """
    The Input Validation Protocol - Kumaras' Gate.

    OWNER: Mahajana.KUMARAS

    Like the Kumaras who reject impurity,
    this protocol rejects invalid data.
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.KUMARAS."""
        ...

    # Rule Management
    def add_rule(self, field: str, rule: ValidationRule) -> bool:
        """Add a validation rule for a field."""
        ...

    def remove_rule(self, field: str, rule_name: str) -> bool:
        """Remove a validation rule."""
        ...

    def get_rules(self, field: str) -> List[ValidationRule]:
        """Get rules for a field."""
        ...

    # Validation
    def validate(self, field: str, data: PurifiableData) -> ValidationResult:
        """Validate a single field."""
        ...

    def validate_all(self, data: Dict[str, PurifiableData]) -> Dict[str, ValidationResult]:
        """Validate multiple fields."""
        ...

    def is_valid(self, field: str, data: PurifiableData) -> bool:
        """Quick check if data is valid."""
        ...


# =============================================================================
# VALIDATOR IMPLEMENTATION
# =============================================================================

class Validator:
    """
    Kumaras' Validator - Input Gate.

    OWNER: Mahajana.KUMARAS

    Features:
    - Multiple validation types
    - Rule-based validation
    - Purity level assessment
    """

    def __init__(self) -> None:
        """Initialize validator."""
        self._rules: Dict[str, List[ValidationRule]] = {}
        self._validation_count = 0
        self._rejection_count = 0

    @property
    def owner(self) -> Mahajana:
        return Mahajana.KUMARAS

    def add_rule(self, field: str, rule: ValidationRule) -> bool:
        """Add a validation rule for a field."""
        if field not in self._rules:
            self._rules[field] = []
        self._rules[field].append(rule)
        return True

    def remove_rule(self, field: str, rule_name: str) -> bool:
        """Remove a validation rule."""
        if field not in self._rules:
            return False
        for i, rule in enumerate(self._rules[field]):
            if rule.name == rule_name:
                self._rules[field].pop(i)
                return True
        return False

    def get_rules(self, field: str) -> List[ValidationRule]:
        """Get rules for a field."""
        return self._rules.get(field, [])

    def validate(self, field: str, data: PurifiableData) -> ValidationResult:
        """Validate a single field."""
        self._validation_count += 1
        errors: List[str] = []

        rules = self._rules.get(field, [])
        for rule in rules:
            if not rule.validate(data):
                errors.append(rule.error_message)

        if errors:
            self._rejection_count += 1

        # Determine purity level based on errors
        if not errors:
            purity = PurityLevel.PRISTINE
        elif len(errors) == 1:
            purity = PurityLevel.TAINTED
        else:
            purity = PurityLevel.CORRUPTED

        return ValidationResult(
            valid=len(errors) == 0,
            field=field,
            value_type=type(data).__name__ if data is not None else "NoneType",
            errors=errors,
            purity_level=purity,
        )

    def validate_all(self, data: Dict[str, PurifiableData]) -> Dict[str, ValidationResult]:
        """Validate multiple fields."""
        results: Dict[str, ValidationResult] = {}
        for field, value in data.items():
            results[field] = self.validate(field, value)
        return results

    def is_valid(self, field: str, data: PurifiableData) -> bool:
        """Quick check if data is valid."""
        return self.validate(field, data).valid

    def get_state(self) -> PurityState:
        """Get validation state."""
        rejection_rate = self._rejection_count / max(1, self._validation_count)
        if rejection_rate < 0.1:
            purity = PurityLevel.PRISTINE
        elif rejection_rate < 0.3:
            purity = PurityLevel.CLEAN
        elif rejection_rate < 0.5:
            purity = PurityLevel.TAINTED
        else:
            purity = PurityLevel.CORRUPTED

        return PurityState(
            is_pure=rejection_rate < 0.1,
            purity_level=purity.value,
            total_purifications=self._validation_count,
            total_resets=0,
            last_purification=datetime.now().isoformat(),
            health="healthy" if rejection_rate < 0.3 else "degraded",
        )


# =============================================================================
# COMMON RULES (Factory Functions)
# =============================================================================

def required(field_name: str) -> ValidationRule:
    """Create a required field rule."""
    return ValidationRule(
        name=f"{field_name}_required",
        validation_type=ValidationType.REQUIRED,
        error_message=f"{field_name} is required",
    )


def type_check(field_name: str, expected: str) -> ValidationRule:
    """Create a type check rule."""
    return ValidationRule(
        name=f"{field_name}_type",
        validation_type=ValidationType.TYPE,
        expected_type=expected,
        error_message=f"{field_name} must be {expected}",
    )


def range_check(field_name: str, min_val: Optional[float] = None, max_val: Optional[float] = None) -> ValidationRule:
    """Create a range check rule."""
    return ValidationRule(
        name=f"{field_name}_range",
        validation_type=ValidationType.RANGE,
        min_value=min_val,
        max_value=max_val,
        error_message=f"{field_name} must be between {min_val} and {max_val}",
    )


def pattern_check(field_name: str, pattern: str, description: str = "pattern") -> ValidationRule:
    """Create a pattern check rule."""
    return ValidationRule(
        name=f"{field_name}_pattern",
        validation_type=ValidationType.PATTERN,
        pattern=pattern,
        error_message=f"{field_name} must match {description}",
    )


def length_check(field_name: str, min_len: Optional[int] = None, max_len: Optional[int] = None) -> ValidationRule:
    """Create a length check rule."""
    return ValidationRule(
        name=f"{field_name}_length",
        validation_type=ValidationType.LENGTH,
        min_length=min_len,
        max_length=max_len,
        error_message=f"{field_name} length must be between {min_len} and {max_len}",
    )


# =============================================================================
# NULL VALIDATOR
# =============================================================================

class NullValidator:
    """Null validator - everything is valid."""

    @property
    def owner(self) -> Mahajana:
        return Mahajana.KUMARAS

    def add_rule(self, field: str, rule: ValidationRule) -> bool:
        return True

    def remove_rule(self, field: str, rule_name: str) -> bool:
        return True

    def get_rules(self, field: str) -> List[ValidationRule]:
        return []

    def validate(self, field: str, data: PurifiableData) -> ValidationResult:
        return ValidationResult(valid=True, field=field, value_type=type(data).__name__, errors=[], purity_level=PurityLevel.PRISTINE)

    def validate_all(self, data: Dict[str, PurifiableData]) -> Dict[str, ValidationResult]:
        return {k: self.validate(k, v) for k, v in data.items()}

    def is_valid(self, field: str, data: PurifiableData) -> bool:
        return True


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "OWNER", "LOTUS_POSITION", "LOTUS_QUARTER", "OWNED_OPCODES",
    "ValidationType", "ValidationRule", "ValidationResult", "ValidatorFunc",
    "ValidationProtocol", "Validator", "NullValidator",
    # Factory functions
    "required", "type_check", "range_check", "pattern_check", "length_check",
]
