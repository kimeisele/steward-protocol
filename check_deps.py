import sys

print(f"Python: {sys.version}")
try:
    import aiofiles

    print("✅ aiofiles found")
except ImportError as e:
    print(f"❌ aiofiles MISSING: {e}")

try:
    import ecdsa

    print("✅ ecdsa found")
except ImportError as e:
    print(f"❌ ecdsa MISSING: {e}")

try:
    from fastapi.staticfiles import StaticFiles

    print("✅ FastAPI StaticFiles importable")
except ImportError as e:
    print(f"❌ FastAPI StaticFiles import failed: {e}")
