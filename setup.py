"""
SamFWTool - Advanced Firmware Analysis & Manipulation Toolkit

Setup configuration for installing samfwtool package.

Author: SamFWTool Team
License: MIT
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README if it exists
readme_path: Path = Path(__file__).parent / "README.md"
long_description: str

if readme_path.exists():
    try:
        with open(readme_path, "r", encoding="utf-8") as fh:
            long_description = fh.read()
    except (IOError, OSError, UnicodeDecodeError) as e:
        # Fallback if README cannot be read
        long_description = "Advanced cross-platform firmware analysis and manipulation toolkit"
else:
    long_description = "Advanced cross-platform firmware analysis and manipulation toolkit"

setup(
    name="samfwtool",
    version="2.0.0",
    author="SamFWTool Team",
    description="Advanced cross-platform firmware analysis and manipulation toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/samfwtool/samfwtool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
        "pycryptodome>=3.15.0",
        "lz4>=4.0.0",
        # Note: lzma is part of Python standard library (no separate package needed)
        "brotli>=1.0.0",
        "python-magic>=0.4.27",
        "pefile>=2022.5.30",
        "pyelftools>=0.29",
        "capstone>=5.0.0",
        "requests>=2.28.0",
        "tqdm>=4.64.0",
        "colorama>=0.4.6",
        "pywin32>=304; sys_platform == 'win32'",
    ],
    entry_points={
        "console_scripts": [
            "samfwtool=samfwtool.cli.main:cli",
            "samfwtool-gui=samfwtool.gui.main_gui:main",
        ],
        "gui_scripts": [
            "samfwtool-gui=samfwtool.gui.main_gui:main",
        ],
    },
)
