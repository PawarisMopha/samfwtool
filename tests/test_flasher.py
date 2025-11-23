"""
Unit tests for device flasher module
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
import subprocess

from samfwtool.flash.flasher import DeviceFlasher, FlashResult
from samfwtool.flash.device import Device, DeviceMode, DeviceVendor


@pytest.fixture
def mock_device():
    """Create a mock device for testing"""
    device = MagicMock(spec=Device)
    device.serial = "ABC12345"
    device.model = "SM-G960F"
    device.vendor = DeviceVendor.SAMSUNG
    device.mode = DeviceMode.FASTBOOT
    device.bootloader_locked = False
    return device


@pytest.fixture
def mock_locked_device():
    """Create a mock device with locked bootloader"""
    device = MagicMock(spec=Device)
    device.serial = "ABC12345"
    device.model = "SM-G960F"
    device.vendor = DeviceVendor.SAMSUNG
    device.mode = DeviceMode.FASTBOOT
    device.bootloader_locked = True
    return device


class TestFlashResult:
    """Test FlashResult enum"""

    def test_flash_result_values(self):
        """Test FlashResult enum values"""
        assert FlashResult.SUCCESS.value == "success"
        assert FlashResult.FAILED.value == "failed"
        assert FlashResult.DEVICE_NOT_FOUND.value == "device_not_found"
        assert FlashResult.BOOTLOADER_LOCKED.value == "bootloader_locked"
        assert FlashResult.INVALID_IMAGE.value == "invalid_image"
        assert FlashResult.USER_CANCELLED.value == "user_cancelled"


class TestDeviceFlasherInit:
    """Test DeviceFlasher initialization"""

    def test_init(self, mock_device):
        """Test flasher initialization"""
        flasher = DeviceFlasher(mock_device)

        assert flasher.device == mock_device
        assert flasher.safety_checks is True
        assert flasher.progress_callback is None

    def test_init_no_safety_checks(self, mock_device):
        """Test flasher with disabled safety checks"""
        flasher = DeviceFlasher(mock_device, safety_checks=False)

        assert flasher.safety_checks is False

    def test_set_progress_callback(self, mock_device):
        """Test setting progress callback"""
        flasher = DeviceFlasher(mock_device)

        callback = MagicMock()
        flasher.set_progress_callback(callback)

        assert flasher.progress_callback == callback


class TestFlashPartition:
    """Test flash_partition method"""

    def test_flash_invalid_image_path(self, mock_device, tmp_path):
        """Test flashing non-existent image"""
        flasher = DeviceFlasher(mock_device)

        result = flasher.flash_partition("boot", tmp_path / "nonexistent.img")

        assert result == FlashResult.INVALID_IMAGE

    def test_flash_locked_bootloader(self, mock_locked_device, tmp_path):
        """Test flashing with locked bootloader"""
        flasher = DeviceFlasher(mock_locked_device)

        image = tmp_path / "boot.img"
        image.write_bytes(b"boot content")

        result = flasher.flash_partition("boot", image)

        assert result == FlashResult.BOOTLOADER_LOCKED

    @patch('subprocess.run')
    @patch('builtins.input', return_value='yes')
    def test_flash_fastboot_success(self, mock_input, mock_run, mock_device, tmp_path):
        """Test successful fastboot flash"""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        flasher = DeviceFlasher(mock_device)
        image = tmp_path / "boot.img"
        image.write_bytes(b"boot content")

        result = flasher.flash_partition("boot", image)

        assert result == FlashResult.SUCCESS
        mock_run.assert_called_once()

    @patch('subprocess.run')
    @patch('builtins.input', return_value='yes')
    def test_flash_fastboot_failure(self, mock_input, mock_run, mock_device, tmp_path):
        """Test failed fastboot flash"""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="flash failed")

        flasher = DeviceFlasher(mock_device)
        image = tmp_path / "boot.img"
        image.write_bytes(b"boot content")

        result = flasher.flash_partition("boot", image)

        assert result == FlashResult.FAILED

    @patch('subprocess.run')
    @patch('builtins.input', return_value='yes')
    def test_flash_fastboot_timeout(self, mock_input, mock_run, mock_device, tmp_path):
        """Test fastboot flash timeout"""
        mock_run.side_effect = subprocess.TimeoutExpired("fastboot", 300)

        flasher = DeviceFlasher(mock_device)
        image = tmp_path / "boot.img"
        image.write_bytes(b"boot content")

        result = flasher.flash_partition("boot", image)

        assert result == FlashResult.FAILED

    @patch('builtins.input', return_value='no')
    def test_flash_user_cancelled(self, mock_input, mock_device, tmp_path):
        """Test user cancellation"""
        flasher = DeviceFlasher(mock_device)
        image = tmp_path / "boot.img"
        image.write_bytes(b"boot content")

        result = flasher.flash_partition("boot", image)

        assert result == FlashResult.USER_CANCELLED

    def test_flash_no_safety_checks(self, mock_device, tmp_path):
        """Test flashing without safety checks skips confirmation"""
        mock_device.mode = DeviceMode.RECOVERY  # Use unsupported mode
        flasher = DeviceFlasher(mock_device, safety_checks=False)

        image = tmp_path / "boot.img"
        image.write_bytes(b"boot content")

        result = flasher.flash_partition("boot", image)

        # Should fail due to unsupported mode, not user cancellation
        assert result == FlashResult.FAILED


class TestFlashModes:
    """Test flashing in different device modes"""

    @patch('subprocess.run')
    @patch('builtins.input', return_value='yes')
    @patch('time.sleep')
    def test_flash_adb_mode(self, mock_sleep, mock_input, mock_run, mock_device, tmp_path):
        """Test flashing in ADB mode reboots to bootloader"""
        mock_device.mode = DeviceMode.ADB
        mock_run.return_value = MagicMock(returncode=0)

        flasher = DeviceFlasher(mock_device)
        image = tmp_path / "boot.img"
        image.write_bytes(b"content")

        result = flasher.flash_partition("boot", image)

        assert result == FlashResult.SUCCESS
        # Should have called adb reboot and fastboot flash
        assert mock_run.call_count == 2

    @patch('subprocess.run')
    @patch('builtins.input', return_value='yes')
    def test_flash_download_mode(self, mock_input, mock_run, mock_device, tmp_path):
        """Test flashing in Samsung download mode"""
        mock_device.mode = DeviceMode.DOWNLOAD
        mock_run.return_value = MagicMock(returncode=0)

        flasher = DeviceFlasher(mock_device)
        image = tmp_path / "boot.img"
        image.write_bytes(b"content")

        result = flasher.flash_partition("boot", image)

        assert result == FlashResult.SUCCESS


class TestSamsungFlashing:
    """Test Samsung-specific flashing"""

    @patch('subprocess.run')
    @patch('builtins.input', return_value='yes')
    def test_samsung_partition_mapping(self, mock_input, mock_run, mock_device, tmp_path):
        """Test Samsung partition name mapping"""
        mock_device.mode = DeviceMode.DOWNLOAD
        mock_run.return_value = MagicMock(returncode=0)

        flasher = DeviceFlasher(mock_device)
        image = tmp_path / "boot.img"
        image.write_bytes(b"content")

        flasher.flash_partition("boot", image)

        # Verify heimdall was called with uppercase partition name
        call_args = mock_run.call_args[0][0]
        assert '--BOOT' in call_args

    @patch('subprocess.run')
    @patch('builtins.input', return_value='yes')
    def test_samsung_heimdall_not_found(self, mock_input, mock_run, mock_device, tmp_path):
        """Test when heimdall is not installed"""
        mock_device.mode = DeviceMode.DOWNLOAD
        mock_run.side_effect = FileNotFoundError("heimdall not found")

        flasher = DeviceFlasher(mock_device)
        image = tmp_path / "boot.img"
        image.write_bytes(b"content")

        result = flasher.flash_partition("boot", image)

        assert result == FlashResult.FAILED


class TestFullFirmwareFlash:
    """Test full firmware flashing"""

    @patch('subprocess.run')
    @patch('builtins.input', return_value='I UNDERSTAND')
    def test_flash_full_samsung_firmware(self, mock_input, mock_run, mock_device, tmp_path):
        """Test flashing complete Samsung firmware"""
        mock_run.return_value = MagicMock(returncode=0)

        flasher = DeviceFlasher(mock_device)
        firmware = tmp_path / "firmware.tar.md5"
        firmware.write_bytes(b"fake firmware")

        result = flasher.flash_full_firmware(firmware)

        assert result == FlashResult.SUCCESS

    @patch('builtins.input', return_value='no')
    def test_flash_full_firmware_cancelled(self, mock_input, mock_device, tmp_path):
        """Test user cancellation for full firmware flash"""
        flasher = DeviceFlasher(mock_device)
        firmware = tmp_path / "firmware.tar.md5"
        firmware.write_bytes(b"fake firmware")

        result = flasher.flash_full_firmware(firmware)

        assert result == FlashResult.USER_CANCELLED

    @patch('builtins.input', return_value='I UNDERSTAND')
    def test_flash_generic_firmware(self, mock_input, mock_device, tmp_path):
        """Test generic firmware flash (not implemented)"""
        mock_device.vendor = DeviceVendor.GENERIC

        flasher = DeviceFlasher(mock_device)
        firmware = tmp_path / "firmware.zip"
        firmware.write_bytes(b"fake firmware")

        result = flasher.flash_full_firmware(firmware)

        assert result == FlashResult.FAILED  # Not implemented


class TestBackupPartition:
    """Test partition backup functionality"""

    @patch('subprocess.run')
    def test_backup_adb_success(self, mock_run, mock_device, tmp_path):
        """Test successful ADB backup"""
        mock_device.mode = DeviceMode.ADB
        # First call finds partition, second pulls it
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="/dev/block/boot"),
            MagicMock(returncode=0),
        ]

        flasher = DeviceFlasher(mock_device)
        output = tmp_path / "boot_backup.img"

        result = flasher.backup_partition("boot", output)

        assert result is True

    @patch('subprocess.run')
    def test_backup_adb_partition_not_found(self, mock_run, mock_device, tmp_path):
        """Test backup when partition not found"""
        mock_device.mode = DeviceMode.ADB
        mock_run.return_value = MagicMock(returncode=1, stdout="")

        flasher = DeviceFlasher(mock_device)
        output = tmp_path / "boot_backup.img"

        result = flasher.backup_partition("boot", output)

        assert result is False

    def test_backup_unsupported_mode(self, mock_device, tmp_path):
        """Test backup in unsupported mode"""
        mock_device.mode = DeviceMode.FASTBOOT

        flasher = DeviceFlasher(mock_device)
        output = tmp_path / "boot_backup.img"

        result = flasher.backup_partition("boot", output)

        assert result is False


class TestSafetyWarnings:
    """Test safety warning functionality"""

    def test_critical_partition_warning(self, mock_device):
        """Test warning for critical partitions"""
        flasher = DeviceFlasher(mock_device)

        warnings = flasher.get_safety_warnings("bootloader")

        assert len(warnings) >= 1
        assert any("CRITICAL" in w for w in warnings)

    def test_locked_bootloader_warning(self, mock_locked_device):
        """Test warning for locked bootloader"""
        flasher = DeviceFlasher(mock_locked_device)

        warnings = flasher.get_safety_warnings("boot")

        assert len(warnings) >= 1
        assert any("LOCKED" in w for w in warnings)

    def test_no_warnings_safe_partition(self, mock_device):
        """Test no warnings for safe partitions on unlocked device"""
        flasher = DeviceFlasher(mock_device)

        warnings = flasher.get_safety_warnings("cache")

        assert len(warnings) == 0

    def test_multiple_critical_partitions(self, mock_device):
        """Test warnings for various critical partitions"""
        flasher = DeviceFlasher(mock_device)

        critical = ['bootloader', 'aboot', 'sbl1', 'rpm', 'tz']
        for partition in critical:
            warnings = flasher.get_safety_warnings(partition)
            assert any("CRITICAL" in w for w in warnings), f"No warning for {partition}"


class TestADBReboot:
    """Test ADB reboot functionality"""

    @patch('subprocess.run')
    def test_adb_reboot_bootloader(self, mock_run, mock_device):
        """Test ADB reboot to bootloader"""
        mock_run.return_value = MagicMock(returncode=0)

        flasher = DeviceFlasher(mock_device)
        flasher._adb_reboot_bootloader()

        call_args = mock_run.call_args[0][0]
        assert 'adb' in call_args
        assert 'reboot' in call_args
        assert 'bootloader' in call_args
