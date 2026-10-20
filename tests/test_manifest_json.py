import json
import os

def test_manifest_valid_json():
    manifest_path = os.path.join(os.path.dirname(__file__), '..', 'manifest.json')
    with open(manifest_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert "name" in data, "manifest.json is missing 'name' key"
    assert "version" in data, "manifest.json is missing 'version' key"
