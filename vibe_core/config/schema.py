"""
THE DHARMA SCHEMA: Pydantic Models for Configuration Validation

These models define the structure and constraints for the entire system.
If the Soul (Config) is corrupted, the Body (Kernel) must not wake.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

# ============================================================================
# GOVERNANCE LAYER
# ============================================================================


class GovernanceConfig(BaseModel):
    """Constitutional Parameters for the City"""

    voting_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Fraction of votes required for proposal to pass",
    )
    quorum_required: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Fraction of agents required to vote for quorum",
    )
    proposal_cost: float = Field(default=5, ge=0, description="Credits required to submit a proposal")
    proposal_duration_hours: int = Field(default=24, ge=1, description="Hours voting stays open")
    license_revocation_enabled: bool = Field(default=True, description="Whether CIVIC can revoke agent licenses")
    credit_audit_frequency_hours: int = Field(default=6, ge=1, description="How often to audit agent credits")

    model_config = ConfigDict(extra="forbid")


# ============================================================================
# ECONOMY LAYER
# ============================================================================


class EconomyConfig(BaseModel):
    """Credit System Parameters"""

    initial_credits: float = Field(default=100, ge=0, description="Starting credits for each agent")
    refill_amount: float = Field(default=50, ge=0, description="Credits in emergency refill")
    refill_frequency_hours: int = Field(default=12, ge=1, description="How often agents can request refills")

    # Costs
    broadcast_cost: float = Field(default=1, ge=0, description="Cost per post")
    proposal_cost: float = Field(default=5, ge=0, description="Cost per proposal")
    research_cost: float = Field(default=2, ge=0, description="Cost per research search")
    media_cost: float = Field(default=1, ge=0, description="Cost per image generation")

    # Rewards
    vote_reward: float = Field(default=0, ge=0, description="Reward for voting")
    verification_reward: float = Field(default=1, ge=0, description="Reward for verification")

    # Supply control
    total_credit_supply_cap: float = Field(default=100000, ge=0, description="Maximum credits in circulation")
    inflation_monthly_percent: float = Field(default=5, ge=0, le=100, description="Monthly inflation rate")

    model_config = ConfigDict(extra="forbid")


# ============================================================================
# AGENT PARAMETERS
# ============================================================================


class HeraldConfig(BaseModel):
    """Media Agent Parameters"""

    content_style: str = Field(default="cyberpunk_professional")
    tone_variation: float = Field(default=0.3, ge=0.0, le=1.0)
    posting_frequency_hours: int = Field(default=2, ge=1)
    batch_size: int = Field(default=3, ge=1)
    research_enabled: bool = Field(default=True)
    research_frequency_hours: int = Field(default=4, ge=1)
    default_search_engine: str = Field(default="tavily")
    max_posts_per_day: int = Field(default=20, ge=1)
    twitter_enabled: bool = Field(default=True)
    reddit_enabled: bool = Field(default=True)

    model_config = ConfigDict(extra="forbid")


class ScienceConfig(BaseModel):
    """Research Agent Parameters"""

    search_provider: str = Field(default="tavily")
    max_search_results: int = Field(default=5, ge=1)
    search_freshness_days: int = Field(default=7, ge=1)
    fact_check_enabled: bool = Field(default=True)
    source_verification_required: bool = Field(default=True)
    anomaly_detection_enabled: bool = Field(default=True)
    pattern_recognition_enabled: bool = Field(default=True)
    searches_per_hour: int = Field(default=10, ge=1)
    validation_timeout_seconds: int = Field(default=30, ge=1)

    model_config = ConfigDict(extra="forbid")


class ForumConfig(BaseModel):
    """Democracy Agent Parameters"""

    proposal_min_length: int = Field(default=50, ge=1)
    proposal_max_length: int = Field(default=5000, ge=1)
    description_required: bool = Field(default=True)
    voting_enabled: bool = Field(default=True)
    anonymous_voting: bool = Field(default=False)
    constitutional_amendments_require_supermajority: bool = Field(default=True)

    model_config = ConfigDict(extra="forbid")


class CivicConfig(BaseModel):
    """Authority Agent Parameters"""

    auto_register_new_agents: bool = Field(default=True)
    validation_strict_mode: bool = Field(default=False)
    auto_revoke_zero_credits: bool = Field(default=True)
    revocation_grace_period_hours: int = Field(default=0, ge=0)
    ledger_compression_enabled: bool = Field(default=True)
    ledger_backup_frequency_hours: int = Field(default=24, ge=1)

    model_config = ConfigDict(extra="forbid")


class AgentParametersConfig(BaseModel):
    """All Agent Configuration Parameters"""

    herald: HeraldConfig = Field(default_factory=HeraldConfig)
    science: ScienceConfig = Field(default_factory=ScienceConfig)
    forum: ForumConfig = Field(default_factory=ForumConfig)
    civic: CivicConfig = Field(default_factory=CivicConfig)

    model_config = ConfigDict(extra="allow")  # Allow additional agents


# ============================================================================
# MONITORING & AUDIT
# ============================================================================


class MonitoringConfig(BaseModel):
    """System Monitoring & Audit Parameters"""

    health_check_interval_minutes: int = Field(default=5, ge=1)
    log_level: str = Field(default="INFO")
    log_all_transactions: bool = Field(default=True)
    transaction_log_path: str = Field(default="data/logs/transactions.log")
    metrics_collection_enabled: bool = Field(default=True)
    metrics_export_frequency_hours: int = Field(default=1, ge=1)

    model_config = ConfigDict(extra="forbid")


# ============================================================================
# SECURITY
# ============================================================================


class SecurityConfig(BaseModel):
    """Security Parameters"""

    require_signatures: bool = Field(default=True)
    signature_algorithm: str = Field(default="ecdsa")
    global_rate_limit_requests_per_minute: int = Field(default=100, ge=1)
    per_agent_rate_limit_per_minute: int = Field(default=10, ge=1)
    immutable_ledger: bool = Field(default=True)
    enable_access_logs: bool = Field(default=True)

    model_config = ConfigDict(extra="forbid")


# ============================================================================
# INTEGRATIONS
# ============================================================================


class TavilyConfig(BaseModel):
    """Tavily Integration Parameters"""

    enabled: bool = Field(default=True)
    model: str = Field(default="gpt-4-turbo")
    timeout_seconds: int = Field(default=30, ge=1)

    model_config = ConfigDict(extra="forbid")


class TwitterConfig(BaseModel):
    """Twitter Integration Parameters"""

    enabled: bool = Field(default=True)
    max_tweets_per_agent: int = Field(default=20, ge=1)
    rate_limit_window_minutes: int = Field(default=60, ge=1)

    model_config = ConfigDict(extra="forbid")


class RedditConfig(BaseModel):
    """Reddit Integration Parameters"""

    enabled: bool = Field(default=True)
    subreddits: List[str] = Field(default_factory=lambda: ["r/agenttech"])
    rate_limit_window_minutes: int = Field(default=60, ge=1)

    model_config = ConfigDict(extra="forbid")


class DatabaseConfig(BaseModel):
    """Database Configuration"""

    path: str = Field(default="data/registry/")
    backup_enabled: bool = Field(default=True)
    backup_interval_hours: int = Field(default=24, ge=1)

    model_config = ConfigDict(extra="forbid")


class IntegrationsConfig(BaseModel):
    """External Integration Parameters"""

    tavily: TavilyConfig = Field(default_factory=TavilyConfig)
    twitter: TwitterConfig = Field(default_factory=TwitterConfig)
    reddit: RedditConfig = Field(default_factory=RedditConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)

    model_config = ConfigDict(extra="allow")  # Allow additional integrations


# ============================================================================
# CITY CONFIG - THE DHARMA (ROOT)
# ============================================================================


class CityConfig(BaseModel):
    """
    THE DHARMA: Complete Configuration Schema for Agent City

    This is the DNA of the system. If code dies, this resurrects it.
    All parameters are validated at load time - corruption is detected immediately.
    """

    city_name: str = Field(default="Agent City Alpha", min_length=1)
    federation_version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$")
    timestamp_created: Optional[datetime] = Field(default=None)

    governance: GovernanceConfig = Field(default_factory=GovernanceConfig)
    economy: EconomyConfig = Field(default_factory=EconomyConfig)
    agents: AgentParametersConfig = Field(default_factory=AgentParametersConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    integrations: IntegrationsConfig = Field(default_factory=IntegrationsConfig)

    notes: Optional[str] = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    def get_agent_config(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve configuration for a specific agent"""
        return getattr(self.agents, agent_id, None)

    def get_integration_config(self, integration_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve configuration for a specific integration"""
        return getattr(self.integrations, integration_name, None)


# ============================================================================
# CONFIG LOADING FUNCTION
# ============================================================================


def load_config(config_path: str) -> CityConfig:
    """
    Load and validate configuration from YAML file.

    Args:
        config_path: Path to dharma.yaml or matrix.yaml

    Returns:
        Validated CityConfig instance

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config validation fails
    """
    from pathlib import Path

    import yaml

    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_file, "r") as f:
            config_data = yaml.safe_load(f)

        if not config_data:
            raise ValueError("Configuration file is empty")

        # Validate and construct CityConfig
        city_config = CityConfig(**config_data)
        return city_config

    except yaml.YAMLError as e:
        raise ValueError(f"YAML parsing error in {config_path}: {e}")
    except Exception as e:
        raise ValueError(f"Configuration validation failed: {e}")
