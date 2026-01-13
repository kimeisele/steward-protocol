"""City Configuration - Agent City settings from matrix.yaml."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x404a82c2"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class GovernanceConfig:
    """Democracy and authority parameters."""

    voting_threshold: float = 0.5
    quorum_required: float = 0.3
    proposal_cost: int = 5
    proposal_duration_hours: int = 24
    license_revocation_enabled: bool = True
    credit_audit_frequency_hours: int = 6


@dataclass
class EconomyConfig:
    """Credit system parameters."""

    initial_credits: int = 100
    refill_amount: int = 50
    refill_frequency_hours: int = 12
    broadcast_cost: int = 1
    proposal_cost: int = 5
    research_cost: int = 2
    media_cost: int = 1
    vote_reward: int = 0
    verification_reward: int = 1
    total_credit_supply_cap: int = 100000
    inflation_monthly_percent: int = 5


@dataclass
class HeraldConfig:
    """Herald agent configuration."""

    content_style: str = "cyberpunk_professional"
    tone_variation: float = 0.3
    posting_frequency_hours: int = 2
    batch_size: int = 3
    research_enabled: bool = True
    research_frequency_hours: int = 4
    default_search_engine: str = "tavily"
    max_posts_per_day: int = 20
    twitter_enabled: bool = True
    reddit_enabled: bool = True


@dataclass
class ScienceConfig:
    """Science agent configuration."""

    search_provider: str = "tavily"
    max_search_results: int = 5
    search_freshness_days: int = 7
    fact_check_enabled: bool = True
    source_verification_required: bool = True
    anomaly_detection_enabled: bool = True
    pattern_recognition_enabled: bool = True
    searches_per_hour: int = 10
    validation_timeout_seconds: int = 30


@dataclass
class ForumConfig:
    """Forum agent configuration."""

    proposal_min_length: int = 50
    proposal_max_length: int = 5000
    description_required: bool = True
    voting_enabled: bool = True
    anonymous_voting: bool = False
    constitutional_amendments_require_supermajority: bool = True


@dataclass
class CivicConfig:
    """Civic agent configuration."""

    auto_register_new_agents: bool = True
    validation_strict_mode: bool = False
    auto_revoke_zero_credits: bool = True
    revocation_grace_period_hours: int = 0
    ledger_compression_enabled: bool = True
    ledger_backup_frequency_hours: int = 24


@dataclass
class AgentsConfig:
    """All agent configurations."""

    herald: HeraldConfig = field(default_factory=HeraldConfig)
    science: ScienceConfig = field(default_factory=ScienceConfig)
    forum: ForumConfig = field(default_factory=ForumConfig)
    civic: CivicConfig = field(default_factory=CivicConfig)


@dataclass
class MonitoringConfig:
    """Monitoring and logging configuration."""

    health_check_interval_minutes: int = 5
    log_level: str = "INFO"
    log_all_transactions: bool = True
    transaction_log_path: str = "data/logs/transactions.log"
    metrics_collection_enabled: bool = True
    metrics_export_frequency_hours: int = 1


@dataclass
class SecurityConfig:
    """Security configuration."""

    require_signatures: bool = True
    signature_algorithm: str = "ecdsa"
    global_rate_limit_requests_per_minute: int = 100
    per_agent_rate_limit_per_minute: int = 10
    immutable_ledger: bool = True
    enable_access_logs: bool = True


@dataclass
class CityConfig:
    """
    Complete city configuration from matrix.yaml.

    Auto-discovered by SectionLoader → loads from config/matrix.yaml
    """

    # Class-level section identifier for auto-discovery
    section_id = "city"
    # Actual source file (not default city.yaml)
    source_file = "matrix.yaml"

    name: str = "Agent City Alpha"
    federation_version: str = "1.0.0"
    governance: GovernanceConfig = field(default_factory=GovernanceConfig)
    economy: EconomyConfig = field(default_factory=EconomyConfig)
    agents: AgentsConfig = field(default_factory=AgentsConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CityConfig":
        """Create CityConfig from parsed YAML dict."""
        # Governance
        gov_data = data.get("governance", {})
        governance = GovernanceConfig(
            voting_threshold=gov_data.get("voting_threshold", 0.5),
            quorum_required=gov_data.get("quorum_required", 0.3),
            proposal_cost=gov_data.get("proposal_cost", 5),
            proposal_duration_hours=gov_data.get("proposal_duration_hours", 24),
            license_revocation_enabled=gov_data.get("license_revocation_enabled", True),
            credit_audit_frequency_hours=gov_data.get("credit_audit_frequency_hours", 6),
        )

        # Economy
        econ_data = data.get("economy", {})
        economy = EconomyConfig(
            initial_credits=econ_data.get("initial_credits", 100),
            refill_amount=econ_data.get("refill_amount", 50),
            refill_frequency_hours=econ_data.get("refill_frequency_hours", 12),
            broadcast_cost=econ_data.get("broadcast_cost", 1),
            proposal_cost=econ_data.get("proposal_cost", 5),
            research_cost=econ_data.get("research_cost", 2),
            media_cost=econ_data.get("media_cost", 1),
            vote_reward=econ_data.get("vote_reward", 0),
            verification_reward=econ_data.get("verification_reward", 1),
            total_credit_supply_cap=econ_data.get("total_credit_supply_cap", 100000),
            inflation_monthly_percent=econ_data.get("inflation_monthly_percent", 5),
        )

        # Agents
        agents_data = data.get("agents", {})
        herald_data = agents_data.get("herald", {})
        science_data = agents_data.get("science", {})
        forum_data = agents_data.get("forum", {})
        civic_data = agents_data.get("civic", {})

        agents = AgentsConfig(
            herald=HeraldConfig(
                content_style=herald_data.get("content_style", "cyberpunk_professional"),
                tone_variation=herald_data.get("tone_variation", 0.3),
                posting_frequency_hours=herald_data.get("posting_frequency_hours", 2),
                batch_size=herald_data.get("batch_size", 3),
                research_enabled=herald_data.get("research_enabled", True),
                research_frequency_hours=herald_data.get("research_frequency_hours", 4),
                default_search_engine=herald_data.get("default_search_engine", "tavily"),
                max_posts_per_day=herald_data.get("max_posts_per_day", 20),
                twitter_enabled=herald_data.get("twitter_enabled", True),
                reddit_enabled=herald_data.get("reddit_enabled", True),
            ),
            science=ScienceConfig(
                search_provider=science_data.get("search_provider", "tavily"),
                max_search_results=science_data.get("max_search_results", 5),
                search_freshness_days=science_data.get("search_freshness_days", 7),
                fact_check_enabled=science_data.get("fact_check_enabled", True),
                source_verification_required=science_data.get("source_verification_required", True),
                anomaly_detection_enabled=science_data.get("anomaly_detection_enabled", True),
                pattern_recognition_enabled=science_data.get("pattern_recognition_enabled", True),
                searches_per_hour=science_data.get("searches_per_hour", 10),
                validation_timeout_seconds=science_data.get("validation_timeout_seconds", 30),
            ),
            forum=ForumConfig(
                proposal_min_length=forum_data.get("proposal_min_length", 50),
                proposal_max_length=forum_data.get("proposal_max_length", 5000),
                description_required=forum_data.get("description_required", True),
                voting_enabled=forum_data.get("voting_enabled", True),
                anonymous_voting=forum_data.get("anonymous_voting", False),
                constitutional_amendments_require_supermajority=forum_data.get(
                    "constitutional_amendments_require_supermajority", True
                ),
            ),
            civic=CivicConfig(
                auto_register_new_agents=civic_data.get("auto_register_new_agents", True),
                validation_strict_mode=civic_data.get("validation_strict_mode", False),
                auto_revoke_zero_credits=civic_data.get("auto_revoke_zero_credits", True),
                revocation_grace_period_hours=civic_data.get("revocation_grace_period_hours", 0),
                ledger_compression_enabled=civic_data.get("ledger_compression_enabled", True),
                ledger_backup_frequency_hours=civic_data.get("ledger_backup_frequency_hours", 24),
            ),
        )

        # Monitoring
        mon_data = data.get("monitoring", {})
        monitoring = MonitoringConfig(
            health_check_interval_minutes=mon_data.get("health_check_interval_minutes", 5),
            log_level=mon_data.get("log_level", "INFO"),
            log_all_transactions=mon_data.get("log_all_transactions", True),
            transaction_log_path=mon_data.get("transaction_log_path", "data/logs/transactions.log"),
            metrics_collection_enabled=mon_data.get("metrics_collection_enabled", True),
            metrics_export_frequency_hours=mon_data.get("metrics_export_frequency_hours", 1),
        )

        # Security
        sec_data = data.get("security", {})
        security = SecurityConfig(
            require_signatures=sec_data.get("require_signatures", True),
            signature_algorithm=sec_data.get("signature_algorithm", "ecdsa"),
            global_rate_limit_requests_per_minute=sec_data.get("global_rate_limit_requests_per_minute", 100),
            per_agent_rate_limit_per_minute=sec_data.get("per_agent_rate_limit_per_minute", 10),
            immutable_ledger=sec_data.get("immutable_ledger", True),
            enable_access_logs=sec_data.get("enable_access_logs", True),
        )

        return cls(
            name=data.get("city_name", "Agent City Alpha"),
            federation_version=data.get("federation_version", "1.0.0"),
            governance=governance,
            economy=economy,
            agents=agents,
            monitoring=monitoring,
            security=security,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize back to YAML-compatible dict."""
        return {
            "city_name": self.name,
            "federation_version": self.federation_version,
            "governance": {
                "voting_threshold": self.governance.voting_threshold,
                "quorum_required": self.governance.quorum_required,
                "proposal_cost": self.governance.proposal_cost,
                "proposal_duration_hours": self.governance.proposal_duration_hours,
                "license_revocation_enabled": self.governance.license_revocation_enabled,
                "credit_audit_frequency_hours": self.governance.credit_audit_frequency_hours,
            },
            "economy": {
                "initial_credits": self.economy.initial_credits,
                "refill_amount": self.economy.refill_amount,
                "refill_frequency_hours": self.economy.refill_frequency_hours,
                "broadcast_cost": self.economy.broadcast_cost,
                "proposal_cost": self.economy.proposal_cost,
                "research_cost": self.economy.research_cost,
                "media_cost": self.economy.media_cost,
                "vote_reward": self.economy.vote_reward,
                "verification_reward": self.economy.verification_reward,
                "total_credit_supply_cap": self.economy.total_credit_supply_cap,
                "inflation_monthly_percent": self.economy.inflation_monthly_percent,
            },
            "agents": {
                "herald": {
                    "content_style": self.agents.herald.content_style,
                    "tone_variation": self.agents.herald.tone_variation,
                    "posting_frequency_hours": self.agents.herald.posting_frequency_hours,
                    "batch_size": self.agents.herald.batch_size,
                    "research_enabled": self.agents.herald.research_enabled,
                    "research_frequency_hours": self.agents.herald.research_frequency_hours,
                    "default_search_engine": self.agents.herald.default_search_engine,
                    "max_posts_per_day": self.agents.herald.max_posts_per_day,
                    "twitter_enabled": self.agents.herald.twitter_enabled,
                    "reddit_enabled": self.agents.herald.reddit_enabled,
                },
                "science": {
                    "search_provider": self.agents.science.search_provider,
                    "max_search_results": self.agents.science.max_search_results,
                    "search_freshness_days": self.agents.science.search_freshness_days,
                    "fact_check_enabled": self.agents.science.fact_check_enabled,
                    "source_verification_required": self.agents.science.source_verification_required,
                    "anomaly_detection_enabled": self.agents.science.anomaly_detection_enabled,
                    "pattern_recognition_enabled": self.agents.science.pattern_recognition_enabled,
                    "searches_per_hour": self.agents.science.searches_per_hour,
                    "validation_timeout_seconds": self.agents.science.validation_timeout_seconds,
                },
                "forum": {
                    "proposal_min_length": self.agents.forum.proposal_min_length,
                    "proposal_max_length": self.agents.forum.proposal_max_length,
                    "description_required": self.agents.forum.description_required,
                    "voting_enabled": self.agents.forum.voting_enabled,
                    "anonymous_voting": self.agents.forum.anonymous_voting,
                    "constitutional_amendments_require_supermajority": self.agents.forum.constitutional_amendments_require_supermajority,
                },
                "civic": {
                    "auto_register_new_agents": self.agents.civic.auto_register_new_agents,
                    "validation_strict_mode": self.agents.civic.validation_strict_mode,
                    "auto_revoke_zero_credits": self.agents.civic.auto_revoke_zero_credits,
                    "revocation_grace_period_hours": self.agents.civic.revocation_grace_period_hours,
                    "ledger_compression_enabled": self.agents.civic.ledger_compression_enabled,
                    "ledger_backup_frequency_hours": self.agents.civic.ledger_backup_frequency_hours,
                },
            },
            "monitoring": {
                "health_check_interval_minutes": self.monitoring.health_check_interval_minutes,
                "log_level": self.monitoring.log_level,
                "log_all_transactions": self.monitoring.log_all_transactions,
                "transaction_log_path": self.monitoring.transaction_log_path,
                "metrics_collection_enabled": self.monitoring.metrics_collection_enabled,
                "metrics_export_frequency_hours": self.monitoring.metrics_export_frequency_hours,
            },
            "security": {
                "require_signatures": self.security.require_signatures,
                "signature_algorithm": self.security.signature_algorithm,
                "global_rate_limit_requests_per_minute": self.security.global_rate_limit_requests_per_minute,
                "per_agent_rate_limit_per_minute": self.security.per_agent_rate_limit_per_minute,
                "immutable_ledger": self.security.immutable_ledger,
                "enable_access_logs": self.security.enable_access_logs,
            },
        }
