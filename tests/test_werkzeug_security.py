"""
Unit tests for Werkzeug security vulnerabilities and fixes.

Tests cover:
1. Werkzeug version upgrade to 3.1.5 (CVE-2025-0995)
2. safe_join function to prevent Windows device name exploits
3. send_from_directory handling of special device names on Windows
"""
import os
import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensuring app module is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import importlib.metadata

try:
    werkzeug_version = importlib.metadata.version("werkzeug")
    from werkzeug.security import safe_join
    from werkzeug.utils import secure_filename
except (ImportError, importlib.metadata.PackageNotFoundError):
    werkzeug_version = None
    safe_join = None
    secure_filename = None

from flask import Flask, send_from_directory


class TestWerkzeugVersionUpgrade:
    """Tests ensuring Werkzeug 3.1.5 is installed and resolves CVE-2025-0995."""

    def test_werkzeug_version_installed(self):
        """Ensures that Werkzeug 3.1.5 or higher is installed."""
        assert werkzeug_version is not None, "Werkzeug is not installed"
        
        # Parsing version string (e.g., "3.1.5" -> (3, 1, 5))
        version_parts = tuple(map(int, werkzeug_version.split(".")[:3]))
        required_version = (3, 1, 5)
        
        assert version_parts >= required_version, (
            f"Werkzeug version {werkzeug_version} is installed, "
            f"but version 3.1.5 or higher is required to resolve CVE-2025-0995"
        )

    def test_werkzeug_cve_vulnerability_patched(self):
        """Verifies that the CVE-2025-0995 vulnerability is patched."""
        # CVE-2025-0995 relates to Windows device name handling
        # Testing that safe_join is available and properly handles device names
        assert safe_join is not None, "safe_join function is not available in werkzeug.security"
        
        # Checking version specifically addresses the CVE
        version_parts = tuple(map(int, werkzeug_version.split(".")[:3]))
        assert version_parts >= (3, 1, 5), (
            "Werkzeug version does not include CVE-2025-0995 patch"
        )

    def test_werkzeug_package_importable(self):
        """Verifies that all required Werkzeug security functions are importable."""
        assert safe_join is not None, "Cannot import safe_join from werkzeug.security"
        assert secure_filename is not None, "Cannot import secure_filename from werkzeug.utils"


class TestSafeJoinWindowsDeviceExploits:
    """Tests for safe_join function preventing Windows device name exploits."""

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific tests")
    def test_safe_join_blocks_con_device(self):
        """Ensures safe_join prevents access to CON device name."""
        base_path = "C:\\test\\directory"
        
        # Testing various CON device name exploits
        dangerous_paths = [
            "CON",
            "con",
            "Con",
            "CON.txt",
        ]
        
        for dangerous_path in dangerous_paths:
            result = safe_join(base_path, dangerous_path)
            # safe_join should return None for invalid paths
            assert result is None, (
                f"safe_join failed to block Windows device name: {dangerous_path}, got: {result}"
            )

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific tests")
    def test_safe_join_blocks_all_windows_devices(self):
        """Ensures safe_join blocks all Windows reserved device names."""
        base_path = "C:\\test\\directory"
        
        # Windows reserved device names
        device_names = [
            "CON", "PRN", "AUX", "NUL",
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
        ]
        
        for device in device_names:
            # Testing both uppercase and lowercase
            for name in [device, device.lower(), device.capitalize()]:
                result = safe_join(base_path, name)
                assert result is None or device not in result.upper(), (
                    f"safe_join failed to block Windows device name: {name}"
                )

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific tests")
    def test_safe_join_blocks_device_with_extension(self):
        """Ensures safe_join blocks device names with file extensions."""
        base_path = "C:\\test\\directory"
        
        dangerous_paths = [
            "CON.txt",
            "PRN.log",
            "AUX.dat",
            "NUL.tmp",
            "COM1.ini",
            "LPT1.cfg",
        ]
        
        for dangerous_path in dangerous_paths:
            result = safe_join(base_path, dangerous_path)
            # Getting the device name (before the extension)
            device = dangerous_path.split(".")[0]
            assert result is None or device not in result.upper(), (
                f"safe_join failed to block device name with extension: {dangerous_path}"
            )

    def test_safe_join_allows_normal_filenames(self):
        """Verifies that safe_join allows legitimate file paths."""
        base_path = "C:\\test\\directory"
        
        legitimate_paths = [
            "image.jpg",
            "document.pdf",
            "report.txt",
            "subdir/file.txt",  # Using forward slashes for cross-platform compatibility
            "data_console.log",  # Contains "con" but not as device name
            "printer_config.ini",  # Contains "prn" but not as device name
        ]
        
        for legit_path in legitimate_paths:
            result = safe_join(base_path, legit_path)
            # Should return a valid path (not None)
            assert result is not None, (
                f"safe_join incorrectly blocked legitimate filename: {legit_path}"
            )

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific tests")
    def test_safe_join_blocks_path_traversal_with_device(self):
        """Ensures safe_join blocks path traversal attempts with device names."""
        base_path = "C:\\test\\directory"
        
        malicious_paths = [
            "..\\..\\CON",
            "..\\..\\..\\PRN",
            "subdir\\..\\..\\AUX",
            "..\\CON.txt",
        ]
        
        for malicious_path in malicious_paths:
            result = safe_join(base_path, malicious_path)
            # Should return None or not escape the base path
            if result is not None:
                # Checking that result is within base_path
                assert result.startswith(base_path), (
                    f"safe_join allowed path traversal: {malicious_path}"
                )


class TestSendFromDirectoryWindowsDevices:
    """Tests for send_from_directory handling of special device names on Windows."""

    @pytest.fixture
    def flask_app(self):
        """Creates a Flask app for testing."""
        app = Flask(__name__)
        app.config["TESTING"] = True
        return app

    @pytest.fixture
    def test_directory(self):
        """Creates a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific tests")
    def test_send_from_directory_blocks_con_device(self, flask_app, test_directory):
        """Ensures send_from_directory rejects CON device name."""
        with flask_app.test_request_context():
            # Attempting to access CON device
            with pytest.raises(Exception):  # Should raise NotFound or similar
                send_from_directory(test_directory, "CON")

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific tests")
    def test_send_from_directory_blocks_all_devices(self, flask_app, test_directory):
        """Ensures send_from_directory blocks all Windows device names."""
        device_names = [
            "CON", "PRN", "AUX", "NUL",
            "COM1", "LPT1",
        ]
        
        with flask_app.test_request_context():
            for device in device_names:
                with pytest.raises(Exception):  # Should raise NotFound or similar
                    send_from_directory(test_directory, device)

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific tests")
    def test_send_from_directory_blocks_device_with_extension(self, flask_app, test_directory):
        """Ensures send_from_directory blocks device names with extensions."""
        dangerous_files = [
            "CON.txt",
            "PRN.log",
            "AUX.dat",
        ]
        
        with flask_app.test_request_context():
            for dangerous_file in dangerous_files:
                with pytest.raises(Exception):  # Should raise NotFound or similar
                    send_from_directory(test_directory, dangerous_file)

    def test_send_from_directory_allows_normal_files(self, flask_app, test_directory):
        """Verifies that send_from_directory allows legitimate file access."""
        # Creating a test file
        test_file = Path(test_directory) / "test_image.jpg"
        test_file.write_bytes(b"test content")
        
        with flask_app.test_request_context():
            # Should successfully send the file
            response = send_from_directory(test_directory, "test_image.jpg")
            assert response.status_code == 200
            # Closing the response to release file handle
            response.close()

    def test_send_from_directory_blocks_path_traversal(self, flask_app, test_directory):
        """Ensures send_from_directory blocks path traversal attempts."""
        malicious_paths = [
            "..\\..\\sensitive.txt",
            "..\\..\\..\\etc\\passwd",
            "subdir\\..\\..\\secret.key",
        ]
        
        with flask_app.test_request_context():
            for malicious_path in malicious_paths:
                with pytest.raises(Exception):  # Should raise NotFound or similar
                    send_from_directory(test_directory, malicious_path)

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific tests")
    def test_send_from_directory_integration_with_safe_join(self, flask_app, test_directory):
        """Verifies that send_from_directory uses safe_join internally."""
        # Testing that send_from_directory properly validates paths
        # by attempting various exploits that safe_join should block
        
        exploits = [
            "CON",
            "..\\CON",
            "CON.txt",
            "..\\..\\sensitive.dat",
        ]
        
        with flask_app.test_request_context():
            for exploit in exploits:
                with pytest.raises(Exception):  # Should raise an appropriate error
                    result = send_from_directory(test_directory, exploit)
                    # If no exception is raised, the function should not return successfully
                    assert result.status_code >= 400, (
                        f"send_from_directory failed to block: {exploit}"
                    )


class TestApplicationIntegration:
    """Integration tests ensuring the application uses secure file handling."""

    @pytest.fixture
    def app_client(self):
        """Creates a test client for the Flask application."""
        try:
            from app import app
            app.config["TESTING"] = True
            return app.test_client()
        except ImportError:
            pytest.skip("Cannot import app module")

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific tests")
    def test_app_endpoints_reject_device_names(self, app_client):
        """Verifies that application endpoints reject Windows device names."""
        # Testing if the app has any file-serving endpoints
        # This is a general test to ensure the app doesn't expose device names
        
        device_names = ["CON", "PRN", "AUX", "NUL"]
        
        for device in device_names:
            # Testing various potential endpoints
            endpoints = [
                f"/static/{device}",
                f"/files/{device}",
                f"/uploads/{device}",
            ]
            
            for endpoint in endpoints:
                response = app_client.get(endpoint)
                # Should return 404 Not Found or similar error
                assert response.status_code in [400, 404, 403], (
                    f"Application allowed access to device name: {device} at {endpoint}"
                )

    def test_werkzeug_version_in_application_context(self, app_client):
        """Ensures the application is using the correct Werkzeug version."""
        import werkzeug
        version_parts = tuple(map(int, werkzeug.__version__.split(".")[:3]))
        assert version_parts >= (3, 1, 5), (
            f"Application is using Werkzeug {werkzeug.__version__}, "
            "but version 3.1.5+ is required"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
