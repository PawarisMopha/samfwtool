"""
Unit tests for custom exceptions
"""
import pytest
from samfwtool.exceptions import (
    SamFWToolError,
    FirmwareError,
    FirmwareParseError,
    FirmwareExtractionError,
    FirmwarePackError,
    DeviceError,
    DeviceNotFoundError,
    DeviceFlashError,
    BootloaderLockedError,
    SecurityScanError,
    ValidationError,
    PathValidationError,
    ChecksumError,
)


class TestSamFWToolError:
    """Test base SamFWToolError"""

    def test_basic_error(self):
        """Test basic error creation"""
        err = SamFWToolError("Test error")
        assert err.message == "Test error"
        assert err.details is None
        assert str(err) == "Test error"

    def test_error_with_details(self):
        """Test error with details"""
        err = SamFWToolError("Test error", details="More info")
        assert err.message == "Test error"
        assert err.details == "More info"
        assert str(err) == "Test error: More info"

    def test_error_inheritance(self):
        """Test that it inherits from Exception"""
        err = SamFWToolError("Test")
        assert isinstance(err, Exception)


class TestFirmwareErrors:
    """Test firmware-related exceptions"""

    def test_firmware_error(self):
        """Test base FirmwareError"""
        err = FirmwareError("Firmware issue")
        assert isinstance(err, SamFWToolError)
        assert str(err) == "Firmware issue"

    def test_firmware_parse_error(self):
        """Test FirmwareParseError"""
        err = FirmwareParseError("Parse failed", firmware_path="/path/to/file.tar")
        assert err.firmware_path == "/path/to/file.tar"
        assert isinstance(err, FirmwareError)

    def test_firmware_parse_error_with_details(self):
        """Test FirmwareParseError with details"""
        err = FirmwareParseError("Parse failed", firmware_path="/path", details="Invalid format")
        assert err.firmware_path == "/path"
        assert err.details == "Invalid format"
        assert "Invalid format" in str(err)

    def test_firmware_extraction_error(self):
        """Test FirmwareExtractionError"""
        err = FirmwareExtractionError("Extract failed", partition="boot")
        assert err.partition == "boot"
        assert isinstance(err, FirmwareError)

    def test_firmware_extraction_error_with_details(self):
        """Test FirmwareExtractionError with details"""
        err = FirmwareExtractionError("Extract failed", partition="system", details="Corrupted")
        assert err.partition == "system"
        assert err.details == "Corrupted"

    def test_firmware_pack_error(self):
        """Test FirmwarePackError"""
        err = FirmwarePackError("Pack failed")
        assert isinstance(err, FirmwareError)


class TestDeviceErrors:
    """Test device-related exceptions"""

    def test_device_error(self):
        """Test base DeviceError"""
        err = DeviceError("Device issue")
        assert isinstance(err, SamFWToolError)

    def test_device_not_found_error_default(self):
        """Test DeviceNotFoundError with default message"""
        err = DeviceNotFoundError()
        assert err.message == "No device found"
        assert err.serial is None

    def test_device_not_found_error_with_serial(self):
        """Test DeviceNotFoundError with serial"""
        err = DeviceNotFoundError("Device disconnected", serial="ABC123")
        assert err.serial == "ABC123"
        assert err.message == "Device disconnected"

    def test_device_flash_error(self):
        """Test DeviceFlashError"""
        err = DeviceFlashError("Flash failed", partition="boot")
        assert err.partition == "boot"
        assert isinstance(err, DeviceError)

    def test_device_flash_error_with_details(self):
        """Test DeviceFlashError with details"""
        err = DeviceFlashError("Flash failed", partition="system", details="Timeout")
        assert err.partition == "system"
        assert err.details == "Timeout"

    def test_bootloader_locked_error_default(self):
        """Test BootloaderLockedError with default message"""
        err = BootloaderLockedError()
        assert err.message == "Bootloader is locked"
        assert err.device_model is None

    def test_bootloader_locked_error_with_model(self):
        """Test BootloaderLockedError with device model"""
        err = BootloaderLockedError("Cannot flash", device_model="SM-G991B")
        assert err.device_model == "SM-G991B"


class TestSecurityScanError:
    """Test SecurityScanError"""

    def test_security_scan_error(self):
        """Test SecurityScanError creation"""
        err = SecurityScanError("Scan failed")
        assert isinstance(err, SamFWToolError)
        assert str(err) == "Scan failed"


class TestValidationErrors:
    """Test validation exceptions"""

    def test_validation_error(self):
        """Test base ValidationError"""
        err = ValidationError("Invalid input")
        assert isinstance(err, SamFWToolError)

    def test_path_validation_error(self):
        """Test PathValidationError"""
        err = PathValidationError("Invalid path", path="/bad/path")
        assert err.path == "/bad/path"
        assert isinstance(err, ValidationError)

    def test_checksum_error_basic(self):
        """Test ChecksumError without expected/actual"""
        err = ChecksumError("Checksum mismatch")
        assert err.expected is None
        assert err.actual is None
        assert err.details is None

    def test_checksum_error_with_values(self):
        """Test ChecksumError with expected and actual values"""
        err = ChecksumError("Checksum mismatch", expected="abc123", actual="def456")
        assert err.expected == "abc123"
        assert err.actual == "def456"
        assert "Expected: abc123" in str(err)
        assert "Got: def456" in str(err)

    def test_checksum_error_partial_values(self):
        """Test ChecksumError with only expected value"""
        err = ChecksumError("Checksum mismatch", expected="abc123")
        assert err.expected == "abc123"
        assert err.actual is None
        assert err.details is None  # details only set when both are provided


class TestExceptionHierarchy:
    """Test exception class hierarchy"""

    def test_firmware_errors_are_samfwtool_errors(self):
        """Test that all firmware errors inherit from SamFWToolError"""
        assert issubclass(FirmwareError, SamFWToolError)
        assert issubclass(FirmwareParseError, SamFWToolError)
        assert issubclass(FirmwareExtractionError, SamFWToolError)
        assert issubclass(FirmwarePackError, SamFWToolError)

    def test_device_errors_are_samfwtool_errors(self):
        """Test that all device errors inherit from SamFWToolError"""
        assert issubclass(DeviceError, SamFWToolError)
        assert issubclass(DeviceNotFoundError, SamFWToolError)
        assert issubclass(DeviceFlashError, SamFWToolError)
        assert issubclass(BootloaderLockedError, SamFWToolError)

    def test_validation_errors_are_samfwtool_errors(self):
        """Test that all validation errors inherit from SamFWToolError"""
        assert issubclass(ValidationError, SamFWToolError)
        assert issubclass(PathValidationError, SamFWToolError)
        assert issubclass(ChecksumError, SamFWToolError)

    def test_can_catch_base_exception(self):
        """Test that SamFWToolError can catch all custom exceptions"""
        exceptions_to_test = [
            FirmwareError("test"),
            FirmwareParseError("test"),
            DeviceError("test"),
            DeviceNotFoundError(),
            ValidationError("test"),
            PathValidationError("test"),
            ChecksumError("test"),
        ]

        for exc in exceptions_to_test:
            try:
                raise exc
            except SamFWToolError as e:
                assert e is exc
