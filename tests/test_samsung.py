"""
Unit tests for Samsung device support
"""
import pytest
from samfwtool.devices.samsung import SamsungDevice


class TestSamsungDevice:
    """Test SamsungDevice class"""

    def test_init_galaxy_s(self):
        """Test initialization with Galaxy S model"""
        device = SamsungDevice("SM-G991B")
        assert device.model == "SM-G991B"
        assert device.series == "Galaxy S Series"

    def test_init_galaxy_note(self):
        """Test initialization with Galaxy Note model"""
        device = SamsungDevice("SM-N976V")
        assert device.model == "SM-N976V"
        assert device.series == "Galaxy Note Series"

    def test_init_galaxy_a(self):
        """Test initialization with Galaxy A model"""
        device = SamsungDevice("SM-A515F")
        assert device.series == "Galaxy A Series"

    def test_init_galaxy_m(self):
        """Test initialization with Galaxy M model"""
        device = SamsungDevice("SM-M317F")
        assert device.series == "Galaxy M Series"

    def test_init_galaxy_fold(self):
        """Test initialization with Galaxy Fold model"""
        device = SamsungDevice("SM-F926B")
        assert device.series == "Galaxy Fold Series"

    def test_init_galaxy_z(self):
        """Test initialization with Galaxy Z model"""
        device = SamsungDevice("SM-Z123")
        assert device.series == "Galaxy Z Series"

    def test_init_unknown_series(self):
        """Test initialization with unknown model"""
        device = SamsungDevice("UNKNOWN-123")
        assert device.series == "Unknown Series"


class TestPartitionInfo:
    """Test partition information methods"""

    def test_get_partition_info_bl(self):
        """Test getting BL partition info"""
        device = SamsungDevice("SM-G991B")
        info = device.get_partition_info("BL")

        assert info["short_name"] == "BL"
        assert info["full_name"] == "bootloader"
        assert info["critical"] is True
        assert "Bootloader" in info["description"]

    def test_get_partition_info_ap(self):
        """Test getting AP partition info"""
        device = SamsungDevice("SM-G991B")
        info = device.get_partition_info("AP")

        assert info["short_name"] == "AP"
        assert info["full_name"] == "system"
        assert info["critical"] is True
        assert "Android" in info["description"]

    def test_get_partition_info_cp(self):
        """Test getting CP partition info"""
        device = SamsungDevice("SM-G991B")
        info = device.get_partition_info("CP")

        assert info["full_name"] == "modem"
        assert info["critical"] is False
        assert "modem" in info["description"].lower()

    def test_get_partition_info_csc(self):
        """Test getting CSC partition info"""
        device = SamsungDevice("SM-G991B")
        info = device.get_partition_info("CSC")

        assert info["full_name"] == "customer_software_customization"
        assert "region" in info["description"].lower()

    def test_get_partition_info_home_csc(self):
        """Test getting HOME_CSC partition info"""
        device = SamsungDevice("SM-G991B")
        info = device.get_partition_info("HOME_CSC")

        assert "wipe" in info["description"].lower()

    def test_get_partition_info_unknown(self):
        """Test getting unknown partition info"""
        device = SamsungDevice("SM-G991B")
        info = device.get_partition_info("UNKNOWN")

        assert info["short_name"] == "UNKNOWN"
        assert info["full_name"] == "UNKNOWN"
        assert info["critical"] is False


class TestFirmwareValidation:
    """Test firmware validation methods"""

    def test_validate_complete_firmware(self):
        """Test validating complete firmware"""
        device = SamsungDevice("SM-G991B")
        files = ["BL_G991B.tar", "AP_G991B.tar", "CP_G991B.tar", "CSC_G991B.tar"]

        result = device.validate_firmware_structure(files)

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_missing_bl(self):
        """Test validating firmware missing BL"""
        device = SamsungDevice("SM-G991B")
        files = ["AP_G991B.tar", "CP_G991B.tar", "CSC_G991B.tar"]

        result = device.validate_firmware_structure(files)

        assert result["valid"] is False
        assert any("BL" in err for err in result["errors"])

    def test_validate_csc_warning(self):
        """Test CSC vs HOME_CSC warning"""
        device = SamsungDevice("SM-G991B")
        files = ["BL_G991B.tar", "AP_G991B.tar", "CP_G991B.tar", "CSC_G991B.tar"]

        result = device.validate_firmware_structure(files)

        assert any("wipe" in w.lower() for w in result["warnings"])

    def test_validate_empty_firmware(self):
        """Test validating empty firmware list"""
        device = SamsungDevice("SM-G991B")
        result = device.validate_firmware_structure([])

        assert result["valid"] is False
        assert len(result["errors"]) > 0


class TestFlashOrder:
    """Test flash order methods"""

    def test_recommended_flash_order(self):
        """Test recommended flash order"""
        device = SamsungDevice("SM-G991B")
        order = device.get_recommended_flash_order()

        assert order == ["BL", "AP", "CP", "CSC"]
        assert order[0] == "BL"  # Bootloader first


class TestFilenameParser:
    """Test firmware filename parsing"""

    def test_parse_full_filename(self):
        """Test parsing full Samsung firmware filename"""
        info = SamsungDevice.parse_firmware_filename(
            "SM-G991B_1_20230101120000_abcdefg_fac.tar.md5"
        )

        assert info["model"] == "SM-G991B"
        assert info["region"] == "1"
        assert info["build_date"] == "20230101120000"
        assert info["changelist"] == "abcdefg"
        assert info["type"] == "fac"

    def test_parse_tar_filename(self):
        """Test parsing .tar filename"""
        info = SamsungDevice.parse_firmware_filename(
            "SM-A515F_XEF_20220601_abc_fac.tar"
        )

        assert info["model"] == "SM-A515F"

    def test_parse_short_filename(self):
        """Test parsing short filename"""
        info = SamsungDevice.parse_firmware_filename("SM-G991B.tar.md5")

        assert info["model"] == "SM-G991B"
        assert info["region"] == "unknown"

    def test_parse_minimal_filename(self):
        """Test parsing minimal filename"""
        info = SamsungDevice.parse_firmware_filename("firmware")

        assert info["model"] == "firmware"


class TestSamsungPartitions:
    """Test Samsung partition constants"""

    def test_partition_mapping(self):
        """Test partition name mapping"""
        assert SamsungDevice.SAMSUNG_PARTITIONS["BL"] == "bootloader"
        assert SamsungDevice.SAMSUNG_PARTITIONS["AP"] == "system"
        assert SamsungDevice.SAMSUNG_PARTITIONS["CP"] == "modem"
        assert SamsungDevice.SAMSUNG_PARTITIONS["CSC"] == "customer_software_customization"

    def test_device_models_mapping(self):
        """Test device model prefix mapping"""
        assert SamsungDevice.DEVICE_MODELS["SM-G"] == "Galaxy S Series"
        assert SamsungDevice.DEVICE_MODELS["SM-N"] == "Galaxy Note Series"
        assert SamsungDevice.DEVICE_MODELS["SM-A"] == "Galaxy A Series"
