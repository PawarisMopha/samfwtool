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
