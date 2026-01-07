import hashlib
import json
import os
from datetime import datetime
from pathlib import Path


def get_file_hash(path: str) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def main():
    base_dir = Path(".")

    # Files to hash
    files = {
        "CONSTITUTION.md": "CONSTITUTION.md",
        "gad000.md": "docs/architecture/GAD-0XX/GAD-000.md",
        "samkhya.md": "vibe_core/naga/intel/SAMKHYA.md",
        "genesis_v1": "data/dhruva/genesis_block.json",
    }

    hashes = {}
    print("🌊 VEDIC CRYPTO: Calculating Genesis V2 Hashes...\n")

    for key, path in files.items():
        full_path = base_dir / path
        if full_path.exists():
            h = get_file_hash(full_path)
            hashes[key] = h
            print(f"✅ {key:15} : {h}")
        else:
            print(f"❌ {key:15} : FILE NOT FOUND ({path})")
            return

    # Construct v2 Block
    genesis_v2 = {
        "genesis_id": "GEN-001-HOLOGRAPHIC",
        "previous_genesis_id": "GEN-000",
        "previous_genesis_hash": hashes["genesis_v1"],
        "timestamp": datetime.now().isoformat() + "+00:00",
        "constitution_hash": hashes["CONSTITUTION.md"],
        "gad000_hash": hashes["gad000.md"],
        "samkhya_hash": hashes["samkhya.md"],
        "protocol_invariants": {
            "5_regulative_principles": [
                "NO_CORRUPT_DATA_INGESTION",
                "NO_HALLUCINATION_DETERMINISM",
                "NO_RESOURCE_LEAKS",
                "NO_UNAUTHORIZED_CONNECTIONS",
                "PRIORITY_OF_CONNECTION",
            ],
            "immutable_properties": {
                "constitutional_oath_required": True,
                "ledger_append_only": True,
                "agent_registry_authoritative": True,
                "kernel_is_source_of_truth": True,
                "anti_mayavad_enforcement": True,
                "bhakti_priority_interrupt": True,
            },
        },
        "upgrade_manifest": {
            "reason": "Hard Fork to v2.0 Holographic Architecture",
            "authorized_by": "The 37th Sovereign",
            "breaking_changes": [
                "Added MantraProtocol (Bhakti) as 5th Principle",
                "Enforced Sovereign Signatures on all State Changes",
            ],
        },
        "bootstrap_agents": [
            "civic",
            "herald",
            "auditor",
            "archivist",
            "forum",
            "science",
            "temple",
            "oracle",
            "supreme_court",
            "dhruva",
            "watchman",
        ],
        "signature": "SIGNED_BY_USER_VIA_CHAT_CONFIRMATION",
    }

    output_path = base_dir / "data/dhruva/genesis_v2_holographic.json"
    with open(output_path, "w") as f:
        json.dump(genesis_v2, f, indent=2)

    print("\n✨ GEN-001 Sealing Complete.")
    print(f"📄 Written to: {output_path}")
    print("\nNext: Create chain.json and patch bootloader.")


if __name__ == "__main__":
    main()
