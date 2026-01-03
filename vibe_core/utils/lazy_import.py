"""Lazy import utilities for boot optimization."""

from typing import Type, TypeVar

T = TypeVar("T")

_cache = {}


def lazy_class(module_path: str, class_name: str) -> Type[T]:
    """Import a class lazily on first access."""
    key = f"{module_path}.{class_name}"
    if key not in _cache:
        import importlib

        module = importlib.import_module(module_path)
        _cache[key] = getattr(module, class_name)
    return _cache[key]
