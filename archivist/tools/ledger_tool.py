"""
ARCHIVIST Ledger Tool
Writes and manages the Chain of Trust ledger in JSON format
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger('ARCHIVIST_LEDGER')


class LedgerTool:
    """Manages the immutable ledger of verified broadcasts"""

    def __init__(self, ledger_path: str = 'archive/ledger.json'):
        self.logger = logger
        self.ledger_path = ledger_path
        self.logger.info(f'📚 Ledger Tool initialized: {ledger_path}')
        self._ensure_ledger_exists()

    def _ensure_ledger_exists(self):
        """Ensure ledger file exists with proper structure"""
        os.makedirs(os.path.dirname(self.ledger_path) or '.', exist_ok=True)

        if not os.path.exists(self.ledger_path):
            initial_ledger = {
                'chain_of_trust': {
                    'genesis_block': {
                        'timestamp': datetime.now().isoformat(),
                        'message': 'ARCHIVIST Chain of Trust initialized',
                        'agent': 'ARCHIVIST_Agent',
                        'version': '1.0'
                    },
                    'entries': []
                },
                'statistics': {
                    'total_verified': 0,
                    'total_rejected': 0,
                    'verification_start': datetime.now().isoformat()
                }
            }
            self._write_ledger(initial_ledger)
            self.logger.info('✅ New ledger created')

    def write_entry(self, broadcast: Dict[str, Any], verification_proof: Dict[str, Any]) -> bool:
        """
        Write verified broadcast entry to ledger

        Args:
            broadcast: The original HERALD broadcast
            verification_proof: The verification proof from ARCHIVIST

        Returns:
            Success status
        """
        self.logger.info(f'📝 Writing entry for broadcast: {broadcast.get("id")}')

        try:
            ledger = self._read_ledger()

            entry = {
                'broadcast_id': broadcast.get('id'),
                'broadcast_content': broadcast.get('content'),
                'broadcast_author': broadcast.get('author'),
                'broadcast_timestamp': broadcast.get('timestamp'),
                'original_signature': broadcast.get('signature'),
                'verification_proof': verification_proof,
                'archivist_signature': self._generate_archivist_signature(broadcast, verification_proof),
                'entry_timestamp': datetime.now().isoformat(),
                'sequence_number': len(ledger['chain_of_trust']['entries']) + 1
            }

            ledger['chain_of_trust']['entries'].append(entry)
            ledger['statistics']['total_verified'] += 1

            self._write_ledger(ledger)
            self.logger.info(f'✅ Entry written to ledger')
            return True

        except Exception as e:
            self.logger.error(f'❌ Failed to write entry: {e}')
            return False

    def _generate_archivist_signature(self, broadcast: Dict[str, Any], proof: Dict[str, Any]) -> str:
        """Generate ARCHIVIST's signature over the verification proof"""
        import hashlib
        combined = json.dumps({
            'broadcast': broadcast,
            'proof': proof
        }, sort_keys=True)
        hash_obj = hashlib.sha256(combined.encode())
        return f'ARCHIVIST_SIG_{hash_obj.hexdigest()[:16].upper()}'

    def _read_ledger(self) -> Dict[str, Any]:
        """Read current ledger state"""
        with open(self.ledger_path, 'r') as f:
            return json.load(f)

    def _write_ledger(self, ledger: Dict[str, Any]):
        """Write ledger to file"""
        with open(self.ledger_path, 'w') as f:
            json.dump(ledger, f, indent=2)

    def get_ledger_summary(self) -> Dict[str, Any]:
        """Get summary of ledger statistics"""
        ledger = self._read_ledger()
        return {
            'total_entries': len(ledger['chain_of_trust']['entries']),
            'verified_count': ledger['statistics']['total_verified'],
            'rejected_count': ledger['statistics']['total_rejected'],
            'ledger_file': self.ledger_path
        }
