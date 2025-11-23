"""
Unit tests for boot image tools
"""
import pytest
import struct
from pathlib import Path
from samfwtool.tools.bootimg import BootImageInfo, BootImageTool


class TestBootImageInfo:
    """Test BootImageInfo dataclass"""

    def test_create_boot_image_info(self):
        """Test creating BootImageInfo"""
        info = BootImageInfo(
            kernel_size=1000,
            kernel_addr=0x10000000,
            ramdisk_size=500,
            ramdisk_addr=0x11000000,
            second_size=0,
            second_addr=0,
            tags_addr=0x10000100,
            page_size=2048,
            os_version=0x0b000000,
            name="test_boot",
            cmdline="console=ttyMSM0",
            id=b'\x00' * 32
        )
        assert info.kernel_size == 1000
        assert info.page_size == 2048
        assert info.name == "test_boot"


class TestBootImageTool:
    """Test BootImageTool class"""

    @pytest.fixture
    def create_boot_image(self, tmp_path):
        """Create a minimal valid boot image"""
        def _create(name="boot.img", kernel_size=1024, ramdisk_size=512, page_size=2048):
            path = tmp_path / name
            with open(path, 'wb') as f:
                # Write ANDROID! magic
                f.write(b'ANDROID!')
                # Write header fields
                f.write(struct.pack('<I', kernel_size))  # kernel_size
                f.write(struct.pack('<I', 0x10008000))   # kernel_addr
                f.write(struct.pack('<I', ramdisk_size)) # ramdisk_size
                f.write(struct.pack('<I', 0x11000000))   # ramdisk_addr
                f.write(struct.pack('<I', 0))            # second_size
                f.write(struct.pack('<I', 0))            # second_addr
                f.write(struct.pack('<I', 0x10000100))   # tags_addr
                f.write(struct.pack('<I', page_size))    # page_size
                f.write(struct.pack('<I', 0))            # dt_size (header version)
                f.write(struct.pack('<I', 0x0b000000))   # os_version
                f.write(b'testboot'.ljust(16, b'\x00'))  # name
                f.write(b'console=ttyMSM0'.ljust(512, b'\x00'))  # cmdline
                f.write(b'\x00' * 32)                    # id (SHA)

                # Pad header to page_size
                current = f.tell()
                padding = page_size - current
                f.write(b'\x00' * padding)

                # Write kernel data
                f.write(b'K' * kernel_size)
                # Pad kernel to page boundary
                kernel_pages = (kernel_size + page_size - 1) // page_size
                kernel_padding = (kernel_pages * page_size) - kernel_size
                f.write(b'\x00' * kernel_padding)

                # Write ramdisk data
                f.write(b'R' * ramdisk_size)

            return path
        return _create

    def test_init(self, tmp_path):
        """Test BootImageTool initialization"""
        path = tmp_path / "boot.img"
        path.write_bytes(b'\x00' * 100)
        tool = BootImageTool(str(path))
        assert tool.boot_image_path == path
        assert tool.info is None

    def test_parse_valid_image(self, create_boot_image):
        """Test parsing a valid boot image"""
        path = create_boot_image()
        tool = BootImageTool(str(path))
        info = tool.parse()

        assert info.kernel_size == 1024
        assert info.ramdisk_size == 512
        assert info.page_size == 2048
        assert "testboot" in info.name

    def test_parse_invalid_magic(self, tmp_path):
        """Test parsing image with invalid magic"""
        path = tmp_path / "invalid.img"
        path.write_bytes(b'NOTVALID' + b'\x00' * 100)

        tool = BootImageTool(str(path))
        with pytest.raises(ValueError, match="Invalid boot image magic"):
            tool.parse()

    def test_extract_kernel(self, create_boot_image, tmp_path):
        """Test extracting kernel from boot image"""
        boot_path = create_boot_image(kernel_size=1024)
        output_path = tmp_path / "kernel"

        tool = BootImageTool(str(boot_path))
        result = tool.extract_kernel(str(output_path))

        assert result is True
        assert output_path.exists()
        assert output_path.stat().st_size == 1024

        # Check content
        content = output_path.read_bytes()
        assert content == b'K' * 1024

    def test_extract_ramdisk(self, create_boot_image, tmp_path):
        """Test extracting ramdisk from boot image"""
        boot_path = create_boot_image(kernel_size=1024, ramdisk_size=512)
        output_path = tmp_path / "ramdisk"

        tool = BootImageTool(str(boot_path))
        result = tool.extract_ramdisk(str(output_path))

        assert result is True
        assert output_path.exists()
        assert output_path.stat().st_size == 512

        # Check content
        content = output_path.read_bytes()
        assert content == b'R' * 512

    def test_print_info(self, create_boot_image, capsys):
        """Test printing boot image info"""
        path = create_boot_image()
        tool = BootImageTool(str(path))
        tool.print_info()

        captured = capsys.readouterr()
        assert "BOOT IMAGE INFORMATION" in captured.out
        assert "Kernel Size" in captured.out
        assert "Ramdisk Size" in captured.out
        assert "Page Size" in captured.out

    def test_parse_auto_called_on_extract(self, create_boot_image, tmp_path):
        """Test that parse is automatically called when needed"""
        boot_path = create_boot_image()
        output_path = tmp_path / "kernel"

        tool = BootImageTool(str(boot_path))
        assert tool.info is None

        tool.extract_kernel(str(output_path))
        assert tool.info is not None

    def test_constants(self):
        """Test BootImageTool constants"""
        assert BootImageTool.BOOT_MAGIC == b'ANDROID!'
        assert BootImageTool.BOOT_MAGIC_SIZE == 8
        assert BootImageTool.BOOT_NAME_SIZE == 16
        assert BootImageTool.BOOT_ARGS_SIZE == 512
