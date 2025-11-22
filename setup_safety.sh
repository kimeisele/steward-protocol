#!/bin/bash
# STEWARD PROTOCOL SAFETY INSTALLATION SCRIPT
# Installs git hooks to protect against accidental private key leaks and unsigned changes

set -e

HOOK_FILE=".git/hooks/pre-commit"
REPO_ROOT=$(git rev-parse --show-toplevel)

echo "🛡️  Installing STEWARD Safety Protocols..."
echo "   Protecting: $REPO_ROOT"

# Create the pre-commit hook
cat > "$HOOK_FILE" << 'HOOKEOF'
#!/bin/bash
# STEWARD PROTOCOL - SECURITY INTERLOCK SYSTEM
# Prevents accidental commits of:
#   1. Private cryptographic keys
#   2. Unsigned or invalid STEWARD.md manifests

echo "🔒 STEWARD: Pre-flight security check..."

ERRORS=0

# ============================================================================
# CHECK 1: PRIVATE KEY LEAK DETECTION
# ============================================================================

# Scan staged files for PEM private key headers
# (looking for "BEGIN [type] PRIVATE KEY" patterns)
if git diff --cached -U0 | grep -qE "BEGIN [A-Z]+ PRIVATE KEY"; then
    echo "❌ CRITICAL SECURITY ALERT"
    echo "   Attempted commit contains private key material!"
    echo "   Files with 'BEGIN.*PRIVATE KEY':"
    git diff --cached --name-only | while read file; do
        if git show ":$file" 2>/dev/null | grep -qE "BEGIN [A-Z]+ PRIVATE KEY"; then
            echo "      - $file"
        fi
    done
    echo ""
    echo "   ACTION: Remove these files from staging immediately"
    echo "   $ git reset <filename>"
    ((ERRORS++))
fi

# Check for attempts to commit private.pem files
if git diff --cached --name-only | grep -qE "private\.pem|\.steward/keys"; then
    echo "❌ CRITICAL SECURITY ALERT"
    echo "   Attempted commit of .steward/keys directory!"
    echo "   Files detected:"
    git diff --cached --name-only | grep -E "private\.pem|\.steward/keys" | sed 's/^/      - /'
    echo ""
    echo "   ACTION: Remove these files from staging immediately"
    echo "   $ git reset <filename>"
    ((ERRORS++))
fi

# ============================================================================
# CHECK 2: STEWARD.MD SIGNATURE VERIFICATION (if modified)
# ============================================================================

# Check if STEWARD.md is being committed
if git diff --cached --name-only | grep -q "STEWARD.md"; then
    echo ""
    echo "🔎 Verifying STEWARD.md identity signature..."

    # Get the staged version of STEWARD.md
    STAGED_FILE=$(git diff --cached --name-only | grep "STEWARD.md")

    # Create temporary file with staged content
    TEMP_FILE=$(mktemp)
    git show ":$STAGED_FILE" > "$TEMP_FILE" 2>/dev/null

    # Try to verify using steward CLI if available
    if command -v steward &> /dev/null; then
        if ! steward verify "$TEMP_FILE" > /dev/null 2>&1; then
            echo "❌ SIGNATURE VERIFICATION FAILED"
            echo "   File: $STAGED_FILE"
            echo "   Reason: Invalid or missing cryptographic signature"
            echo ""
            echo "   ACTION: Sign the file before committing"
            echo "   $ steward sign $STAGED_FILE --append"
            rm -f "$TEMP_FILE"
            ((ERRORS++))
        else
            echo "   ✅ Signature valid"
        fi
    else
        # Fallback: check for signature comment without verification
        if ! grep -q "STEWARD_SIGNATURE:" "$TEMP_FILE"; then
            echo "⚠️  WARNING: STEWARD.md is missing cryptographic signature"
            echo "   File: $STAGED_FILE"
            echo ""
            echo "   RECOMMENDED: Sign the file"
            echo "   $ steward sign $STAGED_FILE --append"
            echo ""
            echo "   (Proceeding anyway - steward CLI not found)"
        fi
    fi

    rm -f "$TEMP_FILE"
fi

# ============================================================================
# FINAL DECISION
# ============================================================================

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✅ Safety check PASSED. Proceeding with commit."
    exit 0
else
    echo "❌ Safety check FAILED with $ERRORS error(s)."
    echo ""
    echo "Fix the issues above and try again:"
    echo "  $ git reset                    # Unstage everything"
    echo "  $ git add <correct-files>      # Re-add only safe files"
    echo "  $ git commit -m 'Your message'"
    exit 1
fi
HOOKEOF

# Make hook executable
chmod +x "$HOOK_FILE"

echo "✅ Pre-commit hook installed at: $HOOK_FILE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛡️  STEWARD SAFETY PROTOCOLS ACTIVE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Protections Enabled:"
echo "  ✓ Private key leak detection (PEM headers)"
echo "  ✓ .steward/keys directory protection"
echo "  ✓ STEWARD.md signature verification"
echo ""
echo "From now on, every 'git commit' will be protected."
echo ""
echo "If you accidentally stage a private key:"
echo "  $ git reset <filename>          # Remove from staging"
echo "  $ git clean -fd                 # Delete local copies (optional)"
echo ""
echo "To disable these protections (not recommended):"
echo "  $ rm .git/hooks/pre-commit"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
