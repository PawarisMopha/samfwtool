# 🚀 SamFWTool - One-Click Quick Start Guide

**The easiest way to run SamFWTool - no configuration needed!**

---

## ⚡ Super Quick Start (Recommended)

### Linux / macOS

```bash
# One command to install and run:
./RUN.sh
```

### Windows

```cmd
REM Double-click or run:
RUN.bat
```

That's it! The script will:
- ✅ Auto-detect your system
- ✅ Install all dependencies
- ✅ Set up SamFWTool
- ✅ Show you an interactive menu

---

## 📋 What You Get

### Interactive Menu

When you run `RUN.sh` (Linux/macOS) or `RUN.bat` (Windows), you'll see:

```
╔════════════════════════════════════════╗
║     SamFWTool - Quick Launcher        ║
╚════════════════════════════════════════╝

What would you like to do?

  1) Run CLI (command line)
  2) Run GUI (graphical interface)
  3) Show help
  4) Show tool comparison
  5) Exit

Enter choice [1-5]:
```

---

## 🎯 Usage Options

### Option 1: Interactive Menu (Easiest)

**Linux/macOS:**
```bash
./RUN.sh
```

**Windows:**
```cmd
RUN.bat
```

### Option 2: Direct Launchers

**CLI Launcher:**
```bash
# Linux/macOS
./samfwtool-run.sh --help
./samfwtool-run.sh compare
./samfwtool-run.sh devices

# Windows
samfwtool-run.bat --help
samfwtool-run.bat compare
samfwtool-run.bat devices
```

**GUI Launcher:**
```bash
# Linux/macOS (requires X11 display)
./samfwtool-gui-run.sh

# Windows
samfwtool-gui-run.bat
```

### Option 3: Manual Installation

If you prefer traditional installation:

```bash
# Linux/macOS
./INSTALL.sh

# Windows
INSTALL.bat
```

After installation, use the launchers or direct Python commands.

---

## 🔧 Installation Details

### What Gets Installed

The installation script (`INSTALL.sh` or `INSTALL.bat`) will:

1. ✅ **Check Python 3.8+** - Verifies you have the right version
2. ✅ **Install System Dependencies** - Tkinter for GUI (Linux only)
3. ✅ **Install Python Packages** - All required dependencies
4. ✅ **Configure SamFWTool** - Sets up PYTHONPATH
5. ✅ **Create Launchers** - Easy-to-use scripts
6. ✅ **Verify Installation** - Ensures everything works

### System Requirements

- **Python:** 3.8 or higher
- **OS:** Linux, macOS, or Windows
- **Disk Space:** ~50 MB
- **Display:** Optional (GUI requires X11 on Linux)

### Dependencies Installed

The following packages are installed automatically:
- click (CLI framework)
- rich (beautiful terminal output)
- pycryptodome (cryptography)
- lz4, brotli (compression)
- python-magic (file type detection)
- pefile, pyelftools (binary analysis)
- capstone (disassembly)
- requests, tqdm (utilities)
- colorama (colored output)

---

## 📖 Command Examples

### Analyze Firmware

```bash
./samfwtool-run.sh info firmware.tar.md5
./samfwtool-run.sh analyze firmware.zip --security
```

### Extract Firmware

```bash
./samfwtool-run.sh extract firmware.tar.md5 -o output_dir/
```

### Flash Device

```bash
./samfwtool-run.sh devices                    # List devices
./samfwtool-run.sh flash boot.img boot       # Flash partition
```

### Security Scanning

```bash
./samfwtool-run.sh scan firmware_dir/ --full
./samfwtool-run.sh frp firmware_dir/         # FRP analysis
```

### Boot Image Tools

```bash
./samfwtool-run.sh bootimg boot.img --extract-kernel
./samfwtool-run.sh bootimg boot.img --extract-ramdisk
```

### Compare Firmware

```bash
./samfwtool-run.sh diff old.tar.md5 new.tar.md5
```

### Pack Firmware

```bash
./samfwtool-run.sh pack partitions/ -o custom.tar.md5
```

### Chipset-Specific Tools

```bash
# MediaTek
./samfwtool-run.sh mtk parse scatter.txt

# Qualcomm EDL
./samfwtool-run.sh edl list-ports
./samfwtool-run.sh edl flash rawprogram.xml
```

---

## 🎨 GUI Features

Launch the GUI with:
```bash
./samfwtool-gui-run.sh      # Linux/macOS
samfwtool-gui-run.bat       # Windows
```

### GUI Tabs

1. **📊 Analyze** - View firmware info and partitions
2. **📦 Extract** - Extract firmware with progress bar
3. **🔥 Flash** - Flash devices with safety checks
4. **🔒 Security** - Security scanning and FRP analysis
5. **🔧 Chipset Tools** - MTK and Qualcomm tools
6. **🛠️ Tools** - Pack, compare, and modify firmware

---

## 🆘 Troubleshooting

### "Python not found"

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip

# Fedora
sudo dnf install python3 python3-pip

# Arch
sudo pacman -S python python-pip
```

**macOS:**
```bash
brew install python3
```

**Windows:**
1. Download from https://python.org
2. Run installer
3. ✅ **Check "Add Python to PATH"**
4. Restart terminal

### "No display available" (GUI on Linux)

The GUI requires X11. Options:
1. Use CLI instead: `./samfwtool-run.sh`
2. Enable X11 forwarding: `export DISPLAY=:0`
3. Use remote display via SSH: `ssh -X user@host`

### "Permission denied"

Make scripts executable:
```bash
chmod +x RUN.sh INSTALL.sh samfwtool-run.sh samfwtool-gui-run.sh
```

### "Module not found"

Reinstall:
```bash
./INSTALL.sh    # Linux/macOS
INSTALL.bat     # Windows
```

### Dependencies fail to install

System-managed Python (like on Debian/Ubuntu):
```bash
# Use --break-system-packages (already handled in script)
# Or install to user directory:
python3 -m pip install --user -r requirements.txt
```

---

## 🌟 Advanced Usage

### Add to Shell Permanently

**Linux/macOS:**
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'source /path/to/samfwtool/samfwtool-alias.sh' >> ~/.bashrc
source ~/.bashrc

# Now use anywhere:
samfwtool --help
samfwtool-gui
```

**Windows:**
Add the samfwtool directory to your PATH environment variable.

### Use as Python Module

```python
from samfwtool.core.parser import FirmwareParser
from samfwtool.analysis.security import SecurityScanner

# Parse firmware
parser = FirmwareParser("firmware.tar.md5")
info = parser.parse()

# Security scan
scanner = SecurityScanner("firmware_dir/")
results = scanner.scan()
```

### Environment Variables

```bash
# Set custom paths
export SAMFWTOOL_HOME=/path/to/samfwtool
export PYTHONPATH=$SAMFWTOOL_HOME:$PYTHONPATH

# Enable debug mode
export SAMFWTOOL_DEBUG=1
```

---

## 📚 Next Steps

After installation:

1. **Try the comparison:** `./samfwtool-run.sh compare`
2. **Read the docs:** See `docs/` directory
3. **View examples:** Check `examples/` directory
4. **Explore features:** Run `./samfwtool-run.sh --help`

---

## 🎯 Why SamFWTool?

### vs Samsung Odin
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Multi-vendor support (not just Samsung)
- ✅ Advanced analysis and security scanning
- ✅ Firmware modification capabilities

### vs SP Flash Tool
- ✅ Works on all platforms (not just Windows)
- ✅ Supports more chipsets (MTK + Qualcomm + more)
- ✅ Open source and scriptable

### vs QFIL
- ✅ Cross-platform
- ✅ Modern GUI and CLI
- ✅ Better error handling

### Unique Features
- 🔒 Security vulnerability scanning
- 🛡️ FRP (Factory Reset Protection) analysis
- 🔄 Firmware comparison and diffing
- 📦 OTA package generation
- 🔧 Boot image modification
- 🎯 Multi-format support (TAR, ZIP, IMG, SPARSE, etc.)

---

## 📄 License

MIT License - Free to use, modify, and distribute

---

## 🤝 Support

- **Documentation:** `docs/` directory
- **Examples:** `examples/` directory
- **Issues:** Open an issue on GitHub
- **Contributing:** See `CONTRIBUTING.md`

---

**Enjoy using SamFWTool! 🎉**
