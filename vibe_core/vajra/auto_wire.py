"""
⚡ VAJRA Auto-Wire - Automatic Kernel Injection
===============================================

Utilities for automatically wiring components to the kernel.

Used in:
- Test fixtures (auto-wire all components)
- Kernel boot (wire system components)
- Plugin initialization
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x54ef262e"  # GenesisByte: parampara % 37 == 0

import logging
from typing import TYPE_CHECKING, Any, Sequence

from vibe_core.vajra.protocol import is_wirable

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("VAJRA")


def auto_wire(kernel: "RealVibeKernel", component: Any) -> bool:
    """
    Automatically wire a component to the kernel.

    If the component implements WiringProtocol, calls inject_kernel().
    If not wirable, returns False without error.

    Args:
        kernel: The RealVibeKernel to inject
        component: Any object that might be wirable

    Returns:
        True if component was wired, False if not wirable
    """
    if not is_wirable(component):
        return False

    try:
        component.inject_kernel(kernel)
        logger.debug(f"⚡ VAJRA: Auto-wired {component.__class__.__name__}")
        return True
    except Exception as e:
        logger.error(f"⚡ VAJRA: Failed to wire {component.__class__.__name__}: {e}")
        return False


def wire_all(kernel: "RealVibeKernel", *components: Any) -> int:
    """
    Wire multiple components to the kernel.

    Args:
        kernel: The RealVibeKernel to inject
        *components: Variable number of components to wire

    Returns:
        Number of components successfully wired
    """
    wired_count = 0
    for component in components:
        if auto_wire(kernel, component):
            wired_count += 1
    return wired_count


def deep_wire(
    kernel: "RealVibeKernel",
    obj: Any,
    visited: set | None = None,
    max_depth: int = 5,
) -> int:
    """
    Recursively wire an object and all its wirable attributes.

    Useful for wiring complex component trees.

    Args:
        kernel: The RealVibeKernel to inject
        obj: Root object to wire
        visited: Set of already-visited objects (for cycle detection)
        max_depth: Maximum recursion depth

    Returns:
        Total number of components wired
    """
    if visited is None:
        visited = set()

    if max_depth <= 0:
        return 0

    obj_id = id(obj)
    if obj_id in visited:
        return 0
    visited.add(obj_id)

    wired_count = 0

    # Wire this object if wirable
    if auto_wire(kernel, obj):
        wired_count += 1

    # Recurse into attributes
    for attr_name in dir(obj):
        if attr_name.startswith("_"):
            continue  # Skip private/dunder

        try:
            attr = getattr(obj, attr_name, None)
            if attr is None:
                continue

            # Skip non-objects (primitives, functions, etc.)
            if not hasattr(attr, "__dict__") and not hasattr(attr, "__slots__"):
                continue

            # Recurse
            wired_count += deep_wire(kernel, attr, visited, max_depth - 1)

        except Exception:
            continue  # Skip attributes that can't be accessed

    return wired_count


def wire_tools(kernel: "RealVibeKernel", tools: Sequence[Any]) -> int:
    """
    Wire a collection of tool objects.

    Common pattern for wiring tool registries.

    Args:
        kernel: The RealVibeKernel to inject
        tools: Sequence of tool objects

    Returns:
        Number of tools wired
    """
    wired = 0
    for tool in tools:
        if auto_wire(kernel, tool):
            wired += 1
            logger.info(f"⚡ VAJRA: Wired tool {getattr(tool, 'name', tool.__class__.__name__)}")
    return wired
