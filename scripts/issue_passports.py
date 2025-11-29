#!/usr/bin/env python3
"""
📜 THE PASSPORT OFFICE - STEWARD PROTOCOL COMPLIANCE 📜
=========================================================

This is the Certification Authority (CA) of the Agent Operating System.
It issues cryptographically-sealed passports (steward.json) for all agents.

PHASE 6: STEWARD PROTOCOL COMPLIANCE

The Passport Office:
1. Scans steward/system_agents/ for existing steward.json manifests
2. Extracts agent metadata from existing manifests
3. Generates new steward.json with Phase 6 schema
4. Calculates SHA-256 hash of the manifest (The Seal)
5. Records PASSPORT_ISSUED in Parampara blockchain
6. Saves updated steward.json to agent directory

GUARDRAILS (The 3 Laws):
✅ No Side Effects - Reads existing manifests, no agent instantiation
✅ Cryptographic Bind - Manifest hash recorded in Parampara
✅ No Blank Cheques - No passports for agents without capabilities

Usage:
    python scripts/issue_passports.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import hashlib
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from vibe_core.lineage import LineageChain, LineageEventType

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("PASSPORT_OFFICE")


class PassportOffice:
    """
    The Certification Authority for Agent Passports.

    This is the Notar. The Notary. The Issuer of Truth.
    """

    def __init__(self, lineage_path: str = "/tmp/vibe_os/kernel/lineage.db"):
        """Initialize the Passport Office with access to Parampara chain"""
        self.lineage = LineageChain(db_path=lineage_path)
        self.issued_count = 0
        self.denied_count = 0

        # Get constitution hash from Genesis Block (The Anchor)
        genesis = self.lineage.get_genesis_block()
        if genesis:
            self.constitution_hash = genesis.data.get("anchors", {}).get(
                "constitution_hash", "unknown"
            )
        else:
            logger.warning(
                "⚠️  Genesis Block not found - using placeholder constitution hash"
            )
            self.constitution_hash = "unknown"

        logger.info("📜 Passport Office initialized")
        logger.info(f"   Constitution Hash: {self.constitution_hash[:16]}...")

    def _calculate_manifest_hash(self, manifest: Dict[str, Any]) -> str:
        """
        Calculate SHA-256 hash of the manifest.

        This is The Seal. The cryptographic fingerprint.
        Any change to the manifest invalidates the seal.
        """
        # Serialize to canonical JSON (sorted keys, no whitespace)
        canonical_json = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    def _parse_old_manifest(self, manifest_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse an existing steward.json manifest and extract metadata.

        Handles two schemas:
        1. Nested schema: {"agent": {...}, "capabilities": {"operations": [...]}}
        2. Flat schema: {"agent_id": "...", "capabilities": ["..."]}

        Args:
            manifest_path: Path to existing steward.json

        Returns:
            Metadata dict, or None if parsing fails
        """
        try:
            with open(manifest_path, "r") as f:
                old_manifest = json.load(f)

            # Detect schema type
            if "agent" in old_manifest:
                # Nested schema (herald, civic, etc.)
                agent_data = old_manifest.get("agent", {})
                capabilities_data = old_manifest.get("capabilities", {})
                operations = capabilities_data.get("operations", [])
                capability_names = [op.get("name") for op in operations if "name" in op]

                metadata = {
                    "agent_id": agent_data.get("id", "unknown"),
                    "name": agent_data.get("name", "Unknown"),
                    "version": agent_data.get("version", "1.0.0"),
                    "description": old_manifest.get("credentials", {}).get(
                        "mandate", ""
                    ),
                    "domain": agent_data.get("specialization", "SYSTEM"),
                    "capabilities": capability_names,
                }
            else:
                # Flat schema (scribe, etc.)
                capabilities = old_manifest.get("capabilities", [])
                # If capabilities is already a list, use it directly
                if isinstance(capabilities, list):
                    capability_names = capabilities
                else:
                    # Fallback to operations format
                    operations = capabilities.get("operations", [])
                    capability_names = [
                        op.get("name") for op in operations if "name" in op
                    ]

                metadata = {
                    "agent_id": old_manifest.get("agent_id", "unknown"),
                    "name": old_manifest.get("name", "Unknown"),
                    "version": old_manifest.get("version", "1.0.0"),
                    "description": old_manifest.get("description", ""),
                    "domain": old_manifest.get("domain", "SYSTEM"),
                    "capabilities": capability_names,
                }

            # GUARDRAIL #3: No Blank Cheques
            if not metadata["capabilities"] or len(metadata["capabilities"]) == 0:
                logger.warning(
                    f"⚠️  Agent '{metadata['agent_id']}' has no capabilities defined. Passport DENIED."
                )
                return None

            return metadata

        except Exception as e:
            logger.error(f"❌ Failed to parse manifest {manifest_path}: {e}")
            import traceback

            traceback.print_exc()
            return None

    def _generate_manifest(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a STEWARD Protocol compliant manifest (Phase 6 schema).

        Schema:
        {
            "identity": { "agent_id", "name" },
            "specs": { "version", "domain", "description" },
            "capabilities": { "operations": [...] },
            "governance": { "constitution_hash", "issued_at", "compliance_level" }
        }
        """
        manifest = {
            "identity": {"agent_id": metadata["agent_id"], "name": metadata["name"]},
            "specs": {
                "version": metadata["version"],
                "domain": metadata["domain"],
                "description": metadata["description"],
            },
            "capabilities": {
                "operations": [
                    {"name": cap, "description": f"{cap} operation"}
                    for cap in metadata["capabilities"]
                ]
            },
            "governance": {
                "constitution_hash": self.constitution_hash,
                "issued_at": datetime.utcnow().isoformat() + "Z",
                "compliance_level": 2,  # Level 2: Full manifest
                "issuer": "passport_office",
            },
        }

        return manifest

    def issue_passport(self, manifest_path: Path) -> bool:
        """
        Issue a passport for an agent by reissuing their steward.json.

        This is the full workflow:
        1. Parse old manifest
        2. Extract metadata
        3. Generate new manifest (Phase 6 schema)
        4. Calculate hash (The Seal)
        5. Record in Parampara
        6. Save steward.json

        Args:
            manifest_path: Path to existing steward.json

        Returns:
            True if passport issued successfully, False otherwise
        """
        agent_dir = manifest_path.parent
        agent_id = agent_dir.name

        logger.info(f"📋 Processing: {agent_id}")

        # Step 1: Parse old manifest
        metadata = self._parse_old_manifest(manifest_path)
        if not metadata:
            self.denied_count += 1
            return False

        # Step 2: Generate new manifest
        manifest = self._generate_manifest(metadata)

        # Step 3: Calculate hash (The Seal)
        manifest_hash = self._calculate_manifest_hash(manifest)
        logger.info(f"   🔒 Manifest hash: {manifest_hash[:16]}...")

        # Step 4: Record in Parampara (GUARDRAIL #2: Cryptographic Bind)
        try:
            self.lineage.add_block(
                event_type=LineageEventType.PASSPORT_ISSUED,
                agent_id=metadata["agent_id"],
                data={
                    "manifest_hash": manifest_hash,
                    "capabilities": metadata["capabilities"],
                    "version": metadata["version"],
                    "issued_at": manifest["governance"]["issued_at"],
                    "constitution_hash": self.constitution_hash,
                },
            )
            logger.info(f"   ⛓️  Recorded in Parampara")
        except Exception as e:
            logger.error(f"   ❌ Failed to record in Parampara: {e}")
            return False

        # Step 5: Save steward.json (overwrite with new schema)
        try:
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2, sort_keys=True)
            logger.info(f"   ✅ Passport issued: {manifest_path}")
            self.issued_count += 1
            return True
        except Exception as e:
            logger.error(f"   ❌ Failed to write manifest: {e}")
            return False

    def close(self):
        """Close the Passport Office"""
        if self.lineage:
            self.lineage.close()


def discover_manifests(include_citizens: bool = True) -> List[Path]:
    """
    Discover all existing steward.json manifests.

    Args:
        include_citizens: If True, also scan agent_city/registry/ for citizen agents

    Returns:
        List of paths to steward.json files
    """
    manifests = []

    # Scan system agents
    system_agents_path = Path("steward/system_agents")
    for manifest_path in system_agents_path.glob("*/steward.json"):
        manifests.append(manifest_path)

    # Scan citizen agents (agent_city/registry/)
    if include_citizens:
        citizen_agents_path = Path("agent_city/registry")
        for manifest_path in citizen_agents_path.glob("*/steward.json"):
            manifests.append(manifest_path)

    return sorted(manifests)


def main():
    """
    Main execution: Issue passports for all agents.
    """
    print("=" * 70)
    print("📜 PASSPORT OFFICE - STEWARD PROTOCOL COMPLIANCE")
    print("=" * 70)
    print()

    # Initialize Passport Office
    office = PassportOffice()

    try:
        # Discover all manifests
        print("[STEP 1] Discovering existing steward.json manifests...")
        manifests = discover_manifests()
        print(f"         Found {len(manifests)} manifests")
        print()

        if len(manifests) == 0:
            print("⚠️  No manifests found. Check that steward.json files exist.")
            return False

        # Issue passports
        print("[STEP 2] Issuing passports...")
        for manifest_path in manifests:
            office.issue_passport(manifest_path)

        print()
        print("=" * 70)
        print("📊 PASSPORT ISSUANCE REPORT")
        print("=" * 70)
        print(f"Total Agents Processed: {office.issued_count + office.denied_count}")
        print(f"Passports Issued: {office.issued_count}")
        print(f"Passports Denied: {office.denied_count}")
        print()

        if office.denied_count > 0:
            print("⚠️  Some agents were denied passports (no capabilities)")

        # Verify Parampara chain
        print("[VERIFICATION] Checking Parampara chain integrity...")
        if office.lineage.verify_chain():
            print("               ✅ Chain integrity verified")
        else:
            print("               ❌ Chain corrupted!")
            return False

        chain_length = office.lineage.get_chain_length()
        print(f"               Total blocks: {chain_length}")
        print()

        print("=" * 70)
        print("✅ PASSPORT ISSUANCE COMPLETE")
        print("=" * 70)
        print()
        print(f"All {office.issued_count} agents now have:")
        print("  📜 steward.json (Phase 6 schema, cryptographically sealed)")
        print("  ⛓️  PASSPORT_ISSUED block in Parampara")
        print("  🏛️  STEWARD Protocol Compliance Level 2")
        print()
        print("🚀 READY FOR DEPLOYMENT")
        print()

        return True

    except Exception as e:
        print(f"\n❌ PASSPORT OFFICE ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        office.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
