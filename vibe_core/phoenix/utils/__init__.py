"""Phoenix utilities - helper modules that are NOT config sections."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x226a87dd"  # GenesisByte: parampara % 37 == 0

from .circuits import CircuitConfig, CircuitStep, discover_circuits
from .routing import RoutingRule, load_routing_rules, parse_matrix_md, save_routing_rules

__all__ = [
    "CircuitConfig",
    "CircuitStep",
    "discover_circuits",
    "RoutingRule",
    "load_routing_rules",
    "parse_matrix_md",
    "save_routing_rules",
]
