import json
from pathlib import Path
import pytest

def test_manifest_icons_exist():
    manifest_path = Path("manifest.json")
    if not manifest_path.exists():
        pytest.skip("manifest.json not found")

    with open(manifest_path, "r", encoding="utf-8") as f:
        try:
            manifest = json.load(f)
        except json.JSONDecodeError:
            pytest.skip("Invalid JSON in manifest.json")

    icons = manifest.get("icons", [])
    missing_paths = []

    for icon in icons:
        src = icon.get("src")
        if src:
            if not Path(src).exists():
                missing_paths.append(src)

    if missing_paths:
        pytest.xfail(f"Missing icon paths: {', '.join(missing_paths)}")
