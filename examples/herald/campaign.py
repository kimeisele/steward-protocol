import os
import sys
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

# Pfad-Hack für Imports im CI/CD
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from examples.herald.publisher import TwitterPublisher

def run_campaign():
    print("🦅 PHOENIX: Starting HERALD Campaign...")

    # 1. Init
    try:
        publisher = TwitterPublisher()
    except Exception as e:
        print(f"❌ CRITICAL: Publisher init failed: {e}")
        sys.exit(1)

    # 2. Diagnostic (Simpel & Robust)
    if publisher.client:
        print("✅ DIAGNOSTIC: Client initialized successfully.")
    else:
        print("⚠️ DIAGNOSTIC: Client is None. Check GitHub Secrets!")
        # Wir lassen es weiterlaufen, um zu sehen was passiert

    # 3. Execution
    content = "Steward Protocol HERALD is live! 🦅 #BuildInPublic"
    print(f"🚀 Publishing: {content}")

    success = publisher.publish(content)

    if success:
        print("✅ SUCCESS: Published.")
        sys.exit(0)
    else:
        print("❌ FAILURE: Publishing failed.")
        # Wir setzen exit 0, damit der Workflow grün wird, solange der Code nicht crasht.
        # Wenn du rot willst bei Fail, mach sys.exit(1)
        sys.exit(1)

if __name__ == "__main__":
    run_campaign()
