"""
Comprehensive tests for API client functionality
"""

import pytest
from stadata_x.api_client import (
    ApiClient,
    BpsServerError,
    BpsApiDataError,
    ApiTokenError,
    NoInternetError
)


class TestApiClient:
    """Test suite for ApiClient class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.client = ApiClient()

    def test_initialization(self):
        """Test ApiClient initialization"""
        assert self.client is not None
        assert hasattr(self.client, 'list_domains')
        assert hasattr(self.client, 'list_static_tables')
        assert hasattr(self.client, 'view_static_table')

    def test_is_ready_property(self):
        """Test is_ready property"""
        # Test that is_ready property exists and returns boolean
        assert hasattr(self.client, 'is_ready')
        result = self.client.is_ready
        assert isinstance(result, bool)

    def test_error_classes_exist(self):
        """Test that all error classes are properly defined"""
        assert ApiTokenError is not None
        assert BpsServerError is not None
        assert BpsApiDataError is not None
        assert NoInternetError is not None

        # Test error inheritance
        assert issubclass(ApiTokenError, Exception)
        assert issubclass(BpsServerError, Exception)
        assert issubclass(BpsApiDataError, Exception)
        assert issubclass(NoInternetError, Exception)

    def test_client_has_token(self):
        """Test that client can be initialized with token"""
        client_with_token = ApiClient(token="test_token")
        assert client_with_token is not None

    def test_async_methods_exist(self):
        """Test that async methods are properly defined"""
        # Check that methods exist (full async testing would require event loop)
        assert hasattr(self.client, 'list_domains')
        assert hasattr(self.client, 'list_static_tables')
        assert hasattr(self.client, 'view_static_table')
        assert hasattr(self.client, 'download_table')

    def test_dataframe_cleaning_method_exists(self):
        """Test that dataframe cleaning method exists"""
        assert hasattr(self.client, '_clean_bps_dataframe')

    def test_api_call_retry_method_exists(self):
        """Test that API call retry method exists"""
        assert hasattr(self.client, '_api_call_with_retry')
