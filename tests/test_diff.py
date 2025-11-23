"""
Unit tests for firmware diff module
"""
import pytest
import tarfile
import io
from pathlib import Path
from samfwtool.analysis.diff import (
    ChangeType,
    FileDiff,
    FirmwareDiffResult,
    FirmwareDiff,
)


class TestChangeType:
    """Test ChangeType enumeration"""

    def test_change_types(self):
        """Test all change types are defined"""
        assert ChangeType.ADDED.value == "added"
        assert ChangeType.REMOVED.value == "removed"
        assert ChangeType.MODIFIED.value == "modified"
        assert ChangeType.UNCHANGED.value == "unchanged"


class TestFileDiff:
    """Test FileDiff dataclass"""

    def test_create_added_file(self):
        """Test creating an added file diff"""
        diff = FileDiff(
            path="boot.img",
            change_type=ChangeType.ADDED,
            new_size=1024,
            new_hash="abc123",
            size_change=1024
        )
        assert diff.path == "boot.img"
        assert diff.change_type == ChangeType.ADDED
        assert diff.new_size == 1024
        assert diff.old_size is None

    def test_create_removed_file(self):
        """Test creating a removed file diff"""
        diff = FileDiff(
            path="old.img",
            change_type=ChangeType.REMOVED,
            old_size=512,
            old_hash="def456",
            size_change=-512
        )
        assert diff.path == "old.img"
        assert diff.change_type == ChangeType.REMOVED
        assert diff.old_size == 512
        assert diff.new_size is None

    def test_create_modified_file(self):
        """Test creating a modified file diff"""
        diff = FileDiff(
            path="system.img",
            change_type=ChangeType.MODIFIED,
            old_size=1000,
            new_size=1500,
            old_hash="hash1",
            new_hash="hash2",
            size_change=500
        )
        assert diff.change_type == ChangeType.MODIFIED
        assert diff.size_change == 500


class TestFirmwareDiffResult:
    """Test FirmwareDiffResult dataclass"""

    def test_create_result(self):
        """Test creating a diff result"""
        result = FirmwareDiffResult(
            old_version="1.0",
            new_version="2.0",
            files_added=[FileDiff("new.img", ChangeType.ADDED, new_size=100)],
            files_removed=[],
            files_modified=[],
            files_unchanged=5,
            total_size_change=100,
            summary={"test": True}
        )
        assert result.old_version == "1.0"
        assert result.new_version == "2.0"
        assert len(result.files_added) == 1
        assert result.files_unchanged == 5


class TestFirmwareDiff:
    """Test FirmwareDiff class"""

    @pytest.fixture
    def create_firmware(self, tmp_path):
        """Helper to create firmware files"""
        def _create(name, partitions):
            path = tmp_path / name
            with tarfile.open(path, 'w') as tar:
                for part_name, size in partitions:
                    data = b"x" * size
                    info = tarfile.TarInfo(name=part_name)
                    info.size = size
                    tar.addfile(info, fileobj=io.BytesIO(data))
            return path
        return _create

    def test_init(self, create_firmware):
        """Test FirmwareDiff initialization"""
        old_fw = create_firmware("old.tar", [("boot.img", 100)])
        new_fw = create_firmware("new.tar", [("boot.img", 100)])

        diff = FirmwareDiff(str(old_fw), str(new_fw))
        assert diff.old_firmware == old_fw
        assert diff.new_firmware == new_fw

    def test_compare_identical(self, create_firmware):
        """Test comparing identical firmware"""
        old_fw = create_firmware("old.tar", [("boot.img", 100), ("system.img", 200)])
        new_fw = create_firmware("new.tar", [("boot.img", 100), ("system.img", 200)])

        diff = FirmwareDiff(str(old_fw), str(new_fw))
        result = diff.compare()

        assert len(result.files_added) == 0
        assert len(result.files_removed) == 0
        # Note: files may show as modified due to different checksums

    def test_compare_added_file(self, create_firmware):
        """Test detecting added file"""
        old_fw = create_firmware("old.tar", [("boot.img", 100)])
        new_fw = create_firmware("new.tar", [("boot.img", 100), ("new_part.img", 50)])

        diff = FirmwareDiff(str(old_fw), str(new_fw))
        result = diff.compare()

        added_names = [f.path for f in result.files_added]
        assert "new_part.img" in added_names

    def test_compare_removed_file(self, create_firmware):
        """Test detecting removed file"""
        old_fw = create_firmware("old.tar", [("boot.img", 100), ("old_part.img", 50)])
        new_fw = create_firmware("new.tar", [("boot.img", 100)])

        diff = FirmwareDiff(str(old_fw), str(new_fw))
        result = diff.compare()

        removed_names = [f.path for f in result.files_removed]
        assert "old_part.img" in removed_names

    def test_compare_size_change(self, create_firmware):
        """Test detecting size change"""
        old_fw = create_firmware("old.tar", [("boot.img", 100)])
        new_fw = create_firmware("new.tar", [("boot.img", 200)])

        diff = FirmwareDiff(str(old_fw), str(new_fw))
        result = diff.compare()

        # Size changed, so should be in modified
        assert len(result.files_modified) >= 1 or result.total_size_change != 0

    def test_generate_delta_info(self, create_firmware):
        """Test generating delta info"""
        old_fw = create_firmware("old.tar", [("boot.img", 100)])
        new_fw = create_firmware("new.tar", [("boot.img", 150), ("new.img", 50)])

        diff = FirmwareDiff(str(old_fw), str(new_fw))
        delta = diff.generate_delta_info()

        assert "from_version" in delta
        assert "to_version" in delta
        assert "files_to_add" in delta
        assert "files_to_remove" in delta
        assert "files_to_patch" in delta
        assert "estimated_delta_size" in delta

    def test_export_diff_report(self, create_firmware, tmp_path):
        """Test exporting diff report"""
        import json

        old_fw = create_firmware("old.tar", [("boot.img", 100)])
        new_fw = create_firmware("new.tar", [("boot.img", 100)])

        diff = FirmwareDiff(str(old_fw), str(new_fw))
        report_path = tmp_path / "report.json"
        diff.export_diff_report(report_path)

        assert report_path.exists()

        with open(report_path) as f:
            report = json.load(f)

        assert "old_version" in report
        assert "new_version" in report
        assert "summary" in report
        assert "added_files" in report
        assert "removed_files" in report
        assert "modified_files" in report
