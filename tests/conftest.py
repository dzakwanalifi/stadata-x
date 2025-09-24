"""
Pytest configuration and shared fixtures
"""

import pytest
import tempfile
import pandas as pd
from unittest.mock import MagicMock
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup is handled by pytest


@pytest.fixture
def sample_dataframe():
    """Create sample pandas DataFrame for testing"""
    return pd.DataFrame({
        'Provinsi': ['ACEH', 'SUMATERA UTARA', 'SUMATERA BARAT'],
        'Luas_Panen': [15000, 20000, 12000],
        'Produksi': [75000, 100000, 60000],
        'Tahun': [2023, 2023, 2023]
    })


@pytest.fixture
def mock_api_client():
    """Create mock API client for testing"""
    mock_client = MagicMock()
    mock_client.get_regions.return_value = [
        {'kode': '11', 'nama': 'ACEH'},
        {'kode': '12', 'nama': 'SUMATERA UTARA'},
        {'kode': '13', 'nama': 'SUMATERA BARAT'}
    ]

    mock_client.get_table_list.return_value = [
        {
            'table_id': '287',
            'title': 'Luas Panen Padi',
            'subject': 'Pertanian',
            'update_date': '2023-12-01'
        }
    ]

    return mock_client


@pytest.fixture
def mock_config(temp_dir):
    """Create mock configuration for testing"""
    from stadata_x.config import Config

    # Override home directory for testing
    with patch('stadata_x.config.Path.home', return_value=Path(temp_dir)):
        config = Config()
        config.api_token = "test_token_123"
        config.download_path = Path(temp_dir) / "downloads"
        yield config


@pytest.fixture
def mock_response_success():
    """Create mock successful HTTP response"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'data': [
            {'kode': '11', 'nama': 'ACEH'},
            {'kode': '12', 'nama': 'SUMATERA UTARA'}
        ]
    }
    return mock_response


@pytest.fixture
def mock_response_error():
    """Create mock error HTTP response"""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = Exception("404 Not Found")
    return mock_response


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Test configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "ui: marks tests as UI tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Add markers based on test names
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        if "ui" in str(item.fspath):
            item.add_marker(pytest.mark.ui)
        if "performance" in item.name.lower():
            item.add_marker(pytest.mark.slow)
