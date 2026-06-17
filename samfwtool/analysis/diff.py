"""
Firmware comparison and differential analysis
Advanced feature not available in Odin

Author: SamFWTool Team
License: MIT
"""

import os
import hashlib
import difflib
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from samfwtool.core.parser import FirmwareParser

__all__ = [
    "ChangeType",
    "FileDiff",
    "FirmwareDiffResult",
    "FirmwareDiff",
]


class ChangeType(Enum):
    """Types of changes between firmware versions"""

    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


@dataclass
class FileDiff:
    """Represents a difference in a single file"""

    path: str
    change_type: ChangeType
    old_size: Optional[int] = None
    new_size: Optional[int] = None
    old_hash: Optional[str] = None
    new_hash: Optional[str] = None
    size_change: Optional[int] = None


@dataclass
class FirmwareDiffResult:
    """Complete firmware diff result"""

    old_version: str
    new_version: str
    files_added: List[FileDiff]
    files_removed: List[FileDiff]
    files_modified: List[FileDiff]
    files_unchanged: int
    total_size_change: int
    summary: Dict[str, Any]  # Fixed typo: any -> Any


class FirmwareDiff:
    """
    Advanced firmware comparison and differential analysis

    Features:
    - Compare two firmware versions
    - Identify added, removed, and modified files
    - Calculate size differences
    - Generate delta information for OTA
    - Detailed partition-level comparison
    """

    def __init__(self, old_firmware: str, new_firmware: str):
        self.old_firmware = Path(old_firmware)
        self.new_firmware = Path(new_firmware)
        self.old_parser = FirmwareParser(str(self.old_firmware))
        self.new_parser = FirmwareParser(str(self.new_firmware))

    def compare(self, extract_dir: Optional[Path] = None) -> FirmwareDiffResult:
        """
        Compare two firmware versions

        Args:
            extract_dir: Optional directory containing extracted firmware

        Returns:
            Complete diff result
        """
        print(f"Comparing firmware versions...")
        print(f"  Old: {self.old_firmware.name}")
        print(f"  New: {self.new_firmware.name}")

        # Parse both firmware files
        old_info = self.old_parser.parse()
        new_info = self.new_parser.parse()

        print(f"\nOld firmware: {len(old_info.partitions)} partitions")
        print(f"New firmware: {len(new_info.partitions)} partitions")

        # Create partition maps
        old_parts = {p.name: p for p in old_info.partitions}
        new_parts = {p.name: p for p in new_info.partitions}

        # Find differences
        files_added = []
        files_removed = []
        files_modified = []
        files_unchanged_count = 0

        all_files = set(old_parts.keys()) | set(new_parts.keys())

        for filename in sorted(all_files):
            if filename in new_parts and filename not in old_parts:
                # Added file
                new_part = new_parts[filename]
                files_added.append(
                    FileDiff(
                        path=filename,
                        change_type=ChangeType.ADDED,
                        new_size=new_part.size,
                        new_hash=new_part.checksum,
                        size_change=new_part.size,
                    )
                )

            elif filename in old_parts and filename not in new_parts:
                # Removed file
                old_part = old_parts[filename]
                files_removed.append(
                    FileDiff(
                        path=filename,
                        change_type=ChangeType.REMOVED,
                        old_size=old_part.size,
                        old_hash=old_part.checksum,
                        size_change=-old_part.size,
                    )
                )

            else:
                # Exists in both - check if modified
                old_part = old_parts[filename]
                new_part = new_parts[filename]

                if old_part.size != new_part.size or old_part.checksum != new_part.checksum:
                    # Modified
                    files_modified.append(
                        FileDiff(
                            path=filename,
                            change_type=ChangeType.MODIFIED,
                            old_size=old_part.size,
                            new_size=new_part.size,
                            old_hash=old_part.checksum,
                            new_hash=new_part.checksum,
                            size_change=new_part.size - old_part.size,
                        )
                    )
                else:
                    # Unchanged
                    files_unchanged_count += 1

        # Calculate total size change
        total_size_change = sum(
            f.size_change or 0 for f in files_added + files_removed + files_modified
        )

        # Create summary
        summary = {
            "total_files_old": len(old_parts),
            "total_files_new": len(new_parts),
            "files_added": len(files_added),
            "files_removed": len(files_removed),
            "files_modified": len(files_modified),
            "files_unchanged": files_unchanged_count,
            "size_change_bytes": total_size_change,
            "size_change_mb": total_size_change / (1024 * 1024),
            "old_version": old_info.version,
            "new_version": new_info.version,
        }

        result = FirmwareDiffResult(
            old_version=old_info.version,
            new_version=new_info.version,
            files_added=files_added,
            files_removed=files_removed,
            files_modified=files_modified,
            files_unchanged=files_unchanged_count,
            total_size_change=total_size_change,
            summary=summary,
        )

        self._print_diff_summary(result)
        return result

    def _print_diff_summary(self, result: FirmwareDiffResult):
        """Print diff summary"""
        print("\n" + "=" * 70)
        print("FIRMWARE DIFF SUMMARY")
        print("=" * 70)

        print(f"\nVersion Change: {result.old_version} → {result.new_version}")
        print(f"\nFiles Changed:")
        print(f"  Added:     {len(result.files_added)}")
        print(f"  Removed:   {len(result.files_removed)}")
        print(f"  Modified:  {len(result.files_modified)}")
        print(f"  Unchanged: {result.files_unchanged}")

        print(
            f"\nSize Change: {result.total_size_change:+,} bytes ({result.total_size_change/(1024*1024):+.2f} MB)"
        )

        # Show added files
        if result.files_added:
            print("\n" + "-" * 70)
            print("ADDED FILES:")
            print("-" * 70)
            for diff in result.files_added[:10]:  # Show first 10
                print(f"  + {diff.path} ({diff.new_size:,} bytes)")
            if len(result.files_added) > 10:
                print(f"  ... and {len(result.files_added) - 10} more")

        # Show removed files
        if result.files_removed:
            print("\n" + "-" * 70)
            print("REMOVED FILES:")
            print("-" * 70)
            for diff in result.files_removed[:10]:
                print(f"  - {diff.path} ({diff.old_size:,} bytes)")
            if len(result.files_removed) > 10:
                print(f"  ... and {len(result.files_removed) - 10} more")

        # Show modified files
        if result.files_modified:
            print("\n" + "-" * 70)
            print("MODIFIED FILES:")
            print("-" * 70)
            for diff in sorted(
                result.files_modified, key=lambda x: abs(x.size_change or 0), reverse=True
            )[:10]:
                size_change = diff.size_change or 0
                print(f"  ~ {diff.path} ({size_change:+,} bytes)")
            if len(result.files_modified) > 10:
                print(f"  ... and {len(result.files_modified) - 10} more")

    def generate_delta_info(self) -> Dict:
        """
        Generate information needed for delta/OTA updates
        """
        result = self.compare()

        delta_info = {
            "from_version": result.old_version,
            "to_version": result.new_version,
            "files_to_add": [f.path for f in result.files_added],
            "files_to_remove": [f.path for f in result.files_removed],
            "files_to_patch": [
                {
                    "path": f.path,
                    "old_hash": f.old_hash,
                    "new_hash": f.new_hash,
                    "old_size": f.old_size,
                    "new_size": f.new_size,
                }
                for f in result.files_modified
            ],
            "estimated_delta_size": sum(
                f.new_size or 0 for f in result.files_added + result.files_modified
            ),
        }

        return delta_info

    def export_diff_report(self, output_path: Path):
        """Export diff report to JSON"""
        import json

        result = self.compare()

        report = {
            "old_version": result.old_version,
            "new_version": result.new_version,
            "summary": result.summary,
            "added_files": [
                {"path": f.path, "size": f.new_size, "hash": f.new_hash} for f in result.files_added
            ],
            "removed_files": [
                {"path": f.path, "size": f.old_size, "hash": f.old_hash}
                for f in result.files_removed
            ],
            "modified_files": [
                {
                    "path": f.path,
                    "old_size": f.old_size,
                    "new_size": f.new_size,
                    "size_change": f.size_change,
                    "old_hash": f.old_hash,
                    "new_hash": f.new_hash,
                }
                for f in result.files_modified
            ],
        }

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\nDiff report exported to: {output_path}")
