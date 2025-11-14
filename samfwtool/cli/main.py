"""
SamFWTool CLI - Main entry point
Advanced command-line interface surpassing Odin
"""
import click
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from samfwtool import __version__
from samfwtool.core.parser import FirmwareParser
from samfwtool.core.extractor import FirmwareExtractor
from samfwtool.analysis.security import SecurityScanner
from samfwtool.analysis.diff import FirmwareDiff
from samfwtool.tools.bootimg import BootImageTool

console = Console()


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
@click.argument('firmware_path', type=click.Path(exists=True))
@click.option('--detailed', '-d', is_flag=True, help='Show detailed partition information')
def info(firmware_path, detailed):
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
        console.print(f"[green]Size:[/green] {firmware_info.size:,} bytes ({firmware_info.size/(1024*1024):.2f} MB)")
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
            row = [
                partition.name,
                partition.type,
                size_mb,
                partition.format
            ]

            if detailed:
                row.append(partition.compression or "none")
                row.append(partition.checksum[:16] + "..." if partition.checksum else "N/A")

            table.add_row(*row)

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.argument('firmware_path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), required=True, help='Output directory')
@click.option('--partition', '-p', help='Extract specific partition only')
@click.option('--decompress/--no-decompress', default=True, help='Automatically decompress files')
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
@click.argument('firmware_dir', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output report path (JSON)')
@click.option('--deep', is_flag=True, help='Perform deep security analysis')
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

        # Return non-zero if critical/high findings
        critical_high = [f for f in findings
                        if f.severity.value in ['critical', 'high']]
        if critical_high:
            sys.exit(len(critical_high))

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.argument('old_firmware', type=click.Path(exists=True))
@click.argument('new_firmware', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output diff report (JSON)')
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
@click.argument('boot_image', type=click.Path(exists=True))
@click.option('--extract-kernel', type=click.Path(), help='Extract kernel to file')
@click.option('--extract-ramdisk', type=click.Path(), help='Extract ramdisk to file')
@click.option('--info', is_flag=True, help='Show boot image information')
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
def compare():
    """
    Show comparison between SamFWTool and Odin

    Displays a comprehensive feature comparison table.
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


if __name__ == '__main__':
    cli()
