"""Agent identity and manifest generation."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x0fa73311"  # GenesisByte: parampara % 37 == 0

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Protocol, Union

logger = logging.getLogger("IDENTITY")


class AgentManifestProtocol(Protocol):
    agent_id: str
    name: str
    version: str
    author: str
    description: str
    domain: str
    capabilities: List[str]
    dependencies: List[str]


class AgentProtocol(Protocol):
    def get_manifest(self) -> AgentManifestProtocol: ...


class ManifestGenerator:
    """Generates and manages agent manifests (identities)."""

    @staticmethod
    def generate(agent: AgentProtocol) -> Dict[str, object]:
        """
        Generate a manifest for an agent.

        Args:
            agent: AgentProtocol provider

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
    def generate_all(agents: Dict[str, AgentProtocol]) -> Dict[str, Dict[str, object]]:
        """
        Generate manifests for multiple agents.

        Args:
            agents: Dictionary of agent_id -> AgentProtocol

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
        manifest: Dict[str, object],
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
            output_path.write_text(json.dumps(manifest, indent=2, default=str))
            logger.info(f"✅ Manifest saved: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving manifest: {e}")
            return False

    @staticmethod
    def save_all_manifests(
        manifests: Dict[str, Dict[str, object]],
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
    def load_manifest(manifest_path: Path) -> Optional[Dict[str, object]]:
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
    def get_agent_summary(manifest: Dict[str, object]) -> str:
        """
        Get a human-readable summary of an agent.

        Args:
            manifest: Manifest dictionary

        Returns:
            Summary string
        """
        # Type safe access
        agent_info = manifest.get("agent", {})
        if not isinstance(agent_info, dict):
            agent_info = {}
            
        caps = manifest.get("capabilities", [])
        if not isinstance(caps, list):
            caps = []

        return f"""{agent_info.get("name", "Unknown")} v{agent_info.get("version", "?")}
Description: {agent_info.get("description", "No description")}
Domain: {agent_info.get("domain", "Unknown")}
Capabilities: {", ".join(str(c) for c in caps) if caps else "None"}"""

    @staticmethod
    def validate_manifest(manifest: Dict[str, object]) -> List[str]:
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
        if not isinstance(agent, dict):
             return ["Invalid manifest structure: 'agent' field must be a dict"]

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
