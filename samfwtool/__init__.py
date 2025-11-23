"""
SamFWTool - Advanced Firmware Analysis & Manipulation Toolkit

A comprehensive, cross-platform firmware toolkit that significantly
surpasses Samsung's Odin and other firmware tools.

Features:
    - Multi-format firmware parsing (TAR, ZIP, IMG, SPARSE)
    - Advanced security analysis
    - Firmware comparison and diffing
    - Boot image manipulation
    - Cross-platform support (Linux, macOS, Windows)
    - Multi-vendor support (Samsung, Google, Xiaomi, OnePlus, Motorola)

Example:
    >>> from samfwtool import FirmwareParser
    >>> parser = FirmwareParser("firmware.tar.md5")
    >>> info = parser.parse()
    >>> print(info.partitions)
"""

__version__ = "2.1.0"
__author__ = "SamFWTool Team"
__license__ = "MIT"

from samfwtool.core.parser import FirmwareParser, FirmwareFormat, FirmwareInfo, PartitionInfo
from samfwtool.core.extractor import FirmwareExtractor
from samfwtool.core.packer import FirmwarePacker
from samfwtool.analysis.security import SecurityScanner, SecurityFinding, VulnerabilitySeverity
from samfwtool.analysis.diff import FirmwareDiff
from samfwtool.logging_config import setup_logging, get_logger

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    # Core classes
    "FirmwareParser",
    "FirmwareExtractor",
    "FirmwarePacker",
    "FirmwareFormat",
    "FirmwareInfo",
    "PartitionInfo",
    # Analysis
    "SecurityScanner",
    "SecurityFinding",
    "VulnerabilitySeverity",
    "FirmwareDiff",
    # Utilities
    "setup_logging",
    "get_logger",
]
