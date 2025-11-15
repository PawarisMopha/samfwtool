#!/usr/bin/env python3
"""
SamFWTool Installation Wizard
Professional installation with comprehensive error handling
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import tkinter.font as tkfont
import platform
import sys
import subprocess
import os
from pathlib import Path
import shutil


class InstallationWizard:
    """
    Comprehensive installation wizard for SamFWTool

    Features:
    - Dependency checking
    - Automatic installation
    - PATH configuration
    - Desktop shortcut creation
    - Comprehensive error handling
    - Progress tracking
    """

    def __init__(self, root):
        self.root = root
        self.root.title("SamFWTool Installation Wizard")
        self.root.geometry("700x600")
        self.root.resizable(False, False)

        self.system = platform.system()
        self.install_path = self._get_default_install_path()
        self.current_step = 0

        # Installation state
        self.python_ok = False
        self.dependencies_ok = False
        self.path_configured = False
        self.shortcut_created = False

        self._create_ui()
        self._center_window()

    def _get_default_install_path(self):
        """Get default installation path"""
        if self.system == "Windows":
            return Path(os.environ.get('LOCALAPPDATA', 'C:/')) / 'SamFWTool'
        elif self.system == "Darwin":  # macOS
            return Path.home() / 'Applications' / 'SamFWTool'
        else:  # Linux
            return Path.home() / '.local' / 'share' / 'samfwtool'

    def _create_ui(self):
        """Create UI"""
        # Header
        header = tk.Frame(self.root, bg='#2196F3', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title_font = tkfont.Font(family="Helvetica", size=20, weight="bold")
        tk.Label(
            header,
            text="🚀 SamFWTool Installation Wizard",
            font=title_font,
            bg='#2196F3',
            fg='white'
        ).pack(pady=25)

        # Main content
        self.content_frame = ttk.Frame(self.root, padding=20)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Progress bar
        self.progress = ttk.Progressbar(self.content_frame, mode='determinate', maximum=100)
        self.progress.pack(fill=tk.X, pady=(0, 20))

        # Buttons (pack BEFORE content so they're always visible at bottom)
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        self.back_btn = ttk.Button(button_frame, text="< Back", command=self._prev_step, state='disabled')
        self.back_btn.pack(side=tk.LEFT)

        self.next_btn = ttk.Button(button_frame, text="Next >", command=self._next_step)
        self.next_btn.pack(side=tk.RIGHT)

        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self._cancel)
        self.cancel_btn.pack(side=tk.RIGHT, padx=(0, 5))

        # Content area (changes per step) - pack AFTER buttons
        self.step_frame = ttk.Frame(self.content_frame)
        self.step_frame.pack(fill=tk.BOTH, expand=True)

        # Start with welcome step
        self._show_welcome()

    def _center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def _clear_step_frame(self):
        """Clear step frame"""
        for widget in self.step_frame.winfo_children():
            widget.destroy()

    def _show_welcome(self):
        """Show welcome screen"""
        try:
            self._clear_step_frame()
            self.progress['value'] = 0

            # Enable Next button, disable Back button
            self.next_btn.config(state='normal')
            self.back_btn.config(state='disabled')
            self.cancel_btn.config(state='normal')

            title_font = tkfont.Font(family="Helvetica", size=16, weight="bold")
            ttk.Label(
                self.step_frame,
                text="Welcome to SamFWTool!",
                font=title_font
            ).pack(pady=(20, 10))

            welcome_text = """
SamFWTool is the ULTIMATE universal firmware toolkit that surpasses
ALL competitors: Odin, SP Flash Tool, QFIL, and more!

Features:
• Cross-platform (Windows, macOS, Linux)
• Multi-vendor support (Samsung, MediaTek, Qualcomm, etc.)
• Comprehensive security analysis
• Factory Reset Protection (FRP) analysis
• Device flashing and backup
• Firmware extraction and creation

This wizard will:
1. Check system requirements
2. Install dependencies
3. Configure PATH
4. Create desktop shortcuts
5. Set up one-click launcher

Click Next to begin installation.
            """

            text_widget = tk.Text(self.step_frame, height=15, wrap=tk.WORD, relief=tk.FLAT)
            text_widget.pack(fill=tk.X, pady=10)
            text_widget.insert('1.0', welcome_text)
            text_widget.config(state='disabled')

            self.current_step = 0

        except Exception as e:
            messagebox.showerror("Error", f"Failed to show welcome screen: {e}")
            print(f"Error in _show_welcome: {e}")
            import traceback
            traceback.print_exc()

    def _show_requirements(self):
        """Show requirements check"""
        try:
            self._clear_step_frame()
            self.progress['value'] = 20

            # Enable back button, disable next until checks complete
            self.back_btn.config(state='normal')
            self.next_btn.config(state='disabled')
            self.cancel_btn.config(state='normal')

            title_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
            ttk.Label(
                self.step_frame,
                text="Checking System Requirements",
                font=title_font
            ).pack(pady=(10, 20))

            # Results frame
            results_frame = ttk.Frame(self.step_frame)
            results_frame.pack(fill=tk.BOTH, expand=True)

            self.check_log = scrolledtext.ScrolledText(results_frame, height=15, wrap=tk.WORD)
            self.check_log.pack(fill=tk.BOTH, expand=True)

            # Run checks
            self._run_requirements_check()

            self.current_step = 1

        except Exception as e:
            messagebox.showerror("Error", f"Failed to show requirements screen: {e}")
            print(f"Error in _show_requirements: {e}")
            import traceback
            traceback.print_exc()

    def _run_requirements_check(self):
        """Run requirements check"""
        self._log("Checking system requirements...\n")

        # Check Python version
        self._log(f"✓ Python version: {sys.version}")
        py_version = sys.version_info
        if py_version.major >= 3 and py_version.minor >= 8:
            self._log("✓ Python version is compatible (3.8+)\n")
            self.python_ok = True
        else:
            self._log("✗ Python 3.8+ required!\n", error=True)
            self.python_ok = False

        # Check pip
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', '--version'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self._log(f"✓ pip is available: {result.stdout.strip()}\n")
            else:
                self._log("✗ pip is not available\n", error=True)
        except Exception as e:
            self._log(f"✗ Error checking pip: {e}\n", error=True)

        # Check platform
        self._log(f"✓ Operating System: {platform.system()} {platform.release()}")
        self._log(f"✓ Architecture: {platform.machine()}\n")

        # Check disk space
        try:
            stat = shutil.disk_usage(self.install_path.parent if self.install_path.parent.exists() else Path.home())
            free_gb = stat.free / (1024**3)
            self._log(f"✓ Available disk space: {free_gb:.2f} GB\n")
            if free_gb < 0.5:
                self._log("⚠ Warning: Low disk space (< 500 MB)\n", error=True)
        except Exception as e:
            self._log(f"⚠ Could not check disk space: {e}\n")

        # Check required tools
        self._log("\nChecking optional tools (for flashing):")
        tools = {
            'adb': 'Android Debug Bridge',
            'fastboot': 'Fastboot',
            'heimdall': 'Heimdall (Samsung)'
        }

        for tool, name in tools.items():
            if shutil.which(tool):
                self._log(f"  ✓ {name} found")
            else:
                self._log(f"  ✗ {name} not found (optional)")

        self._log("\n" + "="*50)
        if self.python_ok:
            self._log("\n✓ System requirements check PASSED")
            self.next_btn.config(state='normal')
        else:
            self._log("\n✗ System requirements check FAILED")
            self._log("\nPlease install Python 3.8+ and try again.")
            self.next_btn.config(state='disabled')

    def _show_installation_path(self):
        """Show installation path selection"""
        try:
            self._clear_step_frame()
            self.progress['value'] = 40

            # Enable buttons FIRST to ensure they're always enabled on this screen
            self.next_btn.config(state='normal')
            self.back_btn.config(state='normal')
            self.cancel_btn.config(state='normal')

            title_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
            ttk.Label(
                self.step_frame,
                text="Select Installation Path",
                font=title_font
            ).pack(pady=(10, 20))

            # Path selection
            path_frame = ttk.LabelFrame(self.step_frame, text="Installation Directory", padding=10)
            path_frame.pack(fill=tk.X, pady=10)

            self.path_var = tk.StringVar(value=str(self.install_path))
            ttk.Entry(path_frame, textvariable=self.path_var, width=50).pack(side=tk.LEFT, padx=5)
            ttk.Button(path_frame, text="Browse...", command=self._browse_install_path).pack(side=tk.LEFT)

            # Options
            options_frame = ttk.LabelFrame(self.step_frame, text="Installation Options", padding=10)
            options_frame.pack(fill=tk.X, pady=10)

            self.add_to_path_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                options_frame,
                text="Add to PATH (recommended)",
                variable=self.add_to_path_var
            ).pack(anchor=tk.W, pady=2)

            self.create_shortcut_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                options_frame,
                text="Create desktop shortcut",
                variable=self.create_shortcut_var
            ).pack(anchor=tk.W, pady=2)

            self.install_deps_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                options_frame,
                text="Install Python dependencies",
                variable=self.install_deps_var
            ).pack(anchor=tk.W, pady=2)

            # Info
            info_text = f"""
Installation will:
• Copy SamFWTool to: {self.install_path}
• Install required Python packages
• Configure system PATH
• Create desktop shortcuts
• Set up one-click launcher

Estimated time: 2-5 minutes
Required space: ~100 MB
            """

            info_widget = tk.Text(self.step_frame, height=8, wrap=tk.WORD, relief=tk.FLAT)
            info_widget.pack(fill=tk.X, pady=10)
            info_widget.insert('1.0', info_text)
            info_widget.config(state='disabled')

            self.current_step = 2

        except Exception as e:
            messagebox.showerror("Error", f"Failed to show installation path screen: {e}")
            print(f"Error in _show_installation_path: {e}")
            import traceback
            traceback.print_exc()

    def _show_installation(self):
        """Show installation progress"""
        self._clear_step_frame()
        self.progress['value'] = 60

        title_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        ttk.Label(
            self.step_frame,
            text="Installing SamFWTool",
            font=title_font
        ).pack(pady=(10, 20))

        # Progress
        self.install_progress = ttk.Progressbar(self.step_frame, mode='indeterminate')
        self.install_progress.pack(fill=tk.X, pady=10)

        # Log
        self.install_log = scrolledtext.ScrolledText(self.step_frame, height=15, wrap=tk.WORD)
        self.install_log.pack(fill=tk.BOTH, expand=True)

        # Disable all buttons during installation
        self.back_btn.config(state='disabled')
        self.next_btn.config(state='disabled')
        self.cancel_btn.config(state='disabled')

        self.current_step = 3

        # Run installation (must be after setting current_step)
        self._run_installation()

    def _run_installation(self):
        """Run actual installation"""
        import threading

        def install_thread():
            try:
                self.install_progress.start()

                # Step 1: Create installation directory
                self._install_log("Creating installation directory...")
                install_path = Path(self.path_var.get())
                install_path.mkdir(parents=True, exist_ok=True)
                self._install_log(f"✓ Created: {install_path}\n")

                # Step 2: Copy files
                self._install_log("Copying SamFWTool files...")
                source_dir = Path(__file__).parent
                for item in source_dir.rglob('*.py'):
                    if '__pycache__' not in str(item) and 'build' not in str(item):
                        rel_path = item.relative_to(source_dir)
                        dest = install_path / rel_path
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest)
                self._install_log("✓ Files copied\n")

                # Step 3: Install dependencies
                if self.install_deps_var.get():
                    self._install_log("Installing Python dependencies...")
                    req_file = source_dir / 'requirements.txt'
                    if req_file.exists():
                        result = subprocess.run(
                            [sys.executable, '-m', 'pip', 'install', '-r', str(req_file)],
                            capture_output=True,
                            text=True,
                            timeout=300
                        )
                        if result.returncode == 0:
                            self._install_log("✓ Dependencies installed\n")
                            self.dependencies_ok = True
                        else:
                            self._install_log(f"✗ Dependency installation failed:\n{result.stderr}\n", error=True)
                    else:
                        self._install_log("⚠ requirements.txt not found\n")

                # Step 4: Configure PATH
                if self.add_to_path_var.get():
                    self._install_log("Configuring PATH...")
                    if self._add_to_path(install_path):
                        self._install_log("✓ Added to PATH\n")
                        self.path_configured = True
                    else:
                        self._install_log("✗ Failed to add to PATH\n", error=True)

                # Step 5: Create desktop shortcut
                if self.create_shortcut_var.get():
                    self._install_log("Creating desktop shortcut...")
                    if self._create_desktop_shortcut(install_path):
                        self._install_log("✓ Desktop shortcut created\n")
                        self.shortcut_created = True
                    else:
                        self._install_log("✗ Failed to create shortcut\n", error=True)

                # Step 6: Create launcher
                self._install_log("Creating launcher scripts...")
                self._create_launcher(install_path)
                self._install_log("✓ Launcher created\n")

                self.install_progress.stop()
                self._install_log("\n" + "="*50)
                self._install_log("\n✓ Installation completed successfully!")
                self._install_log("\nYou can now launch SamFWTool from:")
                self._install_log(f"  • Desktop shortcut")
                self._install_log(f"  • Command line: samfwtool")
                self._install_log(f"  • GUI: samfwtool-gui")

                self.root.after(0, lambda: self.next_btn.config(state='normal'))
                self.root.after(0, lambda: self.cancel_btn.config(state='normal'))

            except Exception as e:
                self.install_progress.stop()
                self._install_log(f"\n✗ Installation failed: {str(e)}\n", error=True)
                self.root.after(0, lambda: messagebox.showerror("Installation Failed", str(e)))
                self.root.after(0, lambda: self.cancel_btn.config(state='normal'))

        threading.Thread(target=install_thread, daemon=True).start()

    def _show_complete(self):
        """Show completion screen"""
        try:
            self._clear_step_frame()
            self.progress['value'] = 100

            # Configure buttons for final screen
            self.next_btn.config(text="Launch SamFWTool", command=self._launch_app, state='normal')
            self.back_btn.config(state='disabled')
            self.cancel_btn.config(text="Close", command=self.root.quit, state='normal')

            title_font = tkfont.Font(family="Helvetica", size=16, weight="bold")
            ttk.Label(
                self.step_frame,
                text="🎉 Installation Complete!",
                font=title_font,
                foreground='green'
            ).pack(pady=(20, 10))

            complete_text = f"""
SamFWTool has been successfully installed!

Installation Summary:
  ✓ Installed to: {self.path_var.get()}
  {'✓' if self.dependencies_ok else '✗'} Python dependencies installed
  {'✓' if self.path_configured else '✗'} Added to PATH
  {'✓' if self.shortcut_created else '✗'} Desktop shortcut created

You can now use SamFWTool:

• Launch GUI: Double-click desktop icon
• Command line: samfwtool --help
• GUI from terminal: samfwtool-gui

Documentation: See docs/ folder
Support: https://github.com/samfwtool/samfwtool

Thank you for choosing SamFWTool!
            """

            text_widget = tk.Text(self.step_frame, height=14, wrap=tk.WORD, relief=tk.FLAT)
            text_widget.pack(fill=tk.X, pady=10)
            text_widget.insert('1.0', complete_text)
            text_widget.config(state='disabled')

            self.current_step = 4

        except Exception as e:
            messagebox.showerror("Error", f"Failed to show completion screen: {e}")
            print(f"Error in _show_complete: {e}")
            import traceback
            traceback.print_exc()

    # Helper methods
    def _log(self, message, error=False):
        """Log to check log"""
        if hasattr(self, 'check_log'):
            self.check_log.insert(tk.END, message + '\n')
            if error:
                # Would colorize in red
                pass
            self.check_log.see(tk.END)

    def _install_log(self, message, error=False):
        """Log to install log"""
        if hasattr(self, 'install_log'):
            self.install_log.insert(tk.END, message + '\n')
            self.install_log.see(tk.END)

    def _browse_install_path(self):
        """Browse for installation path"""
        from tkinter import filedialog
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)

    def _add_to_path(self, install_path):
        """Add to system PATH"""
        try:
            if self.system == "Windows":
                # Windows: Add to user PATH
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS)
                try:
                    path, _ = winreg.QueryValueEx(key, 'Path')
                except WindowsError:
                    path = ''

                if str(install_path) not in path:
                    new_path = f"{path};{install_path}" if path else str(install_path)
                    winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)

                winreg.CloseKey(key)
                return True

            else:
                # Linux/macOS: Add to shell profile
                shell_profile = Path.home() / '.bashrc'
                if self.system == "Darwin":
                    shell_profile = Path.home() / '.zshrc'

                export_line = f'\nexport PATH="$PATH:{install_path}"\n'

                with open(shell_profile, 'a') as f:
                    f.write(export_line)

                return True

        except Exception as e:
            print(f"Error adding to PATH: {e}")
            return False

    def _create_desktop_shortcut(self, install_path):
        """Create desktop shortcut"""
        try:
            desktop = Path.home() / 'Desktop'

            if self.system == "Windows":
                # Windows shortcut
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(str(desktop / "SamFWTool.lnk"))
                shortcut.Targetpath = sys.executable
                shortcut.Arguments = f'"{install_path / "samfwtool" / "gui" / "main_gui.py"}"'
                shortcut.WorkingDirectory = str(install_path)
                shortcut.IconLocation = sys.executable
                shortcut.save()

            elif self.system == "Darwin":
                # macOS .command file
                launcher = desktop / "SamFWTool.command"
                launcher.write_text(f'#!/bin/bash\ncd "{install_path}"\n{sys.executable} -m samfwtool.gui.main_gui\n')
                launcher.chmod(0o755)

            else:
                # Linux .desktop file
                desktop_file = desktop / "SamFWTool.desktop"
                desktop_file.write_text(f"""[Desktop Entry]
Type=Application
Name=SamFWTool
Comment=Universal Firmware Toolkit
Exec={sys.executable} -m samfwtool.gui.main_gui
Icon={install_path}/icon.png
Terminal=false
Categories=Development;Utility;
""")
                desktop_file.chmod(0o755)

            return True

        except Exception as e:
            print(f"Error creating shortcut: {e}")
            return False

    def _create_launcher(self, install_path):
        """Create launcher scripts"""
        # CLI launcher
        if self.system == "Windows":
            launcher = install_path / "samfwtool.bat"
            launcher.write_text(f'@echo off\n{sys.executable} -m samfwtool.cli.main %*\n')
        else:
            launcher = install_path / "samfwtool"
            launcher.write_text(f'#!/bin/bash\n{sys.executable} -m samfwtool.cli.main "$@"\n')
            launcher.chmod(0o755)

        # GUI launcher
        if self.system == "Windows":
            gui_launcher = install_path / "samfwtool-gui.bat"
            gui_launcher.write_text(f'@echo off\nstart {sys.executable} -m samfwtool.gui.main_gui\n')
        else:
            gui_launcher = install_path / "samfwtool-gui"
            gui_launcher.write_text(f'#!/bin/bash\n{sys.executable} -m samfwtool.gui.main_gui &\n')
            gui_launcher.chmod(0o755)

    def _next_step(self):
        """Go to next step"""
        steps = [
            self._show_requirements,
            self._show_installation_path,
            self._show_installation,
            self._show_complete,
        ]

        if self.current_step < len(steps):
            steps[self.current_step]()
            # Don't override button states here - each step manages its own button states

    def _prev_step(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 2  # Will be incremented in _next_step
            self._next_step()

    def _cancel(self):
        """Cancel installation"""
        if messagebox.askyesno("Cancel Installation", "Are you sure you want to cancel?"):
            self.root.quit()

    def _launch_app(self):
        """Launch application"""
        try:
            install_path = Path(self.path_var.get())
            gui_script = install_path / "samfwtool" / "gui" / "main_gui.py"

            if gui_script.exists():
                subprocess.Popen([sys.executable, str(gui_script)])
                self.root.quit()
            else:
                messagebox.showerror("Error", "GUI script not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch: {e}")


def main():
    """Main entry point"""
    root = tk.Tk()

    # Configure style
    style = ttk.Style()
    style.theme_use('clam')

    wizard = InstallationWizard(root)
    root.mainloop()


if __name__ == '__main__':
    main()
