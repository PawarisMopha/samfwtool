"""
Firmware packing and repacking engine
Allows creating firmware files from extracted partitions

Author: SamFWTool Team
License: MIT
"""
import os
import tarfile
import hashlib
import struct
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from tqdm import tqdm

from samfwtool.core.parser import FirmwareFormat

__all__ = [
    "FirmwarePacker",
    "quick_pack",
]


class FirmwarePacker:
    """
    Advanced firmware packing engine

    Creates firmware files from individual partitions.
    This is a CRITICAL feature missing from Odin (read-only).

    Features:
    - Pack partitions into TAR/TAR.MD5
    - Generate MD5 checksums
    - Create sparse images from raw
    - Validate packed firmware
    - Support custom metadata
    """

    def __init__(self, output_path: str, format: FirmwareFormat = FirmwareFormat.TAR_MD5):
        self.output_path = Path(output_path)
        self.format = format
        self.files_to_pack: List[Tuple[Path, str]] = []

    def add_file(self, file_path: Path, archive_name: Optional[str] = None) -> None:
        """Add a file to be packed"""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self.files_to_pack.append((file_path, archive_name or file_path.name))

    def add_files(self, files: List[Path]):
        """Add multiple files to be packed"""
        for file_path in files:
            self.add_file(file_path)

    def pack(self) -> bool:
        """
        Pack all added files into firmware

        Returns:
            True if successful
        """
        if self.format in [FirmwareFormat.TAR, FirmwareFormat.TAR_MD5]:
            return self._pack_tar()
        else:
            raise NotImplementedError(f"Packing format {self.format} not yet implemented")

    def _pack_tar(self) -> bool:
        """Pack files into TAR format"""
        print(f"Packing {len(self.files_to_pack)} files into TAR...")

        # Determine output file
        if self.format == FirmwareFormat.TAR_MD5:
            tar_path = self.output_path.with_suffix('.tar.md5')
        else:
            tar_path = self.output_path

        # Create TAR archive
        with tarfile.open(tar_path, 'w') as tar:
            for file_path, archive_name in tqdm(self.files_to_pack, desc="Packing", unit="file"):
                print(f"  Adding: {archive_name} ({file_path.stat().st_size:,} bytes)")
                tar.add(file_path, arcname=archive_name)

        print(f"TAR created: {tar_path}")

        # Generate MD5 if needed
        if self.format == FirmwareFormat.TAR_MD5:
            md5_hash = self._generate_md5(tar_path)
            print(f"MD5 checksum: {md5_hash}")

            # Optionally create .md5 file
            md5_file = tar_path.with_suffix('.md5')
            with open(md5_file, 'w') as f:
                f.write(f"{md5_hash}  {tar_path.name}\n")
            print(f"MD5 file created: {md5_file}")

        print(f"\n✓ Firmware packing complete: {tar_path}")
        return True

    def _generate_md5(self, file_path: Path) -> str:
        """Generate MD5 checksum of a file"""
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
        return md5.hexdigest()

    def create_sparse_image(self, raw_image: Path, output_path: Path,
                           block_size: int = 4096) -> bool:
        """
        Convert raw image to Android sparse format

        This is an ADVANCED feature not in Odin.

        Args:
            raw_image: Path to raw image file
            output_path: Path for output sparse image
            block_size: Block size for sparse image (default 4096)

        Returns:
            True if successful
        """
        print(f"Converting raw image to sparse format...")
        print(f"  Input: {raw_image}")
        print(f"  Output: {output_path}")
        print(f"  Block size: {block_size} bytes")

        if not raw_image.exists():
            raise FileNotFoundError(f"Raw image not found: {raw_image}")

        raw_size = raw_image.stat().st_size
        total_blocks = (raw_size + block_size - 1) // block_size

        print(f"  Raw size: {raw_size:,} bytes ({raw_size/(1024*1024):.2f} MB)")
        print(f"  Total blocks: {total_blocks}")

        # Sparse image header
        SPARSE_HEADER_MAGIC = 0xed26ff3a
        SPARSE_HEADER_MAJOR_VERSION = 1
        SPARSE_HEADER_MINOR_VERSION = 0
        FILE_HDR_SIZE = 28
        CHUNK_HDR_SIZE = 12

        chunks = []
        chunk_count = 0

        # Read raw image and create chunks
        with open(raw_image, 'rb') as f:
            for block_num in tqdm(range(total_blocks), desc="Analyzing blocks", unit="block"):
                block_data = f.read(block_size)
                if not block_data:
                    break

                # Check if block is all zeros (don't care chunk)
                if block_data == b'\x00' * len(block_data):
                    chunk_type = 0xCAC3  # Don't care
                    chunks.append((chunk_type, 1, None))
                else:
                    # Raw chunk
                    chunk_type = 0xCAC1
                    chunks.append((chunk_type, 1, block_data))

                chunk_count += 1

        # Merge consecutive chunks of same type
        merged_chunks = []
        i = 0
        while i < len(chunks):
            chunk_type, chunk_blocks, chunk_data = chunks[i]
            merged_data = [chunk_data] if chunk_data else []

            # Merge consecutive chunks of same type
            j = i + 1
            while j < len(chunks) and chunks[j][0] == chunk_type:
                if chunk_type == 0xCAC1:  # Only merge raw chunks with data
                    merged_data.append(chunks[j][2])
                chunk_blocks += 1
                j += 1

            if chunk_type == 0xCAC1:
                merged_chunks.append((chunk_type, chunk_blocks, b''.join(merged_data)))
            else:
                merged_chunks.append((chunk_type, chunk_blocks, None))

            i = j if j > i else i + 1

        print(f"  Chunks optimized: {len(chunks)} → {len(merged_chunks)}")

        # Write sparse image
        with open(output_path, 'wb') as f:
            # Write file header
            f.write(struct.pack('<I', SPARSE_HEADER_MAGIC))
            f.write(struct.pack('<H', SPARSE_HEADER_MAJOR_VERSION))
            f.write(struct.pack('<H', SPARSE_HEADER_MINOR_VERSION))
            f.write(struct.pack('<H', FILE_HDR_SIZE))
            f.write(struct.pack('<H', CHUNK_HDR_SIZE))
            f.write(struct.pack('<I', block_size))
            f.write(struct.pack('<I', total_blocks))
            f.write(struct.pack('<I', len(merged_chunks)))
            f.write(struct.pack('<I', 0))  # Image checksum (optional)

            # Write chunks
            for chunk_type, chunk_blocks, chunk_data in tqdm(merged_chunks, desc="Writing chunks", unit="chunk"):
                # Chunk header
                f.write(struct.pack('<H', chunk_type))
                f.write(struct.pack('<H', 0))  # Reserved
                f.write(struct.pack('<I', chunk_blocks))

                if chunk_type == 0xCAC1:  # Raw chunk
                    total_size = CHUNK_HDR_SIZE + len(chunk_data)
                else:
                    total_size = CHUNK_HDR_SIZE

                f.write(struct.pack('<I', total_size))

                # Chunk data (only for raw chunks)
                if chunk_type == 0xCAC1 and chunk_data:
                    f.write(chunk_data)

        sparse_size = output_path.stat().st_size
        compression_ratio = (1 - sparse_size / raw_size) * 100 if raw_size > 0 else 0

        print(f"\n✓ Sparse image created!")
        print(f"  Original size: {raw_size:,} bytes ({raw_size/(1024*1024):.2f} MB)")
        print(f"  Sparse size: {sparse_size:,} bytes ({sparse_size/(1024*1024):.2f} MB)")
        print(f"  Compression: {compression_ratio:.1f}%")

        return True

    def validate_packed_firmware(self) -> bool:
        """Validate the packed firmware"""
        if not self.output_path.exists():
            return False

        # Verify it can be opened
        try:
            if self.format in [FirmwareFormat.TAR, FirmwareFormat.TAR_MD5]:
                with tarfile.open(self.output_path, 'r') as tar:
                    members = tar.getmembers()
                    print(f"Validation: Found {len(members)} files in archive")
                    return len(members) > 0
        except Exception as e:
            print(f"Validation failed: {e}")
            return False

        return True


def quick_pack(files: List[Path], output: Path, format: FirmwareFormat = FirmwareFormat.TAR_MD5) -> bool:
    """
    Quick utility function to pack files into firmware

    Args:
        files: List of files to pack
        output: Output firmware path
        format: Firmware format (default TAR_MD5)

    Returns:
        True if successful
    """
    packer = FirmwarePacker(output, format)
    packer.add_files(files)
    return packer.pack()
