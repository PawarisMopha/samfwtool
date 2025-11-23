"""
Unit tests for CLI module
"""
import pytest
from click.testing import CliRunner
from samfwtool.cli.main import cli


class TestCLIBasics:
    """Test basic CLI functionality"""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner"""
        return CliRunner()

    def test_cli_help(self, runner):
        """Test CLI help command"""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'SamFWTool' in result.output
        assert 'firmware' in result.output.lower()

    def test_cli_version(self, runner):
        """Test CLI version command"""
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        # Should show version number

    def test_info_command_help(self, runner):
        """Test info command help"""
        result = runner.invoke(cli, ['info', '--help'])
        assert result.exit_code == 0
        assert 'firmware' in result.output.lower()

    def test_extract_command_help(self, runner):
        """Test extract command help"""
        result = runner.invoke(cli, ['extract', '--help'])
        assert result.exit_code == 0

    def test_pack_command_help(self, runner):
        """Test pack command help"""
        result = runner.invoke(cli, ['pack', '--help'])
        assert result.exit_code == 0

    def test_scan_command_help(self, runner):
        """Test scan command help"""
        result = runner.invoke(cli, ['scan', '--help'])
        assert result.exit_code == 0

    def test_diff_command_help(self, runner):
        """Test diff command help"""
        result = runner.invoke(cli, ['diff', '--help'])
        assert result.exit_code == 0

    def test_devices_command_help(self, runner):
        """Test devices command help"""
        result = runner.invoke(cli, ['devices', '--help'])
        assert result.exit_code == 0

    def test_flash_command_help(self, runner):
        """Test flash command help"""
        result = runner.invoke(cli, ['flash', '--help'])
        assert result.exit_code == 0

    def test_frp_command_help(self, runner):
        """Test frp command help"""
        result = runner.invoke(cli, ['frp', '--help'])
        assert result.exit_code == 0

    def test_bootimg_command_help(self, runner):
        """Test bootimg command help"""
        result = runner.invoke(cli, ['bootimg', '--help'])
        assert result.exit_code == 0

    def test_mtk_command_help(self, runner):
        """Test mtk command help"""
        result = runner.invoke(cli, ['mtk', '--help'])
        assert result.exit_code == 0

    def test_edl_command_help(self, runner):
        """Test edl command help"""
        result = runner.invoke(cli, ['edl', '--help'])
        assert result.exit_code == 0

    def test_compare_command_help(self, runner):
        """Test compare command help"""
        result = runner.invoke(cli, ['compare', '--help'])
        assert result.exit_code == 0


class TestCLIInfoCommand:
    """Test info command functionality"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_info_nonexistent_file(self, runner):
        """Test info on nonexistent file"""
        result = runner.invoke(cli, ['info', '/nonexistent/file.tar'])
        # Should fail gracefully
        assert result.exit_code != 0 or 'error' in result.output.lower() or 'not found' in result.output.lower()

    def test_info_valid_tar(self, runner, tmp_path):
        """Test info on valid TAR file"""
        import tarfile
        import io

        tar_file = tmp_path / "test.tar"
        with tarfile.open(tar_file, 'w') as tar:
            data = b"test content"
            info = tarfile.TarInfo(name="boot.img")
            info.size = len(data)
            tar.addfile(info, fileobj=io.BytesIO(data))

        result = runner.invoke(cli, ['info', str(tar_file)])
        # Should succeed and show info
        assert result.exit_code == 0 or 'boot.img' in result.output


class TestCLIExtractCommand:
    """Test extract command functionality"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_extract_nonexistent_file(self, runner, tmp_path):
        """Test extract on nonexistent file"""
        result = runner.invoke(cli, ['extract', '/nonexistent/file.tar', '-o', str(tmp_path)])
        assert result.exit_code != 0


class TestCLIScanCommand:
    """Test scan command functionality"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_scan_empty_directory(self, runner, tmp_path):
        """Test scan on empty directory"""
        result = runner.invoke(cli, ['scan', str(tmp_path)])
        # Should complete (possibly with no findings)
        assert result.exit_code == 0 or 'findings' in result.output.lower()


class TestCLIDevicesCommand:
    """Test devices command functionality"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_devices_list(self, runner):
        """Test devices command"""
        result = runner.invoke(cli, ['devices'])
        # Should run (may show no devices)
        assert result.exit_code == 0 or 'device' in result.output.lower()


class TestCLICompareCommand:
    """Test compare command functionality"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_compare_command(self, runner):
        """Test compare command shows tool comparison"""
        result = runner.invoke(cli, ['compare'])
        assert result.exit_code == 0
        # Should show comparison info
        assert 'odin' in result.output.lower() or 'samfw' in result.output.lower()
