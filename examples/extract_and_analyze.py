#!/usr/bin/env python3
"""
Example: Extract firmware and perform security analysis
"""
from pathlib import Path
from samfwtool import FirmwareParser, FirmwareExtractor, SecurityScanner


def main():
    # Configuration
    firmware_file = "firmware.tar.md5"
    output_dir = "extracted_firmware"

    print("="*70)
    print("SamFWTool - Extract and Analyze Example")
    print("="*70)

    # Step 1: Parse firmware
    print("\n[1/3] Parsing firmware...")
    parser = FirmwareParser(firmware_file)
    info = parser.parse()

    print(f"  Format: {info.format.value}")
    print(f"  Vendor: {info.vendor}")
    print(f"  Device: {info.device}")
    print(f"  Version: {info.version}")
    print(f"  Partitions: {len(info.partitions)}")

    # Step 2: Extract firmware
    print(f"\n[2/3] Extracting firmware to {output_dir}...")
    extractor = FirmwareExtractor(firmware_file, output_dir)
    extractor.extract_all(decompress=True)

    # Step 3: Security scan
    print("\n[3/3] Running security scan...")
    scanner = SecurityScanner(Path(output_dir))
    findings = scanner.scan_all()

    # Export security report
    report_file = "security_report.json"
    scanner.export_report(Path(report_file))
    print(f"\nSecurity report saved to: {report_file}")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Firmware extracted: {output_dir}")
    print(f"Security findings: {len(findings)}")

    critical = [f for f in findings if f.severity.value == 'critical']
    high = [f for f in findings if f.severity.value == 'high']

    if critical:
        print(f"⚠️  CRITICAL issues found: {len(critical)}")
    if high:
        print(f"⚠️  HIGH severity issues found: {len(high)}")

    print("\nDone!")


if __name__ == '__main__':
    main()
