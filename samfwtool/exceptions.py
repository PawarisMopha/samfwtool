"""
Custom exceptions for SamFWTool

Provides a hierarchy of specific exceptions for better error handling
and more informative error messages.

Author: SamFWTool Team
License: MIT
"""

__all__ = [
    "SamFWToolError",
    "FirmwareError",
    "FirmwareParseError",
    "FirmwareExtractionError",
    "FirmwarePackError",
    "DeviceError",
    "DeviceNotFoundError",
    "DeviceFlashError",
    "BootloaderLockedError",
    "SecurityScanError",
    "ValidationError",
    "PathValidationError",
    "ChecksumError",
]


class SamFWToolError(Exception):
    """Base exception for all SamFWTool errors"""

    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(message)

    def __str__(self):
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class FirmwareError(SamFWToolError):
    """Base exception for firmware-related errors"""

    pass


class FirmwareParseError(FirmwareError):
    """Error parsing firmware file"""

    def __init__(self, message: str, firmware_path: str = None, details: str = None):
        self.firmware_path = firmware_path
        super().__init__(message, details)


class FirmwareExtractionError(FirmwareError):
    """Error extracting firmware contents"""

    def __init__(self, message: str, partition: str = None, details: str = None):
        self.partition = partition
        super().__init__(message, details)


class FirmwarePackError(FirmwareError):
    """Error packing firmware files"""

    pass


class DeviceError(SamFWToolError):
    """Base exception for device-related errors"""

    pass


class DeviceNotFoundError(DeviceError):
    """No device found or device disconnected"""

    def __init__(self, message: str = "No device found", serial: str = None):
        self.serial = serial
        super().__init__(message)


class DeviceFlashError(DeviceError):
    """Error flashing device"""

    def __init__(self, message: str, partition: str = None, details: str = None):
        self.partition = partition
        super().__init__(message, details)


class BootloaderLockedError(DeviceError):
    """Device bootloader is locked"""

    def __init__(self, message: str = "Bootloader is locked", device_model: str = None):
        self.device_model = device_model
        super().__init__(message)


class SecurityScanError(SamFWToolError):
    """Error during security scanning"""

    pass


class ValidationError(SamFWToolError):
    """Base exception for validation errors"""

    pass


class PathValidationError(ValidationError):
    """Invalid or unsafe path provided"""

    def __init__(self, message: str, path: str = None):
        self.path = path
        super().__init__(message)


class ChecksumError(ValidationError):
    """Checksum validation failed"""

    def __init__(self, message: str, expected: str = None, actual: str = None):
        self.expected = expected
        self.actual = actual
        details = None
        if expected and actual:
            details = f"Expected: {expected}, Got: {actual}"
        super().__init__(message, details)
