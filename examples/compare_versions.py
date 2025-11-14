#!/usr/bin/env python3
"""
Example: Compare two firmware versions
"""
import sys
from pathlib import Path
from samfwtool.analysis.diff import FirmwareDiff


def main():
    if len(sys.argv) != 3:
        print("Usage: python compare_versions.py <old_firmware> <new_firmware>")
        sys.exit(1)

    old_firmware = sys.argv[1]
    new_firmware = sys.argv[2]

    print("="*70)
    print("SamFWTool - Firmware Version Comparison")
    print("="*70)

    # Create differ
    differ = FirmwareDiff(old_firmware, new_firmware)

    # Perform comparison
    result = differ.compare()

    # Export detailed report
    report_file = "firmware_diff.json"
    differ.export_diff_report(Path(report_file))

    print(f"\nDetailed report saved to: {report_file}")

    # Highlight major changes
    print("\n" + "="*70)
    print("MAJOR CHANGES")
    print("="*70)

    # Show largest additions
    if result.files_added:
        largest_additions = sorted(result.files_added,
                                  key=lambda x: x.new_size or 0,
                                  reverse=True)[:5]
        print("\nLargest new files:")
        for f in largest_additions:
            print(f"  + {f.path} ({f.new_size/(1024*1024):.2f} MB)")

    # Show largest modifications
    if result.files_modified:
        largest_changes = sorted(result.files_modified,
                               key=lambda x: abs(x.size_change or 0),
                               reverse=True)[:5]
        print("\nLargest modifications:")
        for f in largest_changes:
            change_mb = (f.size_change or 0) / (1024*1024)
            print(f"  ~ {f.path} ({change_mb:+.2f} MB)")

    print("\nDone!")


if __name__ == '__main__':
    main()
