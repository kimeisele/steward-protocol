"""Typed contracts for research language runtime orchestration."""

from __future__ import annotations

from typing import NamedTuple, Optional


class RuntimeTick(NamedTuple):
    """Normalized tick payload from Venu DIW dispatch."""

    tick: int
    position: int
    phase: int
    mode: int
    diw: int
    venu: int
    vamsi: int
    murali: int


class InputSignal(NamedTuple):
    """Normalized user signal entering runtime orchestration."""

    text: str
    source: str = "text"


class RuntimeEnvelope(NamedTuple):
    """Envelope passed from runtime scheduler to language generation output."""

    input_signal: InputSignal
    tick: Optional[RuntimeTick]
    rhythm_signature: str
    seed: int
    attractor: int
    output: str
