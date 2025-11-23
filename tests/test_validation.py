"""
Unit tests for input validation utilities
"""
import pytest
from pathlib import Path
from samfwtool.utils.validation import (
    validate_path,
    validate_firmware_path,
    validate_output_path,
    validate_partition_name,
    sanitize_filename,
    is_safe_path,
)
from samfwtool.exceptions import PathValidationError, ValidationError


class TestValidatePath:
    """Test path validation"""

    def test_valid_path(self, tmp_path):
        """Test validating a valid path"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        result = validate_path(str(test_file), must_exist=True, must_be_file=True)
        assert result == test_file

    def test_empty_path(self):
        """Test empty path raises error"""
        with pytest.raises(PathValidationError, match="cannot be empty"):
            validate_path("")

    def test_nonexistent_path(self, tmp_path):
        """Test non-existent path with must_exist"""
        with pytest.raises(PathValidationError, match="does not exist"):
            validate_path(str(tmp_path / "nonexistent"), must_exist=True)

    def test_path_not_file(self, tmp_path):
        """Test directory when file expected"""
        with pytest.raises(PathValidationError, match="not a file"):
            validate_path(str(tmp_path), must_exist=True, must_be_file=True)

    def test_path_not_dir(self, tmp_path):
        """Test file when directory expected"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        with pytest.raises(PathValidationError, match="not a directory"):
            validate_path(str(test_file), must_exist=True, must_be_dir=True)

    def test_allowed_extensions(self, tmp_path):
        """Test allowed extensions validation"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        with pytest.raises(PathValidationError, match="Invalid file extension"):
            validate_path(str(test_file), allowed_extensions=[".tar", ".zip"])

    def test_allowed_extension_tar_md5(self, tmp_path):
        """Test .tar.md5 extension"""
        test_file = tmp_path / "firmware.tar.md5"
        test_file.write_text("test")

        result = validate_path(
            str(test_file),
            allowed_extensions=[".tar", ".tar.md5"]
        )
        assert result == test_file

    def test_base_dir_constraint(self, tmp_path):
        """Test base directory constraint"""
        # Create a file outside base_dir
        other_dir = tmp_path / "other"
        other_dir.mkdir()
        test_file = other_dir / "test.txt"
        test_file.write_text("test")

        base_dir = tmp_path / "allowed"
        base_dir.mkdir()

        with pytest.raises(PathValidationError, match="must be within"):
            validate_path(str(test_file), base_dir=base_dir)


class TestValidateFirmwarePath:
    """Test firmware path validation"""

    def test_valid_tar_file(self, tmp_path):
        """Test valid TAR firmware file"""
        firmware = tmp_path / "firmware.tar"
        firmware.write_text("fake tar")

        result = validate_firmware_path(str(firmware))
        assert result == firmware

    def test_valid_tar_md5_file(self, tmp_path):
        """Test valid TAR.MD5 firmware file"""
        firmware = tmp_path / "firmware.tar.md5"
        firmware.write_text("fake tar md5")

        result = validate_firmware_path(str(firmware))
        assert result == firmware

    def test_invalid_extension(self, tmp_path):
        """Test invalid firmware extension"""
        firmware = tmp_path / "firmware.exe"
        firmware.write_text("fake exe")

        with pytest.raises(PathValidationError, match="Invalid file extension"):
            validate_firmware_path(str(firmware))


class TestValidatePartitionName:
    """Test partition name validation"""

    def test_valid_names(self):
        """Test valid partition names"""
        valid_names = ["boot", "system", "vendor", "boot.img", "system_a", "super-partition"]
        for name in valid_names:
            assert validate_partition_name(name) == name

    def test_empty_name(self):
        """Test empty partition name"""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_partition_name("")

    def test_invalid_characters(self):
        """Test invalid characters in partition name"""
        with pytest.raises(ValidationError, match="Invalid partition name"):
            validate_partition_name("boot/../system")

    def test_special_characters(self):
        """Test special characters"""
        with pytest.raises(ValidationError, match="Invalid partition name"):
            validate_partition_name("boot<>system")


class TestSanitizeFilename:
    """Test filename sanitization"""

    def test_normal_filename(self):
        """Test normal filename"""
        assert sanitize_filename("boot.img") == "boot.img"

    def test_path_in_filename(self):
        """Test path separators removed"""
        assert sanitize_filename("/path/to/boot.img") == "boot.img"

    def test_dangerous_characters(self):
        """Test dangerous characters replaced"""
        result = sanitize_filename('file<>:"|?*.img')
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result

    def test_empty_filename(self):
        """Test empty filename"""
        assert sanitize_filename("") == "unnamed"

    def test_null_bytes(self):
        """Test null bytes removed"""
        result = sanitize_filename("file\x00name.img")
        assert "\x00" not in result


class TestIsSafePath:
    """Test is_safe_path function"""

    def test_safe_path(self, tmp_path):
        """Test safe path returns True"""
        assert is_safe_path(str(tmp_path))

    def test_unsafe_empty_path(self):
        """Test unsafe path returns False"""
        assert is_safe_path("") is False
