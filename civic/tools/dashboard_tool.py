#!/usr/bin/env python3
"""
Agent City Operations Dashboard Generator

Reads the configuration (matrix.yaml) and ledger (transaction history)
and generates OPERATIONS.md - a human-readable snapshot of the city's current state.

Philosophy:
"The dashboard is the human interface to governance. It shows:
- What the city is configured to do (matrix.yaml)
- What the city has actually done (ledger)
- What the city is about to do (proposals)
This is the 'pulse' of Agent City."
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger("DASHBOARD")


@dataclass
class DashboardMetrics:
    """Metrics snapshot for the city."""
    total_transactions: int
    unique_agents: int
    total_credits_allocated: int
    total_credits_deducted: int
    top_spender: Optional[Dict[str, Any]]
    top_agent: Optional[Dict[str, Any]]
    most_recent_event: Optional[Dict[str, Any]]


class DashboardGenerator:
    """
    Generates the OPERATIONS.md dashboard from matrix.yaml and ledger.
    """

    def __init__(self, repo_root: str = "."):
        """
        Initialize dashboard generator.

        Args:
            repo_root: Root directory of steward-protocol repo
        """
        self.repo_root = Path(repo_root)
        self.matrix_path = self.repo_root / "config" / "matrix.yaml"
        self.ledger_path = self.repo_root / "data" / "ledger" / "audit_trail.jsonl"
        self.output_path = self.repo_root / "OPERATIONS.md"

        self.matrix = self._load_matrix()
        self.ledger_entries = self._load_ledger()

        logger.info(f"Dashboard initialized: {len(self.ledger_entries)} ledger entries")

    def _load_matrix(self) -> Dict[str, Any]:
        """Load configuration from matrix.yaml."""
        if not self.matrix_path.exists():
            logger.warning(f"matrix.yaml not found: {self.matrix_path}")
            return {}

        try:
            with open(self.matrix_path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Error loading matrix.yaml: {e}")
            return {}

    def _load_ledger(self) -> List[Dict[str, Any]]:
        """Load ledger entries from JSONL file."""
        if not self.ledger_path.exists():
            logger.warning(f"Ledger not found: {self.ledger_path}")
            return []

        entries = []
        try:
            with open(self.ledger_path, "r") as f:
                for line in f:
                    if line.strip():
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            logger.warning(f"Skipping invalid ledger entry: {e}")
        except Exception as e:
            logger.error(f"Error loading ledger: {e}")

        return entries

    def compute_metrics(self) -> DashboardMetrics:
        """Compute key metrics from ledger."""
        if not self.ledger_entries:
            return DashboardMetrics(
                total_transactions=0,
                unique_agents=0,
                total_credits_allocated=0,
                total_credits_deducted=0,
                top_spender=None,
                top_agent=None,
                most_recent_event=None,
            )

        # Aggregate statistics
        agents = {}
        total_allocated = 0
        total_deducted = 0

        for entry in self.ledger_entries:
            agent = entry.get("agent_name", "unknown")
            operation = entry.get("operation", "")
            amount = entry.get("amount", 0)

            # Track per-agent statistics
            if agent not in agents:
                agents[agent] = {
                    "agent": agent,
                    "balance": 0,
                    "allocated": 0,
                    "deducted": 0,
                    "transactions": 0,
                }

            agents[agent]["balance"] = entry.get("balance_after", 0)
            agents[agent]["transactions"] += 1

            if operation == "allocate":
                agents[agent]["allocated"] += amount
                total_allocated += amount
            elif operation == "deduct":
                agents[agent]["deducted"] += amount
                total_deducted += amount

        # Find top spender and agent
        top_spender = max(
            (a for a in agents.values() if a["deducted"] > 0),
            key=lambda x: x["deducted"],
            default=None,
        )
        top_agent = max(
            agents.values(),
            key=lambda x: x["balance"],
            default=None,
        )

        return DashboardMetrics(
            total_transactions=len(self.ledger_entries),
            unique_agents=len(agents),
            total_credits_allocated=total_allocated,
            total_credits_deducted=total_deducted,
            top_spender=top_spender,
            top_agent=top_agent,
            most_recent_event=self.ledger_entries[-1] if self.ledger_entries else None,
        )

    def get_city_status(self) -> str:
        """Determine city health status based on metrics."""
        if not self.ledger_entries:
            return "⚫ GENESIS (No activity yet)"

        metrics = self.compute_metrics()

        # Determine status based on activity
        if metrics.total_transactions < 10:
            return "🟡 INITIALIZING (Early stage)"
        elif metrics.total_credits_deducted == 0:
            return "🟠 IDLE (Credits allocated, no spending)"
        elif metrics.total_credits_allocated > metrics.total_credits_deducted * 2:
            return "🟢 HEALTHY (Good credit reserve)"
        else:
            return "🔴 CRITICAL (Low credit reserves)"

    def generate_operations_md(self) -> str:
        """Generate OPERATIONS.md content."""
        city_name = self.matrix.get("city_name", "Agent City")
        timestamp = datetime.now().isoformat()
        metrics = self.compute_metrics()

        # Build markdown
        md_lines = []

        # Header
        md_lines.append(f"# 📊 {city_name} - Operations Dashboard")
        md_lines.append("")
        md_lines.append(f"**Generated:** {timestamp}")
        md_lines.append(f"**Status:** {self.get_city_status()}")
        md_lines.append("")

        # City Status Section
        md_lines.append("## 🏙️ City Overview")
        md_lines.append("")
        md_lines.append(f"| Metric | Value |")
        md_lines.append("|--------|-------|")
        md_lines.append(f"| Total Transactions | {metrics.total_transactions} |")
        md_lines.append(f"| Unique Agents | {metrics.unique_agents} |")
        md_lines.append(f"| Credits Allocated | {metrics.total_credits_allocated} |")
        md_lines.append(f"| Credits Spent | {metrics.total_credits_deducted} |")
        if metrics.total_credits_allocated > 0:
            reserve = metrics.total_credits_allocated - metrics.total_credits_deducted
            reserve_pct = (reserve / metrics.total_credits_allocated) * 100
            md_lines.append(f"| Reserve | {reserve} ({reserve_pct:.1f}%) |")
        md_lines.append("")

        # Agent Standings
        if self.ledger_entries:
            md_lines.append("## 🤖 Agent Standings")
            md_lines.append("")

            if metrics.top_agent:
                md_lines.append(f"**Wealthiest Agent:** {metrics.top_agent['agent']} ({metrics.top_agent['balance']} credits)")
            if metrics.top_spender:
                md_lines.append(f"**Top Spender:** {metrics.top_spender['agent']} ({metrics.top_spender['deducted']} credits spent)")
            md_lines.append("")

        # Configuration Status
        md_lines.append("## ⚙️ Configuration (matrix.yaml)")
        md_lines.append("")

        # Governance
        if "governance" in self.matrix:
            gov = self.matrix["governance"]
            md_lines.append("### Governance")
            md_lines.append(f"- Voting Threshold: {gov.get('voting_threshold', 'N/A')} (50% majority required)")
            md_lines.append(f"- Quorum Required: {gov.get('quorum_required', 'N/A')} (30% must participate)")
            md_lines.append(f"- Proposal Cost: {gov.get('proposal_cost', 'N/A')} credits")
            md_lines.append("")

        # Economy
        if "economy" in self.matrix:
            econ = self.matrix["economy"]
            md_lines.append("### Economy")
            md_lines.append(f"- Initial Credits per Agent: {econ.get('initial_credits', 'N/A')}")
            md_lines.append(f"- Broadcast Cost: {econ.get('broadcast_cost', 'N/A')} credits")
            md_lines.append(f"- Research Cost: {econ.get('research_cost', 'N/A')} credits")
            md_lines.append(f"- Credit Supply Cap: {econ.get('total_credit_supply_cap', 'N/A')}")
            md_lines.append("")

        # Agent Parameters
        if "agents" in self.matrix:
            md_lines.append("### Active Agents")
            agents_config = self.matrix["agents"]
            for agent_name in ["herald", "science", "forum", "civic"]:
                if agent_name in agents_config:
                    config = agents_config[agent_name]
                    emoji_map = {
                        "herald": "📢",
                        "science": "🔬",
                        "forum": "💬",
                        "civic": "🏛️",
                    }
                    emoji = emoji_map.get(agent_name, "🤖")
                    md_lines.append(f"- {emoji} **{agent_name.upper()}** - Active")
            md_lines.append("")

        # Recent Activity
        if self.ledger_entries:
            md_lines.append("## 📜 Recent Activity")
            md_lines.append("")
            md_lines.append("Last 5 transactions:")
            md_lines.append("")
            for entry in self.ledger_entries[-5:]:
                timestamp = entry.get("timestamp", "")[:10]  # Just date
                agent = entry.get("agent_name", "?")
                op = entry.get("operation", "?")
                amount = entry.get("amount", 0)
                reason = entry.get("reason", "")
                md_lines.append(
                    f"- [{timestamp}] **{agent}** {op} {amount} credits - {reason}"
                )
            md_lines.append("")

        # Ledger Health
        if self.ledger_entries:
            md_lines.append("## 🔍 Ledger Health")
            md_lines.append("")
            md_lines.append(f"- Total Entries: {len(self.ledger_entries)}")
            md_lines.append(f"- First Entry: {self.ledger_entries[0].get('timestamp', 'N/A')}")
            md_lines.append(f"- Last Entry: {self.ledger_entries[-1].get('timestamp', 'N/A')}")
            md_lines.append("")

        # Policy Recommendations
        md_lines.append("## 💡 Policy Notes")
        md_lines.append("")
        md_lines.append("Edit `config/matrix.yaml` to adjust:")
        md_lines.append("- Agent behavior parameters (posting frequency, research, etc.)")
        md_lines.append("- Economic settings (costs, rewards, inflation)")
        md_lines.append("- Governance thresholds (voting majority, quorum)")
        md_lines.append("")
        md_lines.append("Then restart Agent City to apply changes.")
        md_lines.append("")

        # Footer
        md_lines.append("---")
        md_lines.append("*Dashboard generated by Agent City Operations System*")
        md_lines.append("")

        return "\n".join(md_lines)

    def write_dashboard(self) -> Path:
        """Write dashboard to OPERATIONS.md."""
        content = self.generate_operations_md()

        try:
            with open(self.output_path, "w") as f:
                f.write(content)
            logger.info(f"✅ Dashboard written to {self.output_path}")
            return self.output_path
        except Exception as e:
            logger.error(f"Error writing dashboard: {e}")
            raise


def main():
    """Generate dashboard from CLI."""
    import sys

    repo_root = sys.argv[1] if len(sys.argv) > 1 else "."

    try:
        dashboard = DashboardGenerator(repo_root)
        output = dashboard.write_dashboard()
        print(f"✅ Operations dashboard generated: {output}")
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
