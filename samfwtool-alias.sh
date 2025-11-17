# SamFWTool Convenience Aliases
# Add to your ~/.bashrc or ~/.zshrc:
# source /path/to/samfwtool/samfwtool-alias.sh

SAMFWTOOL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SAMFWTOOL_DIR}:${PYTHONPATH}"

alias samfwtool='python3 -m samfwtool.cli.main'
alias samfwtool-gui='python3 -m samfwtool.gui.main_gui'
