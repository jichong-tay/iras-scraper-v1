# UV Configuration Guide for Network-Restricted Environments

**Complete Setup Guide for Offline UV Package Management**

## Overview

This guide helps you configure UV (Python package manager) to work in network-restricted environments where:
- Python downloads are blocked
- Package downloads are restricted  
- Only system Python installations are available
- Insecure hosts need to be allowed

## Quick Setup Steps

### 1. Create UV Configuration File

Create a `uv.toml` file in your project root:

```bash
# Navigate to your project directory
cd /path/to/iras-scraper-v1

# Create uv.toml configuration
touch uv.toml
```

### 2. Configure UV Settings

Add the following configuration to `uv.toml`:

```toml
[tool.uv]
# Disable automatic Python downloads
python-downloads = "never"

# Use only system-installed Python versions
python-preference = "only-system"

# Enable offline mode (no network requests for packages)
offline = true

# Allow connections to insecure hosts (if needed for internal repositories)
allow-insecure-host = [
    # Add your internal hosts here, e.g.:
    # "internal-pypi.company.com",
    # "mirror.local"
]

# Optional: Configure custom index URLs for internal repositories
# [[tool.uv.index]]
# name = "internal"
# url = "https://internal-pypi.company.com/simple/"

# Optional: Set cache directory
# cache-dir = "./uv-cache"

# Optional: Require exact versions (more deterministic)
# resolution = "highest"
```

### 3. Find and Configure System Python

```bash
# Find available system Python installations
uv python find --system

# Example output:
# Found Python 3.8.20 at /usr/bin/python3.8
# Found Python 3.9.18 at /usr/bin/python3.9
# Found Python 3.11.9 at /opt/homebrew/bin/python3.11
```

### 4. Sync with Specific Python Version

```bash
# Use specific Python path found above
uv sync --python /usr/bin/python3.8

# Or use Python version (UV will find system installation)
uv sync --python 3.8

# Or use Python executable name if in PATH
uv sync --python python3.8
```

## Complete Configuration Examples

### Basic Network-Restricted Setup

**File: `uv.toml`**
```toml
[tool.uv]
python-downloads = "never"
python-preference = "only-system"
offline = true
```

### Advanced Corporate Environment Setup

**File: `uv.toml`**
```toml
[tool.uv]
# Core offline settings
python-downloads = "never"
python-preference = "only-system"
offline = true

# Corporate network settings
allow-insecure-host = [
    "internal-pypi.company.com",
    "mirror.company.local",
    "artifactory.internal"
]

# Internal package repositories
[[tool.uv.index]]
name = "corporate"
url = "https://internal-pypi.company.com/simple/"
default = true

[[tool.uv.index]]
name = "public-mirror" 
url = "https://mirror.company.local/pypi/simple/"

# Performance and caching
cache-dir = "./uv-cache"
resolution = "highest"

# Security settings
no-build-isolation = false
compile-bytecode = true
```

## Step-by-Step Setup Process

### 1. Pre-Setup Verification

```bash
# Check available Python versions on system
python3 --version
python3.8 --version
python3.9 --version

# Check UV installation
uv --version

# Verify UV can find system Python
uv python find --system
```

### 2. Project Configuration

```bash
# Navigate to project
cd /path/to/iras-scraper-v1

# Create UV configuration
cat > uv.toml << 'EOF'
[tool.uv]
python-downloads = "never"
python-preference = "only-system"
offline = true
allow-insecure-host = []
EOF

# Verify configuration
cat uv.toml
```

### 3. Python Environment Setup

```bash
# Find system Python (note the path)
PYTHON_PATH=$(uv python find --system | head -n1 | awk '{print $4}')
echo "Using Python: $PYTHON_PATH"

# Initialize project with system Python
uv sync --python "$PYTHON_PATH"

# Verify environment
uv run python --version
```

### 4. Package Installation (Pre-downloaded)

For offline environments, you'll need to pre-download packages:

```bash
# On a connected machine, download all dependencies
uv export --format requirements-txt > requirements.txt

# Download packages for offline installation
pip download -r requirements.txt -d ./packages/

# Transfer the ./packages/ directory to your restricted environment

# In restricted environment, install from local packages
uv pip install --find-links ./packages/ -r requirements.txt
```

## Troubleshooting

### Common Issues

#### 1. **Python Not Found**
```bash
# Error: No Python installations found
# Solution: Install Python on system first
sudo apt-get install python3.8  # Ubuntu/Debian
brew install python@3.8         # macOS (if allowed)

# Or specify exact path
uv sync --python /usr/local/bin/python3.8
```

#### 2. **Network Errors in Offline Mode**
```bash
# Error: Network request blocked
# Solution: Ensure offline mode is enabled
echo 'offline = true' >> uv.toml

# Or set environment variable
export UV_OFFLINE=1
```

#### 3. **Package Download Issues**
```bash
# Error: Package not available offline
# Solution: Pre-download packages or configure local repository

# Check what's missing
uv lock --offline --dry-run

# Pre-download specific packages
uv pip download selenium pandas openpyxl
```

#### 4. **Insecure Host Warnings**
```toml
# Add problematic hosts to configuration
[tool.uv]
allow-insecure-host = [
    "your-internal-host.com",
    "192.168.1.100"  # IP addresses
]
```

## Environment Variables

Alternative to `uv.toml`, you can use environment variables:

```bash
# Offline configuration via environment
export UV_OFFLINE=1
export UV_PYTHON_DOWNLOADS=never
export UV_PYTHON_PREFERENCE=only-system
export UV_ALLOW_INSECURE_HOST="internal.com,mirror.local"

# Run commands with environment variables
uv sync --python python3.8
```

## Validation Commands

```bash
# Test UV configuration
uv python find --system
uv sync --python python3.8 --dry-run

# Test project functionality  
uv run python -c "import sys; print(f'Python: {sys.version}')"
uv run python -m iras_scraper.main --create-sample

# Check installed packages
uv pip list
uv tree
```

## Integration with IRAS Scraper

After setting up UV configuration:

```bash
# 1. Configure UV for offline use
cat > uv.toml << 'EOF'
[tool.uv]
python-downloads = "never"
python-preference = "only-system"  
offline = true
EOF

# 2. Setup with system Python
uv sync --python $(uv python find --system | head -n1 | awk '{print $4}')

# 3. Test IRAS scraper
uv run python test_chromedriver_setup.py
uv run python -m iras_scraper.main --create-sample

# 4. Run actual scraping
uv run python -m iras_scraper.main
```

## Complete Example Workflow

```bash
#!/bin/bash
# Complete setup script for network-restricted environment

# 1. Create UV configuration
cat > uv.toml << 'EOF'
[tool.uv]
python-downloads = "never"
python-preference = "only-system"
offline = true
allow-insecure-host = []
EOF

# 2. Find and use system Python
PYTHON_PATH=$(uv python find --system | head -n1 | awk '{print $4}')
echo "Using Python: $PYTHON_PATH"

# 3. Sync dependencies
uv sync --python "$PYTHON_PATH"

# 4. Test setup
echo "Testing UV configuration..."
uv run python --version
uv run python -c "import selenium, pandas; print('Dependencies OK')"

# 5. Test scraper
echo "Testing IRAS scraper..."
uv run python test_chromedriver_setup.py

echo "Setup complete! Ready for offline use."
```

## Security Considerations

- **Verify Package Sources**: When using `allow-insecure-host`, ensure hosts are trusted
- **Local Package Verification**: Check integrity of pre-downloaded packages
- **System Python Security**: Keep system Python installations updated
- **Network Isolation**: Confirm offline mode prevents unexpected network requests

---

**Related Guides:**
- [Manual WebDriver Setup](MANUAL_WEBDRIVER_SETUP.md) - ChromeDriver for network restrictions
- [Package Usage Guide](PACKAGE_USAGE_GUIDE.md) - Using the scraper package
- Main [README.md](../README.md) - Complete project documentation