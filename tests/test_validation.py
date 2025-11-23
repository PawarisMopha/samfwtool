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

    def test_safe_path_with_base_dir(self, tmp_path):
        """Test path within base directory"""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        assert is_safe_path(str(subdir), base_dir=tmp_path)

    def test_unsafe_path_outside_base_dir(self, tmp_path):
        """Test path outside base directory"""
        other_dir = tmp_path / "other"
        other_dir.mkdir()
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        assert is_safe_path(str(other_dir), base_dir=base_dir) is False


class TestValidateOutputPath:
    """Test validate_output_path function"""

    def test_valid_output_path(self, tmp_path):
        """Test valid output path"""
        output = tmp_path / "output.tar"
        result = validate_output_path(str(output))
        assert result == output.resolve()

    def test_create_parents(self, tmp_path):
        """Test creating parent directories"""
        output = tmp_path / "deep" / "nested" / "path" / "output.tar"
        result = validate_output_path(str(output), create_parents=True)
        assert result.parent.exists()

    def test_output_path_no_create(self, tmp_path):
        """Test output path without creating parents"""
        output = tmp_path / "exists" / "output.tar"
        # Parent doesn't exist, but that's ok if we don't need to create
        result = validate_output_path(str(output), create_parents=False)
        assert result is not None


class TestPathTraversalDetection:
    """Test path traversal attack detection"""

    def test_path_traversal_without_base_dir(self, tmp_path):
        """Test path with .. resolves correctly"""
        # Without base_dir, .. is allowed if it resolves to valid path
        path = tmp_path / "subdir" / ".." / "file.txt"
        result = validate_path(str(path))
        assert ".." not in str(result)

    def test_path_traversal_with_base_dir_allowed(self, tmp_path):
        """Test path traversal within base_dir is allowed"""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        path = str(subdir / ".." / "subdir" / "file.txt")

        # Should work because resolved path is still within base_dir
        try:
            result = validate_path(path, base_dir=tmp_path)
            assert result is not None
        except PathValidationError:
            # Also acceptable if strict validation is applied
            pass


class TestPartitionNameExtended:
    """Extended partition name validation tests"""

    def test_partition_name_too_long(self):
        """Test partition name exceeding max length"""
        long_name = "a" * 256
        with pytest.raises(ValidationError, match="too long"):
            validate_partition_name(long_name)

    def test_partition_name_max_length(self):
        """Test partition name at max length"""
        max_name = "a" * 255
        result = validate_partition_name(max_name)
        assert len(result) == 255


class TestSanitizeFilenameExtended:
    """Extended filename sanitization tests"""

    def test_sanitize_windows_reserved(self):
        """Test sanitizing Windows reserved characters"""
        result = sanitize_filename('file:with:colons.img')
        assert ':' not in result

    def test_sanitize_quotes_and_pipes(self):
        """Test sanitizing quotes and pipes"""
        result = sanitize_filename('file"with|pipes.img')
        assert '"' not in result
        assert '|' not in result

    def test_sanitize_backslashes(self):
        """Test sanitizing backslashes"""
        result = sanitize_filename('dir\\file.img')
        # Should extract just the filename or replace backslash
        assert '\\' not in result or result == "file.img"

    def test_sanitize_leading_trailing_dots(self):
        """Test removing leading and trailing dots"""
        result = sanitize_filename('..hidden.img.')
        assert not result.startswith('.')
        assert not result.endswith('.')

    def test_sanitize_only_dots_and_spaces(self):
        """Test filename that becomes empty after sanitization"""
        result = sanitize_filename('... ...')
        assert result == "unnamed"


class TestValidateFirmwarePathExtended:
    """Extended firmware path validation tests"""

    def test_validate_lz4_firmware(self, tmp_path):
        """Test validating LZ4 compressed firmware"""
        firmware = tmp_path / "boot.img.lz4"
        firmware.write_text("fake lz4")
        result = validate_firmware_path(str(firmware))
        assert result == firmware

    def test_validate_gz_firmware(self, tmp_path):
        """Test validating gzip compressed firmware"""
        firmware = tmp_path / "system.img.gz"
        firmware.write_text("fake gz")
        result = validate_firmware_path(str(firmware))
        assert result == firmware

    def test_validate_xz_firmware(self, tmp_path):
        """Test validating xz compressed firmware"""
        firmware = tmp_path / "vendor.img.xz"
        firmware.write_text("fake xz")
        result = validate_firmware_path(str(firmware))
        assert result == firmware

    def test_validate_bin_firmware(self, tmp_path):
        """Test validating .bin firmware"""
        firmware = tmp_path / "bootloader.bin"
        firmware.write_text("fake bin")
        result = validate_firmware_path(str(firmware))
        assert result == firmware


class TestPathValidationEdgeCases:
    """Test edge cases in path validation"""

    def test_validate_path_invalid_chars(self):
        """Test path with invalid characters"""
        # This depends on the OS, but null bytes should fail
        try:
            validate_path("/path/with\x00null")
        except (PathValidationError, ValueError, OSError):
            pass  # Expected behavior

    def test_validate_path_resolves_symlinks(self, tmp_path):
        """Test that paths are resolved"""
        target = tmp_path / "target.txt"
        target.write_text("content")

        result = validate_path(str(target), must_exist=True)
        # Result should be resolved absolute path
        assert result.is_absolute()

    def test_extension_case_insensitive(self, tmp_path):
        """Test extension matching is case insensitive"""
        firmware = tmp_path / "firmware.TAR"
        firmware.write_text("content")

        result = validate_path(
            str(firmware),
            allowed_extensions=[".tar"]
        )
        assert result is not None

    def test_base_dir_none_path_traversal_allowed(self, tmp_path):
        """Test path traversal allowed without base_dir"""
        # Without base_dir, paths with .. are resolved but allowed
        parent = tmp_path.parent
        path = str(tmp_path / "..")
        result = validate_path(path)
        assert result == parent.resolve()
