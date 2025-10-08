# IRAS Scraper - Distribution Directory

This directory is for packaging and distributing the IRAS Scraper to end users.

> **📖 For end-user installation guide, see**: [`docs/DISTRIBUTION_README.md`](../docs/DISTRIBUTION_README.md)

## 📦 **Distribution Package Contents**

When creating a distribution package, include these files:

### **Essential Files:**
```
distribution/
├── iras_scraper_v1-1.0.0-py3-none-any.whl    # Main package
├── install.sh                             # Installation script
├── README.md                              # Quick start guide
├── sample_input_template.xlsx             # Example input format
└── .env.example                          # Configuration template
```

### **Optional Files:**
```
distribution/
├── docs/                                  # Full documentation
│   ├── PACKAGE_USAGE_GUIDE.md           # Technical guide
│   └── SPEED_OPTIMIZATION_SUMMARY.md    # Performance guide
└── examples/
    └── quick_start.py                    # Code examples
```

---

## 🚀 **Creating Distribution Package**

### **Automated Creation:**
```bash
# Run from project root
./scripts/build.sh

# Copy distribution files
cp dist/*.whl distribution/
cp scripts/install.sh distribution/
cp docs/DISTRIBUTION_README.md distribution/README.md
cp sample_input_template.xlsx distribution/
cp .env.example distribution/

# Create distributable archive
tar -czf iras-scraper-v1.0.0-distribution.tar.gz distribution/
```

### **Manual Creation:**
1. Build the wheel package: `uv build`
2. Copy wheel file to `distribution/`
3. Copy `install.sh` script
4. Copy documentation and templates
5. Create archive for distribution

---

## 📋 **End User Instructions**

Include these instructions with your distribution:

### **System Requirements:**
- Python 3.8 or higher
- Chrome browser installed
- Internet connection
- 100MB free disk space

### **Installation Steps:**
1. Extract the distribution package
2. Run `./install.sh` (or `bash install.sh` on Windows)
3. Follow the on-screen instructions
4. Edit `data/input_uens.xlsx` with your UENs
5. Run `iras-scraper`

### **Quick Test:**
```bash
# Test installation
iras-scraper --help

# Create and test sample
iras-scraper --create-sample
iras-scraper --debug-single-uen "200012345A"
```

---

## 🔧 **Distribution Checklist**

Before distributing, verify:

- [ ] Wheel package builds successfully
- [ ] Install script works on clean system
- [ ] All required files are included
- [ ] Documentation is up-to-date
- [ ] Sample files are valid
- [ ] Version numbers are consistent

---

## 📞 **Support Information**

Include support information in your distribution:

- **Documentation**: Full guides in `docs/` directory
- **Examples**: Working code samples in `examples/`
- **Issues**: GitHub repository for bug reports
- **Configuration**: `.env.example` for customization

---

*Distribution package for IRAS Scraper v1.0.0 - Professional GST registration verification tool*