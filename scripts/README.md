# IRAS Scraper - Scripts Directory

This directory contains automation and utility scripts for building, installing, and managing the IRAS Scraper package.

## 🔧 **Available Scripts**

### **build.sh**
- **Purpose**: Build the distributable wheel package
- **Usage**: `./scripts/build.sh`
- **Output**: Creates `dist/iras_scraper_v1-1.0.0-py3-none-any.whl`
- **Requirements**: UV package manager installed

```bash
# Build the package
cd /path/to/iras-scraper-v1
./scripts/build.sh
```

### **install.sh**
- **Purpose**: Easy installation script for end users
- **Usage**: `./scripts/install.sh` (in directory with wheel file)
- **Features**: 
  - Checks Python version compatibility
  - Installs the wheel package
  - Verifies installation
  - Creates sample files
  - Sets up environment

```bash
# For end users (in distribution directory)
./install.sh
```

---

## 📦 **Distribution Workflow**

### **For Package Maintainers:**

1. **Build Package:**
   ```bash
   ./scripts/build.sh
   ```

2. **Test Installation:**
   ```bash
   # Copy wheel to test directory
   cp dist/*.whl /tmp/test/
   cd /tmp/test/
   # Copy and run installer
   cp /path/to/scripts/install.sh .
   ./install.sh
   ```

3. **Distribute:**
   ```bash
   # Create distribution package
   mkdir iras-scraper-distribution
   cp dist/*.whl iras-scraper-distribution/
   cp scripts/install.sh iras-scraper-distribution/
   cp sample_input_template.xlsx iras-scraper-distribution/
   cp .env.example iras-scraper-distribution/
   cp docs/DISTRIBUTION_README.md iras-scraper-distribution/README.md
   
   # Package for distribution
   tar -czf iras-scraper-v1.0.0.tar.gz iras-scraper-distribution/
   ```

### **For End Users:**

1. **Download** the distribution package
2. **Extract** to desired location
3. **Run** `./install.sh`
4. **Follow** on-screen instructions

---

## 🛠️ **Script Maintenance**

- **Testing**: All scripts are tested on macOS and Linux
- **Dependencies**: Minimal external dependencies (Python 3.8+, pip/uv)
- **Error Handling**: Comprehensive error checking and user feedback
- **Portability**: Compatible with bash and zsh shells

---

## ⚡ **Quick Commands**

```bash
# Make scripts executable (if needed)
chmod +x scripts/*.sh

# Build and test complete workflow
./scripts/build.sh && echo "Build successful!"

# Clean build artifacts
rm -rf dist/ build/ *.egg-info/
```