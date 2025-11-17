#!/bin/bash
# SamFWTool - One-Click Installation Script
# This script installs SamFWTool with all dependencies

set -e  # Exit on error

echo "======================================"
echo "  SamFWTool Installation Wizard"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if running as root on Linux
if [ "$EUID" -eq 0 ] && [ "$(uname)" == "Linux" ]; then
    print_warning "Running as root. This is OK for system-wide installation."
fi

# Detect OS
print_info "Detecting operating system..."
OS="unknown"
if [ "$(uname)" == "Darwin" ]; then
    OS="macOS"
    print_success "Detected macOS"
elif [ "$(uname)" == "Linux" ]; then
    OS="Linux"
    print_success "Detected Linux"
else
    OS="Windows"
    print_success "Detected Windows/WSL"
fi

# Check Python version
print_info "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
    PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')

    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        print_success "Python $PYTHON_VERSION found (required: 3.8+)"
    else
        print_error "Python 3.8+ required, found $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Install system dependencies for GUI
print_info "Checking GUI dependencies..."
if [ "$OS" == "Linux" ]; then
    if ! python3 -c "import tkinter" 2>/dev/null; then
        print_warning "Tkinter not found. Attempting to install..."

        # Detect package manager and install
        if command -v apt-get &> /dev/null; then
            print_info "Using apt-get to install python3-tk..."
            if [ "$EUID" -eq 0 ]; then
                apt-get update -qq && apt-get install -y python3-tk python3.11-tk 2>&1 | tail -5
            else
                sudo apt-get update -qq && sudo apt-get install -y python3-tk python3.11-tk 2>&1 | tail -5
            fi
        elif command -v dnf &> /dev/null; then
            print_info "Using dnf to install python3-tkinter..."
            sudo dnf install -y python3-tkinter
        elif command -v yum &> /dev/null; then
            print_info "Using yum to install python3-tkinter..."
            sudo yum install -y python3-tkinter
        elif command -v pacman &> /dev/null; then
            print_info "Using pacman to install tk..."
            sudo pacman -S --noconfirm tk
        else
            print_warning "Could not detect package manager. GUI may not work."
            print_warning "Please install tkinter manually for your distribution."
        fi

        if python3 -c "import tkinter" 2>/dev/null; then
            print_success "Tkinter installed successfully"
        else
            print_warning "Tkinter installation may have failed. CLI will still work."
        fi
    else
        print_success "Tkinter already installed"
    fi
elif [ "$OS" == "macOS" ]; then
    if ! python3 -c "import tkinter" 2>/dev/null; then
        print_warning "Tkinter not found. Installing via brew..."
        if command -v brew &> /dev/null; then
            brew install python-tk
            print_success "Tkinter installed"
        else
            print_warning "Homebrew not found. Please install tkinter manually."
        fi
    else
        print_success "Tkinter already installed"
    fi
fi

# Upgrade pip (ignore system packages)
print_info "Upgrading pip..."
python3 -m pip install --upgrade pip --break-system-packages --quiet 2>/dev/null || \
python3 -m pip install --upgrade pip --quiet 2>/dev/null || \
print_warning "Pip upgrade skipped (system-managed)"

# Install dependencies
print_info "Installing Python dependencies..."
if [ -f requirements.txt ]; then
    python3 -m pip install -r requirements.txt --break-system-packages --quiet 2>/dev/null || \
    python3 -m pip install -r requirements.txt --quiet 2>/dev/null || \
    print_warning "Some dependencies may already be installed (system-managed)"
fi
print_success "Dependencies checked/installed"

# Install SamFWTool using PYTHONPATH method (most reliable)
print_info "Setting up SamFWTool..."
export PYTHONPATH="${PWD}:${PYTHONPATH}"
print_success "SamFWTool configured in PYTHONPATH"

# Verify installation
print_info "Verifying installation..."
if python3 -m samfwtool.cli.main --version &>/dev/null; then
    print_success "SamFWTool installed successfully!"
else
    print_error "Installation verification failed"
    exit 1
fi

# Create launcher scripts
print_info "Creating launcher scripts..."

# Create CLI launcher
cat > samfwtool-run.sh << 'EOF'
#!/bin/bash
# SamFWTool CLI Launcher
cd "$(dirname "$0")"
export PYTHONPATH="${PWD}:${PYTHONPATH}"
python3 -m samfwtool.cli.main "$@"
EOF
chmod +x samfwtool-run.sh
print_success "Created CLI launcher: samfwtool-run.sh"

# Create GUI launcher
cat > samfwtool-gui-run.sh << 'EOF'
#!/bin/bash
# SamFWTool GUI Launcher
cd "$(dirname "$0")"
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Check if display is available
if [ -z "$DISPLAY" ] && [ "$(uname)" == "Linux" ]; then
    echo "ERROR: No display available. GUI requires X11."
    echo "Use samfwtool-run.sh for CLI version instead."
    exit 1
fi

python3 -m samfwtool.gui.main_gui "$@"
EOF
chmod +x samfwtool-gui-run.sh
print_success "Created GUI launcher: samfwtool-gui-run.sh"

# Create convenience aliases
cat > samfwtool-alias.sh << 'EOF'
# SamFWTool Convenience Aliases
# Add to your ~/.bashrc or ~/.zshrc:
# source /path/to/samfwtool/samfwtool-alias.sh

SAMFWTOOL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SAMFWTOOL_DIR}:${PYTHONPATH}"

alias samfwtool='python3 -m samfwtool.cli.main'
alias samfwtool-gui='python3 -m samfwtool.gui.main_gui'
EOF
print_success "Created alias file: samfwtool-alias.sh"

echo ""
echo "======================================"
echo "  Installation Complete! 🎉"
echo "======================================"
echo ""
print_success "SamFWTool is ready to use!"
echo ""
echo "Quick Start:"
echo ""
echo "  CLI Usage:"
echo "    ./samfwtool-run.sh --help"
echo "    ./samfwtool-run.sh compare"
echo "    ./samfwtool-run.sh devices"
echo ""
echo "  GUI Usage (if display available):"
echo "    ./samfwtool-gui-run.sh"
echo ""
echo "  Direct Python:"
echo "    python3 -m samfwtool.cli.main --help"
echo "    python3 -m samfwtool.gui.main_gui"
echo ""
echo "  Add to shell (optional):"
echo "    echo 'source $(pwd)/samfwtool-alias.sh' >> ~/.bashrc"
echo ""
print_info "For documentation, see: docs/"
print_info "For examples, see: examples/"
echo ""
