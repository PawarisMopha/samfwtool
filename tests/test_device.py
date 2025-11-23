"""
Unit tests for device detection and flashing
"""
import pytest
from unittest.mock import patch, MagicMock
from samfwtool.flash.device import (
    Device,
    DeviceMode,
    DeviceVendor,
    DeviceDetector,
)
from samfwtool.flash.flasher import DeviceFlasher, FlashResult


class TestDeviceMode:
    """Test device mode enumeration"""

    def test_device_modes(self):
        """Test that all device modes are defined"""
        assert DeviceMode.ADB.value == "adb"
        assert DeviceMode.FASTBOOT.value == "fastboot"
        assert DeviceMode.DOWNLOAD.value == "download"
        assert DeviceMode.RECOVERY.value == "recovery"
        assert DeviceMode.EDL.value == "edl"
        assert DeviceMode.UNKNOWN.value == "unknown"


class TestDeviceVendor:
    """Test device vendor enumeration"""

    def test_device_vendors(self):
        """Test that all device vendors are defined"""
        assert DeviceVendor.SAMSUNG.value == "samsung"
        assert DeviceVendor.GOOGLE.value == "google"
        assert DeviceVendor.XIAOMI.value == "xiaomi"
        assert DeviceVendor.ONEPLUS.value == "oneplus"
        assert DeviceVendor.MOTOROLA.value == "motorola"
        assert DeviceVendor.GENERIC.value == "generic"


class TestDevice:
    """Test Device dataclass"""

    def test_create_device(self):
        """Test creating a device instance"""
        device = Device(
            serial="ABC123",
            vendor=DeviceVendor.SAMSUNG,
            model="SM-G991B",
            mode=DeviceMode.FASTBOOT,
            bootloader_locked=False,
            properties={"ro.product.name": "test"},
        )

        assert device.serial == "ABC123"
        assert device.vendor == DeviceVendor.SAMSUNG
        assert device.model == "SM-G991B"
        assert device.mode == DeviceMode.FASTBOOT
        assert device.bootloader_locked is False


class TestDeviceDetector:
    """Test device detection functionality"""

    def test_detect_vendor_samsung(self):
        """Test Samsung vendor detection"""
        props = {"ro.product.manufacturer": "samsung", "ro.product.brand": "samsung"}
        vendor = DeviceDetector._detect_vendor(props)
        assert vendor == DeviceVendor.SAMSUNG

    def test_detect_vendor_google(self):
        """Test Google vendor detection"""
        props = {"ro.product.manufacturer": "Google", "ro.product.brand": "google"}
        vendor = DeviceDetector._detect_vendor(props)
        assert vendor == DeviceVendor.GOOGLE

    def test_detect_vendor_xiaomi(self):
        """Test Xiaomi vendor detection"""
        props = {"ro.product.manufacturer": "Xiaomi", "ro.product.brand": "Redmi"}
        vendor = DeviceDetector._detect_vendor(props)
        assert vendor == DeviceVendor.XIAOMI

    def test_detect_vendor_oneplus(self):
        """Test OnePlus vendor detection"""
        props = {"ro.product.manufacturer": "OnePlus", "ro.product.brand": "oneplus"}
        vendor = DeviceDetector._detect_vendor(props)
        assert vendor == DeviceVendor.ONEPLUS

    def test_detect_vendor_motorola(self):
        """Test Motorola vendor detection"""
        props = {"ro.product.manufacturer": "motorola", "ro.product.brand": "motorola"}
        vendor = DeviceDetector._detect_vendor(props)
        assert vendor == DeviceVendor.MOTOROLA

    def test_detect_vendor_generic(self):
        """Test generic vendor detection"""
        props = {"ro.product.manufacturer": "unknown", "ro.product.brand": "unknown"}
        vendor = DeviceDetector._detect_vendor(props)
        assert vendor == DeviceVendor.GENERIC

    @patch('subprocess.run')
    def test_detect_adb_devices_none(self, mock_run):
        """Test ADB detection when no devices"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="List of devices attached\n\n"
        )
        devices = DeviceDetector.detect_adb_devices()
        assert devices == []

    @patch('subprocess.run')
    def test_detect_fastboot_devices_none(self, mock_run):
        """Test Fastboot detection when no devices"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=""
        )
        devices = DeviceDetector.detect_fastboot_devices()
        assert devices == []


class TestFlashResult:
    """Test flash result enumeration"""

    def test_flash_results(self):
        """Test that all flash results are defined"""
        assert FlashResult.SUCCESS.value == "success"
        assert FlashResult.FAILED.value == "failed"
        assert FlashResult.DEVICE_NOT_FOUND.value == "device_not_found"
        assert FlashResult.BOOTLOADER_LOCKED.value == "bootloader_locked"
        assert FlashResult.INVALID_IMAGE.value == "invalid_image"
        assert FlashResult.USER_CANCELLED.value == "user_cancelled"


class TestDeviceFlasher:
    """Test device flasher functionality"""

    def test_flash_nonexistent_image(self, tmp_path):
        """Test flashing with non-existent image"""
        device = Device(
            serial="ABC123",
            vendor=DeviceVendor.GOOGLE,
            model="Pixel",
            mode=DeviceMode.FASTBOOT,
            bootloader_locked=False,
            properties={},
        )

        flasher = DeviceFlasher(device)
        result = flasher.flash_partition("boot", tmp_path / "nonexistent.img")

        assert result == FlashResult.INVALID_IMAGE

    def test_flash_locked_bootloader(self, tmp_path):
        """Test flashing with locked bootloader"""
        device = Device(
            serial="ABC123",
            vendor=DeviceVendor.GOOGLE,
            model="Pixel",
            mode=DeviceMode.FASTBOOT,
            bootloader_locked=True,  # Locked
            properties={},
        )

        # Create a dummy image
        image = tmp_path / "boot.img"
        image.write_bytes(b"fake image")

        flasher = DeviceFlasher(device, safety_checks=True)
        result = flasher.flash_partition("boot", image)

        assert result == FlashResult.BOOTLOADER_LOCKED

    def test_safety_warnings_critical_partition(self):
        """Test safety warnings for critical partitions"""
        device = Device(
            serial="ABC123",
            vendor=DeviceVendor.GOOGLE,
            model="Pixel",
            mode=DeviceMode.FASTBOOT,
            bootloader_locked=True,
            properties={},
        )

        flasher = DeviceFlasher(device)
        warnings = flasher.get_safety_warnings("bootloader")

        assert len(warnings) > 0
        assert any("CRITICAL" in w for w in warnings)
        assert any("LOCKED" in w for w in warnings)
