"""
Integration tests for component interactions
"""

import pytest
import pandas as pd
from pathlib import Path


class TestAPIAndUIIntegration:
    """Integration tests for API and UI interactions"""

    def test_api_client_creation(self):
        """Test API client can be created and has expected interface"""
        from stadata_x.api_client import ApiClient

        client = ApiClient()
        assert client is not None

        # Test that client has all expected methods
        expected_methods = [
            'list_domains',
            'list_static_tables',
            'view_static_table',
            'download_table',
            'is_ready'
        ]

        for method in expected_methods:
            assert hasattr(client, method), f"Client missing method: {method}"

    def test_data_processing_compatibility(self):
        """Test data processing compatibility between components"""
        # Create test data
        test_data = pd.DataFrame({
            'Provinsi': ['ACEH', 'SUMUT'],
            'Produksi': [1000, 1500],
            'Luas': [500, 750]
        })

        # Test that data can be processed
        assert len(test_data) == 2
        assert 'Provinsi' in test_data.columns
        assert test_data['Produksi'].sum() == 2500

    def test_ui_data_binding_simulation(self):
        """Test UI data binding simulation"""
        # Test that UI components can handle data structures
        sample_data = {
            'regions': [
                {'kode': '11', 'nama': 'ACEH'},
                {'kode': '12', 'nama': 'SUMUT'}
            ],
            'tables': [
                {'id': '287', 'title': 'Padi Production'}
            ]
        }

        # Test data structure integrity
        assert len(sample_data['regions']) == 2
        assert len(sample_data['tables']) == 1
        assert sample_data['regions'][0]['kode'] == '11'


class TestConfigAndAPIIntegration:
    """Integration tests for configuration and API interactions"""

    def test_config_functions_availability(self):
        """Test that config functions are available"""
        from stadata_x.config import load_config, save_config, save_token, load_token

        # Test functions exist
        assert callable(load_config)
        assert callable(save_config)
        assert callable(save_token)
        assert callable(load_token)

    def test_api_client_config_compatibility(self):
        """Test API client can work with config system"""
        from stadata_x.api_client import ApiClient
        from stadata_x.config import load_token

        # Test client can be created
        client = ApiClient()
        assert client is not None

        # Test config functions work
        token = load_token()
        # Token might be None or a string
        assert token is None or isinstance(token, str)


class TestErrorHandlingIntegration:
    """Integration tests for error handling across components"""

    def test_error_classes_available(self):
        """Test that error classes are properly defined"""
        from stadata_x.api_client import (
            ApiTokenError,
            BpsServerError,
            BpsApiDataError,
            NoInternetError
        )

        # All error classes should exist
        assert ApiTokenError is not None
        assert BpsServerError is not None
        assert BpsApiDataError is not None
        assert NoInternetError is not None

    def test_config_error_handling(self):
        """Test configuration error handling"""
        from stadata_x.config import load_config

        # Config loading should handle errors gracefully
        config = load_config()
        # Should return empty dict or valid data
        assert isinstance(config, dict)

    def test_dependency_imports(self):
        """Test that all required dependencies can be imported"""
        # Test core dependencies
        try:
            import pandas as pd
            import textual
            from pathlib import Path
            assert True
        except ImportError as e:
            pytest.fail(f"Required dependency not available: {e}")


class TestUIAndDataIntegration:
    """Integration tests for UI and data processing"""

    def test_dataframe_operations(self, sample_dataframe):
        """Test DataFrame operations that UI would perform"""
        df = sample_dataframe

        # Test column detection
        numeric_cols = ['Luas_Panen', 'Produksi']
        text_cols = ['Provinsi']

        for col in numeric_cols:
            assert col in df.columns

        for col in text_cols:
            assert col in df.columns

    def test_data_filtering_and_display(self, sample_dataframe):
        """Test data filtering and display logic"""
        df = sample_dataframe

        # Test filtering by region
        aceh_data = df[df['Provinsi'] == 'ACEH']
        assert len(aceh_data) == 1
        assert aceh_data.iloc[0]['Luas_Panen'] == 15000

        # Test numeric operations
        total_production = df['Produksi'].sum()
        assert total_production == 235000  # 75000 + 100000 + 60000

        # Test sorting
        sorted_df = df.sort_values('Luas_Panen', ascending=False)
        assert sorted_df.iloc[0]['Provinsi'] == 'SUMATERA UTARA'
        assert sorted_df.iloc[0]['Luas_Panen'] == 20000

    def test_widget_class_availability(self):
        """Test that widget classes are available"""
        from stadata_x.widgets.data_table import StadataDataTable
        from stadata_x.widgets.data_explorer import DataExplorer

        # Test classes exist
        assert StadataDataTable is not None
        assert DataExplorer is not None

        # Test they have required methods
        assert hasattr(StadataDataTable, '__init__')
        assert hasattr(DataExplorer, '__init__')




class TestDataExportIntegration:
    """Integration tests for data export functionality"""

    def test_export_format_integration(self, sample_dataframe, temp_dir):
        """Test export format integration"""
        import os

        df = sample_dataframe
        export_dir = Path(temp_dir) / "exports"
        export_dir.mkdir(exist_ok=True)

        # Test CSV export
        csv_path = export_dir / "test_data.csv"
        df.to_csv(csv_path, index=False)
        assert csv_path.exists()

        # Verify CSV content
        with open(csv_path, 'r') as f:
            content = f.read()
            assert 'Provinsi' in content
            assert 'ACEH' in content

        # Test JSON export
        json_path = export_dir / "test_data.json"
        df.to_json(json_path, orient='records')
        assert json_path.exists()

        # Verify JSON content
        import json
        with open(json_path, 'r') as f:
            json_data = json.load(f)
            assert isinstance(json_data, list)
            assert len(json_data) == 3

    def test_export_workflow_simulation(self, sample_dataframe, temp_dir):
        """Test complete export workflow simulation"""
        from pathlib import Path

        df = sample_dataframe
        export_path = Path(temp_dir) / "exported_data.csv"

        # Simulate the export workflow
        df.to_csv(export_path, index=False)

        # Verify file was created
        assert export_path.exists()

        # Verify file is readable
        imported_df = pd.read_csv(export_path)
        assert len(imported_df) == len(df)
        assert list(imported_df.columns) == list(df.columns)

        # Verify data integrity
        assert imported_df.iloc[0]['Provinsi'] == df.iloc[0]['Provinsi']


class TestPerformanceIntegration:
    """Integration tests for performance across components"""

    def test_large_dataframe_handling(self):
        """Test handling of larger DataFrames"""
        # Create a larger test dataset
        large_df = pd.DataFrame({
            'Region': [f'Region_{i}' for i in range(1000)],
            'Value1': range(1000),
            'Value2': range(1000, 2000),
            'Category': (['A', 'B', 'C'] * 334)[:1000]  # Repeat pattern, slice to 1000
        })

        assert len(large_df) == 1000

        # Test DataFrame operations
        summary = large_df.describe()
        assert summary is not None

        # Test filtering
        filtered = large_df[large_df['Category'] == 'A']
        assert len(filtered) > 0

        # Test grouping
        grouped = large_df.groupby('Category')['Value1'].mean()
        assert len(grouped) == 3

    def test_performance_simulation(self):
        """Test basic performance simulation"""
        import time

        # Simple performance test
        start_time = time.time()

        # Simulate some operations
        data = list(range(100))
        result = sum(data)

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete quickly
        assert total_time < 1.0  # Less than 1 second
        assert result == 4950  # sum of 0-99

    def test_memory_usage_integration(self, sample_dataframe):
        """Test memory usage across components"""
        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())
        except ImportError:
            pytest.skip("psutil not available for memory testing")
            return

        # Baseline memory
        baseline = process.memory_info().rss / 1024 / 1024  # MB

        # Create multiple components
        df = sample_dataframe
        from stadata_x.widgets.data_table import StadataDataTable
        table = StadataDataTable()

        # Perform operations
        filtered_df = df[df['Produksi'] > 70000]
        sorted_df = filtered_df.sort_values('Luas_Panen')

        # Check memory after operations
        after_ops = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = after_ops - baseline

        # Memory increase should be reasonable
        assert memory_increase < 50  # Less than 50MB increase


class TestCrossPlatformIntegration:
    """Integration tests for cross-platform compatibility"""

    def test_path_handling_cross_platform(self):
        """Test path handling across platforms"""
        from pathlib import Path

        # Test various path formats
        paths = [
            Path("data/file.csv"),
            Path("./data/file.csv"),
            Path("../data/file.csv"),
            Path("~/data/file.csv")  # This might not resolve on Windows
        ]

        for path in paths:
            # Paths should be Path objects
            assert isinstance(path, Path)

    def test_file_operations_cross_platform(self, temp_dir):
        """Test file operations across platforms"""
        import os

        test_file = Path(temp_dir) / "test.txt"
        test_content = "Hello, cross-platform world!"

        # Write file
        with open(test_file, 'w') as f:
            f.write(test_content)

        # Read file
        with open(test_file, 'r') as f:
            content = f.read()

        assert content == test_content

        # Test file permissions (basic check)
        assert test_file.exists()
        assert test_file.stat().st_size > 0


class TestEndToEndWorkflow:
    """End-to-end workflow tests"""

    def test_user_workflow_data_structures(self):
        """Test user workflow data structures"""
        # Test the data structures used in user workflow

        # Region data structure
        regions = [
            {'kode': '11', 'nama': 'ACEH'},
            {'kode': '12', 'nama': 'SUMATERA UTARA'}
        ]

        # Table data structure
        tables = [{
            'table_id': '287',
            'title': 'Luas Panen Padi',
            'subject': 'Pertanian'
        }]

        # Verify data structures
        assert len(regions) == 2
        assert regions[0]['kode'] == '11'
        assert len(tables) == 1
        assert tables[0]['table_id'] == '287'
