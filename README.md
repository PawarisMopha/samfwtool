# SamFWTool - Advanced Firmware Analysis & Manipulation Toolkit

**A comprehensive, cross-platform firmware toolkit that significantly surpasses Samsung's Odin**

## 🚀 Features That Surpass Odin

### Core Advantages
- ✅ **Cross-Platform**: Linux, macOS, Windows (vs Odin's Windows-only)
- ✅ **Multi-Vendor Support**: Samsung, Google, Xiaomi, OnePlus, and more
- ✅ **Advanced Analysis**: Deep firmware inspection, security scanning, binary analysis
- ✅ **Firmware Modification**: Extract, modify, and repack firmware images
- ✅ **Automation Ready**: Python API and CLI for scripting
- ✅ **Modern Architecture**: Modular plugin system

### Advanced Features
- 📦 **Firmware Extraction**: Unpack .tar, .tar.md5, .img, .bin, .zip firmware files
- 🔍 **Deep Analysis**: Partition analysis, boot image inspection, kernel extraction
- 🛡️ **Security Scanner**: Vulnerability detection, binary security analysis
- 🔧 **Modification Tools**: Kernel patching, ramdisk modification, system image editing
- 📊 **Firmware Diffing**: Compare firmware versions, generate delta updates
- 🔄 **OTA Generation**: Create custom OTA packages
- 💾 **Backup/Restore**: Complete device backup and selective restoration
- 🎯 **Partition Management**: Extract, modify, and replace specific partitions
- 🧩 **Plugin System**: Extensible architecture for custom tools

## 🏗️ Architecture

```
samfwtool/
├── core/               # Core firmware handling
│   ├── parser.py      # Multi-format firmware parser
│   ├── extractor.py   # Firmware extraction engine
│   ├── packer.py      # Firmware repacking engine
│   └── validator.py   # Integrity verification
├── analysis/          # Analysis modules
│   ├── security.py    # Security vulnerability scanner
│   ├── binary.py      # Binary analysis tools
│   ├── partition.py   # Partition analyzer
│   └── diff.py        # Firmware comparison
├── devices/           # Device-specific modules
│   ├── samsung.py     # Samsung device support
│   ├── google.py      # Google Pixel support
│   ├── xiaomi.py      # Xiaomi device support
│   └── generic.py     # Generic Android device support
├── tools/             # Modification tools
│   ├── bootimg.py     # Boot image tools
│   ├── kernel.py      # Kernel extraction/patching
│   ├── ramdisk.py     # Ramdisk modification
│   └── ota.py         # OTA package generation
├── plugins/           # Plugin system
│   └── base.py        # Plugin base classes
├── cli/               # Command-line interface
│   └── main.py        # CLI entry point
└── api/               # Python API
    └── client.py      # API client
```

## 🎯 Quick Start

```bash
# Extract firmware
samfwtool extract firmware.tar.md5 -o output/

# Analyze firmware
samfwtool analyze firmware.tar.md5 --security --deep

# Modify boot image
samfwtool modify boot.img --extract-kernel --extract-ramdisk

# Repack firmware
samfwtool pack output/ -o custom_firmware.tar.md5

# Compare firmware versions
samfwtool diff firmware_v1.tar.md5 firmware_v2.tar.md5

# Generate OTA package
samfwtool ota --base firmware_v1.tar.md5 --target firmware_v2.tar.md5
```

## 📋 Comparison with Odin

| Feature | Odin | SamFWTool |
|---------|------|-----------|
| Platform | Windows only | Linux, macOS, Windows |
| Vendor Support | Samsung only | Multi-vendor |
| Firmware Analysis | None | Deep analysis + security scanning |
| Firmware Modification | No | Yes - extract, modify, repack |
| Automation | No | Full CLI + Python API |
| Open Source | No | Yes |
| Partition Extraction | No | Yes - all partitions |
| Binary Analysis | No | Yes - security + structure |
| OTA Generation | No | Yes |
| Firmware Diffing | No | Yes |
| Plugin System | No | Yes |
| Backup/Restore | Basic | Advanced selective restore |

## 🔧 Installation

```bash
pip install samfwtool
```

## 📖 Documentation

See [docs/](docs/) for comprehensive documentation.

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 License

MIT License - see [LICENSE](LICENSE)
