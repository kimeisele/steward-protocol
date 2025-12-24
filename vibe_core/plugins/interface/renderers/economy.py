"""
ECONOMY.md Renderer - Resource Meters

OPUS-014: Token usage, credits, costs transparency.
OPUS-151: This file IS the economic reality.

Architecture Pattern:
- Uses render_sections() from BaseRenderer (config-driven)
- Registers data sources for treasury and credits
- NO hardcoded generate_content() - sections come from interface.yaml
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel


class EconomyRenderer(BaseRenderer):
    """Manifests the economic reality.

    Components:
    - Treasury: Token budgets and usage
    - Credits: Per-agent credit allocation
    - Transactions: Recent economic events
    """

    def __init__(self, kernel: "RealVibeKernel"):
        super().__init__(kernel)
        self._register_data_sources()

    @property
    def name(self) -> str:
        return "economy"

    @property
    def output_file(self) -> str:
        return "ECONOMY.md"

    @property
    def doc_type(self):
        """Document type for IO service."""
        from vibe_core.io_service import DocumentType

        return DocumentType.READONLY

    def render(self) -> None:
        """Render ECONOMY.md using config-driven sections.

        This is the CORRECT pattern - uses interface.yaml sections.
        """
        config = self.get_config()
        if config and config.sections:
            content = self.render_sections()
            self.merge_and_write(content)
        else:
            # Fallback if no sections defined
            content = self.generate_content()
            if content:
                self.merge_and_write(content)

    def generate_content(self) -> Optional[str]:
        """Fallback content generation if config sections not defined."""
        lines = [
            "# ECONOMY",
            "",
            "> Resource Meters & Token Transparency",
            "> OPUS-014: Every token visible",
            "",
        ]

        # Treasury
        lines.append("## Treasury")
        lines.append("")
        treasury = self._get_treasury()
        lines.extend(self._format_treasury_table(treasury))
        lines.append("")

        # Agent Credits
        lines.append("## Agent Credits")
        lines.append("")
        credits = self._get_agent_credits()
        lines.extend(self._format_credits_table(credits))
        lines.append("")

        # Recent Transactions
        lines.append("## Recent Transactions")
        lines.append("")
        transactions = self._get_transactions()
        lines.extend(self._format_transactions_table(transactions))

        return "\n".join(lines)

    # =========================================================================
    # DATA SOURCE REGISTRATION
    # =========================================================================

    def _register_data_sources(self) -> None:
        """Register data sources for section-based rendering."""
        self.register_data_source("economy.treasury", self._get_treasury)
        self.register_data_source("economy.credits", self._get_agent_credits)
        self.register_data_source("economy.transactions", self._get_transactions)
        self.register_data_source("economy.summary", self._get_economy_summary)

    # =========================================================================
    # DATA RETRIEVAL
    # =========================================================================

    def _get_economy_config(self) -> Dict[str, Any]:
        """Load economy config from config/economy.yaml if exists."""
        try:
            import yaml

            config_path = Path("config/economy.yaml")
            if config_path.exists():
                return yaml.safe_load(config_path.read_text()) or {}
        except Exception as e:
            logger.debug(f"Could not load economy config: {e}")
        return {}

    def _get_governance_plugin(self) -> Optional[Any]:
        """Get VedicGovernance plugin if loaded."""
        if hasattr(self.kernel, "get_plugin"):
            try:
                return self.kernel.get_plugin("vedic_governance")
            except Exception as e:
                logger.debug(f"Could not get vedic_governance plugin: {e}")
        return None

    def _get_ledger(self) -> Optional[Any]:
        """Get ledger from Prakriti."""
        if hasattr(self.kernel, "prakriti") and hasattr(self.kernel.prakriti, "ledger"):
            return self.kernel.prakriti.ledger
        return None

    def _get_treasury(self) -> List[Dict[str, Any]]:
        """Get treasury/budget information."""
        config = self._get_economy_config()
        treasury_config = config.get("treasury", {})

        treasury = []

        # OpenAI tokens
        openai = treasury_config.get("openai_tokens", {})
        treasury.append(
            {
                "Resource": "OpenAI Tokens",
                "Budget": openai.get("budget", 100000),
                "Used": self._get_token_usage("openai"),
                "Remaining": openai.get("budget", 100000) - self._get_token_usage("openai"),
            }
        )

        # API calls
        api = treasury_config.get("api_calls", {})
        treasury.append(
            {
                "Resource": "API Calls",
                "Budget": api.get("budget", 1000),
                "Used": self._get_api_calls_count(),
                "Remaining": api.get("budget", 1000) - self._get_api_calls_count(),
            }
        )

        # Local LLM (unlimited)
        treasury.append(
            {
                "Resource": "Local LLM",
                "Budget": "unlimited",
                "Used": self._get_local_llm_count(),
                "Remaining": "unlimited",
            }
        )

        return treasury

    def _get_agent_credits(self) -> List[Dict[str, Any]]:
        """Get per-agent credit allocation."""
        governance = self._get_governance_plugin()
        credits = []

        if governance and hasattr(governance, "get_credits"):
            try:
                agent_credits = governance.get_credits()
                for agent_id, credit_info in agent_credits.items():
                    credits.append(
                        {
                            "Agent": agent_id,
                            "Credits": credit_info.get("credits", 0),
                            "Spent Today": credit_info.get("spent_today", 0),
                            "Status": self._credit_status(credit_info),
                        }
                    )
            except Exception as e:
                logger.debug(f"Could not get agent credits from governance: {e}")

        if not credits:
            # Default placeholder
            credits.append(
                {
                    "Agent": "system",
                    "Credits": 10000,
                    "Spent Today": 0,
                    "Status": "active",
                }
            )

        return credits

    def _get_transactions(self) -> List[Dict[str, Any]]:
        """Get recent economic transactions from ledger."""
        ledger = self._get_ledger()
        transactions = []

        if ledger and hasattr(ledger, "get_events"):
            try:
                events = ledger.get_events(event_type="token_usage", limit=10)
                for event in events:
                    transactions.append(
                        {
                            "Time": event.get("timestamp", ""),
                            "Agent": event.get("agent_id", "unknown"),
                            "Action": event.get("action", "query"),
                            "Cost": event.get("tokens", 0),
                        }
                    )
            except Exception as e:
                logger.debug(f"Operation failed in economy renderer: {e}")

        if not transactions:
            transactions.append(
                {
                    "Time": "-",
                    "Agent": "-",
                    "Action": "No transactions recorded",
                    "Cost": "-",
                }
            )

        return transactions

    def _get_economy_summary(self) -> Dict[str, Any]:
        """Get economy summary."""
        treasury = self._get_treasury()
        total_used = sum(t.get("Used", 0) for t in treasury if isinstance(t.get("Used"), (int, float)))
        return {
            "total_resources": len(treasury),
            "total_used": total_used,
            "status": "healthy",
        }

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _get_token_usage(self, provider: str) -> int:
        """Get token usage for a provider."""
        ledger = self._get_ledger()
        if ledger and hasattr(ledger, "get_metric"):
            try:
                return ledger.get_metric(f"{provider}_tokens_used") or 0
            except Exception as e:
                logger.debug(f"Operation failed in economy renderer: {e}")
        return 0

    def _get_api_calls_count(self) -> int:
        """Get API call count."""
        ledger = self._get_ledger()
        if ledger and hasattr(ledger, "get_metric"):
            try:
                return ledger.get_metric("api_calls_count") or 0
            except Exception as e:
                logger.debug(f"Operation failed in economy renderer: {e}")
        return 0

    def _get_local_llm_count(self) -> int:
        """Get local LLM query count."""
        ledger = self._get_ledger()
        if ledger and hasattr(ledger, "get_metric"):
            try:
                return ledger.get_metric("local_llm_queries") or 0
            except Exception as e:
                logger.debug(f"Operation failed in economy renderer: {e}")
        return 0

    def _credit_status(self, credit_info: Dict[str, Any]) -> str:
        """Determine credit status."""
        credits = credit_info.get("credits", 0)
        spent = credit_info.get("spent_today", 0)
        if credits <= 0:
            return "exhausted"
        elif spent > credits * 0.8:
            return "low"
        return "active"

    # =========================================================================
    # FORMATTING
    # =========================================================================

    def _format_treasury_table(self, treasury: List[Dict[str, Any]]) -> List[str]:
        """Format treasury as table."""
        if not treasury:
            return ["_No treasury data_"]

        lines = ["| Resource | Used | Budget | Remaining |", "| --- | --- | --- | --- |"]
        for row in treasury:
            lines.append(f"| {row['Resource']} | {row['Used']} | {row['Budget']} | {row['Remaining']} |")
        return lines

    def _format_credits_table(self, credits: List[Dict[str, Any]]) -> List[str]:
        """Format agent credits as table."""
        if not credits:
            return ["_No credit data_"]

        lines = ["| Agent | Credits | Spent Today | Status |", "| --- | --- | --- | --- |"]
        for row in credits:
            lines.append(f"| {row['Agent']} | {row['Credits']} | {row['Spent Today']} | {row['Status']} |")
        return lines

    def _format_transactions_table(self, transactions: List[Dict[str, Any]]) -> List[str]:
        """Format transactions as table."""
        if not transactions:
            return ["_No transactions_"]

        lines = ["| Time | Agent | Action | Cost |", "| --- | --- | --- | --- |"]
        for row in transactions:
            lines.append(f"| {row['Time']} | {row['Agent']} | {row['Action']} | {row['Cost']} |")
        return lines


def create_renderer(kernel: "RealVibeKernel", config: Dict[str, Any]) -> EconomyRenderer:
    """Factory function for InterfacePlugin."""
    return EconomyRenderer(kernel)
