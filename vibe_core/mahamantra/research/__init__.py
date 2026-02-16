"""
Compatibility bridge for migrated research package.

Canonical location:
    vibe_core.mahamantra_research

Transitional compatibility:
    vibe_core.mahamantra.research
"""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any


def _get_impl():
    """Load canonical research package lazily to avoid import recursion."""
    return import_module("vibe_core.mahamantra_research")


# Redirect old package namespace to new on-disk module path, so imports like
# `vibe_core.mahamantra.research.physics` still resolve.
_new_root = Path(__file__).resolve().parents[2] / "mahamantra_research"
__path__ = [str(_new_root)]


def __getattr__(name: str) -> Any:
    """Delegate attribute access to canonical research package."""
    return getattr(_get_impl(), name)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(dir(_get_impl())))
