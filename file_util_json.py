"""
Secure file utilities using JSON instead of pickle
Prevents code execution vulnerabilities (CWE-502)
"""

import json
import gzip


def save_to_json_file(obj, filename):
    """
    Safely save object to compressed JSON file

    Args:
        obj: Object to save (must be JSON-serializable)
        filename: Output filename (will add .json.gz)
    """
    if not filename.endswith('.json.gz'):
        filename = filename.replace('.pkl.gz', '.json.gz')

    with gzip.open(filename, 'wt', encoding='utf-8') as f:
        json.dump(obj, f, indent=2)


def load_from_json_file(filename):
    """
    Safely load object from compressed JSON file

    Args:
        filename: Input filename

    Returns:
        Loaded object

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is corrupted
    """
    # Support both .json.gz and .pkl.gz extensions for compatibility
    if filename.endswith('.pkl.gz'):
        json_filename = filename.replace('.pkl.gz', '.json.gz')
        # Try JSON first, fallback to pickle filename
        try:
            with gzip.open(json_filename, 'rt', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Try original filename in case it was already converted
            pass

    with gzip.open(filename, 'rt', encoding='utf-8') as f:
        return json.load(f)


def convert_pickle_to_json(pickle_file, json_file):
    """
    Convert existing pickle file to JSON (for migration)

    Args:
        pickle_file: Source .pkl.gz file
        json_file: Destination .json.gz file
    """
    import pickle

    # Load from pickle
    with gzip.open(pickle_file, 'rb') as f:
        data = pickle.load(f)

    # Convert keys from tuples to strings if needed
    if isinstance(data, dict):
        # Check if keys are tuples (common in board hash dictionaries)
        sample_key = next(iter(data.keys())) if data else None
        if isinstance(sample_key, tuple):
            # Convert tuple keys to string representation
            data = {str(k): v for k, v in data.items()}

    # Save as JSON
    save_to_json_file(data, json_file)
    print(f"✓ Converted {pickle_file} → {json_file}")
