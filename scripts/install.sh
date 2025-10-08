#!/bin/bash
# IRAS Scraper - Easy Installation Script

echo "🚀 IRAS Scraper Installation Script"
echo "=================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ -z "$python_version" ]]; then
    echo "❌ Python 3 not found. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python $python_version detected"

# Check if wheel file exists
wheel_file="iras_scraper_v1-1.0.0-py3-none-any.whl"
if [[ ! -f "$wheel_file" ]]; then
    echo "❌ Wheel file '$wheel_file' not found in current directory"
    echo "   Please ensure the wheel file is in the same directory as this script."
    exit 1
fi

echo "✅ Package file found: $wheel_file"

# Install the package
echo ""
echo "📦 Installing IRAS Scraper package..."
if command -v uv &> /dev/null; then
    echo "Using UV package manager..."
    uv pip install "$wheel_file"
else
    echo "Using pip package manager..."
    pip3 install "$wheel_file"
fi

if [[ $? -eq 0 ]]; then
    echo "✅ Package installed successfully!"
else
    echo "❌ Package installation failed"
    exit 1
fi

# Verify installation
echo ""
echo "🔍 Verifying installation..."
if command -v iras-scraper &> /dev/null; then
    echo "✅ CLI command available"
    
    # Test import
    python3 -c "
from iras_scraper import IRASScraper, __version__
print(f'✅ Package import successful - Version {__version__}')
" 2>/dev/null
    
    if [[ $? -eq 0 ]]; then
        echo "✅ Package import successful"
    else
        echo "⚠️  Package installed but import test failed"
    fi
else
    echo "⚠️  CLI command not found - installation may have issues"
fi

# Create sample files
echo ""
echo "📁 Setting up sample files..."
iras-scraper --create-sample
if [[ $? -eq 0 ]]; then
    echo "✅ Sample input file created: data/input_uens.xlsx"
else
    echo "⚠️  Could not create sample file"
fi

# Copy environment template if available
if [[ -f ".env.example" ]]; then
    cp .env.example .env.local
    echo "✅ Environment template copied to .env.local"
fi

echo ""
echo "🎉 Installation Complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. Edit data/input_uens.xlsx with your UENs"
echo "   2. Run: iras-scraper"
echo "   3. View results in: data/output_results.xlsx"
echo ""
echo "💡 Quick Commands:"
echo "   iras-scraper --help                    # Show all options"
echo "   iras-scraper --debug-single-uen UEN   # Test single UEN"
echo "   iras-scraper --headless               # Run in background"
echo ""
echo "📖 Full documentation: PACKAGE_USAGE_GUIDE.md"