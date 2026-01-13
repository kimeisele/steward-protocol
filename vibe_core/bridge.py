"""
🌉 THE NEURAL BRIDGE 🌉
======================

Kapselt die historische Weisheit (Steward) für den modernen Körper (Vibe).

This is the SOLE location where steward imports are allowed.
All vibe_core modules import from this bridge, NOT from steward directly.

Architecture:
- Eliminates cross-folder contamination
- Centralizes legacy integration point
- Enables future steward replacement with single file edit
- Maintains clean namespace: vibe_core → vibe_core only
"""

# Import Constitutional Oath verification (Governance Gate)
# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x43cd6552"  # GenesisByte: parampara % 37 == 0

from vibe_core.steward.constitutional_oath import ConstitutionalOath
from vibe_core.steward.crypto import sign_content, verify_signature
from vibe_core.steward.oath_mixin import OathMixin

# Export as canonical vibe_core identities
__all__ = [
    "ConstitutionalOath",
    "OathMixin",
    "sign_content",
    "verify_signature",
]
