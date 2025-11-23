#!/usr/bin/env python3
"""
ARCHIVIST Shim
Execution interface for ARCHIVIST cartridge
"""

import logging
import sys
import os
import argparse
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('ARCHIVIST_SHIM')

# Add cartridge to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cartridge'))

from archivist_cartridge import Archivist


class ArchivistShim:
    """Interface to execute ARCHIVIST cartridge"""

    def __init__(self):
        self.archivist = Archivist()
        logger.info('🗃️  ARCHIVIST Shim initialized')

    def run_archival(self):
        """Execute archival cycle"""
        logger.info('=' * 70)
        logger.info('🗃️  ARCHIVIST: Archival Agent')
        logger.info('=' * 70)

        success = self.archivist.run_archival_cycle()

        if success:
            logger.info('\n✅ ARCHIVAL SUCCESSFUL')
            return 0
        else:
            logger.info('\n❌ ARCHIVAL FAILED')
            return 1

    def show_ledger(self):
        """Display current ledger status"""
        logger.info('=' * 70)
        logger.info('📖 LEDGER STATUS')
        logger.info('=' * 70)

        summary = self.archivist.ledger.get_ledger_summary()
        logger.info(f"📚 Total entries: {summary['total_entries']}")
        logger.info(f"✅ Verified count: {summary['verified_count']}")
        logger.info(f"❌ Rejected count: {summary['rejected_count']}")
        logger.info(f"📄 Ledger file: {summary['ledger_file']}")

        # Display ledger contents
        try:
            with open(summary['ledger_file'], 'r') as f:
                ledger_data = json.load(f)
                logger.info('\n📋 Recent entries:')
                entries = ledger_data['chain_of_trust']['entries']
                for entry in entries[-3:]:  # Show last 3
                    logger.info(f"  - [{entry['sequence_number']}] {entry['broadcast_id']}")
        except Exception as e:
            logger.warning(f'Could not read ledger: {e}')

        return 0


def main():
    parser = argparse.ArgumentParser(description='ARCHIVIST Agent Execution')
    parser.add_argument(
        '--action',
        choices=['archive', 'ledger'],
        default='archive',
        help='Action to perform'
    )

    args = parser.parse_args()
    shim = ArchivistShim()

    if args.action == 'archive':
        return shim.run_archival()
    elif args.action == 'ledger':
        return shim.show_ledger()

    return 0


if __name__ == '__main__':
    sys.exit(main())
