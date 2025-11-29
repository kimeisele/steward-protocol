"""
CONFIG LOADER: Service for loading and managing configuration

Provides high-level interface for configuration management.
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from .schema import CityConfig
from .schema import load_config as schema_load_config


class ConfigLoader:
    """High-level configuration loading service"""

    def __init__(self, config_path: str = "config/matrix.yaml"):
        """
        Initialize ConfigLoader.

        Args:
            config_path: Path to configuration YAML file
        """
        self.config_path = Path(config_path)
        self._config: Optional[CityConfig] = None

    def load(self) -> CityConfig:
        """
        Load and validate configuration.

        Returns:
            Validated CityConfig instance

        Raises:
            FileNotFoundError: If config file not found
            ValueError: If config validation fails
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\nExpected at: {self.config_path.absolute()}"
            )

        try:
            self._config = schema_load_config(str(self.config_path))
            return self._config
        except ValueError as e:
            raise ValueError(f"Failed to load configuration: {e}")

    @property
    def config(self) -> CityConfig:
        """
        Get current configuration (must load first).

        Returns:
            CityConfig instance

        Raises:
            RuntimeError: If load() hasn't been called yet
        """
        if self._config is None:
            raise RuntimeError("Configuration not loaded. Call load() first.")
        return self._config

    def is_loaded(self) -> bool:
        """Check if configuration has been loaded"""
        return self._config is not None

    def validate(self) -> Dict[str, Any]:
        """
        Validate loaded configuration and return diagnostic report.

        Returns:
            Diagnostic report with validation results

        Raises:
            RuntimeError: If load() hasn't been called yet
        """
        if not self.is_loaded():
            raise RuntimeError("Configuration not loaded. Call load() first.")

        config = self._config
        report = {
            "valid": True,
            "city_name": config.city_name,
            "federation_version": config.federation_version,
            "checks": {
                "governance": self._check_governance(config),
                "economy": self._check_economy(config),
                "security": self._check_security(config),
                "integrations": self._check_integrations(config),
            },
        }

        return report

    @staticmethod
    def _check_governance(config: CityConfig) -> Dict[str, Any]:
        """Check governance configuration"""
        gov = config.governance
        return {
            "voting_threshold": f"{gov.voting_threshold * 100}%",
            "quorum_required": f"{gov.quorum_required * 100}%",
            "proposal_cost": gov.proposal_cost,
            "status": "OK",
        }

    @staticmethod
    def _check_economy(config: CityConfig) -> Dict[str, Any]:
        """Check economy configuration"""
        econ = config.economy
        return {
            "initial_credits": econ.initial_credits,
            "total_supply_cap": econ.total_credit_supply_cap,
            "broadcast_cost": econ.broadcast_cost,
            "research_cost": econ.research_cost,
            "status": "OK",
        }

    @staticmethod
    def _check_security(config: CityConfig) -> Dict[str, Any]:
        """Check security configuration"""
        sec = config.security
        return {
            "signatures_required": sec.require_signatures,
            "algorithm": sec.signature_algorithm,
            "immutable_ledger": sec.immutable_ledger,
            "status": "OK",
        }

    @staticmethod
    def _check_integrations(config: CityConfig) -> Dict[str, Any]:
        """Check integration configuration"""
        integ = config.integrations
        return {
            "tavily_enabled": integ.tavily.enabled,
            "twitter_enabled": integ.twitter.enabled,
            "reddit_enabled": integ.reddit.enabled,
            "status": "OK",
        }

    def print_summary(self) -> None:
        """Print human-readable configuration summary"""
        if not self.is_loaded():
            print("❌ Configuration not loaded")
            return

        config = self._config
        print("\n" + "=" * 70)
        print("🏙️  CITY CONFIGURATION SUMMARY")
        print("=" * 70)
        print(f"City: {config.city_name}")
        print(f"Version: {config.federation_version}")
        print(f"Timestamp: {config.timestamp_created}")

        print("\n💰 ECONOMY")
        print(f"  Initial Credits: {config.economy.initial_credits}")
        print(f"  Supply Cap: {config.economy.total_credit_supply_cap}")
        print(f"  Broadcast Cost: {config.economy.broadcast_cost}")

        print("\n🏛️  GOVERNANCE")
        print(f"  Voting Threshold: {config.governance.voting_threshold * 100}%")
        print(f"  Quorum Required: {config.governance.quorum_required * 100}%")

        print("\n🔐 SECURITY")
        print(f"  Signatures Required: {config.security.require_signatures}")
        print(f"  Algorithm: {config.security.signature_algorithm}")

        print("\n" + "=" * 70)
