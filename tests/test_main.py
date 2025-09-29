"""Tests for the main application entry point."""

import pytest
from unittest.mock import patch, MagicMock
from app.main import main


class TestMainApplication:
    """Test the main application entry point."""

    @patch('app.main.uvicorn.run')
    @patch('app.main.setup_logging')
    @patch('app.main.settings')
    def test_main_function_success(self, mock_settings, mock_setup_logging, mock_uvicorn_run):
        """Test successful main function execution."""
        # Arrange
        mock_logger = MagicMock()
        mock_setup_logging.return_value = mock_logger
        mock_settings.DEBUG = True
        mock_settings.ENABLE_METRICS = True
        mock_settings.API_HOST = "0.0.0.0"
        mock_settings.API_PORT = 8000

        # Act
        main()

        # Assert
        mock_setup_logging.assert_called_once_with(
            app_name="dexter_ai_agent",
            log_level="DEBUG"
        )
        mock_logger.info.assert_any_call("Starting Dexter AI Agent")
        mock_logger.info.assert_any_call("Debug mode: True")
        mock_logger.info.assert_any_call("Metrics enabled: True")
        mock_uvicorn_run.assert_called_once_with(
            "app.api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="debug"
        )

    @patch('app.main.uvicorn.run')
    @patch('app.main.setup_logging')
    @patch('app.main.settings')
    def test_main_function_production_mode(self, mock_settings, mock_setup_logging, mock_uvicorn_run):
        """Test main function execution in production mode (DEBUG=False)."""
        # Arrange
        mock_logger = MagicMock()
        mock_setup_logging.return_value = mock_logger
        mock_settings.DEBUG = False
        mock_settings.ENABLE_METRICS = False
        mock_settings.API_HOST = "127.0.0.1"
        mock_settings.API_PORT = 8080

        # Act
        main()

        # Assert
        mock_setup_logging.assert_called_once_with(
            app_name="dexter_ai_agent",
            log_level="INFO"
        )
        mock_logger.info.assert_any_call("Debug mode: False")
        mock_logger.info.assert_any_call("Metrics enabled: False")
        mock_uvicorn_run.assert_called_once_with(
            "app.api.main:app",
            host="127.0.0.1",
            port=8080,
            reload=False,
            log_level="info"
        )

    @patch('app.main.uvicorn.run')
    @patch('app.main.setup_logging')
    @patch('app.main.settings')
    def test_main_function_custom_host_port(self, mock_settings, mock_setup_logging, mock_uvicorn_run):
        """Test main function with custom host and port settings."""
        # Arrange
        mock_logger = MagicMock()
        mock_setup_logging.return_value = mock_logger
        mock_settings.DEBUG = False
        mock_settings.ENABLE_METRICS = True
        mock_settings.API_HOST = "192.168.1.100"
        mock_settings.API_PORT = 9000

        # Act
        main()

        # Assert
        mock_uvicorn_run.assert_called_once_with(
            "app.api.main:app",
            host="192.168.1.100",
            port=9000,
            reload=False,
            log_level="info"
        )

    @patch('app.main.uvicorn.run')
    @patch('app.main.setup_logging')
    @patch('app.main.settings')
    def test_main_function_logging_setup(self, mock_settings, mock_setup_logging, mock_uvicorn_run):
        """Test that logging is properly set up in main function."""
        # Arrange
        mock_logger = MagicMock()
        mock_setup_logging.return_value = mock_logger
        mock_settings.DEBUG = True
        mock_settings.ENABLE_METRICS = True
        mock_settings.API_HOST = "0.0.0.0"
        mock_settings.API_PORT = 8000

        # Act
        main()

        # Assert
        mock_setup_logging.assert_called_once()
        mock_logger.info.assert_called()

    @patch('app.main.uvicorn.run')
    @patch('app.main.setup_logging')
    @patch('app.main.settings')
    def test_main_function_uvicorn_configuration(self, mock_settings, mock_setup_logging, mock_uvicorn_run):
        """Test that uvicorn is configured correctly based on settings."""
        # Arrange
        mock_logger = MagicMock()
        mock_setup_logging.return_value = mock_logger
        mock_settings.DEBUG = True
        mock_settings.ENABLE_METRICS = True
        mock_settings.API_HOST = "0.0.0.0"
        mock_settings.API_PORT = 8000

        # Act
        main()

        # Assert
        mock_uvicorn_run.assert_called_once()
        call_args = mock_uvicorn_run.call_args
        assert call_args[0][0] == "app.api.main:app"  # app module
        assert call_args[1]["host"] == "0.0.0.0"
        assert call_args[1]["port"] == 8000
        assert call_args[1]["reload"] is True
        assert call_args[1]["log_level"] == "debug"

    @patch('app.main.uvicorn.run')
    @patch('app.main.setup_logging')
    @patch('app.main.settings')
    def test_main_function_production_uvicorn_configuration(self, mock_settings, mock_setup_logging, mock_uvicorn_run):
        """Test uvicorn configuration in production mode."""
        # Arrange
        mock_logger = MagicMock()
        mock_setup_logging.return_value = mock_logger
        mock_settings.DEBUG = False
        mock_settings.ENABLE_METRICS = False
        mock_settings.API_HOST = "127.0.0.1"
        mock_settings.API_PORT = 8080

        # Act
        main()

        # Assert
        call_args = mock_uvicorn_run.call_args
        assert call_args[1]["reload"] is False
        assert call_args[1]["log_level"] == "info"

    @patch('app.main.uvicorn.run')
    @patch('app.main.setup_logging')
    @patch('app.main.settings')
    def test_main_function_metrics_enabled(self, mock_settings, mock_setup_logging, mock_uvicorn_run):
        """Test main function when metrics are enabled."""
        # Arrange
        mock_logger = MagicMock()
        mock_setup_logging.return_value = mock_logger
        mock_settings.DEBUG = False
        mock_settings.ENABLE_METRICS = True
        mock_settings.API_HOST = "0.0.0.0"
        mock_settings.API_PORT = 8000

        # Act
        main()

        # Assert
        mock_logger.info.assert_any_call("Metrics enabled: True")

    @patch('app.main.uvicorn.run')
    @patch('app.main.setup_logging')
    @patch('app.main.settings')
    def test_main_function_metrics_disabled(self, mock_settings, mock_setup_logging, mock_uvicorn_run):
        """Test main function when metrics are disabled."""
        # Arrange
        mock_logger = MagicMock()
        mock_setup_logging.return_value = mock_logger
        mock_settings.DEBUG = False
        mock_settings.ENABLE_METRICS = False
        mock_settings.API_HOST = "0.0.0.0"
        mock_settings.API_PORT = 8000

        # Act
        main()

        # Assert
        mock_logger.info.assert_any_call("Metrics enabled: False")

    @patch('app.main.uvicorn.run')
    @patch('app.main.setup_logging')
    @patch('app.main.settings')
    def test_main_function_debug_mode_true(self, mock_settings, mock_setup_logging, mock_uvicorn_run):
        """Test main function when debug mode is enabled."""
        # Arrange
        mock_logger = MagicMock()
        mock_setup_logging.return_value = mock_logger
        mock_settings.DEBUG = True
        mock_settings.ENABLE_METRICS = True
        mock_settings.API_HOST = "0.0.0.0"
        mock_settings.API_PORT = 8000

        # Act
        main()

        # Assert
        mock_logger.info.assert_any_call("Debug mode: True")
        mock_uvicorn_run.assert_called_once()
        call_args = mock_uvicorn_run.call_args
        assert call_args[1]["reload"] is True
        assert call_args[1]["log_level"] == "debug"

    @patch('app.main.uvicorn.run')
    @patch('app.main.setup_logging')
    @patch('app.main.settings')
    def test_main_function_debug_mode_false(self, mock_settings, mock_setup_logging, mock_uvicorn_run):
        """Test main function when debug mode is disabled."""
        # Arrange
        mock_logger = MagicMock()
        mock_setup_logging.return_value = mock_logger
        mock_settings.DEBUG = False
        mock_settings.ENABLE_METRICS = True
        mock_settings.API_HOST = "0.0.0.0"
        mock_settings.API_PORT = 8000

        # Act
        main()

        # Assert
        mock_logger.info.assert_any_call("Debug mode: False")
        mock_uvicorn_run.assert_called_once()
        call_args = mock_uvicorn_run.call_args
        assert call_args[1]["reload"] is False
        assert call_args[1]["log_level"] == "info"
