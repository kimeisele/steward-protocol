"""
NAGA Cartridge - The Invisible Guardian.

"Wir sind selbst NAGAs - Hüter des Schatzes dieses AOS."

This cartridge provides Agent City access to the NAGA Federation:
- Sesha: Data foundation, gossip sync, Ledger access
- Vasuki: Network bridge, serialization, external boundary
- Takshaka: Security guardian, toxicity detection

Tools:
- naga.status: Federation health status
- naga.scan: Toxicity scanning
- naga.detect: Drift and violation detection
- naga.audit: Ledger audit trail
"""

from vibe_core.cartridges.system.naga.cartridge_main import NagaCartridge

__all__ = ["NagaCartridge"]
