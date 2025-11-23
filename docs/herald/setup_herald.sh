#!/bin/bash
# HERALD Agent Quick Start Script
# Run this to get HERALD up and running

set -e

echo "🚀 HERALD Agent Setup"
echo "====================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version"
echo ""

# Create directory structure
echo "Creating directory structure..."
mkdir -p herald/queue
mkdir -p steward/keys
echo "✓ Directories created"
echo ""

# Check if STEWARD is installed
echo "Checking STEWARD Protocol..."
if ! pip show steward-protocol > /dev/null 2>&1; then
    echo "⚠️  STEWARD Protocol not found"
    echo "Install from: https://github.com/kimeisele/steward-protocol"
    read -p "Install now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install steward-protocol
    else
        echo "❌ STEWARD Protocol required. Exiting."
        exit 1
    fi
fi
echo "✓ STEWARD Protocol installed"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install tweepy praw anthropic python-dotenv schedule
echo "✓ Dependencies installed"
echo ""

# Generate HERALD identity
echo "Generating HERALD identity..."
if [ ! -f "steward/keys/herald_private_key" ]; then
    cd steward
    steward keygen --agent-id agent.vibe.herald
    cd ..
    echo "✓ HERALD identity generated"
else
    echo "✓ HERALD identity already exists"
fi
echo ""

# Create .env template if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env template..."
    cat > .env << 'EOF'
# Twitter API
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_SECRET=your_access_secret_here

# Reddit API
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USERNAME=your_username_here
REDDIT_PASSWORD=your_password_here

# Anthropic API
ANTHROPIC_API_KEY=your_anthropic_key_here
EOF
    echo "✓ .env template created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env with your actual API keys!"
    echo ""
else
    echo "✓ .env already exists"
    echo ""
fi

# Create gitignore
echo "Creating .gitignore..."
cat > .gitignore << 'EOF'
.env
*.pyc
__pycache__/
steward/keys/*_private_key
herald/queue/
herald_audit_log.json
herald_paused.txt
pause_until.txt
EOF
echo "✓ .gitignore created"
echo ""

# Test HERALD
echo "Testing HERALD installation..."
python3 << 'EOF'
try:
    from herald_agent import HeraldAgent
    print("✓ HERALD agent can be imported")
except ImportError as e:
    print(f"❌ Error importing HERALD: {e}")
    exit(1)
EOF
echo ""

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Edit .env with your API keys:"
echo "   nano .env"
echo ""
echo "2. Review the setup guide:"
echo "   cat HERALD_SETUP_GUIDE.md"
echo ""
echo "3. Start with manual mode (Phase 1):"
echo "   python3 herald_agent.py --test-mode"
echo ""
echo "4. Read why posts get downvoted:"
echo "   cat WHY_DOWNVOTED.md"
echo ""
echo "⚠️  REMEMBER: Start manual, build karma, provide value first!"
echo ""
echo "Good luck! 🚀"
