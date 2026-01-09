"""
VAJRA IDENTITY REGISTRY (VajraProtocol)
=======================================

"The Diamond Keys to the Castle."

This module defines the Immutable Anchor of Trust.
Instead of brittle JSON files, the integrity hashes are defined as
CODE CONSTANTS within the Python Type System.

To update a hash, you must change this file, which requires:
1. Git History Tracking
2. Code Review / Pull Request
3. Sovereign Authorization (merge to main)

This IS the Protocol.
"""

from typing import Dict, Final

# The Source of Truth (SHA-256 Hashes)
# Updated: 2026-01-09
# Status: GAD-000_ACTIVE
VAJRA_KEYS: Final[Dict[str, str]] = {
    # -------------------------------------------------------------------------
    # GAD-000: The Constitution & Law
    # -------------------------------------------------------------------------
    "CONSTITUTION.md": "a868f2647445ab356c485ac4363cc718c38d3bf3a8a7452a72d19f027a92c41f",
    "docs/architecture/GAD-0XX/GAD-000.md": "1edfa6e03f94b45c8a2c0d2b604efdf2a4ed65253fb491533022dfb450d5288e",
    # -------------------------------------------------------------------------
    # Ring 0: The Kernel Core
    # -------------------------------------------------------------------------
    "vibe_core/kernel_impl.py": "6f1121c28fdbef4cc463b76ed5cef2f53b20f8b30275a4e0284205aaa1a393dd",
    "vibe_core/kernel_ops.py": "51ddee7fb5e0b4f01a9e5620768dac5b53cd315022ef92afe155de66dab7c83f",
    "vibe_core/ledger.py": "33d222ea5fc0914a14c40aec230046f56e532372cb20df77c01d44b89b7923a0",
    # -------------------------------------------------------------------------
    # Ring 0: Protocols & Security
    # -------------------------------------------------------------------------
    "vibe_core/security.py": "52df4028c883f95c92a469f1e9bd496e31c003ce858791a4a69778f933770c9f",  # Updated for GAD-000
    "vibe_core/protocols/integrity.py": "5e31909db28c991a7f3312021334a2c00c32e8372f5848ee259c2ee5189da071",  # Updated for Keys Registry
    "vibe_core/protocols/substrate.py": "b544708985646609ba912a186ee08fde7266f46ee4f1bc0e51613742310c6788",
    "vibe_core/narasimha.py": "2c9ce88ba49216c97020d2741f65015ab86748d0becfa6e065261ab8adbb8fdf",
    "vibe_core/capability_registry.py": "bac393afde8744a51afbb8e7cd7368da306d6a6f44660f88354f583facfc04bb",
    "vibe_core/bridge.py": "a79b06711964e1a5ef932e18280076e69e6922eaf3ddeae3a59b7a20847843a5",
    # -------------------------------------------------------------------------
    # Ring 0: Plugin System
    # -------------------------------------------------------------------------
    "vibe_core/plugin_protocol.py": "5d9e469d7b2096fcf5fb8af66ce45e58cd07dbf901bd4e9ed17209d42032d6eb",
    "vibe_core/plugin_loader.py": "042b8f96bae10c8782cdfc6fcfc49651f25e20601d67c8f2d4f15ec79da04181",
    # -------------------------------------------------------------------------
    # Ring 0: Infrastructure & Workflows
    # -------------------------------------------------------------------------
    ".github/workflows/attest.yml": "a546c5cf343917b31ede30c68ffe7cf2ea97fae41b0ea9ffcbf20f719f9b668c",
    ".github/workflows/container-build.yml": "d303af901e0d3d9031436c40cbda9b5b7d8b5f8e125ab1c81762ffa9d9103805",
    ".github/workflows/deploy.yml": "5b86104b01fe4fc2f6371b1ad56dce89795c161ef868dc88e081581beab34ed1",
    ".github/workflows/factory.yml": "8a313882e7e9e969b6e8b036753a71a6a248c37f3b5cdce304172bda3967c3ae",
    ".github/workflows/heartbeat.yml": "6be13990888a0b38104a89cf4c6e985cacca08c2921833dc74502718ec154d0b",
    ".github/workflows/integration-tests.yml": "06c4ae417af9190095fd198e812598828ca5abc28cfd33fcd5864d8355e912a6",
    ".github/workflows/scheduled-agents.yml": "a2e678ec15ba0ebd7bf7c6ed96605fbdb47a77e732d1b5af880f9616405cc082",
    ".github/workflows/scribe-docs.yml": "05761742e35a98505a8c662b190e2a675745e49fdb1efbde7c372cbe3d4b0076",
    ".github/workflows/steward-ci.yml": "a29bdc460b439cb441c60076d95b1d8210cf18a3fda9b55febbb124b3497322e",
    ".github/workflows/system-cycle.yml": "a3fb672d1797e4a541f5aea81472c5b3c6e0a8020fc483ce82842342ba67da85",
    ".pre-commit-config.yaml": "f510af9dbfc4ae191c95d1d05ba12b38f1471b12d8aa72f14e088ef49f055dc4",
    ".gitignore": "2787351a91ba738b66b45f3e19da8304410ef91175ef541850c33bab183e7320",
    "scripts/governance/vishnu_guard.py": "ad997b101704806ec414b712a51db4a79e2a897b4e1077df540d1c587df09171",
}
