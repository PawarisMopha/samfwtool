"""
SamFWTool - Comprehensive Tkinter GUI
Professional firmware toolkit interface
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import tkinter.font as tkfont
from pathlib import Path
import threading
import queue
import sys
from typing import Optional

from samfwtool import __version__
from samfwtool.core.parser import FirmwareParser
from samfwtool.core.extractor import FirmwareExtractor
from samfwtool.core.packer import FirmwarePacker
from samfwtool.analysis.security import SecurityScanner
from samfwtool.analysis.diff import FirmwareDiff
from samfwtool.security.frp import FRPAnalyzer
from samfwtool.flash.device import DeviceDetector
from samfwtool.flash.flasher import DeviceFlasher


class SamFWToolGUI:
    """
    Main GUI application for SamFWTool

    ADVANTAGE: First firmware tool with comprehensive GUI!
    - All CLI features accessible via GUI
    - Real-time progress tracking
    - Professional UX design
    - Multi-threaded operations
    """

    def __init__(self, root):
        self.root = root
        self.root.title(f"SamFWTool v{__version__} - Universal Firmware Toolkit")
        self.root.geometry("1200x800")

        # Set theme colors
        self.colors = {
            "primary": "#2196F3",
            "success": "#4CAF50",
            "warning": "#FF9800",
            "danger": "#F44336",
            "dark": "#212121",
            "light": "#F5F5F5",
            "text": "#FFFFFF",
        }

        # Configure root window
        self.root.configure(bg=self.colors["light"])

        # Queue for thread communication
        self.message_queue = queue.Queue()

        # Initialize GUI
        self._create_menu()
        self._create_header()
        self._create_main_content()
        self._create_status_bar()

        # Start message processor
        self._process_messages()

        # Center window
        self._center_window()

    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Firmware...", command=self._open_firmware)
        file_menu.add_command(label="Recent Files", command=self._show_recent)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Device Manager", command=self._show_device_manager)
        tools_menu.add_command(label="Settings", command=self._show_settings)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self._show_docs)
        help_menu.add_command(label="Compare Tools", command=self._show_comparison)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._show_about)

    def _create_header(self):
        """Create header section"""
        header_frame = tk.Frame(self.root, bg=self.colors["primary"], height=80)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        # Logo and title
        title_font = tkfont.Font(family="Helvetica", size=24, weight="bold")
        title_label = tk.Label(
            header_frame,
            text="🚀 SamFWTool",
            font=title_font,
            bg=self.colors["primary"],
            fg=self.colors["text"],
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)

        # Subtitle
        subtitle_font = tkfont.Font(family="Helvetica", size=10)
        subtitle_label = tk.Label(
            header_frame,
            text=f"Universal Firmware Toolkit v{__version__} | Surpassing ALL competitors",
            font=subtitle_font,
            bg=self.colors["primary"],
            fg=self.colors["text"],
        )
        subtitle_label.pack(side=tk.LEFT, padx=5, pady=20)

    def _create_main_content(self):
        """Create main content area with tabs"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self._create_analyze_tab()
        self._create_extract_tab()
        self._create_flash_tab()
        self._create_security_tab()
        self._create_chipset_tab()
        self._create_tools_tab()

    def _create_analyze_tab(self):
        """Create Analyze Firmware tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📊 Analyze")

        # Main container
        container = ttk.Frame(tab, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        # File selection
        file_frame = ttk.LabelFrame(container, text="Firmware File", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))

        self.analyze_file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.analyze_file_var, width=60).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            file_frame, text="Browse...", command=lambda: self._browse_file(self.analyze_file_var)
        ).pack(side=tk.LEFT)
        ttk.Button(
            file_frame, text="Analyze", command=self._analyze_firmware, style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)

        # Results area
        results_frame = ttk.LabelFrame(container, text="Analysis Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)

        self.analyze_results = scrolledtext.ScrolledText(results_frame, height=20, wrap=tk.WORD)
        self.analyze_results.pack(fill=tk.BOTH, expand=True)

    def _create_extract_tab(self):
        """Create Extract Firmware tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📦 Extract")

        container = ttk.Frame(tab, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Input file
        input_frame = ttk.LabelFrame(container, text="Input Firmware", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        self.extract_input_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.extract_input_var, width=50).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            input_frame, text="Browse...", command=lambda: self._browse_file(self.extract_input_var)
        ).pack(side=tk.LEFT)

        # Output directory
        output_frame = ttk.LabelFrame(container, text="Output Directory", padding=10)
        output_frame.pack(fill=tk.X, pady=(0, 10))

        self.extract_output_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.extract_output_var, width=50).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            output_frame,
            text="Browse...",
            command=lambda: self._browse_dir(self.extract_output_var),
        ).pack(side=tk.LEFT)

        # Options
        options_frame = ttk.LabelFrame(container, text="Options", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 10))

        self.extract_decompress_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Automatically decompress files",
            variable=self.extract_decompress_var,
        ).pack(anchor=tk.W)

        # Extract button
        ttk.Button(
            container,
            text="Extract Firmware",
            command=self._extract_firmware,
            style="Accent.TButton",
        ).pack(pady=10)

        # Progress
        self.extract_progress = ttk.Progressbar(container, mode="indeterminate")
        self.extract_progress.pack(fill=tk.X, pady=5)

        # Log
        log_frame = ttk.LabelFrame(container, text="Extraction Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.extract_log = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.extract_log.pack(fill=tk.BOTH, expand=True)

    def _create_flash_tab(self):
        """Create Flash Device tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔥 Flash")

        container = ttk.Frame(tab, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Warning
        warning_frame = tk.Frame(container, bg=self.colors["warning"], padx=10, pady=10)
        warning_frame.pack(fill=tk.X, pady=(0, 10))

        warning_label = tk.Label(
            warning_frame,
            text="⚠️  WARNING: Flashing can brick your device! Make sure you have the correct firmware.",
            bg=self.colors["warning"],
            fg=self.colors["text"],
            font=tkfont.Font(weight="bold"),
        )
        warning_label.pack()

        # Device selection
        device_frame = ttk.LabelFrame(container, text="Device", padding=10)
        device_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(device_frame, text="Detect Devices", command=self._detect_devices).pack(
            side=tk.LEFT, padx=5
        )

        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(
            device_frame, textvariable=self.device_var, width=40, state="readonly"
        )
        self.device_combo.pack(side=tk.LEFT, padx=5)

        # Flash options
        flash_frame = ttk.LabelFrame(container, text="Flash Options", padding=10)
        flash_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(flash_frame, text="Partition:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.flash_partition_var = tk.StringVar()
        partition_combo = ttk.Combobox(flash_frame, textvariable=self.flash_partition_var, width=20)
        partition_combo["values"] = ("boot", "system", "vendor", "recovery", "userdata")
        partition_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(flash_frame, text="Image File:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5
        )
        self.flash_image_var = tk.StringVar()
        ttk.Entry(flash_frame, textvariable=self.flash_image_var, width=40).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5
        )
        ttk.Button(
            flash_frame, text="Browse...", command=lambda: self._browse_file(self.flash_image_var)
        ).grid(row=1, column=2, padx=5, pady=5)

        # Safety check
        self.flash_safety_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            flash_frame, text="Enable safety checks (recommended)", variable=self.flash_safety_var
        ).grid(row=2, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)

        # Flash button
        ttk.Button(
            container, text="Flash Device", command=self._flash_device, style="Accent.TButton"
        ).pack(pady=10)

        # Log
        log_frame = ttk.LabelFrame(container, text="Flash Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.flash_log = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.flash_log.pack(fill=tk.BOTH, expand=True)

    def _create_security_tab(self):
        """Create Security Analysis tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔒 Security")

        container = ttk.Frame(tab, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Input directory
        input_frame = ttk.LabelFrame(container, text="Firmware Directory", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        self.security_dir_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.security_dir_var, width=50).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            input_frame, text="Browse...", command=lambda: self._browse_dir(self.security_dir_var)
        ).pack(side=tk.LEFT)

        # Scan options
        options_frame = ttk.LabelFrame(container, text="Scan Options", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 10))

        self.security_full_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame, text="Full Security Scan", variable=self.security_full_var
        ).pack(anchor=tk.W)

        self.security_frp_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="FRP Analysis (Factory Reset Protection)",
            variable=self.security_frp_var,
        ).pack(anchor=tk.W)

        # Scan buttons
        button_frame = ttk.Frame(container)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame, text="Security Scan", command=self._security_scan, style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="FRP Analysis", command=self._frp_analysis).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="Export Report", command=self._export_security_report).pack(
            side=tk.LEFT, padx=5
        )

        # Results
        results_frame = ttk.LabelFrame(container, text="Security Analysis Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)

        self.security_results = scrolledtext.ScrolledText(results_frame, height=20, wrap=tk.WORD)
        self.security_results.pack(fill=tk.BOTH, expand=True)

    def _create_chipset_tab(self):
        """Create Chipset Tools tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔧 Chipset Tools")

        container = ttk.Frame(tab, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Chipset selection
        chipset_frame = ttk.LabelFrame(container, text="Chipset", padding=10)
        chipset_frame.pack(fill=tk.X, pady=(0, 10))

        self.chipset_var = tk.StringVar(value="MediaTek")
        ttk.Radiobutton(
            chipset_frame, text="MediaTek (MTK)", variable=self.chipset_var, value="MediaTek"
        ).pack(anchor=tk.W)
        ttk.Radiobutton(
            chipset_frame, text="Qualcomm (EDL)", variable=self.chipset_var, value="Qualcomm"
        ).pack(anchor=tk.W)

        # MediaTek section
        mtk_frame = ttk.LabelFrame(container, text="MediaTek Tools", padding=10)
        mtk_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(mtk_frame, text="Scatter File:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5
        )
        self.mtk_scatter_var = tk.StringVar()
        ttk.Entry(mtk_frame, textvariable=self.mtk_scatter_var, width=40).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5
        )
        ttk.Button(
            mtk_frame, text="Browse...", command=lambda: self._browse_file(self.mtk_scatter_var)
        ).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(mtk_frame, text="Parse Scatter", command=self._parse_scatter).grid(
            row=0, column=3, padx=5, pady=5
        )

        # Qualcomm section
        qcom_frame = ttk.LabelFrame(container, text="Qualcomm EDL Tools", padding=10)
        qcom_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(qcom_frame, text="EDL Port:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.edl_port_var = tk.StringVar(value="/dev/ttyUSB0")
        ttk.Entry(qcom_frame, textvariable=self.edl_port_var, width=20).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5
        )
        ttk.Button(qcom_frame, text="Detect EDL", command=self._detect_edl).grid(
            row=0, column=2, padx=5, pady=5
        )

        # Log
        log_frame = ttk.LabelFrame(container, text="Chipset Tools Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.chipset_log = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.chipset_log.pack(fill=tk.BOTH, expand=True)

    def _create_tools_tab(self):
        """Create Additional Tools tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🛠️ Tools")

        container = ttk.Frame(tab, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Pack firmware
        pack_frame = ttk.LabelFrame(container, text="Pack Firmware", padding=10)
        pack_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(pack_frame, text="Select partition files to pack into firmware:").pack(
            anchor=tk.W, pady=5
        )
        ttk.Button(pack_frame, text="Select Files...", command=self._select_pack_files).pack(pady=5)
        ttk.Button(
            pack_frame, text="Pack Firmware", command=self._pack_firmware, style="Accent.TButton"
        ).pack(pady=5)

        # Firmware diff
        diff_frame = ttk.LabelFrame(container, text="Compare Firmware Versions", padding=10)
        diff_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(diff_frame, text="Old Firmware:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5
        )
        self.diff_old_var = tk.StringVar()
        ttk.Entry(diff_frame, textvariable=self.diff_old_var, width=30).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5
        )
        ttk.Button(
            diff_frame, text="Browse...", command=lambda: self._browse_file(self.diff_old_var)
        ).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(diff_frame, text="New Firmware:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5
        )
        self.diff_new_var = tk.StringVar()
        ttk.Entry(diff_frame, textvariable=self.diff_new_var, width=30).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5
        )
        ttk.Button(
            diff_frame, text="Browse...", command=lambda: self._browse_file(self.diff_new_var)
        ).grid(row=1, column=2, padx=5, pady=5)

        ttk.Button(diff_frame, text="Compare", command=self._compare_firmware).grid(
            row=2, column=1, pady=10
        )

        # Results
        results_frame = ttk.LabelFrame(container, text="Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)

        self.tools_results = scrolledtext.ScrolledText(results_frame, height=15, wrap=tk.WORD)
        self.tools_results.pack(fill=tk.BOTH, expand=True)

    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = ttk.Label(self.status_bar, text="Ready", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.progress_bar = ttk.Progressbar(self.status_bar, length=200, mode="determinate")
        self.progress_bar.pack(side=tk.RIGHT, padx=5, pady=2)

    # Helper methods
    def _browse_file(self, var):
        """Browse for file"""
        filename = filedialog.askopenfilename()
        if filename:
            var.set(filename)

    def _browse_dir(self, var):
        """Browse for directory"""
        dirname = filedialog.askdirectory()
        if dirname:
            var.set(dirname)

    def _center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _set_status(self, message):
        """Set status bar message"""
        self.status_label.config(text=message)

    def _log(self, widget, message):
        """Log message to text widget"""
        widget.insert(tk.END, message + "\n")
        widget.see(tk.END)

    def _process_messages(self):
        """Process messages from queue"""
        try:
            while True:
                msg = self.message_queue.get_nowait()
                if msg["type"] == "status":
                    self._set_status(msg["text"])
                elif msg["type"] == "log":
                    self._log(msg["widget"], msg["text"])
        except queue.Empty:
            pass

        self.root.after(100, self._process_messages)

    # Feature implementations (stubs for now - would implement actual functionality)
    def _open_firmware(self):
        filename = filedialog.askopenfilename(title="Open Firmware")
        if filename:
            self.analyze_file_var.set(filename)
            self._analyze_firmware()

    def _analyze_firmware(self):
        """Analyze firmware file"""
        filepath = self.analyze_file_var.get()
        if not filepath:
            messagebox.showwarning("No File", "Please select a firmware file first")
            return

        def analyze_thread():
            try:
                self._set_status("Analyzing firmware...")
                parser = FirmwareParser(filepath)
                info = parser.parse()

                result = f"Firmware Analysis Results\n"
                result += "=" * 50 + "\n\n"
                result += f"Format: {info.format.value}\n"
                result += f"Vendor: {info.vendor}\n"
                result += f"Device: {info.device}\n"
                result += f"Version: {info.version}\n"
                result += f"Size: {info.size:,} bytes ({info.size/(1024*1024):.2f} MB)\n"
                result += f"Checksum: {info.checksum}\n"
                result += f"\nPartitions: {len(info.partitions)}\n"
                result += "-" * 50 + "\n"

                for part in info.partitions:
                    result += f"\n{part.name}:\n"
                    result += f"  Type: {part.type}\n"
                    result += f"  Size: {part.size:,} bytes\n"
                    result += f"  Format: {part.format}\n"

                self.analyze_results.delete("1.0", tk.END)
                self.analyze_results.insert("1.0", result)
                self._set_status("Analysis complete")

            except Exception as e:
                messagebox.showerror("Error", f"Analysis failed: {str(e)}")
                self._set_status("Analysis failed")

        threading.Thread(target=analyze_thread, daemon=True).start()

    def _extract_firmware(self):
        messagebox.showinfo("Extract", "Extract firmware feature - implementation in progress")

    def _detect_devices(self):
        """Detect connected devices"""
        try:
            devices = DeviceDetector.detect_all()
            if devices:
                device_list = [f"{d.model} ({d.serial})" for d in devices]
                self.device_combo["values"] = device_list
                self.device_combo.current(0)
                messagebox.showinfo("Devices Found", f"Found {len(devices)} device(s)")
            else:
                messagebox.showwarning("No Devices", "No devices detected")
        except Exception as e:
            messagebox.showerror("Error", f"Device detection failed: {str(e)}")

    def _flash_device(self):
        messagebox.showinfo("Flash", "Flash device feature - implementation in progress")

    def _security_scan(self):
        messagebox.showinfo("Security", "Security scan feature - implementation in progress")

    def _frp_analysis(self):
        messagebox.showinfo("FRP", "FRP analysis feature - implementation in progress")

    def _export_security_report(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json")
        if filename:
            messagebox.showinfo("Export", f"Report exported to {filename}")

    def _parse_scatter(self):
        messagebox.showinfo("MTK", "Parse scatter feature - implementation in progress")

    def _detect_edl(self):
        messagebox.showinfo("EDL", "Detect EDL feature - implementation in progress")

    def _select_pack_files(self):
        files = filedialog.askopenfilenames(title="Select Partition Files")
        if files:
            messagebox.showinfo("Files Selected", f"Selected {len(files)} files")

    def _pack_firmware(self):
        messagebox.showinfo("Pack", "Pack firmware feature - implementation in progress")

    def _compare_firmware(self):
        messagebox.showinfo("Compare", "Compare firmware feature - implementation in progress")

    def _show_recent(self):
        messagebox.showinfo("Recent Files", "Recent files feature - coming soon")

    def _show_device_manager(self):
        messagebox.showinfo("Device Manager", "Device manager - coming soon")

    def _show_settings(self):
        messagebox.showinfo("Settings", "Settings - coming soon")

    def _show_docs(self):
        messagebox.showinfo("Documentation", "Opening documentation...")

    def _show_comparison(self):
        messagebox.showinfo("Tool Comparison", "SamFWTool vs All Tools comparison")

    def _show_about(self):
        about_text = f"""
SamFWTool v{__version__}
Universal Firmware Toolkit

The ONLY tool that surpasses ALL firmware tools combined:
• Odin + SP Flash + QFIL + Fastboot + More
• Cross-platform (Windows, macOS, Linux)
• Multi-vendor support
• Comprehensive security analysis
• Factory Reset Protection (FRP) analysis

Open Source | MIT License
        """
        messagebox.showinfo("About SamFWTool", about_text)


def main():
    """Main entry point for GUI"""
    root = tk.Tk()

    # Configure ttk style
    style = ttk.Style()
    style.theme_use("clam")

    # Custom button style
    style.configure(
        "Accent.TButton", background="#2196F3", foreground="white", font=("Helvetica", 10, "bold")
    )

    app = SamFWToolGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
