"""
Schema Validation for Manifests.

Uses jsonschema for validation. Pre-flight check before loading ANY item.

Usage:
    from vibe_core.loaders.schema import validate_manifest, validate_manifest_file

    # Validate a dict
    errors = validate_manifest({"type": "plugin", "id": "my_plugin", "name": "My Plugin"})
    if errors:
        print(f"Invalid manifest: {errors}")

    # Validate a file
    errors = validate_manifest_file(Path("plugins/my_plugin/manifest.json"))
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0xc0dd2713"  # GenesisByte: parampara % 37 == 0

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("UNIFIED.SCHEMA")

# Try to import jsonschema, fall back to basic validation if not available
try:
    from jsonschema import Draft7Validator

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    Draft7Validator = None  # type: ignore
    logger.warning("jsonschema not installed. Using basic validation only.")


# Load schema at module level
_SCHEMA: Optional[Dict[str, Any]] = None
_SCHEMA_PATH = Path(__file__).parent / "manifest_schema.json"


def _get_schema() -> Dict[str, Any]:
    """Load and cache the manifest schema."""
    global _SCHEMA
    if _SCHEMA is None:
        if _SCHEMA_PATH.exists():
            with open(_SCHEMA_PATH, "r") as f:
                _SCHEMA = json.load(f)
        else:
            logger.error(f"Schema file not found: {_SCHEMA_PATH}")
            _SCHEMA = {}
    return _SCHEMA


def validate_manifest(manifest: Dict[str, Any]) -> List[str]:
    """
    Validate a manifest dict against the schema.

    Args:
        manifest: The manifest dictionary to validate

    Returns:
        List of error messages (empty if valid)
    """
    errors: List[str] = []

    # Basic required field validation (always runs)
    if "type" not in manifest:
        errors.append("Missing required field: 'type'")
    if "id" not in manifest and "name" not in manifest:
        errors.append("Missing required field: 'id' or 'name'")

    # ID format validation
    item_id = manifest.get("id", "")
    if item_id:
        import re

        if not re.match(r"^[a-z][a-z0-9_]*$", item_id):
            errors.append(f"Invalid id format: '{item_id}' (must be snake_case, start with letter)")

    # Version format validation
    version = manifest.get("version", "")
    if version:
        import re

        if not re.match(r"^[0-9]+\.[0-9]+\.[0-9]+$", version):
            errors.append(f"Invalid version format: '{version}' (must be semver: X.Y.Z)")

    # Type validation
    valid_types = ["plugin", "agent", "section", "workflow", "tool", "guard"]
    item_type = manifest.get("type", "")
    if item_type and item_type not in valid_types:
        errors.append(f"Invalid type: '{item_type}' (must be one of: {valid_types})")

    # Priority range validation
    priority = manifest.get("priority")
    if priority is not None:
        if not isinstance(priority, int) or priority < 0 or priority > 1000:
            errors.append(f"Invalid priority: {priority} (must be 0-1000)")

    # Full JSON Schema validation if available
    if HAS_JSONSCHEMA and not errors:
        schema = _get_schema()
        if schema:
            try:
                validator = Draft7Validator(schema)
                for error in validator.iter_errors(manifest):
                    errors.append(f"{error.json_path}: {error.message}")
            except Exception as e:
                errors.append(f"Schema validation error: {e}")

    return errors


def validate_manifest_file(manifest_path: Path) -> List[str]:
    """
    Validate a manifest file.

    Args:
        manifest_path: Path to the manifest.json file

    Returns:
        List of error messages (empty if valid)
    """
    errors: List[str] = []

    if not manifest_path.exists():
        return [f"File not found: {manifest_path}"]

    try:
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]
    except Exception as e:
        return [f"Failed to read file: {e}"]

    return validate_manifest(manifest)


def validate_all_manifests(
    scan_paths: Optional[List[Path]] = None,
    manifest_filename: str = "manifest.json",
) -> Dict[Path, List[str]]:
    """
    Validate all manifest files in the given paths.

    Args:
        scan_paths: Directories to scan for manifests
        manifest_filename: Name of manifest files to find

    Returns:
        Dict mapping manifest path -> list of errors (empty list if valid)
    """
    if scan_paths is None:
        # Default: scan common locations
        scan_paths = [
            Path("vibe_core/plugins"),
            Path("vibe_core/cartridges/system"),
            Path("vibe_core/cartridges/agent_city"),
            Path("vibe_core/phoenix/sections"),
        ]

    results: Dict[Path, List[str]] = {}

    for base_path in scan_paths:
        if not base_path.exists():
            continue

        # Find all manifest files
        for manifest_path in base_path.rglob(manifest_filename):
            errors = validate_manifest_file(manifest_path)
            results[manifest_path] = errors

    return results


def check_manifests_valid(
    scan_paths: Optional[List[Path]] = None,
) -> bool:
    """
    Check if ALL manifests are valid.

    Returns:
        True if all valid, False if any invalid
    """
    results = validate_all_manifests(scan_paths)

    all_valid = True
    for path, errors in results.items():
        if errors:
            all_valid = False
            logger.error(f"❌ Invalid manifest: {path}")
            for error in errors:
                logger.error(f"   - {error}")
        else:
            logger.debug(f"✅ Valid: {path}")

    return all_valid


# CLI entry point for pre-commit hook
def main() -> int:
    """
    CLI entry point for manifest validation.

    Usage:
        python -m vibe_core.loaders.schema [files...]

    Returns:
        0 if all valid, 1 if any invalid
    """
    import sys

    # Parse arguments
    files = sys.argv[1:] if len(sys.argv) > 1 else []

    if files:
        # Validate specific files
        all_valid = True
        for file_path in files:
            path = Path(file_path)
            if path.name == "manifest.json":
                errors = validate_manifest_file(path)
                if errors:
                    all_valid = False
                    print(f"❌ {path}")
                    for error in errors:
                        print(f"   - {error}")
                else:
                    print(f"✅ {path}")
        return 0 if all_valid else 1
    else:
        # Validate all manifests
        all_valid = check_manifests_valid()
        return 0 if all_valid else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
