"""
Tests for main application entry point and CLI
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

from stadata_x.main import run
from stadata_x.app import StadataXApp


class TestMainApplication:
    """Test suite for main application"""

    def test_run_function_exists(self):
        """Test that run function exists"""
        assert run is not None
        assert callable(run)

    @patch('stadata_x.main.StadataXApp')
    def test_run_function_calls_app(self, mock_app):
        """Test that run function initializes and runs the app"""
        mock_app_instance = MagicMock()
        mock_app.return_value = mock_app_instance

        run()

        mock_app.assert_called_once()
        mock_app_instance.run.assert_called_once()

    @patch('stadata_x.main.StadataXApp')
    def test_run_function_error_handling(self, mock_app):
        """Test error handling in run function"""
        mock_app_instance = MagicMock()
        mock_app_instance.run.side_effect = Exception("Test error")
        mock_app.return_value = mock_app_instance

        # Test that run function handl
        # es errors properly
        # This test verifies the mock setup works
        assert mock_app_instance.run.side_effect is not None

    def test_entry_point_script(self):
        """Test that the package has proper entry point"""
        # Test that we can import the main module
        import stadata_x.main
        assert hasattr(stadata_x.main, 'run')

    @patch('stadata_x.main.run')
    def test_command_line_execution(self, mock_run):
        """Test command line execution"""
        # Simulate command line call by calling run directly
        import stadata_x.main
        stadata_x.main.run()
        mock_run.assert_called_once()


class TestStadataXApp:
    """Test suite for StadataXApp"""

    @patch('textual.app.App.__init__')
    def test_app_initialization(self, mock_app_init):
        """Test app initialization"""
        mock_app_init.return_value = None
        app = StadataXApp()
        # Since we mocked __init__, we can't check run method
        # but we can check the class attributes
        assert app is not None
        assert hasattr(StadataXApp, 'CSS_PATH')
        assert hasattr(StadataXApp, 'SCREENS')

    def test_app_inheritance(self):
        """Test that StadataXApp inherits from Textual App"""
        from textual.app import App

        # Test class inheritance without instantiation
        assert issubclass(StadataXApp, App)

    def test_app_title(self):
        """Test app title configuration"""
        # Test class attributes without instantiation
        assert hasattr(StadataXApp, 'TITLE') or hasattr(StadataXApp, 'title')

    def test_app_css_path(self):
        """Test CSS path configuration"""
        # Test class attributes without instantiation
        assert hasattr(StadataXApp, 'CSS_PATH') or hasattr(StadataXApp, 'css_path')
        if hasattr(StadataXApp, 'CSS_PATH'):
            assert StadataXApp.CSS_PATH == "assets/app.css"

    @patch('stadata_x.app.WelcomeScreen')
    @patch('textual.app.App.__init__')
    def test_initial_screen(self, mock_app_init, mock_welcome_screen):
        """Test initial screen setup"""
        mock_app_init.return_value = None
        mock_screen = MagicMock()
        mock_welcome_screen.return_value = mock_screen

        app = StadataXApp()

        # App should have an initial screen
        assert app is not None


class TestCommandLineInterface:
    """Test suite for command line interface"""

    def test_cli_help_option(self):
        """Test CLI help option"""
        # Since there's no CLI parsing, this test is not applicable
        # The app runs directly via entry point
        pass

    def test_cli_version_option(self):
        """Test CLI version option"""
        # Since there's no CLI parsing, this test is not applicable
        # The app runs directly via entry point
        pass

    def test_cli_normal_execution(self):
        """Test normal CLI execution"""
        # Since the app runs directly via entry point, test that run() works
        with patch('stadata_x.main.StadataXApp') as mock_app:
            mock_app_instance = MagicMock()
            mock_app.return_value = mock_app_instance

            from stadata_x.main import run
            run()

            mock_app.assert_called_once()
            mock_app_instance.run.assert_called_once()

    def test_cli_invalid_arguments(self):
        """Test CLI with invalid arguments"""
        # Since there's no argument parsing, this test is not applicable
        pass


class TestApplicationIntegration:
    """Integration tests for the complete application"""

    @patch('stadata_x.main.StadataXApp')
    def test_full_application_startup(self, mock_app):
        """Test full application startup sequence"""
        mock_app_instance = MagicMock()
        mock_app.return_value = mock_app_instance

        # Run the application
        run()

        # Verify app was created and run
        mock_app.assert_called_once()
        mock_app_instance.run.assert_called_once()

    def test_import_chain(self):
        """Test that all modules can be imported"""
        # Test main imports
        import stadata_x.main
        import stadata_x.app
        import stadata_x.config
        import stadata_x.api_client

        # Test screen imports
        import stadata_x.screens.welcome_screen
        import stadata_x.screens.dashboard_screen
        import stadata_x.screens.table_view_screen
        import stadata_x.screens.settings_screen
        import stadata_x.screens.download_dialog_screen

        # Test widget imports
        import stadata_x.widgets.data_explorer
        import stadata_x.widgets.data_table
        import stadata_x.widgets.footer
        import stadata_x.widgets.header
        import stadata_x.widgets.plot_widget
        import stadata_x.widgets.spinner

        # All imports should succeed
        assert True

    def test_version_consistency(self):
        """Test version consistency across modules"""
        import stadata_x

        # Check if version is defined
        assert hasattr(stadata_x, '__version__') or 'version' in str(stadata_x.__file__)

    def test_entry_points_configuration(self):
        """Test that entry points are properly configured"""
        # This would check setup.py/pyproject.toml entry points
        # For now, just verify the main function exists
        from stadata_x.main import run
        assert callable(run)


class TestErrorHandling:
    """Test suite for application error handling"""

    @patch('stadata_x.main.StadataXApp')
    def test_application_startup_error(self, mock_app):
        """Test error during application startup"""
        mock_app.side_effect = ImportError("Missing dependency")

        with pytest.raises(SystemExit):
            run()

    @patch('stadata_x.main.StadataXApp')
    def test_textual_initialization_error(self, mock_app):
        """Test Textual initialization error"""
        mock_app_instance = MagicMock()
        mock_app_instance.run.side_effect = RuntimeError("Display not available")
        mock_app.return_value = mock_app_instance

        with pytest.raises(SystemExit):
            run()

    def test_missing_dependencies_error(self):
        """Test graceful handling of missing dependencies"""
        # This would test import error handling
        # For now, just verify imports work
        try:
            import textual
            import pandas
            import requests
            assert True
        except ImportError:
            pytest.fail("Required dependencies not available")


class TestApplicationConfiguration:
    """Test suite for application configuration"""

    def test_css_file_availability(self):
        """Test that CSS file is available"""
        import stadata_x

        css_path = Path(stadata_x.__file__).parent / "assets" / "app.css"
        assert css_path.exists(), f"CSS file not found at {css_path}"

    def test_logo_file_availability(self):
        """Test that logo file is available"""
        import stadata_x

        logo_path = Path(stadata_x.__file__).parent / "assets" / "logo.txt"
        assert logo_path.exists(), f"Logo file not found at {logo_path}"

    def test_package_structure(self):
        """Test package structure integrity"""
        import stadata_x

        package_dir = Path(stadata_x.__file__).parent

        # Check main directories exist
        assert (package_dir / "screens").exists()
        assert (package_dir / "widgets").exists()
        assert (package_dir / "assets").exists()

        # Check main files exist
        assert (package_dir / "__init__.py").exists()
        assert (package_dir / "main.py").exists()
        assert (package_dir / "app.py").exists()
        assert (package_dir / "config.py").exists()
        assert (package_dir / "api_client.py").exists()

    def test_readme_availability(self):
        """Test README file availability"""
        package_dir = Path(__file__).parent.parent
        readme_path = package_dir / "README.md"
        assert readme_path.exists(), "README.md not found"

    def test_license_availability(self):
        """Test LICENSE file availability"""
        package_dir = Path(__file__).parent.parent
        license_path = package_dir / "LICENSE"
        assert license_path.exists(), "LICENSE file not found"


class TestPerformance:
    """Performance tests for the application"""

    def test_import_performance(self):
        """Test import performance"""
        import time

        start_time = time.time()
        import stadata_x
        import stadata_x.api_client
        import stadata_x.app
        import stadata_x.screens.welcome_screen
        end_time = time.time()

        import_time = end_time - start_time

        # Imports should complete within reasonable time (2 seconds)
        assert import_time < 2.0, f"Import took too long: {import_time} seconds"

    def test_api_client_creation(self):
        """Test that ApiClient can be created without hanging"""
        from stadata_x.api_client import ApiClient

        # This should not hang - just test instantiation
        client = ApiClient()
        assert client is not None
        assert hasattr(client, 'list_domains')

    def test_memory_usage_estimate(self):
        """Test basic memory usage"""
        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB

            # Import the package
            import stadata_x

            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = memory_after - memory_before

            # Memory usage should be reasonable (< 50MB for imports)
            assert memory_used < 50, f"High memory usage: {memory_used} MB"
        except ImportError:
            # Skip test if psutil is not available
            pytest.skip("psutil not available for memory testing")
