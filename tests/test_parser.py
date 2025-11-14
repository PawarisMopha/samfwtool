"""
Unit tests for firmware parser
"""
import pytest
import tempfile
import tarfile
from pathlib import Path
from samfwtool.core.parser import FirmwareParser, FirmwareFormat


class TestFirmwareParser:
    """Test firmware parser functionality"""

    def test_detect_tar_format(self, tmp_path):
        """Test TAR format detection"""
        # Create a dummy TAR file
        tar_file = tmp_path / "test.tar"
        with tarfile.open(tar_file, 'w') as tar:
            # Add a dummy file
            info = tarfile.TarInfo(name="boot.img")
            info.size = 0
            tar.addfile(info)

        parser = FirmwareParser(str(tar_file))
        assert parser.detect_format() == FirmwareFormat.TAR

    def test_detect_tar_md5_format(self, tmp_path):
        """Test TAR.MD5 format detection"""
        tar_file = tmp_path / "test.tar.md5"
        with tarfile.open(tar_file, 'w') as tar:
            info = tarfile.TarInfo(name="boot.img")
            info.size = 0
            tar.addfile(info)

        parser = FirmwareParser(str(tar_file))
        assert parser.detect_format() == FirmwareFormat.TAR_MD5

    def test_partition_type_detection(self):
        """Test partition type detection from filename"""
        parser = FirmwareParser.__new__(FirmwareParser)

        assert parser._detect_partition_type("boot.img") == "boot"
        assert parser._detect_partition_type("system.img") == "system"
        assert parser._detect_partition_type("vendor.img") == "vendor"
        assert parser._detect_partition_type("recovery.img") == "recovery"
        assert parser._detect_partition_type("unknown.bin") == "unknown"

    def test_samsung_filename_parsing(self):
        """Test Samsung firmware filename parsing"""
        parser = FirmwareParser.__new__(FirmwareParser)
        parser.firmware_path = Path("SM-G991B_1_20230101120000_abcdefg_fac.tar.md5")

        vendor, device, version = parser._parse_filename_metadata()
        assert vendor == "Samsung"
        assert device == "SM-G991B"
        assert version == "1"

    def test_file_not_found(self, tmp_path):
        """Test error handling for non-existent file"""
        parser = FirmwareParser(str(tmp_path / "nonexistent.tar"))
        with pytest.raises(FileNotFoundError):
            parser.detect_format()


class TestFirmwareInfo:
    """Test firmware info extraction"""

    def test_partition_list(self, tmp_path):
        """Test getting partition list"""
        tar_file = tmp_path / "test.tar"
        with tarfile.open(tar_file, 'w') as tar:
            for name in ["boot.img", "system.img", "vendor.img"]:
                info = tarfile.TarInfo(name=name)
                info.size = 1024
                tar.addfile(info)

        parser = FirmwareParser(str(tar_file))
        info = parser.parse()

        assert len(info.partitions) == 3
        partition_names = [p.name for p in info.partitions]
        assert "boot.img" in partition_names
        assert "system.img" in partition_names
        assert "vendor.img" in partition_names


# Fixtures for test data
@pytest.fixture
def sample_firmware(tmp_path):
    """Create a sample firmware file for testing"""
    tar_file = tmp_path / "sample.tar.md5"
    with tarfile.open(tar_file, 'w') as tar:
        # Add sample partitions
        for name, size in [("boot.img", 1024), ("system.img", 2048)]:
            info = tarfile.TarInfo(name=name)
            info.size = size
            tar.addfile(info)
    return tar_file
