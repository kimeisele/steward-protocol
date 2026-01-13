#!/usr/bin/env python3
"""
Cartridges - ARCH-050

A Cartridge is a specialized "app" for Vibe OS.
Each cartridge encapsulates:
  - A domain (e.g., Document Analysis, Code Refactoring, Research)
  - A specialized agent (e.g., Archivist, Coder, Researcher)
  - A playbook (workflow definition)
  - Tools specific to that domain
  - Offline-first capabilities (SmartLocalProvider)

This module provides the base classes and registry for cartridge management.

Design Philosophy:
- Cartridges are like "macOS apps" - installable, composable, offline-capable
- Each cartridge solves ONE problem really well (Unix philosophy)
- Cartridges can call each other (composability)
- Cartridges prioritize offline operation (SmartLocalProvider first)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x1c88f811"  # GenesisByte: parampara % 37 == 0

from .base import CartridgeBase, CartridgeConfig, CartridgeSpec
from .registry import CartridgeRegistry, get_default_cartridge_registry

__all__ = [
    "CartridgeBase",
    "CartridgeConfig",
    "CartridgeRegistry",
    "CartridgeSpec",
    "get_default_cartridge_registry",
]
