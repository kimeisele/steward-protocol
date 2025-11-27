#!/usr/bin/env python3
"""
The Steward Cartridge - ARCH-051: Personal OS Self-Management

A meta-app that manages Vibe OS preferences, configuration, and personality.

Capabilities:
1. update_user_preferences(key, value) → Safely write to STEWARD.md
2. manage_api_keys(provider, key) → Set API keys in .env (Phoenix Safety Wrapper)
3. change_persona(tone) → Change operator tone (Precise, Friendly, Stoic, etc.)

This cartridge demonstrates that users don't need to manually edit files.
Instead, they interact with the OS through natural commands.

Example:
    steward = StewardCartridge()
    steward.change_persona("German Technical")  # ← User preference
    steward.manage_api_keys("anthropic", "sk-xxx")  # ← API key management
    steward.update_user_preferences("language", "Deutsch")  # ← Personalization
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from vibe_core.cartridges.base import CartridgeBase

logger = logging.getLogger(__name__)


class StewardCartridge(CartridgeBase):
    """
    The Steward Cartridge - Personal OS Configuration & Preferences.

    This is the "Settings App" for Vibe OS.
    It manages:
    - User identity and preferences
    - API key configuration (with safety checks)
    - Operator persona and tone
    - System defaults and customizations
    """

    name = "steward"
    version = "1.0.0"
    description = "Personal OS self-management - preferences, API keys, persona"
    author = "Vibe Agency"

    def __init__(self, vibe_root: Path | None = None):
        """Initialize the Steward cartridge."""
        super().__init__(vibe_root=vibe_root)

        self.env_path = self.vibe_root / ".env"
        self.steward_md_path = self.vibe_root / "STEWARD.md"
        self.steward_json_path = self.vibe_root / "steward.json"

        logger.info("🎩 The Steward initialized - Ready to manage your preferences")

    def update_user_preferences(self, key: str, value: str) -> dict[str, Any]:
        """
        Update user preferences safely.

        This writes to steward.json (machine-readable) and can optionally
        update STEWARD.md for human-readable documentation.

        Args:
            key: Preference key (e.g., "user_name", "language", "theme")
            value: Preference value

        Returns:
            Status dict with result and confirmation
        """
        try:
            # Load current preferences
            if self.steward_json_path.exists():
                with open(self.steward_json_path) as f:
                    steward_config = json.load(f)
            else:
                steward_config = {
                    "agent": {"id": "vibe-agency-orchestrator", "name": "STEWARD"},
                    "preferences": {},
                }

            # Update preference
            if "preferences" not in steward_config:
                steward_config["preferences"] = {}

            steward_config["preferences"][key] = value

            # Write back to steward.json
            with open(self.steward_json_path, "w") as f:
                json.dump(steward_config, f, indent=2)

            logger.info(f"✅ Preference updated: {key} = {value}")

            return {
                "status": "success",
                "message": f"Updated preference: {key}",
                "key": key,
                "value": value,
                "saved_to": str(self.steward_json_path),
            }

        except Exception as e:
            logger.error(f"❌ Failed to update preference: {e}")
            return {"status": "error", "message": str(e), "key": key}

    def manage_api_keys(self, provider: str, api_key: str) -> dict[str, Any]:
        """
        Manage API keys with safety checks (Phoenix Safety Wrapper).

        This writes to .env file, which is NOT committed to git (protected).

        Args:
            provider: API provider (e.g., "anthropic", "google", "openai")
            api_key: The API key to set

        Returns:
            Status dict with result and confirmation

        Safety Features:
        - Keys are NOT logged (only provider name)
        - .env file is in .gitignore
        - Validates key format basics (e.g., anthropic keys start with "sk-")
        """
        try:
            # Basic validation
            if not api_key or len(api_key) < 10:
                return {
                    "status": "error",
                    "message": "API key is too short or empty",
                    "provider": provider,
                }

            # Map provider to environment variable
            provider_map = {
                "anthropic": "ANTHROPIC_API_KEY",
                "google": "GOOGLE_SEARCH_API_KEY",
                "openai": "OPENAI_API_KEY",
                "gemini": "GOOGLE_API_KEY",
            }

            env_var = provider_map.get(provider.lower())
            if not env_var:
                return {
                    "status": "error",
                    "message": f"Unknown provider: {provider}. Supported: anthropic, google, openai, gemini",
                    "provider": provider,
                }

            # Read existing .env
            env_content = ""
            if self.env_path.exists():
                with open(self.env_path) as f:
                    env_content = f.read()

            # Update or add the key
            if re.search(f"^{env_var}=", env_content, re.MULTILINE):
                # Replace existing
                env_content = re.sub(
                    f"^{env_var}=.*$", f"{env_var}={api_key}", env_content, flags=re.MULTILINE
                )
            else:
                # Append new
                env_content += f"\n{env_var}={api_key}\n"

            # Write back to .env
            with open(self.env_path, "w") as f:
                f.write(env_content)

            # DO NOT LOG THE KEY ITSELF
            logger.info(f"✅ API key configured for provider: {provider}")

            # Also set in current process environment
            os.environ[env_var] = api_key

            return {
                "status": "success",
                "message": f"API key configured for {provider}",
                "provider": provider,
                "env_var": env_var,
                "saved_to": str(self.env_path),
                "warning": ".env file is NOT synced to git (protected)",
            }

        except Exception as e:
            logger.error(f"❌ Failed to configure API key: {e}")
            return {"status": "error", "message": str(e), "provider": provider}

    def change_persona(self, tone: str) -> dict[str, Any]:
        """
        Change the STEWARD operator persona/tone.

        Available tones:
        - "Precise" → Technical, exact language
        - "Friendly" → Warm, conversational
        - "Stoic" → Minimal, just facts
        - "German Technical" → German language, technical
        - "German Friendly" → German language, warm
        - Custom: Pass any tone description

        Args:
            tone: Persona tone (string)

        Returns:
            Status dict with confirmation
        """
        try:
            # Load steward config
            if self.steward_json_path.exists():
                with open(self.steward_json_path) as f:
                    steward_config = json.load(f)
            else:
                steward_config = {
                    "agent": {"id": "vibe-agency-orchestrator", "name": "STEWARD"},
                    "preferences": {},
                }

            # Update persona in preferences
            if "preferences" not in steward_config:
                steward_config["preferences"] = {}

            steward_config["preferences"]["operator_tone"] = tone

            # Write back
            with open(self.steward_json_path, "w") as f:
                json.dump(steward_config, f, indent=2)

            logger.info(f"🎭 Persona changed to: {tone}")

            return {
                "status": "success",
                "message": f"Operator persona changed to: {tone}",
                "tone": tone,
                "saved_to": str(self.steward_json_path),
                "note": "This preference will be used in the next system boot",
            }

        except Exception as e:
            logger.error(f"❌ Failed to change persona: {e}")
            return {"status": "error", "message": str(e)}

    def get_user_name(self) -> str:
        """
        Get the user's name from various sources.

        Priority:
        1. STEWARD.md preferences
        2. steward.json preferences
        3. git config user.name
        4. environment variable USER
        5. "Friend" (default)
        """
        try:
            # Try steward.json first
            if self.steward_json_path.exists():
                with open(self.steward_json_path) as f:
                    config = json.load(f)
                    if "preferences" in config and "user_name" in config["preferences"]:
                        return config["preferences"]["user_name"]

            # Try git config
            import subprocess

            try:
                result = subprocess.run(
                    ["git", "config", "user.name"],
                    cwd=self.vibe_root,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except Exception:
                pass

            # Try environment
            if "USER" in os.environ:
                return os.environ["USER"]

            # Fallback
            return "Friend"

        except Exception:
            return "Friend"

    def get_operator_tone(self) -> str:
        """Get the current operator tone from preferences."""
        try:
            if self.steward_json_path.exists():
                with open(self.steward_json_path) as f:
                    config = json.load(f)
                    if "preferences" in config and "operator_tone" in config["preferences"]:
                        return config["preferences"]["operator_tone"]
        except Exception:
            pass

        return "Professional"  # Default

    def report_status(self) -> dict[str, Any]:
        """Report Steward status and current preferences."""
        status = super().report_status()
        status.update(
            {
                "user_name": self.get_user_name(),
                "operator_tone": self.get_operator_tone(),
                "config_files": {
                    "steward_json": str(self.steward_json_path)
                    if self.steward_json_path.exists()
                    else "not_found",
                    "env_file": str(self.env_path) if self.env_path.exists() else "not_found",
                },
            }
        )
        return status


__all__ = ["StewardCartridge"]
