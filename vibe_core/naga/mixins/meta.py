"""
NAGA Active Mixin Metaclass Base.

Provides a unified metaclass that can handle multiple Active Genes.
Solves the metaclass conflict when combining ActiveSeshaMixin + ActiveTakshakaMixin.

The pattern: All Active Gene metaclasses inherit from NagaActiveMixinMeta,
which allows Python to resolve the MRO correctly.
"""

from typing import Any, Dict, Tuple


class NagaActiveMixinMeta(type):
    """
    Base metaclass for all NAGA Active Mixins.

    This metaclass does nothing on its own - it serves as a common
    ancestor so that derived metaclasses can be combined without conflict.

    Usage:
        class MyMixinMeta(NagaActiveMixinMeta):
            def __new__(mcs, name, bases, namespace):
                cls = super().__new__(mcs, name, bases, namespace)
                # Custom wrapping logic here
                return cls
    """

    def __new__(
        mcs,
        name: str,
        bases: Tuple[type, ...],
        namespace: Dict[str, Any],
    ) -> type:
        return super().__new__(mcs, name, bases, namespace)
