"""
Unit tests for firmware packer
"""
import pytest
import tarfile
from pathlib import Path
from samfwtool.core.packer import FirmwarePacker, quick_pack
from samfwtool.core.parser import FirmwareFormat


class TestFirmwarePacker:
    """Test firmware packer functionality"""

    def test_add_file(self, tmp_path):
        """Test adding a file to packer"""
        # Create a test file
        test_file = tmp_path / "boot.img"
        test_file.write_bytes(b"test content")

        output_file = tmp_path / "output.tar"
        packer = FirmwarePacker(str(output_file), FirmwareFormat.TAR)
        packer.add_file(test_file)

        assert len(packer.files_to_pack) == 1
        assert packer.files_to_pack[0][0] == test_file

    def test_add_nonexistent_file(self, tmp_path):
        """Test error handling for non-existent file"""
        output_file = tmp_path / "output.tar"
        packer = FirmwarePacker(str(output_file), FirmwareFormat.TAR)

        with pytest.raises(FileNotFoundError):
            packer.add_file(tmp_path / "nonexistent.img")

    def test_add_multiple_files(self, tmp_path):
        """Test adding multiple files"""
        # Create test files
        files = []
        for name in ["boot.img", "system.img", "vendor.img"]:
            file = tmp_path / name
            file.write_bytes(f"content of {name}".encode())
            files.append(file)

        output_file = tmp_path / "output.tar"
        packer = FirmwarePacker(str(output_file), FirmwareFormat.TAR)
        packer.add_files(files)

        assert len(packer.files_to_pack) == 3

    def test_pack_tar(self, tmp_path):
        """Test packing files into TAR"""
        # Create test files
        test_file = tmp_path / "boot.img"
        test_file.write_bytes(b"boot image content")

        output_file = tmp_path / "output.tar"
        packer = FirmwarePacker(str(output_file), FirmwareFormat.TAR)
        packer.add_file(test_file)

        result = packer.pack()

        assert result is True
        assert output_file.exists()

        # Verify TAR contents
        with tarfile.open(output_file, 'r') as tar:
            members = tar.getmembers()
            assert len(members) == 1
            assert members[0].name == "boot.img"

    def test_pack_tar_md5(self, tmp_path):
        """Test packing files into TAR.MD5"""
        test_file = tmp_path / "boot.img"
        test_file.write_bytes(b"boot image content")

        output_file = tmp_path / "output"
        packer = FirmwarePacker(str(output_file), FirmwareFormat.TAR_MD5)
        packer.add_file(test_file)

        result = packer.pack()

        assert result is True
        # TAR.MD5 creates .tar.md5 file
        tar_md5_file = output_file.with_suffix('.tar.md5')
        assert tar_md5_file.exists()

    def test_validate_packed_firmware(self, tmp_path):
        """Test validating packed firmware"""
        test_file = tmp_path / "boot.img"
        test_file.write_bytes(b"boot image content")

        output_file = tmp_path / "output.tar"
        packer = FirmwarePacker(str(output_file), FirmwareFormat.TAR)
        packer.add_file(test_file)
        packer.pack()

        # Change output_path to the actual file for validation
        packer.output_path = output_file
        assert packer.validate_packed_firmware() is True

    def test_validate_nonexistent_firmware(self, tmp_path):
        """Test validation of non-existent firmware"""
        output_file = tmp_path / "nonexistent.tar"
        packer = FirmwarePacker(str(output_file), FirmwareFormat.TAR)

        assert packer.validate_packed_firmware() is False


class TestQuickPack:
    """Test quick_pack utility function"""

    def test_quick_pack(self, tmp_path):
        """Test quick pack utility"""
        # Create test files
        files = []
        for name in ["boot.img", "system.img"]:
            file = tmp_path / name
            file.write_bytes(f"content of {name}".encode())
            files.append(file)

        output_file = tmp_path / "output"
        result = quick_pack(files, output_file, FirmwareFormat.TAR_MD5)

        assert result is True


class TestMD5Generation:
    """Test MD5 generation functionality"""

    def test_generate_md5(self, tmp_path):
        """Test MD5 generation"""
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"test content for md5")

        output_file = tmp_path / "output.tar"
        packer = FirmwarePacker(str(output_file), FirmwareFormat.TAR)

        md5 = packer._generate_md5(test_file)

        assert md5 is not None
        assert len(md5) == 32  # MD5 hash is 32 hex characters
        # Verify it's a valid hex string
        int(md5, 16)

    def test_generate_md5_large_file(self, tmp_path):
        """Test MD5 generation with larger file (multiple chunks)"""
        test_file = tmp_path / "large.bin"
        # Create file larger than 8192 byte chunk
        test_file.write_bytes(b"x" * 20000)

        output_file = tmp_path / "output.tar"
        packer = FirmwarePacker(str(output_file), FirmwareFormat.TAR)

        md5 = packer._generate_md5(test_file)

        assert md5 is not None
        assert len(md5) == 32


class TestAddFileOptions:
    """Test add_file with various options"""

    def test_add_file_with_custom_name(self, tmp_path):
        """Test adding file with custom archive name"""
        test_file = tmp_path / "original.img"
        test_file.write_bytes(b"test content")

        output_file = tmp_path / "output.tar"
        packer = FirmwarePacker(str(output_file), FirmwareFormat.TAR)
        packer.add_file(test_file, archive_name="renamed.img")

        assert len(packer.files_to_pack) == 1
        assert packer.files_to_pack[0][1] == "renamed.img"

    def test_add_file_default_name(self, tmp_path):
        """Test adding file uses filename as default archive name"""
        test_file = tmp_path / "boot.img"
        test_file.write_bytes(b"test content")

        output_file = tmp_path / "output.tar"
        packer = FirmwarePacker(str(output_file), FirmwareFormat.TAR)
        packer.add_file(test_file)

        assert packer.files_to_pack[0][1] == "boot.img"


class TestUnsupportedFormats:
    """Test handling of unsupported formats"""

    def test_pack_unsupported_format(self, tmp_path):
        """Test packing with unsupported format raises error"""
        test_file = tmp_path / "boot.img"
        test_file.write_bytes(b"test content")

        output_file = tmp_path / "output.zip"
        packer = FirmwarePacker(str(output_file), FirmwareFormat.ZIP)
        packer.add_file(test_file)

        with pytest.raises(NotImplementedError, match="not yet implemented"):
            packer.pack()


class TestSparseImageCreation:
    """Test sparse image creation functionality"""

    def test_create_sparse_from_raw(self, tmp_path):
        """Test creating sparse image from raw image"""
        # Create a raw image with some data and some zeros
        raw_file = tmp_path / "system.img"
        # Mix of data and zeros to test chunk optimization
        data = b"A" * 4096 + b"\x00" * 4096 + b"B" * 4096
        raw_file.write_bytes(data)

        output_file = tmp_path / "system.sparse"
        packer = FirmwarePacker(str(tmp_path / "output"), FirmwareFormat.TAR)

        result = packer.create_sparse_image(raw_file, output_file, block_size=4096)

        assert result is True
        assert output_file.exists()

        # Verify sparse header magic
        with open(output_file, 'rb') as f:
            import struct
            magic = struct.unpack('<I', f.read(4))[0]
            assert magic == 0xed26ff3a

    def test_create_sparse_nonexistent_raw(self, tmp_path):
        """Test error when raw image doesn't exist"""
        output_file = tmp_path / "output.sparse"
        packer = FirmwarePacker(str(tmp_path / "output"), FirmwareFormat.TAR)

        with pytest.raises(FileNotFoundError, match="Raw image not found"):
            packer.create_sparse_image(tmp_path / "nonexistent.img", output_file)

    def test_create_sparse_all_zeros(self, tmp_path):
        """Test creating sparse from all-zeros image"""
        raw_file = tmp_path / "zeros.img"
        raw_file.write_bytes(b"\x00" * 8192)

        output_file = tmp_path / "zeros.sparse"
        packer = FirmwarePacker(str(tmp_path / "output"), FirmwareFormat.TAR)

        result = packer.create_sparse_image(raw_file, output_file, block_size=4096)

        assert result is True
        assert output_file.exists()
        # Sparse file should be smaller than raw (only header + don't care chunks)
        assert output_file.stat().st_size < raw_file.stat().st_size

    def test_create_sparse_all_data(self, tmp_path):
        """Test creating sparse from all-data image (no zeros)"""
        raw_file = tmp_path / "data.img"
        raw_file.write_bytes(b"X" * 8192)

        output_file = tmp_path / "data.sparse"
        packer = FirmwarePacker(str(tmp_path / "output"), FirmwareFormat.TAR)

        result = packer.create_sparse_image(raw_file, output_file, block_size=4096)

        assert result is True
        assert output_file.exists()

    def test_create_sparse_small_block_size(self, tmp_path):
        """Test sparse with smaller block size"""
        raw_file = tmp_path / "test.img"
        raw_file.write_bytes(b"A" * 256 + b"\x00" * 256)

        output_file = tmp_path / "test.sparse"
        packer = FirmwarePacker(str(tmp_path / "output"), FirmwareFormat.TAR)

        result = packer.create_sparse_image(raw_file, output_file, block_size=256)

        assert result is True
        assert output_file.exists()

    def test_create_sparse_consecutive_same_type_chunks(self, tmp_path):
        """Test merging consecutive chunks of same type"""
        raw_file = tmp_path / "test.img"
        # Multiple consecutive data blocks
        raw_file.write_bytes(b"A" * 4096 + b"B" * 4096 + b"C" * 4096)

        output_file = tmp_path / "test.sparse"
        packer = FirmwarePacker(str(tmp_path / "output"), FirmwareFormat.TAR)

        result = packer.create_sparse_image(raw_file, output_file, block_size=4096)

        assert result is True


class TestValidation:
    """Extended validation tests"""

    def test_validate_corrupted_tar(self, tmp_path):
        """Test validation of corrupted TAR file"""
        output_file = tmp_path / "corrupted.tar"
        output_file.write_bytes(b"not a valid tar file content")

        packer = FirmwarePacker(str(output_file), FirmwareFormat.TAR)

        # Should return False for corrupted files
        assert packer.validate_packed_firmware() is False

    def test_validate_empty_tar(self, tmp_path):
        """Test validation of empty TAR file"""
        output_file = tmp_path / "empty.tar"
        # Create minimal valid but empty TAR
        with tarfile.open(output_file, 'w') as tar:
            pass  # Empty tar

        packer = FirmwarePacker(str(output_file), FirmwareFormat.TAR)

        # Empty tar should fail validation (no members)
        assert packer.validate_packed_firmware() is False


class TestPackingWorkflow:
    """Test complete packing workflows"""

    def test_pack_multiple_files_tar(self, tmp_path):
        """Test packing multiple files into TAR"""
        files = []
        for name in ["boot.img", "system.img", "vendor.img", "recovery.img"]:
            file = tmp_path / name
            file.write_bytes(f"content of {name}".encode())
            files.append(file)

        output_file = tmp_path / "firmware.tar"
        packer = FirmwarePacker(str(output_file), FirmwareFormat.TAR)
        packer.add_files(files)

        result = packer.pack()

        assert result is True
        assert output_file.exists()

        # Verify all files in TAR
        with tarfile.open(output_file, 'r') as tar:
            members = tar.getmembers()
            assert len(members) == 4
            member_names = [m.name for m in members]
            assert "boot.img" in member_names
            assert "system.img" in member_names

    def test_pack_and_validate_workflow(self, tmp_path):
        """Test complete pack and validate workflow"""
        test_file = tmp_path / "boot.img"
        test_file.write_bytes(b"boot image content" * 100)

        output_file = tmp_path / "output.tar"
        packer = FirmwarePacker(str(output_file), FirmwareFormat.TAR)
        packer.add_file(test_file)

        # Pack
        pack_result = packer.pack()
        assert pack_result is True

        # Validate
        validate_result = packer.validate_packed_firmware()
        assert validate_result is True

    def test_tar_md5_creates_checksum_file(self, tmp_path):
        """Test TAR_MD5 format creates separate MD5 file"""
        test_file = tmp_path / "boot.img"
        test_file.write_bytes(b"boot image content")

        output_file = tmp_path / "firmware"
        packer = FirmwarePacker(str(output_file), FirmwareFormat.TAR_MD5)
        packer.add_file(test_file)

        result = packer.pack()

        assert result is True
        # Check both files exist
        tar_md5_file = output_file.with_suffix('.tar.md5')
        md5_file = tar_md5_file.with_suffix('.md5')
        assert tar_md5_file.exists()
        assert md5_file.exists()

        # Verify MD5 file content format
        md5_content = md5_file.read_text()
        assert "  " in md5_content  # MD5 format: "hash  filename"
        assert len(md5_content.split()[0]) == 32  # Valid MD5 hash
