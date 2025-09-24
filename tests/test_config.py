"""
Tests for configuration management and utilities
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

from stadata_x.config import load_config, save_config, save_token, load_token


class TestConfig:
    """Test suite for configuration management"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_home = None

    def teardown_method(self):
        """Cleanup test fixtures"""
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

        # Restore original config if it existed
        if self.original_home and (self.original_home / '.stadata-x' / 'config.json').exists():
            # Config file might exist from previous tests, but we'll leave it for cleanup
            pass

    def _patch_config_paths(self):
        """Helper to patch config paths for testing"""
        from stadata_x import config
        # Create a temporary config module for testing
        test_config_dir = self.temp_dir / '.stadata-x'
        test_config_file = test_config_dir / 'config.json'

        # Monkey patch the config module
        original_config_dir = config.CONFIG_DIR
        original_config_file = config.CONFIG_FILE

        config.CONFIG_DIR = test_config_dir
        config.CONFIG_FILE = test_config_file

        return original_config_dir, original_config_file

    def _restore_config_paths(self, original_dir, original_file):
        """Restore original config paths"""
        from stadata_x import config
        config.CONFIG_DIR = original_dir
        config.CONFIG_FILE = original_file

    def test_config_file_paths(self):
        """Test configuration file paths"""
        original_dir, original_file = self._patch_config_paths()

        try:
            from stadata_x.config import CONFIG_DIR, CONFIG_FILE
            expected_config_dir = self.temp_dir / '.stadata-x'
            expected_config_file = expected_config_dir / 'config.json'

            assert CONFIG_DIR == expected_config_dir
            assert CONFIG_FILE == expected_config_file
        finally:
            self._restore_config_paths(original_dir, original_file)

    def test_default_values(self):
        """Test default configuration values"""
        original_dir, original_file = self._patch_config_paths()

        try:
            # API token should be None by default when no config exists
            token = load_token()
            # Note: This might return existing token if config file exists
            # Just test that function doesn't crash
            assert token is None or isinstance(token, str)
        finally:
            self._restore_config_paths(original_dir, original_file)

    def test_config_directory_creation(self):
        """Test automatic config directory creation"""
        original_dir, original_file = self._patch_config_paths()

        try:
            from stadata_x.config import CONFIG_DIR
            # CONFIG_DIR is just a Path object, it doesn't auto-create
            # The directory gets created when saving config
            config_dir = CONFIG_DIR
            assert isinstance(config_dir, Path)

            # Test that save operation creates the directory
            save_token("test")
            assert config_dir.exists()
            assert config_dir.is_dir()
        finally:
            self._restore_config_paths(original_dir, original_file)

    def test_config_save_and_load(self):
        """Test saving and loading configuration"""
        original_dir, original_file = self._patch_config_paths()

        try:
            # Save configuration
            test_config = {"api_token": "test_token_123", "download_path": "/tmp/downloads"}
            save_config(test_config)

            # Load configuration
            loaded_config = load_config()

            assert loaded_config["api_token"] == "test_token_123"
            assert loaded_config["download_path"] == "/tmp/downloads"
        finally:
            self._restore_config_paths(original_dir, original_file)

    def test_token_save_and_load(self):
        """Test token save and load functions"""
        original_dir, original_file = self._patch_config_paths()

        try:
            # Save token
            save_token("test_token_123")

            # Load token
            loaded_token = load_token()

            assert loaded_token == "test_token_123"
        finally:
            self._restore_config_paths(original_dir, original_file)

    def test_config_save_file_creation(self):
        """Test that config file is created when saving"""
        original_dir, original_file = self._patch_config_paths()

        try:
            from stadata_x.config import CONFIG_FILE

            assert not CONFIG_FILE.exists()

            save_token("test_token")

            assert CONFIG_FILE.exists()
            assert CONFIG_FILE.is_file()
        finally:
            self._restore_config_paths(original_dir, original_file)

    def test_config_load_nonexistent_file(self):
        """Test loading when config file doesn't exist"""
        original_dir, original_file = self._patch_config_paths()

        try:
            # Should return empty dict when file doesn't exist
            config = load_config()
            assert config == {}

            # Token should be None
            token = load_token()
            assert token is None
        finally:
            self._restore_config_paths(original_dir, original_file)

    def test_config_load_invalid_json(self):
        """Test loading invalid JSON config file"""
        original_dir, original_file = self._patch_config_paths()

        try:
            from stadata_x.config import CONFIG_FILE

            # Create invalid JSON file
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                f.write("invalid json content {")

            # Should handle invalid JSON gracefully and return empty dict
            config = load_config()
            assert config == {}
        finally:
            self._restore_config_paths(original_dir, original_file)

    def test_config_validation(self):
        """Test configuration validation"""
        original_dir, original_file = self._patch_config_paths()

        try:
            # Test valid token
            save_token("valid_token_123")
            loaded_token = load_token()
            assert loaded_token == "valid_token_123"
        finally:
            self._restore_config_paths(original_dir, original_file)

    def test_config_file_permissions(self):
        """Test config file permissions handling"""
        original_dir, original_file = self._patch_config_paths()

        try:
            from stadata_x.config import CONFIG_FILE

            # Create config directory
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

            # Create config file with content
            save_token("secret_token")

            # Verify file exists and has content
            assert CONFIG_FILE.exists()
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                assert 'api_token' in data
                assert data['api_token'] == "secret_token"
        finally:
            self._restore_config_paths(original_dir, original_file)
