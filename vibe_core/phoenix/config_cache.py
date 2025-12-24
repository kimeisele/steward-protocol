"""Cache parsed config to avoid YAML parsing on every boot."""
import hashlib
import pickle
from pathlib import Path

CACHE_PATH = Path(".vibe/cache/config.pkl")
HASH_PATH = Path(".vibe/cache/config.hash")

def get_yaml_hash(config_dir: Path) -> str:
    """Hash all YAML files for cache invalidation."""
    content = ""
    for f in sorted(config_dir.glob("**/*.yaml")):
        content += f.read_text()
    return hashlib.md5(content.encode()).hexdigest()

def get_cached_or_parse(config_dir: Path, parse_fn):
    """Return cached config or parse fresh."""
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

    current_hash = get_yaml_hash(config_dir)

    if HASH_PATH.exists() and CACHE_PATH.exists():
        if HASH_PATH.read_text() == current_hash:
            try:
                return pickle.loads(CACHE_PATH.read_bytes())
            except Exception:
                pass

    config = parse_fn()
    CACHE_PATH.write_bytes(pickle.dumps(config))
    HASH_PATH.write_text(current_hash)
    return config