"""
Android boot image manipulation tools
Advanced feature not in Odin

Author: SamFWTool Team
License: MIT
"""

import struct
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass

__all__ = [
    "BootImageInfo",
    "BootImageTool",
]


@dataclass
class BootImageInfo:
    """Boot image information"""

    kernel_size: int
    kernel_addr: int
    ramdisk_size: int
    ramdisk_addr: int
    second_size: int
    second_addr: int
    tags_addr: int
    page_size: int
    os_version: int
    name: str
    cmdline: str
    id: bytes


class BootImageTool:
    """
    Android boot image parser and modifier

    Handles ANDROID! boot image format
    """

    BOOT_MAGIC = b"ANDROID!"
    BOOT_MAGIC_SIZE = 8
    BOOT_NAME_SIZE = 16
    BOOT_ARGS_SIZE = 512
    BOOT_EXTRA_ARGS_SIZE = 1024

    def __init__(self, boot_image_path: str):
        self.boot_image_path = Path(boot_image_path)
        self.info = None

    def parse(self) -> BootImageInfo:
        """Parse boot image header"""
        with open(self.boot_image_path, "rb") as f:
            # Read header
            magic = f.read(8)
            if magic != self.BOOT_MAGIC:
                raise ValueError(f"Invalid boot image magic: {magic}")

            kernel_size = struct.unpack("<I", f.read(4))[0]
            kernel_addr = struct.unpack("<I", f.read(4))[0]
            ramdisk_size = struct.unpack("<I", f.read(4))[0]
            ramdisk_addr = struct.unpack("<I", f.read(4))[0]
            second_size = struct.unpack("<I", f.read(4))[0]
            second_addr = struct.unpack("<I", f.read(4))[0]
            tags_addr = struct.unpack("<I", f.read(4))[0]
            page_size = struct.unpack("<I", f.read(4))[0]

            # Header version and OS version (combined in one field)
            dt_size = struct.unpack("<I", f.read(4))[0]
            os_version = struct.unpack("<I", f.read(4))[0]

            name = f.read(self.BOOT_NAME_SIZE).rstrip(b"\x00").decode("ascii", errors="ignore")
            cmdline = f.read(self.BOOT_ARGS_SIZE).rstrip(b"\x00").decode("ascii", errors="ignore")
            id = f.read(32)  # SHA-1 hash

            self.info = BootImageInfo(
                kernel_size=kernel_size,
                kernel_addr=kernel_addr,
                ramdisk_size=ramdisk_size,
                ramdisk_addr=ramdisk_addr,
                second_size=second_size,
                second_addr=second_addr,
                tags_addr=tags_addr,
                page_size=page_size,
                os_version=os_version,
                name=name,
                cmdline=cmdline,
                id=id,
            )

            return self.info

    def extract_kernel(self, output_path: str) -> bool:
        """Extract kernel from boot image"""
        if not self.info:
            self.parse()

        with open(self.boot_image_path, "rb") as f:
            # Skip to kernel (after page-aligned header)
            f.seek(self.info.page_size)
            kernel_data = f.read(self.info.kernel_size)

        with open(output_path, "wb") as f:
            f.write(kernel_data)

        print(f"Kernel extracted to: {output_path} ({self.info.kernel_size} bytes)")
        return True

    def extract_ramdisk(self, output_path: str) -> bool:
        """Extract ramdisk from boot image"""
        if not self.info:
            self.parse()

        with open(self.boot_image_path, "rb") as f:
            # Skip to ramdisk
            kernel_pages = (self.info.kernel_size + self.info.page_size - 1) // self.info.page_size
            f.seek(self.info.page_size * (1 + kernel_pages))
            ramdisk_data = f.read(self.info.ramdisk_size)

        with open(output_path, "wb") as f:
            f.write(ramdisk_data)

        print(f"Ramdisk extracted to: {output_path} ({self.info.ramdisk_size} bytes)")
        return True

    def print_info(self):
        """Print boot image information"""
        if not self.info:
            self.parse()

        print("\n" + "=" * 70)
        print("BOOT IMAGE INFORMATION")
        print("=" * 70)
        print(f"\nName: {self.info.name}")
        print(f"Kernel Size: {self.info.kernel_size} bytes ({self.info.kernel_size/1024:.2f} KB)")
        print(f"Kernel Address: 0x{self.info.kernel_addr:08x}")
        print(
            f"Ramdisk Size: {self.info.ramdisk_size} bytes ({self.info.ramdisk_size/1024:.2f} KB)"
        )
        print(f"Ramdisk Address: 0x{self.info.ramdisk_addr:08x}")
        print(f"Page Size: {self.info.page_size} bytes")
        print(f"Tags Address: 0x{self.info.tags_addr:08x}")
        print(f"\nCommand Line: {self.info.cmdline}")
        print(f"\nOS Version: 0x{self.info.os_version:08x}")
