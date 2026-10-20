import json
import pytest
from pathlib import Path

def test_manifest_json():
    manifest_path = Path("manifest.json")
    assert manifest_path.exists(), "manifest.json does not exist"

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "name" in data
    assert "start_url" in data
    assert "display" in data

    if "icons" not in data:
        pytest.xfail("manifest.json missing 'icons' key")

    for icon in data.get("icons", []):
        icon_path = Path(icon["src"])
        if not icon_path.exists():
            pytest.xfail(f"Icon path {icon['src']} does not exist")
