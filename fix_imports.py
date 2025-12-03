import re
from pathlib import Path


def fix_cartridge_imports(file_path: Path):
    """
    Reads a cartridge_main.py file, converts relative imports to absolute imports,
    and writes the changes back to the file.
    """
    content = file_path.read_text()
    original_content = content

    # Extract agent_id from the file path
    # e.g., steward/system_agents/civic/cartridge_main.py -> civic
    agent_id = file_path.parent.name

    # Regex to find relative imports: from .module import Class
    # Group 1: leading dots ('.', '..', etc.)
    # Group 2: module name
    # Group 3: rest of the import statement (import Class, etc.)
    # This also handles 'from .module.submodule import Class'
    relative_import_pattern = re.compile(r"from (\.+)([\w.]+)( import .*|$)")

    def replace_import(match):
        dots = match.group(1)
        module_name = match.group(2)
        rest = match.group(3)

        if dots == ".":
            # from .module import Class -> from steward.system_agents.agent_id.module import Class
            absolute_path = f"steward.system_agents.{agent_id}.{module_name}"
        elif dots == "..":
            # This implies importing from the parent of agent_id, e.g., steward.system_agents
            # from ..module import Class -> from steward.system_agents.module import Class
            # This pattern is less common given the current structure, but good to handle.
            absolute_path = f"steward.system_agents.{module_name}"
        else:
            # More than two dots, indicating further up the hierarchy
            # This is complex and might need manual review.
            print(f"WARNING: Complex relative import '{match.group(0)}' in {file_path}. Skipping automatic fix.")
            return match.group(0)  # Return original string if not handled

        new_import = f"from {absolute_path}{rest}"
        return new_import

    content = relative_import_pattern.sub(replace_import, content)

    if content != original_content:
        print(f"Fixing imports in {file_path}")
        file_path.write_text(content)
        return True
    return False


def main():
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent.parent  # Adjust based on script location

    # Find all cartridge_main.py files
    cartridge_files = project_root.glob("steward/system_agents/*/cartridge_main.py")

    fixed_count = 0
    for file_path in cartridge_files:
        if fix_cartridge_imports(file_path):
            fixed_count += 1

    print(f"\nCompleted fixing imports. {fixed_count} files modified.")


if __name__ == "__main__":
    main()
