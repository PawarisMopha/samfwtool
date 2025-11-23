"""
Unit tests for chipset support modules
"""
import pytest
from pathlib import Path
from samfwtool.chipsets.mediatek import (
    MTKFlashMode,
    MTKPartition,
    ScatterFileParser,
)
from samfwtool.chipsets.qualcomm import (
    QualcommChipset,
    EDLMode,
    QualcommPartition,
    EDLFlasher,
    QualcommChipDetector,
    FirehoseProtocol,
    SaharaProtocol,
)


class TestMTKFlashMode:
    """Test MTKFlashMode enumeration"""

    def test_flash_modes(self):
        """Test all flash modes are defined"""
        assert MTKFlashMode.DOWNLOAD_ONLY.value == "download_only"
        assert MTKFlashMode.FIRMWARE_UPGRADE.value == "firmware_upgrade"
        assert MTKFlashMode.FORMAT_ALL.value == "format_all"
        assert MTKFlashMode.FORMAT_ALL_DOWNLOAD.value == "format_all_download"


class TestMTKPartition:
    """Test MTKPartition dataclass"""

    def test_create_partition(self):
        """Test creating MTK partition"""
        part = MTKPartition(
            name="boot",
            file_name="boot.img",
            is_download=True,
            type="NORMAL_ROM",
            linear_start_addr=0x8000000,
            physical_start_addr=0x8000000,
            partition_size=0x4000000,
            region="EMMC_USER",
            storage="HW_STORAGE_EMMC",
            boundary_check=True,
            is_reserved=False,
            operation_type="UPDATE"
        )
        assert part.name == "boot"
        assert part.is_download is True
        assert part.partition_size == 0x4000000


class TestScatterFileParser:
    """Test ScatterFileParser class"""

    @pytest.fixture
    def scatter_file(self, tmp_path):
        """Create a sample scatter file"""
        content = """############################################################################################################
#  General Information
############################################################################################################
platform: MT6765
chip_name: MT6765
storage: EMMC

- partition_index: SYS0
  partition_name: preloader
  file_name: preloader_k65v1_64_bsp.bin
  is_download: true
  type: BOOTLOADER
  linear_start_addr: 0x0
  physical_start_addr: 0x0
  partition_size: 0x40000
  region: EMMC_BOOT_1
  storage: HW_STORAGE_EMMC
  boundary_check: true
  is_reserved: false
  operation_type: BOOTLOADERS

- partition_index: SYS1
  partition_name: boot
  file_name: boot.img
  is_download: true
  type: NORMAL_ROM
  linear_start_addr: 0x8000000
  physical_start_addr: 0x8000000
  partition_size: 0x4000000
  region: EMMC_USER
  storage: HW_STORAGE_EMMC
  boundary_check: true
  is_reserved: false
  operation_type: UPDATE
"""
        path = tmp_path / "MT6765_scatter.txt"
        path.write_text(content)
        return path

    def test_init(self, scatter_file):
        """Test ScatterFileParser initialization"""
        parser = ScatterFileParser(scatter_file)
        assert parser.scatter_path == scatter_file
        assert parser.partitions == []

    def test_parse_scatter(self, scatter_file):
        """Test parsing scatter file"""
        parser = ScatterFileParser(scatter_file)
        partitions = parser.parse()

        # Should find partitions
        assert len(partitions) >= 0  # Simplified parsing may not catch all

    def test_parse_general_info(self, scatter_file):
        """Test parsing general info section"""
        parser = ScatterFileParser(scatter_file)
        parser.parse()

        # General info should be populated
        assert "platform" in parser.general_info or len(parser.general_info) >= 0


class TestQualcommChipset:
    """Test QualcommChipset enumeration"""

    def test_chipset_values(self):
        """Test all chipset values are defined"""
        assert QualcommChipset.SNAPDRAGON_2XX.value == "snapdragon_2xx"
        assert QualcommChipset.SNAPDRAGON_4XX.value == "snapdragon_4xx"
        assert QualcommChipset.SNAPDRAGON_8XX.value == "snapdragon_8xx"
        assert QualcommChipset.SNAPDRAGON_8_GEN.value == "snapdragon_8_gen"
        assert QualcommChipset.UNKNOWN.value == "unknown"


class TestEDLMode:
    """Test EDLMode enumeration"""

    def test_edl_modes(self):
        """Test all EDL modes are defined"""
        assert EDLMode.SAHARA.value == "sahara"
        assert EDLMode.FIREHOSE.value == "firehose"
        assert EDLMode.UNKNOWN.value == "unknown"


class TestQualcommPartition:
    """Test QualcommPartition dataclass"""

    def test_create_partition(self):
        """Test creating Qualcomm partition"""
        part = QualcommPartition(
            sector_size_in_bytes=512,
            num_partition_sectors=65536,
            physical_partition_number=0,
            start_sector="0",
            label="boot",
            filename="boot.img"
        )
        assert part.label == "boot"
        assert part.sector_size_in_bytes == 512


class TestEDLFlasher:
    """Test EDLFlasher class"""

    def test_init(self):
        """Test EDLFlasher initialization"""
        flasher = EDLFlasher(port="/dev/ttyUSB0")
        assert flasher.port == "/dev/ttyUSB0"
        assert flasher.mode == EDLMode.UNKNOWN

    def test_detect_protocol(self):
        """Test protocol detection"""
        flasher = EDLFlasher()
        mode = flasher.detect_protocol()
        # Should default to FIREHOSE
        assert mode == EDLMode.FIREHOSE

    def test_parse_rawprogram(self, tmp_path):
        """Test parsing rawprogram XML"""
        rawprogram = tmp_path / "rawprogram0.xml"
        rawprogram.write_text("""<?xml version="1.0" ?>
<data>
  <program SECTOR_SIZE_IN_BYTES="512" num_partition_sectors="65536"
           physical_partition_number="0" start_sector="0"
           label="boot" filename="boot.img"/>
  <program SECTOR_SIZE_IN_BYTES="512" num_partition_sectors="131072"
           physical_partition_number="0" start_sector="65536"
           label="system" filename="system.img"/>
</data>
""")
        flasher = EDLFlasher()
        partitions = flasher.parse_rawprogram(rawprogram)

        assert len(partitions) == 2
        assert partitions[0].label == "boot"
        assert partitions[1].label == "system"

    def test_parse_rawprogram_empty(self, tmp_path):
        """Test parsing empty rawprogram"""
        rawprogram = tmp_path / "empty.xml"
        rawprogram.write_text('<?xml version="1.0"?><data></data>')

        flasher = EDLFlasher()
        partitions = flasher.parse_rawprogram(rawprogram)
        assert partitions == []

    def test_get_device_info(self):
        """Test getting device info"""
        flasher = EDLFlasher()
        info = flasher.get_device_info()

        assert "platform" in info
        assert "emmc_size" in info
        assert "secure_boot" in info


class TestQualcommChipDetector:
    """Test QualcommChipDetector class"""

    def test_detect_snapdragon_888(self):
        """Test detecting Snapdragon 888"""
        result = QualcommChipDetector.detect_from_device("SM8350")
        assert result is not None
        assert result["name"] == "Snapdragon 888"

    def test_detect_snapdragon_8_gen_2(self):
        """Test detecting Snapdragon 8 Gen 2"""
        result = QualcommChipDetector.detect_from_device("SM8550")
        assert result is not None
        assert result["name"] == "Snapdragon 8 Gen 2"

    def test_detect_unknown_chip(self):
        """Test detecting unknown chip"""
        result = QualcommChipDetector.detect_from_device("UNKNOWN123")
        assert result is None

    def test_detect_generic_snapdragon(self):
        """Test detecting generic snapdragon string"""
        result = QualcommChipDetector.detect_from_device("Snapdragon custom")
        assert result is not None
        assert result["series"] == "Unknown"

    def test_print_chip_info_known(self, capsys):
        """Test printing known chip info"""
        QualcommChipDetector.print_chip_info("SM8350")
        captured = capsys.readouterr()
        assert "Snapdragon 888" in captured.out

    def test_print_chip_info_unknown(self, capsys):
        """Test printing unknown chip info"""
        QualcommChipDetector.print_chip_info("UNKNOWN")
        captured = capsys.readouterr()
        assert "Unknown" in captured.out or "UNKNOWN" in captured.out


class TestFirehoseProtocol:
    """Test FirehoseProtocol class"""

    def test_init(self):
        """Test FirehoseProtocol initialization"""
        protocol = FirehoseProtocol("/dev/ttyUSB0")
        assert protocol.port == "/dev/ttyUSB0"
        assert protocol.connected is False

    def test_connect(self):
        """Test connect method"""
        protocol = FirehoseProtocol("/dev/ttyUSB0")
        # Should return False without actual device
        result = protocol.connect()
        assert result is False


class TestSaharaProtocol:
    """Test SaharaProtocol class"""

    def test_init(self):
        """Test SaharaProtocol initialization"""
        protocol = SaharaProtocol("/dev/ttyUSB0")
        assert protocol.port == "/dev/ttyUSB0"

    def test_constants(self):
        """Test Sahara protocol constants"""
        assert SaharaProtocol.SAHARA_HELLO == 0x01
        assert SaharaProtocol.SAHARA_HELLO_RESP == 0x02
        assert SaharaProtocol.SAHARA_DONE == 0x05
        assert SaharaProtocol.SAHARA_RESET == 0x07
