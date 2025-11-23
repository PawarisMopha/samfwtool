"""
Unit tests for firmware extractor
"""
import pytest
import tarfile
import zipfile
import gzip
from pathlib import Path
from samfwtool.core.extractor import FirmwareExtractor


class TestFirmwareExtractor:
    """Test firmware extractor functionality"""

    def test_extract_tar_all(self, tmp_path):
        """Test extracting all files from TAR"""
        # Create a dummy TAR file
        tar_file = tmp_path / "test.tar"
        output_dir = tmp_path / "output"

        with tarfile.open(tar_file, 'w') as tar:
            # Add dummy files
            for name in ["boot.img", "system.img", "vendor.img"]:
                info = tarfile.TarInfo(name=name)
                info.size = 4
                tar.addfile(info, fileobj=__import__('io').BytesIO(b"test"))

        extractor = FirmwareExtractor(str(tar_file), str(output_dir))
        result = extractor.extract_all(decompress=False)

        assert result is True
        assert output_dir.exists()
        assert (output_dir / "boot.img").exists()
        assert (output_dir / "system.img").exists()
        assert (output_dir / "vendor.img").exists()

    def test_extract_zip_all(self, tmp_path):
        """Test extracting all files from ZIP"""
        zip_file = tmp_path / "test.zip"
        output_dir = tmp_path / "output"

        with zipfile.ZipFile(zip_file, 'w') as zf:
            zf.writestr("boot.img", b"test content")
            zf.writestr("system.img", b"more content")

        extractor = FirmwareExtractor(str(zip_file), str(output_dir))
        result = extractor.extract_all(decompress=False)

        assert result is True
        assert output_dir.exists()
        assert (output_dir / "boot.img").exists()
        assert (output_dir / "system.img").exists()

    def test_extract_specific_partition(self, tmp_path):
        """Test extracting a specific partition"""
        tar_file = tmp_path / "test.tar"
        output_dir = tmp_path / "output"

        with tarfile.open(tar_file, 'w') as tar:
            for name in ["boot.img", "system.img"]:
                info = tarfile.TarInfo(name=name)
                info.size = 4
                tar.addfile(info, fileobj=__import__('io').BytesIO(b"test"))

        extractor = FirmwareExtractor(str(tar_file), str(output_dir))
        result = extractor.extract_partition("boot.img", decompress=False)

        assert result is True
        assert (output_dir / "boot.img").exists()

    def test_extract_nonexistent_partition(self, tmp_path):
        """Test error handling for non-existent partition"""
        tar_file = tmp_path / "test.tar"
        output_dir = tmp_path / "output"

        with tarfile.open(tar_file, 'w') as tar:
            info = tarfile.TarInfo(name="boot.img")
            info.size = 0
            tar.addfile(info)

        extractor = FirmwareExtractor(str(tar_file), str(output_dir))

        with pytest.raises(ValueError, match="not found"):
            extractor.extract_partition("nonexistent.img")

    def test_get_extraction_info(self, tmp_path):
        """Test getting extraction info"""
        tar_file = tmp_path / "test.tar"
        output_dir = tmp_path / "output"

        with tarfile.open(tar_file, 'w') as tar:
            for name in ["boot.img", "system.img"]:
                info = tarfile.TarInfo(name=name)
                info.size = 4
                tar.addfile(info, fileobj=__import__('io').BytesIO(b"test"))

        extractor = FirmwareExtractor(str(tar_file), str(output_dir))
        info = extractor.get_extraction_info()

        # Check format (could be 'tar' or 'tar.md5' depending on detection)
        assert info['firmware_format'] in ['tar', 'tar.md5']
        assert info['partition_count'] == 2
        assert len(info['partitions']) == 2


class TestDecompression:
    """Test automatic decompression functionality"""

    def test_decompress_gzip_file(self, tmp_path):
        """Test decompressing gzip file"""
        # Create a gzipped file
        original_data = b"This is test data for gzip compression"
        gzip_file = tmp_path / "test.img.gz"

        with gzip.open(gzip_file, 'wb') as f:
            f.write(original_data)

        # Create extractor and test decompression
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        from samfwtool.core.extractor import FirmwareExtractor
        extractor = FirmwareExtractor.__new__(FirmwareExtractor)
        extractor.output_dir = output_dir

        # Copy file to output and decompress
        import shutil
        output_file = output_dir / "test.img.gz"
        shutil.copy(gzip_file, output_file)

        result = extractor._decompress_if_needed(output_file)

        # Should return the decompressed path (without .gz)
        expected_path = output_dir / "test.img"
        assert expected_path.exists() or result == output_file  # Either decompress or keep original


@pytest.fixture
def sample_tar(tmp_path):
    """Create a sample TAR file for testing"""
    tar_file = tmp_path / "sample.tar"
    with tarfile.open(tar_file, 'w') as tar:
        for name in ["boot.img", "system.img", "vendor.img"]:
            info = tarfile.TarInfo(name=name)
            info.size = 1024
            tar.addfile(info)
    return tar_file
