#!/bin/bash
set -e

# Create dist directory if it doesn't exist
mkdir -p dist/plugins

echo "Building all plugin containers..."

# Iterate over all directories in vibe_core/plugins/
for plugin_dir in vibe_core/plugins/*/; do
    plugin_name=$(basename "$plugin_dir")
    
    # Skip __pycache__, files, or backup directories
    if [ ! -d "$plugin_dir" ] || [ "$plugin_name" == "__pycache__" ] || [ "$plugin_name" == "_crypto_BACKUP" ] || [ "$plugin_name" == "plugin_template" ]; then
        continue
    fi
    
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
