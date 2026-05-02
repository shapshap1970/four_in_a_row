import pytest
import os
import tempfile
import file_util


class TestFileSaveLoad:
    """Test file saving and loading functionality"""

    def test_save_and_load_dict(self):
        """Test saving and loading a dictionary"""
        test_data = {'key1': 'value1', 'key2': 42, 'key3': [1, 2, 3]}

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Save
            file_util.save(test_data, tmp_path)

            # Load
            loaded_data = file_util.load(tmp_path)

            assert loaded_data == test_data
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_save_and_load_list(self):
        """Test saving and loading a list"""
        test_data = [1, 2, 3, 'four', 5.0, {'nested': 'dict'}]

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            file_util.save(test_data, tmp_path)
            loaded_data = file_util.load(tmp_path)

            assert loaded_data == test_data
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_save_and_load_string(self):
        """Test saving and loading a string"""
        test_data = "This is a test string with special chars: !@#$%^&*()"

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            file_util.save(test_data, tmp_path)
            loaded_data = file_util.load(tmp_path)

            assert loaded_data == test_data
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_save_and_load_nested_structure(self):
        """Test saving and loading complex nested structure"""
        test_data = {
            'level1': {
                'level2': {
                    'level3': [1, 2, 3],
                    'another': 'value'
                },
                'list': [{'a': 1}, {'b': 2}]
            }
        }

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            file_util.save(test_data, tmp_path)
            loaded_data = file_util.load(tmp_path)

            assert loaded_data == test_data
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_save_and_load_empty_dict(self):
        """Test saving and loading empty dictionary"""
        test_data = {}

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            file_util.save(test_data, tmp_path)
            loaded_data = file_util.load(tmp_path)

            assert loaded_data == test_data
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_save_and_load_large_dict(self):
        """Test saving and loading large dictionary (memoization cache simulation)"""
        # Simulate memoization cache with many entries
        test_data = {i: (i % 3 - 1, i % 7) for i in range(1000)}

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            file_util.save(test_data, tmp_path)
            loaded_data = file_util.load(tmp_path)

            assert len(loaded_data) == 1000
            assert loaded_data == test_data
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_save_creates_file(self):
        """Test that save creates a file"""
        test_data = {'test': 'data'}

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp_path = tmp.name

        # Remove the file first
        os.remove(tmp_path)

        try:
            assert not os.path.exists(tmp_path)

            file_util.save(test_data, tmp_path)

            assert os.path.exists(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_load_nonexistent_file_raises_error(self):
        """Test that loading non-existent file raises error"""
        with pytest.raises(FileNotFoundError):
            file_util.load('/nonexistent/path/file.zip')

    def test_file_is_compressed(self):
        """Test that saved file is compressed (smaller than uncompressed)"""
        # Large repetitive data compresses well
        test_data = {'key': 'value' * 1000}

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            file_util.save(test_data, tmp_path)

            # File should exist and be relatively small due to compression
            assert os.path.exists(tmp_path)
            file_size = os.path.getsize(tmp_path)

            # Compressed file should be significantly smaller than uncompressed
            # (this is a rough check)
            assert file_size < 5000  # Should be much smaller than 5KB
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_save_with_binary_protocol(self):
        """Test saving with binary protocol"""
        test_data = {'test': [1, 2, 3]}

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Default binary protocol is 1
            file_util.save(test_data, tmp_path)
            loaded_data = file_util.load(tmp_path)

            assert loaded_data == test_data
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_save_overwrite_existing(self):
        """Test that save overwrites existing file"""
        test_data1 = {'version': 1}
        test_data2 = {'version': 2}

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Save first version
            file_util.save(test_data1, tmp_path)
            loaded1 = file_util.load(tmp_path)
            assert loaded1 == test_data1

            # Overwrite with second version
            file_util.save(test_data2, tmp_path)
            loaded2 = file_util.load(tmp_path)
            assert loaded2 == test_data2
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TestDataIntegrity:
    """Test data integrity and type preservation"""

    def test_integer_types_preserved(self):
        """Test that integer types are preserved"""
        test_data = {'small': 42, 'large': 999999999}

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            file_util.save(test_data, tmp_path)
            loaded_data = file_util.load(tmp_path)

            assert isinstance(loaded_data['small'], int)
            assert isinstance(loaded_data['large'], int)
            assert loaded_data == test_data
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_float_types_preserved(self):
        """Test that float types are preserved"""
        test_data = {'pi': 3.14159, 'negative': -2.5}

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            file_util.save(test_data, tmp_path)
            loaded_data = file_util.load(tmp_path)

            assert isinstance(loaded_data['pi'], float)
            assert isinstance(loaded_data['negative'], float)
            assert loaded_data == test_data
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_boolean_types_preserved(self):
        """Test that boolean types are preserved"""
        test_data = {'true_val': True, 'false_val': False}

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            file_util.save(test_data, tmp_path)
            loaded_data = file_util.load(tmp_path)

            assert isinstance(loaded_data['true_val'], bool)
            assert isinstance(loaded_data['false_val'], bool)
            assert loaded_data == test_data
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_none_value_preserved(self):
        """Test that None values are preserved"""
        test_data = {'null_value': None, 'other': 'value'}

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            file_util.save(test_data, tmp_path)
            loaded_data = file_util.load(tmp_path)

            assert loaded_data['null_value'] is None
            assert loaded_data == test_data
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_tuple_preserved(self):
        """Test that tuples are preserved"""
        test_data = {'tuple': (1, 2, 'three')}

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            file_util.save(test_data, tmp_path)
            loaded_data = file_util.load(tmp_path)

            assert isinstance(loaded_data['tuple'], tuple)
            assert loaded_data == test_data
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TestGameCacheSimulation:
    """Test with real game memoization cache structure"""

    def test_save_load_memoization_cache(self):
        """Test saving/loading structure similar to game memoization cache"""
        # Simulate memoization cache: hash -> (eval, move)
        test_cache = {
            12345: (2, 3),    # X wins by playing column 3
            67890: (-2, 1),   # O wins by playing column 1
            11111: (1, 2),    # Draw, play column 2
            22222: (None, 0)  # Game in progress
        }

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            file_util.save(test_cache, tmp_path)
            loaded_cache = file_util.load(tmp_path)

            assert loaded_cache == test_cache
            assert loaded_cache[12345] == (2, 3)
            assert loaded_cache[67890] == (-2, 1)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_large_cache_performance(self):
        """Test performance with large cache (10000 entries)"""
        import time

        # Create large cache similar to trained model
        large_cache = {i: (i % 5 - 2, i % 7) for i in range(10000)}

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Test save performance
            start_save = time.time()
            file_util.save(large_cache, tmp_path)
            save_time = time.time() - start_save

            # Test load performance
            start_load = time.time()
            loaded_cache = file_util.load(tmp_path)
            load_time = time.time() - start_load

            assert len(loaded_cache) == 10000
            assert loaded_cache == large_cache

            # Performance should be reasonable (less than 5 seconds each)
            assert save_time < 5.0
            assert load_time < 5.0
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
