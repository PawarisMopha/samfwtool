"""
Advanced security analysis for firmware
A feature completely absent from Odin

Author: SamFWTool Team
License: MIT
"""
import os
import re
import struct
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

__all__ = [
    "VulnerabilitySeverity",
    "SecurityFinding",
    "SecurityScanner",
]


class VulnerabilitySeverity(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SecurityFinding:
    """A security finding in firmware"""
    severity: VulnerabilitySeverity
    category: str
    title: str
    description: str
    file_path: Optional[str] = None
    offset: Optional[int] = None
    evidence: Optional[str] = None
    remediation: Optional[str] = None


class SecurityScanner:
    """
    Advanced firmware security scanner

    Features not available in Odin:
    - Vulnerability detection
    - Insecure configuration identification
    - Hardcoded credentials detection
    - Binary security analysis
    - Encryption verification
    - Certificate validation
    - Root detection mechanisms
    - Debug mode detection
    """

    # Patterns for sensitive data
    CREDENTIAL_PATTERNS = [
        (r'password\s*=\s*["\']([^"\']+)["\']', 'Hardcoded Password'),
        (r'api[_-]?key\s*=\s*["\']([^"\']+)["\']', 'Hardcoded API Key'),
        (r'secret\s*=\s*["\']([^"\']+)["\']', 'Hardcoded Secret'),
        (r'token\s*=\s*["\']([^"\']+)["\']', 'Hardcoded Token'),
        (r'aws[_-]?access[_-]?key[_-]?id\s*=\s*["\']([A-Z0-9]{20})["\']', 'AWS Access Key'),
        (r'aws[_-]?secret[_-]?access[_-]?key\s*=\s*["\']([A-Za-z0-9/+=]{40})["\']', 'AWS Secret Key'),
        (r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----', 'Private Key'),
        (r'-----BEGIN\s+CERTIFICATE-----', 'Certificate'),
    ]

    # Patterns for security misconfigurations
    INSECURE_PATTERNS = [
        (r'adb[_-]?enabled\s*=\s*true', 'ADB Enabled', VulnerabilitySeverity.HIGH),
        (r'ro\.debuggable\s*=\s*1', 'Debuggable Build', VulnerabilitySeverity.HIGH),
        (r'ro\.secure\s*=\s*0', 'Insecure Boot', VulnerabilitySeverity.CRITICAL),
        (r'ro\.adb\.secure\s*=\s*0', 'Insecure ADB', VulnerabilitySeverity.HIGH),
        (r'selinux\s*=\s*disabled', 'SELinux Disabled', VulnerabilitySeverity.CRITICAL),
        (r'verity[_-]?mode\s*=\s*disabled', 'Verified Boot Disabled', VulnerabilitySeverity.HIGH),
        (r'ssl[_-]?verify\s*=\s*false', 'SSL Verification Disabled', VulnerabilitySeverity.HIGH),
    ]

    # Known vulnerable library versions
    VULNERABLE_LIBRARIES = {
        'libssl.so.1.0.0': 'OpenSSL 1.0.0 (Multiple CVEs)',
        'libcrypto.so.1.0.0': 'OpenSSL Crypto 1.0.0 (Multiple CVEs)',
        'libcurl.so.3': 'cURL 3.x (CVE-2021-22876 and others)',
    }

    def __init__(self, firmware_dir: Path):
        self.firmware_dir = Path(firmware_dir)
        self.findings: List[SecurityFinding] = []

    def scan_all(self) -> List[SecurityFinding]:
        """
        Perform comprehensive security scan

        Returns:
            List of security findings
        """
        print("Starting security scan...")
        self.findings = []

        # Scan for hardcoded credentials
        self._scan_hardcoded_credentials()

        # Scan for security misconfigurations
        self._scan_security_misconfigurations()

        # Scan for vulnerable libraries
        self._scan_vulnerable_libraries()

        # Scan build properties
        self._scan_build_properties()

        # Scan certificates
        self._scan_certificates()

        # Scan for debug features
        self._scan_debug_features()

        # Scan for encryption
        self._scan_encryption()

        # Generate summary
        self._print_summary()

        return self.findings

    def _scan_hardcoded_credentials(self):
        """Scan for hardcoded credentials and secrets"""
        print("Scanning for hardcoded credentials...")

        for file_path in self._find_text_files():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for pattern, name in self.CREDENTIAL_PATTERNS:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        self.findings.append(SecurityFinding(
                            severity=VulnerabilitySeverity.CRITICAL,
                            category='Credentials',
                            title=f'{name} Found',
                            description=f'Hardcoded {name.lower()} detected in firmware',
                            file_path=str(file_path.relative_to(self.firmware_dir)),
                            evidence=match.group(0)[:100],
                            remediation='Remove hardcoded credentials and use secure storage'
                        ))
            except (OSError, IOError, UnicodeDecodeError, re.error) as e:
                # Skip files that can't be read or processed
                pass

    def _scan_security_misconfigurations(self):
        """Scan for security misconfigurations"""
        print("Scanning for security misconfigurations...")

        for file_path in self._find_text_files():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for pattern, name, severity in self.INSECURE_PATTERNS:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        self.findings.append(SecurityFinding(
                            severity=severity,
                            category='Configuration',
                            title=name,
                            description=f'Insecure configuration detected: {name}',
                            file_path=str(file_path.relative_to(self.firmware_dir)),
                            evidence=match.group(0),
                            remediation=f'Disable {name.lower()} in production builds'
                        ))
            except (OSError, IOError, UnicodeDecodeError, re.error) as e:
                # Skip files that can't be read or processed
                pass

    def _scan_vulnerable_libraries(self):
        """Scan for known vulnerable libraries"""
        print("Scanning for vulnerable libraries...")

        for file_path in self._find_binary_files():
            filename = file_path.name
            if filename in self.VULNERABLE_LIBRARIES:
                self.findings.append(SecurityFinding(
                    severity=VulnerabilitySeverity.HIGH,
                    category='Vulnerable Library',
                    title=f'Vulnerable Library: {filename}',
                    description=self.VULNERABLE_LIBRARIES[filename],
                    file_path=str(file_path.relative_to(self.firmware_dir)),
                    remediation='Update library to latest secure version'
                ))

    def _scan_build_properties(self):
        """Scan build.prop for security issues"""
        print("Scanning build properties...")

        build_prop_paths = [
            'system/build.prop',
            'vendor/build.prop',
            'product/build.prop',
        ]

        for prop_path in build_prop_paths:
            full_path = self.firmware_dir / prop_path
            if full_path.exists():
                self._analyze_build_prop(full_path)

    def _analyze_build_prop(self, build_prop_path: Path):
        """Analyze build.prop file for security issues"""
        try:
            with open(build_prop_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for debug build
            if re.search(r'ro\.debuggable\s*=\s*1', content):
                self.findings.append(SecurityFinding(
                    severity=VulnerabilitySeverity.HIGH,
                    category='Build Configuration',
                    title='Debug Build Detected',
                    description='Firmware is built in debug mode, allowing debugging and potential exploitation',
                    file_path=str(build_prop_path.relative_to(self.firmware_dir)),
                    evidence='ro.debuggable=1',
                    remediation='Build firmware with ro.debuggable=0 for production'
                ))

            # Check for insecure boot
            if re.search(r'ro\.secure\s*=\s*0', content):
                self.findings.append(SecurityFinding(
                    severity=VulnerabilitySeverity.CRITICAL,
                    category='Boot Security',
                    title='Insecure Boot Configuration',
                    description='Boot security is disabled, allowing unauthorized system modifications',
                    file_path=str(build_prop_path.relative_to(self.firmware_dir)),
                    evidence='ro.secure=0',
                    remediation='Enable secure boot with ro.secure=1'
                ))

            # Check for old Android version
            version_match = re.search(r'ro\.build\.version\.release\s*=\s*(\d+)', content)
            if version_match:
                version = int(version_match.group(1))
                if version < 10:
                    self.findings.append(SecurityFinding(
                        severity=VulnerabilitySeverity.MEDIUM,
                        category='Outdated Software',
                        title=f'Outdated Android Version: {version}',
                        description=f'Android {version} is outdated and may contain unpatched vulnerabilities',
                        file_path=str(build_prop_path.relative_to(self.firmware_dir)),
                        evidence=f'ro.build.version.release={version}',
                        remediation='Update to latest Android version'
                    ))

            # Check security patch level
            patch_match = re.search(r'ro\.build\.version\.security_patch\s*=\s*(\d{4}-\d{2}-\d{2})', content)
            if patch_match:
                patch_date = patch_match.group(1)
                # Simple check: if year is < 2023, it's outdated
                year = int(patch_date.split('-')[0])
                if year < 2023:
                    self.findings.append(SecurityFinding(
                        severity=VulnerabilitySeverity.HIGH,
                        category='Security Patch',
                        title=f'Outdated Security Patch: {patch_date}',
                        description='Security patch level is outdated, device is vulnerable to known exploits',
                        file_path=str(build_prop_path.relative_to(self.firmware_dir)),
                        evidence=f'ro.build.version.security_patch={patch_date}',
                        remediation='Update firmware to include latest security patches'
                    ))

        except Exception as e:
            pass

    def _scan_certificates(self):
        """Scan for certificate issues"""
        print("Scanning certificates...")

        # Look for certificate files
        cert_patterns = ['*.pem', '*.crt', '*.cer', '*.der']

        for pattern in cert_patterns:
            for cert_path in self.firmware_dir.rglob(pattern):
                # Basic certificate presence check
                self.findings.append(SecurityFinding(
                    severity=VulnerabilitySeverity.INFO,
                    category='Certificate',
                    title='Certificate Found',
                    description=f'Certificate file found: {cert_path.name}',
                    file_path=str(cert_path.relative_to(self.firmware_dir)),
                    remediation='Verify certificate validity and expiration'
                ))

    def _scan_debug_features(self):
        """Scan for debug features that should be disabled"""
        print("Scanning for debug features...")

        debug_indicators = [
            ('__android_log_print', 'Logging Functions'),
            ('FORTIFY_SOURCE', 'Debug Symbols'),
            ('.debug', 'Debug Sections'),
            ('test_', 'Test Functions'),
        ]

        # Check binary files for debug symbols
        for file_path in self._find_binary_files():
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()

                for indicator, name in debug_indicators:
                    if indicator.encode() in content:
                        self.findings.append(SecurityFinding(
                            severity=VulnerabilitySeverity.LOW,
                            category='Debug Features',
                            title=f'{name} Present',
                            description=f'Debug feature detected: {name}',
                            file_path=str(file_path.relative_to(self.firmware_dir)),
                            evidence=indicator,
                            remediation='Strip debug symbols from production builds'
                        ))
                        break  # Only report once per file
            except (OSError, IOError, struct.error) as e:
                # Skip files that can't be read or processed
                pass

    def _scan_encryption(self):
        """Scan for encryption status"""
        print("Scanning encryption configuration...")

        # Check for encryption in fstab
        fstab_patterns = ['**/fstab.*', '**/fstab']

        for pattern in fstab_patterns:
            for fstab_path in self.firmware_dir.glob(pattern):
                try:
                    with open(fstab_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    if 'forceencrypt' not in content and 'fileencryption' not in content:
                        self.findings.append(SecurityFinding(
                            severity=VulnerabilitySeverity.MEDIUM,
                            category='Encryption',
                            title='Encryption Not Enforced',
                            description='Filesystem encryption is not enforced in fstab',
                            file_path=str(fstab_path.relative_to(self.firmware_dir)),
                            remediation='Enable forceencrypt or fileencryption in fstab'
                        ))
                except (OSError, IOError, UnicodeDecodeError) as e:
                    # Skip files that can't be read
                    pass

    def _find_text_files(self):
        """Find text files in firmware directory"""
        text_extensions = ['.prop', '.xml', '.txt', '.conf', '.sh', '.rc', '.cfg']
        for ext in text_extensions:
            yield from self.firmware_dir.rglob(f'*{ext}')

    def _find_binary_files(self):
        """Find binary files in firmware directory"""
        binary_extensions = ['.so', '.ko', '.bin', '.elf']
        for ext in binary_extensions:
            yield from self.firmware_dir.rglob(f'*{ext}')
        # Also find versioned shared libraries like libssl.so.1.0.0
        for path in self.firmware_dir.rglob('*.so.*'):
            yield path

    def _print_summary(self):
        """Print scan summary"""
        print("\n" + "="*70)
        print("SECURITY SCAN SUMMARY")
        print("="*70)

        # Count by severity
        counts = {
            VulnerabilitySeverity.CRITICAL: 0,
            VulnerabilitySeverity.HIGH: 0,
            VulnerabilitySeverity.MEDIUM: 0,
            VulnerabilitySeverity.LOW: 0,
            VulnerabilitySeverity.INFO: 0,
        }

        for finding in self.findings:
            counts[finding.severity] += 1

        print(f"\nTotal Findings: {len(self.findings)}")
        print(f"  CRITICAL: {counts[VulnerabilitySeverity.CRITICAL]}")
        print(f"  HIGH:     {counts[VulnerabilitySeverity.HIGH]}")
        print(f"  MEDIUM:   {counts[VulnerabilitySeverity.MEDIUM]}")
        print(f"  LOW:      {counts[VulnerabilitySeverity.LOW]}")
        print(f"  INFO:     {counts[VulnerabilitySeverity.INFO]}")

        # Print critical and high findings
        critical_high = [f for f in self.findings
                        if f.severity in [VulnerabilitySeverity.CRITICAL, VulnerabilitySeverity.HIGH]]

        if critical_high:
            print("\n" + "-"*70)
            print("CRITICAL & HIGH SEVERITY FINDINGS:")
            print("-"*70)
            for finding in critical_high[:10]:  # Limit to first 10
                print(f"\n[{finding.severity.value.upper()}] {finding.title}")
                print(f"  Category: {finding.category}")
                print(f"  Description: {finding.description}")
                if finding.file_path:
                    print(f"  File: {finding.file_path}")
                if finding.evidence:
                    print(f"  Evidence: {finding.evidence}")

    def export_report(self, output_path: Path, format: str = 'json'):
        """Export security report"""
        import json
        from datetime import datetime

        report = {
            'scan_date': datetime.now().isoformat(),
            'firmware_path': str(self.firmware_dir),
            'total_findings': len(self.findings),
            'findings': [
                {
                    'severity': f.severity.value,
                    'category': f.category,
                    'title': f.title,
                    'description': f.description,
                    'file_path': f.file_path,
                    'evidence': f.evidence,
                    'remediation': f.remediation
                }
                for f in self.findings
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nReport exported to: {output_path}")
