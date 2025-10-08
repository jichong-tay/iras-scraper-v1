# Manual ChromeDriver Setup Guide

**For Network-Restricted Environments**

## Quick Setup Steps

### 1. Check Chrome Version
```bash
# Open Chrome browser → Help → About Google Chrome
# Note the version (e.g., 120.0.6099.109)
```

### 2. Download ChromeDriver

**Download Links:**
- **Latest Stable**: https://googlechromelabs.github.io/chrome-for-testing/
- **Legacy Versions**: https://chromedriver.chromium.org/downloads

**Platform Selection:**
- Windows 64-bit: `chromedriver-win64.zip`
- Windows 32-bit: `chromedriver-win32.zip` 
- Linux 64-bit: `chromedriver-linux64.zip`
- macOS Intel: `chromedriver-mac-x64.zip`
- macOS Apple Silicon: `chromedriver-mac-arm64.zip`

### 3. Installation Options

#### Option A: System PATH (Recommended)
```bash
# Windows
# Extract and copy chromedriver.exe to C:\Windows\System32\

# Linux/macOS
chmod +x chromedriver
sudo mv chromedriver /usr/local/bin/

# Verify installation
chromedriver --version
```

#### Option B: Project Directory
```bash
# Create drivers folder
mkdir -p drivers

# Copy ChromeDriver to project
# Linux/macOS: cp chromedriver ./drivers/
# Windows: copy chromedriver.exe ./drivers/

# Update .env file
echo "CHROMEDRIVER_PATH=./drivers/chromedriver" >> .env
```

### 4. Configuration

**For Project-Specific Setup (.env file):**
```env
# Manual ChromeDriver path
CHROMEDRIVER_PATH=./drivers/chromedriver

# OR disable automatic downloads
WDM_LOCAL=true
```

### 5. Test Installation

```bash
# Test with debug mode
uv run python -m iras_scraper.main --create-sample
uv run python -m iras_scraper.main --debug-single-uen "200012345A"
```

## Troubleshooting

### Common Issues

1. **Permission Denied (Linux/macOS)**:
   ```bash
   chmod +x chromedriver
   ```

2. **ChromeDriver Not Found**:
   - Verify the path in CHROMEDRIVER_PATH
   - Check if chromedriver is in system PATH
   - Ensure the executable name is correct (chromedriver.exe on Windows)

3. **Version Mismatch**:
   - Download ChromeDriver version matching your Chrome browser
   - Update Chrome browser if using older version
   - Check compatibility matrix on ChromeDriver website

4. **Network Blocks**:
   - Use WDM_LOCAL=true to disable all automatic downloads
   - Manually download on a different network and transfer files

### Verification Commands

```bash
# Check Chrome version
google-chrome --version          # Linux
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version  # macOS
# Windows: Open Chrome → Help → About

# Check ChromeDriver version  
chromedriver --version

# Test WebDriver connection
uv run python -c "from selenium import webdriver; from selenium.webdriver.chrome.service import Service; driver = webdriver.Chrome(service=Service()); print('Success!'); driver.quit()"
```

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `CHROMEDRIVER_PATH` | Manual ChromeDriver path | `./drivers/chromedriver` |
| `WDM_LOCAL` | Disable automatic downloads | `true` |
| `HEADLESS` | Headless browser mode | `false` |

## Security Notes

- Download ChromeDriver only from official Google sources
- Verify checksums if provided
- Keep ChromeDriver updated with Chrome browser updates
- Use HTTPS downloads when possible

---

**Need Help?** Check the main [README.md](../README.md) troubleshooting section or create an issue in the repository.