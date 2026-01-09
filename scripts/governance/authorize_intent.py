import os
import sys

sys.path.append(os.getcwd())

import sys

from vibe_core.security import SecurityIntentManager


def main():
    if len(sys.argv) < 3:
        print("Usage: python authorize_intent.py <intent_id> <sovereign_key>")
        sys.exit(1)

    intent_id = sys.argv[1]
    key = sys.argv[2]

    manager = SecurityIntentManager()

    # 1. Authorize
    if manager.authorize_intent(intent_id, key):
        print(f"✅ Intent {intent_id} AUTHORIZED.")

        # 2. Execute
        if manager.execute_intent(intent_id):
            print(f"🚀 Intent {intent_id} EXECUTED. Hashes updated.")
            sys.exit(0)
        else:
            print("❌ Execution failed.")
            sys.exit(1)
    else:
        print("❌ Authorization failed. Intent not found?")
        sys.exit(1)


if __name__ == "__main__":
    main()
