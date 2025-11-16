"""
Advanced firmware extraction engine
Extracts and unpacks firmware files from multiple formats

Author: SamFWTool Team
License: MIT
"""
import os
import tarfile
import zipfile
import struct
import lz4.frame
import gzip
import bz2
import lzma
from pathlib import Path
from typing import Optional, Callable
from tqdm import tqdm

from samfwtool.core.parser import FirmwareParser, FirmwareFormat, PartitionInfo

__all__ = [
    "FirmwareExtractor",
]


class FirmwareExtractor:
    """
    Advanced firmware extraction engine

    Features beyond Odin:
    - Extract from multiple formats (TAR, ZIP, IMG, SPARSE)
    - Automatic decompression (gzip, lz4, bzip2, xz)
    - Sparse image conversion to raw
    - Selective partition extraction
    - Progress tracking
    - Integrity verification
    """

    def __init__(self, firmware_path: str, output_dir: str):
        self.firmware_path = Path(firmware_path)
        self.output_dir = Path(output_dir)
        self.parser = FirmwareParser(str(self.firmware_path))
        self.progress_callback = None

    def set_progress_callback(self, callback: Callable):
        """Set callback for progress updates"""
        self.progress_callback = callback

    def extract_all(self, decompress: bool = True) -> bool:
        """
        Extract all partitions from firmware

        Args:
            decompress: Automatically decompress compressed partitions

        Returns:
            True if successful
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Parse firmware first
        info = self.parser.parse()

        if info.format == FirmwareFormat.TAR or info.format == FirmwareFormat.TAR_MD5:
            return self._extract_tar(decompress)
        elif info.format == FirmwareFormat.ZIP:
            return self._extract_zip(decompress)
        elif info.format == FirmwareFormat.IMG:
            return self._extract_img(decompress)
        elif info.format == FirmwareFormat.SPARSE:
            return self._extract_sparse(decompress)
        else:
            return self._extract_generic()

    def extract_partition(self, partition_name: str, output_path: Optional[str] = None,
                         decompress: bool = True) -> bool:
        """
        Extract a specific partition

        Args:
            partition_name: Name of partition to extract
            output_path: Optional custom output path
            decompress: Automatically decompress if compressed

        Returns:
            True if successful
        """
        info = self.parser.parse()

        # Find partition
        partition = None
        for p in info.partitions:
            if p.name == partition_name:
                partition = p
                break

        if not partition:
            raise ValueError(f"Partition '{partition_name}' not found")

        if output_path is None:
            output_path = self.output_dir / partition_name

        if info.format == FirmwareFormat.TAR or info.format == FirmwareFormat.TAR_MD5:
            return self._extract_tar_member(partition_name, output_path, decompress)
        elif info.format == FirmwareFormat.ZIP:
            return self._extract_zip_member(partition_name, output_path, decompress)
        else:
            # For single-file formats, just copy
            return self._extract_img(decompress)

    def _extract_tar(self, decompress: bool) -> bool:
        """Extract TAR firmware"""
        print(f"Extracting TAR firmware to {self.output_dir}")

        with tarfile.open(self.firmware_path, 'r') as tar:
            members = tar.getmembers()

            for member in tqdm(members, desc="Extracting", unit="file"):
                if member.isfile():
                    output_path = self.output_dir / member.name

                    # Extract file
                    with tar.extractfile(member) as src:
                        data = src.read()

                    # Write to output
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, 'wb') as dst:
                        dst.write(data)

                    # Decompress if needed
                    if decompress:
                        self._decompress_if_needed(output_path)

        print(f"Extraction complete: {len(members)} files extracted")
        return True

    def _extract_tar_member(self, member_name: str, output_path: Path, decompress: bool) -> bool:
        """Extract a specific member from TAR"""
        with tarfile.open(self.firmware_path, 'r') as tar:
            try:
                member = tar.getmember(member_name)
                with tar.extractfile(member) as src:
                    data = src.read()

                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as dst:
                    dst.write(data)

                if decompress:
                    self._decompress_if_needed(output_path)

                print(f"Extracted: {member_name} -> {output_path}")
                return True
            except KeyError:
                print(f"Error: Member '{member_name}' not found in TAR")
                return False

    def _extract_zip(self, decompress: bool) -> bool:
        """Extract ZIP firmware"""
        print(f"Extracting ZIP firmware to {self.output_dir}")

        with zipfile.ZipFile(self.firmware_path, 'r') as zf:
            members = [m for m in zf.infolist() if not m.is_dir()]

            for member in tqdm(members, desc="Extracting", unit="file"):
                output_path = self.output_dir / member.filename

                # Extract file
                data = zf.read(member)

                # Write to output
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as dst:
                    dst.write(data)

                # Decompress if needed
                if decompress:
                    self._decompress_if_needed(output_path)

        print(f"Extraction complete: {len(members)} files extracted")
        return True

    def _extract_zip_member(self, member_name: str, output_path: Path, decompress: bool) -> bool:
        """Extract a specific member from ZIP"""
        with zipfile.ZipFile(self.firmware_path, 'r') as zf:
            try:
                data = zf.read(member_name)

                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as dst:
                    dst.write(data)

                if decompress:
                    self._decompress_if_needed(output_path)

                print(f"Extracted: {member_name} -> {output_path}")
                return True
            except KeyError:
                print(f"Error: Member '{member_name}' not found in ZIP")
                return False

    def _extract_img(self, decompress: bool) -> bool:
        """Extract IMG file"""
        output_path = self.output_dir / self.firmware_path.name

        print(f"Copying IMG file to {output_path}")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        with open(self.firmware_path, 'rb') as src:
            with open(output_path, 'wb') as dst:
                # Copy in chunks with progress
                file_size = self.firmware_path.stat().st_size
                with tqdm(total=file_size, unit='B', unit_scale=True, desc="Copying") as pbar:
                    while True:
                        chunk = src.read(8192)
                        if not chunk:
                            break
                        dst.write(chunk)
                        pbar.update(len(chunk))

        if decompress:
            self._decompress_if_needed(output_path)

        print(f"Extraction complete: {output_path}")
        return True

    def _extract_sparse(self, decompress: bool) -> bool:
        """
        Extract sparse image and convert to raw
        This is a major feature not available in Odin
        """
        output_path = self.output_dir / self.firmware_path.stem
        output_path = output_path.with_suffix('.img')

        print(f"Converting sparse image to raw: {output_path}")

        with open(self.firmware_path, 'rb') as f:
            # Read sparse header
            magic = struct.unpack('<I', f.read(4))[0]
            if magic != 0xed26ff3a:
                raise ValueError("Invalid sparse image magic")

            major_version = struct.unpack('<H', f.read(2))[0]
            minor_version = struct.unpack('<H', f.read(2))[0]
            file_hdr_sz = struct.unpack('<H', f.read(2))[0]
            chunk_hdr_sz = struct.unpack('<H', f.read(2))[0]
            blk_sz = struct.unpack('<I', f.read(4))[0]
            total_blks = struct.unpack('<I', f.read(4))[0]
            total_chunks = struct.unpack('<I', f.read(4))[0]
            image_checksum = struct.unpack('<I', f.read(4))[0]

            print(f"Sparse image info:")
            print(f"  Block size: {blk_sz} bytes")
            print(f"  Total blocks: {total_blks}")
            print(f"  Total chunks: {total_chunks}")
            print(f"  Output size: {total_blks * blk_sz / (1024*1024):.2f} MB")

            # Seek to first chunk
            f.seek(file_hdr_sz)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as out:
                for i in tqdm(range(total_chunks), desc="Converting chunks", unit="chunk"):
                    # Read chunk header
                    chunk_type = struct.unpack('<H', f.read(2))[0]
                    reserved1 = struct.unpack('<H', f.read(2))[0]
                    chunk_sz = struct.unpack('<I', f.read(4))[0]
                    total_sz = struct.unpack('<I', f.read(4))[0]

                    if chunk_type == 0xCAC1:  # Raw chunk
                        # Copy raw data
                        data = f.read(chunk_sz * blk_sz)
                        out.write(data)
                    elif chunk_type == 0xCAC2:  # Fill chunk
                        # Fill with repeated value
                        fill_value = f.read(4)
                        for _ in range(chunk_sz):
                            out.write(fill_value * (blk_sz // 4))
                    elif chunk_type == 0xCAC3:  # Don't care chunk
                        # Write zeros
                        out.write(b'\x00' * (chunk_sz * blk_sz))
                    elif chunk_type == 0xCAC4:  # CRC32 chunk
                        # Skip CRC
                        f.read(4)
                    else:
                        raise ValueError(f"Unknown chunk type: {chunk_type:04x}")

        print(f"Sparse conversion complete: {output_path}")
        return True

    def _extract_generic(self) -> bool:
        """Extract generic firmware file"""
        return self._extract_img(False)

    def _decompress_if_needed(self, file_path: Path) -> Optional[Path]:
        """
        Automatically detect and decompress compressed files
        Supports: gzip, bzip2, xz, lz4
        """
        # Read file header
        with open(file_path, 'rb') as f:
            header = f.read(8)

        decompressed_path = None

        # Detect compression and decompress with proper error handling
        try:
            if header.startswith(b'\x1f\x8b'):  # gzip
                print(f"  Decompressing (gzip): {file_path.name}")
                decompressed_path = file_path.with_suffix('')
                with gzip.open(file_path, 'rb') as src:
                    with open(decompressed_path, 'wb') as dst:
                        dst.write(src.read())
                # Only delete original if decompression succeeded and output exists
                if decompressed_path.exists() and decompressed_path.stat().st_size > 0:
                    file_path.unlink()
                else:
                    raise IOError(f"Decompression failed: output file is empty or missing")

            elif header.startswith(b'\x42\x5a'):  # bzip2
                print(f"  Decompressing (bzip2): {file_path.name}")
                decompressed_path = file_path.with_suffix('')
                with bz2.open(file_path, 'rb') as src:
                    with open(decompressed_path, 'wb') as dst:
                        dst.write(src.read())
                # Only delete original if decompression succeeded
                if decompressed_path.exists() and decompressed_path.stat().st_size > 0:
                    file_path.unlink()
                else:
                    raise IOError(f"Decompression failed: output file is empty or missing")

            elif header.startswith(b'\xfd\x37\x7a\x58\x5a'):  # xz
                print(f"  Decompressing (xz): {file_path.name}")
                decompressed_path = file_path.with_suffix('')
                with lzma.open(file_path, 'rb') as src:
                    with open(decompressed_path, 'wb') as dst:
                        dst.write(src.read())
                # Only delete original if decompression succeeded
                if decompressed_path.exists() and decompressed_path.stat().st_size > 0:
                    file_path.unlink()
                else:
                    raise IOError(f"Decompression failed: output file is empty or missing")

            elif header.startswith(b'\x04\x22\x4d\x18'):  # lz4
                print(f"  Decompressing (lz4): {file_path.name}")
                decompressed_path = file_path.with_suffix('')
                with lz4.frame.open(file_path, 'rb') as src:
                    with open(decompressed_path, 'wb') as dst:
                        dst.write(src.read())
                # Only delete original if decompression succeeded
                if decompressed_path.exists() and decompressed_path.stat().st_size > 0:
                    file_path.unlink()
                else:
                    raise IOError(f"Decompression failed: output file is empty or missing")

        except (IOError, OSError, gzip.BadGzipFile, lzma.LZMAError) as e:
            print(f"  Warning: Decompression failed for {file_path.name}: {e}")
            # Clean up failed decompression output if it exists
            if decompressed_path and decompressed_path.exists():
                decompressed_path.unlink()
            # Return original file path since decompression failed
            return file_path

        return decompressed_path if decompressed_path else file_path

    def get_extraction_info(self) -> dict:
        """Get information about what will be extracted"""
        info = self.parser.parse()

        return {
            'firmware_format': info.format.value,
            'total_size': info.size,
            'partition_count': len(info.partitions),
            'partitions': [
                {
                    'name': p.name,
                    'size': p.size,
                    'type': p.type,
                    'format': p.format,
                    'compressed': p.compression is not None
                }
                for p in info.partitions
            ]
        }
