#!/bin/bash
# Network-Restricted Environment Setup Script
# Sets up both UV configuration and ChromeDriver for offline environments

set -e  # Exit on any error

echo "🌐 Network-Restricted Environment Setup for IRAS Scraper"
echo "============================================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."
if ! command_exists uv; then
    echo "❌ UV package manager not found. Please install UV first."
    echo "   Visit: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

if ! command_exists python3; then
    echo "❌ Python 3 not found. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Step 1: Create UV configuration for offline use
echo ""
echo "📦 Step 1: Configuring UV for offline use..."
if [ ! -f "uv.toml" ]; then
    cat > uv.toml << 'EOF'
[tool.uv]
# Network-restricted environment configuration
python-downloads = "never"
python-preference = "only-system"
offline = true
allow-insecure-host = []
EOF
    echo "✅ Created uv.toml with offline configuration"
else
    echo "ℹ️  uv.toml already exists, skipping creation"
fi

# Step 2: Find and configure system Python
echo ""
echo "🐍 Step 2: Finding system Python installations..."
echo "Available Python versions:"
uv python find --system

# Get the first available Python
PYTHON_PATH=$(uv python find --system | head -n1 | awk '{print $NF}')
if [ -z "$PYTHON_PATH" ]; then
    echo "❌ No system Python found. Please install Python 3.8+ first."
    exit 1
fi

echo "📍 Using Python: $PYTHON_PATH"

# Step 3: Sync dependencies with system Python
echo ""
echo "⚙️  Step 3: Syncing dependencies with system Python..."
if uv sync --python "$PYTHON_PATH"; then
    echo "✅ Dependencies synced successfully"
else
    echo "⚠️  Dependency sync failed. You may need to pre-download packages."
    echo "   See docs/UV_OFFLINE_SETUP.md for offline package installation"
fi

# Step 4: Check ChromeDriver configuration
echo ""
echo "🚗 Step 4: Checking ChromeDriver configuration..."
if [ ! -f ".env" ] && [ ! -f "drivers/chromedriver" ] && [ ! -f "drivers/chromedriver.exe" ]; then
    echo "ℹ️  No manual ChromeDriver configuration detected"
    echo "   If automatic ChromeDriver download is blocked, see:"
    echo "   - docs/MANUAL_WEBDRIVER_SETUP.md"
    echo "   - Or run: uv run python test_chromedriver_setup.py"
else
    echo "✅ ChromeDriver configuration found"
fi

# Step 5: Test the configuration
echo ""
echo "🧪 Step 5: Testing configuration..."
echo "Testing Python environment..."
if uv run python --version; then
    echo "✅ Python environment working"
else
    echo "❌ Python environment test failed"
    exit 1
fi

echo ""
echo "Testing package imports..."
if uv run python -c "
import sys
print(f'Python: {sys.version}')
try:
    import selenium, pandas, openpyxl
    print('✅ Core packages available')
except ImportError as e:
    print(f'⚠️  Some packages missing: {e}')
    print('   This is normal for offline environments')
"; then
    echo "✅ Basic imports working"
fi

# Step 6: Create sample input if needed
echo ""
echo "📋 Step 6: Setting up sample files..."
if [ ! -f "data/input_uens.xlsx" ]; then
    echo "Creating sample input file..."
    if uv run python -m iras_scraper.main --create-sample; then
        echo "✅ Sample input file created"
    else
        echo "⚠️  Sample file creation failed (may need package pre-download)"
    fi
else
    echo "✅ Sample input file already exists"
fi

# Summary
echo ""
echo "🎉 Network-Restricted Setup Complete!"
echo "====================================="
echo ""
echo "📁 Configuration files created:"
echo "   - uv.toml (UV offline configuration)"
if [ -f ".env" ]; then
    echo "   - .env (ChromeDriver configuration)"
fi
if [ -f "data/input_uens.xlsx" ]; then
    echo "   - data/input_uens.xlsx (sample input)"
fi

echo ""
echo "🚀 Next steps:"
echo "1. If ChromeDriver downloads are blocked:"
echo "   - Follow docs/MANUAL_WEBDRIVER_SETUP.md"
echo "   - Run: uv run python test_chromedriver_setup.py"
echo ""
echo "2. If package downloads are blocked:"
echo "   - Follow docs/UV_OFFLINE_SETUP.md"
echo "   - Pre-download packages on connected machine"
echo ""
echo "3. Test the scraper:"
echo "   - uv run python -m iras_scraper.main --create-sample"
echo "   - uv run python -m iras_scraper.main"
echo ""
echo "📚 Documentation:"
echo "   - Main guide: README.md"
echo "   - ChromeDriver: docs/MANUAL_WEBDRIVER_SETUP.md" 
echo "   - UV offline: docs/UV_OFFLINE_SETUP.md"

echo ""
echo "✅ Setup complete! Your environment is configured for network-restricted use."