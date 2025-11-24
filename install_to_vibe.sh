#!/bin/bash
# Steward Protocol - VibeOS Cartridge Installation Script
# This script installs the steward-protocol cartridge pack into a VibeOS installation.
#
# Usage: ./install_to_vibe.sh /path/to/vibe-agency
#
# What it does:
# 1. Validates VibeOS installation
# 2. Creates symlinks for all cartridges
# 3. Runs cartridge registration
# 4. Validates installation

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STEWARD_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VIBE_HOME="${1:-.}"
VIBE_CARTRIDGES_DIR="${VIBE_HOME}/vibe_core/cartridges"
VIBE_CONFIG_DIR="${VIBE_HOME}/vibe_core/config"

# Cartridges to install
CARTRIDGES=(
  "herald"
  "civic"
  "forum"
  "science"
  "archivist"
  "artisan"
  "envoy"
)

# Helper functions
print_header() {
  echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
  echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
  echo -e "${RED}✗ $1${NC}"
}

print_info() {
  echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if target directory exists and is a VibeOS installation
validate_vibe_installation() {
  if [ ! -d "$VIBE_HOME" ]; then
    print_error "VibeOS directory not found: $VIBE_HOME"
    echo "Usage: ./install_to_vibe.sh /path/to/vibe-agency"
    exit 1
  fi

  if [ ! -d "$VIBE_CARTRIDGES_DIR" ]; then
    print_info "Creating cartridges directory: $VIBE_CARTRIDGES_DIR"
    mkdir -p "$VIBE_CARTRIDGES_DIR"
  fi

  if [ ! -f "$VIBE_HOME/vibe_core/__init__.py" ] && [ ! -f "$VIBE_HOME/vibe_core/kernel.py" ]; then
    print_info "Warning: VibeOS kernel structure may be different than expected"
    print_info "Proceeding anyway - verify paths manually if needed"
  fi
}

# Create symlinks for all cartridges
install_cartridges() {
  print_header "Installing Cartridges"

  for cartridge in "${CARTRIDGES[@]}"; do
    local source="$STEWARD_ROOT/$cartridge"
    local target="$VIBE_CARTRIDGES_DIR/$cartridge"

    if [ ! -d "$source" ]; then
      print_error "Cartridge source not found: $source"
      continue
    fi

    # Remove existing symlink or directory if it exists
    if [ -L "$target" ]; then
      print_info "Removing old symlink: $target"
      rm "$target"
    elif [ -d "$target" ]; then
      print_error "Target directory already exists and is not a symlink: $target"
      echo "Please manually remove it or choose a different VibeOS installation."
      exit 1
    fi

    # Create symlink
    ln -s "$source" "$target"
    print_success "Installed $cartridge → ${target#$VIBE_HOME/}"
  done
}

# Register cartridge pack manifest
register_manifest() {
  print_header "Registering Package Manifest"

  local manifest_source="$STEWARD_ROOT/steward.yaml"
  local manifest_target="$VIBE_CONFIG_DIR/cartridges/steward-protocol.yaml"

  if [ ! -f "$manifest_source" ]; then
    print_error "steward.yaml manifest not found at: $manifest_source"
    return 1
  fi

  mkdir -p "$VIBE_CONFIG_DIR/cartridges"
  cp "$manifest_source" "$manifest_target"
  print_success "Registered manifest: steward-protocol.yaml"
}

# Validate installation
validate_installation() {
  print_header "Validating Installation"

  local all_good=true

  for cartridge in "${CARTRIDGES[@]}"; do
    local target="$VIBE_CARTRIDGES_DIR/$cartridge"
    if [ -L "$target" ] && [ -d "$target" ]; then
      print_success "Cartridge symlink verified: $cartridge"
    else
      print_error "Cartridge symlink missing or broken: $cartridge"
      all_good=false
    fi
  done

  if [ "$all_good" = true ]; then
    return 0
  else
    return 1
  fi
}

# Print summary
print_summary() {
  print_header "Installation Summary"

  echo "Steward Protocol has been installed to:"
  echo -e "  ${BLUE}${VIBE_CARTRIDGES_DIR}${NC}"
  echo ""
  echo "Installed Cartridges:"
  for cartridge in "${CARTRIDGES[@]}"; do
    echo -e "  • ${GREEN}$cartridge${NC}"
  done
  echo ""
  echo "Next Steps:"
  echo -e "  1. Verify VibeOS recognizes the cartridges:"
  echo -e "     ${BLUE}vibe list cartridges --pack=steward-protocol${NC}"
  echo ""
  echo -e "  2. Register an agent in Agent City:"
  echo -e "     ${BLUE}vibe agent register --city=Agent%20City${NC}"
  echo ""
  echo -e "  3. View the Agent City dashboard:"
  echo -e "     ${BLUE}vibe dashboard${NC}"
  echo ""
  echo -e "Documentation: ${BLUE}https://github.com/kimeisele/steward-protocol${NC}"
  echo ""
}

# Main installation flow
main() {
  print_header "🔧 Steward Protocol - VibeOS Installation"

  echo "Configuration:"
  echo "  VibeOS Home:     $VIBE_HOME"
  echo "  Cartridges Dir:  $VIBE_CARTRIDGES_DIR"
  echo "  Steward Root:    $STEWARD_ROOT"
  echo ""

  # Validation
  print_info "Validating VibeOS installation..."
  validate_vibe_installation
  print_success "VibeOS directory validated"

  # Installation
  install_cartridges

  # Register manifest
  if ! register_manifest; then
    print_error "Failed to register manifest (non-critical, continuing)"
  fi

  # Validation
  if validate_installation; then
    print_success "All cartridges installed successfully!"
  else
    print_error "Installation validation failed!"
    exit 1
  fi

  # Summary
  print_summary

  echo -e "${GREEN}✨ Agent City successfully annexed to VibeOS.${NC}"
  echo ""
}

# Run main
main "$@"
