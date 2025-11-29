"""Agent identity and manifest generation."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.protocols import AgentManifest, VibeAgent

logger = logging.getLogger("IDENTITY")


class ManifestGenerator:
    """Generates and manages agent manifests (identities)."""

    @staticmethod
    def generate(agent: VibeAgent) -> Dict[str, Any]:
        """
        Generate a manifest for an agent.

        Args:
            agent: VibeAgent instance

        Returns:
            Dictionary representation of the agent's manifest
        """
        manifest = agent.get_manifest()

        return {
            "agent": {
                "id": manifest.agent_id,
                "name": manifest.name,
                "version": manifest.version,
                "author": manifest.author,
                "description": manifest.description,
                "domain": manifest.domain,
            },
            "capabilities": manifest.capabilities,
            "dependencies": manifest.dependencies,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def generate_all(agents: Dict[str, VibeAgent]) -> Dict[str, Dict[str, Any]]:
        """
        Generate manifests for multiple agents.

        Args:
            agents: Dictionary of agent_id -> VibeAgent

        Returns:
            Dictionary of agent_id -> manifest
        """
        manifests = {}

        for agent_id, agent in agents.items():
            try:
                manifests[agent_id] = ManifestGenerator.generate(agent)
            except Exception as e:
                logger.error(f"Error generating manifest for {agent_id}: {e}")
                manifests[agent_id] = {
                    "error": str(e),
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                }

        return manifests

    @staticmethod
    def save_manifest(
        manifest: Dict[str, Any],
        output_path: Path,
        agent_id: Optional[str] = None,
    ) -> bool:
        """
        Save a manifest to disk.

        Args:
            manifest: Manifest dictionary
            output_path: Path to write manifest file
            agent_id: Optional agent ID for filename if not provided

        Returns:
            True if successful
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(manifest, indent=2))
            logger.info(f"✅ Manifest saved: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving manifest: {e}")
            return False

    @staticmethod
    def save_all_manifests(
        manifests: Dict[str, Dict[str, Any]],
        output_dir: Path,
    ) -> int:
        """
        Save all manifests to disk.

        Args:
            manifests: Dictionary of agent_id -> manifest
            output_dir: Directory to save manifest files

        Returns:
            Number of manifests saved
        """
        saved = 0

        for agent_id, manifest in manifests.items():
            manifest_path = output_dir / f"{agent_id}_manifest.json"

            if ManifestGenerator.save_manifest(manifest, manifest_path, agent_id):
                saved += 1

        logger.info(f"✅ Saved {saved}/{len(manifests)} manifests")

        return saved

    @staticmethod
    def load_manifest(manifest_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load a manifest from disk.

        Args:
            manifest_path: Path to manifest file

        Returns:
            Manifest dictionary, or None if error
        """
        try:
            if not manifest_path.exists():
                logger.warning(f"Manifest not found: {manifest_path}")
                return None

            return json.loads(manifest_path.read_text())
        except Exception as e:
            logger.error(f"Error loading manifest: {e}")
            return None

    @staticmethod
    def get_agent_summary(manifest: Dict[str, Any]) -> str:
        """
        Get a human-readable summary of an agent.

        Args:
            manifest: Manifest dictionary

        Returns:
            Summary string
        """
        agent = manifest.get("agent", {})
        caps = manifest.get("capabilities", [])

        return f"""{agent.get("name", "Unknown")} v{agent.get("version", "?")}
Description: {agent.get("description", "No description")}
Domain: {agent.get("domain", "Unknown")}
Capabilities: {", ".join(caps) if caps else "None"}"""

    @staticmethod
    def validate_manifest(manifest: Dict[str, Any]) -> List[str]:
        """
        Validate a manifest structure.

        Args:
            manifest: Manifest dictionary

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check required agent fields
        agent = manifest.get("agent", {})

        if not agent.get("id"):
            errors.append("Missing required field: agent.id")
        if not agent.get("name"):
            errors.append("Missing required field: agent.name")
        if not agent.get("version"):
            errors.append("Missing required field: agent.version")

        # Check capabilities is a list
        if "capabilities" in manifest and not isinstance(manifest["capabilities"], list):
            errors.append("Field 'capabilities' must be a list")

        # Check dependencies is a list
        if "dependencies" in manifest and not isinstance(manifest["dependencies"], list):
            errors.append("Field 'dependencies' must be a list")

        return errors
