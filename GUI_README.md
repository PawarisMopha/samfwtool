# SamFWTool GUI Installation Guide

## 🚀 One-Click Installation

### Windows

1. **Double-click `INSTALL_GUI.bat`**
2. Follow the installation wizard
3. Done! Desktop shortcut will be created

### Linux / macOS

1. **Open terminal and run:**
   ```bash
   ./INSTALL_GUI.sh
   ```
2. Follow the installation wizard
3. Done! Desktop shortcut will be created

---

## 📋 What Gets Installed

The installer will:

- ✅ Check system requirements (Python 3.8+)
- ✅ Install Python dependencies automatically
- ✅ Configure system PATH
- ✅ Create desktop shortcut
- ✅ Create one-click launchers

---

## 🎯 Running SamFWTool GUI

### After Installation

**Option 1: Desktop Shortcut**
- Double-click the "SamFWTool" icon on your desktop

**Option 2: One-Click Launcher**
- Windows: Double-click `RUN_GUI.bat`
- Linux/macOS: Run `./RUN_GUI.sh`

**Option 3: Command Line**
```bash
samfwtool-gui
```

**Option 4: From Python**
```bash
python -m samfwtool.gui.main_gui
```

---

## 🔧 GUI Features

The GUI provides all SamFWTool features in an easy-to-use interface:

### 📊 Analyze Tab
- Open and analyze firmware files
- View partition information
- Check firmware format and metadata

### 📦 Extract Tab
- Extract firmware to directory
- Automatic decompression
- Progress tracking

### 🔥 Flash Tab
- Detect connected devices
- Flash partitions
- Safety checks enabled

### 🔒 Security Tab
- Full security scanning
- FRP (Factory Reset Protection) analysis
- Export security reports

### 🔧 Chipset Tools Tab
- MediaTek (MTK) scatter file parsing
- Qualcomm EDL mode tools
- Chipset-specific features

### 🛠️ Tools Tab
- Pack firmware from partitions
- Compare firmware versions
- Boot image tools

---

## ❓ Troubleshooting

### Python Not Found

**Windows:**
1. Download Python from https://python.org/downloads/
2. Run installer
3. ✅ **IMPORTANT:** Check "Add Python to PATH"
4. Complete installation
5. Restart computer
6. Run `INSTALL_GUI.bat` again

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip python3-tk

# Fedora
sudo dnf install python3 python3-tkinter

# Arch
sudo pacman -S python python-pip tk
```

**macOS:**
```bash
brew install python-tk
```

### Tkinter Not Found

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

**macOS:**
```bash
brew install python-tk
```

### Permission Denied (Linux/macOS)

```bash
chmod +x INSTALL_GUI.sh
chmod +x RUN_GUI.sh
./INSTALL_GUI.sh
```

### GUI Won't Start

1. Try running from terminal to see errors:
   ```bash
   python -m samfwtool.gui.main_gui
   ```

2. Check if tkinter is installed:
   ```bash
   python -c "import tkinter; print('OK')"
   ```

3. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 📝 Manual Installation (Advanced)

If automatic installation fails:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install SamFWTool
pip install -e .

# 3. Run GUI
python -m samfwtool.gui.main_gui
```

---

## 🆘 Getting Help

**Installation Issues:**
- Check Python version: `python --version` (need 3.8+)
- Check pip: `pip --version`
- See full documentation in `docs/`

**GUI Issues:**
- Run from terminal to see error messages
- Check `~/.samfwtool/logs/` for log files

**Feature Requests:**
- Open issue on GitHub

---

## 🎓 Next Steps

After installation:

1. **Read the Quick Start:** See `docs/QUICKSTART.md`
2. **Explore Features:** Check `docs/FEATURES.md`
3. **View Comparisons:** See `docs/COMPARISON_ALL_TOOLS.md`
4. **Try Examples:** Look in `examples/` directory

---

## 💡 Tips

- **First Time:** Start with the Analyze tab to explore firmware files
- **Safety:** Always enable safety checks when flashing
- **Backups:** Use the backup feature before flashing
- **Updates:** Run installer again to update to latest version

---

## 🌟 Features Available in GUI

All SamFWTool features accessible via GUI:

✅ Multi-format firmware parsing
✅ Security vulnerability scanning
✅ FRP analysis (Factory Reset Protection)
✅ Device flashing (Samsung, MTK, Qualcomm, etc.)
✅ Firmware extraction and creation
✅ Version comparison
✅ Boot image manipulation
✅ Chipset-specific tools

**No other firmware tool has a GUI this comprehensive!**
