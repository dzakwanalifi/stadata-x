# Test Suite for stadata-x

Comprehensive test suite for the stadata-x package - Terminal UI for exploring Indonesian BPS statistical data.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest configuration and shared fixtures
├── test_api_client.py         # API client functionality tests
├── test_ui_components.py      # UI components and screens tests
├── test_config.py             # Configuration management tests
├── test_main.py               # Main application and CLI tests
├── test_utils.py              # Utility functions tests
├── test_integration.py        # Integration tests
└── README.md                  # This file
```

## Test Categories

### Unit Tests
- **API Client**: HTTP requests, data parsing, error handling
- **Configuration**: File operations, validation, persistence
- **UI Components**: Widget initialization, data binding
- **Utilities**: Data processing, file operations, validation

### Integration Tests
- **API + UI**: Data flow from API to UI components
- **Config + API**: Configuration integration with API calls
- **Data Export**: Complete export workflow testing
- **Error Handling**: Error propagation across components

### End-to-End Tests
- **Complete Workflow**: Full user journey simulation
- **Cross-Platform**: Path handling, file operations
- **Performance**: Memory usage, response times

## Running Tests

### Prerequisites
```bash
pip install pytest pytest-cov requests pandas
```

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest -m "not integration"

# Integration tests only
pytest -m integration

# UI tests only
pytest -m ui

# Performance tests
pytest -m slow
```

### Run Specific Test Files
```bash
pytest tests/test_api_client.py
pytest tests/test_integration.py
```

### Run with Coverage
```bash
pytest --cov=stadata_x --cov-report=html
```

### Run with Verbose Output
```bash
pytest -v
```

## Test Fixtures

### Shared Fixtures (conftest.py)
- `temp_dir`: Temporary directory for file operations
- `sample_dataframe`: Sample pandas DataFrame for testing
- `mock_api_client`: Mock API client for testing
- `mock_config`: Mock configuration for testing
- `mock_response_success`: Mock successful HTTP response
- `mock_response_error`: Mock error HTTP response

## Test Coverage

The test suite covers:

### API Client (`test_api_client.py`)
- ✅ Region retrieval (success/error cases)
- ✅ Table list retrieval with filters
- ✅ Static table viewing (DataFrame conversion)
- ✅ Error handling (network, API, data format)
- ✅ Numeric column detection
- ✅ HTTP status code handling

### UI Components (`test_ui_components.py`)
- ✅ Screen initialization and composition
- ✅ Data table widget functionality
- ✅ Data explorer widget
- ✅ Download dialog validation
- ✅ Error message formatting
- ✅ Responsive layout

### Configuration (`test_config.py`)
- ✅ Config file creation and paths
- ✅ Save/load operations
- ✅ Validation and error handling
- ✅ Thread safety
- ✅ Migration support

### Main Application (`test_main.py`)
- ✅ CLI entry points
- ✅ Application startup
- ✅ Error handling
- ✅ Package structure validation

### Utilities (`test_utils.py`)
- ✅ Data processing helpers
- ✅ File operations
- ✅ Path handling
- ✅ Export format validation
- ✅ UI helper functions

### Integration (`test_integration.py`)
- ✅ API to UI data flow
- ✅ Configuration integration
- ✅ Export workflow
- ✅ Error propagation
- ✅ Performance testing
- ✅ Cross-platform compatibility

## Mock Strategy

The tests use comprehensive mocking:

### HTTP Requests
```python
@patch('stadata_x.api_client.requests.get')
def test_api_call(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': []}
    mock_get.return_value = mock_response
```

### File System Operations
```python
@patch('stadata_x.config.Path.home')
def test_config_operations(mock_home, temp_dir):
    mock_home.return_value = Path(temp_dir)
```

### UI Components
```python
@patch('stadata_x.screens.dashboard_screen.ApiClient')
def test_screen_functionality(mock_api_client):
    # Test UI logic without actual rendering
```

## Performance Testing

### Memory Usage
```python
def test_memory_usage_integration(self, sample_dataframe):
    # Monitor memory usage during operations
    baseline = process.memory_info().rss / 1024 / 1024  # MB
    # ... perform operations ...
    memory_increase = after_ops - baseline
    assert memory_increase < 50  # MB
```

### Response Times
```python
def test_api_response_time_simulation(self, mock_get):
    start_time = time.time()
    result = client.get_regions()
    response_time = time.time() - start_time
    assert response_time < 1.0  # seconds
```

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run Tests
  run: |
    pip install -e .[dev]
    pytest --cov=stadata_x --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Test Data

### Sample Datasets
- Regional BPS data (provinces, districts)
- Agricultural statistics (rice production, land area)
- Mixed data types (numeric, text, dates)

### Mock API Responses
- Successful data retrieval
- Error conditions (404, 500, timeout)
- Invalid data formats
- Network failures

## Contributing to Tests

### Adding New Tests
1. Create test file in appropriate category
2. Use descriptive test names: `test_<functionality>_<condition>`
3. Include docstrings explaining test purpose
4. Use fixtures from `conftest.py`
5. Mock external dependencies

### Test Naming Convention
```python
def test_api_client_get_regions_success(self):
    """Test successful region data retrieval"""

def test_api_client_get_regions_network_error(self):
    """Test region retrieval with network failure"""

def test_config_save_load_integration(self):
    """Test configuration save and load operations"""
```

### Test Organization
- Group related tests in classes
- Use setup/teardown methods for common initialization
- Separate unit, integration, and e2e tests
- Mark slow tests appropriately

## Test Maintenance

### Regular Updates Needed
- Update mock data when API changes
- Add tests for new features
- Update performance benchmarks
- Review and update fixtures

### Coverage Goals
- **API Client**: >95% coverage
- **Configuration**: >90% coverage
- **UI Components**: >80% coverage (UI testing limitations)
- **Utilities**: >95% coverage
- **Overall**: >85% coverage

## Troubleshooting

### Common Issues
1. **Mock not working**: Check import paths and patch targets
2. **Fixture conflicts**: Ensure proper fixture scoping
3. **Async test issues**: Use appropriate async test patterns
4. **Platform differences**: Test on multiple platforms when possible

### Debugging Tests
```bash
# Run specific test with debug output
pytest tests/test_api_client.py::TestApiClient::test_get_regions_success -v -s

# Run with pdb on failure
pytest --pdb

# Run with coverage details
pytest --cov=stadata_x --cov-report=term-missing
```

This comprehensive test suite ensures stadata-x maintains high quality and reliability across all components and use cases.
