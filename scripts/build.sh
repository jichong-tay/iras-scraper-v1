#!/bin/bash
# Build script for IRAS Scraper package

echo "🔨 Building IRAS Scraper Package"
echo "================================"
echo ""

# Clean previous builds
if [ -d "dist" ]; then
    echo "🧹 Cleaning previous builds..."
    rm -rf dist/
fi

# Build the package
echo "📦 Building wheel package..."
uv build

if [ $? -eq 0 ]; then
    echo "✅ Package built successfully!"
    echo ""
    echo "📋 Generated files:"
    ls -la dist/
    
    echo ""
    echo "🎯 Next steps:"
    echo "  1. Test installation: uv pip install dist/*.whl"
    echo "  2. Distribute: Copy wheel file to target systems"
    echo "  3. Install on target: pip install iras_scraper_v1-*.whl"
    
else
    echo "❌ Build failed!"
    exit 1
fi