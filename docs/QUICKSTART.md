# SamFWTool Quick Start Guide

## Installation

```bash
# Install from source
git clone https://github.com/samfwtool/samfwtool.git
cd samfwtool
pip install -e .

# Or install from PyPI (when available)
pip install samfwtool
```

## Basic Usage

### 1. Analyze Firmware

```bash
# Get firmware information
samfwtool info firmware.tar.md5

# Get detailed partition info
samfwtool info firmware.tar.md5 --detailed
```

### 2. Extract Firmware

```bash
# Extract all partitions
samfwtool extract firmware.tar.md5 -o extracted/

# Extract specific partition
samfwtool extract firmware.tar.md5 -o extracted/ -p boot.img

# Extract without decompression
samfwtool extract firmware.tar.md5 -o extracted/ --no-decompress
```

### 3. Security Scanning

```bash
# Scan extracted firmware for vulnerabilities
samfwtool scan extracted/

# Export security report
samfwtool scan extracted/ -o security_report.json

# Deep security analysis
samfwtool scan extracted/ --deep
```

### 4. Compare Firmware Versions

```bash
# Compare two firmware versions
samfwtool diff old_firmware.tar.md5 new_firmware.tar.md5

# Export diff report
samfwtool diff old.tar.md5 new.tar.md5 -o diff_report.json
```

### 5. Boot Image Manipulation

```bash
# Show boot image info
samfwtool bootimg boot.img --info

# Extract kernel
samfwtool bootimg boot.img --extract-kernel kernel.img

# Extract ramdisk
samfwtool bootimg boot.img --extract-ramdisk ramdisk.gz
```

## Advanced Examples

### Automated Security Audit

```bash
#!/bin/bash
# security_audit.sh

FIRMWARE="$1"
OUTPUT_DIR="audit_$(date +%Y%m%d)"

# Extract firmware
samfwtool extract "$FIRMWARE" -o "$OUTPUT_DIR/extracted"

# Run security scan
samfwtool scan "$OUTPUT_DIR/extracted" -o "$OUTPUT_DIR/security_report.json"

# Analyze boot image
if [ -f "$OUTPUT_DIR/extracted/boot.img" ]; then
    samfwtool bootimg "$OUTPUT_DIR/extracted/boot.img" --info > "$OUTPUT_DIR/boot_info.txt"
fi

echo "Audit complete: $OUTPUT_DIR"
```

### Firmware Version Tracking

```bash
#!/bin/bash
# track_versions.sh

OLD_FW="firmware_v1.tar.md5"
NEW_FW="firmware_v2.tar.md5"

# Generate diff report
samfwtool diff "$OLD_FW" "$NEW_FW" -o version_diff.json

# Extract only changed files
jq -r '.modified_files[].path' version_diff.json | while read file; do
    samfwtool extract "$NEW_FW" -o changes/ -p "$file"
done
```

## Python API

```python
from samfwtool import FirmwareParser, FirmwareExtractor, SecurityScanner

# Parse firmware
parser = FirmwareParser('firmware.tar.md5')
info = parser.parse()
print(f"Firmware version: {info.version}")
print(f"Total partitions: {len(info.partitions)}")

# Extract firmware
extractor = FirmwareExtractor('firmware.tar.md5', 'output/')
extractor.extract_all(decompress=True)

# Security scan
scanner = SecurityScanner('output/')
findings = scanner.scan_all()
critical = [f for f in findings if f.severity.value == 'critical']
print(f"Critical findings: {len(critical)}")
```

## Tips & Best Practices

1. **Always verify checksums** before working with firmware
2. **Extract to SSD** for better performance with large files
3. **Use security scanning** on all firmware before deployment
4. **Compare versions** before updating to understand changes
5. **Keep backups** of original firmware files

## Troubleshooting

### Issue: "Invalid firmware magic"
**Solution:** Firmware file may be corrupted. Verify checksum.

### Issue: "Permission denied"
**Solution:** Run with appropriate permissions or use `sudo` on Linux.

### Issue: "Module not found"
**Solution:** Install all dependencies with `pip install -r requirements.txt`

## Next Steps

- Read the [full documentation](https://samfwtool.readthedocs.io)
- Check out [advanced features](ADVANCED.md)
- Join our [community forum](https://forum.samfwtool.org)
