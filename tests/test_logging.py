"""
Unit tests for logging configuration
"""
import pytest
import logging
from pathlib import Path
from samfwtool.logging_config import (
    setup_logging,
    get_logger,
    DEBUG,
    INFO,
    WARNING,
    ERROR,
    CRITICAL,
)


class TestSetupLogging:
    """Test setup_logging function"""

    def test_default_setup(self):
        """Test default logging setup"""
        setup_logging()
        logger = logging.getLogger("samfwtool")
        assert logger.level == logging.INFO
        assert len(logger.handlers) >= 1

    def test_custom_level(self):
        """Test logging with custom level"""
        setup_logging(level=logging.DEBUG)
        logger = logging.getLogger("samfwtool")
        assert logger.level == logging.DEBUG

    def test_custom_format(self):
        """Test logging with custom format string"""
        custom_format = "%(levelname)s: %(message)s"
        setup_logging(format_string=custom_format)
        logger = logging.getLogger("samfwtool")
        # Check that formatter was set
        assert len(logger.handlers) > 0

    def test_file_logging(self, tmp_path):
        """Test logging to file"""
        log_file = tmp_path / "test.log"
        setup_logging(log_file=log_file)

        logger = logging.getLogger("samfwtool")
        logger.info("Test message")

        # Force flush
        for handler in logger.handlers:
            handler.flush()

        assert log_file.exists()
        content = log_file.read_text()
        assert "Test message" in content

    def test_handlers_cleared(self):
        """Test that existing handlers are cleared"""
        setup_logging()
        initial_count = len(logging.getLogger("samfwtool").handlers)

        setup_logging()
        final_count = len(logging.getLogger("samfwtool").handlers)

        # Should have same number of handlers (cleared and re-added)
        assert final_count == initial_count

    def test_console_and_file_handlers(self, tmp_path):
        """Test both console and file handlers"""
        log_file = tmp_path / "combined.log"
        setup_logging(log_file=log_file)

        logger = logging.getLogger("samfwtool")
        # Should have 2 handlers: console and file
        assert len(logger.handlers) == 2


class TestGetLogger:
    """Test get_logger function"""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a Logger instance"""
        logger = get_logger("test.module")
        assert isinstance(logger, logging.Logger)

    def test_get_logger_name(self):
        """Test that logger has correct name"""
        logger = get_logger("samfwtool.core.parser")
        assert logger.name == "samfwtool.core.parser"

    def test_get_logger_hierarchy(self):
        """Test logger hierarchy"""
        setup_logging(level=logging.DEBUG)
        parent = get_logger("samfwtool")
        child = get_logger("samfwtool.core")

        # Child should inherit from parent
        assert child.parent == parent or child.parent.name == "samfwtool"


class TestLoggingConstants:
    """Test logging level constants"""

    def test_debug_constant(self):
        """Test DEBUG constant"""
        assert DEBUG == logging.DEBUG

    def test_info_constant(self):
        """Test INFO constant"""
        assert INFO == logging.INFO

    def test_warning_constant(self):
        """Test WARNING constant"""
        assert WARNING == logging.WARNING

    def test_error_constant(self):
        """Test ERROR constant"""
        assert ERROR == logging.ERROR

    def test_critical_constant(self):
        """Test CRITICAL constant"""
        assert CRITICAL == logging.CRITICAL


class TestLoggingIntegration:
    """Integration tests for logging"""

    def test_log_message_formats(self, tmp_path):
        """Test that log messages are properly formatted"""
        log_file = tmp_path / "format_test.log"
        setup_logging(log_file=log_file, level=logging.DEBUG)

        logger = get_logger("samfwtool.test")
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        for handler in logging.getLogger("samfwtool").handlers:
            handler.flush()

        content = log_file.read_text()
        assert "DEBUG" in content
        assert "INFO" in content
        assert "WARNING" in content
        assert "ERROR" in content

    def test_multiple_loggers(self):
        """Test multiple loggers work correctly"""
        setup_logging()

        logger1 = get_logger("samfwtool.module1")
        logger2 = get_logger("samfwtool.module2")

        assert logger1 != logger2
        assert logger1.name != logger2.name
