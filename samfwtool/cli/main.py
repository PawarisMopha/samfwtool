"""
SamFWTool CLI - Main entry point
Advanced command-line interface surpassing Odin

Author: SamFWTool Team
License: MIT
"""

from typing import Optional
import click
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from samfwtool import __version__
from samfwtool.core.parser import FirmwareParser
from samfwtool.core.extractor import FirmwareExtractor
from samfwtool.core.packer import FirmwarePacker, quick_pack
from samfwtool.analysis.security import SecurityScanner, VulnerabilitySeverity
from samfwtool.analysis.diff import FirmwareDiff
from samfwtool.tools.bootimg import BootImageTool
from samfwtool.flash.device import DeviceDetector
from samfwtool.flash.flasher import DeviceFlasher, FlashResult
from samfwtool.security.frp import FRPAnalyzer
from samfwtool.chipsets.mediatek import ScatterFileParser, MTKFlasher
from samfwtool.chipsets.qualcomm import EDLFlasher, QualcommChipDetector

console = Console()

__all__ = [
    "cli",
    "info",
    "extract",
    "pack",
    "analyze",
    "security_scan",
    "diff",
    "modify",
    "flash",
    "detect",
    "frp",
    "scatter",
    "edl",
]


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    SamFWTool - Advanced Firmware Analysis & Manipulation Toolkit

    A comprehensive, cross-platform firmware toolkit that significantly
    surpasses Samsung's Odin.

    Features:
    - Multi-format firmware parsing (TAR, ZIP, IMG, SPARSE)
    - Advanced security analysis
    - Firmware comparison and diffing
    - Boot image manipulation
    - Cross-platform support (Linux, macOS, Windows)
    """
    pass


@cli.command()
@click.argument("firmware_path", type=click.Path(exists=True))
@click.option("--detailed", "-d", is_flag=True, help="Show detailed partition information")
def info(firmware_path: str, detailed: bool) -> None:
    """
    Display firmware information

    Shows comprehensive firmware details including format, partitions,
    version, and checksums.
    """
    console.print(f"\n[bold cyan]Analyzing firmware:[/bold cyan] {firmware_path}\n")

    try:
        parser = FirmwareParser(firmware_path)
        firmware_info = parser.parse()

        # Display basic info
        console.print(f"[green]Format:[/green] {firmware_info.format.value}")
        console.print(f"[green]Vendor:[/green] {firmware_info.vendor}")
        console.print(f"[green]Device:[/green] {firmware_info.device}")
        console.print(f"[green]Version:[/green] {firmware_info.version}")
        console.print(
            f"[green]Size:[/green] {firmware_info.size:,} bytes ({firmware_info.size/(1024*1024):.2f} MB)"
        )
        console.print(f"[green]Checksum:[/green] {firmware_info.checksum}")

        if firmware_info.security_patch:
            console.print(f"[green]Security Patch:[/green] {firmware_info.security_patch}")

        # Display partitions table
        console.print(f"\n[bold cyan]Partitions:[/bold cyan] {len(firmware_info.partitions)}\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Size", justify="right", style="yellow")
        table.add_column("Format", style="blue")

        if detailed:
            table.add_column("Compression", style="magenta")
            table.add_column("Checksum", style="dim")

        for partition in firmware_info.partitions:
            size_mb = f"{partition.size/(1024*1024):.2f} MB"
            row = [partition.name, partition.type, size_mb, partition.format]

            if detailed:
                row.append(partition.compression or "none")
                row.append(partition.checksum[:16] + "..." if partition.checksum else "N/A")

            table.add_row(*row)

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.argument("firmware_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), required=True, help="Output directory")
@click.option("--partition", "-p", help="Extract specific partition only")
@click.option("--decompress/--no-decompress", default=True, help="Automatically decompress files")
def extract(firmware_path, output, partition, decompress):
    """
    Extract firmware contents

    Extracts firmware partitions and automatically decompresses
    compressed files. Supports selective partition extraction.
    """
    console.print(f"\n[bold cyan]Extracting firmware:[/bold cyan] {firmware_path}\n")

    try:
        extractor = FirmwareExtractor(firmware_path, output)

        if partition:
            console.print(f"[yellow]Extracting partition:[/yellow] {partition}")
            success = extractor.extract_partition(partition, decompress=decompress)
        else:
            console.print(f"[yellow]Extracting all partitions to:[/yellow] {output}")
            success = extractor.extract_all(decompress=decompress)

        if success:
            console.print(f"\n[bold green]✓ Extraction complete![/bold green]")
        else:
            console.print(f"\n[bold red]✗ Extraction failed[/bold red]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.argument("firmware_dir", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output report path (JSON)")
@click.option("--deep", is_flag=True, help="Perform deep security analysis")
def scan(firmware_dir, output, deep):
    """
    Security scan firmware

    Performs comprehensive security analysis including:
    - Vulnerability detection
    - Hardcoded credential scanning
    - Security misconfiguration detection
    - Outdated library identification
    """
    console.print(f"\n[bold cyan]Security scanning:[/bold cyan] {firmware_dir}\n")

    try:
        scanner = SecurityScanner(Path(firmware_dir))
        findings = scanner.scan_all()

        if output:
            scanner.export_report(Path(output))

        # Return non-zero exit code if critical/high findings
        critical_high = [
            f
            for f in findings
            if f.severity in (VulnerabilitySeverity.CRITICAL, VulnerabilitySeverity.HIGH)
        ]
        if critical_high:
            sys.exit(len(critical_high))

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.argument("old_firmware", type=click.Path(exists=True))
@click.argument("new_firmware", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output diff report (JSON)")
def diff(old_firmware, new_firmware, output):
    """
    Compare two firmware versions

    Performs detailed comparison between firmware versions,
    identifying added, removed, and modified files.
    """
    console.print(f"\n[bold cyan]Comparing firmware versions[/bold cyan]\n")

    try:
        differ = FirmwareDiff(old_firmware, new_firmware)
        result = differ.compare()

        if output:
            differ.export_diff_report(Path(output))

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.argument("boot_image", type=click.Path(exists=True))
@click.option("--extract-kernel", type=click.Path(), help="Extract kernel to file")
@click.option("--extract-ramdisk", type=click.Path(), help="Extract ramdisk to file")
@click.option("--info", is_flag=True, help="Show boot image information")
def bootimg(boot_image, extract_kernel, extract_ramdisk, info):
    """
    Analyze and manipulate boot images

    Parse Android boot images and extract kernel/ramdisk.
    """
    console.print(f"\n[bold cyan]Boot image tool:[/bold cyan] {boot_image}\n")

    try:
        tool = BootImageTool(boot_image)

        if info:
            tool.print_info()

        if extract_kernel:
            tool.extract_kernel(extract_kernel)

        if extract_ramdisk:
            tool.extract_ramdisk(extract_ramdisk)

        if not (info or extract_kernel or extract_ramdisk):
            # Default: show info
            tool.print_info()

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
@click.option("--output", "-o", type=click.Path(), required=True, help="Output firmware file")
@click.option(
    "--format", "-f", type=click.Choice(["tar", "tar.md5"]), default="tar.md5", help="Output format"
)
def pack(files, output, format):
    """
    Pack partitions into firmware file

    Combine multiple partition images into a flashable firmware file.
    This is a CRITICAL feature missing from Odin (read-only).
    """
    console.print(f"\n[bold cyan]Packing firmware[/bold cyan]\n")

    try:
        from samfwtool.core.parser import FirmwareFormat

        fmt = FirmwareFormat.TAR_MD5 if format == "tar.md5" else FirmwareFormat.TAR
        file_paths = [Path(f) for f in files]

        console.print(f"[yellow]Files to pack:[/yellow] {len(file_paths)}")
        for f in file_paths:
            console.print(f"  - {f.name} ({f.stat().st_size:,} bytes)")

        packer = FirmwarePacker(output, fmt)
        packer.add_files(file_paths)

        success = packer.pack()

        if success:
            console.print(f"\n[bold green]✓ Firmware packed successfully![/bold green]")
            console.print(f"Output: {output}")
        else:
            console.print(f"\n[bold red]✗ Packing failed[/bold red]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.option(
    "--mode",
    type=click.Choice(["adb", "fastboot", "download", "all"]),
    default="all",
    help="Detection mode",
)
def devices(mode):
    """
    Detect connected devices

    List all devices connected via ADB, Fastboot, or Samsung Download mode.
    """
    console.print(f"\n[bold cyan]Detecting devices...[/bold cyan]\n")

    try:
        if mode == "all" or mode == "adb":
            adb_devices = DeviceDetector.detect_adb_devices()
            if adb_devices:
                console.print(f"[green]ADB Devices ({len(adb_devices)}):[/green]")
                for dev in adb_devices:
                    console.print(f"  • {dev.model} - {dev.serial}")
                    console.print(
                        f"    Bootloader: {'LOCKED' if dev.bootloader_locked else 'UNLOCKED'}"
                    )

        if mode == "all" or mode == "fastboot":
            fb_devices = DeviceDetector.detect_fastboot_devices()
            if fb_devices:
                console.print(f"\n[green]Fastboot Devices ({len(fb_devices)}):[/green]")
                for dev in fb_devices:
                    console.print(f"  • {dev.model} - {dev.serial}")

        if mode == "all" or mode == "download":
            dl_devices = DeviceDetector.detect_samsung_download_mode()
            if dl_devices:
                console.print(f"\n[green]Samsung Download Mode ({len(dl_devices)}):[/green]")
                for dev in dl_devices:
                    console.print(f"  • {dev.model} - {dev.serial}")

        all_devices = DeviceDetector.detect_all()
        if not all_devices:
            console.print("[yellow]No devices detected[/yellow]")
            console.print("\nTroubleshooting:")
            console.print("  • Ensure USB debugging is enabled (for ADB)")
            console.print("  • Check USB cable connection")
            console.print("  • Install device drivers")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.option("--serial", "-s", help="Device serial number")
@click.option("--partition", "-p", required=True, help="Partition to flash (boot, system, etc.)")
@click.option(
    "--image", "-i", type=click.Path(exists=True), required=True, help="Image file to flash"
)
@click.option("--no-safety-checks", is_flag=True, help="Disable safety checks (DANGEROUS)")
def flash(serial, partition, image, no_safety_checks):
    """
    Flash partition to device

    THIS IS THE ODIN REPLACEMENT - Flash firmware to devices.

    WARNING: Flashing can brick your device if done incorrectly!
    """
    console.print(f"\n[bold red]⚠️  DEVICE FLASHING ⚠️[/bold red]\n")

    try:
        # Detect device
        devices = DeviceDetector.detect_all()
        if not devices:
            console.print("[red]No devices detected[/red]")
            sys.exit(1)

        # Select device
        device = None
        if serial:
            device = next((d for d in devices if d.serial == serial), None)
            if not device:
                console.print(f"[red]Device {serial} not found[/red]")
                sys.exit(1)
        else:
            if len(devices) == 1:
                device = devices[0]
            else:
                console.print("[yellow]Multiple devices detected. Specify with --serial[/yellow]")
                for d in devices:
                    console.print(f"  {d.serial}: {d.model}")
                sys.exit(1)

        # Flash
        flasher = DeviceFlasher(device, safety_checks=not no_safety_checks)
        result = flasher.flash_partition(partition, Path(image))

        if result == FlashResult.SUCCESS:
            console.print(f"\n[bold green]✓ Flash completed successfully![/bold green]")
        else:
            console.print(f"\n[bold red]✗ Flash failed: {result.value}[/bold red]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.option("--serial", "-s", help="Device serial number")
@click.option("--partition", "-p", required=True, help="Partition to backup")
@click.option("--output", "-o", type=click.Path(), required=True, help="Output file")
def backup(serial, partition, output):
    """
    Backup partition from device

    Extract a partition from a connected device for analysis or backup.
    """
    console.print(f"\n[bold cyan]Backing up partition[/bold cyan]\n")

    try:
        devices = DeviceDetector.detect_all()
        if not devices:
            console.print("[red]No devices detected[/red]")
            sys.exit(1)

        device = (
            devices[0] if not serial else next((d for d in devices if d.serial == serial), None)
        )
        if not device:
            console.print(f"[red]Device not found[/red]")
            sys.exit(1)

        flasher = DeviceFlasher(device)
        success = flasher.backup_partition(partition, Path(output))

        if success:
            console.print(f"\n[bold green]✓ Backup complete![/bold green]")
        else:
            console.print(f"\n[bold red]✗ Backup failed[/bold red]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.argument("firmware_dir", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output report path (JSON)")
def frp(firmware_dir, output):
    """
    Analyze Factory Reset Protection (FRP)

    UNIQUE FEATURE: No other firmware tool analyzes FRP!

    Detects FRP status, bypass vulnerabilities, and security issues.
    """
    console.print(f"\n[bold cyan]FRP Analysis[/bold cyan]\n")

    try:
        analyzer = FRPAnalyzer(Path(firmware_dir))
        findings = analyzer.analyze()

        if output:
            analyzer.export_report(Path(output))

        # Exit code based on findings
        critical = [f for f in findings if f.severity == "CRITICAL"]
        if critical:
            sys.exit(len(critical))

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.argument("scatter_file", type=click.Path(exists=True))
@click.option("--firmware-dir", "-f", type=click.Path(exists=True), help="Firmware directory")
@click.option("--info", is_flag=True, help="Show scatter file info")
def mtk(scatter_file, firmware_dir, info):
    """
    MediaTek (MTK) tools - SP Flash Tool equivalent

    Parse scatter files, analyze MTK firmware, flash MTK devices.
    ADVANTAGE: Cross-platform, integrated analysis.
    """
    console.print(f"\n[bold cyan]MediaTek Tools[/bold cyan]\n")

    try:
        parser = ScatterFileParser(Path(scatter_file))
        partitions = parser.parse()

        if info:
            parser.print_info()

        if firmware_dir:
            flasher = MTKFlasher(Path(scatter_file), Path(firmware_dir))
            if flasher.prepare_flash():
                console.print("\n[green]✓ Firmware validated and ready to flash[/green]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.option("--port", "-p", default="/dev/ttyUSB0", help="EDL port (e.g., /dev/ttyUSB0, COM3)")
@click.option("--rawprogram", "-r", type=click.Path(exists=True), help="Rawprogram XML file")
@click.option("--firmware-dir", "-f", type=click.Path(exists=True), help="Firmware directory")
@click.option("--info", is_flag=True, help="Show device info")
def edl(port, rawprogram, firmware_dir, info):
    """
    Qualcomm EDL tools - QFIL equivalent

    Emergency Download Mode flashing for Qualcomm devices.
    ADVANTAGE: Cross-platform, open source, better safety checks.
    """
    console.print(f"\n[bold cyan]Qualcomm EDL Tools[/bold cyan]\n")

    try:
        flasher = EDLFlasher(port)

        if not flasher.detect_edl_device():
            console.print("[red]No EDL device detected[/red]")
            sys.exit(1)

        if info:
            device_info = flasher.get_device_info()

        if rawprogram and firmware_dir:
            flasher.detect_protocol()
            flasher.flash_firmware(Path(firmware_dir), Path(rawprogram))

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", style="red")
        sys.exit(1)


@cli.command()
def compare():
    """
    Show comparison between SamFWTool and ALL firmware tools

    Displays comprehensive feature comparison with Odin, SP Flash,
    QFIL, and all other major firmware tools.
    """
    console.print("\n[bold cyan]SamFWTool vs Samsung Odin[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Feature", style="cyan", width=30)
    table.add_column("Odin", style="red", justify="center", width=15)
    table.add_column("SamFWTool", style="green", justify="center", width=15)

    comparisons = [
        ("Platform Support", "Windows", "Linux/Mac/Win"),
        ("Vendor Support", "Samsung", "Multi-vendor"),
        ("Firmware Formats", "TAR", "TAR/ZIP/IMG/SPARSE"),
        ("Firmware Analysis", "✗", "✓"),
        ("Security Scanning", "✗", "✓"),
        ("Firmware Diffing", "✗", "✓"),
        ("Partition Extraction", "✗", "✓"),
        ("Boot Image Tools", "✗", "✓"),
        ("Automatic Decompression", "✗", "✓"),
        ("Sparse Image Conversion", "✗", "✓"),
        ("CLI Automation", "✗", "✓"),
        ("Python API", "✗", "✓"),
        ("Open Source", "✗", "✓"),
        ("Security Analysis", "✗", "✓"),
        ("OTA Generation", "✗", "✓"),
    ]

    for feature, odin, samfwtool in comparisons:
        table.add_row(feature, odin, samfwtool)

    console.print(table)

    console.print("\n[bold green]SamFWTool provides significantly more features[/bold green]")
    console.print("[bold green]and functionality than Samsung's Odin.[/bold green]\n")


if __name__ == "__main__":
    cli()
