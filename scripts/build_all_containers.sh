#!/bin/bash
set -e

# Create dist directory if it doesn't exist
mkdir -p dist/plugins

echo "Building all plugin containers..."

# Iterate over all directories in vibe_core/plugins/
# Function to find plugin directories
find_plugin_dirs() {
    for dir in vibe_core/plugins/*/; do
        [ -d "$dir" ] || continue
        dirname=$(basename "$dir")

        # Skip exclusion list
        if [ "$dirname" == "__pycache__" ] || [ "$dirname" == "_crypto_BACKUP" ] || [ "$dirname" == "plugin_template" ]; then
            continue
        fi

        # Logic: If manifest.json exists, it's a plugin.
        # If NOT, check immediate subdirectories (namespace case).
        if [ -f "${dir}manifest.json" ]; then
            echo "$dir"
        else
            # Check subdirectories one level deep
            for subdir in "${dir}"*/; do
                if [ -d "$subdir" ] && [ -f "${subdir}manifest.json" ]; then
                    echo "$subdir"
                fi
            done
        fi
    done
}

# Iterate over found plugins
find_plugin_dirs | while read plugin_dir; do
    plugin_name=$(basename "$plugin_dir")

    echo "----------------------------------------"
    echo "Building plugin: $plugin_name"

    output_file="dist/plugins/${plugin_name}.vibe"

    # Run pack_vibe.py
    # We assume python is available and PYTHONPATH is set by the caller (or we set it)
    # The user request said "PYTHONPATH gesetzt für Crypto-Import" in the yaml,
    # but good practice to ensure it here or rely on the yaml env.
    # The yaml sets `export PYTHONPATH=$PWD`.

    python3 scripts/pack_vibe.py "$plugin_dir" -o "$output_file"

    if [ -f "$output_file" ]; then
        echo "Successfully built: $output_file"
    else
        echo "Failed to build: $plugin_name"
        exit 1
    fi
done

echo "----------------------------------------"
echo "All plugins built successfully."
